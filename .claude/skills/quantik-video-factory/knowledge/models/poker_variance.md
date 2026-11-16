# Phương sai — người có lợi thế vẫn thua rất lâu (EN series)

Winrate 5 bb/100, độ lệch chuẩn 100 bb/100 (mức thường gặp ở no-limit hold'em, dùng làm giả định minh hoạ). Mô phỏng 1.000 người × 100.000 hand. Đo: tỷ lệ còn âm sau 10k/50k/100k hand, chuỗi dài nhất không lập đỉnh mới.

## video_defaults

```json
{
  "lang": "en",
  "tag": "VARIANCE",
  "sensitive": "gambling",
  "title": "A winning player can lose for tens of thousands of hands",
  "kicker": "Variance",
  "hook": "This player has a real edge. After 10,000 hands, there's a {behind_10k} chance they're still losing.",
  "sequence": [
    {
      "type": "hook",
      "clip": "cards_deal",
      "say": "This player has a real, proven edge. After ten thousand hands, there's still a {behind_10k} chance they're losing money."
    },
    {
      "type": "broll",
      "clip": "poker_chips",
      "text": "{players} players. The exact same edge.",
      "say": "Let's simulate {players} players with exactly the same skill: winning {winrate} big blinds per hundred hands on average."
    },
    {
      "type": "chart",
      "label": "Same skill, different luck",
      "note": "Typical longest slump: {median_flat} hands",
      "say": "Every grey line has the same edge. Green is what skill alone would give. The orange player spends long stretches going nowhere."
    },
    {
      "type": "number",
      "value": "{median_flat}",
      "label": "hands: the typical longest stretch with no new high",
      "say": "For the typical player, the longest slump lasts {median_flat} hands. And after fifty thousand hands, {behind_50k} of these winners are still behind."
    },
    {
      "type": "code",
      "title": "poker_variance.py",
      "say": "In the code, every hundred hands is one random draw. Average {winrate}, spread {sd}. The noise is twenty times the edge."
    },
    {
      "type": "broll",
      "clip": "trader",
      "text": "Edge is quiet. Luck is loud.",
      "say": "Any small edge works like this, including in markets. It takes a very long time to show up."
    }
  ],
  "takeaway": "Having an edge and seeing it are different things. Size risk so you survive the slumps.",
  "takeaway_clip": "cards_shuffle",
  "caption": "Same skill, 1,000 players, 100,000 hands each. Many genuine winners spend tens of thousands of hands losing. Variance, simulated with real code. Poker is only our probability example.",
  "hashtags": [
    "variance",
    "probability",
    "riskmanagement",
    "statistics",
    "math",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "10,000"
  ]
}
```
