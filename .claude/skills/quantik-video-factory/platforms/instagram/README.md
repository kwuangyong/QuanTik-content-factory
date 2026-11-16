# Instagram Reels — tiếng Anh, đang thử nghiệm

**Ngôn ngữ:** **tiếng Anh** (chủ sản phẩm chốt 11/2026), như YouTube Shorts: giọng, số, nhãn, câu miễn trừ tự chuyển sang
tiếng Anh khi chạy `--platform instagram`. **Độ dài:** không cần dưới 1 phút, tối đa **2 phút**.

Khác YouTube Shorts ở chỗ: Shorts bán *sự thật khó nghe* (dark truth, poker, psychology); Instagram bán *cảm giác
"đúng mình"* để người xem share/save.

**Vai trò:** lan truyền, đưa thương hiệu tới tầng TAM.
**Người xem:** phần lớn Gen Z, rất trẻ, không thích học nhiều. Họ share, save, repost thứ khiến họ thấy
"đúng mình", buồn cười, hoặc có động lực.
**Trạng thái:** chưa có công thức đã kiểm chứng. Làm theo vòng thử, chưa đầu tư nghiên cứu sâu.

## Dạng thử

| Dạng | Ví dụ | Style | Độ dài |
| --- | --- | --- | --- |
| Larping / POV | "POV: the market is red and you calmly open the volatility table" · "Me and my boss when the market is green" | `meme-quant`, `kinetic-text`; skit cần người quay | 15–60s |
| Motivational, kỷ luật | "Emotion says sell. Data says wait." · "The market doesn't owe you a bounce." | `kinetic-text` | 20–60s |
| Meme quant | "Nobody: … Quants: …" | `meme-quant` | 12–30s |
| Câu chuyện có số | "I bet 40% every time. Here's what happened after 500 bets." | `kinetic-text`, `myth-buster` | 45–120s |
| Đáng lưu | cheat sheet: "5 risk numbers every investor should know" | `carousel` (1–3 slide) | — |

## Quy trình

1. **Chọn một dạng** trong vòng thử hiện tại (mục *Vòng thử* dưới đây).
2. **Viết episode tiếng Anh** `episodes/en-<id>.json` với `"platform": "instagram"`: hook ngắn, câu chữ đời thường,
   một ý. Ghi đè mọi trường chữ (lời mặc định là tiếng Việt; QA chặn chữ Việt còn sót). Số vẫn qua placeholder.
   Thêm `"broll"`: từ khoá ảnh người/vật cụ thể (xem `brand/identity.md` › Hình ảnh thật).
3. **Dựng:**
   ```bash
   cd pipeline && python batch.py --platform instagram --episode ../episodes/<id>.json
   ```
   CTA thẻ cuối mặc định: "Save this. Send it to a friend who trades." Tối đa 120 giây.
4. **Caption** (mục *Instagram Reels (English)*): ngắn, emoji vừa phải, hashtag tiếng Anh, câu miễn trừ tiếng Anh,
   dòng ghi nguồn ảnh.
5. **QA** như mọi video.

## Ranh giới (vẫn theo `brand/compliance.md`)

- Không khoe lãi, ảnh tài khoản, lifestyle "giàu nhanh", "tự do tài chính nhờ…".
- Motivational là về **kỷ luật và quy trình**, không về tiền. Không hứa thắng.
- Nhạc và meme template phải có giấy phép.

## Vòng thử

Mỗi vòng 2 tuần, 2–3 dạng, mỗi dạng 3–4 video. Ghi share và save (không chỉ view) vào `notes` của
`knowledge/episodes.csv`. Dạng nào thắng rõ thì đưa lên bảng *Dạng thử* thành dạng chính và ghi ngày.

| Vòng | Từ ngày | Dạng thử | Kết quả |
| --- | --- | --- | --- |
| 1 | _(chưa bắt đầu)_ | | |

## Đo

`views_reels`, cộng share, save, repost (ghi vào `notes`).
