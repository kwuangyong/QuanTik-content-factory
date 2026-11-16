# Instagram Reels — đang thử nghiệm

(YouTube Shorts là nhánh riêng, tiếng Anh: `../youtube-shorts/README.md`.)

**Vai trò:** lan truyền, đưa thương hiệu tới tầng TAM.
**Người xem:** phần lớn Gen Z, rất trẻ, không thích học nhiều. Họ share, save, repost thứ khiến họ thấy
"đúng mình", buồn cười, hoặc có động lực.
**Trạng thái:** chưa có công thức đã kiểm chứng. Làm theo vòng thử, chưa đầu tư nghiên cứu sâu.

## Dạng thử

| Dạng | Ví dụ | Style | Độ dài |
| --- | --- | --- | --- |
| Larping / POV | "POV: bạn là quant, thị trường đỏ, còn bạn bình tĩnh mở bảng biến động" | `meme-quant`, `kinetic-text` | 10–20s |
| Motivational, kỷ luật | "Cảm xúc bảo bán. Dữ liệu bảo đợi." | `kinetic-text` | 15–30s |
| Meme quant | "Nobody: … Quant: …" | `meme-quant` | 12–20s |
| Đáng lưu | cheat sheet: "5 chỉ số rủi ro nên biết" | `carousel` (1–3 slide) | — |

## Quy trình

1. **Chọn một dạng** trong vòng thử hiện tại (mục *Vòng thử* dưới đây).
2. **Viết episode** `episodes/<id>.json` với `"platform": "instagram"`: hook ngắn, câu chữ đời thường, một ý.
   Số vẫn qua placeholder.
3. **Dựng:**
   ```bash
   cd pipeline && python batch.py --platform instagram --episode ../episodes/<id>.json
   python batch.py --platform instagram --topics kelly,hurst --styles meme-quant   # lời mặc định
   ```
   CTA thẻ cuối mặc định kêu gọi share/save ("Lưu lại, gửi cho đứa bạn hay bàn chứng khoán"). Tối đa 45 giây.
4. **Caption:** ngắn, emoji vừa phải, hashtag cuối, có câu miễn trừ.
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
