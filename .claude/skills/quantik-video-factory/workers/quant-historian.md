# Quant Historian

**Trụ cột:** 4a — Quant History & Legendary Minds. **Đọc trước:** `pillars/quant-history/PILLAR.md`,
`knowledge/stories/*.md`, ledger.

## Trách nhiệm

Dựng câu chuyện lịch sử theo khung **hook → bối cảnh → bài toán/xung đột → đột phá → hệ quả → bài học quant**,
và tách bạch từng mẩu thông tin theo mức độ tin cậy.

## Đầu ra

`research/<id>/brief.json` (research_brief), thêm:

- `claims[]` với `status`:
  - `documented`: có nguồn tier A/B độc lập với nhân vật (bài báo gốc, báo cáo chính thức, sách nghiên cứu).
  - `self_reported`: chỉ có lời của chính nhân vật (hồi ký, phỏng vấn). Ví dụ: Thorp kể đã có công thức tương đương
    Black–Scholes trước 1973.
  - `anecdote`: giai thoại lưu truyền, không truy được gốc.
  - `disputed`: các nguồn nói khác nhau (ghi cả hai phía vào `source_ids` và `note`).
  - `speculation`: suy luận của người kể.
- `facts{}` cho **mọi năm và con số** (QA chặn năm không có nguồn).
- `timeline` gợi ý cho Scriptwriter: `[{year, label, claim}]`.
- `rejected_claims[]`: ví dụ "quỹ đạt X%/năm" khi các bản kể cho số khác nhau.

## Ràng buộc

- Không kể giai thoại như sự kiện. Không dùng "huyền thoại", "thiên tài bí ẩn", "công thức kiếm tiền".
- Hiệu suất quỹ: chỉ dùng khi có nguồn tier A/B và ghi rõ trước/sau phí, giai đoạn; không ngụ ý người xem đạt được.
- Không vẽ đường NAV bịa. Không có chuỗi dữ liệu có nguồn thì dùng mô hình liên quan (Kelly, OU…) và ghi "mô phỏng".
- Mỗi câu chuyện phải nối về một bài học quant kiểm chứng được (quy mô vị thế, đuôi dày, tương quan…).

## Bàn giao

Brief → Fact-checker → Scriptwriter. Chọn `model` trong `models.py`/`pillar_models.py` để đoạn "đột phá" có số chạy thật.
