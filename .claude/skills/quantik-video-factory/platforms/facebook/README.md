# Facebook — nội dung sản phẩm, để chuyển đổi

**Vai trò:** biến người xem thành người dùng QuanTik (đăng ký Free → nâng Pro).
**Người xem nhắm tới:** tầng SOM — nhà đầu tư muốn dùng quant làm công cụ chính, tiết kiệm thời gian lọc mã,
ra quyết định có hệ thống. Họ không vào Facebook để học; họ cần thứ "ăn liền".
**Trọng tâm:** **Quét toàn sàn** và **Phân tích Quant**.

Video giáo dục (giải thích mô hình) **không đăng lên Facebook**: dạng này đã thử và không hiệu quả ở đây.
Vì vậy `batch.py --platform facebook` từ chối chạy với lời mặc định của chủ đề: phải có episode góc sản phẩm.

## Mỗi bài trả lời một câu

> *"Mở QuanTik ra thì mình làm được gì ngay, trong bao lâu, kết quả trông ra sao?"*

## Dạng nội dung

| Dạng | Ví dụ góc | Làm bằng | Độ dài |
| --- | --- | --- | --- |
| Demo một việc | "Buổi sáng mở Quét toàn sàn: 5 mã điểm cao nhất, 5 mã nên tránh nhất theo thứ hạng screening" | `tutorial/` — một luồng | 20–45s |
| Trước / sau | "Lọc mã bằng tay cả tối" → "đọc bảng đã xếp hạng theo 34 chỉ tiêu" | `tutorial/` hoặc `talking-head-script` | 25–45s |
| Một mã, một báo cáo | "Gõ một mã → kết luận dễ đọc, vùng giá mô phỏng, rủi ro, mô hình 3D" | `tutorial/` cảnh Phân tích Quant | 30–50s |
| Carousel tính năng | "Bảng Quét toàn sàn có gì: mỗi cột để làm gì" | ảnh chụp từ `tutorial/capture` (chưa có style tự động, xem *Còn thiếu*) | 5–7 slide |
| Hỏi đáp / phản biện | "Quant có quyết định thay mình không? Không. Nó làm việc này…" | `talking-head-script` | 45–60s |
| Hướng dẫn đầy đủ | đăng ký → quét → phân tích (ghim đầu trang) | `tutorial/run.sh` nguyên bản | 2–3 phút |

## Quy trình

1. **Chọn dạng và một tính năng** từ bảng trên. Một bài một tính năng.
2. **Viết lời theo lợi ích người dùng.**
   - 3 giây đầu là **kết quả trên màn hình** (bảng quét, báo cáo), không phải câu hỏi lý thuyết.
   - "bạn thấy ngay…", "khỏi phải…". Thuật ngữ chỉ dùng khi nó là nhãn trên giao diện.
   - Tính năng nói đúng như `brand/identity.md` mục Sản phẩm. Không nói "screening chọn cổ phiếu tốt cho bạn",
     nói "screening xếp hạng theo bộ chỉ tiêu công bố".
   - Lợi ích là thời gian, kỷ luật, đọc rủi ro trước khi quyết định. **Không** hứa kiếm tiền.
3. **Dựng.**
   - Video quay giao diện: làm theo `tutorial/README.md` (giao diện production local, API giả, **mã bịa** QTA, QTV…).
     Bản ngắn: chép `tutorial/beats.py` ra file mới, giữ các beat của một luồng, chạy `BEATS_FILE=… bash tutorial/run.sh <workdir>`.
   - Tự quay (talking-head): viết `episodes/<id>.json` có `"platform": "facebook"`, rồi
     ```bash
     cd pipeline && python batch.py --platform facebook --episode ../episodes/<id>.json
     ```
     Ví dụ episode:
     ```json
     {"id": "fb-quet-san-th-01", "platform": "facebook", "topic": "sharpe", "style": "talking-head-script",
      "title": "Quét toàn sàn: mở ra là có bảng xếp hạng",
      "hook": "Tối nay khỏi lọc mã bằng tay.",
      "beats": ["Mình mở Quét toàn sàn. Bảng screening mới nhất đã có sẵn.",
                "Trên cùng là năm mã điểm cao nhất, bên dưới là năm mã nên tránh nhất theo thứ hạng screening.",
                "Mỗi cột có định nghĩa. Bấm vào là biết chỉ tiêu đó đo gì.",
                "Thấy mã nào cần xem kỹ thì chuyển sang Phân tích Quant."],
      "takeaway": "Máy xếp hạng, bạn vẫn là người quyết định.",
      "caption": "Quét toàn sàn đọc bản công bố screening mới nhất và xếp hạng theo bộ chỉ tiêu công bố.",
      "cta": "Dùng thử miễn phí Quét toàn sàn tại quantik.io.vn"}
     ```
     `topic` chỉ để pipeline có B-roll; khi quay, chèn ảnh giao diện từ `tutorial/` thay cho B-roll quant.
     Style khác (`carousel`, `kinetic-text`, `code-reel`…) dựng cảnh công thức/chart nên bị `--platform facebook` từ chối.
4. **CTA thẻ cuối là dùng thử**, mặc định trong `profiles.json`: "Dùng thử miễn phí Quét toàn sàn và Phân tích
   Quant tại quantik.io.vn". Nhắc giá hay ưu đãi thì đối chiếu https://quantik.io.vn/plans trước.
5. **Caption Facebook:** câu đầu nêu việc làm được → link quantik.io.vn ở dòng 2–3 → 3–5 hashtag → câu miễn trừ.
6. **QA** như mọi video (`qa_report.md` ĐẠT), cộng kiểm tra tay: mọi mã trên màn hình là mã bịa; không cảnh nào
   lộ thông tin tài khoản thật.

## Còn thiếu (việc đóng gói tiếp theo)

- Style `product-carousel`: slide từ ảnh chụp giao diện (`tutorial/capture`) + chú thích, cho dạng *Carousel tính năng*.
- Chế độ cắt ngắn của `tutorial/`: chọn một luồng (chỉ Quét toàn sàn hoặc chỉ Phân tích Quant) bằng một tham số.

## Đo

Sau 7 ngày, ghi vào `notes` của `knowledge/episodes.csv`: lượt click link, số đăng ký mới trong tuần (nếu có từ
admin), bình luận hỏi về sản phẩm. View chỉ là phụ.
