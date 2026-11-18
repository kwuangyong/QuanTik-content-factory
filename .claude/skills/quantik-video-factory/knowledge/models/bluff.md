# Không bao giờ bluff là cách chơi dở nhất

> Chủ đề tâm lý / lý thuyết trò chơi. Code: `pipeline/mind_models.py` → `bluff_demo`. Style gợi ý: `dark-truth`.

## Là gì

Von Neumann và Morgenstern phân tích bluff trong sách năm 1944. Kết luận: bluff là một phần của chiến lược tối ưu. MDF: tần suất tối thiểu phải theo để đối thủ không bluff có lời.

Nguồn: von Neumann & Morgenstern, Theory of Games and Economic Behavior (1944)

## Ý chính

Không bao giờ bluff là cách chơi dở nhất. Toán chứng minh.

Nếu bạn chỉ cược khi có bài mạnh, đối thủ cứ bỏ mỗi khi bạn cược. Bạn không bao giờ được trả tiền. Cược bằng pot thì tối ưu là {bluff_pot} số lần cược là bluff. Cược nửa pot: {bluff_half}. Cược gấp đôi: {bluff_2x}. Đường đỏ là tỷ lệ bluff tối ưu, đường xanh là tần suất đối thủ phải theo. Cược càng to, càng được bluff nhiều. Bề mặt 3D là lời lỗ của một cú bluff theo cỡ cược và tần suất đối thủ bỏ bài.

## Mặt tối

Người không bao giờ bluff bị đọc như sách mở. Người bluff quá nhiều thì bị bắt. Ai lệch khỏi tỷ lệ cân bằng là đang trả tiền cho đối thủ.

## Mang về

Bị đoán trước là bị khai thác. Ở đâu có đối thủ quan sát, thứ cần tối ưu là tỷ lệ, không phải từng nước đi.

## video_defaults

```json
{
  "tag": "GTO",
  "title": "Không bao giờ bluff là cách chơi dở nhất",
  "hook": "Không bao giờ bluff là cách chơi dở nhất. Toán chứng minh.",
  "kicker": "Game theory optimal",
  "wiki": {
    "title": "Bluff trong lý thuyết trò chơi",
    "en": "Bluffing · GTO",
    "lines": [
      "Von Neumann và Morgenstern phân tích bluff trong sách năm 1944.",
      "Kết luận: bluff là một phần của chiến lược tối ưu.",
      "MDF: tần suất tối thiểu phải theo để đối thủ không bluff có lời."
    ],
    "source": "von Neumann & Morgenstern, Theory of Games and Economic Behavior (1944)",
    "say": "Từ năm 1944, von Neumann và Morgenstern đã chứng minh: bluff là một phần của chiến lược tối ưu."
  },
  "anim": {
    "kind": "cards",
    "hole": [
      "7♣",
      "6♣"
    ],
    "board": [
      "A♠",
      "K♦",
      "J♥",
      "2♠",
      "4♦"
    ],
    "label": "Bài rác, nhưng cược như bài mạnh"
  },
  "beats": [
    "Nếu bạn chỉ cược khi có bài mạnh, đối thủ cứ bỏ mỗi khi bạn cược. Bạn không bao giờ được trả tiền.",
    "Cược bằng pot thì tối ưu là {bluff_pot} số lần cược là bluff. Cược nửa pot: {bluff_half}. Cược gấp đôi: {bluff_2x}.",
    "Đường đỏ là tỷ lệ bluff tối ưu, đường xanh là tần suất đối thủ phải theo. Cược càng to, càng được bluff nhiều.",
    "Bề mặt 3D là lời lỗ của một cú bluff theo cỡ cược và tần suất đối thủ bỏ bài."
  ],
  "dark": "Người không bao giờ bluff bị đọc như sách mở. Người bluff quá nhiều thì bị bắt. Ai lệch khỏi tỷ lệ cân bằng là đang trả tiền cho đối thủ.",
  "takeaway": "Bị đoán trước là bị khai thác. Ở đâu có đối thủ quan sát, thứ cần tối ưu là tỷ lệ, không phải từng nước đi.",
  "myth": "Chơi chắc, chỉ cược khi có bài mạnh là an toàn nhất.",
  "fact": "Sai. Với cược bằng pot, chiến lược cân bằng có {bluff_pot} là bluff. Không bluff thì đối thủ chỉ việc bỏ.",
  "story": [
    {
      "at": 0.2,
      "label": "Cược nhỏ",
      "say": "Cược một phần ba pot: bluff {bluff_third}, phải theo {mdf_third}."
    },
    {
      "at": 0.4,
      "label": "Bằng pot",
      "say": "Cược bằng pot: bluff {bluff_pot}, phải theo {mdf_pot}."
    },
    {
      "at": 1.0,
      "label": "Cược lớn",
      "say": "Cược càng lớn, tỷ lệ bluff càng cao."
    }
  ],
  "formula": "\\mathrm{bluff}=\\frac{B}{P+2B},\\ \\mathrm{MDF}=\\frac{P}{P+B}",
  "formula_numeric": "\\frac{1}{3}=<<bluff_pot>>,\\ \\frac{1}{2}=<<mdf_pot>>",
  "symbols": [
    {
      "sym": "B",
      "say": "Cỡ cược."
    },
    {
      "sym": "P",
      "say": "Pot."
    }
  ],
  "outputs": [
    {
      "label": "bluff, cược nửa pot",
      "key": "bluff_half"
    },
    {
      "label": "bluff, cược bằng pot",
      "key": "bluff_pot",
      "highlight": true
    },
    {
      "label": "bluff, cược gấp đôi",
      "key": "bluff_2x"
    },
    {
      "label": "MDF, cược bằng pot",
      "key": "mdf_pot"
    }
  ],
  "meme": {
    "format": "nobody-quant",
    "setup": "Bạn: “Mình chỉ cược khi có bài mạnh.”",
    "punch": "Cả bàn: bỏ bài. Lần nào cũng vậy.",
    "truth": "Cân bằng với cược bằng pot cần {bluff_pot} là bluff."
  },
  "caption": "Vì sao bluff là toán chứ không phải liều? Tỷ lệ bluff và MDF theo lý thuyết trò chơi. Nội dung giáo dục về lý thuyết trò chơi, không cổ vũ cờ bạc.",
  "hashtags": [
    "poker",
    "gto",
    "bluff",
    "gametheory",
    "QuanTik",
    "tamlyhoc",
    "lythuyettrochoi",
    "xacsuat",
    "shorts"
  ],
  "allowed_literals": [
    "1944"
  ],
  "formula_parts": [
    "\\mathrm{bluff}=\\frac{B}{P+2B},\\ \\mathrm{MDF}=\\frac{P}{P+B}"
  ],
  "cta": "Xem cách QuanTik đo rủi ro bằng mô hình trong Phân tích Quant tại quantik.io.vn",
  "anim_say": "Bài rác, nhưng cược như bài mạnh",
  "max_seconds": 90
}
```
