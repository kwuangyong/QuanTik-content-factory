# Kế hoạch thăm dò khách hàng QuanTik — 3 tuần

Bản nháp ngày 15/11/2026. Mục đích: trả lời **khách thật của QuanTik là ai, đến từ đâu, vì sao trả tiền**,
trước khi chọn một hướng nội dung để sản xuất hàng loạt.

## 1. Câu hỏi cần trả lời sau 3 tuần

1. Nhóm người nào **đăng ký và trả tiền** (không phải nhóm nào xem nhiều nhất)?
2. Họ đến từ kênh nào: TikTok, Facebook hay YouTube?
3. Họ mở QuanTik để giải quyết chuyện gì?

## 2. Ba giả thuyết đem ra thử

| Mã | Nhóm | Nỗi đau | Tính năng khớp |
| --- | --- | --- | --- |
| **A** | Lướt sóng (giữ mã vài ngày đến vài tuần) | Không biết nhìn mã nào, hay mua đuổi | Quét toàn sàn |
| **B** | Nắm giữ (giữ mã vài tháng trở lên) | Không biết mã đang cầm rủi ro cỡ nào | Phân tích Quant (phần Rủi ro, vùng giá mô phỏng) |
| **C** | Tò mò về quant (sinh viên, dân IT/data) | Muốn hiểu mô hình | Báo cáo chuyên sâu 16 nhóm chỉ tiêu |

Mỗi nhóm có 3 video, tổng cộng **9 video trong 3 tuần**.

## 3. Luật để phép thử công bằng

- Mỗi video đăng **cùng lúc lên TikTok, Facebook Reels, YouTube Shorts**, cùng khung giờ (ví dụ 19:30).
- 3 video mỗi tuần, thứ Hai, Tư, Sáu. **Đảo thứ tự nhóm mỗi tuần** để không nhóm nào luôn được ngày đẹp.
- Thời lượng 30–60 giây cho cả ba nhóm.
- Cùng một câu hỏi bình luận ở **mọi** video, để biết ai đang xem:
  > *Bạn thường giữ một mã bao lâu? Bình luận 1 = vài ngày, 2 = vài tuần, 3 = vài tháng trở lên, 4 = chưa đầu tư*
- Cùng một câu kết: *"Thử miễn phí tại quantik.io.vn"* (đối chiếu https://quantik.io.vn/plans trước khi đăng).
- Không chạy quảng cáo trả tiền cho video nào trong 3 tuần, để số liệu sạch.

## 4. Lịch đăng

| Tuần | Thứ Hai | Thứ Tư | Thứ Sáu |
| --- | --- | --- | --- |
| 1 (17–21/11) | A1 | B1 | C1 |
| 2 (24–28/11) | B2 | C2 | A2 |
| 3 (1–5/12) | C3 | A3 | B3 |
| 8/12 | Tổng kết, chốt hướng | | |

Song song trong cùng 3 tuần: phỏng vấn người dùng Pro (mục 7) và thêm câu hỏi lúc đăng ký (mục 8).

## 5. Chín video

Video sản phẩm dùng **mã bịa** (QTA, QTV…) và giao diện chạy local với API giả (`tutorial/`).
Mọi con số trên màn hình đi qua placeholder `{key}` do code tính. Thẻ cuối và caption có câu miễn trừ.

### Nhóm A — Lướt sóng

**A1. "Vì sao bạn hay mua đúng lúc mã vừa tăng xong?"** (kiểu: kinetic-text hoặc myth-buster)
- Hook: *"Bạn vào lệnh sau khi thấy mã tăng 3 phiên liền. Rồi nó đứng im. Không phải xui."*
- Ý chính: biến động đi thành cụm. Sau một đợt tăng mạnh, biến động thường còn cao, nên rung lắc cũng mạnh.
  Người mua đuổi thường vào đúng lúc rủi ro cao nhất.
- Chuyển sang sản phẩm: *"QuanTik đo mức biến động hiện tại của từng mã, để bạn biết mình đang vào lúc nào."*
- Nguồn trong repo: chủ đề GARCH / volatility clustering, dữ liệu mô phỏng.

**A2. "Trước giờ mở cửa, mình xem gì trong 30 giây"** (kiểu: tutorial, quay màn hình)
- Hook: *"Hơn 1.500 mã trên ba sàn. Mình không đọc hết. Mình xem bảng này."*
- Ý chính: mở Quét toàn sàn, xem bản công bố mới nhất, 5 mã xếp cao và **5 mã xếp cuối** theo bộ chỉ tiêu,
  bấm vào một cột để xem định nghĩa.
- Câu bắt buộc: *"Đây là xếp hạng theo bộ chỉ tiêu công bố, không phải khuyến nghị."*
- (Đếm lại số mã thật trên ba sàn trước khi dùng con số 1.500.)

**A3. "Mã đang được nhắc nhiều trên hội nhóm: kiểm tra trước khi vào"** (kiểu: tutorial)
- Hook: *"Cả nhóm đang bàn về một mã. Trước khi làm theo, mình mất 30 giây làm việc này."*
- Ý chính: gõ mã QTA vào Phân tích Quant, đọc kết luận, xu hướng, mức rủi ro.
- Kết: *"Bạn vẫn là người quyết định. QuanTik chỉ cho bạn thêm số liệu."*

### Nhóm B — Nắm giữ

**B1. "Lỗ 30%, cần tăng bao nhiêu để về bờ?"** (kiểu: whiteboard-math)
- Hook: *"Lỗ 30%. Tăng lại 30% là hoà? Không."*
- Ý chính: công thức về bờ = 1 / (1 − mức lỗ) − 1. Lỗ càng sâu, phần cần tăng càng lớn nhanh.
  Bảng 10% / 30% / 50% do code tính.
- Chuyển sang sản phẩm: *"Vì vậy biết trước mã mình cầm có thể sụt sâu cỡ nào quan trọng hơn đoán nó tăng bao nhiêu.
  QuanTik tính mức sụt sâu nhất trong quá khứ cho từng mã."*

**B2. "Mã bạn đang cầm rủi ro cỡ nào? Đọc trong 1 phút"** (kiểu: tutorial)
- Hook: *"Bạn biết mình lãi bao nhiêu. Nhưng bạn có biết mình đang chịu rủi ro bao nhiêu?"*
- Ý chính: mở Phân tích Quant với mã QTV, đọc phần rủi ro: biến động, mức sụt sâu nhất, VaR viết bằng lời thường.

**B3. "Vùng giá mô phỏng: đọc thế nào cho đúng"** (kiểu: tutorial kết hợp chart-story)
- Hook: *"Đây không phải dự báo giá. Và đó chính là lý do nó có ích."*
- Ý chính: Monte Carlo chạy hàng nghìn kịch bản và cho ra một vùng, không phải một điểm.
  Vùng rộng nghĩa là bất định cao. Đọc trên màn Phân tích Quant với mã bịa.

### Nhóm C — Tò mò về quant

**C1. "GARCH trong 60 giây"** (kiểu: code-reel, có sẵn trong pipeline)
- `cd pipeline && python batch.py --topics garch --styles code-reel`

**C2. "Sharpe cao hơn mà lãi ít hơn?"** (kiểu: myth-buster, đã có `episodes/sharpe-myth-example.json`)

**C3. "Bên trong một báo cáo Quant: 16 nhóm chỉ tiêu"** (kiểu: tutorial, phần chuyên sâu)
- Hook: *"Phần lớn app chỉ cho bạn một con số. Đây là 16 nhóm chỉ tiêu phía sau nó."*
- Ý chính: lướt nhanh HMM, GARCH, Monte Carlo trong báo cáo chuyên sâu, mỗi phần một câu.

## 6. Đo gì, ghi ở đâu

Ghi vào bảng sau **48 giờ** sau khi đăng (và cập nhật lại sau 7 ngày).

| Chỉ số | Vì sao quan trọng | Trọng số |
| --- | --- | --- |
| Tài khoản mới trong 48 giờ (xem trong admin) | Tín hiệu gần với tiền nhất | Cao nhất |
| Bình luận **hỏi thật** (nhắc tên mã, hỏi cách dùng, hỏi giá) | Ý định dùng thử | Cao |
| Tin nhắn riêng hỏi về sản phẩm | Ý định dùng thử | Cao |
| Lượt vào hồ sơ / bấm link | Quan tâm tới thương hiệu | Trung bình |
| Lượt lưu, chia sẻ | Nội dung có ích | Trung bình |
| Tỷ lệ xem hết | Hook và nhịp video | Thấp |
| Lượt xem | Chủ yếu do thuật toán | Thấp nhất |
| Phân bố câu trả lời 1/2/3/4 | **Ai đang xem** | Dùng để đọc kết quả |

Mẫu bảng (chép vào Google Sheets):

```
Video	Nhóm	Ngày đăng	Nền tảng	Xem	% xem hết	Lưu	Chia sẻ	Bình luận	Bình luận hỏi thật	Trả lời 1	Trả lời 2	Trả lời 3	Trả lời 4	Vào hồ sơ	Tin nhắn	Tài khoản mới 48h
A1	A	17/11	TikTok
A1	A	17/11	Facebook
A1	A	17/11	YouTube
```

Link trong hồ sơ từng nền tảng gắn sẵn UTM, phòng khi web hoặc Google Analytics đã ghi nhận:

```
https://quantik.io.vn/?utm_source=tiktok&utm_medium=social&utm_campaign=tham-do-t11
https://quantik.io.vn/?utm_source=facebook&utm_medium=social&utm_campaign=tham-do-t11
https://quantik.io.vn/?utm_source=youtube&utm_medium=social&utm_campaign=tham-do-t11
```

## 7. Phỏng vấn người dùng Pro (song song, tuần 1–3)

Mục tiêu: 5–10 người đang trả Pro, mỗi người 15 phút qua điện thoại hoặc Zalo. Có thể tặng thêm 1 tháng Pro để cảm ơn.

Tin nhắn mời (copy được):

```
Chào anh/chị, mình là người làm QuanTik. Cảm ơn anh/chị đã dùng gói Pro.
Mình muốn xin 15 phút để hỏi anh/chị dùng QuanTik thế nào, để làm sản phẩm tốt hơn.
Không bán hàng gì cả. Mình xin tặng thêm 1 tháng Pro để cảm ơn. Anh/chị tiện hôm nào ạ?
```

Câu hỏi:

```
1. Trước khi biết QuanTik, anh/chị chọn mã bằng cách nào?
2. Anh/chị thường giữ một mã bao lâu?
3. Lần gần nhất mở QuanTik là để làm gì? Lúc đó đang gặp chuyện gì?
4. Điều gì khiến anh/chị quyết định trả tiền?
5. Phần nào anh/chị hay xem nhất? Phần nào chưa từng bấm vào?
6. Nếu mai QuanTik đóng cửa, anh/chị sẽ dùng gì thay thế?
7. Anh/chị biết QuanTik từ đâu?
8. Anh/chị hay theo dõi ai, kênh nào, nhóm nào về chứng khoán?
```

Ghi lại **nguyên văn** những câu khách nói. Đó sẽ là hook cho video sau này.

## 8. Câu hỏi lúc đăng ký (cần sửa web, repo `QuanTik---Design`)

```
Bạn đầu tư theo kiểu nào?
○ Lướt sóng (vài ngày đến vài tuần)   ○ Nắm giữ (vài tháng trở lên)
○ Mới bắt đầu, đang tìm hiểu           ○ Tìm hiểu về quant/dữ liệu

Bạn biết QuanTik từ đâu?
○ TikTok   ○ Facebook   ○ YouTube   ○ Bạn bè giới thiệu   ○ Khác
```

Không bắt buộc trả lời, để không làm giảm tỷ lệ đăng ký. Đồng thời lưu `utm_source` nếu có trên link.

## 9. Đọc kết quả ngày 8/12

- **Chọn nhóm theo tài khoản mới và bình luận hỏi thật**, không theo lượt xem.
- Một nhóm chỉ "thắng" khi **ít nhất 2 trên 3 video** của nhóm đó tốt hơn hẳn. Một video lọt đề xuất không đủ kết luận.
- Đối chiếu với phỏng vấn: nếu người trả Pro kể giống nhóm thắng thì chốt. Nếu khác nhau, **tin phỏng vấn hơn**.
- Nhóm C nhiều view nhưng ít đăng ký: giữ khoảng 10–20% để xây uy tín, không làm trục chính.
- Không nhóm nào rõ ràng: chạy thêm 2 tuần với 2 nhóm dẫn đầu, mỗi nhóm thêm 3 video.

Kết quả là đầu vào cho file định vị `brand/positioning.md`: khách chính, thông điệp, vai trò từng kênh, CTA mặc định.

## 10. Việc cần làm trước ngày 17/11

- [ ] Chủ sản phẩm: đối chiếu trang /plans, xác nhận câu "thử miễn phí" còn đúng
- [ ] Chủ sản phẩm: gắn link UTM vào hồ sơ 3 nền tảng
- [ ] Chủ sản phẩm: lấy danh sách người trả Pro, gửi tin mời phỏng vấn
- [ ] Chủ sản phẩm: tạo Google Sheets theo mẫu ở mục 6
- [ ] Dựng A1, B1, C1 cho tuần 1 (dùng pipeline của repo này)
- [ ] (Nếu đồng ý) thêm câu hỏi đăng ký trên web
