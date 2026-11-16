"""Facebook posts (1080×1350, 4:5): humorous comic strips about trading life, product-feature carousels, and the
weekly market thermometer. Same brand, compliance and QA rules as the videos (platforms/facebook/README.md).

    python post.py comic    ../posts/fb-comic-vo-hoi-lai.json
    python post.py carousel ../posts/fb-carousel-quet-san.json [--shots <dir of UI screenshots>]
                     (UI screenshots: posts/shots/ — mã bịa, API giả — refresh with tutorial/capture)
    python post.py market   [BUNDLE]          # latest social-output/_market/bundle-* by default
    python post.py all                        # every JSON in ../posts + the market post

Output: social-output/<id>/post-01.png … , captions.md (Facebook), qa_report.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

from PIL import Image, ImageDraw  # noqa: E402

import core as C  # noqa: E402
import frames as F  # noqa: E402
import figures as G  # noqa: E402
import illustrations as ILL  # noqa: E402
import check_banned  # noqa: E402
import check_numbers  # noqa: E402
from core import DEFAULT_OUT, THEME as T, disclaimer, fill, load_json  # noqa: E402

PW, PH = 1080, 1350
M = 60                       # outer margin
POSTS = HERE.parent / "posts"
INK = (24, 30, 27)
PAPER = (246, 242, 233)


# ---------------------------------------------------------------- shared frame
def canvas():
    img = Image.new("RGB", (PW, PH), T["bg"])
    d = ImageDraw.Draw(img)
    for x in range(0, PW, 60):
        d.line([(x, 0), (x, PH)], fill=(14, 22, 18))
    for y in range(0, PH, 60):
        d.line([(0, y), (PW, y)], fill=(14, 22, 18))
    return img


def header(img, tag):
    d = ImageDraw.Draw(img)
    lg = F.logo(56)
    img.paste(lg, (M, 34), lg)
    d.text((M + 70, 36), "QuanTik", font=F.font("sans-bold", 30), fill=T["text"])
    d.text((M + 70, 72), "quant cho cổ phiếu Việt Nam", font=F.font("sans", 16), fill=T["muted"])
    f = F.font("mono-bold", 22)
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle([PW - M - tw - 32, 42, PW - M, 82], radius=20, outline=T["accent"], width=2, fill=(30, 22, 16))
    d.text((PW - M - tw - 16, 50), tag, font=f, fill=T["accent"])


def footer(img, extra=""):
    text = (extra + " · " if extra else "") + disclaimer()
    F.text_box(img, text, (M, PH - 92, PW - M, PH - 24), "sans", 17, T["muted"], "left", "middle", min_size=13,
               label="footer")


def plain(s):
    """Drop emoji / pictographs for rendering (the brand fonts have none); captions keep them."""
    import re
    return re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]", "", s or "").replace("  ", " ").strip()


def text(img, s, box, kind="sans-bold", size=40, color=None, align="left", valign="top", min_size=22, label="t"):
    s = plain(s)
    F.text_box(img, s, box, kind, size, color or T["text"], align, valign, min_size=min_size, label=label)


def bubble(img, s, box, tail_x, tail_y, label):
    """Comic speech bubble with a tail pointing at (tail_x, tail_y)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    tx = max(x0 + 30, min(x1 - 30, tail_x))
    d.polygon([(tx - 18, y1 - 4), (tx + 18, y1 - 4), (tail_x, tail_y)], fill=PAPER, outline=INK)
    d.rounded_rectangle(box, radius=26, fill=PAPER, outline=INK, width=3)
    d.line([(tx - 16, y1 - 2), (tx + 16, y1 - 2)], fill=PAPER, width=4)
    F.text_box(img, plain(s), (x0 + 18, y0 + 12, x1 - 18, y1 - 12), "sans-bold", 30, INK, "center", "middle", min_size=17,
               label=label)


# ---------------------------------------------------------------- comic
def _panels_layout(n, top, bottom):
    gap = 22
    if n == 4:
        w, h = (PW - 2 * M - gap) // 2, (bottom - top - gap) // 2
        return [(M + (i % 2) * (w + gap), top + (i // 2) * (h + gap), w, h) for i in range(4)]
    h = (bottom - top - gap * (n - 1)) // n
    return [(M, top + i * (h + gap), PW - 2 * M, h) for i in range(n)]


def comic(post):
    """Panels of characters (figures.py) with speech bubbles; title on top, optional punchline under the strip."""
    img = canvas()
    header(img, post.get("tag", "CHUYỆN NGHỀ"))
    text(img, post["title"], (M, 118, PW - M, 196), "sans-black", 50, valign="middle", min_size=30, label="title")
    bottom = PH - 110 - (90 if post.get("punchline") else 0)
    panels = post["panels"][:4]
    for i, (pn, (x, y, w, h)) in enumerate(zip(panels, _panels_layout(len(panels), 214, bottom))):
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([x, y, x + w, y + h], radius=22, fill=(26, 40, 33), outline=T["border"], width=3)
        cap_h = 0
        if pn.get("caption"):
            F.chip(img, (x + 16, y + 14), pn["caption"], T["neutral"], 20)
            cap_h = 44
        spec = ILL.stage_spec(pn["stage"])
        sh = int(h * 0.58)
        stage = G.stage(spec, w - 24, sh, 1.0, 1.0)
        img.paste(stage, (x + 12, y + h - sh - 10), stage)
        cast = spec.get("cast", [])
        bubbles = pn.get("bubbles", [])
        for j, b in enumerate(bubbles):
            who = cast[min(b.get("who", j), len(cast) - 1)] if cast else {"x": 0.5}
            cx = x + 12 + int((w - 24) * who.get("x", 0.5))
            bw = min(w - 32, int(w * (0.62 if len(bubbles) > 1 else 0.86)))
            bx0 = max(x + 16, min(x + w - 16 - bw, cx - bw // 2))
            if len(bubbles) > 1:  # two speakers: stagger vertically so tails don't cross
                by0 = y + 16 + cap_h + j * int((h - sh - cap_h) * 0.42)
            else:
                by0 = y + 16 + cap_h
            bh = max(70, min(150, int((h - sh - cap_h) * (0.52 if len(bubbles) > 1 else 0.8))))
            bubble(img, b["text"], (bx0, by0, bx0 + bw, by0 + bh), cx, y + h - sh + 16, f"p{i}-b{j}")
    if post.get("punchline"):
        text(img, post["punchline"], (M, bottom + 18, PW - M, bottom + 88), "sans-black", 36, T["accent"],
             valign="middle", min_size=22, label="punchline")
    footer(img, "Nhân vật minh hoạ")
    return [img], _texts(post)


# ---------------------------------------------------------------- product carousel
def _device(shot, w, h):
    """Phone frame with a real UI screenshot (mã bịa, API giả) inside."""
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=48, fill=(12, 14, 13, 255), outline=(70, 80, 75, 255), width=4)
    im = Image.open(shot).convert("RGB")
    sw, sh = w - 28, h - 28
    s = sw / im.width
    im = im.resize((sw, int(im.height * s)), Image.LANCZOS)
    im = im.crop((0, 0, sw, min(sh, im.height)))
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=36, fill=255)
    out.paste(im, (14, 14), mask)
    return out


def carousel(post, shots_dir=None):
    shots_dir = Path(shots_dir) if shots_dir else None
    slides, missing = [], []
    n = len(post["slides"])
    for i, sl in enumerate(post["slides"]):
        img = canvas()
        header(img, post.get("tag", "TÍNH NĂNG"))
        F.chip(img, (M, 116), f"{i + 1}/{n}", T["accent"], 22)
        text(img, sl["title"], (M, 162, PW - M, 262), "sans-black", 50, valign="middle", min_size=30, label=f"s{i}-title")
        shot = None
        if sl.get("shot"):
            for base in [p for p in (shots_dir, POSTS / "shots", POSTS) if p]:
                if (base / sl["shot"]).exists():
                    shot = base / sl["shot"]
                    break
        body_top = 1100
        if shot:
            dev = _device(shot, 480, 800)
            img.paste(dev, (PW - M - dev.width - (0 if sl.get("stage") else 240), 280), dev)
        elif sl.get("shot"):
            missing.append(sl["shot"])
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([PW - M - 480, 280, PW - M, 1080], radius=48, outline=T["negative"], width=4)
            text(img, f"THIẾU ẢNH GIAO DIỆN\n{sl['shot']}\n(chạy tutorial/capture)", (PW - M - 410, 560, PW - M - 20, 760),
                 "sans-bold", 28, T["negative"], "center", "middle", label=f"s{i}-missing")
        if sl.get("stage"):
            st = G.stage(ILL.stage_spec(sl["stage"]), 470 if sl.get("shot") else PW - 2 * M, 700, 1.0, 1.0)
            img.paste(st, (M - 10, 380), st)
        elif not sl.get("shot") and sl.get("art"):
            fr = ILL.frame(sl["art"], 0.8).resize((PW - 2 * M, int((PW - 2 * M) * 780 / 1080)))
            img.paste(fr, (M, 300), fr)
        text(img, sl["body"], (M, body_top, PW - M, PH - 110), "sans-bold", 36, T["text"], valign="top", min_size=22,
             label=f"s{i}-body")
        footer(img, "Mã cổ phiếu trong ảnh là mã minh hoạ" if sl.get("shot") else "")
        slides.append(img)
    return slides, _texts(post), missing


# ---------------------------------------------------------------- market thermometer
def _market_values(rep):
    vals, fmts = {}, {}
    for group in ("observed", "model"):
        for k, v in (rep.get(group) or {}).items():
            if isinstance(v, dict) and "value" in v:
                vals[k], fmts[k] = v["value"], v.get("fmt", "num2")
            else:
                vals[k] = v
    return vals, fmts


def _thresholds():
    from market.editorial import THRESHOLDS
    return list(THRESHOLDS)


def market(bundle):
    bundle = Path(bundle)
    rep = load_json(bundle / "market_report.json")
    ed = load_json(bundle / "market_editorial.json")
    vals, fmts = _market_values(rep)
    rendered = set()

    def f(s):
        return fill(s, vals, fmts, rendered)

    y_, m_, d_ = str(rep["as_of"])[:10].split("-")
    day = f"{d_}/{m_}/{y_}"  # session date comes from the data bundle (as_of), declared as a sourced literal below
    img = canvas()
    header(img, "NHIỆT KẾ THỊ TRƯỜNG")
    status = "trong phiên" if rep.get("data_status") == "intraday" else rep.get("data_status", "")
    text(img, f"Phiên {day} · {status}", (M, 112, PW - M, 150), "sans", 24, T["muted"], label="asof")
    # big index line
    chg = vals.get("vnindex_chg", 0) or 0
    col = T["positive"] if chg >= 0 else T["negative"]
    text(img, f("VN-INDEX {vnindex}"), (M, 156, PW - M, 236), "sans-black", 62, valign="middle", label="vnindex")
    text(img, f("{vnindex_pts} điểm ({vnindex_chg})"), (M, 236, PW - M, 280), "sans-bold", 34, col, label="vnchg")
    # stat tiles
    tiles = [("Độ rộng HOSE", f("{breadth_pct}"), f("{adv} tăng · {dec} giảm")),
             ("Khối ngoại", f("{foreign_net_abs_bn:num0} tỷ"), str(vals.get("foreign_side", ""))),
             ("Top 10 mã lớn", f("{top10_share}"), "tỷ trọng giá trị khớp")]
    tw = (PW - 2 * M - 2 * 20) // 3
    for i, (lab, big, sub) in enumerate(tiles):
        x = M + i * (tw + 20)
        ImageDraw.Draw(img).rounded_rectangle([x, 300, x + tw, 470], radius=20, fill=T["raised"], outline=T["border"], width=2)
        text(img, lab, (x + 18, 314, x + tw - 18, 346), "sans", 22, T["muted"], label=f"tile{i}-l")
        text(img, big, (x + 18, 350, x + tw - 18, 414), "sans-black", 46, T["accent"], valign="middle", min_size=26, label=f"tile{i}-b")
        text(img, sub, (x + 18, 418, x + tw - 18, 458), "sans", 20, T["text"], min_size=14, label=f"tile{i}-s")
    # one reading line
    interp = ed["interpretations"][0]["text"] if ed.get("interpretations") else ""
    text(img, f(interp), (M, 490, PW - M, 580), "sans-bold", 30, T["text"], min_size=20, label="interp")
    # three scenarios
    names = {"bull": ("KỊCH BẢN TÍCH CỰC", T["positive"]), "base": ("KỊCH BẢN CƠ SỞ", T["neutral"]),
             "bear": ("KỊCH BẢN TIÊU CỰC", T["negative"])}
    y = 600
    for i, sc in enumerate(ed["scenarios"]):
        lab, c = names.get(sc["name"], (sc["name"], T["text"]))
        ImageDraw.Draw(img).rounded_rectangle([M, y, PW - M, y + 196], radius=20, fill=(20, 32, 26), outline=c, width=3)
        F.chip(img, (M + 18, y + 14), lab, c, 20)
        text(img, f(sc["description"]), (M + 18, y + 52, PW - M - 18, y + 92), "sans-bold", 26, min_size=18, label=f"sc{i}-d")
        text(img, "Xác nhận: " + f("; ".join(sc["confirmation"])), (M + 18, y + 94, PW - M - 18, y + 128), "sans", 21,
             T["text"], min_size=15, label=f"sc{i}-c")
        text(img, "Vô hiệu: " + f("; ".join(sc["invalidation"])), (M + 18, y + 128, PW - M - 18, y + 160), "sans", 21,
             T["muted"], min_size=15, label=f"sc{i}-i")
        text(img, "Quản trị rủi ro: " + f("; ".join(sc.get("investor_actions", []))), (M + 18, y + 160, PW - M - 18, y + 192),
             "sans", 21, c, min_size=15, label=f"sc{i}-a")
        y += 210
    text(img, "Ba kịch bản là điều kiện để theo dõi, không phải dự báo. Không nêu mã, không khuyến nghị mua bán.",
         (M, y, PW - M, y + 40), "sans", 20, T["muted"], min_size=14, label="note")
    footer(img, "Dữ liệu: AGR datafeed")
    texts = [interp] + [x for sc in ed["scenarios"] for x in [sc["description"]] + sc["confirmation"] + sc["invalidation"]
                        + sc.get("investor_actions", [])]
    texts = [f(t) for t in texts]
    post = {"id": f"fb-market-{rep['as_of']}", "type": "market",
            "caption": f(f"Nhịp thị trường phiên {day}: VN-INDEX {{vnindex}} ({{vnindex_chg}}), độ rộng "
                         f"{{breadth_pct}}, khối ngoại {vals.get('foreign_side', '')} {{foreign_net_abs_bn:num0}} tỷ. "
                         f"Ba kịch bản để theo dõi tuần này trong ảnh."),
            "link_line": "Muốn xem từng mã theo cùng bộ chỉ tiêu: Phân tích Quant tại quantik.io.vn",
            "hashtags": ["nhipthitruong", "vnindex", "chungkhoan", "quant", "QuanTik"],
            # fixed rule thresholds of the scenario engine (declared in market/editorial.py), as the video does
            "allowed_literals": _thresholds() + [day, d_, m_, y_]}
    return [img], texts, post, vals, fmts, rendered


# ---------------------------------------------------------------- QA + output
def _texts(post):
    out = [post.get("title", ""), post.get("punchline", ""), post.get("caption", "")]
    for pn in post.get("panels", []):
        out += [pn.get("caption", "")] + [b["text"] for b in pn.get("bubbles", [])]
    for sl in post.get("slides", []):
        out += [sl.get("title", ""), sl.get("body", "")]
    return [t for t in out if t]


def captions(post):
    tags = " ".join("#" + h.lstrip("#") for h in post.get("hashtags", []))
    link = post.get("link_line", "")
    body = post.get("caption", "")
    return (f"# Caption — {post['id']} (Facebook post)\n\n## Facebook\n{body}\n\n"
            + (f"👉 {link}\n\n" if link else "") + f"{tags}\n\n{disclaimer()}\n")


def write(post, images, texts, out_root=DEFAULT_OUT, values=None, formats=None, rendered=None, missing=()):
    out = Path(out_root) / post["id"]
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("post-*.png"):
        old.unlink()
    F.LAYOUT.__init__()
    files = []
    for i, im in enumerate(images, 1):
        p = out / f"post-{i:02d}.png"
        im.save(p)
        files.append(p)
    corpus = texts + [post.get("caption", ""), post.get("link_line", "")]
    banned = check_banned.check(corpus)
    nums = check_numbers.check(corpus, values or {}, formats or {}, rendered or set(), post.get("allowed_literals", []),
                               post.get("facts", {}))
    issues = []
    if missing:
        issues.append("thiếu ảnh giao diện thật: " + ", ".join(missing) + " — không đăng bản này")
    ok = not (banned["fail"] or nums["fail"] or issues)
    cap = captions(post)
    (out / "captions.md").write_text(cap, encoding="utf-8")
    lines = [f"# Phiếu QA — {post['id']} (post Facebook, {post['type']})", "", f"- **Kết luận: {'ĐẠT' if ok else 'KHÔNG ĐẠT'}**",
             f"- Ảnh: {len(files)} × {PW}×{PH}", f"- Cụm cấm: {'ĐẠT' if not banned['fail'] else 'KHÔNG ĐẠT ' + str(banned['hits'][:3])}",
             f"- Số có nguồn: {'ĐẠT' if not nums['fail'] else 'KHÔNG ĐẠT ' + str(nums['unsourced'][:3])}"]
    lines += [f"- {x}" for x in issues]
    lines += ["", "## Người duyệt", "- [ ] Đọc to câu đùa: hài về tình huống, không chế giễu người thua lỗ",
              "- [ ] Không có mã thật, không gọi mua/bán; giá gói (nếu nhắc) khớp /plans"]
    (out / "qa_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"=== {post['id']} → {out}  ({len(files)} ảnh)  QA: {'ĐẠT' if ok else 'KHÔNG ĐẠT'}")
    if not ok:
        for x in (banned["hits"][:3] + nums["unsourced"][:3] + issues):
            print("   ✗", x)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", choices=["comic", "carousel", "market", "all"])
    ap.add_argument("src", nargs="?")
    ap.add_argument("--shots", help="folder of UI screenshots (tutorial capture output)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args()
    C.set_lang("vi")
    C.set_branding("full")
    results = []

    def run_json(path):
        post = load_json(path)
        if post["type"] == "comic":
            ims, tx = comic(post)
            results.append(write(post, ims, tx, a.out))
        elif post["type"] == "carousel":
            ims, tx, miss = carousel(post, a.shots)
            results.append(write(post, ims, tx, a.out, missing=miss))

    def run_market(src):
        if src:
            b = Path(src)
        else:
            bs = sorted((Path(DEFAULT_OUT) / "_market").glob("bundle-*"))
            if not bs:
                raise SystemExit("chưa có bundle thị trường — chạy: python pillar.py market fetch && … analyze && … editorial")
            b = bs[-1]
        ims, tx, post, v, fm, r = market(b)
        results.append(write(post, ims, tx, a.out, v, fm, r))

    if a.kind in ("comic", "carousel"):
        run_json(a.src)
    elif a.kind == "market":
        run_market(a.src)
    else:
        for p in sorted(POSTS.glob("*.json")):
            run_json(p)
        run_market(None)
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
