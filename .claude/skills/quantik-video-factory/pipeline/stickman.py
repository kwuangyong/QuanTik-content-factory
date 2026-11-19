"""Stickman scene composer for dark-story: every scene is staged to match its narration line.

A scene spec (episode JSON, field "stick") is a small stage direction:

    {"set": "office", "accent": "red",
     "items": [
        {"t": "man", "x": 300, "pose": "slump", "face": "sad", "col": "bone"},
        {"t": "man", "x": 760, "pose": "walk", "move": [980, 0.2, 0.9], "col": "red", "hold": "briefcase"},
        {"t": "prop", "k": "coin", "x": 540, "y": 120, "motion": "rain", "n": 12},
        {"t": "bubble", "x": 300, "y": 120, "text": "Again?", "at": 0.4},
        {"t": "label", "x": 540, "y": 40, "text": "RENT", "col": "red", "at": 0.2},
        {"t": "arrow", "from": [200, 300], "to": [800, 200], "at": 0.3}]}

Coordinates are pixels inside the illustration band (1080 x 710, ground line at y = 640).
Poses: stand walk run sit slump cheer point shrug fall think push climb carry phone cry hold flip bet wave kneel.
Props: see PROPS. Motions: pop fall rain fly pile shrink float spin pulse shake burn drain.
Everything is drawn in code (no stock art), supersampled for clean anti-aliased strokes.
"""
from __future__ import annotations

import math

import numpy as np

import darkart as G
from core import font

P = G.P
W, H = 1080, 710
GROUND = H - 70
COLS = {"bone": P["bone"], "red": P["red"], "gold": P["gold"], "green": P["green"], "glow": P["glow"],
        "muted": P["muted"], "crowd": P["crowd"], "warm": P["warm"], "ink": P["ink"], "blue": (90, 140, 220),
        "orange": (238, 140, 70), "purple": (150, 110, 210), "teal": (70, 180, 170), "pink": (230, 120, 160)}


def col(c, default="bone"):
    if isinstance(c, (list, tuple)):
        return tuple(c)
    return COLS.get(c or default, COLS.get(default) or COLS["bone"])


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def seg(p, a, b):
    return max(0.0, min(1.0, (p - a) / max(1e-6, b - a)))


def mix(c1, c2, k):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * k) for i in range(3))


# ================================================================ settings (backgrounds inside the band)
def _set_city(a, t, acc):
    rng = np.random.default_rng(4)
    x = 0
    while x < W:
        bw, bh = int(rng.integers(60, 140)), int(rng.integers(160, 420))
        a.rect([x, GROUND - bh, x + bw - 6, GROUND], fill=(24, 26, 36))
        for wy in range(GROUND - bh + 16, GROUND - 20, 30):
            for wx in range(x + 10, x + bw - 20, 22):
                if rng.random() < 0.22:
                    a.rect([wx, wy, wx + 9, wy + 13], fill=(78, 70, 48))
        x += bw
    a.circle(900, 90, 40, (200, 196, 180))


def _set_office(a, t, acc):
    a.rect([60, 30, 1020, 330], fill=(20, 22, 30), r=6)
    for k in range(4):
        a.line([(60 + k * 320, 30), (60 + k * 320, 330)], P["ink"], 10)
    a.rect([0, GROUND - 160, W, GROUND - 150], fill=(34, 36, 46))
    for x in (140, 520, 900):
        a.rect([x - 110, GROUND - 150, x + 110, GROUND - 130], fill=(40, 42, 52), r=4)
        a.rect([x - 40, GROUND - 230, x + 40, GROUND - 160], fill=(60, 90, 130), r=6)


def _set_casino(a, t, acc):
    a.ellipse([80, GROUND - 230, 1000, GROUND + 40], fill=(20, 80, 52))
    a.ellipse([110, GROUND - 210, 970, GROUND + 20], fill=(26, 100, 64))
    for x in (220, 540, 860):
        a.glow(x, 60, 120, P["warm"], 70)
        a.poly([(x - 40, 40), (x + 40, 40), (x + 70, 90), (x - 70, 90)], (60, 50, 34))


def _set_home(a, t, acc):
    a.rect([640, 60, 960, 330], fill=(26, 34, 52), r=8, outline=(60, 56, 46), width=10)
    a.line([(800, 60), (800, 330)], (60, 56, 46), 8); a.line([(640, 195), (960, 195)], (60, 56, 46), 8)
    a.rect([80, GROUND - 150, 520, GROUND - 40], fill=(70, 48, 44), r=26)
    a.rect([60, GROUND - 210, 120, GROUND - 40], fill=(80, 56, 50), r=20)
    a.rect([480, GROUND - 210, 540, GROUND - 40], fill=(80, 56, 50), r=20)


def _set_street(a, t, acc):
    a.rect([0, GROUND, W, H], fill=(28, 28, 32))
    for k in range(6):
        x = (k * 220 - t * 80) % (W + 220) - 110
        a.rect([x, GROUND + 26, x + 110, GROUND + 34], fill=(120, 116, 100))
    a.rect([120, 120, 132, GROUND], fill=(60, 60, 66)); a.rect([120, 112, 220, 124], fill=(60, 60, 66))
    a.glow(210, 150, 140, P["warm"], 80)


def _set_stage(a, t, acc):
    a.rect([0, 0, 150, GROUND], fill=(90, 20, 26)); a.rect([W - 150, 0, W, GROUND], fill=(90, 20, 26))
    a.rect([0, 0, W, 50], fill=(110, 26, 30))
    a.poly([(480, 0), (600, 0), (800, GROUND + 10), (280, GROUND + 10)], (44, 40, 34))


def _set_lab(a, t, acc):
    a.rect([120, 40, 960, 360], fill=(26, 46, 38), r=10, outline=(90, 70, 50), width=12)
    rng = np.random.default_rng(9)
    for _ in range(14):
        x, y = rng.integers(160, 900), rng.integers(70, 330)
        a.line([(x, y), (x + rng.integers(20, 70), y + rng.integers(-8, 8))], (150, 170, 150), 3)


def _set_bank(a, t, acc):
    a.poly([(140, 120), (540, 20), (940, 120)], (52, 52, 60))
    for x in range(190, 920, 120):
        a.rect([x, 130, x + 46, GROUND - 20], fill=(58, 58, 66))
    a.rect([140, GROUND - 24, 940, GROUND], fill=(66, 66, 74))


def _set_market(a, t, acc):
    for i, x in enumerate((90, 380, 670)):
        a.rect([x, 50, x + 300, 260], fill=(14, 18, 24), r=10, outline=(50, 56, 70), width=5)
        for k in range(5):
            y = 80 + k * 34
            w = 60 + int(150 * (0.5 + 0.5 * math.sin(t * 2 + i + k)))
            a.rect([x + 20, y, x + 20 + w, y + 16], fill=(P["green"] if (i + k) % 3 else P["red"]), r=4)


def _set_sea(a, t, acc):
    for k in range(5):
        y = GROUND - 120 + k * 30
        pts = [(x, y + 10 * math.sin(x / 70 + t * 2 + k)) for x in range(0, W + 40, 40)]
        a.line(pts, (30 + 8 * k, 70 + 10 * k, 110 + 10 * k), 18)


def _set_void(a, t, acc):
    pass


def _set_crowdwall(a, t, acc):
    rng = np.random.default_rng(2)
    for row in range(3):
        for k in range(16):
            x = 40 + k * 66 + (row % 2) * 30
            y = GROUND - 140 - row * 70
            a.circle(x, y, 18, (40 + row * 6, 44 + row * 6, 56 + row * 6))
            a.rect([x - 22, y + 18, x + 22, y + 80], fill=(40 + row * 6, 44 + row * 6, 56 + row * 6), r=14)


SETS = {k[5:]: v for k, v in dict(globals()).items() if k.startswith("_set_")}


# ================================================================ stickman
# pose = torso lean, head tilt, (shoulder, elbow) back arm, front arm, (hip, knee) back leg, front leg  (degrees)
POSES = {
    "stand": dict(lean=0, head=0, ab=(8, 6), af=(-8, -6), lb=(4, 0), lf=(-4, 0)),
    "slump": dict(lean=14, head=38, ab=(6, 4), af=(10, 6), lb=(4, 0), lf=(-4, 0)),
    "cheer": dict(lean=-4, head=-12, ab=(-160, -10), af=(160, 10), lb=(10, 0), lf=(-10, 0)),
    "point": dict(lean=0, head=-4, ab=(8, 6), af=(-95, 0), lb=(4, 0), lf=(-4, 0)),
    "shrug": dict(lean=0, head=8, ab=(55, -110), af=(-55, 110), lb=(4, 0), lf=(-4, 0)),
    "think": dict(lean=4, head=10, ab=(10, 8), af=(-30, -150), lb=(4, 0), lf=(-4, 0)),
    "push": dict(lean=-34, head=-10, ab=(-80, -10), af=(-95, -10), lb=(30, 10), lf=(-25, 30)),
    "carry": dict(lean=6, head=4, ab=(-60, -70), af=(-60, -70), lb=(4, 0), lf=(-4, 0)),
    "phone": dict(lean=10, head=30, ab=(10, 8), af=(-40, -120), lb=(4, 0), lf=(-4, 0)),
    "cry": dict(lean=18, head=40, ab=(-40, -140), af=(-50, -130), lb=(4, 0), lf=(-4, 0)),
    "hold": dict(lean=0, head=-14, ab=(-170, 0), af=(170, 0), lb=(6, 0), lf=(-6, 0)),
    "bet": dict(lean=-18, head=10, ab=(10, 8), af=(-70, -20), lb=(8, 0), lf=(-8, 0)),
    "wave": dict(lean=0, head=0, ab=(8, 6), af=(-150, -30), lb=(4, 0), lf=(-4, 0)),
    "kneel": dict(lean=10, head=30, ab=(20, 10), af=(10, 20), lb=(90, -90), lf=(-80, 80)),
    "sit": dict(lean=4, head=20, ab=(-40, -60), af=(-40, -60), lb=(-80, 80), lf=(-85, 85)),
    "climb": dict(lean=-8, head=-20, ab=(-150, -10), af=(-170, -20), lb=(-60, 60), lf=(10, 10)),
    "flip": dict(lean=0, head=-25, ab=(8, 6), af=(-60, -110), lb=(4, 0), lf=(-4, 0)),
    "fall": dict(lean=0, head=0, ab=(-120, 20), af=(120, -20), lb=(30, 0), lf=(-30, 0)),
}


def _limb(start, a1, a2, l1, l2, facing):
    r1, r2 = math.radians(a1), math.radians(a1 + a2)
    j = (start[0] - facing * math.sin(r1) * l1, start[1] + math.cos(r1) * l1)
    e = (j[0] - facing * math.sin(r2) * l2, j[1] + math.cos(r2) * l2)
    return j, e


def stickman(a, x, feet, h, c, pose="stand", t=0.0, facing=1, face="neutral", hold=None, rot=0.0, tremble=0.0):
    """Draw a stick figure; returns dict of joint positions (head, hands) so props can attach."""
    ps = dict(POSES.get(pose, POSES["stand"]))
    ph = t * (9 if pose == "run" else 6)
    if pose in ("walk", "run"):
        amp = 38 if pose == "run" else 26
        s = math.sin(ph)
        ps = dict(lean=-10 if pose == "run" else -2, head=-4, ab=(-s * amp, -20 if pose == "run" else -8),
                  af=(s * amp, -20 if pose == "run" else -8), lb=(s * amp, max(0, -s) * 50),
                  lf=(-s * amp, max(0, s) * 50))
    if pose == "flip":   # thumb flick loop
        ps["af"] = (-60 - 20 * math.sin(t * 6), -110)
    if pose == "cheer":
        ps["ab"] = (-160 + 10 * math.sin(t * 8), -10); ps["af"] = (160 - 10 * math.sin(t * 8), 10)
    lw = max(4, h * 0.062)
    torso, head_r = h * 0.32, h * 0.1
    thigh, shin, up, fore = h * 0.24, h * 0.24, h * 0.18, h * 0.17
    jx = tremble * math.sin(t * 40)
    if pose == "sit":
        hip = (x + jx, feet - shin - 6)
    elif pose == "kneel":
        hip = (x + jx, feet - shin * 0.95)
    else:
        hip = (x + jx, feet - thigh - shin)
    lean = math.radians(ps["lean"])
    neck = (hip[0] + facing * math.sin(lean) * torso, hip[1] - math.cos(lean) * torso)
    hl = math.radians(ps["lean"] + ps["head"])
    head = (neck[0] + facing * math.sin(hl) * head_r * 1.15, neck[1] - math.cos(hl) * head_r * 1.15)

    def R(pt):  # whole-figure rotation (falls) around the feet
        if not rot:
            return pt
        cx, cy = x, feet
        rr = math.radians(rot) * facing
        dx, dy = pt[0] - cx, pt[1] - cy
        return (cx + dx * math.cos(rr) - dy * math.sin(rr), cy + dx * math.sin(rr) + dy * math.cos(rr))

    back = tuple(max(0, v - 45) for v in c)
    kb, fb = _limb(hip, ps["lb"][0], ps["lb"][1], thigh, shin, facing)
    kf, ff = _limb(hip, ps["lf"][0], ps["lf"][1], thigh, shin, facing)
    eb, hb = _limb(neck, ps["ab"][0], ps["ab"][1], up, fore, facing)
    ef, hf = _limb(neck, ps["af"][0], ps["af"][1], up, fore, facing)
    a.line([R(hip), R(kb), R(fb)], back, lw)
    a.line([R(neck), R(eb), R(hb)], back, lw)
    a.line([R(neck), R(hip)], c, lw * 1.15)
    a.line([R(hip), R(kf), R(ff)], c, lw)
    a.line([R(neck), R(ef), R(hf)], c, lw)
    hc = R(head)
    a.circle(hc[0], hc[1], head_r, c)
    # face (small, readable at phone size)
    ex = facing * head_r * 0.35
    eye = P["ink"]
    if face != "none":
        for k in (-1, 1):
            a.circle(hc[0] + ex + k * head_r * 0.28, hc[1] - head_r * 0.12, head_r * 0.11, eye)
        mx, my, mw = hc[0] + ex, hc[1] + head_r * 0.38, head_r * 0.42
        if face == "happy":
            a.d.arc([(mx - mw) * a.ss, (my - mw * 0.9) * a.ss, (mx + mw) * a.ss, (my + mw * 0.5) * a.ss], 20, 160,
                    fill=eye, width=int(head_r * 0.14 * a.ss))
        elif face in ("sad", "cry"):
            a.d.arc([(mx - mw) * a.ss, (my - mw * 0.1) * a.ss, (mx + mw) * a.ss, (my + mw * 1.1) * a.ss], 200, 340,
                    fill=eye, width=int(head_r * 0.14 * a.ss))
            if face == "cry":
                for k in (-1, 1):
                    yy = hc[1] + head_r * (0.1 + (t * 1.5 % 1) * 0.9)
                    a.circle(hc[0] + ex + k * head_r * 0.3, yy, head_r * 0.09, P["glow"])
        elif face == "shock":
            a.circle(mx, my, mw * 0.45, eye)
        elif face == "angry":
            a.line([(mx - mw, my), (mx + mw, my)], eye, head_r * 0.14)
            for k in (-1, 1):
                a.line([(hc[0] + ex + k * head_r * 0.45, hc[1] - head_r * 0.42), (hc[0] + ex + k * head_r * 0.12, hc[1] - head_r * 0.3)], eye, head_r * 0.12)
        else:
            a.line([(mx - mw * 0.7, my), (mx + mw * 0.7, my)], eye, head_r * 0.12)
    out = {"head": hc, "hand": R(hf), "hand2": R(hb), "hip": R(hip)}
    if hold:
        hx, hy = out["hand"] if pose not in ("hold", "carry") else ((R(hf)[0] + R(hb)[0]) / 2, min(R(hf)[1], R(hb)[1]))
        prop(a, hold, hx, hy - h * 0.06, h * 0.28, None, t)
    return out


# ================================================================ props
def prop(a, k, x, y, s, c=None, t=0.0):
    """Flat icons. (x, y) = centre, s = size."""
    if k in ("car", "house", "plane", "ring", "bag", "phone", "heart", "coin"):
        G.icon(a, k, x, y, s, c or (P["gold"] if k == "coin" else P["bone"]))
        return
    c = c or P["bone"]
    ink = P["ink"]
    if k == "cash":
        for i in range(3):
            yy = y - i * s * 0.12
            a.rect([x - s * 0.5, yy - s * 0.18, x + s * 0.5, yy + s * 0.18], fill=(98, 170, 110), r=s * 0.04,
                   outline=(50, 100, 60), width=s * 0.03)
        a.circle(x, y - s * 0.24, s * 0.1, (60, 120, 70))
    elif k == "card":
        a.rect([x - s * 0.32, y - s * 0.45, x + s * 0.32, y + s * 0.45], fill=(240, 236, 226), r=s * 0.06,
               outline=(120, 110, 100), width=s * 0.025)
        G.icon(a, "heart", x, y, s * 0.42, P["red"])
    elif k == "chips":
        for i, cc in enumerate([P["red"], (60, 90, 170), P["gold"], P["green"]]):
            a.ellipse([x - s * 0.4, y - i * s * 0.14 - s * 0.1, x + s * 0.4, y - i * s * 0.14 + s * 0.1], fill=cc,
                      outline=(240, 240, 240), width=s * 0.03)
    elif k == "door":
        a.rect([x - s * 0.3, y - s * 0.6, x + s * 0.3, y + s * 0.6], fill=(110, 84, 58), r=s * 0.03)
        a.circle(x + s * 0.2, y, s * 0.05, P["gold"])
    elif k == "die":
        a.rect([x - s * 0.4, y - s * 0.4, x + s * 0.4, y + s * 0.4], fill=(240, 236, 226), r=s * 0.1)
        for dx, dy in ((-0.2, -0.2), (0, 0), (0.2, 0.2)):
            a.circle(x + dx * s, y + dy * s, s * 0.07, ink)
    elif k == "clock":
        a.circle(x, y, s * 0.5, (230, 226, 214)); a.circle(x, y, s * 0.42, None, outline=ink, width=s * 0.05)
        a.line([(x, y), (x + math.sin(t * 4) * s * 0.33, y - math.cos(t * 4) * s * 0.33)], P["red"], s * 0.05)
        a.line([(x, y), (x + math.sin(t / 3) * s * 0.22, y - math.cos(t / 3) * s * 0.22)], ink, s * 0.07)
    elif k == "calendar":
        a.rect([x - s * 0.45, y - s * 0.4, x + s * 0.45, y + s * 0.45], fill=(236, 232, 222), r=s * 0.05)
        a.rect([x - s * 0.45, y - s * 0.4, x + s * 0.45, y - s * 0.18], fill=P["red"], r=s * 0.05)
        for i in range(3):
            for j in range(4):
                a.rect([x - s * 0.36 + j * s * 0.2, y - s * 0.08 + i * s * 0.16, x - s * 0.26 + j * s * 0.2,
                        y + s * 0.02 + i * s * 0.16], fill=(170, 166, 156))
    elif k == "briefcase":
        a.rect([x - s * 0.45, y - s * 0.25, x + s * 0.45, y + s * 0.3], fill=(90, 60, 40), r=s * 0.06)
        a.rect([x - s * 0.15, y - s * 0.38, x + s * 0.15, y - s * 0.25], fill=None, r=s * 0.04, outline=(90, 60, 40), width=s * 0.05)
    elif k == "bill":
        a.rect([x - s * 0.32, y - s * 0.45, x + s * 0.32, y + s * 0.45], fill=(236, 232, 222), r=s * 0.03)
        for i in range(5):
            a.line([(x - s * 0.22, y - s * 0.3 + i * s * 0.13), (x + s * (0.22 if i < 4 else 0.0), y - s * 0.3 + i * s * 0.13)], (150, 146, 136), s * 0.03)
        a.circle(x + s * 0.14, y + s * 0.3, s * 0.08, P["red"])
    elif k == "piggy":
        a.ellipse([x - s * 0.45, y - s * 0.3, x + s * 0.45, y + s * 0.3], fill=(230, 140, 160))
        a.circle(x + s * 0.4, y - s * 0.02, s * 0.12, (240, 160, 176))
        a.rect([x - s * 0.08, y - s * 0.32, x + s * 0.08, y - s * 0.26], fill=ink)
        for dx in (-0.25, 0.2):
            a.rect([x + dx * s, y + s * 0.2, x + dx * s + s * 0.1, y + s * 0.42], fill=(230, 140, 160))
    elif k == "cage":
        a.rect([x - s * 0.5, y - s * 0.6, x + s * 0.5, y + s * 0.5], fill=None, outline=c, width=s * 0.04, r=s * 0.06)
        for i in range(1, 6):
            xx = x - s * 0.5 + i * s / 6
            a.line([(xx, y - s * 0.6), (xx, y + s * 0.5)], c, s * 0.03)
    elif k == "ladder":
        a.line([(x - s * 0.2, y + s * 0.6), (x - s * 0.2, y - s * 0.6)], (150, 110, 70), s * 0.05)
        a.line([(x + s * 0.2, y + s * 0.6), (x + s * 0.2, y - s * 0.6)], (150, 110, 70), s * 0.05)
        for i in range(7):
            yy = y + s * 0.5 - i * s * 0.17
            a.line([(x - s * 0.2, yy), (x + s * 0.2, yy)], (150, 110, 70), s * 0.04)
    elif k == "trophy":
        a.poly([(x - s * 0.3, y - s * 0.4), (x + s * 0.3, y - s * 0.4), (x + s * 0.18, y), (x - s * 0.18, y)], P["gold"])
        a.rect([x - s * 0.06, y, x + s * 0.06, y + s * 0.25], fill=P["gold"]); a.rect([x - s * 0.22, y + s * 0.25, x + s * 0.22, y + s * 0.34], fill=P["gold"])
    elif k == "bulb":
        for i, al in enumerate((40, 70, 110)):
            a.circle(x, y - s * 0.1, s * (0.55 - i * 0.1), mix(P["bg0"], P["warm"], al / 160))
        a.circle(x, y - s * 0.1, s * 0.3, P["warm"]); a.rect([x - s * 0.12, y + s * 0.18, x + s * 0.12, y + s * 0.35], fill=(150, 150, 160))
    elif k == "brain":
        for dx, dy in ((-0.15, -0.1), (0.15, -0.1), (-0.2, 0.1), (0.2, 0.1), (0, 0)):
            a.circle(x + dx * s, y + dy * s, s * 0.22, (230, 150, 170))
    elif k == "laptop":
        a.rect([x - s * 0.45, y - s * 0.35, x + s * 0.45, y + s * 0.15], fill=(40, 44, 56), r=s * 0.04)
        a.rect([x - s * 0.4, y - s * 0.3, x + s * 0.4, y + s * 0.1], fill=(90, 130, 190))
        a.rect([x - s * 0.55, y + s * 0.15, x + s * 0.55, y + s * 0.22], fill=(70, 74, 86), r=s * 0.03)
    elif k == "news":
        a.rect([x - s * 0.45, y - s * 0.4, x + s * 0.45, y + s * 0.4], fill=(226, 222, 210), r=s * 0.02)
        a.rect([x - s * 0.38, y - s * 0.32, x + s * 0.38, y - s * 0.15], fill=(60, 60, 64))
        for i in range(4):
            a.line([(x - s * 0.38, y - s * 0.05 + i * s * 0.1), (x + s * 0.38, y - s * 0.05 + i * s * 0.1)], (150, 146, 136), s * 0.03)
    elif k == "ticket":
        a.rect([x - s * 0.5, y - s * 0.25, x + s * 0.5, y + s * 0.25], fill=(240, 200, 90), r=s * 0.05)
        for i in range(6):
            a.circle(x - s * 0.35 + i * s * 0.14, y, s * 0.05, (200, 60, 60))
    elif k == "mug":
        a.rect([x - s * 0.28, y - s * 0.3, x + s * 0.22, y + s * 0.3], fill=(220, 216, 206), r=s * 0.05)
        a.circle(x + s * 0.3, y, s * 0.13, None, outline=(220, 216, 206), width=s * 0.06)
    elif k == "box":
        a.rect([x - s * 0.4, y - s * 0.32, x + s * 0.4, y + s * 0.32], fill=(170, 130, 86), r=s * 0.03)
        a.line([(x - s * 0.4, y - s * 0.12), (x + s * 0.4, y - s * 0.12)], (130, 96, 60), s * 0.04)
    elif k == "boulder":
        a.ellipse([x - s * 0.55, y - s * 0.45, x + s * 0.55, y + s * 0.45], fill=(90, 86, 82))
        a.ellipse([x - s * 0.3, y - s * 0.3, x + s * 0.05, y - s * 0.1], fill=(110, 106, 100))
    elif k == "flame":
        for i, cc in enumerate([(230, 80, 40), (250, 150, 50), (255, 220, 120)]):
            r = s * (0.4 - i * 0.11)
            fl = 1 + 0.08 * math.sin(t * 12 + i)
            a.poly([(x - r, y), (x, y - r * 2.2 * fl), (x + r, y)], cc); a.circle(x, y, r, cc)
    elif k == "fish":
        a.ellipse([x - s * 0.4, y - s * 0.18, x + s * 0.3, y + s * 0.18], fill=(120, 170, 200))
        a.poly([(x + s * 0.25, y), (x + s * 0.5, y - s * 0.2), (x + s * 0.5, y + s * 0.2)], (120, 170, 200))
    elif k == "boat":
        a.poly([(x - s * 0.5, y), (x + s * 0.5, y), (x + s * 0.35, y + s * 0.22), (x - s * 0.35, y + s * 0.22)], (140, 80, 50))
        a.line([(x, y), (x, y - s * 0.6)], (90, 70, 50), s * 0.04)
        a.poly([(x + s * 0.02, y - s * 0.58), (x + s * 0.4, y - s * 0.1), (x + s * 0.02, y - s * 0.1)], (230, 226, 214))
    elif k == "cake":
        a.rect([x - s * 0.45, y - s * 0.15, x + s * 0.45, y + s * 0.3], fill=(230, 180, 190), r=s * 0.05)
        for i in range(5):
            xx = x - s * 0.32 + i * s * 0.16
            a.rect([xx - s * 0.02, y - s * 0.38, xx + s * 0.02, y - s * 0.15], fill=(240, 240, 240))
            a.circle(xx, y - s * 0.42, s * 0.04, P["warm"])
    elif k == "lock":
        a.rect([x - s * 0.32, y - s * 0.05, x + s * 0.32, y + s * 0.42], fill=P["gold"], r=s * 0.05)
        a.d.arc([(x - s * 0.22) * a.ss, (y - s * 0.38) * a.ss, (x + s * 0.22) * a.ss, (y + s * 0.06) * a.ss], 180, 360,
                fill=P["gold"], width=int(s * 0.08 * a.ss))
    elif k == "hourglass":
        a.poly([(x - s * 0.3, y - s * 0.45), (x + s * 0.3, y - s * 0.45), (x, y)], (230, 210, 160))
        a.poly([(x - s * 0.3, y + s * 0.45), (x + s * 0.3, y + s * 0.45), (x, y)], (230, 210, 160))
        a.rect([x - s * 0.36, y - s * 0.5, x + s * 0.36, y - s * 0.44], fill=(120, 90, 60))
        a.rect([x - s * 0.36, y + s * 0.44, x + s * 0.36, y + s * 0.5], fill=(120, 90, 60))
    elif k == "crown":
        a.poly([(x - s * 0.4, y + s * 0.2), (x - s * 0.4, y - s * 0.2), (x - s * 0.2, y), (x, y - s * 0.3), (x + s * 0.2, y),
                (x + s * 0.4, y - s * 0.2), (x + s * 0.4, y + s * 0.2)], P["gold"])
    elif k == "megaphone":
        a.poly([(x - s * 0.3, y - s * 0.1), (x + s * 0.3, y - s * 0.35), (x + s * 0.3, y + s * 0.35), (x - s * 0.3, y + s * 0.1)], (220, 90, 60))
    elif k == "magnifier":
        a.circle(x - s * 0.08, y - s * 0.08, s * 0.28, None, outline=c, width=s * 0.07)
        a.line([(x + s * 0.12, y + s * 0.12), (x + s * 0.4, y + s * 0.4)], c, s * 0.09)
    elif k == "scale":
        a.line([(x, y - s * 0.4), (x, y + s * 0.4)], c, s * 0.05)
        a.line([(x - s * 0.45, y - s * 0.3), (x + s * 0.45, y - s * 0.3)], c, s * 0.05)
        for dx in (-0.45, 0.45):
            a.ellipse([x + dx * s - s * 0.18, y - s * 0.05, x + dx * s + s * 0.18, y + s * 0.05], fill=c)
    elif k == "arrowup":
        a.poly([(x, y - s * 0.5), (x + s * 0.35, y - s * 0.1), (x - s * 0.35, y - s * 0.1)], P["green"])
        a.rect([x - s * 0.12, y - s * 0.1, x + s * 0.12, y + s * 0.5], fill=P["green"])
    elif k == "arrowdown":
        a.poly([(x, y + s * 0.5), (x + s * 0.35, y + s * 0.1), (x - s * 0.35, y + s * 0.1)], P["red"])
        a.rect([x - s * 0.12, y - s * 0.5, x + s * 0.12, y + s * 0.1], fill=P["red"])
    elif k == "flag":
        a.line([(x - s * 0.3, y + s * 0.5), (x - s * 0.3, y - s * 0.5)], (180, 180, 186), s * 0.05)
        a.poly([(x - s * 0.3, y - s * 0.5), (x + s * 0.35, y - s * 0.32), (x - s * 0.3, y - s * 0.12)], P["red"])
    elif k == "shield":
        a.poly([(x - s * 0.35, y - s * 0.4), (x + s * 0.35, y - s * 0.4), (x + s * 0.3, y + s * 0.1), (x, y + s * 0.45),
                (x - s * 0.3, y + s * 0.1)], (90, 140, 220))
    elif k == "ship":
        a.poly([(x - s * 0.55, y), (x + s * 0.55, y), (x + s * 0.4, y + s * 0.25), (x - s * 0.4, y + s * 0.25)], (80, 70, 64))
        a.rect([x - s * 0.25, y - s * 0.25, x + s * 0.2, y], fill=(110, 100, 90))
    elif k == "gavel":
        a.rect([x - s * 0.35, y - s * 0.3, x + s * 0.05, y - s * 0.1], fill=(120, 80, 50), r=s * 0.04)
        a.line([(x - s * 0.15, y - s * 0.1), (x + s * 0.3, y + s * 0.35)], (120, 80, 50), s * 0.07)
    elif k == "fork":
        a.line([(x, y + s * 0.5), (x, y)], c, s * 0.06)
        a.line([(x, y), (x - s * 0.35, y - s * 0.45)], c, s * 0.06); a.line([(x, y), (x + s * 0.35, y - s * 0.45)], c, s * 0.06)
    elif k == "cliff":
        a.poly([(x - s, y + s * 0.6), (x - s, y - s * 0.2), (x + s * 0.1, y - s * 0.2), (x + s * 0.25, y + s * 0.6)], (52, 50, 56))
    elif k == "pot":
        a.ellipse([x - s * 0.5, y - s * 0.25, x + s * 0.5, y + s * 0.35], fill=(60, 60, 66))
        for i in range(6):
            G.icon(a, "coin", x - s * 0.3 + i * s * 0.12, y - s * 0.22 - (i % 2) * s * 0.06, s * 0.2, P["gold"])
    elif k == "eye":
        a.ellipse([x - s * 0.45, y - s * 0.22, x + s * 0.45, y + s * 0.22], fill=(236, 232, 222))
        a.circle(x, y, s * 0.16, (60, 90, 150)); a.circle(x, y, s * 0.07, ink)
    elif k == "spotlight":
        a.poly([(x - s * 0.2, 0), (x + s * 0.2, 0), (x + s * 0.7, GROUND + 10), (x - s * 0.7, GROUND + 10)], (52, 48, 40))
    else:  # unknown → a labelled box
        a.rect([x - s * 0.4, y - s * 0.3, x + s * 0.4, y + s * 0.3], fill=(80, 80, 90), r=s * 0.06)


PROPS = ["car", "house", "plane", "ring", "bag", "phone", "heart", "coin", "cash", "card", "chips", "door", "die",
         "clock", "calendar", "briefcase", "bill", "piggy", "cage", "ladder", "trophy", "bulb", "brain", "laptop",
         "news", "ticket", "mug", "box", "boulder", "flame", "fish", "boat", "cake", "lock", "hourglass", "crown",
         "megaphone", "magnifier", "scale", "arrowup", "arrowdown", "flag", "shield", "ship", "gavel", "fork", "cliff",
         "pot", "eye", "spotlight"]


# ================================================================ text overlays inside the art
def bubble(a, x, y, text, kind="say", alpha=1.0, size=34):
    f = font("sans-black", int(size * a.ss))
    tw = a.d.textlength(text, font=f) / a.ss
    w, h = tw + 44, size * 1.7
    fill = (240, 236, 226) if kind != "alarm" else P["red"]
    tc = P["ink"] if kind != "alarm" else (255, 255, 255)
    if kind == "think":
        a.ellipse([x - w / 2 - 10, y - h / 2 - 8, x + w / 2 + 10, y + h / 2 + 8], fill=fill)
        a.circle(x - w / 4, y + h / 2 + 22, 10, fill); a.circle(x - w / 4 - 16, y + h / 2 + 42, 6, fill)
    else:
        a.rect([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=fill, r=h / 2.6)
        a.poly([(x - 18, y + h / 2 - 2), (x + 6, y + h / 2 - 2), (x - 26, y + h / 2 + 26)], fill)
    a.d.text(((x - tw / 2) * a.ss, (y - size * 0.62) * a.ss), text, font=f, fill=tc)


def label(a, x, y, text, c, size=40):
    f = font("sans-black", int(size * a.ss))
    tw = a.d.textlength(text, font=f) / a.ss
    a.d.text(((x - tw / 2) * a.ss, (y - size * 0.6) * a.ss), text, font=f, fill=c)


def arrow(a, p0, p1, c, k=1.0, w=8):
    x = p0[0] + (p1[0] - p0[0]) * k; y = p0[1] + (p1[1] - p0[1]) * k
    a.line([tuple(p0), (x, y)], c, w)
    if k > 0.6:
        ang = math.atan2(y - p0[1], x - p0[0])
        hl = w * 3
        a.poly([(x, y), (x - hl * math.cos(ang - 0.45), y - hl * math.sin(ang - 0.45)),
                (x - hl * math.cos(ang + 0.45), y - hl * math.sin(ang + 0.45))], c)


# ================================================================ scene renderer
def render(spec, w, h, t, p):
    """RGBA image (w x h) of a stickman scene at time t (s) / progress p (0..1)."""
    a = G.Art(w, h)
    acc = col(spec.get("accent"), "red")
    SETS.get(spec.get("set", "void"), _set_void)(a, t, acc)
    if spec.get("ground", True):
        a.rect([0, GROUND + 4, w, GROUND + 12], fill=(40, 40, 50))
    for it in spec.get("items", []):
        at = it.get("at", 0.0)
        if p < at:
            continue
        k_in = ease(seg(p, at, at + 0.12))
        typ = it["t"]
        if typ == "glow":
            a.glow(it["x"], it["y"], it.get("r", 200), col(it.get("col"), "warm"), int(it.get("alpha", 90) * k_in))
        elif typ == "man":
            x = it["x"]
            if it.get("move"):
                x1, p0, p1 = it["move"]
                x = it["x"] + (x1 - it["x"]) * ease(seg(p, p0, p1))
            moving = it.get("move") and seg(p, it["move"][1], it["move"][2]) not in (0.0, 1.0)
            pose = it.get("pose", "walk" if moving else "stand")
            if it.get("move") and not moving and pose in ("walk", "run"):
                pose = it.get("end_pose", "stand")
            rot = 0.0
            if it.get("fall"):
                rot = 88 * ease(seg(p, it["fall"][0], it["fall"][1]))
            hh = it.get("h", 300) * (1 + (it.get("grow", 0) * ease(seg(p, at, 1.0))))
            feet = it.get("y", GROUND + 8)
            if it.get("jump"):
                feet -= abs(math.sin(t * 5)) * 30
            c = col(it.get("col"), "bone")
            if it.get("dim"):
                c = mix(c, (40, 40, 48), it["dim"])
            stickman(a, x, feet, hh, c, pose, t + it.get("phase", 0), it.get("facing", 1), it.get("face", "neutral"),
                     it.get("hold"), rot, it.get("tremble", 0.0))
            if it.get("tag"):
                label(a, x, feet + 34 if feet < GROUND - 40 else GROUND + 40, it["tag"], c, 28)
        elif typ == "prop":
            n, motion = it.get("n", 1), it.get("motion")
            s = it.get("s", 120)
            c = col(it.get("col"), None) if it.get("col") else None
            for i in range(n):
                x, y = it["x"] + i * it.get("dx", 0), it["y"] + i * it.get("dy", 0)
                ss = s * (k_in if motion in (None, "pop") else 1)
                if motion == "rain":
                    ph = (t * it.get("speed", 0.6) + i / n) % 1
                    x = it["x"] + ((i * 137) % it.get("spread", 900)) - it.get("spread", 900) / 2
                    y = -40 + ph * (GROUND + 40)
                elif motion == "fall":
                    y = -60 + (it["y"] + 60) * ease(seg(p, at + i * 0.05, at + 0.25 + i * 0.05))
                elif motion == "fly":
                    tx, ty = it["to"]
                    kk = ease(seg(p, at + i * 0.06, at + 0.35 + i * 0.06))
                    x, y = x + (tx - x) * kk, y + (ty - y) * kk - math.sin(kk * math.pi) * 80
                elif motion == "pile":
                    if i >= int(n * ease(seg(p, at, it.get("until", 0.9)))) + 1:
                        continue
                elif motion == "shrink":
                    ss = s * (1 - 0.85 * ease(seg(p, at, it.get("until", 0.9))))
                elif motion == "float":
                    y = y - 260 * ease(seg(p, at + i * 0.04, 1.0))
                    ss = s * (1 - 0.6 * ease(seg(p, at + i * 0.04, 1.0)))
                elif motion == "spin":
                    x = x + math.cos(t * 3 + i) * it.get("r", 60); y = y + math.sin(t * 3 + i) * it.get("r", 60) * 0.4
                elif motion == "pulse":
                    ss = s * (1 + 0.08 * math.sin(t * 6))
                elif motion == "shake":
                    x += 6 * math.sin(t * 30 + i)
                elif motion == "drain":
                    if i >= max(0, int(n * (1 - ease(seg(p, at, it.get("until", 0.9)))))):
                        continue
                if ss > 2:
                    prop(a, it["k"], x, y, ss, c, t)
                if motion == "burn" and p > at:
                    prop(a, "flame", x, y + s * 0.2, s * 0.6 * k_in, None, t + i)
        elif typ == "bubble":
            bubble(a, it["x"], it["y"], it["text"], it.get("kind", "say"), k_in, it.get("size", 34))
        elif typ == "label":
            label(a, it["x"], it["y"], it["text"], col(it.get("col"), "bone"), it.get("size", 40))
        elif typ == "arrow":
            arrow(a, it["from"], it["to"], col(it.get("col"), "red"), k_in, it.get("w", 8))
        elif typ == "line":
            a.line([tuple(q) for q in it["pts"]], col(it.get("col"), "muted"), it.get("w", 6))
        elif typ == "crowd":   # row of small grey stickmen; k of them highlighted
            n, hi = it.get("n", 12), it.get("hi", [])
            for i in range(n):
                x = it.get("x0", 80) + i * it.get("gap", 80)
                c = col(it.get("hicol"), "red") if i in hi else col("crowd")
                stickman(a, x, it.get("y", GROUND + 8), it.get("h", 150), c, it.get("pose", "stand"), t + i * 0.3,
                         1, "none" if i not in hi else it.get("face", "neutral"))
    return a.image()


if __name__ == "__main__":   # python stickman.py → contact sheet of poses and props in the scratch dir
    import sys
    from PIL import Image

    out = sys.argv[1] if len(sys.argv) > 1 else "stickman_sheet.png"
    poses = list(POSES) + ["walk", "run"]
    items = [{"t": "man", "x": 70 + i * 95, "pose": ps, "h": 200, "face": ["happy", "sad", "shock", "angry", "cry"][i % 5],
              "col": "bone"} for i, ps in enumerate(poses[:11])]
    sheet = Image.new("RGB", (W, H * 3), (14, 14, 19))
    sheet.paste(render({"set": "void", "items": items}, W, H, 0.4, 1.0), (0, 0))
    items = [{"t": "man", "x": 70 + i * 100, "pose": ps, "h": 200, "col": "red"} for i, ps in enumerate(poses[11:])]
    sheet.paste(render({"set": "city", "items": items}, W, H, 0.4, 1.0), (0, H))
    pr = [{"t": "prop", "k": k, "x": 60 + (i % 10) * 105, "y": 80 + (i // 10) * 120, "s": 90} for i, k in enumerate(PROPS)]
    sheet.paste(render({"set": "void", "ground": False, "items": pr}, W, H, 0.4, 1.0), (0, H * 2))
    sheet.save(out)
    print(out)
