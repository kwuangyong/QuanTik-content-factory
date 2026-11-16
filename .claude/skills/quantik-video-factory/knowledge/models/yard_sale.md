# Mô hình yard-sale — bất bình đẳng sinh ra từ trò chơi công bằng (EN series)

Nguồn: B. Boghosian, "The Inescapable Casino", *Scientific American*, 11/2019; A. Chakraborti (2002). Mỗi giao dịch: tung đồng xu công bằng, người thua trả 10% tài sản của **người nghèo hơn**. Không ai gian lận, tiền vẫn dồn về một phía ("wealth condensation"). Mô hình bỏ qua thuế/phúc lợi — chính các cơ chế này kéo ngược lại.

## video_defaults

```json
{
  "lang": "en",
  "tag": "WEALTH",
  "title": "Why a perfectly fair game still creates the super-rich",
  "kicker": "Yard-sale model",
  "hook": "A perfectly fair economy. No cheating. A few people still end up with most of the money.",
  "sequence": [
    {
      "type": "hook",
      "clip": "crowd",
      "say": "Imagine the fairest economy possible. No cheating, no talent. A few people still end up with most of the money."
    },
    {
      "type": "anim",
      "anim": "crowd",
      "text": "{people} people, ${start_cash} each",
      "opt": {
        "morph": [
          0.35,
          0.9
        ]
      },
      "say": "{people} people start with {start_cash} dollars each. Two random people meet and flip a fair coin. The loser pays {bet_frac} of the poorer person's wealth."
    },
    {
      "type": "chart",
      "label": "Wealth held by the top 1%",
      "note": "Top 1% now hold {top1_end}",
      "say": "Now repeat that {trades} times. The richest one percent start with a fair {top1_start} of the money. They end with {top1_end}."
    },
    {
      "type": "number",
      "value": "{bottom50_end}",
      "label": "of all the money is left for the poorest half",
      "say": "The poorest half of people now share just {bottom50_end} of everything. {under_10} are down to less than ten dollars."
    },
    {
      "type": "code",
      "title": "yard_sale.py",
      "say": "The key line: the bet is sized by the poorer person. A loss hurts them far more than a win helps."
    },
    {
      "type": "broll",
      "clip": "cash_count",
      "text": "Fair rules. Unequal outcome.",
      "say": "Physicist Bruce Boghosian calls this the yard-sale model. Real economies have taxes and safety nets that push back. Without them, chance piles money up."
    }
  ],
  "takeaway": "Inequality doesn't need villains. Chance plus compounding is enough.",
  "takeaway_clip": "dollars",
  "caption": "Everyone starts equal. Every trade is a fair coin flip. Still, money piles up at the top. This is the yard-sale model of wealth (Boghosian, Scientific American 2019), simulated with real code.",
  "hashtags": [
    "inequality",
    "money",
    "economics",
    "gametheory",
    "probability",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "1%",
    "2019"
  ],
  "facts": {
    "boghosian": {
      "value": "yard-sale model",
      "source": "Boghosian, 'The Inescapable Casino', Scientific American, Nov 2019"
    }
  }
}
```
