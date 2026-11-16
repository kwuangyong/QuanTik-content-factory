"""Pictograms drawn in code (brand palette, thick strokes) to give text-only scenes a visual anchor.

They are icons, not illustrations of real things or people, so they need no licence or credit.
    icon(name, size, color) -> RGBA image        NAMES lists what exists
    python pictos.py                              -> writes a contact sheet to the scratch path given
"""
from __future__ import annotations

import math
from functools import lru_cache

from PIL import Image, ImageDraw

from core import THEME as T

SS = 2  # supersampling for smooth edges


def _c(color, a=255):
    return tuple(color[:3]) + (a,)


def _canvas(size):
    s = size * SS
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im), s


def _arc_pts(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
            for a in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]


def warning(d, s, c, w):
    pad = s * 0.08
    d.polygon([(s / 2, pad), (s - pad, s - pad * 1.4), (pad, s - pad * 1.4)], outline=c, width=w)
    d.line([(s / 2, s * 0.36), (s / 2, s * 0.64)], fill=c, width=int(w * 1.3))
    r = w * 0.9
    d.ellipse([s / 2 - r, s * 0.74 - r, s / 2 + r, s * 0.74 + r], fill=c)


def bulb(d, s, c, w):
    cx, cy, r = s / 2, s * 0.40, s * 0.27
    d.arc([cx - r, cy - r, cx + r, cy + r], 140, 400, fill=c, width=w)
    d.line([(cx - r * 0.55, cy + r * 0.78), (cx - r * 0.42, s * 0.78)], fill=c, width=w)
    d.line([(cx + r * 0.55, cy + r * 0.78), (cx + r * 0.42, s * 0.78)], fill=c, width=w)
    for k in (0.80, 0.88):
        d.line([(cx - r * 0.45, s * k), (cx + r * 0.45, s * k)], fill=c, width=w)
    for ang in (-150, -90, -30):
        x0, y0 = cx + (r + s * 0.06) * math.cos(math.radians(ang)), cy + (r + s * 0.06) * math.sin(math.radians(ang))
        x1, y1 = cx + (r + s * 0.14) * math.cos(math.radians(ang)), cy + (r + s * 0.14) * math.sin(math.radians(ang))
        d.line([(x0, y0), (x1, y1)], fill=c, width=w)


def gear(d, s, c, w):
    cx = cy = s / 2
    R, r_in, teeth = s * 0.30, s * 0.12, 8
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        rr = R + (s * 0.09 if (i % 4) in (1, 2) else 0)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.line(pts + [pts[0]], fill=c, width=w, joint="curve")
    d.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], outline=c, width=w)


def scale(d, s, c, w):
    cx = s / 2
    d.line([(cx, s * 0.18), (cx, s * 0.82)], fill=c, width=w)
    d.line([(s * 0.30, s * 0.82), (s * 0.70, s * 0.82)], fill=c, width=w)
    d.line([(s * 0.14, s * 0.28), (s * 0.86, s * 0.28)], fill=c, width=w)
    for x in (s * 0.22, s * 0.78):
        d.line([(x, s * 0.28), (x - s * 0.10, s * 0.55)], fill=c, width=max(2, w // 2))
        d.line([(x, s * 0.28), (x + s * 0.10, s * 0.55)], fill=c, width=max(2, w // 2))
        d.arc([x - s * 0.12, s * 0.45, x + s * 0.12, s * 0.65], 0, 180, fill=c, width=w)


def shield(d, s, c, w):
    pts = [(s / 2, s * 0.10), (s * 0.84, s * 0.22), (s * 0.80, s * 0.55), (s / 2, s * 0.90), (s * 0.20, s * 0.55),
           (s * 0.16, s * 0.22)]
    d.line(pts + [pts[0]], fill=c, width=w, joint="curve")
    d.line([(s * 0.36, s * 0.50), (s * 0.47, s * 0.62), (s * 0.66, s * 0.38)], fill=c, width=w, joint="curve")


def target(d, s, c, w):
    cx = cy = s / 2
    for r in (0.40, 0.27, 0.13):
        d.ellipse([cx - s * r, cy - s * r, cx + s * r, cy + s * r], outline=c, width=w)
    d.line([(cx, cy), (s * 0.92, s * 0.08)], fill=c, width=w)
    d.polygon([(s * 0.92, s * 0.08), (s * 0.80, s * 0.10), (s * 0.90, s * 0.20)], fill=c)


def coins(d, s, c, w):
    for i in range(4):
        y = s * (0.70 - i * 0.13)
        d.ellipse([s * 0.22, y - s * 0.08, s * 0.78, y + s * 0.08], outline=c, width=w)
    d.line([(s * 0.22, s * 0.31), (s * 0.22, s * 0.70)], fill=c, width=w)
    d.line([(s * 0.78, s * 0.31), (s * 0.78, s * 0.70)], fill=c, width=w)


def chart_up(d, s, c, w):
    d.line([(s * 0.12, s * 0.12), (s * 0.12, s * 0.88), (s * 0.88, s * 0.88)], fill=c, width=w)
    pts = [(s * 0.18, s * 0.74), (s * 0.38, s * 0.58), (s * 0.54, s * 0.66), (s * 0.82, s * 0.28)]
    d.line(pts, fill=c, width=w, joint="curve")
    d.polygon([(s * 0.86, s * 0.22), (s * 0.70, s * 0.28), (s * 0.82, s * 0.40)], fill=c)


def chart_down(d, s, c, w):
    d.line([(s * 0.12, s * 0.12), (s * 0.12, s * 0.88), (s * 0.88, s * 0.88)], fill=c, width=w)
    pts = [(s * 0.18, s * 0.26), (s * 0.40, s * 0.44), (s * 0.56, s * 0.36), (s * 0.82, s * 0.72)]
    d.line(pts, fill=c, width=w, joint="curve")
    d.polygon([(s * 0.86, s * 0.78), (s * 0.82, s * 0.60), (s * 0.70, s * 0.72)], fill=c)


def hourglass(d, s, c, w):
    d.line([(s * 0.25, s * 0.12), (s * 0.75, s * 0.12)], fill=c, width=w)
    d.line([(s * 0.25, s * 0.88), (s * 0.75, s * 0.88)], fill=c, width=w)
    d.line([(s * 0.30, s * 0.12), (s * 0.70, s * 0.88)], fill=c, width=w)
    d.line([(s * 0.70, s * 0.12), (s * 0.30, s * 0.88)], fill=c, width=w)
    d.polygon([(s * 0.40, s * 0.80), (s * 0.60, s * 0.80), (s / 2, s * 0.62)], fill=c)


def dice(d, s, c, w):
    d.rounded_rectangle([s * 0.16, s * 0.16, s * 0.84, s * 0.84], radius=s * 0.12, outline=c, width=w)
    r = s * 0.055
    for x, y in ((0.32, 0.32), (0.68, 0.68), (0.5, 0.5), (0.68, 0.32), (0.32, 0.68)):
        d.ellipse([s * x - r, s * y - r, s * x + r, s * y + r], fill=c)


def _lens_arc(s, x0, x1, y, h, up):
    """Circular arc through (x0,y) and (x1,y) bulging by h (up or down)."""
    c = x1 - x0
    R = c * c / (8 * h) + h / 2
    cy = y + (R - h) if up else y - (R - h)
    a = math.degrees(math.asin((c / 2) / R))
    mid = 270 if up else 90
    return _arc_pts((x0 + x1) / 2, cy, R, mid - a, mid + a)


def eye(d, s, c, w):
    d.line(_lens_arc(s, s * 0.08, s * 0.92, s / 2, s * 0.24, True), fill=c, width=w, joint="curve")
    d.line(_lens_arc(s, s * 0.08, s * 0.92, s / 2, s * 0.24, False), fill=c, width=w, joint="curve")
    r = s * 0.15
    d.ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r], outline=c, width=w)
    d.ellipse([s / 2 - r * 0.45, s / 2 - r * 0.45, s / 2 + r * 0.45, s / 2 + r * 0.45], fill=c)


def people(d, s, c, w):
    for x, k in ((0.30, 0.8), (0.70, 0.8), (0.50, 1.0)):
        r = s * 0.09 * k
        cy = s * (0.36 if k == 1.0 else 0.42)
        d.ellipse([s * x - r, cy - r, s * x + r, cy + r], outline=c, width=w)
        d.arc([s * x - r * 2, cy + r * 1.3, s * x + r * 2, cy + r * 5.3], 180, 360, fill=c, width=w)


def magnifier(d, s, c, w):
    r = s * 0.24
    d.ellipse([s * 0.38 - r, s * 0.38 - r, s * 0.38 + r, s * 0.38 + r], outline=c, width=w)
    d.line([(s * 0.56, s * 0.56), (s * 0.86, s * 0.86)], fill=c, width=int(w * 1.6))


def book(d, s, c, w):
    d.line([(s / 2, s * 0.24), (s / 2, s * 0.84)], fill=c, width=w)
    for sx in (-1, 1):
        x1 = s / 2 + sx * s * 0.36
        d.line([(s / 2, s * 0.24), (x1, s * 0.18), (x1, s * 0.78), (s / 2, s * 0.84)], fill=c, width=w, joint="curve")
        for k in (0.36, 0.48, 0.60):
            d.line([(s / 2 + sx * s * 0.08, s * k), (s / 2 + sx * s * 0.28, s * (k - 0.02))], fill=c, width=max(2, w // 2))


def building(d, s, c, w):
    d.polygon([(s / 2, s * 0.10), (s * 0.88, s * 0.30), (s * 0.12, s * 0.30)], outline=c, width=w)
    for x in (0.22, 0.40, 0.60, 0.78):
        d.line([(s * x, s * 0.36), (s * x, s * 0.76)], fill=c, width=w)
    d.line([(s * 0.10, s * 0.84), (s * 0.90, s * 0.84)], fill=c, width=w)


def cards(d, s, c, w):
    for i, ang in enumerate((-14, 0, 14)):
        card = Image.new("RGBA", (int(s * 0.36), int(s * 0.52)), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([w, w, card.width - w, card.height - w], radius=s * 0.04, outline=c, width=w,
                             fill=_c(T["raised"]))
        cd.text((card.width * 0.30, card.height * 0.28), "JQK"[i], fill=c,
                font=__import__("core").font("sans-black", int(s * 0.22)))
        card = card.rotate(-ang, expand=True, resample=Image.BICUBIC)
        d._image.paste(card, (int(s * (0.18 + 0.20 * i) - card.width * 0.25), int(s * 0.22)), card)


def check(d, s, c, w):
    d.ellipse([s * 0.12, s * 0.12, s * 0.88, s * 0.88], outline=c, width=w)
    d.line([(s * 0.30, s * 0.52), (s * 0.45, s * 0.66), (s * 0.72, s * 0.36)], fill=c, width=int(w * 1.3), joint="curve")


DRAW = {"warning": warning, "bulb": bulb, "gear": gear, "scale": scale, "shield": shield, "target": target,
        "coins": coins, "chart_up": chart_up, "chart_down": chart_down, "hourglass": hourglass, "dice": dice,
        "eye": eye, "people": people, "magnifier": magnifier, "book": book, "building": building, "cards": cards,
        "check": check}
NAMES = sorted(DRAW)


@lru_cache(maxsize=64)
def icon(name, size=360, color=None):
    color = color or T["accent"]
    im, d, s = _canvas(size)
    DRAW[name](d, s, _c(color), max(4, int(s * 0.045)))
    return im.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "pictos.png"
    cols = 6
    rows = (len(NAMES) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 200, rows * 230), T["bg"])
    from core import font

    for i, n in enumerate(NAMES):
        x, y = (i % cols) * 200, (i // cols) * 230
        sheet.paste(icon(n, 160), (x + 20, y + 10), icon(n, 160))
        ImageDraw.Draw(sheet).text((x + 20, y + 180), n, font=font("sans", 22), fill=T["muted"])
    sheet.save(out)
    print(out)
