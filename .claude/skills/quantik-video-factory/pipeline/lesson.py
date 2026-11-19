"""Lesson topics: series "Học Quant cùng QuanTik" (knowledge/lessons/*.json).

Each lesson carries a short demo (the exact code shown on screen) that really runs; every number in the
narration is a variable from that run, referenced as {key}. A hidden `plot` snippet may add arrays for the
chart only. Same interface as models.Model, so every style template works unchanged.

Lesson JSON fields
  id, no, name, seed
  code      : shown + executed (≤ 16 lines, ≤ 56 chars/line)
  plot      : optional hidden code run after `code` (chart-only arrays, never quoted in narration)
  values    : {"key": "fmt"} or {"key": ["python expr", "fmt"]}  → placeholders
  chart     : {"type": line|hist|bar|scatter|heatmap|vectors, ...}   (expressions evaluated in the run namespace)
  surface   : optional {"type": gauss2d|grid|line3d, ...}; without it the 3D slot shows the formula card
  episode   : hook, kicker, title, beats[4], outputs, takeaway, formula, caption, hashtags, broll, hook_broll…

python lesson.py --list | --check [ids] | --show <id>
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np

from core import KNOWLEDGE, THEME as T, hex_

LESSONS = KNOWLEDGE / "lessons"
C = {"text": hex_(T["text"]), "muted": hex_(T["muted"]), "accent": hex_(T["accent"]), "pos": hex_(T["positive"]),
     "neg": hex_(T["negative"]), "neu": hex_(T["neutral"]), "border": hex_(T["border"])}
PALETTE = [C["accent"], C["pos"], C["neu"], C["neg"], C["text"]]


@lru_cache(maxsize=1)
def load_all():
    out = {}
    for p in sorted(LESSONS.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        for les in data.get("lessons", []):  # broll-v2.json etc. are overlays, not series
            les["series"] = data.get("series", p.stem)
            les["_file"] = p.name
            out[les["id"]] = les
    return out


def get(topic):
    return load_all().get(topic)


def _col(c, i=0):
    return C.get(c, c) if c else PALETTE[i % len(PALETTE)]


class LessonModel:
    def __init__(self, spec, seed=None, returns=None):
        self.spec = spec
        self.topic = spec["id"]
        self.seed = spec.get("seed", 0)
        self.real_data = False
        self.code = spec["code"].rstrip()
        self.code_title = f"{spec['id'].split('-', 1)[-1]}.py"
        self.run_title = f"python {self.code_title}"
        ns = {"np": np}
        exec(compile(self.code, f"<{self.topic}>", "exec"), ns)
        if spec.get("plot"):
            exec(compile(spec["plot"], f"<{self.topic}:plot>", "exec"), ns)
        self.ns = ns
        self.values, self.formats = {}, {}
        for k, v in spec["values"].items():
            expr, fmt = (v if isinstance(v, list) else [k, v])
            val = eval(expr, ns)
            val = val.item() if hasattr(val, "item") else val
            self.values[k] = float(val) if isinstance(val, float) else int(val) if isinstance(val, (int, np.integer)) else val
            self.formats[k] = fmt
        self.series = {}
        self.has_chart = bool(spec.get("chart"))
        self.has_surface = bool(spec.get("surface"))
        f = spec.get("episode", {}).get("formula", "")
        self.entry = {"formulaLatex": f, "vi": spec.get("name", self.topic), "methods": []}
        self.has_formula = bool(f)

    def ev(self, e):
        return eval(e, self.ns) if isinstance(e, str) else e

    # ------------------------------------------------------------ 2D
    def plot2d(self, ax, upto=1.0):
        ch = self.spec["chart"]
        kind = ch["type"]
        getattr(self, "_" + kind)(ax, ch, upto)
        for e in ch.get("hlines", []):
            ax.axhline(self.ev(e[0]), color=_col(e[2] if len(e) > 2 else "muted"), lw=2, ls="--")
            if len(e) > 1 and e[1]:
                ax.text(ax.get_xlim()[0], self.ev(e[0]), " " + e[1], color=_col(e[2] if len(e) > 2 else "muted"),
                        fontsize=17, va="bottom")
        if ch.get("xlabel"):
            ax.set_xlabel(ch["xlabel"], fontsize=18)
        if ch.get("ylabel"):
            ax.set_ylabel(ch["ylabel"], fontsize=18)
        ax.tick_params(labelsize=15)
        if any(len(y) > 1 and y[1] for y in ch.get("ys", [])) or ch.get("legend"):
            lg = ax.legend(fontsize=16, loc=ch.get("legend_loc", "upper right"), facecolor=hex_(T["surface"]),
                           edgecolor=C["border"], labelcolor=C["text"])
            if ch["type"] == "hist":
                lg.set_alpha(max(0.0, min(1.0, (upto - 0.35) / 0.25)))
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)

    def _line(self, ax, ch, upto):
        ys = [(np.asarray(self.ev(y[0]), float), y) for y in ch["ys"]]
        n = max(len(a) for a, _ in ys)
        x_all = np.asarray(self.ev(ch["x"]), float) if ch.get("x") else np.arange(n)
        k = max(2, int(n * upto))
        lo = min(np.nanmin(a) for a, _ in ys); hi = max(np.nanmax(a) for a, _ in ys)
        for i, (a, y) in enumerate(ys):
            x = x_all[: len(a)]
            ax.plot(x[:k], a[:k], color=_col(y[2] if len(y) > 2 else None, i), lw=y[3] if len(y) > 3 else 2.6,
                    label=y[1] if len(y) > 1 and y[1] else None)
        pad = (hi - lo) * 0.08 or 1
        ax.set_xlim(x_all[0], x_all[n - 1]); ax.set_ylim(lo - pad, hi + pad)

    def _hist(self, ax, ch, upto):
        data = np.asarray(self.ev(ch["data"]), float)
        k = max(20, int(len(data) * upto))
        bins = np.linspace(*(ch.get("range") or (np.percentile(data, 0.5), np.percentile(data, 99.5))), ch.get("bins", 40))
        full, _ = np.histogram(data, bins=bins, density=True)
        ax.hist(data[:k], bins=bins, density=True, color=C["accent"], alpha=0.85, edgecolor=hex_(T["surface"]))
        ax.set_ylim(0, full.max() * 1.25)
        ca = max(0.0, min(1.0, (upto - 0.35) / 0.25))     # overlays fade in instead of popping
        va = max(0.0, min(1.0, (upto - 0.55) / 0.25))
        for i, e in enumerate(ch.get("curves", [])):
            x, y = self.ev(e[0]), self.ev(e[1])
            ax.plot(x, y, color=_col(e[3] if len(e) > 3 else "pos"), lw=3, alpha=ca, label=e[2] if len(e) > 2 else None)
        for e in ch.get("vlines", []):
            ax.axvline(self.ev(e[0]), color=_col(e[2] if len(e) > 2 else "neu"), lw=2.5, ls="--", alpha=va,
                       label=e[1] if len(e) > 1 else None)
        if ch.get("curves") or ch.get("vlines"):
            ch["legend"] = True

    def _bar(self, ax, ch, upto):
        h = np.asarray(self.ev(ch["heights"]), float)
        labels = self.ev(ch["labels"]) if ch.get("labels") is not None else [str(i) for i in range(len(h))]
        k = max(1, int(round(len(h) * upto + 0.49)))
        cols = [(_col("pos") if v >= 0 else _col("neg")) if ch.get("signed") else _col(ch.get("color", "accent"))
                for v in h]
        ax.bar(range(k), h[:k], color=cols[:k], width=0.7)
        ax.set_xlim(-0.6, len(h) - 0.4)
        lo, hi = min(0, h.min()), max(0, h.max())
        ax.set_ylim(lo - 0.1 * (hi - lo), hi + 0.15 * (hi - lo))
        ax.set_xticks(range(len(h)))
        ax.set_xticklabels([str(x) for x in labels], fontsize=15, rotation=ch.get("rot", 0))
        for b in ch.get("band", []):
            ax.axhspan(-self.ev(b), self.ev(b), color=C["muted"], alpha=0.15)

    def _scatter(self, ax, ch, upto):
        x, y = np.asarray(self.ev(ch["x"]), float), np.asarray(self.ev(ch["y"]), float)
        k = max(5, int(len(x) * upto))
        ax.scatter(x[:k], y[:k], s=ch.get("s", 26), color=C["accent"], alpha=0.75, edgecolors="none")
        ax.set_xlim(x.min() - 0.05 * np.ptp(x), x.max() + 0.05 * np.ptp(x))
        ax.set_ylim(y.min() - 0.05 * np.ptp(y), y.max() + 0.05 * np.ptp(y))
        if ch.get("fit") and upto > 0.6:
            b, a = np.polyfit(x, y, 1)
            xs = np.linspace(x.min(), x.max(), 10)
            ax.plot(xs, a + b * xs, color=C["pos"], lw=3)

    def _heatmap(self, ax, ch, upto):
        M = np.asarray(self.ev(ch["M"]), float)
        k = max(1, int(round(M.shape[0] * upto + 0.49)))
        show = np.full_like(M, np.nan); show[:k] = M[:k]
        vmax = ch.get("vmax") or np.abs(M).max()
        ax.imshow(show, cmap=ch.get("cmap", "RdYlGn"), vmin=-vmax if ch.get("signed", True) else 0, vmax=vmax)
        labels = self.ev(ch["labels"]) if ch.get("labels") else [str(i) for i in range(M.shape[0])]
        ax.set_xticks(range(M.shape[1])); ax.set_yticks(range(M.shape[0]))
        ax.set_xticklabels(labels, fontsize=16); ax.set_yticklabels(labels, fontsize=16)
        for i in range(k):
            for j in range(M.shape[1]):
                ax.text(j, i, f"{M[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=17,
                        color="#101010", weight="bold")
        ax.grid(False)

    def _vectors(self, ax, ch, upto):
        vecs = ch["vecs"]
        k = max(1, int(round(len(vecs) * upto + 0.49)))
        lim = ch.get("lim", 3)
        if ch.get("grid"):  # transformed grid lines
            M = np.asarray(self.ev(ch["grid"]), float)
            a = min(1.0, upto * 1.5)
            for g in np.arange(-lim, lim + 1):
                for line in (np.array([[g, -lim], [g, lim]]), np.array([[-lim, g], [lim, g]])):
                    tl = line @ ((1 - a) * np.eye(2) + a * M).T
                    ax.plot(tl[:, 0], tl[:, 1], color=C["border"], lw=1.2)
        for i, v in enumerate(vecs[:k]):
            xy = np.asarray(self.ev(v[0]), float)
            c = _col(v[2] if len(v) > 2 else None, i)
            ax.annotate("", xy=xy, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=4, mutation_scale=28))
            if len(v) > 1 and v[1]:
                ax.text(xy[0] * 1.08, xy[1] * 1.08, v[1], color=c, fontsize=20, weight="bold")
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
        ax.axhline(0, color=C["muted"], lw=1); ax.axvline(0, color=C["muted"], lw=1)

    # ------------------------------------------------------------ 3D
    def surface(self):
        sp = self.spec["surface"]
        kind = sp["type"]
        if kind == "gauss2d":
            S = np.asarray(self.ev(sp["cov"]), float)
            lim = sp.get("lim", 3 * np.sqrt(max(S[0, 0], S[1, 1])))
            g = np.linspace(-lim, lim, 70)
            X, Y = np.meshgrid(g, g)
            P = np.stack([X, Y], -1)
            inv = np.linalg.inv(S)
            Z = np.exp(-0.5 * np.einsum("...i,ij,...j", P, inv, P)) / (2 * np.pi * np.sqrt(np.linalg.det(S)))
            return {"X": X, "Y": Y, "Z": Z, "xl": sp.get("xl", "x"), "yl": sp.get("yl", "y"), "zl": sp.get("zl", "mật độ")}
        if kind == "grid":
            fn = eval(sp["fn"], self.ns)
            X, Y = np.meshgrid(np.linspace(*sp["x"], 60), np.linspace(*sp["y"], 60))
            return {"X": X, "Y": Y, "Z": fn(X, Y), "xl": sp["xl"], "yl": sp["yl"], "zl": sp["zl"]}
        if kind == "hist2d":  # joint distribution of two simulated quantities, as a 3D histogram surface
            x, y = np.asarray(self.ev(sp["x"]), float), np.asarray(self.ev(sp["y"]), float)
            lo = np.percentile(x, 1), np.percentile(y, 1)
            hi = np.percentile(x, 99), np.percentile(y, 99)
            Z, xe, ye = np.histogram2d(x, y, bins=sp.get("bins", 40), range=[[lo[0], hi[0]], [lo[1], hi[1]]], density=True)
            X, Y = np.meshgrid((xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2, indexing="ij")
            k = np.array([1, 4, 6, 4, 1], float); k /= k.sum()  # light smoothing, numpy only
            Z = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 0, Z)
            Z = np.apply_along_axis(lambda r: np.convolve(r, k, "same"), 1, Z)
            return {"X": X, "Y": Y, "Z": Z, "xl": sp["xl"], "yl": sp["yl"], "zl": sp["zl"]}
        if kind == "line3d":
            return {"line": [np.asarray(self.ev(sp[a]), float) for a in ("x", "y", "z")], "xl": sp["xl"],
                    "yl": sp["yl"], "zl": sp["zl"]}
        raise ValueError(kind)


@lru_cache(maxsize=1)
def broll_v2():
    p = LESSONS / "broll-v2.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def episode(spec):
    ep = dict(spec.get("episode", {}))
    ep.update(broll_v2().get(spec["id"], {}))   # 4 lớp B-roll ảnh thật (hook, người, hiện tượng, câu chốt)
    ep.setdefault("max_seconds", 75)            # thêm cảnh B-roll → nới giới hạn (Shorts/Reels nhận > 60s)
    # huy hiệu góc phải chỉ ghi tên chủ đề, không đánh số tập (yêu cầu chủ kênh)
    ep.setdefault("tag", spec.get("short", spec["id"].split("-", 1)[-1].upper())[:18])
    ep.setdefault("title", spec.get("name"))
    ep.setdefault("allowed_literals", [])
    ep["series_no"] = spec.get("no")
    return ep


# ---------------------------------------------------------------- dev tools
def check(ids=None):
    import re

    from core import fill_tree

    bad = 0
    for lid, spec in load_all().items():
        if ids and lid not in ids:
            continue
        try:
            m = LessonModel(spec)
            lines = m.code.splitlines()
            probs = [f"code {len(lines)} dòng > 16"] if len(lines) > 16 else []
            probs += [f"dòng {i + 1} dài {len(l)}" for i, l in enumerate(lines) if len(l) > 56]
            ep = episode(spec)
            fill_tree(ep, m.values, m.formats, set())
            if len(ep.get("beats", [])) < 4:
                probs.append("cần 4 beats")
            for o in ep.get("outputs", []):
                if o["key"] not in m.values:
                    probs.append(f"output {o['key']} không có giá trị")
            if m.has_chart:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(); m.plot2d(ax, 0.5); m.plot2d(ax, 1.0); plt.close(fig)
            if m.has_surface:
                m.surface()
        except Exception as e:  # noqa
            probs = [f"{type(e).__name__}: {e}"]
        status = "OK " if not probs else "ERR"
        bad += bool(probs)
        print(f"{status} {lid:<34} " + ("; ".join(probs) if probs else
              " ".join(f"{k}={v:.4g}" if isinstance(v, float) else f"{k}={v}" for k, v in list(m.values.items())[:5])))
    return bad


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "--list":
        for lid, s in load_all().items():
            print(f"{s.get('no', ''):>3}  {lid:<34} {s.get('name', '')}")
    elif args[0] == "--check":
        sys.exit(1 if check(set(args[1:]) or None) else 0)
    elif args[0] == "--show":
        from core import fmt_vi

        m = LessonModel(get(args[1]))
        print(m.code)
        for k, v in m.values.items():
            print(f"  {{{k}}}".ljust(24), fmt_vi(v, m.formats[k]))
