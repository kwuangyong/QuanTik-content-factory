# dark-story

Video "dark truth" không mặt người thật, kể chuyện xã hội bằng **nhân vật hoạt hoạ phẳng** vẽ bằng code
(`pipeline/figures.py`): người đi làm cúi đầu, feed điện thoại, người khoe xe/nhà, tiền lương chảy vào đồ hiệu,
chạy trong bánh xe, đám đông, bước ra cửa sáng. Màu tối lạnh, viền tối nặng, film grain, một màu đỏ cảnh báo.
**Không chart, không code trên màn hình.**

**Hợp với:** chủ đề tâm lý tiền bạc / áp lực xã hội (lifestyle creep, so sánh trên mạng, vòng 9-5). Tiếng Anh hoặc Việt.

| Trường | Ý nghĩa |
| --- | --- |
| `scenes[]` | mỗi cảnh: `kind` (office, commute, scroll, compare, spend, wheel, crowd, walkaway, alone), `say` (lời đọc), `show` (dòng chữ to trên đầu khung), tuỳ chọn `note`, `min_dur` |
| `crowd` | đám đông `n_paths` người tí hon, chỉ `esc_a_n` người sáng lên và bay đi (lấy từ `values` của mô hình) |
| `cta` | thẻ cuối (theo dõi kênh) |
| `cover_scene` | chỉ số cảnh dùng làm `cover-frame.jpg` |

**Viết lời:** 8–10 cảnh, mỗi cảnh 1–2 câu ngắn, giọng nam trầm (`--voice male`, có thể `QT_RATE=-6%`).
Số vẫn đi qua `{key}` và chỉ nên xuất hiện ở cảnh `crowd` (kèm `note` ghi giả định mô phỏng).
Thêm `kind` mới: viết hàm `art_<kind>(a, t, p, ctx)` trong `template.py` và đăng ký trong `ART`.

**Dựng:** `python make.py <tập>` (look `dark-truth` lo giọng, nhạc, thumbnail). Một tập có thể kèm phiên bản
`chart-story` trong khối `variants` của cùng file JSON.
