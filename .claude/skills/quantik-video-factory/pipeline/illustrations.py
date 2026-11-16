"""Procedural motion-graphics ("hoạt họa") for the broll-story style: coins, crowds, cards, wheels, balls...

Every function has the signature ``draw(img, t, p, model, box, **opt)`` and draws inside ``box``.
Anything that shows a number takes it from ``model.values`` / ``model.series`` (so QA's rule "every number comes
from code" still holds); labels pass through ``fmt_num``.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import frames as F
from core import THEME as T, font, fmt_num

SUIT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _suit_font(size):
    from PIL import ImageFont
    return ImageFont.truetype(SUIT, int(size))


def _v(model, key):
    return fmt_num(model.values[key], model.formats.get(key, "num2"))


def _glow(img, xy, r, color, strength=110):
    g = Image.new("L", img.size, 0)
    ImageDraw.Draw(g).ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r], fill=strength)
    g = g.filter(ImageFilter.GaussianBlur(r / 2))
    img.paste(Image.new("RGB", img.size, color), (0, 0), g)


# ---------------------------------------------------------------- coins (ergodicity, survivorship)
def coins(img, t, p, model, box, n=12, up_key="up", down_key="down", seed=1, **_):
    """A row of coins flipping one after another; each lands heads (+up) or tails (−down)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rng = np.random.default_rng(seed)
    faces = rng.random(n) < 0.5
    cols, r = 4, 78
    gapx = (x1 - x0) / cols
    up = "+" + _v(model, up_key) if up_key in model.values else "H"
    dn = "-" + _v(model, down_key) if down_key in model.values else "T"
    for i in range(n):
        cx = x0 + gapx * (i % cols + 0.5)
        cy = y0 + 150 + (i // cols) * 250
        start = i / n * 0.7
        k = F.seg(p, start, start + 0.18)
        if k <= 0:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=T["border"], width=3)
            continue
        spin = math.cos(k * math.pi * 5) if k < 1 else 1.0
        w = max(6, abs(spin) * r)
        hop = math.sin(k * math.pi) * 90 if k < 1 else 0
        landed = k >= 1
        col = (T["positive"] if faces[i] else T["negative"]) if landed else T["neutral"]
        d.ellipse([cx - w, cy - r - hop, cx + w, cy + r - hop], fill=(40, 34, 18) if not landed else (20, 30, 24),
                  outline=col, width=6)
        if landed:
            lab = up if faces[i] else dn
            f = font("mono-bold", 38)
            tw = d.textlength(lab, font=f)
            d.text((cx - tw / 2, cy - 22), lab, font=f, fill=col)


# ---------------------------------------------------------------- crowd (yard-sale, ergodicity)
def crowd(img, t, p, model, box, series_key="w", n_side=10, morph=(0.15, 0.75), **_):
    """100 people. They start equal; then each icon grows/shrinks to the simulated final wealth."""
    w = np.asarray(model.series[series_key])
    w = w[:, -1] if w.ndim == 2 else w
    rng = np.random.default_rng(0)
    sample = rng.choice(w, n_side * n_side, replace=False)
    rel = sample / sample.mean()
    k = F.ease_in_out(F.seg(p, *morph))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    cell = min((x1 - x0) / n_side, (y1 - y0) / n_side)
    order = np.argsort(rel)
    rank = np.empty_like(order); rank[order] = np.arange(len(order))
    for idx in range(n_side * n_side):
        cx = x0 + cell * (idx % n_side + 0.5)
        cy = y0 + cell * (idx // n_side + 0.5)
        s = (1 - k) * 1.0 + k * float(np.clip(np.sqrt(rel[idx]), 0.12, 3.2))
        q = rank[idx] / (len(rank) - 1)
        col = tuple(int(a + (b - a) * k) for a, b in zip(T["muted"], (T["accent"] if q > 0.95 else
                                                                      T["neutral"] if q > 0.6 else T["border"])))
        hr = cell * 0.14 * s
        d.ellipse([cx - hr, cy - cell * 0.28 * s - hr, cx + hr, cy - cell * 0.28 * s + hr], fill=col)
        d.rounded_rectangle([cx - cell * 0.2 * s, cy - cell * 0.1 * s, cx + cell * 0.2 * s, cy + cell * 0.3 * s],
                            radius=max(2, int(cell * 0.1 * s)), fill=col)


# ---------------------------------------------------------------- halving dots (survivorship / newsletter scam)
def halving(img, t, p, model, box, total_key="letters", rounds=10, **_):
    """1,024 dots; each round half of them (the wrong guesses) go dark. Counter = what is left."""
    total = int(model.values[total_key])
    side = int(math.ceil(math.sqrt(total)))
    r_done = min(rounds, int(F.seg(p, 0.08, 0.88) * (rounds + 0.999)))
    alive_n = total // (2 ** r_done)
    rng = np.random.default_rng(3)
    order = rng.permutation(total)          # who survives longest
    alive = np.zeros(total, bool); alive[order[:alive_n]] = True
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    cell = min((x1 - x0) / side, (y1 - y0 - 160) / side)
    for i in range(total):
        cx = x0 + cell * (i % side + 0.5); cy = y0 + 150 + cell * (i // side + 0.5)
        rr = cell * (0.42 if alive[i] else 0.18)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=T["accent"] if alive[i] else (30, 42, 36))
    f = font("mono-bold", 64)
    lab = f"{alive_n:,}"
    d.text((x0, y0 + 10), lab, font=f, fill=T["accent"])
    d.text((x0 + d.textlength(lab, font=f) + 24, y0 + 36), "still 'perfect'", font=font("sans-bold", 34), fill=T["muted"])
    d.text((x1 - 200, y0 + 36), f"round {r_done}", font=font("sans-bold", 34), fill=T["muted"])


# ---------------------------------------------------------------- cards (pot odds, bluffing)
def _card(rank, suit, w=150):
    h = int(w * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 9, fill=(246, 244, 236), outline=(60, 60, 60), width=3)
    red = suit in "♥♦"
    c = (205, 45, 60) if red else (25, 25, 30)
    d.text((w * 0.1, h * 0.05), rank, font=font("sans-black", int(w * 0.34)), fill=c)
    sf = _suit_font(w * 0.55)
    tw = d.textlength(suit, font=sf)
    d.text(((w - tw) / 2, h * 0.36), suit, font=sf, fill=c)
    return im


def _card_back(w=150):
    h = int(w * 1.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=w // 9, fill=(120, 40, 30), outline=T["accent"], width=4)
    for k in range(-h, w, 18):
        d.line([(k, 0), (k + h, h)], fill=(150, 60, 40), width=3)
    return im


def cards(img, t, p, model, box, hand=("A♥", "K♥"), board=("2♥", "7♥", "J♣"), outs_key="outs", **_):
    """Deal a hand + flop, then fan out the outs (cards that complete the draw)."""
    x0, y0, x1, y1 = box
    cw = 150
    def put(card, xy, k, rot=0):
        if k <= 0:
            return
        im = _card(card[:-1], card[-1], cw) if card != "back" else _card_back(cw)
        if rot:
            im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
        e = F.ease_out(k)
        tx, ty = xy
        F.paste(img, im, (tx + (1 - e) * 500, ty - (1 - e) * 200), alpha=min(1, k * 2))
    d = ImageDraw.Draw(img)
    d.text((x0, y0), "your hand", font=font("sans-bold", 30), fill=T["muted"])
    for i, c in enumerate(hand):
        put(c, (x0 + i * (cw + 20), y0 + 50), F.seg(p, 0.02 + i * 0.06, 0.16 + i * 0.06))
    d.text((x0, y0 + 300), "the board", font=font("sans-bold", 30), fill=T["muted"])
    for i, c in enumerate(board):
        put(c, (x0 + i * (cw + 20), y0 + 350), F.seg(p, 0.15 + i * 0.06, 0.3 + i * 0.06))
    for i in range(2):
        put("back", (x0 + (3 + i) * (cw + 20), y0 + 350), F.seg(p, 0.3, 0.4))
    k = F.seg(p, 0.45, 0.8)
    if k > 0:
        n = int(model.values.get(outs_key, 9))
        used = {c[:-1] for c in hand + board if c.endswith("♥")}
        ranks = [r for r in ["3", "4", "5", "6", "8", "9", "10", "J", "Q", "A", "K", "2", "7"] if r not in used][:n]
        d.text((x0, y0 + 620), f"{n} outs left in the deck", font=font("sans-bold", 34), fill=T["accent"])
        for i, r in enumerate(ranks):
            kk = F.seg(k, i / n * 0.7, i / n * 0.7 + 0.3)
            if kk <= 0:
                continue
            im = _card(r, "♥", 110)
            F.paste(img, im, (x0 + i * 90, y0 + 690 + (1 - F.ease_out(kk)) * 80), alpha=kk)


# ---------------------------------------------------------------- roulette wheel (gambler's ruin)
_WHEEL = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
          22, 18, 29, 7, 28, 12, 35, 3, 26]


def roulette(img, t, p, model, box, **_):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, y0 + (y1 - y0) * 0.45
    R = min(x1 - x0, y1 - y0) * 0.42
    rot = 360 * 2.2 * (1 - (1 - F.clamp(p)) ** 2)
    size = int(R * 2 + 20)
    wheel = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(wheel)
    c = size / 2
    n = len(_WHEEL)
    reds = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    for i, num in enumerate(_WHEEL):
        a0, a1 = i * 360 / n, (i + 1) * 360 / n
        col = (30, 140, 80) if num == 0 else ((190, 40, 50) if num in reds else (25, 25, 28))
        d.pieslice([c - R, c - R, c + R, c + R], a0, a1, fill=col, outline=(200, 170, 90), width=2)
    for i, num in enumerate(_WHEEL):
        a = math.radians((i + 0.5) * 360 / n)
        tx, ty = c + R * 0.84 * math.cos(a), c + R * 0.84 * math.sin(a)
        s = str(num)
        f = font("sans-bold", int(R * 0.075))
        d.text((tx - d.textlength(s, font=f) / 2, ty - R * 0.04), s, font=f, fill=(240, 236, 220))
    d.ellipse([c - R * 0.62, c - R * 0.62, c + R * 0.62, c + R * 0.62], fill=(60, 40, 24), outline=(200, 170, 90), width=4)
    d.ellipse([c - R * 0.12, c - R * 0.12, c + R * 0.12, c + R * 0.12], fill=(200, 170, 90))
    wheel = wheel.rotate(rot, resample=Image.BICUBIC)
    F.paste(img, wheel, (cx, cy), anchor="center")
    ba = math.radians(-rot * 1.6 + 90)
    br = R * (0.95 - 0.2 * F.seg(p, 0.7, 1.0))
    bx, by = cx + br * math.cos(ba), cy + br * math.sin(ba)
    ImageDraw.Draw(img).ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=(250, 250, 250))
    dd = ImageDraw.Draw(img)
    lab = f"18 red · 18 black · 1 green zero"
    f = font("sans-bold", 36)
    dd.text((cx - dd.textlength(lab, font=f) / 2, cy + R + 50), lab, font=f, fill=T["text"])


# ---------------------------------------------------------------- lottery balls
def lottery_balls(img, t, p, model, box, pool_key="pool", pick_key="pick", seed=7, **_):
    pool, pick = int(model.values[pool_key]), int(model.values[pick_key])
    rng = np.random.default_rng(seed)
    drawn = list(rng.choice(np.arange(1, pool + 1), pick, replace=False))
    x0, y0, x1, y1 = box
    cols = 7
    cell = (x1 - x0) / cols
    d = ImageDraw.Draw(img)
    for i in range(pool):
        num = i + 1
        cx = x0 + cell * (i % cols + 0.5); cy = y0 + cell * 0.75 * (i // cols + 0.5)
        k = drawn.index(num) if num in drawn else -1
        lit = k >= 0 and p > 0.25 + k * 0.1
        r = cell * 0.3
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=T["accent"] if lit else (26, 40, 33),
                  outline=T["border"], width=2)
        s = str(num); f = font("sans-bold", int(r * 0.8))
        d.text((cx - d.textlength(s, font=f) / 2, cy - r * 0.5), s, font=f, fill=T["bg"] if lit else T["muted"])
    yb = y0 + cell * 0.75 * 7.4
    for k, num in enumerate(sorted(drawn)):
        kk = F.seg(p, 0.25 + k * 0.1, 0.35 + k * 0.1)
        if kk <= 0:
            continue
        cx = x0 + 70 + k * 140; cy = yb + 80 - math.sin(kk * math.pi) * 60
        _glow(img, (int(cx), int(cy)), 60, T["accent"], 60)
        d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(250, 245, 230), outline=T["accent"], width=6)
        s = str(num); f = font("sans-black", 52)
        d.text((cx - d.textlength(s, font=f) / 2, cy - 32), s, font=f, fill=T["bg"])


# ---------------------------------------------------------------- payoff matrix (prisoner's dilemma)
def payoff_matrix(img, t, p, model, box, **_):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    v = model.values
    cells = [("both cooperate", v["r"], v["r"], T["positive"]), ("you cooperate, they defect", v["s"], v["t"], T["negative"]),
             ("you defect, they cooperate", v["t"], v["s"], T["neutral"]), ("both defect", v["p"], v["p"], T["muted"])]
    gw = (x1 - x0 - 30) / 2; gh = 300
    for i, (lab, a, b, col) in enumerate(cells):
        k = F.ease_out(F.seg(p, 0.05 + i * 0.15, 0.25 + i * 0.15))
        if k <= 0:
            continue
        cx = x0 + (i % 2) * (gw + 30); cy = y0 + 120 + (i // 2) * (gh + 30) + (1 - k) * 60
        d.rounded_rectangle([cx, cy, cx + gw, cy + gh], radius=26, fill=T["surface"], outline=col, width=4)
        F.text_box(img, lab, (cx + 24, cy + 20, cx + gw - 24, cy + 120), "sans-bold", 32, T["muted"], label="pd-cell",
                   alpha=k)
        d.text((cx + 30, cy + 150), f"you {a}", font=font("mono-bold", 56), fill=col)
        d.text((cx + 30, cy + 220), f"them {b}", font=font("mono", 36), fill=T["muted"])
    d.text((x0, y0 + 20), "points per round", font=font("sans-bold", 36), fill=T["text"])


# ---------------------------------------------------------------- auction (dollar auction)
def auction(img, t, p, model, box, **_):
    h = model.series["hist"]
    n = len(h)
    i = min(n - 1, int(F.seg(p, 0.1, 0.9) * n))
    a, b = int(h[i][0]), int(h[i][1])
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    # the $100 bill
    bx0, by0 = x0 + 140, y0 + 30
    d.rounded_rectangle([bx0, by0, x1 - 140, by0 + 260], radius=18, fill=(60, 95, 60), outline=(150, 200, 140), width=5)
    d.ellipse([(bx0 + x1 - 140) / 2 - 90, by0 + 40, (bx0 + x1 - 140) / 2 + 90, by0 + 220], outline=(170, 215, 160), width=4)
    prize = f"${int(model.values['prize'])}"
    f = font("sans-black", 80)
    d.text(((bx0 + x1 - 140) / 2 - d.textlength(prize, font=f) / 2, by0 + 80), prize, font=f, fill=(220, 240, 210))
    for j, (name, val, col) in enumerate([("A", a, T["accent"]), ("B", b, T["neutral"])]):
        cx = x0 + 180 + j * 520; cy = y0 + 560
        lead = val == max(a, b)
        d.ellipse([cx - 60, cy - 170, cx + 60, cy - 50], fill=col)
        d.rounded_rectangle([cx - 90, cy - 40, cx + 90, cy + 160], radius=40, fill=col)
        lift = 40 if lead else 0
        d.line([(cx + 90, cy), (cx + 140, cy - 120 - lift)], fill=T["text"], width=8)
        d.ellipse([cx + 100, cy - 220 - lift, cx + 200, cy - 120 - lift], fill=(240, 240, 240))
        d.text((cx + 128, cy - 196 - lift), name, font=font("sans-black", 46), fill=T["bg"])
        s = f"${val}"
        f2 = font("mono-bold", 64)
        d.text((cx - d.textlength(s, font=f2) / 2, cy + 190), s, font=f2, fill=T["negative"] if val > 100 else col)
    tot = f"auctioneer has collected ${a + b}"
    f3 = font("sans-bold", 36)
    d.text(((x0 + x1) / 2 - d.textlength(tot, font=f3) / 2, y1 - 60), tot, font=f3, fill=T["muted"])


# ---------------------------------------------------------------- bluff balance (scales)
def bluff_scale(img, t, p, model, box, **_):
    """A betting range drawn as 30 cards: value bets vs bluffs, filling to the balanced share."""
    share = model.values["bluff_share"]
    x0, y0, x1, y1 = box
    n = 30
    k = F.ease_in_out(F.seg(p, 0.05, 0.6))
    n_bluff = int(round(n * share * k))
    cols, cw = 6, 120
    gap = (x1 - x0 - cols * cw) / (cols - 1)
    d = ImageDraw.Draw(img)
    for i in range(n):
        cx = x0 + (i % cols) * (cw + gap); cy = y0 + 110 + (i // cols) * 175
        bluff = i >= n - n_bluff
        im = _card("7", "♣", cw) if bluff else _card("A", "♠", cw)
        F.paste(img, im, (cx, cy))
        if bluff:
            d.rounded_rectangle([cx, cy, cx + cw, cy + int(cw * 1.4)], radius=12, outline=T["negative"], width=6)
    d.text((x0, y0 + 20), "value bets", font=font("sans-bold", 38), fill=T["positive"])
    lab = f"bluffs: {fmt_num(n_bluff / n, 'pct0')}"
    f = font("sans-bold", 38)
    d.text((x1 - d.textlength(lab, font=f), y0 + 20), lab, font=f, fill=T["negative"])


ANIMS = {"coins": coins, "crowd": crowd, "halving": halving, "cards": cards, "roulette": roulette,
         "lottery_balls": lottery_balls, "payoff_matrix": payoff_matrix, "auction": auction,
         "bluff_scale": bluff_scale}
