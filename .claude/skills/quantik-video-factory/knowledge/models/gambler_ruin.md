# Nhà cái chỉ cần lệch một chút

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `gambler_ruin_demo`. Style gợi ý: `dark-truth`.

## Là gì

Pascal đặt bài toán, Fermat giải năm 1656. Huygens công bố năm 1657. Hỏi: với vốn hữu hạn, xác suất cháy trước khi đạt mục tiêu là bao nhiêu?

Nguồn: Wikipedia: Gambler's ruin

## Ý chính

Nhà cái không cần bạn thua nhiều. Chỉ cần bạn chơi đủ lâu.

Mỗi chấm là một người, bắt đầu với {start} đồng, muốn chạm {target}. Mỗi ván thắng {p_player}, chỉ kém 50/50 một chút. Công thức cho xác suất cháy: {ruin_edge}. Code mô phỏng {sims} người ra {ruin_sim}, khớp với công thức. Đường xám là ván công bằng. Đường đỏ chỉ lệch 1 điểm phần trăm. Mục tiêu càng xa, đường đỏ càng dính sát 100%. Bề mặt 3D: tỷ lệ thắng giảm một chút, mục tiêu tăng một chút, xác suất cháy dựng đứng.

## Mặt tối

Ván công bằng thì cháy {ruin_fair}. Lệch nhẹ về nhà cái thì cháy {ruin_edge}. Mục tiêu {target_far} thì cháy {ruin_far}. Nhà cái chỉ cần thời gian.

## Mang về

Lợi thế nhỏ cộng với thời gian là thứ đáng sợ nhất. Trên thị trường, phí và trượt giá cũng là một lợi thế nhỏ chống lại bạn.

## video_defaults

```json
{
  "tag": "PHÁ SẢN",
  "title": "Nhà cái chỉ cần lệch một chút",
  "hook": "Nhà cái không cần bạn thua nhiều. Chỉ cần bạn chơi đủ lâu.",
  "kicker": "Gambler's ruin",
  "wiki": {
    "title": "Bài toán phá sản con bạc",
    "en": "Gambler's ruin",
    "lines": [
      "Pascal đặt bài toán, Fermat giải năm 1656.",
      "Huygens công bố năm 1657.",
      "Hỏi: với vốn hữu hạn, xác suất cháy trước khi đạt mục tiêu là bao nhiêu?"
    ],
    "source": "Wikipedia: Gambler's ruin",
    "say": "Bài toán phá sản con bạc có từ thời Pascal và Fermat: với vốn hữu hạn, xác suất cháy trước khi đạt mục tiêu là bao nhiêu?"
  },
  "anim": {
    "kind": "crowd",
    "mode": "survive",
    "left": 27,
    "label": "Chỉ {win_edge} về đích, còn lại cháy túi"
  },
  "beats": [
    "Mỗi chấm là một người, bắt đầu với {start} đồng, muốn chạm {target}. Mỗi ván thắng {p_player}, chỉ kém 50/50 một chút.",
    "Công thức cho xác suất cháy: {ruin_edge}. Code mô phỏng {sims} người ra {ruin_sim}, khớp với công thức.",
    "Đường xám là ván công bằng. Đường đỏ chỉ lệch 1 điểm phần trăm. Mục tiêu càng xa, đường đỏ càng dính sát 100%.",
    "Bề mặt 3D: tỷ lệ thắng giảm một chút, mục tiêu tăng một chút, xác suất cháy dựng đứng."
  ],
  "dark": "Ván công bằng thì cháy {ruin_fair}. Lệch nhẹ về nhà cái thì cháy {ruin_edge}. Mục tiêu {target_far} thì cháy {ruin_far}. Nhà cái chỉ cần thời gian.",
  "takeaway": "Lợi thế nhỏ cộng với thời gian là thứ đáng sợ nhất. Trên thị trường, phí và trượt giá cũng là một lợi thế nhỏ chống lại bạn.",
  "myth": "Chỉ thua thiệt chút xíu mỗi ván thì chẳng ảnh hưởng gì.",
  "fact": "Sai. Thắng {p_player} mỗi ván, từ {start} lên {target} có tới {ruin_edge} khả năng cháy trước. Ván 50/50 chỉ là {ruin_fair}.",
  "story": [
    {
      "at": 0.15,
      "label": "Gần đích",
      "say": "Mục tiêu gần, hai đường còn sát nhau."
    },
    {
      "at": 0.5,
      "label": "Tách xa",
      "say": "Mục tiêu xa dần, đường đỏ vọt lên trước."
    },
    {
      "at": 1.0,
      "label": "Gần chắc chắn",
      "say": "Mục tiêu {target_far}: cháy {ruin_far}."
    }
  ],
  "formula": "P_{\\mathrm{cháy}}=\\frac{r^{a}-r^{N}}{1-r^{N}},\\ r=\\frac{q}{p}",
  "formula_numeric": "P_{\\mathrm{cháy}}=<<ruin_edge>>",
  "symbols": [
    {
      "sym": "a",
      "say": "Vốn ban đầu."
    },
    {
      "sym": "N",
      "say": "Mục tiêu muốn đạt."
    }
  ],
  "outputs": [
    {
      "label": "thắng mỗi ván",
      "key": "p_player"
    },
    {
      "label": "cháy, ván công bằng",
      "key": "ruin_fair"
    },
    {
      "label": "cháy, công thức",
      "key": "ruin_edge",
      "highlight": true
    },
    {
      "label": "cháy, mô phỏng",
      "key": "ruin_sim"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Thua có chút xíu mỗi ván thôi mà.”",
    "punch": "Toán: “Cháy {ruin_edge}.”",
    "truth": "Thắng {p_player} mỗi ván, từ {start} lên {target}: {ruin_edge} khả năng cháy trước."
  },
  "caption": "Vì sao nhà cái luôn thắng về dài hạn? Bài toán phá sản con bạc từ thời Pascal, mô phỏng 4.000 người. Nội dung giáo dục về xác suất, không cổ vũ cờ bạc.",
  "hashtags": [
    "xacsuat",
    "gamblersruin",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "shorts"
  ],
  "allowed_literals": [
    "50/50",
    "1656",
    "1657",
    "1 điểm",
    "100%",
    "4.000"
  ],
  "formula_parts": [
    "P_{\\mathrm{cháy}}=\\frac{r^{a}-r^{N}}{1-r^{N}},\\ r=\\frac{q}{p}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Chỉ {win_edge} về đích, còn lại cháy túi",
  "max_seconds": 90
}
```
