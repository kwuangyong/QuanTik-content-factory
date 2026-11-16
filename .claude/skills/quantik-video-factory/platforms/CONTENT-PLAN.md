# Kế hoạch nội dung theo nền tảng — bản chốt 11/2026

Một trang tổng hợp: mỗi nền tảng đăng gì, ví dụ cụ thể, dựng bằng gì, đăng bao nhiêu, đo bằng gì.
Chi tiết quy trình từng nền tảng ở `platforms/<nền tảng>/README.md`; lý do chọn hướng ở `RESEARCH-2026-11.md`.

| | **Facebook Reels** | **TikTok** | **Instagram Reels** | **YouTube Shorts** |
| --- | --- | --- | --- | --- |
| Ngôn ngữ | Việt | Việt | Việt | **Anh** |
| Vai trò | **chuyển đổi** (ra người dùng trả tiền) | **giáo dục**, xây độ tin cậy | **lan truyền**, nhớ tên QuanTik | **kéo view nhanh** ("ăn xổi") |
| Người xem | người muốn dùng quant làm công cụ chính | nhà đầu tư tò mò về quant | Gen Z, không thích học | người xem quốc tế, thích sự thật khó nghe |
| Nội dung | sản phẩm: Quét toàn sàn, Phân tích Quant | quant đọc tin · series Học quant · cầm tay chỉ việc | skit/POV · câu kỷ luật · thử thách 100 ngày | dark truth · tâm lý nhà đầu tư · poker theory |
| Độ dài | 20–45s | 35–60s | 12–30s | 15–45s |
| Tần suất | 3/tuần | 5/tuần | 4/tuần | 5/tuần |
| CTA thẻ cuối | Dùng thử miễn phí tại quantik.io.vn | Theo dõi để học quant mỗi ngày | Lưu lại, gửi cho bạn | Follow for the math behind the market |
| Đo | click link, đăng ký, nâng Pro | follow, tỉ lệ xem hết | share, save | xem hết, sub mới |

## Facebook Reels — sản phẩm, "ăn liền"

3 giây đầu là kết quả trên màn hình. Mã cổ phiếu luôn là mã bịa (QTA, QTV…). Không đăng video giáo dục.

| # | Video | Dạng | Dựng bằng |
| --- | --- | --- | --- |
| 1 | Buổi sáng 1 phút với Quét toàn sàn: 5 mã điểm cao nhất, 5 mã nên tránh nhất theo thứ hạng screening | demo | `tutorial/` (bản ngắn) |
| 2 | Lọc mã cả tối bằng tay → mở bảng đã xếp hạng theo 34 chỉ tiêu | trước / sau | `tutorial/` |
| 3 | Gõ một mã → báo cáo Phân tích Quant đọc trong 30 giây | demo | `tutorial/` |
| 4 | Vùng giá mô phỏng là gì, và không phải là gì | demo + giải thích | `tutorial/` |
| 5 | Xoay mô hình 3D để thấy rủi ro của một mã | demo | `tutorial/` |
| 6 | "Quant có quyết định thay bạn không? Không. Nó làm việc này…" | hỏi đáp, tự quay | `talking-head-script` |
| 7 | Mỗi cột trong bảng quét đo gì (series cắt nhỏ, 1 video 3–4 cột) | series | `tutorial/` |
| 8 | Đăng ký → quét → phân tích trong 2 phút (ghim đầu trang) | hướng dẫn đầy đủ | `tutorial/run.sh` |

## TikTok — giáo dục "Học quant cùng QuanTik"

| Trụ (tỉ lệ) | Ví dụ | Dựng bằng |
| --- | --- | --- |
| **Quant đọc tin** (50%) — trong 24–48h sau sự kiện | "Một mã giảm 11 phiên liền: về thống kê hiếm cỡ nào?" · "VN-Index biến động mạnh: GARCH nói cụm biến động kéo dài bao lâu?" · "Thị trường đổi trạng thái: HMM đọc thế nào?" | `batch.py --prices <csv> --data-source …` (dữ liệu thật chỉ minh hoạ cách tính, không nói hướng giá) |
| **Series Học quant #N** (30%) | 8 mô hình viết tay: Sharpe, Sortino, VaR/CVaR, Kelly, Hurst, HMM, Monte Carlo, GARCH · ~200 chủ đề catalog, ưu tiên chỉ số có trong báo cáo (`module_*`, `sheet-*`) | `batch.py --platform tiktok --topics … --styles …` |
| **Cầm tay chỉ việc bằng QuanTik** (20%) | "Tập 3: đọc báo cáo Phân tích Quant trong 60 giây" · "Một chỉ số trong bảng quét, đọc sao cho đúng" | `tutorial/` (bản ngắn) |

## Instagram Reels — larping, motivational, vui

Không khoe lãi, không lifestyle giàu nhanh. Motivational là về kỷ luật, không về tiền.

| Dạng | Ví dụ | Dựng bằng |
| --- | --- | --- |
| **Skit / POV** đời nhà đầu tư | "Tôi và sếp mỗi khi thị trường xanh" · "Mẹ hỏi: con chơi chứng khoán à?" · "POV: cả group mua theo tin, bạn mở bảng biến động" | cần người quay; kịch bản bằng `talking-head-script` |
| **Một câu kỷ luật** | "Cảm xúc bảo bán. Dữ liệu bảo đợi." · "Thị trường không nợ bạn một cú hồi." | `kinetic-text`, `--platform instagram` |
| **Thử thách 100 ngày** | "Ngày 1/100: Sharpe trong 30 giây" … lấy từ catalog ~200 chủ đề | `meme-quant`, `kinetic-text` |
| **Cheat sheet để lưu** | "5 chỉ số rủi ro nên biết" (1–3 slide) | `carousel` |

## YouTube Shorts — tiếng Anh, dark truth · psychology · poker

Mỗi video là một sự thật khó nghe, chứng minh bằng số do code tính. Không dự báo giá, không nêu mã, poker chỉ là
khung tư duy xác suất.

| # | Video | Trụ | Mô hình · style | Trạng thái |
| --- | --- | --- | --- | --- |
| 1 | Poker pros with an edge still bet small | poker | `kelly` · myth-buster | **đã dựng** (`episodes/en-poker-kelly-myth.json`) |
| 2 | You don't get the average return. You get one path. | dark truth | `monte_carlo` · kinetic-text | **đã dựng** (`episodes/en-dark-truth-paths.json`) |
| 3 | Your brain plans for a bad day. The market plans for a worse one. | psychology | `var_cvar` · meme-quant | **đã dựng** (`episodes/en-psych-worst-day.json`) |
| 4 | Gambler's ruin: how a winning player still goes broke | poker | `kelly` · kinetic-text | cần viết |
| 5 | Revenge trading is just doubling your bet | psychology | `kelly` (double Kelly) · meme-quant | cần viết |
| 6 | Your chart pattern might be pure noise | dark truth | `hurst` (random walk) · myth-buster | cần viết |
| 7 | Calm markets are where storms are born | dark truth | `garch` · kinetic-text | cần viết |
| 8 | Higher return, worse strategy | psychology | `sharpe` · myth-buster | cần viết |
| 9 | The "once in a century" day happens every few years | dark truth | `var_cvar` (fat tails) · kinetic-text | cần viết |
| 10 | The market has moods, and you can't see them | psychology | `hmm` · kinetic-text | cần viết |

## Sẵn sàng và còn thiếu

| Nền tảng | Làm được ngay | Còn thiếu |
| --- | --- | --- |
| Facebook Reels | hướng dẫn đầy đủ (`tutorial/run.sh`), hỏi đáp tự quay | **tutorial bản ngắn** (một luồng, 20–40s) cho các video 1–5, 7 |
| TikTok | series Học quant (8 mô hình + catalog), quant đọc tin với `--prices` | tutorial bản ngắn; mẫu episode "quant đọc tin" chặt compliance hơn |
| Instagram Reels | câu kỷ luật, thử thách 100 ngày, cheat sheet | người quay skit; lịch tự động series 100 ngày |
| YouTube Shorts | toàn bộ pipeline tiếng Anh, 3 tập mẫu | viết tiếp episode tiếng Anh 4–10 |
