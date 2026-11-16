# Survivorship bias — 10.000 quản lý quỹ tung đồng xu (EN series)

Mỗi năm mỗi người 'thắng thị trường' với xác suất 50% (không kỹ năng). Xác suất 10 năm liên tiếp = 1/1.024. Với 10.000 người, kỳ vọng ≈ 10 'thiên tài'. Biến thể lừa đảo: gửi 1.024 email dự đoán ngược chiều nhau, giữ nhóm đoán đúng, sau 10 vòng còn 1 người thấy 10/10 lần đúng.

## video_defaults

```json
{
  "lang": "en",
  "tag": "SURVIVORSHIP",
  "title": "Ten perfect years in a row, with zero skill",
  "kicker": "Survivorship bias",
  "hook": "{managers} fund managers with zero skill. Some will beat the market ten years in a row.",
  "sequence": [
    {
      "type": "hook",
      "clip": "market_screen",
      "say": "Take {managers} fund managers with zero skill. Each year, each one just flips a coin: beat the market, or not."
    },
    {
      "type": "chart",
      "label": "Managers with a perfect record",
      "note": "{perfect} 'geniuses', by pure luck",
      "say": "After three years, {after3} still have a perfect record. After five, {after5}. After ten years, {perfect} managers have never lost."
    },
    {
      "type": "number",
      "value": "1 in {one_in}",
      "label": "chance of a perfect ten-year run by luck",
      "say": "For one person, the odds are one in {one_in}. But with {managers} players, about {expected_perfect} perfect records are expected. Someone always wins."
    },
    {
      "type": "anim",
      "anim": "halving",
      "text": "The newsletter scam",
      "say": "Scammers use this. Send {letters} emails. Half say up, half say down. Keep the ones who got the right call. After ten rounds, one person has seen ten perfect predictions."
    },
    {
      "type": "code",
      "title": "survivorship.py",
      "say": "Here's the code. No skill anywhere. Every streak is pure chance."
    },
    {
      "type": "broll",
      "clip": "trader",
      "text": "You only see the survivors.",
      "say": "That's survivorship bias. The losers disappear quietly. The winner gets interviewed."
    }
  ],
  "takeaway": "Before trusting a track record, ask how many tried and failed that you never heard of.",
  "takeaway_clip": "market_screen",
  "takeaway_start": 6,
  "caption": "10,000 fund managers flip coins for 10 years. About 10 end up with a perfect record, with zero skill. Survivorship bias, simulated with real code.",
  "hashtags": [
    "survivorshipbias",
    "investing",
    "probability",
    "money",
    "psychology",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": []
}
```
