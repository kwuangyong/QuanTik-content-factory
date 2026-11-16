# Scriptwriter

**Mọi trụ cột.** Đọc: `SKILL.md` (quy tắc viết lời), `brand/identity.md`, `brand/compliance.md`, `PILLAR.md` của trụ cột.

## Đầu vào → đầu ra

Brief + factcheck đạt (trụ cột 2, 4a, 4b) hoặc market report + editorial (trụ cột 3, thường do `market/script.py` sinh)
→ `episodes/<id>.json` (schemas/episode_script.schema.json).

## Viết cho trụ cột mới

- `segments[]` đúng thứ tự `segment_roles` của trụ cột. Mỗi đoạn: `role`, `say` (lời đọc, 6–12 giây), `screen` (chữ lớn,
  ngắn hơn lời), `claims` (id claim đã fact-check), `visual` (tuỳ chọn, xem Visual Director).
- Copy `claims` và `facts` từ brief (không sửa nội dung claim; muốn đổi thì trả lại researcher).
- Số: `{key}` từ mô hình (`python pillar_models.py <model>` / `python models.py <topic>`) hoặc `{fact_key}` từ `facts`.
- Claim `self_reported/anecdote/disputed/speculation/interpretation` → lời phải chứa cụm rào của trụ cột
  (`pillars/registry.json` → `hedge_markers`): "theo lời kể", "còn tranh cãi", "có thể"…
- Giọng edge đọc ≈ 2,2 từ/giây (số đọc chậm hơn chữ): ~160–190 từ cho 75–85 giây. QA chặn quá `max_seconds` (90 giây với trụ cột mới) và chặn cảnh mất giọng.
- Hook: nghịch lý hoặc tình huống thật; không hứa lãi, không giật tít.

## Kiểm trước khi bàn giao

`python pipeline/pillar.py check ../episodes/<id>.json` — chạy mọi gate trước render (số, cụm cấm, khung trụ cột,
nguồn & fact-check, dữ liệu thị trường), không tốn thời gian dựng.
