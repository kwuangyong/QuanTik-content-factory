# Trụ cột 5 — Dark Truth (tiếng Anh)

Nội dung **tiếng Anh** cho IG Reels / YouTube Shorts quốc tế: sự thật khó nghe về tiền, địa vị và áp lực xã hội
(social insecurity). Kể bằng **nhân vật hoạt hoạ** (style `dark-story`), không chart, không code trên màn hình.

## Ranh giới với các trụ cột khác (để không lẫn)

| Chủ đề | Trụ cột | Vì sao |
| --- | --- | --- |
| Tiền & địa vị, so sánh trên mạng, lifestyle creep, vòng 9-5 (góc xã hội, cảm xúc) | **5 `dark-truth`** | khán giả quốc tế, tiếng Anh, kể chuyện |
| Thiên kiến nhà đầu tư khi giao dịch (FOMO, né lỗ, bầy đàn) | 2 `behavioral-finance` | tiếng Việt, bằng chứng học thuật từng đoạn |
| Poker, Nash, EV, Kelly, game theory | 4b `decision-science` | toán ra quyết định, có chart |
| Mô hình, chỉ số quant | 1 `quant-education` | code chạy thật trên màn hình |

Một tập dark-truth có thể chạm tâm lý học, nhưng nếu nội dung chính là *một thiên kiến khi đầu tư* thì thuộc trụ cột 2;
nếu là *chiến lược trong trò chơi* thì thuộc 4b. Episode luôn khai báo `"pillar"`, nên batch, QA, thumbnail và
`knowledge/episodes.csv` (cột notes `pillar=dark-truth`) tách bạch theo trụ cột.

## Quy tắc

- `"lang": "en"`; giọng `male-deep` → `en-US-ChristopherNeural` trầm; nền âm `drone` tự tổng hợp.
- Tối đa một con số "đắt" mỗi tập, đi qua `{key}` từ mô hình (`pipeline/pillar_models.py`) hoặc `facts` có `source_id` trong ledger.
  Cảnh có số kèm `note` ghi giả định mô phỏng.
- Không khuyên nghỉ việc, không hứa "financial freedom", không chỉ sản phẩm đầu tư. Cụm cấm: `brand/compliance.md` + `extra_banned`.
- Thumbnail: tối, nặng, series **"THE DARK TRUTH OF MONEY #N"** (tự sinh trong `styles/dark-story/template.py`).

## Lệnh

```bash
cd pipeline && python batch.py --episode ../episodes/escape-velocity-dark-story.json
```

## Tập đã làm: escape velocity
Chủ đề tài chính cá nhân / tâm lý xã hội (social insecurity), làm bằng **tiếng Anh** (`"lang": "en"`) cho IG / YouTube Shorts quốc tế, tông "dark truth".
Style chính: `dark-story` (hoạt hoạ người, không chart, không code). Mô hình chỉ chạy ngầm để cấp đúng một con số có nguồn (bao nhiêu sự nghiệp thoát được).

## Ý tưởng

"Thoát ly" = thu nhập từ khoản đầu tư (theo quy tắc rút 4%/năm) trả được toàn bộ chi tiêu hằng năm.
Tỷ lệ phủ `cover_t = 0,04 · tài sản_t / chi tiêu_t`; thoát ly khi `cover ≥ 100%` (cần tài sản ≈ 25 lần chi tiêu năm).

Sự thật khó nghe: thứ giữ người ta trong vòng 9-5 thường không phải mức lương mà là **chi tiêu tăng theo lương**
(lifestyle creep). Mỗi lần tăng lương mà tiêu hết thì mục tiêu (25 × chi tiêu) cũng chạy xa thêm, nên
tốc độ tích luỹ không bao giờ vượt được tốc độ của mục tiêu.

## Mô hình trong code (`escape_velocity_demo`)

- 2.000 sự nghiệp mô phỏng, 40 năm, lợi suất thực mỗi năm ~ N(5%, 15%) (seed cố định).
- Lương thực tăng 2%/năm. Cả hai người tiết kiệm 10% lương năm đầu.
- **A (spend the raises):** chi tiêu = 90% lương mỗi năm → tỷ lệ tiết kiệm cố định 10%.
- **B (save the raises):** chi tiêu giữ nguyên mức năm đầu → phần tăng lương đi vào tiết kiệm (cuối kỳ ~58%).
- 3D: tỷ lệ phủ sau 40 năm (tăng trưởng trung vị, tất định) theo tỷ lệ tiết kiệm × phần tăng lương bị tiêu.

## Giới hạn (phải nói rõ)

- Giả định đơn giản: lợi suất chuẩn độc lập, không thuế, không phí, không biến cố (thất nghiệp, bệnh, con cái).
- Quy tắc 4% là quy ước từ nghiên cứu Mỹ (Bengen 1994, Trinity study), không phải bảo đảm.
- Video không hứa "nghỉ hưu sớm", không chỉ sản phẩm đầu tư; chỉ minh hoạ cơ chế.

