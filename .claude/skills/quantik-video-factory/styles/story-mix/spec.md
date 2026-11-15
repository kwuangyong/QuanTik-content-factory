# story-mix

Style linh hoạt: **episode tự xếp chuỗi cảnh**, nên mỗi video có cấu trúc riêng thay vì cùng một khuôn.
Dùng khi làm loạt bài cùng một mô hình mà không muốn các tập giống nhau, hoặc khi cần kể chuyện lịch sử, cách
dùng, đố vui. Độ dài mục tiêu 45–75s (`max_seconds` mặc định 75).

**Chống lặp giữa các tập cùng chủ đề:** mỗi episode nên khác nhau ở cả bốn lớp:

1. **Góc kể** (thứ tự cảnh): lịch sử → cơ chế, đố vui → lời giải, sai lầm → cách dùng đúng, so sánh hai kịch bản…
2. **Dữ liệu**: `seed` riêng và `params` riêng (VD GARCH `{"a": 0.12, "b": 0.85}`, Kelly `{"W": 0.53, "R": 1.2}`,
   OU `{"theta": 0.25}`, Hurst `{"phi": 0.7}`, VaR `{"df": 4}`). Số, chart, 3D và dòng `def` trên màn hình đổi theo.
3. **Hình**: 2D hay 3D hay cả hai; góc quay 3D `view`; code cả hàm hay chỉ vài dòng (`lines`, `hl`).
4. **Chữ ngoài video**: `title`, `caption`, `hashtags`, khối `thumb` riêng trong episode.

## Loại cảnh (`scenes[].type`)

| type | Trường | Ghi chú |
| --- | --- | --- |
| `hook` | `text`, `say?`, `kicker?` | luôn đặt đầu |
| `story` | `era`, `title`, `text`, `say`, `chip?`, `source?` | lịch sử/nhân vật; số năm, số tiền vào `facts` kèm nguồn |
| `usage` | `title?`, `steps[]` (2–4 bước), `say`, `chip?` | cách dùng/đọc chỉ số, nơi xem trong QuanTik |
| `quiz` | `question`, `options[]` (2–4), `answer` (chỉ số 0..), `say`, `reveal_at?` (0..1, mặc định 0,62) | lời nên đặt câu hỏi, ngập ngừng, rồi nói đáp án |
| `compare` | `title?`, `left`/`right` = `{label, value, note?, color?}`, `say` | hai con số đối đầu; `color`: positive/negative/neutral/accent |
| `myth` | `myth`, `fact`, `say` | thẻ "Bạn nghĩ" bị gạch → "Thực ra" |
| `code` | `say`, `lines? [a, b]`, `hl?` (số dòng), `note?`, `title?` | luôn là code thật của mô hình; trích dòng để đổi trọng tâm |
| `run` | `outputs[]` (như code-reel), `say` | một mục `highlight: true` |
| `chart` | `say`, `title?`, `notes? [[tiến độ, chữ], …]` | chart 2D vẽ dần |
| `surface` | `say`, `view?`, `caption?` | `view`: `orbit` · `top` · `low` · `spin` · `dive` · `side` |
| `formula` | `latex`, `say`, `caption?` | trong LaTeX dùng `<<key>>` cho số |
| `statement` | `text`, `say?`, `chip?` | câu mang về |

Thẻ cuối (CTA theo dõi kênh + miễn trừ) tự gắn. Mỗi cảnh có `min_dur?` nếu cần giữ lâu hơn giọng đọc.

## Quy tắc

- Số trong lời và chữ: placeholder `{key}` hoặc `facts`. QA chặn số gõ tay như mọi style.
- Chuyện lịch sử: chỉ dùng sự kiện có nguồn; ghi `source` trên thẻ. Không chắc thì bỏ.
- Mỗi video tối đa 9–10 cảnh; tối thiểu một cảnh hình (chart/surface/compare) chứng minh bằng số.
- Ví dụ đầy đủ: `episodes/ep06-garch-nobel.json`.

```bash
python batch.py --episode ../episodes/ep06-garch-nobel.json
python thumbnail.py --episode ../episodes/ep06-garch-nobel.json --no 6 --out ../../../../social-output/ep06-garch-nobel
```
