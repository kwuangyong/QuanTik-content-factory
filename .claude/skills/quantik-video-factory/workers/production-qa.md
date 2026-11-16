# Production QA

## Gate tự động (chặn trước render → không tốn thời gian dựng)

| Gate | File | Áp dụng | Chặn khi |
| --- | --- | --- | --- |
| Số khớp code | `qa/check_numbers.py` | mọi tập | số không đến từ mô hình/report, `facts`, citation trong ledger hay `allowed_literals` |
| Cụm cấm | `qa/check_banned.py` | mọi tập (+ `extra_banned` của trụ cột) | hô hào mua bán, hứa lãi; trụ cột 3: "sẽ tăng", "chắc chắn", "bắt đáy"… |
| Khung trụ cột | `qa/check_script.py` | tập có `pillar` | sai schema, sai thứ tự vai, claim không tồn tại, decision-science thiếu GIỐNG/KHÁC |
| Nguồn & fact-check | `qa/check_sources.py` | tập có `pillar` | nguồn không trong ledger, `documented` dưới tier, đoạn không có claim, thiếu cụm rào, fact-check thiếu/không đạt/lệch trạng thái |
| Ảnh nhân vật & bản quyền | `qa/check_images.py` | trụ cột 2, 4a, 4b (và mọi tập có ảnh) | người/hãng/sự kiện được nhắc mà không có ảnh hay lý do; ảnh không có trong sổ ảnh; ảnh thật không có giấy phép tự do, tác giả, ghi công; ảnh minh hoạ không ghi "minh hoạ" |
| Dữ liệu thị trường | `qa/check_market.py` | trụ cột 3 | không có dữ liệu, dữ liệu mẫu, dữ liệu cũ không khai báo, trộn quan sát/mô hình/nhận định, thiếu 3 kịch bản có điều kiện, nhắc mã cụ thể, giới hạn không lên caption |

## Gate sau render

`qa/check_format.py`: 9:16, 12 giây ≤ thời lượng ≤ `max_seconds`, có âm thanh, không chữ tràn khung/ra ngoài vùng an toàn.

## Đầu ra

`qa_report.md` (người đọc) + `qa_report.json` (schemas/qa_report.schema.json) trong `social-output/<id>/`, kèm
`sources.md` cho tập trụ cột. Kết luận ĐẠT chỉ khi mọi gate đạt.

## Người duyệt (không tự động được)

Checklist trong `qa_report.md`: nghe hết video, nhãn dữ liệu, không câu nào như lời khuyên mua/bán, giá gói, nhạc có
giấy phép; với trụ cột mới thêm: nhãn trạng thái đúng với nguồn, mở `sources.md` đối chiếu số chính.
Lệnh: `python pillar.py check <episode>` (chỉ gate trước render), `python -m unittest discover -s tests` (bộ test).
