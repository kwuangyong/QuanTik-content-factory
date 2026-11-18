# Momentum — Hiệu ứng động lượng

## Định nghĩa
Momentum: nhóm cổ phiếu tăng mạnh trong quá khứ (thường 3–12 tháng) có xu hướng tiếp tục vượt nhóm yếu trong vài tháng sau. Jegadeesh & Titman (*Journal of Finance*, 1993) ghi nhận trên thị trường Mỹ 1965–1989.

## Vì sao có thể tồn tại
Chỉ khi có thứ gì đó **bền**: lợi thế riêng của doanh nghiệp, dòng tiền chậm, phản ứng chậm với tin. Code bên dưới cho thấy: có lợi thế bền thì chênh lệch dương; xoá lợi thế đi thì chênh lệch trung bình gần 0.

## Trong QuanTik
Module "Điểm động lượng nhiều cửa sổ" và "Sức mạnh tương đối 20 phiên" trong báo cáo Quant.

## Sai lầm hay gặp
- Lấy một lần mô phỏng/backtest làm bằng chứng. Phải lặp nhiều lần.
- Quên đảo chiều ngắn hạn (1 tháng) và momentum crash khi thị trường đảo chiều mạnh.

## video_defaults

```json
{
  "tag": "MOMENTUM",
  "kicker": "Nhân tố",
  "title": "Mạnh hôm qua có mạnh tiếp hôm nay? Kiểm chứng momentum",
  "hook": "Nhóm mạnh nhất quá khứ có tiếp tục mạnh? Chỉ khi có một điều kiện.",
  "formula": "\\text{spread} = \\bar r_{\\text{top}} - \\bar r_{\\text{bottom}}",
  "beats": [
    "Code tạo {n_stocks} mã, mỗi mã có một lợi thế nhỏ riêng. Xếp hạng theo {look} phiên trước, chia nhóm mạnh và nhóm yếu, rồi xem {hold} phiên sau.",
    "Nhóm mạnh lãi {top_fwd}, nhóm yếu {bot_fwd}. Trung bình {reps} lần mô phỏng, chênh lệch là {spread_avg}.",
    "Chấm xanh là nhóm mạnh, chấm đỏ là nhóm yếu. Hai vạch ngang là lợi suất trung bình giai đoạn sau.",
    "3D: chênh lệch theo cửa sổ nhìn lại và thời gian giữ. Không phải cấu hình nào cũng cho kết quả giống nhau."
  ],
  "outputs": [
    {
      "label": "nhóm mạnh, giai đoạn sau",
      "key": "top_fwd"
    },
    {
      "label": "nhóm yếu, giai đoạn sau",
      "key": "bot_fwd"
    },
    {
      "label": "chênh lệch TB",
      "key": "spread_avg",
      "highlight": true
    },
    {
      "label": "khi không có lợi thế",
      "key": "spread_noise"
    }
  ],
  "takeaway": "Momentum chỉ tồn tại khi có thứ gì đó bền đứng sau. Không có thì chỉ là nhiễu.",
  "cta": "Xem điểm động lượng nhiều cửa sổ trong Phân tích Quant tại quantik.io.vn",
  "caption": "Momentum: nhóm mạnh trong quá khứ có thể tiếp tục mạnh, nhưng chỉ khi có lợi thế bền đứng sau. Mình kiểm chứng bằng mô phỏng lặp nhiều lần.",
  "hashtags": [
    "quant",
    "momentum",
    "nhanto",
    "chungkhoan",
    "QuanTik"
  ],
  "facts": {
    "jt": {
      "value": "1993",
      "source": "Jegadeesh & Titman (1993), Journal of Finance 48(1)"
    }
  },
  "thumb": {
    "tag": "Momentum",
    "headline": [
      {
        "t": "MẠNH HÔM QUA",
        "size": 140
      },
      {
        "t": "CÓ MẠNH TIẾP?",
        "size": 150
      },
      {
        "t": "CHÊNH [g]{spread_avg}[/g]",
        "size": 130
      }
    ],
    "pill": "Lặp {reps} lần mô phỏng · code Python",
    "labels": [
      {
        "label": "Có lợi thế",
        "value": "{spread_avg}",
        "color": "green"
      },
      {
        "label": "Nhiễu thuần",
        "value": "{spread_noise}",
        "color": "orange"
      }
    ]
  }
}
```
