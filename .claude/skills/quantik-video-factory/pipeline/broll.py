"""B-roll: real photos from Wikimedia Commons (with on-screen credit) or, when none can be used, a hand-drawn
animated doodle. Flexible by design: every spec asks for a real image first and always has a drawn fallback.

Spec (episode field "broll" = list, "hook_broll" = one spec):
  {"query": "Carl Friedrich Gauss portrait",   # Commons search; or "file": "File:Exact name.jpg"
   "draw": "bell",                              # doodle kind used when no free image is found (see DOODLES)
   "label": "Carl Friedrich Gauss",             # chip on screen
   "say": "Người đặt tên cho đường cong này: Gauss.",  # narration for the cutaway (QA-checked like any beat)
   "after": "hook"}                             # insert after this scene name (default: hook)

Only licences that allow reuse with attribution are accepted: CC0, Public domain, CC BY, CC BY-SA
(never NC / ND). Downloads are cached in brand/assets/broll/ together with their credit, so a video can be
rebuilt offline and the source is always on record.

Usage: python broll.py "Thomas Bayes"      → fetch + print the credit (cache warm-up)
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from core import BRAND, THEME as T

CACHE = BRAND / "assets" / "broll"
API = "https://commons.wikimedia.org/w/api.php"
UA = "QuanTikContentFactory/1.0 (educational short videos; attribution shown on screen)"
OK_LICENSE = re.compile(r"^(cc0|public domain|pd\b|pd-|cc[- ]by(-sa)?[- ]?\d)", re.I)
BAD_LICENSE = re.compile(r"\b(nc|nd)\b|non-?commercial|no ?deriv|fair use", re.I)
_last_call = [0.0]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] + "-" + hashlib.md5(s.encode()).hexdigest()[:6]


def _get(url, tries=None):
    import os

    tries = tries or (1 if os.environ.get("QT_BROLL_FAST") else 4)  # render: fail fast; prefetch: patient
    for i in range(tries):
        wait = 1.2 - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        _last_call[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                time.sleep(6 * (i + 1) ** 2)
                continue
            raise
    raise RuntimeError("unreachable")


def _clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()
    return re.sub(r"\s+", " ", s)


def _candidates(spec):
    q = {"action": "query", "format": "json", "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime",
         "iiurlwidth": "1280"}
    if spec.get("file"):
        q["titles"] = spec["file"] if spec["file"].startswith("File:") else "File:" + spec["file"]
    else:
        q.update({"generator": "search", "gsrsearch": spec["query"] + " filetype:bitmap", "gsrnamespace": "6",
                  "gsrlimit": "12"})
    data = json.loads(_get(API + "?" + urllib.parse.urlencode(q)))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    for p in pages:
        for ii in p.get("imageinfo", []):
            md = ii.get("extmetadata", {})
            lic = _clean(md.get("LicenseShortName", {}).get("value"))
            if not lic or not OK_LICENSE.search(lic) or BAD_LICENSE.search(lic):
                continue
            if ii.get("mime") not in ("image/jpeg", "image/png") or min(ii.get("width", 0), ii.get("height", 0)) < 400:
                continue
            artist = _clean(md.get("Artist", {}).get("value")) or _clean(md.get("Credit", {}).get("value")) or "không rõ tác giả"
            url = (ii.get("thumburl") or ii["url"]).split("?")[0]
            url = url.replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/")  # same file, allowed host
            yield {"title": p["title"], "url": url,
                   "page": ii.get("descriptionurl", "").split("?")[0], "artist": artist[:80], "license": lic,
                   "license_url": md.get("LicenseUrl", {}).get("value", "")}


def fetch(spec):
    """Return {"path", credit...} for a free image, or {"error": why}. Cached by query/file."""
    key = spec.get("file") or spec.get("query")
    if not key:
        return {"error": "không có query/file"}
    CACHE.mkdir(parents=True, exist_ok=True)
    meta = CACHE / (_slug(key) + ".json")
    if meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        if m.get("error") or (CACHE / m["file"]).exists():
            return m if m.get("error") else {**m, "path": str(CACHE / m["file"])}
    try:
        for c in _candidates(spec):
            raw = _get(c["url"])
            ext = ".png" if c["url"].lower().endswith(".png") else ".jpg"
            name = _slug(key) + ext
            (CACHE / name).write_bytes(raw)
            c["file"], c["query"] = name, key
            meta.write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
            return {**c, "path": str(CACHE / name)}
        res = {"error": "không có ảnh giấy phép tự do", "query": key}
        meta.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")  # cache the miss too
        return res
    except Exception as e:  # offline, blocked, rate-limited: fall back to drawing (not cached, retry next time)
        return {"error": f"{type(e).__name__}: {str(e)[:80]}"}


def credit_line(c):
    return f"Ảnh: {c['artist'][:42]} · {c['license']} · Wikimedia Commons"


# ---------------------------------------------------------------- hand-drawn doodles (unit square, y down)
def _circle(cx, cy, r, n=40, a0=0.0, a1=2 * math.pi):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _axes():
    return [[(0.08, 0.08), (0.08, 0.92), (0.95, 0.92)]]


def _fn(f, x0=0.1, x1=0.93, n=60):
    return [(x0 + (x1 - x0) * i / n, f(i / n)) for i in range(n + 1)]


DOODLES = {
    "chart-up": lambda: _axes() + [_fn(lambda u: 0.82 - 0.6 * u + 0.07 * math.sin(u * 19))],
    "crash": lambda: _axes() + [_fn(lambda u: 0.3 + 0.08 * math.sin(u * 15) if u < 0.65 else 0.3 + (u - 0.65) * 1.7)],
    "zigzag": lambda: _axes() + [_fn(lambda u: 0.5 + (0.05 if u < 0.45 else 0.3) * math.sin(u * 70) * (0.6 + 0.4 * math.sin(u * 9)), n=140)],
    "bell": lambda: _axes() + [_fn(lambda u: 0.88 - 0.72 * math.exp(-((u - 0.5) ** 2) / 0.02))],
    "skew": lambda: _axes() + [_fn(lambda u: 0.88 - 0.72 * (u / 0.3) * math.exp(1 - u / 0.3) * 0.9)],
    "dice": lambda: [[(0.2, 0.25), (0.7, 0.25), (0.7, 0.75), (0.2, 0.75), (0.2, 0.25)],
                     [(0.7, 0.25), (0.85, 0.12), (0.85, 0.62), (0.7, 0.75)], [(0.2, 0.25), (0.35, 0.12), (0.85, 0.12)]]
                    + [_circle(x, y, 0.035, 12) for x, y in [(0.32, 0.37), (0.45, 0.5), (0.58, 0.63)]],
    "coin": lambda: [_circle(0.5, 0.5, 0.33), _circle(0.5, 0.5, 0.25), [(0.5, 0.33), (0.5, 0.67)],
                     [(0.42, 0.4), (0.56, 0.4), (0.44, 0.6), (0.58, 0.6)]],
    "clock": lambda: [_circle(0.5, 0.5, 0.36), [(0.5, 0.5), (0.5, 0.25)], [(0.5, 0.5), (0.68, 0.58)]]
                     + [[(0.5 + 0.31 * math.cos(a), 0.5 + 0.31 * math.sin(a)), (0.5 + 0.36 * math.cos(a), 0.5 + 0.36 * math.sin(a))]
                        for a in [k * math.pi / 6 for k in range(12)]],
    "warning": lambda: [[(0.5, 0.12), (0.9, 0.85), (0.1, 0.85), (0.5, 0.12)], [(0.5, 0.35), (0.5, 0.62)], _circle(0.5, 0.73, 0.025, 10)],
    "scale": lambda: [[(0.5, 0.15), (0.5, 0.85)], [(0.3, 0.85), (0.7, 0.85)], [(0.15, 0.3), (0.85, 0.24)],
                      [(0.15, 0.3), (0.07, 0.55), (0.25, 0.55), (0.15, 0.3)], [(0.85, 0.24), (0.77, 0.49), (0.95, 0.49), (0.85, 0.24)]],
    "matrix": lambda: [[(0.18, 0.15), (0.1, 0.15), (0.1, 0.85), (0.18, 0.85)], [(0.82, 0.15), (0.9, 0.15), (0.9, 0.85), (0.82, 0.85)]]
                      + [_circle(0.25 + 0.25 * i, 0.27 + 0.23 * j, 0.05, 14) for i in range(3) for j in range(3)],
    "arrows": lambda: [[(0.15, 0.85), (0.15, 0.1)], [(0.15, 0.85), (0.92, 0.85)], [(0.15, 0.85), (0.7, 0.3)],
                       [(0.6, 0.31), (0.7, 0.3), (0.69, 0.4)], [(0.15, 0.85), (0.8, 0.65)], [(0.71, 0.6), (0.8, 0.65), (0.72, 0.72)]],
    "network": lambda: [_circle(x, y, 0.06, 16) for x, y in [(0.2, 0.3), (0.8, 0.25), (0.5, 0.55), (0.25, 0.8), (0.78, 0.78)]]
                       + [[(0.25, 0.33), (0.45, 0.51)], [(0.75, 0.29), (0.55, 0.51)], [(0.47, 0.6), (0.29, 0.75)], [(0.55, 0.6), (0.73, 0.74)]],
    "two-lines": lambda: _axes() + [_fn(lambda u: 0.45 - 0.2 * u + 0.08 * math.sin(u * 12)),
                                    _fn(lambda u: 0.62 - 0.2 * u + 0.08 * math.sin(u * 12 + 0.6))],
    "orderbook": lambda: [[(0.1, 0.5), (0.9, 0.5)]] + [[(0.5, 0.45 - 0.08 * i), (0.5 + 0.08 * (5 - i), 0.45 - 0.08 * i)] for i in range(5)]
                         + [[(0.5, 0.55 + 0.08 * i), (0.5 - 0.08 * (5 - i), 0.55 + 0.08 * i)] for i in range(5)],
    "question": lambda: [_circle(0.5, 0.33, 0.18, 30, math.pi, 2.3 * math.pi) + [(0.5, 0.62)], _circle(0.5, 0.78, 0.03, 10)],
}
_GUESS = [("crash|sập|lỗ|trượt|impact|tác động", "crash"), ("biến động|arch|garch|nhiễu|noise", "zigzag"),
          ("chuẩn|phân phối|normal|bell|gauss", "bell"), ("lệch|skew|nhọn|kurt", "skew"), ("xác suất|bayes|ngẫu nhiên|random", "dice"),
          ("kỳ vọng|expected|cược|kelly", "coin"), ("thời gian|chuỗi|time|lãi suất|giá trị", "clock"),
          ("ma trận|matrix|riêng|eigen|nghịch|pca|hiệp phương sai", "matrix"), ("vector|tích|biến đổi|linear", "arrows"),
          ("cặp|pair|đồng liên|coint|tương quan|corr", "two-lines"), ("spread|lệnh|bid|ask|vi cấu trúc|micro", "orderbook"),
          ("arbitrage|chênh lệch", "scale"), ("thuật toán|algorithm|mạng", "network"), ("động lượng|momentum|xu hướng", "chart-up")]


def guess_doodle(*texts):
    s = " ".join(t or "" for t in texts).lower()
    return next((k for pat, k in _GUESS if re.search(pat, s)), "question")


def _wobble(pts, seed, amp=0.006):
    out = []
    for i, (x, y) in enumerate(pts):
        n1 = math.sin(seed * 12.9898 + i * 0.73) * 43758.5453
        n2 = math.sin(seed * 78.233 + i * 0.41) * 12543.1234
        out.append((x + amp * (n1 - math.floor(n1) - 0.5) * 2, y + amp * (n2 - math.floor(n2) - 0.5) * 2))
    return out


def draw_doodle(img, kind, box, p, color=None, width=9, t=0.0):
    """Animated sketch: strokes are drawn progressively (p 0..0.7), then breathe gently."""
    from PIL import ImageDraw

    strokes = DOODLES.get(kind, DOODLES["question"])()
    x0, y0, x1, y1 = box
    s = min(x1 - x0, y1 - y0)
    ox, oy = x0 + (x1 - x0 - s) / 2, y0 + (y1 - y0 - s) / 2 + 6 * math.sin(t * 2.2)
    lengths = [sum(math.dist(a, b) for a, b in zip(st, st[1:])) for st in strokes]
    total = sum(lengths) or 1
    budget = total * min(1.0, p / 0.5)
    tip = None
    d = ImageDraw.Draw(img)
    colors = [color or T["text"], T["accent"], T["neutral"], T["positive"]]
    for k, (st, ln) in enumerate(zip(strokes, lengths)):
        if budget <= 0:
            break
        pts = _wobble(st, k + 1)
        out, acc = [pts[0]], 0.0
        for a, b in zip(pts, pts[1:]):
            seg = math.dist(a, b)
            if acc + seg > budget:
                f = (budget - acc) / max(seg, 1e-9)
                out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
                break
            out.append(b); acc += seg
        budget -= ln
        xy = [(ox + u * s, oy + v * s) for u, v in out]
        if len(xy) > 1 and budget > -ln:
            tip = xy[-1]
        if len(xy) > 1:
            c = colors[0] if k == 0 or kind in ("dice", "coin", "clock", "warning", "question") else colors[min(k, 3) % 4 or 1]
            d.line(xy, fill=c, width=width, joint="curve")
            r = width // 2
            for q in (xy[0], xy[-1]):
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=c)
    if tip and p < 0.5:  # pen tip while drawing: reads as a hand sketching live
        R = width * 1.6
        d.ellipse([tip[0] - R, tip[1] - R, tip[0] + R, tip[1] + R], fill=T["accent"])


# ---------------------------------------------------------------- photo helpers
_IMG = {}


def load_cover(path, w, h):
    from PIL import Image, ImageOps

    key = (path, w, h)
    if key not in _IMG:
        im = Image.open(path).convert("RGB")
        _IMG[key] = ImageOps.fit(im, (int(w * 1.12), int(h * 1.12)), Image.LANCZOS, centering=(0.5, 0.35))
    return _IMG[key]


def ken_burns(img, path, box, p, dim=0.0, radius=28):
    """Slow zoom + pan of a photo inside box (rounded), optional darkening for text on top."""
    from PIL import Image, ImageDraw

    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    big = load_cover(path, w, h)
    z = 1.12 - 0.1 * p
    cw, ch = int(big.width * z / 1.12), int(big.height * z / 1.12)
    cx = int((big.width - cw) * (0.2 + 0.6 * p)); cy = int((big.height - ch) * 0.5)
    crop = big.crop((cx, cy, cx + cw, cy + ch)).resize((w, h), Image.BILINEAR)
    if dim:
        crop = Image.blend(crop, Image.new("RGB", (w, h), T["bg"]), dim)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    img.paste(crop, (x0, y0), mask)


# ---------------------------------------------------------------- pipeline hook
def resolve(spec):
    """Try a real image; keep the drawn fallback. Returns spec + path/credit or + fallback reason."""
    spec = dict(spec or {})
    if spec.get("query") or spec.get("file"):
        got = fetch(spec)
        if got.get("path"):
            spec.update(got)
        else:
            spec["fallback"] = got.get("error", "")
    return spec


def apply(scenes, ep, mode="full", log=print):
    """Mutates the scene list: hook backdrop + cutaways. Returns a list of records for captions/QA.
    mode: 'full' (backdrop + cutaways), 'hook' (backdrop only), False (nothing)."""
    import scenes as S

    if not mode:
        return []
    records = []
    hook_i = next((i for i, s in enumerate(scenes) if s.name == "hook"), None)
    if hook_i is not None:
        hb = resolve(ep.get("hook_broll") or {"draw": guess_doodle(ep.get("kicker"), ep.get("hook"), ep.get("topic"))})
        S.with_backdrop(scenes[hook_i], hb)
        records.append(_record("hook", hb))
    if mode == "full":
        for k, spec in enumerate(ep.get("broll") or []):
            if not spec.get("say"):
                continue
            sp = resolve(spec)
            after = spec.get("after", "hook")
            at = next((i for i, s in enumerate(scenes) if s.name == after), 0) + 1
            scenes.insert(at, S.broll(sp, spec["say"], name=f"broll{k}"))
            records.append(_record(f"broll{k}", sp))
    for r in records:
        log(f"  b-roll {r['scene']:<8} {r['kind']}: {r['what']}")
    return records


def _record(scene, sp):
    if sp.get("path"):
        return {"scene": scene, "kind": "ảnh thật", "what": sp["title"], "credit": credit_line(sp),
                "page": sp.get("page", ""), "license_url": sp.get("license_url", "")}
    why = sp.get("fallback")
    return {"scene": scene, "kind": "vẽ tay", "what": (sp.get("draw") or "auto") + (f" (không lấy được ảnh: {why})" if why else "")}


def captions_block(records):
    real = [r for r in records if r["kind"] == "ảnh thật"]
    if not real:
        return ""
    lines = [f"- {r['credit']} — {r['page']}" for r in real]
    return "\n**Nguồn ảnh:**\n" + "\n".join(lines) + "\n"


if __name__ == "__main__":
    import sys

    for q in sys.argv[1:]:
        print(json.dumps(fetch({"query": q}), ensure_ascii=False, indent=2))
