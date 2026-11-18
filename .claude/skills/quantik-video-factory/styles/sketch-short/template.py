"""sketch-short: hand-drawn explainer for the YT Shorts / IG Reels channel (channels/yt-ig.md). 30–50 s.

Chalk-on-board look: hook pops in with a hand-drawn underline, the concept's simulation/diagram is drawn
stroke by stroke (matplotlib xkcd mode), the key number counts up inside a scribbled circle, then a
takeaway and the follow card. Every number comes from concepts.ConceptModel (or a sourced fact).

Scenes: hook → beats[0] → visual (beats[1]) → punch (beats[2]) → beats[3] → takeaway → end
"""
from __future__ import annotations

import math
import re
from functools import lru_cache

import numpy as np

import frames as F
import scenes as S
from core import THEME as T, hex_
from render import Scene

KIND = "video"
VOICE_RATE = "+8%"      # Shorts/Reels: a touch faster than the calm explainer pace
DEFAULTS = {"max_seconds": 60}


# ---------------------------------------------------------------- hand-drawn strokes (PIL)
def wobble_line(img, p0, p1, progress, color, width=8, seed=0, amp=5):
    if progress <= 0:
        return
    rng = np.random.default_rng(seed)
    n = 28
    xs = np.linspace(p0[0], p1[0], n); ys = np.linspace(p0[1], p1[1], n)
    noise = np.convolve(rng.normal(0, amp, n + 4), np.ones(5) / 5, "valid")[:n]
    nx, ny = -(p1[1] - p0[1]), (p1[0] - p0[0])
    L = math.hypot(nx, ny) or 1
    pts = [(x + noise[i] * nx / L, y + noise[i] * ny / L) for i, (x, y) in enumerate(zip(xs, ys))]
    k = max(2, int(n * F.clamp(progress)))
    F.ImageDraw.Draw(img).line(pts[:k], fill=color, width=width, joint="curve")


def scribble_circle(img, box, progress, color, width=7, seed=1):
    if progress <= 0:
        return
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    n = 90
    a0 = -2.4
    ts = np.linspace(a0, a0 + 2 * math.pi * 1.12, n)
    jit = np.convolve(rng.normal(0, 0.035, n + 6), np.ones(7) / 7, "valid")[:n]
    pts = [(cx + rx * (1 + jit[i]) * math.cos(t), cy + ry * (1 + jit[i]) * math.sin(t)) for i, t in enumerate(ts)]
    k = max(2, int(n * F.clamp(progress)))
    F.ImageDraw.Draw(img).line(pts[:k], fill=color, width=width, joint="curve")


# ---------------------------------------------------------------- sketch chart (matplotlib xkcd)
_MODELS = {}


@lru_cache(maxsize=128)
def _sketch(model_id, step, steps, w, h, title):
    import matplotlib.patheffects as pe

    plt = F.plt
    model = _MODELS[model_id]
    with plt.xkcd(scale=1.8, length=90, randomness=3):
        plt.rcParams["font.family"] = [F._SANS_NAME, "DejaVu Sans"]
        plt.rcParams["path.effects"] = [pe.withStroke(linewidth=3, foreground=hex_(T["bg"]))]
        fig = plt.figure(figsize=(w / 100, h / 100))
        fig.patch.set_alpha(0)
        ax = fig.add_axes([0.14, 0.12, 0.82, 0.76 if title else 0.84])
        model.plot2d(ax, max(0.02, step / steps))
        if title:
            fig.text(0.03, 0.97, title, fontsize=26, color=hex_(T["text"]), weight="bold", va="top")
        im = F.fig_to_img(fig, transparent=True)
    return im


def sketch_chart(model, say, title=None, note=None, name="visual", min_dur=5.0):
    _MODELS[id(model)] = model
    box = (S.X0, 330, S.X1, 1130 if note else 1290)
    w, h = box[2] - box[0], box[3] - box[1]
    steps = 30

    def draw(img, t, p):
        step = max(1, int(steps * F.ease_in_out(F.seg(p, 0, 0.8)) + 0.5))
        F.paste(img, _sketch(id(model), step, steps, w, h, title), (box[0], box[1]))
        if note:
            F.text_box(img, note, (S.X0, box[3] + 24, S.X1, S.BOT), "sans", 30, T["muted"], "left", "top",
                       min_size=22, label=f"{name}-note", alpha=F.ease_out(F.seg(p, 0.1, 0.3)))

    return Scene(name, say, draw, min_dur, texts=[title or "", note or ""])


# ---------------------------------------------------------------- text scenes
def hook(ep, ctx):
    text, words = ep["hook"], ep["hook"].split()
    kicker, en = ep.get("kicker", ""), ep.get("en", "")

    def draw(img, t, p):
        if kicker:
            F.chip(img, (S.X0, 390), kicker, T["accent"], 28)
        if en:
            F.text_box(img, en, (S.X0, 470, S.X1, 540), "mono-bold", 40, T["neutral"], label="hook-en")
        k = max(1, int(len(words) * F.ease_out(F.seg(p, 0, 0.45)) + 0.999))
        used = F.text_box(img, " ".join(words[:k]), (S.X0, 570, S.X1, 1180), "sans-black", 88, T["text"], "left",
                          "middle", min_size=46, label="hook", spacing=1.12, hl_numbers=True)
        y = min(1230, used[3] + 30)
        wobble_line(img, (S.X0, y), (S.X0 + 420, y + 6), F.seg(p, 0.35, 0.7), T["accent"], 10, seed=4)

    return Scene("hook", text, draw, 2.8, texts=[text, kicker, en])


def written(text, name, chip=None, size=64, color=None, min_dur=3.0, underline=True):
    words = text.split()

    def draw(img, t, p):
        if chip:
            F.chip(img, (S.X0, 400), chip, T["raised"], 26)
        n = max(1, int(len(words) * F.seg(p, 0.02, 0.6) + 0.999))
        used = F.text_box(img, " ".join(words[:n]), (S.X0, 500, S.X1, 1220), "sans-bold", size, color or T["text"],
                          "left", "middle", min_size=38, label=name, hl_numbers=True)
        if underline:
            y = min(1260, used[3] + 26)
            wobble_line(img, (S.X0, y), (S.X0 + 260, y + 4), F.seg(p, 0.55, 0.8), T["neutral"], 7, seed=len(text))

    return Scene(name, text, draw, min_dur, texts=[text, chip or ""])


_NUM = re.compile(r"([−\-]?)(\d[\d.]*)(?:,(\d+))?(.*)")


def _countup(token, k):
    m = _NUM.fullmatch(token)
    if not m or k >= 1:
        return token
    sign, ip, fp, suf = m.group(1), m.group(2).replace(".", ""), m.group(3) or "", m.group(4) or ""
    val = float(ip + ("." + fp if fp else "")) * k
    s = f"{val:.{len(fp)}f}"
    a, _, b = s.partition(".")
    return sign + f"{int(a):,}".replace(",", ".") + ("," + b if b else "") + suf


def punch(ep, say):
    pc = ep.get("punch") or {}
    value, label = pc.get("value", ""), pc.get("label", "")
    if not value:
        return written(say, "punch", size=66)

    def draw(img, t, p):
        k = F.ease_out(F.seg(p, 0.0, 0.4))
        F.text_box(img, label, (S.X0, 400, S.X1, 520), "sans-bold", 44, T["muted"], "center", "middle", min_size=28,
                   label="punch-label")
        used = F.text_box(img, _countup(value, k), (S.X0 + 40, 560, S.X1 - 40, 900), "mono-bold", 200, T["accent"],
                          "center", "middle", min_size=80, label="punch-value")
        scribble_circle(img, (used[0] - 60, used[1] - 50, used[2] + 60, used[3] + 60), F.seg(p, 0.35, 0.65),
                        T["neutral"], 8)
        F.text_box(img, say, (S.X0, 1000, S.X1, S.BOT), "sans-bold", 48, T["text"], "center", "top", min_size=30,
                   label="punch-say", hl_numbers=True, alpha=F.ease_out(F.seg(p, 0.15, 0.35)))

    return Scene("punch", say, draw, 3.5, texts=[value, label, say])


def build(ep, model, ctx):
    b = ep["beats"]
    out = [hook(ep, ctx),
           written(b[0], "beat1"),
           sketch_chart(model, b[1], title=ep.get("chart_title"), note=ep.get("chart_note")),
           punch(ep, b[2]),
           written(b[3], "beat4", size=60),
           written(ep["takeaway"], "takeaway", chip="Mang về", size=60, color=T["neutral"], underline=False),
           S.end(ep["cta"], ctx["disclaimer"], ctx["tag"])]
    return out
