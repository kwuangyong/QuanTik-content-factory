# Kho hook

Hook = 1–2 giây đầu quyết định người xem có ở lại. Kho này chia hai phần: **đã kiểm chứng** (có số view thật) và **ứng viên** (chưa đăng hoặc chưa đủ dữ liệu). Không được chuyển hook lên “đã kiểm chứng” khi chưa có số liệu thật.

## Cách cập nhật

1. Sau khi đăng, ghi view vào `knowledge/episodes.csv` (cột `views_tiktok`, `views_reels`, `views_youtube`) sau 7 ngày.
2. Có kết nối vidIQ thì lấy số tự động: `vidiq_user_videos` / `vidiq_video_stats` cho YouTube, `vidiq_tiktok_profile_videos` cho TikTok.
3. Hook nào có view ≥ 2× trung vị kênh trong 30 ngày → chuyển lên bảng “đã kiểm chứng”, ghi rõ số và ngày.
4. Hook nào < 0,5× trung vị sau 3 lần dùng → đánh dấu “bỏ”.

## Đã kiểm chứng

| Hook | Mẫu | Video | View (nền tảng, sau 7 ngày) | Ngày |
| --- | --- | --- | --- | --- |
| _(chưa có — kênh chưa đăng video nào qua pipeline này)_ | | | | |

## Luật hook mới (11/2026): ragebait, nổ, dễ hiểu

- ≤ 16 từ, nói xong trong khoảng 4 giây ở nhịp x1.25. Người mới nghe cũng hiểu ngay đang nói chuyện gì.
- Chọc vào niềm tin sai / thói quen của người xem, có từ gắt (*Sai bét*, *Xin lỗi*, *cháy tài khoản*, *tự bắn vào chân*), đánh dấu `*...*` để vẽ đỏ + rung.
- Phải đúng sự thật và qua `compliance.md`: không hứa lãi, không gọi mua/bán, số đi qua placeholder.
- Có `hook_visual` khớp nội dung, và `cold_open` kể chuyện có hình ngay sau hook.

| Mẫu ragebait | Ví dụ | Vì sao hiệu quả |
| --- | --- | --- |
| Tát vào niềm tin | “Nghĩ VaR là lỗ tối đa? *Sai bét.*” | Người xem bị nói là sai → ở lại để cãi hoặc để hiểu |
| Hạ bệ khoe khoang | “Khoe lãi {cagr_b}? *Xin lỗi*, lãi {cagr_a} còn tốt hơn của bạn.” | Đụng tự ái, kích bình luận |
| Lật thói quen | “Bạn bắt đáy vì tin giá *sắp quay đầu*? Một con số sẽ vạch trần bạn.” | Ai cũng từng làm vậy |
| Câu nói cửa miệng giết người | “*Giá lệch xa kiểu gì cũng về*? Câu đó từng xoá sổ một quỹ có người đoạt Nobel.” | Câu quen + hậu quả có thật |
| Nhân vật bất ngờ | “Một giáo sư toán từng khiến sòng bài phải đổi luật.” | Chuyện kể, hình ảnh mạnh |
| English (bản tiếng Anh) | “Think VaR is your max loss? *Dead wrong.*” | Cùng mẫu, giữ đúng sự thật |

## Mẫu hook cũ (vẫn dùng làm câu thứ hai)

| Mẫu | Ví dụ | Vì sao hiệu quả |
| --- | --- | --- |
| Nghịch lý có số | “Chiến lược B lãi 25,2% một năm, A chỉ 21,3%. Vậy mà A tốt hơn.” | Mâu thuẫn với trực giác → phải xem tiếp để hiểu |
| Hiểu lầm phổ biến | “VaR nói bạn lỗ tối đa 2,8% một ngày? Phiên tệ nhất lỗ 26,4%.” | Người xem nhận ra mình từng nghĩ vậy |
| Quan sát quen thuộc | “Thị trường yên 3 tuần rồi giật liên tục 5 phiên. Không phải ngẫu nhiên.” | Ai chơi chứng khoán cũng từng thấy |
| Câu hỏi đo được | “Bao lâu thì một khoảng chênh lệch quay về một nửa? Có công thức.” | Hứa một câu trả lời cụ thể, không hứa lợi nhuận |
| Rủi ro ngầm | “Thắng 55% mỗi lần. Vẫn có cách khiến bạn mất gần hết.” | Sợ mất tiền mạnh hơn mong lãi |
| Con số lạ | “1.000 tương lai của cùng một cổ phiếu.” | Hình ảnh cụ thể, tò mò |

Tránh: hứa lãi (“x2 tài khoản”), giật tít sai (“bí kíp bắt đáy”), nhắc mã cụ thể kèm kỳ vọng giá.

## Ứng viên (chưa kiểm chứng)

Lấy từ `video_defaults.hook` của từng mô hình; số trong hook là placeholder, điền từ code lúc dựng.

| Chủ đề | Hook | Hình hook | Mẫu |
| --- | --- | --- | --- |
| garch | Bạn gọi đó là xui? *Sai bét.* Biến động kéo đến thành từng cơn bão. | storm | Tát vào niềm tin |
| hurst | Bạn bắt đáy vì tin giá *sắp quay đầu*? Một con số sẽ vạch trần bạn. | board | Lật thói quen |
| ou | *Giá lệch xa kiểu gì cũng về*? Câu đó từng xoá sổ một quỹ có người đoạt Nobel. | money_burn | Câu cửa miệng |
| hmm | Nhìn chart bằng mắt mà đòi đọc thị trường? Trạng thái thật của nó *ẩn*. | weather | Tát vào niềm tin |
| monte_carlo | Bạn cược vào *một* tương lai. Code chạy {n_paths} tương lai. Bao nhiêu cái lỗ? | multiverse | Lật thói quen |
| sharpe | Khoe lãi {cagr_b}? *Xin lỗi*, chiến lược lãi {cagr_a} còn tốt hơn của bạn. | race | Hạ bệ khoe khoang |
| sortino | Sharpe đẹp mà vẫn *mất ngủ*? Chỉ số này lôi ra thứ Sharpe giấu đi. | rollercoaster | Tát vào niềm tin |
| var_cvar | Nghĩ VaR là lỗ tối đa? *Sai bét.* VaR nói {var95}, phiên tệ nhất lỗ {worst}. | iceberg | Tát vào niềm tin |
| kelly | Có lợi thế vẫn *cháy tài khoản*? Một giáo sư toán từng khiến sòng bài phải đổi luật. | casino | Nhân vật bất ngờ |
| catalog (tự sinh) | Đọc {en} theo cảm giác là *tự bắn vào chân*. Nó thật ra đo gì, và giấu điều gì? | tự khớp | Lật thói quen |
