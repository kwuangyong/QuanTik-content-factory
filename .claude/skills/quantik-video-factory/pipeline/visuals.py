"""Visual assets for any episode: find who/what is mentioned, get a real licensed image or make an illustration,
register it, place it in a scene, and run the image QA. Skill: .claude/skills/quantik-visual-assets/SKILL.md

  python visuals.py auto ../episodes/<id>.json            # plan only: what is mentioned, what image each would get
  python visuals.py auto ../episodes/<id>.json --write    # do it: fetch/make images, add entities, place them
  python visuals.py auto ../episodes/<id>.json --write --offline   # illustrations only (no network)
  python visuals.py find "Claude Shannon"                 # real-image candidates on Wikimedia Commons (licence shown)

Order of preference for every person / firm / place / event:
  1. an image already in knowledge/images/ledger.json (reused, never downloaded twice);
  2. a Wikimedia Commons file whose title or description names the subject AND whose licence is free
     (public domain, CC0, CC BY, CC BY-SA) — credit and licence go on screen;
  3. an illustration drawn in code (initials card for a person, building card for a firm, date card for an event),
     always labelled "Ảnh minh hoạ".
Generic people and objects for storytelling (an investor, a poker table…) come from figures.py / pictos.py and need
no entity: they are not anybody in particular.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

import check_images  # noqa: E402
import images as IMG  # noqa: E402
from core import KNOWLEDGE, SKILL  # noqa: E402

FIRM = re.compile(r"\b(Labs?|Capital|Bank|Inc|Corp|Management|Technologies|Partners|Fund|Group|University|Institute|"
                  r"Exchange|Securities|Reserve)\b")


NOT_PORTRAIT = re.compile(r"logo|signature|autograph|grave|tomb|stamp|coat of arms|poster|plaque|seal|icon|map", re.I)


def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40]


def full_names():
    """surname → full author name from the source ledger ("Odean" → "Terrance Odean")."""
    data = json.loads((KNOWLEDGE / "sources/ledger.json").read_text(encoding="utf-8"))
    out = {}
    for s in data["sources"]:
        for a in s.get("authors", []):
            parts = re.findall(r"[A-Z][a-z]{2,}", a)
            if parts:
                out.setdefault(parts[-1], a)
    return out


def find_real(name, opener=None):
    """Best free-licence Commons file that actually names the subject, or None."""
    tokens = [t.lower() for t in re.findall(r"[A-Za-z]{3,}", name)]
    cands = []
    try:
        cands += IMG.category(name, 20, opener)
    except Exception:
        pass
    try:
        cands += IMG.search(f'"{name}" filetype:bitmap', 15, opener)
    except Exception as ex:
        if "429" in str(ex) or "URLError" in type(ex).__name__ or "Forbidden" in str(ex):
            raise
    for c in cands:
        blob = (c["title"] + " " + c.get("description", "")).lower()
        if NOT_PORTRAIT.search(c["title"]) or not re.search(r"\.(jpe?g|png|tiff?)$", c["title"], re.I):
            continue
        if c.get("free") and all(t in blob for t in tokens) and c.get("author"):
            return dict(c, origin="commons")
    try:   # second source: Openverse (Flickr, museums, libraries) — title must name the subject too
        for c in IMG.openverse_search(name, 20, opener):
            if c["free"] and c["author"] and all(t in c["title"].lower() for t in tokens) \
                    and not NOT_PORTRAIT.search(c["title"]) and (c.get("width") or 0) >= 400:
                return c
    except Exception:
        pass
    return None


def fetch_found(c, img_id, name, opener=None):
    if c.get("origin") == "openverse":
        return IMG.openverse_fetch(c["ov_id"], img_id, name, opener=opener)
    return IMG.fetch(c["title"], img_id, name, opener=opener)


def make_illustration(img_id, name, kind, role=""):
    if kind == "firm":
        return IMG.org(img_id, name, role)
    if kind == "event":
        return IMG.event(img_id, name)
    return IMG.person(img_id, name, role)


def _style_visuals(style):
    import batch

    try:
        return getattr(batch.load_style(style), "VISUALS", {})
    except SystemExit:
        return {}


def place(ep, entity):
    """Put the entity's image where the narration names it. Returns a description or None if no slot."""
    iid = entity["image"]
    names = [entity["name"]] + entity.get("aliases", [])
    hit = lambda txt: any(n.lower() in (txt or "").lower() for n in names)
    defaults = _style_visuals(ep.get("style", ""))
    for ev in ep.get("timeline", []):
        if hit(ev.get("label")):
            if not ev.get("image"):
                ev["image"] = iid
                return f"timeline {ev['year']}"
            extra = ev.setdefault("images", [])
            if len(extra) < 1 and iid != ev["image"] and iid not in extra:   # at most two faces per event
                extra.append(iid)
                return f"timeline {ev['year']} (ảnh thứ hai)"
    for seg in ep.get("segments", []):
        if not (hit(seg.get("say")) or hit(seg.get("screen"))):
            continue
        v = seg.get("visual") or {}
        kind = v.get("kind") or defaults.get(seg["role"], "statement")
        if kind == "citation" and not v.get("image"):
            seg["visual"] = dict(v, kind="citation", image=iid)
            return f"thẻ trích dẫn ({seg['role']})"
        if kind == "statement" and not v.get("scene") and not v.get("image"):
            seg["visual"] = {"kind": "image", "image": iid}
            return f"ảnh lớn ({seg['role']})"
    return None


def auto(ep_path, write=False, offline=False, opener=None, log=print):
    ep = json.loads(Path(ep_path).read_text(encoding="utf-8"))
    ents = ep.setdefault("entities", [])
    declared = [n.lower() for e in ents for n in [e["name"]] + e.get("aliases", [])]
    fulls = full_names()
    idx = IMG.index()
    online = not offline
    plan = []
    for m in sorted(check_images.mentions(ep)):
        if any(m.lower() in d or d in m.lower() for d in declared) or m in ep.get("entity_ignore", []):
            continue
        name = fulls.get(m, m)
        kind = "firm" if FIRM.search(name) else "person"
        img_id = slug(name)
        src = "đã có trong sổ ảnh" if img_id in idx else None
        if not src and online and write:
            try:
                c = find_real(name, opener)
                if c:
                    fetch_found(c, img_id, name, opener)
                    src = f"ảnh thật ({c.get('origin')}): {c['title'][:50]} ({c['license']})"
            except Exception as ex:
                log(f"  ⚠ Commons không truy cập được ({type(ex).__name__}: {str(ex)[:60]}) → dùng ảnh minh hoạ")
                online = False
        if not src:
            if write:
                make_illustration(img_id, name, kind)
            src = "ảnh minh hoạ " + ("thẻ tổ chức" if kind == "firm" else "thẻ nhân vật")
        ent = {"name": name, "aliases": sorted({m, name.split()[-1]} - {name}), "kind": kind, "image": img_id}
        ents.append(ent)
        declared += [n.lower() for n in [name] + ent["aliases"]]
        plan.append((m, ent, src))
    # place every entity image that is not on screen yet
    shown = set(check_images.used_images(ep))
    placed = []
    for ent in ents:
        if ent.get("image") and ent["image"] not in shown:
            where = place(ep, ent)
            placed.append((ent["name"], where))
            if where:
                shown = set(check_images.used_images(ep))
    for m, ent, src in plan:
        log(f"  + {m:<22} → {ent['name']:<28} {src}")
    for n, where in placed:
        log(f"  ↳ {n:<28} " + (f"đặt vào {where}" if where else "CHƯA có chỗ đặt — thêm visual.image cho một đoạn, hoặc ghi waiver"))
    if write:
        Path(ep_path).write_text(json.dumps(ep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    res = check_images.check(ep) if write else None
    if res:
        log(("  ✅ check_images ĐẠT" if not res["fail"] else "  ❌ check_images:\n    - " + "\n    - ".join(res["issues"])))
    elif not plan and not placed:
        log("  không có nhân vật/hãng mới cần ảnh")
    return {"plan": plan, "placed": placed, "check": res}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("auto"); s.add_argument("episode"); s.add_argument("--write", action="store_true")
    s.add_argument("--offline", action="store_true")
    s = sub.add_parser("find"); s.add_argument("name")
    a = ap.parse_args()
    if a.cmd == "auto":
        r = auto(a.episode, a.write, a.offline)
        sys.exit(1 if r["check"] and r["check"]["fail"] else 0)
    c = find_real(a.name)
    print(f"✅ [{c.get('origin')}] {c['title']}\n   {c['license']} · {c['author']}"
          + (f"\n   openverse id: {c['ov_id']}" if c.get("ov_id") else "") if c
          else "không có ảnh giấy phép tự do nào ghi đúng tên này (Commons + Openverse)")


if __name__ == "__main__":
    main()
