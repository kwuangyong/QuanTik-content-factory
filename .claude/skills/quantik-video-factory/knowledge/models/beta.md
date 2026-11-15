# Beta — Độ nhạy với thị trường

## Định nghĩa
β = Cov(r_cổ phiếu, r_thị trường) / Var(r_thị trường): thị trường đi 1% thì cổ phiếu trung bình đi β%. Là độ dốc hồi quy OLS của lợi suất cổ phiếu theo lợi suất thị trường.

## Đọc thế nào
- β > 1: khuếch đại thị trường; β < 1: phòng thủ hơn; β âm hiếm.
- β không phải toàn bộ rủi ro: phần biến động riêng (phần dư) không nằm trong β. Xem thêm tương quan.

## Sai lầm hay gặp
- β thấp = an toàn. Một mã β thấp vẫn có thể biến động mạnh vì lý do riêng.
- β ổn định mãi; thực tế β thay đổi theo giai đoạn và cửa sổ ước lượng.

## video_defaults

```json
{
  "tag": "BETA",
  "kicker": "Rủi ro thị trường",
  "title": "Cùng một thị trường, vì sao có mã rung gấp đôi?",
  "hook": "Thị trường giảm {mkt_worst}. Mã A giảm {a_worst}, mã B giảm {b_worst}. Vì sao?",
  "formula": "\\beta = \\frac{\\mathrm{Cov}(r_i, r_m)}{\\mathrm{Var}(r_m)}",
  "beats": [
    "Code tạo lợi suất thị trường, rồi hai mã: A ăn theo thị trường ít, B ăn theo nhiều. Beta là hiệp phương sai chia phương sai thị trường.",
    "Beta của A là {beta_a}, của B là {beta_b}. Ngày thị trường giảm {mkt_worst}, B giảm tới {b_worst}.",
    "Mỗi chấm là một ngày. Độ dốc đường xanh là beta của A, đường đỏ là beta của B.",
    "3D đặt ba đường lợi suất cộng dồn cạnh nhau: B phóng đại mọi nhịp của thị trường."
  ],
  "outputs": [
    {
      "label": "β mã A",
      "key": "beta_a"
    },
    {
      "label": "β mã B",
      "key": "beta_b",
      "highlight": true
    },
    {
      "label": "biến động năm thị trường",
      "key": "vol_m"
    }
  ],
  "takeaway": "Beta đo bạn ăn theo thị trường bao nhiêu, không đo toàn bộ rủi ro.",
  "cta": "Xem beta của từng mã trong Phân tích Quant tại quantik.io.vn",
  "caption": "Beta là độ dốc giữa lợi suất cổ phiếu và thị trường. Beta 1,8 nghĩa là thị trường đi 1%, mã đi trung bình 1,8%. Code tính thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "beta",
    "chungkhoan",
    "dautu",
    "QuanTik"
  ],
  "allowed_literals": [
    "1%"
  ],
  "thumb": {
    "tag": "Beta",
    "headline": [
      {
        "t": "THỊ TRƯỜNG GIẢM",
        "size": 120
      },
      {
        "t": "[o]{mkt_worst}[/o]",
        "size": 190
      },
      {
        "t": "MÃ B GIẢM [o]{b_worst}[/o]",
        "size": 120
      }
    ],
    "pill": "Beta = độ dốc theo thị trường · code Python",
    "labels": [
      {
        "label": "β mã A",
        "value": "{beta_a}",
        "color": "green"
      },
      {
        "label": "β mã B",
        "value": "{beta_b}",
        "color": "orange"
      }
    ]
  }
}
```
