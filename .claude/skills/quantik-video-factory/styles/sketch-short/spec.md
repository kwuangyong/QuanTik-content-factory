# sketch-short

Style cho kênh **YouTube Shorts + Instagram Reels** (`channels/yt-ig.md`). Phong cách bảng phấn vẽ tay: biểu đồ
matplotlib chế độ xkcd hiện dần từng nét, gạch chân và vòng khoanh run tay vẽ bằng PIL, số chính đếm lên.

| # | Cảnh | Trường episode |
| --- | --- | --- |
| 1 | hook: chip nhóm, tên khái niệm tiếng Anh, câu hook, gạch chân vẽ tay | `kicker`, `en`, `hook` |
| 2 | ý mở | `beats[0]` |
| 3 | hình vẽ tay: mô phỏng/sơ đồ hiện dần + ghi chú giả định/nguồn | `beats[1]`, `chart_title`, `chart_note` |
| 4 | số chính đếm lên trong vòng khoanh (sơ đồ không có số → chữ) | `beats[2]`, `punch.value`, `punch.label` |
| 5 | vì sao / giới hạn | `beats[3]` |
| 6 | mang về | `takeaway` |
| 7 | thẻ cuối theo dõi kênh | `cta` |

- Giọng đọc nhanh hơn 8% (`VOICE_RATE`). Độ dài 40–55s, QA chặn quá 60s.
- Chỉ dùng cho topic trong `knowledge/concepts/*.json` (dữ liệu mô phỏng ở `pipeline/concepts.py`).
- Viết lời: tối đa khoảng 125 từ cho hook + 4 beat + takeaway, nếu dài hơn thì video vượt 60 giây.
