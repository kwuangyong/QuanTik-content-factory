# Nhận diện QuanTik cho video

## Màu (đồng bộ `frontend/src/app/globals.css`, theme tối)

| Vai trò | Mã | Dùng cho |
| --- | --- | --- |
| Nền | `#080d0b` | nền video, có lưới mờ 60px |
| Bề mặt | `#0d1913` | panel, chart |
| Viền | `#294337` | khung panel, trục |
| Chữ | `#edf4ef` | chữ chính |
| Chữ phụ | `#a6b9ad` | nhãn, ghi chú |
| Nhấn | `#ff914d` (cam) | hook, số quan trọng, đường chính của chart |
| Tăng | `#67d6a5` | giá/lợi suất dương, “thực ra” trong myth-buster |
| Giảm | `#f08088` | giá/lợi suất âm, “bạn nghĩ” trong myth-buster |
| Trung tính | `#e3c16c` | số trong phụ đề, chú thích |

Màu luôn đi cùng chữ hoặc số (giống quy tắc giao diện web): không để người mù màu phải đoán.

## Chữ

- Thương hiệu dùng **IBM Plex Mono** cho số, mã và code. Thả `IBMPlexMono-Regular.ttf` và `IBMPlexMono-Bold.ttf` (giấy phép OFL) vào `brand/assets/fonts/` thì pipeline tự dùng; chưa có thì dùng JetBrains Mono.
- Chữ thường: Be Vietnam Pro nếu có trong `brand/assets/fonts/`, không thì Inter. Cả hai đủ dấu tiếng Việt.
- Hook 80–96px, đậm nhất. Phụ đề 42px đậm, tối đa 2 dòng. Chữ nhỏ nhất trên video 20px.

## Logo

`brand/assets/logo.jpg` (lấy từ `frontend/public/quantik-logo.jpg`). Góc trên trái mỗi cảnh, to ở thẻ cuối.

## Khung hình

- 1080×1920, 30 fps, H.264 + AAC.
- Vùng an toàn (tránh nút và caption của TikTok/Reels/Shorts): x 60–940, y 170–1500. Mọi chữ phải nằm trong vùng này; `qa/check_format.py` bắt lỗi.
- Phụ đề luôn bật (nhiều người xem không bật tiếng).

## Hình ảnh thật & B-roll (bắt buộc cho MỌI video)

Chủ sản phẩm yêu cầu cố định (11/2026): video phải có **nhiều sự vật, hình ảnh, con người, ảnh thật**, không chỉ
chữ và chart trên nền tối.

- **Nguồn:** Pexels (ảnh + video dọc, chất lượng cao; cần `PEXELS_API_KEY`) → Openverse (ảnh thật, không cần key).
  `pipeline/broll.py` tìm, tải, lưu cache `social-output/_broll/`.
- **Giấy phép được dùng:** Pexels License; Openverse chỉ CC0, PDM, CC BY. **Không** CC BY-SA (ép cả video theo BY-SA),
  **không** NC (kênh thương hiệu là thương mại), **không** ND (mình cắt/zoom ảnh).
- **Ghi nguồn:** dòng nhỏ trên ảnh, một dòng "Ảnh/Images:" trong caption, đầy đủ ở `credits.md`. Pipeline tự làm.
- **Cách dựng:** mọi cảnh trừ thẻ cuối có ảnh. Ảnh dọc phủ kín khung; ảnh ngang/vuông nằm nét ở nửa trên, nền là bản
  phóng mờ của chính ảnh; zoom chậm (Ken Burns); phủ tối để chữ đọc được. Chart/code vẫn đè lên trên.
- **Chọn ảnh:** episode ghi `"broll"`: danh sách từ khoá tiếng Anh (xoay vòng theo cảnh) hoặc `{tên cảnh: từ khoá}`.
  Không ghi thì dùng từ khoá mặc định theo mô hình (`TOPIC_QUERIES`) + người/nơi chốn chung. Từ khoá nên là vật
  cụ thể và người ("poker chips", "trader at desk", "storm clouds"), không là khái niệm trừu tượng.
- **Tránh:** người nổi tiếng, logo/thương hiệu thật, bảng giá có mã thật, cảnh tai nạn/bệnh tật, ảnh gợi ý người
  trong ảnh đang dùng hay khuyên dùng QuanTik.
- **Hình hoạ tự vẽ (linh hoạt, nhất là video tiếng Anh):** `pipeline/illustrations.py` vẽ bằng code các hình hoạt hoạ
  phẳng theo màu thương hiệu: `chips` (chip poker), `dice`, `cards`, `coins`, `storm`, `brain`, `person` (người ngồi
  laptop), `paths` (nhiều ngả tương lai), `scale` (cân), `hourglass`, `target` (bia phi tiêu). Không cần giấy phép hay
  ghi nguồn. Video tiếng Anh tự xen hình hoạ vào mỗi cảnh thứ ba (bắt đầu từ cảnh 2); episode chọn bằng
  `"art": ["chips", "cards"]` hoặc `{tên cảnh: "brain"}`, tắt bằng `"art": false`. Video tiếng Việt chỉ có hình hoạ
  khi episode ghi `"art"`. Xem toàn bộ: `python pipeline/illustrations.py --sheet hinh-hoa.png`.
- **QA:** dưới 60% cảnh có hình (ảnh thật, B-roll hoặc hình hoạ), hoặc dưới 1/3 cảnh là **ảnh thật** → KHÔNG ĐẠT. Người duyệt xem `broll.jpg` (tờ ảnh đã chọn) trước khi đăng.
- **Video hướng dẫn sản phẩm** (`tutorial/`): chèn cảnh B-roll người dùng thật (người cầm điện thoại, ngồi trước
  laptop…) giữa các cảnh quay giao diện; chưa tự động, làm tay theo `tutorial/README.md`.

## Giọng văn: chuyên gia, dễ hiểu

- Nói như một người làm quant giải thích cho bạn thông minh nhưng không học tài chính. Câu ngắn, động từ mạnh, mỗi câu một ý.
- Luôn đi từ trực giác → công thức → con số do code tính → giới hạn của mô hình.
- Dùng “mình” và “bạn”. Thuật ngữ tiếng Anh giữ nguyên lần đầu kèm nghĩa Việt: “volatility, tức độ biến động”.
- Không hô hào, không hứa hẹn, không giật tít sai sự thật. Hook gây tò mò bằng nghịch lý có thật (“Sharpe cao hơn mà lãi ít hơn?”), không bằng lời hứa.
- Kết bằng một câu “mang về được” và giới hạn của mô hình.

Ví dụ tốt: “Biến động không rải đều. Nó đi thành cụm. GARCH đo đúng điều đó.”
Ví dụ tránh: “Bí kíp GARCH giúp bạn bắt đáy chuẩn 100%!”

## Sản phẩm (dùng cho CTA và video quảng bá)

Theo `README.md` và `docs/` của repo này, cập nhật đến 11/2026:

- **Dashboard**: bảng điện realtime từ AGR (HOSE, HNX, UPCoM), VN-INDEX, VN30, UPCOM, HNX-INDEX, bảng nhóm ngành.
- **Quét toàn sàn**: đọc bản công bố screening mới nhất, 5 mã điểm cao nhất và 5 mã nên tránh nhất theo thứ hạng screening, 34 cột chỉ tiêu có định nghĩa.
- **Phân tích Quant**: chọn mã → kết luận dễ đọc, xu hướng, vùng giá mô phỏng, rủi ro, mô hình 3D tương tác; phần chuyên sâu có 16 nhóm chỉ tiêu, HMM, GARCH, Monte Carlo.
- **Gói**: Free 30 ngày cho tài khoản mới (5 yêu cầu/ngày); QuanTik Pro 149.000đ/30 ngày (giá niêm yết 229.000đ), 20 yêu cầu/ngày — theo `docs/LAUNCH-OFFER-PRODUCTION.md` (ưu đãi từ 19/10/2026, chưa có ngày kết thúc). **Đối chiếu https://quantik.io.vn/plans trước khi nhắc giá.**
- Website: quantik.io.vn

CTA thẻ cuối theo nền tảng (`platforms/profiles.json`): Facebook = dùng thử sản phẩm, Reels · Shorts = lưu/chia sẻ, TikTok = câu dưới đây. CTA thẻ cuối mặc định khi không chọn nền tảng: “Thả tim và theo dõi QuanTik để học một kiến thức quant mỗi ngày” (`FOLLOW_CTA` trong `pipeline/batch.py`, tự áp dụng). Câu dẫn link tính năng (“Xem … tại quantik.io.vn”) chuyển xuống caption. Chỉ video quảng bá mới ghi `cta` riêng trong episode JSON. CTA quảng bá không nói “screening chọn cổ phiếu tốt cho bạn”; nói “screening xếp hạng theo bộ chỉ tiêu công bố”.
