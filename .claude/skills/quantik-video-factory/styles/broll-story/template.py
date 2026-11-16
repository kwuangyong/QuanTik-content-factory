"""broll-story: stock B-roll + procedural animation + the model's real chart/code, with overlapping transitions.

The episode lists its scenes in ``sequence`` (see spec.md). Hook and takeaway sit on top of footage; numbers
still come only from the model run (placeholders), and every clip/image used is credited in captions.md.
"""
import json
import re
from functools import lru_cache

import broll as B
import frames as F
import illustrations as IL
import scenes as S
from core import BRAND, H, THEME as T, W, tr
from PIL import Image, ImageDraw
from render import Scene

KIND = "video"
DEFAULTS = {"max_seconds": 60, "lang": "en"}
CONTENT = (S.X0, 330, S.X1, 1300)


@lru_cache(maxsize=2)
def _shade():
    """Dark overlay for footage: strong at top (header) and bottom (subtitles), lighter in the middle."""
    import numpy as np
    y = np.linspace(0, 1, H)[:, None]
    a = 0.55 + 0.35 * np.clip((y - 0.62) / 0.2, 0, 1) + 0.25 * np.clip((0.16 - y) / 0.16, 0, 1)
    return Image.fromarray((np.clip(a, 0, 0.92) * 255).astype("uint8").repeat(W, axis=1), "L")


def _footage(img, clip, t, tint=None):
    fr = clip.at(t)
    if fr is None:
        return
    im = Image.fromarray(fr)
    img.paste(im)
    img.paste(Image.new("RGB", (W, H), T["bg"]), (0, 0), _shade())
    if tint:
        img.paste(Image.new("RGB", (W, H), tint), (0, 0), Image.new("L", (W, H), 28))


def _shadow_text(img, text, box, size, color, label, align="left", valign="middle", kind="sans-black", alpha=1.0):
    x0, y0, x1, y1 = box
    F.text_box(img, text, (x0 + 4, y0 + 5, x1, y1 + 5), kind, size, (0, 0, 0), align, valign, min_size=40,
               label=label + "-shadow", alpha=0.7 * alpha)
    F.text_box(img, text, (x0, y0, x1 - 4, y1), kind, size, color, align, valign, min_size=40, label=label, hl_numbers=True,
               alpha=alpha)


def _clip(item, used):
    key = item["clip"]
    used.add(("clip", key))
    return B.Clip(key, start=item.get("start", 0.0), speed=item.get("speed", 1.0))


def hook(item, ep, model, ctx, used):
    clip = _clip(item, used)
    words = ep["hook"].split()
    anim = IL.ANIMS.get(item.get("anim"))

    def draw(img, t, p):
        _footage(img, clip, t)
        F.header(img, ctx["tag"], ctx["note"])
        k = max(1, int(len(words) * F.ease_out(F.seg(p, 0, 0.4)) + 0.999))
        if ep.get("kicker"):
            F.chip(img, (S.X0, 400), ep["kicker"], T["accent"], 28)
        _shadow_text(img, " ".join(words[:k]), (S.X0, 480, S.X1, 1060 if anim else 1240), 88, T["text"], "hook")
        if anim:
            anim(img, t, F.seg(p, 0.35, 1.0), model, (S.X0, 1060, S.X1, 1300), **item.get("opt", {}))

    return Scene("hook", item.get("say", ep["hook"]), draw, item.get("min_dur", 3.0),
                 texts=[ep["hook"], ep.get("kicker", "")], header=False)


def broll(item, ep, model, ctx, used, i):
    clip = _clip(item, used)
    text = item.get("text", "")
    anim = IL.ANIMS.get(item.get("anim"))

    def draw(img, t, p):
        _footage(img, clip, t, item.get("tint") and tuple(item["tint"]))
        F.header(img, ctx["tag"], ctx["note"])
        a = F.ease_out(F.seg(p, 0.0, 0.25))
        if text:
            _shadow_text(img, text, (S.X0, 520 - 30 * (1 - a), S.X1, 1000 if anim else 1250), item.get("size", 78),
                         T["text"], f"broll{i}", alpha=a)
        if anim:
            anim(img, t, F.seg(p, 0.15, 1.0), model, (S.X0, 960, S.X1, 1300), **item.get("opt", {}))

    return Scene(f"broll{i}", item["say"], draw, item.get("min_dur", 3.0), texts=[text], header=False,
                 transition=item.get("transition", "zoom"))


def anim(item, ep, model, ctx, used, i):
    fn = IL.ANIMS[item["anim"]]
    text = item.get("text", "")
    box = tuple(item.get("box", (S.X0, 430 if text else 340, S.X1, 1300)))

    def draw(img, t, p):
        if text:
            F.text_box(img, text, (S.X0, 330, S.X1, 420), "sans-black", 52, T["accent"], "left", "middle",
                       min_size=30, label=f"anim{i}-title", hl_numbers=True)
        fn(img, t, p, model, box, **item.get("opt", {}))

    return Scene(f"anim{i}", item["say"], draw, item.get("min_dur", 3.5), texts=[text], transition="fade")


def chart(item, ep, model, ctx, used, i):
    a0, a1 = item.get("from", 0.0), item.get("to", 1.0)
    box = (S.X0, 430, S.X1, 1180 if item.get("note") else 1300)
    steps = 40
    S._MODELS[id(model)] = model

    def draw(img, t, p):
        upto = a0 + (a1 - a0) * F.ease_in_out(F.seg(p, 0, 0.8))
        step = max(1, int(round(upto * steps)))
        F.paste(img, S._chart_cached(id(model), step, steps, box[2] - box[0], box[3] - box[1], None), (box[0], box[1]))
        if item.get("label"):
            F.chip(img, (S.X0, 340), item["label"], T["raised"], 26)
        if item.get("note") and p > 0.45:
            F.text_box(img, item["note"], (S.X0, 1190, S.X1, 1300), "sans-bold", 40, T["neutral"], "left", "middle",
                       min_size=28, label=f"chart{i}-note", hl_numbers=True, alpha=F.ease_out(F.seg(p, 0.45, 0.6)))

    return Scene(f"chart{i}", item["say"], draw, item.get("min_dur", 3.5),
                 texts=[item.get("label", ""), item.get("note", "")], transition="slide")


def image(item, ep, model, ctx, used, i):
    meta = json.loads((BRAND / "assets/images/manifest.json").read_text(encoding="utf-8"))["images"][item["image"]]
    used.add(("image", item["image"]))
    src = Image.open(BRAND / "assets/images" / meta["file"]).convert("RGB")
    fw, fh = S.X1 - S.X0, 700
    text = item.get("text", "")

    def draw(img, t, p):
        z = 1.0 + 0.10 * p
        s = max(fw / src.width, fh / src.height) * z
        im = src.resize((int(src.width * s), int(src.height * s)), Image.BILINEAR)
        ox = int((im.width - fw) * (0.3 + 0.4 * p)); oy = int((im.height - fh) * 0.25)
        im = im.crop((ox, oy, ox + fw, oy + fh))
        mask = Image.new("L", (fw, fh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, fw - 1, fh - 1], radius=28, fill=255)
        a = F.ease_out(F.seg(p, 0, 0.2))
        img.paste(im, (S.X0, 360 + int(30 * (1 - a))), mask)
        F.text_box(img, meta["label"], (S.X0, 1080, S.X1, 1140), "sans-black", 48, T["accent"], label=f"img{i}-label")
        if text:
            F.text_box(img, text, (S.X0, 1150, S.X1, 1270), "sans-bold", 38, T["text"], label=f"img{i}-text",
                       hl_numbers=True)
        F.text_box(img, f"Photo: {meta['credit']} · {meta['license']}", (S.X0, 1272, S.X1, 1302), "sans", 20,
                   T["muted"], min_size=20, label=f"img{i}-credit")

    return Scene(f"image{i}", item["say"], draw, item.get("min_dur", 3.5), texts=[meta["label"], text],
                 transition="fade")


def number(item, ep, model, ctx, used, i):
    value, label = item["value"], item.get("label", "")
    m = re.search(r"\d[\d,]*\.?\d*", value)

    def draw(img, t, p):
        k = F.ease_out(F.seg(p, 0.05, 0.55))
        shown = value
        if m and k < 1:
            target = float(m.group(0).replace(",", ""))
            dec = len(m.group(0).split(".")[1]) if "." in m.group(0) else 0
            cur = f"{target * k:,.{dec}f}"
            shown = value[:m.start()] + cur + value[m.end():]
        F.panel(img, (S.X0, 520, S.X1, 1120), fill=(30, 22, 16), outline=T["accent"])
        F.text_box(img, shown, (S.X0 + 30, 560, S.X1 - 30, 880), "sans-black", 200, T["accent"], "center", "middle",
                   min_size=70, label=f"num{i}-value")
        F.text_box(img, label, (S.X0 + 40, 890, S.X1 - 40, 1100), "sans-bold", 46, T["text"], "center", "top",
                   min_size=30, label=f"num{i}-label", alpha=F.ease_out(F.seg(p, 0.3, 0.6)))

    return Scene(f"number{i}", item["say"], draw, item.get("min_dur", 3.0), texts=[value, label], transition="zoom")


def end(ep, ctx, used):
    extra = ctx.get("disclaimer_extra", "")

    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.25))
        F.paste(img, F.logo(180), (W // 2, 400 - 30 * (1 - a)), alpha=a, anchor="n")
        F.text_box(img, "QuanTik", (S.X0, 600, S.X1, 690), "sans-black", 76, T["text"], "center", label="end-brand",
                   alpha=a)
        F.text_box(img, ep["cta"], (S.X0 + 20, 710, S.X1 - 20, 870), "sans-bold", 46, T["accent"], "center",
                   label="end-cta", alpha=F.ease_out(F.seg(p, 0.12, 0.35)))
        F.panel(img, (S.X0, 900, S.X1, 1300), fill=T["surface"])
        if extra:
            F.text_box(img, extra, (S.X0 + 30, 925, S.X1 - 30, 1060), "sans-bold", 30, T["neutral"], "center",
                       min_size=22, label="end-extra", alpha=F.ease_out(F.seg(p, 0.2, 0.45)))
        dy = (1070, 1220) if extra else (960, 1200)
        F.text_box(img, ctx["disclaimer"], (S.X0 + 30, dy[0], S.X1 - 30, dy[1]), "sans", 28 if not extra else 25,
                   T["muted"], "center",
                   min_size=20, label="end-disclaimer", alpha=F.ease_out(F.seg(p, 0.25, 0.5)))
        F.text_box(img, "B-roll: Pexels · simulation: QuanTik code", (S.X0 + 30, 1240, S.X1 - 30, 1280), "sans", 20,
                   T["muted"], "center", min_size=20, label="end-credit")

    return Scene("end", ep["cta"], draw, 4.5, texts=[ep["cta"], ctx["disclaimer"], extra], header=False,
                 transition="fade")


def build(ep, model, ctx):
    used = set()
    out = []
    for i, item in enumerate(ep["sequence"]):
        kind = item["type"]
        if kind == "hook":
            out.append(hook(item, ep, model, ctx, used))
        elif kind == "broll":
            out.append(broll(item, ep, model, ctx, used, i))
        elif kind == "anim":
            out.append(anim(item, ep, model, ctx, used, i))
        elif kind == "chart":
            out.append(chart(item, ep, model, ctx, used, i))
        elif kind == "image":
            out.append(image(item, ep, model, ctx, used, i))
        elif kind == "number":
            out.append(number(item, ep, model, ctx, used, i))
        elif kind == "surface":
            sc = S.surface(model, item["say"], caption=item.get("caption"), name=f"surface{i}",
                           min_dur=item.get("min_dur", 4.0)); sc.transition = "fade"; out.append(sc)
        elif kind == "code":
            sc = S.code_typing(model, item["say"], name=f"code{i}", title=item.get("title"),
                               latex=item.get("latex")); sc.transition = "slide"; out.append(sc)
        elif kind == "terminal":
            sc = S.terminal(model, item["outputs"], item["say"], name=f"run{i}"); sc.transition = "fade"; out.append(sc)
        elif kind == "formula":
            sc = S.formula(item["latex"], item["say"], name=f"formula{i}", caption=item.get("caption"))
            sc.transition = "fade"; out.append(sc)
        elif kind == "statement":
            sc = S.statement(item["text"], item.get("say"), name=f"statement{i}", size=item.get("size", 68),
                             label_chip=item.get("chip")); sc.transition = "fade"; out.append(sc)
        else:
            raise ValueError(f"broll-story: unknown scene type {kind!r}")
    take = ep.get("takeaway_clip")
    if take:
        out.append(broll({"clip": take, "say": ep["takeaway"], "text": ep["takeaway"], "size": 64,
                          "start": ep.get("takeaway_start", 0.0), "min_dur": 4.0}, ep, model, ctx, used, 99))
        out[-1].name = "takeaway"
    else:
        sc = S.statement(ep["takeaway"], name="takeaway", size=64, label_chip=tr("Mang về", "Takeaway"))
        sc.transition = "fade"; out.append(sc)
    out.append(end(ep, ctx, used))
    credits = []
    for kind, key in sorted(used):
        if kind == "clip":
            credits.append("Video: " + B.credit(key))
        else:
            meta = json.loads((BRAND / "assets/images/manifest.json").read_text(encoding="utf-8"))["images"][key]
            credits.append(f"Photo: {meta['credit']} ({meta['license']}) {meta['page']}")
    ep["credits"] = credits
    return out
