# RSI — Chỉ số sức mạnh tương đối

## Định nghĩa
RSI (Relative Strength Index, J. Welles Wilder, *New Concepts in Technical Trading Systems*, 1978) so sánh độ lớn trung bình các phiên tăng với các phiên giảm trong một cửa sổ (mặc định 14 phiên), quy về thang 0–100.

## Công thức
RS = trung bình tăng / trung bình giảm (làm mượt kiểu Wilder: TB mới = (TB cũ·13 + giá trị mới)/14); RSI = 100 − 100/(1 + RS).

## Đọc thế nào
- Trên 70: các phiên tăng đang áp đảo (thường gọi là "quá mua"); dưới 30: phiên giảm áp đảo ("quá bán").
- RSI đo **động lượng đã xảy ra**, không đo xác suất đảo chiều. Trong xu hướng mạnh RSI có thể nằm trên 70 rất lâu.

## Sai lầm hay gặp
- "RSI trên 70 là sắp giảm". Trên dữ liệu ngẫu nhiên (code bên dưới), sau RSI > 70 giá tăng hay giảm gần như 50/50.
- Dùng một ngưỡng cố định cho mọi mã; mã biến động mạnh chạm 70/30 thường xuyên hơn.

## video_defaults

```json
{
  "tag": "RSI",
  "kicker": "Chỉ báo kỹ thuật",
  "title": "RSI trên 70 có phải sắp giảm? Kiểm chứng bằng code",
  "hook": "RSI trên {hi} là quá mua, sắp giảm? Mình cho code kiểm tra {n_days} phiên.",
  "formula": "RSI = 100 - \\frac{100}{1 + RS}",
  "beats": [
    "RSI so trung bình phiên tăng với trung bình phiên giảm trong {period} phiên, làm mượt kiểu Wilder, rồi quy về thang 0 đến 100.",
    "Trên {n_days} phiên mô phỏng có {days_ob} phiên RSI vượt {hi}. Mười phiên sau đó, tỷ lệ tăng là {up_after_ob}.",
    "Đường cam là RSI, vùng đỏ phía trên là quá mua. Giá vẫn đi tiếp theo hướng của nó, chẳng quan tâm vạch {hi}.",
    "3D cho thấy RSI phân bố thế nào theo thời gian: có giai đoạn dồn lên cao, có giai đoạn dồn xuống thấp."
  ],
  "outputs": [
    {
      "label": "cửa sổ (phiên)",
      "key": "period"
    },
    {
      "label": "số phiên RSI > 70",
      "key": "days_ob"
    },
    {
      "label": "tăng sau 10 phiên",
      "key": "up_after_ob",
      "highlight": true
    }
  ],
  "takeaway": "RSI kể lại động lượng đã qua. Nó không hứa điều gì về phiên tới.",
  "cta": "Xem RSI cùng 16 nhóm chỉ tiêu trong Phân tích Quant tại quantik.io.vn",
  "caption": "RSI do J. Welles Wilder công bố năm 1978. Trên 70 gọi là quá mua, nhưng quá mua không có nghĩa sắp giảm. Code chạy thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "RSI",
    "phantichkythuat",
    "chungkhoan",
    "QuanTik"
  ],
  "facts": {
    "wilder_year": {
      "value": "1978",
      "source": "Wilder, New Concepts in Technical Trading Systems (1978)"
    }
  },
  "thumb": {
    "tag": "RSI",
    "headline": [
      {
        "t": "RSI TRÊN 70",
        "size": 150
      },
      {
        "t": "LÀ SẮP GIẢM?",
        "size": 150
      },
      {
        "t": "TĂNG [o]{up_after_ob}[/o] SỐ LẦN",
        "size": 110
      }
    ],
    "pill": "Kiểm chứng {days_ob} lần quá mua · code Python",
    "labels": [
      {
        "label": "Quá mua",
        "value": "{days_ob}",
        "color": "orange"
      },
      {
        "label": "Tăng sau đó",
        "value": "{up_after_ob}",
        "color": "green"
      }
    ]
  }
}
```
