"""Write qa_report.md (the pass/fail sheet, layout follows qa/qa_report.md) into a video's output folder."""
from __future__ import annotations

import datetime as dt
from pathlib import Path


def _mark(res):
    if res is None:
        return "— (chưa chạy)"
    return "❌ KHÔNG ĐẠT" if res["fail"] else "✅ ĐẠT"


def summary(nums, banned, fmt, more=None):
    s = (f"  QA  số liệu: {_mark(nums)} ({nums['checked']} số)   cụm cấm: {_mark(banned)}   "
         f"định dạng: {_mark(fmt)}")
    for name, res in more or []:
        s += f"\n      {name}: {_mark(res)}" + "".join(f"\n        - {i}" for i in res.get("issues", [])[:8])
    return s


def write(out: Path, ep, nums, banned, fmt, status, extra=None, more=None):
    """more: [(name, result)] extra gates (pillar script, sources/fact-check, market) — also written to qa_report.json."""
    lines = [f"# Phiếu QA — {ep['id']}", "",
             f"- Ngày: {dt.datetime.now():%Y-%m-%d %H:%M}",
             f"- Chủ đề × style: `{ep['topic']}` × `{ep['style']}`",
             f"- **Kết luận: {status}**"]
    for k, v in (extra or {}).items():
        lines.append(f"- {k}: {v}")
    lines += ["", "| Hạng mục | Kết quả | Chi tiết |", "| --- | --- | --- |"]
    det = "; ".join(f"`{b['number']}` trong “{b['in']}”" for b in nums["unsourced"]) or f"{nums['checked']} số đều có nguồn"
    lines.append(f"| Số khớp code | {_mark(nums)} | {det} |")
    det = "; ".join(f"“{h['phrase']}” trong “{h['in']}”" for h in banned["hits"]) or f"không dính {banned['checked_phrases']} cụm cấm"
    lines.append(f"| Cụm cấm | {_mark(banned)} | {det} |")
    if fmt is not None:
        det = "; ".join(fmt["issues"]) or ", ".join(f"{k} {v}" for k, v in fmt["facts"].items())
        lines.append(f"| Định dạng / khung chữ | {_mark(fmt)} | {det} |")
    for name, res in more or []:
        det = "; ".join(res.get("issues", [])) or "; ".join(f"{k}: {v}" for k, v in (res.get("details") or {}).items()) or "ổn"
        lines.append(f"| {name} | {_mark(res)} | {det.replace('|', '/')} |")
        for w in res.get("warnings", []):
            lines.append(f"| ↳ cảnh báo | — | {w} |")
    lines += ["", "## Người duyệt kiểm tra bằng mắt trước khi đăng", "",
              "- [ ] Xem hết video có tiếng; giọng đọc đúng số trên màn hình",
              "- [ ] Nhãn “Dữ liệu mô phỏng” hoặc nguồn dữ liệu thật hiển thị rõ",
              "- [ ] Không có câu nào đọc như lời khuyên mua/bán mã cụ thể",
              "- [ ] Caption có câu miễn trừ; giá gói (nếu nhắc) khớp trang /plans hiện tại",
              "- [ ] Nhạc nền có giấy phép (hoặc là pad tự tạo của pipeline)", ""]
    if ep.get("pillar") and ep.get("pillar") != "quant-education":
        lines.insert(-1, "- [ ] Mọi nhãn trạng thái (tư liệu / lời tự kể / tranh cãi / quan sát / mô hình / nhận định) đúng với nguồn")
        lines.insert(-1, "- [ ] Mở `sources.md`, đối chiếu ít nhất các nguồn của số liệu chính")
    (Path(out) / "qa_report.md").write_text("\n".join(lines), encoding="utf-8")
    checks = [{"name": "Số khớp code", "fail": nums["fail"], "issues": nums["unsourced"]},
              {"name": "Cụm cấm", "fail": banned["fail"], "issues": banned["hits"]}]
    if fmt is not None:
        checks.append({"name": "Định dạng / khung chữ", "fail": fmt["fail"], "issues": fmt["issues"]})
    checks += [{"name": n, "fail": r["fail"], "issues": r.get("issues", []), "details": r.get("details")} for n, r in more or []]
    import json

    (Path(out) / "qa_report.json").write_text(json.dumps(
        {"id": ep["id"], "pillar": ep.get("pillar"), "status": status, "checks": checks,
         "voice": str((extra or {}).get("Giọng đọc", "")), "generated": f"{dt.datetime.now():%Y-%m-%dT%H:%M:%S}"},
        ensure_ascii=False, indent=2, default=str), encoding="utf-8")
