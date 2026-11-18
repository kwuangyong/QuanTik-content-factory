"""Facebook feed posts (image 1080×1350 + post text): product + entertainment.

  python fbpost.py --spec ../episodes/fb-posts/posts.json            # all posts
  python fbpost.py --spec ../episodes/fb-posts/posts.json --only fb07

Kinds: meme · er (expectation/reality with a model chart) · poll · quiz · stat (model number + chart) · hottake
       · screener (mock "Quét toàn sàn", fake tickers) · quant (mock "Phân tích Quant", fake ticker + 3D) · feature.
Numbers in text use {key} placeholders from a model (field "topic"), or allowed_literals (product facts in
brand/identity.md). Post text goes through the banned-phrase check and always ends with the disclaimer.
Output: social-output/fb-posts/<id>/post.jpg + post.md, and social-output/fb-posts/ALL.md for copy-paste.
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "qa"))

import frames as F  # noqa: E402
from core import DEFAULT_OUT, THEME as T, disclaimer, fill, fmt_vi, load_json  # noqa: E402
from models import Model  # noqa: E402
import check_banned, check_numbers  # noqa: E402

W, H = 1080, 1350
X0, X1 = 70, 1010
FAKE = ["QTA", "QTB", "QTC", "QTD", "QTE", "QTV", "QTX", "QTM", "QTN", "QTS", "QTR", "QTL"]


@lru_cache(maxsize=2)
def _bg():
    img = Image.new("RGB", (W, H), T["bg"])
    d = ImageDraw.Draw(img)
    for x in range(0, W, 60):
        d.line([(x, 0), (x, H)], fill=(14, 22, 18))
    for y in range(0, H, 60):
        d.line([(0, y), (W, y)], fill=(14, 22, 18))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse([-300, -400, 900, 600], fill=40)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    img.paste(Image.new("RGB", (W, H), T["accent"]), (0, 0), glow.point(lambda v: v // 3))
    return img


def canvas(tag):
    img = _bg().copy()
    d = ImageDraw.Draw(img)
    img.paste(F.logo(64), (X0, 50), F.logo(64))
    d.text((X0 + 80, 56), "QuanTik", font=F.font("sans-bold", 34), fill=T["text"])
    d.text((X0 + 80, 94), "quant cho cổ phiếu Việt Nam", font=F.font("sans", 18), fill=T["muted"])
    f = F.font("mono-bold", 24); tw = d.textlength(tag, font=f)
    d.rounded_rectangle([X1 - tw - 36, 62, X1, 106], radius=22, outline=T["accent"], width=2, fill=(30, 22, 16))
    d.text((X1 - tw - 18, 70), tag, font=f, fill=T["accent"])
    return img


def footer(img, note="Nội dung giáo dục, không phải khuyến nghị"):
    d = ImageDraw.Draw(img)
    d.line([(X0, H - 96), (X1, H - 96)], fill=T["border"], width=2)
    d.text((X0, H - 76), "quantik.io.vn", font=F.font("mono-bold", 28), fill=T["accent"])
    f = F.font("sans", 20); tw = d.textlength(note, font=f)
    d.text((X1 - tw, H - 70), note, font=f, fill=T["muted"])


def chart(model, w, h, title=None):
    return F.chart_img(model, w, h, title=title)


# ------------------------------------------------------------------ kinds
def k_meme(img, p, m):
    F.text_box(img, p["setup"], (X0, 170, X1, 500), "sans-black", 66, T["muted"], "left", "middle", label="setup")
    F.panel(img, (X0, 540, X1, 960), fill=(30, 22, 16), outline=T["accent"])
    F.text_box(img, p["punch"], (X0 + 40, 570, X1 - 40, 930), "sans-black", 72, T["text"], "left", "middle", min_size=36,
               label="punch", hl_numbers=True)
    if p.get("truth"):
        F.chip(img, (X0, 1000), p.get("truth_chip", "Nhưng đúng toán"), T["accent"], 26)
        F.text_box(img, p["truth"], (X0, 1060, X1, H - 120), "sans-bold", 40, T["neutral"], label="truth", hl_numbers=True)


def k_er(img, p, m):
    F.chip(img, (X0, 160), "KỲ VỌNG", T["positive"], 30)
    F.text_box(img, p["setup"], (X0, 225, X1, 330), "sans-black", 50, T["text"], label="setup")
    fig = F.plt.figure(figsize=(9.4, 2.6)); ax = fig.add_axes([0.04, 0.1, 0.92, 0.8])
    x = np.linspace(0, 1, 100); ax.plot(x, 100 + 30 * x, color=F.hex_(T["positive"]), lw=5); ax.set_xticks([]); ax.set_yticks([])
    F.paste(img, F.fig_to_img(fig), (X0, 340))
    F.chip(img, (X0, 630), "THỰC TẾ", T["negative"], 30)
    F.text_box(img, p["punch"], (X0, 695, X1, 790), "sans-black", 48, T["accent"], label="punch", hl_numbers=True)
    F.paste(img, chart(m, X1 - X0, 420), (X0, 800))


def k_poll(img, p, m):
    F.text_box(img, p["question"], (X0, 170, X1, 600), "sans-black", 74, T["text"], "left", "middle", min_size=40,
               label="question", hl_numbers=True)
    for i, (opt, col) in enumerate(zip(p["options"], (T["positive"], T["negative"]))):
        y = 650 + i * 270
        F.panel(img, (X0, y, X1, y + 240), fill=(int(col[0] * .14), int(col[1] * .14), int(col[2] * .14)), outline=col)
        F.text_box(img, "AB"[i], (X0 + 30, y + 40, X0 + 150, y + 200), "sans-black", 120, col, "center", "middle", label=f"opt{i}l")
        F.text_box(img, opt, (X0 + 180, y + 30, X1 - 30, y + 210), "sans-bold", 50, T["text"], "left", "middle", min_size=30,
                   label=f"opt{i}", hl_numbers=True)
    F.text_box(img, p.get("cta_line", "Bình luận A hoặc B. Lý do càng gắt càng tốt."), (X0, 1195, X1, 1245), "sans-bold", 34,
               T["neutral"], "center", label="poll-cta")


def k_quiz(img, p, m):
    F.chip(img, (X0, 160), p.get("chip", "ĐỐ VUI XÁC SUẤT"), T["accent"], 28)
    F.text_box(img, p["question"], (X0, 230, X1, 640), "sans-black", 60, T["text"], "left", "middle", min_size=34,
               label="question", hl_numbers=True)
    for i, opt in enumerate(p["options"]):
        y = 680 + i * 125
        F.panel(img, (X0, y, X1, y + 105), fill=T["surface"])
        F.text_box(img, f"{'ABCD'[i]}.  {opt}", (X0 + 30, y + 10, X1 - 30, y + 95), "sans-bold", 42, T["text"], "left", "middle",
                   min_size=26, label=f"q{i}", hl_numbers=True)
    F.text_box(img, p.get("cta_line", "Đáp án và code chứng minh: bình luận đầu tiên"), (X0, 1190, X1, 1240), "sans-bold", 32,
               T["neutral"], "center", label="quiz-cta")


def k_stat(img, p, m):
    F.text_box(img, p["big"], (X0, 160, X1, 400), "mono-bold", 190, T["accent"], "left", "middle", min_size=80, label="big")
    F.text_box(img, p["line"], (X0, 410, X1, 600), "sans-black", 50, T["text"], "left", "top", min_size=30, label="line",
               hl_numbers=True)
    F.paste(img, chart(m, X1 - X0, 560, title=p.get("chart_title")), (X0, 620))


def k_hottake(img, p, m):
    F.chip(img, (X0, 170), p.get("chip", "HOT TAKE"), T["negative"], 30)
    F.text_box(img, p["take"], (X0, 260, X1, 900), "sans-black", 92, T["text"], "left", "middle", min_size=44, label="take",
               hl_numbers=True)
    F.ImageDraw.Draw(img).rectangle([X0, 930, X0 + 300, 942], fill=T["negative"])
    F.text_box(img, p.get("sub", ""), (X0, 980, X1, 1180), "sans-bold", 40, T["muted"], label="sub", hl_numbers=True)
    F.text_box(img, p.get("cta_line", "Đồng ý hay phản đối? Cãi nhau văn minh dưới bình luận."), (X0, 1190, X1, 1240), "sans-bold",
               32, T["neutral"], "center", label="ht-cta")


def _rows(seed, n=10):
    rng = np.random.default_rng(seed)
    names = list(rng.permutation(FAKE))[:n]
    score = np.concatenate([np.sort(rng.uniform(72, 96, n // 2))[::-1], np.sort(rng.uniform(8, 38, n - n // 2))[::-1]])
    return list(zip(names, score))


def k_screener(img, p, m):
    d = ImageDraw.Draw(img)
    F.text_box(img, p["headline"], (X0, 150, X1, 330), "sans-black", 56, T["text"], "left", "middle", min_size=32,
               label="headline", hl_numbers=True)
    F.panel(img, (X0, 350, X1, 1150), fill=T["surface"])
    d.rectangle([X0 + 2, 352, X1 - 2, 410], fill=T["raised"])
    d.text((X0 + 26, 364), "Quét toàn sàn · bản screening mới nhất", font=F.font("sans-bold", 28), fill=T["text"])
    rows = _rows(p.get("seed", 1))
    top, low = rows[:5], rows[-5:]
    for blk, (label, items, col) in enumerate((("5 mã điểm cao nhất", top, T["positive"]), ("5 mã xếp hạng thấp nhất", low, T["negative"]))):
        y = 425 + blk * 340
        d.text((X0 + 26, y), label, font=F.font("sans-bold", 28), fill=col)
        for i, (nm, sc) in enumerate(items):
            yy = y + 46 + i * 56
            d.rounded_rectangle([X0 + 20, yy, X1 - 20, yy + 50], radius=10, fill=(18, 32, 25))
            d.text((X0 + 40, yy + 9), nm, font=F.font("mono-bold", 30), fill=T["text"])
            bw = (X1 - X0 - 380) * sc / 100
            d.rounded_rectangle([X0 + 200, yy + 16, X0 + 200 + bw, yy + 34], radius=8, fill=col)
            d.text((X1 - 120, yy + 9), fmt_vi(sc, "num1"), font=F.font("mono-bold", 28), fill=T["neutral"])
    d.text((X0 + 26, 1118), "Minh hoạ giao diện · mã giả lập, không phải mã thật", font=F.font("sans", 20), fill=T["muted"])
    F.text_box(img, p.get("sub", ""), (X0, 1165, X1, 1245), "sans-bold", 32, T["neutral"], label="sub", hl_numbers=True)


def k_quant(img, p, m):
    d = ImageDraw.Draw(img)
    F.text_box(img, p["headline"], (X0, 150, X1, 320), "sans-black", 54, T["text"], "left", "middle", min_size=30,
               label="headline", hl_numbers=True)
    F.panel(img, (X0, 340, X1, 1150), fill=T["surface"])
    d.text((X0 + 30, 365), p.get("ticker", "QTA"), font=F.font("mono-bold", 54), fill=T["accent"])
    d.text((X0 + 200, 382), "Phân tích Quant · mã giả lập", font=F.font("sans-bold", 26), fill=T["muted"])
    surf = F.surface_img(m, -55, 26, 520, 470)
    F.paste(img, surf, (X1 - 540, 440))
    rows = p.get("rows", [["Kết luận", "dễ đọc, 1 câu"], ["Xu hướng", "theo trạng thái"], ["Vùng giá", "mô phỏng"],
                          ["Rủi ro", "GARCH · VaR"], ["Chuyên sâu", "16 nhóm chỉ tiêu"]])
    for i, (k, v) in enumerate(rows):
        y = 460 + i * 92
        d.text((X0 + 30, y), k, font=F.font("sans", 24), fill=T["muted"])
        F.text_box(img, v, (X0 + 30, y + 30, X1 - 560, y + 80), "sans-bold", 30, T["text"], label=f"qrow{i}")
    d.text((X0 + 30, 1110), "Minh hoạ giao diện · dữ liệu mô phỏng", font=F.font("sans", 20), fill=T["muted"])
    F.text_box(img, p.get("sub", ""), (X0, 1165, X1, 1245), "sans-bold", 32, T["neutral"], label="sub", hl_numbers=True)


def k_feature(img, p, m):
    F.text_box(img, p["headline"], (X0, 160, X1, 430), "sans-black", 66, T["text"], "left", "middle", min_size=36,
               label="headline", hl_numbers=True)
    for i, item in enumerate(p["items"]):
        y = 470 + i * 150
        F.panel(img, (X0, y, X1, y + 130), fill=T["surface"])
        F.text_box(img, f"{i + 1:02d}", (X0 + 24, y + 20, X0 + 140, y + 110), "mono-bold", 54, T["accent"], "center", "middle",
                   label=f"fi{i}n")
        F.text_box(img, item, (X0 + 160, y + 15, X1 - 24, y + 115), "sans-bold", 38, T["text"], "left", "middle", min_size=24,
                   label=f"fi{i}", hl_numbers=True)


KINDS = {"meme": k_meme, "er": k_er, "poll": k_poll, "quiz": k_quiz, "stat": k_stat, "hottake": k_hottake,
         "screener": k_screener, "quant": k_quant, "feature": k_feature}
TEXT_FIELDS = ("setup", "punch", "truth", "question", "options", "big", "line", "take", "sub", "headline", "items", "rows",
               "cta_line", "chart_title")


def _fill_obj(o, v, fm, rendered):
    if isinstance(o, str):
        return fill(o, v, fm, rendered)
    if isinstance(o, list):
        return [_fill_obj(x, v, fm, rendered) for x in o]
    return o


def make(p, out_root, disc):
    m = Model(p["topic"]) if p.get("topic") else None
    vals, fmts = (m.values, m.formats) if m else ({}, {})
    rendered = set()
    q = dict(p)
    for k in TEXT_FIELDS + ("text",):
        if k in q:
            q[k] = _fill_obj(q[k], vals, fmts, rendered)
    out = Path(out_root) / p["id"]
    out.mkdir(parents=True, exist_ok=True)
    img = canvas(p.get("tag", "QuanTik"))
    KINDS[p["kind"]](img, q, m)
    footer(img, "Dữ liệu mô phỏng · giáo dục, không phải khuyến nghị" if m else "Nội dung giáo dục, không phải khuyến nghị")
    img.save(out / "post.jpg", quality=92)
    tags = " ".join("#" + h for h in p.get("hashtags", []) + ["QuanTik"])
    text = q["text"].strip() + f"\n\n👉 {p.get('link', 'quantik.io.vn')}\n\n{tags}\n\n{disc}"
    corpus = [text] + [x for k in TEXT_FIELDS if k in q for x in (q[k] if isinstance(q[k], list) else [q[k]])
                       if isinstance(x, str)] + [y for r in q.get("rows", []) if isinstance(r, list) for y in r]
    nums = check_numbers.check(corpus, vals, fmts, rendered, p.get("allowed_literals", []) + ["30", "2"], {})
    banned = check_banned.check(corpus)
    ok = not nums["fail"] and not banned["fail"]
    (out / "post.md").write_text(f"# {p['id']} · {p.get('title', '')}\n\nẢnh: post.jpg (1080×1350)\n\n"
                                 f"QA: {'ĐẠT' if ok else 'KHÔNG ĐẠT'} · số {nums['unsourced']} · cụm cấm {banned.get('hits', banned)}\n\n"
                                 f"```text\n{text}\n```\n", encoding="utf-8")
    return {"id": p["id"], "ok": ok, "title": p.get("title", ""), "text": text, "kind": p["kind"],
            "nums": nums["unsourced"], "banned": banned}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True); ap.add_argument("--only", default="")
    ap.add_argument("--out", default=str(DEFAULT_OUT / "fb-posts"))
    a = ap.parse_args()
    posts = load_json(a.spec)
    disc = disclaimer()
    res = [make(p, a.out, disc) for p in posts if not a.only or p["id"].startswith(a.only)]
    lines = ["# 50 bài Facebook — QuanTik\n"]
    for r in res:
        lines.append(f"## {r['id']} · {r['title']}  ({r['kind']}, QA {'ĐẠT' if r['ok'] else 'KHÔNG ĐẠT'})\n\n"
                     f"Ảnh: `social-output/fb-posts/{r['id']}/post.jpg`\n\n```text\n{r['text']}\n```\n")
    if not a.only:
        (Path(a.out) / "ALL.md").write_text("\n".join(lines), encoding="utf-8")
    bad = [(r["id"], r["nums"], r["banned"]) for r in res if not r["ok"]]
    print(json.dumps({"n": len(res), "fail": bad}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
