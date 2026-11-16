# AGENTS.md — QuanTik content factory

Hướng dẫn cho mọi coding agent (Codex, Claude Code, Cursor…) làm việc trong repo này.

## Repo này làm gì

Sản xuất nội dung mạng xã hội cho QuanTik (quantik.io.vn): video dọc 9:16, carousel, caption, kịch bản về
quant finance và về cách dùng sản phẩm. Toàn bộ quy trình nằm trong skill:

**`.claude/skills/quantik-video-factory/SKILL.md`: đọc file này TRƯỚC KHI làm bất kỳ nội dung nào.**
Đây là Markdown thường, không phụ thuộc Claude: thư mục `.claude/` chỉ là nơi để file.

**Mỗi nền tảng một quy trình riêng** (`platforms/README.md`). Chọn nhánh theo nền tảng trước:

| Nền tảng | Vai trò · nội dung | Đọc | Lệnh chính |
| --- | --- | --- | --- |
| Facebook | **post** tính năng sản phẩm + chuyện hài về nghề (chuyển đổi); **Reels** chỉ cập nhật thị trường + kịch bản có điều kiện, không gọi mua/bán | `platforms/facebook/README.md` | post: `cd pipeline && python post.py comic\|carousel ../posts/<id>.json` · `python post.py market` · Reels: `python pillar.py market produce` |
| TikTok | giáo dục: "Học quant cùng QuanTik" | `platforms/tiktok/README.md` → `SKILL.md` | `cd pipeline && python batch.py --platform tiktok --topics <id> --styles <style>` |
| Instagram Reels | **tiếng Anh**, ≤ 2 phút: larping, motivational, vui, đáng share/save | `platforms/instagram/README.md` | `batch.py --platform instagram --episode ../episodes/en-<id>.json` |
| YouTube Shorts | **tiếng Anh**, ≤ 2 phút, kéo view nhanh: dark truth, tâm lý nhà đầu tư, poker theory | `platforms/youtube-shorts/README.md` | `batch.py --episode ../episodes/en-<id>.json` |

Theo **loại nội dung** (dùng chung mọi nền tảng):

| Người dùng muốn | Đọc | Lệnh chính |
| --- | --- | --- |
| Video/carousel giải thích một mô hình, chỉ số, thuật ngữ quant | `SKILL.md` → `knowledge/`, `styles/` | `cd pipeline && python batch.py --topics <id> --styles <style>` |
| Video **hướng dẫn dùng sản phẩm** (đăng ký, quét toàn sàn, phân tích Quant…) | `tutorial/README.md` | `bash tutorial/run.sh <workdir>` |
| Tâm lý nhà đầu tư, thiên kiến, tài chính hành vi | `pillars/behavioral-finance/PILLAR.md`, `workers/` | `cd pipeline && python pillar.py scaffold behavioral-finance <topic>` → brief → fact-check → `python pillar.py make <episode>` |
| Nhịp thị trường, độ rộng, dòng tiền, kịch bản | `pillars/market-intelligence/PILLAR.md` | `cd pipeline && python pillar.py market produce` |
| Lịch sử quant, nhân vật, quỹ | `pillars/quant-history/PILLAR.md` | như dòng tâm lý, trụ cột `quant-history` |
| Lý thuyết trò chơi, poker, EV, Kelly, rủi ro phá sản | `pillars/decision-science/PILLAR.md` | như dòng tâm lý, trụ cột `decision-science` |
| Ảnh thật / minh hoạ cho người, hãng, sự kiện; nhân vật, hiện vật, biểu tượng | `../quantik-visual-assets/SKILL.md` | `cd pipeline && python visuals.py auto <episode> --write` |

Kiến trúc năm trụ cột: `pillars/README.md`. Vai nghiên cứu/kiểm chứng/sản xuất và hợp đồng bàn giao: `workers/README.md`,
`schemas/`. Chuyển đổi và lệnh mẫu: `MIGRATION.md`. Kiểm thử: `python -m unittest discover -s tests -v` (từ thư mục skill).

(đường dẫn tính từ `.claude/skills/quantik-video-factory/`)

## Luật không được phá

1. **Compliance** (`brand/compliance.md`): nội dung giáo dục, không gọi mua/bán, không hứa lợi nhuận, không có cụm
   cấm. Caption và thẻ cuối luôn có câu miễn trừ. Video sản phẩm dùng **mã cổ phiếu bịa** (QTA…, QTV…).
2. **Số phải có nguồn**: số trong video mô hình đi qua placeholder `{key}` do code tính; QA chặn số gõ tay.
3. **Giá gói**: đối chiếu `https://quantik.io.vn/plans` trước khi nhắc. Ưu đãi thay đổi theo thời gian.
4. Giọng văn, màu, font, vùng an toàn khung hình: `brand/identity.md`.
5. Không dùng tài khoản/thông tin cá nhân của người dùng để đăng nhập site thật; màn cần đăng nhập thì chạy
   giao diện production local với API giả (xem `tutorial/README.md`).
6. **Nguồn truy được** (trụ cột 2–4): mọi claim có `status` và `source_ids` trong `knowledge/sources/ledger.json`; tập
   nghiên cứu cần `research/<id>/factcheck.json` đạt. Lời tự kể, giai thoại, tranh cãi, nhận định phải nói rõ bằng lời
   (QA `check_sources` chặn). Không bịa thống kê, năm, hay trích dẫn.
7. **Thị trường** (trụ cột 3): chỉ dùng dữ liệu có dấu thời gian trong bundle; tách quan sát / mô hình / nhận định; ba
   kịch bản có điều kiện xác nhận và vô hiệu; không nhắc mã cụ thể, không "sẽ tăng/giảm". Không có dữ liệu → nói rõ
   giới hạn, không dựng video.
8. **Ảnh người/hãng/sự kiện**: nhắc ai thì có ảnh — Wikimedia Commons giấy phép tự do (ghi tác giả, giấy phép) hoặc ảnh
   minh hoạ tạo bằng code ghi rõ "minh hoạ"; không bao giờ tạo ảnh giả như ảnh chụp người thật
   (`knowledge/images/README.md`, QA `check_images` chặn).
9. **Mọi video phải có hình ảnh thật** (yêu cầu cố định của chủ sản phẩm): sự vật, nơi chốn, con người, ảnh thật
   hoặc B-roll — không làm video chỉ có chữ trên nền tối. Nguồn: **Openverse** (miễn phí, CC0/PDM/CC BY), **Pexels** (ảnh + video, cần
   `PEXELS_API_KEY`), Wikimedia Commons (luật 8) và **hoạt hoạ vẽ bằng code** (nhân vật, hiện vật, hình hoạ). Các cảnh
   **gối đầu, không lặp** (mọi nền tảng): ảnh thật → nhân vật → ảnh thật → hình hoạ…, cảnh liền nhau khác loại, không
   dùng lại cùng một ảnh/hoạt hoạ trong một video. `batch.py` tự gắn; QA chặn video dưới 60% cảnh có hình, dưới 1/3 ảnh
   thật, có lặp hoặc liền kề cùng loại; Instagram/YouTube Shorts dùng branding tối giản (`profiles.json` › `branding`);
   ảnh CC BY phải ghi nguồn (pipeline tự ghi vào `credits.md` và caption). Chi tiết: `brand/identity.md` mục
   *Hình ảnh thật & B-roll*.
10. Output vào `social-output/<id>/` (đã gitignore). Trả về trong chat: đường dẫn file, thời lượng, kết luận QA,
   engine giọng, caption từng nền tảng trong khối copy được, và lưu ý còn lại cho người duyệt.

## Môi trường

- Python 3.10+, `pip install -r .claude/skills/quantik-video-factory/requirements.txt edge-tts`, ffmpeg.
- Video hướng dẫn cần thêm Node 20.9+ và Chromium cho Playwright.
- Mạng: `speech.platform.bing.com` (giọng đọc edge-tts), `quantik.io.vn`, `github.com` (clone `QuanTik---Design`),
  `trading.agr.vn` (dữ liệu thị trường cho trụ cột 3), `commons.wikimedia.org` + `upload.wikimedia.org` (ảnh có giấy phép mở;
  `thumb.wikimedia.org` nếu muốn tải trực tiếp, không bắt buộc), `api.openverse.org` (ảnh thật), `api.pexels.com` +
  `images.pexels.com` + `videos.pexels.com` (B-roll, cần key).
  Không có mạng tới TTS thì pipeline lùi về gTTS → espeak → không giọng; phải báo người dùng.
- Repo nguồn liên quan (chỉ đọc): `kwuangyong/QuanTik---Design` (web production, Next.js),
  `kwuangyong/QuanTik-website` (engine quant `backend/quant_engine/quant.py`; frontend React cũ, không dùng để quay).

## Người dùng

Chủ sản phẩm QuanTik, nói tiếng Việt, muốn kết quả nhanh và văn bản copy đăng được ngay. Trọng tâm quảng bá là
**Quét toàn sàn** và **Phân tích Quant**. Trả kết quả tập trụ cột mới kèm nguồn chính và nhãn trạng thái từ `sources.md`. Báo tiến độ ngắn gọn khi việc kéo dài.
