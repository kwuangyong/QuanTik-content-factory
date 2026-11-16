# Escape velocity — vận tốc thoát ly tài chính (tiết kiệm vs lạm phát lối sống)

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

## video_defaults

```json
{
  "lang": "en",
  "tag": "DARK TRUTH",
  "title": "Escape velocity: why you can't escape the 9-to-5",
  "hook": "You got the raise. So why are you still trapped?",
  "scenes": [
    {
      "kind": "office",
      "show": "You got the raise. So why are you still trapped?",
      "say": "You got the raise. So why are you still trapped?",
      "min_dur": 3.2
    },
    {
      "kind": "commute",
      "show": "Same train. Same desk.",
      "say": "Same train. Same desk. Same hope that next year is different."
    },
    {
      "kind": "scroll",
      "show": "Then you open your phone.",
      "say": "Then you open your phone. Everyone else is winning."
    },
    {
      "kind": "compare",
      "show": "Their car. Their house. Their trip.",
      "say": "Their car. Their house. Their trip. Yours feels small.",
      "min_dur": 4.0
    },
    {
      "kind": "spend",
      "show": "The raise buys a life that looks fine.",
      "say": "So every raise buys a life that looks fine. Never a way out."
    },
    {
      "kind": "wheel",
      "show": "Every upgrade is another bill.",
      "say": "Every upgrade is another bill. The bigger it looks, the tighter it holds."
    },
    {
      "kind": "crowd",
      "show": "{esc_a_n} out of {n_paths}",
      "say": "Of {n_paths} simulated careers that spent every raise, only {esc_a_n} broke free.",
      "note": "Simulation: {years} years · {save} saved · {raise} raises a year · {ret} real return · {wr} rule",
      "min_dur": 5.0
    },
    {
      "kind": "walkaway",
      "show": "Escape velocity.",
      "say": "Escape velocity isn't a bigger salary. It's when you stop paying to be seen.",
      "min_dur": 4.5
    },
    {
      "kind": "alone",
      "show": "The salary was never the trap.",
      "say": "The salary was never the trap. Needing them to see it was."
    }
  ],
  "takeaway": "Your salary was never the trap. Needing them to see it was.",
  "cta": "Like and follow QuanTik for more dark truths about money",
  "caption": "You got the raise. You're still trapped. Not because you earn too little, but because every raise goes into looking like you're doing fine. We simulated {n_paths} careers that saved {save} and spent every raise: after {years} years, only {esc_a_n} broke free. Escape velocity isn't a bigger salary. It's needing less applause than you earn.\n\n(Simulation: {ret} real return, {vol} volatility, {raise} raises a year, {wr} withdrawal rule, no taxes or fees. An illustration of a mechanism, not a plan.)",
  "hashtags": [
    "darktruth",
    "socialpressure",
    "lifestylecreep",
    "moneymindset",
    "personalfinance",
    "9to5",
    "financialfreedom",
    "QuanTik"
  ],
  "allowed_literals": [],
  "thumb": {
    "series": "THE DARK TRUTH OF MONEY",
    "headline": [
      "YOU GOT THE RAISE.",
      "STILL",
      "TRAPPED."
    ],
    "sub": "Only {esc_a_n} of {n_paths} careers broke free",
    "footer": "Simulated data • Not financial advice"
  },
  "series": "dark-truth"
}
```
