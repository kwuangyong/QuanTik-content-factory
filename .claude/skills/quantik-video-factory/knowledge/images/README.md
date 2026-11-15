# Ảnh nhân vật, hãng, sự kiện

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
python images.py fetch "File:<tên file>" --id shannon --subject "Claude Shannon"
python images.py person --id thorp --name "Edward O. Thorp" --role "nhà toán học"
python images.py event --id ltcm-1998 --title "LTCM được giải cứu" --when "9/1998" --where "New York"
python images.py cards --id kuhn-cards --cards J,Q,K
python images.py list
```

`fetch`/`search` cần mạng tới `commons.wikimedia.org` và `upload.wikimedia.org`.

Ưu tiên: ảnh thật có giấy phép mở khi tìm được; không có thì ảnh minh hoạ. Một ảnh thật thay ảnh minh hoạ: fetch với
cùng `--id` là xong, episode không phải sửa.
