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


KINDS = {"dice": dice, "coin": coin, "galton": galton, "wave": wave, "crash": crash, "orderbook": orderbook,
         "leash": leash, "vectors": vectors, "matrix": matrix, "scale": scale, "compound": compound,
         "pendulum": pendulum, "cone": cone, "dominoes": dominoes, "gears": gears, "thermometer": thermometer,
         "network": network, "bell": bell, "skew": skew}


def draw(img, kind, box, t, p):
    d = ImageDraw.Draw(img, "RGBA")
    KINDS.get(kind, network)(d, box, t, p)
