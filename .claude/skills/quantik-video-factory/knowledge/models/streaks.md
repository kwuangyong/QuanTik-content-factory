# Ngửa nhiều lần liền thì lần sau sấp?

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `streaks_demo`. Style gợi ý: `dark-truth`.

## Là gì

Tin rằng sự kiện ngẫu nhiên sẽ "tự cân bằng". Gilovich, Vallone, Tversky năm 1985 nghiên cứu "bàn tay nóng". Con người đánh giá thấp độ dài chuỗi trong dữ liệu ngẫu nhiên.

Nguồn: Wikipedia: Gambler's fallacy; Gilovich, Vallone & Tversky (1985)

## Ý chính

Ngửa sáu lần liền, bạn nghĩ lần sau chắc ra sấp? Đồng xu không có trí nhớ.

Đây là {flips} lần tung đồng xu thật sự ngẫu nhiên. Ô cam là chuỗi cùng mặt dài nhất. Trông như có quy luật, nhưng không. Code cho {people} người, mỗi người tung {flips} lần. Chuỗi dài nhất trung vị là {median_best}. {p6} người gặp chuỗi từ sáu trở lên. Biểu đồ: chuỗi dài nhất thường rơi vào khoảng 6 đến 8. Ai thấy 6 lần liền mà tưởng bất thường là đang đánh giá thấp ngẫu nhiên. Bề mặt 3D: tung càng nhiều, chuỗi dài càng chắc chắn xuất hiện.

## Mặt tối

Thị trường cũng vậy: vài phiên tăng liền không có nghĩa là sắp giảm, cũng không có nghĩa là sẽ tăng tiếp. Ai bán cho bạn "quy luật chuỗi" đang bán ảo giác.

## Mang về

Chuỗi dài là bình thường trong dữ liệu ngẫu nhiên. Trước khi thấy quy luật, hãy hỏi: ngẫu nhiên thuần tuý có tạo ra cảnh này không?

## video_defaults

```json
{
  "tag": "CHUỖI",
  "title": "Ngửa nhiều lần liền thì lần sau sấp?",
  "hook": "Ngửa sáu lần liền, bạn nghĩ lần sau chắc ra sấp? Đồng xu không có trí nhớ.",
  "kicker": "Ngụy biện con bạc",
  "wiki": {
    "title": "Ngụy biện con bạc",
    "en": "Gambler's fallacy · clustering illusion",
    "lines": [
      "Tin rằng sự kiện ngẫu nhiên sẽ \"tự cân bằng\".",
      "Gilovich, Vallone, Tversky năm 1985 nghiên cứu \"bàn tay nóng\".",
      "Con người đánh giá thấp độ dài chuỗi trong dữ liệu ngẫu nhiên."
    ],
    "source": "Wikipedia: Gambler's fallacy; Gilovich, Vallone & Tversky (1985)",
    "say": "Ngụy biện con bạc là tin rằng chuỗi ngẫu nhiên sẽ tự cân bằng. Thực tế, chuỗi dài xuất hiện thường hơn bạn nghĩ."
  },
  "anim": {
    "kind": "coins",
    "rows": 10,
    "cols": 10,
    "seed": 4,
    "label": "Ô cam: chuỗi dài nhất trong {flips} lần tung"
  },
  "beats": [
    "Đây là {flips} lần tung đồng xu thật sự ngẫu nhiên. Ô cam là chuỗi cùng mặt dài nhất. Trông như có quy luật, nhưng không.",
    "Code cho {people} người, mỗi người tung {flips} lần. Chuỗi dài nhất trung vị là {median_best}. {p6} người gặp chuỗi từ sáu trở lên.",
    "Biểu đồ: chuỗi dài nhất thường rơi vào khoảng 6 đến 8. Ai thấy 6 lần liền mà tưởng bất thường là đang đánh giá thấp ngẫu nhiên.",
    "Bề mặt 3D: tung càng nhiều, chuỗi dài càng chắc chắn xuất hiện."
  ],
  "dark": "Thị trường cũng vậy: vài phiên tăng liền không có nghĩa là sắp giảm, cũng không có nghĩa là sẽ tăng tiếp. Ai bán cho bạn \"quy luật chuỗi\" đang bán ảo giác.",
  "takeaway": "Chuỗi dài là bình thường trong dữ liệu ngẫu nhiên. Trước khi thấy quy luật, hãy hỏi: ngẫu nhiên thuần tuý có tạo ra cảnh này không?",
  "myth": "Ra ngửa nhiều lần liền thì lần sau dễ ra sấp hơn.",
  "fact": "Sai. Mỗi lần tung độc lập. Và trong {flips} lần tung, {p6} người gặp chuỗi từ sáu trở lên.",
  "story": [
    {
      "at": 0.3,
      "label": "Chuỗi ngắn",
      "say": "Chuỗi dài nhất bằng 4 hay 5 thì khá hiếm."
    },
    {
      "at": 0.6,
      "label": "Phổ biến nhất",
      "say": "6 đến 8 là bình thường nhất."
    },
    {
      "at": 1.0,
      "label": "Đuôi dài",
      "say": "Có người còn gặp chuỗi {max_seen}."
    }
  ],
  "formula": "P(\\mathrm{chuỗi}\\ge k)\\approx 1-e^{-(n-k+1)/2^k}",
  "formula_numeric": "n=<<flips>>,\\ P(\\ge 6)\\approx<<p6>>",
  "symbols": [
    {
      "sym": "n",
      "say": "Số lần tung."
    },
    {
      "sym": "k",
      "say": "Độ dài chuỗi."
    }
  ],
  "outputs": [
    {
      "label": "số người",
      "key": "people"
    },
    {
      "label": "chuỗi dài nhất trung vị",
      "key": "median_best"
    },
    {
      "label": "gặp chuỗi ≥ 6",
      "key": "p6",
      "highlight": true
    },
    {
      "label": "gặp chuỗi ≥ 8",
      "key": "p8"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Ngửa sáu lần liền: “Lần này chắc chắn sấp!”",
    "punch": "Đồng xu: không có trí nhớ.",
    "truth": "{p6} người tung {flips} lần gặp chuỗi từ sáu trở lên."
  },
  "caption": "Ngụy biện con bạc: vì sao chuỗi dài trong dữ liệu ngẫu nhiên phổ biến hơn bạn nghĩ. Mô phỏng 20.000 người tung đồng xu. Nội dung giáo dục về xác suất.",
  "hashtags": [
    "xacsuat",
    "tamlyhoc",
    "gamblersfallacy",
    "QuanTik",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "1985",
    "6 đến 8",
    "4 hay 5",
    "20.000"
  ],
  "formula_parts": [
    "P(\\mathrm{chuỗi}\\ge k)\\approx 1-e^{-(n-k+1)/2^k}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Ô cam: chuỗi dài nhất trong {flips} lần tung",
  "max_seconds": 90
}
```
