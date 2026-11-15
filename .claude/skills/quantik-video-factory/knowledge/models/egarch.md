# EGARCH — Tin xấu và tin tốt không đối xứng

## Định nghĩa
EGARCH (Daniel Nelson, *Econometrica*, 1991) mô hình log phương sai: ln σ²_t = ω + β·ln σ²_{t−1} + α(|z_{t−1}| − E|z|) + γ·z_{t−1}. Hệ số γ cho phép cú sốc âm và dương tác động khác nhau; γ < 0 là "hiệu ứng đòn bẩy" (Black 1976): giá giảm làm biến động tăng mạnh hơn giá tăng cùng độ lớn.

## Trong QuanTik
Module "γ · Tác động bất đối xứng trong EGARCH" trong báo cáo Quant; GARCHEngine ước lượng GARCH(1,1)-t và EGARCH.

## Sai lầm hay gặp
- Dùng GARCH đối xứng rồi ngạc nhiên vì biến động sau phiên giảm sâu cao hơn dự báo.
- Đọc γ như tín hiệu hướng giá. γ nói về **độ rung** sau tin, không nói giá sẽ đi đâu.

## video_defaults

```json
{
  "tag": "EGARCH",
  "kicker": "Biến động bất đối xứng",
  "title": "Vì sao tin xấu làm thị trường rung mạnh hơn tin tốt?",
  "hook": "Cùng một cú sốc {shock} sigma. Tin xấu đẩy biến động lên {vol_down}, tin tốt chỉ {vol_up}.",
  "formula": "\\ln\\sigma_t^2 = \\omega + \\beta\\ln\\sigma_{t-1}^2 + \\alpha(|z|-E|z|) + \\gamma z",
  "beats": [
    "EGARCH viết biến động dưới dạng log, và thêm một số hạng gamma nhân cú sốc có dấu. Gamma âm thì tin xấu được tính nặng hơn.",
    "Với gamma {gamma}, sau cú giảm {shock} sigma biến động là {vol_down}; sau cú tăng cùng cỡ chỉ {vol_up}, chênh {ratio}.",
    "Đường nét đứt là mô hình đối xứng. Đường cam là EGARCH: bên trái dựng cao hơn, vùng đỏ là phần tin xấu bị khuếch đại.",
    "3D: trục ngang là cú sốc, trục sâu là gamma. Gamma càng âm, sườn tin xấu càng dốc."
  ],
  "outputs": [
    {
      "label": "γ",
      "key": "gamma"
    },
    {
      "label": "vol sau tin xấu",
      "key": "vol_down",
      "highlight": true
    },
    {
      "label": "vol sau tin tốt",
      "key": "vol_up"
    },
    {
      "label": "chênh lệch",
      "key": "ratio"
    }
  ],
  "takeaway": "Thị trường sợ nhiều hơn mừng. EGARCH đo đúng sự bất đối xứng đó.",
  "cta": "Xem hệ số γ EGARCH của từng mã trong Phân tích Quant tại quantik.io.vn",
  "caption": "EGARCH (Nelson, 1991) cho phép tin xấu tác động lên biến động mạnh hơn tin tốt. QuanTik báo cáo hệ số γ này cho từng mã. Code chạy thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "EGARCH",
    "biendong",
    "chungkhoan",
    "QuanTik"
  ],
  "facts": {
    "nelson": {
      "value": "1991",
      "source": "Nelson, D. (1991), Econometrica 59(2)"
    }
  },
  "thumb": {
    "tag": "EGARCH γ",
    "headline": [
      {
        "t": "TIN XẤU",
        "size": 180
      },
      {
        "t": "RUNG MẠNH HƠN",
        "size": 130
      },
      {
        "t": "TIN TỐT [o]{ratio}[/o]",
        "size": 140
      }
    ],
    "pill": "Hệ số γ bất đối xứng · code Python",
    "labels": [
      {
        "label": "Sau tin xấu",
        "value": "{vol_down}",
        "color": "orange"
      },
      {
        "label": "Sau tin tốt",
        "value": "{vol_up}",
        "color": "green"
      }
    ]
  }
}
```
