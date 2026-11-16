# Nền tảng: mỗi nơi một quy trình riêng

Chủ sản phẩm chốt 11/2026: **không làm một video rồi đăng mọi nơi.** Mỗi nền tảng có vai trò, loại nội dung,
CTA, caption và cách đo riêng. Mọi yêu cầu làm nội dung bắt đầu bằng câu hỏi *"cho nền tảng nào?"*, rồi đọc
đúng một file dưới đây và làm theo nó từ đầu đến cuối.

| Nền tảng | Vai trò | Nội dung | Quy trình | Lệnh |
| --- | --- | --- | --- | --- |
| **Facebook** | chuyển đổi (ra người trả tiền) | sản phẩm QuanTik, xem là dùng được | [`facebook/README.md`](facebook/README.md) | `tutorial/run.sh` (chính) · `batch.py --platform facebook --episode …` (talking-head) |
| **TikTok** | giáo dục, xây độ tin cậy | series "Học quant cùng QuanTik #N" | [`tiktok/README.md`](tiktok/README.md) | `batch.py --platform tiktok --topics … --styles …` |
| **Instagram Reels** | thử nghiệm, lan truyền | larping, motivational, vui, đáng share/save | [`instagram/README.md`](instagram/README.md) | `batch.py --platform instagram …` |
| **YouTube Shorts (tiếng Anh)** | kéo view nhanh, "ăn xổi" | dark truth, tâm lý nhà đầu tư, poker theory | [`youtube-shorts/README.md`](youtube-shorts/README.md) | `batch.py --platform youtube-shorts --episode ../episodes/en-….json` |

**Bản tổng hợp: mỗi nền tảng đăng gì → [`CONTENT-PLAN.md`](CONTENT-PLAN.md).**

Nghiên cứu nền tảng (người xem cần gì, dạng nào đang lên, vòng thử 4 tuần): [`RESEARCH-2026-11.md`](RESEARCH-2026-11.md).

`profiles.json` là bản máy đọc của bảng trên: style được phép, CTA thẻ cuối, mục caption, độ dài tối đa.
`batch.py --platform <tên>` dùng nó để gắn CTA, chỉ in caption của nền tảng đó, thêm hậu tố nền tảng vào id
output, và từ chối style không thuộc nền tảng. Không có `--platform` thì chạy như cũ (CTA TikTok, caption mọi nơi). Nền tảng có `"lang": "en"` (YouTube Shorts) tự chuyển toàn bộ video sang tiếng Anh.

## Điều phối yêu cầu

| Người dùng nói | Nền tảng |
| --- | --- |
| "video Facebook", "bán hàng", "quảng bá", "chuyển đổi", "demo tính năng", "hướng dẫn dùng" | Facebook |
| "TikTok", "học quant", "giải thích X", "series", "tập #N" | TikTok |
| "Reels", "Instagram", "Gen Z", "meme", "trend" | Instagram Reels |
| "Shorts", "YouTube", "tiếng Anh", "English", "dark truth", "poker", "tâm lý nhà đầu tư" | YouTube Shorts (tiếng Anh) |
| không nói nền tảng | hỏi lại một câu; nếu là chủ đề quant thuần thì mặc định TikTok |

Người dùng muốn đăng một video lên nhiều nơi: làm được, nhưng nêu trong lưu ý cho người duyệt rằng nó lệch
vai trò của nền tảng phụ (video giáo dục trên Facebook là dạng đã thấy không hiệu quả).

## Ai trả tiền cho QuanTik (TAM → SAM → SOM)

Ước tính nội bộ của chủ sản phẩm, chỉ để định hướng. **Không đưa vào video hay caption** (không có nguồn công bố;
QA số sẽ chặn).

| Tầng | Ai | Quy mô ước tính | Nền tảng nuôi tầng này |
| --- | --- | --- | --- |
| TAM | tài khoản chứng khoán tại Việt Nam | hơn 14 triệu | Instagram Reels (biết đến thương hiệu); YouTube Shorts tiếng Anh nhắm ra ngoài Việt Nam |
| SAM | nhà đầu tư biết, tò mò, hứng thú với quant | khoảng 100 nghìn | TikTok (giáo dục) |
| SOM | người muốn dùng quant làm **công cụ chính**: tiết kiệm thời gian, ra quyết định có hệ thống | khoảng 5 nghìn | Facebook (chuyển đổi) |

## Luật chung mọi nền tảng

`brand/compliance.md` và `brand/identity.md` vẫn áp dụng nguyên vẹn: không gọi mua/bán, không hứa lợi nhuận,
câu miễn trừ trong caption và thẻ cuối, số qua placeholder, giá gói đối chiếu `/plans`, mã bịa trong demo sản phẩm.

## Ghi kết quả

`knowledge/episodes.csv`: cột `notes` có `platform=<tên>` (batch tự ghi). Sau 7 ngày ghi số theo cách đo của
nền tảng (xem mục *Đo* trong từng file). Đây là dữ liệu cho vòng nghiên cứu sau.
