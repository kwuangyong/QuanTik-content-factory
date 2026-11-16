"""Hand-drawn (code-drawn) animated illustrations: flat, brand-coloured motifs that mix with real photos in the
English branches (Instagram, YouTube Shorts) — poker chips, dice, cards, coins, storm, brain, person at a laptop,
branching paths, balance scale, hourglass, dartboard. Drawn by us, so no licence or credit is needed.

    python illustrations.py chips --out /tmp/chips.png     # one still at progress 0.7
    python illustrations.py --sheet /tmp/all.png           # every motif side by side
"""
from __future__ import annotations

import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw

from core import THEME as T, W

SS = 2                 # supersampling: draw at 2× then downscale for smooth edges
BW, BH = W, 780        # band size (1×), placed under the header like a landscape photo
STEPS = 48             # animation is quantised to 48 poses per scene and cached

MOTIFS = {}

# Default motifs per topic (used when an English episode gives no "art").
TOPIC_ART = {
    "kelly": ["chips", "dice", "cards", "scale"],
    "monte_carlo": ["paths", "dice", "hourglass"],
    "var_cvar": ["storm", "hourglass", "target"],
    "garch": ["storm", "paths"],
    "hurst": ["paths", "target"],
    "hmm": ["brain", "storm"],
    "sharpe": ["scale", "target", "coins"],
    "ou": ["scale", "hourglass"],
}
GENERIC_ART = ["brain", "person", "coins", "paths"]


def motif(name):
    def reg(fn):
        MOTIFS[name] = fn
        return fn
    return reg


def _s(v):
    return [int(round(x * SS)) for x in v]


def _rgba(c, a=255):
    return tuple(c[:3]) + (a,)


def _dark(c, k=0.6):
    return tuple(int(x * k) for x in c[:3]) + (255,)


def ease(p):
    return 1 - (1 - max(0.0, min(1.0, p))) ** 3


def _rot(points, cx, cy, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in points]


def _poly(d, pts, fill, outline=None, width=0):
    d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill, outline=outline, width=width * SS)


# ---------------------------------------------------------------- motifs (draw(d, p) on a BW×BH canvas, 1× coords)
@motif("chips")
def _chips(d, p):
    """Four stacks: small bets grow steadily, the overbet stack collapses."""
    cols = [T["positive"], T["accent"], T["neutral"], T["negative"]]
    for i, (x, h0, trend) in enumerate([(200, 4, 5), (420, 5, 9), (640, 6, 2), (860, 9, -8)]):
        n = max(1, int(h0 + trend * ease(p)))
        for k in range(n):
            y = BH - 110 - k * 24
            d.ellipse(_s([x - 85, y - 24, x + 85, y + 24]), fill=_dark(cols[i], 0.55))
            d.ellipse(_s([x - 85, y - 32, x + 85, y + 16]), fill=_rgba(cols[i]), outline=_dark(cols[i]), width=3 * SS)
            for a in range(6):  # edge stripes
                ang = a * math.pi / 3 + 0.3
                sx, sy = x + 70 * math.cos(ang), y - 8 + 20 * math.sin(ang)
                d.rectangle(_s([sx - 7, sy - 4, sx + 7, sy + 4]), fill=_rgba(T["text"], 230))


@motif("coins")
def _coins(d, p):
    jx, jy, jw, jh = BW / 2, 330, 300, 380
    level = 40 + 260 * ease(p)
    d.rounded_rectangle(_s([jx - jw / 2, jy + jh - level, jx + jw / 2, jy + jh]), radius=30 * SS, fill=_rgba(T["neutral"], 200))
    d.rounded_rectangle(_s([jx - jw / 2, jy, jx + jw / 2, jy + jh]), radius=40 * SS, outline=_rgba(T["text"], 220), width=6 * SS)
    for k in range(7):
        ph = (p * 2.5 + k / 7) % 1
        y = 40 + ph * (jy + jh - level - 60)
        x = jx + 90 * math.sin(k * 1.7)
        r = 34
        d.ellipse(_s([x - r, y - r, x + r, y + r]), fill=_rgba(T["neutral"]), outline=_dark(T["neutral"]), width=4 * SS)
        d.ellipse(_s([x - r * 0.55, y - r * 0.55, x + r * 0.55, y + r * 0.55]), outline=_dark(T["neutral"], 0.7), width=3 * SS)


@motif("dice")
def _dice(d, p):
    pips = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
            5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    for j, (x0, face_end) in enumerate([(300, 5), (700, 2)]):
        roll = ease(min(1, p / 0.7))
        ang = (1 - roll) * (4 + j) * math.pi
        cx, cy = x0 + (1 - roll) * (-160 if j == 0 else 160), 420 - 120 * math.sin(roll * math.pi) * (1 - roll)
        face = face_end if roll > 0.98 else 1 + int(p * 40 + j * 3) % 6
        s = 120
        sq = _rot([(cx - s, cy - s), (cx + s, cy - s), (cx + s, cy + s), (cx - s, cy + s)], cx, cy, ang)
        _poly(d, [(x + 10, y + 14) for x, y in sq], fill=(0, 0, 0, 90))
        _poly(d, sq, fill=_rgba(T["text"]), outline=_dark(T["text"], 0.5), width=4)
        for px, py in pips[face]:
            (qx, qy), = _rot([(cx + px * s * 0.5, cy + py * s * 0.5)], cx, cy, ang)
            d.ellipse(_s([qx - 18, qy - 18, qx + 18, qy + 18]), fill=_rgba(T["negative"] if face == 1 else (20, 30, 25)))


@motif("cards")
def _cards(d, p):
    cx, cy = BW / 2, BH - 120
    for i in range(5):
        ang = math.radians((-36 + 18 * i) * ease(p))
        w, h = 150, 220
        pts = _rot([(cx - w / 2, cy - h - 60), (cx + w / 2, cy - h - 60), (cx + w / 2, cy - 60), (cx - w / 2, cy - 60)], cx, cy, ang)
        _poly(d, pts, fill=_rgba(T["text"]), outline=_dark(T["text"], 0.45), width=4)
        (sx, sy), = _rot([(cx, cy - h / 2 - 60)], cx, cy, ang)
        red = i % 2 == 0
        col = _rgba(T["negative"] if red else (25, 35, 30))
        if red:  # diamond
            _poly(d, [(sx, sy - 34), (sx + 24, sy), (sx, sy + 34), (sx - 24, sy)], fill=col)
        else:  # spade-ish: circle pair + stem
            d.ellipse(_s([sx - 26, sy - 14, sx, sy + 12]), fill=col)
            d.ellipse(_s([sx, sy - 14, sx + 26, sy + 12]), fill=col)
            _poly(d, [(sx - 26, sy - 2), (sx + 26, sy - 2), (sx, sy - 40)], fill=col)
            _poly(d, [(sx, sy + 4), (sx - 12, sy + 30), (sx + 12, sy + 30)], fill=col)


@motif("storm")
def _storm(d, p):
    flash = (p * 5) % 1 < 0.1
    if flash:
        d.rectangle(_s([0, 0, BW, BH]), fill=_rgba(T["text"], 40))
    rnd = random.Random(3)
    for k in range(60):  # rain
        x = rnd.uniform(120, BW - 120)
        y = (rnd.uniform(0, 1) + p * 3) % 1 * (BH - 300) + 300
        d.line(_s([x, y, x - 10, y + 36]), fill=_rgba(T["muted"], 170), width=3 * SS)
    for cx, cy, r in [(380, 230, 120), (520, 180, 150), (680, 230, 120), (300, 290, 90), (760, 290, 90), (540, 290, 130)]:
        d.ellipse(_s([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8]), fill=_rgba((90, 104, 98)))
    if flash or (p * 5) % 1 < 0.18:
        bolt = [(560, 320), (500, 470), (560, 470), (480, 660), (620, 430), (555, 430), (610, 320)]
        _poly(d, bolt, fill=_rgba(T["neutral"]))


@motif("brain")
def _brain(d, p):
    cx, cy = BW / 2, 400
    for k in range(3):  # pulses
        r = 160 + ((p * 2 + k / 3) % 1) * 260
        a = int(160 * (1 - ((p * 2 + k / 3) % 1)))
        d.ellipse(_s([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8]), outline=_rgba(T["accent"], a), width=4 * SS)
    for side in (-1, 1):
        d.ellipse(_s([cx + side * 110 - 150, cy - 170, cx + side * 110 + 150, cy + 170]), fill=_rgba((236, 160, 170)),
                  outline=_dark((236, 160, 170)), width=5 * SS)
    for i, (dx, dy, r) in enumerate([(-150, -60, 60), (-90, 50, 55), (-170, 80, 40), (120, -70, 60), (170, 40, 50), (80, 90, 45)]):
        d.arc(_s([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r]), 200 + i * 20, 340 + i * 20,
              fill=_dark((236, 160, 170), 0.6), width=5 * SS)
    d.line(_s([cx, cy - 165, cx, cy + 165]), fill=_dark((236, 160, 170), 0.6), width=5 * SS)


@motif("person")
def _person(d, p):
    dx = BW / 2
    d.rectangle(_s([dx - 380, 560, dx + 380, 584]), fill=_rgba((120, 92, 70)))           # desk
    d.ellipse(_s([dx - 250 - 55, 250, dx - 250 + 55, 360]), fill=_rgba((214, 170, 140)))  # head
    d.rounded_rectangle(_s([dx - 340, 370, dx - 160, 560]), radius=40 * SS, fill=_rgba(T["positive"]))  # body
    d.line(_s([dx - 200, 440, dx - 40, 520]), fill=_rgba((214, 170, 140)), width=22 * SS)  # arm
    _poly(d, [(dx - 60, 540), (dx + 300, 540), (dx + 330, 560), (dx - 90, 560)], fill=_rgba((60, 70, 66)))  # keyboard
    d.rounded_rectangle(_s([dx - 40, 300, dx + 290, 540]), radius=14 * SS, fill=_rgba((40, 50, 46)))  # screen frame
    d.rectangle(_s([dx - 22, 318, dx + 272, 522]), fill=_rgba((14, 24, 20)))
    rnd = random.Random(7)
    pts, y = [], 470
    n = 24
    for i in range(int(n * ease(p)) + 1):
        y = max(340, min(505, y + rnd.uniform(-22, 18)))
        pts.append((dx - 10 + i * 11.5, y))
    if len(pts) > 1:
        d.line(_s([c for pt in pts for c in pt]), fill=_rgba(T["accent"]), width=5 * SS)


@motif("paths")
def _paths(d, p):
    rnd = random.Random(11)
    x0, y0, n = 110, BH / 2, 26
    for k in range(18):
        y, pts = y0, [(x0, y0)]
        for i in range(1, n):
            y += rnd.gauss(0, 18)
            pts.append((x0 + i * (BW - 2 * x0) / (n - 1), y))
        m = max(2, int(n * ease(p)))
        hi = k == 5
        d.line(_s([c for pt in pts[:m] for c in pt]), fill=_rgba(T["accent"] if hi else T["muted"], 255 if hi else 110),
               width=(6 if hi else 3) * SS)
        if hi:
            ex, ey = pts[m - 1]
            d.ellipse(_s([ex - 14, ey - 14, ex + 14, ey + 14]), fill=_rgba(T["accent"]))
    d.ellipse(_s([x0 - 16, y0 - 16, x0 + 16, y0 + 16]), fill=_rgba(T["text"]))


@motif("scale")
def _scale(d, p):
    cx, top = BW / 2, 200
    ang = math.radians(-14 * ease(p) + 4 * math.sin(p * 14) * (1 - p))  # heavier left pan sinks, with a wobble
    d.rectangle(_s([cx - 10, top, cx + 10, BH - 110]), fill=_rgba(T["neutral"]))
    d.rounded_rectangle(_s([cx - 130, BH - 120, cx + 130, BH - 90]), radius=10 * SS, fill=_rgba(T["neutral"]))
    (lx, ly), (rx, ry) = _rot([(cx - 300, top), (cx + 300, top)], cx, top, ang)
    d.line(_s([lx, ly, rx, ry]), fill=_rgba(T["neutral"]), width=14 * SS)
    for (px, py), col, wts in [((lx, ly), T["positive"], 3), ((rx, ry), T["negative"], 1)]:
        d.line(_s([px, py, px - 80, py + 200]), fill=_rgba(T["muted"]), width=3 * SS)
        d.line(_s([px, py, px + 80, py + 200]), fill=_rgba(T["muted"]), width=3 * SS)
        d.chord(_s([px - 110, py + 150, px + 110, py + 260]), 0, 180, fill=_rgba(col))
        for k in range(wts):
            d.ellipse(_s([px - 70 + k * 50, py + 130, px - 30 + k * 50, py + 170]), fill=_rgba(T["text"]))


@motif("hourglass")
def _hourglass(d, p):
    cx, top, bot, w = BW / 2, 110, BH - 90, 230
    mid = (top + bot) / 2
    k = ease(p)
    _poly(d, [(cx - w, top), (cx + w, top), (cx + 18, mid), (cx - 18, mid)], fill=_rgba(T["text"], 40), outline=_rgba(T["text"]), width=5)
    _poly(d, [(cx - 18, mid), (cx + 18, mid), (cx + w, bot), (cx - w, bot)], fill=_rgba(T["text"], 40), outline=_rgba(T["text"]), width=5)
    st = top + (mid - top) * (0.15 + 0.85 * k)  # top sand surface sinks
    hw = 18 + (w - 18) * (mid - st) / (mid - top)
    _poly(d, [(cx - hw, st), (cx + hw, st), (cx + 18, mid), (cx - 18, mid)], fill=_rgba(T["neutral"]))
    hb = (bot - mid) * 0.85 * k  # bottom pile grows
    _poly(d, [(cx - w + 10, bot - 4), (cx + w - 10, bot - 4), (cx, bot - 4 - hb)], fill=_rgba(T["neutral"]))
    if k < 0.99:
        d.line(_s([cx, mid, cx, bot - hb]), fill=_rgba(T["neutral"]), width=6 * SS)
    for y in (top, bot):
        d.rounded_rectangle(_s([cx - w - 40, y - 18, cx + w + 40, y + 18]), radius=10 * SS, fill=_rgba((120, 92, 70)))


@motif("target")
def _target(d, p):
    cx, cy = BW / 2, BH / 2 + 10
    for i, r in enumerate([300, 240, 180, 120, 60]):
        d.ellipse(_s([cx - r, cy - r, cx + r, cy + r]), fill=_rgba(T["negative"] if i % 2 else T["text"]))
    rnd = random.Random(5)
    for k in range(9):
        t0 = k / 9 * 0.8
        if p < t0:
            break
        f = ease((p - t0) / 0.15)
        tx, ty = cx + rnd.gauss(0, 120), cy + rnd.gauss(0, 120)
        sx, sy = tx + (1 - f) * 500, ty - (1 - f) * 300
        d.line(_s([sx, sy, sx + 60, sy - 30]), fill=_rgba(T["accent"]), width=7 * SS)
        d.ellipse(_s([sx - 8, sy - 8, sx + 8, sy + 8]), fill=_rgba((30, 40, 35)))


# ---------------------------------------------------------------- rendering
@lru_cache(maxsize=512)
def _frame(name, step):
    im = Image.new("RGBA", (BW * SS, BH * SS), (0, 0, 0, 0))
    MOTIFS[name](ImageDraw.Draw(im), step / (STEPS - 1))
    return im.resize((BW, BH), Image.LANCZOS)


def frame(name, p):
    """RGBA band BW×BH of motif `name` at progress p (0..1)."""
    if name not in MOTIFS:
        raise KeyError(f"unknown illustration {name!r}; choose {sorted(MOTIFS)}")
    return _frame(name, int(round(max(0.0, min(1.0, p)) * (STEPS - 1))))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?")
    ap.add_argument("--p", type=float, default=0.7)
    ap.add_argument("--out", default="illustration.png")
    ap.add_argument("--sheet")
    a = ap.parse_args()
    if a.sheet:
        names = sorted(MOTIFS)
        sheet = Image.new("RGB", (BW // 3 * 4, BH // 3 * ((len(names) + 3) // 4)), T["bg"] if "bg" in T else (10, 20, 16))
        for i, n in enumerate(names):
            im = frame(n, a.p).resize((BW // 3, BH // 3))
            sheet.paste(im, (i % 4 * BW // 3, i // 4 * BH // 3), im)
        sheet.save(a.sheet)
    else:
        frame(a.name, a.p).save(a.out)


# ---------------------------------------------------------------- character stages (figures.py cast + props)
# Each stage: {"cast": [{who, pose, face, x, flip}], "props": [{what, x, y, s}]}. who: investor, quant, rival,
# professor, analyst · pose: stand, point, think, worried, cheer, shrug, present, hold · face: neutral, smile,
# worried, surprised, focus · props: poker_table, cards, chips, phone_up, phone_down, laptop_up, laptop_down,
# chalkboard, book, newspaper.
STAGES = {
    "poker_duel": {"cast": [{"who": "rival", "pose": "hold", "face": "focus", "x": 0.27},
                            {"who": "investor", "pose": "think", "face": "worried", "x": 0.73, "flip": True}],
                   "props": [{"what": "poker_table"}, {"what": "cards", "x": 0.5, "y": 0.8, "s": 0.6},
                             {"what": "chips", "x": 0.36, "y": 0.84, "s": 0.5}]},
    "poker_allin": {"cast": [{"who": "investor", "pose": "cheer", "face": "surprised", "x": 0.3},
                             {"who": "quant", "pose": "shrug", "face": "neutral", "x": 0.72, "flip": True}],
                    "props": [{"what": "poker_table"}, {"what": "chips", "x": 0.5, "y": 0.82, "s": 0.8}]},
    "phone_panic": {"cast": [{"who": "investor", "pose": "worried", "face": "worried", "x": 0.32}],
                    "props": [{"what": "phone_down", "x": 0.72, "y": 0.55}]},
    "phone_happy": {"cast": [{"who": "investor", "pose": "cheer", "face": "smile", "x": 0.32}],
                    "props": [{"what": "phone_up", "x": 0.72, "y": 0.55}]},
    "quant_lesson": {"cast": [{"who": "quant", "pose": "present", "face": "smile", "x": 0.25}],
                     "props": [{"what": "chalkboard", "x": 0.68, "y": 0.42}]},
    "laptop_check": {"cast": [{"who": "analyst", "pose": "point", "face": "focus", "x": 0.28}],
                     "props": [{"what": "laptop_up", "x": 0.7, "y": 0.62}]},
    "laptop_drop": {"cast": [{"who": "investor", "pose": "shrug", "face": "worried", "x": 0.28}],
                    "props": [{"what": "laptop_down", "x": 0.7, "y": 0.62}]},
    "professor_book": {"cast": [{"who": "professor", "pose": "point", "face": "neutral", "x": 0.3}],
                       "props": [{"what": "book", "x": 0.72, "y": 0.6}]},
    "news_debate": {"cast": [{"who": "investor", "pose": "point", "face": "surprised", "x": 0.25},
                             {"who": "analyst", "pose": "think", "face": "neutral", "x": 0.75, "flip": True}],
                    "props": [{"what": "newspaper", "x": 0.5, "y": 0.66, "s": 0.8}]},
}
TOPIC_STAGES = {
    "kelly": ["poker_duel", "poker_allin", "quant_lesson"],
    "monte_carlo": ["laptop_check", "phone_panic", "quant_lesson"],
    "var_cvar": ["phone_panic", "laptop_drop", "news_debate"],
    "garch": ["news_debate", "phone_panic"],
    "hurst": ["laptop_check", "professor_book"],
    "hmm": ["news_debate", "phone_happy"],
    "sharpe": ["laptop_check", "news_debate"],
    "ou": ["quant_lesson", "professor_book"],
}
GENERIC_STAGES = ["phone_panic", "laptop_check", "quant_lesson", "news_debate", "phone_happy", "professor_book"]


def stage_spec(item):
    """A stage name from STAGES, or an inline spec dict from an episode."""
    return STAGES[item] if isinstance(item, str) else item
