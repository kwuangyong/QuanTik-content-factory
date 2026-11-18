# Kênh YouTube Shorts + Instagram Reels

Chủ sản phẩm chốt (11/2026): **YT Shorts và IG Reels chỉ đăng nhóm nội dung dưới đây.** Video giải thích mô hình
quant và video hướng dẫn sản phẩm QuanTik không đăng lên hai nền tảng này (chúng đi TikTok / Facebook).

## Chủ đề (80 ý tưởng, `knowledge/concepts/*.json`)

| Nhóm | Số | File |
| --- | --- | --- |
| Dark Truth Finance | 01–20 | `dark-truth.json` |
| Poker Theory | 21–35 | `poker.json` |
| Psychology Facts | 36–55 | `psychology.json` |
| Game Theory | 56–70 | `game-theory.json` |
| Quant Mindset (kinh tế học hành vi & xác suất) | 71–80 | `quant-mindset.json` |

Thêm nhóm mới: hỏi chủ sản phẩm trước.

## Dựng

```bash
cd pipeline
python concepts.py --list                                     # 80 id
python concepts.py 71-monty-hall                              # số dùng được làm {placeholder}
python batch.py --topics 71-monty-hall --styles sketch-short  # một video
python batch.py --topics concepts:poker --styles sketch-short # một nhóm
python batch.py --topics concepts --styles sketch-short       # cả 80 (khoảng 2 giờ)
```

Mỗi concept có `visual.kind`. Đó là đoạn code chạy thật trong `pipeline/concepts.py`, gồm các loại: mô phỏng
(ruin, montyhall, ipd, commons…), công thức đóng (birthday, kelly, potodds…), bảng số từ nghiên cứu có nguồn
(`bars`) hoặc sơ đồ vẽ tay không có số (`diagram`). Lời thoại dùng `{key}` từ lần chạy đó, nên QA số vẫn áp dụng.

## Quy chuẩn sản xuất (mặc định đã áp dụng, người dùng có thể đổi)

| Mặt | Đang dùng |
| --- | --- |
| Ngôn ngữ | Lời đọc và phụ đề tiếng Việt. Tên khái niệm tiếng Anh hiện trên màn hình và nhắc ở lần đầu |
| Hình ảnh | Nhận diện QuanTik (nền tối, logo, màu cam), style `sketch-short` |
| Hoạt hoạ vẽ tay | Biểu đồ/sơ đồ nét xkcd hiện dần, gạch chân và vòng khoanh run tay |
| B-roll | Không dùng stock. Mọi hình vẽ bằng code (chưa có nguồn B-roll có giấy phép) |
| Hook | Câu nghịch lý/câu hỏi ở 2–3 giây đầu, tên khái niệm ở chip phía trên |
| Tempo giọng | edge-tts vi-VN-HoaiMyNeural, nhanh hơn 8%. Video 40–55s |
| Caption | `captions.md` chỉ có YouTube Shorts + Instagram Reels |
| CTA | Thẻ cuối theo dõi QuanTik (`FOLLOW_CTA`) |

## Luật vẫn áp dụng

- `brand/compliance.md`: dark truth finance không gọi mua/bán, không hứa lợi nhuận, không có cụm cấm. Poker
  thêm câu "không khuyến khích cờ bạc" trong caption.
- "Facts" tâm lý học có nguồn trong `facts` của concept. Số trong nghiên cứu (nhóm `bars`) cần người duyệt đối
  chiếu bản gốc trước khi đăng: 37, 43, 45, 48, 50, 51, 53 (xem lưu ý trong báo cáo).
- Nhạc, ảnh, meme, B-roll phải có giấy phép.
