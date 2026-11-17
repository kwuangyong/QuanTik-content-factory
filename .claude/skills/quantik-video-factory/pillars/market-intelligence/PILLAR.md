# Trụ cột 3 — Market Intelligence & Research (nhịp thị trường)

**Mục tiêu:** đọc trạng thái thị trường bằng dữ liệu có dấu thời gian, tách bạch **quan sát / mô hình / nhận định**,
và luôn nói giới hạn. Worker: `workers/market-intelligence-analyst.md`. Style: `market-brief`.

## Pipeline 4 giai đoạn (mỗi giai đoạn chỉ đọc file của giai đoạn trước)

```
fetch ──▶ bundle-*/manifest.json + indexsnaps.json + instruments.json [+ history.csv]
analyze ──▶ market_report.json   (observed · model · regime · sectors · limitations · data_status)
editorial ──▶ market_editorial.json   (nhận định có rào + 3 kịch bản có điều kiện; bản nháp luật cố định → Analyst duyệt)
script + make ──▶ episode.json ──▶ video + sources.md (dataset, URL, giờ lấy, kỳ dữ liệu, giới hạn)
```

```bash
cd .claude/skills/quantik-video-factory/pipeline
python pillar.py market fetch          # ~1 phút (bảng giá ~3 MB)
python pillar.py market analyze
python pillar.py market editorial      # rồi Analyst đọc/sửa market_editorial.json
python pillar.py market script
python pillar.py check <bundle>/episode.json
python pillar.py make  <bundle>/episode.json --scale 0.5
# hoặc một lệnh: python pillar.py market produce --scale 0.5
```

Dữ liệu thô nằm ở `social-output/_market/` (gitignored).

## Nguồn dữ liệu

| Dataset | Nguồn (ledger id) | Cho gì |
| --- | --- | --- |
| indexsnaps | `agr-indexsnaps` — feed AGR, cùng nguồn dashboard QuanTik | điểm/% VN-INDEX, VN30, HNX, UPCOM; số mã tăng/giảm/đứng; KL, giá trị |
| instruments | `agr-instruments` | % từng mã → trung vị nhóm ngành, tỷ trọng 10 mã lớn nhất, khối ngoại ước tính |
| history (tuỳ chọn) | `user-history-csv` + manifest bắt buộc | regime MA50/MA200, σ 20 phiên, sụt từ đỉnh 52 tuần |
| sector_map.json | `quantik-industry-watchlist` (commit 306f46d) | nhóm ngành tham chiếu (18 nhóm ngành; 5 rổ theo dõi bị loại) |

Lưu trữ: mỗi lần `fetch` sau 15:00 là một snapshot cuối phiên; `analyze` gom các snapshot này thành lịch sử riêng, đủ
200 phiên thì tự phân loại regime mà không cần CSV.

## Phân tích (giai đoạn 2) — luật, không phán đoán

| Chỉ số | Cách tính | Loại |
| --- | --- | --- |
| breadth_pct, breadth_state | tăng / (tăng + giảm); ≥ 60% tích cực, ≤ 40% tiêu cực | mô hình |
| updown_vol | KL mã tăng / KL mã giảm | mô hình |
| top10_share | giá trị 10 mã lớn nhất / tổng giá trị cổ phiếu HOSE | mô hình |
| foreign_net_bn | Σ(KL ngoại mua − bán) × giá bình quân (ước tính) | mô hình |
| sectors, lead/lag | trung vị % thay đổi trong nhóm (≥ 5 mã có khớp), sức mạnh tương đối 1 phiên = trung vị − % VN-INDEX | mô hình |
| regime | tăng: giá > MA200, MA50 > MA200, MA200 dốc lên 20 phiên; giảm: ngược lại cả ba; còn lại đi ngang. Biến động: phân vị σ20 trong 252 giá trị | mô hình (cần ≥ 200 phiên) |

## Trạng thái dữ liệu

| data_status | Khi nào | Hệ quả |
| --- | --- | --- |
| fresh | as_of là phiên đã đóng gần nhất | dựng bình thường |
| intraday | snapshot trước 15:00 cùng ngày | ghi giờ snapshot, giới hạn "số còn thay đổi" |
| stale | đã có phiên đóng cửa sau as_of | editorial từ chối; `--allow-stale` chỉ cho bản tổng kết, lời phải nói ngày + "dữ liệu cũ" |
| unavailable | không lấy được chỉ số | không có số nào, không có video |
| sample | fixture test | không bao giờ được đăng |

Ngày nghỉ lễ: thêm vào `holidays.json` (`{"dates": ["2027-02-15", …]}`) — chưa có sẵn, cần chủ sản phẩm cập nhật.

## Khung tập phim

`hook → asof → breadth → liquidity → sectors → regime → interpretation → scenarios → risk → takeaway → end`

Nhãn từng đoạn: asof/breadth/liquidity/sectors = QUAN SÁT hoặc MÔ HÌNH; regime = MÔ HÌNH hoặc đoạn giới hạn;
interpretation/scenarios/risk = NHẬN ĐỊNH. `check_market` chặn đoạn trộn loại.

## Kịch bản (bắt buộc đúng ba)

Mỗi kịch bản có điều kiện **xác nhận** và **vô hiệu** đo được bằng dữ liệu pipeline có, cộng hành động quản trị rủi ro
chung. Xác suất (nếu có) phải gọi là "ước lượng chủ quan". Không nêu mã, không "sẽ tăng/giảm".

## Catalog

`catalog.json`: nhịp cuối phiên (đã chạy với dữ liệu thật), regime tuần (cần lịch sử), luân chuyển ngành, thanh khoản &
khối ngoại, điều kiện rủi ro (cần lịch sử), sự kiện vĩ mô (chỉ sự kiện đã công bố, có nguồn).
