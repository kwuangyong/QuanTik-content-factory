# Pot odds & EV — thua ván vẫn là quyết định đúng (EN series)

Draw flush sau flop: 9 outs / 47 lá chưa thấy → xác suất trúng tới river = 1 − (38/47)(37/46) ≈ 35%. Pot 100, cược 50 → cần thắng 50/(100+2·50) = 25%. EV mỗi lần gọi ≈ +20 chip. Bẫy 'resulting': đánh giá quyết định bằng kết quả.

## video_defaults

```json
{
  "lang": "en",
  "tag": "EXPECTED VALUE",
  "sensitive": "gambling",
  "title": "You lost the hand. It was still the right call.",
  "kicker": "Pot odds",
  "hook": "You call. You lose. And it was still the right decision.",
  "sequence": [
    {
      "type": "hook",
      "clip": "poker_chips",
      "say": "You call a bet. You lose the hand. And it was still the right decision. Here's the math."
    },
    {
      "type": "anim",
      "anim": "cards",
      "text": "A flush draw",
      "say": "You hold two hearts, and two more are on the board. {outs} hearts are left in the deck. Your chance to hit by the river: {equity}."
    },
    {
      "type": "formula",
      "latex": "\\mathrm{need}=\\frac{bet}{pot+2\\,bet}=\\frac{<<bet>>}{<<pot>>+<<bet>>+<<bet>>}=<<need>>",
      "caption": "Risk {bet} to win {win_amt}",
      "say": "The pot is {pot} chips and your opponent bets {bet}. You risk {bet} to win {win_amt}. So you only need to win {need} of the time."
    },
    {
      "type": "number",
      "value": "+{ev}",
      "label": "chips per call, on average",
      "say": "Your expected value is plus {ev} chips every time you make this call."
    },
    {
      "type": "chart",
      "label": "The same call, {hands} times",
      "note": "Result: +{total} chips",
      "say": "But you lose this hand {lose_rate} of the time. Once you lost {worst_streak} in a row. Over {hands} calls, you still finish {total} chips ahead."
    },
    {
      "type": "broll",
      "clip": "cards_shuffle",
      "text": "Judge decisions, not outcomes.",
      "say": "Poker players call the mistake 'resulting': judging a decision by its outcome. Investors make it every day."
    }
  ],
  "takeaway": "Good decisions can lose. Bad ones can win. Over many tries, only the decision counts.",
  "takeaway_clip": "casino_table",
  "caption": "Why losing a hand can still be the right call: pot odds and expected value, explained with a real simulation. We use poker only as a probability example.",
  "hashtags": [
    "probability",
    "expectedvalue",
    "decisionmaking",
    "gametheory",
    "math",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": []
}
```
