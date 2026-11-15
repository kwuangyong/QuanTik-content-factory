# AGENTS.md — QuanTik content factory

Hướng dẫn cho mọi coding agent (Codex, Claude Code, Cursor…) làm việc trong repo này.

## Repo này làm gì

Sản xuất nội dung mạng xã hội cho QuanTik (quantik.io.vn): video dọc 9:16, carousel, caption, kịch bản về
quant finance và về cách dùng sản phẩm. Toàn bộ quy trình nằm trong skill:

**`.claude/skills/quantik-video-factory/SKILL.md`: đọc file này TRƯỚC KHI làm bất kỳ nội dung nào.**
Đây là Markdown thường, không phụ thuộc Claude: thư mục `.claude/` chỉ là nơi để file.

Chọn nhánh theo yêu cầu:

| Người dùng muốn | Đọc | Lệnh chính |
| --- | --- | --- |
| Video/carousel giải thích một mô hình, chỉ số, thuật ngữ quant | `SKILL.md` → `knowledge/`, `styles/` | `cd pipeline && python batch.py --topics <id> --styles <style>` |
| Video **hướng dẫn dùng sản phẩm** (đăng ký, quét toàn sàn, phân tích Quant…) | `tutorial/README.md` | `bash tutorial/run.sh <workdir>` |
| Tâm lý nhà đầu tư, thiên kiến, tài chính hành vi | `pillars/behavioral-finance/PILLAR.md`, `workers/` | `cd pipeline && python pillar.py scaffold behavioral-finance <topic>` → brief → fact-check → `python pillar.py make <episode>` |
| Nhịp thị trường, độ rộng, dòng tiền, kịch bản | `pillars/market-intelligence/PILLAR.md` | `cd pipeline && python pillar.py market produce` |
| Lịch sử quant, nhân vật, quỹ | `pillars/quant-history/PILLAR.md` | như dòng tâm lý, trụ cột `quant-history` |
| Lý thuyết trò chơi, poker, EV, Kelly, rủi ro phá sản | `pillars/decision-science/PILLAR.md` | như dòng tâm lý, trụ cột `decision-science` |

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
8. Output vào `social-output/<id>/` (đã gitignore). Trả về trong chat: đường dẫn file, thời lượng, kết luận QA,
   engine giọng, caption từng nền tảng trong khối copy được, và lưu ý còn lại cho người duyệt.

## Môi trường

- Python 3.10+, `pip install -r .claude/skills/quantik-video-factory/requirements.txt edge-tts`, ffmpeg.
- Video hướng dẫn cần thêm Node 20.9+ và Chromium cho Playwright.
- Mạng: `speech.platform.bing.com` (giọng đọc edge-tts), `quantik.io.vn`, `github.com` (clone `QuanTik---Design`),
  `trading.agr.vn` (dữ liệu thị trường cho trụ cột 3).
  Không có mạng tới TTS thì pipeline lùi về gTTS → espeak → không giọng; phải báo người dùng.
- Repo nguồn liên quan (chỉ đọc): `kwuangyong/QuanTik---Design` (web production, Next.js),
  `kwuangyong/QuanTik-website` (engine quant `backend/quant_engine/quant.py`; frontend React cũ, không dùng để quay).

## Người dùng

Chủ sản phẩm QuanTik, nói tiếng Việt, muốn kết quả nhanh và văn bản copy đăng được ngay. Trọng tâm quảng bá là
**Quét toàn sàn** và **Phân tích Quant**. Trả kết quả tập trụ cột mới kèm nguồn chính và nhãn trạng thái từ `sources.md`. Báo tiến độ ngắn gọn khi việc kéo dài.
