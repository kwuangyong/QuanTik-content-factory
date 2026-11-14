"""Ảnh bìa 1080x1920, nền sáng, có số tập series "Học Quant cùng QuanTik #N".

    python thumbnail.py --topic sortino --no 4 --out ../../../../social-output/sortino-myth-buster

Thiết kế: brand/thumbnail.md (đọc trước khi sửa). Ảnh mẫu: brand/thumbnail-refs/.
Nội dung lấy từ khối "thumb" trong video_defaults của knowledge/models/<topic>.md; mọi số đi qua {key}.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import frames as F
from core import fill, load_model_kb
from models import Model

W, H = 1080, 1920
SERIES = "HỌC QUANT CÙNG QUANTIK"
C = {  # bảng màu nền sáng (brand/thumbnail.md)
    "bg": (245, 242, 235), "grid": (230, 226, 216), "ink": (15, 59, 46), "orange": (232, 116, 42),
    "green": (35, 160, 95), "pill": (220, 232, 224), "muted": (74, 90, 82), "white": (255, 255, 255),
}
INTER = "/usr/share/fonts/opentype/inter/"


def fnt(weight, size):
    name = {"black": "InterDisplay-Black.otf", "xbold": "InterDisplay-ExtraBold.otf", "bold": "Inter-Bold.otf",
            "semi": "Inter-SemiBold.otf"}[weight]
    try:
        return ImageFont.truetype(INTER + name, size)
    except OSError:
        return F.font("sans-bold", size)


def background():
    img = Image.new("RGB", (W, H), C["bg"])
    d = ImageDraw.Draw(img)
    for v in range(0, max(W, H), 54):
        d.line([(v, 0), (v, H)], fill=C["grid"]); d.line([(0, v), (W, v)], fill=C["grid"])
    return img


def spans(text):
    """'CÙNG SHARPE [o]1,38[/o]' → [(text, màu)]. Thẻ: [o] cam, [g] xanh lá."""
    out = []
    for part in re.split(r"(\[[og]\].*?\[/[og]\])", text):
        if not part:
            continue
        m = re.match(r"\[([og])\](.*?)\[/\1\]", part)
        out.append((m.group(2), C["orange" if m.group(1) == "o" else "green"]) if m else (part, C["ink"]))
    return out


def headline_line(d, y, text, max_size, weight="black", max_w=W - 120):
    """Một dòng tiêu đề căn giữa, tự thu nhỏ cho vừa bề ngang. Trả về y của dòng kế tiếp."""
    sp = spans(text)
    s = max_size
    while True:
        f = fnt(weight, s)
        tw = sum(d.textlength(t, font=f) for t, _ in sp)
        if tw <= max_w or s <= 40:
            break
        s -= 4
    x = (W - tw) / 2
    top = f.getbbox("ÂH")[1]
    for t, col in sp:
        d.text((x, y - top), t, font=f, fill=col)
        x += d.textlength(t, font=f)
    return y + int(s * 1.02)


def pill(d, cx, y, text, size=40, fill_=None, color=None, weight="semi", pad=(40, 18)):
    f = fnt(weight, size)
    tw = d.textlength(text, font=f)
    x0, x1 = cx - tw / 2 - pad[0], cx + tw / 2 + pad[0]
    y1 = y + size + 2 * pad[1]
    d.rounded_rectangle([x0, y, x1, y1], radius=(y1 - y) // 2, fill=fill_)
    d.text((x0 + pad[0], y + pad[1] - size * 0.1), text, font=f, fill=color or C["ink"])
    return x0, y1


def logo_tile(img, x, y, size=150):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + size, y + size], radius=size // 5, fill=(24, 24, 22))
    lg = F.logo(int(size * 0.8)).copy()
    img.paste(lg, (x + size // 10, y + size // 10), lg)


def series_badge(d, y, no):
    """Dải series căn giữa: 'HỌC QUANT CÙNG QUANTIK' xanh đậm + ô cam '#N' chữ trắng."""
    f = fnt("xbold", 40); fb = fnt("black", 54)
    t, b = SERIES, f"#{no}"
    tw, bw = d.textlength(t, font=f), d.textlength(b, font=fb)
    x = (W - (tw + 24 + bw + 40)) / 2
    d.text((x, y + 38 - f.getbbox("H")[3] / 2 - 2), t, font=f, fill=C["ink"])
    bx = x + tw + 24
    d.rounded_rectangle([bx, y, bx + bw + 40, y + 76], radius=20, fill=C["orange"])
    d.text((bx + 20, y + 38 - fb.getbbox("#4")[3] / 2 - 4), b, font=fb, fill=C["white"])
    return y + 76


# ---------------------------------------------------------------- chart nền sáng (trong suốt)
def chart_sortino(m, w, h):
    s = m.series
    fig = F.plt.figure(figsize=(w / 100, h / 100)); fig.patch.set_alpha(0)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96]); ax.set_facecolor((0, 0, 0, 0))
    off = 0.1
    for r, y0 in ((s["a"], off), (s["b"], -off)):
        x = np.arange(len(r))
        ax.vlines(x[r >= 0], y0, y0 + r[r >= 0], color="#9fb8aa", lw=1.3)
        ax.vlines(x[r < 0], y0, y0 + r[r < 0], color="#e8742a", lw=1.7)
        ax.axhline(y0, color="#0f3b2e", lw=1.4)
    ax.set_ylim(-off - 0.065, off + 0.065); ax.set_xlim(0, len(s["a"])); ax.axis("off")
    return F.fig_to_img(fig, transparent=True)


def chart_generic(m, w, h):
    """Mặc định: chart 2D của mô hình, đổi màu trục cho nền sáng."""
    fig = F.plt.figure(figsize=(w / 100, h / 100)); fig.patch.set_alpha(0)
    ax = fig.add_axes([0.1, 0.1, 0.86, 0.86]); ax.set_facecolor((0, 0, 0, 0))
    m.plot2d(ax)
    ax.tick_params(colors="#4a5a52"); ax.xaxis.label.set_color("#4a5a52"); ax.yaxis.label.set_color("#4a5a52")
    for sp in ax.spines.values():
        sp.set_color("#0f3b2e")
    if ax.get_legend():
        for t in ax.get_legend().get_texts():
            t.set_color("#0f3b2e")
    return F.fig_to_img(fig, transparent=True)


CHARTS = {"sortino": chart_sortino}  # thêm chart riêng cho topic khác ở đây


def build(topic, no, out):
    m = Model(topic)
    vd = load_model_kb(topic)
    th = vd.get("thumb", {})
    f = lambda s: fill(s, m.values, m.formats)
    img = background(); d = ImageDraw.Draw(img)

    logo_tile(img, 64, 64)
    tag = th.get("tag", vd.get("kicker", topic)).upper()
    ft = fnt("xbold", 38); tw = d.textlength(tag, font=ft)
    d.rounded_rectangle([W - 64 - tw - 64, 100, W - 64, 176], radius=38, outline=C["ink"], width=4)
    d.text((W - 64 - tw - 32, 138 - ft.getbbox("H")[3] / 2 - 2), tag, font=ft, fill=C["ink"])

    y = series_badge(d, 262, no) + 64
    for ln in th.get("headline", [vd.get("kicker", topic).upper()]):
        ln = {"t": ln} if isinstance(ln, str) else ln
        y = headline_line(d, y, f(ln["t"]), ln.get("size", 110), ln.get("weight", "black")) + 26
    if th.get("pill"):
        _, y = pill(d, W / 2, y + 10, f(th["pill"]), 40, fill_=C["pill"])
    y += 56

    labels = th.get("labels", [])
    cw = W - 128 - (270 if labels else 0)
    ch_h = 1610 - y
    im = CHARTS.get(topic, chart_generic)(m, cw, ch_h)
    img.paste(im, (64, y), im)
    for i, lb in enumerate(labels):
        col = C["green"] if lb.get("color") == "green" else C["orange"]
        step = ch_h / len(labels)
        ly = y + step * i + step / 2 - 70
        d.text((W - 64 - 260, ly), f(lb["label"]), font=fnt("bold", 34), fill=col)
        d.text((W - 64 - 260, ly + 40), f(lb["value"]), font=fnt("black", 96), fill=col)

    a, _, b = th.get("footer", "Dữ liệu mô phỏng • Không phải khuyến nghị").partition("•")
    fs = fnt("semi", 40); a, b = a.strip(), b.strip()
    wa, wb = d.textlength(a, font=fs), d.textlength(b, font=fs)
    x = (W - wa - wb - 70) / 2
    d.text((x, 1680), a, font=fs, fill=C["ink"])
    d.ellipse([x + wa + 26, 1702, x + wa + 44, 1720], fill=C["orange"])
    d.text((x + wa + 70, 1680), b, font=fs, fill=C["ink"])
    fu = fnt("xbold", 50); url = "quantik.io.vn"; uw = d.textlength(url, font=fu)
    d.text(((W - uw) / 2, 1770), url, font=fu, fill=C["ink"])
    d.line([(110, 1806), ((W - uw) / 2 - 30, 1806)], fill=C["ink"], width=3)
    d.line([((W + uw) / 2 + 30, 1806), (W - 110, 1806)], fill=C["ink"], width=3)

    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    p = out / f"thumbnail-{no:02d}.jpg"
    img.save(p, quality=95)
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--no", type=int, required=True, help="số tập trong series Học Quant cùng QuanTik")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    print(build(a.topic, a.no, a.out))
