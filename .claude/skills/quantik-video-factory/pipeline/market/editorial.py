"""Stage 3 — editorial interpretation. Turns a market_report into market_editorial.json: hedged interpretations
(each tied to the report keys it rests on) and exactly three scenarios with measurable confirmation and
invalidation conditions. Generic risk actions only; never a ticker, never a call.

`draft()` is a deterministic rule-based first draft so the pipeline is runnable end to end. The Market Intelligence
Analyst worker (workers/market-intelligence-analyst.md) reviews or rewrites it; its author field says which.

Numbers go in as {placeholders} filled from the report at render time. The fixed thresholds of the rules below are
declared in THRESHOLDS so QA can accept them as literals.
"""
from __future__ import annotations

THRESHOLDS = ["60%", "40%", "3 phiên", "2 phiên", "5 phiên", "3 phiên liền"]

REFUSE = {"unavailable": "không có dữ liệu thị trường", "sample": "dữ liệu mẫu không được dùng cho nhận định thật"}


class EditorialRefused(Exception):
    pass


def draft(report, allow_stale=False):
    st = report["data_status"]
    if st in REFUSE:
        raise EditorialRefused(f"không viết nhận định: {REFUSE[st]}. Giới hạn: " + " | ".join(report["limitations"]))
    if st == "stale" and not allow_stale:
        raise EditorialRefused("dữ liệu cũ (" + str(report["sessions_behind"]) + " phiên sau as_of) — chạy fetch lại, "
                               "hoặc --allow-stale để làm bản tổng kết có ghi rõ ngày")
    M = report["model"]
    has = lambda k: k in M and M[k]["value"] is not None
    inter = [{"text": "Độ rộng {breadth_pct} cho thấy phiên này {breadth_state}: nên đọc chỉ số cùng số mã tăng giảm.", "based_on": ["breadth_pct", "adv", "dec"]}]
    if has("lead_sector"):
        inter.append({"text": "Dòng tiền trong phiên có thể đang nghiêng về {lead_sector} hơn {lag_sector}; một phiên "
                              "chưa đủ để gọi là luân chuyển ngành.", "based_on": ["lead_sector", "lag_sector"]})
    if has("top10_share"):
        inter.append({"text": "Mười mã lớn nhất chiếm {top10_share} giá trị khớp: nếu tỷ trọng này cao, chỉ số có thể "
                              "phản ánh một nhóm nhỏ hơn là cả thị trường.", "based_on": ["top10_share"]})
    scen = [
        {"name": "bull", "description": "Độ rộng cải thiện và lan sang nhiều nhóm ngành.",
         "confirmation": ["Trên 60% mã tăng 3 phiên liền, VN-INDEX giữ trên {vnindex:num0}"],
         "invalidation": ["Độ rộng quay lại dưới 40% trong 2 phiên"],
         "investor_actions": ["Giữ quy mô vị thế theo mức rủi ro đã định, không tăng đòn bẩy chỉ vì một phiên tốt"]},
        {"name": "base", "description": "Thị trường phân hoá, chỉ số đi ngang quanh vùng hiện tại.",
         "confirmation": ["Độ rộng dao động giữa 40% và 60% trong 5 phiên"],
         "invalidation": ["Độ rộng vượt 60% hoặc xuống dưới 40% trong 3 phiên liên tiếp"],
         "investor_actions": ["Đánh giá lại từng vị thế theo điều kiện thoát đã đặt trước"]},
        {"name": "bear", "description": "Độ rộng thu hẹp, áp lực lan rộng.",
         "confirmation": ["Dưới 40% mã tăng 3 phiên, VN-INDEX đóng cửa dưới {vnindex:num0}"],
         "invalidation": ["Độ rộng trở lại trên 60% trong 2 phiên"],
         "investor_actions": ["Kiểm tra tổng rủi ro danh mục, ưu tiên giảm đòn bẩy trước khi ra quyết định khác"]},
    ]
    return {"report": report["id"], "author": "editorial.py draft (luật cố định) — cần Market Intelligence Analyst duyệt",
            "interpretations": inter, "scenarios": scen,
            "risk_notes": ["Ba kịch bản là điều kiện để theo dõi, không phải dự báo; không kịch bản nào chắc chắn xảy ra."]}
