# YouTube Shorts — bản tiếng Anh, "ăn xổi"

**Vai trò:** kéo view nhanh, phủ tên QuanTik ra ngoài thị trường Việt.
**Ngôn ngữ:** **tiếng Anh**, giọng nam trầm (edge-tts `en-US-AndrewNeural`), số viết kiểu Anh (12.3%, 1,000).
**Độ dài:** không cần dưới 1 phút, tối đa **2 phút** (QA chặn > 120s). Bản ngắn 20–45s để kéo view, bản 60–120s cho
chuyện cần kể (gambler's ruin, chuỗi thua).

Giọng điệu khác hẳn TikTok: không dạy từng bước, mà nói **một sự thật khó nghe** rồi chứng minh bằng số do code tính.
Cảm giác "dark, honest, a bit uncomfortable", không phải "học bài".

## Ba trụ nội dung

| Trụ | Góc | Ví dụ hook | Mô hình / style |
| --- | --- | --- | --- |
| **Dark truth** | sự thật khó nghe về thị trường | "You don't get the average return. You get one path." · "Most of your returns come from a handful of days." · "Your 'safe' stock has fatter tails than you think." | `monte_carlo`, `var_cvar`, `garch` · `kinetic-text`, `myth-buster` |
| **Investor psychology & problems** | não người chơi chứng khoán lừa mình thế nào | "Your brain plans for a bad day. The market plans for a worse one." · "Why you sell winners too early." · "Revenge trading, in one chart." | `var_cvar`, `sharpe`, `hurst` · `meme-quant`, `kinetic-text` |
| **Poker theory** | tư duy xác suất của dân poker áp vào đầu tư | "Poker pros with an edge still bet small." · "Gambler's ruin: how a winning player goes broke." · "Pot odds, but for stocks." | `kelly`, `monte_carlo` · `myth-buster`, `code-reel` |

Mẫu đã viết sẵn: `episodes/en-poker-kelly-myth.json`, `episodes/en-dark-truth-paths.json`, `episodes/en-psych-worst-day.json`.

## Quy trình

0. **Hình ảnh:** ảnh thật bắt buộc + hình hoạ tự vẽ xen kẽ (tự động mỗi cảnh thứ ba). Chọn bằng `"broll"` (từ khoá ảnh)
   và `"art"` (`chips`, `dice`, `cards`, `coins`, `storm`, `brain`, `person`, `paths`, `scale`, `hourglass`, `target`).
   Ghi chú cũ — thêm `"broll"` (từ khoá người/vật cụ thể, tiếng Anh) vào episode; xem `brand/identity.md`.
1. **Chọn trụ và một sự thật** có thể chứng minh bằng một trong 8 mô hình viết tay (danh sách số: `python pipeline/models.py <topic>`).
2. **Viết episode tiếng Anh** `episodes/en-<id>.json`, có `"platform": "youtube-shorts"`. Phải ghi đè **mọi** trường
   chữ mà style dùng (`hook`, `beats`, `myth`/`fact` hoặc `meme`, `takeaway`, `title`, `caption`, `hashtags`, `tag`),
   vì lời mặc định của chủ đề là tiếng Việt. QA chặn nếu còn sót chữ tiếng Việt.
   - Câu đầu nói thẳng sự thật, dưới 12 từ. Không mở bằng "Hi guys" hay "Did you know".
   - Số vẫn qua placeholder `{key}`. Hiện tượng tâm lý (loss aversion, disposition effect…) là sự kiện có nguồn:
     ghi vào `facts` kèm `source` (ví dụ Kahneman & Tversky 1979), không gõ số tay.
   - Kết bằng một câu "mang về được", không bao giờ thành lời khuyên mua/bán.
3. **Dựng:**
   ```bash
   cd pipeline && python batch.py --episode ../episodes/en-poker-kelly-myth.json
   python batch.py --platform youtube-shorts --episode ../episodes/en-dark-truth-paths.json --episode ../episodes/en-psych-worst-day.json
   ```
   Pipeline tự chuyển sang tiếng Anh: giọng, số, nhãn trên màn hình ("YOU THINK / THE TRUTH", "Takeaway"),
   chữ trên chart, câu miễn trừ tiếng Anh, CTA thẻ cuối "Follow for the math behind the market".
4. **Caption** trong `captions.md`, mục *YouTube Shorts (English)*: tiêu đề ≤ 90 ký tự + `#Shorts`, mô tả, CTA,
   disclaimer tiếng Anh, hashtag tiếng Anh.
5. **QA** như mọi video: số khớp code, cụm cấm **cả tiếng Việt lẫn tiếng Anh** (`brand/compliance.md`), không sót
   chữ tiếng Việt, khung chữ.

## Ranh giới

"Dark" là về **sự thật của rủi ro**, không phải doạ hay giật tít sai:

- Không "the market is about to crash", không dự báo giá, không nêu mã nào sẽ tăng/giảm.
- Không "get rich", "quit your job", "financial freedom in…", "easy money" (QA chặn).
- Poker theory là **khung tư duy xác suất**, không cổ vũ cờ bạc, không gợi ý đặt cược thật.
- Câu miễn trừ tiếng Anh luôn có ở caption và thẻ cuối.

## Đo

Sau 7 ngày: `views_youtube`, tỉ lệ xem hết (viewed vs swiped away), sub mới. Trụ nào có lượt xem hết cao nhất sau
6–8 video thì dồn vào trụ đó.
