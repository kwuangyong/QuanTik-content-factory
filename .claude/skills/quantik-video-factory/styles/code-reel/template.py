"""code-reel: real code types out → it runs → chart → 3D (only where it helps) or a hand-drawn concept
animation → takeaway → end card. B-roll cutaways are inserted by pipeline/broll.py."""
import scenes as S

KIND = "video"
DEFAULTS = {"max_seconds": 60}


def build(ep, model, ctx):
    b = ep["beats"]
    sk = ep.get("sketch") or {}
    has3d = getattr(model, "has_surface", True) and not ep.get("no_3d")
    scenes = [
        S.hook(ep["hook"], kicker=ep.get("kicker")),
        S.code_typing(model, b[0], min_dur=5.5, latex=ep.get("formula") if ep.get("formula_real", True) else None),
        S.terminal(model, ep["outputs"], b[1], min_dur=4.5),
        S.chart(model, b[2], title=ep.get("chart_title"), min_dur=4.5),
    ]
    if has3d:
        if sk.get("say"):  # extra explainer beat before the 3D view
            scenes.append(S.sketch(sk["kind"], sk["say"], sk.get("label"), name="sketch"))
        scenes.append(S.surface(model, b[3], min_dur=5.0))
    elif sk.get("kind"):
        scenes.append(S.sketch(sk["kind"], b[3], sk.get("label"), name="sketch", min_dur=4.5))
    else:
        scenes.append(S.surface(model, b[3], min_dur=5.0))  # formula card fallback
    scenes += [
        S.statement(ep["takeaway"], name="takeaway", size=64, label_chip="Mang về"),
        S.end(ep["cta"], ctx["disclaimer"], ctx["tag"]),
    ]
    return scenes
