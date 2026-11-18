# PSR / DSR — Sharpe có phải do may mắn?

## Định nghĩa
- **PSR** (Probabilistic Sharpe Ratio, Bailey & López de Prado, 2012): xác suất Sharpe thật lớn hơn một ngưỡng, tính từ Sharpe quan sát, độ dài mẫu, độ lệch và độ nhọn của lợi suất.
- **DSR** (Deflated Sharpe Ratio, Bailey & López de Prado, 2014): PSR với ngưỡng bằng Sharpe tối đa kỳ vọng khi đã thử N chiến lược, để trừ đi "may mắn do thử nhiều".

## Công thức PSR
PSR = Φ( (SR − SR*)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²) ).

## Sai lầm hay gặp
- Thử hàng trăm cấu hình rồi chỉ báo cáo cấu hình tốt nhất (data snooping).
- Tin PSR gần 100% của một backtest được chọn ra từ nhiều lần thử.

## video_defaults

```json
{
  "tag": "PSR · DSR",
  "kicker": "Backtest",
  "title": "Backtest Sharpe gần 2 mà lợi thế thật bằng 0?",
  "hook": "Backtest Sharpe {best_sr}, PSR {psr_best}. Lợi thế thật của nó: bằng không.",
  "formula": "PSR = \\Phi\\!\\left(\\frac{(\\widehat{SR}-SR^*)\\sqrt{T-1}}{\\sqrt{1-\\gamma_3\\widehat{SR}+\\frac{\\gamma_4-1}{4}\\widehat{SR}^2}}\\right)",
  "beats": [
    "Code tạo {trials} chiến lược ngẫu nhiên, không chiến lược nào có lợi thế, mỗi cái chạy {T} phiên. Rồi chọn cái có Sharpe cao nhất.",
    "Cái tốt nhất có Sharpe {best_sr} và PSR {psr_best}. Trừ đi số lần thử, DSR chỉ còn {dsr_best}.",
    "Cột đỏ là các chiến lược Sharpe trên 1 hoàn toàn nhờ may. Vạch cam là cái được chọn.",
    "3D: PSR theo Sharpe quan sát và độ dài backtest. Backtest ngắn thì Sharpe cao cũng chưa chắc."
  ],
  "outputs": [
    {
      "label": "số chiến lược thử",
      "key": "trials"
    },
    {
      "label": "Sharpe tốt nhất",
      "key": "best_sr"
    },
    {
      "label": "PSR (bỏ qua số lần thử)",
      "key": "psr_best"
    },
    {
      "label": "DSR (tính số lần thử)",
      "key": "dsr_best",
      "highlight": true
    }
  ],
  "takeaway": "Thử càng nhiều, cái tốt nhất càng dễ là may. Hãy hỏi: đã thử bao nhiêu lần?",
  "cta": "Xem PSR và DSR trong Phân tích Quant tại quantik.io.vn",
  "caption": "PSR và DSR (Bailey & López de Prado) trả lời câu hỏi: Sharpe đẹp này có phải do may? Mô phỏng 200 chiến lược không có lợi thế bằng code thật.",
  "hashtags": [
    "quant",
    "backtest",
    "sharpe",
    "PSR",
    "QuanTik"
  ],
  "facts": {
    "psr_year": {
      "value": "2012",
      "source": "Bailey & López de Prado (2012), The Sharpe Ratio Efficient Frontier, Journal of Risk 15(2)"
    },
    "dsr_year": {
      "value": "2014",
      "source": "Bailey & López de Prado (2014), The Deflated Sharpe Ratio, Journal of Portfolio Management 40(5)"
    }
  },
  "thumb": {
    "tag": "PSR · DSR",
    "headline": [
      {
        "t": "SHARPE [o]{best_sr}[/o]",
        "size": 150
      },
      {
        "t": "LỢI THẾ THẬT",
        "size": 140
      },
      {
        "t": "[o]BẰNG 0[/o]",
        "size": 180
      }
    ],
    "pill": "{trials} backtest ngẫu nhiên · code Python",
    "labels": [
      {
        "label": "PSR",
        "value": "{psr_best}",
        "color": "orange"
      },
      {
        "label": "DSR",
        "value": "{dsr_best}",
        "color": "green"
      }
    ]
  }
}
```
