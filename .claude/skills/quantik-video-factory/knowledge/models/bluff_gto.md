# GTO bluffing — vì sao chiến lược tối ưu buộc phải bluff (EN series)

Nguồn: von Neumann & Morgenstern, *Theory of Games and Economic Behavior* (1944) phân tích bluff trong mô hình poker đơn giản. Cược b (theo pot = 1): đối thủ cần equity b/(1+2b) để gọi; tỷ lệ bluff cân bằng trong dải cược = b/(1+2b); MDF = 1/(1+b). Cược bằng pot → 1/3 bluff, 2 value : 1 bluff.

## video_defaults

```json
{
  "lang": "en",
  "tag": "GAME THEORY",
  "sensitive": "gambling",
  "title": "Why the best strategy is forced to bluff",
  "kicker": "Nash equilibrium",
  "hook": "The best poker strategy isn't honest. Math forces it to bluff.",
  "sequence": [
    {
      "type": "hook",
      "clip": "casino_table",
      "say": "The best poker strategy isn't honest. It is forced to bluff, and math tells you exactly how often."
    },
    {
      "type": "image",
      "image": "von_neumann",
      "text": "Studied bluffing in his 1944 book on game theory",
      "say": "John von Neumann, a founder of game theory, studied poker. His insight: if you never bluff, you're predictable. And predictable players get exploited."
    },
    {
      "type": "formula",
      "latex": "\\mathrm{bluffs}=\\frac{bet}{pot+2\\,bet}",
      "caption": "Pot-sized bet: {bluff_share} of your bets are bluffs",
      "say": "Bet the size of the pot, and your opponent risks one pot to win two. They need to be right {need} of the time. Balance means {bluff_share} of your bets are bluffs."
    },
    {
      "type": "anim",
      "anim": "bluff_scale",
      "text": "A balanced betting range",
      "say": "So for every {ratio_value} strong hands you bet, you add one bluff."
    },
    {
      "type": "chart",
      "label": "Opponent's payoff from calling",
      "say": "Bluff less, and they should simply fold. Bluff more, and they should call everything. Only at {bluff_share} does neither choice help them."
    },
    {
      "type": "terminal",
      "outputs": [
        {
          "label": "half-pot bet",
          "key": "bluff_half"
        },
        {
          "label": "pot-sized bet",
          "key": "bluff_share",
          "highlight": true
        },
        {
          "label": "2x pot bet",
          "key": "bluff_over"
        }
      ],
      "say": "Bigger bets allow more bluffs: {bluff_half} for a half-pot bet, {bluff_over} for a bet twice the pot."
    }
  ],
  "takeaway": "Optimal isn't honest. It's unpredictable. Being readable is a cost.",
  "takeaway_clip": "cards_deal",
  "caption": "Game theory says a perfect strategy must bluff, and how often: a third of your bets for a pot-sized bet. Von Neumann's idea, computed in code. Poker is only our game-theory example.",
  "hashtags": [
    "gametheory",
    "nashequilibrium",
    "strategy",
    "math",
    "psychology",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "1944",
    "2x"
  ],
  "facts": {
    "tgeb": {
      "value": "1944",
      "source": "von Neumann & Morgenstern, Theory of Games and Economic Behavior, Princeton University Press, 1944"
    }
  }
}
```
