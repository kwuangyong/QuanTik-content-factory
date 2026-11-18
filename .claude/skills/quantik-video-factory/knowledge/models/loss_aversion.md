# Mất tiền đau gấp đôi được tiền

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `loss_aversion_demo`. Style gợi ý: `dark-truth`.

## Là gì

Kahneman và Tversky công bố Lý thuyết triển vọng năm 1979. Kahneman nhận Nobel Kinh tế năm 2002. Ước lượng năm 1992: nỗi đau mất mát nặng khoảng 2,25 lần.

Nguồn: Kahneman & Tversky (1979), Econometrica; Tversky & Kahneman (1992)

## Ý chính

Mất {stake} nghìn đau hơn gấp đôi niềm vui được {stake} nghìn. Não bạn được lập trình như vậy.

Hai đĩa cân cùng số tiền: mất {stake} và được {stake}. Nhưng đĩa mất nặng hơn hẳn trong đầu bạn. Theo hàm giá trị, được {stake} cho cảm giác {v_gain}. Mất {stake} cho {v_loss}. Nặng gấp {pain_ratio}. Đường cong gãy ở số 0: phía lỗ dốc hơn phía lãi. Đó là lý do cắt lỗ khó đến vậy. Bề mặt 3D: hệ số sợ lỗ càng lớn, vùng lỗ càng lún sâu.

## Mặt tối

Tung đồng xu thua {stake}, phải thắng khoảng {need_win} người ta mới chịu chơi. Vì sợ lỗ, nhiều người ôm cổ phiếu lỗ quá lâu và chốt lãi quá sớm.

## Mang về

Nhận ra nỗi sợ lỗ là bước đầu. Quy tắc viết sẵn trước khi vào lệnh giúp bạn không quyết định bằng cảm giác.

## video_defaults

```json
{
  "tag": "SỢ LỖ",
  "title": "Mất tiền đau gấp đôi được tiền",
  "hook": "Mất {stake} nghìn đau hơn gấp đôi niềm vui được {stake} nghìn. Não bạn được lập trình như vậy.",
  "kicker": "Prospect theory",
  "wiki": {
    "title": "Ác cảm mất mát",
    "en": "Loss aversion · Prospect theory",
    "lines": [
      "Kahneman và Tversky công bố Lý thuyết triển vọng năm 1979.",
      "Kahneman nhận Nobel Kinh tế năm 2002.",
      "Ước lượng năm 1992: nỗi đau mất mát nặng khoảng 2,25 lần."
    ],
    "source": "Kahneman & Tversky (1979), Econometrica; Tversky & Kahneman (1992)",
    "say": "Năm 1979, Kahneman và Tversky công bố Lý thuyết triển vọng, công trình góp phần mang về giải Nobel."
  },
  "anim": {
    "kind": "scale",
    "left": "−{stake}",
    "right": "+{stake}",
    "tilt": 20,
    "label": "Cùng số tiền, hai cảm giác khác nhau"
  },
  "beats": [
    "Hai đĩa cân cùng số tiền: mất {stake} và được {stake}. Nhưng đĩa mất nặng hơn hẳn trong đầu bạn.",
    "Theo hàm giá trị, được {stake} cho cảm giác {v_gain}. Mất {stake} cho {v_loss}. Nặng gấp {pain_ratio}.",
    "Đường cong gãy ở số 0: phía lỗ dốc hơn phía lãi. Đó là lý do cắt lỗ khó đến vậy.",
    "Bề mặt 3D: hệ số sợ lỗ càng lớn, vùng lỗ càng lún sâu."
  ],
  "dark": "Tung đồng xu thua {stake}, phải thắng khoảng {need_win} người ta mới chịu chơi. Vì sợ lỗ, nhiều người ôm cổ phiếu lỗ quá lâu và chốt lãi quá sớm.",
  "takeaway": "Nhận ra nỗi sợ lỗ là bước đầu. Quy tắc viết sẵn trước khi vào lệnh giúp bạn không quyết định bằng cảm giác.",
  "myth": "Mình quyết định tiền bạc hoàn toàn bằng lý trí.",
  "fact": "Không ai cả. Mất {stake} cảm thấy như {v_loss}, được {stake} chỉ như {v_gain}.",
  "story": [
    {
      "at": 0.45,
      "label": "Vùng lỗ",
      "say": "Phía lỗ, đường cong dốc đứng."
    },
    {
      "at": 0.55,
      "label": "Điểm gãy",
      "say": "Tại số 0, đường cong gãy gập."
    },
    {
      "at": 1.0,
      "label": "Vùng lãi",
      "say": "Phía lãi thoải dần: lãi thêm vui thêm ít."
    }
  ],
  "formula": "v(x)=\\begin{cases}x^{\\alpha} & x\\ge 0\\\\ -\\lambda(-x)^{\\alpha} & x<0\\end{cases}",
  "formula_numeric": "\\alpha=<<alpha>>,\\ \\lambda=<<lam>>",
  "symbols": [
    {
      "sym": "\\lambda",
      "say": "Hệ số sợ lỗ."
    },
    {
      "sym": "\\alpha",
      "say": "Độ cong."
    }
  ],
  "outputs": [
    {
      "label": "λ sợ lỗ",
      "key": "lam"
    },
    {
      "label": "cảm giác được 100",
      "key": "v_gain"
    },
    {
      "label": "cảm giác mất 100",
      "key": "v_loss",
      "highlight": true
    },
    {
      "label": "thắng bao nhiêu mới chịu chơi",
      "key": "need_win"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Lãi {stake}: “Ừ, cũng được.”",
    "punch": "Lỗ {stake}: mất ngủ ba đêm.",
    "truth": "Hàm giá trị: mất {stake} nặng gấp {pain_ratio} được {stake}."
  },
  "caption": "Vì sao mất tiền đau hơn được tiền? Lý thuyết triển vọng của Kahneman & Tversky, tính bằng code. Nội dung giáo dục về tâm lý ra quyết định.",
  "hashtags": [
    "tamlyhoc",
    "lossaversion",
    "kahneman",
    "QuanTik",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1979",
    "2002",
    "1992",
    "2,25",
    "ba đêm"
  ],
  "formula_parts": [
    "v(x)=\\begin{cases}x^{\\alpha} & x\\ge 0\\\\ -\\lambda(-x)^{\\alpha} & x<0\\end{cases}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Cùng số tiền, hai cảm giác khác nhau",
  "max_seconds": 90
}
```
