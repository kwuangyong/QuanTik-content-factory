# Market Intelligence Analyst

**Trụ cột:** 3 — Market Intelligence & Research. **Đọc trước:** `pillars/market-intelligence/PILLAR.md`.

## Bốn giai đoạn, tách hẳn nhau

| Giai đoạn | Ai | Lệnh | Đầu ra |
| --- | --- | --- | --- |
| 1. Lấy dữ liệu | code | `python pillar.py market fetch [--history h.csv --history-manifest h.json]` | `social-output/_market/bundle-*/manifest.json` + file thô |
| 2. Phân tích | code | `python pillar.py market analyze` | `market_report.json` (observed / model / limitations) |
| 3. Nhận định | **Analyst** (agent) trên bản nháp code | `python pillar.py market editorial` rồi duyệt/sửa | `market_editorial.json` |
| 4. Kịch bản + dựng | code | `python pillar.py market script` → `pillar.py make <bundle>/episode.json` | episode, video |

`python pillar.py market produce` chạy cả bốn; dùng khi bản nháp nhận định đã đủ tốt.

## Vai của Analyst ở giai đoạn 3

Đầu vào: `market_report.json`. Đầu ra: `market_editorial.json` (schemas/market_editorial.schema.json):

- `interpretations[]`: mỗi câu một nhận định, có `based_on` là key trong report, có từ rào ("có thể", "nhiều khả năng",
  "cho thấy", "nếu"). Không câu nào thêm số không có trong report.
- `scenarios[]`: đúng ba — `bull`, `base`, `bear` — mỗi kịch bản có `confirmation[]` và `invalidation[]` **đo được
  bằng chính loại dữ liệu pipeline có** (độ rộng, mức chỉ số, thanh khoản), và `investor_actions[]` là hành động quản trị
  rủi ro chung (quy mô vị thế, đòn bẩy, điều kiện thoát), không nêu mã.
- `subjective_probability` chỉ khi có lý do; lời đọc phải gọi đó là "ước lượng chủ quan".
- Đổi `author` thành tên người/agent đã duyệt.

## Ràng buộc cứng (QA chặn)

- Không có dữ liệu → không có video. `data_status = unavailable/sample` thì editorial từ chối, check_market chặn.
- Dữ liệu cũ hơn phiên đã đóng gần nhất → chặn, trừ khi làm bản tổng kết `--allow-stale` và lời nói rõ ngày + "dữ liệu cũ".
- Không nhắc mã cổ phiếu cụ thể; không "sẽ tăng/giảm", "chắc chắn", "đáy rồi", "bắt đáy" (extra_banned của trụ cột).
- Regime chỉ khi có ≥ 200 phiên lịch sử có nguồn (CSV người dùng có manifest, hoặc lưu trữ snapshot cuối phiên tích
  luỹ qua nhiều lần fetch). Thiếu thì nói đó là giới hạn.
- Sự kiện vĩ mô: chỉ sự kiện đã công bố, có nguồn trong ledger; giải thích kênh tác động, không dự báo hệ quả như chắc chắn.

## Giới hạn hiện tại (nói thật)

- Nguồn dữ liệu tự động duy nhất là feed AGR (snapshot chỉ số + bảng giá). Không có API lịch sử → regime, biến động thực
  hiện, thanh khoản so trung bình 20 phiên chỉ có khi người dùng đưa CSV lịch sử hoặc khi đã tích luỹ đủ snapshot.
- Nhóm ngành là danh sách tham chiếu của QuanTik (`sector_map.json`), không phải ICB.
- Khối ngoại là **ước tính** (khối lượng ròng × giá bình quân).
