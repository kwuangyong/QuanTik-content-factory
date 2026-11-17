# Luật số lớn & Định lý giới hạn trung tâm

## Định nghĩa
- **Luật số lớn (LLN):** trung bình mẫu tiến về kỳ vọng khi số quan sát tăng (Jacob Bernoulli, *Ars Conjectandi*, 1713).
- **Định lý giới hạn trung tâm (CLT):** trung bình của nhiều biến độc lập, cùng phân phối, phương sai hữu hạn, xấp xỉ phân phối chuẩn, độ lệch chuẩn σ/√n, dù dữ liệu gốc lệch (de Moivre 1733; Laplace 1812).

## Liên quan tới đầu tư
- Lợi thế nhỏ chỉ lộ ra sau rất nhiều lần lặp; vài lệnh thắng/thua chưa nói gì.
- Sai số của trung bình giảm theo √n: muốn sai số giảm một nửa cần gấp 4 lần dữ liệu.

## Sai lầm hay gặp
- "Luật số bù trừ": thua 5 lần thì lần sau dễ thắng. LLN không bù trừ, nó pha loãng.
- Áp CLT khi phương sai không hữu hạn hoặc dữ liệu phụ thuộc mạnh (đuôi rất dày, khủng hoảng).

## video_defaults

```json
{
  "tag": "LLN · CLT",
  "kicker": "Xác suất",
  "title": "Vì sao trung bình đáng tin hơn từng lần? Luật số lớn và CLT",
  "hook": "Sau 10 lần, trung bình lệch tới {mean_10}. Sau {n} lần, nó về {mean_n}. Không phải phép màu.",
  "formula": "\\bar X_n \\to \\mu, \\quad \\sqrt{n}\\,\\frac{\\bar X_n-\\mu}{\\sigma} \\to \\mathcal{N}(0,1)",
  "beats": [
    "Code lấy {n} quan sát từ một phân phối lệch hẳn sang phải, kỳ vọng bằng {true_mean}, rồi tính trung bình cộng dồn.",
    "Trung bình sau 10 lần là {mean_10}, sau 100 lần {mean_100}, sau {n} lần {mean_n}.",
    "Đường cam lắc mạnh lúc đầu rồi bám vạch kỳ vọng. Vùng xanh hẹp dần theo căn bậc hai số quan sát.",
    "3D: mỗi lát là phân phối của trung bình k quan sát. k càng lớn, núi lệch biến thành quả chuông."
  ],
  "outputs": [
    {
      "label": "kỳ vọng thật",
      "key": "true_mean"
    },
    {
      "label": "TB sau 10 lần",
      "key": "mean_10"
    },
    {
      "label": "TB sau n lần",
      "key": "mean_n",
      "highlight": true
    },
    {
      "label": "độ lệch dữ liệu gốc",
      "key": "skew_raw"
    }
  ],
  "takeaway": "Một lần chưa nói gì. Lợi thế thật chỉ lộ ra sau rất nhiều lần.",
  "cta": "Học thêm nền tảng thống kê quant tại quantik.io.vn",
  "caption": "Luật số lớn và định lý giới hạn trung tâm: vì sao trung bình đáng tin hơn từng lần, và vì sao vài lệnh thắng chưa chứng minh gì. Code chạy thật.",
  "hashtags": [
    "quant",
    "xacsuat",
    "thongke",
    "CLT",
    "QuanTik"
  ],
  "allowed_literals": [
    "10 lần",
    "100 lần"
  ],
  "thumb": {
    "tag": "LLN · CLT",
    "headline": [
      {
        "t": "MỘT LẦN",
        "size": 170
      },
      {
        "t": "CHƯA NÓI GÌ",
        "size": 150
      },
      {
        "t": "[o]{n}[/o] LẦN MỚI NÓI",
        "size": 110
      }
    ],
    "pill": "Luật số lớn & giới hạn trung tâm · code Python",
    "labels": [
      {
        "label": "Sau 10 lần",
        "value": "{mean_10}",
        "color": "orange"
      },
      {
        "label": "Sau n lần",
        "value": "{mean_n}",
        "color": "green"
      }
    ]
  }
}
```
