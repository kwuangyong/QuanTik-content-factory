"""Multi-pillar entry point. batch.py keeps working unchanged; this adds pillar research and market workflows.

  python pillar.py list                                   # the 5 pillar architectures
  python pillar.py topics behavioral-finance              # catalog of one pillar
  python pillar.py scaffold quant-history qh_ltcm --id qh-ltcm-history-story   # brief + factcheck + episode skeletons
  python pillar.py validate ../research/<id>/brief.json research_brief          # any file against any schema
  python pillar.py check ../episodes/<id>.json            # every pre-render gate, no render
  python pillar.py make  ../episodes/<id>.json --scale 0.5 [--no-log]

  python pillar.py market fetch [--history h.csv --history-manifest h.json] [--fixture DIR] [--skip-instruments]
  python pillar.py market analyze  [BUNDLE]               # → BUNDLE/market_report.json
  python pillar.py market editorial [BUNDLE] [--allow-stale]   # → BUNDLE/market_editorial.json (rule-based draft)
  python pillar.py market script   [BUNDLE] [--editorial file.json] [--allow-stale]  # → BUNDLE/episode.json
  python pillar.py market produce  [--bundle BUNDLE] [--allow-stale] [--scale 0.5] [--check-only]  # all stages

BUNDLE defaults to the newest bundle in social-output/_market/. Each stage reads only the previous stage's file,
so a human or the Market Intelligence Analyst can stop, review and edit between stages.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

import pillar_registry as PR  # noqa: E402
from core import SKILL, load_json, save_json  # noqa: E402


def cmd_list(a):
    for p in PR.pillars():
        n = len(PR.catalog(p["id"])) if p["id"] != "quant-education" else len(load_json(SKILL / p["catalog"])["topics"])
        print(f"{p['number']:<3} {p['id']:<20} {n:>4} chủ đề  style mặc định {p['default_style']:<14} "
              f"worker: {p['research_worker'] or '—'}")
        print(f"    {p['name']}")
        if p["segment_roles"]:
            print(f"    khung: {' → '.join(['hook'] + p['segment_roles'] + ['takeaway', 'end'])}")


def cmd_topics(a):
    if a.pillar == "quant-education":
        print("Trụ cột 1 dùng knowledge/CATALOG.md: python catalog.py --list"); return
    for t in PR.catalog(a.pillar):
        print(f"{t['id']:<26} {t['status']:<8} {t.get('model') or '—':<16} {t['group']} · {t['name']}")


def cmd_scaffold(a):
    p = PR.get(a.pillar)
    entry = next((t for t in PR.catalog(a.pillar) if t["id"] == a.topic), None)
    if entry is None:
        raise SystemExit(f"{a.topic} không có trong catalog {a.pillar}; thêm vào {p['catalog']} trước")
    eid = a.id or f"{a.topic.replace('_', '-')}-{p['default_style']}"
    rdir = SKILL / "research" / eid
    rdir.mkdir(parents=True, exist_ok=True)
    claim = {"id": "c1", "text": "…", "status": p["claim_statuses"][0], "source_ids": ["<id trong ledger>"]}
    brief = {"id": eid, "pillar": p["id"], "topic": a.topic, "question": "…", "audience_problem": "…", "claims": [claim],
             "facts": {}, "framework": {r: "…" for r in p["segment_roles"]}, "model": entry.get("model"),
             "rejected_claims": [], "open_questions": [], "created": "YYYY-MM-DD", "researcher": p["research_worker"]}
    if p["id"] == "decision-science":
        brief["analogy"] = {"similar": ["…"], "breaks": ["…"]}
    fc = {"brief": f"research/{eid}/brief.json", "checked": "YYYY-MM-DD", "checker": "fact-checker",
          "verdicts": [{"claim": "c1", "verdict": "unverified", "evidence": [], "note": "…"}]}
    ep = {"id": eid, "pillar": p["id"], "topic": a.topic, "style": a.style or p["default_style"], "model": entry.get("model"),
          "brief": f"research/{eid}/brief.json", "factcheck": f"research/{eid}/factcheck.json", "title": "…", "hook": "…",
          "segments": [{"role": r, "say": "…", "claims": ["c1"]} for r in p["segment_roles"]],
          "claims": [claim], "facts": {}, "takeaway": "…", "caption": "…", "hashtags": ["quant", "QuanTik"],
          "allowed_literals": []}
    for path, obj in ((rdir / "brief.json", brief), (rdir / "factcheck.json", fc), (SKILL / "episodes" / f"{eid}.json", ep)):
        if path.exists() and not a.force:
            print(f"  giữ nguyên {path.relative_to(SKILL)} (đã có; --force để ghi đè)")
        else:
            save_json(path, obj); print(f"  tạo {path.relative_to(SKILL)}")
    print(f"Tiếp: worker {p['research_worker']} điền brief → fact-checker điền factcheck → scriptwriter viết episode → "
          f"python pillar.py check ../episodes/{eid}.json")


def cmd_validate(a):
    import check_script

    errs = check_script.validate(load_json(a.file), a.schema)
    print("✅ hợp lệ" if not errs else "\n".join("❌ " + e for e in errs))
    sys.exit(1 if errs else 0)


def _make(ep_path, a, check_only):
    import batch

    ep = load_json(ep_path)
    return batch.make(ep["topic"], ep["style"], ep, a.out, a.voice_engine, a.voice, a.music, a.scale, 30, None, None,
                      False, not a.no_log, check_only)


def cmd_check(a):
    import check_script

    ep = load_json(a.episode)
    for key, schema in (("brief", "research_brief"), ("factcheck", "factcheck")):
        if ep.get(key):
            errs = check_script.validate(load_json(SKILL / ep[key]), schema)
            print(f"  {key}: " + ("✅ hợp lệ schema" if not errs else "❌ " + "; ".join(errs[:5])))
    r = _make(a.episode, a, True)
    sys.exit(0 if r["ok"] else 1)


def cmd_make(a):
    r = _make(a.episode, a, False)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(0 if r["ok"] else 1)


# ---------------------------------------------------------------- market
def _bundle(arg):
    from market.common import DEFAULT_DATA

    if arg:
        return Path(arg)
    bs = sorted(Path(DEFAULT_DATA).glob("bundle-*"))
    if not bs:
        raise SystemExit("chưa có bundle nào — chạy: python pillar.py market fetch")
    return bs[-1]


def cmd_market(a):
    from market import analyze as AN, editorial as ED, fetch as FE, script as SC
    from market.common import DEFAULT_DATA, load, save

    import check_script

    stage = a.stage
    if stage == "fetch":
        b = FE.fetch(a.data_dir or DEFAULT_DATA, a.history, a.history_manifest, fixture=a.fixture,
                     skip_instruments=a.skip_instruments)
        print(b); return
    if stage == "produce" and not a.bundle and not a.no_fetch:
        b = FE.fetch(a.data_dir or DEFAULT_DATA, a.history, a.history_manifest, skip_instruments=a.skip_instruments)
    else:
        b = _bundle(a.bundle)
    if stage in ("analyze", "produce"):
        rep = AN.analyze(b, data_root=a.data_dir)
        print(f"  report: {b/'market_report.json'} · data_status={rep['data_status']} · as_of={rep['as_of']}")
        for lim in rep["limitations"]:
            print(f"    giới hạn: {lim}")
        errs = check_script.validate(rep, "market_report")
        if errs:
            raise SystemExit("market_report sai schema: " + "; ".join(errs[:5]))
        if stage == "analyze":
            return
    rep = load(b / "market_report.json")
    if stage in ("editorial", "produce") and not a.editorial:
        try:
            ed = ED.draft(rep, allow_stale=a.allow_stale)
        except ED.EditorialRefused as ex:
            print(f"  ✗ editorial từ chối: {ex}")
            sys.exit(2)
        save(b / "market_editorial.json", ed)
        print(f"  editorial: {b/'market_editorial.json'} ({ed['author']})")
        if stage == "editorial":
            return
    ed = load(a.editorial) if a.editorial else load(b / "market_editorial.json")
    errs = check_script.validate(ed, "market_editorial")
    if errs:
        raise SystemExit("market_editorial sai schema: " + "; ".join(errs[:5]))
    ep = SC.build(rep, ed, b / "market_report.json", allow_stale=a.allow_stale)
    save(b / "episode.json", ep)
    print(f"  episode: {b/'episode.json'}")
    if stage == "script":
        return
    r = _make(b / "episode.json", a, a.check_only)
    print(json.dumps(r, ensure_ascii=False, indent=2))
    sys.exit(0 if r["ok"] else 1)


def main():
    from core import DEFAULT_OUT

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    s = sub.add_parser("topics"); s.add_argument("pillar"); s.set_defaults(fn=cmd_topics)
    s = sub.add_parser("scaffold"); s.add_argument("pillar"); s.add_argument("topic"); s.add_argument("--id")
    s.add_argument("--style"); s.add_argument("--force", action="store_true"); s.set_defaults(fn=cmd_scaffold)
    s = sub.add_parser("validate"); s.add_argument("file"); s.add_argument("schema"); s.set_defaults(fn=cmd_validate)

    def render_opts(s):
        s.add_argument("--out", default=str(DEFAULT_OUT)); s.add_argument("--scale", type=float, default=1.0)
        s.add_argument("--voice-engine", default="auto"); s.add_argument("--voice", default="male-deep")
        s.add_argument("--music", default=None); s.add_argument("--no-log", action="store_true")

    s = sub.add_parser("check"); s.add_argument("episode"); render_opts(s); s.set_defaults(fn=cmd_check)
    s = sub.add_parser("make"); s.add_argument("episode"); render_opts(s); s.set_defaults(fn=cmd_make)
    s = sub.add_parser("market"); s.add_argument("stage", choices=["fetch", "analyze", "editorial", "script", "produce"])
    s.add_argument("bundle", nargs="?"); s.add_argument("--bundle", dest="bundle_opt")
    s.add_argument("--data-dir"); s.add_argument("--history"); s.add_argument("--history-manifest")
    s.add_argument("--fixture"); s.add_argument("--skip-instruments", action="store_true")
    s.add_argument("--editorial"); s.add_argument("--allow-stale", action="store_true")
    s.add_argument("--check-only", action="store_true"); s.add_argument("--no-fetch", action="store_true")
    render_opts(s); s.set_defaults(fn=cmd_market)
    a = ap.parse_args()
    if a.cmd == "market":
        a.bundle = a.bundle_opt or a.bundle
    a.fn(a)


if __name__ == "__main__":
    main()
