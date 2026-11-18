"""Procedural animations ("hoạt họa") and the wiki card scene. Everything is drawn by code: no stock footage,
no copyrighted images. Each animation illustrates the idea the voice is saying at that moment.

ep["anim"] = {"kind": <one of KINDS>, ...options}; ep["wiki"] = {"title", "en", "lines": [..], "source", "say"}.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import ImageDraw, ImageFont

import frames as F
import scenes as S
from core import THEME as T
from render import Scene

SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"   # has ♠♥♦♣ (Inter does not)


def _sym(size):
    return ImageFont.truetype(SYM, size)


def _rng(seed):
    return np.random.default_rng(seed)


# ------------------------------------------------------------------ primitives
def _coin(d, cx, cy, r, heads, flip=1.0):
    """Coin seen edge-on while flipping: flip in 0..1 (1 = flat)."""
    w = max(2, int(r * abs(math.cos((1 - flip) * math.pi))))
    col = T["positive"] if heads else T["negative"]
    d.ellipse([cx - w, cy - r, cx + w, cy + r], fill=col, outline=T["bg"], width=3)
    if w > r * 0.6:
        f = F.font("sans-black", int(r * 0.9))
        txt = "N" if heads else "S"
        tw = d.textlength(txt, font=f)
        d.text((cx - tw / 2, cy - r * 0.62), txt, font=f, fill=T["bg"])


def _card(img, x, y, w, h, rank, suit, face_up=1.0):
    d = ImageDraw.Draw(img)
    if face_up < 0.5:
        d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=(60, 30, 20), outline=T["accent"], width=3)
        for i in range(0, w, 18):
            d.line([(x + i, y), (x, y + i)], fill=(90, 48, 30), width=2)
        return
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=(240, 238, 230), outline=T["border"], width=3)
    red = suit in "♥♦"
    col = (200, 40, 50) if red else (20, 20, 24)
    d.text((x + 12, y + 6), rank, font=F.font("sans-black", int(h * 0.26)), fill=col)
    fs = _sym(int(h * 0.42))
    tw = d.textlength(suit, font=fs)
    d.text((x + w / 2 - tw / 2, y + h * 0.42), suit, font=fs, fill=col)


def _person(d, cx, cy, s, col):
    d.ellipse([cx - s * 0.32, cy - s, cx + s * 0.32, cy - s * 0.36], fill=col)
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.3, cx + s * 0.5, cy + s * 0.55], radius=int(s * 0.3), fill=col)


# ------------------------------------------------------------------ kinds
def coins(img, p, a):
    """Grid of coin flips appearing one by one; the longest run gets boxed. a: rows, cols, seed, highlight."""
    rows, cols = a.get("rows", 10), a.get("cols", 10)
    rng = _rng(a.get("seed", 4))
    x = rng.random(rows * cols) < 0.5
    best, run, start, bs = 1, 1, 0, 0
    for i in range(1, len(x)):
        run = run + 1 if x[i] == x[i - 1] else 1
        if run > best:
            best, bs = run, i - run + 1
    d = ImageDraw.Draw(img)
    x0, y0, cell = S.X0 + 20, 380, (S.CW - 40) // cols
    shown = int(len(x) * F.seg(p, 0.0, 0.65))
    for i in range(len(x)):
        if i > shown:
            break
        r, c = divmod(i, cols)
        flip = F.clamp((shown - i) / 4)
        _coin(d, x0 + c * cell + cell // 2, y0 + r * cell + cell // 2, int(cell * 0.4), bool(x[i]), flip)
    if p > 0.7 and a.get("highlight", True):
        for i in range(bs, bs + best):
            r, c = divmod(i, cols)
            d.rounded_rectangle([x0 + c * cell + 2, y0 + r * cell + 2, x0 + (c + 1) * cell - 2, y0 + (r + 1) * cell - 2],
                                radius=12, outline=T["accent"], width=6)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, y0 + rows * cell + 30, S.X1, S.BOT), "sans-bold", 40, T["neutral"],
                   "center", label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


def cards(img, p, a):
    """Deal two hole cards and a board. a: hole, board (list like ["A♠","K♠"]), label."""
    hole = a.get("hole", ["A♥", "K♥"])
    board = a.get("board", ["Q♥", "7♥", "2♣", "9♦"])
    w, h = 150, 210
    y_board, y_hole = 470, 820
    gap = (S.CW - len(board) * w) // (len(board) + 1)
    for i, c in enumerate(board):
        k = F.ease_out(F.seg(p, 0.05 + 0.1 * i, 0.15 + 0.1 * i))
        if k <= 0:
            continue
        x = S.X0 + gap + i * (w + gap)
        _card(img, x, int(y_board - 80 * (1 - k)), w, h, c[:-1], c[-1], face_up=k)
    for i, c in enumerate(hole):
        k = F.ease_out(F.seg(p, 0.0 + 0.08 * i, 0.12 + 0.08 * i))
        x = S.X0 + S.CW // 2 - w - 15 + i * (w + 30)
        _card(img, x, int(y_hole + 120 * (1 - k)), w, h, c[:-1], c[-1], face_up=1.0 if k > 0.5 else 0.0)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1080, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.55, 0.7)))


def matrix(img, p, a):
    """2×2 payoff matrix. a: rows (2 labels), cols (2 labels), cells [[ "3 / 3", ...], ...], hl [r, c]."""
    rows, cols, cells = a["rows"], a["cols"], a["cells"]
    d = ImageDraw.Draw(img)
    x0, y0 = S.X0 + 200, 520
    cw, ch = (S.X1 - x0) // 2, 300
    F.text_box(img, a.get("top", ""), (x0, 380, S.X1, 440), "sans-bold", 32, T["muted"], "center", label="anim-top")
    for j, c in enumerate(cols):
        F.text_box(img, c, (x0 + j * cw, 445, x0 + (j + 1) * cw, 510), "sans-black", 34, T["text"], "center",
                   label=f"anim-col{j}")
    for i, r in enumerate(rows):
        F.text_box(img, r, (S.X0, y0 + i * ch, x0 - 10, y0 + (i + 1) * ch), "sans-black", 34, T["text"], "left",
                   "middle", label=f"anim-row{i}")
        for j in range(2):
            k = F.ease_out(F.seg(p, 0.1 + 0.12 * (2 * i + j), 0.25 + 0.12 * (2 * i + j)))
            if k <= 0:
                continue
            hl = a.get("hl") == [i, j] and p > 0.7
            box = [x0 + j * cw + 8, y0 + i * ch + 8, x0 + (j + 1) * cw - 8, y0 + (i + 1) * ch - 8]
            d.rounded_rectangle(box, radius=22, fill=(30, 22, 16) if hl else T["surface"],
                                outline=T["accent"] if hl else T["border"], width=5 if hl else 2)
            F.text_box(img, cells[i][j], (box[0] + 10, box[1], box[2] - 10, box[3]), "mono-bold", 58,
                       T["accent"] if hl else T["text"], "center", "middle", min_size=30, label=f"anim-cell{i}{j}",
                       alpha=k)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, y0 + 2 * ch + 20, S.X1, S.BOT), "sans-bold", 38, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


def crowd(img, p, a):
    """Grid of people. mode 'survive': fade out until `left` remain; mode 'highlight': color `hits` of them."""
    rows, cols = a.get("rows", 16), a.get("cols", 14)
    n = rows * cols
    rng = _rng(a.get("seed", 3))
    order = rng.permutation(n)
    d = ImageDraw.Draw(img)
    x0, y0 = S.X0 + 10, 380
    cell = min((S.CW - 20) / cols, (1130 - y0) / rows)
    mode = a.get("mode", "survive")
    for idx in range(n):
        r, c = divmod(idx, cols)
        rank = int(np.where(order == idx)[0][0])
        col = T["muted"]
        if mode == "survive":
            alive_n = int(n - (n - a.get("left", 3)) * F.ease_in_out(F.seg(p, 0.1, 0.75)))
            col = T["accent"] if rank < a.get("left", 3) and p > 0.75 else (T["muted"] if rank < alive_n else (35, 48, 42))
        else:
            hits, false = a.get("hits", 4), a.get("false", 20)
            if rank < hits and p > 0.3:
                col = T["positive"]
            elif rank < hits + false and p > 0.55:
                col = T["negative"]
        _person(d, x0 + c * cell + cell / 2, y0 + r * cell + cell * 0.6, cell * 0.42, col)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1150, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.75, 0.9)))


def doors(img, p, a):
    """Monty Hall: three doors, pick one, host opens a goat door, the car is behind the other."""
    d = ImageDraw.Draw(img)
    w, h, gap = 240, 460, 40
    x0 = S.X0 + (S.CW - 3 * w - 2 * gap) // 2
    y0 = 470
    pick, car, opened = 0, 2, 1
    for i in range(3):
        x = x0 + i * (w + gap)
        is_open = (i == opened and p > 0.35) or (i == car and p > 0.75)
        d.rounded_rectangle([x, y0, x + w, y0 + h], radius=16, fill=(20, 14, 10) if is_open else (120, 70, 40),
                            outline=T["accent"] if (i == pick and p > 0.12) else T["border"], width=8 if i == pick else 3)
        if is_open:
            txt = "XE" if i == car else "DÊ"
            F.text_box(img, txt, (x, y0 + 150, x + w, y0 + 300), "sans-black", 80,
                       T["positive"] if i == car else T["muted"], "center", "middle", label=f"door{i}")
        else:
            F.text_box(img, str(i + 1), (x, y0 + 150, x + w, y0 + 300), "sans-black", 110, (240, 210, 170), "center",
                       "middle", label=f"door{i}")
            d.ellipse([x + w - 50, y0 + h // 2 - 12, x + w - 26, y0 + h // 2 + 12], fill=(230, 190, 90))
    if p > 0.12:
        F.text_box(img, "bạn chọn", (x0, y0 + h + 20, x0 + w, y0 + h + 80), "sans-bold", 34, T["accent"], "center",
                   label="door-pick")
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1090, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.78, 0.92)))


def wheel(img, p, a):
    """Roulette-like wheel spinning with a bet stack doubling beside it."""
    d = ImageDraw.Draw(img)
    cx, cy, R = S.X0 + S.CW // 2, 680, 240
    rot = 900 * F.ease_out(F.seg(p, 0, 0.8))
    nseg = 37
    for i in range(nseg):
        a0 = rot + i * 360 / nseg
        col = (30, 140, 80) if i == 0 else ((190, 40, 50) if i % 2 else (25, 25, 28))
        d.pieslice([cx - R, cy - R, cx + R, cy + R], a0, a0 + 360 / nseg, fill=col, outline=(200, 170, 90))
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(200, 170, 90))
    d.polygon([(cx, cy - R - 10), (cx - 18, cy - R - 50), (cx + 18, cy - R - 50)], fill=T["accent"])
    stacks = a.get("stacks", [1, 2, 4, 8, 16, 32, 64, 128])
    k = int(len(stacks) * F.seg(p, 0.05, 0.85)) + 1
    n = len(stacks); bw = S.CW / n
    base, tallest = 1090, 110
    for i, s in enumerate(stacks[:k]):
        hgt = 12 + tallest * math.log2(s) / math.log2(stacks[-1])
        x = S.X0 + i * bw + bw * 0.2
        col = T["negative"] if i == k - 1 and p > 0.6 else T["neutral"]
        d.rounded_rectangle([x, base - hgt, x + bw * 0.6, base], radius=8, fill=col)
        F.text_box(img, str(s), (x - 20, base + 4, x + bw * 0.6 + 20, base + 40), "mono-bold", 26, T["text"], "center",
                   label=f"stack{i}")
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1150, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


def _num(v):
    """'1.234,5%' (vi-VN display string filled from a placeholder) or a plain number → float."""
    if isinstance(v, (int, float)):
        return float(v)
    s = v.replace("−", "-").replace(".", "").replace(",", ".").rstrip("%x đ")
    return float(s)


def steps(img, p, a):
    """Staircase of bars (e.g. beauty contest levels, drawdown → required gain). a: items [[label, value]], unit."""
    items = [(lab, _num(v), v if isinstance(v, str) else None) for lab, v in a["items"]]
    d = ImageDraw.Draw(img)
    vmax = max(abs(v) for _, v, _ in items) or 1
    n = len(items)
    bw = (S.CW - 40) / n
    base_y, top_y = 1120, 470
    for i, (lab, v, disp) in enumerate(items):
        k = F.ease_out(F.seg(p, 0.05 + 0.12 * i, 0.2 + 0.12 * i))
        if k <= 0:
            continue
        hgt = (base_y - top_y) * abs(v) / vmax * k
        x = S.X0 + 20 + i * bw
        col = T["accent"] if i == a.get("hl", n - 1) else T["muted"]
        d.rounded_rectangle([x + 10, base_y - hgt, x + bw - 10, base_y], radius=12, fill=col)
        val = disp if disp is not None else a.get("fmt", "{:.0f}").format(v).replace(".", ",") + a.get("unit", "")
        F.text_box(img, val, (x, base_y - hgt - 70, x + bw, base_y - hgt - 8), "mono-bold", 40, T["text"], "center",
                   min_size=22, label=f"step{i}-v")
        F.text_box(img, lab, (x, base_y + 12, x + bw, base_y + 110), "sans-bold", 28, T["muted"], "center",
                   min_size=18, label=f"step{i}-l")
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 380, S.X1, 460), "sans-bold", 38, T["neutral"], "center",
                   label="anim-label")


def scale(img, p, a):
    """Balance: a loss on one pan outweighs an equal gain on the other. a: left, right, tilt (deg)."""
    d = ImageDraw.Draw(img)
    cx, cy = S.X0 + S.CW // 2, 620
    tilt = math.radians(a.get("tilt", 18)) * F.ease_out(F.seg(p, 0.25, 0.7))
    L = 330
    lx, ly = cx - L * math.cos(tilt), cy + L * math.sin(tilt)
    rx, ry = cx + L * math.cos(tilt), cy - L * math.sin(tilt)
    d.polygon([(cx, cy), (cx - 60, 1180), (cx + 60, 1180)], fill=T["border"])
    d.line([(lx, ly), (rx, ry)], fill=T["muted"], width=12)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=T["accent"])
    for (x, y, txt, col, nm) in ((lx, ly, a.get("left", "−100"), T["negative"], "pan-l"),
                                  (rx, ry, a.get("right", "+100"), T["positive"], "pan-r")):
        d.line([(x, y), (x - 90, y + 190)], fill=T["muted"], width=3)
        d.line([(x, y), (x + 90, y + 190)], fill=T["muted"], width=3)
        d.chord([x - 130, y + 120, x + 130, y + 260], 0, 180, fill=col)
        F.text_box(img, txt, (x - 140, y + 60, x + 140, y + 180), "mono-bold", 64, col, "center", "middle",
                   min_size=30, label=nm)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1200, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


def goal(img, p, a):
    """Penalty: goal mouth, keeper dives one way, ball goes the other."""
    d = ImageDraw.Draw(img)
    gx0, gx1, gy0, gy1 = S.X0 + 40, S.X1 - 40, 520, 900
    for i in range(gx0, gx1, 40):
        d.line([(i, gy0), (i, gy1)], fill=(40, 60, 50), width=2)
    for j in range(gy0, gy1, 40):
        d.line([(gx0, j), (gx1, j)], fill=(40, 60, 50), width=2)
    d.line([(gx0, gy1), (gx0, gy0), (gx1, gy0), (gx1, gy1)], fill=(235, 235, 235), width=14)
    d.line([(S.X0 - 20, gy1), (S.X1 + 20, gy1)], fill=T["positive"], width=4)
    k = F.ease_out(F.seg(p, 0.2, 0.6))
    kx = S.X0 + S.CW // 2 + (a.get("keeper", -1)) * 230 * k
    _person(d, kx, gy1 - 120, 110, T["neutral"])
    bx0, by0 = S.X0 + S.CW // 2, 1150
    bx1, by1 = S.X0 + S.CW // 2 + a.get("ball", 1) * 280, gy0 + 120
    bx, by = bx0 + (bx1 - bx0) * k, by0 + (by1 - by0) * k
    d.ellipse([bx - 34, by - 34, bx + 34, by + 34], fill=(245, 245, 245), outline=(20, 20, 20), width=4)
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1210, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.65, 0.8)))


def gavel(img, p, a):
    """Auction: paddles rise with estimates; the highest wins and the true value line sits below it."""
    d = ImageDraw.Draw(img)
    rng = _rng(a.get("seed", 2))
    n = a.get("n", 8)
    est = 100 + rng.normal(0, 20, n)
    vmax = est.max() * 1.15
    base, top = 1160, 470
    bw = S.CW / n
    true_y = base - (base - top) * 100 / vmax
    for i, e in enumerate(est):
        k = F.ease_out(F.seg(p, 0.05 + 0.05 * i, 0.25 + 0.05 * i))
        hgt = (base - top) * e / vmax * k
        x = S.X0 + i * bw + bw / 2
        win = i == int(est.argmax()) and p > 0.6
        col = T["accent"] if win else T["muted"]
        d.line([(x, base), (x, base - hgt)], fill=T["border"], width=8)
        d.ellipse([x - 38, base - hgt - 76, x + 38, base - hgt], fill=col)
        F.text_box(img, f"{e:.0f}", (x - 45, base - hgt - 60, x + 45, base - hgt - 16), "mono-bold", 28, T["bg"],
                   "center", label=f"bid{i}")
    if p > 0.45:
        d.line([(S.X0, true_y), (S.X1, true_y)], fill=T["positive"], width=5)
        F.text_box(img, a.get("true_label", "giá trị thật"), (S.X0, true_y + 8, S.X1, true_y + 60), "sans-bold", 32,
                   T["positive"], "right", label="true-val")
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1190, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


def ticker(img, p, a):
    """Order ticket counter: every trade drops a fee coin into the broker's jar."""
    d = ImageDraw.Draw(img)
    n = a.get("trades", 20)
    k = int(n * F.seg(p, 0.05, 0.8))
    F.text_box(img, a.get("left_label", "tài khoản của bạn"), (S.X0, 390, S.X0 + 420, 450), "sans-bold", 32,
               T["muted"], "center", label="jar-l")
    F.text_box(img, a.get("right_label", "phí + thuế"), (S.X1 - 420, 390, S.X1, 450), "sans-bold", 32, T["muted"],
               "center", label="jar-r")
    lh = 560 * (1 - 0.6 * k / n)
    rh = 560 * 0.6 * k / n
    d.rounded_rectangle([S.X0 + 60, 1100 - lh, S.X0 + 360, 1100], radius=20, fill=T["positive"])
    d.rounded_rectangle([S.X1 - 360, 1100 - rh, S.X1 - 60, 1100], radius=20, fill=T["negative"])
    for i in range(k):
        y = 470 + (i % 10) * 60
        if i == k - 1:
            x = S.X0 + S.CW // 2
            d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=T["neutral"])
    F.text_box(img, f"{k}", (S.X0 + 360, 900, S.X1 - 360, 1080), "mono-bold", 120, T["accent"], "center", "middle",
               label="trade-count")
    if a.get("label"):
        F.text_box(img, a["label"], (S.X0, 1130, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "center",
                   label="anim-label", alpha=F.ease_out(F.seg(p, 0.7, 0.85)))


KINDS = {"coins": coins, "cards": cards, "matrix": matrix, "crowd": crowd, "doors": doors, "wheel": wheel,
         "steps": steps, "scale": scale, "goal": goal, "gavel": gavel, "ticker": ticker}


def anim_texts(a):
    out = [a.get("label", ""), a.get("top", "")]
    for k in ("rows", "cols"):
        if isinstance(a.get(k), list):
            out += a[k]
    for row in a.get("cells", []):
        out += row
    out += [str(x[0]) for x in a.get("items", [])] + [x[1] for x in a.get("items", []) if isinstance(x[1], str)]
    return [x for x in out if x]


def anim(a, say, name="anim", min_dur=4.0):
    fn = KINDS[a["kind"]]

    def draw(img, t, p):
        fn(img, p, a)

    return Scene(name, say, draw, min_dur, texts=anim_texts(a))


# ------------------------------------------------------------------ real photos (Wikimedia Commons) — Ken Burns
from functools import lru_cache as _lru  # noqa: E402

from PIL import Image as _Image  # noqa: E402


@_lru(maxsize=32)
def _cover(key, w, h, zoom=1.14):
    import media
    im, meta = media.fetch(json_loads(key))
    if im is None:
        return None, None
    s = max(w * zoom / im.width, h * zoom / im.height)
    return im.resize((int(im.width * s) + 1, int(im.height * s) + 1), _Image.LANCZOS), meta


def json_loads(k):
    import json
    return json.loads(k)


def _spec_key(spec):
    import json
    return json.dumps(spec, sort_keys=True)


def kenburns(img, spec, box, p, dim=0.0, credit=True, direction=1):
    """Paint a slowly zooming/panning photo into box. Returns the credit meta (or None if unavailable)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    big, meta = _cover(_spec_key(spec), w, h)
    if big is None:
        return None
    z = 1.0 + 0.12 * F.ease_in_out(p)
    # crop a w×h window scaled by 1/z, panning horizontally with p
    sw, sh = int(w * 1.14 / z), int(h * 1.14 / z)
    sw, sh = min(sw, big.width), min(sh, big.height)
    px = int((big.width - sw) * (0.5 + 0.4 * direction * (p - 0.5)))
    py = int((big.height - sh) * 0.4)
    crop = big.crop((px, py, px + sw, py + sh)).resize((w, h), _Image.BILINEAR)
    if dim > 0:
        crop = _Image.blend(crop, _Image.new("RGB", (w, h), T["bg"]), dim)
    img.paste(crop, (x0, y0))
    if credit:
        import media
        line = media.credit_line(meta)
        d = ImageDraw.Draw(img, "RGBA")
        f = F.font("sans", 18)
        tw = d.textlength(line, font=f)
        d.rectangle([x1 - tw - 20, y1 - 30, x1, y1], fill=(0, 0, 0, 150))
        d.text((x1 - tw - 10, y1 - 26), line, font=f, fill=(220, 225, 220))
    return meta


def with_bg(scene, spec, dim=0.62):
    """Wrap a scene: real photo full-width behind it (below the header), darkened so text stays readable."""
    inner = scene.draw

    def draw(img, t, p):
        kenburns(img, spec, (0, 290, 1080, 1320), p, dim=dim)
        inner(img, t, p)

    scene.draw = draw
    return scene


def photo(spec, say, caption=None, name="broll", min_dur=3.5):
    """Standalone B-roll: a real photo with Ken Burns in a rounded frame, optional caption below."""
    def draw(img, t, p):
        kenburns(img, spec, (S.X0, 330, S.X1, 1150), p, credit=True)
        if caption:
            F.text_box(img, caption, (S.X0, 1170, S.X1, S.BOT), "sans-bold", 40, T["neutral"], "left", "top",
                       min_size=26, label=f"{name}-cap", hl_numbers=True)

    return Scene(name, say, draw, min_dur, texts=[caption or ""])


# ------------------------------------------------------------------ wiki card
def wiki(w, name="wiki", min_dur=4.5):
    """Encyclopedia-style card: real image (if any), title, English name, fact lines typed in, source at the bottom."""
    lines = w.get("lines", [])
    if w.get("image"):
        import media
        if media.fetch(w["image"])[0] is not None:
            return _wiki_img(w, name, min_dur)

    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.15))
        d = ImageDraw.Draw(img)
        F.panel(img, (S.X0, 330, S.X1, S.BOT), fill=(236, 238, 234), outline=(200, 205, 200))
        d.rectangle([S.X0 + 2, 330, S.X1 - 2, 400], fill=(210, 214, 208))
        F.text_box(img, "W  Bách khoa · tóm tắt", (S.X0 + 30, 342, S.X1 - 30, 392), "sans-bold", 30, (60, 64, 60),
                   label=f"{name}-bar")
        F.text_box(img, w["title"], (S.X0 + 40, 425, S.X1 - 40, 560), "sans-black", 62, (20, 22, 20), label=f"{name}-title",
                   alpha=a)
        if w.get("en"):
            F.text_box(img, w["en"], (S.X0 + 40, 565, S.X1 - 40, 615), "sans", 32, (90, 96, 90),
                       label=f"{name}-en", alpha=a)
        d.line([(S.X0 + 40, 630), (S.X1 - 40, 630)], fill=(190, 196, 190), width=2)
        y = 655
        for i, ln in enumerate(lines):
            k = F.seg(p, 0.06 + 0.12 * i, 0.2 + 0.12 * i)
            if k <= 0:
                break
            shown = ln[:max(1, int(len(ln) * k))]
            used = F.text_box(img, "• " + shown, (S.X0 + 40, y, S.X1 - 40, y + 150), "sans-bold", 38, (30, 34, 30),
                              min_size=26, label=f"{name}-l{i}")
            y = max(y + 60, used[3] + 18)
        if w.get("source"):
            F.text_box(img, "Nguồn: " + w["source"], (S.X0 + 40, S.BOT - 80, S.X1 - 40, S.BOT - 20), "sans", 24,
                       (100, 106, 100), min_size=18, label=f"{name}-src")

    return Scene(name, w.get("say", " ".join(lines)), draw, min_dur,
                 texts=[w["title"], w.get("en", ""), w.get("source", "")] + lines)


def _wiki_img(w, name, min_dur):
    lines = w.get("lines", [])

    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.15))
        d = ImageDraw.Draw(img)
        F.panel(img, (S.X0, 330, S.X1, S.BOT), fill=(236, 238, 234), outline=(200, 205, 200))
        d.rectangle([S.X0 + 2, 330, S.X1 - 2, 390], fill=(210, 214, 208))
        F.text_box(img, "W  Bách khoa · tóm tắt", (S.X0 + 30, 340, S.X1 - 30, 384), "sans-bold", 28, (60, 64, 60),
                   label=f"{name}-bar")
        kenburns(img, w["image"], (S.X0 + 2, 392, S.X1 - 2, 800), p, credit=True)
        F.text_box(img, w["title"], (S.X0 + 36, 815, S.X1 - 36, 895), "sans-black", 52, (20, 22, 20), min_size=32,
                   label=f"{name}-title", alpha=a)
        if w.get("en"):
            F.text_box(img, w["en"], (S.X0 + 36, 895, S.X1 - 36, 935), "sans", 28, (90, 96, 90), min_size=18,
                       label=f"{name}-en", alpha=a)
        y = 950
        for i, ln in enumerate(lines):
            k = F.seg(p, 0.06 + 0.12 * i, 0.2 + 0.12 * i)
            if k <= 0:
                break
            shown = ln[:max(1, int(len(ln) * k))]
            used = F.text_box(img, "• " + shown, (S.X0 + 36, y, S.X1 - 36, min(y + 100, S.BOT - 50)), "sans-bold", 32,
                              (30, 34, 30), min_size=22, label=f"{name}-l{i}")
            y = max(y + 46, used[3] + 10)
        if w.get("source"):
            F.text_box(img, "Nguồn: " + w["source"], (S.X0 + 36, S.BOT - 44, S.X1 - 36, S.BOT - 10), "sans", 20,
                       (100, 106, 100), min_size=16, label=f"{name}-src")

    return Scene(name, w.get("say", " ".join(lines)), draw, min_dur,
                 texts=[w["title"], w.get("en", ""), w.get("source", "")] + lines)
