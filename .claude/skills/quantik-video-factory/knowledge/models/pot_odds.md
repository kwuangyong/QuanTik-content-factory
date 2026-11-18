# Theo bài vì cảm giác là ném tiền qua cửa sổ

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `pot_odds_demo`. Style gợi ý: `dark-truth`.

## Là gì

Pot odds: số tiền phải bỏ ra so với số tiền có thể thắng. Equity: xác suất bài của bạn thắng. Theo khi equity lớn hơn tỷ lệ pot odds đòi hỏi.

Nguồn: Wikipedia: Pot odds

## Ý chính

Bạn theo bài vì cảm giác. Toán nói bạn vừa ném tiền qua cửa sổ.

Bạn có bốn lá cơ, cần thêm một lá cơ. Còn {outs} lá như vậy. Với một lá cuối, xác suất trúng là {eq_one}. Đối thủ cược nửa pot: bạn cần {need_half} để theo có lời. Cược bằng pot: cần {need_pot}. Bạn chỉ có {eq_one}. Đường cam là equity cần thiết theo cỡ cược. Đường xanh là equity bạn có. Vùng đỏ là mọi lần theo bị lỗ kỳ vọng. Bề mặt 3D là lời lỗ kỳ vọng khi theo, theo equity và cỡ cược. Mặt nằm dưới 0 là tiền bạn đang tặng.

## Mặt tối

Thắng một ván khiến bạn nhớ mãi. Ba, bốn ván thua lặng lẽ thì quên. Mỗi lần theo cược bằng pot, kỳ vọng mất {ev_call_pot} phần trăm pot.

## Mang về

Một quyết định đúng có thể ra kết quả xấu, và ngược lại. Hãy chấm điểm quyết định bằng kỳ vọng, không bằng kết quả.

## video_defaults

```json
{
  "tag": "POT ODDS",
  "title": "Theo bài vì cảm giác là ném tiền qua cửa sổ",
  "hook": "Bạn theo bài vì cảm giác. Toán nói bạn vừa ném tiền qua cửa sổ.",
  "kicker": "Poker theory",
  "wiki": {
    "title": "Pot odds và equity",
    "en": "Pot odds · equity",
    "lines": [
      "Pot odds: số tiền phải bỏ ra so với số tiền có thể thắng.",
      "Equity: xác suất bài của bạn thắng.",
      "Theo khi equity lớn hơn tỷ lệ pot odds đòi hỏi."
    ],
    "source": "Wikipedia: Pot odds",
    "say": "Pot odds là số tiền phải bỏ ra so với số tiền có thể thắng. Chỉ theo khi xác suất thắng lớn hơn tỷ lệ đó."
  },
  "anim": {
    "kind": "cards",
    "hole": [
      "A♥",
      "K♥"
    ],
    "board": [
      "Q♥",
      "7♥",
      "2♣",
      "9♠"
    ],
    "label": "Chờ thùng: {outs} lá cứu bạn"
  },
  "beats": [
    "Bạn có bốn lá cơ, cần thêm một lá cơ. Còn {outs} lá như vậy. Với một lá cuối, xác suất trúng là {eq_one}.",
    "Đối thủ cược nửa pot: bạn cần {need_half} để theo có lời. Cược bằng pot: cần {need_pot}. Bạn chỉ có {eq_one}.",
    "Đường cam là equity cần thiết theo cỡ cược. Đường xanh là equity bạn có. Vùng đỏ là mọi lần theo bị lỗ kỳ vọng.",
    "Bề mặt 3D là lời lỗ kỳ vọng khi theo, theo equity và cỡ cược. Mặt nằm dưới 0 là tiền bạn đang tặng."
  ],
  "dark": "Thắng một ván khiến bạn nhớ mãi. Ba, bốn ván thua lặng lẽ thì quên. Mỗi lần theo cược bằng pot, kỳ vọng mất {ev_call_pot} phần trăm pot.",
  "takeaway": "Một quyết định đúng có thể ra kết quả xấu, và ngược lại. Hãy chấm điểm quyết định bằng kỳ vọng, không bằng kết quả.",
  "myth": "Còn cơ hội trúng là cứ theo, biết đâu.",
  "fact": "Sai. Chờ thùng một lá có {eq_one}. Theo cược bằng pot cần {need_pot}: lỗ kỳ vọng mỗi lần.",
  "story": [
    {
      "at": 0.15,
      "label": "Cược nhỏ",
      "say": "Cược nhỏ, theo vẫn có lời."
    },
    {
      "at": 0.35,
      "label": "Điểm gãy",
      "say": "Từ khoảng một phần ba pot, theo bắt đầu lỗ."
    },
    {
      "at": 1.0,
      "label": "Cược lớn",
      "say": "Cược gấp đôi pot, cần tới {need_double}."
    }
  ],
  "formula": "\\mathrm{equity\\ cần}=\\frac{B}{P+2B}",
  "formula_numeric": "\\frac{1}{1+2}=<<need_pot>>",
  "symbols": [
    {
      "sym": "B",
      "say": "Cỡ cược phải theo."
    },
    {
      "sym": "P",
      "say": "Pot trước khi cược."
    }
  ],
  "outputs": [
    {
      "label": "outs",
      "key": "outs"
    },
    {
      "label": "equity 1 lá",
      "key": "eq_one"
    },
    {
      "label": "cần, cược nửa pot",
      "key": "need_half"
    },
    {
      "label": "cần, cược bằng pot",
      "key": "need_pot",
      "highlight": true
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Còn {outs} lá, theo luôn!”",
    "punch": "Toán: “Cần {need_pot}, bạn có {eq_one}.”",
    "truth": "Theo cược bằng pot khi chỉ có {eq_one} equity là lỗ kỳ vọng mỗi lần."
  },
  "caption": "Pot odds: vì sao theo bài theo cảm giác là lỗ kỳ vọng. Mô phỏng 200.000 lượt rút bài. Nội dung giáo dục về xác suất và ra quyết định, không cổ vũ cờ bạc.",
  "hashtags": [
    "poker",
    "potodds",
    "xacsuat",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "200.000"
  ],
  "formula_parts": [
    "\\mathrm{equity\\ cần}=\\frac{B}{P+2B}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Chờ thùng: {outs} lá cứu bạn",
  "max_seconds": 90
}
```
