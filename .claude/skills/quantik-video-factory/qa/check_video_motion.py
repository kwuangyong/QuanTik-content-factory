"""Motion QA on a rendered video: find frames that jump much more than their neighbours, ignoring scene cuts.

python qa/check_video_motion.py social-output/<id>        → prints suspicious timestamps with the scene + line said
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def frames(path, w=270, h=480):
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"scale={w}:{h}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h:
            break
        yield np.frombuffer(b, np.uint8).astype(np.int16)


def check(out_dir, fps=30):
    out = Path(out_dir)
    tl = json.loads((out / "timeline.json").read_text(encoding="utf-8"))
    cuts = [s["start"] for s in tl[1:]]
    prev, d = None, []
    for f in frames(out / "final.mp4"):
        if prev is not None:
            d.append(np.abs(f - prev).mean())
        prev = f
    d = np.array(d)
    issues = []
    for i in range(len(d)):
        t = (i + 1) / fps
        if any(abs(t - c) < 0.1 for c in cuts):
            continue
        nb = np.concatenate([d[max(0, i - 3):i], d[i + 1:i + 4]])
        r = d[i] / (nb.mean() + 0.3)
        if r > 5 and d[i] > 2.0:
            sc = next((s for s in tl if s["start"] <= t < s["end"]), tl[-1])
            issues.append((round(t, 2), sc["scene"], round(float(r), 1), sc["say"][:60]))
    return issues


if __name__ == "__main__":
    bad = 0
    for o in sys.argv[1:]:
        iss = check(o)
        print(f"{Path(o).name}: {'OK — không có khung giật' if not iss else str(len(iss)) + ' khung đáng ngờ'}")
        for t, sc, r, say in iss:
            print(f"   {t:6.2f}s  {sc:<10} ×{r:<5} «{say}»")
        bad += bool(iss)
    sys.exit(1 if bad else 0)
