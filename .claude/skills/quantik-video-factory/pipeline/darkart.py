"""Dark-truth illustration kit (dark-story style): silhouettes, crowds, phones, status objects, heavy dark grade.

Everything is drawn procedurally with PIL on a supersampled canvas (anti-aliased when shrunk back), so no
stock images or licensed art are needed. Coordinates are in output pixels of the canvas box.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# dark-truth palette: cold, heavy, one warning red, one warm light
P = {
    "bg0": (14, 14, 19), "bg1": (4, 4, 6),
    "crowd": (58, 64, 78), "crowd_dk": (36, 40, 50), "ink": (22, 23, 30),
    "bone": (232, 226, 214), "muted": (140, 138, 132),
    "red": (204, 52, 46), "red_dk": (120, 26, 24),
    "glow": (170, 205, 255), "gold": (226, 176, 86), "warm": (255, 214, 150),
    "green": (98, 176, 120),
}


class Art:
    """Supersampled RGBA canvas. All drawing methods take output-pixel coordinates."""

    def __init__(self, w, h, ss=2):
        self.w, self.h, self.ss = int(w), int(h), ss
        self.im = Image.new("RGBA", (self.w * ss, self.h * ss), (0, 0, 0, 0))
        self.gl = Image.new("RGBA", self.im.size, (0, 0, 0, 0))   # light layer, always under the drawing
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def circle(self, x, y, r, fill, outline=None, width=0):
        s = self.ss
        self.d.ellipse([(x - r) * s, (y - r) * s, (x + r) * s, (y + r) * s], fill=fill, outline=outline,
                       width=int(width * s))

    def ellipse(self, box, fill=None, outline=None, width=0):
        s = self.ss
        self.d.ellipse([v * s for v in box], fill=fill, outline=outline, width=int(width * s))

    def rect(self, box, fill=None, r=0, outline=None, width=0):
        s = self.ss
        self.d.rounded_rectangle([v * s for v in box], radius=r * s, fill=fill, outline=outline,
                                 width=int(width * s))

    def poly(self, pts, fill):
        self.d.polygon(self._p(pts), fill=fill)

    def line(self, pts, fill, width, round_=True):
        self.d.line(self._p(pts), fill=fill, width=max(1, int(width * self.ss)), joint="curve")
        if round_:
            for x, y in (pts[0], pts[-1]):
                self.circle(x, y, width / 2, fill)

    def glow(self, x, y, r, color, alpha=120):
        """Soft radial light: a blurred disc rendered small (1/4 scale) over just its own region, then upscaled."""
        ss, k = self.ss, 4
        pad = r * 1.6
        x0, y0 = int(max(0, (x - pad) * ss)), int(max(0, (y - pad) * ss))
        x1, y1 = int(min(self.im.width, (x + pad) * ss)), int(min(self.im.height, (y + pad) * ss))
        if x1 - x0 < k or y1 - y0 < k:
            return
        sw, sh = (x1 - x0) // k, (y1 - y0) // k
        layer = Image.new("RGBA", (sw, sh), color + (0,))
        cx, cy, rr = (x * ss - x0) / k, (y * ss - y0) / k, r * ss / k
        ImageDraw.Draw(layer).ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (alpha,))
        layer = layer.filter(ImageFilter.GaussianBlur(max(1, rr * 0.45))).resize((x1 - x0, y1 - y0), Image.BILINEAR)
        self.gl.alpha_composite(layer, dest=(x0, y0))

    def image(self):
        out = self.gl
        if out.getbbox():
            out = out.copy(); out.putalpha(Image.fromarray(
                (np.asarray(out.getchannel("A"), "float32") * _feather(*out.size)).astype("uint8")))
        out.alpha_composite(self.im)
        return out.resize((self.w, self.h), Image.LANCZOS)


@lru_cache(maxsize=4)
def _feather(w, h, edge=0.16):
    """Alpha ramp so light never ends in a hard edge at the canvas border."""
    fx = np.clip(np.minimum(np.arange(w), np.arange(w)[::-1]) / (w * edge), 0, 1)
    fy = np.clip(np.minimum(np.arange(h), np.arange(h)[::-1]) / (h * edge), 0, 1)
    return (fy[:, None] * fx[None, :]) ** 1.5


# ---------------------------------------------------------------- people
def person(a: Art, x, feet, h, col, phase=None, phone=False, head_down=0.0, arms_up=False, bag=0.0,
           facing=1, screen=None, run=False):
    """A flat silhouette. phase (radians) animates walking; phone=True holds a glowing phone at the face.
    bag (0..1) adds a growing backpack; arms_up = posing/celebrating."""
    r = h * 0.085
    hip = (x, feet - h * 0.46)
    neck = (x + facing * h * 0.02 * (1 if run else 0), feet - h + 2.1 * r)
    head = (neck[0] + facing * head_down * r * 0.9, feet - h + r + head_down * r * 0.5)
    lw, aw = h * 0.075, h * 0.06
    sw = 0.0 if phase is None else math.sin(phase)
    amp = 0.62 if run else 0.42
    # legs
    for sgn in (1, -1):
        ang = sgn * (sw * amp if phase is not None else 0.07)
        knee = (hip[0] + math.sin(ang) * h * 0.24, hip[1] + math.cos(ang) * h * 0.24)
        bend = max(0.0, -sgn * sw) * (0.5 if run else 0.25)
        foot = (knee[0] + math.sin(ang - bend * facing) * h * 0.23, knee[1] + math.cos(ang - bend) * h * 0.23)
        a.line([hip, knee, foot], col, lw)
    # backpack behind the torso
    if bag > 0:
        bw, bh = h * (0.12 + 0.22 * bag), h * (0.16 + 0.3 * bag)
        bx = neck[0] - facing * (h * 0.07 + bw / 2)
        a.rect([bx - bw / 2, neck[1] + h * 0.02, bx + bw / 2, neck[1] + h * 0.02 + bh], fill=tuple(max(0, c - 18) for c in col),
               r=h * 0.04)
    # torso
    a.line([neck, hip], col, h * 0.15)
    sh = (neck[0], neck[1] + h * 0.04)
    if phone:
        elbow = (sh[0] + facing * h * 0.1, sh[1] + h * 0.2)
        hand = (head[0] + facing * h * 0.13, head[1] + h * 0.12)
        a.line([sh, elbow, hand], col, aw)
        ph_w, ph_h = h * 0.05, h * 0.085
        a.glow(hand[0], hand[1] - ph_h * 0.3, h * 0.14, screen or P["glow"], 70)
        a.rect([hand[0] - ph_w / 2, hand[1] - ph_h, hand[0] + ph_w / 2, hand[1]], fill=screen or P["glow"], r=ph_w * 0.2)
        other = (sh[0] - facing * h * 0.05, sh[1] + h * 0.3)
        a.line([sh, other], col, aw)
    elif arms_up:
        for sgn in (1, -1):
            a.line([sh, (sh[0] + sgn * h * 0.15, sh[1] - h * 0.12), (sh[0] + sgn * h * 0.2, sh[1] - h * 0.3)], col, aw)
    else:
        for sgn in (1, -1):
            ang = -sgn * sw * amp * 0.9
            el = (sh[0] + math.sin(ang) * h * 0.2, sh[1] + math.cos(ang) * h * 0.2)
            bend = 0.9 if run else 0.25
            hd = (el[0] + math.sin(ang + bend * facing) * h * 0.18, el[1] + math.cos(ang + bend) * h * 0.18)
            a.line([sh, el, hd], col, aw)
    a.circle(head[0], head[1], r, col)
    return head


def tiny_person(d: ImageDraw.ImageDraw, x, y, s, col):
    """Crowd dot person for grids (head + shoulders), drawn on an already-supersampled draw."""
    d.ellipse([x - s * 0.32, y - s * 0.95, x + s * 0.32, y - s * 0.32], fill=col)
    d.rounded_rectangle([x - s * 0.45, y - s * 0.25, x + s * 0.45, y + s * 0.55], radius=s * 0.3, fill=col)


# ---------------------------------------------------------------- objects
def icon(a: Art, kind, x, y, s, col):
    """Status objects: car, house, plane, ring, bag, phone, watch. (x, y) = centre, s = size."""
    if kind == "car":
        a.rect([x - s * 0.5, y - s * 0.05, x + s * 0.5, y + s * 0.22], fill=col, r=s * 0.08)
        a.poly([(x - s * 0.3, y - s * 0.05), (x - s * 0.17, y - s * 0.26), (x + s * 0.18, y - s * 0.26),
                (x + s * 0.32, y - s * 0.05)], col)
        for wx in (-0.3, 0.3):
            a.circle(x + wx * s, y + s * 0.22, s * 0.1, P["ink"]); a.circle(x + wx * s, y + s * 0.22, s * 0.05, col)
    elif kind == "house":
        a.rect([x - s * 0.38, y - s * 0.1, x + s * 0.38, y + s * 0.32], fill=col)
        a.poly([(x - s * 0.5, y - s * 0.08), (x, y - s * 0.45), (x + s * 0.5, y - s * 0.08)], col)
        a.rect([x - s * 0.07, y + s * 0.08, x + s * 0.07, y + s * 0.32], fill=P["ink"])
    elif kind == "plane":
        a.line([(x - s * 0.45, y + s * 0.1), (x + s * 0.45, y - s * 0.1)], col, s * 0.11)
        a.poly([(x - s * 0.05, y), (x + s * 0.12, y - s * 0.4), (x + s * 0.22, y - s * 0.4), (x + s * 0.1, y)], col)
        a.poly([(x - s * 0.05, y + s * 0.02), (x - s * 0.2, y + s * 0.36), (x - s * 0.1, y + s * 0.36), (x + s * 0.1, y)], col)
    elif kind == "ring":
        a.circle(x, y + s * 0.1, s * 0.3, None, outline=col, width=s * 0.08)
        a.poly([(x, y - s * 0.45), (x + s * 0.15, y - s * 0.28), (x, y - s * 0.15), (x - s * 0.15, y - s * 0.28)], col)
    elif kind == "bag":
        a.rect([x - s * 0.35, y - s * 0.2, x + s * 0.35, y + s * 0.35], fill=col, r=s * 0.05)
        a.d.arc([(x - s * 0.18) * a.ss, (y - s * 0.42) * a.ss, (x + s * 0.18) * a.ss, (y - s * 0.02) * a.ss],
                180, 360, fill=col, width=int(s * 0.06 * a.ss))
    elif kind == "phone":
        a.rect([x - s * 0.22, y - s * 0.4, x + s * 0.22, y + s * 0.4], fill=col, r=s * 0.06)
        a.rect([x - s * 0.18, y - s * 0.34, x + s * 0.18, y + s * 0.3], fill=P["ink"], r=s * 0.03)
    elif kind == "heart":
        a.circle(x - s * 0.15, y - s * 0.08, s * 0.17, col); a.circle(x + s * 0.15, y - s * 0.08, s * 0.17, col)
        a.poly([(x - s * 0.31, y - s * 0.02), (x + s * 0.31, y - s * 0.02), (x, y + s * 0.32)], col)
    elif kind == "coin":
        a.circle(x, y, s * 0.5, col); a.circle(x, y, s * 0.34, None, outline=P["ink"], width=s * 0.07)


# ---------------------------------------------------------------- backgrounds
@lru_cache(maxsize=8)
def backdrop(w, h, tint=None):
    """Vertical gradient + heavy vignette (+ optional coloured haze)."""
    y = np.linspace(0, 1, h)[:, None, None]
    top, bot = np.array(P["bg0"], float), np.array(P["bg1"], float)
    img = np.broadcast_to(top * (1 - y) + bot * y, (h, w, 3)).copy()
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h * 0.45) / (h * 0.62)) ** 2)
    img *= np.clip(1.15 - dist * 0.75, 0.25, 1)[..., None]
    if tint:
        haze = np.exp(-(((xx - w * tint[1]) / (w * 0.5)) ** 2 + ((yy - h * tint[2]) / (h * 0.25)) ** 2))
        img += haze[..., None] * np.array(tint[0], float) * 0.22
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"))


@lru_cache(maxsize=4)
def _grain(w, h, k):
    rng = np.random.default_rng(k)
    g = rng.normal(0, 7, (h // 2, w // 2)).astype("float32")
    g = np.asarray(Image.fromarray(np.clip(g + 128, 0, 255).astype("uint8")).resize((w, h)), "int16") - 128
    return g[..., None]


def film_grain(img, t):
    """Cheap animated grain (3 cached noise plates cycled) — the heavy documentary texture. Keeps blacks black."""
    arr = np.asarray(img, "int16") + _grain(img.width, img.height, int(t * 12) % 3)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))
