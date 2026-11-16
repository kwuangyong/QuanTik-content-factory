# Trụ cột 4b — Game Theory, Poker & Decision Science (ra quyết định)

**Mục tiêu:** EV, phương sai, Nash, Kelly, rủi ro phá sản — đúng kỹ thuật, hấp dẫn, và luôn nói rõ poker giống/khác
thị trường ở đâu. Worker: `workers/game-theory-researcher.md`. Style: `decision-lab` (mặc định), code-reel, kinetic-text,
whiteboard-math, carousel.

## Khung (bắt buộc)

`hook → setup → intuition → math → simulation → analogy → lesson → takeaway → end`

| Vai | Nội dung | Hình mặc định |
| --- | --- | --- |
| setup | trò chơi và giả định (nói "giả sử") | chữ lớn |
| intuition | trực giác thường gặp và chỗ nó sai | chữ lớn |
| math | code chạy thật + kết quả | code + terminal |
| simulation | hình mô phỏng | chart |
| analogy | **GIỐNG / KHÁC** thị trường — bắt buộc (`analogy.similar`, `analogy.breaks`) | hai cột |
| lesson | quy tắc ra quyết định | 3D |

## Mô hình chạy được (`pipeline/pillar_models.py`)

| Mô hình | Kết quả kiểm bằng test |
| --- | --- |
| `ev_variance` | % người có lợi thế vẫn lỗ sau n ván khớp Φ(−μ√n/σ) trong 3 điểm %; rủi ro phá sản mô phỏng ≤ công thức |
| `kuhn_poker` | CFR hội tụ cân bằng Nash Kuhn (1950): giá trị −1/18, Q theo 1/3, K tố ≈ 3× J bluff |
| `kelly` (dùng lại từ trụ cột 1) | — |

## Phân loại chủ đề

`catalog.json` — Xác suất & EV · Lý thuyết trò chơi · Quy mô vị thế · Ra quyết định (resulting, pot odds).

## Ranh giới

Không cổ vũ cờ bạc ("kiếm tiền từ poker", "bất bại" là cụm cấm của trụ cột). Tham số mô phỏng là giả định.

## Tập mẫu

`episodes/ds-ev-variance-decision-lab.json` — "Chơi đúng mà vẫn thua".
