# Visual Director

## Trách nhiệm

Chọn style và hình cho từng đoạn sao cho hình **chứng minh** lời, không trang trí.

| Trụ cột | Style mặc định | Hình theo vai (mặc định trong template) |
| --- | --- | --- |
| 2 Behavioral | `bias-lab` | problem: chữ · mechanism: chart mô hình · evidence: thẻ nghiên cứu (citation) · implication: 3D · lesson: chữ · quant: terminal số |
| 3 Market | `market-brief` | asof: terminal · breadth: gauge · liquidity: terminal · sectors: bar nhóm ngành · regime: terminal/giới hạn · interpretation: chữ · scenarios: 3 thẻ · risk: chữ |
| 4a History | `history-story` | context/consequences: timeline tô màu theo trạng thái claim · conflict: chữ · breakthrough: chart mô hình · lesson: terminal |
| 4b Decision | `decision-lab` | setup/intuition: chữ · math: code + kết quả · simulation: chart · analogy: hai cột GIỐNG/KHÁC · lesson: 3D |

Đổi hình một đoạn bằng `"visual": {"kind": "<statement|chart|surface|code|terminal|citation|timeline|split|scenarios|gauge|sectors>", ...}`
(`rows` cho terminal/code, `title` cho chart, `upto` cho timeline). Hình không có dữ liệu (ví dụ chart khi mô hình không
có) tự lùi về `statement`.

## Ràng buộc nhận diện

- Màu, font, vùng an toàn: `brand/identity.md`. Mỗi đoạn trụ cột mới luôn có nhãn vai + nhãn trạng thái
  (TƯ LIỆU / LỜI TỰ KỂ / GIAI THOẠI / CÒN TRANH CÃI / SUY ĐOÁN / QUAN SÁT / MÔ HÌNH / NHẬN ĐỊNH) và chân trang nguồn.
- Không ảnh/meme có bản quyền; không ảnh chân dung nhân vật lịch sử khi chưa có giấy phép.
- Muốn style hẳn mới: `styles/<tên>/` với `spec.md` + `template.py` (xem `SKILL.md` mục Mở rộng).
