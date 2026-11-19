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
        h = landed[k] * (H * 0.42 / 66)        # scaled to the box: the tallest bin ends ~42% of its height
        d.rectangle([x - bw * 0.42, base - h, x + bw * 0.42, base], fill=(255, 145, 77, 255))
        line(d, [(x - bw / 2, base), (x - bw / 2, base - H * 0.45)], (60, 80, 70), 3, k)
    fly = 1.0 - ease((p - 0.9) / 0.1)       # balls in flight fade out at the end instead of vanishing
    for j in range(5):  # balls in flight
        i = min(shown + j, 239)
        if fly <= 0:
            break
        f = (t * 2.4 + j / 5) % 1.0
        r = int(f * rows)
        pos = sum(paths[i][:r]) - r / 2
        bx, by = cx + pos * bw, y0 + 70 + f * rows * dy
        d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(*NEU, int(255 * fly)))
    if p > 0.75:
        pts = [(cx + (k - rows / 2) * bw, base - (H * 0.42 / 66) * 240 * math.comb(rows, k) / 2 ** rows) for k in range(nb)]
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
    """Calm climb, then the plunge (from p≈0.6, as the narration reaches the crash)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    k = ease(min(1.0, p / 0.85))
    n = max(2, int(160 * k))
    pts = []
    for i in range(n):
        u = i / 159
        y = y0 + H * (0.55 - 0.25 * u + 0.04 * math.sin(u * 40)) if u < 0.7 else y0 + H * (0.38 + (u - 0.7) * 1.8)
        pts.append((x0 + 30 + u * (W - 60), y))
    red = max(0.0, min(1.0, (p - 0.55) / 0.25))  # colour fades green → red, no pop
    col = tuple(int(POS[c] + (NEG[c] - POS[c]) * red) for c in range(3))
    shake = 2.5 * math.sin(t * 30) * max(0.0, 1 - abs(p - 0.75) / 0.08) if 0.67 < p < 0.83 else 0
    line(d, [(x + shake, y) for x, y in pts], col, 7)
    a = ease((p - 0.75) / 0.15)
    if a > 0:
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
    """Row × column sweep; the highlight glides from cell to cell and result cells fill in gradually."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n, s_ = 3, min(W / 11.2, H * 0.13)
    ox, oy = x0 + W * 0.1, y0 + H * 0.3
    pos = ease(min(1.0, p / 0.9)) * (n * n - 1e-6)   # continuous position 0..9 over the scene
    step, frac = int(pos), pos - int(pos)
    r, c = divmod(step, n)
    def mix(a, b_, f):
        return tuple(int(a[i] + (b_[i] - a[i]) * f) for i in range(3))
    pr, pc = divmod(max(0, step - 1), n)
    fin = ease(min(1.0, frac / 0.35))                 # new highlight fades in while the old one fades out
    for g, gx in ((0, ox), (1, ox + s_ * 3.6), (2, ox + s_ * 7.4)):
        for i in range(n):
            for j in range(n):
                cur = (g == 0 and i == r) or (g == 1 and j == c) or (g == 2 and i == r and j == c)
                old = step > 0 and ((g == 0 and i == pr) or (g == 1 and j == pc) or (g == 2 and i == pr and j == pc))
                w = max(fin if cur else 0.0, (1 - fin) if old else 0.0)
                idx = i * n + j
                fill_k = 1.0 if (g == 2 and idx < step) else (frac if (g == 2 and idx == step) else 0.0)
                col = mix(MUT, ACC, w)
                fill = mix((16, 30, 24), (60, 45, 30), max(fill_k, 0.7 * w))
                rect(d, gx + j * s_, oy + i * s_, gx + (j + 1) * s_ - 8, oy + (i + 1) * s_ - 8, col, 3 + int(2 * w),
                     fill=fill, seed=i * 3 + j)
    line(d, [(ox + s_ * 3.05, oy + s_ * 1.2), (ox + s_ * 3.35, oy + s_ * 1.6)], INK, 6)
    line(d, [(ox + s_ * 3.35, oy + s_ * 1.2), (ox + s_ * 3.05, oy + s_ * 1.6)], INK, 6, 2)
    line(d, [(ox + s_ * 6.85, oy + s_ * 1.25), (ox + s_ * 7.2, oy + s_ * 1.25)], INK, 6, 3)
    line(d, [(ox + s_ * 6.85, oy + s_ * 1.55), (ox + s_ * 7.2, oy + s_ * 1.55)], INK, 6, 4)

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
    """Coin stacks grow year by year, each stack rising smoothly; the growth curve follows the tops."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    n = 12
    pos = ease(min(1.0, p / 0.9)) * n
    tops = []
    for i in range(n):
        g = max(0.0, min(1.0, pos - i))
        if g <= 0:
            break
        coins = (18 * 1.32 ** i / 18) * g
        x = x0 + 40 + i * (W - 80) / n
        full = int(coins)
        for j in range(full + (1 if coins - full > 0.05 else 0)):
            y = y1 - 40 - j * 16
            d.ellipse([x, y - 10, x + (W - 80) / n - 10, y + 10], fill=(150, 120, 40), outline=NEU, width=3)
        tops.append((x + 30, y1 - 40 - 16 * max(0, coins - 1)))
    if len(tops) > 1:
        line(d, tops, ACC, 6, 3)

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
    front = ease(min(1.0, p / 0.9)) * (n + 2)
    for i in range(n):
        x = x0 + 60 + i * (W - 120) / n
        ang = 1.15 * ease((front - i) / 1.6)          # each piece tips over smoothly
        h = H * 0.38
        bx, by = x, y1 - 80
        tx, ty = bx + h * math.sin(ang), by - h * math.cos(ang)
        col = tuple(int(INK[c] + (ACC[c] - INK[c]) * min(1, ang / 1.15)) for c in range(3))
        line(d, [(bx, by), (tx, ty)], col, 26, i)
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
    k = ease((p - 0.6) / 0.2)
    if k > 0:
        y = top + (bot - top) * 0.2
        line(d, _partial([(cx + 100, y), (x1 - 40, y)], k), NEG, 5, 9)


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
    tail = ease((p - 0.6) / 0.15)
    if tail > 0:  # tails glow in, then pulse: where the risk lives
        fl = (0.5 + 0.5 * math.sin(t * 5)) * tail
        for side in (0, 1):
            xs = range(0, 30) if side == 0 else range(130, 160)
            poly = [(x0 + 30 + (W - 60) * i / 159, base - H * 0.7 * math.exp(-((i / 159 - 0.5) ** 2) / 0.018)) for i in xs]
            poly = poly + [(poly[-1][0], base), (poly[0][0], base)]
            d.polygon(poly, fill=(int(120 + 100 * fl), 50, 55, int(255 * tail)))
    line(d, pts, ACC, 7)


def skew(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    base = y1 - 60
    n = 18
    for i in range(n):
        u = i / (n - 1)
        grow = ease((p * 1.4 - u * 0.6) / 0.4)        # bars rise, left to right
        if grow <= 0:
            continue
        h = H * 0.65 * (math.exp(-((u - 0.78) ** 2) / 0.006) + 0.05 * (u < 0.3)) * grow
        x = x0 + 40 + u * (W - 100)
        d.rectangle([x, base - h, x + (W - 100) / n - 6, base], fill=NEG if u < 0.3 else ACC)
    line(d, [(x0 + 30, base), (x1 - 30, base)], MUT, 4)
    k = ease((p - 0.65) / 0.2)
    if k > 0:
        line(d, _partial([(x0 + W * 0.45, y0 + H * 0.35), (x0 + 70, base - 40)], k), NEG, 7, 3)

def ripple(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, y0 + H * 0.62
    d.ellipse([x0 + 10, cy - H * 0.3, x1 - 10, cy + H * 0.3], fill=(25, 55, 70))
    for k in range(6):
        r = ((t * 0.55 + k / 6) % 1.0)
        R = 30 + r * W * 0.46
        a = int(255 * (1 - r) ** 1.2)
        d.ellipse([cx - R, cy - R * 0.32, cx + R, cy + R * 0.32], outline=(*NEU, a), width=max(2, int(8 * (1 - r))))
    ph = (t * 0.55) % 1.0
    if ph > 0.7:  # stone falling
        y = cy - (1 - (ph - 0.7) / 0.3) * H * 0.55
        circle(d, cx, y, 22, INK, 5, fill=(120, 110, 100))
    elif ph < 0.25:  # splash
        for j in range(7):
            a = math.pi + j * math.pi / 6
            u = ph / 0.25
            line(d, [(cx + 20 * math.cos(a), cy - 10), (cx + (20 + 90 * u) * math.cos(a), cy - 10 - 120 * u * math.sin(-a) * (1 - u))],
                 (180, 220, 235), 5, j)


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
    """Pulled down at first, released at p≈0.3, then a damped bounce back to rest (no periodic reset)."""
    x0, y0, x1, y1 = b
    cx, top = (x0 + x1) / 2, y0 + 50
    rest = (y1 - y0) * 0.42
    if p < 0.3:
        ext = rest * (1 + 0.45 * ease(p / 0.3))
    else:
        tt = (p - 0.3) * 6.0
        ext = rest * (1 + 0.45 * math.exp(-tt * 0.9) * math.cos(tt * 4.2))
    line(d, [(cx - 150, top), (cx + 150, top)], INK, 8)
    pts = [(cx + (45 if i % 2 else -45) * (0 < i < 20), top + ext * i / 20) for i in range(21)]
    line(d, pts, ACC, 6, 2)
    rect(d, cx - 70, top + ext, cx + 70, top + ext + 90, INK, 6, fill=(60, 45, 30), seed=3)
    line(d, [(cx + 120, top + rest + 45), (cx + 200, top + rest + 45)], POS, 5, 4)
    if p < 0.3:  # hand pulling
        hy = top + ext + 110
        line(d, [(cx, top + ext + 90), (cx, hy)], INK, 5, 5)
        circle(d, cx, hy + 18, 20, INK, 5, fill=(235, 205, 170), seed=6)

def snowball(d, b, t, p):
    """One roll down the slope over the scene: small → big, then it hits the tree (no loop, no teleport)."""
    x0, y0, x1, y1 = b
    slope = [(x0 + 20, y0 + 80), (x1 - 120, y1 - 60)]
    line(d, slope, INK, 6)
    tx, ty = x1 - 70, y1 - 60
    line(d, [(tx, ty), (tx, ty - 200)], (120, 90, 60), 16, 3)
    circle(d, tx, ty - 230, 60, POS, 5, fill=(40, 90, 60), seed=4)
    u = ease(min(1.0, p / 0.85)) * 0.92
    x, y = slope[0][0] + u * (slope[1][0] - slope[0][0]), slope[0][1] + u * (slope[1][1] - slope[0][1])
    r = 18 + u * 110
    hit = max(0.0, (p - 0.85) / 0.15)
    cx, cy = x + r * 0.45 + 6 * math.sin(t * 50) * hit, y - r * 0.9
    circle(d, cx, cy, r, INK, 7, fill=(200, 210, 215))
    a = u * 18
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


def scientist(d, b, t, p):
    """Cartoon person at a chalkboard, writing (stands in for any historical figure; name comes from the label)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    bx0, by0, bx1, by1 = x0 + W * 0.38, y0 + 30, x1 - 20, y0 + H * 0.62
    d.rectangle([bx0, by0, bx1, by1], fill=(22, 52, 40))
    rect(d, bx0, by0, bx1, by1, (120, 90, 60), 8, seed=1)
    k = min(1.0, p * 1.3)
    for row in range(4):  # chalk "formula" squiggles appear line by line
        fr = max(0.0, min(1.0, k * 4 - row))
        if fr <= 0:
            break
        yy = by0 + 50 + row * (by1 - by0 - 80) / 4
        pts = [(bx0 + 30 + u * (bx1 - bx0 - 60) * fr, yy + 10 * math.sin(u * 22 + row * 2)) for u in [i / 30 for i in range(31)]]
        line(d, pts, INK if row % 2 else NEU, 5, row + 3)
    cx, cy = x0 + W * 0.22, y0 + H * 0.38
    circle(d, cx, cy, 62, INK, 7, fill=(235, 205, 170))                   # head
    line(d, [(cx - 60, cy - 30), (cx - 30, cy - 70), (cx, cy - 62), (cx + 35, cy - 72), (cx + 62, cy - 28)], MUT, 9, 2)  # hair
    circle(d, cx - 22, cy - 5, 14, INK, 4); circle(d, cx + 22, cy - 5, 14, INK, 4)  # glasses
    line(d, [(cx - 8, cy - 5), (cx + 8, cy - 5)], INK, 4, 4)
    line(d, [(cx - 18, cy + 30), (cx, cy + 36), (cx + 18, cy + 30)], INK, 4, 5)       # smile
    body = [(cx - 85, y1 - 20), (cx - 70, cy + 80), (cx + 70, cy + 80), (cx + 85, y1 - 20)]
    d.polygon(body, fill=(60, 80, 110)); line(d, body, INK, 6, 6)
    tipx = bx0 + 30 + (bx1 - bx0 - 60) * ((k * 4) % 1.0) * 0.9
    tipy = by0 + 50 + min(3, int(k * 4)) * (by1 - by0 - 80) / 4
    line(d, [(cx + 60, cy + 110), (cx + 150, cy + 60), (tipx, tipy)], INK, 9, 7)      # writing arm
    d.ellipse([tipx - 9, tipy - 9, tipx + 9, tipy + 9], fill=INK)


def crowd(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    rnd = random.Random(4)
    for i in range(22):
        bx = x0 + 40 + rnd.random() * (W - 80)
        by = y0 + H * 0.35 + rnd.random() * H * 0.55
        jump = abs(math.sin(t * (3 + rnd.random() * 3) + i)) * 18
        c = (ACC, POS, NEU, INK, NEG)[i % 5]
        circle(d, bx, by - 70 - jump, 16, c, 4, fill=c, seed=i)
        line(d, [(bx, by - 54 - jump), (bx, by - 10 - jump)], c, 6, i)
        arm = 0.8 * math.sin(t * 5 + i)
        line(d, [(bx - 26, by - 60 - jump + 20 * arm), (bx, by - 40 - jump), (bx + 26, by - 60 - jump - 20 * arm)], c, 5, i + 1)
        line(d, [(bx - 14, by - jump), (bx, by - 12 - jump), (bx + 14, by - jump)], c, 5, i + 2)


def storm(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    for k, (fx, fy, r) in enumerate(((0.3, 0.2, 90), (0.5, 0.15, 120), (0.72, 0.22, 95))):
        cx = x0 + W * fx + 15 * math.sin(t + k)
        circle(d, cx, y0 + H * fy, r, MUT, 6, fill=(70, 80, 90), seed=k)
    if (t * 1.3) % 1.0 < 0.18:
        lx = x0 + W * 0.5
        pts = [(lx, y0 + H * 0.3), (lx - 40, y0 + H * 0.5), (lx + 20, y0 + H * 0.52), (lx - 30, y0 + H * 0.8)]
        line(d, pts, NEU, 10, 3)
    rnd = random.Random(2)
    for i in range(45):
        x = x0 + rnd.random() * W
        y = y0 + H * 0.35 + ((rnd.random() + t * 1.4) % 1.0) * H * 0.6
        line(d, [(x, y), (x - 14, y + 30)], (150, 190, 210), 4, i)


def volcano(d, b, t, p):
    """Quiet mountain, a wisp of smoke… then it erupts from p≈0.55 (matches 'yên bình… rồi một ngày')."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    cx = x0 + W / 2
    mount = [(x0 + 40, y1 - 30), (cx - 70, y0 + H * 0.45), (cx + 70, y0 + H * 0.45), (x1 - 40, y1 - 30)]
    d.polygon(mount, fill=(70, 55, 45)); line(d, mount, INK, 7)
    erupt = ease((p - 0.55) / 0.2)
    rnd = random.Random(8)
    for i in range(30):
        ph = rnd.random()
        u = (t * 0.8 + ph) % 1.0
        ang = -math.pi / 2 + (rnd.random() - 0.5) * 1.6
        v = 420 * (0.6 + rnd.random() * 0.6) * erupt
        if v < 5:
            continue
        x = cx + math.cos(ang) * v * u
        y = y0 + H * 0.45 + math.sin(ang) * v * u + 520 * u * u * erupt
        if y < y0 + 10:
            continue
        r = (10 + 10 * (1 - u)) * erupt
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, int(120 + 100 * (1 - u)), 40))
    for k in range(3):  # smoke puffs rise and fade out (no pop at the edge)
        ph = (t * 0.3 + k / 3) % 1.0
        sy = y0 + H * 0.42 - ph * H * 0.3
        rr = (18 + 10 * k) * (1 + 1.4 * erupt) * (0.6 + 0.6 * ph)
        al = int(200 * math.sin(math.pi * ph))
        d.ellipse([cx + 30 * math.sin(t + k) - rr, sy - rr, cx + 30 * math.sin(t + k) + rr, sy + rr], fill=(90, 90, 90, al))

def bigwave(d, b, t, p):
    """Calm sea, then one huge wave rolls in from the left and over the houses (p≈0.4 → 0.9)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    crest = x0 - W * 0.2 + ease((p - 0.35) / 0.55) * W * 1.1
    pts = []
    for i in range(80):
        x = x0 + i * W / 79
        h = H * 0.12 + H * 0.02 * math.sin(i * 0.5 + t * 3) + H * 0.55 * math.exp(-((x - crest) / (W * 0.15)) ** 2)
        pts.append((x, y1 - 40 - h))
    d.polygon(pts + [(x1, y1 - 30), (x0, y1 - 30)], fill=(40, 90, 120))
    line(d, pts, (190, 230, 240), 7)
    for hx in [x0 + W * u for u in (0.2, 0.45, 0.7, 0.9)]:
        rect(d, hx - 30, y1 - 120, hx + 30, y1 - 40, INK, 5, seed=int(hx))
        line(d, [(hx - 38, y1 - 118), (hx, y1 - 160), (hx + 38, y1 - 118)], INK, 5, int(hx) + 1)

def bridge(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    twist = math.sin(t * 2.4) * 40 * min(1, p * 1.5)
    for tx in (x0 + W * 0.25, x0 + W * 0.75):
        line(d, [(tx, y1 - 40), (tx, y0 + 80)], INK, 12, int(tx))
    deck = [(x0 + 20 + u * (W - 40), y0 + H * 0.6 + twist * math.sin(u * math.pi * 2)) for u in [i / 40 for i in range(41)]]
    line(d, deck, ACC, 12)
    cable = [(x0 + 20 + u * (W - 40), y0 + 80 + (H * 0.5) * (2 * u - 1) ** 2 * 0.8 + twist * 0.3 * math.sin(u * 6)) for u in [i / 40 for i in range(41)]]
    line(d, cable, MUT, 5, 3)
    for i in range(6):
        wx = x0 + ((t * 0.6 + i / 6) % 1.0) * W
        line(d, [(wx - 70, y0 + 60 + i * 25), (wx, y0 + 55 + i * 25)], (140, 170, 180), 3, i)


def medal(d, b, t, p):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 40
    spin = 1 - ease(min(1.0, p / 0.6))                 # spins in, then faces the viewer
    sq = abs(math.cos(spin * 7))
    line(d, [(cx - 60, y0 + 30), (cx, cy - 150)], (60, 100, 180), 14)
    line(d, [(cx + 60, y0 + 30), (cx, cy - 150)], (180, 60, 60), 14, 1)
    d.ellipse([cx - 150 * sq, cy - 150, cx + 150 * sq, cy + 150], fill=(200, 160, 50), outline=NEU, width=8)
    if sq > 0.5:
        circle(d, cx, cy, 95 * sq, (150, 110, 30), 5)
    for k in range(5):
        a = t * 1.2 + k * 1.25
        star(d, cx + 230 * math.cos(a), cy + 180 * math.sin(a), 16 * ease((p - 0.5) / 0.3), t + k)

def roulette(d, b, t, p):
    """Wheel spins fast, slows down and stops as the scene ends."""
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = min(x1 - x0, y1 - y0) * 0.42
    q = min(1.0, p)
    a0 = 9.0 * (q - q * q / 2) * 2          # angle = ∫ speed, speed falls linearly to 0
    for k in range(18):
        a, a2 = a0 + k * 2 * math.pi / 18, a0 + (k + 1) * 2 * math.pi / 18
        d.polygon([(cx, cy), (cx + R * math.cos(a), cy + R * math.sin(a)), (cx + R * math.cos(a2), cy + R * math.sin(a2))],
                  fill=(170, 40, 45) if k % 2 else (25, 25, 25))
    circle(d, cx, cy, R, NEU, 8)
    circle(d, cx, cy, R * 0.3, NEU, 6, fill=(90, 60, 30))
    ba = -14.0 * (q - q * q / 2) * 2
    rr = R * (0.88 - 0.12 * ease((p - 0.7) / 0.3))
    bx, by = cx + rr * math.cos(ba), cy + rr * math.sin(ba)
    d.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=INK)

def ticker(d, b, t, p):
    """Exchange board: rows of blinking prices scrolling (stock exchange, trading floor, screens)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], fill=(10, 14, 12))
    rnd = random.Random(1)
    rows = 9
    for r in range(rows):
        y = y0 + 40 + r * (H - 80) / rows
        off = (t * 120 * (1 + r % 3 * 0.3)) % (W * 0.5)
        for c in range(6):
            x = x0 + 30 + c * W * 0.25 - off
            if x < x0 + 20 or x > x1 - 120:
                continue
            up = rnd.random() < 0.5 if int(t * 2 + r + c) % 3 else not (rnd.random() < 0.5)
            col = POS if up else NEG
            d.rectangle([x, y, x + 90, y + 26], fill=(30, 40, 35))
            line(d, [(x + 100, y + (20 if up else 6)), (x + 112, y + (6 if up else 20)), (x + 124, y + (20 if up else 6))], col, 5, r * 7 + c)


def ship(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    sx = x0 + ((t * 0.12) % 1.0) * W * 0.6 + W * 0.05
    sea = y0 + H * 0.65
    bob = 8 * math.sin(t * 2)
    hull = [(sx, sea + bob), (sx + 380, sea + bob), (sx + 330, sea + 70 + bob), (sx + 40, sea + 70 + bob)]
    d.polygon(hull, fill=(150, 60, 50)); line(d, hull + [hull[0]], INK, 6)
    for k in range(4):
        rect(d, sx + 50 + k * 70, sea - 50 + bob, sx + 110 + k * 70, sea + bob, INK, 4,
             fill=((60, 110, 160), (200, 140, 50), (70, 140, 90), (170, 70, 70))[k], seed=k)
    for i in range(8):
        wx = sx - 30 - i * 45
        line(d, [(wx, sea + 60 + 6 * math.sin(t * 4 + i)), (wx + 40, sea + 55)], (170, 210, 225), 4, i)
    for i in range(7):
        wx = x0 + ((i / 7 - t * 0.2) % 1.0) * W
        line(d, [(wx, sea + 110), (wx + 50, sea + 100), (wx + 100, sea + 110)], (120, 170, 190), 4, i + 9)


def building(d, b, t, p):
    """Classical facade (bank, exchange, treasury, university)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    roof = [(x0 + 60, y0 + H * 0.3), (x0 + W / 2, y0 + 50), (x1 - 60, y0 + H * 0.3)]
    line(d, roof + [roof[0]], NEU, 8)
    n = 6
    for k in range(n):
        x = x0 + 100 + k * (W - 200) / (n - 1)
        hgt = min(1.0, p * 2 - k * 0.12)
        if hgt > 0:
            line(d, [(x, y1 - 60), (x, y1 - 60 - (y1 - 60 - y0 - H * 0.32) * hgt)], INK, 16, k)
    line(d, [(x0 + 40, y1 - 50), (x1 - 40, y1 - 50)], INK, 9, 9)
    for k in range(3):
        fy = y0 + 20 + 6 * math.sin(t * 3 + k)
        line(d, [(x0 + W / 2, y0 + 50), (x0 + W / 2, fy - 40)], MUT, 4, 12)
    line(d, [(x0 + W / 2, y0 - 10), (x0 + W / 2 + 70, y0 + 5 + 10 * math.sin(t * 4)), (x0 + W / 2, y0 + 20)], ACC, 6, 13)


def newspaper(d, b, t, p):
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    spin = 1 - ease(min(1.0, p / 0.45))
    sc = 1 - 0.7 * spin
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = W * 0.7 * sc, H * 0.8 * sc
    a = spin * 6
    def rot(px, py):
        return (cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a))
    d.polygon([rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)], fill=(225, 220, 205))
    k = ease((p - 0.45) / 0.35)                        # print appears progressively once the paper lands
    if k > 0:
        d.rectangle([cx - w / 2 + 30, cy - h / 2 + 30, cx - w / 2 + 30 + (w - 60) * min(1, k * 2), cy - h / 2 + 110], fill=(30, 30, 30))
        line(d, _partial([(cx - w / 2 + 40, cy - h / 2 + 160), (cx + w / 2 - 40, cy - h / 2 + 160)], k * 1.5), NEG, 14, 1)
        for r in range(7):
            kk = max(0.0, min(1.0, k * 8 - r))
            yy = cy - h / 2 + 210 + r * 40
            x_end = cx + (w / 2 - 40) * (0.4 if r % 3 == 2 else 1)
            line(d, _partial([(cx - w / 2 + 40, yy), (x_end, yy)], kk), (110, 110, 110), 6, r + 2)
        k2 = ease((p - 0.8) / 0.15)
        line(d, _partial([(cx + w * 0.05, cy + h * 0.05), (cx + w * 0.4, cy - h * 0.15), (cx + w * 0.42, cy + h * 0.3)], k2), NEG, 9, 9)

def car(d, b, t, p):
    """Traffic / cars moving (traffic jam, roads, toll booth)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    for lane in range(3):
        y = y0 + H * (0.3 + lane * 0.22)
        line(d, [(x0 + 10, y + 60), (x1 - 10, y + 60)], MUT, 3, lane)
        for k in range(4):
            sp = 0.08 + lane * 0.05
            x = x0 + ((k / 4 + t * sp) % 1.0) * (W + 200) - 150
            c = (ACC, POS, NEU, NEG)[(k + lane) % 4]
            d.rounded_rectangle([x, y, x + 140, y + 50], radius=14, fill=c)
            d.ellipse([x + 15, y + 38, x + 45, y + 68], fill=INK); d.ellipse([x + 95, y + 38, x + 125, y + 68], fill=INK)


def sun(d, b, t, p):
    """Sun / heat / summer (sunspots, beach, ice cream, hot days)."""
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - 40
    for k in range(16):
        a = t * 0.6 + k * math.pi / 8
        r1, r2 = 150, 210 + 25 * math.sin(t * 4 + k)
        line(d, [(cx + r1 * math.cos(a), cy + r1 * math.sin(a)), (cx + r2 * math.cos(a), cy + r2 * math.sin(a))], NEU, 8, k)
    circle(d, cx, cy, 120, NEU, 8, fill=(240, 180, 60))
    for k in range(3):
        sx = cx - 50 + k * 45 + 10 * math.sin(t + k)
        d.ellipse([sx - 12, cy - 20 + k * 20, sx + 12, cy + 4 + k * 20], fill=(150, 90, 30))
    line(d, [(x0 + 30, y1 - 50), (x1 - 30, y1 - 50)], (120, 170, 190), 5)


def banknote(d, b, t, p):
    """Old banknote with a portrait and the bell curve printed on it (Gauss on the 10 Mark)."""
    x0, y0, x1, y1 = b
    W, H = x1 - x0, y1 - y0
    tilt = 0.06 * math.sin(t * 1.5)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = W * 0.86, H * 0.62
    def rot(px, py):
        return (cx + px * math.cos(tilt) - py * math.sin(tilt), cy + px * math.sin(tilt) + py * math.cos(tilt))
    note = [rot(-w / 2, -h / 2), rot(w / 2, -h / 2), rot(w / 2, h / 2), rot(-w / 2, h / 2)]
    d.polygon(note, fill=(150, 160, 120)); line(d, note + [note[0]], (70, 80, 50), 7)
    px, py = rot(-w * 0.25, 0)
    circle(d, px, py, h * 0.3, (60, 70, 45), 6, fill=(190, 195, 160))
    circle(d, px, py - h * 0.05, h * 0.12, (60, 70, 45), 5)
    line(d, [rot(-w * 0.36, h * 0.25), rot(-w * 0.25, h * 0.08), rot(-w * 0.14, h * 0.25)], (60, 70, 45), 5, 2)
    k = min(1.0, p * 1.4)
    pts = [rot(w * 0.02 + u * w * 0.42, h * 0.28 - h * 0.5 * math.exp(-((u - 0.5) ** 2) / 0.02)) for u in [i / 40 for i in range(int(41 * k))]]
    if len(pts) > 1:
        line(d, pts, (90, 40, 40), 6, 3)
    line(d, [rot(w * 0.02, h * 0.3), rot(w * 0.44, h * 0.3)], (60, 70, 45), 4, 4)
    for j in range(3):
        sx, sy = rot(w * 0.4 + 30 * math.sin(t * 3 + j), -h * 0.36)
        star(d, sx, sy, 10, t + j, NEU)


KINDS = {"dice": dice, "coin": coin, "galton": galton, "wave": wave, "crash": crash, "orderbook": orderbook,
         "leash": leash, "vectors": vectors, "matrix": matrix, "scale": scale, "compound": compound,
         "pendulum": pendulum, "cone": cone, "dominoes": dominoes, "gears": gears, "thermometer": thermometer,
         "network": network, "bell": bell, "skew": skew, "ripple": ripple, "rain": rain, "spring": spring,
         "snowball": snowball, "turbine": turbine, "juggle": juggle, "rowing": rowing, "brownian": brownian, "tug": tug,
         "orbit": orbit, "scientist": scientist, "crowd": crowd, "storm": storm, "volcano": volcano,
         "bigwave": bigwave, "bridge": bridge, "medal": medal, "roulette": roulette, "ticker": ticker, "ship": ship,
         "building": building, "newspaper": newspaper, "car": car, "sun": sun, "banknote": banknote}


def draw(img, kind, box, t, p):
    """Render on an off-screen layer at a comfortable size, then fit it into box: never spills outside the box,
    and small cards get the same composition as full scenes."""
    from PIL import Image

    x0, y0, x1, y1 = [int(v) for v in box]
    bw, bh = x1 - x0, y1 - y0
    f = max(1.0, 700 / max(1, bh))
    cw, ch = int(bw * f), int(bh * f)
    layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    KINDS.get(kind, network)(d, (0, 0, cw, ch), t, p)
    if f > 1:
        layer = layer.resize((bw, bh), Image.BILINEAR)
    img.paste(layer, (x0, y0), layer)


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
    """Small hand-drawn animation in a translucent rounded card (hook, takeaway)."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle(box, radius=22, fill=(10, 20, 16, alpha), outline=(*NEU, int(160 * alpha / 210)), width=3)
    draw(img, kind, (x0 + 14, y0 + 14, x1 - 14, y1 - 14), t, p)


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


# related animation to use when a cutaway would repeat the lesson's main animation
ALT = {"pendulum": "spring", "spring": "pendulum", "wave": "ripple", "ripple": "wave", "dice": "coin", "coin": "dice",
       "leash": "orbit", "orbit": "leash", "orderbook": "ticker", "ticker": "orderbook", "galton": "dice", "bell": "galton",
       "network": "brownian", "brownian": "network", "scale": "tug", "tug": "scale", "matrix": "vectors",
       "vectors": "matrix", "crash": "ticker", "cone": "storm", "compound": "coin", "thermometer": "crowd",
       "gears": "ticker", "dominoes": "ripple", "skew": "crash"}
