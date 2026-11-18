# CMF — Dòng tiền Chaikin

## Định nghĩa
Chaikin Money Flow (Marc Chaikin): trung bình có trọng số khối lượng của vị trí giá đóng cửa trong biên độ ngày, cửa sổ 20 phiên.
MFM = ((C − L) − (H − C)) / (H − L) ∈ [−1, 1]; CMF = Σ(MFM·V) / ΣV.

## Đọc thế nào
- CMF > 0: phiên thường đóng cửa ở nửa trên biên độ, có khối lượng → áp lực mua chiếm ưu thế; CMF < 0 ngược lại.
- Phân kỳ: giá tăng nhưng CMF âm → giá lên mà đóng cửa yếu.

## Trong QuanTik
Có trong bảng thuật ngữ và là một thành phần của Điểm Quant (AdaptiveScorer, trọng số cmf).

## Sai lầm hay gặp
- Đọc CMF như "tiền vào/ra" theo nghĩa đen; nó chỉ dùng giá đóng cửa trong biên độ ngày và khối lượng.
- Bỏ qua phiên biên độ rất hẹp (H ≈ L) làm MFM nhảy mạnh.

## video_defaults

```json
{
  "tag": "CMF",
  "kicker": "Dòng tiền",
  "title": "Giá tăng nhưng tiền có thật sự vào? Đọc CMF",
  "hook": "Giá tăng 20 phiên liền mà CMF vẫn âm. Có {div_days} phiên như vậy trong mô phỏng này.",
  "formula": "CMF = \\frac{\\sum MFM_t\\, V_t}{\\sum V_t}",
  "beats": [
    "Mỗi phiên, code đo giá đóng cửa nằm ở đâu trong biên độ cao thấp, từ âm một đến một, nhân khối lượng, rồi lấy trung bình {w} phiên.",
    "CMF cao nhất {cmf_max}, thấp nhất {cmf_min}. {pct_pos} số phiên CMF dương.",
    "Cột xanh đỏ là CMF, đường xám là giá. Những đoạn giá đi lên mà cột đỏ là phân kỳ.",
    "3D: CMF theo thời gian và độ dài cửa sổ. Cửa sổ ngắn thì nhiễu, cửa sổ dài thì chậm."
  ],
  "outputs": [
    {
      "label": "cửa sổ (phiên)",
      "key": "w"
    },
    {
      "label": "CMF cao nhất",
      "key": "cmf_max"
    },
    {
      "label": "CMF thấp nhất",
      "key": "cmf_min"
    },
    {
      "label": "phiên phân kỳ",
      "key": "div_days",
      "highlight": true
    }
  ],
  "takeaway": "CMF đo giá đóng cửa mạnh hay yếu có khối lượng đi kèm. Đọc nó cùng giá, đừng đọc một mình.",
  "cta": "CMF là một thành phần của Điểm Quant. Xem tại quantik.io.vn",
  "caption": "Chaikin Money Flow: giá đóng cửa nằm ở đâu trong biên độ ngày, có khối lượng đi kèm hay không. Code tính thật trên dữ liệu mô phỏng.",
  "hashtags": [
    "quant",
    "CMF",
    "dongtien",
    "phantichkythuat",
    "QuanTik"
  ],
  "allowed_literals": [
    "20 phiên"
  ],
  "thumb": {
    "tag": "CMF",
    "headline": [
      {
        "t": "GIÁ TĂNG",
        "size": 180
      },
      {
        "t": "MÀ TIỀN",
        "size": 160
      },
      {
        "t": "[o]KHÔNG VÀO?[/o]",
        "size": 150
      }
    ],
    "pill": "Dòng tiền Chaikin · code Python",
    "labels": [
      {
        "label": "CMF cao",
        "value": "{cmf_max}",
        "color": "green"
      },
      {
        "label": "CMF thấp",
        "value": "{cmf_min}",
        "color": "orange"
      }
    ]
  }
}
```
