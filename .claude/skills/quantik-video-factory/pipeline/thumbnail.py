"""Ảnh bìa (thumbnail) 1080x1920 có đánh số tập series "Học Quant cùng QuanTik #N".

    python thumbnail.py --topic sortino --no 4 --out ../../../../social-output/sortino-myth-buster

Mọi số trên ảnh lấy từ model (placeholder {key}), như video. Nội dung chính nằm trong dải giữa
(y 280..1640) để không bị cắt khi TikTok/Reels hiện lưới 3:4 trên trang cá nhân.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import ImageDraw

import frames as F
from core import THEME as T, W, fill, font, load_model_kb
from models import Model

SERIES = "Học Quant cùng QuanTik"


def stat_card(img, box, label, value, color):
    F.panel(img, box, fill=(16, 26, 21), outline=color)
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.text((x0 + 32, y0 + 26), label, font=font("sans-bold", 34), fill=T["muted"])
    F.text_box(img, value, (x0 + 32, y0 + 78, x1 - 32, y1 - 20), "sans-bold", 76, color, label="thumb-stat")


def build(topic, no, out, title=None, question=None):
    m = Model(topic)
    kb = load_model_kb(topic)
    vd = kb["video_defaults"] if isinstance(kb, dict) and "video_defaults" in kb else kb
    th = vd.get("thumb", {})
    f = lambda s: fill(s, m.values, m.formats)
    img = F.base()
    d = ImageDraw.Draw(img)

    # Dải series + số tập
    img.paste(F.logo(84), (60, 120), F.logo(84))
    d.text((164, 128), SERIES, font=font("sans-bold", 40), fill=T["text"])
    d.text((164, 178), "quantik.io.vn", font=font("sans", 26), fill=T["muted"])
    badge = f"#{no}"
    fb = font("sans-bold", 92)
    bw = d.textlength(badge, font=fb)
    d.rounded_rectangle([W - 60 - bw - 56, 104, W - 60, 228], radius=30, fill=T["accent"])
    d.text((W - 60 - bw - 28, 112), badge, font=fb, fill=T["bg"])

    # Tiêu đề lớn + câu hỏi
    F.text_box(img, title or th.get("title", vd.get("kicker", topic)).upper(), (60, 300, W - 60, 520),
               "sans-bold", 170, T["accent"], label="thumb-title", max_lines=1)
    F.text_box(img, f(question or th.get("question", vd["hook"])), (60, 530, W - 60, 800),
               "sans-bold", 76, T["text"], label="thumb-q", max_lines=3)

    # Chart thật của mô hình
    fig = F.plt.figure(figsize=(9.6, 5.6))
    ax = fig.add_axes([0.04, 0.2, 0.92, 0.78])
    m.plot2d(ax)
    ch = F.fit_width(F.fig_to_img(fig), W - 120)
    F.paste(img, ch, (60, 770))

    # Thẻ số
    cards = th.get("cards", [])
    if cards:
        y0 = 770 + ch.height + 30
        cw = (W - 120 - 30) // len(cards)
        cols = [T["positive"], T["negative"], T["accent"]]
        for i, c in enumerate(cards):
            x0 = 60 + i * (cw + 30)
            stat_card(img, (x0, y0, x0 + cw, y0 + 220), f(c["label"]), f(c["value"]), cols[i % 3])

    y_foot = (770 + ch.height + 30 + 220 + 30) if cards else 1700
    d.text((60, y_foot), "Dữ liệu mô phỏng · giáo dục, không phải khuyến nghị", font=font("sans", 26), fill=T["muted"])
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    p = out / f"thumbnail-{no:02d}.jpg"
    img.convert("RGB").save(p, quality=95)
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--no", type=int, required=True, help="số tập trong series")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title"); ap.add_argument("--question")
    a = ap.parse_args()
    print(build(a.topic, a.no, a.out, a.title, a.question))
