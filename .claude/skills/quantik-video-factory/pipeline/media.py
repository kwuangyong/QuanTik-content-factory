"""Real images from Wikimedia Commons (the media library behind Wikipedia), with license + attribution.

Only freely licensed files are accepted: public domain, CC0, CC BY, CC BY-SA (no NC/ND, no fair use).
Every image used in a video is recorded in CREDITS and printed on screen and in captions.md.

  spec: {"commons": "File:Exact title.jpg"}  or  {"q": "search words", "pick": 0}
  python media.py "roulette wheel"            # list candidates with license (to choose a file title)
Hosts: commons.wikimedia.org (API), upload.wikimedia.org (files). Cache: social-output/_media/.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core import DEFAULT_OUT  # noqa: E402

API = "https://commons.wikimedia.org/w/api.php"
UA = "QuanTikContentBot/1.0 (educational short videos; contact via quantik.io.vn)"
CACHE = DEFAULT_OUT / "_media"
OK_LICENSE = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?( \d\.\d)?|cc by(-sa)? \d\.\d( \w+)?)", re.I)
BAD = re.compile(r"\b(nc|nd|fair use|non-free)\b", re.I)
CREDITS: list[dict] = []


def _get(url, tries=5, wait=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:  # 429 / transient
            if i == tries - 1:
                raise
            if getattr(e, "code", None) == 400:
                raise
            time.sleep(wait * (i + 1))


def _api(**params):
    params.update(format="json", formatversion="2")
    return json.loads(_get(API + "?" + urllib.parse.urlencode(params)))


def _clean(s):
    s = re.sub(r"<[^>]+>", "", html.unescape(s or "")).strip()
    return re.sub(r"\s+", " ", s)[:80]


def _info(pages, width):
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [None])[0]
        if not ii:
            continue
        m = ii.get("extmetadata", {})
        lic = _clean(m.get("LicenseShortName", {}).get("value", ""))
        if not lic or BAD.search(lic) or not OK_LICENSE.search(lic):
            continue
        thumb = (ii.get("thumburl") or ii["url"]).replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/")
        out.append({"title": p["title"], "thumb": thumb.split("?")[0], "license": lic,
                    "artist": _clean(m.get("Artist", {}).get("value", "")) or "không rõ",
                    "page": ii.get("descriptionurl", ""), "w": ii.get("thumbwidth"), "h": ii.get("thumbheight"),
                    "mime": ii.get("mime", "")})
    return out


OPENVERSE = "https://api.openverse.org/v1/images/"
LIC = {"by": "CC BY", "by-sa": "CC BY-SA", "cc0": "CC0", "pdm": "Public domain"}


def search(q, width=1080, limit=12):
    """Openverse index of Wikimedia Commons (the Commons API rate-limits this network): free licenses only."""
    qs = urllib.parse.urlencode({"q": q, "source": "wikimedia", "license": "by,by-sa,cc0,pdm", "page_size": limit,
                                 "mature": "false"})
    d = json.loads(_get(OPENVERSE + "?" + qs))
    out = []
    for r in d.get("results", []):
        url = r.get("url", "")
        if "upload.wikimedia.org" not in url or not re.search(r"\.(jpe?g|png)$", url, re.I):
            continue
        if (r.get("width") or 0) < 700 or (r.get("filesize") or 0) > 15e6:
            continue
        lic = LIC.get(r.get("license"), r.get("license", "")) + (f" {r['license_version']}" if r.get("license_version")
                                                                 and r.get("license") not in ("cc0", "pdm") else "")
        out.append({"title": "File:" + urllib.parse.unquote(url.rsplit("/", 1)[-1]).replace("_", " "), "thumb": url,
                    "license": lic, "artist": _clean(r.get("creator") or "") or "không rõ",
                    "page": r.get("foreign_landing_url", ""), "w": r.get("width"), "h": r.get("height"), "mime": ""})
    return out


def by_title(title, width=1080):
    name = title.replace("File:", "").rsplit(".", 1)[0]
    c = search(name)
    exact = [x for x in c if x["title"].lower().startswith(title.lower().rsplit(".", 1)[0])]
    return exact or c


def _thumbs(url):
    """Wikimedia only serves standard thumbnail widths to this network (originals and odd sizes get 429)."""
    m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/([^/?]+)$", url)
    if not m:
        return [url]
    base, h, name = m.groups()
    return [f"{base}/thumb/{h}/{name}/{w}px-{name}" for w in (960, 500)]


def fetch(spec, width=1080):
    """spec → (PIL.Image RGB, credit dict) or (None, None). Cached on disk."""
    if not spec:
        return None, None
    key = hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16] + f"-{width}"
    CACHE.mkdir(parents=True, exist_ok=True)
    jp, ip = CACHE / f"{key}.json", CACHE / f"{key}.jpg"
    if jp.exists() and ip.exists():
        meta = json.loads(jp.read_text(encoding="utf-8"))
    elif __import__("os").environ.get("QT_MEDIA_OFFLINE"):
        return None, None          # render from cache only; prefetch fills it
    else:
        try:
            cands = by_title(spec["commons"], width) if spec.get("commons") else search(spec["q"], width)
        except Exception as e:
            print(f"  media: {spec} → {e}")
            return None, None
        if not cands:
            print(f"  media: no freely licensed result for {spec}")
            return None, None
        meta = None
        for c in cands[spec.get("pick", 0):]:
            try:
                im = None
                for u in _thumbs(c["thumb"]):
                    try:
                        im = Image.open(__import__("io").BytesIO(_get(u, tries=4, wait=15))).convert("RGB")
                        break
                    except Exception:
                        continue
                if im is None:
                    raise RuntimeError("no thumbnail size available")
                im.thumbnail((1600, 1600))
                im.save(ip, quality=90)
                meta = c
                break
            except Exception as e:
                print(f"  media: skip {c['title']}: {e}")
        if meta is None:
            return None, None
        jp.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if meta["title"] not in [c["title"] for c in CREDITS]:
        CREDITS.append(meta)
    return Image.open(ip).convert("RGB"), meta


def credit_line(meta):
    t = meta["title"].replace("File:", "")
    return f"Ảnh: {meta['artist']} · {meta['license']} · Wikimedia Commons ({t[:40]})"




def prefetch(pause=30):
    """Resolve and cache every spec in knowledge/media.json, slowly: wiki images first, then hook, then dark
    backgrounds (Wikimedia rate-limits this network hard). Safe to re-run: cached specs are skipped."""
    from core import KNOWLEDGE
    mp = {k: v for k, v in json.loads((KNOWLEDGE / "media.json").read_text(encoding="utf-8")).items()
          if not k.startswith("_")}
    for topic, d in mp.items():
        for slot in ("wiki", "hook_bg", "dark_bg"):
            if not d.get(slot):
                continue
            key = hashlib.sha1(json.dumps(d[slot], sort_keys=True).encode()).hexdigest()[:16] + "-1080"
            if (CACHE / f"{key}.json").exists():
                continue
            try:
                im, meta = fetch(d[slot])
            except Exception as e:
                im, meta = None, None
                print("  error", e)
            print(f"{topic:<16} {slot:<8} {(meta or {}).get('license', ''):<14} {(meta or {}).get('title', '—')}", flush=True)
            time.sleep(pause)

if __name__ == "__main__":
    if sys.argv[1:] == ["--prefetch"]:
        prefetch()
    else:
        for c in search(" ".join(sys.argv[1:])):
            print(f"{c['license']:<14} {c['artist'][:28]:<28} {c['title']}")
