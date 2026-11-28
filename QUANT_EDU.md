# Quant Edu · 100 tập

Lộ trình nội dung tiếng Việt về tài chính và giao dịch định lượng cho QuanTik, từ đọc dữ liệu thị trường đến xây chiến lược, kiểm định và giao dịch mô phỏng.

## Tiến độ

Chưa bắt đầu triển khai theo lộ trình này. Tập đầu tiên là **01**.

## Tiếp tục series

- Với yêu cầu **“Làm tiếp Quant Edu”**, tiếp tục tập đang dở được ghi ở mục Tiến độ. Khi không có tập đang dở, lấy tập có số nhỏ nhất chưa được đánh dấu. Nếu yêu cầu nêu số tập, dùng tập đó.
- Dùng quy trình QuanTik Video Factory và tra nhật ký các tập đã dựng để tận dụng nội dung có sẵn. Kịch bản Variance là tư liệu cho tập 23. Số thứ tự 01–100 bên dưới dùng để tra lộ trình. [Quy trình](.claude/skills/quantik-video-factory/SKILL.md) · [Nhật ký](.claude/skills/quantik-video-factory/knowledge/episodes.csv) · [Kịch bản Variance](.claude/skills/quantik-video-factory/episodes/04-variance-quiz.json)
- Khi bàn giao một tập, đánh dấu `- [x]` và gắn đường dẫn tới nội dung đã lưu. Nếu dừng giữa chừng, ghi số tập, phần đã làm, đường dẫn và bước tiếp theo ở mục Tiến độ.

## Tập 1–10 · Tư duy quant và cơ chế thị trường

Đặt giả thuyết có thể kiểm định, đọc giá và khối lượng, tính lợi suất kép và chọn chỉ số tham chiếu. Hiểu bán khống, đòn bẩy, giá bid/ask và cơ chế khớp lệnh.

- [ ] **01** Một quant làm gì khi có ý tưởng giao dịch mới?
- [ ] **02** Biến câu “cổ phiếu tăng mạnh sẽ còn tăng” thành giả thuyết có thể kiểm định
- [ ] **03** Nến giá và khối lượng cho biết gì về một phiên giao dịch?
- [ ] **04** Lãi 10% rồi lỗ 10%, vốn còn bao nhiêu?
- [ ] **05** Khi nào dùng lợi suất đơn và khi nào dùng lợi suất log?
- [ ] **06** Một chiến lược lãi 12% có thực sự thắng thị trường?
- [ ] **07** Bán khống tạo ra lãi và lỗ như thế nào?
- [ ] **08** Đọc giá bid, giá ask và tính chi phí từ chênh lệch mua bán
- [ ] **09** Bấm mua ngay thì lệnh thực sự khớp ở giá nào?
- [ ] **10** Dùng đòn bẩy 2x, một phiên giảm 5% ảnh hưởng đến vốn ra sao?

## Tập 11–20 · Dữ liệu thị trường và Python

Dùng Python và pandas để lấy, làm sạch, ghép và tái tạo dữ liệu. Xử lý cổ tức, chia tách, thời điểm công bố thông tin và thiên lệch sống sót.

- [ ] **11** Lấy bộ dữ liệu giá đầu tiên bằng Python
- [ ] **12** Đọc CSV với pandas và đặt ngày giao dịch làm chỉ mục
- [ ] **13** Xử lý dòng trùng, dữ liệu thiếu và mức giá bất thường
- [ ] **14** Ghép dữ liệu của nhiều tài sản có lịch giao dịch khác nhau
- [ ] **15** Giá điều chỉnh xử lý cổ tức và chia tách cổ phiếu ra sao?
- [ ] **16** Tạo nến 5 phút từ dữ liệu từng giao dịch
- [ ] **17** Dùng `shift()` để tính lợi suất của phiên kế tiếp
- [ ] **18** Ghép báo cáo tài chính vào dữ liệu giá theo ngày công bố
- [ ] **19** Kết quả thay đổi thế nào khi đưa cổ phiếu đã hủy niêm yết vào dữ liệu?
- [ ] **20** Viết một script có thể dựng lại toàn bộ bộ dữ liệu nghiên cứu

## Tập 21–30 · Xác suất và thống kê cho quant

Đo kỳ vọng lãi lỗ, độ phân tán và quan hệ giữa các tài sản. Dùng khoảng tin cậy, p-value và Monte Carlo để đánh giá kết quả và hiểu vai trò của ngẫu nhiên.

- [ ] **21** Thắng 7 trên 10 lệnh thì kỳ vọng lãi bao nhiêu?
- [ ] **22** Một phiên tăng đột biến ảnh hưởng thế nào đến trung bình và trung vị?
- [ ] **23** Dùng độ lệch chuẩn để đo mức dao động của lợi suất
- [ ] **24** Những phiên cực đoan xuất hiện bao nhiêu lần so với dự báo của phân phối chuẩn?
- [ ] **25** Tương quan giữa hai tài sản thay đổi thế nào theo giai đoạn?
- [ ] **26** Dùng hồi quy tuyến tính để ước tính mức nhạy của cổ phiếu với chỉ số
- [ ] **27** Tính khoảng tin cậy cho lợi suất trung bình
- [ ] **28** Đọc p-value khi kiểm định một tín hiệu giao dịch
- [ ] **29** Thử 100 tín hiệu thì có bao nhiêu tín hiệu trông có vẻ hiệu quả do may mắn?
- [ ] **30** Mô phỏng 1.000 chuỗi thắng thua bằng Monte Carlo

## Tập 31–40 · Chuỗi thời gian tài chính

Kiểm tra tính dừng, tự tương quan, mùa vụ và đồng liên kết. Dùng trung bình trượt, EWMA và AR(1) để mô tả xu hướng, biến động và thử dự báo.

- [ ] **31** Kiểm tra tính dừng của chuỗi giá và chuỗi lợi suất
- [ ] **32** Lợi suất hôm qua liên hệ thế nào với hôm nay qua tự tương quan?
- [ ] **33** Dùng trung bình trượt để quan sát xu hướng giá
- [ ] **34** Nhìn thấy các cụm biến động trên biểu đồ lợi suất
- [ ] **35** Ước tính biến động bằng EWMA để đặt trọng số cao hơn cho dữ liệu gần đây
- [ ] **36** Kiểm tra hiệu ứng ngày trong tuần trên dữ liệu thị trường
- [ ] **37** Dùng đồng liên kết để nghiên cứu chênh lệch giá giữa hai tài sản
- [ ] **38** Phân nhóm các giai đoạn thị trường biến động cao và thấp
- [ ] **39** Thử dự báo lợi suất phiên tới bằng mô hình AR(1)
- [ ] **40** So dự báo biến động với mốc đơn giản là mức biến động kỳ trước

## Tập 41–50 · Xây tín hiệu và chiến lược

Xây tín hiệu theo xu hướng, momentum, phá đỉnh, hồi quy về trung bình và giao dịch theo cặp. Xếp hạng cổ phiếu theo các yếu tố định giá và chất lượng, sau đó chuyển tín hiệu thành quy tắc giao dịch.

- [ ] **41** Theo xu hướng bằng giao cắt hai đường trung bình
- [ ] **42** Xếp hạng cổ phiếu bằng momentum 12 tháng
- [ ] **43** Dùng z-score để tìm điểm vào cho chiến lược hồi quy về trung bình
- [ ] **44** Xây một giao dịch theo cặp bằng chênh lệch giá đã điều chỉnh
- [ ] **45** Đặt quy tắc mua khi giá vượt đỉnh 20 phiên
- [ ] **46** Xây tín hiệu value từ các chỉ số định giá
- [ ] **47** Dùng ROE và tỷ lệ nợ để xếp hạng chất lượng doanh nghiệp
- [ ] **48** Gộp momentum, value và quality vào cùng một bảng điểm
- [ ] **49** Xây danh mục long–short từ hai đầu bảng xếp hạng
- [ ] **50** Viết quy tắc vào lệnh, thoát lệnh và tái cân bằng thành code

## Tập 51–60 · Backtest và kiểm định chiến lược

Mô phỏng tín hiệu và khớp lệnh theo đúng dòng thời gian, tính chi phí rồi đọc CAGR, Sharpe và drawdown. Đánh giá độ ổn định bằng kiểm định ngoài mẫu, walk-forward và thay đổi tham số hoặc chi phí.

- [ ] **51** Viết backtest đầu tiên cho một tín hiệu mua bán
- [ ] **52** Mô phỏng đúng thời điểm phát tín hiệu, đặt lệnh và khớp lệnh
- [ ] **53** Phát hiện lỗi nhìn trước dữ liệu bằng cách cắt ngắn chuỗi lịch sử
- [ ] **54** Tính phí, thuế và trượt giá vào từng giao dịch
- [ ] **55** Dựng sổ lệnh, số dư tiền mặt và giá trị danh mục theo phiên
- [ ] **56** Đọc báo cáo backtest qua CAGR, Sharpe và max drawdown
- [ ] **57** Giữ riêng một giai đoạn ngoài mẫu để kiểm định chiến lược
- [ ] **58** Chạy walk-forward với tham số được cập nhật theo từng kỳ
- [ ] **59** Đổi tham số một chút thì kết quả backtest thay đổi bao nhiêu?
- [ ] **60** Kiểm tra lợi nhuận khi chi phí giao dịch tăng gấp đôi

## Tập 61–70 · Danh mục và quản trị rủi ro

Phân bổ vốn, tính quy mô vị thế và tái cân bằng. Đo đóng góp rủi ro, độ nhạy với thị trường và mức lỗ trong kịch bản xấu bằng beta, VaR, Expected Shortfall và stress test.

- [ ] **61** Chia vốn theo tỷ trọng đều và theo mức biến động
- [ ] **62** Tính kích thước vị thế từ ngân sách rủi ro cho mỗi lệnh
- [ ] **63** Một tài sản mới làm rủi ro danh mục thay đổi thế nào?
- [ ] **64** Tìm danh mục phương sai tối thiểu với giới hạn tỷ trọng
- [ ] **65** Dùng risk parity để cân bằng đóng góp rủi ro giữa các tài sản
- [ ] **66** Tái cân bằng theo lịch và theo ngưỡng lệch tỷ trọng
- [ ] **67** Dùng beta để ước tính tác động của một nhịp giảm thị trường lên danh mục
- [ ] **68** Đo rủi ro thua lỗ bằng VaR và Expected Shortfall
- [ ] **69** Stress test danh mục qua một đợt thị trường giảm mạnh trong lịch sử
- [ ] **70** Đặt giới hạn đòn bẩy, mức tập trung và drawdown cho danh mục

## Tập 71–80 · Hợp đồng tương lai và quyền chọn

Tính lãi lỗ, ký quỹ và phòng hộ với futures. Vẽ đồ thị lãi lỗ quyền chọn, định giá bằng cây nhị phân và Black–Scholes, đọc Greeks và điều chỉnh phòng hộ Delta.

- [ ] **71** Lãi lỗ hợp đồng tương lai được ghi nhận mỗi ngày như thế nào?
- [ ] **72** Khi nào vị thế futures bị yêu cầu bổ sung ký quỹ?
- [ ] **73** Nối dữ liệu futures qua các kỳ đáo hạn để tạo chuỗi giá liên tục
- [ ] **74** Tính số hợp đồng futures cần để phòng hộ danh mục cổ phiếu
- [ ] **75** Vẽ đồ thị lãi lỗ của quyền chọn call và put khi đáo hạn
- [ ] **76** Định giá quyền chọn bằng cây nhị phân hai bước
- [ ] **77** Khám phá các đầu vào của mô hình Black–Scholes
- [ ] **78** Đọc Delta, Gamma, Vega và Theta của một vị thế quyền chọn
- [ ] **79** Suy ra biến động hàm ý từ giá quyền chọn
- [ ] **80** Thực hành điều chỉnh vị thế phòng hộ Delta khi giá thay đổi

## Tập 81–90 · Machine learning cho giao dịch

Tạo nhãn và đặc trưng, so sánh hồi quy logistic với gradient boosting và chia tập theo thời gian để tránh rò rỉ dữ liệu. Chuyển dự báo thành tín hiệu, đánh giá lợi nhuận sau phí và theo dõi chất lượng dự báo.

- [ ] **81** Tạo nhãn tăng hoặc giảm từ lợi suất của 5 phiên tới
- [ ] **82** Tạo đặc trưng từ giá, khối lượng và biến động
- [ ] **83** Huấn luyện mô hình hồi quy logistic làm mốc đánh giá
- [ ] **84** Thử gradient boosting trên cùng bộ dữ liệu
- [ ] **85** Ngăn rò rỉ dữ liệu khi chuẩn hóa đặc trưng
- [ ] **86** Chia tập theo thời gian khi các cửa sổ tính nhãn chồng lấn
- [ ] **87** Chuyển xác suất dự báo thành quyết định đặt lệnh
- [ ] **88** Đo tác động của độ chính xác dự báo lên lợi nhuận sau phí
- [ ] **89** Đảo thứ tự từng đặc trưng để xem mô hình dựa vào yếu tố nào
- [ ] **90** Theo dõi sự thay đổi của dữ liệu đầu vào và chất lượng dự báo theo thời gian

## Tập 91–100 · Thực thi lệnh và dự án cuối

Đọc độ sâu sổ lệnh, ước tính giá khớp, chia lệnh và đo chi phí thực thi. Dự án cuối là danh mục cổ phiếu momentum tái cân bằng hằng tháng, có backtest sau phí, giao dịch mô phỏng và báo cáo tái lập kết quả.

- [ ] **91** Đọc độ sâu sổ lệnh để ước tính giá khớp của một lệnh lớn
- [ ] **92** Đo tác động lên giá khi tăng kích thước lệnh
- [ ] **93** Chia lệnh lớn theo lịch TWAP hoặc theo khối lượng VWAP
- [ ] **94** Chuyển tỷ trọng mục tiêu thành số lượng đặt lệnh theo quy mô lô
- [ ] **95** Chạy paper trading và đối chiếu tín hiệu với lịch sử lệnh mô phỏng
- [ ] **96** Đo chi phí thực thi từ mức giá tại thời điểm ra quyết định
- [ ] **97** Xử lý tình huống nguồn giá gián đoạn hoặc lệnh bị từ chối
- [ ] **98** Dự án cuối · Xây danh mục momentum tái cân bằng hằng tháng
- [ ] **99** Dự án cuối · Backtest danh mục với chi phí thực thi và dữ liệu ngoài mẫu
- [ ] **100** Dự án cuối · Chạy thử danh mục và viết báo cáo để người khác có thể tái lập kết quả
