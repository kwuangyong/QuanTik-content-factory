# Trụ cột 2 — Investor Psychology & Behavioral Finance (tâm lý nhà đầu tư)

**Mục tiêu:** giải thích sai lầm của nhà đầu tư bằng bằng chứng, không bằng lời động viên.
Worker nghiên cứu: `workers/behavioral-finance-researcher.md`. Style: `bias-lab` (mặc định), kinetic-text, myth-buster,
carousel, talking-head-script.

## Khung tập phim (bắt buộc, QA kiểm thứ tự)

`hook → problem → mechanism → evidence → implication → lesson → quant → takeaway → end`

| Vai | Câu hỏi đoạn trả lời | Hình mặc định |
| --- | --- | --- |
| problem | Nhà đầu tư thật gặp chuyện gì? (tình huống cụ thể) | chữ lớn |
| mechanism | Cơ chế tâm lý nào? (kèm "còn tranh cãi" nếu đúng vậy) | chart mô hình (ví dụ hàm giá trị) |
| evidence | Nghiên cứu nào, mẫu nào, thấy gì? | thẻ nghiên cứu: tác giả, năm, tạp chí, phát hiện |
| implication | Hệ quả tài chính, tính bằng mô hình | 3D / chart |
| lesson | Làm gì khác đi, kiểm được | chữ lớn |
| quant | Dân quant đo/khử thiên kiến này thế nào | terminal số |

## Phân loại chủ đề

`catalog.json` — 19 chủ đề, 5 nhóm: Lợi ích & thua lỗ (loss aversion, prospect theory, disposition, bẫy gỡ hoà) ·
Cảm xúc & đám đông (FOMO, bán tháo, bầy đàn, cổ phiếu gây chú ý) · Tự tin & niềm tin (quá tự tin, xác nhận, biết trước,
neo giá) · Rủi ro & bất định (rủi ro cảm nhận, phóng đại xác suất nhỏ, ngại mơ hồ, kế toán tinh thần) · Sai lầm nhà đầu
tư cá nhân (tổng hợp, đa dạng hoá ngây thơ, thiên vị sân nhà). `ready` = có tập mẫu; `backlog` = cần brief.

## Quy trình nghiên cứu

1. `python pillar.py scaffold behavioral-finance <topic> --id <id>` → khung brief/factcheck/episode.
2. Researcher: tìm bài bình duyệt gốc → claims + facts + framework; nguồn mới vào ledger.
3. Fact-checker: mở từng nguồn, ghi verdict. Số không xác nhận được → `rejected_claims`.
4. Scriptwriter → `episodes/<id>.json`; `python pillar.py check …`; `python pillar.py make … --scale 0.5`.

## Kiểm chứng

- `min_source_tier: A` — claim `documented` cần bài bình duyệt hoặc dữ liệu gốc.
- Claim `disputed` → lời có "còn tranh cãi"/"có nguồn cho rằng"; `speculation` → "có thể"/"giả thuyết";
  `interpretation` → "có thể"/"nếu"/"cho thấy".
- Fact-check bắt buộc (`requires_factcheck: true`).

## QA riêng

Ngoài gate chung: `extra_banned` ("bí kíp tâm lý", "tư duy triệu phú"…). Không chẩn đoán người xem ("bạn bị tâm lý yếu").

## Tập mẫu đã dựng và kiểm

`episodes/bf-disposition-bias-lab.json` · brief `research/bf-disposition-bias-lab/` · mô hình `prospect_theory`.
