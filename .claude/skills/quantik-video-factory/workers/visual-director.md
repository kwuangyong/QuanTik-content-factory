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

## Ảnh người, hãng, sự kiện

Mọi người/hãng/sự kiện được nhắc trong lời hoặc chữ trên màn hình phải có trong `entities` của episode, kèm `image`
(id trong `knowledge/images/ledger.json`) được hiện ở ít nhất một cảnh, hoặc `waiver` nêu lý do (ví dụ "chỉ nhắc như
tên khái niệm 'cân bằng Nash'"). `qa/check_images.py` tự phát hiện họ tên tác giả trong ledger nguồn và tên riêng hai từ
("Jay Regan") rồi chặn nếu chưa khai báo.

Cách đặt ảnh: `"visual": {"kind": "image", "image": "<id>"}` (ảnh lớn + chú thích), `timeline[].image` (ảnh nhỏ cạnh
mốc), `"visual": {"kind": "citation", "image": "<id>"}` (ảnh tác giả trên thẻ nghiên cứu). Lấy ảnh: thử
`python pipeline/images.py search "<tên>"` trên Wikimedia Commons; chỉ giấy phép tự do; không có thì
`images.py person/event/cards` (ảnh minh hoạ). Chi tiết: `knowledge/images/README.md`.

## Cho dễ xem

- Cảnh chỉ có chữ tự có **biểu tượng** theo vai (bảng `ICONS` trong `template.py` của từng style); đổi cho một đoạn bằng
  `"visual": {"kind": "statement", "icon": "<tên>"}`. Danh sách: `python pipeline/pictos.py <file.png>` (18 biểu tượng:
  book, building, bulb, cards, chart_up, chart_down, check, coins, dice, eye, gear, hourglass, magnifier, people, scale,
  shield, target, warning).
- Chữ lớn hiện từng từ; biểu tượng bật lên rồi trôi nhẹ; phụ đề sáng từng từ theo giọng (karaoke); chuyển cảnh mờ dần
  0,25 giây; chấm tiến trình chương ở góc phải cho biết đang ở đoạn nào. Tất cả tự động, không cần khai báo.
- Mỗi đoạn nên có `screen` ngắn (≤ 10 từ) khác với lời đọc: màn hình nói ý chính, giọng giải thích.

## Ràng buộc nhận diện

- Màu, font, vùng an toàn: `brand/identity.md`. Mỗi đoạn trụ cột mới luôn có nhãn vai + nhãn trạng thái
  (TƯ LIỆU / LỜI TỰ KỂ / GIAI THOẠI / CÒN TRANH CÃI / SUY ĐOÁN / QUAN SÁT / MÔ HÌNH / NHẬN ĐỊNH) và chân trang nguồn.
- Không ảnh/meme có bản quyền; không ảnh chân dung nhân vật lịch sử khi chưa có giấy phép.
- Muốn style hẳn mới: `styles/<tên>/` với `spec.md` + `template.py` (xem `SKILL.md` mục Mở rộng).
