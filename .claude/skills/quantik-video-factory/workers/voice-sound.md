# Voice & Sound (code)

| File | Việc |
| --- | --- |
| `pipeline/voiceover.py` | TTS: edge-tts (vi-VN-HoaiMyNeural / NamMinhNeural) → gTTS → espeak-ng → không giọng; `brand/pronunciation.json` |
| `pipeline/assemble.py` | ghép giọng từng cảnh + nhạc nền (pad tự tạo hoặc file có giấy phép) → `final.mp4` |

Engine thực tế ghi trong `qa_report.md` — báo người dùng nếu không có giọng. Sau proxy kiểm tra TLS, `voiceover.py`
nạp thêm CA từ `SSL_CERT_FILE` và đi qua `HTTPS_PROXY` cho edge-tts (đã sửa và kiểm tra trong lần nâng cấp này). edge-tts lỗi tạm thời khoảng 1/5 lần gọi → mỗi cảnh thử lại tối đa 5 lần; cảnh vẫn không có giọng thì `batch.py` đánh KHÔNG ĐẠT.
Thuật ngữ mới hay đọc sai (tên người nước ngoài, "disposition", "Kelly") thêm vào `brand/pronunciation.json`.
