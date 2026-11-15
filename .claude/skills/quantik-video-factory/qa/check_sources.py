"""Source traceability and fact-check gate for research-based pillar episodes.

Checks, in order of how often they catch real mistakes:
  1. every claim's source_ids exist in knowledge/sources/ledger.json, and documented claims have a source of the
     pillar's minimum tier (A = peer-reviewed / official / primary data, B = serious book or press, C = memoir/blog);
  2. every fact (sourced number) points to a ledger source (source_id or a claim with sources) — free-text
     "source" strings are legacy and not accepted for pillar episodes;
  3. every segment (except declared limitations) carries at least one claim;
  4. a segment that uses a self-reported / anecdotal / disputed / speculative / interpretive claim says so out loud
     (pillar hedge_markers), so the narration never upgrades a story into a fact;
  5. if the pillar requires fact-checking: research/<episode>/factcheck.json has a passing verdict for every claim the
     script uses, and the verdict's status (if given) matches the claim's status.

What it cannot do: judge whether a source really says what the claim says. That is the Fact-checker worker's job
(workers/fact-checker.md); this gate only refuses scripts whose claims were not checked or not traceable.

Usage: python check_sources.py <episode.json>
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from core import KNOWLEDGE, SKILL  # noqa: E402

TIER = {"A": 0, "B": 1, "C": 2}
PASS = {"verified", "verified_with_correction", "status_changed"}
NO_SOURCE_OK = {"model_output", "interpretation", "speculation"}


def _norm(s):
    return unicodedata.normalize("NFC", s or "").lower()


def ledger():
    data = json.loads((KNOWLEDGE / "sources/ledger.json").read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["sources"]}


def load_factcheck(ep):
    p = ep.get("factcheck")
    if not p:
        return None, "episode không khai báo 'factcheck' (đường dẫn research/<id>/factcheck.json)"
    path = (SKILL / p) if not Path(p).is_absolute() else Path(p)
    if not path.exists():
        return None, f"không thấy file fact-check {p}"
    return json.loads(path.read_text(encoding="utf-8")), None


def check(ep, pillar, factcheck=None):
    issues, warnings = [], []
    led = ledger()
    claims = {c["id"]: c for c in ep.get("claims", [])}
    min_tier = TIER[pillar.get("min_source_tier", "B")]
    used = []
    for seg in ep.get("segments", []):
        cl = seg.get("claims", [])
        if not cl and not seg.get("limitation"):
            issues.append(f"đoạn '{seg['role']}' không gắn claim nào — mọi khẳng định phải truy được nguồn")
        used += [c for c in cl if c not in used]
    # 1. ledger + tiers
    for cid, c in claims.items():
        srcs = c.get("source_ids", [])
        missing = [s for s in srcs if s not in led]
        if missing:
            issues.append(f"claim {cid}: nguồn {missing} không có trong ledger")
        if not srcs and c["status"] not in NO_SOURCE_OK:
            issues.append(f"claim {cid} ({c['status']}) không có nguồn")
        if c["status"] == "documented":
            tiers = [TIER[led[s]["tier"]] for s in srcs if s in led]
            if not tiers or min(tiers) > min_tier:
                issues.append(f"claim {cid} ghi 'documented' nhưng không có nguồn cấp ≥ {pillar.get('min_source_tier')}"
                              f" — hạ thành self_reported/anecdote hoặc thêm nguồn")
        if any(led.get(s, {}).get("id") == "synthetic-fixture" for s in srcs):
            issues.append(f"claim {cid} dựa trên dữ liệu mẫu — không được đăng")
    for cid in claims:
        if cid not in used:
            warnings.append(f"claim {cid} khai báo nhưng không đoạn nào dùng")
    # 2. facts
    for key, f in (ep.get("facts") or {}).items():
        if not isinstance(f, dict):
            issues.append(f"fact {key} không có nguồn")
            continue
        sid, cl = f.get("source_id"), f.get("claim")
        if sid and sid not in led:
            issues.append(f"fact {key}: source_id '{sid}' không có trong ledger")
        elif not sid and not (cl and claims.get(cl, {}).get("source_ids")):
            issues.append(f"fact {key}: thiếu source_id (nguồn dạng chữ '{f.get('source', '')[:40]}' không truy được)")
    # 4. hedges
    hedges = pillar.get("hedge_markers", {})
    for seg in ep.get("segments", []):
        say = _norm(seg["say"])
        for cid in seg.get("claims", []):
            st = claims.get(cid, {}).get("status")
            marks = hedges.get(st)
            if marks and not any(_norm(m) in say for m in marks):
                issues.append(f"đoạn '{seg['role']}' dùng claim {cid} trạng thái '{st}' nhưng lời không nói rõ "
                              f"(cần một trong: {', '.join(marks[:4])}…)")
    # 5. fact-check verdicts
    if pillar.get("requires_factcheck"):
        fc, err = (factcheck, None) if factcheck is not None else load_factcheck(ep)
        if err:
            issues.append(err)
        else:
            verdicts = {v["claim"]: v for v in fc["verdicts"]}
            for cid in used:
                v = verdicts.get(cid)
                if v is None:
                    issues.append(f"claim {cid} chưa được fact-check")
                elif v["verdict"] not in PASS:
                    issues.append(f"claim {cid}: fact-check '{v['verdict']}' — {v.get('note', '')[:80]}")
                elif v.get("status") and v["status"] != claims[cid]["status"]:
                    issues.append(f"claim {cid}: fact-checker kết luận trạng thái '{v['status']}', kịch bản ghi "
                                  f"'{claims[cid]['status']}'")
    sources = sorted({s for c in used for s in claims.get(c, {}).get("source_ids", [])})
    return {"fail": bool(issues), "issues": issues, "warnings": warnings,
            "details": {"claims_used": len(used), "sources": sources}}


if __name__ == "__main__":
    import pillar_registry as PR

    ep = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    p = PR.pillar_of(ep)
    if p is None:
        print("không phải episode trụ cột nghiên cứu — bỏ qua"); sys.exit(0)
    res = check(ep, p)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if res["fail"] else 0)
