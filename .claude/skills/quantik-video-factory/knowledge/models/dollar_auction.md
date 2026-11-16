# Đấu giá đô la — leo thang và chi phí chìm (EN series)

Nguồn: M. Shubik, "The Dollar Auction Game: A Paradox in Noncooperative Behavior and Escalation", *Journal of Conflict Resolution* 15(1), 1971. Luật: người trả cao nhất nhận tờ tiền, người cao nhì cũng phải trả giá của mình. Mỗi bước nâng giá đều 'hợp lý cục bộ' (lỗ ít hơn bỏ cuộc) nên giá vượt giá trị giải thưởng. Mô phỏng: bước 5$, ví ngẫu nhiên 150–300$, seed 6.

## video_defaults

```json
{
  "lang": "en",
  "tag": "ESCALATION",
  "title": "Rational people paying $220 for a $100 bill",
  "kicker": "Dollar auction",
  "hook": "I auction a $100 bill. Rational people pay ${win_bid} for it.",
  "sequence": [
    {
      "type": "hook",
      "clip": "gavel",
      "say": "I'm auctioning a hundred-dollar bill. Smart, rational people end up paying {win_bid} dollars for it."
    },
    {
      "type": "broll",
      "clip": "dollars",
      "text": "One twist: second place pays too.",
      "say": "One rule changes everything: the highest bidder wins the bill, but the second-highest bidder pays their bid too."
    },
    {
      "type": "anim",
      "anim": "auction",
      "text": "Watch the bids",
      "say": "Early on, it's a bargain. But whoever is behind always has a choice: quit and lose their bid, or raise by {step} and maybe win."
    },
    {
      "type": "chart",
      "label": "Bid by bid",
      "note": "Bids pass $100 at bid number {first_over}",
      "say": "So they keep raising. They pass the prize at bid number {first_over}, and keep going until someone runs out of cash."
    },
    {
      "type": "number",
      "value": "${collected}",
      "label": "collected for a $100 bill",
      "say": "Final bids: {win_bid} and {lose_bid}. The auctioneer collects {collected} dollars for a hundred-dollar bill."
    },
    {
      "type": "broll",
      "clip": "trader",
      "text": "Sunk costs pull you deeper.",
      "say": "This is Martin Shubik's dollar auction. It's the logic of bidding wars, price wars, and holding a losing position just to get back to even."
    }
  ],
  "takeaway": "Don't ask how much you've already put in. Ask what the next step is worth from here.",
  "takeaway_clip": "gavel",
  "takeaway_start": 4,
  "caption": "Why do rational people pay $220 for a $100 bill? Martin Shubik's dollar auction (1971) shows how every step can make sense while the whole path doesn't. Simulated with real code.",
  "hashtags": [
    "gametheory",
    "sunkcost",
    "psychology",
    "behavioraleconomics",
    "money",
    "quant",
    "QuanTik"
  ],
  "allowed_literals": [
    "$100",
    "100",
    "$220",
    "1971"
  ],
  "facts": {
    "shubik": {
      "value": "1971",
      "source": "Shubik, 'The Dollar Auction Game', Journal of Conflict Resolution 15(1), 1971"
    }
  }
}
```
