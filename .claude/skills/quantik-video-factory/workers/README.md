# Workers — ai làm gì trong dây chuyền nội dung

Worker là **một vai** có đầu vào, đầu ra và hợp đồng bàn giao rõ ràng, không phải một chương trình chạy riêng.
Phần việc cần phán đoán (đọc tài liệu, viết lời, kiểm chứng) do một agent đảm nhận bằng cách đọc file spec của vai đó;
phần việc lặp lại được (lấy dữ liệu, tính toán, dựng hình, QA) là code trong `pipeline/` và `qa/`.
Không có agent độc lập nào chạy nền: mỗi vai được gọi như một subagent/task khi cần, rồi bàn giao bằng file JSON.

## Cách gọi một worker

Trong Claude Code (hoặc Codex/Cursor), giao cho một subagent/task với lời nhắn:

> Đọc `.claude/skills/quantik-video-factory/workers/<worker>.md` và làm đúng vai đó cho chủ đề `<topic id>`
> (trụ cột `<pillar>`). Ghi đầu ra vào các đường dẫn file spec yêu cầu. Không làm việc của worker khác.

Một agent duy nhất cũng có thể đóng lần lượt nhiều vai trong cùng phiên, miễn là **mỗi vai ghi ra đúng file bàn giao**
và Fact-checker không kiểm chính claim do mình vừa viết mà không tra nguồn lại.

## Danh sách

| Worker | Loại | File spec | Đầu ra (schema) | Trạng thái |
| --- | --- | --- | --- | --- |
| Behavioral Finance Researcher | agent | `behavioral-finance-researcher.md` | `research/<id>/brief.json` (research_brief) | đã chạy thử 1 tập (`bf-disposition-bias-lab`) |
| Market Intelligence Analyst | code + agent | `market-intelligence-analyst.md` | bundle → `market_report.json` → `market_editorial.json` | code fetch/analyze/editorial chạy thật với dữ liệu AGR; phần duyệt nhận định là vai agent |
| Quant Historian | agent | `quant-historian.md` | `research/<id>/brief.json` | đã chạy thử 1 tập (`qh-thorp-history-story`) |
| Game Theory Researcher | agent + code | `game-theory-researcher.md` | `research/<id>/brief.json` + mô hình trong `pipeline/pillar_models.py` | đã chạy thử 1 tập (`ds-ev-variance-decision-lab`); 3 mô hình có test |
| Fact-checker | agent + gate | `fact-checker.md` | `research/<id>/factcheck.json` (factcheck) + gate `qa/check_sources.py` | gate có 10 test; vai agent đã kiểm 3 brief bằng web search |
| Scriptwriter | agent | `scriptwriter.md` | `episodes/<id>.json` (episode_script) | dùng chung cho 5 trụ cột |
| Visual Director | agent (chọn) + code (dựng) | `visual-director.md` | style + trường `visual` từng đoạn | 4 style mới + 8 style cũ |
| Animation | code | `animation.md` | khung hình, `storyboard.json`, `visual_assets.json` | `render.py`, `frames.py`, `scenes.py`, `pillar_scenes.py` |
| Voice & Sound | code | `voice-sound.md` | wav từng cảnh, nhạc nền, `final.mp4` | `voiceover.py`, `assemble.py` |
| Production QA | code + người duyệt | `production-qa.md` | `qa_report.md`, `qa_report.json` | 6 gate tự động + checklist người duyệt |

## Luồng bàn giao

```
                 ┌──────────────── trụ cột nghiên cứu (2, 4a, 4b) ───────────────┐
 chủ đề ─▶ Researcher ─brief.json─▶ Fact-checker ─factcheck.json─▶ Scriptwriter ─episode.json─┐
                                                                                             │
                 ┌──────────────── trụ cột thị trường (3) ───────────────────────┐            │
 lịch ─▶ fetch ─bundle─▶ analyze ─market_report─▶ Analyst (editorial) ─▶ script ─episode.json─┤
                                                                                             ▼
                          Visual Director (style, visual) ─▶ Production QA (trước render: số, cụm cấm,
                          khung trụ cột, nguồn & fact-check, dữ liệu thị trường) ─▶ Animation + Voice & Sound
                          ─▶ Production QA (sau render: định dạng, khung chữ) ─▶ người duyệt ─▶ đăng
```

Trụ cột 1 (Quant Education) giữ nguyên quy trình cũ trong `SKILL.md`: không có researcher, số liệu do mô hình viết tay
hoặc định nghĩa catalog đã duyệt.

## Hợp đồng chung

1. Mỗi bàn giao là một file JSON hợp lệ theo `schemas/`. Kiểm: `python pipeline/pillar.py validate <file> <schema>`.
2. Mọi claim mang `status` và `source_ids` trỏ vào `knowledge/sources/ledger.json`. Nguồn mới phải vào ledger trước.
3. Số trong lời đọc chỉ đến từ `{placeholder}` (mô hình, market report) hoặc `facts` có `source_id`.
4. Worker sau không sửa ngầm đầu ra của worker trước: thấy sai thì trả lại, ghi lý do vào `open_questions`/`note`.
5. Không ai được dùng `--force` để đăng.
