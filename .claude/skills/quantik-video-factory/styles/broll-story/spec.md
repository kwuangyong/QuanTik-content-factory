# broll-story

B-roll thật (Pexels) + hoạt họa vẽ bằng code + chart/code của mô hình, chuyển cảnh gối đầu (fade/slide/zoom chồng lên
cảnh trước). Hook và câu mang về đặt trên footage. Dùng cho loạt tiếng Anh (`"lang": "en"`), dùng được cho tiếng Việt.

Episode khai báo cảnh trong `sequence` (theo thứ tự); pipeline tự thêm cảnh mang về và thẻ cuối.

| `type` | Hiển thị | Trường |
| --- | --- | --- |
| `hook` | footage + hook bật từng chữ | `clip`, `say`, tuỳ chọn `anim`, `start` |
| `broll` | footage + chữ lớn (+ hoạt họa phía dưới) | `clip`, `text`, `say`, `anim`, `opt`, `start`, `speed` |
| `anim` | hoạt họa trong `pipeline/illustrations.py` | `anim` (coins, crowd, halving, cards, roulette, lottery_balls, payoff_matrix, auction, bluff_scale), `text`, `opt` |
| `chart` | chart mô hình vẽ dần từ `from` → `to` | `label`, `note`, `say` |
| `number` | số lớn đếm lên | `value` (placeholder), `label` |
| `image` | ảnh Ken Burns + nhãn + ghi nguồn | `image` (key trong images/manifest.json), `text` |
| `code` / `terminal` / `formula` / `surface` / `statement` | như các style khác | |

Cuối: `takeaway` (+ `takeaway_clip` để đặt trên footage), thẻ cuối có CTA, lưu ý giáo dục (`sensitive`) và miễn trừ.

**Viết lời:** 6–7 cảnh, ~140 từ tiếng Anh để vừa 60s. Mọi số qua `{placeholder}`; năm/nguồn lịch sử vào `facts`.
