# Max Drawdown — Sụt giảm tối đa

## Định nghĩa
Mức giảm lớn nhất từ một đỉnh xuống đáy sau đó trong cả giai đoạn: MDD = max(1 − giá/đỉnh trước đó).

## Toán của việc về bờ
Mất L thì phải tăng L/(1 − L) mới về lại đỉnh: mất 10% cần 11%, mất 30% cần 43%, mất 50% cần 100%, mất 80% cần 400%. Lỗ và lãi không đối xứng vì tính trên nền vốn khác nhau.

## Đọc thế nào
- Đi kèm thời gian "dưới nước" (số phiên chưa về đỉnh): cùng MDD nhưng hồi trong 1 tháng khác hồi trong 3 năm.
- Calmar = lợi nhuận năm / MDD.

## Sai lầm hay gặp
- Nghĩ "giảm 50% rồi tăng 50% là hoà". Thực tế còn 75%.
- Lấy MDD của backtest ngắn làm mức xấu nhất; giai đoạn dài hơn gần như luôn có MDD sâu hơn.

## video_defaults

```json
{
  "tag": "MAX DRAWDOWN",
  "kicker": "Rủi ro",
  "title": "Giảm 50% thì phải tăng bao nhiêu để về bờ?",
  "hook": "Giảm {loss_50} rồi tăng {loss_50}. Bạn nghĩ đã hoà vốn?",
  "formula": "\\text{cần tăng} = \\frac{L}{1-L}",
  "beats": [
    "Code đi theo đỉnh cao nhất từ trước tới nay, và đo giá đang thấp hơn đỉnh đó bao nhiêu phần trăm.",
    "Sụt giảm sâu nhất là {mdd}. Muốn về đỉnh phải tăng {need_mdd}, và mất {underwater_days} phiên dưới nước.",
    "Vùng đỏ là khoảng cách tới đỉnh. Chấm cam là đáy sâu nhất.",
    "3D: trục ngang là mức sụt, trục sâu là lãi mỗi năm, chiều cao là số năm để về đỉnh. Sụt càng sâu, núi càng dựng đứng."
  ],
  "outputs": [
    {
      "label": "sụt giảm tối đa",
      "key": "mdd"
    },
    {
      "label": "phải tăng để về đỉnh",
      "key": "need_mdd",
      "highlight": true
    },
    {
      "label": "số phiên dưới nước",
      "key": "underwater_days"
    }
  ],
  "takeaway": "Mất ít quan trọng hơn lãi nhiều: lỗ càng sâu, đường về càng dốc.",
  "cta": "Xem sụt giảm tối đa của từng mã trong Phân tích Quant tại quantik.io.vn",
  "caption": "Giảm 50% cần tăng 100% mới về bờ. Max drawdown là chỉ số rủi ro người mới hay bỏ qua nhất. Code tính thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "drawdown",
    "quanlyruiro",
    "chungkhoan",
    "QuanTik"
  ],
  "thumb": {
    "tag": "Max drawdown",
    "headline": [
      {
        "t": "GIẢM [o]{loss_50}[/o]",
        "size": 150
      },
      {
        "t": "CẦN TĂNG",
        "size": 150
      },
      {
        "t": "[o]{need_50}[/o] ĐỂ VỀ BỜ",
        "size": 140
      }
    ],
    "pill": "Toán bất đối xứng của lỗ · code Python",
    "labels": [
      {
        "label": "Mất 30%",
        "value": "{need_30}",
        "color": "orange"
      },
      {
        "label": "Mất 10%",
        "value": "{need_10}",
        "color": "green"
      }
    ]
  }
}
```
