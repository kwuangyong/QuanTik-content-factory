# Tín hiệu đúng 90% vẫn báo nhầm phần lớn

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `base_rate_demo`. Style gợi ý: `dark-truth`.

## Là gì

Định lý Bayes được công bố năm 1763, sau khi Thomas Bayes qua đời. Kahneman và Tversky chỉ ra người ta thường bỏ qua tỷ lệ nền. Sự kiện càng hiếm, báo động càng hay nhầm.

Nguồn: Wikipedia: Base rate fallacy; Bayes (1763)

## Ý chính

Một tín hiệu đúng {acc} báo thị trường sắp sập. Xác suất sập thật chỉ {hit_exact}.

Mỗi hình là một phiên. Sự kiện sập chỉ xảy ra {base} số phiên. Màu xanh là báo đúng, màu đỏ là báo nhầm. Đỏ nhiều hơn hẳn. Tín hiệu đúng {acc}. Nhưng trong 1.000 phiên, nó kêu {alarms_1000} lần, chỉ {true_1000} lần là thật. Code mô phỏng {n} phiên ra {hit_sim}. Ba đường là ba mức độ hiếm của sự kiện. Sự kiện càng hiếm, độ chính xác phải cực cao báo động mới đáng tin. Bề mặt 3D: xác suất báo động là thật theo tần suất sự kiện và độ chính xác.

## Mặt tối

{false_share} số lần báo động là nhầm. Nội dung giật tít "sắp sập" sống nhờ việc bạn quên mất sự kiện đó hiếm đến mức nào.

## Mang về

Gặp tín hiệu nào cũng hỏi hai câu: nó đúng bao nhiêu, và sự kiện đó vốn hiếm đến đâu?

## video_defaults

```json
{
  "tag": "BAYES",
  "title": "Tín hiệu đúng 90% vẫn báo nhầm phần lớn",
  "hook": "Một tín hiệu đúng {acc} báo thị trường sắp sập. Xác suất sập thật chỉ {hit_exact}.",
  "kicker": "Bỏ qua tỷ lệ nền",
  "wiki": {
    "title": "Ngụy biện tỷ lệ nền",
    "en": "Base rate fallacy",
    "lines": [
      "Định lý Bayes được công bố năm 1763, sau khi Thomas Bayes qua đời.",
      "Kahneman và Tversky chỉ ra người ta thường bỏ qua tỷ lệ nền.",
      "Sự kiện càng hiếm, báo động càng hay nhầm."
    ],
    "source": "Wikipedia: Base rate fallacy; Bayes (1763)",
    "say": "Định lý Bayes có từ năm 1763. Kahneman và Tversky chỉ ra: con người thường bỏ qua sự kiện đó hiếm đến mức nào."
  },
  "anim": {
    "kind": "crowd",
    "mode": "highlight",
    "hits": 4,
    "false": 22,
    "label": "{true_1000} báo đúng, {false_1000} báo nhầm, trên 1.000 lần"
  },
  "beats": [
    "Mỗi hình là một phiên. Sự kiện sập chỉ xảy ra {base} số phiên. Màu xanh là báo đúng, màu đỏ là báo nhầm. Đỏ nhiều hơn hẳn.",
    "Tín hiệu đúng {acc}. Nhưng trong 1.000 phiên, nó kêu {alarms_1000} lần, chỉ {true_1000} lần là thật. Code mô phỏng {n} phiên ra {hit_sim}.",
    "Ba đường là ba mức độ hiếm của sự kiện. Sự kiện càng hiếm, độ chính xác phải cực cao báo động mới đáng tin.",
    "Bề mặt 3D: xác suất báo động là thật theo tần suất sự kiện và độ chính xác."
  ],
  "dark": "{false_share} số lần báo động là nhầm. Nội dung giật tít \"sắp sập\" sống nhờ việc bạn quên mất sự kiện đó hiếm đến mức nào.",
  "takeaway": "Gặp tín hiệu nào cũng hỏi hai câu: nó đúng bao nhiêu, và sự kiện đó vốn hiếm đến đâu?",
  "myth": "Tín hiệu đúng {acc} thì khi nó kêu, {acc} là thật.",
  "fact": "Sai. Với sự kiện chỉ xảy ra {base} số phiên, báo động là thật chỉ {hit_exact}.",
  "story": [
    {
      "at": 0.4,
      "label": "Chính xác vừa",
      "say": "Độ chính xác bảy, tám mươi phần trăm: báo động gần như vô nghĩa."
    },
    {
      "at": 0.8,
      "label": "Đúng {acc}",
      "say": "Đúng {acc}, sự kiện {base}: chỉ {hit_exact}."
    },
    {
      "at": 1.0,
      "label": "Gần hoàn hảo",
      "say": "Phải gần hoàn hảo, báo động mới đáng tin."
    }
  ],
  "formula": "P(S\\mid B)=\\frac{P(B\\mid S)P(S)}{P(B)}",
  "formula_numeric": "\\frac{<<acc>>\\cdot<<base>>}{<<acc>>\\cdot<<base>>+<<false_share>>\\ldots}=<<hit_exact>>",
  "symbols": [
    {
      "sym": "P(S)",
      "say": "Tỷ lệ nền: sự kiện hiếm đến đâu."
    },
    {
      "sym": "P(B|S)",
      "say": "Độ chính xác tín hiệu."
    }
  ],
  "outputs": [
    {
      "label": "tỷ lệ nền",
      "key": "base"
    },
    {
      "label": "độ chính xác",
      "key": "acc"
    },
    {
      "label": "báo động là thật",
      "key": "hit_exact",
      "highlight": true
    },
    {
      "label": "mô phỏng",
      "key": "hit_sim"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Kênh tin: “Tín hiệu đúng {acc}, sắp sập!”",
    "punch": "Bayes: “Chỉ {hit_exact} thôi.”",
    "truth": "Sự kiện hiếm {base}, tín hiệu đúng {acc}: báo động là thật chỉ {hit_exact}."
  },
  "caption": "Tín hiệu đúng 90% nhưng báo nhầm phần lớn? Ngụy biện tỷ lệ nền và định lý Bayes, mô phỏng 100.000 phiên. Nội dung giáo dục về xác suất, không phải khuyến nghị.",
  "hashtags": [
    "bayes",
    "xacsuat",
    "tamlyhoc",
    "QuanTik",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "1763",
    "1.000",
    "90%",
    "100.000",
    "bảy, tám mươi"
  ],
  "formula_parts": [
    "P(S\\mid B)=\\frac{P(B\\mid S)P(S)}{P(B)}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "{true_1000} báo đúng, {false_1000} báo nhầm, trên 1.000 lần",
  "max_seconds": 90
}
```
