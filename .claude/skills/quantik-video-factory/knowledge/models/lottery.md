# Xác suất xổ số 6/49 (EN series)

C(49,6) = 13.983.816 tổ hợp. Mua 1 vé/ngày: thời gian chờ trung bình ≈ 38.000 năm. Mô phỏng 1 triệu người, mỗi người 1 vé/tuần trong 50 năm (2.600 vé). Chỉ dùng xác suất, không nói về cơ cấu giải hay tỷ lệ trả thưởng (cần nguồn riêng cho từng loại xổ số).

## video_defaults

```json
{
  "lang": "en",
  "tag": "PROBABILITY",
  "sensitive": "gambling",
  "title": "One lottery ticket a day: how long until you win?",
  "kicker": "Lottery odds",
  "hook": "Buy a lottery ticket every day. You'd wait about {years_daily} years for the jackpot.",
  "sequence": [
    {
      "type": "hook",
      "clip": "cash_count",
      "say": "Buy one lottery ticket every single day. On average, you'd wait about {years_daily} years to hit the jackpot."
    },
    {
      "type": "anim",
      "anim": "lottery_balls",
      "text": "Pick {pick} numbers of {pool}",
      "say": "A classic lotto: pick {pick} numbers out of {pool}. That makes {combos} possible tickets. Only one wins."
    },
    {
      "type": "chart",
      "label": "Chance of EVER winning",
      "say": "Play every week for {years} years: {tickets} tickets, and about a {p_life} chance of ever winning."
    },
    {
      "type": "number",
      "value": "{winners}",
      "label": "jackpot winners among {players} lifelong players",
      "say": "We simulated {players} people playing every week for {years} years. Only {winners} ever win. {never} never do."
    },
    {
      "type": "broll",
      "clip": "slots",
      "text": "You're buying a story, not odds.",
      "say": "Lotteries sell hope. The winner on TV is real. You just never see the millions of tickets that paid for it."
    }
  ],
  "takeaway": "A tiny chance times a huge prize feels like a deal. The math says you're paying for a dream.",
  "takeaway_clip": "dollars",
  "caption": "One ticket a day, and the average wait for a 6/49 jackpot is about 38,000 years. We simulated a million lifelong players. Educational probability content.",
  "hashtags": [
    "probability",
    "lottery",
    "math",
    "money",
    "statistics",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "38,000",
    "6/49"
  ]
}
```
