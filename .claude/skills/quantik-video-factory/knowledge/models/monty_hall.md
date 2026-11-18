# Bài toán ba cánh cửa làm cả tiến sĩ cãi sai

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `monty_hall_demo`. Style gợi ý: `dark-truth`.

## Là gì

Đặt theo tên người dẫn gameshow Let's Make a Deal. Marilyn vos Savant giải trên tạp chí Parade năm 1990. Hàng nghìn lá thư phản đối, nhiều người có bằng tiến sĩ.

Nguồn: Wikipedia: Monty Hall problem

## Ý chính

Bài toán này từng khiến hàng nghìn người, cả tiến sĩ toán, viết thư mắng người giải đúng.

Ba cánh cửa, một chiếc xe. Bạn chọn cửa 1. Người dẫn, biết xe ở đâu, mở một cửa có dê. Bạn có nên đổi? Code chơi {games} ván. Giữ cửa thắng {p_stay}. Đổi cửa thắng {p_switch}, gấp {ratio}. Hai đường chạy lúc đầu loạn xạ, rồi dính chặt vào một phần ba và hai phần ba. Không phải 50/50. Nhiều cửa hơn thì càng rõ. Với 10 cửa, người dẫn mở 8 cửa dê: đổi cửa thắng gần như luôn.

## Mặt tối

Trực giác nói 50/50 vì quên mất một điều: người dẫn biết đáp án. Khi người có thông tin hành động, hành động đó là dữ liệu.

## Mang về

Đừng chỉ nhìn kết quả còn lại. Hỏi: ai đã lọc thông tin này, và họ biết gì?

## video_defaults

```json
{
  "tag": "3 CỬA",
  "title": "Bài toán ba cánh cửa làm cả tiến sĩ cãi sai",
  "hook": "Bài toán này từng khiến hàng nghìn người, cả tiến sĩ toán, viết thư mắng người giải đúng.",
  "kicker": "Monty Hall",
  "wiki": {
    "title": "Bài toán Monty Hall",
    "en": "Monty Hall problem",
    "lines": [
      "Đặt theo tên người dẫn gameshow Let's Make a Deal.",
      "Marilyn vos Savant giải trên tạp chí Parade năm 1990.",
      "Hàng nghìn lá thư phản đối, nhiều người có bằng tiến sĩ."
    ],
    "source": "Wikipedia: Monty Hall problem",
    "say": "Năm 1990, Marilyn vos Savant giải bài này trên tạp chí Parade và nhận hàng nghìn lá thư phản đối."
  },
  "anim": {
    "kind": "doors",
    "label": "Đổi cửa thắng {p_switch} số lần"
  },
  "beats": [
    "Ba cánh cửa, một chiếc xe. Bạn chọn cửa 1. Người dẫn, biết xe ở đâu, mở một cửa có dê. Bạn có nên đổi?",
    "Code chơi {games} ván. Giữ cửa thắng {p_stay}. Đổi cửa thắng {p_switch}, gấp {ratio}.",
    "Hai đường chạy lúc đầu loạn xạ, rồi dính chặt vào một phần ba và hai phần ba. Không phải 50/50.",
    "Nhiều cửa hơn thì càng rõ. Với 10 cửa, người dẫn mở 8 cửa dê: đổi cửa thắng gần như luôn."
  ],
  "dark": "Trực giác nói 50/50 vì quên mất một điều: người dẫn biết đáp án. Khi người có thông tin hành động, hành động đó là dữ liệu.",
  "takeaway": "Đừng chỉ nhìn kết quả còn lại. Hỏi: ai đã lọc thông tin này, và họ biết gì?",
  "myth": "Còn hai cửa thì cơ hội là 50/50, đổi hay giữ như nhau.",
  "fact": "Sai. {games} ván mô phỏng: giữ cửa thắng {p_stay}, đổi cửa thắng {p_switch}.",
  "story": [
    {
      "at": 0.2,
      "label": "Loạn",
      "say": "Vài ván đầu, may rủi lấn át."
    },
    {
      "at": 0.6,
      "label": "Hội tụ",
      "say": "Càng nhiều ván, hai đường tách hẳn."
    },
    {
      "at": 1.0,
      "label": "Đáp án",
      "say": "Đổi cửa {p_switch}, giữ cửa {p_stay}."
    }
  ],
  "formula": "P(\\mathrm{thắng}\\mid\\mathrm{đổi})=1-\\frac{1}{n}",
  "formula_numeric": "1-\\frac{1}{3}\\approx<<p_switch>>",
  "symbols": [
    {
      "sym": "n",
      "say": "Số cửa."
    }
  ],
  "outputs": [
    {
      "label": "số ván",
      "key": "games"
    },
    {
      "label": "giữ cửa thắng",
      "key": "p_stay"
    },
    {
      "label": "đổi cửa thắng",
      "key": "p_switch",
      "highlight": true
    },
    {
      "label": "gấp",
      "key": "ratio"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Ai cũng: “Còn 2 cửa thì 50/50.”",
    "punch": "Code chạy {games} ván: “Đổi đi.”",
    "truth": "Đổi cửa thắng {p_switch}, giữ cửa chỉ {p_stay}."
  },
  "caption": "Bài toán Monty Hall: còn hai cửa nhưng không phải 50/50. Code chơi 10.000 ván để chứng minh. Nội dung giáo dục về xác suất.",
  "hashtags": [
    "montyhall",
    "xacsuat",
    "toanhoc",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "1990",
    "50/50",
    "10 cửa",
    "8 cửa",
    "cửa 1",
    "10.000"
  ],
  "formula_parts": [
    "P(\\mathrm{thắng}\\mid\\mathrm{đổi})=1-\\frac{1}{n}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Đổi cửa thắng {p_switch} số lần",
  "max_seconds": 90
}
```
