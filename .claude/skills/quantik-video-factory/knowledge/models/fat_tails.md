# Phân phối chuẩn, log-normal và đuôi dày

## Định nghĩa
- **Chuẩn:** hình chuông, mọi thứ quyết định bởi trung bình và độ lệch chuẩn; ngày vượt 4σ cực hiếm.
- **Log-normal:** nếu lợi suất log là chuẩn thì giá là log-normal: giá không âm, lệch phải (Osborne 1959; nền của Black–Scholes 1973).
- **Đuôi dày (fat tails):** lợi suất thực tế có nhiều ngày cực đoan hơn phân phối chuẩn; đo bằng kurtosis dư > 0. Mandelbrot (1963) chỉ ra điều này trên giá bông.

## Vì sao quan trọng
VaR theo phân phối chuẩn đánh giá thấp rủi ro đuôi; mô hình Student-t, GARCH-t (QuanTik dùng GARCH(1,1)–t) xử lý tốt hơn.

## Sai lầm hay gặp
- Coi ngày "4 sigma" là chuyện trăm năm có một.
- Nghĩ đuôi dày nghĩa là biến động trung bình cao; thực ra cùng σ, đuôi dày có nhiều ngày yên ắng hơn *và* nhiều ngày cực đoan hơn.

## video_defaults

```json
{
  "tag": "ĐUÔI DÀY",
  "kicker": "Phân phối lợi suất",
  "title": "Ngày '4 sigma': sách nói hiếm, dữ liệu nói khác",
  "hook": "Phân phối chuẩn nói ngày biến động {sigma_k} sigma khoảng {once_every_years} năm mới gặp một lần. Mô phỏng đuôi dày có {big_t} ngày như thế trong {years} năm.",
  "formula": "\\kappa = \\frac{E[(r-\\mu)^4]}{\\sigma^4} - 3",
  "beats": [
    "Code tạo hai chuỗi {n_days} phiên cùng độ lệch chuẩn: một chuỗi chuẩn, một chuỗi đuôi dày Student-t, rồi đếm ngày vượt {sigma_k} sigma.",
    "Chuỗi chuẩn có {big_z} ngày như thế, chuỗi đuôi dày có {big_t}. Kurtosis dư {kurt_t} so với {kurt_z}.",
    "Trục dọc thang log để thấy đuôi. Cột đỏ kéo dài xa ngoài vạch {sigma_k} sigma, nơi đường chuẩn đã gần bằng không.",
    "3D: trục sâu là bậc tự do. Bậc tự do càng nhỏ, hai cánh càng nâng lên, đuôi càng dày."
  ],
  "outputs": [
    {
      "label": "ngày > 4σ, chuẩn",
      "key": "big_z"
    },
    {
      "label": "ngày > 4σ, đuôi dày",
      "key": "big_t",
      "highlight": true
    },
    {
      "label": "kurtosis dư (t)",
      "key": "kurt_t"
    }
  ],
  "takeaway": "Lợi suất thật không chuẩn. Mô hình rủi ro phải tính tới đuôi.",
  "cta": "Xem kiểm định phân phối lợi suất của từng mã trong Phân tích Quant tại quantik.io.vn",
  "caption": "Phân phối chuẩn, log-normal và đuôi dày: vì sao lợi suất thực tế có nhiều ngày cực đoan hơn sách giáo khoa. Code chạy thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "fattails",
    "xacsuat",
    "quanlyruiro",
    "QuanTik"
  ],
  "facts": {
    "mandelbrot": {
      "value": "1963",
      "source": "Mandelbrot, B. (1963), The Variation of Certain Speculative Prices, Journal of Business 36(4)"
    }
  },
  "thumb": {
    "tag": "Đuôi dày",
    "headline": [
      {
        "t": "SÁCH NÓI",
        "size": 140
      },
      {
        "t": "[o]{once_every_years}[/o] NĂM 1 LẦN",
        "size": 140
      },
      {
        "t": "DỮ LIỆU: [o]{big_t}[/o] LẦN",
        "size": 130
      }
    ],
    "pill": "Chuẩn · log-normal · đuôi dày · code Python",
    "labels": [
      {
        "label": "Chuẩn",
        "value": "{big_z}",
        "color": "green"
      },
      {
        "label": "Đuôi dày",
        "value": "{big_t}",
        "color": "orange"
      }
    ]
  }
}
```
