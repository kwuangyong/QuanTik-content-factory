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

## Khi số liệu là sự kiện lịch sử

Số không do code tính (ví dụ LTCM lỗ bao nhiêu) phải nằm trong `facts` của episode, mỗi số kèm `source`. Ưu tiên nguồn gốc: báo cáo chính thức, sách đã xuất bản, báo tài chính lớn. Nếu không chắc, bỏ số đó.

## Nội dung tiếng Anh (IG / YouTube Shorts quốc tế)

Episode có `"lang": "en"` dùng cùng ranh giới như trên. Cụm cấm tiếng Việt vẫn quét, cộng thêm danh sách dưới đây.
Chủ đề tài chính cá nhân (tiết kiệm, lãi kép, độc lập tài chính) chỉ minh hoạ cơ chế bằng mô phỏng có giả định ghi rõ,
không hứa "nghỉ hưu sớm", không chỉ sản phẩm đầu tư cụ thể.

## Banned phrases

```text
buy now
sell now
guaranteed returns
guaranteed return
guaranteed profit
guaranteed income
risk-free returns
can't lose
cannot lose
never lose
100% win
double your account
double your money
get rich quick
to the moon
price target
strong buy
must buy
quit your job now
retire early guaranteed
financial advice from
```

## Disclaimer

```text
Educational content about quantitative methods, not financial advice or a recommendation to buy or sell any security. Model results depend on assumptions and data; past performance does not guarantee future results.
```
