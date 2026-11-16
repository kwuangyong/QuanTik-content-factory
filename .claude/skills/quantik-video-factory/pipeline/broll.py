"""Stock B-roll for the broll-story style: download (from brand/assets/broll/manifest.json) and stream frames.

  python broll.py            # download every clip in the manifest that is missing
  python broll.py --list     # keys, credit, local status

Clips are Pexels videos found with vidIQ find_broll. Every clip used in a video is credited in captions.md.
Frames are decoded by ffmpeg, cropped to 1080x1920, and streamed in order (one ffmpeg per clip use).
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

from core import BRAND, FPS, H, W

DIR = BRAND / "assets/broll"


def manifest():
    return json.loads((DIR / "manifest.json").read_text(encoding="utf-8"))["clips"]


def path(key):
    return DIR / f"{key}.mp4"


def credit(key):
    c = manifest()[key]
    return f"{c['credit']} (Pexels) {c['page']}"


def download(keys=None):
    for k, c in manifest().items():
        if keys and k not in keys:
            continue
        p = path(k)
        if p.exists() and p.stat().st_size > 10_000:
            continue
        print(f"  ↓ {k}")
        req = urllib.request.Request(c["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(p, "wb") as fh:
            fh.write(r.read())


def download_images():
    """Wikimedia stills listed in brand/assets/images/manifest.json (polite UA, slow down on HTTP 429)."""
    import time
    d = BRAND / "assets/images"
    for k, c in json.loads((d / "manifest.json").read_text(encoding="utf-8"))["images"].items():
        p = d / c["file"]
        if p.exists() and p.stat().st_size > 5_000:
            continue
        print(f"  ↓ image {k}")
        for wait in (0, 10, 30):
            time.sleep(wait)
            try:
                req = urllib.request.Request(c["url"], headers={"User-Agent": "QuanTikContentBot/1.0 (educational video)"})
                with urllib.request.urlopen(req, timeout=60) as r, open(p, "wb") as fh:
                    fh.write(r.read())
                break
            except Exception as ex:  # 429 rate limit → retry later
                print(f"    retry ({ex})")


class Clip:
    """Sequential frame reader with cover-crop to 1080x1920; rewinds (re-opens) when asked for an earlier time.
    Loops the clip if a scene is longer than the footage. `start` skips into the clip (seconds)."""

    def __init__(self, key, start=0.0, scale=1.0, speed=1.0):
        self.key, self.start, self.speed = key, start, speed
        self.w, self.h = W, H
        self.proc, self.idx, self.frame = None, -1, None
        self.zoom = scale

    def _open(self, t0):
        if self.proc:
            self.proc.kill()
        vf = (f"setpts=PTS/{self.speed},fps={FPS},scale={self.w}:{self.h}:force_original_aspect_ratio=increase,"
              f"crop={self.w}:{self.h}")
        self.proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1",
                                      "-ss", f"{self.start + t0 * self.speed:.3f}", "-i", str(path(self.key)),
                                      "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.base = int(round(t0 * FPS)); self.idx = self.base - 1

    def at(self, t):
        want = int(round(t * FPS))
        if self.proc is None or want < self.idx or want - self.idx > FPS * 2:
            self._open(t)
        while self.idx < want:
            raw = self.proc.stdout.read(self.w * self.h * 3)
            if len(raw) < self.w * self.h * 3:
                break
            self.frame = np.frombuffer(raw, np.uint8).reshape(self.h, self.w, 3)
            self.idx += 1
        return self.frame

    def close(self):
        if self.proc:
            self.proc.kill(); self.proc = None


if __name__ == "__main__":
    if "--list" in sys.argv:
        for k, c in manifest().items():
            print(f"{k:<15} {'ok ' if path(k).exists() else '-- '} {c['credit']}")
    else:
        download(sys.argv[1:] or None)
        download_images()
