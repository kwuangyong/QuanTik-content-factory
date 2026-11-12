# QuanTik Content Factory

Skill Claude Code `quantik-video-factory`: dựng video ngắn và carousel cho mạng xã hội của QuanTik (TikTok, Reels, YouTube Shorts, Facebook). Video giải thích công thức và thuật ngữ quant finance, gồm code Python chạy thật, chart, 3D xoay, phụ đề, giọng đọc tiếng Việt. Mỗi video kèm caption cho từng nền tảng và một phiếu QA.

Mọi con số trong lời thoại đều do code tính ra. QA chặn số gõ tay, cụm từ hô hào mua bán và chữ tràn khung trước khi đăng.

## Có gì

- **8 style:** code-reel, kinetic-text, chart-story, myth-buster, whiteboard-math, talking-head-script, carousel, meme-quant. Mỗi style có `spec.md` và một mẫu trong `styles/<style>/`.
- **8 mô hình:** GARCH, Hurst, Ornstein–Uhlenbeck, HMM, Monte Carlo, Sharpe, VaR/CVaR, Kelly (`knowledge/models/`).
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
python models.py kelly   # xem các số dùng được trong lời thoại
```

Kết quả nằm trong `social-output/<id>/`: `final.mp4`, `thumbnail.jpg`, `captions.md`, `subtitles.srt`, `qa_report.md`.

Chi tiết quy trình xem `.claude/skills/quantik-video-factory/SKILL.md`.

Nội dung giáo dục về phương pháp định lượng, không phải khuyến nghị mua bán chứng khoán.
