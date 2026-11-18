---
name: quantik-video-factory
description: Dựng video ngắn và carousel cho mạng xã hội của QuanTik (TikTok, Reels, YouTube Shorts, Facebook) giải thích công thức, mô hình và thuật ngữ quant finance — code Python chạy thật, chart, 3D xoay, phụ đề, giọng đọc tiếng Việt, kèm caption từng nền tảng và phiếu QA. Có 8 style (code-reel, kinetic-text, chart-story, myth-buster, whiteboard-math, talking-head-script, carousel, meme-quant), 8 mô hình chạy code thật (GARCH, Hurst, OU, HMM, Monte Carlo, Sharpe, VaR/CVaR, Kelly) và catalog gần 200 chủ đề lấy từ chính QuanTik: mọi thuật ngữ glossary, chỉ số 16 module báo cáo Quant, trường hành động, cột sheet quét sàn và 27 engine trong quant.py (ARIMA, EGARCH, LightGBM, meta-label, agreement, residual reversion…). Ngoài trụ cột học quant gốc còn có bốn kiến trúc nội dung riêng: tâm lý nhà đầu tư & tài chính hành vi (bias-lab), nhịp thị trường từ dữ liệu thật có dấu thời gian (market-brief), lịch sử quant & nhân vật huyền thoại (history-story), lý thuyết trò chơi, poker & ra quyết định (decision-lab) — mỗi trụ cột có worker nghiên cứu, fact-check, sổ nguồn và gate QA riêng. Dùng skill này bất cứ khi nào người dùng muốn làm nội dung social media, video, reel, short, TikTok, carousel, kịch bản quay, caption, hook, lịch đăng hoặc nội dung quảng bá cho QuanTik — kể cả khi chỉ nói "làm video về GARCH", "giải thích Sharpe cho TikTok", "viết kịch bản về VaR", "làm loạt bài về Kelly", "video về hiệu ứng FOMO", "tóm tắt thị trường hôm nay", "kể chuyện Jim Simons", "poker và Kelly" hay "quảng bá gói Pro" mà không nhắc tới skill.
---

# QuanTik Video Factory

Biến một chủ đề quant thành video dọc 9:16 (hoặc carousel) đúng thương hiệu QuanTik. Nguyên tắc cốt lõi: **mọi con số người xem nghe hoặc thấy đều do code trong video tính ra.** Lời thoại dùng placeholder `{key}`; pipeline chạy mô hình, điền số, rồi QA chặn mọi số không có nguồn. Đó là thứ phân biệt QuanTik với nội dung tài chính "nói cho hay".

Đường dẫn trong file này tính từ thư mục skill: `.claude/skills/quantik-video-factory/`.

```
SKILL.md                 ← bạn đang đọc: điều phối
pillars/                 6 trụ cột (1–4b + 5 dark-truth): registry.json · <id>/PILLAR.md · <id>/catalog.json · README.md (kiến trúc)
workers/                 vai nghiên cứu/kiểm chứng/sản xuất: đầu vào, đầu ra, ràng buộc, bàn giao
schemas/                 hợp đồng JSON (pillar, brief, ledger, factcheck, market report/editorial, episode, storyboard, assets, QA)
research/<id>/           brief.json + factcheck.json của từng tập nghiên cứu
knowledge/sources/       ledger.json — sổ nguồn dùng chung
brand/                   identity.md (màu, chữ, giọng văn, thông tin sản phẩm) · compliance.md (cụm cấm, miễn trừ)
                         pronunciation.json (cách TTS đọc thuật ngữ) · assets/ (logo, font, nhạc có giấy phép)
knowledge/models/*.md    8 mô hình viết tay: công thức, tham số đẹp, ngưỡng, ví dụ HOSE, sai lầm hay gặp, video_defaults
knowledge/catalog.json   ~200 chủ đề sinh tự động từ QuanTik (định nghĩa, công thức, ngưỡng đọc, code engine trích)
knowledge/CATALOG.md     bảng tra id → tên, nhóm, engine, mô hình demo
knowledge/episodes.csv   tập đã dựng/đăng → tránh trùng, nối mạch, ghi view
knowledge/hooks.md       kho hook (đã kiểm chứng bằng view thật / ứng viên)
knowledge/stories/       chuyện lịch sử có nguồn (LTCM, Medallion)
tutorial/                video HƯỚNG DẪN SẢN PHẨM (quay giao diện web thật): README.md · run.sh · beats.py · render.py
styles/<style>/          spec.md (cấu trúc cảnh) + template.py (dựng cảnh) + mẫu
looks.json               look: tông giọng, nội dung, thumbnail, giọng đọc, nhạc cho từng dòng nội dung (đọc bởi make.py)
pipeline/                make.py (lệnh nhanh) · models.py (code mô hình) · batch.py (lệnh chính) · render/voiceover/assemble
qa/                      check_numbers · check_banned · check_format · check_script · check_sources · check_market · qa_report.md
tests/                   python -m unittest discover -s tests (không cần mạng) · RESULTS.md
episodes/                episode JSON đã viết (ghi đè mặc định của mô hình)
```

## Lệnh nhanh: `make.py` + `looks.json`

```bash
cd pipeline
python make.py menu                                   # look = tông giọng + nội dung + thumbnail; tập + phiên bản
python make.py escape-velocity --as chart-story       # một ý tưởng, nhiều phiên bản style (khối "variants")
python make.py sortino --as myth-buster --no 4        # chủ đề quant + thumbnail series #4
python make.py new <id> --look dark-truth             # khung tập mới, điền TODO theo look
```

Look hiện có: `quant-vi` (Học Quant cùng QuanTik, tiếng Việt, thumbnail sáng) và `dark-truth` (tiếng Anh, giọng trầm,
nền drone, thumbnail tối). Thêm look mới = thêm khối trong `looks.json`.

## Chọn trụ cột trước

Repo có sáu kiến trúc nội dung (1, 2, 3, 4a, 4b, 5) (chi tiết: `pillars/README.md`). Xác định trụ cột từ yêu cầu, rồi đọc `PILLAR.md` của nó:

| Người dùng muốn | Trụ cột | Đọc | Lệnh |
| --- | --- | --- | --- |
| giải thích mô hình, chỉ số, thuật ngữ quant | 1 `quant-education` | phần Quy trình bên dưới | `python batch.py --topics <id> --styles <style>` |
| tâm lý, thiên kiến, sai lầm nhà đầu tư (FOMO, né lỗ, bầy đàn…) | 2 `behavioral-finance` | `pillars/behavioral-finance/PILLAR.md` | `pillar.py scaffold` → brief → fact-check → `pillar.py make` |
| thị trường hôm nay/tuần này, độ rộng, dòng tiền, kịch bản | 3 `market-intelligence` | `pillars/market-intelligence/PILLAR.md` | `python pillar.py market produce` |
| lịch sử quant, Thorp, Simons, LTCM, Black–Scholes | 4a `quant-history` | `pillars/quant-history/PILLAR.md` | như trụ cột 2 |
| EV, Nash, poker, Kelly, rủi ro phá sản | 4b `decision-science` | `pillars/decision-science/PILLAR.md` | như trụ cột 2 |
| "dark truth" tiếng Anh cho IG/Shorts: tiền, địa vị, áp lực xã hội, vòng 9-5 (hoạt hoạ, không chart) | 5 `dark-truth` | `pillars/dark-truth/PILLAR.md` | `python batch.py --episode ../episodes/<id>.json` |

Trụ cột 2, 4a, 4b đi qua các vai trong `workers/` (researcher → fact-checker → scriptwriter), mỗi vai bàn giao một file
JSON theo `schemas/`. Mọi claim trỏ về `knowledge/sources/ledger.json`; `qa/check_sources.py` chặn render nếu thiếu
nguồn, thiếu fact-check, hoặc lời kể một giai thoại/lời tự kể như sự kiện. Trụ cột 3 không bao giờ bịa số thị trường:
không có dữ liệu thì không có video, dữ liệu cũ phải khai báo (`qa/check_market.py`).

**Hình ảnh:** dùng skill **`quantik-visual-assets`** (`.claude/skills/quantik-visual-assets/SKILL.md`) cho ảnh thật,
ảnh minh hoạ, nhân vật, hiện vật, biểu tượng; lệnh nhanh `python pipeline/visuals.py auto <episode> --write`.
Nhắc tới người, hãng, sự kiện thì phải có ảnh — ảnh Wikimedia Commons giấy phép tự do (ghi tác giả + giấy
phép trên màn hình) hoặc ảnh minh hoạ vẽ bằng code (ghi "minh hoạ"). Khai báo trong `entities` của episode;
`qa/check_images.py` chặn nếu thiếu. Hướng dẫn: `knowledge/images/README.md`, lệnh `python pipeline/images.py`.

Chạy từ `pipeline/`: `python pillar.py list` · `python pillar.py topics <pillar>` · `python pillar.py check <episode>` ·
`python pillar.py make <episode> --scale 0.5`. Kết quả thêm `sources.md`, `storyboard.json`, `visual_assets.json`,
`qa_report.json` cạnh các file cũ. Trả kết quả trong chat như mục 6, kèm danh sách nguồn chính và nhãn trạng thái.

## Quy trình (trụ cột 1 — Quant Education)

> **Video hướng dẫn dùng sản phẩm** ("hướng dẫn sử dụng QuanTik", "workflow từ tạo tài khoản đến phân tích",
> "demo tính năng quét sàn") không đi qua `batch.py`. Đọc `tutorial/README.md` và làm theo đó: quay giao diện
> production thật bằng Playwright, dữ liệu minh hoạ với mã bịa, rồi lồng tiếng và ghép bằng `tutorial/run.sh`.
>
> **Nội dung YouTube Shorts / IG Reels (tiếng Anh)**: dark truth finance, poker theory, psychology facts, game theory,
> quant mindset. 80 tập trong `episodes/yt/`, style `dark-story` (không chart, ảnh thật có ghi nguồn + hoạt hoạ vẽ tay).
> Đọc `channels/yt-ig.md`.

### 1. Chốt yêu cầu

Xác định từ lời người dùng (hỏi lại chỉ khi thật sự mơ hồ):

- **Chủ đề → topic.** Có hai tầng:
  - **Viết tay (sâu nhất):** `garch`, `hurst`, `ou`, `hmm`, `monte_carlo`, `sharpe`, `sortino`, `var_cvar`, `kelly` (trong `models.py`) và `rsi`, `max_drawdown`, `beta`, `ols`, `lln_clt` (luật số lớn & CLT), `egarch`, `fat_tails` (chuẩn/log-normal/đuôi dày), `momentum`, `martingale`, `psr` (PSR/DSR), `cmf` (trong `models_extra.py`). Code mô hình chạy thật trong video, mọi số đến từ lần chạy đó.
  - **Catalog (rộng nhất):** mọi id trong `knowledge/CATALOG.md`, gồm thuật ngữ (`sortino`, `calmar`, `cmf`, `psr`…), chỉ số module (`module_egarch_gamma`, `module_adf_p`, `module_lightgbm`…), trường hành động (`action_kelly_half`…), cột sheet (`sheet-…`), mô hình trang Home (`home_…`) và engine (`engine_garch`, `engine_meta_label`, `engine_cross_sectional_light_gbm`…). Tìm: `python pipeline/catalog.py --list | grep -i <từ khoá>`; xem chi tiết: `--show <id>`.
  - Người dùng nói tên thường ("EGARCH", "meta-label", "độ phủ mô hình") thì tra catalog để ra id. Chủ đề trùng một mô hình viết tay thì ưu tiên bản viết tay.
- **Style.** Người dùng không chọn thì gợi ý theo bảng:

| Style | Khi nào | Độ dài |
| --- | --- | --- |
| `code-reel` | mặc định cho người thích kỹ thuật; chứng minh số từ code | 35–55s |
| `kinetic-text` | lướt nhanh, một con số "đắt" | 30–45s |
| `chart-story` | chuỗi thời gian có diễn biến, kể theo chương | 35–55s |
| `myth-buster` | có một hiểu lầm phổ biến để bác bằng số | 35–50s |
| `whiteboard-math` | người xem muốn hiểu từng ký hiệu công thức | 45–75s |
| `talking-head-script` | bạn tự quay: kịch bản + teleprompter + B-roll | 45–90s |
| `carousel` | feed Facebook/TikTok photo, đọc chậm, 7 slide | — |
| `meme-quant` | giải trí, kéo người mới, 12–20s | 12–20s |
| `story-mix` | **loạt bài nhiều tập cùng mô hình**: episode tự xếp cảnh (lịch sử, cách dùng, đố vui, so sánh, code trích dòng, 2D/3D tuỳ chọn) | 45–75s |

- **Số lượng.** "Làm loạt", "cả tuần" → mỗi video một episode JSON riêng (thường là `story-mix`), không chạy topic × style hàng loạt.
- **Đã đăng / đã có (đừng làm lại):** Monte Carlo, Sharpe, Sortino, Autoregressive, Hurst; loạt #6–#23 trong `episodes/ep*.json` (cột `series_no`). Đọc `episodes.csv` và thư mục `episodes/` trước khi lên kế hoạch.
- **Mỗi chủ đề tối đa một tập trong một loạt**; không đủ chủ đề viết tay thì lấy từ catalog (gần 200 chủ đề) hoặc nâng chủ đề catalog lên viết tay (mục Mở rộng).
- **Chống lặp (bắt buộc với loạt bài).** Các style cũ dùng chung lời, seed, chart, 3D và caption theo chủ đề, nên cùng chủ đề khác style vẫn ra nội dung gần như y hệt. Mỗi video trong loạt phải khác ở: góc kể (thứ tự cảnh), `seed` + `params`, hình (2D/3D, góc quay `view`, đoạn code trích), và `title`/`caption`/`thumb`. Xem `styles/story-mix/spec.md`. Trình bày kế hoạch nội dung cho người dùng duyệt trước khi dựng cả lô.

Đọc `knowledge/episodes.csv` trước: tránh trùng cặp topic × style đã đăng; nếu là loạt bài, tham chiếu tập trước trong hook hoặc CTA ("Tập trước mình nói về GARCH…").

### 2. Đọc kiến thức và thương hiệu

- `knowledge/models/<topic>.md` — nội dung chuyên môn và `video_defaults` (hook, beats, outputs, myth/fact, meme, story, công thức, symbols, caption, hashtags).
- `brand/identity.md` phần **Giọng văn** và **Sản phẩm**; `brand/compliance.md` toàn bộ. Không đọc được hai file này thì không viết lời.
- `styles/<style>/spec.md` — style dùng trường nào, cảnh nào.

### 3. Viết episode (khi cần khác mặc định)

`video_defaults` đủ để dựng ngay. Viết episode JSON vào `episodes/<id>.json` khi người dùng muốn góc riêng, hook khác, giọng khác, hay ghép chủ đề thời sự. Chỉ cần ghi các trường muốn đổi, cộng `topic`, `style`, `id`:

```json
{"id": "kelly-meme-tap03", "topic": "kelly", "style": "meme-quant",
 "meme": {"format": "nobody-quant", "setup": "...", "punch": "...", "truth": "... {f_star} ..."}}
```

Quy tắc viết lời — mỗi quy tắc đều có lý do:

- **Số chỉ đi qua placeholder** `{key}` hoặc `{key:fmt}` (fmt: `pct0..3`, `num0..3`, `int`, `vnd`, `x1`, `x2`). Xem các key có sẵn: `python pipeline/models.py <topic>`. Gõ tay "biến động 35%" sẽ bị QA chặn, vì giọng nói một số còn chart vẽ số khác là cách nhanh nhất mất uy tín.
- Trong LaTeX (`formula_numeric`) dùng `<<key>>` vì ngoặc nhọn đã thuộc về LaTeX.
- Số không do code tính: số nhỏ dùng như chữ (0–10) tự qua; con số cố định của công thức ("252", "GARCH(1,1)") vào `allowed_literals`; sự kiện lịch sử vào `facts` kèm `source`.
- Mỗi beat một ý, câu ngắn, đọc to được trong 6–10 giây. Beat mô tả đúng thứ đang hiện trên màn hình ("đường cam là…").
- **Hook phải nổ, ragebait, dễ hiểu ngay câu đầu** (yêu cầu chủ sản phẩm 11/2026): chọc thẳng vào niềm tin sai của người xem ("Khoe lãi {cagr_b}? *Xin lỗi*, chiến lược lãi {cagr_a} còn tốt hơn của bạn."), ≤ 16 từ, đọc xong trong khoảng 4 giây. Đánh dấu cụm khiêu khích bằng `*...*` → vẽ đỏ, gạch chân, rung và chớp khung; lời đọc và caption tự bỏ dấu sao. Ragebait nhưng **phải đúng sự thật** và vẫn theo `compliance.md`: không hứa lãi, không gọi mua/bán, không bịa số. Xem mẫu trong `knowledge/hooks.md`.
- **Hình khớp lời.** `hook_visual` chọn hình minh hoạ cho hook (tag trong `knowledge/visuals.json`); `cold_open` là 1–2 câu chuyện kể ngay sau hook, mỗi câu một cảnh B-roll có hình đúng nội dung (nói giáo sư toán vào casino → hình bàn blackjack, nói Titanic → tảng băng). Không ghi `visual` thì pipeline tự khớp theo từ khoá. Hình code/Python (`code`) chỉ xuất hiện khi lời thật sự nói về code.
- Kết bằng giới hạn của mô hình hoặc một câu mang về được. Không bao giờ chuyển thành lời khuyên mua/bán.
- Thẻ cuối luôn là CTA theo dõi kênh (like, follow QuanTik để học quant mỗi ngày), pipeline tự gắn; trường `cta` trong kiến thức chỉ còn là câu dẫn link trong caption.
- Hook phải tự hiểu được với người mới: đặt câu hỏi "X là gì? Vì sao nó quan trọng với bạn?" theo cách bất ngờ, không mở bằng số khô.
- CTA quảng bá: chỉ nói tính năng đúng như `identity.md`. Nhắc giá gói thì đối chiếu https://quantik.io.vn/plans trước, vì ưu đãi có thể đã đổi.

**Tiếng Anh** (IG / YouTube Shorts quốc tế): thêm `"lang": "en"` vào episode (mọi trụ cột). Số in kiểu
1,234.5 · $1,234 (`usd`), giọng `en-US-AriaNeural` / `en-US-ChristopherNeural` (`--voice male`), nhãn giao diện, câu
miễn trừ và cụm cấm tiếng Anh lấy từ `brand/compliance.md` (cụm cấm tiếng Việt vẫn quét). Ví dụ đầy đủ:
`episodes/escape-velocity.json` (trụ cột 5, hai phiên bản `dark-story` và `chart-story`, thumbnail tối tự sinh).

### 4. Dựng

Chạy từ thư mục `pipeline/`:

```bash
python batch.py --topics garch --styles code-reel                      # một video
python batch.py --topics garch,kelly --styles myth-buster,meme-quant   # 4 video
python batch.py --episode ../episodes/kelly-meme-tap03.json            # episode tự viết
python batch.py --topics var_cvar --styles code-reel --prices FPT.csv --data-source "FPT, HOSE, 2023–2025"
```

Tuỳ chọn: `--scale 0.5` (bản xem nhanh 540×960, dựng lại `--scale 1` trước khi đăng) · `--voice male|male-deep|female` (mặc định **male**: nam miền Bắc, sáng và thanh, +25%; `male-deep` = nam trầm; episode `"lang": "en"` tự dùng giọng en-US cùng tên) · `--broll auto|draw|photo` (ảnh thật xen kẽ hoạt hoạ tự vẽ / chỉ vẽ / ưu tiên ảnh thật) · `--voice-engine edge|gtts|espeak|silent` · `--music <file có giấy phép>|none` · `--no-log` (không ghi episodes.csv, dùng khi thử) · `--force` (dựng dù QA trước render thất bại — chỉ để xem, không đăng).

Mỗi video ra `social-output/<id>/` (thư mục gốc repo): `final.mp4`, `thumbnail.jpg`, `captions.md`, `subtitles.srt`, `qa_report.md`, `values.json` (số + code đã chạy), `layout.json`. Carousel ra `slides/1080x1920/` và `slides/1080x1350/`. Talking-head ra `teleprompter.mp4`, `script.md`, `broll/`. Một video mất khoảng 1–2 phút dựng.

**Thumbnail** (series "Học Quant cùng QuanTik #N", nền sáng): đọc `brand/thumbnail.md` rồi chạy `python thumbnail.py --episode <episode.json> --no <N> --out <thư mục output>` (hoặc `--topic <topic> [--style <style>]`) → `thumbnail-NN.jpg`. Nội dung: khối `thumb` của mô hình ← `thumb_variants[style]` ← khối `thumb` trong episode (ưu tiên cao nhất); seed/params lấy theo episode nên số trên ảnh khớp video. Hỏi người dùng số tập nếu chưa rõ.

**Dữ liệu thật:** `--prices` nhận CSV có cột `close`. Chỉ dùng để minh hoạ cách tính, nhãn nguồn hiện trên màn hình; vẫn không nói gì về hướng giá của mã đó. Không có `--prices` thì luôn là dữ liệu mô phỏng có seed cố định, và màn hình ghi "Dữ liệu mô phỏng".

**Nhịp và giọng:** mặc định nhịp x1.25 (`TEMPO` trong `pipeline/core.py`, đổi bằng `QT_TEMPO`): giọng đọc +25%, cảnh ngắn lại, nhạc nền hồi hộp tự tổng hợp (nhịp tim + tích tắc, căng dần) ở 120 bpm. Giọng mặc định `vi-VN-NamMinhNeural` (nam, Hà Nội) nâng cao độ +8Hz cho sáng và thanh; ghi đè bằng `QT_VOICE`, `QT_PITCH`, `QT_RATE`.

**Hình minh hoạ và B-roll — thứ tự ưu tiên:**
1. **Ảnh thật của người / nơi / sự kiện có thật** được nhắc tên (Ulam, Legendre, Titanic, sòng Monte Carlo…): ghi `"image": "<id>"` vào cảnh (`cold_open`, `broll`, `story`). Ảnh lấy từ sổ ảnh `knowledge/images/ledger.json` (chỉ Public domain/CC0/CC BY/CC BY-SA, thêm bằng `python images.py fetch …` hoặc `python visuals.py find "<tên>"`); trên màn hình có tên (`label`) và dòng ghi công, caption có mục "## Ảnh". Chân dung dọc hiện trọn trên nền mờ, không cắt mặt. Không bao giờ vẽ/AI một hình trông như ảnh người thật.
2. **Video B-roll Pexels** khớp nghĩa (bàn blackjack, roulette, sóng bão, tàu lượn, bảng điện, trader, tung xu…): `brand/assets/broll/manifest.json` (`tags` → clip), tìm thêm bằng vidIQ `find_broll`, pipeline tự tải (`python pipeline/clips.py`) và ghi công "Video: <tác giả> (Pexels)". Chỉ gắn clip vào tag khi nội dung clip đúng với lời.
3. **Hoạt hoạ tự vẽ** (`pipeline/illustrate.py`, 27 cảnh: casino, giáo sư + bảng đen đúng công thức chủ đề, bão, tảng băng, thiên nga đen, cửa thoát hiểm, hạt bụi Brown, đám đông tung xu, bể nước dòng tiền…). `--broll auto` xen kẽ hình thật (slot lẻ) và hoạt hoạ (slot chẵn); `photo` luôn ưu tiên hình thật; `draw` chỉ vẽ. Hình code/Python chỉ khi lời nói về code.

**Giọng đọc:** edge-tts (vi-VN-NamMinhNeural mặc định / HoaiMyNeural) cần Internet tới `speech.platform.bing.com`. Không vào được thì pipeline lùi về gTTS → espeak-ng → không giọng (phụ đề vẫn đầy đủ, thời lượng ước theo số chữ). Engine thực tế ghi trong `qa_report.md` — phải báo người dùng nếu video không có giọng, kèm cách khắc phục: chạy lệnh trên máy có Internet, hoặc thêm host đó vào allowlist mạng của môi trường.

### 5. Kiểm tra

1. QA tự chạy: số khớp code và cụm cấm **trước** khi render (sai thì dừng), định dạng và khung chữ **sau** render. Đọc `qa_report.md`; KHÔNG ĐẠT thì sửa episode và dựng lại, không lách bằng `--force`.
2. Tự xem: mở `thumbnail.jpg` và trích 5–7 khung hình rải đều video (`ffmpeg -ss <t> -i final.mp4 -frames:v 1 f.png`), xem chữ có đè chart, chart có đọc được trên điện thoại, lời và hình có khớp không. QA máy không bắt được lỗi "nhìn xấu".
3. **Chi tiết trong hình phải đúng logic**, không chỉ "trông giống": số đếm bài phải tính từ đúng các lá đang hiện (Hi-Lo: 2–6 = +1, 7–9 = 0, 10/J/Q/K/A = −1), đồng hồ chỉ đúng giờ được nói, mũi tên lên/xuống đúng màu tăng/giảm, nhãn đúng thuật ngữ. Không vẽ số trang trí; số nào xuất hiện thì phải tính ra được.
4. Chart và 3D phải **tự giải thích, khớp lời**: nhãn đường đặt đúng tên lời đọc dùng (vd "½ Kelly, Kelly, 2×, 4×", không phải "f = 5%"), số cuối đường bằng đúng số được đọc, thứ lời đọc nhắc ("có một đỉnh") phải nhìn thấy được trên hình. Chuỗi khác biên độ thì chuẩn hoá và ghi rõ trên trục.

### 6. Trả kết quả trong chat

Người dùng muốn **văn bản trong chat để copy đăng ngay**. Với mỗi video:

- Tiêu đề, đường dẫn file (`social-output/<id>/final.mp4`), thời lượng, kết luận QA, engine giọng.
- Caption từng nền tảng lấy từ `captions.md`, trong khối copy được, có hashtag và câu miễn trừ. Chỉ đưa **TikTok** và **Facebook**: YT Shorts và IG Reels chỉ đăng nhóm chủ đề ở `channels/yt-ig.md` (dark truth finance, poker theory, psychology facts, game theory).
- Lưu ý còn lại cho người duyệt (giọng thiếu, giá gói cần đối chiếu, nhạc chưa có giấy phép…).

Sau khi đăng, nhắc người dùng ghi view vào `knowledge/episodes.csv` sau 7 ngày (hoặc lấy qua công cụ vidIQ nếu có kết nối) để `hooks.md` dần có hook đã kiểm chứng.

## Chủ đề catalog

Mỗi chủ đề catalog dựng được ngay bằng mọi style, không cần viết gì thêm. `pipeline/term_topic.py` sinh episode từ định nghĩa đã duyệt của QuanTik:

- **Lời thoại:** định nghĩa → cách đọc theo ngưỡng → biến số trong công thức → ví dụ → giới hạn. Câu được rút từ chính định nghĩa, nên mọi số trong đó là sự kiện có nguồn (`facts` trỏ về file và id gốc). QA số vẫn chạy.
- **Code:** đoạn trích thật từ engine tương ứng trong `QuanTik-website/backend/quant_engine/quant.py`, ghi "trích, chỉ đọc". Video không chạy đoạn này, nên không gán số nào cho nó. Đừng viết lời kiểu "code này tính ra…".
- **Chart/3D:** chủ đề thuộc họ một mô hình viết tay (cột *Mô hình demo*, ví dụ `module_egarch_gamma` → garch) thì mô hình đó chạy trên dữ liệu mô phỏng và được ghi rõ là minh hoạ. Nếu không thuộc họ nào: thang ngưỡng đọc vẽ từ định nghĩa; không có ngưỡng thì dùng thẻ công thức hoặc thẻ engine (mục đích + hàm chính).
- **Engine (`engine_*`):** mục đích, số dòng code, hàm công khai, và các chỉ số báo cáo lấy kết quả từ engine đó (đếm từ catalog).

Lời tự sinh mới đạt mức **bản nháp đúng**: chính xác nhưng khô. Trước khi đăng, nên viết episode JSON ghi đè `hook`, `beats`, `takeaway` (giữ nguyên số và ý của định nghĩa) theo giọng văn ở `brand/identity.md`. Viết đè thì vẫn phải bám định nghĩa catalog; muốn nói số không có trong định nghĩa thì đó là chủ đề cho mô hình viết tay.

Một số tổ hợp bị từ chối có lý do: `chart-story` cần chart, `code-reel` cần code engine. Batch báo rõ lý do rồi chạy tiếp. Hai chủ đề bị QA chặn có chủ đích: `sheet-action` có nhãn hệ thống "BUY_NOW: mua ngay", `take_profit` có "giá mục tiêu". Muốn làm thì viết episode diễn đạt lại ("nhãn hành động", "mức chốt lời"), không dùng `--force`.

`python batch.py --topics all --styles carousel --scale 0.5 --no-log` dựng toàn bộ catalog một style (mất vài giờ, chạy nền).

**Làm mới catalog** khi frontend hoặc engine đổi (catalog đã commit nên skill chạy được cả khi không có hai repo nguồn):

```bash
git clone --depth 1 https://github.com/kwuangyong/QuanTik-website /tmp/QuanTik-website
python pipeline/catalog.py --design <đường dẫn QuanTik---Design> --website /tmp/QuanTik-website
```

Cần Node 22.6+ (đọc file TypeScript trực tiếp). Script ghi `knowledge/catalog.json` và `knowledge/CATALOG.md`, kèm commit nguồn để biết catalog lấy từ phiên bản nào.

## Mở rộng

**Nâng một chủ đề catalog lên viết tay** khi nó quan trọng (đăng nhiều, cần số chạy thật). Ví dụ `sortino`:
1. `pipeline/models.py`: `sortino_demo` (≤ 16 dòng, ≤ 56 ký tự/dòng — đây là code hiện lên màn hình), `compute_sortino` → (values, formats, series), `plot2d_sortino(ax, s, upto)` (cố định ylim theo toàn chuỗi để chart không nhảy khi vẽ dần), `surface_sortino` (bề mặt `X,Y,Z` hoặc `lines`/`line`), thêm vào `TOPICS`.
2. `knowledge/models/sortino.md`: các mục như file có sẵn + khối `## video_defaults` JSON đủ trường. Định nghĩa lấy từ `glossary.json` để thống nhất với web.
3. `python batch.py --topics sortino --styles code-reel,carousel --scale 0.5 --no-log` và xem khung hình.

**Thêm style:** thư mục `styles/<tên>/` với `spec.md` và `template.py` có `KIND` (`video`/`carousel`), `DEFAULTS`, `build(ep, model, ctx) -> list[Scene]`, tuỳ chọn `VOICE`, `MUSIC`, `export()`. Ghép từ `pipeline/scenes.py`; mọi chữ vẽ bằng `frames.text_box` để QA đo được tràn khung.

**Cài đặt:** Python 3.10+, `pip install -r requirements.txt`, ffmpeg. Font thương hiệu IBM Plex Mono: thả vào `brand/assets/fonts/`.
