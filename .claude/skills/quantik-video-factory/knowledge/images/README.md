# Ảnh nhân vật, hãng, sự kiện

Quy trình đầy đủ (tự động dò tên → ảnh thật hoặc minh hoạ → đặt vào cảnh): skill **`.claude/skills/quantik-visual-assets/SKILL.md`**,
lệnh `python pipeline/visuals.py auto <episode> --write`.

`ledger.json` (schemas/image_ledger.schema.json) là sổ ảnh: mọi ảnh dùng trong video phải có ở đây. `files/` chứa file.

| Loại | Lấy từ đâu | Điều kiện | Dòng ghi công trên màn hình |
| --- | --- | --- | --- |
| `photo` | Wikimedia Commons (`python pipeline/images.py fetch "File:…"`) | giấy phép public domain, CC0, CC BY, CC BY-SA (từ chối NC, ND, fair use); có tác giả và URL | `Ảnh: <tác giả> · <giấy phép> · Wikimedia Commons` |
| `illustration` | vẽ bằng code (`images.py person / event / cards`) | phong cách đồ hoạ thương hiệu, chữ cái đầu tên — **không bao giờ giả ảnh chụp người thật** | `Ảnh minh hoạ tạo bằng code, không phải ảnh thật` |

Không dùng ảnh tìm trên Google, báo chí, Facebook… khi chưa có giấy phép (`brand/compliance.md`). Không dùng AI tạo
ảnh giống thật của người có thật.

```bash
cd .claude/skills/quantik-video-factory/pipeline
python images.py search "Claude Shannon"                 # ứng viên + giấy phép (✅ dùng được / ⛔ không)
python images.py categories "Bell Labs"                  # tìm danh mục Commons (chính xác hơn tìm chữ)
python images.py category "Bell Labs Murray Hill"         # file trong một danh mục
python images.py fetch "File:<tên file>" --id shannon --subject "Claude Shannon"
python images.py person --id thorp --name "Edward O. Thorp" --role "nhà toán học"
python images.py event --id ltcm-1998 --title "LTCM được giải cứu" --when "9/1998" --where "New York"
python images.py cards --id kuhn-cards --cards J,Q,K
python images.py list
```

`fetch`/`search` cần mạng tới `commons.wikimedia.org` và `upload.wikimedia.org`.

Ưu tiên: ảnh thật có giấy phép mở khi tìm được; không có thì ảnh minh hoạ. Một ảnh thật thay ảnh minh hoạ: fetch với
cùng `--id` là xong, episode không phải sửa.

## Ghi chú kỹ thuật

- Wikimedia chỉ phục vụ ảnh thu nhỏ ở kích thước chuẩn (https://w.wiki/GHai); `images.py` dùng 1280 px. Kích thước lạ
  bị trả HTTP 429.
- Commons đôi khi trả URL `thumb.wikimedia.org`; `images.py` tự đổi sang `upload.wikimedia.org` (cùng đường dẫn).
- Gặp 429, `images.py` tự chờ (`Retry-After`) rồi thử lại. IP dùng chung của môi trường cloud hay bị giới hạn lâu
  hơn; chạy trên máy cá nhân thì ổn định.

## Kết quả tìm ảnh thật (2026-11-15)

| Đối tượng | Kết quả trên Wikimedia Commons | Đang dùng |
| --- | --- | --- |
| Edward O. Thorp | không có ảnh giấy phép tự do (kết quả "Ed Thorp" là cúp NFL, người khác) | ảnh minh hoạ `thorp` |
| John L. Kelly Jr. | không có ảnh giấy phép tự do | ảnh minh hoạ `kelly` |
| Harold W. Kuhn | không có ảnh giấy phép tự do, không có danh mục riêng | ảnh minh hoạ `kuhn` |
| Jim Simons | **có**: `File:Jim Simons at MSRI.jpg`, CC BY-SA 3.0 (Gleuschk) | ảnh thật `jim-simons` |
| Claude Shannon | **có**: `File:ClaudeShannon MFO3807.jpg`, CC BY-SA 2.0 de (Konrad Jacobs) | ảnh thật `claude-shannon` |
| Bell Labs, Murray Hill (nơi Kelly làm việc) | có: bộ ảnh Gottscho-Schleisner 1942, **public domain** (Library of Congress), ví dụ `File:Bell Telephone Laboratories, Murray Hill, New Jersey. LOC gsc.5a08392.jpg` | chưa tải được (Wikimedia giới hạn IP cloud) — lệnh bên dưới |

```bash
python images.py fetch "File:Bell Telephone Laboratories, Murray Hill, New Jersey. LOC gsc.5a08392.jpg" --id bell-labs --subject "Bell Labs, Murray Hill" --depicts "Bell Telephone Laboratories, Murray Hill, New Jersey (1942)"
```

Sau khi tải: trong `episodes/qh-thorp-history-story.json`, đổi thực thể Bell Labs từ `waiver` sang `"image": "bell-labs"` và
đặt `"visual": {"kind": "image", "image": "bell-labs"}` cho đoạn `context` (hoặc gắn vào mốc 1956).
