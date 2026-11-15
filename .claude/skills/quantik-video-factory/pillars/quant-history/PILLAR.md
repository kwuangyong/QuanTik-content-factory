# Trụ cột 4a — Quant History & Legendary Minds (lịch sử quant)

**Mục tiêu:** kể chuyện người, quỹ và đột phá toán học trong tài chính mà không biến giai thoại thành sự kiện.
Worker: `workers/quant-historian.md`. Style: `history-story` (mặc định), chart-story, talking-head-script, carousel.

## Khung (bắt buộc)

`hook → context → conflict → breakthrough → consequences → lesson → takeaway → end`

| Vai | Nội dung | Hình mặc định |
| --- | --- | --- |
| context | bối cảnh, mốc thời gian | timeline (chấm tô màu theo trạng thái claim) |
| conflict | bài toán / xung đột | chữ lớn |
| breakthrough | đột phá, chạy mô hình liên quan | chart mô hình (Kelly, OU, Sharpe…) |
| consequences | hệ quả, thành công/thất bại | timeline đầy đủ |
| lesson | bài học quant còn đúng hôm nay | terminal số |

## Phân loại chủ đề

`catalog.json` — Con người (Thorp, Simons, Shannon, Markowitz, Black–Scholes–Merton, Bachelier) · Hãng & thất bại
(LTCM, quant quake 2007, lịch sử stat-arb, Knight Capital) · Tiến hoá giao dịch thuật toán. `knowledge/stories/` có
sẵn tư liệu LTCM, Medallion — chuyển dần sang brief + ledger.

## Mức tin cậy (hiện trên màn hình)

| status | Nhãn | Lời phải có |
| --- | --- | --- |
| documented | TƯ LIỆU | — (cần nguồn tier ≤ B) |
| self_reported | LỜI TỰ KỂ | "theo lời kể", "theo hồi ký", "ông kể"… |
| anecdote | GIAI THOẠI | "giai thoại", "tương truyền", "người ta kể" |
| disputed | CÒN TRANH CÃI | "còn tranh cãi", "nguồn khác" |
| speculation | SUY ĐOÁN | "có thể", "giả thuyết", "chưa có bằng chứng" |

Mọi năm/con số là `facts` có `source_id` (QA chặn năm không nguồn). Nhãn của một đoạn là trạng thái **yếu nhất**
trong các claim của đoạn đó.

## Tập mẫu

`episodes/qh-thorp-history-story.json` — Thorp: Kelly (1956), Beat the Dealer (1962), Beat the Market (1967), quỹ 1969,
và lời tự kể về công thức quyền chọn trước 1973 (nhãn LỜI TỰ KỂ). Mô hình `kelly`.
