import json, math, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import importlib.util as _iu, os as _o
_bf = _o.environ.get("BEATS_FILE") or _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "beats.py")
_sp = _iu.spec_from_file_location("beats", _bf); _bm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_bm); BEATS = _bm.BEATS
W, H, FPS = 1080, 1920, 30
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
CAP = "cap/"
BG, SURF, BORDER, TXT, MUTED, ACC, POS, NEU = "#080d0b", "#0d1913", "#294337", "#edf4ef", "#a6b9ad", "#ff914d", "#67d6a5", "#e3c16c"
import glob as _glob, os as _os
_FONT_DIRS = [_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "brand", "assets", "fonts"),
              "/usr/share/fonts", "/usr/local/share/fonts", _os.path.expanduser("~/.fonts"), "/Library/Fonts", "C:/Windows/Fonts"]
def _find(names):
    for d in _FONT_DIRS:
        for n in names:
            hit = _glob.glob(_os.path.join(d, "**", n), recursive=True)
            if hit: return hit[0]
    raise SystemExit(f"Thiếu font {names[0]}: cài Inter + JetBrains Mono hoặc thả file vào brand/assets/fonts/")
_fc = {}
def F(w, s):   # Inter (đủ dấu tiếng Việt); w = Regular/Medium/SemiBold/Bold/ExtraBold
    k = ("F", w)
    if k not in _fc: _fc[k] = _find([f"Inter-{w}.otf", f"Inter-{w}.ttf", "Inter.ttf", "Inter*.ttf"])
    return ImageFont.truetype(_fc[k], s)
def M(s):
    if "M" not in _fc: _fc["M"] = _find(["JetBrainsMono-Bold.ttf", "IBMPlexMono-Bold.ttf", "JetBrainsMono*.ttf"])
    return ImageFont.truetype(_fc["M"], s)
boxes = json.load(open(CAP + "boxes.json"))
durs = json.load(open("vo/durs.json"))
import os
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = Image.open(os.path.join(HERE, "..", "brand", "assets", "logo.jpg")).convert("RGB")
PX, PY, PW, PH = 60, 330, 960, 990          # screenshot panel
K = PW / 860                                 # screenshot px -> frame px
DISC = "Nội dung giáo dục, không phải khuyến nghị mua bán chứng khoán. Dữ liệu trên màn hình Quét sàn & Quant là minh hoạ."

def bg():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line([(x, 0), (x, H)], fill="#0c1410")
    for y in range(0, H, 60): d.line([(0, y), (W, y)], fill="#0c1410")
    return im
BASE = bg()

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        words, line = para.split(), ""
        for w in words:
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def chunks(text):
    # split narration into subtitle chunks of <= ~8 words, at punctuation when possible
    parts, cur = [], []
    for w in text.split():
        cur.append(w)
        if (w[-1] in ".,:?!" and len(cur) >= 4) or len(cur) >= 9: parts.append(" ".join(cur)); cur = []
    if cur: parts.append(" ".join(cur))
    return parts

cache = {}
def load(name):
    if name not in cache: cache[name] = Image.open(CAP + name + ".png").convert("RGB")
    return cache[name]

def ease(t): return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def panel(frame, name, top_css, t, tap, beat_t):
    if name.startswith("SEQ:"):
        pre = name[4:]; k = int(t * 6 * 1.2) % 6
        src = load(f"{pre}{k}")
    else:
        src = load(name)
    win = int(PH / K)                         # source px visible
    top = int(top_css * 2); top = max(0, min(src.height - win, top))
    # gentle Ken Burns: drift 40 src px
    drift = int(40 * ease(t)) if not tap else 0
    top = max(0, min(src.height - win, top + drift))
    crop = src.crop((0, top, 860, top + win)).resize((PW, PH), Image.LANCZOS)
    mask = Image.new("L", (PW, PH), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, PW - 1, PH - 1], 28, fill=255)
    # shadow + border
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([PX - 4, PY - 4, PX + PW + 3, PY + PH + 3], 32, outline=BORDER, width=4)
    frame.paste(crop, (PX, PY), mask)
    if tap:
        if isinstance(tap, str):
            s, k2 = tap.split("."); bx = boxes[s][k2]; x, y, w, h = bx["x"], bx["y"], bx["width"], bx["height"]
        else: x, y, w, h = tap
        cx = PX + (x + w / 2) * 2 * K; cy = PY + ((y + h / 2) * 2 - top) * K
        hw, hh = w * K + 24, h * K + 24
        d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], 18, outline=ACC, width=6)
        p = (t * 1.6) % 1.0
        if t > 0.35:
            r = 20 + 70 * p; a = int(255 * (1 - p))
            ov = Image.new("RGBA", (W, H)); od = ImageDraw.Draw(ov)
            od.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 145, 77, a), width=8)
            od.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 255, 255, 170))
            frame.paste(ov, (0, 0), ov)

def header(frame, step, title):
    d = ImageDraw.Draw(frame)
    frame.paste(LOGO.resize((72, 72)), (60, 175)); d.text((146, 186), "QuanTik", font=F("Bold", 40), fill=TXT)
    d.text((146 + d.textlength("QuanTik", font=F("Bold", 40)) - 0, 186), "", font=F("Bold", 40))
    if step:
        f = M(28); tw = d.textlength(step, font=f)
        d.rounded_rectangle([940 - tw - 36, 186, 940, 236], 25, fill=ACC); d.text((940 - tw - 18, 192), step, font=f, fill="#1a0d05")
    if title:
        d.text((60, 258), title, font=F("Bold", 50), fill=TXT)

def subtitle(frame, text):
    d = ImageDraw.Draw(frame); f = F("Bold", 42)
    lines = wrap(d, text, f, 880)[:2]
    y0 = 1500 - 62 * len(lines) - 20
    hl = 62 * len(lines) + 28
    ov = Image.new("RGBA", (W, H)); ImageDraw.Draw(ov).rounded_rectangle([50, y0 - 14, 1030, y0 - 14 + hl], 22, fill=(8, 13, 11, 225))
    frame.paste(ov, (0, 0), ov)
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f); d.text(((W - tw) / 2, y0 + i * 62), l, font=f, fill=TXT)

def intro(frame, t):
    d = ImageDraw.Draw(frame)
    lg = LOGO.resize((220, 220)); frame.paste(lg, ((W - 220) // 2, 330))
    f = F("ExtraBold", 92)
    for i, l in enumerate(["Dùng QuanTik", "từ A đến Z"]):
        tw = d.textlength(l, font=f); d.text(((W - tw) / 2, 620 + i * 112), l, font=f, fill=ACC if i else TXT)
    steps = [("01", "Tạo tài khoản"), ("02", "Quét toàn sàn · Top 5 / Tránh 5"), ("03", "Phân tích Quant · 16 module")]
    for i, (n, s) in enumerate(steps):
        a = ease((t * 3) - i * 0.5)
        if a <= 0: continue
        y = 900 + i * 110 + int(30 * (1 - a))
        d.rounded_rectangle([110, y, 970, y + 86], 18, fill=SURF, outline=BORDER, width=3)
        d.text((140, y + 18), n, font=M(40), fill=ACC); d.text((220, y + 20), s, font=F("SemiBold", 40), fill=TXT)

def cta(frame, t):
    d = ImageDraw.Draw(frame)
    lg = LOGO.resize((200, 200)); frame.paste(lg, ((W - 200) // 2, 260))
    f = F("ExtraBold", 66)
    for i, l in enumerate(wrap(d, "Đăng ký & theo dõi", f, 900)):
        tw = d.textlength(l, font=f); d.text(((W - tw) / 2, 500 + i * 80), l, font=f, fill=ACC)
    f2 = F("SemiBold", 42)
    for i, l in enumerate(wrap(d, "Video kiến thức quant finance mỗi ngày: cách dùng hiệu quả từng module QuanTik.", f2, 860)):
        tw = d.textlength(l, font=f2); d.text(((W - tw) / 2, 620 + i * 58), l, font=f2, fill=TXT)
    p = 1 + 0.04 * math.sin(t * 12)
    bw, bh = int(560 * p), int(110 * p)
    d.rounded_rectangle([(W - bw) / 2, 860, (W + bw) / 2, 860 + bh], 55, fill=ACC)
    f3 = F("Bold", int(46 * p)); s = "quantik.io.vn"; tw = d.textlength(s, font=f3); d.text(((W - tw) / 2, 860 + bh / 2 - 30 * p), s, font=f3, fill="#1a0d05")
    f4 = F("Regular", 26)
    for i, l in enumerate(wrap(d, DISC, f4, 860)):
        tw = d.textlength(l, font=f4); d.text(((W - tw) / 2, 1040 + i * 36), l, font=f4, fill=MUTED)

def label(frame):
    d = ImageDraw.Draw(frame); f = F("Medium", 24); s = "Giao diện thật · dữ liệu minh hoạ"
    tw = d.textlength(s, font=f); d.rounded_rectangle([PX + PW - tw - 40, PY + PH - 56, PX + PW - 12, PY + PH - 14], 14, fill=(8, 13, 11)); d.text((PX + PW - tw - 26, PY + PH - 50), s, font=f, fill=NEU)

import os as _os2; _os2.makedirs("out", exist_ok=True)
PAD = 0.35
timeline, srt, t0 = [], [], 0.0
for i, b in enumerate(BEATS):
    dur = durs[i] + PAD + (1.2 if i == len(BEATS) - 1 else 0)
    timeline.append((t0, dur, i)); 
    cs = chunks(b[2]); tot = sum(len(c) for c in cs); acc = 0
    for c in cs:
        s = t0 + durs[i] * acc / tot; acc += len(c); e = t0 + durs[i] * acc / tot
        srt.append((s, e, c))
    t0 += dur
TOTAL = t0
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
open("out/subtitles.srt", "w").write("\n".join(f"{k+1}\n{ts(s)} --> {ts(e)}\n{c}\n" for k, (s, e, c) in enumerate(srt)))
json.dump({"timeline": timeline, "total": TOTAL}, open("out/timeline.json", "w"))

ow, oh = int(W * SCALE), int(H * SCALE)
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{ow}x{oh}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "out/video.mp4"], stdin=subprocess.PIPE)
N = int(TOTAL * FPS)
only = sys.argv[2:] and [float(x) for x in sys.argv[2:]]
for fi in range(N):
    t = fi / FPS
    if only and not any(abs(t - x) < 0.5 / FPS for x in only): continue
    st, dur, i = next(x for x in timeline if x[0] <= t < x[0] + x[1]) if t < TOTAL else timeline[-1]
    step, title, nar, shots = BEATS[i]; lt = t - st
    fr = BASE.copy()
    kind = shots[0][0]
    if kind == "intro": intro(fr, lt)
    elif kind == "cta": cta(fr, lt)
    else:
        header(fr, step, title)
        sd = dur / len(shots); k = min(len(shots) - 1, int(lt // sd)); name, top, tap = shots[k]
        panel(fr, name, top, (lt - k * sd) / sd, tap, lt)
        label(fr)
    sub = next((c for s, e, c in srt if s <= t < e + 0.15), None)
    if sub and kind != "cta": subtitle(fr, sub)
    # fade in/out per beat
    a = min(1, lt / 0.18)
    if a < 1: fr = Image.blend(BASE, fr, a)
    if only: fr.save(f"out/f_{t:.1f}.png"); continue
    if SCALE != 1: fr = fr.resize((ow, oh), Image.BILINEAR)
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait(); print("total", TOTAL)
