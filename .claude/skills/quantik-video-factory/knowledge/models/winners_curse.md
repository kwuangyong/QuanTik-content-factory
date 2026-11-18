# Thắng đấu giá thường là thua

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `winners_curse_demo`. Style gợi ý: `dark-truth`.

## Là gì

Capen, Clapp và Campbell mô tả năm 1971. Các công ty dầu thắng đấu giá lô thăm dò nhưng lãi thấp bất ngờ. Người trả cao nhất thường là người đánh giá quá lạc quan nhất.

Nguồn: Capen, Clapp & Campbell (1971), Journal of Petroleum Technology

## Ý chính

Thắng đấu giá thường là thua. Người thắng là người ước lượng sai nhiều nhất.

Mười người đấu giá một món giá trị thật là {value}. Ai cũng ước lượng, có người cao có người thấp. Người cao nhất thắng. Ước lượng trung bình đúng, sai số {noise}. Nhưng với 10 người, người thắng trả dư trung bình {over10}, tức {over10_pct}. Càng đông người đấu giá, người thắng càng trả dư: 2 người dư {over2}, 20 người dư {over20}. Bề mặt 3D: số người đấu giá và độ nhiễu ước lượng cùng đẩy mức trả dư lên.

## Mặt tối

Bạn vui vì thắng, nhưng chính việc thắng là bằng chứng bạn lạc quan hơn mọi người. Cổ phiếu đang được săn đón nhất cũng chịu cùng một lời nguyền.

## Mang về

Khi thắng một cuộc tranh giành đông người, hãy hỏi: vì sao không ai khác chịu trả mức này?

## video_defaults

```json
{
  "tag": "ĐẤU GIÁ",
  "title": "Thắng đấu giá thường là thua",
  "hook": "Thắng đấu giá thường là thua. Người thắng là người ước lượng sai nhiều nhất.",
  "kicker": "Lời nguyền người thắng",
  "wiki": {
    "title": "Lời nguyền người thắng",
    "en": "Winner's curse",
    "lines": [
      "Capen, Clapp và Campbell mô tả năm 1971.",
      "Các công ty dầu thắng đấu giá lô thăm dò nhưng lãi thấp bất ngờ.",
      "Người trả cao nhất thường là người đánh giá quá lạc quan nhất."
    ],
    "source": "Capen, Clapp & Campbell (1971), Journal of Petroleum Technology",
    "say": "Năm 1971, ba kỹ sư dầu khí nhận ra các công ty thắng đấu giá lô dầu lại thường lãi thấp bất ngờ."
  },
  "anim": {
    "kind": "gavel",
    "n": 10,
    "label": "Người thắng: ước lượng cao nhất, không phải đúng nhất"
  },
  "beats": [
    "Mười người đấu giá một món giá trị thật là {value}. Ai cũng ước lượng, có người cao có người thấp. Người cao nhất thắng.",
    "Ước lượng trung bình đúng, sai số {noise}. Nhưng với 10 người, người thắng trả dư trung bình {over10}, tức {over10_pct}.",
    "Càng đông người đấu giá, người thắng càng trả dư: 2 người dư {over2}, 20 người dư {over20}.",
    "Bề mặt 3D: số người đấu giá và độ nhiễu ước lượng cùng đẩy mức trả dư lên."
  ],
  "dark": "Bạn vui vì thắng, nhưng chính việc thắng là bằng chứng bạn lạc quan hơn mọi người. Cổ phiếu đang được săn đón nhất cũng chịu cùng một lời nguyền.",
  "takeaway": "Khi thắng một cuộc tranh giành đông người, hãy hỏi: vì sao không ai khác chịu trả mức này?",
  "myth": "Thắng đấu giá là mua được món hời.",
  "fact": "Thường ngược lại. Mười người đấu giá, người thắng trả dư trung bình {over10_pct} giá trị thật.",
  "story": [
    {
      "at": 0.1,
      "label": "Ít người",
      "say": "Hai người: trả dư {over2}."
    },
    {
      "at": 0.35,
      "label": "Đông dần",
      "say": "Mười người: trả dư {over10}."
    },
    {
      "at": 1.0,
      "label": "Rất đông",
      "say": "Càng đông, người thắng càng là kẻ lạc quan cực đoan."
    }
  ],
  "formula": "E[\\max_i \\hat{V}_i]>V",
  "formula_numeric": "<<value>>+<<over10>>>{<<value>>}",
  "symbols": [
    {
      "sym": "\\hat{V}_i",
      "say": "Ước lượng của người thứ i."
    },
    {
      "sym": "V",
      "say": "Giá trị thật."
    }
  ],
  "outputs": [
    {
      "label": "giá trị thật",
      "key": "value"
    },
    {
      "label": "trả dư, 2 người",
      "key": "over2"
    },
    {
      "label": "trả dư, 10 người",
      "key": "over10",
      "highlight": true
    },
    {
      "label": "trả dư, 20 người",
      "key": "over20"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Thắng đấu giá rồi!”",
    "punch": "Thị trường: “Chúc mừng, bạn trả dư.”",
    "truth": "Mười người đấu giá, người thắng trả dư {over10_pct}."
  },
  "caption": "Lời nguyền người thắng: vì sao thắng đấu giá thường là trả dư. Mô phỏng 20.000 cuộc đấu giá. Nội dung giáo dục về lý thuyết trò chơi, không phải khuyến nghị.",
  "hashtags": [
    "lythuyettrochoi",
    "winnerscurse",
    "tamlyhoc",
    "QuanTik",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1971",
    "10 người",
    "2 người",
    "20 người",
    "Mười",
    "20.000"
  ],
  "formula_parts": [
    "E[\\max_i \\hat{V}_i]>V"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Người thắng: ước lượng cao nhất, không phải đúng nhất",
  "max_seconds": 90
}
```
