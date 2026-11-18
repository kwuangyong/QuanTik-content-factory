# Kẻ phản bội thắng từng ván, nhưng thua cả giải

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `prisoners_demo`. Style gợi ý: `dark-truth`.

## Là gì

Flood và Dresher ở RAND đặt ra năm 1950. Albert Tucker đặt tên và kể thành chuyện hai tù nhân. Robert Axelrod tổ chức giải đấu chiến thuật năm 1980.

Nguồn: Wikipedia: Prisoner's dilemma; Axelrod, The Evolution of Cooperation (1984)

## Ý chính

Người tốt bụng nhất thua. Kẻ phản bội cũng thua. Vậy ai thắng?

Cùng hợp tác: mỗi bên {pay_cc} điểm. Mình phản bội khi đối thủ hợp tác: mình {pay_dc}, họ {pay_cd}. Nhìn từng ván, phản bội luôn lợi. Nhưng chơi lặp lại {rounds} ván. Ăn miếng trả miếng đạt {s_tft} điểm, gấp {tft_vs_defect} kẻ luôn phản bội. Bốn chiến thuật đấu vòng tròn. Luôn phản bội về chót. Luôn hợp tác bị bóc lột. Ăn miếng trả miếng và thù dai đứng đầu. Bề mặt 3D là điểm kỳ vọng theo mức hợp tác của hai bên. Góc cao nhất cần cả hai cùng hợp tác.

## Mặt tối

Kẻ phản bội thắng mọi trận đối đầu, nhưng thua cả giải. Họ không thấy, vì họ chỉ đếm từng ván.

## Mang về

Trong trò chơi lặp lại, uy tín là tài sản. Tử tế trước, trả đũa ngay, rồi tha thứ.

## video_defaults

```json
{
  "tag": "TÙ NHÂN",
  "title": "Kẻ phản bội thắng từng ván, nhưng thua cả giải",
  "hook": "Người tốt bụng nhất thua. Kẻ phản bội cũng thua. Vậy ai thắng?",
  "kicker": "Thế lưỡng nan tù nhân",
  "wiki": {
    "title": "Thế lưỡng nan của tù nhân",
    "en": "Prisoner's dilemma",
    "lines": [
      "Flood và Dresher ở RAND đặt ra năm 1950.",
      "Albert Tucker đặt tên và kể thành chuyện hai tù nhân.",
      "Robert Axelrod tổ chức giải đấu chiến thuật năm 1980."
    ],
    "source": "Wikipedia: Prisoner's dilemma; Axelrod, The Evolution of Cooperation (1984)",
    "say": "Thế lưỡng nan tù nhân ra đời ở RAND năm 1950. Ba mươi năm sau, Robert Axelrod tổ chức một giải đấu giữa các chiến thuật."
  },
  "anim": {
    "kind": "matrix",
    "top": "điểm của mình / đối thủ",
    "rows": [
      "Hợp tác",
      "Phản bội"
    ],
    "cols": [
      "Hợp tác",
      "Phản bội"
    ],
    "cells": [
      [
        "{pay_cc} / {pay_cc}",
        "{pay_cd} / {pay_dc}"
      ],
      [
        "{pay_dc} / {pay_cd}",
        "{pay_dd} / {pay_dd}"
      ]
    ],
    "hl": [
      1,
      0
    ],
    "label": "Mỗi ván, phản bội luôn có lợi hơn"
  },
  "beats": [
    "Cùng hợp tác: mỗi bên {pay_cc} điểm. Mình phản bội khi đối thủ hợp tác: mình {pay_dc}, họ {pay_cd}. Nhìn từng ván, phản bội luôn lợi.",
    "Nhưng chơi lặp lại {rounds} ván. Ăn miếng trả miếng đạt {s_tft} điểm, gấp {tft_vs_defect} kẻ luôn phản bội.",
    "Bốn chiến thuật đấu vòng tròn. Luôn phản bội về chót. Luôn hợp tác bị bóc lột. Ăn miếng trả miếng và thù dai đứng đầu.",
    "Bề mặt 3D là điểm kỳ vọng theo mức hợp tác của hai bên. Góc cao nhất cần cả hai cùng hợp tác."
  ],
  "dark": "Kẻ phản bội thắng mọi trận đối đầu, nhưng thua cả giải. Họ không thấy, vì họ chỉ đếm từng ván.",
  "takeaway": "Trong trò chơi lặp lại, uy tín là tài sản. Tử tế trước, trả đũa ngay, rồi tha thứ.",
  "myth": "Muốn thắng thì phải chơi xấu, người tốt luôn thiệt.",
  "fact": "Sai trong trò chơi lặp lại. Ăn miếng trả miếng đạt {s_tft} điểm, luôn phản bội chỉ {s_defect}.",
  "story": [
    {
      "at": 0.4,
      "label": "Xuất phát",
      "say": "Bốn chiến thuật, mỗi cặp đấu {rounds} ván."
    },
    {
      "at": 0.8,
      "label": "Bóc lột",
      "say": "Kẻ phản bội ăn điểm của người luôn hợp tác."
    },
    {
      "at": 1.0,
      "label": "Tổng kết",
      "say": "Ăn miếng trả miếng {s_tft} điểm, luôn phản bội {s_defect}."
    }
  ],
  "formula": "T>R>P>S:\\ 5>3>1>0",
  "formula_numeric": "<<pay_dc>>><<pay_cc>>><<pay_dd>>><<pay_cd>>",
  "symbols": [
    {
      "sym": "T",
      "say": "Cám dỗ phản bội."
    },
    {
      "sym": "R",
      "say": "Phần thưởng khi cùng hợp tác."
    }
  ],
  "outputs": [
    {
      "label": "luôn hợp tác",
      "key": "s_coop"
    },
    {
      "label": "luôn phản bội",
      "key": "s_defect"
    },
    {
      "label": "ăn miếng trả miếng",
      "key": "s_tft",
      "highlight": true
    },
    {
      "label": "thù dai",
      "key": "s_grudge"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Kẻ phản bội: “Mình thắng mọi trận!”",
    "punch": "Bảng tổng: hạng chót.",
    "truth": "Ăn miếng trả miếng {s_tft} điểm, luôn phản bội {s_defect}."
  },
  "caption": "Thế lưỡng nan tù nhân và giải đấu của Axelrod: vì sao kẻ phản bội thắng từng trận mà thua cả giải. Code đấu vòng tròn chạy thật. Nội dung giáo dục về lý thuyết trò chơi.",
  "hashtags": [
    "lythuyettrochoi",
    "gametheory",
    "QuanTik",
    "tamlyhoc",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1950",
    "1980",
    "1984",
    "5>3>1>0",
    "Ba mươi năm"
  ],
  "formula_parts": [
    "T>R>P>S:\\ 5>3>1>0"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Mỗi ván, phản bội luôn có lợi hơn",
  "max_seconds": 90
}
```
