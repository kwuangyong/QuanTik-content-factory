# Facebook — post là chính, Reels chỉ cập nhật thị trường

Chủ sản phẩm chốt 11/2026:

- **Post (trọng tâm):** **tính năng sản phẩm** (Quét toàn sàn, Phân tích Quant) và **chuyện hài về nghề** đầu tư
  chứng khoán. Đây là nơi chuyển đổi người đã follow thành người dùng.
- **Reels (phụ):** chỉ **cập nhật thị trường + kịch bản hành động**. Không làm Reels demo hay giáo dục trên Facebook.

**Người xem nhắm tới:** tầng SOM — nhà đầu tư muốn dùng quant làm công cụ chính. **Branding:** đầy đủ (logo, tên).
**Mã cổ phiếu trong mọi hình sản phẩm:** mã bịa (QTA, QTV…). **Mọi post/Reels:** câu miễn trừ, có hình ảnh thật hoặc
nhân vật/hình hoạ (luật 9, `brand/identity.md`).

## "Khuyến nghị" trên Facebook: làm được gì, không được gì

Tư vấn/khuyến nghị đầu tư chứng khoán là hoạt động phải có giấy phép (Luật Chứng khoán 2019), và Facebook giảm phân
phối/gỡ nội dung dạng "phím hàng". Vì vậy:

| Được | Không được |
| --- | --- |
| Ba **kịch bản có điều kiện** cho thị trường chung, mỗi kịch bản có điều kiện xác nhận và vô hiệu đo được | Gọi mua/bán/nắm giữ một mã, "điểm mua", "giá mục tiêu", "cắt lỗ tại" |
| **Hành động quản trị rủi ro chung** theo kịch bản: "kịch bản B thì ưu tiên giữ tỷ trọng tiền mặt, tránh dùng margin" | "Nên mua nhóm X", "cổ phiếu sẽ tăng", danh sách mã thật nên mua |
| Trạng thái thị trường đọc bằng số: độ rộng, thanh khoản, khối ngoại, regime | Đăng top mã thật từ Quét toàn sàn lên mạng xã hội (gần như khuyến nghị) |

Nếu sau này QuanTik có pháp nhân/đối tác được cấp phép tư vấn, cập nhật mục này và `brand/compliance.md` trước khi
đổi cách làm.

## Post — 4–5 bài/tuần

| Ngày | Dạng | Ví dụ | Làm bằng |
| --- | --- | --- | --- |
| Thứ 2 | **Nhiệt kế thị trường tuần** (ảnh 1080×1350) | trạng thái VN-Index, độ rộng, thanh khoản tuần qua, ba kịch bản tuần này; cuối bài "từng mã xem trong Phân tích Quant" | trụ cột `market-intelligence` (dữ liệu AGR thật) → ảnh tĩnh *(cần bước xuất post, xem Còn thiếu)* |
| Thứ 3 | **Tính năng: album 3–5 ảnh** | "Quét toàn sàn có gì": ảnh giao diện (mã bịa) + chú thích + nhân vật chỉ vào màn hình | ảnh chụp `tutorial/capture` + nhân vật `figures.py` *(cần style carousel sản phẩm)* |
| Thứ 4 | **Chuyện hài về nghề** (truyện tranh 2–4 khung) | "Vợ hỏi: tháng này lãi không? / Tôi: để anh xem Sharpe đã" · "Sếp và tôi khi thị trường xanh" · "Group chat lúc 14h45" · "Tôi sau khi đọc 3 bài phân tích trái ngược" | nhân vật + bong bóng thoại (`figures.py`, `pillar_scenes.draw_stage`) *(cần xuất ảnh truyện tranh)* |
| Thứ 5 | **Tính năng: một ảnh, một lợi ích** | "Gõ một mã → kết luận, rủi ro, vùng giá mô phỏng trong 30 giây" | ảnh chụp giao diện + caption |
| Thứ 6 | **Chuyện hài / câu hỏi mở** | "Bạn là kiểu nhà đầu tư nào khi VN-Index giảm 3%?" (4 nhân vật, mời bình luận) | nhân vật `STAGES` |
| Khi có | **Câu chuyện người dùng thật** (có đồng ý) | quy trình của họ, thời gian tiết kiệm; **không nói lãi** | làm tay |

### Chuyện hài về nghề — luật riêng

- Đùa về **tình huống và thói quen** của người chơi chứng khoán (FOMO, xem bảng điện giờ làm, group chat, "gồng lỗ"),
  không đùa về người thua lỗ thật, không chế giễu nhà đầu tư.
- Không lồng lời khuyên mua/bán vào câu đùa; cụm cấm vẫn áp dụng ("tất tay", "kèo thơm"… bị chặn).
- Kết bằng một dòng nối về sản phẩm khi hợp lý ("hoặc mở Quét toàn sàn, 1 phút là xong"), không bắt buộc mọi bài.
- Nhân vật luôn là hoạt hoạ phẳng của QuanTik; không dùng ảnh/meme người thật, không meme có bản quyền.

### Caption post

Câu đầu là điểm hài hoặc lợi ích → link quantik.io.vn ở dòng 2–3 (bài tính năng) → 3–5 hashtag → câu miễn trừ →
dòng ghi nguồn ảnh (nếu có ảnh CC BY).

## Reels — cập nhật thị trường, 2–3 video/tuần

Chỉ một dạng: **nhịp thị trường + ba kịch bản + hành động quản trị rủi ro chung**, dữ liệu thật có dấu thời gian.

```bash
cd pipeline && python pillar.py market produce            # fetch → analyze → editorial → script → video
```

Khung: `hook → asof → breadth → liquidity → sectors → regime → interpretation → scenarios → risk → takeaway → end`
(`pillars/market-intelligence/PILLAR.md`). QA `check_market` chặn đoạn trộn quan sát/nhận định, chặn tên mã và
"sẽ tăng/giảm". Không có dữ liệu mới → không dựng, nói rõ giới hạn.

- Hook nói trạng thái bằng số ("Độ rộng xấu nhất 3 tuần, thanh khoản giảm…"), không giật tít.
- Hình: chart thị trường + ảnh thật (sàn, người nhìn bảng điện) + nhân vật, theo luật gối đầu.
- CTA: "Theo dõi để nhận nhịp thị trường mỗi tuần" + link Phân tích Quant trong caption.

## Không làm trên Facebook

- Reels giải thích mô hình (đi TikTok), Reels demo tính năng (chuyển thành post), Reels giải trí (đi Instagram/YouTube).

## Còn thiếu (việc đóng gói tiếp theo)

1. **Xuất ảnh truyện tranh** 1080×1350 (2–4 khung, nhân vật + bong bóng thoại) cho chuyện hài về nghề.
2. **Style carousel sản phẩm**: ảnh giao diện từ `tutorial/capture` + chú thích + nhân vật, cho album tính năng.
3. **Xuất post nhiệt kế thị trường**: từ báo cáo của trụ cột thị trường ra một ảnh 1080×1350 + caption post.

## Đo

Post: bình luận, chia sẻ, click link, đăng ký trong tuần. Reels: lượt xem hết, follow trang.
