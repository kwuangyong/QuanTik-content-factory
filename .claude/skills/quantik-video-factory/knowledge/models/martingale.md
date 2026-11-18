# Martingale — Chiến lược gấp thếp

## Định nghĩa
Chiến lược martingale (gấp thếp): sau mỗi lần thua, gấp đôi mức cược; thắng một lần là gỡ hết và lãi đúng một đơn vị. Phổ biến ở sòng bạc thế kỷ 18. (Khác với "martingale" trong lý thuyết xác suất: quá trình có kỳ vọng tương lai bằng giá trị hiện tại.)

## Vì sao thất bại
Vốn hữu hạn: với vốn 1.023 đơn vị chỉ chịu được 10 lần thua liên tiếp (1+2+…+512). Xác suất gặp chuỗi thua dài nhỏ mỗi ván nhưng gần như chắc chắn xảy ra khi chơi đủ lâu. Kết quả: đa số người chơi lãi nhỏ, số ít cháy toàn bộ, kỳ vọng tổng âm nếu xác suất thắng < 50%.

## Liên hệ đầu tư
"Bình quân giá xuống" bằng cách tăng gấp vị thế khi lỗ là cùng cấu trúc rủi ro; so với Kelly: tăng cược khi đang thua là ngược lại hoàn toàn.

## Sai lầm hay gặp
- Nhìn tỷ lệ người lãi (cao) mà bỏ qua độ lớn khoản lỗ hiếm.

## video_defaults

```json
{
  "tag": "MARTINGALE",
  "kicker": "Gấp thếp",
  "title": "Gấp thếp: {pct_up} người lãi, vậy mà tổng vẫn lỗ",
  "hook": "Thua thì gấp đôi, thắng một lần là gỡ hết. Nghe không thể thua?",
  "formula": "1+2+4+\\dots+2^{k-1} = 2^k - 1",
  "beats": [
    "Code cho {players} người chơi, mỗi người vốn {cap} đơn vị, xác suất thắng {p_win}. Thua thì gấp đôi cược, thắng thì về một đơn vị.",
    "Sau {rounds} ván, {pct_up} người đang lãi. Nhưng {pct_bust} người cháy sạch, và lãi lỗ trung bình là {mean_pnl}.",
    "Mỗi đường là một người: leo lên đều từng bậc nhỏ, rồi một chuỗi thua kéo thẳng xuống đáy.",
    "3D: xác suất cháy theo số lần thua chịu được và số ván. Chơi đủ lâu, mọi bề mặt đều leo lên."
  ],
  "outputs": [
    {
      "label": "người đang lãi",
      "key": "pct_up"
    },
    {
      "label": "người cháy tài khoản",
      "key": "pct_bust",
      "highlight": true
    },
    {
      "label": "lãi lỗ trung bình",
      "key": "mean_pnl"
    },
    {
      "label": "chịu được số lần thua",
      "key": "max_losses"
    }
  ],
  "takeaway": "Gấp thếp đổi nhiều lần lãi nhỏ lấy một lần mất hết.",
  "cta": "Học quản trị vốn đúng cách tại quantik.io.vn",
  "caption": "Martingale (gấp thếp): đa số người chơi lãi nhỏ, số ít mất sạch, và tổng kỳ vọng vẫn âm. Mô phỏng 2.000 người chơi bằng code thật.",
  "hashtags": [
    "quant",
    "martingale",
    "quanlyvon",
    "xacsuat",
    "QuanTik"
  ],
  "thumb": {
    "tag": "Martingale",
    "headline": [
      {
        "t": "[g]{pct_up}[/g] NGƯỜI LÃI",
        "size": 140
      },
      {
        "t": "TỔNG VẪN",
        "size": 170
      },
      {
        "t": "[o]LỖ[/o]",
        "size": 190
      }
    ],
    "pill": "Gấp thếp sau mỗi lần thua · code Python",
    "labels": [
      {
        "label": "Đang lãi",
        "value": "{pct_up}",
        "color": "green"
      },
      {
        "label": "Cháy",
        "value": "{pct_bust}",
        "color": "orange"
      }
    ]
  }
}
```
