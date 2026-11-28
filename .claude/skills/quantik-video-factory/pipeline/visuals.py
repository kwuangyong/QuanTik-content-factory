"""Hình ảnh cho mọi cảnh chữ (trừ chart, 3D, code, công thức): ảnh thật + hoạt hình vẽ bằng Python.

Hai lớp, cả hai chuyển động theo từng khung hình:
  1. Ảnh thật làm nền toàn khung, chuyển động Ken Burns (zoom + trượt chậm), phủ tối để chữ vẫn đọc rõ.
     Nguồn lần lượt: Pexels (env PEXELS_API_KEY) → Unsplash (env UNSPLASH_ACCESS_KEY) → Openverse (không cần key,
     chỉ lấy ảnh giấy phép cho phép dùng thương mại + chỉnh sửa) → Wikimedia Commons. Ảnh được cache.
     Không có mạng thì bỏ lớp này, video vẫn dựng được.
  2. Hoạt hình (sprite) vẽ bằng PIL ở góc phải trên: đồng xu lật, xúc xắc, người vẫy tay, mèo, cánh cửa,
     sóng, mũi tên giá, xấp tiền, bánh sinh nhật, bia bắn, bão, con lắc… Chuyển động là hàm của t, không phải ảnh tĩnh.

Chọn hình: episode JSON có "visuals": {"<tên cảnh>": "từ khoá ảnh tiếng Anh | cartoon:coin | off"}; không có thì
tự đoán từ chữ tiếng Việt trong cảnh (bảng KEYWORDS), rồi tới mặc định theo chủ đề (TOPIC_DEFAULT).
Giấy phép: mọi ảnh dùng được ghi vào credits (tác giả, giấy phép, link), pipeline chép vào captions.md.

  python visuals.py "đồng xu"        # thử tìm ảnh + sprite cho một câu
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import re
import unicodedata
import urllib.parse
import urllib.request
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps

from core import SAFE, THEME as T, W, H

CACHE = Path(__file__).resolve().parents[4] / "social-output" / "_photo_cache"
UA = "QuanTikVideoFactory/1.0 (https://quantik.io.vn; educational video pipeline)"

# Cảnh KHÔNG thêm hình (đã là hình: chart, 3D, code, công thức, bảng số; thẻ cuối giữ sạch).
SKIP = re.compile(r"^(chart|surface|code|run|formula|write|numbers|chapter|end|symbol)")

# từ khoá tiếng Việt → (truy vấn ảnh tiếng Anh, sprite)
KEYWORDS = [
    (("đồng xu", "tung xu", "mặt ngửa", "mặt sấp"), "coin toss", "coin"),
    (("xúc xắc", "gieo"), "dice", "dice"),
    (("sinh nhật",), "birthday party", "cake"),
    (("cánh cửa", "cửa có xe", "đổi cửa", " cửa"), "doors", "door"),
    (("sòng bạc", "cá cược", "đặt cược", "canh bạc", "poker"), "casino chips", "dice"),
    (("bão", "khủng hoảng", "sụp đổ", "đuôi dày", "thiên nga đen"), "storm lightning", "storm"),
    (("sóng", "biến động", "dao động", "phương sai", "volatility"), "ocean waves", "wave"),
    (("tài khoản", "vốn", "tiền", "lãi", "lỗ", "lợi nhuận"), "money cash", "money"),
    (("cổ phiếu", "thị trường", "chứng khoán", "giá", "sàn"), "stock market trading screen", "arrow"),
    (("mục tiêu", "chính xác", "sharpe", "hiệu quả"), "archery target", "target"),
    (("quay về", "trung bình", "kéo về", "hồi quy", "dây chun"), "pendulum", "pendulum"),
    (("trạng thái", "chế độ", "đèn"), "traffic light", "light"),
    (("mô phỏng", "ngẫu nhiên", "kịch bản", "may rủi"), "dice", "dice"),
    (("người", "nhà đầu tư", "bạn", "mọi người", "ai cũng"), "people crowd street", "person"),
    (("mèo", "con vật"), "cat", "cat"),
    (("thời gian", "ngày", "năm", "tháng"), "calendar clock", "clock"),
    (("dòng sông", "xu hướng", "trí nhớ", "hurst"), "river", "wave"),
]
TOPIC_DEFAULT = {
    "garch": ("stormy sea", "wave"), "hurst": ("river meander", "wave"), "ou": ("pendulum", "pendulum"),
    "hmm": ("traffic light", "light"), "monte_carlo": ("casino monte carlo", "dice"),
    "sharpe": ("archery target", "target"), "sortino": ("archery target", "target"),
    "var_cvar": ("storm lightning", "storm"), "kelly": ("poker chips", "coin"), "variance": ("ocean waves", "wave"),
}


def _norm(s):
    return unicodedata.normalize("NFC", s or "").lower()


def choose(scene, ep):
    """(photo query | None, sprite | None) for a scene."""
    if SKIP.match(scene.name):
        return None, None
    over = (ep.get("visuals") or {}).get(scene.name)
    if over == "off":
        return None, None
    q, sp = None, None
    if over:
        if over.startswith("cartoon:"):
            sp = over.split(":", 1)[1]
        else:
            q = over
    text = " " + _norm(" ".join([scene.say or ""] + list(scene.texts))) + " "
    for keys, query, sprite in KEYWORDS:
        if any(k in text for k in keys):
            q = q or query
            sp = sp or sprite
            break
    dq, ds = TOPIC_DEFAULT.get(ep.get("topic", ""), ("abstract light bokeh", "arrow"))
    return q or dq, sp or ds


# ------------------------------------------------------------------ photo search (cached)
def _get(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _pexels(q):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        return None
    d = json.loads(_get("https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": q, "orientation": "portrait", "per_page": 5}), {"Authorization": key}))
    for p in d.get("photos", []):
        return dict(url=p["src"]["large2x"], creator=p["photographer"], license="Pexels License",
                    link=p["url"], source="Pexels")


def _unsplash(q):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    d = json.loads(_get("https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(
        {"query": q, "orientation": "portrait", "per_page": 5, "content_filter": "high"}),
        {"Authorization": f"Client-ID {key}"}))
    for p in d.get("results", []):
        return dict(url=p["urls"]["regular"], creator=p["user"]["name"], license="Unsplash License",
                    link=p["links"]["html"], source="Unsplash")


def _openverse(q):
    d = json.loads(_get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
        {"q": q, "page_size": 20, "license_type": "commercial,modification", "mature": "false",
         "category": "photograph"})))
    words = [w for w in q.lower().split() if len(w) > 2]
    for p in d.get("results", []):
        about = (p.get("title") or "").lower() + " " + " ".join(t.get("name", "") for t in p.get("tags") or []).lower()
        if not any(w in about or w.rstrip("s") in about for w in words):  # ảnh lạc đề (ví dụ "dice" ra món ăn)
            continue
        if (p.get("width") or 0) >= 800 and (p.get("height") or 0) >= 600:
            lic = f"CC {p['license'].upper()} {p.get('license_version') or ''}".strip().replace("CC CC0", "CC0")
            return dict(url=f"https://api.openverse.org/v1/images/{p['id']}/thumb/?full_size=true",
                        creator=p.get("creator") or "không rõ", license=lic,
                        link=p.get("foreign_landing_url") or p.get("url"), source=p.get("source", "Openverse"))


def _wikimedia(q):
    d = json.loads(_get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrsearch": q + " filetype:bitmap",
         "gsrlimit": 5, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 1400})))
    for p in (d.get("query") or {}).get("pages", {}).values():
        ii = p["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        lic = meta.get("LicenseShortName", {}).get("value", "")
        if not re.search(r"CC0|CC BY(-SA)?|Public domain", lic, re.I):
            continue
        creator = re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "không rõ"))[:60]
        return dict(url=ii["thumburl"], creator=creator, license=lic, link=ii["descriptionurl"], source="Wikimedia")


PROVIDERS = [_pexels, _unsplash, _openverse, _wikimedia]


@lru_cache(maxsize=64)
def photo(q):
    """(PIL image, credit dict) or (None, None)."""
    if not q or os.environ.get("QUANTIK_NO_PHOTOS"):
        return None, None
    CACHE.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(q.encode()).hexdigest()[:16]
    jp, ip = CACHE / f"{h}.json", CACHE / f"{h}.jpg"
    if jp.exists() and ip.exists():
        return Image.open(ip).convert("RGB"), json.loads(jp.read_text(encoding="utf-8"))
    if jp.exists():  # cached miss
        return None, None
    for prov in PROVIDERS:
        try:
            meta = prov(q)
            if meta:
                im = Image.open(io.BytesIO(_get(meta["url"], timeout=25))).convert("RGB")
                im.thumbnail((1600, 1600))
                im.save(ip, quality=88)
                meta["query"] = q
                jp.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
                return im, meta
        except Exception as ex:  # mạng chặn, hết hạn mức, ảnh lỗi: thử nguồn tiếp theo
            last = ex
    jp.write_text(json.dumps({"miss": q}), encoding="utf-8")
    return None, None


@lru_cache(maxsize=32)
def _cover(key, im_id):
    im = _IMGS[im_id]
    big = ImageOps.fit(im, (int(W * 1.18), int(H * 1.18)), Image.LANCZOS)
    # phủ tối + chuyển màu dọc để chữ trắng luôn đọc được
    shade = Image.new("RGB", big.size, T["bg"])
    mask = Image.linear_gradient("L").resize(big.size).point(lambda v: 95 + v * 120 // 255)
    return Image.composite(shade, big, mask).filter(ImageFilter.GaussianBlur(1.2))


_IMGS = {}


def ken_burns(img, im, t, p, seed=0):
    _IMGS[id(im)] = im
    big = _cover("c", id(im))
    z = 1.0 - 0.10 * p  # zoom out chậm theo tiến độ cảnh
    cw, ch = int(big.width * z), int(big.height * z)
    ang = (seed % 4) * math.pi / 2
    dx = int((big.width - cw) * (0.5 + 0.4 * math.cos(ang) * (p - 0.5)))
    dy = int((big.height - ch) * (0.5 + 0.4 * math.sin(ang + 1) * (p - 0.5)))
    frame = big.crop((dx, dy, dx + cw, dy + ch)).resize((W, H), Image.BILINEAR)
    img.paste(frame, (0, 0))


# ------------------------------------------------------------------ sprites: animated, drawn per frame
def _ease(x):
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))


def sp_coin(d, cx, cy, r, t, p):
    sx = abs(math.cos(t * 6.0))  # lật
    y = cy - abs(math.sin(t * 3.0)) * r * 0.6
    d.ellipse([cx - r * sx, y - r, cx + r * sx, y + r], fill=(240, 190, 70), outline=(150, 105, 20), width=6)
    if sx > 0.35:
        d.text((cx, y), "₫", fill=(150, 105, 20), anchor="mm", font=_f(int(r * 1.1 * sx) + 1))


def sp_dice(d, cx, cy, r, t, p):
    face = int(t * 5) % 6 + 1 if p < 0.7 else 6
    ang = math.sin(t * 7) * 18 * (1 - p)
    bounce = abs(math.sin(t * 5)) * r * 0.3 * (1 - p)
    pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    poly = [(cx + r * (x * c - y * s), cy - bounce + r * (x * s + y * c)) for x, y in pts]
    d.polygon(poly, fill=(245, 245, 240), outline=(60, 60, 60))
    pip = {1: [(0, 0)], 2: [(-.5, -.5), (.5, .5)], 3: [(-.5, -.5), (0, 0), (.5, .5)],
           4: [(-.5, -.5), (.5, -.5), (-.5, .5), (.5, .5)], 5: [(-.5, -.5), (.5, -.5), (0, 0), (-.5, .5), (.5, .5)],
           6: [(-.5, -.5), (.5, -.5), (-.5, 0), (.5, 0), (-.5, .5), (.5, .5)]}[face]
    for x, y in pip:
        px, py = cx + r * (x * c - y * s), cy - bounce + r * (x * s + y * c)
        d.ellipse([px - r * .14, py - r * .14, px + r * .14, py + r * .14], fill=(200, 40, 50))


def sp_person(d, cx, cy, r, t, p):
    bob = math.sin(t * 4) * r * 0.05
    skin, shirt = (241, 194, 150), T["accent"]
    d.rounded_rectangle([cx - r * .45, cy - r * .05 + bob, cx + r * .45, cy + r * .95], radius=int(r * .3), fill=shirt)
    d.ellipse([cx - r * .32, cy - r * .7 + bob, cx + r * .32, cy - r * .06 + bob], fill=skin)
    d.ellipse([cx - r * .14, cy - r * .45 + bob, cx - r * .06, cy - r * .36 + bob], fill=(40, 30, 30))
    d.ellipse([cx + r * .06, cy - r * .45 + bob, cx + r * .14, cy - r * .36 + bob], fill=(40, 30, 30))
    d.arc([cx - r * .14, cy - r * .36 + bob, cx + r * .14, cy - r * .18 + bob], 20, 160, fill=(40, 30, 30), width=4)
    wave = math.sin(t * 8) * 35
    sx, sy = cx + r * .42, cy + r * .1 + bob
    a = math.radians(-60 + wave)
    ex, ey = sx + r * .6 * math.cos(a), sy + r * .6 * math.sin(a)
    d.line([sx, sy, ex, ey], fill=skin, width=int(r * .16))
    d.ellipse([ex - r * .1, ey - r * .1, ex + r * .1, ey + r * .1], fill=skin)


def sp_cat(d, cx, cy, r, t, p):
    c = (230, 150, 70)
    d.ellipse([cx - r * .6, cy, cx + r * .6, cy + r * .9], fill=c)
    d.ellipse([cx - r * .45, cy - r * .6, cx + r * .45, cy + r * .2], fill=c)
    for s in (-1, 1):
        d.polygon([(cx + s * r * .42, cy - r * .3), (cx + s * r * .35, cy - r * .8), (cx + s * r * .12, cy - r * .55)], fill=c)
    blink = (t % 3) < 0.15
    for s in (-1, 1):
        ex = cx + s * r * .18
        if blink:
            d.line([ex - r * .07, cy - r * .2, ex + r * .07, cy - r * .2], fill=(30, 30, 30), width=4)
        else:
            d.ellipse([ex - r * .07, cy - r * .28, ex + r * .07, cy - r * .12], fill=(30, 30, 30))
    sw = math.sin(t * 3) * r * .4
    d.line([cx + r * .55, cy + r * .7, cx + r * .9, cy + r * .3 + sw * .3, cx + r * .8 + sw * .5, cy - r * .1],
           fill=c, width=int(r * .14), joint="curve")


def sp_door(d, cx, cy, r, t, p):
    for i, x in enumerate((-1, 0, 1)):
        x0 = cx + x * r * .7 - r * .3
        d.rectangle([x0, cy - r * .7, x0 + r * .6, cy + r * .8], fill=(70, 50, 35), outline=(30, 20, 10), width=3)
        if i == 2:  # cửa bên phải từ từ mở
            o = _ease(p * 1.6)
            d.polygon([(x0, cy - r * .7), (x0 + r * .6 * (1 - o), cy - r * .6), (x0 + r * .6 * (1 - o), cy + r * .7),
                       (x0, cy + r * .8)], fill=(150, 100, 60))
        else:
            d.ellipse([x0 + r * .45, cy, x0 + r * .52, cy + r * .07], fill=(240, 200, 80))
        d.text((x0 + r * .3, cy - r * .9), "ABC"[i], fill=T["text"], anchor="mm", font=_f(int(r * .3)))


def sp_wave(d, cx, cy, r, t, p):
    for k, col in enumerate([(60, 140, 200), (90, 170, 220), (150, 210, 240)]):
        pts = [(cx - r + i * 2 * r / 40, cy + k * r * .25 + math.sin(i / 5 + t * 3 + k) * r * .18 * (1 + k * .3))
               for i in range(41)]
        d.line(pts, fill=col, width=int(r * .12), joint="curve")


def sp_arrow(d, cx, cy, r, t, p):
    n = 9
    k = min(n, max(2, int(n * _ease(p * 1.3)) + 1))
    ys = [0.2, -0.1, 0.3, 0.0, 0.4, 0.2, 0.6, 0.45, 0.8]
    pts = [(cx - r + i * 2 * r / (n - 1), cy + r * .6 - ys[i] * r * 1.4) for i in range(k)]
    col = T["positive"] if len(pts) < 2 or pts[-1][1] <= pts[-2][1] else T["negative"]
    d.line(pts, fill=col, width=int(r * .1), joint="curve")
    x, y = pts[-1]
    d.ellipse([x - r * .09, y - r * .09, x + r * .09, y + r * .09], fill=col)


def sp_money(d, cx, cy, r, t, p):
    n = 1 + int(5 * _ease(p * 1.5))
    for i in range(n):
        y = cy + r * .6 - i * r * .22
        d.rounded_rectangle([cx - r * .8, y - r * .14, cx + r * .8, y + r * .14], radius=8,
                            fill=(120, 190, 120), outline=(50, 110, 60), width=3)
    y = cy + r * .6 - (n - 1) * r * .22 - r * .4 - abs(math.sin(t * 4)) * r * .3
    d.rounded_rectangle([cx - r * .8, y - r * .14, cx + r * .8, y + r * .14], radius=8, fill=(140, 210, 140),
                        outline=(50, 110, 60), width=3)


def sp_cake(d, cx, cy, r, t, p):
    d.rounded_rectangle([cx - r * .8, cy, cx + r * .8, cy + r * .7], radius=14, fill=(240, 160, 180))
    d.rectangle([cx - r * .8, cy + r * .25, cx + r * .8, cy + r * .35], fill=(255, 240, 245))
    for i in (-1, 0, 1):
        x = cx + i * r * .4
        d.rectangle([x - r * .04, cy - r * .35, x + r * .04, cy], fill=(120, 180, 240))
        fl = r * (.12 + .04 * math.sin(t * 15 + i))
        d.ellipse([x - fl * .6, cy - r * .35 - fl * 2, x + fl * .6, cy - r * .35], fill=(255, 200, 60))


def sp_target(d, cx, cy, r, t, p):
    for k, col in enumerate([(240, 240, 240), (220, 60, 60), (240, 240, 240), (220, 60, 60)]):
        rr = r * (1 - k * .22)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
    a = _ease(p * 1.8)
    x = cx - r * 2.2 * (1 - a)
    d.line([x - r * .9, cy - r * .1 * (1 - a), x, cy], fill=(90, 60, 30), width=int(r * .07))
    d.polygon([(x, cy), (x - r * .2, cy - r * .1), (x - r * .2, cy + r * .1)], fill=(60, 60, 60))


def sp_storm(d, cx, cy, r, t, p):
    d.ellipse([cx - r, cy - r * .6, cx, cy + r * .1], fill=(120, 130, 150))
    d.ellipse([cx - r * .5, cy - r * .9, cx + r * .6, cy + r * .1], fill=(140, 150, 170))
    d.ellipse([cx, cy - r * .55, cx + r, cy + r * .1], fill=(120, 130, 150))
    if (t * 2.5) % 1 < 0.35:
        d.polygon([(cx, cy), (cx - r * .25, cy + r * .5), (cx, cy + r * .45), (cx - r * .15, cy + r),
                   (cx + r * .25, cy + r * .35), (cx + r * .02, cy + r * .4)], fill=(255, 220, 60))
    for i in range(6):
        x = cx - r * .8 + i * r * .3
        y = cy + r * .2 + ((t * 2 + i * .37) % 1) * r * .8
        d.line([x, y, x - r * .06, y + r * .15], fill=(150, 190, 240), width=4)


def sp_pendulum(d, cx, cy, r, t, p):
    a = math.radians(40 * math.sin(t * 3) * math.exp(-p * 1.2))
    top = (cx, cy - r * .8)
    bx, by = cx + r * 1.4 * math.sin(a), cy - r * .8 + r * 1.4 * math.cos(a)
    d.line([cx - r * .5, top[1], cx + r * .5, top[1]], fill=T["muted"], width=6)
    d.line([top, (bx, by)], fill=T["text"], width=4)
    d.ellipse([bx - r * .22, by - r * .22, bx + r * .22, by + r * .22], fill=T["accent"])


def sp_light(d, cx, cy, r, t, p):
    d.rounded_rectangle([cx - r * .4, cy - r, cx + r * .4, cy + r], radius=20, fill=(40, 40, 40))
    on = int(t * 1.2) % 3
    for i, col in enumerate([(230, 60, 60), (240, 190, 50), (70, 200, 110)]):
        y = cy - r * .62 + i * r * .62
        c = col if i == on else tuple(v // 4 for v in col)
        d.ellipse([cx - r * .25, y - r * .25, cx + r * .25, y + r * .25], fill=c)


def sp_clock(d, cx, cy, r, t, p):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 240, 235), outline=T["accent"], width=8)
    for k in range(12):
        a = k * math.pi / 6
        d.line([cx + r * .8 * math.sin(a), cy - r * .8 * math.cos(a), cx + r * .9 * math.sin(a), cy - r * .9 * math.cos(a)],
               fill=(60, 60, 60), width=4)
    for L, sp, wd in ((.5, .5, 8), (.8, 4, 5)):
        a = t * sp
        d.line([cx, cy, cx + r * L * math.sin(a), cy - r * L * math.cos(a)], fill=(40, 40, 40), width=wd)


SPRITES = {k[3:]: v for k, v in globals().items() if k.startswith("sp_")}


@lru_cache(maxsize=16)
def _f(size):
    import frames as F
    return F.font("sans-black", max(8, size))


def sprite(img, name, t, p, box=None):
    """Draw sprite in its own RGBA layer with a soft round badge so it reads on top of any photo."""
    fn = SPRITES.get(name)
    if not fn:
        return
    box = box or (SAFE["right"] - 210, 288, SAFE["right"], 468)
    w, h = box[2] - box[0], box[3] - box[1]
    pop = _ease(min(1.0, t / 0.35))  # nảy vào khi cảnh bắt đầu
    layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([w * .1, h * .05, w * 1.9, h * 1.95], fill=(*T["surface"], 210), outline=(*T["accent"], 255), width=6)
    fn(d, w, h, min(w, h) * .62, t, p)
    s = max(1, int(w * pop)), max(1, int(h * pop))
    layer = layer.resize(s, Image.LANCZOS)
    img.paste(layer, (box[0] + (w - s[0]) // 2, box[1] + (h - s[1]) // 2), layer)


# ------------------------------------------------------------------ wire into scenes
def illustrate(scenes, ep, kind="video"):
    """Add photo backdrop + sprite to every text scene. Returns list of photo credits used."""
    credits = []
    if kind != "video" or ep.get("visuals") == "off":
        return credits
    for i, s in enumerate(scenes):
        q, sp = choose(s, ep)
        if q is None and sp is None:
            continue
        im, meta = photo(q) if q else (None, None)
        if im is None and q:  # từ khoá không ra ảnh hợp lệ → ảnh mặc định của chủ đề
            im, meta = photo(TOPIC_DEFAULT.get(ep.get("topic", ""), ("abstract light bokeh",))[0])
        if meta and meta not in credits:
            credits.append(meta)

        def backdrop(img, t, p, im=im, seed=i):
            if im is not None:
                ken_burns(img, im, t, p, seed)

        def draw(img, t, p, orig=s.draw, sp=sp):
            orig(img, t, p)
            if sp:
                sprite(img, sp, t, p)

        s.backdrop = backdrop
        s.draw = draw
    return credits


def credit_lines(credits):
    return [f"Ảnh: {c['creator']} / {c['source']} ({c['license']}) {c['link']}" for c in credits]


if __name__ == "__main__":
    import sys
    from render import Scene
    sc = Scene("statement", " ".join(sys.argv[1:]) or "Tung đồng xu 50 lần")
    print(choose(sc, {"topic": ""}))
    q, _ = choose(sc, {"topic": ""})
    im, meta = photo(q)
    print(meta or "không lấy được ảnh (mạng?)")
