"""Ảnh thật B-roll từ Wikimedia Commons: chỉ giấy phép tự do (Public domain, CC0, CC BY, CC BY-SA), có ghi công.

Ưu tiên ảnh chủ kênh tự thả vào brand/assets/broll/<tag>/ (đã có giấy phép, không cần ghi công).
Ảnh tải về lưu đệm ở social-output/_broll/<tag>/ (đã gitignore) kèm credits.json. Video dùng ảnh nào thì
captions.md có dòng "Ảnh:" ghi tác giả + giấy phép (CC BY/BY-SA bắt buộc ghi công).
Không vào được mạng → trả về rỗng, pipeline dùng hình tự vẽ.

  python broll.py casino storm        # tải trước ảnh cho vài tag
  python broll.py --all
"""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from core import BRAND, DEFAULT_OUT

CACHE = DEFAULT_OUT / "_broll"
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "QuanTikContentFactory/1.0 (educational short-video pipeline)"}
OK_LICENSE = re.compile(r"^(public domain|pd|cc0|cc by(-sa)? \d)", re.I)
RANK = {"cc0": 0, "public domain": 0, "pd": 0}


def _ctx():
    ca = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()


_DOWN = {"why": None}   # circuit breaker: once Commons refuses (429/offline), stop asking for this run


def _get(url, timeout=15):
    """One polite request; Wikimedia rate-limits bursts (HTTP 429) → give up fast and draw instead."""
    import time

    if _DOWN["why"]:
        raise RuntimeError(_DOWN["why"])
    time.sleep(0.5)
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), context=_ctx(), timeout=timeout).read()
    except Exception as ex:
        _DOWN["why"] = f"Commons không phản hồi ({type(ex).__name__}: {str(ex)[:60]})"
        raise


def _clean(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()[:120]


def fetch(tag, query, n=3, min_w=1200):
    """Tải tối đa n ảnh cho tag. Trả về list {path, title, artist, license, url}."""
    d = CACHE / tag
    cred = d / "credits.json"
    if cred.exists():
        have = json.loads(cred.read_text(encoding="utf-8"))
        if len(have) >= n:
            return have
    q = urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search",
                                "gsrsearch": query + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": 25,
                                "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1280})
    pages = json.loads(_get(f"{API}?{q}"))["query"]["pages"].values()
    cands = []
    for pg in pages:
        ii = pg["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = _clean(m.get("LicenseShortName", {}).get("value", ""))
        if not OK_LICENSE.match(lic) or ii["width"] < min_w or ii["width"] < ii["height"] * 0.6:
            continue
        cands.append((RANK.get(lic.lower(), 1), pg.get("index", 99), pg["title"], ii, lic, _clean(m.get("Artist", {}).get("value", ""))))
    cands.sort(key=lambda c: (c[0], c[1]))
    d.mkdir(parents=True, exist_ok=True)
    out = []
    for i, (_, _, title, ii, lic, artist) in enumerate(cands[:n]):
        path = d / f"{i:02d}.jpg"
        path.write_bytes(_get(ii.get("thumburl") or ii["url"], 40))
        out.append({"path": str(path), "title": title, "artist": artist or "không rõ", "license": lic,
                    "url": ii.get("descriptionurl", "")})
    cred.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def photos(tag, allow_fetch=True):
    """Ảnh đã có (hoặc tải nếu được phép) cho tag; lỗi mạng → []."""
    from illustrate import tags

    # 1) ảnh/B-roll chủ kênh tự thả vào (đã có giấy phép): brand/assets/broll/<tag>/*.jpg|png
    own = sorted(p for p in (BRAND / "assets/broll" / tag).glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if own:
        return [{"path": str(p), "title": p.name, "artist": "QuanTik", "license": "của kênh", "url": str(p)} for p in own]
    spec = tags().get(tag)
    if not spec or not spec.get("commons"):
        return []
    cred = CACHE / tag / "credits.json"
    try:
        if allow_fetch:
            return fetch(tag, spec["commons"])
        return json.loads(cred.read_text(encoding="utf-8")) if cred.exists() else []
    except Exception as ex:  # offline / blocked host: drawn illustration instead
        print(f"  broll {tag}: không tải được ảnh thật ({type(ex).__name__}) → dùng hình vẽ")
        return []


def credit_line(items):
    """Dòng ghi công cho caption: ảnh Wikimedia, ảnh trong sổ ảnh, video Pexels (bỏ ảnh của kênh)."""
    seen, out = set(), []
    for it in items:
        if it["url"] in seen or it.get("license") == "của kênh":
            continue
        seen.add(it["url"])
        if it.get("kind") == "clip":
            out.append(f"Video: {it['artist']} (Pexels) {it['url']}")
        elif it.get("kind") == "ledger":
            continue  # ảnh trong sổ ảnh được batch._write_provenance ghi ở mục "## Ảnh" (scene.images)
        else:
            out.append(f"{it['artist']} ({it['license']}, Wikimedia Commons)")
    return "Hình: " + "; ".join(out) if out else ""


if __name__ == "__main__":
    from illustrate import tags

    want = sorted(tags()) if "--all" in sys.argv else [a for a in sys.argv[1:] if not a.startswith("-")]
    for tg in want:
        got = photos(tg)
        print(tg, len(got), [g["license"] for g in got])
