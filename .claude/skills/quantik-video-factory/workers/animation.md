# Animation (code)

| File | Việc |
| --- | --- |
| `pipeline/render.py` | `Scene` dataclass, render khung → ffmpeg, phụ đề `.srt`, `layout.json` |
| `pipeline/frames.py` | nền, header, chữ tự co (`text_box` ghi tràn khung cho QA), chart/3D/code/terminal panel |
| `pipeline/scenes.py` | cảnh dùng chung cho 8 style cũ (hook, chart, surface, formula, code, terminal, end) |
| `pipeline/pillar_scenes.py` | cảnh trụ cột mới: nhãn vai + trạng thái, chân trang nguồn, citation, timeline, split, scenarios, gauge |

Đầu vào: episode đã điền số + model. Đầu ra: `final.mp4`, `thumbnail.jpg`, `subtitles.srt`, `layout.json`, và (mới)
`storyboard.json` (cảnh, thời điểm, lời, claim, nguồn, loại hình) + `visual_assets.json` (xuất xứ từng tài sản).
Ràng buộc: mọi chữ vẽ bằng `frames.text_box` để QA đo được; nội dung trong y 300–1240, chân trang nguồn 1258–1308,
phụ đề 1326–1488.
