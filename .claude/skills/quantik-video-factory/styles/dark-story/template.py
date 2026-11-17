"""dark-story: faceless "dark truth" social story — animated flat people and objects, heavy dark grade, no charts/code.

Episode field `scenes`: [{"kind": <illustration>, "say": narration, "show": big on-screen line}] ; kinds in ART.
The only numbers are in the `crowd` scene (a grid of n people where only k escape), taken from the model run.
"""
import math

import numpy as np
from PIL import Image, ImageDraw

import darkart as G
import frames as F
from core import SAFE, L, font
from render import Scene

KIND = "video"
DEFAULTS = {"max_seconds": 60}
MUSIC = "drone"   # synthesised dark bed (pipeline/assemble.py), ducked under the voice
P = G.P
W, H = 1080, 1920
ART_BOX = (0, 600, 1080, 1310)          # illustration band (full bleed; no text inside it)
AW, AH = ART_BOX[2] - ART_BOX[0], ART_BOX[3] - ART_BOX[1]
TEXT_BOX = (SAFE["left"], 300, SAFE["right"], 580)
GROUND = AH - 70


# ================================================================ illustrations: draw(a: Art, t, p, ctx)
def art_office(a, t, p, c):
    # city window behind, lone worker at a desk late at night, clock hands spinning (days blur together)
    a.rect([90, 20, 990, 300], fill=(18, 20, 28), r=8)
    rng = np.random.default_rng(3)
    x = 100
    while x < 980:
        bw = int(rng.integers(50, 110)); bh = int(rng.integers(90, 250))
        a.rect([x, 300 - bh, x + bw - 8, 300], fill=(26, 28, 38))
        for wy in range(300 - bh + 14, 290, 26):
            for wx in range(x + 8, x + bw - 18, 20):
                if rng.random() < 0.18:
                    a.rect([wx, wy, wx + 8, wy + 12], fill=(70, 66, 50))
        x += bw
    for k in range(0, 901, 300):
        a.line([(90 + k, 20), (90 + k, 300)], P["ink"], 10)
    cx, cy, r = 870, 110, 58
    a.circle(cx, cy, r, P["ink"], outline=P["muted"], width=5)
    ang = t * 5.0
    a.line([(cx, cy), (cx + math.sin(ang) * r * 0.8, cy - math.cos(ang) * r * 0.8)], P["bone"], 5)
    a.line([(cx, cy), (cx + math.sin(ang / 12) * r * 0.5, cy - math.cos(ang / 12) * r * 0.5)], P["red"], 7)
    a.glow(560, 380, 220, P["glow"], 90)
    G.person(a, 660, GROUND + 10, 450, (70, 80, 100), head_down=0.6, facing=-1)
    a.rect([250, 340, 470, 455], fill=(150, 190, 240), r=10)
    a.rect([345, 455, 375, 482], fill=P["crowd_dk"])
    a.rect([150, 480, 930, 506], fill=P["crowd_dk"], r=6)
    a.rect([200, 506, 230, GROUND + 10], fill=P["crowd_dk"]); a.rect([850, 506, 880, GROUND + 10], fill=P["crowd_dk"])


def art_commute(a, t, p, c):
    # identical heads-down commuters on a loop; one of them is you (red scarf of colour)
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    for k in range(-1, 6):  # train windows passing behind
        x = (k * 260 - t * 120) % (AW + 260) - 130
        a.rect([x, 110, x + 220, 300], fill=(22, 25, 33), r=14, outline=(40, 44, 56), width=4)
    n, gap = 7, 170
    for i in range(n):
        x = (i * gap + t * 60) % (n * gap) - 90
        G.person(a, x, GROUND, 330, P["crowd"], phase=t * 6 + i * 0.9, head_down=0.6)
    G.person(a, 540, GROUND, 350, P["red"], phase=t * 6, head_down=0.6)


def art_scroll(a, t, p, c):
    # a phone feed scrolling with other people's wins; your silhouette from behind, lit by the screen
    px0, py0, px1, py1 = 320, 10, 760, 600
    a.glow(540, 300, 330, P["glow"], 60)
    a.rect([px0, py0, px1, py1], fill=(12, 12, 16), r=46, outline=(60, 62, 70), width=6)
    a.rect([px0 + 22, py0 + 40, px1 - 22, py1 - 40], fill=(28, 30, 38), r=20)
    kinds = ["car", "house", "plane", "ring", "bag", "car", "house", "plane"]
    off = (t * 260) % 230
    for i, k in enumerate(kinds):
        y = py0 + 60 + i * 230 - off
        if y < py0 + 30 or y > py1 - 200:
            continue
        a.rect([px0 + 40, y, px1 - 40, y + 200], fill=(46, 48, 60), r=16)
        G.icon(a, k, 540, y + 95, 130, P["gold"])
        G.icon(a, "heart", px1 - 80, y + 170, 34, P["red"])
    # back of a head + shoulders
    a.rect([220, 640, 860, AH + 80], fill=P["ink"], r=150)
    a.circle(540, 600, 105, P["ink"])
    a.glow(540, 520, 110, P["glow"], 30)


def art_compare(a, t, p, c):
    # three glowing "posts": other people posing with status objects; below, a small grey-red you
    items = [("car", 190), ("house", 540), ("plane", 890)]
    for i, (k, x) in enumerate(items):
        e = F.ease_out(F.seg(p, i * 0.18, i * 0.18 + 0.3))
        if e <= 0:
            continue
        y0 = 20 + (1 - e) * 50
        a.glow(x, y0 + 200, 190, P["gold"], int(60 * e))
        a.rect([x - 150, y0, x + 150, y0 + 400], fill=(int(40 * e), int(36 * e), int(30 * e)), r=22,
               outline=tuple(int(v * e) for v in P["gold"]), width=4)
        G.icon(a, k, x, y0 + 95, 120, tuple(int(v * e) for v in P["gold"]))
        G.person(a, x, y0 + 380, 230, tuple(int(v * e) for v in (120, 108, 84)), arms_up=True)
        G.icon(a, "heart", x + 110, y0 + 370, 30, tuple(int(v * e) for v in P["red"]))
    s = 1 - 0.4 * F.ease_in_out(F.seg(p, 0.2, 1.0))
    G.person(a, 540, GROUND + 50, 230 * s, P["red"], head_down=0.9)


def art_spend(a, t, p, c):
    # the paycheck arrives and drains straight into things that make you look fine
    a.rect([340, 20, 740, 170], fill=P["green"], r=14)
    a.rect([360, 40, 720, 150], fill=None, r=10, outline=(60, 120, 80), width=5)
    a.circle(540, 95, 40, (60, 120, 80)); a.line([(540, 70), (540, 120)], P["green"], 8)
    shelf = [("car", 170), ("house", 400), ("phone", 640), ("bag", 880)]
    grow = F.ease_out(F.seg(p, 0.1, 1.0))
    for i, (k, x) in enumerate(shelf):
        for j in range(4):  # falling coins
            ph = (t * 0.9 + j / 4 + i * 0.13) % 1
            cy = 180 + ph * 300
            cx = 540 + (x - 540) * ph
            G.icon(a, "coin", cx, cy, 34, P["gold"])
        sz = 110 + 70 * grow
        a.glow(x, 560, 110, P["gold"], int(40 + 40 * grow))
        G.icon(a, k, x, 560, sz, P["gold"])
    a.rect([60, GROUND - 4, AW - 60, GROUND + 8], fill=P["crowd_dk"])


def art_wheel(a, t, p, c):
    # running in a wheel; the bag of upgrades on your back keeps growing
    cx, cy, r = 540, 360, 330
    a.circle(cx, cy, r, None, outline=P["muted"], width=14)
    a.circle(cx, cy, r - 40, None, outline=(60, 60, 66), width=5)
    rot = t * 1.6
    for k in range(12):
        ang = rot + k * math.pi / 6
        a.line([(cx, cy), (cx + math.cos(ang) * (r - 6), cy + math.sin(ang) * (r - 6))], (52, 52, 58), 5)
    a.circle(cx, cy, 26, P["muted"])
    a.rect([cx - 30, cy, cx + 30, GROUND + 10], fill=P["crowd_dk"])
    a.rect([cx - 220, GROUND + 6, cx + 220, GROUND + 20], fill=P["crowd_dk"], r=6)
    G.person(a, cx, cy + r - 22, 300, P["red"], phase=t * 9, run=True, bag=F.ease_in_out(p), head_down=0.3)


def art_crowd(a, t, p, c):
    # n people (one per simulated career); only k light up and float away
    n, k = c["n"], c["k"]
    base = _crowd_plate(n, AW, AH)
    a.im.alpha_composite(base.resize(a.im.size))
    pos = _crowd_positions(n, AW, AH)
    rng = np.random.default_rng(11)
    pick = rng.choice(n, size=k, replace=False)
    lit = F.ease_out(F.seg(p, 0.25, 0.5)); rise = F.ease_in_out(F.seg(p, 0.5, 1.0))
    for j, i in enumerate(pick):
        x, y = pos[i]
        yy = y - rise * (120 + (j % 7) * 30)
        if lit > 0:
            a.glow(x, yy - 6, 20, P["warm"], int(110 * lit))
            col = tuple(int(P["crowd"][m] + (P["warm"][m] - P["crowd"][m]) * lit) for m in range(3))
            a.circle(x, yy - 9, 4.2, col); a.rect([x - 5.5, yy - 3, x + 5.5, yy + 7], fill=col, r=3)


def _crowd_positions(n, w, h):
    cols = int(math.sqrt(n * w / h) + 0.5); rows = math.ceil(n / cols)
    dx, dy = (w - 60) / cols, (h - 60) / rows
    return [(30 + dx * (i % cols) + dx / 2, 40 + dy * (i // cols) + dy / 2) for i in range(n)]


_PLATES = {}


def _crowd_plate(n, w, h):
    if n not in _PLATES:
        ss = 2
        im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        rng = np.random.default_rng(5)
        for x, y in _crowd_positions(n, w, h):
            shade = int(rng.integers(-10, 10))
            G.tiny_person(d, x * ss, y * ss, 11 * ss, tuple(max(0, v + shade) for v in P["crowd"]))
        _PLATES[n] = im
    return _PLATES[n]


def art_walkaway(a, t, p, c):
    # the crowd stays lit by their screens; you drop the phone and walk toward a door of light
    door = (900, 110, 1010, GROUND)
    a.glow(955, 380, 260, P["warm"], 110)
    a.rect(list(door), fill=P["warm"], r=6)
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    for i, x in enumerate((60, 190, 320)):
        G.person(a, x, GROUND, 300 + (i % 2) * 24, P["crowd"], phone=True, head_down=0.9, facing=1)
    G.icon(a, "phone", 520, GROUND - 14, 46, (90, 96, 110))
    e = F.ease_in_out(F.seg(p, 0.1, 1.0))
    G.person(a, 540 + e * 320, GROUND, 330 - e * 110, P["bone"], phase=t * 6)


def art_alone(a, t, p, c):
    # one person in a cone of light; the cracked phone at their feet
    a.poly([(470, 0), (610, 0), (800, GROUND + 10), (280, GROUND + 10)], (40, 38, 34))
    a.ellipse([300, GROUND - 20, 780, GROUND + 40], fill=(58, 54, 46))
    G.person(a, 540, GROUND + 10, 440, P["bone"])
    G.icon(a, "phone", 700, GROUND + 4, 60, (80, 84, 96))
    a.line([(690, GROUND - 14), (706, GROUND + 2), (696, GROUND + 18)], P["bone"], 2.5)


# ---------------------------------------------------------------- three people, same salary (#2)
TRIO = [(200, P["red"]), (540, P["crowd"]), (880, P["bone"])]      # spender · middle · builder


def _paycheck(a, x, y, s, al=1.0):
    col = tuple(int(v * al) for v in P["green"])
    a.rect([x - s * 0.5, y - s * 0.28, x + s * 0.5, y + s * 0.28], fill=col, r=s * 0.06)
    a.circle(x, y, s * 0.13, tuple(int(v * al) for v in (60, 120, 80)))


def art_payday3(a, t, p, c):
    # three people side by side; the exact same paycheck drops into each pair of hands
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    for i, (x, col) in enumerate(TRIO):
        a.glow(x, 300, 170, P["glow"], 40)
        G.person(a, x, GROUND, 380, col, arms_up=False)
        e = F.ease_out(F.seg(p, 0.1 + i * 0.12, 0.45 + i * 0.12))
        _paycheck(a, x, 40 + e * 150, 140, 0.4 + 0.6 * e)


def art_split3(a, t, p, c):
    # time runs; spender's lane fills with things, middle grows a small pile, builder a tall quiet block
    v = c.get("v", {})
    mb = max(v.get("months_b", 48), 1)
    g = F.ease_in_out(F.seg(p, 0.05, 0.95))
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    for k in (360, 720):
        a.line([(k, 20), (k, GROUND)], (40, 42, 52), 4)
    # spender: status objects pop in, nothing stacks
    for j, (k, dx, dy) in enumerate([("phone", -80, 150), ("bag", 70, 230), ("car", 0, 360), ("ring", -90, 300),
                                    ("plane", 80, 90)]):
        e = F.ease_out(F.seg(g, j * 0.17, j * 0.17 + 0.2))
        if e > 0:
            a.glow(200 + dx, dy, 60, P["gold"], int(50 * e))
            G.icon(a, k, 200 + dx, dy, 90 * e, P["gold"])
    G.person(a, 200, GROUND, 250, P["red"], phone=True, head_down=0.7)
    # middle and builder: a pile of coins/blocks whose height follows the model's runway
    for x, key, col in ((540, "months_m", P["muted"]), (880, "months_b", P["warm"])):
        hgt = 470 * g * v.get(key, 0) / mb
        if hgt > 2:
            a.glow(x + 70, GROUND - hgt / 2, 90 + hgt / 4, col, 50)
            a.rect([x + 20, GROUND - hgt, x + 130, GROUND], fill=tuple(int(q * 0.75) for q in col), r=8)
            for yy in range(int(GROUND - hgt) + 24, GROUND, 36):
                a.line([(x + 26, yy), (x + 124, yy)], P["ink"], 3)
    G.person(a, 500, GROUND, 250, P["crowd"], head_down=0.3)
    G.person(a, 830, GROUND, 250, P["bone"], head_down=0.1)


def art_paycheck_stops(a, t, p, c):
    # the paychecks stop; each walks out on a bridge as long as their savings; the gap below is dark
    v = c.get("v", {})
    mb = max(v.get("months_b", 48), 1)
    a.rect([0, GROUND + 20, AW, AH], fill=(6, 6, 8))
    e = F.ease_in_out(F.seg(p, 0.15, 0.95))
    for i, (key, col) in enumerate((("months_s", P["red"]), ("months_m", P["crowd"]), ("months_b", P["bone"]))):
        y = 215 + i * 195
        length = 60 + 880 * v.get(key, 0) / mb
        a.rect([0, y, 60, y + 16], fill=P["crowd_dk"])           # solid ground: the last paycheck
        a.rect([60, y, length, y + 16], fill=(70, 62, 46) if i else P["red_dk"], r=4)
        walk = min(e * 900, length - 40)
        sway = 0 if walk >= length - 41 else t * 7
        G.person(a, 40 + walk, y, 175, col, phase=sway if walk < length - 41 else None, head_down=0.4 if i == 0 else 0.1)
        if i == 0:   # the spender stops at the edge, looking down
            a.glow(80, y - 60, 70, P["red"], int(60 * e))


def art_flex(a, t, p, c):
    # the photo shoot: posing by a car that isn't theirs, flashes popping, hearts floating up
    flash = max(0.0, math.sin(t * 7.0)) ** 8
    a.glow(540, 330, 420, (255, 255, 255), int(40 + 120 * flash))
    G.icon(a, "car", 600, GROUND - 90, 520, P["gold"])
    G.person(a, 270, GROUND, 400, (150, 132, 96), arms_up=True)
    G.icon(a, "bag", 360, GROUND - 120, 70, P["gold"])
    for j in range(7):
        ph = (t * 0.5 + j / 7) % 1
        G.icon(a, "heart", 120 + j * 130 + 20 * math.sin(t + j), 520 - ph * 480, 40 * (1 - ph * 0.5),
               tuple(int(q * (1 - ph)) for q in P["red"]))
    a.rect([880, 260, 980, 440], fill=(12, 12, 16), r=18, outline=(70, 72, 80), width=4)   # the phone filming it
    a.circle(930, 300, 12, (255, 255, 255) if flash > 0.3 else (80, 80, 90))


def art_reveal(a, t, p, c):
    # after the shoot: the car drives off without them, the bag goes back in its box, bills drift down
    e = F.ease_in_out(F.seg(p, 0.05, 0.7))
    G.icon(a, "car", 600 + e * 900, GROUND - 90, 520, P["gold"])
    a.rect([700, GROUND - 120, 860, GROUND], fill=(96, 78, 52), r=6)               # return box
    a.line([(700, GROUND - 120), (860, GROUND - 120)], (60, 48, 30), 6)
    G.icon(a, "bag", 780, GROUND - 160 + 110 * e, 70, P["gold"])
    G.person(a, 270, GROUND, 400, (110, 100, 84), phone=True, head_down=0.8)
    for j in range(9):
        ph = (t * 0.25 + j / 9) % 1
        x = 80 + j * 110 + 30 * math.sin(t * 1.3 + j)
        y = -40 + ph * (GROUND + 40)
        a.rect([x - 26, y - 34, x + 26, y + 34], fill=(220, 214, 200), r=3)
        for k in range(4):
            a.line([(x - 16, y - 18 + k * 12), (x + 16, y - 18 + k * 12)], P["red"] if k == 3 else (120, 116, 108), 3)


def art_quiet(a, t, p, c):
    # nobody looks: the crowd stares at phones while a plain person walks past a tree that keeps growing
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    g = F.ease_in_out(F.seg(p, 0.0, 1.0))
    tx, h = 760, 120 + 380 * g
    a.rect([tx - 14, GROUND - h, tx + 14, GROUND], fill=(90, 70, 46))
    for k, (dx, dy, r) in enumerate([(0, 0, 1.0), (-70, 60, 0.75), (70, 60, 0.75), (0, 110, 0.8)]):
        rr = (60 + 120 * g) * r
        a.glow(tx + dx * g, GROUND - h + dy * g, rr * 1.4, P["warm"], int(40 * g))
        a.circle(tx + dx * g, GROUND - h + dy * g, rr, (176, 140, 70))
    for i, x in enumerate((90, 220, 980)):
        G.person(a, x, GROUND, 290 + (i % 2) * 20, P["crowd"], phone=True, head_down=0.9, facing=1 if x < 500 else -1)
    G.person(a, 380 + 200 * g, GROUND, 320, P["bone"], phase=t * 6)


def _card(a, x, y, s, col, ang=0.0):
    w, h = s, s * 0.63
    a.rect([x - w / 2, y - h / 2, x + w / 2, y + h / 2], fill=col, r=s * 0.06)
    a.rect([x - w * 0.36, y - h * 0.18, x - w * 0.14, y + h * 0.06], fill=P["gold"], r=s * 0.02)
    a.line([(x - w * 0.36, y + h * 0.28), (x + w * 0.2, y + h * 0.28)], P["ink"], s * 0.03)


def art_blade(a, t, p, c):
    # a double-edged blade turning slowly: one edge lit gold (a home, a skill), the other red (a swipe)
    cx, top, bot = 540, 20, GROUND - 40
    turn = math.cos(t * 1.1)
    hw = 40 + 50 * abs(turn)
    left, right = (P["gold"], P["red"]) if turn > 0 else (P["red"], P["gold"])
    a.glow(cx - 220, 300, 200, P["gold"], 70); a.glow(cx + 220, 300, 200, P["red"], 70)
    a.poly([(cx, top), (cx + hw, top + 120), (cx + hw * 0.8, bot - 120), (cx, bot - 80)], (150, 152, 160))
    a.poly([(cx, top), (cx - hw, top + 120), (cx - hw * 0.8, bot - 120), (cx, bot - 80)], (120, 122, 130))
    a.line([(cx - hw, top + 120), (cx - hw * 0.8, bot - 120)], left, 8)
    a.line([(cx + hw, top + 120), (cx + hw * 0.8, bot - 120)], right, 8)
    a.rect([cx - 120, bot - 80, cx + 120, bot - 50], fill=P["crowd_dk"], r=8)
    a.rect([cx - 22, bot - 50, cx + 22, GROUND + 10], fill=(60, 44, 30), r=8)
    G.icon(a, "house", cx - 300, 330, 220, P["gold"])
    _card(a, cx + 300, 330, 220, P["red_dk"])


def art_ladder(a, t, p, c):
    # the good edge: a loan as a ladder up to something that grows (a house), climbed rung by rung
    a.rect([0, GROUND + 6, AW, GROUND + 14], fill=P["crowd_dk"])
    x0, x1 = 360, 500
    a.glow(760, 150, 230, P["warm"], 80)
    G.icon(a, "house", 760, 190, 330, P["gold"])
    a.rect([600, 296, 1000, 314], fill=P["crowd_dk"])
    a.line([(x0, GROUND), (x0 + 160, 296)], (130, 110, 80), 12)
    a.line([(x1, GROUND), (x1 + 160, 296)], (130, 110, 80), 12)
    for k in range(9):
        f = k / 8
        a.line([(x0 + 160 * f, GROUND - (GROUND - 296) * f), (x1 + 160 * f, GROUND - (GROUND - 296) * f)],
               (130, 110, 80), 8)
    e = F.ease_in_out(F.seg(p, 0.05, 0.95)) * 0.85
    G.person(a, x0 + 70 + 160 * e, GROUND - (GROUND - 296) * e, 240, P["bone"], phase=t * 5)


def art_snowball(a, t, p, c):
    # the bad edge: pushing a red ball up a hill with minimum payments; it barely shrinks
    a.poly([(0, GROUND + 14), (AW, 140), (AW, AH), (0, AH)], (26, 28, 36))
    g = F.ease_in_out(F.seg(p, 0.0, 1.0))
    bx = 520 + 70 * g
    by = GROUND + 14 - (GROUND - 126) * bx / AW
    r = 170 - 25 * g
    a.glow(bx, by - r, r * 1.3, P["red"], 70)
    a.circle(bx, by - r, r, P["red_dk"], outline=P["red"], width=6)
    for k in range(5):  # interest keeps rolling in
        ph = (t * 0.6 + k / 5) % 1
        G.icon(a, "coin", bx + 260 - ph * 200, by - r - 220 + ph * 150, 36, P["red"])
    px = bx - r - 50
    py = GROUND + 14 - (GROUND - 126) * px / AW
    G.person(a, px, py, 280, P["bone"], phase=t * 3, run=True, head_down=0.5)
    for k in range(3):   # small coins out: the minimum payment
        ph = (t * 0.8 + k / 3) % 1
        G.icon(a, "coin", px - 40 - ph * 120, py - 120 + ph * 90, 24, P["gold"])


ART = {"office": art_office, "commute": art_commute, "scroll": art_scroll, "compare": art_compare,
       "spend": art_spend, "wheel": art_wheel, "crowd": art_crowd, "walkaway": art_walkaway, "alone": art_alone,
       "payday3": art_payday3, "split3": art_split3, "paycheck_stops": art_paycheck_stops, "flex": art_flex,
       "reveal": art_reveal, "quiet": art_quiet, "blade": art_blade, "ladder": art_ladder, "snowball": art_snowball}
TINT = {"office": (P["glow"], 0.45, 0.45), "scroll": (P["glow"], 0.5, 0.4), "compare": (P["gold"], 0.5, 0.4),
        "spend": (P["gold"], 0.5, 0.5), "wheel": (P["red"], 0.5, 0.55), "crowd": (P["warm"], 0.5, 0.35),
        "walkaway": (P["warm"], 0.9, 0.5), "alone": (P["warm"], 0.5, 0.3), "payday3": (P["green"], 0.5, 0.3),
        "split3": (P["gold"], 0.5, 0.4), "paycheck_stops": (P["red"], 0.5, 0.45), "flex": (P["gold"], 0.5, 0.5),
        "reveal": (P["red"], 0.5, 0.45), "quiet": (P["warm"], 0.7, 0.4), "blade": (P["red"], 0.5, 0.4),
        "ladder": (P["warm"], 0.7, 0.4), "snowball": (P["red"], 0.5, 0.55)}


# ================================================================ frame assembly
def brand(img, tag):
    d = ImageDraw.Draw(img)
    x, y = SAFE["left"], SAFE["top"] + 4
    lg = F.logo(56)
    img.paste(lg, (x, y), lg)
    d.text((x + 72, y + 10), "QuanTik", font=font("sans-bold", 30), fill=P["bone"])
    f = font("sans-bold", 22); tw = d.textlength(tag, font=f)
    d.rounded_rectangle([SAFE["right"] - tw - 36, y + 10, SAFE["right"], y + 50], radius=20, outline=P["red"], width=2)
    d.text((SAFE["right"] - tw - 18, y + 17), tag, font=f, fill=P["red"])


def story_scene(i, item, ctx, art_ctx):
    kind = item["kind"]; show = item.get("show", "")
    draw_art = ART[kind]

    def draw(img, t, p):
        img.paste(G.backdrop(W, H, TINT.get(kind)), (0, 0))
        a = G.Art(AW, AH)
        draw_art(a, t, p, art_ctx)
        im = a.image()
        drift = int(10 * math.sin(t * 0.6))                         # slow handheld drift
        img.paste(im, (ART_BOX[0] + drift, ART_BOX[1]), im)
        brand(img, ctx["tag"])
        if show:
            al = F.ease_out(F.seg(p, 0.0, 0.18))
            F.text_box(img, show, TEXT_BOX, "sans-black", 84, P["bone"], "left", "middle", min_size=44,
                       label=f"s{i}-show", hl_numbers=True, hl_color=P["red"], alpha=al, spacing=1.08)
        if item.get("note"):
            F.text_box(img, item["note"], (SAFE["left"], 1270, SAFE["right"], 1316), "sans", 22, P["muted"], "left",
                       "middle", min_size=18, label=f"s{i}-note")
        img.paste(G.film_grain(img, t), (0, 0))

    return Scene(f"s{i:02d}-{kind}", item["say"], draw, item.get("min_dur", 3.0), texts=[show, item.get("note", "")],
                 header=False)


def end_scene(ep, ctx):
    def draw(img, t, p):
        img.paste(G.backdrop(W, H, (P["red"], 0.5, 0.35)), (0, 0))
        F.end_card(img, p, ep["cta"], ctx["disclaimer"], ctx["tag"])
        img.paste(G.film_grain(img, t), (0, 0))

    return Scene("end", ep["cta"], draw, 3.5, texts=[ep["cta"], ctx["disclaimer"]], header=False)


def build(ep, model, ctx):
    v = model.values
    art_ctx = {"n": int(v.get("n_paths", 2000)), "k": int(v.get("esc_a_n", 30)), "v": v}
    out = [story_scene(i, it, ctx, art_ctx) for i, it in enumerate(ep["scenes"], 1)]
    out.append(end_scene(ep, ctx))
    return out


def export(scenes, ep, model, ctx):
    """Dark cover (thumbnail.jpg): heavy headline + one illustration (thumb.art, default wheel) + the one sourced number."""
    thumbnail(ep, model, ctx["out"] / "thumbnail.jpg", ep.get("episode_no"))


def thumbnail(ep, model, path, no=None):
    th = ep.get("thumb", {})
    img = G.backdrop(W, H, (P["red"], 0.5, 0.72)).copy()
    d = ImageDraw.Draw(img)
    # series badge
    lg = F.logo(120); img.paste(lg, (64, 64), lg)
    series = th.get("series", "THE DARK TRUTH OF MONEY") + (f"  #{no}" if no else "")
    f = font("sans-black", 34); tw = d.textlength(series, font=f)
    d.rounded_rectangle([W - 64 - tw - 56, 88, W - 64, 160], radius=36, outline=P["red"], width=4)
    d.text((W - 64 - tw - 28, 104), series, font=f, fill=P["red"])
    # headline: three heavy lines, last one red
    lines = th.get("headline", ["YOU GOT THE RAISE.", "STILL", "TRAPPED."])
    sizes = [104, 300, 230]
    y = 250
    for i, (ln, sz) in enumerate(zip(lines, sizes)):
        while d.textlength(ln, font=font("sans-black", sz)) > W - 128 and sz > 40:
            sz -= 6
        fo = font("sans-black", sz)
        x = (W - d.textlength(ln, font=fo)) / 2
        col = P["red"] if i == len(lines) - 1 else P["bone"]
        top = fo.getbbox("H")[1]
        d.text((x + 6, y - top + 8), ln, font=fo, fill=(0, 0, 0))   # hard drop shadow
        d.text((x, y - top), ln, font=fo, fill=col)
        y += int(sz * 0.98) + 18
    # illustration: running in the wheel with the bag of upgrades
    a = G.Art(AW, AH)
    ART[th.get("art", "wheel")](a, th.get("art_t", 0.17), th.get("art_p", 1.0), {"v": model.values, "n": 1, "k": 0})
    im = a.image().resize((int(AW * 1.0), int(AH * 1.0)))
    img.paste(im, (0, y + 10), im)
    # the one number, from the model
    sub = th.get("sub", "")
    if sub:
        F.text_box(img, sub, (64, 1560, W - 64, 1660), "sans-black", 58, P["bone"], "center", "middle", min_size=36,
                   label="thumb-sub", hl_numbers=True, hl_color=P["red"])
    fs = font("sans-bold", 34)
    foot = th.get("footer", L("thumb_footer"))
    d.text(((W - d.textlength(foot, font=fs)) / 2, 1700), foot, font=fs, fill=P["muted"])
    fu = font("sans-black", 44); url = "quantik.io.vn"
    d.text(((W - d.textlength(url, font=fu)) / 2, 1770), url, font=fu, fill=P["bone"])
    img = G.film_grain(img, 0.0)
    img.save(path, quality=95)
    return path
