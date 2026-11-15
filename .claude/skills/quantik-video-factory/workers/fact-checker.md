# Fact-checker

**Mọi trụ cột nghiên cứu** (2, 4a, 4b; trụ cột 3 kiểm bằng dữ liệu và `check_market`).

## Trách nhiệm

Kiểm từng claim trong brief **với nguồn gốc**, không với trí nhớ, rồi ghi phán quyết. Gate tự động
`qa/check_sources.py` từ chối render nếu thiếu phán quyết, phán quyết không đạt, hoặc trạng thái lệch.

## Đầu vào → đầu ra

`research/<id>/brief.json` → `research/<id>/factcheck.json` (schemas/factcheck.schema.json):

```json
{"brief": "research/<id>/brief.json", "checked": "YYYY-MM-DD", "checker": "tên",
 "verdicts": [{"claim": "c_odean", "verdict": "verified", "evidence": ["doi:…", "https://…"], "note": "…"}]}
```

`verdict`: `verified` · `verified_with_correction` (sửa claim/brief cho khớp, ghi note) · `status_changed` (bắt buộc ghi
`status` mới, ví dụ hạ `documented` → `self_reported`) · `unverified` · `rejected`.

## Quy trình mỗi claim

1. Mở nguồn trong ledger (DOI/ISBN/URL). Tìm đúng chỗ (`locator`). Nguồn thứ cấp chỉ để định hướng.
2. Số: khớp đến chữ số được nói; đơn vị, giai đoạn, trước/sau phí.
3. Trạng thái: chỉ có lời nhân vật → `self_reported`; nguồn mâu thuẫn → `disputed`; không truy được → `anecdote`/bỏ.
4. Tier: `documented` cần nguồn đạt `min_source_tier` của trụ cột.
5. Ghi bằng chứng (URL/DOI đã mở) vào `evidence` và vào `verified_by` của nguồn trong ledger.
6. Claim không xác nhận được: chuyển vào `rejected_claims` của brief để không ai dùng lại.

## Ví dụ thật từ lần chạy đầu (2026-11-15)

- Odean (1998): PGR 0,148 / PLR 0,098 — xác nhận qua CFA Digest và trang DOI → `verified`.
- "Mã đã bán vượt mã giữ lại 3,41%" — không tìm được nguồn xác nhận → `rejected`, bỏ khỏi kịch bản.
- Thorp có công thức tương đương Black–Scholes trước 1973 — chỉ có lời kể của ông và nguồn thứ cấp nhắc lại →
  `status_changed` → `self_reported`; lời đọc phải có "theo lời kể".
- Princeton/Newport lập năm 1969 — đa số nguồn ghi 1969, một nguồn ghi 1974 → `verified_with_correction`, ghi chú mâu thuẫn.

## Giới hạn

Gate tự động chỉ kiểm **truy vết và kỷ luật trạng thái**; nó không đọc được tài liệu. Phán quyết `verified` là trách
nhiệm của người/agent ký tên trong `checker`. Không tự kiểm claim do chính mình vừa viết mà không mở lại nguồn.
