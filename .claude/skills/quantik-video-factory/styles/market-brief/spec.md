# market-brief — trụ cột Nhịp thị trường

Chỉ dựng từ `market_report.json` (không bao giờ mô phỏng). Cảnh: `hook → asof (terminal chỉ số) → breadth (thanh tăng/
giảm/đứng) → liquidity (terminal) → sectors (bar trung vị nhóm ngành) → regime (terminal hoặc đoạn giới hạn) →
interpretation → scenarios (3 thẻ: ✓ xác nhận, ✗ vô hiệu) → risk → takeaway → end`. Header ghi nguồn + phiên + trạng
thái dữ liệu. Episode do `python pillar.py market script` sinh. 60–90 giây.
