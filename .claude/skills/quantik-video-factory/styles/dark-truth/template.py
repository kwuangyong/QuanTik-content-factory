"""dark-truth: YouTube Shorts on psychology, poker theory and game theory.

Hook that provokes (an uncomfortable but TRUE claim) → wiki card (what it is, who found it, with source) →
hand-drawn animation of the idea → the key number counting up → chart → rotating 3D → the dark twist → takeaway.
Every number still comes from the model run; the provocation is in the framing, never in invented facts.
"""
import anims as A
import frames as F
import scenes as S
from core import THEME as T
from render import Scene

KIND = "video"
DEFAULTS = {"max_seconds": 90}


def _hook(text, kicker):
    words = text.split()

    def draw(img, t, p):
        k = max(1, int(len(words) * F.ease_out(F.seg(p, 0, 0.4)) + 0.999))
        F.chip(img, (S.X0, 420), kicker, T["negative"], 30)
        F.text_box(img, " ".join(words[:k]), (S.X0, 520, S.X1, 1200), "sans-black", 96, T["text"], "left", "middle",
                   min_size=50, label="hook", spacing=1.1, hl_numbers=True)
        w = int(S.CW * F.ease_out(F.seg(p, 0.05, 0.6)))
        F.ImageDraw.Draw(img).rectangle([S.X0, 1230, S.X0 + w, 1240], fill=T["negative"])

    return Scene("hook", text, draw, 2.6, texts=[text, kicker])


def _dark(text):
    def draw(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.2))
        F.panel(img, (S.X0, 420, S.X1, 1250), fill=(34, 12, 14), outline=T["negative"])
        F.chip(img, (S.X0 + 30, 450), "MẶT TỐI", T["negative"], 28)
        F.text_box(img, text, (S.X0 + 40, 540, S.X1 - 40, 1220), "sans-black", 64, T["text"], "left", "middle",
                   min_size=36, label="dark", hl_numbers=True, alpha=a)

    return Scene("dark", text, draw, 3.5, texts=[text, "MẶT TỐI"])


def build(ep, model, ctx):
    import importlib.util
    from core import STYLES

    spec = importlib.util.spec_from_file_location("kt", STYLES / "kinetic-text" / "template.py")
    kt = importlib.util.module_from_spec(spec); spec.loader.exec_module(kt)
    b = ep["beats"]
    out = [_hook(ep["hook"], ep.get("dark_kicker", "SỰ THẬT ĐEN TỐI"))]
    if ep.get("wiki"):
        out.append(A.wiki(ep["wiki"]))
    if ep.get("anim"):
        out.append(A.anim(ep["anim"], b[0], min_dur=4.5))
    else:
        out.append(kt.beat(b[0], "beat0"))
    out.append(kt.beat(b[1], "beat1"))
    out.append(S.chart(model, b[2], title=ep.get("chart_title"), min_dur=4.5))
    out.append(S.surface(model, b[3], min_dur=4.5))
    if ep.get("dark"):
        out.append(_dark(ep["dark"]))
    out.append(S.statement(ep["takeaway"], name="takeaway", size=62, label_chip="Mang về"))
    out.append(S.end(ep["cta"], ctx["disclaimer"], ctx["tag"]))
    return out
