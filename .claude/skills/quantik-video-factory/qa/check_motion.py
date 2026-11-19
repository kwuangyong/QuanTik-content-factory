"""Motion QA for hand-drawn animations: render each kind over a scene-like span at 30 fps and flag jumps.

A jump = one frame-to-frame change much larger than the animation's typical change (a pop, a teleport, a
flicker). Reports per kind: median change, max change, ratio, and the time of the worst frame.

python qa/check_motion.py [kind ...]      (from the skill folder)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import sketch as SK  # noqa: E402

FPS, DUR, W, H = 30, 5.0, 450, 400


def profile(kind):
    prev, diffs = None, []
    n = int(FPS * DUR)
    for i in range(n):
        t = i / FPS
        img = Image.new("RGB", (W, H), (16, 30, 24))
        SK.draw(img, kind, (20, 30, W - 20, H - 20), t, t / DUR)
        a = np.asarray(img, dtype=np.int16)
        if prev is not None:
            diffs.append(np.abs(a - prev).mean())
        prev = a
    d = np.array(diffs)
    # local test: a frame change much bigger than its neighbours (±3 frames) is a pop/teleport, not motion
    ratios = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - 3):i], d[i + 1:i + 4]])
        ratios.append(d[i] / (nb.mean() + 0.15))
    ratios = np.array(ratios)
    worst = int(ratios.argmax())
    med = float(np.median(d))
    return med, float(d[worst]), float(ratios[worst]), (worst + 1) / FPS


if __name__ == "__main__":
    kinds = sys.argv[1:] or list(SK.KINDS)
    bad = 0
    for k in kinds:
        med, mx, ratio, at = profile(k)
        flag = "JUMP" if ratio > 4 and mx > 1.5 else "ok"
        bad += flag != "ok"
        print(f"{flag:<5} {k:<12} median {med:5.2f}  worst Δ {mx:5.2f}  vs neighbours ×{ratio:4.1f}  worst at {at:4.2f}s")
    sys.exit(1 if bad else 0)
