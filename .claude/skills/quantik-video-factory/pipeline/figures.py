"""Flat-vector characters and props drawn in code, composed into small animated "stage" scenes.

Characters are generic roles (an investor, a quant, a rival player, a professor) — never likenesses of real
people. Real people keep their name card / licensed photo (knowledge/images). Props carry no digits, so nothing on
screen escapes the number check; speech-bubble text is drawn with frames.text_box and goes through QA.

    stage(spec, w, h, t, p) -> RGBA image      spec = {"cast": [...], "props": [...], "bubble": {...}}
    cast item:  {"who": "investor|quant|rival|professor|analyst", "pose": POSES, "face": FACES, "x": 0..1, "flip": bool}
    prop item:  {"what": PROPS, "x": 0..1, "y": 0..1, "s": scale}
    python figures.py sheet.png                 contact sheet of every character, pose, face and prop
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

from core import THEME as T

SS = 2
U = 400.0   # character coordinates: feet at y=0, top of head at about y=-360

CHARACTERS = {
    "investor": {"skin": (241, 196, 160), "hair": (52, 40, 34), "style": "short", "shirt": T["accent"], "glasses": False},
    "quant": {"skin": (224, 172, 130), "hair": (25, 25, 28), "style": "short", "shirt": T["positive"], "glasses": True},
    "rival": {"skin": (198, 136, 100), "hair": (92, 60, 40), "style": "cap", "shirt": T["negative"], "glasses": False},
    "professor": {"skin": (240, 204, 176), "hair": (200, 200, 200), "style": "bald", "shirt": (120, 132, 140),
                  "glasses": True, "tie": T["accent"]},
    "analyst": {"skin": (236, 188, 150), "hair": (60, 36, 30), "style": "bun", "shirt": T["neutral"], "glasses": False},
}
PANTS = (40, 52, 64)

# arm targets per pose: (elbow, hand) for the character's left (viewer right) and right (viewer left) arms
POSES = {
    "stand": (((62, -190), (60, -128)), ((-62, -190), (-60, -128))),
    "point": (((96, -236), (162, -262)), ((-62, -190), (-60, -128))),
    "think": (((62, -190), (60, -128)), ((-60, -200), (-14, -276))),
    "worried": (((86, -300), (40, -350)), ((-86, -300), (-40, -350))),
    "cheer": (((82, -300), (100, -372)), ((-82, -300), (-100, -372))),
    "shrug": (((84, -214), (116, -252)), ((-84, -214), (-116, -252))),
    "present": (((78, -204), (122, -222)), ((-78, -204), (-122, -222))),
    "hold": (((62, -196), (26, -170)), ((-62, -196), (-26, -170))),
}
FACES = ["neutral", "smile", "worried", "surprised", "focus"]


def _k(height):
    return height * SS / U


def _pt(p, k, ox, oy, flip=False):
    x, y = p
    return (ox + (-x if flip else x) * k, oy + y * k)


def _draw_character(d, who, pose, face, k, ox, oy, flip=False, blink=False):
    c = CHARACTERS[who]
    P = lambda p: _pt(p, k, ox, oy, flip)
    w = lambda v: max(1, int(v * k))
    outline = (12, 18, 15)
    # legs
    for x in (-24, 24):
        a, b = P((x - 17, -124)), P((x + 17, 0))
        d.rounded_rectangle([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], radius=w(12), fill=PANTS)
        s0, s1 = P((x - 20, -14)), P((x + 24, 2))
        d.rounded_rectangle([min(s0[0], s1[0]), s0[1], max(s0[0], s1[0]), s1[1]], radius=w(8), fill=(24, 28, 30))
    # arms behind torso edges
    arms = POSES[pose]
    for side, (elbow, hand) in zip((1, -1), arms):
        sh = (50 * side, -250)
        d.line([P(sh), P(elbow), P(hand)], fill=c["shirt"], width=w(26), joint="curve")
        hx, hy = P(hand)
        r = w(14)
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=c["skin"])
    # torso
    a, b = P((-56, -262)), P((56, -118))
    d.rounded_rectangle([min(a[0], b[0]), a[1], max(a[0], b[0]), b[1]], radius=w(30), fill=c["shirt"])
    if c.get("tie"):
        d.polygon([P((0, -258)), P((10, -236)), P((0, -170)), P((-10, -236))], fill=c["tie"])
        d.line([P((-30, -258)), P((0, -232)), P((30, -258))], fill=(235, 235, 235), width=w(6))
    # neck + head
    n0, n1 = P((-12, -282)), P((12, -256))
    d.rectangle([min(n0[0], n1[0]), n0[1], max(n0[0], n1[0]), n1[1]], fill=c["skin"])
    hx, hy = P((0, -316))
    hr = w(44)
    if c["style"] == "bun":
        br = w(20)
        bx, by = P((0, -368))
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=c["hair"])
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=c["skin"])
    # hair
    if c["style"] in ("short", "bun"):
        d.chord([hx - hr - w(2), hy - hr - w(4), hx + hr + w(2), hy + hr * 0.5], 180, 360, fill=c["hair"])
    elif c["style"] == "cap":
        d.chord([hx - hr - w(3), hy - hr - w(6), hx + hr + w(3), hy + hr * 0.4], 180, 360, fill=c["shirt"])
        vx = hx + (-1 if flip else 1) * hr * 0.2
        d.rounded_rectangle([vx - hr * 0.2 if not flip else vx - hr * 1.3, hy - hr * 0.42,
                             vx + hr * 1.3 if not flip else vx + hr * 0.2, hy - hr * 0.22], radius=w(6), fill=c["shirt"])
    elif c["style"] == "bald":
        for sx in (-1, 1):
            d.chord([hx + sx * hr * 0.55 - hr * 0.5, hy - hr * 0.5, hx + sx * hr * 0.55 + hr * 0.5, hy + hr * 0.3],
                    90 if sx > 0 else 270, 270 if sx > 0 else 450, fill=c["hair"]) if False else \
                d.ellipse([hx + sx * hr * 0.82 - hr * 0.26, hy - hr * 0.45, hx + sx * hr * 0.82 + hr * 0.26,
                           hy + hr * 0.15], fill=c["hair"])
    # face
    ex = hr * 0.38
    ey = hy - hr * 0.02
    er = w(5.5 if face != "surprised" else 7.5)
    for sx in (-1, 1):
        cx = hx + sx * ex
        if blink:
            d.line([(cx - er, ey), (cx + er, ey)], fill=outline, width=w(3))
        else:
            d.ellipse([cx - er, ey - er, cx + er, ey + er], fill=outline)
        # brows
        by = ey - hr * 0.28
        if face == "worried":
            d.line([(cx - er * 1.6, by - sx * 0 + (w(4) if sx < 0 else -w(2))), (cx + er * 1.6, by + (-w(2) if sx < 0 else w(4)))],
                   fill=outline, width=w(3))
        elif face == "focus":
            d.line([(cx - er * 1.6, by + (w(3) if sx > 0 else -w(1))), (cx + er * 1.6, by + (-w(1) if sx > 0 else w(3)))],
                   fill=outline, width=w(3))
        elif face == "surprised":
            d.arc([cx - er * 1.6, by - er * 1.4, cx + er * 1.6, by + er * 0.6], 200, 340, fill=outline, width=w(3))
        if c["glasses"]:
            gr = w(13)
            d.ellipse([cx - gr, ey - gr, cx + gr, ey + gr], outline=outline, width=w(3))
    if c["glasses"]:
        d.line([(hx - ex + w(13), ey), (hx + ex - w(13), ey)], fill=outline, width=w(3))
    my, mw = hy + hr * 0.42, hr * 0.32
    if face == "smile":
        d.arc([hx - mw, my - mw * 0.9, hx + mw, my + mw * 0.5], 20, 160, fill=outline, width=w(4))
    elif face == "worried":
        d.arc([hx - mw * 0.8, my - mw * 0.1, hx + mw * 0.8, my + mw * 0.9], 200, 340, fill=outline, width=w(4))
    elif face == "surprised":
        r = w(8)
        d.ellipse([hx - r, my - r, hx + r, my + r * 1.3], fill=outline)
    else:
        d.line([(hx - mw * 0.6, my + w(2)), (hx + mw * 0.6, my + w(2))], fill=outline, width=w(4))


@lru_cache(maxsize=256)
def character(who, pose="stand", face="neutral", height=340, flip=False, blink=False):
    """RGBA sprite, feet at bottom centre."""
    k = _k(height)
    wpx, hpx = int(360 * k), int(400 * k)
    im = Image.new("RGBA", (wpx, hpx), (0, 0, 0, 0))
    _draw_character(ImageDraw.Draw(im), who, pose, face, k, wpx / 2, hpx - 2, flip, blink)
    return im.resize((wpx // SS, hpx // SS), Image.LANCZOS)


# ---------------------------------------------------------------- props (no digits anywhere)
def _prop_canvas(w, h):
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def _done(im):
    return im.resize((im.width // SS, im.height // SS), Image.LANCZOS)


def _candles(d, x0, y0, x1, y1, trend, s):
    n = 7
    step = (x1 - x0) / n
    level = 0.75 if trend > 0 else 0.25
    for i in range(n):
        up = (i % 3 != 1) == (trend > 0)
        nxt = level - trend * 0.08 + (0.04 if i % 2 else -0.03)
        top, bot = sorted([level, nxt])
        col = T["positive"] if up else T["negative"]
        cx = x0 + step * (i + 0.5)
        d.line([(cx, y0 + (y1 - y0) * (top - 0.06)), (cx, y0 + (y1 - y0) * (bot + 0.06))], fill=col, width=int(3 * s))
        d.rectangle([cx - step * 0.28, y0 + (y1 - y0) * top, cx + step * 0.28, y0 + (y1 - y0) * max(bot, top + 0.03)], fill=col)
        level = nxt


def phone(trend=-1, w=150):
    h = int(w * 1.9)
    im, d = _prop_canvas(w, h)
    s = SS
    d.rounded_rectangle([0, 0, w * s - 1, h * s - 1], radius=26 * s, fill=(22, 26, 30), outline=(70, 80, 90), width=4 * s)
    d.rounded_rectangle([10 * s, 34 * s, (w - 10) * s, (h - 30) * s], radius=12 * s, fill=(10, 16, 14))
    _candles(d, 18 * s, 50 * s, (w - 18) * s, (h - 50) * s, trend, s)
    return _done(im)


def laptop(trend=1, w=330):
    h = int(w * 0.72)
    im, d = _prop_canvas(w, h)
    s = SS
    d.rounded_rectangle([20 * s, 0, (w - 20) * s, int(h * 0.80) * s], radius=12 * s, fill=(30, 36, 42), outline=(80, 90, 100), width=3 * s)
    d.rectangle([32 * s, 12 * s, (w - 32) * s, int(h * 0.80 - 12) * s], fill=(10, 16, 14))
    pts = [(40, 0.75), (90, 0.62), (130, 0.68), (180, 0.45), (230, 0.50), (w - 44, 0.22)] if trend > 0 else \
          [(40, 0.25), (90, 0.40), (130, 0.35), (180, 0.55), (230, 0.50), (w - 44, 0.78)]
    d.line([(x * s, (12 + (h * 0.80 - 24) * yy) * s) for x, yy in pts], fill=T["positive"] if trend > 0 else T["negative"],
           width=5 * s, joint="curve")
    d.polygon([(0, int(h * 0.82) * s), (w * s, int(h * 0.82) * s), ((w - 12) * s, h * s - 1), (12 * s, h * s - 1)],
              fill=(60, 68, 76))
    return _done(im)


def poker_table(w=880):
    h = int(w * 0.36)
    im, d = _prop_canvas(w, h)
    s = SS
    d.ellipse([0, 0, w * s, h * s * 2], fill=(92, 58, 36))
    d.ellipse([18 * s, 16 * s, (w - 18) * s, h * s * 2 - 16 * s], fill=(28, 96, 64))
    d.ellipse([60 * s, 50 * s, (w - 60) * s, h * s * 2 - 50 * s], outline=(60, 130, 92), width=4 * s)
    # chips
    for cx, col in ((w * 0.42, T["negative"]), (w * 0.50, (235, 235, 235)), (w * 0.58, T["accent"])):
        for i in range(4):
            y = h * 0.62 - i * 9
            d.ellipse([(cx - 26) * s, (y - 9) * s, (cx + 26) * s, (y + 9) * s], fill=col, outline=(20, 20, 20), width=2 * s)
    return _done(im.crop((0, 0, w * s, h * s)))


def cards_fan(w=200, ranks=("J", "Q", "K")):
    from core import font

    im = Image.new("RGBA", (w, int(w * 0.9)), (0, 0, 0, 0))
    for i, r in enumerate(ranks):
        card = Image.new("RGBA", (int(w * 0.42), int(w * 0.6)), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([2, 2, card.width - 3, card.height - 3], radius=10, fill=(245, 242, 235), outline=(40, 40, 40), width=3)
        cd.text((10, 6), r, font=font("sans-black", int(w * 0.16)), fill=T["negative"] if i == 1 else (25, 25, 25))
        card = card.rotate(25 - 25 * i, expand=True, resample=Image.BICUBIC)
        im.paste(card, (int(w * 0.10 + i * w * 0.18), int(w * 0.10 + abs(i - 1) * 10)), card)
    return im


def chalkboard(w=360):
    from core import font

    h = int(w * 0.66)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=14, fill=(92, 62, 40))
    d.rectangle([14, 14, w - 15, h - 15], fill=(30, 52, 42))
    f = font("mono-bold", int(w * 0.11))
    d.text((32, 30), "E[X] > σ ?", font=f, fill=(225, 232, 226))
    d.text((32, 30 + int(w * 0.15)), "f* = W − q/R", font=f, fill=(225, 232, 226))
    d.line([(32, h - 40), (w * 0.45, h - 70), (w * 0.62, h - 55), (w - 40, h - 95)], fill=T["accent"], width=4)
    return im


def book(w=170, color=None):
    h = int(w * 1.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    color = color or T["accent"]
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=color)
    d.rectangle([0, 0, int(w * 0.12), h - 1], fill=tuple(int(v * 0.7) for v in color[:3]))
    for i, ww in enumerate((0.6, 0.45, 0.5)):
        y = int(h * (0.22 + 0.1 * i))
        d.rounded_rectangle([int(w * 0.22), y, int(w * (0.22 + ww)), y + 10], radius=5, fill=(250, 245, 235))
    return im


def newspaper(w=260):
    h = int(w * 0.8)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(236, 232, 220), outline=(80, 80, 80), width=2)
    d.rectangle([14, 14, w - 15, 44], fill=(40, 40, 40))
    for col in range(2):
        x0 = 14 + col * (w - 28) // 2
        for i in range(7):
            d.line([(x0 + 4, 60 + i * 16), (x0 + (w - 28) // 2 - 10, 60 + i * 16)], fill=(120, 120, 120), width=5)
    return im


def chips(w=180):
    im = Image.new("RGBA", (w, int(w * 0.7)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for j, (cx, col) in enumerate(((w * 0.28, T["negative"]), (w * 0.62, T["accent"]), (w * 0.45, (235, 235, 235)))):
        for i in range(5 - j):
            y = w * 0.55 - i * 12 - (j == 2) * 0
            d.ellipse([cx - 34, y - 12, cx + 34, y + 12], fill=col, outline=(20, 20, 20), width=2)
    return im


PROPS = {"phone_down": lambda: phone(-1), "phone_up": lambda: phone(1), "laptop_up": lambda: laptop(1),
         "laptop_down": lambda: laptop(-1), "poker_table": poker_table, "cards": cards_fan, "chalkboard": chalkboard,
         "book": book, "newspaper": newspaper, "chips": chips}


@lru_cache(maxsize=64)
def prop(name):
    return PROPS[name]()


# ---------------------------------------------------------------- stage
def _ease_back(x):
    x = max(0.0, min(1.0, x))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def stage(spec, w, h, t, p):
    """Compose one animated frame of a stage: props slide/pop in, characters breathe and blink."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ground = h - 6
    back = [x for x in spec.get("props", []) if x["what"] in ("chalkboard",)]
    table = [x for x in spec.get("props", []) if x["what"] == "poker_table"]
    front = [x for x in spec.get("props", []) if x not in back and x not in table]
    for i, pr in enumerate(back):
        _place_prop(im, pr, w, h, p, i)
    cast = spec.get("cast", [])
    ch = int(h * 0.92)
    tb = None
    if table:  # players sit behind the table: their waist is at the table's top edge, legs hidden
        tb0 = prop("poker_table")
        tb = tb0.resize((w, int(tb0.height * w / tb0.width * 0.5)), Image.LANCZOS)
        table_top = h - tb.height
    for i, c in enumerate(cast):
        a = _ease_back((p - 0.04 - 0.08 * i) / 0.22)
        if a <= 0.01:
            continue
        blink = (t + i * 0.7) % 3.1 < 0.12
        spr = character(c["who"], c.get("pose", "stand"), c.get("face", "neutral"), ch, bool(c.get("flip")), blink)
        bob = 4 * math.sin(2 * math.pi * (t / 1.9 + i * 0.3))
        x = int(w * c.get("x", 0.5) - spr.width / 2)
        feet = (table_top + int(spr.height * 0.40)) if table else ground
        y = int(feet - spr.height + (1 - a) * 80 + bob)
        im.alpha_composite(spr, (x, y))
    if tb is not None:
        a = min(1.0, max(0.0, p / 0.12))
        im.alpha_composite(tb, (0, int(h - tb.height + (1 - a) * 60)))
    for i, pr in enumerate(front):
        _place_prop(im, pr, w, h, p, i + 1)
    return im


def _place_prop(im, pr, w, h, p, i):
    a = _ease_back((p - 0.10 - 0.06 * i) / 0.22)
    if a <= 0.01:
        return
    sp = prop(pr["what"])
    s = pr.get("s", 1.0) * max(0.05, a)
    sp = sp.resize((max(1, int(sp.width * s)), max(1, int(sp.height * s))), Image.LANCZOS)
    x = int(w * pr.get("x", 0.5) - sp.width / 2)
    y = int(h * pr.get("y", 0.62) - sp.height / 2)
    im.alpha_composite(sp, (max(0, min(w - sp.width, x)), max(0, min(h - sp.height, y))))


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "figures.png"
    W_, H_ = 1500, 1400
    sheet = Image.new("RGBA", (W_, H_), T["bg"] + (255,))
    for i, who in enumerate(CHARACTERS):
        sheet.alpha_composite(character(who, "stand", "smile", 260), (20 + i * 290, 10))
    for i, pose in enumerate(POSES):
        sheet.alpha_composite(character("quant", pose, FACES[i % len(FACES)], 230), (10 + i * 185, 300))
    sheet.alpha_composite(stage({"cast": [{"who": "investor", "pose": "worried", "face": "worried", "x": 0.3}],
                                 "props": [{"what": "phone_down", "x": 0.72}]}, 700, 360, 1, 1), (0, 580))
    sheet.alpha_composite(stage({"cast": [{"who": "rival", "pose": "hold", "face": "focus", "x": 0.25},
                                          {"who": "investor", "pose": "think", "face": "neutral", "x": 0.75, "flip": True}],
                                 "props": [{"what": "poker_table"}]}, 760, 360, 1, 1), (720, 580))
    x = 10
    for n in PROPS:
        pi = prop(n)
        k = min(1.0, 260 / max(pi.width, pi.height))
        pi = pi.resize((int(pi.width * k), int(pi.height * k)))
        sheet.alpha_composite(pi, (x, 1000))
        x += pi.width + 20
    sheet.convert("RGB").save(out)
    print(out)
