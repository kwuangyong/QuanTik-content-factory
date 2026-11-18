# Lướt sóng càng nhiều, ai giàu lên?

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `overtrading_demo`. Style gợi ý: `dark-truth`.

## Là gì

Barber và Odean năm 2000: nhà đầu tư giao dịch nhiều nhất có kết quả kém nhất. Tên nghiên cứu: Trading Is Hazardous to Your Wealth. Mỗi vòng mua bán đều mất phí và thuế, dù đúng hay sai.

Nguồn: Barber & Odean (2000), Journal of Finance

## Ý chính

Bạn giao dịch càng nhiều, phí và thuế càng chắc chắn ăn vào vốn. Thị trường chưa kịp làm gì.

Giả định mỗi vòng mua rồi bán tốn {fee_round} gồm phí hai chiều và thuế bán. Nghe nhỏ. Nhưng nhân lên theo số lần. Cùng một danh mục trong {days} phiên. Giữ nguyên: {ret0}. 8 vòng mỗi tháng: {ret8}. 20 vòng mỗi tháng: {ret20}. Bốn đường cùng một thị trường, chỉ khác số lần giao dịch. Đường đỏ chìm dần dù thị trường đi lên. Bề mặt 3D: số vòng giao dịch nhân với phí mỗi vòng là phần vốn mất đi mỗi năm, chắc chắn như toán.

## Mặt tối

20 vòng mỗi tháng là {trades_year20} vòng mỗi năm, tổng chi phí khoảng {cost20} vốn. Lời lỗ của bạn là may rủi. Phí thì không.

## Mang về

Mỗi lệnh phải đáng giá hơn chi phí của nó. Biết chi phí thật của mình là bước quản trị rủi ro đầu tiên.

## video_defaults

```json
{
  "tag": "PHÍ",
  "title": "Lướt sóng càng nhiều, ai giàu lên?",
  "hook": "Bạn giao dịch càng nhiều, phí và thuế càng chắc chắn ăn vào vốn. Thị trường chưa kịp làm gì.",
  "kicker": "Chi phí giao dịch",
  "wiki": {
    "title": "Giao dịch quá mức",
    "en": "Overtrading",
    "lines": [
      "Barber và Odean năm 2000: nhà đầu tư giao dịch nhiều nhất có kết quả kém nhất.",
      "Tên nghiên cứu: Trading Is Hazardous to Your Wealth.",
      "Mỗi vòng mua bán đều mất phí và thuế, dù đúng hay sai."
    ],
    "source": "Barber & Odean (2000), Journal of Finance",
    "say": "Năm 2000, Barber và Odean phát hiện: nhà đầu tư giao dịch nhiều nhất có kết quả kém nhất."
  },
  "anim": {
    "kind": "ticker",
    "trades": 20,
    "label": "Mỗi vòng mua bán mất {fee_round}"
  },
  "beats": [
    "Giả định mỗi vòng mua rồi bán tốn {fee_round} gồm phí hai chiều và thuế bán. Nghe nhỏ. Nhưng nhân lên theo số lần.",
    "Cùng một danh mục trong {days} phiên. Giữ nguyên: {ret0}. 8 vòng mỗi tháng: {ret8}. 20 vòng mỗi tháng: {ret20}.",
    "Bốn đường cùng một thị trường, chỉ khác số lần giao dịch. Đường đỏ chìm dần dù thị trường đi lên.",
    "Bề mặt 3D: số vòng giao dịch nhân với phí mỗi vòng là phần vốn mất đi mỗi năm, chắc chắn như toán."
  ],
  "dark": "20 vòng mỗi tháng là {trades_year20} vòng mỗi năm, tổng chi phí khoảng {cost20} vốn. Lời lỗ của bạn là may rủi. Phí thì không.",
  "takeaway": "Mỗi lệnh phải đáng giá hơn chi phí của nó. Biết chi phí thật của mình là bước quản trị rủi ro đầu tiên.",
  "myth": "Giao dịch nhiều thì có nhiều cơ hội lãi hơn.",
  "fact": "Không có lợi thế thì chỉ có nhiều chi phí hơn. Cùng danh mục: giữ nguyên {ret0}, 20 vòng mỗi tháng {ret20}.",
  "story": [
    {
      "at": 0.3,
      "label": "Gần nhau",
      "say": "Mấy tuần đầu, bốn đường gần như trùng nhau."
    },
    {
      "at": 0.7,
      "label": "Tách ra",
      "say": "Phí tích tụ, đường đỏ tụt hẳn."
    },
    {
      "at": 1.0,
      "label": "Cuối năm",
      "say": "Giữ nguyên {ret0}, 20 vòng mỗi tháng {ret20}."
    }
  ],
  "formula": "\\mathrm{chi\\ phí/năm}=n\\times 12\\times c",
  "formula_numeric": "20\\times 12\\times<<fee_round>>=<<cost20>>",
  "symbols": [
    {
      "sym": "n",
      "say": "Số vòng giao dịch mỗi tháng."
    },
    {
      "sym": "c",
      "say": "Chi phí một vòng."
    }
  ],
  "outputs": [
    {
      "label": "chi phí 1 vòng",
      "key": "fee_round"
    },
    {
      "label": "giữ nguyên",
      "key": "ret0"
    },
    {
      "label": "8 vòng/tháng",
      "key": "ret8"
    },
    {
      "label": "20 vòng/tháng",
      "key": "ret20",
      "highlight": true
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Hôm nay lướt 5 lệnh.”",
    "punch": "Phí và thuế: “Cảm ơn nhé.”",
    "truth": "20 vòng mỗi tháng: chi phí khoảng {cost20} vốn mỗi năm."
  },
  "caption": "Giao dịch càng nhiều, chi phí càng chắc chắn. Mô phỏng cùng một danh mục với số vòng khác nhau; mức phí là giả định, kiểm tra biểu phí công ty chứng khoán của bạn. Nội dung giáo dục, không phải khuyến nghị.",
  "hashtags": [
    "chiphigiaodich",
    "quanlyvon",
    "chungkhoan",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "2000",
    "8 vòng",
    "20 vòng",
    "5 lệnh",
    "12"
  ],
  "formula_parts": [
    "\\mathrm{chi\\ phí/năm}=n\\times 12\\times c"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Mỗi vòng mua bán mất {fee_round}",
  "max_seconds": 90
}
```
