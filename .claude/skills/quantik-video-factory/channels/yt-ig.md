# Kênh YouTube Shorts + Instagram Reels (tiếng Anh)

Chủ sản phẩm chốt (11/2026): **YT Shorts và IG Reels chỉ đăng nhóm nội dung dưới đây, bằng tiếng Anh.** Video giải
thích mô hình quant và video hướng dẫn sản phẩm QuanTik (tiếng Việt) không đăng lên hai nền tảng này.

## 80 tập (`episodes/yt/ytNN-<slug>.json`)

| Nhóm | Số | Chip trên video | Series thumbnail |
| --- | --- | --- | --- |
| Dark Truth Finance | 01–20 | `DARK TRUTH #NN` | THE DARK TRUTH OF MONEY |
| Poker Theory | 21–35 | `POKER THEORY #NN` | POKER THEORY |
| Psychology Facts | 36–55 | `PSYCHOLOGY #NN` | PSYCHOLOGY FACTS |
| Game Theory | 56–70 | `GAME THEORY #NN` | GAME THEORY |
| Quant Mindset | 71–80 | `QUANT MINDSET #NN` | QUANT MINDSET |

## Quy chuẩn (yêu cầu của chủ sản phẩm)

| Mặt | Quy chuẩn | Ở đâu |
| --- | --- | --- |
| Ngôn ngữ | Tiếng Anh toàn bộ: lời, phụ đề, chữ trên hình, caption, thẻ cuối, câu miễn trừ | `"lang": "en"` |
| Hình | **Không chart.** Style `dark-story`: hoạt hoạ phẳng tông tối, một màu đỏ cảnh báo, film grain | `styles/dark-story/template.py` |
| B-roll ảnh thật | Ảnh Wikimedia Commons giấy phép tự do, **ghi tác giả + giấy phép ngay trên khung**. Có ảnh thật thì dùng, không có thì vẽ tay | `"image"` (sổ ảnh `knowledge/images/ledger.json`), `"visual"` + `"real": true` (B-roll theo tag) |
| Hoạt hoạ vẽ tay | Cảnh dark-story (`office`, `commute`, `scroll`, `compare`, `spend`, `wheel`, `crowd`, `walkaway`, `alone`, `doors`, `duel`, `scale`) + cảnh `illustrate.py` (casino, roulette, coin, iceberg, storm, money_burn…) | `"kind"`, `"visual"` |
| Số | Đếm lên thật to (`"big"`) hoặc đám đông n người sáng k người (`"crowd"`); số từ mô phỏng chạy thật hoặc nguồn trong sổ nguồn | `"sim"` → `pipeline/concept_sims.py`; `facts` + `claims` |
| Hook | Ragebait, nổ ngay câu đầu, **đúng sự thật**, không hứa lãi | cảnh đầu `scenes[0]` |
| Tempo | Giọng ×1,25 (`TEMPO` trong `core.py`), giọng nam trầm `en-US-ChristopherNeural`, nhạc nền hồi hộp 120 bpm tự tổng hợp | `"voice": "male-deep"`, `"music": "suspense"` |
| Caption | Tiếng Anh; poker thêm câu "không khuyến khích cờ bạc" | `"caption"` |

## Dựng

```bash
cd pipeline
python concept_sims.py ../episodes/yt/yt71-monty-hall.json          # số dùng được làm {placeholder}
python batch.py --episode ../episodes/yt/yt71-monty-hall.json --voice male-deep
python batch.py --episode ../episodes/yt/yt71-monty-hall.json --check-only --no-log   # chỉ QA trước render
```

Ảnh người/nơi chốn: `python images.py search "<tên>"` rồi `python images.py fetch "File:…" --id <id> --subject "<tên>"`.
Môi trường cloud dùng chung IP nên Commons hay trả HTTP 429: tải chậm, có ảnh rồi thì dựng lại tập đó.

## Luật vẫn áp dụng

- `brand/compliance.md` (cụm cấm Việt + Anh), không gọi mua/bán, không hứa lợi nhuận.
- Số trong nghiên cứu tâm lý học cần người duyệt đối chiếu bản gốc trước khi đăng (37, 43, 45, 48, 50, 51, 53).
- Nhạc/ảnh/B-roll phải có giấy phép; ảnh CC BY/BY-SA bắt buộc ghi công (pipeline tự ghi trên khung và trong caption).

## Tiến độ (18/11/2026)

- **Đã dựng và giao (50):** 01–42, 56, 57, 58, 71, 72, 77, 78, 80. Tất cả đạt QA.
- **Còn lại (30):** 43–55, 59–70, 73–76, 79. Kịch bản đã viết và đã qua QA trước render (`--check-only`).
- Ảnh thật dự phòng khi Commons trả 429: `python openverse_images.py "<id>|<truy vấn>[|person]" …` (kiểm tra bằng mắt
  mọi ảnh người; xoá ảnh nhận nhầm người khỏi sổ ảnh).
- Đóng gói giao hàng: `python package_yt.py 43-55 59-70 73-76 79 --name yt-ig-lot-30` → `social-output/_zip/`.
