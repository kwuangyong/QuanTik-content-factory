#!/usr/bin/env bash
# Dựng video hướng dẫn sản phẩm QuanTik từ đầu đến cuối.
# Dùng: bash run.sh <thư-mục-làm-việc> [đường-dẫn-QuanTik---Design]
# Cần: Node 20.9+, Python 3.10+ (pillow, edge-tts), ffmpeg, Chromium cho Playwright, Internet tới
#      quantik.io.vn và speech.platform.bing.com.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mkdir -p "${1:?thiếu thư mục làm việc}" && cd "$1" && pwd)"
DESIGN="${2:-$WORK/QuanTik---Design}"
PORT="${LOCAL_PORT:-3210}"
export CAP_DIR="$WORK/cap" LOCAL_BASE="http://127.0.0.1:$PORT"
mkdir -p "$CAP_DIR"

# 1. Lấy và build frontend production (chỉ đọc, không sửa repo nguồn).
if [ ! -d "$DESIGN/.git" ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/kwuangyong/QuanTik---Design "$DESIGN"
fi
cd "$DESIGN"
[ -d node_modules ] || npm ci
cd frontend
# `next build` đôi khi dừng lần đầu để in gợi ý nâng cấp: chạy lại là qua.
[ -f .next/BUILD_ID ] || NEXT_TELEMETRY_DISABLED=1 CI=1 npx next build --webpack || NEXT_TELEMETRY_DISABLED=1 CI=1 npx next build --webpack

# 2. Chạy server local. API thật trỏ vào cổng chết: mọi /api/v1 do Playwright giả lập.
if ! curl -s -o /dev/null "$LOCAL_BASE/screener"; then
  QUANTIK_API_URL=http://127.0.0.1:9 QUANTIK_APP_ORIGIN="$LOCAL_BASE" QUANTIK_UPSTREAM_ORIGIN="$LOCAL_BASE" \
    NEXT_TELEMETRY_DISABLED=1 setsid nohup npx next start -H 127.0.0.1 -p "$PORT" > "$WORK/next.log" 2>&1 &
  for _ in $(seq 1 40); do curl -s -o /dev/null "$LOCAL_BASE/screener" && break; sleep 1; done
fi

# 3. Quay màn hình (spec phải nằm trong frontend/tests để import được fixture của repo).
cp "$HERE"/capture/zz-video-*.spec.ts tests/
cp "$HERE"/capture/video.config.ts .
npx playwright test -c video.config.ts zz-video-real zz-video-local
rm -f tests/zz-video-*.spec.ts video.config.ts
cd "$CAP_DIR"
python3 -c "from PIL import Image; im=Image.open('r_plans.png'); im.crop((0,0,860,1864)).save('v_plans1.png')"

# 4. Giọng đọc → khung hình → ghép tiếng.
cd "$WORK"
ln -sfn "$CAP_DIR" cap
python3 "$HERE/check_beats.py"
python3 "$HERE/vo.py"
python3 "$HERE/render.py" 1
python3 "$HERE/mux.py"
echo "Xong: $WORK/out/final.mp4  (phụ đề: out/subtitles.srt)"
