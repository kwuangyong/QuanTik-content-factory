"""story-mix: mỗi episode tự xếp chuỗi cảnh (lịch sử, cách dùng, đố vui, code trích đoạn, 2D/3D tuỳ chọn…).

Episode khai báo "scenes": [{"type": ..., ...}, ...]; thẻ cuối tự gắn. Xem spec.md để biết trường của từng loại.
Mọi chữ và lời vẫn đi qua placeholder {key} và QA số như các style khác.
"""
import frames as F
import scenes as S
from core import THEME as T
from render import Scene

KIND = "video"
DEFAULTS = {"max_seconds": 75}


def _story(sc, i):
    era, title, body, src = sc.get("era", ""), sc.get("title", ""), sc.get("text", ""), sc.get("source", "")

    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.25))
        F.chip(img, (S.X0, 350), sc.get("chip", "Câu chuyện"), T["neutral"], 26)
        F.text_box(img, era, (S.X0, 420, S.X1, 560), "mono-bold", 96, T["accent"], label=f"story{i}-era", alpha=a,
                   min_size=48)
        F.text_box(img, title, (S.X0, 580, S.X1, 800), "sans-black", 66, T["text"], label=f"story{i}-title",
                   alpha=a, min_size=38)
        b = F.ease_out(F.seg(p, 0.15, 0.4))
        if b > 0:
            F.panel(img, (S.X0, 830, S.X1, 1240), fill=T["surface"])
            F.text_box(img, body, (S.X0 + 36, 864, S.X1 - 36, 1200), "sans-bold", 44, T["text"], label=f"story{i}-body",
                       alpha=b, hl_numbers=True, min_size=28)
        if src:
            F.text_box(img, "Nguồn: " + src, (S.X0, 1252, S.X1, S.BOT), "sans-bold", 22, T["muted"],
                       label=f"story{i}-src", min_size=16)

    return Scene(f"story{i}", sc["say"], draw, sc.get("min_dur", 4.0), texts=[era, title, body])


def _usage(sc, i):
    steps, title = sc["steps"], sc.get("title", "Dùng thế nào?")

    def draw(img, t, p):
        F.chip(img, (S.X0, 350), sc.get("chip", "Áp dụng"), T["positive"], 26)
        F.text_box(img, title, (S.X0, 420, S.X1, 560), "sans-black", 64, T["text"], label=f"usage{i}-title", min_size=36)
        y = 600
        h = min(170, (S.BOT - 600) // max(1, len(steps)))
        for k, st in enumerate(steps):
            a = F.ease_out(F.seg(p, 0.1 + 0.6 * k / len(steps), 0.2 + 0.6 * k / len(steps)))
            if a <= 0:
                break
            F.panel(img, (S.X0, y, S.X1, y + h - 18), fill=T["raised"])
            F.text_box(img, str(k + 1), (S.X0 + 24, y, S.X0 + 100, y + h - 18), "mono-bold", 64, T["positive"],
                       "center", "middle", label=f"usage{i}-n{k}", alpha=a)
            F.text_box(img, st, (S.X0 + 120, y + 14, S.X1 - 24, y + h - 32), "sans-bold", 40, T["text"], "left",
                       "middle", label=f"usage{i}-s{k}", alpha=a, hl_numbers=True, min_size=26)
            y += h

    return Scene(f"usage{i}", sc["say"], draw, sc.get("min_dur", 4.5), texts=[title] + steps)


def _quiz(sc, i):
    q, opts, ans = sc["question"], sc["options"], sc["answer"]
    letters = "ABCD"

    def draw(img, t, p):
        F.chip(img, (S.X0, 350), sc.get("chip", "Đố bạn"), T["accent"], 26)
        F.text_box(img, q, (S.X0, 420, S.X1, 720), "sans-black", 62, T["text"], label=f"quiz{i}-q", hl_numbers=True,
                   min_size=36)
        reveal = p >= sc.get("reveal_at", 0.62)
        y = 760
        for k, o in enumerate(opts):
            a = F.ease_out(F.seg(p, 0.08 + 0.08 * k, 0.2 + 0.08 * k))
            if a <= 0:
                break
            ok = k == ans
            fill = (20, 60, 42) if reveal and ok else T["raised"]
            F.panel(img, (S.X0, y, S.X1, y + 120), fill=fill, outline=T["positive"] if reveal and ok else None)
            col = T["muted"] if reveal and not ok else T["text"]
            F.text_box(img, f"{letters[k]}.  {o}", (S.X0 + 30, y + 10, S.X1 - 30, y + 110), "sans-bold", 44, col,
                       "left", "middle", label=f"quiz{i}-o{k}", alpha=a, hl_numbers=True, min_size=26)
            y += 136

    return Scene(f"quiz{i}", sc["say"], draw, sc.get("min_dur", 5.0), texts=[q] + opts)


def _compare(sc, i):
    L, R = sc["left"], sc["right"]

    def side(img, box, d, color, a, k):
        x0, y0, x1, y1 = box
        F.panel(img, box, fill=(int(color[0] * .13), int(color[1] * .13), int(color[2] * .13)), outline=color)
        F.text_box(img, d["label"], (x0 + 30, y0 + 24, x1 - 30, y0 + 110), "sans-bold", 40, T["muted"],
                   label=f"cmp{i}-l{k}", alpha=a, min_size=24)
        F.text_box(img, d["value"], (x0 + 30, y0 + 110, x1 - 30, y1 - 80), "mono-bold", 150, color, "left", "middle",
                   label=f"cmp{i}-v{k}", alpha=a, min_size=56)
        if d.get("note"):
            F.text_box(img, d["note"], (x0 + 30, y1 - 80, x1 - 30, y1 - 20), "sans-bold", 30, T["text"],
                       label=f"cmp{i}-n{k}", alpha=a, min_size=20)

    def draw(img, t, p):
        if sc.get("title"):
            F.text_box(img, sc["title"], (S.X0, 340, S.X1, 450), "sans-black", 56, T["text"], label=f"cmp{i}-t",
                       min_size=32)
        side(img, (S.X0, 480, S.X1, 860), L, T[L.get("color", "positive")], F.ease_out(F.seg(p, 0, 0.2)), 0)
        side(img, (S.X0, 900, S.X1, 1280), R, T[R.get("color", "negative")], F.ease_out(F.seg(p, 0.25, 0.45)), 1)

    texts = [sc.get("title", ""), L["label"], L["value"], L.get("note", ""), R["label"], R["value"], R.get("note", "")]
    return Scene(f"compare{i}", sc["say"], draw, sc.get("min_dur", 4.5), texts=texts)


def _myth(sc, i):
    myth, fact = sc["myth"], sc["fact"]

    def card(img, box, label, text, color, a, strike=0.0, nm=""):
        x0, y0, x1, y1 = box
        F.panel(img, box, fill=(int(color[0] * .14), int(color[1] * .14), int(color[2] * .14)), outline=color)
        F.chip(img, (x0 + 30, y0 + 30), label, color, 28)
        F.text_box(img, text, (x0 + 34, y0 + 110, x1 - 34, y1 - 30), "sans-bold", 54, T["text"], label=nm,
                   hl_numbers=True, alpha=a, min_size=30)
        if strike:
            F.ImageDraw.Draw(img).line([(x0 + 20, y1 - 20), (x0 + 20 + (x1 - x0 - 40) * strike, y0 + 20)], fill=color,
                                       width=10)

    def draw(img, t, p):
        card(img, (S.X0, 340, S.X1, 790), "BẠN NGHĨ", myth, T["negative"], F.ease_out(F.seg(p, 0, 0.15)),
             F.ease_out(F.seg(p, 0.4, 0.5)), f"myth{i}")
        a = F.ease_out(F.seg(p, 0.45, 0.6))
        if a > 0:
            card(img, (S.X0, 830, S.X1, 1290), "THỰC RA", fact, T["positive"], a, nm=f"fact{i}")

    return Scene(f"myth{i}", sc["say"], draw, sc.get("min_dur", 6.0), texts=[myth, fact, "BẠN NGHĨ", "THỰC RA"])


def _code(sc, model, i):
    """Code thật của mô hình: cả hàm, hoặc chỉ vài dòng (lines=[a, b]) với dòng nhấn (hl)."""
    lines = model.code.splitlines()
    a, b = sc.get("lines", [1, len(lines)])
    sub = "\n".join(lines[a - 1:b])
    hl = sc.get("hl")
    title = sc.get("title") or (f"{model.topic}_demo · dòng {a}–{b}" if (a, b) != (1, len(lines)) else f"{model.topic}.py")
    total = len(sub)

    def draw(img, t, p):
        n = int(total * F.ease_in_out(F.seg(p, 0, 0.7)))
        im = F.fit_width(F.code_panel(sub, S.CW, chars=n if n < total else None,
                                      hl_line=(hl - a) if hl and p > 0.72 else None, title=title), S.CW, 760)
        F.paste(img, im, (S.X0, 340))
        if sc.get("note"):
            y = 340 + im.height + 40
            F.text_box(img, sc["note"], (S.X0, y, S.X1, S.BOT), "sans-bold", 44, T["neutral"], label=f"code{i}-note",
                       hl_numbers=True, alpha=F.ease_out(F.seg(p, 0.7, 0.85)), min_size=28)

    return Scene(f"code{i}", sc["say"], draw, sc.get("min_dur", 5.0), texts=[sc.get("note", "")])


def build(ep, model, ctx):
    out = []
    for i, sc in enumerate(ep["scenes"]):
        k = sc["type"]
        if k == "hook":
            out.append(S.hook(sc["text"], say=sc.get("say"), kicker=sc.get("kicker")))
        elif k == "story":
            out.append(_story(sc, i))
        elif k == "usage":
            out.append(_usage(sc, i))
        elif k == "quiz":
            out.append(_quiz(sc, i))
        elif k == "compare":
            out.append(_compare(sc, i))
        elif k == "myth":
            out.append(_myth(sc, i))
        elif k == "code":
            out.append(_code(sc, model, i))
        elif k == "run":
            out.append(S.terminal(model, sc["outputs"], sc["say"], name=f"run{i}", min_dur=sc.get("min_dur", 4.5)))
        elif k == "chart":
            notes = [(n[0], n[1]) for n in sc.get("notes", [])] or None
            out.append(S.chart(model, sc["say"], title=sc.get("title"), name=f"chart{i}", notes=notes,
                               min_dur=sc.get("min_dur", 4.5)))
        elif k == "surface":
            out.append(S.surface(model, sc["say"], caption=sc.get("caption"), name=f"surface{i}",
                                 view=sc.get("view", "orbit"), min_dur=sc.get("min_dur", 5.0)))
        elif k == "formula":
            out.append(S.formula(sc["latex"], sc["say"], name=f"formula{i}", caption=sc.get("caption"),
                                 min_dur=sc.get("min_dur", 4.0)))
        elif k == "statement":
            out.append(S.statement(sc["text"], say=sc.get("say"), name=f"statement{i}", size=sc.get("size", 64),
                                   label_chip=sc.get("chip")))
        else:
            raise ValueError(f"story-mix: không biết loại cảnh {k!r}")
    out.append(S.end(ep["cta"], ctx["disclaimer"], ctx["tag"]))
    return out
