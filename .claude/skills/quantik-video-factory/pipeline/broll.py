"""Real-world imagery for every video: photos from Openverse (free, no key) and photos/video B-roll from Pexels
(needs PEXELS_API_KEY). Rule from the product owner: no video ships as text-on-dark-only; scenes carry real
objects, places and people behind the content (brand/identity.md › Hình ảnh thật & B-roll).

Each pick is cached under social-output/_broll/ with its attribution, and every video writes credits.md.

    python broll.py "poker chips" --n 3          # search + download, print attribution
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from core import DEFAULT_OUT

CACHE = Path(DEFAULT_OUT) / "_broll"
UA = "QuanTik-content-factory/1.0 (social video pipeline)"
# Openverse licences we may use in a commercial, edited video: CC0, public domain mark, CC BY (credit required).
# Not BY-SA (would force the whole video under BY-SA), not NC (brand channel = commercial), not ND (we crop/zoom).
OPENVERSE_LICENSES = "cc0,pdm,by"
LICENSE_URL = {"cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
               "pdm": "https://creativecommons.org/publicdomain/mark/1.0/",
               "by": "https://creativecommons.org/licenses/by/{v}/"}

# Openverse "photograph" still returns drawings, posters and stock-art series; drop them by title/creator/tag.
EXCLUDE = ("patent", "drawing", "illustration", "vector", "clipart", "clip art", "poster", "wall art", "diagram",
           "infographic", "logo", "cartoon", "screenshot", "meme", "nude", "injury", "accident", "hospital",
           "crutch", "funeral", "protest", "police")

# Default searches per topic when an episode gives no "broll": concrete objects, places and people.
TOPIC_QUERIES = {
    "kelly": ["poker chips", "poker table", "casino cards", "man thinking", "dice"],
    "monte_carlo": ["crossroads", "city crowd", "forest path", "fork in the road", "night city"],
    "var_cvar": ["storm clouds", "lightning", "rough sea", "worried man", "umbrella rain"],
    "garch": ["storm ocean waves", "calm lake", "thunderstorm", "earthquake", "volcano"],
    "hurst": ["river", "ocean waves", "footprints sand", "maze", "pendulum"],
    "hmm": ["traffic lights", "four seasons tree", "weather sky", "crowd street", "mood faces"],
    "sharpe": ["mountain climber", "tightrope", "runner track", "scale balance", "race car"],
    "ou": ["rubber band", "pendulum", "elastic", "spring coil", "boat anchor"],
}
GENERIC = ["stock trader screen", "office desk laptop", "city skyline night", "people walking street",
           "coffee laptop work", "man looking at phone", "woman working laptop", "calculator notebook"]


def _get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _cache_file(url, ext):
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ext)


def search_openverse(query, n=4):
    """Real photographs only, ranked by how many query words appear in the title/tags; drawings, posters and
    off-topic shots (no matching word) are dropped."""
    params = {"q": query, "license": OPENVERSE_LICENSES, "mature": "false", "category": "photograph",
              "size": "large,medium", "page_size": max(n * 4, 20)}
    results = json.loads(_get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params))).get("results", [])
    words = {w for w in query.lower().split() if len(w) > 2}

    def score(r):
        text = " ".join([r.get("title") or "", r.get("creator") or ""] +
                        [t.get("name", "") for t in (r.get("tags") or [])]).lower()
        if any(b in text for b in EXCLUDE):
            return -1
        return sum(w.rstrip("s") in text for w in words)

    ranked = sorted(((score(r), i, r) for i, r in enumerate(results)), key=lambda x: (-x[0], x[1]))
    results = [r for sc, _, r in ranked if sc >= max(1, (len(words) + 1) // 2)]
    out = []
    for r in results:
        lic, ver = r.get("license", ""), r.get("license_version", "")
        # download through Openverse's own image proxy (full size): works where the origin host (Flickr,
        # Wikimedia…) is blocked or slow, and the licence/credit stay those of the original
        out.append({"kind": "image", "url": f"https://api.openverse.org/v1/images/{r['id']}/thumb/?full_size=true",
                    "source": "Openverse/" + (r.get("source") or ""),
                    "title": r.get("title") or query, "creator": r.get("creator") or "unknown",
                    "page": r.get("foreign_landing_url") or r.get("url"),
                    "license": f"CC {lic.upper()} {ver}".strip() if lic not in ("cc0", "pdm") else lic.upper(),
                    "license_url": LICENSE_URL.get(lic, "").format(v=ver), "query": query})
    return out


def search_pexels(query, n=4, video=False):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return []
    kind = "videos/search" if video else "v1/search"
    q = urllib.parse.urlencode({"query": query, "orientation": "portrait", "per_page": max(n * 2, 8)})
    data = json.loads(_get(f"https://api.pexels.com/{kind}?{q}", {"Authorization": key}))
    out = []
    for r in data.get("videos" if video else "photos", []):
        if video:
            files = sorted((f for f in r.get("video_files", []) if (f.get("width") or 0) >= 720),
                           key=lambda f: f.get("width") or 0)
            if not files:
                continue
            url, creator = files[0]["link"], (r.get("user") or {}).get("name", "Pexels")
        else:
            url, creator = r["src"].get("portrait") or r["src"]["large2x"], r.get("photographer", "Pexels")
        out.append({"kind": "video" if video else "image", "url": url, "source": "Pexels", "title": query,
                    "creator": creator, "page": r.get("url", ""), "license": "Pexels License",
                    "license_url": "https://www.pexels.com/license/", "query": query})
    return out


def download(item):
    """Fetch the file into the cache; video B-roll is decoded once to a frame folder (1080×1920, cover crop)."""
    ext = ".mp4" if item["kind"] == "video" else ".jpg"
    path = _cache_file(item["url"], ext)
    if not path.exists():
        path.write_bytes(_get(item["url"], timeout=60))
    item = dict(item, path=str(path))
    if item["kind"] == "video":
        frames = path.with_suffix("")
        if not frames.exists():
            frames.mkdir()
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(path), "-t", "12", "-vf",
                            "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                            "-q:v", "4", str(frames / "%04d.jpg")], check=True)
        item["frames"] = str(frames)
    return item


def pick(queries, count, prefer_video=True, log=print):
    """`count` distinct downloaded items, cycling through queries. Pexels first (video, then photo) when a key
    is set, Openverse photos otherwise or as fallback. Returns (items, errors)."""
    items, seen, errors = [], set(), []
    queries = [q for q in queries if q] or GENERIC
    rounds = 0
    while len(items) < count and rounds < 3:
        for q in queries:
            if len(items) >= count:
                break
            cands = []
            for fn in ((lambda: search_pexels(q, video=True)) if prefer_video else None,
                       lambda: search_pexels(q), lambda: search_openverse(q)):
                if fn is None:
                    continue
                try:
                    cands += fn()
                except Exception as ex:  # network blocked, API down, bad key…
                    errors.append(f"{q}: {type(ex).__name__}: {str(ex)[:80]}")
            for c in cands:
                if c["url"] in seen:
                    continue
                seen.add(c["url"])
                try:
                    items.append(download(c))
                    break
                except Exception as ex:
                    errors.append(f"download {c['url'][:60]}: {type(ex).__name__}")
        rounds += 1
    if errors and log:
        log(f"  b-roll: {len(errors)} lỗi (vd. {errors[0]})")
    return items, errors


def credit_line(item):
    return f"{item['creator']} / {item['source']} ({item['license']})"


def credits_md(items):
    rows = ["# Nguồn hình ảnh / Image credits", ""]
    for i, it in enumerate(items, 1):
        rows.append(f"{i}. \"{it['title']}\" — {it['creator']} · {it['source']} · {it['page']} · "
                    f"{it['license']} {it.get('license_url', '')}".rstrip())
    return "\n".join(rows) + "\n"


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--n", type=int, default=3)
    a = ap.parse_args()
    got, errs = pick([a.query], a.n)
    for it in got:
        print(it["kind"], it["path"], "|", credit_line(it))
    if errs:
        print("errors:", errs[:3])
