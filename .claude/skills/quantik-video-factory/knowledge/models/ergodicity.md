# Ergodicity — trung bình đám đông khác đời một người (EN series)

Nguồn: Ole Peters, "The ergodicity problem in economics", *Nature Physics* 15, 1216–1221 (2019). Trò chơi tung đồng
xu +50% / −40% là ví dụ kinh điển trong bài đó.

## Công thức

- Kỳ vọng mỗi ván (trung bình đám đông): 0,5·1,5 + 0,5·0,6 = 1,05 → +5%/ván.
- Tăng trưởng điển hình theo thời gian (trung bình nhân): √(1,5·0,6) ≈ 0,949 → mất ≈ 5,1%/ván.
- Không ergodic: trung bình theo tập hợp ≠ trung bình theo thời gian của một cá nhân.

## Tham số đẹp để minh hoạ

1.000 người × 50 ván, seed 11. "Trung bình" ×11,5; trung vị còn ≈ 7% vốn; ≈ 74% người nghèo đi; 10 người giàu nhất
nắm ≈ một nửa tổng tiền.

## Sai lầm hay gặp

- Thấy kỳ vọng dương là nghĩ mình sẽ có lãi. Một cá nhân chỉ sống một đường đi, không sống trung bình của đám đông.
- Áp dụng sang đầu tư: lỗ phần trăm lớn khó gỡ (lỗ 40% cần lãi 67% để hoà).

## video_defaults

```json
{
  "lang": "en",
  "sensitive": "gambling",
  "tag": "ERGODICITY",
  "title": "The coin flip that makes the average rich and you poor",
  "kicker": "Ergodicity",
  "hook": "A coin game where you win on average. Almost everyone still goes broke.",
  "sequence": [
    {"type": "hook", "clip": "coin_flip",
     "say": "Here's a coin game where you win on average. And almost everyone still goes broke."},
    {"type": "anim", "anim": "coins", "text": "Heads: gain {up}. Tails: lose {down}.",
     "say": "Heads, your money grows {up}. Tails, it shrinks {down}. On average, you gain {avg_gain} per flip."},
    {"type": "broll", "clip": "crowd", "text": "{people} people. {rounds} flips each.",
     "say": "Let's run it. {people} people, {rounds} flips each."},
    {"type": "chart", "label": "The simulation", "from": 0, "to": 1, "note": "Typical player keeps {median_left} of their money",
     "say": "The green line is the average of everyone. It grows to {expected_x}. The red line is the typical player. They keep just {median_left}."},
    {"type": "number", "value": "{share_poorer}", "label": "of players end up poorer than they started",
     "say": "{share_poorer} of players lose money. And {share_wiped} are almost wiped out."},
    {"type": "anim", "anim": "crowd", "text": "So who got the average?",
     "say": "So where did the average come from? A tiny lucky group. The ten richest players hold {top_share} of all the money."},
    {"type": "code", "title": "ergodicity.py",
     "say": "Here's the whole simulation. Each flip multiplies your money by 1.5 or 0.6. Over time, the typical player loses about {typical_loss} per flip."}
  ],
  "takeaway": "The average of the crowd is not the path of one person. Avoid losses you can't come back from.",
  "takeaway_clip": "market_screen",
  "caption": "Heads +50%, tails -40%. The 'average' player gets rich, yet most real players end up poorer. This is ergodicity: the average of a crowd is not what happens to one person over time. Simulated with real code, fixed seed.",
  "hashtags": ["ergodicity", "probability", "gametheory", "money", "investing", "quant", "QuanTik"],
  "allowed_literals": ["1.5", "0.6", "+50%", "-40%"]
}
```
