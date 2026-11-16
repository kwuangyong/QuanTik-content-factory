# Thế lưỡng nan tù nhân lặp lại — tử tế nhưng không ngây thơ (EN series)

Nguồn: R. Axelrod, "Effective Choice in the Prisoner's Dilemma", *Journal of Conflict Resolution* 24(1), 1980; *The Evolution of Cooperation* (1984). Tit for Tat thắng giải của Axelrod. Bản tái hiện ở đây chỉ 5 chiến lược × 200 vòng (kể cả tự đấu): Grudger và Tit for Tat dẫn đầu — cả hai không phản bội trước nhưng trừng phạt phản bội; Tit for Tat không thắng đối đầu trực tiếp trận nào. Kịch bản nói đúng kết quả này, không nói Tit for Tat 'vô địch' trong bản tái hiện.

## video_defaults

```json
{
  "lang": "en",
  "tag": "GAME THEORY",
  "title": "Selfish players win rounds. They lose the tournament.",
  "kicker": "Prisoner's dilemma",
  "hook": "Betrayal wins every single round. So why do nice strategies win the tournament?",
  "sequence": [
    {
      "type": "hook",
      "clip": "handshake",
      "say": "Betrayal wins every single round. So why do nice strategies win the whole tournament?"
    },
    {
      "type": "anim",
      "anim": "payoff_matrix",
      "text": "The prisoner's dilemma",
      "say": "Two players. Both cooperate: {r} points each. Betray a cooperator: you get {t}, they get {s}. Both betray: {p} each. Betrayal always looks better."
    },
    {
      "type": "image",
      "image": "axelrod",
      "text": "Ran a famous computer tournament in 1980",
      "say": "Robert Axelrod ran a famous computer tournament. The winner, Tit for Tat, was tiny: cooperate first, then copy your opponent."
    },
    {
      "type": "chart",
      "label": "Our replay: {n_strats} strategies, {rounds} rounds",
      "say": "We replayed it in code. The top two, Grudger and Tit for Tat, share one trait: never betray first, but punish betrayal. Always Defect finishes in place {defect_rank}."
    },
    {
      "type": "number",
      "value": "{tft_beats}",
      "label": "opponents Tit for Tat beat head-to-head",
      "say": "The twist: Tit for Tat beat {tft_beats} opponents head-to-head. It never wins a match. It wins by making every match good."
    },
    {
      "type": "broll",
      "clip": "deal",
      "text": "Reputation compounds.",
      "say": "In a one-off game, betrayal pays. Repeat the game, and trust becomes an asset."
    }
  ],
  "takeaway": "Short run, the selfish win rounds. Long run, the nice but not naive win the game.",
  "takeaway_clip": "handshake",
  "takeaway_start": 4,
  "caption": "Why do cooperative strategies beat selfish ones in repeated games? We replay Axelrod's prisoner's dilemma tournament in code. Nice but not naive wins.",
  "hashtags": [
    "gametheory",
    "prisonersdilemma",
    "psychology",
    "strategy",
    "trust",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "1980"
  ],
  "facts": {
    "axelrod": {
      "value": "1980",
      "source": "Axelrod, 'Effective Choice in the Prisoner's Dilemma', Journal of Conflict Resolution 24(1), 1980"
    }
  }
}
```
