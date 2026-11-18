# Kiến trúc đa trụ cột — QuanTik Content Factory

Repo từ một dây chuyền (giải thích mô hình quant) thành nền tảng năm kiến trúc nội dung dùng chung một bộ máy dựng
hình, giọng đọc và QA. Mỗi trụ cột có quy trình nghiên cứu, phân loại chủ đề, worker, khung kịch bản, cách kể, hình,
yêu cầu kiểm chứng và tiêu chí QA riêng — **không ép mọi trụ cột vào cùng một cấu trúc**.

| # | Trụ cột (id) | Khung kể | Style mặc định | Worker nghiên cứu | Bằng chứng tối thiểu | Fact-check |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Quant Education (`quant-education`) | trực giác → công thức → số từ code → giới hạn | code-reel (+7) | — | số từ code | không (số do code) |
| 2 | Behavioral Finance (`behavioral-finance`) | vấn đề → cơ chế → bằng chứng → hệ quả → bài học → góc quant | bias-lab | Behavioral Finance Researcher | tier A | bắt buộc |
| 3 | Market Intelligence (`market-intelligence`) | dữ liệu → độ rộng → thanh khoản → ngành → regime → nhận định → 3 kịch bản → rủi ro | market-brief | Market Intelligence Analyst | dữ liệu gốc có dấu thời gian | qua dữ liệu + check_market |
| 4a | Quant History (`quant-history`) | hook → bối cảnh → xung đột → đột phá → hệ quả → bài học | history-story | Quant Historian | tier B | bắt buộc |
| 4b | Decision Science (`decision-science`) | trò chơi → trực giác → toán → mô phỏng → giống/khác thị trường → bài học | decision-lab | Game Theory Researcher | tier A | bắt buộc |

Trụ cột 4 trong yêu cầu gốc (lịch sử, nhân vật, toán học, lý thuyết trò chơi, poker) được tách thành **4a** và **4b**
vì cách kể và cách kiểm chứng khác hẳn nhau: 4a kể chuyện và phân loại độ tin cậy của lời kể, 4b chứng minh bằng mô hình.

## Thành phần

```
pillars/registry.json          định nghĩa các trụ cột (1, 2, 3, 4a, 4b, 5 dark-truth) (schemas/content_pillar.schema.json)
pillars/<id>/PILLAR.md         quy trình, khung, hình, kiểm chứng, QA của trụ cột
pillars/<id>/catalog.json      phân loại chủ đề (trụ cột 1 dùng knowledge/catalog.json)
workers/*.md                   10 vai: 5 vai nghiên cứu/kiểm chứng mới + 5 vai sản xuất đã có
schemas/*.schema.json          hợp đồng bàn giao (10 schema)
knowledge/sources/ledger.json  sổ nguồn dùng chung — mọi claim trỏ về đây
research/<episode>/            brief.json (researcher) + factcheck.json (fact-checker)
pipeline/pillar.py             CLI đa trụ cột (list, topics, scaffold, validate, check, make, market …)
pipeline/pillar_registry.py    tra trụ cột/chủ đề, sinh mặc định cho episode
pipeline/pillar_models.py      mô hình chạy được: prospect_theory, ev_variance, kuhn_poker, MarketModel
pipeline/pillar_scenes.py      cảnh có nhãn vai + trạng thái + chân trang nguồn
pipeline/market/               fetch → analyze → editorial → script (4 giai đoạn tách biệt)
styles/{bias-lab,history-story,decision-lab,market-brief}/   4 style mới
qa/check_script.py · check_sources.py · check_market.py      3 gate mới
tests/test_pillars.py + tests/fixtures/                      bộ test (không cần mạng)
```

## Bản đồ năng lực cũ → kiến trúc mới

| Năng lực có sẵn | Trong kiến trúc mới | Thay đổi |
| --- | --- | --- |
| `batch.py --topics/--styles/--episode` | lệnh chính của trụ cột 1; cũng dựng episode trụ cột mới | thêm nhánh tra trụ cột *trước* nhánh cũ (chỉ kích hoạt với id trụ cột hoặc `pillar` trong episode); thêm `--check-only` |
| 9 mô hình `models.py` | dùng lại cho trụ cột 4a/4b (Kelly cho Thorp) | không đổi |
| catalog 199 chủ đề, `term_topic.py` | trụ cột 1 | không đổi |
| 8 style | trụ cột 1; dựng được cả episode trụ cột mới (beats suy từ segments) | không đổi |
| `check_numbers` | gate cho mọi trụ cột | tách số trong chuỗi do code sinh (ngày, giờ); `{fact}` dùng làm placeholder |
| `check_banned` | gate cho mọi trụ cột | nhận thêm `extra_banned` của trụ cột |
| `check_format`, `report.py` | Production QA | report thêm dòng gate mới + `qa_report.json` |
| `voiceover.py` | Voice & Sound | edge-tts nạp CA của proxy (`SSL_CERT_FILE`) và đi qua `HTTPS_PROXY` |
| `knowledge/stories/` (LTCM, Medallion) | tư liệu cho Quant Historian | chuyển dần sang brief + ledger |
| `tutorial/` | video hướng dẫn sản phẩm | không đổi |
| `episodes.csv` | nhật ký chung | cột `notes` ghi `pillar=<id>` cho tập trụ cột mới |

## Luồng dữ liệu một tập nghiên cứu

```
catalog topic ─▶ scaffold ─▶ brief.json ─▶ factcheck.json ─▶ episode.json ─▶ pillar.py check (gate trước render)
     ─▶ render (pillar_scenes: nhãn trạng thái + nguồn trên từng cảnh) ─▶ check_format
     ─▶ social-output/<id>/: final.mp4 · captions.md (có mục Nguồn) · sources.md · storyboard.json ·
        visual_assets.json · qa_report.md/json · values.json · narration.json
```

Nguồn đi suốt dây chuyền: claim (brief) → claim id trên đoạn (episode) → nhãn + chân trang trên khung hình →
`storyboard.json` (claim + nguồn từng cảnh) → `sources.md` + mục Nguồn trong caption.

## Kiểm thử

`python -m unittest discover -s tests -v` — xem `tests/RESULTS.md` cho kết quả lần chạy gần nhất.

## Trụ cột 5 — Dark Truth (tiếng Anh)

Nội dung tiếng Anh cho IG Reels / YouTube Shorts: tiền, địa vị, áp lực xã hội. Style `dark-story` (nhân vật hoạt hoạ
vẽ bằng code trong `pipeline/darkart.py`, không chart/code). Không cần worker nghiên cứu; tối đa một số liệu mỗi tập,
từ mô hình trong `pipeline/pillar_models.py` hoặc ledger. Ranh giới với trụ cột 2 (tâm lý đầu tư) và 4b (poker/game
theory): `pillars/dark-truth/PILLAR.md`.
