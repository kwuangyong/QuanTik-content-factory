# Gấp thếp: thắng gần như mọi ván, rồi mất sạch

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `martingale_demo`. Style gợi ý: `dark-truth`.

## Là gì

Thua thì cược gấp đôi, thắng thì quay về mức đầu. Phổ biến trong sòng bạc Pháp từ thế kỷ 18. Mỗi lần thắng chỉ lời đúng một đơn vị.

Nguồn: Wikipedia: Martingale (betting system)

## Ý chính

Chiến thuật gấp thếp thắng gần như mọi ván. Đó chính là cái bẫy.

Vòng quay có {p_red} cơ hội ra đỏ. Thua thì gấp đôi: 1, 2, 4, 8. Vốn {start} đơn vị chịu được 7 ván thua liền. Code cho {players} người chơi gấp thếp {rounds} ván. Kết quả: {ruined} cháy sạch vốn. Đây là một người chơi thật trong mô phỏng. Vốn leo đều lên {path_peak}, rồi một chuỗi thua kéo về 0 sau {path_len} ván. Bề mặt 3D: càng chơi lâu, xác suất cháy càng tiến về gần như chắc chắn, dù vốn dày cỡ nào.

## Mặt tối

Bạn thấy hàng trăm lần thắng nhỏ, nên tin là hệ thống chạy. Nhà cái chỉ cần đợi một chuỗi thua. Trung bình mỗi người mất {loss_avg} đơn vị.

## Mang về

Thắng thường xuyên không có nghĩa là có lợi thế. Hãy hỏi: lần thua tệ nhất lấy đi bao nhiêu?

## video_defaults

```json
{
  "tag": "GẤP THẾP",
  "title": "Gấp thếp: thắng gần như mọi ván, rồi mất sạch",
  "hook": "Chiến thuật gấp thếp thắng gần như mọi ván. Đó chính là cái bẫy.",
  "kicker": "Martingale",
  "dark_kicker": "SỰ THẬT ĐEN TỐI",
  "wiki": {
    "title": "Martingale (gấp thếp)",
    "en": "Martingale betting system",
    "lines": [
      "Thua thì cược gấp đôi, thắng thì quay về mức đầu.",
      "Phổ biến trong sòng bạc Pháp từ thế kỷ 18.",
      "Mỗi lần thắng chỉ lời đúng một đơn vị."
    ],
    "source": "Wikipedia: Martingale (betting system)",
    "say": "Martingale, hay gấp thếp: thua thì cược gấp đôi, thắng thì quay về mức đầu. Mỗi lần thắng chỉ lời đúng một đơn vị."
  },
  "anim": {
    "kind": "wheel",
    "label": "Thua là gấp đôi: 1, 2, 4… 128"
  },
  "beats": [
    "Vòng quay có {p_red} cơ hội ra đỏ. Thua thì gấp đôi: 1, 2, 4, 8. Vốn {start} đơn vị chịu được 7 ván thua liền.",
    "Code cho {players} người chơi gấp thếp {rounds} ván. Kết quả: {ruined} cháy sạch vốn.",
    "Đây là một người chơi thật trong mô phỏng. Vốn leo đều lên {path_peak}, rồi một chuỗi thua kéo về 0 sau {path_len} ván.",
    "Bề mặt 3D: càng chơi lâu, xác suất cháy càng tiến về gần như chắc chắn, dù vốn dày cỡ nào."
  ],
  "dark": "Bạn thấy hàng trăm lần thắng nhỏ, nên tin là hệ thống chạy. Nhà cái chỉ cần đợi một chuỗi thua. Trung bình mỗi người mất {loss_avg} đơn vị.",
  "takeaway": "Thắng thường xuyên không có nghĩa là có lợi thế. Hãy hỏi: lần thua tệ nhất lấy đi bao nhiêu?",
  "myth": "Gấp thếp thì sớm muộn cũng thắng lại, không thể mất.",
  "fact": "Sai. {ruined} người gấp thếp cháy sạch chỉ sau {rounds} ván. Chuỗi 8 ván thua có xác suất {p_streak8} mỗi lần, nhưng chơi đủ lâu là gặp.",
  "story": [
    {
      "at": 0.3,
      "label": "Leo đều",
      "say": "Thắng, thắng, thắng. Mỗi lần lời một đơn vị. Cảm giác rất an toàn."
    },
    {
      "at": 0.8,
      "label": "Rung lắc",
      "say": "Thỉnh thoảng một chuỗi thua kéo vốn tụt sâu, rồi gỡ lại. Niềm tin tăng thêm."
    },
    {
      "at": 1.0,
      "label": "Sập",
      "say": "Rồi chuỗi thua dài tới. Vốn từ {path_peak} về 0 trong vài ván."
    }
  ],
  "formula": "P(\\mathrm{thua}\\ k\\ \\mathrm{ván\\ liền})=(1-p)^k",
  "formula_numeric": "(1-<<p_red:pct1>>)^8=<<p_streak8>>",
  "symbols": [
    {
      "sym": "p",
      "say": "Xác suất thắng mỗi ván."
    },
    {
      "sym": "k",
      "say": "Số ván thua liên tiếp làm cháy vốn."
    }
  ],
  "outputs": [
    {
      "label": "xác suất ra đỏ",
      "key": "p_red"
    },
    {
      "label": "số người chơi",
      "key": "players"
    },
    {
      "label": "cháy vốn",
      "key": "ruined",
      "highlight": true
    },
    {
      "label": "vốn TB cuối",
      "key": "mean_final"
    }
  ],
  "meme": {
    "format": "expectation-reality",
    "setup": "Gấp thếp: thắng đều mỗi ngày",
    "punch": "Ngày thứ {path_len}:",
    "truth": "{ruined} người gấp thếp cháy vốn sau {rounds} ván. Thắng nhỏ đều đặn che giấu cú thua khổng lồ."
  },
  "caption": "Gấp thếp (martingale) thắng gần như mọi ván, vì sao vẫn cháy túi? Mô phỏng 10.000 người chơi, code chạy thật. Nội dung giáo dục về xác suất, không cổ vũ cờ bạc.",
  "hashtags": [
    "gapthep",
    "martingale",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1, 2, 4, 8",
    "1, 2, 4… 128",
    "7 ván",
    "8 ván",
    "thế kỷ 18",
    "10.000"
  ],
  "formula_parts": [
    "P(\\mathrm{thua}\\ k\\ \\mathrm{ván\\ liền})=(1-p)^k"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Thua là gấp đôi: 1, 2, 4… 128",
  "max_seconds": 90
}
```
