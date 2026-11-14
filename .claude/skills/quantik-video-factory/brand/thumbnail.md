# Thumbnail QuanTik: quy chuẩn thiết kế

Đọc file này trước khi làm hoặc sửa thumbnail (người hoặc agent: Claude Code, Codex…).
Ảnh mẫu đã duyệt: `brand/thumbnail-refs/` (`sharpe.jpg`, `monte-carlo.jpg`, `tutorial-a-z.jpg`).
Code: `pipeline/thumbnail.py`. Lệnh:

```bash
cd pipeline && python thumbnail.py --topic <topic> --no <số tập> --out ../../../../social-output/<id>
```

Ra `social-output/<id>/thumbnail-NN.jpg` (NN = số tập, 2 chữ số).

## Yêu cầu của chủ sản phẩm (bắt buộc)

1. **Series có đánh số:** mọi thumbnail video kiến thức đều có dải **"HỌC QUANT CÙNG QUANTIK #N"**, N là số tập.
   Không biết N thì hỏi người dùng (hoặc lấy tập lớn nhất trong `knowledge/episodes.csv` + 1 và xin xác nhận).
2. **Phong cách sáng như ảnh mẫu**, không dùng nền tối của video.
3. Tiêu đề là **một câu nghịch lý/câu hỏi gây tò mò**, chữ in hoa rất to, con số "đắt" tô màu.
4. Mọi con số trên ảnh lấy từ code (placeholder `{key}`), giống luật số liệu của video.
5. Luôn có dòng **"Dữ liệu mô phỏng • Không phải khuyến nghị"** (compliance) và `quantik.io.vn` ở chân ảnh.

## Bố cục 1080×1920 (từ trên xuống)

| Vùng | y (px) | Nội dung |
| --- | --- | --- |
| Logo | 64–214 | Ô vuông bo góc nền gần đen (#181816), logo QuanTik, góc trái |
| Tag | 100–176 | Pill viền xanh đậm 4px, chữ in hoa ExtraBold 38: tên chủ đề (VD "SORTINO RATIO"), góc phải |
| Series | 262–338 | Căn giữa: "HỌC QUANT CÙNG QUANTIK" (ExtraBold 40, xanh đậm) + ô cam bo góc "#N" (Black 54, chữ trắng) |
| Tiêu đề | ~400–830 | 2–4 dòng in hoa, Inter Display Black, căn giữa, mỗi dòng tự co cho vừa 960px. Dòng nhấn mạnh to nhất (~190px), dòng phụ ~110–120px. Khoảng dòng ≥ 1,02 × cỡ chữ để dấu tiếng Việt (Ộ, Ạ, Ủ) không chạm nhau |
| Pill phụ | ngay dưới tiêu đề | Nền xanh nhạt #DCE8E0, chữ SemiBold 40 xanh đậm: cơ chế + "code Python" |
| Chart | đến y≈1610 | Chart thật của mô hình, nền trong suốt, không khung. Bên phải là cột nhãn số: nhãn Bold 34 + số Black 96, màu theo series |
| Chân | 1680–1810 | "Dữ liệu mô phỏng ● Không phải khuyến nghị" (SemiBold 40, chấm cam) · "quantik.io.vn" ExtraBold 50 giữa hai gạch ngang |

Lề trái/phải 64px. Nội dung chính nằm trong y 250–1650 để lưới 3:4 trên trang cá nhân TikTok/Reels không cắt mất.

## Màu

| Token | Hex | Dùng cho |
| --- | --- | --- |
| bg | #F5F2EB | nền kem + lưới ô 54px màu #E6E2D8 |
| ink | #0F3B2E | chữ chính, viền tag, trục |
| orange | #E8742A | số/cụm nhấn, ô "#N", ngày lỗ, series "xấu" |
| green | #23A05F | số/series "tốt" |
| pill | #DCE8E0 | nền pill phụ |
| muted | #4A5A52 | trục/chú thích phụ |

Quy ước: cam = rủi ro/điểm gây sốc, xanh lá = phương án tốt hơn. Một ảnh tối đa 2 màu nhấn.

## Font

Inter Display Black (tiêu đề, số lớn), Inter Display ExtraBold (tag, series, URL), Inter Bold/SemiBold (nhãn, pill, chân).
Đường dẫn mặc định `/usr/share/fonts/opentype/inter/`; thiếu thì code lùi về font sans-bold của brand.

## Nội dung: khối `thumb` trong `knowledge/models/<topic>.md` → `video_defaults`

```json
"thumb": {
  "tag": "Sortino ratio",
  "headline": [
    {"t": "CÙNG SHARPE [o]{sharpe_a}[/o]", "size": 110},
    {"t": "MỘT CÁI", "size": 190},
    {"t": "LÀM BẠN [o]MẤT NGỦ[/o]", "size": 120}
  ],
  "pill": "Sortino chỉ đếm ngày lỗ · code Python",
  "labels": [
    {"label": "A · Sortino", "value": "{sortino_a}", "color": "green"},
    {"label": "B · Sortino", "value": "{sortino_b}", "color": "orange"}
  ],
  "footer": "Dữ liệu mô phỏng • Không phải khuyến nghị"
}
```

- `[o]…[/o]` tô cam, `[g]…[/g]` tô xanh lá. `size` là cỡ tối đa; dòng dài tự co.
- `labels` tuỳ chọn; bỏ đi thì chart chiếm hết bề ngang.
- Chart: `CHARTS[topic]` trong `thumbnail.py` nếu có hàm riêng (vẽ trong suốt, màu bảng trên); không thì dùng `plot2d` của mô hình đổi màu trục. Thêm chủ đề mới thì nên viết hàm chart riêng gọn, ít chữ, không nhãn trục dày.
- Footer có thể đổi vế sau theo chủ đề (VD Monte Carlo: "Không phải dự báo giá").

## Cách viết tiêu đề

- Công thức hay dùng: **[con số/điều kiện] → [nghịch lý in to] → [hệ quả]**. VD: "LÃI 25,2% MỖI NĂM / VẪN THUA / CHIẾN LƯỢC LÃI 21,3%"; "KHÔNG THỂ NHÌN THẤY TƯƠNG LAI / NHƯNG CÓ THỂ NHÌN THẤY 1.000 TƯƠNG LAI".
- Tối đa ~12 từ toàn tiêu đề. Không hứa lợi nhuận, không "mua/bán", không cụm cấm trong `brand/compliance.md`.
- Thumbnail video hướng dẫn sản phẩm (ảnh `tutorial-a-z.jpg`) dùng cùng màu/khung nhưng thay chart bằng ảnh chụp giao diện có số bước 1-2-3; tag "HƯỚNG DẪN"; chưa tự động hoá.

## Kiểm tra trước khi giao

Mở ảnh xem: dấu tiếng Việt không chạm dòng trên/dưới; không chữ nào chạm mép 64px; số trên ảnh khớp `values.json` của video; có "#N" đúng số tập.
