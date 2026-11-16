# Gambler's ruin — lợi thế nhà cái 2,7% (EN series)

Roulette một số 0: 37 ô, cược đỏ thắng 18/37 ≈ 48,6%, lợi thế nhà cái 1/37 ≈ 2,7%. Bài toán phá sản: từ 100 chip, cược 1 chip/lần, dừng ở 0 hoặc 200 → xác suất gấp đôi = (r^100 − 1)/(r^200 − 1), r = q/p ≈ 0,45%. Trò công bằng: 50%. Không đưa 'cách cược tối ưu' (tránh hướng dẫn cờ bạc).

## video_defaults

```json
{
  "lang": "en",
  "tag": "HOUSE EDGE",
  "sensitive": "gambling",
  "title": "The casino doesn't need to cheat",
  "kicker": "Gambler's ruin",
  "hook": "The casino doesn't need to cheat. A {edge} edge is enough.",
  "sequence": [
    {
      "type": "hook",
      "clip": "roulette",
      "say": "The casino doesn't need to cheat. An edge of just {edge} is enough to take nearly everything."
    },
    {
      "type": "anim",
      "anim": "roulette",
      "text": "{pockets} pockets",
      "say": "A single-zero wheel has {pockets} pockets. Bet on red and you win {p_win} of the time. Close to a coin flip. Not quite."
    },
    {
      "type": "image",
      "image": "monte_carlo_casino",
      "text": "Small gaps pay for buildings like this",
      "say": "That tiny gap pays for buildings like this one."
    },
    {
      "type": "chart",
      "label": "One chip per spin",
      "note": "Green: the few who doubled",
      "say": "Simulate {players} players. Each starts with {cash} chips, bets one per spin, and stops at zero or at {goal}."
    },
    {
      "type": "number",
      "value": "{busted}",
      "label": "went broke before doubling",
      "say": "{busted} go broke. Only {doubled} ever double up. The typical player lasts {median_spins} spins."
    },
    {
      "type": "terminal",
      "outputs": [
        {
          "label": "win chance per spin",
          "key": "p_win"
        },
        {
          "label": "house edge",
          "key": "edge"
        },
        {
          "label": "chance to double (theory)",
          "key": "theory_double",
          "highlight": true
        },
        {
          "label": "same, in a fair game",
          "key": "fair_double"
        }
      ],
      "say": "Theory agrees: a {theory_double} chance to double. In a fair game, it would be {fair_double}."
    },
    {
      "type": "broll",
      "clip": "slots",
      "text": "Small edge, many bets: certainty.",
      "say": "Repeat a small edge thousands of times and it stops being luck. Trading fees work the same way."
    }
  ],
  "takeaway": "Small edges repeated many times are destiny. Know who holds the edge.",
  "takeaway_clip": "roulette2",
  "caption": "A 2.7% house edge sounds small. Simulate 1,000 players and almost all of them go broke before doubling. Gambler's ruin, computed in code. Educational probability content.",
  "hashtags": [
    "probability",
    "houseedge",
    "math",
    "riskmanagement",
    "statistics",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "2.7%",
    "1,000"
  ]
}
```
