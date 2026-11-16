# TikTok — "Học quant cùng QuanTik"

**Vai trò:** giáo dục, xây độ tin cậy, nuôi tầng SAM (người tò mò, hứng thú với quant).
**Nội dung:** giải thích mô hình, chỉ số, thuật ngữ quant — đúng thứ pipeline `batch.py` làm tốt nhất.
Giữ nguyên hướng đang chạy.

## Quy trình

1. **Chọn chủ đề** theo `SKILL.md` bước 1 (8 mô hình viết tay hoặc catalog). Ưu tiên chỉ số **có trong sản phẩm**
   (`module_*`, `sheet-*`, `action_*`) để người xem gặp lại chúng khi mở QuanTik. Đọc `knowledge/episodes.csv`
   để không trùng và nối mạch tập trước.
2. **Chọn style:** cả 8 style đều dùng được (bảng trong `SKILL.md`). Gợi ý luân phiên trong tuần: `code-reel`,
   `myth-buster`, `kinetic-text`, `meme-quant`, `carousel` (TikTok photo).
3. **Viết lời** theo `SKILL.md` bước 3: số qua placeholder, hook tự hiểu được với người mới.
4. **Dựng:**
   ```bash
   cd pipeline && python batch.py --platform tiktok --topics garch --styles code-reel
   ```
   Output vào `social-output/<topic>-<style>-tiktok/`. CTA thẻ cuối tự gắn: "Thả tim và theo dõi QuanTik để học
   một kiến thức quant mỗi ngày".
5. **Thumbnail series** "Học Quant cùng QuanTik #N": `brand/thumbnail.md`, hỏi số tập nếu chưa rõ.
6. **Caption TikTok:** câu hook → hashtag → câu miễn trừ. Link tính năng chỉ ở caption ("Chỉ số này có trong
   Phân tích Quant tại quantik.io.vn"), không chèn quảng bá vào lời đọc.
7. **QA** theo `SKILL.md` bước 5.

## Đo

Sau 7 ngày: `views_tiktok`, cộng follow mới và tỉ lệ xem hết (ghi vào `notes`). Hook thắng → `knowledge/hooks.md`.
