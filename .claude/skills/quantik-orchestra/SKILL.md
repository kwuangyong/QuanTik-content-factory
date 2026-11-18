---
name: quantik-orchestra
description: Điều phối dàn worker QuanTik content factory theo model (Haiku tìm nguồn/dựng/đo view, Sonnet viết/kiểm compliance/soát hình, Opus duyệt cuối) để làm video, carousel, loạt bài hoặc video hướng dẫn sản phẩm QuanTik mà tiết kiệm token. Dùng khi người dùng gõ /quantik-orchestra, nói "chạy pipeline", "chạy dàn agent", "làm loạt video cả tuần", "duyệt giúp rồi đăng", hoặc khi yêu cầu nội dung có từ 2 video trở lên.
---

# QuanTik Orchestra

Session chính là **orchestrator**: chỉ điều phối, không tự làm việc của worker, không đọc file lớn.
Quy trình chuyên môn vẫn là `.claude/skills/quantik-video-factory/SKILL.md`; các worker tự đọc phần mình cần.

> Tiết kiệm nhất: chạy session chính bằng **Sonnet** (`/model sonnet`). Opus chỉ vào ở hai cổng duyệt qua
> `quantik-director`. Subagent không gọi được subagent khác, nên mọi bước giao việc đều đi từ session chính.

## Dàn worker

| Agent | Model | Việc | Ra file |
| --- | --- | --- | --- |
| `quantik-scout` | haiku | tra catalog, kiểm trùng, key số, hook, giá /plans, xu hướng vidIQ | `01-brief.md` |
| `quantik-scriptwriter` | sonnet | episode JSON / beats.py, caption, sửa theo chỉ thị | `SK/episodes/<id>.json` |
| `quantik-director` | **opus** | cổng 1 (góc + kịch bản), cổng 2 (phát hành) | `05-verdict-g1/g2.md` |
| `quantik-producer` | haiku | cài đặt, `batch.py` / `run.sh`, trích khung, đo âm | `02-render.md`, `_frames/` |
| `quantik-compliance` | sonnet | cụm cấm, khuyến nghị trá hình, số, giá gói, miễn trừ | `03-compliance.md` |
| `quantik-visual-qa` | sonnet | xem khung: tràn chữ, lệch lời-hình, lộ mã thật | `04-visual.md` |
| `quantik-analyst` | haiku | view sau 7 ngày, hook thắng, đề xuất tuần tới | `social-output/analytics-*.md` |

Handoff qua file trong `social-output/<run_id>/_orchestra/` (đã gitignore). Khi giao việc, chỉ đưa: yêu cầu,
`run_id`, id video, đường dẫn file cần đọc. Worker trả lại vài dòng + đường dẫn; **đừng yêu cầu dán nội dung file**.

## Luồng

`run_id` = `<ngày>-<chủ đề ngắn>` (vd `2026-11-18-kelly-series`).

1. **Scout** (haiku) → brief. Hỏi người dùng chỉ khi brief báo mơ hồ thật sự (vd chưa rõ số tập thumbnail).
2. **Scriptwriter** (sonnet) → episode cho từng video. Nhiều video độc lập: gọi song song nhiều scriptwriter trong
   cùng một lượt (mỗi cái 1–3 video).
3. **Compliance** (sonnet) soát kịch bản (chế độ `--text`). SỬA → quay lại bước 2 với `03-compliance.md`.
4. **Cổng 1 — Director** (opus): đọc brief + episode. SỬA → bước 2 với chỉ thị. LOẠI → báo người dùng, đề xuất thay.
   Loạt nhiều video: duyệt cả loạt **một lần** trong một lời gọi.
5. **Producer** (haiku): dựng bản đăng `--scale 1` (muốn xem trước rẻ hơn thì `--scale 0.5 --no-log` rồi dựng lại sau
   cổng 2). QA máy KHÔNG ĐẠT → bước 2 với lỗi nguyên văn; không dùng `--force`.
6. **Compliance** (render + captions) và **Visual QA** — gọi **song song** trong cùng lượt.
7. **Cổng 2 — Director** (opus): DUYỆT / SỬA / LOẠI. Tối đa 2 vòng SỬA mỗi video.
8. **Trả người dùng** (orchestrator tự làm, theo luật 6 trong AGENTS.md): đường dẫn `final.mp4`, thời lượng, QA,
   engine giọng, caption từng nền tảng lấy từ `captions.md` trong khối copy được, ghi chú của director.
   Nhắc: ghi view sau 7 ngày → gọi `quantik-analyst`.

Video hướng dẫn sản phẩm: cùng luồng, scriptwriter sửa bản chép `beats.py`, producer chạy `tutorial/run.sh`.

## Rút gọn theo cỡ việc

| Việc | Dùng |
| --- | --- |
| 1 video, chủ đề viết tay, style mặc định, không giá gói | scout → producer → compliance ∥ visual → director cổng 2 (bỏ scriptwriter + cổng 1) |
| 1 video có góc riêng | đủ luồng |
| Loạt ≥ 3 video | đủ luồng; scriptwriter song song; director 1 lần/cổng cho cả loạt |
| Chỉ viết caption/kịch bản, không dựng | scout → scriptwriter → compliance → director cổng 1 |
| Cập nhật view / lên lịch tuần | chỉ `quantik-analyst` |

## Luật orchestrator

- Không bỏ cổng compliance. Director không được DUYỆT khi compliance CHẶN.
- Không cho worker đăng nhập site thật bằng thông tin người dùng; không đăng bài lên mạng xã hội khi người dùng chưa bảo.
- Báo tiến độ ngắn sau mỗi cổng (một dòng: "Cổng 1 xong: 4/5 DUYỆT, 1 SỬA hook").
- Môi trường thiếu mạng TTS: producer báo engine thay thế → nêu rõ trong kết quả cuối.
