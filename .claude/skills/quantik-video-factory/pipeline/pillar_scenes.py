"""Scene builders for research-based pillars: every segment carries its role, claim status badge and source footer.

A pillar style (styles/bias-lab, history-story, market-brief, decision-lab) is a thin template: it names its roles,
picks a default visual per role and calls ``segment_scene``. What makes the pillars feel different is the role
sequence (pillars/registry.json), the visuals per role and the label vocabulary, not a different renderer.

Content area: y 300..1240; source footer 1258..1308; subtitles 1326..1488 (render.py).
"""
from __future__ import annotations

import json
from functools import lru_cache

import frames as F
import scenes as S
from core import KNOWLEDGE, THEME as T, fmt_vi
from render import Scene

X0, X1 = S.X0, S.X1
FOOT = (X0, 1258, X1, 1308)

STATUS_LABEL = {
    "documented": ("TƯ LIỆU", T["positive"]),
    "self_reported": ("LỜI TỰ KỂ", T["neutral"]),
    "anecdote": ("GIAI THOẠI", T["neutral"]),
    "disputed": ("CÒN TRANH CÃI", T["negative"]),
    "speculation": ("SUY ĐOÁN", T["negative"]),
    "observed": ("QUAN SÁT", T["positive"]),
    "model_output": ("MÔ HÌNH", T["accent"]),
    "interpretation": ("NHẬN ĐỊNH", T["neutral"]),
    "limitation": ("GIỚI HẠN DỮ LIỆU", T["negative"]),
}
# weakest status wins the badge: a segment mixing a fact and a guess is shown as a guess
WEAKNESS = ["speculation", "disputed", "anecdote", "self_reported", "interpretation", "model_output", "observed",
            "documented"]


@lru_cache(maxsize=1)
def ledger():
    data = json.loads((KNOWLEDGE / "sources/ledger.json").read_text(encoding="utf-8"))
    return {s["id"]: s for s in data["sources"]}


def claim_index(ep):
    return {c["id"]: c for c in ep.get("claims", [])}


def segment_status(ep, seg):
    if seg.get("label"):
        return seg["label"]
    cl = claim_index(ep)
    sts = [cl[c]["status"] for c in seg.get("claims", []) if c in cl]
    return min(sts, key=WEAKNESS.index) if sts else None


def segment_sources(ep, seg):
    cl, led, out = claim_index(ep), ledger(), []
    for c in seg.get("claims", []):
        for sid in (cl.get(c) or {}).get("source_ids", []):
            cite = led.get(sid, {}).get("cite_short", sid)
            if cite not in out:
                out.append(cite)
    return out


CREDIT = (X0, 1212, X1, 1254)


def image_entry(iid):
    import images

    return images.index().get(iid)


def credit_text(ids):
    seen = []
    for iid in ids:
        e = image_entry(iid)
        if e and e["credit"] not in seen:
            seen.append(e["credit"])
    return " · ".join(seen)


def credit_line(img, ids):
    txt = credit_text(ids)
    if txt:
        F.text_box(img, txt, CREDIT, "sans", 20, T["muted"], "left", "middle", min_size=16, label="image-credit",
                   max_lines=2)


@lru_cache(maxsize=64)
def _img_cached(iid, w, h):
    import images
    from PIL import Image

    im = Image.open(images.path_of(image_entry(iid))).convert("RGB")
    k = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)


@lru_cache(maxsize=64)
def _thumb_cached(iid, size):
    import images

    return images.avatar_thumb(image_entry(iid), size)


def footer(img, cites):
    if cites:
        F.text_box(img, "Nguồn: " + " · ".join(cites), FOOT, "sans", 22, T["muted"], "left", "middle", min_size=18,
                   label="source-footer", max_lines=2)


CHAPTER = {"i": 0, "n": 0}   # set per scene by pillar_build: where we are in the story


def chapter_dots(img, i, n, y=346):
    """Small progress dots on the badge row: done / current / to come — viewers see the structure of the story."""
    if n < 2:
        return
    d = F.ImageDraw.Draw(img)
    gap, r = 30, 8
    x = X1 - (n - 1) * gap - r
    for k in range(n):
        cx = x + k * gap
        if k < i:
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=T["muted"])
        elif k == i:
            d.ellipse([cx - r - 3, y - r - 3, cx + r + 3, y + r + 3], fill=T["accent"])
        else:
            d.ellipse([cx - r, y - r, cx + r, y + r], outline=T["border"], width=3)


def badges(img, role_label, status, y=330, chapter=None):
    x = F.chip(img, (X0, y), role_label, T["raised"], 26) + 14
    if status:
        text, col = STATUS_LABEL[status]
        F.chip(img, (x, y), text, col, 26)
    if chapter:
        chapter_dots(img, *chapter)


def _texts(role_label, status, cites, *more):
    out = [role_label, STATUS_LABEL[status][0] if status else ""]
    if cites:
        out.append("Nguồn: " + " · ".join(cites))
    return out + [m for m in more if m]


# ---------------------------------------------------------------- visuals
def ease_back(x):
    """Overshoot then settle — the 'pop' of an icon landing."""
    x = F.clamp(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def _statement(ep, seg, model, role_label, status, cites, accent=None):
    """Big text revealed word by word; with an icon the text sits on top and the pictogram pops in below and floats."""
    import math

    text = seg.get("screen") or seg["say"]
    stg = (seg.get("visual") or {}).get("scene") or seg.get("_scene")
    icon = None if stg else ((seg.get("visual") or {}).get("icon") or seg.get("_icon"))
    words = text.split()
    box = (X0, 430, X1, 760) if stg else (X0, 430, X1, 820) if icon else (X0, 430, X1, 1230)
    size = F.fit_size(text, box, "sans-black", 72 if icon else 68, 38)
    chapter = (CHAPTER["i"], CHAPTER["n"])

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        k = max(1, int(len(words) * F.ease_out(F.seg(p, 0.0, 0.35)) + 0.999))
        F.text_box(img, " ".join(words[:k]), box, "sans-black", size, accent or T["text"], "left",
                   "top" if (icon or stg) else "middle", min_size=size, label=f"{seg['role']}-text", hl_numbers=True)
        if stg:
            draw_stage(img, stg, t, p, seg["role"])
        if icon:
            import pictos

            sc = ease_back(F.seg(p, 0.12, 0.38))
            if sc > 0.02:
                bob = 10 * math.sin(2 * math.pi * t / 2.4)
                side = int(380 * max(0.05, sc))
                ic = pictos.icon(icon, 380).resize((side, side), F.Image.LANCZOS)
                F.paste(img, ic, ((X0 + X1) // 2, 1040 + bob), anchor="center")
        footer(img, cites)

    return draw, _texts(role_label, status, cites, text, ((stg or {}).get("bubble") or {}).get("text"))


STAGE_BOX = (X0, 780, X1, 1236)


def draw_stage(img, spec, t, p, name="stage", box=STAGE_BOX):
    """Characters + props (pipeline/figures.py) in the lower part of the frame, optional speech bubble on top."""
    import figures as G

    w, h = box[2] - box[0], box[3] - box[1]
    F.paste(img, G.stage(spec, w, h, t, p), (box[0], box[1]))
    bub = spec.get("bubble")
    if bub and p > 0.3:
        who = spec.get("cast", [{}])[min(bub.get("who", 0), len(spec.get("cast", [{}])) - 1)]
        cx = box[0] + int(w * who.get("x", 0.5))
        bw, bh = 400, 120
        x0 = max(box[0], min(box[2] - bw, cx - bw // 2))
        y0 = box[1] - 40
        a = F.ease_out(F.seg(p, 0.3, 0.42))
        d = F.ImageDraw.Draw(img)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=30, fill=(245, 242, 235), outline=T["accent"], width=4)
        d.polygon([(cx - 18, y0 + bh - 2), (cx + 18, y0 + bh - 2), (cx, y0 + bh + 34)], fill=(245, 242, 235))
        F.text_box(img, bub["text"], (x0 + 22, y0 + 14, x0 + bw - 22, y0 + bh - 14), "sans-black", 44, T["bg"],
                   "center", "middle", min_size=24, label=f"{name}-bubble", alpha=a)


def hook_scene(text, spec, kicker=None, min_dur=2.6):
    """Hook with a stage: words pop in on top, characters land below — a face in the first second."""
    words = text.split()
    box = (X0, 420, X1, 800)
    size = F.fit_size(text, box, "sans-black", 84, 46)

    def draw(img, t, p):
        k = max(1, int(len(words) * F.ease_out(F.seg(p, 0, 0.45)) + 0.999))
        if kicker:
            F.chip(img, (X0, 330), kicker, T["accent"], 28)
        F.text_box(img, " ".join(words[:k]), box, "sans-black", size, T["text"], "left", "top", min_size=size,
                   label="hook", hl_numbers=True)
        draw_stage(img, spec, t, min(1.0, p * 1.6), "hook")

    return Scene("hook", text, draw, min_dur, texts=[text, kicker or "", (spec.get("bubble") or {}).get("text", "")])


def _chart(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    note = seg.get("screen") or ""
    box = (X0, 420, X1, 1060 if note else 1240)
    S._MODELS[id(model)] = model

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        step = max(1, int(24 * F.ease_in_out(F.seg(p, 0, 0.7)) + 0.5))
        F.paste(img, S._chart_cached(id(model), step, 24, box[2] - box[0], box[3] - box[1],
                                     seg.get("visual", {}).get("title")), (box[0], box[1]))
        if note:
            F.text_box(img, note, (X0, 1080, X1, 1240), "sans-bold", 40, T["neutral"], "left", "top", min_size=26,
                       label=f"{seg['role']}-note", hl_numbers=True)
        footer(img, cites)

    return draw, _texts(role_label, status, cites, note, seg.get("visual", {}).get("title"))


def _surface(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    note = seg.get("screen") or ""
    S._MODELS[id(model)] = model

    def draw(img, t, p):
        e = F.ease_in_out(p)
        F.paste(img, S._surface_cached(id(model), int(-70 + 80 * e), int(30 - 8 * e), S.CW, 760), (X0, 410))
        badges(img, role_label, status, chapter=chapter)
        if note:
            F.text_box(img, note, (X0, 1170, X1, 1245), "sans-bold", 34, T["muted"], "left", "top", min_size=24,
                       label=f"{seg['role']}-note", hl_numbers=True)
        footer(img, cites)

    return draw, _texts(role_label, status, cites, note)


def _code(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    code, total = model.code, len(model.code)
    rows = _rows(seg, model)

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        n = int(total * F.ease_in_out(F.seg(p, 0, 0.6)))
        im = F.fit_width(F.code_panel(code, S.CW, chars=n if n < total else None,
                                      title=getattr(model, "code_title", "") or f"{model.topic}.py"), S.CW, 600)
        F.paste(img, im, (X0, 410))
        if rows and p > 0.6:
            k = min(len(rows), int(len(rows) * F.seg(p, 0.6, 0.9)) + 1)
            F.paste(img, F.fit_width(F.terminal_panel(rows[:k], S.CW, title="kết quả chạy"), S.CW, 1240 - 430 - im.height),
                    (X0, 430 + im.height))
        footer(img, cites)

    return draw, _texts(role_label, status, cites, *[f"{a} {b}" for a, b in rows])


def _rows(seg, model):
    return [(r["label"], fmt_vi(model.values[r["key"]], r.get("fmt") or model.formats.get(r["key"], "num2")))
            for r in seg.get("visual", {}).get("rows", [])]


def _terminal(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    rows = _rows(seg, model)
    note = seg.get("screen") or ""

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        k = min(len(rows), int(len(rows) * F.seg(p, 0.05, 0.6)) + 1)
        im = F.terminal_panel(rows[:k], S.CW, title=seg.get("visual", {}).get("title") or getattr(model, "run_title", "kết quả"))
        F.paste(img, im, (X0, 420))
        if note and p > 0.5:
            y = 420 + F.terminal_panel(rows, S.CW).height + 40
            F.text_box(img, note, (X0, y, X1, 1240), "sans-bold", 46, T["neutral"], "left", "top", min_size=28,
                       label=f"{seg['role']}-note", hl_numbers=True, alpha=F.ease_out(F.seg(p, 0.5, 0.7)))
        footer(img, cites)

    return draw, _texts(role_label, status, cites, note, *[f"{a} {b}" for a, b in rows])


def _citation(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    """Study card: who, where, what was found (the finding is `screen`, numbers only via facts/placeholders)."""
    led = ledger()
    cl = claim_index(ep)
    sid = next((s for c in seg.get("claims", []) for s in cl.get(c, {}).get("source_ids", [])), None)
    src = led.get(sid, {})
    who = src.get("cite_short", "")
    title = src.get("title", "")
    finding = seg.get("screen") or seg["say"]

    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.2))
        badges(img, role_label, status, chapter=chapter)
        F.panel(img, (X0, 420, X1, 1240), fill=T["surface"], outline=T["positive"])
        rx = X1 - (210 if pic else 36)
        F.text_box(img, who, (X0 + 36, 450, rx, 520), "mono-bold", 36, T["positive"], label="cite-who", alpha=a)
        F.text_box(img, "“" + title + "”", (X0 + 36, 530, rx, 680), "sans", 32, T["muted"], label="cite-title",
                   alpha=a, min_size=22)
        F.text_box(img, finding, (X0 + 36, 700, X1 - 36, 1190), "sans-black", 58, T["text"], "left", "top",
                   min_size=34, label="cite-finding", hl_numbers=True, alpha=F.ease_out(F.seg(p, 0.15, 0.35)))
        if pic:
            F.paste(img, _thumb_cached(pic, 150), (X1 - 186, 450), alpha=a)
        credit_line(img, [pic] if pic else [])
        footer(img, cites)

    pic = (seg.get("visual") or {}).get("image") if image_entry((seg.get("visual") or {}).get("image")) else None
    return draw, _texts(role_label, status, cites, who, title, finding, credit_text([pic] if pic else []))


def _timeline(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    """Vertical timeline of ep['timeline'] events up to and including this segment's `upto` index."""
    events = ep.get("timeline", [])
    upto = seg.get("visual", {}).get("upto", len(events) - 1)
    cl = claim_index(ep)

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        d = F.ImageDraw.Draw(img)
        shown = events[:upto + 1]
        n = max(1, len(shown))
        step = min(150, int(800 / n))
        x = X0 + 30
        d.line([(x, 440), (x, 440 + step * (n - 1) + 10)], fill=T["border"], width=6)
        for i, ev in enumerate(shown):
            y = 440 + i * step
            hot = i == upto
            a = 1.0 if not hot else F.ease_out(F.seg(p, 0, 0.3))
            st = cl.get(ev.get("claim"), {}).get("status")
            col = STATUS_LABEL[st][1] if st else T["accent"]
            d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col if hot else T["raised"], outline=col, width=4)
            F.text_box(img, ev["year"], (x + 40, y - 30, x + 230, y + 30), "mono-bold", 44 if hot else 34,
                       T["accent"] if hot else T["muted"], label=f"tl-year{i}", alpha=a)
            has = bool(ev.get("image") and image_entry(ev["image"]))
            F.text_box(img, ev["label"], (x + 240, y - 34, X1 - (120 if has else 0), y + 60), "sans-bold",
                       36 if hot else 30, T["text"] if hot else T["muted"], label=f"tl-label{i}", alpha=a, min_size=22)
            if has:
                F.paste(img, _thumb_cached(ev["image"], 96 if hot else 80), (X1 - (96 if hot else 80), y - 40),
                        alpha=a if hot else 0.75)
        note = seg.get("screen")
        if note:
            F.text_box(img, note, (X0, 1080, X1, 1200), "sans-bold", 40, T["neutral"], label=f"{seg['role']}-note",
                       hl_numbers=True, min_size=26)
        credit_line(img, imgs)
        footer(img, cites)

    imgs = [e["image"] for e in events[:upto + 1] if e.get("image")]
    return draw, _texts(role_label, status, cites, seg.get("screen"), credit_text(imgs),
                        *[e["year"] + " " + e["label"] for e in events[:upto + 1]])


def _split(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    an = ep.get("analogy", {})
    sim, brk = an.get("similar", [])[:3], an.get("breaks", [])[:3]

    def col(img, box, title, items, color, a, name):
        x0, y0, x1, y1 = box
        F.panel(img, box, fill=T["surface"], outline=color)
        F.text_box(img, title, (x0 + 24, y0 + 20, x1 - 24, y0 + 80), "sans-black", 36, color, label=f"{name}-title", alpha=a)
        y = y0 + 100
        h = (y1 - y - 20) // max(1, len(items))
        for i, it in enumerate(items):
            F.text_box(img, "• " + it, (x0 + 24, y, x1 - 20, y + h - 10), "sans-bold", 30, T["text"], min_size=20,
                       label=f"{name}{i}", alpha=a)
            y += h

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        col(img, (X0, 420, X0 + S.CW // 2 - 12, 1240), "GIỐNG", sim, T["positive"], F.ease_out(F.seg(p, 0, 0.2)), "sim")
        col(img, (X0 + S.CW // 2 + 12, 420, X1, 1240), "KHÁC", brk, T["negative"], F.ease_out(F.seg(p, 0.3, 0.5)), "brk")
        footer(img, cites)

    return draw, _texts(role_label, status, cites, "GIỐNG", "KHÁC", *sim, *brk)


def _scenarios(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    """Three scenario cards: name, what confirms it, what invalidates it. No probabilities unless sourced."""
    scs = ep.get("scenarios", [])
    names = {"bull": ("TÍCH CỰC", T["positive"]), "base": ("CƠ SỞ", T["neutral"]), "bear": ("TIÊU CỰC", T["negative"])}

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        y = 420
        h = (1240 - 420 - 2 * 18) // 3
        for i, sc in enumerate(scs[:3]):
            a = F.ease_out(F.seg(p, 0.1 + 0.25 * i, 0.3 + 0.25 * i))
            if a <= 0:
                break
            lab, colr = names.get(sc["name"], (sc["name"], T["accent"]))
            F.panel(img, (X0, y, X1, y + h), fill=T["surface"], outline=colr)
            F.chip(img, (X0 + 20, y + 16), lab, colr, 24)
            F.text_box(img, "✓ " + sc["confirmation"][0], (X0 + 24, y + 76, X1 - 24, y + 76 + (h - 90) // 2),
                       "sans-bold", 28, T["text"], min_size=19, label=f"sc{i}-ok", alpha=a, hl_numbers=True)
            F.text_box(img, "✗ " + sc["invalidation"][0], (X0 + 24, y + 80 + (h - 90) // 2, X1 - 24, y + h - 10),
                       "sans", 26, T["muted"], min_size=19, label=f"sc{i}-ko", alpha=a, hl_numbers=True)
            y += h + 18
        footer(img, cites)

    texts = [x for sc in scs for x in ("✓ " + sc["confirmation"][0], "✗ " + sc["invalidation"][0])]
    return draw, _texts(role_label, status, cites, "TÍCH CỰC", "CƠ SỞ", "TIÊU CỰC", *texts)


def _gauge(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    """Breadth bar: advancers / decliners / unchanged as one stacked bar, with the counts."""
    v = model.values
    parts = [("tăng", v.get("adv", 0), T["positive"]), ("giảm", v.get("dec", 0), T["negative"]),
             ("đứng", v.get("unch", 0), T["neutral"])]
    total = sum(p for _, p, _ in parts) or 1
    note = seg.get("screen") or ""

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        k = F.ease_in_out(F.seg(p, 0, 0.5))
        x = X0
        d = F.ImageDraw.Draw(img)
        for name, n, colr in parts:
            w = int(S.CW * n / total * k)
            d.rounded_rectangle([x, 470, x + max(w, 1), 590], radius=12, fill=colr)
            x += w
        y = 630
        for i, (name, n, colr) in enumerate(parts):
            F.text_box(img, f"{fmt_vi(n, 'int')} mã {name}", (X0, y, X1, y + 70), "mono-bold", 46, colr,
                       label=f"gauge{i}")
            y += 80
        if note:
            F.text_box(img, note, (X0, 900, X1, 1240), "sans-bold", 44, T["text"], label=f"{seg['role']}-note",
                       hl_numbers=True, min_size=28)
        footer(img, cites)

    return draw, _texts(role_label, status, cites, note,
                        *[f"{fmt_vi(n, 'int')} mã {name}" for name, n, _ in parts])


def _image(ep, seg, model, role_label, status, cites):
    chapter = (CHAPTER["i"], CHAPTER["n"])
    """A person / event / object image (licensed photo or labelled illustration) with caption and credit."""
    iid = seg["visual"]["image"]
    note = seg.get("screen") or ""
    box = (X0, 420, X1, 1000)

    def draw(img, t, p):
        badges(img, role_label, status, chapter=chapter)
        im = _img_cached(iid, box[2] - box[0], box[3] - box[1])
        z = 1.0 + 0.04 * F.ease_in_out(p)            # slow push-in
        if z > 1.001:
            from PIL import Image

            zw, zh = int(im.width * z), int(im.height * z)
            im = im.resize((zw, zh), Image.LANCZOS).crop(((zw - im.width) // 2, (zh - im.height) // 2,
                                                          (zw + im.width) // 2, (zh + im.height) // 2))
        F.paste(img, im, ((box[0] + box[2]) // 2, box[1]), alpha=F.ease_out(F.seg(p, 0, 0.15)), anchor="n")
        if note:
            F.text_box(img, note, (X0, 1020, X1, 1200), "sans-bold", 44, T["text"], "left", "top", min_size=28,
                       label=f"{seg['role']}-note", hl_numbers=True)
        credit_line(img, [iid])
        footer(img, cites)

    return draw, _texts(role_label, status, cites, note, credit_text([iid]))


VISUALS = {"statement": _statement, "chart": _chart, "surface": _surface, "code": _code, "terminal": _terminal,
           "citation": _citation, "timeline": _timeline, "split": _split, "scenarios": _scenarios, "gauge": _gauge,
           "sectors": _chart, "image": _image}


def segment_images(ep, seg, kind):
    """Image ids actually drawn by this scene (for QA and storyboard)."""
    if kind in ("image", "citation") and (seg.get("visual") or {}).get("image"):
        return [seg["visual"]["image"]]
    if kind == "timeline":
        upto = seg.get("visual", {}).get("upto", len(ep.get("timeline", [])) - 1)
        return [e["image"] for e in ep.get("timeline", [])[:upto + 1] if e.get("image")]
    return []


def segment_scene(ep, seg, model, role_label, default_visual="statement", min_dur=4.0):
    kind = (seg.get("visual") or {}).get("kind") or default_visual
    if seg.get("limitation"):  # a declared data limitation is said plainly, never drawn as an empty panel
        kind = "statement"
    if kind in ("chart", "sectors") and not getattr(model, "has_chart", True):
        kind = "statement"
    if kind == "surface" and not getattr(model, "has_surface", True):
        kind = "statement"
    if kind == "code" and not getattr(model, "code", ""):
        kind = "statement"
    if kind == "image" and not image_entry((seg.get("visual") or {}).get("image")):
        kind = "statement"   # unknown image id: check_images reports it; never draw a missing picture
    status = "limitation" if seg.get("limitation") else segment_status(ep, seg)
    cites = segment_sources(ep, seg)
    draw, texts = VISUALS[kind](ep, seg, model, role_label, status, cites)
    sc = Scene(seg["role"], seg["say"], draw, seg.get("min_dur", min_dur), texts=texts)
    sc.role, sc.status, sc.claims, sc.sources, sc.visual = seg["role"], status, seg.get("claims", []), cites, kind
    sc.images = segment_images(ep, seg, kind)
    return sc


def pillar_build(ep, model, ctx, role_labels, visuals, takeaway_chip="Mang về", hook_kicker=None, icons=None,
                 scenes=None):
    """Hook → segments (in order) → takeaway → end card. Used by every pillar style.
    icons: role → pictogram for text-only scenes; scenes: role → stage (characters + props, pipeline/figures.py),
    which wins over the icon. An episode overrides with visual.icon / visual.scene, and ep["hook_scene"] (or the
    style's scenes["hook"]) puts characters under the hook; "hook_scene": null turns it off."""
    hs = ep.get("hook_scene", (scenes or {}).get("hook"))
    out = [hook_scene(ep["hook"], hs, ep.get("kicker") or hook_kicker) if hs
           else S.hook(ep["hook"], kicker=ep.get("kicker") or hook_kicker)]
    segs = ep["segments"]
    for i, seg in enumerate(segs):
        CHAPTER.update(i=i, n=len(segs))
        if (icons or {}).get(seg["role"]) and not seg.get("_icon"):
            seg = dict(seg, _icon=icons[seg["role"]])
        if (scenes or {}).get(seg["role"]) and not seg.get("_scene"):
            seg = dict(seg, _scene=scenes[seg["role"]])
        out.append(segment_scene(ep, seg, model, role_labels.get(seg["role"], seg["role"].upper()),
                                 visuals.get(seg["role"], "statement")))
    CHAPTER.update(i=0, n=0)
    if ep.get("takeaway"):
        tk = {"role": "takeaway", "say": ep["takeaway"], "claims": [], "visual": {"kind": "statement", "icon": "check"}}
        draw, texts = _statement(ep, tk, model, takeaway_chip.upper(), None, [])
        out.append(Scene("takeaway", ep["takeaway"], draw, 2.5, texts=texts))
    out.append(S.end(ep["cta"], ctx["disclaimer"], ctx["tag"]))
    return out
