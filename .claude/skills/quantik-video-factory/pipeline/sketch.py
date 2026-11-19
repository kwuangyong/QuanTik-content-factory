"""Hand-drawn concept animations ("hoạt hoạ vẽ tay"): procedural, original, wobbly chalk strokes on a dark board.

Each animation illustrates one idea with real motion (dice tumbling, coins flipping, Galton balls forming a bell,
an order eating the book, a pendulum, a forecast cone…). Used as a scene of its own (scenes.sketch) where a lesson
has no 3D, and as an extra explainer beat where it has.

draw(img, kind, box, t, p)   kind ∈ KINDS
"""
from __future__ import annotations

import math
import random

from PIL import ImageDraw

from core import THEME as T

INK, ACC, NEU, POS, NEG, MUT = T["text"], T["accent"], T["neutral"], T["positive"], T["negative"], T["muted"]


def _jit(i, k=0.0, amp=3.0):
    v = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return (v - math.floor(v) - 0.5) * 2 * amp


def line(d, pts, color=INK, w=7, seed=0):
    """Wobbly hand-drawn polyline."""
    if len(pts) < 2:
        return
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + _jit(i, seed), y + _jit(i, seed + 1)))
    d.line(out, fill=color, width=w, joint="curve")
    r = w // 2
    for x, y in (out[0], out[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)


def circle(d, cx, cy, r, color=INK, w=6, fill=None, seed=0, n=28):
    pts = [(cx + (r + _jit(i, seed, 1.5)) * math.cos(2 * math.pi * i / n),
            cy + (r + _jit(i, seed + 3, 1.5)) * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
    if fill:
        d.polygon(pts, fill=fill)
    d.line(pts, fill=color, width=w, joint="curve")


def rect(d, x0, y0, x1, y1, color=INK, w=6, fill=None, seed=0):
    if fill:
        d.rectangle([x0, y0, x1, y1], fill=fill)
    line(d, [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], color, w, seed)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 3 * x * x - 2 * x * x * x


# ---------------------------------------------------------------- animations (box = x0, y0, x1, y1)
def dice(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    pips = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    line(d, [(x0 + 30, y1 - 80), (x1 - 30, y1 - 80)], MUT, 5)
    for k, cx in enumerate([x0 + W * 0.32, x0 + W * 0.68]):
        roll = ease(min(1, p / 0.6))
        bounce = abs(math.sin((1 - roll) * 9 + k)) * (1 - roll) * H * 0.35
        cy = y1 - 80 - 90 - bounce
        ang = (1 - roll) * (7 + 3 * k)
        s = 85
        face = (int(t * 8 + k * 3) % 6 + 1) if roll < 1 else (6 if k == 0 else 3)
        cs = [(cx + s * math.cos(ang + a) - 0, cy + s * math.sin(ang + a)) for a in (math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4)]
        d.polygon(cs, fill=(28, 44, 36))
        line(d, cs + [cs[0]], INK, 7, k)
        for u, v in pips[face]:
            px = cx + 38 * (u * math.cos(ang) - v * math.sin(ang))
            py = cy + 38 * (u * math.sin(ang) + v * math.cos(ang))
            d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=ACC if face == 6 else INK)


def coin(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    cyc = (t * 0.9) % 1.0
    cx = x0 + W * 0.5
    cy = y1 - 260 - math.sin(cyc * math.pi) * H * 0.35
    sq = abs(math.cos(cyc * math.pi * 6))
    d.ellipse([cx - 90, cy - 90 * sq - 4, cx + 90, cy + 90 * sq + 4], fill=(70, 55, 20))
    circle(d, cx, cy, 90, NEU, 7) if sq > 0.85 else line(d, [(cx - 90, cy), (cx + 90, cy)], NEU, 9)
    line(d, [(x0 + 40, y1 - 160), (x1 - 40, y1 - 160)], MUT, 5)
    n = int(p * 22)  # tally marks of results so far
    rnd = random.Random(3)
    for i in range(n):
        heads = rnd.random() < 0.5
        x = x0 + 60 + (i % 11) * (W - 120) / 11
        y = y1 - 110 + (i // 11) * 50
        line(d, [(x, y - 18), (x + 6, y + 18)], ACC if heads else POS, 6, i)


def galton(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    rows, cx = 8, x0 + W / 2
    dx, dy = W / 20, H * 0.045
    for r in range(rows):
        for k in range(r + 1):
            px, py = cx + (k - r / 2) * dx * 2, y0 + 70 + r * dy
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=MUT)
    nb = rows + 1
    base = y1 - 30
    rnd = random.Random(7)
    paths = [[rnd.random() < 0.5 for _ in range(rows)] for _ in range(240)]
    landed = [0] * nb
    shown = int(p * 240)
    for i in range(shown):
        landed[sum(paths[i])] += 1
    bw = dx * 2
    for k in range(nb):
        x = cx + (k - rows / 2) * bw
        h = landed[k] * 5.2
        d.rectangle([x - bw * 0.42, base - h, x + bw * 0.42, base], fill=(255, 145, 77, 255))
        line(d, [(x - bw / 2, base), (x - bw / 2, base - H * 0.42)], (60, 80, 70), 3, k)
    for j in range(5):  # balls in flight
        i = shown + j
        if i >= 240:
            break
        f = (t * 2.4 + j / 5) % 1.0
        r = int(f * rows)
        pos = sum(paths[i][:r]) - r / 2
        bx, by = cx + pos * bw, y0 + 70 + f * rows * dy
        d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=NEU)
    if p > 0.75:
        pts = [(cx + (k - rows / 2) * bw, base - 5.2 * 240 * math.comb(rows, k) / 2 ** rows) for k in range(nb)]
        line(d, pts, POS, 6, 9)


def wave(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    mid = y0 + H * 0.5
    pts = []
    for i in range(160):
        u = i / 159
        g = (u * 3 + t * 0.6) % 3.0
        amp = (0.05 if g < 1.6 else 0.32) * H * (0.6 + 0.4 * math.sin(u * 23 + t * 3))
        pts.append((x0 + 20 + u * (W - 40), mid + amp * math.sin(u * 70 + t * 9)))
    line(d, pts, ACC, 6)
    line(d, [(x0 + 20, mid), (x1 - 20, mid)], MUT, 3, 4)


def crash(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n = int(10 + 150 * min(1, p / 0.8))
    pts = []
    for i in range(n):
        u = i / 159
        y = y0 + H * (0.55 - 0.25 * u + 0.04 * math.sin(u * 40)) if u < 0.7 else y0 + H * (0.38 + (u - 0.7) * 1.8)
        pts.append((x0 + 30 + u * (W - 60), y))
    shake = 8 * math.sin(t * 60) if 0.6 < p < 0.8 else 0
    pts = [(x + shake, y) for x, y in pts]
    line(d, pts, NEG if p > 0.6 else POS, 7)
    if p > 0.62:
        a = min(1, (p - 0.62) * 5)
        X, Y = pts[-1]
        line(d, [(X - 40 * a, Y - 70 * a), (X, Y), (X + 40 * a, Y - 70 * a)], NEG, 8, 2)


def orderbook(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    mid = x0 + W / 2
    rows = 5
    eat = p * 3.2
    for i in range(rows):
        y = y0 + 60 + i * (H - 120) / rows
        bid = (i + 1) * W * 0.07
        ask = (i + 1) * W * 0.07
        rem = max(0.0, 1 - max(0.0, eat - i))
        d.rectangle([mid - bid, y, mid - 8, y + 50], fill=(40, 110, 85))
        if rem > 0:
            d.rectangle([mid + 8, y, mid + 8 + ask * rem, y + 50], fill=(150, 70, 75))
        line(d, [(mid + 8, y), (mid + 8 + ask, y), (mid + 8 + ask, y + 50), (mid + 8, y + 50)], MUT, 3, i)
    line(d, [(mid, y0 + 30), (mid, y1 - 30)], INK, 4)
    k = min(rows - 1, int(eat))
    ay = y0 + 60 + k * (H - 120) / rows + 25
    ax = mid - 60 + 30 * math.sin(t * 8)
    line(d, [(x0 + 20, ay), (ax, ay)], NEU, 9)
    line(d, [(ax - 30, ay - 25), (ax, ay), (ax - 30, ay + 25)], NEU, 9, 3)


def leash(d, b, t, p):
    """Two walkers wander but an elastic band keeps them together (pairs, cointegration, mean reversion)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    trail_a, trail_b = [], []
    for i in range(60):
        s = t - (59 - i) * 0.05
        base = y0 + H * 0.5 + H * 0.25 * math.sin(s * 0.9) + H * 0.08 * math.sin(s * 3.1)
        gap = H * 0.12 * math.sin(s * 2.3)
        x = x0 + 40 + (i / 59) * (W - 80)
        trail_a.append((x, base - H * 0.08 + gap))
        trail_b.append((x, base + H * 0.08 - gap))
    line(d, trail_a, ACC, 6, 1)
    line(d, trail_b, POS, 6, 2)
    (ax, ay), (bx, by) = trail_a[-1], trail_b[-1]
    stretch = abs(ay - by) / (H * 0.4)
    line(d, [(ax, ay), (ax + 18, (ay + by) / 2), (bx, by)], NEG if stretch > 0.5 else NEU, 5, 5)
    for x, y, c in ((ax, ay, ACC), (bx, by, POS)):
        d.ellipse([x - 18, y - 18, x + 18, y + 18], fill=c)


def vectors(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 60
    R = min(x1 - x0, y1 - y0) * 0.36
    a1, a2 = 0.25, 0.25 + 1.6 * math.sin(t * 0.9) * min(1, p * 2)
    line(d, [(cx - R * 1.2, cy), (cx + R * 1.2, cy)], MUT, 3)
    line(d, [(cx, cy + R * 0.4), (cx, cy - R * 1.2)], MUT, 3, 1)
    for a, c, s in ((a1, ACC, 1), (a2, POS, 2)):
        X, Y = cx + R * math.cos(a), cy - R * math.sin(a)
        line(d, [(cx, cy), (X, Y)], c, 8, s)
        line(d, [(X - 28 * math.cos(a - 0.45), Y + 28 * math.sin(a - 0.45)), (X, Y),
                 (X - 28 * math.cos(a + 0.45), Y + 28 * math.sin(a + 0.45))], c, 8, s + 4)
    proj = R * math.cos(a2 - a1)
    PX, PY = cx + proj * math.cos(a1), cy - proj * math.sin(a1)
    BX, BY = cx + R * math.cos(a2), cy - R * math.sin(a2)
    line(d, [(BX, BY), (PX, PY)], NEU, 4, 7)
    line(d, [(cx, cy), (PX, PY)], NEU, 12, 8)


def matrix(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n, s = 3, min(W / 11.2, H * 0.13)
    ox, oy = x0 + W * 0.1, y0 + H * 0.3
    step = int(t * 1.6) % (n * n)
    r, c = divmod(step, n)
    for g, gx in ((0, ox), (1, ox + s * 3.6), (2, ox + s * 7.4)):
        for i in range(n):
            for j in range(n):
                hi = (g == 0 and i == r) or (g == 1 and j == c) or (g == 2 and i == r and j == c)
                filled = g == 2 and (i * n + j) < step + (1 if hi else 0) and p > 0.05
                rect(d, gx + j * s, oy + i * s, gx + (j + 1) * s - 8, oy + (i + 1) * s - 8,
                     ACC if hi else MUT, 5 if hi else 3, fill=(60, 45, 30) if filled or hi else None, seed=i * 3 + j)
    line(d, [(ox + s * 3.05, oy + s * 1.2), (ox + s * 3.35, oy + s * 1.6)], INK, 6)
    line(d, [(ox + s * 3.35, oy + s * 1.2), (ox + s * 3.05, oy + s * 1.6)], INK, 6, 2)
    line(d, [(ox + s * 6.85, oy + s * 1.25), (ox + s * 7.2, oy + s * 1.25)], INK, 6, 3)
    line(d, [(ox + s * 6.85, oy + s * 1.55), (ox + s * 7.2, oy + s * 1.55)], INK, 6, 4)


def scale(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, y0 + (y1 - y0) * 0.35
    L = (x1 - x0) * 0.36
    tilt = 0.28 * math.sin(t * 1.7) * math.exp(-p * 1.5)
    line(d, [(cx, cy), (cx, y1 - 60)], INK, 8)
    line(d, [(cx - 120, y1 - 60), (cx + 120, y1 - 60)], INK, 8, 1)
    lx, ly = cx - L * math.cos(tilt), cy - L * math.sin(tilt)
    rx, ry = cx + L * math.cos(tilt), cy + L * math.sin(tilt)
    line(d, [(lx, ly), (rx, ry)], ACC, 8, 2)
    for x, y, c, n in ((lx, ly, POS, 3), (rx, ry, NEG, 2)):
        line(d, [(x, y), (x - 70, y + 140), (x + 70, y + 140), (x, y)], MUT, 4, int(x))
        for k in range(n):
            circle(d, x - 40 + k * 40, y + 120, 18, c, 5, fill=c, seed=k)


def compound(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n = 12
    k = int(p * n * 1.1)
    for i in range(min(k, n)):
        h = 18 * 1.32 ** i
        x = x0 + 40 + i * (W - 80) / n
        for j in range(int(h / 18)):
            y = y1 - 40 - j * 16
            d.ellipse([x, y - 10, x + (W - 80) / n - 10, y + 10], fill=(150, 120, 40), outline=NEU, width=3)
    pts = [(x0 + 40 + i * (W - 80) / n + 30, y1 - 40 - 16 * int(18 * 1.32 ** i / 18)) for i in range(min(k, n))]
    if len(pts) > 1:
        line(d, pts, ACC, 6, 3)


def pendulum(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, top = (x0 + x1) / 2, y0 + 60
    L = (y1 - y0) * 0.62
    line(d, [(cx - 160, top), (cx + 160, top)], INK, 8)
    trail = []
    for i in range(30):
        s = t - (29 - i) * 0.04
        a = 0.75 * math.exp(-s * 0.15) * math.cos(s * 2.6)
        trail.append((cx + L * math.sin(a), top + L * math.cos(a)))
    line(d, trail, (90, 70, 50), 10, 2)
    X, Y = trail[-1]
    line(d, [(cx, top), (X, Y)], MUT, 5, 1)
    circle(d, X, Y, 40, ACC, 7, fill=(120, 70, 40))
    line(d, [(cx, top + L + 70), (cx, top + L + 110)], POS, 6, 4)


def cone(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    mid = y0 + H * 0.5
    split = x0 + W * 0.45
    hist = [(x0 + 30 + i * (split - x0 - 30) / 40, mid + H * 0.12 * math.sin(i * 0.7) + H * 0.05 * math.sin(i * 2.3)) for i in range(41)]
    line(d, hist, INK, 6)
    k = min(1, p / 0.7)
    ex = split + (x1 - 30 - split) * k
    Y = hist[-1][1]
    spread = H * 0.38 * k
    d.polygon([(split, Y), (ex, Y - spread), (ex, Y + spread)], fill=(60, 50, 30))
    line(d, [(split, Y), (ex, Y - spread)], NEU, 5, 2)
    line(d, [(split, Y), (ex, Y + spread)], NEU, 5, 3)
    line(d, [(split, Y), (ex, Y)], ACC, 7, 4)
    for j in range(3):  # possible paths flicker inside the cone
        pts = [(split + u * (ex - split), Y + spread * u * math.sin(t * 3 + j * 2.1 + u * 5) * 0.8) for u in [i / 20 for i in range(21)]]
        line(d, pts, (120, 100, 70), 3, j + 6)


def dominoes(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n = 9
    front = p * (n + 1)
    for i in range(n):
        x = x0 + 60 + i * (W - 120) / n
        ang = min(1.2, max(0.0, (front - i) * 1.4))
        h, w = H * 0.38, 26
        bx, by = x, y1 - 80
        tx, ty = bx + h * math.sin(ang), by - h * math.cos(ang)
        line(d, [(bx, by), (tx, ty)], ACC if ang > 0 else INK, w, i)
    line(d, [(x0 + 30, y1 - 70), (x1 - 30, y1 - 70)], MUT, 5)


def gears(d, b, t, p):
    x0, y0, x1, y1 = b
    for cx, cy, r, sp, c in (((x0 + x1) / 2 - 120, (y0 + y1) / 2, 130, 1, ACC), ((x0 + x1) / 2 + 125, (y0 + y1) / 2 - 90, 90, -1.44, POS)):
        a0 = t * sp * 1.5
        pts = []
        for i in range(97):
            a = a0 + 2 * math.pi * i / 96
            rr = r + (18 if (i // 4) % 2 == 0 else 0)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        line(d, pts, c, 6, int(r))
        circle(d, cx, cy, r * 0.3, c, 6)


def thermometer(d, b, t, p):
    x0, y0, x1, y1 = b
    cx = (x0 + x1) / 2
    top, bot = y0 + 60, y1 - 150
    line(d, [(cx - 30, top), (cx - 30, bot)], INK, 6)
    line(d, [(cx + 30, top), (cx + 30, bot)], INK, 6, 1)
    circle(d, cx, bot + 60, 70, INK, 6, fill=(170, 60, 60))
    lvl = bot - (bot - top) * (0.25 + 0.6 * ease(p / 0.7)) + 6 * math.sin(t * 5)
    d.rectangle([cx - 18, lvl, cx + 18, bot + 10], fill=(200, 70, 70))
    for k in range(7):
        y = top + k * (bot - top) / 6
        line(d, [(cx + 40, y), (cx + (80 if k % 3 == 0 else 60), y)], MUT, 4, k)
    if p > 0.6:
        y = top + (bot - top) * 0.2
        line(d, [(cx + 100, y), (x1 - 40, y)], NEG, 5, 9)


def network(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    rnd = random.Random(5)
    nodes = [(x0 + 60 + rnd.random() * (W - 120), y0 + 60 + rnd.random() * (H - 120)) for _ in range(9)]
    for i in range(9):
        for j in range(i + 1, 9):
            if (i * 7 + j * 3) % 4 == 0:
                pulse = 0.5 + 0.5 * math.sin(t * 3 + i + j)
                line(d, [nodes[i], nodes[j]], (int(60 + 120 * pulse), 90, 70), 4, i * 9 + j)
    for i, (x, y) in enumerate(nodes):
        r = 22 + 8 * math.sin(t * 4 + i)
        circle(d, x, y, r, ACC if i == int(t * 2) % 9 else INK, 6, fill=(40, 60, 50), seed=i)


def bell(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    base = y1 - 60
    k = int(10 + 150 * min(1, p / 0.6))
    pts = [(x0 + 30 + (W - 60) * i / 159, base - H * 0.7 * math.exp(-((i / 159 - 0.5) ** 2) / 0.018)) for i in range(k)]
    line(d, [(x0 + 30, base), (x1 - 30, base)], MUT, 4)
    if p > 0.6:  # tails flash: where the risk lives
        fl = 0.5 + 0.5 * math.sin(t * 7)
        for side in (0, 1):
            xs = range(0, 30) if side == 0 else range(130, 160)
            poly = [(x0 + 30 + (W - 60) * i / 159, base - H * 0.7 * math.exp(-((i / 159 - 0.5) ** 2) / 0.018)) for i in xs]
            poly = poly + [(poly[-1][0], base), (poly[0][0], base)]
            d.polygon(poly, fill=(int(120 + 100 * fl), 50, 55))
    line(d, pts, ACC, 7)


def skew(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    base = y1 - 60
    n = 18
    for i in range(int(p * 1.3 * n)):
        if i >= n:
            break
        u = i / (n - 1)
        h = H * 0.65 * (math.exp(-((u - 0.78) ** 2) / 0.006) + 0.05 * (u < 0.3))
        x = x0 + 40 + u * (W - 100)
        d.rectangle([x, base - h, x + (W - 100) / n - 6, base], fill=NEG if u < 0.3 else ACC)
    line(d, [(x0 + 30, base), (x1 - 30, base)], MUT, 4)
    if p > 0.6:
        line(d, [(x0 + W * 0.45, y0 + H * 0.35), (x0 + 70, base - 40)], NEG, 7, 3)


def ripple(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 40
    for k in range(5):
        r = ((t * 0.7 + k / 5) % 1.0)
        R = r * min(x1 - x0, y1 - y0) * 0.48
        a = int(255 * (1 - r))
        d.ellipse([cx - R, cy - R * 0.38, cx + R, cy + R * 0.38], outline=(*NEU, a), width=6)
    drop = (t * 0.7) % 1.0
    if drop > 0.75:
        y = cy - (1 - (drop - 0.75) * 4) * 260
        d.ellipse([cx - 14, y - 14, cx + 14, y + 14], fill=INK)


def rain(d, b, t, p):
    x0, y0, x1, y1 = b
    rnd = random.Random(11)
    for i in range(70):
        x = x0 + rnd.random() * (x1 - x0)
        sp = 0.6 + rnd.random() * 0.6
        y = y0 + ((rnd.random() + t * sp) % 1.0) * (y1 - y0 - 80)
        line(d, [(x, y), (x - 8, y + 34)], (150, 190, 210), 4, i)
    for k in range(4):  # splashes on the ground
        x = x0 + ((k * 0.27 + t * 0.9) % 1.0) * (x1 - x0)
        r = ((t * 3 + k) % 1.0) * 30
        d.ellipse([x - r, y1 - 60 - r * 0.3, x + r, y1 - 60 + r * 0.3], outline=(150, 190, 210, 200), width=3)
    line(d, [(x0 + 20, y1 - 55), (x1 - 20, y1 - 55)], MUT, 4)


def spring(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, top = (x0 + x1) / 2, y0 + 50
    ext = (y1 - y0) * (0.42 + 0.22 * math.cos(t * 3.2) * math.exp(-((t % 4.0) * 0.35)))
    line(d, [(cx - 150, top), (cx + 150, top)], INK, 8)
    pts = [(cx + (45 if i % 2 else -45) * (0 < i < 20), top + ext * i / 20) for i in range(21)]
    line(d, pts, ACC, 6, 2)
    rect(d, cx - 70, top + ext, cx + 70, top + ext + 90, INK, 6, fill=(60, 45, 30), seed=3)
    line(d, [(cx + 120, top + (y1 - y0) * 0.42 + 45), (cx + 200, top + (y1 - y0) * 0.42 + 45)], POS, 5, 4)


def snowball(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    slope = [(x0 + 20, y0 + 80), (x1 - 20, y1 - 60)]
    line(d, slope, INK, 6)
    u = (t * 0.25) % 1.0
    x, y = slope[0][0] + u * (slope[1][0] - slope[0][0]), slope[0][1] + u * (slope[1][1] - slope[0][1])
    r = 18 + u * 110
    cx, cy = x + r * 0.45, y - r * 0.9
    circle(d, cx, cy, r, INK, 7, fill=(200, 210, 215))
    a = t * 5
    line(d, [(cx, cy), (cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a))], MUT, 4, 2)


def turbine(d, b, t, p):
    x0, y0, x1, y1 = b
    for k, (fx, sc) in enumerate(((0.3, 1.0), (0.72, 0.75))):
        cx, cy = x0 + (x1 - x0) * fx, y0 + 200 + (1 - sc) * 120
        L = 170 * sc
        line(d, [(cx, cy), (cx - 12, y1 - 40)], INK, 8, k)
        for j in range(3):
            a = t * 2.2 + j * 2 * math.pi / 3 + k
            line(d, [(cx, cy), (cx + L * math.cos(a), cy + L * math.sin(a))], ACC, 9, j + k * 3)
        circle(d, cx, cy, 14, INK, 5, fill=INK)
    for i in range(4):
        y = y0 + 120 + i * 90
        x = x0 + ((t * 0.5 + i * 0.3) % 1.0) * (x1 - x0)
        line(d, [(x - 60, y), (x, y)], MUT, 3, i)


def juggle(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, base = (x0 + x1) / 2, y1 - 160
    for k, c in enumerate((ACC, POS, NEU, NEG)):
        u = (t * 0.8 + k / 4) % 1.0
        side = 1 if int(t * 0.8 + k / 4) % 2 else -1
        x = cx + side * (1 - 2 * u) * 170
        y = base - math.sin(u * math.pi) * (y1 - y0) * 0.6
        circle(d, x, y, 30, c, 6, fill=c, seed=k)
    line(d, [(cx - 200, base + 40), (cx - 120, base + 10)], INK, 8)
    line(d, [(cx + 200, base + 40), (cx + 120, base + 10)], INK, 8, 1)


def rowing(d, b, t, p):
    x0, y0, x1, y1 = b
    cy = (y0 + y1) / 2 + 60
    bob = 6 * math.sin(t * 3)
    hull = [(x0 + 60, cy + bob), (x1 - 60, cy + bob), (x1 - 120, cy + 60 + bob), (x0 + 120, cy + 60 + bob), (x0 + 60, cy + bob)]
    line(d, hull, ACC, 7)
    a = math.sin(t * 3.2) * 0.6
    for k in range(5):
        x = x0 + 170 + k * (x1 - x0 - 340) / 4
        circle(d, x, cy - 60 + bob, 20, INK, 5, fill=INK, seed=k)
        line(d, [(x, cy - 40 + bob), (x - 140 * math.cos(1.1 + a), cy + 20 + 140 * math.sin(1.1 + a) + bob)], NEU, 6, k + 5)
    for i in range(6):
        wx = x0 + ((i / 6 - t * 0.3) % 1.0) * (x1 - x0)
        line(d, [(wx, cy + 110), (wx + 50, cy + 100), (wx + 100, cy + 110)], (120, 170, 190), 4, i)


def brownian(d, b, t, p):
    x0, y0, x1, y1 = b
    rnd = random.Random(21)
    for k in range(3):
        x, y = (x0 + x1) / 2 + (k - 1) * 120, (y0 + y1) / 2
        pts = [(x, y)]
        steps = int(40 + t * 25)
        for i in range(steps):
            x += rnd.gauss(0, 14); y += rnd.gauss(0, 14)
            x = min(max(x, x0 + 20), x1 - 20); y = min(max(y, y0 + 20), y1 - 20)
            pts.append((x, y))
        line(d, pts[-70:], (ACC, POS, NEU)[k], 3, k)
        circle(d, x, y, 22, (ACC, POS, NEU)[k], 5, fill=(ACC, POS, NEU)[k], seed=k)


def tug(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 80
    shift = 70 * math.sin(t * 1.4) + 30 * math.sin(t * 3.7)
    line(d, [(x0 + 60, cy), (x1 - 60, cy)], NEU, 7)
    line(d, [(cx, cy - 160), (cx, cy + 160)], MUT, 3, 1)
    line(d, [(cx + shift, cy - 30), (cx + shift, cy + 30)], NEG, 10, 2)
    for side, c in ((-1, ACC), (1, POS)):
        for k in range(3):
            x = cx + shift + side * (150 + k * 95)
            lean = side * 0.35
            circle(d, x + 40 * lean, cy - 120, 22, c, 5, fill=c, seed=k)
            line(d, [(x + 40 * lean, cy - 98), (x, cy - 10), (x - side * 20, cy + 80)], c, 7, k + 4)


def orbit(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) * 0.28
    a = t * 1.3
    for k, (c, r) in enumerate(((ACC, 42), (POS, 30))):
        ang = a + k * math.pi
        rr = R * (0.8 if k == 0 else 1.2)
        trail = [(cx + rr * math.cos(ang - i * 0.06), cy + rr * 0.55 * math.sin(ang - i * 0.06)) for i in range(40)]
        line(d, trail, (*c, 120), 4, k)
        circle(d, trail[0][0], trail[0][1], r, c, 6, fill=c, seed=k)
    line(d, [(cx - 6, cy), (cx + 6, cy)], MUT, 4, 3)


KINDS = {"dice": dice, "coin": coin, "galton": galton, "wave": wave, "crash": crash, "orderbook": orderbook,
         "leash": leash, "vectors": vectors, "matrix": matrix, "scale": scale, "compound": compound,
         "pendulum": pendulum, "cone": cone, "dominoes": dominoes, "gears": gears, "thermometer": thermometer,
         "network": network, "bell": bell, "skew": skew, "ripple": ripple, "rain": rain, "spring": spring,
         "snowball": snowball, "turbine": turbine, "juggle": juggle, "rowing": rowing, "brownian": brownian, "tug": tug,
         "orbit": orbit}


def draw(img, kind, box, t, p):
    d = ImageDraw.Draw(img, "RGBA")
    KINDS.get(kind, network)(d, box, t, p)


# ---------------------------------------------------------------- overlays: hand-drawn motion on every scene
def _partial(pts, k):
    """First fraction k of a polyline (draw-on effect)."""
    if k <= 0 or len(pts) < 2:
        return []
    L = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    budget, out = sum(L) * min(1, k), [pts[0]]
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if budget >= l:
            out.append(b); budget -= l
        else:
            f = budget / max(l, 1e-9)
            out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)); break
    return out


def hand_loop(d, cx, cy, rx, ry, k, color=NEU, w=7, seed=0):
    pts = [(cx + rx * (1 + 0.06 * math.sin(i * 0.9)) * math.cos(-0.4 + 2.15 * math.pi * i / 60),
            cy + ry * (1 + 0.06 * math.cos(i * 0.7)) * math.sin(-0.4 + 2.15 * math.pi * i / 60)) for i in range(61)]
    line(d, _partial(pts, k), color, w, seed)


def hand_arrow(d, x0, y0, x1, y1, k, color=NEU, w=8, seed=0):
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.25, (y0 + y1) / 2 - (x1 - x0) * 0.25
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1)
           for u in [i / 30 for i in range(31)]]
    part = _partial(pts, k)
    line(d, part, color, w, seed)
    if k >= 1:
        (ax, ay), (bx, by) = pts[-4], pts[-1]
        a = math.atan2(by - ay, bx - ax)
        line(d, [(bx - 34 * math.cos(a - 0.5), by - 34 * math.sin(a - 0.5)), (bx, by),
                 (bx - 34 * math.cos(a + 0.5), by - 34 * math.sin(a + 0.5))], color, w, seed + 1)


def hand_underline(d, x0, x1, y, k, color=NEU, w=7, seed=0):
    pts = [(x0 + (x1 - x0) * u, y + 6 * math.sin(u * 9 + seed)) for u in [i / 40 for i in range(41)]]
    line(d, _partial(pts, k), color, w, seed)
    if k > 0.6:
        pts2 = [(x0 + 30 + (x1 - x0 - 60) * u, y + 16 + 5 * math.sin(u * 7 + 2)) for u in [i / 40 for i in range(41)]]
        line(d, _partial(pts2, (k - 0.6) / 0.4), color, w - 2, seed + 5)


def star(d, x, y, r, t, color=NEU):
    s = r * (0.8 + 0.25 * math.sin(t * 7 + x))
    line(d, [(x - s, y), (x + s, y)], color, 5)
    line(d, [(x, y - s), (x, y + s)], color, 5, 1)
    line(d, [(x - s * 0.6, y - s * 0.6), (x + s * 0.6, y + s * 0.6)], color, 3, 2)


def mini(img, kind, box, t, p, alpha=200):
    """Small hand-drawn animation in a translucent rounded card (on photos, hook, takeaway)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(box, radius=22, fill=(10, 20, 16, alpha), outline=(*NEU, 160), width=3)
    KINDS.get(kind, network)(d, (x0 + 18, y0 + 18, x1 - 18, y1 - 18), t, p)


def _seg(p, a, b):
    return max(0.0, min(1.0, (p - a) / max(1e-6, b - a)))


def decorate(scenes, kind):
    """Wrap scene draws with hand-drawn motion. Purely visual: no words, no numbers (QA unaffected)."""
    X0, X1, BOT = 60, 940, 1310
    for s in scenes:
        inner, nm = s.draw, s.name

        def wrap(inner=inner, nm=nm):
            def draw(img, t, p):
                inner(img, t, p)
                d = ImageDraw.Draw(img, "RGBA")
                if nm == "hook":
                    mini(img, kind, (X1 - 270, 300, X1, 505), t, min(1, p * 1.4), alpha=150)
                elif nm == "code":
                    y = 380 + 650 * ease(_seg(p, 0, 0.85))
                    line(d, [(8, y), (50, y)], ACC, 7, 1)
                    line(d, [(34, y - 14), (52, y), (34, y + 14)], ACC, 7, 2)
                elif nm == "run":
                    k = _seg(p, 0.82, 0.97)
                    if k > 0:
                        hand_underline(d, 290, 790, BOT - 70, k, NEU, 7, 3)
                        star(d, X0 + 70, BOT - 210, 22 * k, t)
                        star(d, X1 - 70, BOT - 250, 18 * k, t + 1)
                elif nm in ("chart", "evidence"):
                    hand_loop(d, X1 - 170, 640, 150, 240, _seg(p, 0.72, 0.9), NEU, 6, 4)
                    hand_arrow(d, X0 + 90, 1150, X1 - 300, 820, _seg(p, 0.6, 0.78), NEU, 7, 6)
                elif nm == "surface3d":
                    hand_arrow(d, X0 + 60, 520, X0 + 330, 640, _seg(p, 0.35, 0.6), NEU, 7, 8)
                elif nm.startswith("broll"):
                    mini(img, kind, (X1 - 300, 900, X1 - 20, 1180), t, min(1, p * 1.3), alpha=185)
                elif nm == "takeaway":
                    mini(img, kind, (X1 - 250, 300, X1, 500), t, min(1, p * 1.5), alpha=170)
                    hand_underline(d, X0, X0 + 520, 1265, _seg(p, 0.2, 0.55), ACC, 7, 9)
            return draw

        s.draw = wrap()
    return scenes
