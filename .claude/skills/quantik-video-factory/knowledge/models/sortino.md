# Sortino ratio

Định nghĩa (glossary QuanTik): Biến thể của Sharpe nhưng chỉ tính rủi ro giảm giá (downside deviation), không trừng phạt biến động tăng có lợi.

## Công thức
Sortino = (r̄ − MAR) / sqrt(1/N · Σ min(r_t − MAR, 0)²) · √252. Downside moment lấy trên toàn N quan sát.

## Tham số đẹp để minh hoạ
MAR = 0. Hai chiến lược soi gương: B = 2·mean(A) − A ⇒ cùng trung bình, cùng độ lệch chuẩn, nên Sharpe bằng nhau tuyệt đối; A lệch phải (bật vọt), B lệch trái (sập).

## Ngưỡng đọc nhanh (glossary)
< 0 tệ · 0–2 bình thường · 2–3 tốt · > 3 rất tốt.

## Ví dụ HOSE
Không dùng mã thật; minh hoạ bằng dữ liệu mô phỏng.

## Sai lầm hay gặp
- Chỉ lấy độ lệch chuẩn các ngày lỗ thay vì chia cho toàn N.
- MAR khác tần suất với return.
- Sortino cao không có nghĩa không thể sập: mẫu ngắn có thể chưa gặp cú sập.

## video_defaults

```json
{
  "tag": "SORTINO",
  "title": "Cùng Sharpe, nhưng một chiến lược làm bạn mất ngủ: Sortino",
  "hook": "Có một chỉ số chỉ đếm ngày bạn lỗ. Nó tên Sortino, và nó biết vì sao bạn mất ngủ.",
  "kicker": "Sortino ratio",
  "beats": [
    "Code tạo chiến lược A trong {n_days} phiên, rồi soi gương thành B. Cùng trung bình, cùng độ lệch chuẩn, nên Sharpe đều là {sharpe_a}.",
    "Sortino chỉ phạt ngày lỗ. A được {sortino_a}, B chỉ {sortino_b}: chênh {ratio}.",
    "Thanh đỏ là ngày lỗ, thanh xám là ngày lãi. Ngày tệ nhất của A là {worst_a}, của B là {worst_b}.",
    "Sortino lũy kế: đường xanh A tách hẳn đường đỏ B, dù Sharpe không phân biệt được."
  ],
  "outputs": [
    {
      "label": "Sharpe A = Sharpe B",
      "key": "sharpe_a"
    },
    {
      "label": "Sortino A",
      "key": "sortino_a",
      "highlight": true
    },
    {
      "label": "Sortino B",
      "key": "sortino_b"
    },
    {
      "label": "ngày tệ nhất A",
      "key": "worst_a"
    },
    {
      "label": "ngày tệ nhất B",
      "key": "worst_b"
    }
  ],
  "takeaway": "Sharpe đo bạn rung lắc bao nhiêu. Sortino đo bạn đau bao nhiêu. Cùng Sharpe, hãy nhìn Sortino.",
  "cta": "Xem Sharpe, Sortino, Calmar của từng mã trong phân tích Quant tại quantik.io.vn",
  "myth": "Cùng Sharpe {sharpe_a} thì rủi ro như nhau.",
  "fact": "Cùng Sharpe {sharpe_a}, nhưng Sortino của A là {sortino_a}, của B chỉ {sortino_b}. B có ngày sập {worst_b}.",
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Hai chiến lược cùng Sharpe {sharpe_a}, chọn cái nào cũng được.”",
    "punch": "Dân quant: “Thế Sortino bao nhiêu?”",
    "truth": "A: {sortino_a}. B: {sortino_b}. Rủi ro đáng sợ là rủi ro đi xuống."
  },
  "story": [
    {
      "at": 0.3,
      "label": "Giống nhau",
      "say": "Nhìn lướt, hai chiến lược rung lắc như nhau."
    },
    {
      "at": 0.65,
      "label": "Khác hướng",
      "say": "A thỉnh thoảng bật vọt, B thỉnh thoảng sập. Ngày tệ nhất của B là {worst_b}."
    },
    {
      "at": 1.0,
      "label": "Kết quả",
      "say": "Sharpe vẫn bằng nhau, nhưng Sortino A là {sortino_a}, B chỉ {sortino_b}."
    }
  ],
  "formula": "\\mathrm{Sortino}=\\frac{\\bar r-\\mathrm{MAR}}{\\sqrt{\\frac{1}{N}\\sum_t\\min(r_t-\\mathrm{MAR},0)^2}}\\sqrt{252}",
  "formula_parts": [
    "\\bar r-\\mathrm{MAR}",
    "\\sqrt{\\frac{1}{N}\\sum_t\\min(r_t-\\mathrm{MAR},0)^2}",
    "\\mathrm{Sortino}=\\frac{\\bar r-\\mathrm{MAR}}{\\sqrt{\\frac{1}{N}\\sum_t\\min(r_t-\\mathrm{MAR},0)^2}}\\sqrt{252}"
  ],
  "formula_numeric": "\\mathrm{Sortino}_A=<<sortino_a>>,\\quad \\mathrm{Sortino}_B=<<sortino_b>>",
  "symbols": [
    {
      "sym": "\\bar r-\\mathrm{MAR}",
      "say": "Lợi suất trung bình trừ mức tối thiểu chấp nhận được, ở đây bằng 0."
    },
    {
      "sym": "\\min(r_t-\\mathrm{MAR},0)",
      "say": "Chỉ giữ ngày lỗ, ngày lãi bị đặt về 0."
    },
    {
      "sym": "\\sqrt{252}",
      "say": "Quy từ ngày ra năm, giả định 252 phiên."
    }
  ],
  "caption": "Cùng Sharpe chưa chắc cùng rủi ro. Sortino chỉ phạt biến động đi xuống. Code chạy thật trên 2 chiến lược mô phỏng.",
  "hashtags": [
    "quant",
    "sortino",
    "sharpe",
    "chungkhoan",
    "dautu",
    "QuanTik"
  ],
  "allowed_literals": [
    "252",
    "2 chiến lược"
  ],
  "hook_kicker": "Sortino là gì?",
  "myth_say": "Sharpe phạt mọi biến động, kể cả phiên tăng vọt có lợi cho bạn. Nên nhiều người nghĩ: cùng Sharpe {sharpe_a} là rủi ro như nhau."
}
```
