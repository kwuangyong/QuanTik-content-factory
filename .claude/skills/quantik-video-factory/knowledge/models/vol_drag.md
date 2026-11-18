# Lãi 50% rồi lỗ 50%: bạn không hoà

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `vol_drag_demo`. Style gợi ý: `dark-truth`.

## Là gì

Lợi suất nhân với nhau, không cộng với nhau. Tăng trưởng thật xấp xỉ lợi suất trung bình trừ nửa phương sai. Biến động càng lớn, tài sản càng bị kéo xuống.

Nguồn: Wikipedia: Volatility tax

## Ý chính

Lãi 50% rồi lỗ 50%. Bạn nghĩ mình hoà? Bạn đang lỗ {up_down}.

Lỗ 20% cần lãi {need20} để hoà. Lỗ 30% cần {need30}. Lỗ 50% cần lãi {need50}. Code mô phỏng danh mục lợi suất trung bình {mu} mỗi năm, biến động {sig}, chạy {years} năm. Tăng trưởng thật chỉ {geo} mỗi năm. Đường đỏ là mức phải lãi lại theo mức lỗ. Nó cong vút lên, càng lỗ sâu càng khó gỡ. Bề mặt 3D là tài sản sau {years} năm theo lợi suất và biến động. Biến động cao nuốt chửng lợi suất.

## Mặt tối

Trung bình cộng {mu} nghe rất đẹp, nhưng biến động lấy đi {drag} mỗi năm. Sau {years} năm, {p_lose} kịch bản vẫn lỗ. Con số trung bình không nói điều đó.

## Mang về

Tránh lỗ sâu quan trọng hơn lãi lớn. Biến động không chỉ là cảm giác, nó là chi phí thật.

## video_defaults

```json
{
  "tag": "LỖ 50%",
  "title": "Lãi 50% rồi lỗ 50%: bạn không hoà",
  "hook": "Lãi 50% rồi lỗ 50%. Bạn nghĩ mình hoà? Bạn đang lỗ {up_down}.",
  "kicker": "Volatility drag",
  "wiki": {
    "title": "Lực kéo của biến động",
    "en": "Volatility drag · variance drain",
    "lines": [
      "Lợi suất nhân với nhau, không cộng với nhau.",
      "Tăng trưởng thật xấp xỉ lợi suất trung bình trừ nửa phương sai.",
      "Biến động càng lớn, tài sản càng bị kéo xuống."
    ],
    "source": "Wikipedia: Volatility tax",
    "say": "Lợi suất nhân với nhau chứ không cộng. Nên biến động càng lớn, tài sản càng bị kéo xuống."
  },
  "anim": {
    "kind": "steps",
    "items": [
      [
        "lỗ 20%",
        "{need20}"
      ],
      [
        "lỗ 30%",
        "{need30}"
      ],
      [
        "lỗ 50%",
        "{need50}"
      ]
    ],
    "hl": 2,
    "label": "Phải lãi lại bao nhiêu để hoà vốn"
  },
  "beats": [
    "Lỗ 20% cần lãi {need20} để hoà. Lỗ 30% cần {need30}. Lỗ 50% cần lãi {need50}.",
    "Code mô phỏng danh mục lợi suất trung bình {mu} mỗi năm, biến động {sig}, chạy {years} năm. Tăng trưởng thật chỉ {geo} mỗi năm.",
    "Đường đỏ là mức phải lãi lại theo mức lỗ. Nó cong vút lên, càng lỗ sâu càng khó gỡ.",
    "Bề mặt 3D là tài sản sau {years} năm theo lợi suất và biến động. Biến động cao nuốt chửng lợi suất."
  ],
  "dark": "Trung bình cộng {mu} nghe rất đẹp, nhưng biến động lấy đi {drag} mỗi năm. Sau {years} năm, {p_lose} kịch bản vẫn lỗ. Con số trung bình không nói điều đó.",
  "takeaway": "Tránh lỗ sâu quan trọng hơn lãi lớn. Biến động không chỉ là cảm giác, nó là chi phí thật.",
  "myth": "Lãi 50% rồi lỗ 50% thì hoà vốn.",
  "fact": "Sai. Còn lại {up_down} so với vốn đầu. Lỗ 50% phải lãi {need50} mới hoà.",
  "story": [
    {
      "at": 0.25,
      "label": "Lỗ nhẹ",
      "say": "Lỗ nhẹ, gỡ lại gần như tương đương."
    },
    {
      "at": 0.55,
      "label": "Lỗ một nửa",
      "say": "Lỗ 50%, phải lãi {need50}."
    },
    {
      "at": 1.0,
      "label": "Hố sâu",
      "say": "Lỗ sâu hơn, con số cần gỡ tăng vọt."
    }
  ],
  "formula": "g\\approx\\mu-\\frac{\\sigma^2}{2}",
  "formula_numeric": "<<mu>>-\\frac{<<sig>>^2}{2}=<<theory_geo>>",
  "symbols": [
    {
      "sym": "\\mu",
      "say": "Lợi suất trung bình cộng."
    },
    {
      "sym": "\\sigma",
      "say": "Biến động."
    }
  ],
  "outputs": [
    {
      "label": "lợi suất TB",
      "key": "mu"
    },
    {
      "label": "biến động",
      "key": "sig"
    },
    {
      "label": "tăng trưởng thật",
      "key": "geo",
      "highlight": true
    },
    {
      "label": "lực kéo/năm",
      "key": "drag"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Lãi 50%, lỗ 50%, vậy là hoà.”",
    "punch": "Tài khoản: {up_down}.",
    "truth": "Lỗ 50% phải lãi {need50} mới hoà vốn."
  },
  "caption": "Lãi 50% rồi lỗ 50% không phải hoà vốn. Volatility drag và vì sao lỗ sâu khó gỡ, mô phỏng 20.000 kịch bản. Nội dung giáo dục, không phải khuyến nghị.",
  "hashtags": [
    "quanlyvon",
    "ruiro",
    "dautu",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "50%",
    "20%",
    "30%",
    "20.000"
  ],
  "formula_parts": [
    "g\\approx\\mu-\\frac{\\sigma^2}{2}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Phải lãi lại bao nhiêu để hoà vốn",
  "max_seconds": 90
}
```
