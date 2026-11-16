"""Structure check for an episode script: JSON schema + the pillar's segment-role order + claim references.

Usage: python check_script.py <episode.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from core import SKILL  # noqa: E402

SCHEMAS = SKILL / "schemas"


def validate(obj, schema_name):
    """List of schema errors (empty = valid). Uses jsonschema when installed, else a required-keys check."""
    schema = json.loads((SCHEMAS / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ImportError:
        return [f"thiếu trường bắt buộc '{k}'" for k in schema.get("required", []) if k not in obj]
    v = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(map(str, e.absolute_path)) or '(gốc)'}: {e.message}" for e in v.iter_errors(obj)]


def check(ep, pillar):
    issues = validate(ep, "episode_script")
    if pillar is None:
        return {"fail": bool(issues), "issues": issues}
    roles = pillar.get("segment_roles", [])
    segs = ep.get("segments")
    if roles and pillar_style(ep, pillar):
        if not segs:
            issues.append(f"style {ep['style']} cần 'segments' theo thứ tự {roles}")
        else:
            got = [s["role"] for s in segs]
            optional = set(pillar.get("optional_roles", []))
            need = [r for r in roles if r not in optional or r in got]
            if got != need:
                issues.append(f"thứ tự đoạn {got} ≠ khung của trụ cột {need}")
    ids = {c["id"] for c in ep.get("claims", [])}
    for c in ep.get("claims", []):
        if c["status"] not in pillar["claim_statuses"]:
            issues.append(f"claim {c['id']}: trạng thái '{c['status']}' không dùng trong trụ cột {pillar['id']}")
    for s in segs or []:
        for cid in s.get("claims", []):
            if cid not in ids:
                issues.append(f"đoạn {s['role']} trỏ tới claim không tồn tại '{cid}'")
    if ep.get("style") == "decision-lab" or pillar["id"] == "decision-science":
        an = ep.get("analogy") or {}
        if not an.get("similar") or not an.get("breaks"):
            issues.append("trụ cột decision-science bắt buộc 'analogy' có cả 'similar' và 'breaks' (poker giống và khác thị trường ở đâu)")
    return {"fail": bool(issues), "issues": issues}


def pillar_style(ep, pillar):
    """Only the pillar's own styles (first in its list) require segments; legacy styles use derived beats."""
    return ep.get("style") in ("bias-lab", "history-story", "market-brief", "decision-lab")


if __name__ == "__main__":
    import pillar_registry as PR

    ep = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = check(ep, PR.pillar_of(ep))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if res["fail"] else 0)
