"""Video B-roll Pexels: tải theo brand/assets/broll/manifest.json và đọc từng khung (cover-crop vào ô bất kỳ).

  python clips.py            # tải mọi clip còn thiếu
  python clips.py --list     # key, tag, tác giả, đã có file chưa

Mỗi clip dùng trong video được ghi công trong captions.md ("Video: <tác giả> (Pexels) <link>").
"""
from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import urllib.request
from functools import lru_cache

import numpy as np

from core import BRAND, FPS

DIR = BRAND / "assets/broll"


@lru_cache(maxsize=1)
def manifest():
    p = DIR / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"tags": {}, "clips": {}}


def keys_for(tag):
    return manifest()["tags"].get(tag, [])


def path(key):
    return DIR / f"{key}.mp4"


def credit(key):
    c = manifest()["clips"][key]
    return f"Video: {c['credit']} (Pexels) {c['page']}"


def ensure(key):
    """Tải clip nếu chưa có. Trả về True nếu dùng được."""
    p = path(key)
    if p.exists() and p.stat().st_size > 10_000:
        return True
    c = manifest()["clips"].get(key)
    if not c:
        return False
    ca = "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()
    try:
        req = urllib.request.Request(c["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
            data = r.read()
        p.write_bytes(data)
        return True
    except Exception as ex:
        print(f"  clip {key}: không tải được ({type(ex).__name__}) → dùng hình khác")
        return False


class Clip:
    """Đọc tuần tự khung hình, cover-crop vào w×h; mở lại khi tua lùi; lặp nếu cảnh dài hơn clip."""

    def __init__(self, key, w, h, start=0.0):
        self.key, self.w, self.h, self.start = key, w, h, start
        self.proc, self.idx, self.frame = None, -1, None

    def _open(self, t0):
        if self.proc:
            self.proc.kill()
        vf = f"fps={FPS},scale={self.w}:{self.h}:force_original_aspect_ratio=increase,crop={self.w}:{self.h}"
        self.proc = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-stream_loop", "-1", "-ss",
                                      f"{self.start + t0:.3f}", "-i", str(path(self.key)), "-vf", vf,
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.idx = int(round(t0 * FPS)) - 1

    def at(self, t):
        want = int(round(t * FPS))
        if self.proc is None or want < self.idx or want - self.idx > FPS * 2:
            self._open(t)
        n = self.w * self.h * 3
        while self.idx < want:
            raw = self.proc.stdout.read(n)
            if len(raw) < n:
                break
            self.frame = np.frombuffer(raw, np.uint8).reshape(self.h, self.w, 3)
            self.idx += 1
        return self.frame


_OPEN = {}


def frame(key, w, h, t, scene_key=None):
    """Khung của clip tại t giây (np.uint8 h×w×3) hoặc None."""
    k = (key, w, h, scene_key)
    c = _OPEN.get(k)
    if c is None:
        c = _OPEN[k] = Clip(key, w, h)
    return c.at(t)


if __name__ == "__main__":
    m = manifest()
    if "--list" in sys.argv:
        tag_of = {k: t for t, ks in m["tags"].items() for k in ks}
        for k, c in m["clips"].items():
            print(f"{k:<15} {tag_of.get(k, '-'):<14} {'ok ' if path(k).exists() else '-- '} {c['credit']}")
    else:
        for k in m["clips"]:
            print(k, ensure(k))
