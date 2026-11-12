# QuanTik Content Factory

Skill Claude Code `quantik-video-factory`: dựng video ngắn và carousel cho mạng xã hội của QuanTik (TikTok, Reels, YouTube Shorts, Facebook). Video giải thích công thức và thuật ngữ quant finance, gồm code Python chạy thật, chart, 3D xoay, phụ đề, giọng đọc tiếng Việt. Mỗi video kèm caption cho từng nền tảng và một phiếu QA.

Mọi con số trong lời thoại đều do code tính ra. QA chặn số gõ tay, cụm từ hô hào mua bán và chữ tràn khung trước khi đăng.

## Có gì

- **8 style:** code-reel, kinetic-text, chart-story, myth-buster, whiteboard-math, talking-head-script, carousel, meme-quant. Mỗi style có `spec.md` và một mẫu trong `styles/<style>/`.
- **8 mô hình viết tay:** GARCH, Hurst, Ornstein–Uhlenbeck, HMM, Monte Carlo, Sharpe, VaR/CVaR, Kelly (`knowledge/models/`). Code mô hình chạy thật trong video.
- **Catalog 199 chủ đề** (`knowledge/CATALOG.md`), sinh tự động từ QuanTik---Design và QuanTik-website: 57 thuật ngữ glossary, 43 chỉ số module báo cáo Quant, 23 trường hành động, 42 cột sheet quét sàn, mô hình trang Home và 27 engine trong `quant.py` (ARIMA, EGARCH, LightGBM, meta-label…). Video dùng định nghĩa đã duyệt, ngưỡng đọc và code trích từ engine thật.
- **Thương hiệu và compliance:** `brand/identity.md`, `brand/compliance.md`.

## Cài đặt

Cần Python 3.10+ và ffmpeg.

```bash
pip install -r .claude/skills/quantik-video-factory/requirements.txt
```

Giọng đọc (edge-tts) cần Internet. Không có mạng thì video chỉ có phụ đề và nhạc nền.

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

Kết quả nằm trong `social-output/<id>/`: `final.mp4`, `thumbnail.jpg`, `captions.md`, `subtitles.srt`, `qa_report.md`.

Làm mới catalog khi frontend hoặc engine thay đổi (cần Node 22.6+):

```bash
python catalog.py --design /path/QuanTik---Design --website /path/QuanTik-website
```

Chi tiết quy trình xem `.claude/skills/quantik-video-factory/SKILL.md`.

Nội dung giáo dục về phương pháp định lượng, không phải khuyến nghị mua bán chứng khoán.
