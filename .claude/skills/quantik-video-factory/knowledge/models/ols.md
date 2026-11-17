# OLS — Hồi quy bình phương nhỏ nhất

## Định nghĩa
OLS (Ordinary Least Squares) chọn đường thẳng y = a + b·x sao cho tổng bình phương phần dư nhỏ nhất. Nghiệm đóng: β̂ = (XᵀX)⁻¹Xᵀy. Phương pháp do Legendre (1805) và Gauss công bố.

## Đọc thế nào
- b̂: x tăng 1 đơn vị thì y trung bình đổi b̂. R²: tỷ lệ phương sai của y được giải thích.
- Beta cổ phiếu, hệ số mean-reversion AR(1), độ dốc xu hướng trong QuanTik đều là OLS.

## Sai lầm hay gặp
- Bình phương phạt nặng sai số lớn → một điểm ngoại lai kéo lệch cả đường.
- Hồi quy ra hệ số ≠ quan hệ nhân quả. R² cao trên dữ liệu chuỗi thời gian có xu hướng có thể là hồi quy giả.

## video_defaults

```json
{
  "tag": "OLS",
  "kicker": "Hồi quy",
  "title": "Một điểm dữ liệu có thể bẻ cong cả đường hồi quy",
  "hook": "Thêm đúng một điểm dữ liệu, độ dốc tụt từ {b_hat} xuống {b_out}. Đó là OLS.",
  "formula": "\\hat\\beta = (X^\\top X)^{-1} X^\\top y",
  "beats": [
    "OLS tìm đường thẳng có tổng bình phương phần dư nhỏ nhất. Code giải đúng một dòng: X chuyển vị nhân X, nghịch đảo, nhân X chuyển vị y.",
    "Với {n} điểm, độ dốc ước lượng là {b_hat}, R bình phương {r2}.",
    "Mỗi vạch xám là một phần dư. Đường cam làm tổng bình phương các vạch nhỏ nhất. Thêm chấm đỏ, đường đứt kéo lệch hẳn.",
    "3D là sai số theo hệ số chặn và độ dốc: một cái bát. OLS là đáy bát."
  ],
  "outputs": [
    {
      "label": "số điểm",
      "key": "n"
    },
    {
      "label": "độ dốc b̂",
      "key": "b_hat",
      "highlight": true
    },
    {
      "label": "R²",
      "key": "r2"
    },
    {
      "label": "b̂ khi thêm 1 ngoại lai",
      "key": "b_out"
    }
  ],
  "takeaway": "OLS mạnh và nhanh, nhưng nghe lời điểm ngoại lai. Luôn nhìn phần dư.",
  "cta": "Xem độ dốc xu hướng và R² trong Phân tích Quant tại quantik.io.vn",
  "caption": "OLS là nền của beta, xu hướng và rất nhiều mô hình quant. Nhưng một điểm ngoại lai đủ kéo lệch độ dốc. Code chạy thật.",
  "hashtags": [
    "quant",
    "hoiquy",
    "OLS",
    "thongke",
    "QuanTik"
  ],
  "thumb": {
    "tag": "Hồi quy OLS",
    "headline": [
      {
        "t": "THÊM 1 ĐIỂM",
        "size": 150
      },
      {
        "t": "ĐỘ DỐC TỤT",
        "size": 150
      },
      {
        "t": "[g]{b_hat}[/g] → [o]{b_out}[/o]",
        "size": 150
      }
    ],
    "pill": "Bình phương nhỏ nhất · code Python",
    "labels": [
      {
        "label": "R²",
        "value": "{r2}",
        "color": "green"
      },
      {
        "label": "Ngoại lai",
        "value": "{b_out}",
        "color": "orange"
      }
    ]
  }
}
```
