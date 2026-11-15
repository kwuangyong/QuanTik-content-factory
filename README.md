# QuanTik Content Factory

Skill Claude Code `quantik-video-factory`: dựng video ngắn và carousel cho mạng xã hội của QuanTik (TikTok, Reels, YouTube Shorts, Facebook). Video giải thích công thức và thuật ngữ quant finance, gồm code Python chạy thật, chart, 3D xoay, phụ đề, giọng đọc tiếng Việt. Mỗi video kèm caption cho từng nền tảng và một phiếu QA.

Mọi con số trong lời thoại đều do code tính ra. QA chặn số gõ tay, cụm từ hô hào mua bán và chữ tràn khung trước khi đăng.

## Năm trụ cột nội dung

| # | Trụ cột | Style | Nội dung |
| --- | --- | --- | --- |
| 1 | Quant Education | 8 style cũ | mô hình, chỉ số, thuật ngữ quant — số do code chạy thật |
| 2 | Tâm lý nhà đầu tư & tài chính hành vi | `bias-lab` | vấn đề → cơ chế → bằng chứng học thuật → hệ quả → bài học → góc quant |
| 3 | Nhịp thị trường & nghiên cứu | `market-brief` | dữ liệu AGR có dấu thời gian → độ rộng, thanh khoản, nhóm ngành, regime → 3 kịch bản có điều kiện |
| 4a | Lịch sử quant & nhân vật | `history-story` | hook → bối cảnh → xung đột → đột phá → hệ quả → bài học; tách tư liệu / lời tự kể / giai thoại / tranh cãi |
| 4b | Lý thuyết trò chơi, poker & ra quyết định | `decision-lab` | EV, phương sai, Nash, Kelly, rủi ro phá sản; poker giống và khác thị trường ở đâu |

Trụ cột 2–4 dùng worker nghiên cứu, fact-checker, sổ nguồn chung (`knowledge/sources/ledger.json`) và gate QA riêng: không
nguồn thì không render, giai thoại không được kể như sự kiện, không có dữ liệu thị trường thì không có video.
Kiến trúc: `.claude/skills/quantik-video-factory/pillars/README.md` · worker: `workers/README.md` ·
chuyển đổi: `MIGRATION.md`.

## Có gì (trụ cột 1)

- **8 style:** code-reel, kinetic-text, chart-story, myth-buster, whiteboard-math, talking-head-script, carousel, meme-quant. Mỗi style có `spec.md` và một mẫu trong `styles/<style>/`.
- **8 mô hình viết tay:** GARCH, Hurst, Ornstein–Uhlenbeck, HMM, Monte Carlo, Sharpe, VaR/CVaR, Kelly (`knowledge/models/`). Code mô hình chạy thật trong video.
- **Catalog 199 chủ đề** (`knowledge/CATALOG.md`), sinh tự động từ QuanTik---Design và QuanTik-website: 57 thuật ngữ glossary, 43 chỉ số module báo cáo Quant, 23 trường hành động, 42 cột sheet quét sàn, mô hình trang Home và 27 engine trong `quant.py` (ARIMA, EGARCH, LightGBM, meta-label…). Video dùng định nghĩa đã duyệt, ngưỡng đọc và code trích từ engine thật.
- **Thương hiệu và compliance:** `brand/identity.md`, `brand/compliance.md`.

## Cài đặt

Cần Python 3.10+ và ffmpeg.

```bash
pip install -r .claude/skills/quantik-video-factory/requirements.txt
```

Giọng đọc (edge-tts) cần Internet. Không có mạng thì video chỉ có phụ đề và nhạc nền. Trụ cột thị trường cần mạng tới `trading.agr.vn`.

## Chạy

Trong Claude Code, chỉ cần nói kiểu "làm video về Kelly cho TikTok", skill sẽ tự được gọi. Hoặc chạy tay:

```bash
cd .claude/skills/quantik-video-factory/pipeline
python batch.py --topics garch --styles code-reel
python batch.py --topics garch,kelly --styles myth-buster,meme-quant --scale 0.5
python batch.py --topics module_egarch_gamma,engine_meta_label --styles code-reel   # chủ đề catalog
python catalog.py --list | grep -i lightgbm   # tìm id chủ đề
python models.py kelly   # xem các số dùng được trong lời thoại
```

Kết quả nằm trong `social-output/<id>/`: `final.mp4`, `thumbnail.jpg`, `captions.md`, `subtitles.srt`, `qa_report.md`
(+ `qa_report.json`, `storyboard.json`, `visual_assets.json`; tập trụ cột mới thêm `sources.md`).

Trụ cột mới (chạy trong `pipeline/`):

```bash
python pillar.py list                                            # 5 trụ cột
python pillar.py topics behavioral-finance                       # catalog một trụ cột
python pillar.py make ../episodes/bf-disposition-bias-lab.json --scale 0.5     # tập mẫu tâm lý
python pillar.py make ../episodes/qh-thorp-history-story.json --scale 0.5      # tập mẫu lịch sử
python pillar.py make ../episodes/ds-ev-variance-decision-lab.json --scale 0.5 # tập mẫu ra quyết định
python pillar.py market produce --scale 0.5                      # nhịp thị trường từ dữ liệu thật
python pillar.py scaffold quant-history qh_ltcm --id qh-ltcm-history-story     # khung tập mới
python pillar.py check ../episodes/<id>.json                     # mọi gate QA, không render
python batch.py --topics kelly --styles code-reel --check-only   # gate QA cho lệnh cũ
```

Kiểm thử: `cd .claude/skills/quantik-video-factory && python -m unittest discover -s tests -v`.

Làm mới catalog khi frontend hoặc engine thay đổi (cần Node 22.6+):

```bash
python catalog.py --design /path/QuanTik---Design --website /path/QuanTik-website
```

Chi tiết quy trình xem `.claude/skills/quantik-video-factory/SKILL.md`.

Nội dung giáo dục về phương pháp định lượng, không phải khuyến nghị mua bán chứng khoán.
