# Quỹ thắng 10 năm liền có thể chỉ là may

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `survivorship_demo`. Style gợi ý: `dark-truth`.

## Là gì

Chỉ nhìn kẻ sống sót, bỏ qua những ai đã biến mất. Abraham Wald: gia cố chỗ máy bay trở về KHÔNG bị bắn. Vì máy bay trúng đạn ở chỗ khác đã không trở về.

Nguồn: Wikipedia: Survivorship bias; Abraham Wald, Statistical Research Group

## Ý chính

Quỹ thắng thị trường {years} năm liền? Có thể không có chút kỹ năng nào.

Mỗi hình người là một quỹ không có kỹ năng gì, mỗi năm thắng hay thua thị trường như tung đồng xu. Thua một năm là đóng. Bắt đầu {funds} quỹ. Sau {years} năm còn {survivors} quỹ, mỗi quỹ thắng {years} năm liền, lãi trung bình {surv_avg} mỗi năm. Cột cuối màu cam là những quỹ lên báo. {dead} cột đã biến mất không ai nhắc. Hình 3D: đường cam là quỹ còn sống, đường đỏ là nghĩa địa quỹ, ngày càng đông.

## Mặt tối

Bạn chỉ nghe chuyện của {survivors} quỹ thắng. {dead} quỹ đã đóng cửa không ai kể. Thành tích đẹp có thể chỉ là kẻ sống sót của may rủi.

## Mang về

Trước khi tin một thành tích, hỏi: có bao nhiêu người đã thử và biến mất?

## video_defaults

```json
{
  "tag": "KẺ SỐNG SÓT",
  "title": "Quỹ thắng 10 năm liền có thể chỉ là may",
  "hook": "Quỹ thắng thị trường {years} năm liền? Có thể không có chút kỹ năng nào.",
  "kicker": "Thiên kiến kẻ sống sót",
  "wiki": {
    "title": "Thiên kiến kẻ sống sót",
    "en": "Survivorship bias",
    "lines": [
      "Chỉ nhìn kẻ sống sót, bỏ qua những ai đã biến mất.",
      "Abraham Wald: gia cố chỗ máy bay trở về KHÔNG bị bắn.",
      "Vì máy bay trúng đạn ở chỗ khác đã không trở về."
    ],
    "source": "Wikipedia: Survivorship bias; Abraham Wald, Statistical Research Group",
    "say": "Thời Thế chiến thứ hai, Abraham Wald khuyên gia cố chỗ máy bay trở về không bị bắn. Vì máy bay trúng đạn ở chỗ khác đã không trở về."
  },
  "anim": {
    "kind": "crowd",
    "mode": "survive",
    "left": 8,
    "label": "{funds} quỹ → còn {survivors}"
  },
  "beats": [
    "Mỗi hình người là một quỹ không có kỹ năng gì, mỗi năm thắng hay thua thị trường như tung đồng xu. Thua một năm là đóng.",
    "Bắt đầu {funds} quỹ. Sau {years} năm còn {survivors} quỹ, mỗi quỹ thắng {years} năm liền, lãi trung bình {surv_avg} mỗi năm.",
    "Cột cuối màu cam là những quỹ lên báo. {dead} cột đã biến mất không ai nhắc.",
    "Hình 3D: đường cam là quỹ còn sống, đường đỏ là nghĩa địa quỹ, ngày càng đông."
  ],
  "dark": "Bạn chỉ nghe chuyện của {survivors} quỹ thắng. {dead} quỹ đã đóng cửa không ai kể. Thành tích đẹp có thể chỉ là kẻ sống sót của may rủi.",
  "takeaway": "Trước khi tin một thành tích, hỏi: có bao nhiêu người đã thử và biến mất?",
  "myth": "Thắng {years} năm liền thì chắc chắn phải giỏi.",
  "fact": "Không. Trong {funds} quỹ toàn tung đồng xu, vẫn có {survivors} quỹ thắng {years} năm liền.",
  "story": [
    {
      "at": 0.3,
      "label": "Đông đúc",
      "say": "Năm đầu, một nửa đã biến mất."
    },
    {
      "at": 0.6,
      "label": "Thưa dần",
      "say": "Năm thứ năm còn {after5} quỹ."
    },
    {
      "at": 1.0,
      "label": "Huyền thoại",
      "say": "Năm thứ {years}: {survivors} quỹ, thành tích hoàn hảo."
    }
  ],
  "formula": "N_{\\mathrm{sống}}=N\\cdot 0{,}5^{T}",
  "formula_numeric": "<<funds>>\\cdot 0{,}5^{<<years>>}\\approx<<survivors>>",
  "symbols": [
    {
      "sym": "N",
      "say": "Số quỹ ban đầu."
    },
    {
      "sym": "T",
      "say": "Số năm."
    }
  ],
  "outputs": [
    {
      "label": "quỹ ban đầu",
      "key": "funds"
    },
    {
      "label": "còn sau 5 năm",
      "key": "after5"
    },
    {
      "label": "còn sau 10 năm",
      "key": "survivors",
      "highlight": true
    },
    {
      "label": "lãi TB của kẻ sống sót",
      "key": "surv_avg"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Quảng cáo: “Quỹ thắng {years} năm liền!”",
    "punch": "{dead} quỹ đã đóng: …",
    "truth": "Trong {funds} quỹ tung đồng xu, {survivors} quỹ thắng {years} năm liền."
  },
  "caption": "Thành tích đẹp có thể chỉ là may mắn sống sót. Mô phỏng 10.000 quỹ không có kỹ năng. Nội dung giáo dục về thống kê, không phải khuyến nghị.",
  "hashtags": [
    "thienkien",
    "survivorshipbias",
    "dautu",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "0{,}5",
    "0,5",
    "5 năm",
    "10 năm",
    "10.000",
    "thứ hai",
    "thứ năm"
  ],
  "formula_parts": [
    "N_{\\mathrm{sống}}=N\\cdot 0{,}5^{T}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "{funds} quỹ → còn {survivors}",
  "max_seconds": 90
}
```
