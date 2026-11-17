"""kinetic-text: faceless — words land one by one, the key number of each beat counts up big; chart + 3D close."""
import re

import frames as F
import illustrate as I
import scenes as S
from core import THEME as T
from render import Scene

KIND = "video"
DEFAULTS = {"max_seconds": 60}

_NUM = re.compile(r"([−\-]?)(\d[\d.]*)(?:,(\d+))?(%|x)?")


def _countup(token, k):
    """Render token (e.g. '19,5%') at fraction k of its value, keeping its format."""
    m = _NUM.fullmatch(token)
    if not m:
        return token
    sign, ip, fp, suf = m.group(1), m.group(2).replace(".", ""), m.group(3) or "", m.group(4) or ""
    val = float(ip + ("." + fp if fp else "")) * k
    s = f"{val:.{len(fp)}f}"
    a, _, b = s.partition(".")
    a = f"{int(a):,}".replace(",", ".")
    return sign + a + ("," + b if b else "") + suf


def beat(text, name, kicker=None, min_dur=2.8):
    words = text.split()
    big = S.first_number(text)

    tag = None if big else I.pick(text)

    def draw(img, t, p):
        if tag:  # câu không có số "đắt" nhưng có hình khớp lời → hoạ động nửa trên, chữ nửa dưới
            F.paste(img, I.frame(tag, S.CW, 420, p, t), (S.X0, 300))
        if big:
            k = F.ease_out(F.seg(p, 0.0, 0.45))
            F.text_box(img, _countup(big, k) if k < 1 else big, (S.X0, 330, S.X1, 640), "mono-bold", 210,
                       T["accent"], "left", "middle", min_size=90, label=f"{name}-big")
        n = max(1, int(len(words) * F.seg(p, 0.05, 0.75) + 0.999))
        y0 = 680 if big else (760 if tag else 420)
        F.text_box(img, " ".join(words[:n]), (S.X0, y0, S.X1, S.BOT), "sans-bold", 66, T["text"], "left", "top",
                   min_size=38, label=name, hl_numbers=True)
        if kicker:
            F.chip(img, (S.X0, y0 - 80 if not big else 300), kicker, T["raised"], 24)

    return Scene(name, text, draw, min_dur, texts=[text])


def build(ep, model, ctx):
    out = [S.hook(ep["hook"], kicker=ep.get("kicker"), visual=ep.get("hook_visual", "auto"))]
    for i, b in enumerate(ep["beats"][:2]):
        out.append(beat(b, f"beat{i + 1}"))
    out.append(S.chart(model, ep["beats"][2], title=ep.get("chart_title"), min_dur=4.5))  # beat 3 describes the chart
    out.append(S.surface(model, ep["beats"][3], min_dur=4.5))
    out.append(S.statement(ep["takeaway"], name="takeaway", size=64, label_chip="Mang về"))
    out.append(S.end(ep["cta"], ctx["disclaimer"], ctx["tag"]))
    return out
