"""Hình minh hoạ tự vẽ, có chuyển động (hoạt hoạ sự vật, hiện tượng, con người) + ảnh thật B-roll.

Mỗi tag trong knowledge/visuals.json có một hàm draw_<tag>(d, w, h, p, t) vẽ lên canvas RGBA w×h.
  p = tiến độ cảnh 0..1, t = giây trong cảnh (cho chuyển động lặp: nhấp nháy, sóng, lắc).
Nguyên tắc: hình phải khớp lời, và MỌI chi tiết trong hình phải đúng logic (số đếm bài tính từ đúng các lá
đang lật, đồng hồ chỉ đúng giờ được nói, mũi tên/màu đúng chiều). Không vẽ số trang trí vô nghĩa. pick(text) chọn tag theo từ khoá; 'code' chỉ khi lời nói về code/Python.

  frame(tag, w, h, p, t, photo=None) → ảnh RGBA (ảnh thật nếu có ảnh B-roll của tag, không thì hình vẽ)
  pick(text) → tag | None
"""
from __future__ import annotations

import json
import math
import random
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from core import KNOWLEDGE, THEME as T, font

# ---------------------------------------------------------------- palette (flat cartoon, brand-tinted)
SKIN = [(241, 194, 153), (224, 172, 128), (198, 140, 98), (250, 214, 178)]
HAIR = [(40, 30, 25), (70, 50, 35), (25, 25, 30), (200, 200, 205)]
SHIRT = [(70, 120, 200), (200, 80, 80), (90, 170, 120), (230, 170, 60), (140, 100, 190)]
FELT, FELT_D = (22, 110, 70), (14, 78, 50)
WOOD = (120, 72, 40)
SEA, SEA_D = (30, 90, 140), (14, 50, 90)
SKY_N = (20, 28, 48)
WHITE = (245, 245, 240)
RED, GREEN, GOLD = T["negative"], T["positive"], T["neutral"]


@lru_cache(maxsize=1)
def tags():
    return json.loads((KNOWLEDGE / "visuals.json").read_text(encoding="utf-8"))["tags"]


def pick(text: str | None, exclude=()) -> str | None:
    """Tag khớp nhất với câu (đếm từ khoá, ưu tiên cụm dài). None nếu không có hình nào hợp."""
    if not text:
        return None
    low = text.lower()
    best, score = None, 0
    for tag, spec in tags().items():
        if tag in exclude:
            continue
        s = sum(len(k) for k in spec["kw"] if k in low)
        if s > score:
            best, score = tag, s
    return best


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def lerp(a, b, k):
    return a + (b - a) * k


def mix(c1, c2, k):
    return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))


# ---------------------------------------------------------------- characters
def person(d, x, y, s=1.0, shirt=None, skin=None, hair=None, face="neutral", glasses=False, arm=(0.0, 0.0),
           bow=False, sweat=0.0, seed=0, legs=True, lean=0.0):
    """Nhân vật phẳng: (x, y) = chân. s = tỉ lệ (1.0 ≈ cao 300px). arm = góc tay trái/phải (rad, 0 = buông)."""
    r = random.Random(seed)
    shirt = shirt or SHIRT[r.randrange(len(SHIRT))]
    skin = skin or SKIN[r.randrange(len(SKIN))]
    hair = hair or HAIR[r.randrange(len(HAIR))]
    hx = x + lean * 40 * s
    body_top, body_bot = y - 200 * s, y - 90 * s
    if legs:
        for dx in (-22, 22):
            d.rounded_rectangle([x + dx * s - 12 * s, body_bot - 6 * s, x + dx * s + 12 * s, y], radius=int(10 * s),
                                fill=(40, 45, 60))
            d.ellipse([x + dx * s - 18 * s, y - 10 * s, x + dx * s + 18 * s, y + 6 * s], fill=(25, 25, 30))
    d.rounded_rectangle([hx - 50 * s, body_top, hx + 50 * s, body_bot + 10 * s], radius=int(34 * s), fill=shirt)
    if bow:
        d.polygon([(hx, body_top + 14 * s), (hx - 20 * s, body_top + 4 * s), (hx - 20 * s, body_top + 26 * s)], fill=(20, 20, 20))
        d.polygon([(hx, body_top + 14 * s), (hx + 20 * s, body_top + 4 * s), (hx + 20 * s, body_top + 26 * s)], fill=(20, 20, 20))
    for side, ang in ((-1, arm[0]), (1, arm[1])):
        sx, sy = hx + side * 46 * s, body_top + 24 * s
        ex = sx + side * math.sin(abs(ang)) * 90 * s * (1 if ang >= 0 else 1)
        ey = sy + math.cos(ang) * 90 * s
        d.line([(sx, sy), (ex, ey)], fill=shirt, width=int(24 * s))
        d.ellipse([ex - 13 * s, ey - 13 * s, ex + 13 * s, ey + 13 * s], fill=skin)
    # head
    cx, cy, hr = hx, body_top - 52 * s, 50 * s
    d.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=skin)
    d.chord([cx - hr - 2, cy - hr - 6 * s, cx + hr + 2, cy + hr * 0.5], 180, 360, fill=hair)
    ey_ = cy + 4 * s
    for ex in (cx - 18 * s, cx + 18 * s):
        if face == "shock":
            d.ellipse([ex - 9 * s, ey_ - 11 * s, ex + 9 * s, ey_ + 11 * s], fill=WHITE)
            d.ellipse([ex - 4 * s, ey_ - 4 * s, ex + 4 * s, ey_ + 4 * s], fill=(20, 20, 20))
        elif face == "sly":
            d.line([(ex - 9 * s, ey_), (ex + 9 * s, ey_ - 3 * s)], fill=(20, 20, 20), width=int(5 * s))
        else:
            d.ellipse([ex - 6 * s, ey_ - 6 * s, ex + 6 * s, ey_ + 6 * s], fill=(20, 20, 20))
    if glasses:
        for ex in (cx - 18 * s, cx + 18 * s):
            d.ellipse([ex - 16 * s, ey_ - 14 * s, ex + 16 * s, ey_ + 14 * s], outline=(30, 30, 30), width=int(4 * s))
        d.line([(cx - 2 * s, ey_), (cx + 2 * s, ey_)], fill=(30, 30, 30), width=int(4 * s))
    my = cy + 28 * s
    if face == "shock":
        d.ellipse([cx - 11 * s, my - 6 * s, cx + 11 * s, my + 16 * s], fill=(90, 30, 30))
    elif face in ("happy", "sly"):
        d.arc([cx - 18 * s, my - 14 * s, cx + 18 * s, my + 8 * s], 20, 160, fill=(90, 30, 30), width=int(5 * s))
    elif face == "sad":
        d.arc([cx - 16 * s, my, cx + 16 * s, my + 20 * s], 200, 340, fill=(90, 30, 30), width=int(5 * s))
    else:
        d.line([(cx - 12 * s, my + 2 * s), (cx + 12 * s, my + 2 * s)], fill=(90, 30, 30), width=int(5 * s))
    if sweat > 0:
        sx, sy = cx + hr * 0.9, cy - hr * 0.3 + sweat * 30 * s
        d.ellipse([sx - 7 * s, sy - 4 * s, sx + 7 * s, sy + 14 * s], fill=(140, 200, 255))
        d.polygon([(sx - 6 * s, sy + 2 * s), (sx + 6 * s, sy + 2 * s), (sx, sy - 14 * s)], fill=(140, 200, 255))
    return cx, cy


def card(d, x, y, rank, suit, s=1.0, face_up=True, rot=0):
    w, h = 90 * s, 128 * s
    if not face_up:
        d.rounded_rectangle([x, y, x + w, y + h], radius=int(10 * s), fill=(160, 40, 50), outline=WHITE, width=3)
        d.rounded_rectangle([x + 10 * s, y + 10 * s, x + w - 10 * s, y + h - 10 * s], radius=int(6 * s),
                            outline=(230, 150, 150), width=2)
        return
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(10 * s), fill=WHITE, outline=(180, 180, 180), width=2)
    col = (200, 30, 40) if suit in "♥♦" else (20, 20, 20)
    d.text((x + 10 * s, y + 6 * s), rank, font=font("sans-black", int(34 * s)), fill=col)
    d.text((x + w / 2 - 18 * s, y + h / 2 - 12 * s), suit, font=font("sans-bold", int(44 * s)), fill=col)


def chip_stack(d, x, y, n, color, s=1.0):
    for i in range(n):
        yy = y - i * 9 * s
        d.ellipse([x - 32 * s, yy - 12 * s, x + 32 * s, yy + 12 * s], fill=color, outline=WHITE, width=2)


def label(d, x, y, text, size=30, color=WHITE, bg=(0, 0, 0, 150), anchor="mm"):
    f = font("sans-black", size)
    tw = d.textlength(text, font=f)
    bx = x - tw / 2 if anchor == "mm" else x
    d.rounded_rectangle([bx - 16, y - size * 0.75, bx + tw + 16, y + size * 0.75], radius=int(size * 0.6), fill=bg)
    d.text((bx, y - size * 0.62), text, font=f, fill=color)


# ---------------------------------------------------------------- scenes
def draw_casino(d, w, h, p, t):
    # back wall + neon sign
    d.rectangle([0, 0, w, h], fill=(40, 16, 22))
    for i in range(0, w, 60):
        d.line([(i, 0), (i, h * 0.45)], fill=(52, 22, 30), width=2)
    flick = 1.0 if int(t * 7) % 9 else 0.4
    f = font("sans-black", int(h * 0.085))
    txt = "BLACKJACK 21"
    tw = d.textlength(txt, font=f)
    neon = mix((40, 16, 22), (255, 80, 140), flick)
    d.text(((w - tw) / 2, h * 0.025), txt, font=f, fill=neon)
    # dealer behind table
    person(d, w * 0.5, h * 0.68, s=h / 700, shirt=(25, 25, 30), face="sly", bow=True, seed=3,
           arm=(0.4 + 0.3 * math.sin(t * 6), -0.6), legs=False)
    # table
    d.ellipse([-w * 0.25, h * 0.48, w * 1.25, h * 1.5], fill=WOOD)
    d.ellipse([-w * 0.2, h * 0.52, w * 1.2, h * 1.5], fill=FELT)
    d.arc([w * 0.1, h * 0.62, w * 0.9, h * 1.2], 200, 340, fill=GOLD, width=3)
    # dealt cards fly from dealer to player spots
    # Bài nhỏ ra trước → bộ bài còn lại nhiều lá lớn → người đếm bài có lợi thế. Số đếm Hi-Lo TÍNH từ đúng các lá
    # đã lật (2–6: +1, 7–9: 0, 10/J/Q/K/A: −1), không gõ tay: chi tiết trong hình cũng phải đúng logic.
    hands = [("5", "♠"), ("3", "♥"), ("6", "♦"), ("2", "♣")]
    spots = [(w * 0.18, h * 0.72), (w * 0.3, h * 0.74), (w * 0.62, h * 0.74), (w * 0.74, h * 0.72)]
    shown = []
    for i, ((r_, s_), (tx, ty)) in enumerate(zip(hands, spots)):
        k = ease((p - 0.08 * i) / 0.25)
        if k <= 0:
            continue
        x = lerp(w * 0.47, tx, k)
        y = lerp(h * 0.5, ty, k)
        card(d, x, y, r_, s_, s=h / 900, face_up=k > 0.7)
        if k > 0.7:
            shown.append(r_)
    # chips: the player's stack grows (the bet sizing)
    n = 2 + int(6 * ease((p - 0.3) / 0.5))
    chip_stack(d, w * 0.5, h * 0.92, n, (220, 60, 60), s=h / 800)
    chip_stack(d, w * 0.42, h * 0.95, max(1, n - 2), (40, 110, 220), s=h / 800)
    # the professor (glasses) in front, seen from behind-ish, counting cards
    person(d, w * 0.12, h * 1.08, s=h / 620, shirt=(150, 120, 90), face="happy", glasses=True, seed=7,
           arm=(0.2, -1.2 - 0.1 * math.sin(t * 4)), legs=False)
    cnt = hilo_count(shown)
    label(d, w * 0.12 + 110, h * 0.48, f"đếm Hi-Lo: {cnt:+d}" if shown else "đếm Hi-Lo: 0", size=int(h * 0.05),
          color=GREEN if cnt > 0 else (RED if cnt < 0 else GOLD))


def hilo_count(ranks):
    """Đếm bài Hi-Lo (Thorp/Braun): 2–6 = +1, 7–9 = 0, 10/J/Q/K/A = −1."""
    val = {"2": 1, "3": 1, "4": 1, "5": 1, "6": 1, "7": 0, "8": 0, "9": 0}
    return sum(val.get(r, -1) for r in ranks)


def draw_roulette(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(30, 14, 20))
    cx, cy, R = w / 2, h * 0.55, min(w, h) * 0.42
    d.ellipse([cx - R - 20, cy - R - 20, cx + R + 20, cy + R + 20], fill=WOOD)
    ang0 = t * 2.4
    n = 18
    for i in range(n):
        a0 = ang0 + i * 2 * math.pi / n
        a1 = a0 + 2 * math.pi / n
        col = (200, 30, 40) if i % 2 else (20, 20, 20)
        if i == 0:
            col = (20, 140, 70)
        d.pieslice([cx - R, cy - R, cx + R, cy + R], math.degrees(a0), math.degrees(a1), fill=col, outline=GOLD)
    d.ellipse([cx - R * 0.35, cy - R * 0.35, cx + R * 0.35, cy + R * 0.35], fill=(150, 100, 40), outline=GOLD, width=4)
    for i in range(4):
        a = ang0 * 1.5 + i * math.pi / 2
        d.line([(cx, cy), (cx + math.cos(a) * R * 0.3, cy + math.sin(a) * R * 0.3)], fill=GOLD, width=8)
    ba = -t * 5.5
    br = R * (0.92 - 0.25 * ease(p))
    bx, by = cx + math.cos(ba) * br, cy + math.sin(ba) * br
    d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=WHITE)


def draw_professor(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(48, 40, 34))
    bx0, by0, bx1, by1 = w * 0.06, h * 0.08, w * 0.94, h * 0.66
    d.rectangle([bx0 - 12, by0 - 12, bx1 + 12, by1 + 12], fill=WOOD)
    d.rectangle([bx0, by0, bx1, by1], fill=(30, 62, 48))
    # Bảng đen viết đúng công thức của chủ đề đang kể (episode "board" > theo topic); không có thì chỉ nét phấn,
    # vì công thức sai ngữ cảnh (Kelly trong chuyện HMM) là lỗi chi tiết người xem bắt được ngay.
    lines = CFG.get("board") or BOARD.get(CFG.get("topic"), [])
    f = font("mono-bold", int(h * 0.06))
    if not lines:  # nét phấn trừu tượng
        k = ease(p)
        for i in range(4):
            y = by0 + 50 + i * h * 0.13
            pts = [(bx0 + 30 + x, y + 10 * math.sin(x / 23 + i)) for x in range(0, int((bx1 - bx0 - 80) * k), 8)]
            if len(pts) > 1:
                d.line(pts, fill=(225, 235, 225), width=4)
        person(d, w * 0.82, h * 1.02, s=h / 640, shirt=(110, 90, 70), face="happy", glasses=True,
               hair=(200, 200, 205), seed=11, arm=(0.1, -2.3 + 0.15 * math.sin(t * 9)), legs=False)
        return
    shown = p * len(lines) * 1.3
    for i, ln in enumerate(lines):
        k = max(0.0, min(1.0, shown - i))
        if k <= 0:
            break
        d.text((bx0 + 30, by0 + 24 + i * h * 0.13), ln[: max(1, int(len(ln) * k))], font=f, fill=(225, 235, 225))
    i = min(len(lines) - 1, int(shown))
    k = max(0.0, min(1.0, shown - i))
    hand_x = bx0 + 30 + d.textlength(lines[i][: int(len(lines[i]) * k)], font=f)
    hand_y = by0 + 40 + i * h * 0.13
    person(d, min(w * 0.82, hand_x + 120), h * 1.02, s=h / 640, shirt=(110, 90, 70), face="happy", glasses=True,
           hair=(200, 200, 205), seed=11, arm=(0.1, -2.3 + 0.15 * math.sin(t * 9)), legs=False)
    d.ellipse([hand_x - 6, hand_y - 6, hand_x + 6, hand_y + 6], fill=WHITE)


def draw_storm(d, w, h, p, t):
    storm = ease((p - 0.25) / 0.45)
    sky = mix((90, 150, 200), (25, 30, 45), storm)
    d.rectangle([0, 0, w, h], fill=sky)
    if storm > 0.3:
        for i in range(5):
            cx = (i * 0.25 + 0.05 * math.sin(t + i)) * w
            d.ellipse([cx - 140, h * 0.02, cx + 160, h * 0.2], fill=mix(sky, (60, 62, 75), storm))
    else:
        d.ellipse([w * 0.72, h * 0.08, w * 0.86, h * 0.08 + w * 0.14], fill=(255, 220, 120))
    # lightning
    if storm > 0.6 and int(t * 5) % 7 == 0:
        x = w * (0.3 + 0.4 * ((int(t * 5) * 37) % 10) / 10)
        pts = [(x, h * 0.12)]
        for k in range(5):
            pts.append((pts[-1][0] + (25 if k % 2 else -30), pts[-1][1] + h * 0.07))
        d.line(pts, fill=(255, 250, 200), width=6)
        d.rectangle([0, 0, w, h], outline=(255, 255, 230), width=10)
    amp = lerp(6, h * 0.08, storm)
    base_y = h * 0.6
    for layer, col in enumerate([SEA, mix(SEA, SEA_D, 0.5), SEA_D]):
        pts = [(0, h)]
        for x in range(0, w + 20, 20):
            y = base_y + layer * h * 0.1 + amp * math.sin(x / (70 + layer * 20) + t * (2 + storm * 3) + layer)
            pts.append((x, y))
        pts.append((w, h))
        d.polygon(pts, fill=col)
        if layer == 0:
            bx = w * 0.45
            by = base_y + amp * math.sin(bx / 70 + t * (2 + storm * 3))
            tilt = 0.3 * storm * math.sin(t * 4)
            hull = [(bx - 70, by - 10), (bx + 70, by - 10 + 60 * tilt), (bx + 50, by + 25 + 60 * tilt), (bx - 50, by + 25)]
            d.polygon(hull, fill=(150, 60, 40))
            d.line([(bx, by - 10), (bx + 20 * tilt, by - 120)], fill=(60, 40, 30), width=6)
            d.polygon([(bx + 20 * tilt, by - 120), (bx + 20 * tilt, by - 30), (bx + 60, by - 40)], fill=WHITE)
    if storm > 0.2:
        rnd = random.Random(int(t * 12))
        for _ in range(int(80 * storm)):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.8)
            d.line([(x, y), (x - 8, y + 26)], fill=(180, 200, 230), width=2)
    label(d, w * 0.5, h * 0.93, "BIẾN ĐỘNG: " + ("YÊN" if storm < 0.3 else "BÃO"), size=int(h * 0.05),
          color=GREEN if storm < 0.3 else RED)


def draw_drunk_walk(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=SKY_N)
    d.rectangle([0, h * 0.7, w, h], fill=(40, 40, 50))
    for x in range(0, w, 120):
        d.rectangle([x + 20, h * 0.84, x + 80, h * 0.86], fill=(200, 190, 120))
    # lamp
    d.rectangle([w * 0.86, h * 0.18, w * 0.875, h * 0.72], fill=(70, 70, 80))
    d.ellipse([w * 0.83, h * 0.14, w * 0.9, h * 0.2], fill=(255, 225, 140))
    rnd = random.Random(5)
    steps = 40
    pts, y = [], h * 0.55
    for i in range(steps + 1):
        pts.append((w * 0.06 + i * w * 0.7 / steps, y))
        y += rnd.uniform(-1, 1) * h * 0.05
        y = min(max(y, h * 0.3), h * 0.68)
    k = max(1, int(steps * ease(p)))
    d.line(pts[: k + 1], fill=RED, width=5)
    x, y = pts[k]
    person(d, x, y + 10, s=h / 1000, shirt=(200, 80, 80), face="sly", seed=2, lean=0.35 * math.sin(t * 5),
           arm=(1.2, -1.0 + 0.3 * math.sin(t * 7)))
    # soldier: straight line = trend persistence
    sx = w * 0.06 + w * 0.7 * ease(p)
    d.line([(w * 0.06, h * 0.9), (sx, h * 0.9)], fill=GREEN, width=5)
    person(d, sx, h * 0.97, s=h / 1200, shirt=(70, 110, 70), face="neutral", seed=4,
           arm=(0.5 * math.sin(t * 8), -0.5 * math.sin(t * 8)))
    label(d, w * 0.22, h * 0.08, "ngẫu nhiên", size=int(h * 0.045), color=RED)
    label(d, w * 0.72, h * 0.08, "quán tính", size=int(h * 0.045), color=GREEN)


def draw_leash(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(120, 180, 220))
    d.rectangle([0, h * 0.68, w, h], fill=(90, 160, 90))
    d.ellipse([w * 0.08, h * 0.06, w * 0.2, h * 0.06 + w * 0.12], fill=(255, 225, 120))
    ox = w * 0.38
    hx, hy = person(d, ox, h * 0.9, s=h / 900, shirt=(70, 120, 200), face="neutral", seed=9, arm=(0.2, -1.1))
    # dog oscillates around the owner with damped amplitude (mean reversion)
    amp = w * 0.42 * math.exp(-2.2 * p)
    dx = ox + 40 + amp * math.sin(t * 3.2 + 0.5)
    dy = h * 0.86
    hand = (ox + 46 * h / 900 + math.sin(1.1) * 90 * h / 900, h * 0.9 - 176 * h / 900 + math.cos(-1.1) * 90 * h / 900)
    sag = 30 + 50 * (1 - abs(dx - ox) / (w * 0.5))
    mid = ((hand[0] + dx) / 2, max(hand[1], dy - 40) + sag)
    d.line([hand, mid, (dx, dy - 40)], fill=RED, width=5, joint="curve")
    face = 1 if dx > ox else -1
    d.ellipse([dx - 60, dy - 60, dx + 60, dy], fill=(180, 120, 60))
    d.ellipse([dx + face * 45 - 32, dy - 100, dx + face * 45 + 32, dy - 40], fill=(180, 120, 60))
    d.ellipse([dx + face * 55 - 6, dy - 80, dx + face * 55 + 6, dy - 68], fill=(20, 20, 20))
    d.polygon([(dx + face * 30, dy - 96), (dx + face * 20, dy - 130), (dx + face * 50, dy - 100)], fill=(140, 90, 40))
    for lx in (-40, -15, 15, 40):
        d.rectangle([dx + lx - 6, dy - 10, dx + lx + 6, dy + 20 + 6 * math.sin(t * 15 + lx)], fill=(150, 100, 50))
    d.line([(ox, h * 0.95), (ox, h * 0.99)], fill=WHITE, width=3)
    label(d, ox, h * 0.08, "mức cân bằng", size=int(h * 0.045), color=GOLD)


def draw_weather(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(60, 50, 45))
    wx0, wy0, wx1, wy1 = w * 0.08, h * 0.08, w * 0.6, h * 0.62
    state = int(p * 3.0) % 3  # sunny → rain → storm, hidden behind a half-open curtain
    sky = [(130, 190, 240), (110, 120, 140), (50, 55, 70)][state]
    d.rectangle([wx0, wy0, wx1, wy1], fill=sky)
    if state == 0:
        d.ellipse([wx0 + 60, wy0 + 40, wx0 + 160, wy0 + 140], fill=(255, 220, 120))
    else:
        rnd = random.Random(int(t * 10))
        for _ in range(40 * state):
            x, y = rnd.uniform(wx0, wx1), rnd.uniform(wy0, wy1)
            d.line([(x, y), (x - 6, y + 20)], fill=(200, 210, 240), width=2)
    cur = lerp(0.85, 0.55, 0.5 + 0.5 * math.sin(t * 1.5))
    d.rectangle([wx0, wy0, wx0 + (wx1 - wx0) * cur, wy1], fill=(150, 60, 60))
    for i in range(6):
        x = wx0 + (wx1 - wx0) * cur * i / 6
        d.line([(x, wy0), (x, wy1)], fill=(120, 45, 45), width=3)
    d.rectangle([wx0 - 10, wy0 - 10, wx1 + 10, wy0], fill=WOOD)
    # someone walks in: carries an umbrella or not → the only thing we observe
    px = lerp(w * 1.1, w * 0.78, ease(p * 3 % 1 * 1.5))
    person(d, px, h * 0.98, s=h / 820, shirt=SHIRT[state + 1], face="neutral", seed=20 + state, arm=(0.2, -0.5))
    if state > 0:
        ux, uy = px + 60, h * 0.98 - 330 * h / 820
        d.pieslice([ux - 110, uy - 70, ux + 110, uy + 70], 180, 360, fill=(40, 40, 60))
        d.line([(ux, uy), (ux, uy + 150)], fill=(30, 30, 30), width=5)
    f = font("sans-black", int(h * 0.12))
    d.text((wx0 + (wx1 - wx0) * 0.45, wy0 + (wy1 - wy0) * 0.3), "?", font=f, fill=GOLD)
    label(d, w * 0.5, h * 0.72, ["nắng?", "mưa?", "bão?"][state], size=int(h * 0.05), color=GOLD)


def draw_race(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(110, 170, 110))
    for lane, y in enumerate((h * 0.32, h * 0.66)):
        d.rectangle([0, y - h * 0.13, w, y + h * 0.13], fill=(60, 62, 70))
        for x in range(int(-(t * 400) % 120) - 120, w, 120):
            d.rectangle([x, y - 4, x + 60, y + 4], fill=WHITE)
    d.rectangle([w * 0.9, h * 0.15, w * 0.92, h * 0.85], fill=WHITE)
    # red car: fast but crashes / zigzags (high volatility)
    rx = lerp(w * 0.05, w * 0.85, ease(p)) + 30 * math.sin(t * 6)
    ry = h * 0.32 + h * 0.08 * math.sin(t * 9)
    spin = math.sin(t * 9) * 0.4

    def car(x, y, col, tilt=0.0):
        body = [(x - 80, y - 30 + tilt * 40), (x + 80, y - 30 - tilt * 40), (x + 80, y + 30 - tilt * 40), (x - 80, y + 30 + tilt * 40)]
        d.polygon(body, fill=col)
        d.rectangle([x - 20, y - 22, x + 30, y + 22], fill=(30, 40, 60))
        for wx in (-50, 50):
            d.ellipse([x + wx - 18, y - 46 - tilt * wx * 0.5, x + wx + 18, y - 26 - tilt * wx * 0.5], fill=(20, 20, 20))
            d.ellipse([x + wx - 18, y + 26 - tilt * wx * 0.5, x + wx + 18, y + 46 - tilt * wx * 0.5], fill=(20, 20, 20))

    if 0.45 < p < 0.6:
        for i in range(6):
            r = 20 + i * 12
            d.ellipse([rx - 120 - i * 30 - r, ry - r, rx - 120 - i * 30 + r, ry + r], fill=(150, 150, 150))
    car(rx, ry, RED, spin)
    gx = lerp(w * 0.05, w * 0.8, p)
    car(gx, h * 0.66, GREEN)
    label(d, w * 0.25, h * 0.06, "phóng ẩu", size=int(h * 0.045), color=RED)
    label(d, w * 0.25, h * 0.94, "chạy đều", size=int(h * 0.045), color=GREEN)


def draw_rollercoaster(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(120, 170, 230))
    pts = []
    for i in range(61):
        x = i * w / 60
        y = h * 0.5 - h * 0.28 * math.sin(i / 60 * 2 * math.pi * 1.5) * (1 if i < 40 else -1.3)
        pts.append((x, min(h * 0.92, y)))
    for x, y in pts[::4]:
        d.line([(x, y), (x, h)], fill=(120, 80, 60), width=6)
    d.line(pts, fill=(200, 60, 60), width=12, joint="curve")
    k = (p * 1.1 + t * 0.05) % 1
    i = min(59, int(k * 60))
    (x0, y0), (x1, y1) = pts[i], pts[i + 1]
    cx, cy = x0, y0 - 30
    d.rounded_rectangle([cx - 50, cy - 30, cx + 50, cy + 20], radius=12, fill=(250, 200, 60))
    for j, dx in enumerate((-25, 20)):
        d.ellipse([cx + dx - 16, cy - 70, cx + dx + 16, cy - 38], fill=SKIN[j])
        d.ellipse([cx + dx - 6, cy - 60, cx + dx + 6, cy - 46], fill=(90, 30, 30))
        d.line([(cx + dx - 14, cy - 40), (cx + dx - 26, cy - 90)], fill=SKIN[j], width=8)
    if y1 - y0 > 6:
        label(d, w * 0.5, h * 0.08, "AAAAA!", size=int(h * 0.06), color=RED)


def draw_iceberg(d, w, h, p, t):
    # camera tilts down below the waterline: the hidden part is the tail risk
    k = ease((p - 0.55) / 0.4)  # nửa đầu cảnh: chỉ thấy phần nổi; nửa sau mới lặn xuống phần chìm
    off = int(h * 0.42 * k)
    sea_y = h * 0.45 - off
    d.rectangle([0, 0, w, h], fill=(120, 180, 230))
    d.rectangle([0, sea_y, w, h], fill=mix(SEA, SEA_D, 0.3))
    for y in range(int(sea_y), h, 40):
        d.rectangle([0, y, w, y + 20], fill=mix(SEA, SEA_D, 0.3 + 0.6 * (y - sea_y) / h))
    cx = w * 0.5
    tip = [(cx - 110, sea_y), (cx - 40, sea_y - 120), (cx + 10, sea_y - 70), (cx + 60, sea_y - 150), (cx + 120, sea_y)]
    d.polygon(tip, fill=WHITE)
    under = [(cx - 110, sea_y), (cx - 300, sea_y + h * 0.35), (cx - 200, sea_y + h * 0.75), (cx + 50, sea_y + h * 0.9),
             (cx + 320, sea_y + h * 0.6), (cx + 260, sea_y + h * 0.25), (cx + 120, sea_y)]
    d.polygon(under, fill=(170, 210, 235))
    sx = lerp(-w * 0.1, w * 0.2, ease(p / 0.5))
    hull = [(sx - 160, sea_y - 60), (sx + 120, sea_y - 60), (sx + 90, sea_y + 10), (sx - 140, sea_y + 10)]
    d.polygon(hull, fill=(30, 30, 35))
    d.rectangle([sx - 140, sea_y - 66, sx + 115, sea_y - 56], fill=(200, 40, 40))
    for i in range(3):
        d.rectangle([sx - 90 + i * 60, sea_y - 130, sx - 60 + i * 60, sea_y - 66], fill=(230, 180, 60))
    label(d, cx + 240, sea_y - 60, "VaR thấy", size=int(h * 0.04), color=GOLD)
    if k > 0.3:
        label(d, cx, sea_y + h * 0.5, "phần chìm = CVaR", size=int(h * 0.05), color=RED)


def draw_money_burn(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(30, 18, 14))
    n = 9
    burned = ease(p) * n
    for i in range(n):
        x = w * 0.12 + (i % 3) * w * 0.27
        y = h * 0.18 + (i // 3) * h * 0.24
        b = max(0.0, min(1.0, burned - i))
        nh = h * 0.16 * (1 - b)
        if nh > 4:
            d.rounded_rectangle([x, y + h * 0.16 - nh, x + w * 0.22, y + h * 0.16], radius=8, fill=(90, 160, 110),
                                outline=(40, 90, 60), width=3)
            d.text((x + 16, y + h * 0.16 - nh + 6), "₫", font=font("sans-black", int(h * 0.06)), fill=(40, 90, 60))
        if 0 < b < 1:
            fx, fy = x + w * 0.11, y + h * 0.16 - nh
            for j in range(5):
                fl = 30 + 25 * math.sin(t * 14 + j * 1.7)
                d.ellipse([fx - 50 + j * 22 - 18, fy - fl - 20, fx - 50 + j * 22 + 18, fy + 10], fill=(255, 140 + j * 15, 40))
    bw = w * 0.6 * (1 - ease(p))
    d.rounded_rectangle([w * 0.2, h * 0.9, w * 0.8, h * 0.95], radius=12, outline=RED, width=4)
    if bw > 4:
        d.rounded_rectangle([w * 0.2, h * 0.9, w * 0.2 + bw, h * 0.95], radius=12, fill=RED)
    label(d, w * 0.5, h * 0.84, "TÀI KHOẢN", size=int(h * 0.045), color=RED)


def draw_panic(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(40, 18, 20))
    # falling red arrow on a big board
    d.rectangle([w * 0.06, h * 0.05, w * 0.94, h * 0.45], fill=(12, 12, 16), outline=(80, 30, 30), width=4)
    pts = []
    for i in range(30):
        x = w * 0.1 + i * w * 0.8 / 29
        y = h * 0.12 + (h * 0.28) * (i / 29) ** 1.6 + 10 * math.sin(i * 1.3)
        pts.append((x, y))
    k = max(2, int(30 * ease(p / 0.6)))
    d.line(pts[:k], fill=RED, width=8)
    ex, ey = pts[k - 1]
    d.polygon([(ex - 20, ey - 10), (ex + 20, ey - 10), (ex, ey + 28)], fill=RED)
    for i in range(5):
        jitter = 6 * math.sin(t * 20 + i * 2)
        person(d, w * (0.1 + i * 0.2) + jitter, h * 1.02, s=h / 900, face="shock", seed=30 + i, sweat=(t * 1.5 + i * 0.3) % 1,
               arm=(-2.6 + 0.3 * math.sin(t * 10 + i), 2.6 - 0.3 * math.sin(t * 9 + i)), legs=False)


def draw_trader(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(22, 26, 36))
    for m, mx in enumerate((w * 0.08, w * 0.52)):
        d.rounded_rectangle([mx, h * 0.08, mx + w * 0.4, h * 0.5], radius=10, fill=(10, 12, 16), outline=(70, 80, 95), width=4)
        rnd = random.Random(m * 7 + int(t * 3))
        y = h * 0.3
        for c in range(10):
            o = y
            y = min(h * 0.46, max(h * 0.12, y + rnd.uniform(-1, 1) * h * 0.05))
            col = GREEN if y < o else RED
            x = mx + 18 + c * (w * 0.4 - 30) / 10
            d.line([(x + 8, min(o, y) - 14), (x + 8, max(o, y) + 14)], fill=col, width=2)
            d.rectangle([x, min(o, y), x + 16, max(o, y) + 2], fill=col)
        d.rectangle([mx + w * 0.18, h * 0.5, mx + w * 0.22, h * 0.56], fill=(70, 80, 95))
    d.rectangle([0, h * 0.62, w, h], fill=(90, 60, 40))
    person(d, w * 0.5, h * 1.06, s=h / 640, face="shock" if p > 0.5 else "neutral", seed=41, sweat=(t % 1) if p > 0.5 else 0,
           arm=(-0.9, 0.9), legs=False)
    mx_, my_ = w * 0.85, h * 0.6
    d.rectangle([mx_ - 30, my_ - 50, mx_ + 30, my_ + 10], fill=WHITE)
    for j in range(3):
        sy = my_ - 70 - ((t * 40 + j * 20) % 60)
        d.line([(mx_ - 10 + j * 10, sy), (mx_ - 6 + j * 10, sy - 18)], fill=(200, 200, 200), width=3)


def draw_board(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(6, 8, 10))
    codes = ["QTA", "QTV", "QTB", "QTM", "QTX", "QTF", "QTS", "QTH", "QTL", "QTN"]
    rows, f = 7, font("mono-bold", int(h * 0.06))
    rnd = random.Random(int(t * 4))
    scan = ease(p) * rows
    for i in range(rows):
        y = h * 0.06 + i * h * 0.13
        code = codes[(i + int(t * 0.5)) % len(codes)]
        ch = rnd.uniform(-6.9, 6.9)
        col = GREEN if ch > 0.3 else (RED if ch < -0.3 else GOLD)
        if i < scan:
            d.rectangle([w * 0.02, y - 6, w * 0.98, y + h * 0.1], fill=(18, 30, 24))
        d.text((w * 0.05, y), code, font=f, fill=WHITE)
        # không vẽ số giá: mọi số trên màn hình phải có nguồn, nên bảng chỉ có hướng + độ dài thanh
        d.text((w * 0.3, y), "▲" if ch > 0.3 else ("▼" if ch < -0.3 else "■"), font=f, fill=col)
        d.rounded_rectangle([w * 0.42, y + 8, w * 0.42 + w * 0.5 * abs(ch) / 7, y + h * 0.07], radius=8, fill=col)
    sy = h * 0.06 + min(rows - 1, int(scan)) * h * 0.13
    d.rectangle([w * 0.02, sy - 6, w * 0.98, sy + h * 0.1], outline=T["accent"], width=5)
    label(d, w * 0.5, h * 0.96, "mã minh hoạ · dữ liệu giả", size=int(h * 0.035), color=(180, 180, 180))


def draw_coin(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(26, 30, 44))
    up = math.sin(math.pi * ((t * 0.8) % 1))
    cy = h * 0.75 - up * h * 0.45
    sx = abs(math.cos(t * 12))
    cx, R = w * 0.5, h * 0.12
    d.ellipse([cx - R * sx - 4, cy - R, cx + R * sx + 4, cy + R], fill=(150, 110, 30))
    d.ellipse([cx - R * sx, cy - R, cx + R * sx, cy + R], fill=(240, 200, 70))
    if sx > 0.5:
        side = "S" if math.cos(t * 12) > 0 else "N"
        f = font("sans-black", int(R))
        d.text((cx - R * 0.3, cy - R * 0.6), side, font=f, fill=(150, 110, 30))
    person(d, w * 0.25, h * 1.0, s=h / 800, face="shock", seed=50, arm=(0.3, -2.4), legs=False)
    d.ellipse([w * 0.5 - R * 1.2, h * 0.9, w * 0.5 + R * 1.2, h * 0.94], fill=(15, 18, 26))


def draw_multiverse(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(14, 16, 30))
    rnd = random.Random(8)
    for _ in range(60):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        b = 120 + int(100 * (0.5 + 0.5 * math.sin(t * 3 + x)))
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(b, b, b))
    ox, oy = w * 0.08, h * 0.5
    n = 24
    for i in range(n):
        r = random.Random(i)
        pts, y = [(ox, oy)], oy
        for s in range(1, 21):
            y += r.gauss(0.002, 0.045) * h
            pts.append((ox + s * w * 0.85 / 20, y))
        k = max(2, int(21 * ease((p - 0.02 * i) / 0.6)))
        col = GREEN if pts[-1][1] < oy else RED
        d.line(pts[:k], fill=col + (200,), width=3)
    person(d, ox + 20, oy + 160, s=h / 1100, face="shock", seed=60, arm=(0.2, -0.2))


def draw_rocket(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(20, 24, 50))
    k = ease(p / 0.6)
    fall = ease((p - 0.6) / 0.4)
    ry = lerp(h * 0.8, h * 0.15, k) + fall * h * 0.7
    rx = w * 0.5 + fall * w * 0.25
    tilt = fall * 0.8
    d.polygon([(rx, ry - 110), (rx - 40 + tilt * 40, ry + 40), (rx + 40 + tilt * 40, ry + 40)], fill=WHITE)
    d.ellipse([rx - 15, ry - 40, rx + 15, ry - 10], fill=(80, 160, 230))
    if fall < 0.2:
        for j in range(4):
            fl = 50 + 30 * math.sin(t * 20 + j)
            d.polygon([(rx - 25 + j * 15, ry + 40), (rx - 15 + j * 15, ry + 40), (rx - 20 + j * 15, ry + 40 + fl)],
                      fill=(255, 150, 40))
    else:
        for j in range(5):
            r = 15 + j * 8
            d.ellipse([rx - r - j * 10, ry + 40 + j * 20 - r, rx + r - j * 10, ry + 40 + j * 20 + r], fill=(110, 110, 120))
    label(d, w * 0.5, h * 0.06, "TO THE MOON?" if fall < 0.2 else "…rơi", size=int(h * 0.05), color=GOLD if fall < 0.2 else RED)


def draw_code(d, w, h, p, t):
    d.rectangle([0, 0, w, h], fill=(24, 28, 36))
    lx0, ly0, lx1, ly1 = w * 0.1, h * 0.08, w * 0.9, h * 0.72
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=16, fill=(40, 44, 52))
    d.rectangle([lx0 + 18, ly0 + 18, lx1 - 18, ly1 - 18], fill=(10, 18, 14))
    d.polygon([(lx0 - 50, ly1 + 50), (lx1 + 50, ly1 + 50), (lx1, ly1), (lx0, ly1)], fill=(60, 64, 72))
    code = ["import numpy as np", "r = np.diff(np.log(px))", "sigma = r.std() * 252**.5", "print(sigma)"]
    f = font("mono", int(h * 0.045))
    shown = int(sum(len(c) for c in code) * ease(p / 0.8))
    y = ly0 + 40
    for ln in code:
        part = ln[:max(0, shown)]
        shown -= len(ln)
        d.text((lx0 + 40, y), part, font=f, fill=GREEN if part.startswith("import") else WHITE)
        y += h * 0.09
        if shown <= 0:
            if int(t * 3) % 2:
                d.rectangle([lx0 + 40 + d.textlength(part, font=f), y - h * 0.09, lx0 + 52 + d.textlength(part, font=f),
                             y - h * 0.09 + h * 0.05], fill=T["accent"])
            break
    # python logo-ish snakes (two rounded squares, no trademark artwork)
    for i, col in enumerate([(55, 118, 171), (255, 211, 67)]):
        x = w * 0.78 + i * 34
        yy = h * 0.8 + i * 34
        d.rounded_rectangle([x, yy, x + 60, yy + 60], radius=18, fill=col)


def draw_banker(d, w, h, p, t):
    """Văn phòng ngân hàng, đồng hồ chỉ 4:15, sếp chờ một tờ báo cáo rủi ro được đưa tới."""
    d.rectangle([0, 0, w, h], fill=(52, 46, 60))
    d.rectangle([0, h * 0.72, w, h], fill=(90, 60, 45))
    d.rectangle([w * 0.62, h * 0.1, w * 0.95, h * 0.5], fill=(150, 190, 230))
    for i in range(5):
        x = w * 0.64 + i * w * 0.065
        d.rectangle([x, h * 0.25 + (i % 3) * 18, x + w * 0.045, h * 0.5], fill=(70, 80, 100))
    cx, cy, R = w * 0.22, h * 0.24, h * 0.15
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=WHITE, outline=(40, 40, 40), width=6)
    for k in range(12):
        a = k * math.pi / 6
        d.line([(cx + math.cos(a) * R * 0.82, cy + math.sin(a) * R * 0.82), (cx + math.cos(a) * R * 0.95, cy + math.sin(a) * R * 0.95)], fill=(40, 40, 40), width=3)
    mins = 13 + 2 * p  # 4:13 → 4:15
    am = -math.pi / 2 + mins / 60 * 2 * math.pi
    ah = -math.pi / 2 + (4 + mins / 60) / 12 * 2 * math.pi
    d.line([(cx, cy), (cx + math.cos(ah) * R * 0.5, cy + math.sin(ah) * R * 0.5)], fill=(30, 30, 30), width=8)
    d.line([(cx, cy), (cx + math.cos(am) * R * 0.8, cy + math.sin(am) * R * 0.8)], fill=RED, width=5)
    d.rectangle([w * 0.15, h * 0.62, w * 0.85, h * 0.72], fill=(110, 70, 45))
    person(d, w * 0.62, h * 0.95, s=h / 760, shirt=(30, 34, 50), face="neutral", hair=(200, 200, 205), seed=70,
           arm=(-0.4, 0.4), legs=False)
    k = ease((p - 0.2) / 0.5)
    px = lerp(-w * 0.1, w * 0.4, k)
    person(d, px, h * 1.0, s=h / 820, shirt=(70, 110, 170), face="neutral", seed=71, arm=(-1.3, 0.3), legs=False)
    d.rectangle([px + 70, h * 0.5, px + 150, h * 0.62], fill=WHITE, outline=(150, 150, 150), width=2)
    for j in range(4):
        d.line([(px + 80, h * 0.52 + j * 14), (px + 140, h * 0.52 + j * 14)], fill=(120, 120, 120), width=3)
    label(d, w * 0.22, h * 0.48, "4:15", size=int(h * 0.06), color=GOLD)


def draw_telescope(d, w, h, p, t):
    """Đêm sao, nhà thiên văn nhìn kính viễn vọng, sao chổi vạch quỹ đạo, các chấm quan sát lệch quanh đường cong."""
    d.rectangle([0, 0, w, h], fill=(10, 14, 34))
    rnd = random.Random(3)
    for _ in range(70):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.7)
        b = 140 + int(90 * (0.5 + 0.5 * math.sin(t * 2 + x)))
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(b, b, b))
    pts = [(w * (0.15 + 0.75 * u), h * (0.6 - 0.45 * math.sin(math.pi * u * 0.9))) for u in [i / 40 for i in range(41)]]
    k = max(2, int(41 * ease(p / 0.8)))
    d.line(pts[:k], fill=GOLD + (160,), width=3)
    obs = random.Random(9)
    for i in range(0, k, 4):
        x, y = pts[i]
        oy = y + obs.uniform(-1, 1) * h * 0.05
        d.ellipse([x - 7, oy - 7, x + 7, oy + 7], fill=(120, 200, 255))
    cx, cy = pts[k - 1]
    for j in range(6):
        d.line([(cx, cy), (cx - 30 - j * 8, cy + 10 + j * 6)], fill=(200, 230, 255), width=4 - j // 2)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=WHITE)
    d.rectangle([0, h * 0.82, w, h], fill=(30, 34, 40))
    tx, ty = w * 0.2, h * 0.82
    d.line([(tx, ty), (tx - 30, h)], fill=(90, 90, 100), width=6)
    d.line([(tx, ty), (tx + 30, h)], fill=(90, 90, 100), width=6)
    d.polygon([(tx - 10, ty - 10), (tx + 120, ty - 90), (tx + 130, ty - 70), (tx, ty + 10)], fill=(170, 140, 90))
    person(d, tx - 60, h * 1.02, s=h / 900, shirt=(90, 60, 50), face="happy", hair=(220, 220, 220), seed=72,
           arm=(0.3, -1.6), legs=False)


def draw_news(d, w, h, p, t):
    """Hai tờ báo: tin tốt (xanh) khiến người đọc gật gù, tin xấu (đỏ) khiến cả đám đông nhảy dựng."""
    d.rectangle([0, 0, w, h], fill=(34, 30, 36))
    for i, (txt, col, face) in enumerate((("TIN TỐT ▲", GREEN, "happy"), ("TIN XẤU ▼", RED, "shock"))):
        x0 = w * (0.04 + i * 0.5)
        k = ease((p - i * 0.3) / 0.15)
        if k <= 0:
            continue
        shake = 8 * math.sin(t * 30) if i == 1 else 0
        d.rectangle([x0 + shake, h * 0.06, x0 + w * 0.42 + shake, h * 0.46], fill=(235, 230, 215))
        d.text((x0 + 20 + shake, h * 0.09), txt, font=font("sans-black", int(h * 0.07)), fill=col)
        for j in range(5):
            d.line([(x0 + 20 + shake, h * 0.22 + j * h * 0.045), (x0 + w * 0.4 + shake, h * 0.22 + j * h * 0.045)], fill=(150, 150, 140), width=4)
        n = 1 if i == 0 else 3
        for m in range(n):
            jump = (abs(math.sin(t * 9 + m)) * h * 0.05) if i == 1 else 0
            person(d, x0 + w * (0.21 if n == 1 else 0.08 + m * 0.13), h * 1.04 - jump, s=h / (900 if n == 1 else 1100),
                   face=face, seed=80 + i * 5 + m, sweat=(t + m * 0.3) % 1 if i == 1 else 0,
                   arm=(-2.5, 2.5) if i == 1 else (0.2, -0.2), legs=False)


def draw_speech(d, w, h, p, t):
    """Một người nói vào micro, sóng âm bay vào máy tính, máy đoán từng âm tiết (trạng thái ẩn → quan sát)."""
    d.rectangle([0, 0, w, h], fill=(22, 30, 44))
    person(d, w * 0.2, h * 1.02, s=h / 760, shirt=(70, 120, 200), face="happy", seed=90, arm=(0.4, -1.0), legs=False)
    mx, my = w * 0.36, h * 0.5
    d.rounded_rectangle([mx - 16, my - 40, mx + 16, my + 10], radius=14, fill=(60, 60, 70))
    d.line([(mx, my + 10), (mx, h * 0.8)], fill=(60, 60, 70), width=6)
    for k in range(40):
        x = mx + 30 + k * w * 0.0075
        amp = h * 0.12 * abs(math.sin(k * 0.6 + t * 8)) * (0.4 + 0.6 * abs(math.sin(k * 0.13)))
        d.line([(x, my - 15 - amp), (x, my - 15 + amp)], fill=T["accent"], width=4)
    cx0, cy0 = w * 0.7, h * 0.2
    d.rounded_rectangle([cx0, cy0, cx0 + w * 0.27, cy0 + h * 0.42], radius=12, fill=(10, 12, 18), outline=(90, 100, 120), width=4)
    words = ["xin", "chào", "thị", "trường"]
    n = int(len(words) * ease(p / 0.8) + 0.999)
    for i, wd in enumerate(words[:n]):
        d.text((cx0 + 18, cy0 + 16 + i * h * 0.09), wd, font=font("mono-bold", int(h * 0.06)), fill=GREEN)
    d.rectangle([cx0 + w * 0.1, cy0 + h * 0.42, cx0 + w * 0.17, cy0 + h * 0.5], fill=(90, 100, 120))
    label(d, w * 0.83, h * 0.8, "trạng thái ẩn → âm thanh", size=int(h * 0.035), color=GOLD)


def draw_swan(d, w, h, p, t):
    """Hồ nước toàn thiên nga trắng; một con thiên nga đen bất ngờ bơi vào khung (sự kiện hiếm mà có thật)."""
    d.rectangle([0, 0, w, h], fill=(150, 200, 230))
    d.rectangle([0, h * 0.5, w, h], fill=(60, 120, 170))
    for y in range(int(h * 0.55), h, 30):
        d.arc([(t * 40) % 80 - 80, y, w + 80, y + 20], 0, 180, fill=(90, 150, 200), width=2)

    def swan(x, y, col, s=1.0, bob=0.0):
        y += bob
        d.ellipse([x - 60 * s, y - 30 * s, x + 60 * s, y + 25 * s], fill=col)
        d.line([(x + 40 * s, y - 10 * s), (x + 55 * s, y - 80 * s)], fill=col, width=int(16 * s))
        d.ellipse([x + 42 * s, y - 100 * s, x + 74 * s, y - 72 * s], fill=col)
        d.polygon([(x + 72 * s, y - 88 * s), (x + 98 * s, y - 82 * s), (x + 72 * s, y - 78 * s)], fill=(240, 120, 40))

    for i in range(5):
        swan(w * (0.1 + i * 0.17), h * (0.62 + 0.08 * (i % 2)), WHITE, h / 600, 5 * math.sin(t * 2 + i))
    bx = lerp(w * 1.15, w * 0.62, ease((p - 0.25) / 0.45))
    swan(bx, h * 0.85, (20, 20, 24), h / 520, 5 * math.sin(t * 2.5))
    if p > 0.6:
        label(d, w * 0.5, h * 0.1, "hiếm… nhưng CÓ", size=int(h * 0.055), color=RED)


def draw_exit(d, w, h, p, t):
    """Căn phòng đông người, chỉ một cửa thoát hiểm hẹp: lúc yên ổn đi thong thả, lúc báo động thì chen nhau."""
    alarm = p > 0.45
    d.rectangle([0, 0, w, h], fill=(60, 30, 32) if alarm and int(t * 4) % 2 else (40, 40, 48))
    d.rectangle([w * 0.82, h * 0.25, w * 0.95, h * 0.85], fill=(30, 120, 70))
    d.text((w * 0.83, h * 0.27), "EXIT", font=font("sans-black", int(h * 0.06)), fill=WHITE)
    d.rectangle([w * 0.84, h * 0.4, w * 0.93, h * 0.85], fill=(15, 20, 18))
    rnd = random.Random(4)
    for i in range(9):
        bx = rnd.uniform(0.05, 0.6) * w
        if alarm:
            bx = lerp(bx, w * 0.75, ease((p - 0.45) / 0.5) * (0.6 + 0.04 * i))
            bx += 10 * math.sin(t * 20 + i)
        person(d, bx, h * (0.9 + 0.03 * (i % 3)), s=h / 1300, face="shock" if alarm else "neutral", seed=100 + i,
               sweat=((t + i * 0.2) % 1) if alarm else 0, arm=(-2.4, 2.4) if alarm else (0.1, -0.1))
    label(d, w * 0.4, h * 0.08, "BÁO ĐỘNG!" if alarm else "vào thì dễ…", size=int(h * 0.055), color=RED if alarm else GOLD)


def draw_particle(d, w, h, p, t):
    """Cốc nước dưới kính hiển vi: hạt bụi bị va đập ngẫu nhiên nhưng luôn bị kéo về tâm (Ornstein–Uhlenbeck)."""
    d.rectangle([0, 0, w, h], fill=(24, 28, 40))
    cx, cy, R = w * 0.5, h * 0.5, min(w, h) * 0.42
    d.ellipse([cx - R - 14, cy - R - 14, cx + R + 14, cy + R + 14], fill=(80, 85, 100))
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(60, 130, 190))
    rnd = random.Random(int(t * 8))
    for _ in range(40):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(0, R * 0.95)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(150, 200, 240))
    gen = random.Random(12)
    x, y, path = R * 0.7, -R * 0.4, []
    steps = int(160 * ease(p))
    for _ in range(max(2, steps)):
        x += -0.06 * x + gen.gauss(0, R * 0.05)
        y += -0.06 * y + gen.gauss(0, R * 0.05)
        path.append((cx + x, cy + y))
    d.line(path, fill=GOLD + (200,), width=2)
    px, py = path[-1]
    d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=T["accent"])
    d.line([(cx - 14, cy), (cx + 14, cy)], fill=WHITE, width=3)
    d.line([(cx, cy - 14), (cx, cy + 14)], fill=WHITE, width=3)
    label(d, cx, h * 0.06, "va đập ngẫu nhiên + lực kéo về", size=int(h * 0.04), color=GOLD)


def draw_coin_crowd(d, w, h, p, t):
    """Rất nhiều người cùng tung xu; người tung ngửa liền nhiều lần được đội vương miện 'thiên tài' (thật ra là may)."""
    d.rectangle([0, 0, w, h], fill=(26, 30, 44))
    cols, rows = 6, 3
    win = (2, 1)
    for r in range(rows):
        for c in range(cols):
            x = w * (0.09 + c * 0.165)
            y = h * (0.42 + r * 0.27)
            out = (r, c) != win and p > 0.35 + 0.05 * ((r * cols + c) % 7)
            person(d, x, y, s=h / 2100, face="sad" if out else "neutral", seed=110 + r * cols + c,
                   arm=(0.2, -2.4), legs=False)
            if not out:
                cy = y - 200 * h / 2100 - abs(math.sin(t * 6 + c + r)) * h * 0.06
                sx = abs(math.cos(t * 10 + c))
                d.ellipse([x + 30 - 14 * sx, cy - 14, x + 30 + 14 * sx, cy + 14], fill=(240, 200, 70))
    if p > 0.6:
        x = w * (0.09 + win[1] * 0.165)
        y = h * (0.42 + win[0] * 0.27) - 330 * h / 2100
        d.polygon([(x - 30, y), (x - 30, y - 30), (x - 15, y - 15), (x, y - 36), (x + 15, y - 15), (x + 30, y - 30), (x + 30, y)], fill=GOLD)
        label(d, w * 0.5, h * 0.07, "“THIÊN TÀI”?", size=int(h * 0.06), color=GOLD)


def draw_water_flow(d, w, h, p, t):
    """Bể nước = giá; vòi bơm vào (xanh) và vòi xả ra (đỏ) = dòng tiền. Mực nước dâng nhưng vòi xả mở to dần."""
    d.rectangle([0, 0, w, h], fill=(30, 34, 46))
    tx0, ty0, tx1, ty1 = w * 0.3, h * 0.25, w * 0.7, h * 0.9
    level = ty1 - (ty1 - ty0) * (0.35 + 0.25 * ease(p))
    d.rectangle([tx0, level, tx1, ty1], fill=(60, 140, 210))
    for x in range(int(tx0), int(tx1), 24):
        d.arc([x, level - 6 + 4 * math.sin(t * 4 + x), x + 24, level + 6], 180, 360, fill=(140, 200, 240), width=3)
    d.rectangle([tx0 - 8, ty0, tx0, ty1], fill=(180, 190, 200))
    d.rectangle([tx1, ty0, tx1 + 8, ty1], fill=(180, 190, 200))
    d.rectangle([tx0 - 8, ty1, tx1 + 8, ty1 + 8], fill=(180, 190, 200))
    d.rectangle([w * 0.05, h * 0.12, w * 0.4, h * 0.17], fill=GREEN)
    win_ = 6 + 4 * (1 - p)
    for k in range(int(win_)):
        yy = h * 0.17 + ((t * 300 + k * 40) % (level - h * 0.17))
        d.ellipse([w * 0.38 - 6, yy - 6, w * 0.38 + 6, yy + 6], fill=GREEN)
    out = 0.3 + 0.7 * ease(p)
    d.rectangle([tx1 + 8, ty1 - 60, w * 0.95, ty1 - 60 + 30 * out + 10], fill=RED)
    for k in range(int(4 + 8 * out)):
        xx = tx1 + 30 + ((t * 300 + k * 50) % (w * 0.95 - tx1 - 30))
        d.ellipse([xx - 6, ty1 - 50, xx + 6, ty1 - 38], fill=(255, 170, 170))
    label(d, w * 0.22, h * 0.07, "tiền vào", size=int(h * 0.045), color=GREEN)
    label(d, w * 0.84, ty1 + 0.0 - 100, "tiền ra", size=int(h * 0.045), color=RED)
    label(d, w * 0.5, ty0 - 40, "mực nước = giá", size=int(h * 0.04), color=WHITE)


DRAW = {k[5:]: v for k, v in dict(globals()).items() if k.startswith("draw_")}


# ---------------------------------------------------------------- real photos (B-roll) with Ken Burns
@lru_cache(maxsize=32)
def _photo(path, w, h):
    im = Image.open(path).convert("RGB")
    s = max(w * 1.2 / im.width, h * 1.2 / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    # brand grade: a touch darker + warm, so text and logo stay readable on top
    tint = Image.new("RGB", im.size, (40, 22, 10))
    return Image.blend(im, tint, 0.18)


@lru_cache(maxsize=32)
def _portrait(path, w, h):
    """Ảnh dọc / nhỏ (chân dung): hiện TRỌN ảnh ở giữa, nền là chính ảnh đó phóng to làm mờ — không cắt mất mặt."""
    src = Image.open(path).convert("RGB")
    bg = src.resize((w, max(1, int(src.height * w / src.width))), Image.LANCZOS)
    top = max(0, (bg.height - h) // 2)
    bg = bg.crop((0, top, w, top + h)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new("RGB", (w, h), (8, 13, 11)), 0.45)
    s = min(h * 0.96 / src.height, w * 0.9 / src.width)
    fg = src.resize((max(1, int(src.width * s)), max(1, int(src.height * s))), Image.LANCZOS)
    return bg, fg


def photo_frame(path, w, h, p, seed=0):
    with Image.open(str(path)) as probe:
        iw, ih = probe.size
    if ih / iw > (h / w) * 1.15 or iw < w * 0.6:  # chân dung hoặc ảnh nhỏ → contain, không cover-crop
        bg, fg = _portrait(str(path), w, h)
        z = 1.0 + 0.04 * p
        fz = fg.resize((int(fg.width * z), int(fg.height * z)), Image.BILINEAR)
        out = bg.copy()
        out.paste(fz, ((w - fz.width) // 2, (h - fz.height) // 2))
        return out.convert("RGBA")
    im = _photo(str(path), w, h)
    z = 1.0 + 0.14 * p  # slow push-in
    cw, ch = int(im.width / 1.2 / z * 1.0), int(im.height / 1.2 / z)
    cw, ch = min(cw, im.width), min(ch, im.height)
    dirx = 1 if seed % 2 else -1
    x = int((im.width - cw) * (0.5 + 0.35 * dirx * (p - 0.5)))
    y = int((im.height - ch) * (0.5 + 0.2 * (p - 0.5)))
    return im.crop((x, y, x + cw, y + ch)).resize((w, h), Image.LANCZOS).convert("RGBA")


def frame(tag, w, h, p, t, photo=None, radius=28, seed=0):
    """Vẽ một khung minh hoạ w×h (RGBA, bo góc). photo: đường dẫn ảnh thật B-roll (ưu tiên nếu có)."""
    if isinstance(photo, tuple) and photo[0] == "clip":   # video B-roll Pexels
        import clips

        fr = clips.frame(photo[1], w, h, t, scene_key=seed)
        im = Image.fromarray(fr).convert("RGBA") if fr is not None else None
        if im is None:
            im = Image.new("RGBA", (w, h), T["surface"] + (255,))
            DRAW.get(tag, draw_trader)(ImageDraw.Draw(im, "RGBA"), w, h, p, t)
    elif photo:
        im = photo_frame(photo, w, h, p, seed)
    else:
        im = Image.new("RGBA", (w, h), T["surface"] + (255,))
        DRAW.get(tag, draw_trader)(ImageDraw.Draw(im, "RGBA"), w, h, p, t)
    # vignette + rounded mask
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).rectangle([0, 0, w, h], outline=110, width=int(min(w, h) * 0.06))
    vig = vig.filter(ImageFilter.GaussianBlur(min(w, h) * 0.05))
    im = Image.composite(Image.new("RGBA", (w, h), (0, 0, 0, 255)), im, vig)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    im.putalpha(mask)
    return im


if __name__ == "__main__":  # python illustrate.py casino out.png  → xem nhanh một hình
    import sys

    tg = sys.argv[1] if len(sys.argv) > 1 else "casino"
    out = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/{tg}.png"
    sheet = Image.new("RGB", (880 * 3, 560), (0, 0, 0))
    for i, pp in enumerate((0.1, 0.5, 0.9)):
        sheet.paste(frame(tg, 880, 560, pp, pp * 5), (880 * i, 0))
    sheet.save(out)
    print(out, "tags:", sorted(DRAW))


# ---------------------------------------------------------------- photo policy (set by batch.py per video)
CFG = {"mode": "auto", "fetch": True, "topic": None, "board": None}   # mode: auto | draw | photo
BOARD = {  # công thức viết lên bảng đen theo chủ đề. Chỉ ký tự font có (không dùng chỉ số dưới ₜ ᵢ ᵀ)
    "kelly": ["f* = W - (1-W)/R", "g(f) = W·ln(1+f) + (1-W)·ln(1-f)"],
    "monte_carlo": ["P(thắng) ≈ số ván thắng / số ván", "S_t = S_0·exp(Σ ε)"],
    "hmm": ["P(z_t | x_1 … x_t)", "α ← (α·A)·b(x)", "A = [a_ij]"],
    "garch": ["σ²_t = ω + α·ε²_t-1 + β·σ²_t-1"],
    "egarch": ["ln σ²_t = ω + β·ln σ²_t-1", "        + α|z| + γ·z"],
    "ou": ["dX = θ(μ - X)dt + σ·dW"],
    "fat_tails": ["P(|X| > x) ~ x^(-α)", "Gauss: đuôi mỏng"],
    "momentum": ["WML = Thắng - Thua", "r(sau)  vs  r(trước)"],
    "ols": ["β = (X'X)^-1 · X'y", "min Σ (y - Xβ)²"],
    "beta": ["β = Cov(r_i, r_m) / Var(r_m)"],
    "var_cvar": ["VaR_α = -q(α)", "CVaR = E[L | L > VaR]"],
    "sharpe": ["S = (R - R_f) / σ"],
    "sortino": ["S = (R - R_f) / σ_giảm"],
    "psr": ["PSR = P(SR thật > SR*)"],
    "martingale": ["cược: 1, 2, 4, 8, 16 …", "E[lãi] ≤ 0"],
    "cmf": ["CMF = Σ MFV / Σ V"],
    "hurst": ["E[R/S] ~ c·n^H"],
}
USED = []                                # ảnh thật đã dùng trong video hiện tại → dòng ghi công ở caption


def configure(mode="auto", fetch=True, topic=None, board=None):
    CFG.update(mode=mode, fetch=fetch, topic=topic, board=board)
    USED.clear()


def source(tag, slot=0):
    """Nguồn hình THẬT cho tag ở vị trí slot, hoặc None (= hoạt hoạ tự vẽ).
    Ưu tiên: video Pexels khớp nghĩa → ảnh của kênh / Wikimedia. auto: slot lẻ dùng hình thật, slot chẵn dùng hoạt
    hoạ để video xen kẽ; photo: luôn ưu tiên hình thật; draw: chỉ vẽ. 'code' luôn vẽ.
    Trả về ("clip", key) cho video, đường dẫn ảnh cho ảnh tĩnh."""
    if CFG["mode"] == "draw" or not tag or tag == "code":
        return None
    if CFG["mode"] == "auto" and slot % 2 == 0:
        return None
    import clips

    ks = [k for k in clips.keys_for(tag)]
    if ks:
        k = ks[slot // 2 % len(ks)]
        if clips.ensure(k):
            c = clips.manifest()["clips"][k]
            it = {"kind": "clip", "url": c["page"], "artist": c["credit"], "license": "Pexels License"}
            if it not in USED:
                USED.append(it)
            return ("clip", k)
    from broll import photos

    got = photos(tag, CFG["fetch"])
    if not got:
        return None
    it = got[slot // 2 % len(got)]
    if it not in USED:
        USED.append(it)
    return it["path"]


def entity(image_id):
    """Ảnh của một người / nơi / sự kiện có thật trong sổ ảnh (knowledge/images/ledger.json, quản lý bằng images.py).
    Trả về (đường dẫn, dòng ghi công, là ảnh thật?) hoặc None. Ảnh thật luôn được ưu tiên hơn hình vẽ."""
    if not image_id:
        return None
    import images as IMG

    e = IMG.index().get(image_id)
    if not e:
        print(f"  ảnh '{image_id}' chưa có trong sổ ảnh → dùng hình vẽ (python images.py fetch …)")
        return None
    it = {"kind": "ledger", "url": e.get("source_url") or e["id"], "artist": e.get("author", ""),
          "license": e.get("license", ""), "credit": e["credit"]}
    if it not in USED:
        USED.append(it)
    return str(IMG.path_of(e)), e["credit"], e.get("kind") == "photo"
