# Compliance — ranh giới nội dung QuanTik

QuanTik làm nội dung **giáo dục về phương pháp định lượng**. Video giải thích công thức, mô hình và rủi ro; không bảo người xem mua hay bán mã nào. Ở Việt Nam, tư vấn đầu tư chứng khoán là hoạt động phải có giấy phép (Luật Chứng khoán 2019), và nền tảng mạng xã hội cũng gỡ nội dung tài chính dạng hô hào. Vì vậy ranh giới dưới đây vừa là chuyện pháp lý, vừa giữ uy tín thương hiệu.

## Được làm

- Giải thích công thức, tham số, giả định và giới hạn của mô hình.
- Dùng dữ liệu mô phỏng có seed cố định, ghi rõ “Dữ liệu mô phỏng” trên màn hình.
- Dùng dữ liệu thật của một mã **để minh hoạ cách tính** (ghi nguồn, khoảng thời gian), kèm câu “không phải khuyến nghị”.
- So sánh khái niệm (“Sharpe cao chưa chắc lãi nhiều hơn”), kể chuyện lịch sử có nguồn (LTCM, Medallion).
- Giới thiệu tính năng QuanTik đúng như sản phẩm đang có (xem `identity.md`).

## Không được làm

- Gọi mua/bán/nắm giữ một mã cụ thể, đưa “điểm mua”, “giá mục tiêu”, “cắt lỗ tại”.
- Hứa hẹn lợi nhuận, tỷ lệ thắng, “x2 tài khoản”.
- Trình bày kết quả mô phỏng như dự báo giá thật của một mã.
- Dùng số không do code tính ra hoặc không có nguồn (qa/check_numbers.py chặn).
- Nhắc giá gói/ưu đãi mà chưa đối chiếu trang `/plans` hiện tại.
- Dùng nhạc, ảnh, meme template có bản quyền khi chưa có giấy phép.

## Cụm cấm

Quét không phân biệt hoa thường, theo cụm từ nguyên vẹn. Thêm cụm mới vào danh sách khi gặp.

```text
mua ngay
bán ngay
chắc chắn tăng
chắc chắn giảm
chắc chắn lãi
cam kết lợi nhuận
cam kết lãi
đảm bảo lợi nhuận
lãi chắc
bao lời
bao lãi
không thể thua
không bao giờ lỗ
100% thắng
thắng 100%
x2 tài khoản
x3 tài khoản
nhân đôi tài khoản
kèo thơm
kèo ngon
phím hàng
cổ phiếu sẽ tăng
cổ phiếu sẽ giảm
điểm mua
điểm bán
giá mục tiêu
khuyến nghị mua
khuyến nghị bán
nên mua
nên bán
all in
tất tay
làm giàu nhanh
siêu cổ phiếu
lợi nhuận khủng
```

## Câu miễn trừ

Luôn có trong caption và thẻ cuối video (pipeline tự chèn).

```text
Nội dung giáo dục về phương pháp định lượng, không phải khuyến nghị mua bán chứng khoán. Kết quả mô hình phụ thuộc giả định và dữ liệu; hiệu suất quá khứ không đảm bảo tương lai.
```

## Disclaimer (English)

Bản tiếng Anh của câu miễn trừ, dùng cho mọi video `"lang": "en"` (caption + thẻ cuối, pipeline tự chèn).

```text
Educational content about quantitative methods, not investment advice. Model results depend on assumptions and data; past performance does not guarantee future results.
```

## Chủ đề cờ bạc: poker, xổ số, roulette, trò cá cược

Poker, xổ số, roulette chỉ được dùng như **bài toán xác suất và ra quyết định**. Cờ bạc trái phép ở Việt Nam
(ngoài các hình thức được cấp phép), và nền tảng hạn chế nội dung cổ vũ cá cược. Vì vậy:

- Không nhắc tên site/app cá cược, sòng bạc cụ thể, mã giới thiệu, link.
- Không hướng dẫn "kiếm tiền từ poker/xổ số", không khoe tiền thắng, không gợi ý mức cược.
- Kết luận luôn nghiêng về rủi ro và giới hạn (nhà cái có lợi thế, phương sai, xác suất cực nhỏ).
- Episode đặt `"sensitive": "gambling"` → pipeline chèn thêm lưu ý dưới đây vào caption, thẻ cuối và dòng ghi chú
  trên màn hình.

## Lưu ý giáo dục: cờ bạc

```text
Nội dung giáo dục về xác suất và lý thuyết trò chơi. Không khuyến khích cờ bạc, cá cược dưới bất kỳ hình thức nào.
```

## Education note: gambling (English)

```text
Educational content about probability and game theory. It does not encourage gambling or betting of any kind.
```

## Banned phrases (English)

Cùng quy tắc với cụm cấm tiếng Việt; áp dụng cho mọi video (caption có thể lẫn hai thứ tiếng).

```text
buy now
sell now
guaranteed profit
guaranteed return
guaranteed win
risk-free
risk free
can't lose
cannot lose
never lose
sure win
sure thing
get rich quick
double your account
double your money
easy money
free money
price target
buy signal
sell signal
you should buy
you should sell
hot stock
to the moon
bet the house
sign up and play
deposit now
start betting
how to win at poker
beat the casino
```

## Khi số liệu là sự kiện lịch sử

Số không do code tính (ví dụ LTCM lỗ bao nhiêu) phải nằm trong `facts` của episode, mỗi số kèm `source`. Ưu tiên nguồn gốc: báo cáo chính thức, sách đã xuất bản, báo tài chính lớn. Nếu không chắc, bỏ số đó.
