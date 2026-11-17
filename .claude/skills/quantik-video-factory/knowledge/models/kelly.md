# Tiêu chuẩn Kelly — đặt bao nhiêu là vừa?

Nguồn định nghĩa gốc: `glossary.json` id `kelly`: f* = W − (1 − W)/R, Half-Kelly = 0,5 × f* khi áp dụng thực tế.

## Công thức

$$f^*=W-\frac{1-W}{R}$$

- W: tỷ lệ thắng (0–1); R: lãi trung bình / lỗ trung bình.
- Tốc độ tăng trưởng log mỗi lần: g(f) = W·ln(1 + fR) + (1 − W)·ln(1 − f). f* là điểm cực đại của g.

## Tham số đẹp để minh hoạ

W = 55%, R = 1 → f* = 10%. 2.000 người × 500 lần đặt, seed 4. Trung vị tài sản cuối: ½ Kelly ≈ 6,5 lần, Kelly ≈ 12,2 lần, 2× Kelly ≈ 0,9 lần (lỗ dù có lợi thế), 4× Kelly ≈ gần về 0.

## Ngưỡng đọc nhanh (glossary)

- f* < 0: kỳ vọng âm, không nên tham gia.
- 0–20%: dùng Half-Kelly để giảm rủi ro thực tế.
- > 20%: kỳ vọng dương mạnh — vẫn nên chiết giảm.

## Ví dụ HOSE

- W và R ước lượng từ backtest luôn có sai số; đặt quá tay vì ước lượng lạc quan là rủi ro lớn nhất, nên thực tế dùng ½ hoặc ¼ Kelly.
- Kelly mô hình hoá cược độc lập; danh mục cổ phiếu tương quan (cùng ngành ngân hàng chẳng hạn) không độc lập.

## Sai lầm hay gặp

- Nghĩ “có lợi thế thì đặt càng nhiều càng giàu”. Vượt 2× Kelly thì tăng trưởng log âm.
- Dùng f* như tỷ trọng danh mục tối ưu (glossary: không mặc nhiên đúng).
- Quên đòn bẩy và phí giao dịch làm thay đổi R.

## video_defaults

```json
{
  "tag": "KELLY",
  "title": "Có lợi thế mà vẫn mất tiền? Bài toán Kelly",
  "hook": "Có lợi thế vẫn *cháy tài khoản*? Một giáo sư toán từng khiến sòng bài phải đổi luật.",
  "hook_visual": "casino",
  "cold_open": [
    {
      "say": "Giáo sư toán Edward Thorp ngồi vào bàn blackjack ở Las Vegas và bắt đầu đếm bài.",
      "visual": "casino",
      "caption": "Giáo sư toán vào *sòng bài*"
    },
    {
      "say": "Ông dùng công thức Kelly để biết nên cược bao nhiêu. Sòng bài phải đổi luật.",
      "visual": "casino",
      "caption": "Sòng bài phải *đổi luật*"
    }
  ],
  "kicker": "Kelly criterion",
  "beats": [
    "Công thức Kelly: tỷ lệ thắng trừ tỷ lệ thua chia cho tỷ lệ lãi lỗ. Code mô phỏng 2.000 người, mỗi người đặt {bets} lần, với bốn mức cược khác nhau.",
    "Với tỷ lệ thắng {W}, Kelly là {f_star} vốn mỗi lần. Đặt đúng mức đó, tài sản trung vị nhân {med_full}. Đặt gấp đôi, chỉ còn {med_double}.",
    "Bốn đường là bốn mức cược. Đường đỏ đặt {quad_kelly} mỗi lần: cùng lợi thế, nhưng gần như mất sạch.",
    "Bề mặt 3D là tốc độ tăng trưởng theo mức cược và tỷ lệ thắng. Có một đỉnh. Vượt qua đỉnh, càng đặt nhiều càng nghèo."
  ],
  "outputs": [
    {
      "label": "tỷ lệ thắng W",
      "key": "W"
    },
    {
      "label": "Kelly f*",
      "key": "f_star",
      "highlight": true
    },
    {
      "label": "trung vị, ½ Kelly",
      "key": "med_half"
    },
    {
      "label": "trung vị, Kelly",
      "key": "med_full"
    },
    {
      "label": "trung vị, 2× Kelly",
      "key": "med_double"
    },
    {
      "label": "trung vị, 4× Kelly",
      "key": "med_quad"
    }
  ],
  "takeaway": "Lợi thế chưa đủ. Cỡ cược quyết định bạn có sống sót hay không. Dân quant thường chỉ dùng nửa Kelly.",
  "cta": "Xem Kelly và các tham số quản lý vốn trong phân tích Quant tại quantik.io.vn",
  "myth": "Có lợi thế thì càng đặt nhiều càng giàu nhanh.",
  "fact": "Sai. Cùng tỷ lệ thắng {W}, đặt {f_star} cho trung vị {med_full}; đặt {double_kelly} chỉ còn {med_double}.",
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Mình thắng {W}, đặt hết vốn luôn!”",
    "punch": "Kelly: “Bình tĩnh. {f_star} thôi.”",
    "truth": "Đặt {quad_kelly} mỗi lần, tài sản trung vị gần như về 0 dù có lợi thế."
  },
  "story": [
    {
      "at": 0.2,
      "label": "Xuất phát",
      "say": "Bốn nhóm người, cùng lợi thế, chỉ khác mức cược."
    },
    {
      "at": 0.6,
      "label": "Tách đôi",
      "say": "Nhóm cược vừa phải tăng đều. Nhóm cược lớn rung lắc dữ dội."
    },
    {
      "at": 1.0,
      "label": "Kết quả",
      "say": "Kelly nhân {med_full}. Gấp đôi Kelly còn {med_double}. Gấp bốn gần như về 0."
    }
  ],
  "formula": "f^*=W-\\frac{1-W}{R}",
  "formula_parts": [
    "f^*",
    "f^*=W",
    "f^*=W-\\frac{1-W}{R}"
  ],
  "formula_numeric": "f^*=<<W>>-\\frac{1-<<W>>}{1}=<<f_star>>",
  "symbols": [
    {
      "sym": "W",
      "say": "Tỷ lệ thắng mỗi lần."
    },
    {
      "sym": "R",
      "say": "Lãi trung bình chia lỗ trung bình."
    },
    {
      "sym": "f^*",
      "say": "Tỷ lệ vốn đặt mỗi lần để tài sản tăng nhanh nhất về dài hạn."
    }
  ],
  "caption": "Có lợi thế vẫn có thể mất tiền nếu đặt quá tay. Kelly tìm mức cược tối ưu, và vì sao dân quant chỉ dùng một nửa. Code chạy thật, mô phỏng seed cố định.",
  "hashtags": [
    "quant",
    "kelly",
    "quanlyvon",
    "chungkhoan",
    "dautu",
    "QuanTik"
  ],
  "allowed_literals": [
    "2.000",
    "1",
    "0",
    "bốn mức"
  ],
  "thumb": {
    "tag": "Kelly criterion",
    "headline": [
      {
        "t": "CÙNG MỘT LỢI THẾ",
        "size": 110
      },
      {
        "t": "CƯỢC GẤP ĐÔI",
        "size": 160
      },
      {
        "t": "CÒN LẠI [o]{med_double}[/o]",
        "size": 140
      }
    ],
    "pill": "Kelly chọn tỷ trọng vốn · code Python",
    "labels": [
      {
        "label": "Nửa Kelly",
        "value": "{med_half}",
        "color": "green"
      },
      {
        "label": "Gấp đôi",
        "value": "{med_double}",
        "color": "orange"
      }
    ]
  },
  "thumb_variants": {
    "meme-quant": {
      "headline": [
        {
          "t": "CƯỢC [o]{quad_kelly}[/o] VỐN",
          "size": 130
        },
        {
          "t": "TÀI SẢN CÒN",
          "size": 150
        },
        {
          "t": "[o]{med_quad}[/o]",
          "size": 190
        }
      ],
      "labels": [
        {
          "label": "Kelly",
          "value": "{f_star}",
          "color": "green"
        },
        {
          "label": "Quá tay",
          "value": "{quad_kelly}",
          "color": "orange"
        }
      ]
    },
    "myth-buster": {
      "headline": [
        {
          "t": "CÀNG CƯỢC NHIỀU",
          "size": 120
        },
        {
          "t": "CÀNG GIÀU?",
          "size": 180
        },
        {
          "t": "KELLY NÓI [g]{f_star}[/g]",
          "size": 130
        }
      ],
      "labels": [
        {
          "label": "Kelly đủ",
          "value": "{med_full}",
          "color": "green"
        },
        {
          "label": "Gấp bốn",
          "value": "{med_quad}",
          "color": "orange"
        }
      ]
    }
  },
  "facts": {
    "thorp": {
      "value": "Edward Thorp đếm bài blackjack và dùng tiêu chuẩn Kelly để định cỡ cược; sách Beat the Dealer khiến sòng bài đổi luật",
      "source": "Thorp, Beat the Dealer (1962); Poundstone, Fortune's Formula (2005)"
    }
  }
}
```
