# Video hướng dẫn sản phẩm (product tutorial)

Dùng khi người dùng muốn video **hướng dẫn dùng QuanTik** (tạo tài khoản → Quét toàn sàn → Phân tích Quant…),
không phải video giải thích một mô hình. Pipeline `pipeline/batch.py` KHÔNG làm được việc này: nó dựng cảnh
từ code mô hình, còn video hướng dẫn cần **giao diện thật** của web.

Kết quả mẫu (11/2026): 1080×1920, 2:28, 20 beat, giọng HoaiMy, phụ đề, CTA đọc nguyên văn của người dùng.

## Chạy

```bash
bash run.sh /đường/dẫn/thư-mục-làm-việc            # tự clone QuanTik---Design vào đó
bash run.sh ~/work ~/code/QuanTik---Design         # dùng clone sẵn có
```

Ra `out/final.mp4`, `out/subtitles.srt`. Sao chép vào `social-output/<id>/` cùng `captions.md`, `script.md`,
`thumbnail.jpg` (lấy khung giây 2.5: `ffmpeg -ss 2.5 -i final.mp4 -frames:v 1 thumbnail.jpg`).

Muốn đổi lời, thứ tự cảnh hoặc ảnh: sửa `beats.py` (hoặc chép ra file khác, chạy với `BEATS_FILE=...`).
Xoá `vo/NN.mp3` của beat đã đổi lời. `vo.py` bỏ qua file đã có. Xem nhanh vài khung trước khi dựng
toàn bộ (mất khoảng 4 phút):

```bash
python3 render.py 1 1.0 30 60 90     # chỉ ghi out/f_<giây>.png, không ra video
```

## Kiến trúc: vì sao làm thế này

| Màn | Nguồn ảnh | Lý do |
| --- | --- | --- |
| Đăng nhập, Gói | **site thật** quantik.io.vn (`capture/zz-video-real.spec.ts`) | trang công khai |
| Quét toàn sàn, Phân tích Quant | **giao diện production chạy local** + API giả (`capture/zz-video-local.spec.ts`) | phải đăng nhập; không dùng tài khoản người dùng |

- Web production là repo **`kwuangyong/QuanTik---Design`** (Next.js, `frontend/`). Repo `QuanTik-website` là bản
  React/Vite cũ, không có đăng nhập/gói, nên **không dùng**.
- Build rồi `next start` với `QUANTIK_API_URL=http://127.0.0.1:9` (cổng chết). Playwright chặn `**/api/v1/**`
  và trả JSON. Fixture có sẵn trong repo: `tests/fixtures/analysis.ts` (`analysisFixture`: đăng nhập, quota, job,
  báo cáo) và `tests/fixtures/quant-report-sample.ts` (`quantReportSample("complete")`: đủ 16 module). Vì vậy spec
  phải được **chép vào `frontend/tests/`** để import tương đối được (run.sh làm việc này rồi xoá đi).
- Viewport điện thoại 430×932, `deviceScaleFactor: 2` → ảnh 860×1864, chữ đủ nét khi phóng lên khung 1080.
- `boxes.json` lưu toạ độ (CSS px) của nút cần "chạm", để `render.py` vẽ khung cam và vòng gợn đúng chỗ.

## Quy tắc nội dung (bắt buộc)

- **Mã cổ phiếu bịa**: QTA…QTE (top 5), QTV…QTZ (nên tránh). Dùng mã thật trong bảng "tốt nhất/nên tránh"
  = khuyến nghị trá hình. Góc panel luôn có nhãn "Giao diện thật · dữ liệu minh hoạ".
- Không quay lâu hay đọc về các cột/khối **Entry, SL, TP, Khuyến nghị, Kế hoạch vị thế**. Không nói "điểm mua",
  "giá mục tiêu"… Chạy kiểm cụm cấm trước khi dựng:
  ```bash
  python3 check_beats.py      # run.sh cũng tự chạy bước này
  ```
- Nhắc giá/gói: mở `https://quantik.io.vn/plans` trước. Lần dựng 12/11/2026: thanh toán **tạm đóng**, chỉ có
  Free 30 ngày · 5 yêu cầu/ngày → không nhắc giá Pro.
- CTA của người dùng: đọc **nguyên văn**. Thẻ cuối luôn có câu miễn trừ.
- Người dùng (chủ QuanTik) đã nói: **trọng tâm là Quét toàn sàn và Phân tích Quant**. Dashboard không cần,
  bước đăng ký chỉ lướt nhanh.

## Bẫy đã gặp (đọc trước khi sửa spec)

1. **Nút "Gửi yêu cầu Quant" bị disabled** khi mã không có trong `analyses/options.symbols`. Fixture gốc chỉ có
   FPT/HPG/VNM, nên spec route lại `**/api/v1/analyses/options**` để thêm QTA. Route khai báo sau thắng route trước.
2. **Đừng đóng modal screening trước khi bấm link "Phân tích Quant"** trong modal: link biến mất, test treo đến
   timeout. Đặt `actionTimeout: 8000` để lỗi lộ ra nhanh thay vì chờ 3 phút.
3. Bảng screening hiện toàn "—" nếu item thiếu trường sheet. Phải điền đủ khoá trong
   `src/content/screening-sheet.ts` (`action`, `score`, `sharpe`, `hmm_regime`, `trade_model_agreement_pct`…).
4. Chart trong báo cáo chỉ có 3 điểm nếu dùng fixture nguyên bản. Spec sinh chuỗi giá 252 phiên (random walk có
   seed) cho `_price_close`, `research.regime`, `research.drawdown`. Giữ horizon 3 phiên như fixture để các
   nhãn khớp nhau.
5. `next build` lần đầu có thể thoát với gợi ý nâng cấp: chạy lại là qua. Đừng chạy lệnh nâng cấp mà nó gợi ý
   (repo nguồn chỉ đọc).
6. **edge-tts không theo `HTTPS_PROXY`** và không tin CA của proxy. `tts.py` truyền `proxy=` và nạp CA bundle.
   Nếu "No audio was received" thì cứ thử lại; `vo.py` tự thử 4 lần và giữ file đã có.
7. Toạ độ cắt ảnh: panel cao 990 px ứng với **443 px CSS** của ảnh. Giá trị `top_css` lớn nhất =
   (1864 − 887)/2 ≈ **488**. Nút chạm phải nằm trong `[top_css, top_css+443]`, không thì khung cam rơi ra ngoài.
8. 3D trong báo cáo: lấy góc GARCH (`m04_rot*`, tự xoay). Ảnh 3D hồ sơ nhân tố (`f3d*`) bị cắt trên mobile, nên
   dùng `fradar` thay.
9. Sandbox cloud: cần mở mạng tới `quantik.io.vn`, `speech.platform.bing.com` (và `trading.agr.vn` nếu quay
   Dashboard). Chromium có sẵn tại `/opt/pw-browsers/chromium`; đừng `playwright install`.

## Kiểm tra trước khi giao

- Trích 6–10 khung rải đều (`render.py 1 <giây>...`) và tự xem: khung chạm đúng nút, phụ đề không đè nội dung
  quan trọng, không lộ mã thật, không có Entry/SL/TP to rõ.
- `ffmpeg -i out/final.mp4 -af volumedetect -vn -f null -`: mean khoảng −15 dB là ổn.
- Báo người dùng: thời lượng, phần nào là dữ liệu minh hoạ, chỗ lệch giữa ảnh và lời (ví dụ ảnh hiện quota 20/ngày
  trong khi lời nói gói Free 5/ngày), và caption từng nền tảng trong khối copy được.
