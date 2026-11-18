"""One simple entry point for people and coding agents (Codex, Claude Code, Cursor…).

    python make.py menu                                   # looks (tone · content · thumbnail), episodes, versions
    python make.py escape-velocity                        # build the episode's default version
    python make.py escape-velocity --as chart-story       # build another version of the same idea
    python make.py escape-velocity --as all --preview     # every version, fast 540x960, not logged
    python make.py sortino --as myth-buster --no 4        # quant topic + light series thumbnail #4
    python make.py new hedonic-treadmill --look dark-truth   # skeleton episode to fill in

A *look* (looks.json) fixes language, narrator voice, music, tone, content rules and thumbnail, so every agent
produces the same brand voice. An episode JSON (episodes/<id>.json) holds one idea; its "variants" block holds one
script per style ("versions"). Output: social-output/<id>-<style>/ (final.mp4, thumbnail.jpg, captions.md, QA).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

import core  # noqa: E402
from core import DEFAULT_OUT, KNOWLEDGE, SKILL  # noqa: E402

EPISODES = SKILL / "episodes"


def looks():
    return json.loads((SKILL / "looks.json").read_text(encoding="utf-8"))


def look_for(ep=None, name=None):
    data = looks()["looks"]
    if name:
        if name not in data:
            raise SystemExit(f"unknown look {name!r}; looks: {sorted(data)}")
        return name, data[name]
    if ep:
        if ep.get("look") in data:
            return ep["look"], data[ep["look"]]
        for k, lk in data.items():
            if lk["pillar"] == ep.get("pillar"):
                return k, lk
        if ep.get("pillar") and ep["pillar"] != "quant-education":  # research pillar: Vietnamese defaults, own docs
            return ep["pillar"], data["quant-vi"]
    return "quant-vi", data["quant-vi"]


def find_episode(name):
    for p in (Path(name), EPISODES / name, EPISODES / f"{name}.json"):
        if p.is_file():
            return p
    return None


def variants_of(ep):
    return list((ep.get("variants") or {}).keys()) or [ep.get("style")]


def resolve(ep, style):
    """Episode JSON + chosen version → the override batch.make expects."""
    base = {k: v for k, v in ep.items() if k != "variants"}
    if ep.get("variants"):
        if style not in ep["variants"]:
            raise SystemExit(f"{ep['id']} has no version {style!r}; versions: {variants_of(ep)}")
        base = core_merge(base, ep["variants"][style])
        base["id"] = f"{ep['id']}-{style}"
    base["style"] = style
    base.pop("about", None)
    return base


def core_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = core_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _published():
    path = KNOWLEDGE / "episodes.csv"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


# ---------------------------------------------------------------- commands
def cmd_menu():
    data = looks()
    pub = _published()
    print("LOOKS  (python make.py <episode|topic> --look <look>)\n")
    for k, lk in data["looks"].items():
        th = lk["thumbnail"]
        print(f"■ {k}: {lk['name']}  [{lk['lang']} · pillar {lk['pillar']} · voice {lk['voice']} · music {lk['music'] or 'pad'}]")
        print(f"  platforms : {', '.join(lk['platforms'])}")
        print(f"  tone      : {lk['tone']}")
        print(f"  content   : {lk['content']}")
        print(f"  thumbnail : {th['summary']}  (series '{th['series']}', needs {th['needs']}; {th['doc']})")
        print("  versions  : " + " | ".join(f"{s}{' (default)' if s == lk['default_style'] else ''}: {d}"
                                           for s, d in lk["styles"].items()))
        print(f"  example   : {lk['example']}\n")
    print("EPISODES  (episodes/*.json)\n")
    for p in sorted(EPISODES.glob("*.json")):
        ep = json.loads(p.read_text(encoding="utf-8"))
        lname, _ = look_for(ep)
        vers = []
        for s in variants_of(ep):
            oid = f"{ep['id']}-{s}" if ep.get("variants") else ep["id"]
            st = pub.get(oid, {}).get("status")
            vers.append(f"{s}" + (f" [{st}]" if st else ""))
        print(f"• {p.stem:<34} look {lname:<11} {ep.get('title', ep.get('hook', ''))[:60]}")
        print(f"  {'':<34} versions: {', '.join(vers)}")
    print("\nResearch pillars (own workflow, see pillars/<id>/PILLAR.md):")
    for k, v in data["research_pillars"].items():
        print(f"  {k:<20} {v}")
    print("\nQuant topics: python catalog.py --list | grep -i <word>   ·   then: python make.py <topic> --as <style>")


def cmd_make(a):
    import batch

    p = find_episode(a.target)
    ep = json.loads(p.read_text(encoding="utf-8")) if p else None
    lname, lk = look_for(ep, a.look)
    print(f"look {lname}: {lk['name']}  ·  tone: {lk['tone'][:110]}…")
    if ep:
        styles = variants_of(ep) if a.as_ == "all" else (a.as_.split(",") if a.as_ else
                                                          [lk["default_style"] if lk["default_style"] in variants_of(ep)
                                                           else variants_of(ep)[0]])
        jobs = [(ep["topic"], s, resolve(ep, s)) for s in styles]
    else:
        styles = list(lk["styles"]) if a.as_ == "all" else (a.as_.split(",") if a.as_ else [lk["default_style"]])
        jobs = [(a.target, s, None) for s in styles]
    results = []
    for topic, style, ov in jobs:
        if ov is not None and a.no:
            ov["episode_no"] = a.no
        r = batch.make(topic, style, ov, DEFAULT_OUT, voice=lk.get("voice"),
                       music=lk.get("music"), scale=0.5 if a.preview else 1.0, force=a.force, log=not a.preview)
        if r.get("ok") or a.force:
            thumb(lk, topic, style, ov, Path(r["out"]), a.no)
        results.append(r)
    print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(r.get("ok") for r in results) else 1


def thumb(lk, topic, style, ov, out, no):
    """Look-specific thumbnail. dark: the dark-story cover for any version. light-series: brand/thumbnail.md."""
    import batch
    kind = lk["thumbnail"]["kind"]
    if kind == "dark" and style != "dark-story":  # dark-story already writes it in its export()
        core.set_lang(lk["lang"])
        e, _, model = batch.prepare(topic, style, ov)
        filled = core.fill_tree(e, model.values, model.formats, set())
        batch.load_style("dark-story").thumbnail(filled, model, out / "thumbnail.jpg", (ov or {}).get("episode_no") or no)
        print(f"  thumbnail (dark) → {out / 'thumbnail.jpg'}")
    elif kind == "light-series" and no:
        import thumbnail as TH
        try:
            print(f"  thumbnail (series #{no}) → {TH.build(topic, no, out)}")
        except Exception as ex:  # catalog topics have no thumb block
            print(f"  thumbnail skipped ({type(ex).__name__}: {ex}); first frame kept as thumbnail.jpg")


SKELETON_SCENES = ["office", "commute", "scroll", "compare", "spend", "wheel", "crowd", "walkaway", "alone"]


def cmd_new(a):
    lname, lk = look_for(name=a.look or "dark-truth")
    path = EPISODES / f"{a.id}.json"
    if path.exists():
        raise SystemExit(f"{path} already exists")
    if lname != "dark-truth":
        raise SystemExit("quant-vi needs no skeleton: python make.py <topic> --as <style> (episode JSON only to override)")
    ep = {
        "id": a.id, "look": lname, "pillar": lk["pillar"], "topic": a.topic or f"dt_{a.id.replace('-', '_')}",
        "model": a.model, "lang": lk["lang"], "episode_no": a.no, "tag": "DARK TRUTH",
        "title": "TODO short title", "hook": "TODO a question the viewer has felt",
        "caption": "TODO 3-5 sentences; if a number is used, state its assumptions",
        "hashtags": ["darktruth", "moneymindset", "personalfinance", "QuanTik"],
        "cta": "Like and follow QuanTik for more dark truths about money",
        "claims": [], "allowed_literals": [],
        "thumb": {"series": "THE DARK TRUTH OF MONEY", "headline": ["TODO LINE ONE.", "TODO", "TODO."],
                  "sub": "", "footer": "Simulated data • Not financial advice"},
        "variants": {"dark-story": {
            "about": "TODO one line: what the animation shows",
            "scenes": [{"kind": k, "show": "TODO short on-screen line", "say": "TODO 1-2 short sentences"}
                       for k in SKELETON_SCENES]}},
    }
    path.write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}\nfill the TODOs following looks.json → looks.{lname} (tone, content, thumbnail), then:\n"
          f"  python make.py {a.id} --preview")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="menu | new | <episode id or file> | <quant topic id>")
    ap.add_argument("id", nargs="?", help="with 'new': the new episode id")
    ap.add_argument("--as", dest="as_", help="version(s): style name, comma list, or 'all'")
    ap.add_argument("--look", help="force a look from looks.json")
    ap.add_argument("--no", type=int, help="episode number for the series thumbnail")
    ap.add_argument("--preview", action="store_true", help="540x960, not logged in episodes.csv")
    ap.add_argument("--force", action="store_true", help="render even if pre-render QA fails (never publish)")
    ap.add_argument("--topic", help="with 'new': pillar topic id")
    ap.add_argument("--model", help="with 'new': model in pillar_models.py that supplies the one number")
    a = ap.parse_args()
    if a.target == "menu":
        return cmd_menu()
    if a.target == "new":
        if not a.id:
            ap.error("new needs an id: python make.py new <id> --look dark-truth")
        return cmd_new(a)
    return cmd_make(a)


if __name__ == "__main__":
    sys.exit(main() or 0)
