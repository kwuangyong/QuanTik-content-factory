# Hướng dẫn chuyển đổi — từ một dây chuyền sang năm trụ cột

## Không phải làm gì cả nếu chỉ dùng tính năng cũ

Mọi lệnh cũ chạy như trước (đã kiểm bằng test `BackwardCompat`):

```bash
cd .claude/skills/quantik-video-factory/pipeline
python batch.py --topics garch --styles code-reel
python batch.py --topics garch,kelly --styles myth-buster,meme-quant --scale 0.5
python batch.py --episode ../episodes/sharpe-myth-example.json
python batch.py --topics module_egarch_gamma,engine_meta_label --styles code-reel
bash ../tutorial/run.sh <workdir>
```

Episode JSON cũ không có `pillar` → đi đúng nhánh cũ. `models.py`, `term_topic.py`, catalog, 8 style, `tutorial/` không đổi.

## Thay đổi nhỏ trong file cũ (đều tương thích ngược)

| File | Thay đổi | Ảnh hưởng hành vi cũ |
| --- | --- | --- |
| `pipeline/batch.py` | tra trụ cột trước nhánh cũ; `--check-only`; ghi `sources.md`, `storyboard.json`, `visual_assets.json`; `{fact}` làm placeholder; cột `notes` của `episodes.csv` ghi `pillar=` | không: nhánh trụ cột chỉ chạy với id trụ cột hoặc episode có `pillar`. `storyboard.json`/`visual_assets.json` giờ cũng có cho tập cũ (file mới, không thay file nào) |
| `pipeline/core.py` | `RAW_KEYS` thêm khoá trụ cột (`pillar`, `brief`, …) | không |
| `pipeline/voiceover.py` | edge-tts nạp CA từ `SSL_CERT_FILE` và dùng `HTTPS_PROXY`; thử lại tối đa 5 lần (`QT_TTS_RETRIES`) khi engine online lỗi tạm thời | môi trường có proxy TLS: trước rơi về "không giọng", giờ có giọng. Trước đây edge-tts lỗi tạm thời (`NoAudioReceived`, khoảng 1/5 lần gọi) làm **một số cảnh mất giọng mà QA không báo**; giờ được thử lại |
| `qa/check_format` (trong `batch.py`) | cảnh có lời nhưng không có file giọng → KHÔNG ĐẠT | video cũ từng lọt lỗi này giờ bị chặn — dựng lại là hết |
| `qa/check_numbers.py` | số trong chuỗi do code sinh (ngày "13/11/2026", giờ "15:05:05") được chấp nhận | chỉ nới cho chuỗi do code tính, không nới số gõ tay |
| `qa/check_banned.py` | tham số `extra=` | mặc định như cũ |
| `qa/report.py` | dòng gate mới, `qa_report.json` | `qa_report.md` cũ giữ nguyên các dòng cũ |
| `requirements.txt` | thêm `jsonschema` | thiếu thì gate schema lùi về kiểm trường bắt buộc |

Cài thêm: `pip install -r .claude/skills/quantik-video-factory/requirements.txt`.

## Dùng trụ cột mới

### Trụ cột 2 / 4a / 4b (nghiên cứu)

```bash
cd .claude/skills/quantik-video-factory/pipeline
python pillar.py list
python pillar.py topics quant-history
python pillar.py scaffold quant-history qh_ltcm --id qh-ltcm-history-story
#  → research/qh-ltcm-history-story/brief.json, factcheck.json, episodes/qh-ltcm-history-story.json
#  giao cho worker: Quant Historian điền brief → Fact-checker điền factcheck → Scriptwriter viết episode
python pillar.py validate ../research/qh-ltcm-history-story/brief.json research_brief
python pillar.py check ../episodes/qh-ltcm-history-story.json
python pillar.py make  ../episodes/qh-ltcm-history-story.json --scale 0.5 --no-log   # xem nhanh
python pillar.py make  ../episodes/qh-ltcm-history-story.json                        # bản đăng
```

Ba tập mẫu chạy được ngay:

```bash
python pillar.py make ../episodes/bf-disposition-bias-lab.json --scale 0.5 --no-log
python pillar.py make ../episodes/qh-thorp-history-story.json --scale 0.5 --no-log
python pillar.py make ../episodes/ds-ev-variance-decision-lab.json --scale 0.5 --no-log
```

`batch.py --episode <file>` cũng dựng được các episode này (cùng gate).

### Trụ cột 3 (thị trường)

```bash
python pillar.py market produce --scale 0.5          # fetch → analyze → editorial (nháp) → script → dựng
# hoặc từng bước, dừng để Analyst duyệt market_editorial.json:
python pillar.py market fetch
python pillar.py market analyze
python pillar.py market editorial
python pillar.py market script
python pillar.py make ../../../../social-output/_market/<bundle>/episode.json --scale 0.5
# có chuỗi lịch sử VN-INDEX (date,close[,value]) kèm manifest nguồn → có regime:
python pillar.py market fetch --history vnindex.csv --history-manifest vnindex.manifest.json
# bản tổng kết trên dữ liệu cũ (ghi rõ ngày):
python pillar.py market produce --bundle <bundle cũ> --allow-stale
```

Cần mạng tới `trading.agr.vn`. Không có mạng → bundle ghi `failed`, report `unavailable`, không có video (đúng thiết kế).

### Kiểm thử

```bash
cd .claude/skills/quantik-video-factory
python -m unittest discover -s tests -v
QT_RENDER_TESTS=1 python -m unittest tests.test_pillars.RenderTests -v
```

## Chuyển tư liệu cũ

`knowledge/stories/ltcm.md`, `medallion.md` dùng `facts` với `source` dạng chữ — vẫn hợp lệ cho trụ cột 1. Khi làm thành
tập trụ cột 4a: thêm nguồn vào ledger (đã có `ltcm-pwg-1999`, `lowenstein-2000`, `zuckerman-2019`), đổi `source` →
`source_id`, tách từng câu thành claim có `status`, chạy fact-check.

## Ảnh nhân vật (bổ sung)

Episode trụ cột 2, 4a, 4b giờ cần `entities`: mỗi người/hãng/sự kiện được nhắc có `image` (hiện ở một cảnh) hoặc `waiver`.
Episode cũ chưa có `entities` sẽ bị `check_images` chặn khi nhắc tên — thêm khai báo như các tập mẫu
(`episodes/qh-thorp-history-story.json`). Trụ cột 1 và 3 không bắt buộc.

```bash
python images.py person --id <id> --name "<Họ tên>" --role "<vai trò>"     # ảnh minh hoạ
python images.py search "<tên>"; python images.py fetch "File:…" --id <id> --subject "<tên>"   # ảnh thật (cần mạng)
```

## Việc còn để ngỏ (chưa làm, không giả vờ là đã có)

- Chưa có API lịch sử giá tự động → regime/biến động/thanh khoản 20 phiên cần CSV người dùng hoặc tích luỹ snapshot.
- `holidays.json` trống → ngày lễ HOSE chưa được tính khi đo độ cũ dữ liệu.
- Mỗi trụ cột nghiên cứu mới có một tập mẫu; các chủ đề `backlog` trong catalog chưa có brief.
- Nhận định thị trường hiện là bản nháp theo luật; chất lượng diễn giải phụ thuộc bước Analyst duyệt.
- Trong môi trường cloud này, edge-tts không trả âm thanh cho một số câu (không rõ nguyên nhân, nghi proxy). Gate mới chặn
  cảnh câm; dựng bản đăng trên máy có kết nối edge-tts ổn định.
- Chưa tải được ảnh thật từ Wikimedia Commons trong phiên cloud này (host đã thêm vào môi trường nhưng lệnh bị chặn
  ở bước duyệt quyền); các tập mẫu đang dùng ảnh minh hoạ. Chạy `images.py search/fetch` trên máy có mạng.
- Fact-check tự động chỉ kiểm truy vết; độ đúng của nội dung nguồn do người/agent ký `checker` chịu trách nhiệm.
