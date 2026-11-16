# Trụ cột 1 — Quant Education (học quant)

Trụ cột gốc của repo, **không đổi gì**. Quy trình đầy đủ: `SKILL.md` mục Quy trình.

| Thành phần | Ở đâu |
| --- | --- |
| Quy trình nghiên cứu | không cần researcher: số liệu do mô hình viết tay (`knowledge/models/*.md` + `pipeline/models.py`) hoặc định nghĩa đã duyệt trong `knowledge/catalog.json` |
| Phân loại chủ đề | `knowledge/CATALOG.md` (199 chủ đề: glossary, module báo cáo Quant, trường hành động, cột sheet, engine) |
| Khung kịch bản | `hook → beats[0..3] → takeaway → CTA` (`video_defaults`) |
| Kể chuyện | trực giác → công thức → con số do code tính → giới hạn mô hình |
| Hình | 8 style trong `styles/` (code-reel, kinetic-text, chart-story, myth-buster, whiteboard-math, talking-head-script, carousel, meme-quant) |
| Kiểm chứng | `check_numbers` (số từ code), `facts` cho sự kiện lịch sử |
| QA | `check_numbers`, `check_banned`, `check_format` |
| Lệnh | `python batch.py --topics <id> --styles <style>` (không đổi) |

Episode JSON cũ (không có `pillar`) vẫn chạy y như trước. Ghi `"pillar": "quant-education"` là tuỳ chọn và không đổi hành vi.
