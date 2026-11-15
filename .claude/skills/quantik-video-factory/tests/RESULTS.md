# Kết quả kiểm thử — nâng cấp đa trụ cột (2026-11-15)

Môi trường: Python 3.13, ffmpeg, container cloud có proxy TLS. Lệnh chạy từ thư mục skill.

## 1. Bộ test tự động (không cần mạng)

```bash
python -m unittest discover -s tests -v
```

**38 test, 37 đạt, 1 bỏ qua có chủ đích (test render, cần `QT_RENDER_TESTS=1`), 0 lỗi.** Thời gian ~1 giây.

| Nhóm | Test | Kiểm điều gì |
| --- | --- | --- |
| Contracts (5) | registry, ledger, brief/factcheck đúng schema; mô hình trong catalog tra được; style của trụ cột tồn tại | hợp đồng JSON |
| BackwardCompat (5) | topic viết tay, topic catalog, `models.TOPICS` không đổi; style trụ cột từ chối topic cũ; episode mẫu cũ vẫn qua gate | tương thích ngược |
| PillarModels (3) | prospect theory: lãi tối thiểu = 2,25^(1/0,88); EV/variance: mô phỏng khớp Φ(−μ√n/σ) trong 3 điểm %; Kuhn poker: CFR → giá trị −1/18 ± 0,005, Q theo ≈ 1/3, K tố ≈ 3× J bluff | mô hình đúng lý thuyết |
| RepresentativeEpisodes (2) | mỗi tập mẫu của 3 trụ cột nghiên cứu qua mọi gate trước render; episode trụ cột dựng được cả bằng style cũ | tập đại diện |
| SourceTraceability (12) | nguồn lạ, `documented` chỉ dựa hồi ký, lời tự kể thiếu cụm rào, fact-check `rejected`, lệch trạng thái, thiếu factcheck, fact không có `source_id`, đoạn không claim, **số gõ tay "3,41%" (claim đã bị loại) bị chặn end-to-end**, sai thứ tự vai, decision-science thiếu cột KHÁC | truy vết nguồn & fact-check |
| MarketPipeline (9) | URL không tới được → `failed` + `unavailable`, không có số nào, editorial từ chối, gate chặn; dữ liệu cũ 5 phiên → `stale`, từ chối trừ `allow_stale`, lời phải có "dữ liệu cũ"; thiếu lịch sử → đoạn giới hạn; regime tăng/giảm trên lịch sử tổng hợp; CSV lịch sử thiếu manifest bị từ chối; nhắc mã cụ thể / "sẽ tăng" bị chặn, câu phủ định thì không; fixture luôn `sample` không đăng được; kịch bản thiếu điều kiện vô hiệu bị chặn; lịch phiên (Chủ nhật, thứ Hai trước/sau 15:00) | pipeline thị trường |
| VoiceRetry (1) | engine TTS lỗi 2 lần rồi được → vẫn có giọng | giọng đọc |

## 2. Render (test opt-in, giọng offline để kết quả xác định)

```bash
QT_RENDER_TESTS=1 python -m unittest tests.test_pillars.RenderTests -v
```

**Đạt** (229 giây): 3 style mới (`bias-lab`, `history-story`, `decision-lab`) dựng ra `final.mp4`, `sources.md`,
`storyboard.json`, `visual_assets.json`, `qa_report.json`; `qa_report.json` và `storyboard.json` đúng schema; QA số, cụm
cấm, định dạng, khung trụ cột, nguồn & fact-check đều ĐẠT.

## 3. Tập đại diện với giọng thật (edge-tts, bản xem nhanh 540×960)

| Tập | Trụ cột | Gate trước render | Kết quả render |
| --- | --- | --- | --- |
| `bf-disposition-bias-lab` | 2 | ĐẠT | **ĐẠT** — 73,6 s, mọi cảnh có giọng |
| `qh-thorp-history-story` | 4a | ĐẠT | **KHÔNG ĐẠT (đúng)** — 76,6 s; 1 cảnh (`conflict`) TTS không trả âm thanh → gate chặn |
| `ds-ev-variance-decision-lab` | 4b | ĐẠT | **KHÔNG ĐẠT (đúng)** — 73,6 s; 3 cảnh TTS không trả âm thanh → gate chặn |
| `mi-2026-11-13-market-brief` (dữ liệu AGR thật phiên 13/11/2026) | 3 | ĐẠT (số, cụm cấm, khung, nguồn, dữ liệu thị trường) | **KHÔNG ĐẠT (đúng)** — 94,0 s > 90 s và 1 cảnh TTS không trả âm thanh |

Cả bốn tập dựng xong và mọi gate nội dung (số, cụm cấm, khung trụ cột, nguồn & fact-check, dữ liệu thị trường) đều đạt.
Ba tập bị chặn ở gate giọng đọc vì dịch vụ edge-tts không trả âm thanh cho một số câu **trong môi trường này** (xem mục 5).
Lúc render ba tập này đã thử lại 8 lần cho mỗi cảnh và lùi về từng câu. Với giọng offline (mục 2), cả ba đều ĐẠT.
Trước khi đăng: dựng lại trên máy có kết nối edge-tts ổn định, `--scale 1`, và rút kịch bản thị trường thêm ~5 giây.

## 4. Pipeline thị trường với dữ liệu thật

`python pillar.py market fetch` (2026-11-15, Chủ nhật): indexsnaps `ok` 4 dòng, instruments `ok` 2.049 mã, phiên 13/11/2026
→ `data_status = fresh`, `sessions_behind = 0`. Giới hạn được ghi đúng: nhóm ngành không phải ICB; chưa đủ lịch sử
(1/200 phiên) nên không có regime. Lời đọc sinh ra: "VN-INDEX tăng 0,01%, nhưng chỉ 36% số mã tăng…", 108 tăng /
192 giảm / 69 đứng, giá trị khớp 15.138 tỷ, 10 mã lớn nhất chiếm 34%, 2/11 nhóm ngành tăng.

## 5. Vấn đề phát hiện trong lúc kiểm thử (và đã xử lý thế nào)

| Vấn đề | Phát hiện bởi | Xử lý |
| --- | --- | --- |
| edge-tts không chạy sau proxy TLS (pin CA certifi) | probe giọng | `voiceover.py` nạp CA từ `SSL_CERT_FILE`, dùng `HTTPS_PROXY` |
| **edge-tts lỗi tạm thời (`NoAudioReceived`) làm một số cảnh mất giọng mà QA cũ không báo** — ảnh hưởng cả video trụ cột 1 | so thời lượng cảnh với ước lượng | thử lại có backoff, lùi về tổng hợp từng câu, và gate mới: cảnh có lời mà không có giọng → KHÔNG ĐẠT |
| **Một số câu luôn thất bại** (3/3 lần, cách nhau 5 giây, lúc không có tải khác) trong khi câu khác luôn được — ví dụ "2 trên 11 nhóm ngành tăng." thất bại, "Lợi thế càng nhỏ, càng cần nhiều ván." luôn được. Không thấy quy luật theo từ ngữ; nghi do proxy kiểm tra TLS của môi trường cloud chen vào websocket của edge-tts, **chưa xác định được** | gate cảnh mất giọng | không sửa được từ trong repo; gate chặn đúng, nên không video nào đăng ra với cảnh câm. Cần dựng lại trên máy người dùng |
| Kịch bản dài hơn dự tính (giọng edge ≈ 2,2 từ/giây, không phải 3,3) | gate thời lượng | rút gọn kịch bản; trần 90 s cho trụ cột mới |
| Chart nhóm ngành bỏ mất nhóm yếu nhất mà lời đọc nhắc tới; nhãn bị cắt | xem khung hình | hiện đủ hai đầu, nhãn đặt trong vùng vẽ |
| Đoạn giới hạn regime hiện terminal rỗng | xem khung hình | đoạn giới hạn luôn là chữ + nhãn GIỚI HẠN DỮ LIỆU |
| Nhóm ngành 3 mã đứng đầu bảng xếp hạng | đọc lời sinh ra | cần ≥ 5 mã có khớp mới xếp hạng |
| "×12,2x" (trùng ký hiệu) | xem khung hình | sửa chữ màn hình |
| Số "60" gõ tay trong tiêu đề chart, "−10" trong nhãn | gate số | khai báo literal / đổi nhãn |
| Con số "3,41%" (Odean 1998) không xác nhận được | fact-checker (web search) | loại khỏi brief, ghi `rejected_claims`; có test chặn nếu ai thêm lại |
| Thorp có công thức trước Black–Scholes | fact-checker | hạ thành `self_reported`, lời có "theo lời kể" |

## 6. Hồi quy lệnh cũ

`python batch.py --topics garch,module_egarch_gamma --styles code-reel,carousel --scale 0.5 --no-log` → 4/4 ĐẠT
(topic viết tay + topic catalog, video + carousel). `python batch.py --topics kelly --styles kinetic-text` ĐẠT trước
khi sửa (mốc so sánh).
