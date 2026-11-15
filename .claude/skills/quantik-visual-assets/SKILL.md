---
name: quantik-visual-assets
description: Tạo và lấy hình ảnh cho video/carousel QuanTik — ảnh thật có giấy phép mở (Wikimedia Commons, ghi tác giả + giấy phép) cho người, hãng, nơi chốn, sự kiện được nhắc; ảnh minh hoạ vẽ bằng code khi không có ảnh tự do (thẻ nhân vật, thẻ tổ chức, thẻ sự kiện); nhân vật hình người phẳng (nhà đầu tư, dân quant, đối thủ poker, giáo sư, chuyên viên) với tư thế, nét mặt, bong bóng thoại; hiện vật (bàn poker, lá bài, chip, điện thoại/laptop có biểu đồ, bảng phấn, sách, báo) và 18 biểu tượng. Dùng skill này bất cứ khi nào kịch bản nhắc tới một người, một quỹ/hãng, một sự kiện, hoặc khi người dùng muốn video "nhiều hình hơn", "có nhân vật", "có ảnh thật", "minh hoạ", "hình ảnh độc đáo", "tìm ảnh cho …", "thêm hiện vật" — kể cả khi đang làm video bằng skill quantik-video-factory.
---

# QuanTik Visual Assets

Bộ công cụ hình ảnh dùng chung cho mọi video của `quantik-video-factory`. Code nằm trong skill đó
(`.claude/skills/quantik-video-factory/pipeline/`); file này là quy trình. Chạy lệnh từ thư mục `pipeline/` ấy.

## Ba loại hình — chọn đúng loại

| Cần hình cho | Dùng | Công cụ | Ghi trên màn hình |
| --- | --- | --- | --- |
| **Người / hãng / nơi chốn / sự kiện có thật** được nhắc tên | 1) ảnh thật giấy phép tự do (Commons, Openverse) · 2) không có thì ảnh minh hoạ | `visuals.py`, `images.py` | `Ảnh: <tác giả> · <giấy phép> · Wikimedia Commons` hoặc `Ảnh minh hoạ tạo bằng code` |
| **Vai trò chung** để kể chuyện (một nhà đầu tư, hai người chơi poker, một giáo sư) | nhân vật hình người + hiện vật | `figures.py` | không cần (không phải ai cụ thể) |
| **Ý niệm** (cảnh báo, ý tưởng, rủi ro, thời gian) | biểu tượng | `pictos.py` | không cần |

Ranh giới không được vượt:
- Chỉ ảnh **public domain, CC0, CC BY, CC BY-SA**. Từ chối NC, ND, "fair use", ảnh báo chí, ảnh Google, ảnh trang trường.
- **Không bao giờ** vẽ hay tạo bằng AI một hình trông như ảnh chụp người thật. Nhân vật `figures.py` là vai trò chung,
  không được dán tên người thật lên.
- Hiện vật và biểu tượng không chứa chữ số. Chữ trong bong bóng thoại đi qua QA như mọi chữ trên màn hình.

## Quy trình cho một kịch bản (`episodes/<id>.json`)

1. Viết xong kịch bản (lời, `screen`, `timeline`).
2. Xem kế hoạch: `python visuals.py auto ../episodes/<id>.json`
   — liệt kê mọi tên được nhắc (họ tác giả trong sổ nguồn + tên riêng hai từ như "Jay Regan") và loại ảnh mỗi tên sẽ nhận.
3. Thực hiện: `python visuals.py auto ../episodes/<id>.json --write`
   - tìm ảnh thật trên Commons (theo danh mục rồi theo tên file; phải ghi đúng tên, đúng giấy phép, không phải logo/chữ
     ký/tem); có thì tải về sổ ảnh, không thì vẽ thẻ minh hoạ (`--offline` để bỏ qua bước tìm);
   - thêm `entities` vào episode; đặt ảnh vào chỗ lời nhắc tên: mốc timeline (tối đa 2 ảnh/mốc), thẻ trích dẫn, hoặc cảnh
     chữ (đổi thành ảnh lớn);
   - chạy `qa/check_images.py`. Tên nào "CHƯA có chỗ đặt": thêm `"visual": {"kind": "image", "image": "<id>"}` cho
     một đoạn, hoặc ghi `waiver` có lý do (ví dụ "chỉ nhắc như tên khái niệm 'cân bằng Nash'").
4. Thêm nhân vật/hiện vật cho cảnh chữ nếu muốn khác mặc định của style (mục dưới).
5. `python pillar.py check ../episodes/<id>.json` → `python pillar.py make ../episodes/<id>.json`.

## Ảnh thật — lệnh tay

```bash
python visuals.py find "Jim Simons"                  # ứng viên tốt nhất (giấy phép tự do, đúng tên, không phải logo)
python images.py categories "Bell Labs"              # tìm danh mục Commons
python images.py category "Bell Labs Murray Hill"    # file trong danh mục, kèm giấy phép
python images.py search "Edward Thorp"               # tìm chữ (nhiễu hơn; kiểm kỹ đúng người)
python images.py fetch "File:<tên>" --id <id> --subject "<tên>" --depicts "<mô tả>"
python images.py ov-search "stock exchange"          # Openverse: Flickr, bảo tàng, thư viện… chỉ giấy phép tự do
python images.py ov-fetch <openverse id> --id <id> --subject "<mô tả>"
python images.py list
```

`visuals.py find/auto` tìm Commons trước, không có thì Openverse (tên ảnh phải ghi đúng tên người/vật). Openverse rất hợp
cho **ảnh khung cảnh và hiện vật thật** — sàn giao dịch, bàn poker, ván blackjack, toà nhà — đặt vào cảnh bằng
`"visual": {"kind": "image", "image": "<id>"}` (không cần khai báo entity vì không phải người cụ thể). Ghi công tự hiện
dưới cảnh: `Ảnh: <tác giả> · <giấy phép> · <nguồn> qua Openverse`.

Đã có trong sổ ảnh (`knowledge/images/ledger.json`): ảnh thật `jim-simons`, `claude-shannon` (Commons),
`trading-floor-chicago`, `poker-table-photo`, `blackjack-hand` (Openverse/Flickr, CC BY 2.0); ảnh minh hoạ `thorp`,
`kelly`, `kassouf`, `regan`, `black-scholes`, `kuhn`, `odean`, `kuhn-cards`. Kết quả tìm từng người:
`quantik-video-factory/knowledge/images/README.md`.

Mẹo Commons: người nổi tiếng trong ngành tài chính thường **không** có ảnh tự do (đã kiểm: Thorp, Kelly, Kuhn) — khi
đó dùng ảnh nơi chốn/hiện vật có thật và tự do (ví dụ Bell Labs 1942, Library of Congress, public domain) cộng thẻ
minh hoạ cho người. Wikimedia giới hạn tần suất: gặp HTTP 429 thì công cụ tự chờ; IP cloud dùng chung hay bị chặn lâu,
máy cá nhân ổn định hơn.

## Ảnh minh hoạ cho người / hãng / sự kiện

```bash
python images.py person --id <id> --name "Họ Tên" --role "vai trò"      # thẻ chữ cái đầu
python images.py org    --id <id> --name "Renaissance Technologies" --role "quỹ định lượng"
python images.py event  --id <id> --title "LTCM được giải cứu" --when "9/1998" --where "New York"
python images.py cards  --id <id> --cards J,Q,K
```

Ngày/tháng trên thẻ sự kiện là chữ trên ảnh — chỉ ghi khi đã là `facts` có nguồn trong episode.

## Nhân vật và hiện vật (`figures.py`)

- Nhân vật: `investor` (áo cam), `quant` (áo xanh, kính), `rival` (áo đỏ, mũ), `professor` (vest, cà vạt, kính),
  `analyst` (tóc búi, áo vàng).
- Tư thế: `stand, point, think, worried, cheer, shrug, present, hold`. Nét mặt: `neutral, smile, worried, surprised, focus`.
- Hiện vật: `poker_table, cards, chips, phone_up, phone_down, laptop_up, laptop_down, chalkboard, book, newspaper`.
- Xem tất cả: `python figures.py sheet.png`.

Đặt vào một đoạn (cảnh chữ: chữ ở trên, sân khấu ở dưới):

```json
"visual": {"kind": "statement", "scene": {
  "cast": [{"who": "investor", "pose": "point", "face": "smile", "x": 0.24},
           {"who": "rival", "pose": "shrug", "face": "neutral", "x": 0.76, "flip": true}],
  "props": [{"what": "poker_table"}, {"what": "chips", "x": 0.5, "y": 0.84, "s": 0.6}],
  "bubble": {"text": "Lại có K à? Tôi bỏ.", "who": 1}}}
```

`x`, `y` là vị trí 0–1 trong khung sân khấu; `s` là tỉ lệ hiện vật; `flip` lật nhân vật; `bubble.who` là chỉ số nhân vật
nói. Hook có nhân vật: `"hook_scene": {...}` trong episode (`null` để tắt). Mỗi style trụ cột đã có cảnh mặc định
(`SCENES` trong `styles/<style>/template.py`).

## Biểu tượng (`pictos.py`)

`book, building, bulb, cards, chart_up, chart_down, check, coins, dice, eye, gear, hourglass, magnifier, people, scale,
shield, target, warning` — `"visual": {"kind": "statement", "icon": "shield"}`. Xem: `python pictos.py sheet.png`.

## Mở rộng

- Nhân vật mới: thêm vào `CHARACTERS` (màu da, tóc, kiểu tóc `short|bun|cap|bald`, áo, kính, cà vạt).
- Tư thế mới: thêm vào `POSES` (khuỷu tay, bàn tay cho hai tay, toạ độ: chân ở y=0, đỉnh đầu ≈ −360).
- Hiện vật mới: hàm vẽ trả về ảnh RGBA, thêm vào `PROPS`. Không vẽ chữ số, logo hay thương hiệu thật.
- Sau khi thêm: `python -m unittest tests.test_pillars.Figures` (từ thư mục skill video).

## QA liên quan

`qa/check_images.py`: tên được nhắc phải có ảnh hiện trên màn hình hoặc waiver; ảnh phải có trong sổ ảnh; ảnh thật phải
có giấy phép tự do, tác giả, URL; ảnh minh hoạ phải ghi "minh hoạ". Ghi công ảnh tự vào `sources.md` và caption.
