# Quỹ top năm nay, sang năm tụt hạng

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `regression_mean_demo`. Style gợi ý: `dark-truth`.

## Là gì

Francis Galton phát hiện năm 1886 khi đo chiều cao cha mẹ và con. Kết quả cực đoan thường đi kèm may rủi cực đoan. Lần sau, may rủi không lặp lại.

Nguồn: Galton (1886), Journal of the Anthropological Institute

## Ý chính

Quỹ đứng đầu năm nay, sang năm thường tụt hạng. Không phải vì họ kém đi.

Nhóm đứng đầu năm 1 lãi trung bình {top_y1}. Năm 2, cùng nhóm đó chỉ còn {top_y2}. Code tạo {n} quỹ, mỗi quỹ có chút kỹ năng thật cộng rất nhiều may rủi. May rủi chiếm khoảng {luck_share} độ phân tán. Mỗi chấm là một quỹ. Chấm cam là top năm 1. Đường xanh gần như nằm ngang: năm 1 nói rất ít về năm 2. Bề mặt 3D: phần kỹ năng càng nhỏ, hạng năm sau càng bị kéo về giữa.

## Mặt tối

Chỉ {top_rank2} nhóm top năm 1 còn ở top năm 2. Người mua theo bảng xếp hạng thường vào đúng lúc may mắn đã dùng hết.

## Mang về

Kết quả cực đoan nên được đọc là kỹ năng cộng may rủi. Muốn biết phần nào là kỹ năng, cần mẫu dài.

## video_defaults

```json
{
  "tag": "HỒI QUY",
  "title": "Quỹ top năm nay, sang năm tụt hạng",
  "hook": "Quỹ đứng đầu năm nay, sang năm thường tụt hạng. Không phải vì họ kém đi.",
  "kicker": "Hồi quy về trung bình",
  "wiki": {
    "title": "Hồi quy về trung bình",
    "en": "Regression toward the mean",
    "lines": [
      "Francis Galton phát hiện năm 1886 khi đo chiều cao cha mẹ và con.",
      "Kết quả cực đoan thường đi kèm may rủi cực đoan.",
      "Lần sau, may rủi không lặp lại."
    ],
    "source": "Galton (1886), Journal of the Anthropological Institute",
    "say": "Năm 1886, Francis Galton thấy con của cha mẹ rất cao thường thấp hơn cha mẹ. Ông gọi đó là hồi quy về trung bình."
  },
  "anim": {
    "kind": "steps",
    "items": [
      [
        "top 10% năm 1",
        "{top_y1}"
      ],
      [
        "cùng nhóm, năm 2",
        "{top_y2}"
      ]
    ],
    "hl": 0,
    "label": "Lợi nhuận trung bình của nhóm đứng đầu"
  },
  "beats": [
    "Nhóm đứng đầu năm 1 lãi trung bình {top_y1}. Năm 2, cùng nhóm đó chỉ còn {top_y2}.",
    "Code tạo {n} quỹ, mỗi quỹ có chút kỹ năng thật cộng rất nhiều may rủi. May rủi chiếm khoảng {luck_share} độ phân tán.",
    "Mỗi chấm là một quỹ. Chấm cam là top năm 1. Đường xanh gần như nằm ngang: năm 1 nói rất ít về năm 2.",
    "Bề mặt 3D: phần kỹ năng càng nhỏ, hạng năm sau càng bị kéo về giữa."
  ],
  "dark": "Chỉ {top_rank2} nhóm top năm 1 còn ở top năm 2. Người mua theo bảng xếp hạng thường vào đúng lúc may mắn đã dùng hết.",
  "takeaway": "Kết quả cực đoan nên được đọc là kỹ năng cộng may rủi. Muốn biết phần nào là kỹ năng, cần mẫu dài.",
  "myth": "Quỹ top năm nay thì năm sau cũng sẽ top.",
  "fact": "Thường không. Top năm 1 lãi {top_y1}, năm 2 chỉ còn {top_y2}. Chỉ {top_rank2} còn ở top.",
  "story": [
    {
      "at": 0.3,
      "label": "Đám mây",
      "say": "Phần lớn các quỹ dồn quanh giữa."
    },
    {
      "at": 0.7,
      "label": "Nhóm top",
      "say": "Nhóm cam lãi cao nhất năm 1."
    },
    {
      "at": 1.0,
      "label": "Năm 2",
      "say": "Năm 2, nhóm cam rơi về quanh 0."
    }
  ],
  "formula": "E[Y_2\\mid Y_1]=\\rho\\,Y_1",
  "formula_numeric": "\\rho=<<corr>>",
  "symbols": [
    {
      "sym": "\\rho",
      "say": "Tương quan giữa hai năm."
    }
  ],
  "outputs": [
    {
      "label": "top năm 1",
      "key": "top_y1"
    },
    {
      "label": "cùng nhóm năm 2",
      "key": "top_y2",
      "highlight": true
    },
    {
      "label": "tương quan",
      "key": "corr"
    },
    {
      "label": "còn ở top",
      "key": "top_rank2"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Năm 1: “Quỹ số 1 thị trường!”",
    "punch": "Năm 2: “…”",
    "truth": "Top năm 1 lãi {top_y1}, năm 2 còn {top_y2}."
  },
  "caption": "Vì sao quỹ đứng đầu năm nay thường tụt hạng năm sau? Hồi quy về trung bình, mô phỏng 2.000 quỹ. Nội dung giáo dục về thống kê, không phải khuyến nghị.",
  "hashtags": [
    "thongke",
    "dautu",
    "tamlyhoc",
    "QuanTik",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1886",
    "10%",
    "2.000",
    "năm 1",
    "năm 2"
  ],
  "formula_parts": [
    "E[Y_2\\mid Y_1]=\\rho\\,Y_1"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Lợi nhuận trung bình của nhóm đứng đầu",
  "max_seconds": 90
}
```
