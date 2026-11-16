"""Market-intelligence gate: freshness, fact/model/interpretation separation, scenario discipline, no tickers.

  * data_status unavailable or sample → fail (no market video from no data or from test fixtures);
  * freshness is recomputed at check time: data older than the pillar's max_data_sessions_behind fails unless the
    episode sets allow_stale AND the hook and first segment say the as-of date and that the data is old;
  * each role carries the right kind of claim (asof/breadth/liquidity/sectors: observed or model_output; regime:
    model_output or a declared limitation; interpretation/scenarios/risk: interpretation);
  * a missing regime must be said out loud as a limitation, and the report's limitations must reach the caption;
  * exactly three scenarios (bull/base/bear), each with confirmation and invalidation conditions; any probability
    must be called a subjective estimate in the narration;
  * no individual ticker from the data universe appears anywhere (market videos speak about the market, not stocks).

Usage: python check_market.py <episode.filled.json> <market_report.json>
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))

ROLE_KINDS = {"asof": {"observed", "model_output"}, "breadth": {"observed", "model_output"},
              "liquidity": {"observed", "model_output"}, "sectors": {"observed", "model_output"},
              "regime": {"model_output"}, "interpretation": {"interpretation"}, "scenarios": {"interpretation"},
              "risk": {"interpretation"}}
INDEX_WORDS = {"HOSE", "HNX", "VN30", "UPCOM", "VNINDEX", "AGR"}


def check(ep, report, pillar, now=None, corpus=()):
    from market.common import now_ict, sessions_behind, vi_date

    issues = []
    st = report["data_status"]
    if st == "unavailable":
        issues.append("không có dữ liệu thị trường: " + " | ".join(report["limitations"]))
    if st == "sample":
        issues.append("dữ liệu mẫu (fixture) — không được đăng")
    behind = None
    if report.get("as_of"):
        as_of = dt.date.fromisoformat(report["as_of"])
        behind = sessions_behind(as_of, now or now_ict())
        limit = pillar.get("max_data_sessions_behind", 0)
        if behind > limit:
            d = vi_date(as_of)
            if not ep.get("allow_stale"):
                issues.append(f"dữ liệu cũ {behind} phiên (as_of {d}) — fetch lại hoặc làm bản tổng kết với allow_stale")
            else:
                first = (ep.get("segments") or [{}])[0].get("say", "")
                if d not in ep.get("hook", "") + first or "dữ liệu cũ" not in (first + ep.get("hook", "")).lower():
                    issues.append(f"allow_stale nhưng hook/đoạn đầu không nói rõ ngày {d} và 'dữ liệu cũ'")
    claims = {c["id"]: c for c in ep.get("claims", [])}
    roles = []
    for seg in ep.get("segments", []):
        roles.append(seg["role"])
        kinds = {claims[c]["status"] for c in seg.get("claims", []) if c in claims}
        allowed = ROLE_KINDS.get(seg["role"], set())
        if seg.get("limitation"):
            if not re.search(r"chưa đủ|không có dữ liệu|giới hạn", seg["say"].lower()):
                issues.append(f"đoạn giới hạn '{seg['role']}' phải nói rõ giới hạn")
            continue
        bad = kinds - allowed
        if bad:
            issues.append(f"đoạn '{seg['role']}' trộn loại phát biểu {sorted(bad)} (chỉ được {sorted(allowed)})")
    if report.get("regime") is None and "regime" in roles:
        seg = next(s for s in ep["segments"] if s["role"] == "regime")
        if not seg.get("limitation"):
            issues.append("báo cáo không có regime nhưng kịch bản có đoạn regime không phải giới hạn")
    if report["limitations"] and "giới hạn" not in ep.get("caption", "").lower():
        issues.append("caption phải liệt kê giới hạn dữ liệu của báo cáo")
    sc = ep.get("scenarios") or []
    if sorted(s.get("name") for s in sc) != ["base", "bear", "bull"]:
        issues.append("cần đúng 3 kịch bản bull/base/bear")
    for s in sc:
        if not s.get("confirmation") or not s.get("invalidation"):
            issues.append(f"kịch bản {s.get('name')} thiếu điều kiện xác nhận hoặc vô hiệu")
    if any(s.get("subjective_probability") is not None for s in sc):
        say = " ".join(x.get("say", "") for x in ep.get("segments", []) if x["role"] == "scenarios").lower()
        if "chủ quan" not in say:
            issues.append("kịch bản có xác suất thì lời phải nói đó là ước lượng chủ quan")
    universe = set(report.get("universe") or []) - INDEX_WORDS
    hits = sorted({t for text in corpus for t in re.findall(r"(?<![A-Za-z0-9])[A-Z0-9]{3}(?![A-Za-z0-9])", text or "")
                   if t in universe})
    if hits:
        issues.append(f"video thị trường nhắc mã cụ thể {hits[:8]} — chỉ nói về thị trường, nhóm ngành")
    return {"fail": bool(issues), "issues": issues,
            "details": {"data_status": st, "as_of": report.get("as_of"), "sessions_behind_now": behind}}


if __name__ == "__main__":
    import pillar_registry as PR

    ep = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    rep = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    res = check(ep, rep, PR.get("market-intelligence"),
                corpus=[ep.get("hook", ""), ep.get("caption", "")] + [s["say"] for s in ep.get("segments", [])])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if res["fail"] else 0)
