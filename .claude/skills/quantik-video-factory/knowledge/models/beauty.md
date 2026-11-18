# Thị trường là cuộc thi đoán người khác nghĩ gì

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `beauty_demo`. Style gợi ý: `dark-truth`.

## Là gì

Keynes ví von trong cuốn Lý thuyết tổng quát năm 1936. Người chơi không chọn gương mặt mình thấy đẹp nhất. Họ chọn gương mặt họ nghĩ người khác sẽ chọn.

Nguồn: Keynes (1936), The General Theory, chương 12

## Ý chính

Thị trường không thưởng người đúng. Nó thưởng người đoán đúng đám đông nghĩ gì.

Trò chơi: mọi người đoán một số từ 0 đến 100. Ai gần nhất với hai phần ba trung bình thì thắng. Đoán bừa thì trung bình {l0}. Nghĩ một bước: {l1}. Hai bước: {l2}. Lý thuyết hoàn hảo thì về {nash}. Code cho {n} người với các cấp suy luận khác nhau. Trung bình {avg}, con số thắng là {winner}. Không phải {nash}. Bề mặt 3D: con số thắng phụ thuộc vào tỷ lệ người đoán bừa và người nghĩ một bước trong đám đông.

## Mặt tối

Người tính đúng lý thuyết đoán {nash} và thua. Người thắng chỉ cần nghĩ hơn đám đông đúng một, hai bước. Giá cả phản ánh tâm lý đám đông, không chỉ giá trị.

## Mang về

Đúng về giá trị chưa đủ. Còn phải hiểu người khác đang nghĩ gì, và nhớ rằng đám đông có thể sai lâu hơn bạn chịu được.

## video_defaults

```json
{
  "tag": "KEYNES",
  "title": "Thị trường là cuộc thi đoán người khác nghĩ gì",
  "hook": "Thị trường không thưởng người đúng. Nó thưởng người đoán đúng đám đông nghĩ gì.",
  "kicker": "Cuộc thi sắc đẹp Keynes",
  "wiki": {
    "title": "Cuộc thi sắc đẹp của Keynes",
    "en": "Keynesian beauty contest",
    "lines": [
      "Keynes ví von trong cuốn Lý thuyết tổng quát năm 1936.",
      "Người chơi không chọn gương mặt mình thấy đẹp nhất.",
      "Họ chọn gương mặt họ nghĩ người khác sẽ chọn."
    ],
    "source": "Keynes (1936), The General Theory, chương 12",
    "say": "Năm 1936, Keynes ví thị trường như cuộc thi sắc đẹp: bạn không chọn gương mặt đẹp nhất, mà chọn gương mặt người khác sẽ chọn."
  },
  "anim": {
    "kind": "steps",
    "items": [
      [
        "đoán bừa",
        "{l0}"
      ],
      [
        "nghĩ 1 bước",
        "{l1}"
      ],
      [
        "2 bước",
        "{l2}"
      ],
      [
        "3 bước",
        "{l3}"
      ],
      [
        "Nash",
        "{nash}"
      ]
    ],
    "hl": 2,
    "label": "Mỗi bước suy luận nhân thêm hai phần ba"
  },
  "beats": [
    "Trò chơi: mọi người đoán một số từ 0 đến 100. Ai gần nhất với hai phần ba trung bình thì thắng.",
    "Đoán bừa thì trung bình {l0}. Nghĩ một bước: {l1}. Hai bước: {l2}. Lý thuyết hoàn hảo thì về {nash}.",
    "Code cho {n} người với các cấp suy luận khác nhau. Trung bình {avg}, con số thắng là {winner}. Không phải {nash}.",
    "Bề mặt 3D: con số thắng phụ thuộc vào tỷ lệ người đoán bừa và người nghĩ một bước trong đám đông."
  ],
  "dark": "Người tính đúng lý thuyết đoán {nash} và thua. Người thắng chỉ cần nghĩ hơn đám đông đúng một, hai bước. Giá cả phản ánh tâm lý đám đông, không chỉ giá trị.",
  "takeaway": "Đúng về giá trị chưa đủ. Còn phải hiểu người khác đang nghĩ gì, và nhớ rằng đám đông có thể sai lâu hơn bạn chịu được.",
  "myth": "Thị trường chỉ quan tâm giá trị thật của doanh nghiệp.",
  "fact": "Không chỉ vậy. Trong trò chơi Keynes, lý thuyết nói {nash} nhưng con số thắng là {winner}.",
  "story": [
    {
      "at": 0.4,
      "label": "Đám đông",
      "say": "Các con số chụm quanh {l0}, {l1} và {l2}."
    },
    {
      "at": 0.8,
      "label": "Trung bình",
      "say": "Trung bình là {avg}."
    },
    {
      "at": 1.0,
      "label": "Con số thắng",
      "say": "Hai phần ba trung bình: {target}."
    }
  ],
  "formula": "x^*=\\frac{2}{3}\\,\\bar{x}",
  "formula_numeric": "\\frac{2}{3}\\cdot<<avg>>=<<target>>",
  "symbols": [
    {
      "sym": "\\bar{x}",
      "say": "Trung bình mọi người đoán."
    }
  ],
  "outputs": [
    {
      "label": "đoán bừa",
      "key": "l0"
    },
    {
      "label": "nghĩ 1 bước",
      "key": "l1"
    },
    {
      "label": "trung bình",
      "key": "avg"
    },
    {
      "label": "con số thắng",
      "key": "winner",
      "highlight": true
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Thiên tài lý thuyết: “Đáp án là {nash}.”",
    "punch": "Con số thắng: {winner}.",
    "truth": "Thắng là đoán đúng đám đông, không phải đoán đúng lý thuyết."
  },
  "caption": "Cuộc thi sắc đẹp của Keynes: vì sao thị trường thưởng người hiểu đám đông. Mô phỏng 1.000 người chơi. Nội dung giáo dục về lý thuyết trò chơi.",
  "hashtags": [
    "keynes",
    "lythuyettrochoi",
    "tamlydamdong",
    "QuanTik",
    "tamlyhoc",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1936",
    "0 đến 100",
    "12",
    "1.000"
  ],
  "formula_parts": [
    "x^*=\\frac{2}{3}\\,\\bar{x}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Mỗi bước suy luận nhân thêm hai phần ba",
  "max_seconds": 90
}
```
