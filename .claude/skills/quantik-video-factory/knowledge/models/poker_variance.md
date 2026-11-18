# Chơi giỏi vẫn lỗ cả tháng

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `poker_variance_demo`. Style gợi ý: `dark-truth`.

## Là gì

Đo kết quả dao động quanh kỳ vọng bao xa. Lợi thế nhỏ, phương sai lớn: cần rất nhiều lần mới lộ ra. Winrate trong poker đo bằng big blind trên 100 tay.

Nguồn: Wikipedia: Variance

## Ý chính

Một người chơi giỏi thật sự vẫn có thể lỗ suốt {hands_20k} tay. Không phải xui. Là toán.

Người chơi này có lợi thế thật: kỳ vọng thắng {winrate} big blind mỗi 100 tay. Nhưng độ lệch chuẩn là {sd}. Code cho {players} người cùng trình độ chơi {hands} tay. Sau {hands_20k} tay, {lose_20k} vẫn đang lỗ. Đường cam là kỳ vọng. Các đường xám là người thật. Cùng trình độ, có người lãi gấp ba, có người âm cả nghìn. Bề mặt 3D: winrate càng thấp, số tay cần để chắc là mình giỏi càng khổng lồ.

## Mặt tối

Chuỗi lỗ dài nhất trung vị là {dd_median} big blind, và một phần mười người gặp chuỗi lỗ hơn {dd_p90}. Nhiều người giỏi bỏ cuộc đúng lúc đó.

## Mang về

Đừng đánh giá kỹ năng qua vài tuần kết quả. Trên thị trường cũng vậy: mẫu ngắn chủ yếu là nhiễu.

## video_defaults

```json
{
  "tag": "VARIANCE",
  "title": "Chơi giỏi vẫn lỗ cả tháng",
  "hook": "Một người chơi giỏi thật sự vẫn có thể lỗ suốt {hands_20k} tay. Không phải xui. Là toán.",
  "kicker": "Phương sai",
  "wiki": {
    "title": "Phương sai (variance)",
    "en": "Variance",
    "lines": [
      "Đo kết quả dao động quanh kỳ vọng bao xa.",
      "Lợi thế nhỏ, phương sai lớn: cần rất nhiều lần mới lộ ra.",
      "Winrate trong poker đo bằng big blind trên 100 tay."
    ],
    "source": "Wikipedia: Variance",
    "say": "Phương sai đo kết quả dao động quanh kỳ vọng bao xa. Lợi thế nhỏ mà phương sai lớn thì cần rất nhiều lần mới lộ ra."
  },
  "anim": {
    "kind": "cards",
    "hole": [
      "Q♠",
      "Q♣"
    ],
    "board": [
      "A♦",
      "8♣",
      "3♥",
      "K♠",
      "J♦"
    ],
    "label": "Quyết định đúng, kết quả vẫn xấu"
  },
  "beats": [
    "Người chơi này có lợi thế thật: kỳ vọng thắng {winrate} big blind mỗi 100 tay. Nhưng độ lệch chuẩn là {sd}.",
    "Code cho {players} người cùng trình độ chơi {hands} tay. Sau {hands_20k} tay, {lose_20k} vẫn đang lỗ.",
    "Đường cam là kỳ vọng. Các đường xám là người thật. Cùng trình độ, có người lãi gấp ba, có người âm cả nghìn.",
    "Bề mặt 3D: winrate càng thấp, số tay cần để chắc là mình giỏi càng khổng lồ."
  ],
  "dark": "Chuỗi lỗ dài nhất trung vị là {dd_median} big blind, và một phần mười người gặp chuỗi lỗ hơn {dd_p90}. Nhiều người giỏi bỏ cuộc đúng lúc đó.",
  "takeaway": "Đừng đánh giá kỹ năng qua vài tuần kết quả. Trên thị trường cũng vậy: mẫu ngắn chủ yếu là nhiễu.",
  "myth": "Lỗ cả tháng nghĩa là mình chơi dở.",
  "fact": "Chưa chắc. {lose_20k} người có lợi thế thật vẫn lỗ sau {hands_20k} tay.",
  "story": [
    {
      "at": 0.2,
      "label": "Hỗn loạn",
      "say": "Vài nghìn tay đầu, ai cũng như ai."
    },
    {
      "at": 0.6,
      "label": "Tách dần",
      "say": "Đường kỳ vọng bắt đầu kéo đám đông lên."
    },
    {
      "at": 1.0,
      "label": "Vẫn có người lỗ",
      "say": "Sau {hands} tay, {lose_50k} vẫn âm."
    }
  ],
  "formula": "P(\\mathrm{lỗ})=\\Phi\\left(-\\frac{\\mu n}{\\sigma\\sqrt{n}}\\right)",
  "formula_numeric": "\\mu=<<winrate>>,\\ \\sigma=<<sd>>",
  "symbols": [
    {
      "sym": "\\mu",
      "say": "Kỳ vọng mỗi 100 tay."
    },
    {
      "sym": "\\sigma",
      "say": "Độ lệch chuẩn."
    }
  ],
  "outputs": [
    {
      "label": "winrate bb/100",
      "key": "winrate"
    },
    {
      "label": "độ lệch chuẩn",
      "key": "sd"
    },
    {
      "label": "lỗ sau 20.000 tay",
      "key": "lose_20k",
      "highlight": true
    },
    {
      "label": "chuỗi lỗ trung vị",
      "key": "dd_median"
    }
  ],
  "meme": {
    "format": "expectation-reality",
    "setup": "Kỳ vọng: giỏi là lãi đều",
    "punch": "Thực tế:",
    "truth": "{lose_20k} người có lợi thế thật vẫn lỗ sau {hands_20k} tay."
  },
  "caption": "Vì sao người giỏi vẫn có thể lỗ hàng tháng? Phương sai, mô phỏng 1.000 người chơi có lợi thế. Nội dung giáo dục về xác suất, không cổ vũ cờ bạc.",
  "hashtags": [
    "poker",
    "variance",
    "xacsuat",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "100 tay",
    "20.000",
    "1.000",
    "gấp ba"
  ],
  "formula_parts": [
    "P(\\mathrm{lỗ})=\\Phi\\left(-\\frac{\\mu n}{\\sigma\\sqrt{n}}\\right)"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Quyết định đúng, kết quả vẫn xấu",
  "max_seconds": 90
}
```
