"""Images for people, firms and events mentioned in an episode — openly licensed photos or clearly-labelled
illustrations drawn in code. Every image goes through knowledge/images/ledger.json (schemas/image_ledger.schema.json).

Two kinds only (brand/compliance.md: no copyrighted images without a licence):
  photo         from Wikimedia Commons, licence must be public domain / CC0 / CC BY / CC BY-SA (no NC, ND, fair use).
                Author + licence are shown on screen and in captions/sources.md.
  illustration  drawn here with the brand palette (initials avatar, person card, event card, playing cards).
                Always labelled "Ảnh minh hoạ"; never a fake photo of a real person.

  python images.py search "Claude Shannon"                    # Commons candidates with their licences
  python images.py fetch "File:ClaudeShannon MFO3807.jpg" --id shannon --subject "Claude Shannon"
  python images.py person --id thorp --name "Edward O. Thorp" --role "nhà toán học, nhà đầu tư"
  python images.py event  --id ltcm-1998 --title "LTCM được giải cứu" --when "9/1998" --where "New York"
  python images.py cards  --id kuhn-cards --cards J,Q,K
  python images.py list
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

from core import KNOWLEDGE, THEME as T, font

IMG_DIR = KNOWLEDGE / "images"
FILES = IMG_DIR / "files"
LEDGER = IMG_DIR / "ledger.json"
API = "https://commons.wikimedia.org/w/api.php"
UA = "quantik-content-factory/1.0 (educational short videos; attribution shown on screen)"
# Licences we may republish with attribution. NC/ND/fair-use are refused.
FREE = re.compile(r"^(public domain|pd\b|pd-|cc0|cc[- ]by(-sa)?([- ]\d(\.\d)?)?\b)", re.I)
NOT_FREE = re.compile(r"\b(nc|nd|fair use|non-?free|all rights reserved)\b", re.I)
W, H = 1080, 760


# ---------------------------------------------------------------- ledger
def ledger():
    if not LEDGER.exists():
        return {"version": 1, "images": []}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def index():
    return {i["id"]: i for i in ledger()["images"]}


def _save_entry(entry):
    data = ledger()
    data["images"] = [i for i in data["images"] if i["id"] != entry["id"]] + [entry]
    data["images"].sort(key=lambda i: i["id"])
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entry


def path_of(entry):
    return IMG_DIR / entry["file"]


def is_free(license_name):
    return bool(license_name) and bool(FREE.search(license_name.strip())) and not NOT_FREE.search(license_name)


# ---------------------------------------------------------------- Wikimedia Commons
def _api(params, opener=None):
    q = urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with (opener or urllib.request.urlopen)(req, timeout=20) as r:
        return json.loads(r.read())


def _strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def commons_info(title, opener=None):
    """imageinfo + licence metadata for one File: page."""
    d = _api({"action": "query", "titles": title, "prop": "imageinfo", "iiprop": "url|extmetadata|size",
              "iiurlwidth": 1080}, opener)
    page = d["query"]["pages"][0]
    if page.get("missing"):
        raise SystemExit(f"không có trang {title} trên Commons")
    ii = page["imageinfo"][0]
    meta = {k: _strip(v.get("value", "")) for k, v in ii.get("extmetadata", {}).items()}
    return {"title": page["title"], "page_url": ii.get("descriptionurl"), "thumb_url": ii.get("thumburl") or ii["url"],
            "license": meta.get("LicenseShortName", ""), "license_url": meta.get("LicenseUrl", ""),
            "author": meta.get("Artist", "") or meta.get("Credit", ""), "description": meta.get("ImageDescription", "")[:300],
            "date": meta.get("DateTimeOriginal", "")}


def search(query, limit=10, opener=None):
    d = _api({"action": "query", "list": "search", "srsearch": query, "srnamespace": 6, "srlimit": limit}, opener)
    out = []
    for hit in d["query"]["search"]:
        try:
            info = commons_info(hit["title"], opener)
        except Exception as ex:  # one broken page must not stop the listing
            info = {"title": hit["title"], "license": f"? ({ex})", "author": ""}
        info["free"] = is_free(info.get("license", ""))
        out.append(info)
    return out


def fetch(title, img_id, subject, depicts=None, opener=None):
    info = commons_info(title, opener)
    if not is_free(info["license"]):
        raise SystemExit(f"từ chối {title}: giấy phép '{info['license'] or 'không rõ'}' không cho phép dùng lại")
    if not info["author"]:
        raise SystemExit(f"từ chối {title}: không có tác giả để ghi công")
    req = urllib.request.Request(info["thumb_url"], headers={"User-Agent": UA})
    with (opener or urllib.request.urlopen)(req, timeout=30) as r:
        raw = r.read()
    FILES.mkdir(parents=True, exist_ok=True)
    ext = Path(urllib.parse.urlparse(info["thumb_url"]).path).suffix.lower() or ".jpg"
    f = FILES / f"{img_id}{ext}"
    f.write_bytes(raw)
    author = info["author"][:60]
    return _save_entry({
        "id": img_id, "kind": "photo", "subject": subject, "depicts": depicts or info["description"] or subject,
        "file": f"files/{f.name}", "source_url": info["page_url"], "author": author, "license": info["license"],
        "license_url": info["license_url"], "credit": f"Ảnh: {author} · {info['license']} · Wikimedia Commons",
        "retrieved": dt.date.today().isoformat()})


# ---------------------------------------------------------------- illustrations (never photo-like)
def _canvas():
    img = Image.new("RGB", (W, H), T["surface"])
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(18, 32, 25))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(18, 32, 25))
    return img, d


def _initials(name):
    parts = [p for p in re.split(r"[\s.\-–]+", name) if p and p[0].isalpha()]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else name[:2].upper()


def _label(d):
    f = font("sans-bold", 26)
    txt = "ẢNH MINH HOẠ · không phải ảnh thật"
    w = d.textlength(txt, font=f)
    d.rounded_rectangle([W - w - 60, H - 64, W - 24, H - 20], radius=20, fill=T["raised"], outline=T["border"], width=2)
    d.text((W - w - 42, H - 58), txt, font=f, fill=T["muted"])


def _avatar(d, cx, cy, r, text, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=T["raised"], outline=color, width=8)
    f = font("sans-black", int(r * 0.9))
    w = d.textlength(text, font=f)
    d.text((cx - w / 2, cy - r * 0.62), text, font=f, fill=color)


def _wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    return lines + ([cur] if cur else [])


def _save_illustration(img, img_id, subject, depicts, how):
    FILES.mkdir(parents=True, exist_ok=True)
    f = FILES / f"{img_id}.png"
    img.save(f)
    return _save_entry({"id": img_id, "kind": "illustration", "subject": subject, "depicts": depicts,
                        "file": f"files/{f.name}", "source_url": "", "author": "QuanTik content factory",
                        "license": "nội bộ QuanTik", "license_url": "",
                        "credit": "Ảnh minh hoạ tạo bằng code, không phải ảnh thật",
                        "generator": how, "retrieved": dt.date.today().isoformat()})


def person(img_id, name, role="", note=""):
    img, d = _canvas()
    _avatar(d, 250, 330, 170, _initials(name), T["accent"])
    y = 190
    for ln in _wrap(d, name, font("sans-black", 72), 560)[:2]:
        d.text((470, y), ln, font=font("sans-black", 72), fill=T["text"]); y += 86
    for ln in _wrap(d, role, font("sans-bold", 40), 560)[:3]:
        d.text((470, y + 10), ln, font=font("sans-bold", 40), fill=T["neutral"]); y += 52
    if note:
        for ln in _wrap(d, note, font("sans", 32), 560)[:2]:
            d.text((470, y + 30), ln, font=font("sans", 32), fill=T["muted"]); y += 42
    _label(d)
    return _save_illustration(img, img_id, name, f"thẻ nhân vật (chữ cái đầu) — {name}",
                              f"images.py person --name {name!r} --role {role!r}")


def event(img_id, title, when="", where=""):
    img, d = _canvas()
    d.rounded_rectangle([60, 80, 380, 400], radius=36, fill=T["raised"], outline=T["accent"], width=6)
    d.rectangle([60, 80, 380, 160], fill=T["accent"])
    fw = font("sans-black", 64 if len(when) <= 7 else 44)
    tw = d.textlength(when, font=fw)
    d.text((220 - tw / 2, 230), when, font=fw, fill=T["text"])
    y = 110
    for ln in _wrap(d, title, font("sans-black", 64), 580)[:4]:
        d.text((440, y), ln, font=font("sans-black", 64), fill=T["text"]); y += 78
    if where:
        d.text((440, y + 20), "Nơi: " + where, font=font("sans-bold", 38), fill=T["neutral"])
    _label(d)
    return _save_illustration(img, img_id, title, f"thẻ sự kiện — {title} {when}",
                              f"images.py event --title {title!r} --when {when!r} --where {where!r}")


def cards(img_id, ranks=("J", "Q", "K")):
    img, d = _canvas()
    n = len(ranks)
    cw, ch, gap = 230, 330, 60
    x0 = (W - n * cw - (n - 1) * gap) // 2
    suits = ["♠", "♥", "♣", "♦"]
    for i, r in enumerate(ranks):
        x, y = x0 + i * (cw + gap), 170 + (20 if i % 2 else 0)
        col = T["negative"] if suits[i % 4] in "♥♦" else T["text"]
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=24, fill=(28, 44, 36), outline=T["accent"], width=5)
        d.text((x + 22, y + 14), r, font=font("sans-black", 64), fill=col)
        f = font("sans-black", 150)
        w = d.textlength(r, font=f)
        d.text((x + (cw - w) / 2, y + 100), r, font=f, fill=col)
    _label(d)
    return _save_illustration(img, img_id, "lá bài " + ", ".join(ranks), "các lá bài " + " ".join(ranks),
                              f"images.py cards --cards {','.join(ranks)}")


def avatar_thumb(entry, size=120):
    """Small square thumbnail of any ledger image (used on timeline dots)."""
    im = Image.open(path_of(entry)).convert("RGB")
    if entry["kind"] == "illustration" and entry.get("generator", "").startswith("images.py person"):
        im = im.crop((60, 140, 440, 520))     # the initials avatar
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, (im.height - s) // 2, (im.width + s) // 2, (im.height + s) // 2))
    return im.resize((size, size), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--limit", type=int, default=10)
    s = sub.add_parser("fetch"); s.add_argument("title"); s.add_argument("--id", required=True)
    s.add_argument("--subject", required=True); s.add_argument("--depicts")
    s = sub.add_parser("person"); s.add_argument("--id", required=True); s.add_argument("--name", required=True)
    s.add_argument("--role", default=""); s.add_argument("--note", default="")
    s = sub.add_parser("event"); s.add_argument("--id", required=True); s.add_argument("--title", required=True)
    s.add_argument("--when", default=""); s.add_argument("--where", default="")
    s = sub.add_parser("cards"); s.add_argument("--id", required=True); s.add_argument("--cards", default="J,Q,K")
    sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "search":
        for r in search(a.query, a.limit):
            print(f"{'✅' if r['free'] else '⛔'} {r['title']}\n    {r.get('license')} · {r.get('author', '')[:60]}")
    elif a.cmd == "fetch":
        print(json.dumps(fetch(a.title, a.id, a.subject, a.depicts), ensure_ascii=False, indent=2))
    elif a.cmd == "person":
        print(person(a.id, a.name, a.role, a.note)["file"])
    elif a.cmd == "event":
        print(event(a.id, a.title, a.when, a.where)["file"])
    elif a.cmd == "cards":
        print(cards(a.id, tuple(a.cards.split(",")))["file"])
    else:
        for i in ledger()["images"]:
            print(f"{i['id']:<22} {i['kind']:<13} {i['subject']:<28} {i['credit']}")


if __name__ == "__main__":
    sys.exit(main())
