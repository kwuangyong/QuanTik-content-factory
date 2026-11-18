# Sút phạt đền: đoán được là thua

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `penalty_demo`. Style gợi ý: `dark-truth`.

## Là gì

John Nash chứng minh năm 1950: mọi trò chơi hữu hạn đều có cân bằng. Chiến lược hỗn hợp: chọn ngẫu nhiên theo tỷ lệ tối ưu. Palacios-Huerta năm 2003 thấy cầu thủ chuyên nghiệp sút gần đúng tỷ lệ này.

Nguồn: Nash (1950), PNAS; Palacios-Huerta (2003), Review of Economic Studies

## Ý chính

Cầu thủ luôn sút về góc sở trường là đang tặng bàn cho thủ môn.

Giả định: sút góc trái mà thủ môn đoán đúng thì vào {ll}. Sút phải mà đoán đúng vào {rr}. Đoán sai thì gần như chắc vào. Code giải cân bằng: sút trái {p_left}, sút phải {p_right}. Tỷ lệ ghi bàn lúc đó là {score_eq}, thủ môn bay đâu cũng vậy. Hai đường là hai hướng bay của thủ môn. Điểm cam là nơi chúng cắt nhau: thủ môn không còn đoán được gì. Bề mặt 3D là xác suất ghi bàn theo tỷ lệ của cả hai bên. Điểm yên ngựa ở giữa chính là cân bằng Nash.

## Mặt tối

Luôn sút góc mạnh nhất, đối thủ sẽ học ra và tỷ lệ vào chỉ còn {score_always_right}. Ngẫu nhiên đúng cách tăng thêm {gain_vs_pure}.

## Mang về

Khi đối thủ quan sát bạn, dễ đoán là điểm yếu. Ngẫu nhiên có tính toán là một chiến lược, không phải may rủi.

## video_defaults

```json
{
  "tag": "NASH",
  "title": "Sút phạt đền: đoán được là thua",
  "hook": "Cầu thủ luôn sút về góc sở trường là đang tặng bàn cho thủ môn.",
  "kicker": "Cân bằng Nash",
  "wiki": {
    "title": "Cân bằng Nash, chiến lược hỗn hợp",
    "en": "Nash equilibrium · mixed strategy",
    "lines": [
      "John Nash chứng minh năm 1950: mọi trò chơi hữu hạn đều có cân bằng.",
      "Chiến lược hỗn hợp: chọn ngẫu nhiên theo tỷ lệ tối ưu.",
      "Palacios-Huerta năm 2003 thấy cầu thủ chuyên nghiệp sút gần đúng tỷ lệ này."
    ],
    "source": "Nash (1950), PNAS; Palacios-Huerta (2003), Review of Economic Studies",
    "say": "John Nash chứng minh năm 1950: mọi trò chơi hữu hạn đều có một điểm cân bằng, đôi khi là chọn ngẫu nhiên theo tỷ lệ."
  },
  "anim": {
    "kind": "goal",
    "keeper": -1,
    "ball": 1,
    "label": "Thủ môn đoán sai hướng: bàn thắng"
  },
  "beats": [
    "Giả định: sút góc trái mà thủ môn đoán đúng thì vào {ll}. Sút phải mà đoán đúng vào {rr}. Đoán sai thì gần như chắc vào.",
    "Code giải cân bằng: sút trái {p_left}, sút phải {p_right}. Tỷ lệ ghi bàn lúc đó là {score_eq}, thủ môn bay đâu cũng vậy.",
    "Hai đường là hai hướng bay của thủ môn. Điểm cam là nơi chúng cắt nhau: thủ môn không còn đoán được gì.",
    "Bề mặt 3D là xác suất ghi bàn theo tỷ lệ của cả hai bên. Điểm yên ngựa ở giữa chính là cân bằng Nash."
  ],
  "dark": "Luôn sút góc mạnh nhất, đối thủ sẽ học ra và tỷ lệ vào chỉ còn {score_always_right}. Ngẫu nhiên đúng cách tăng thêm {gain_vs_pure}.",
  "takeaway": "Khi đối thủ quan sát bạn, dễ đoán là điểm yếu. Ngẫu nhiên có tính toán là một chiến lược, không phải may rủi.",
  "myth": "Cứ sút về góc mình mạnh nhất là tối ưu.",
  "fact": "Sai. Luôn sút một hướng chỉ vào {score_always_right}. Trộn {p_left} trái, {p_right} phải thì vào {score_eq}.",
  "story": [
    {
      "at": 0.4,
      "label": "Lệch trái",
      "say": "Sút trái quá ít, thủ môn cứ bay phải."
    },
    {
      "at": 0.75,
      "label": "Cân bằng",
      "say": "Sút trái {p_left}: thủ môn bay đâu cũng như nhau."
    },
    {
      "at": 1.0,
      "label": "Lệch phải",
      "say": "Sút trái quá nhiều, thủ môn lại có lợi."
    }
  ],
  "formula": "p^*=\\frac{G_{RR}-G_{RL}}{G_{LL}-G_{RL}-G_{LR}+G_{RR}}",
  "formula_numeric": "p^*=<<p_left>>",
  "symbols": [
    {
      "sym": "p^*",
      "say": "Tỷ lệ sút trái tối ưu."
    },
    {
      "sym": "G",
      "say": "Xác suất ghi bàn từng tình huống."
    }
  ],
  "outputs": [
    {
      "label": "sút trái",
      "key": "p_left"
    },
    {
      "label": "sút phải",
      "key": "p_right"
    },
    {
      "label": "ghi bàn ở cân bằng",
      "key": "score_eq",
      "highlight": true
    },
    {
      "label": "luôn sút phải",
      "key": "score_always_right"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Cầu thủ: “Góc sở trường, chắc ăn!”",
    "punch": "Thủ môn đã xem băng hình.",
    "truth": "Luôn sút một hướng: vào {score_always_right}. Trộn theo cân bằng Nash: {score_eq}."
  },
  "caption": "Vì sao cầu thủ giỏi phải sút ngẫu nhiên? Cân bằng Nash trong phạt đền, giải bằng code. Số liệu xác suất là giả định minh hoạ. Nội dung giáo dục về lý thuyết trò chơi.",
  "hashtags": [
    "nash",
    "bongda",
    "lythuyettrochoi",
    "QuanTik",
    "tamlyhoc",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1950",
    "2003"
  ],
  "formula_parts": [
    "p^*=\\frac{G_{RR}-G_{RL}}{G_{LL}-G_{RL}-G_{LR}+G_{RR}}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Thủ môn đoán sai hướng: bàn thắng",
  "max_seconds": 90
}
```
