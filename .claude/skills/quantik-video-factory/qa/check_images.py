"""Images for people / firms / events: every mention is covered, every picture is legal and credited.

  1. every image id used (segment visual.image, timeline[].image, entities[].image) is in knowledge/images/ledger.json
     and its file exists;
  2. photo → free licence (PD / CC0 / CC BY / CC BY-SA), author, source URL, credit naming the licence;
     illustration → credit says "minh hoạ" (never passed off as a real photo);
  3. each declared entity has an image that is actually shown in some scene, or an explicit waiver (reason);
  4. mention detection: a surname of any author in the source ledger (Thorp, Kelly, Odean, Nash…) or a
     two-word capitalised Latin name ("Jay Regan", "Bell Labs") in narration / on-screen text must be declared in
     `entities` (or listed in `entity_ignore`), so a person is never named without a picture or a stated reason.

Usage: python check_images.py <episode.json>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
from core import KNOWLEDGE  # noqa: E402

NAME2 = re.compile(r"(?<![A-Za-zÀ-ỹ])([A-Z][a-z]+(?: [A-Z]\.)?(?: [A-Z][a-z]+)+)(?![A-Za-zÀ-ỹ])")
STOP = {"The", "And", "Of"}


def _authors_surnames():
    data = json.loads((KNOWLEDGE / "sources/ledger.json").read_text(encoding="utf-8"))
    out = set()
    for s in data["sources"]:
        for a in s.get("authors", []):
            parts = re.findall(r"[A-Z][a-z]{2,}", a)
            if parts and not a.startswith(("President", "QuanTik", "Agriseco")):
                out.add(parts[-1])
    return out


def used_images(ep):
    ids = [s["visual"]["image"] for s in ep.get("segments", [])
           if (s.get("visual") or {}).get("image") and (s.get("visual") or {}).get("kind") in ("image", "citation", None)]
    ups = [(s.get("visual") or {}).get("upto", len(ep.get("timeline", [])) - 1)
           for s in ep.get("segments", []) if (s.get("visual") or {}).get("kind") == "timeline"
           or (s["role"] in ("context", "consequences") and ep.get("style") == "history-story" and not s.get("visual"))]
    shown = max(ups) if ups else -1
    ids += [i for e in ep.get("timeline", [])[:shown + 1] for i in ([e["image"]] if e.get("image") else []) + e.get("images", [])]
    return ids


def mentions(ep):
    texts = [ep.get("hook", ""), ep.get("takeaway", ""), ep.get("title", "")]
    texts += [x for s in ep.get("segments", []) for x in (s.get("say", ""), s.get("screen", ""))]
    texts += [e.get("label", "") for e in ep.get("timeline", [])]
    blob = "\n".join(t for t in texts if t)
    found = {m.group(1) for m in NAME2.finditer(blob) if m.group(1).split()[0] not in STOP}
    for sur in _authors_surnames():
        if re.search(r"(?<![A-Za-z])" + sur + r"(?![a-z])", blob):
            found.add(sur)
    return found


def check(ep, require=True):
    import images

    idx = images.index()
    issues, warnings = [], []
    ents = ep.get("entities") or []
    used = used_images(ep)
    for iid in set(used + [e["image"] for e in ents if e.get("image")]):
        e = idx.get(iid)
        if e is None:
            issues.append(f"ảnh '{iid}' không có trong knowledge/images/ledger.json")
            continue
        if not images.path_of(e).exists():
            issues.append(f"ảnh '{iid}': thiếu file {e['file']}")
        if e["kind"] == "photo":
            if not images.is_free(e.get("license", "")):
                issues.append(f"ảnh '{iid}': giấy phép '{e.get('license')}' không được dùng lại")
            if not e.get("author") or not e.get("source_url"):
                issues.append(f"ảnh '{iid}': thiếu tác giả hoặc URL nguồn")
            if e.get("license", "") not in e.get("credit", ""):
                issues.append(f"ảnh '{iid}': dòng ghi công phải nêu giấy phép")
        elif "minh hoạ" not in e.get("credit", "").lower():
            issues.append(f"ảnh minh hoạ '{iid}' phải ghi rõ 'minh hoạ'")
    for en in ents:
        if en.get("image"):
            if en["image"] not in used:
                issues.append(f"'{en['name']}': có ảnh '{en['image']}' nhưng không cảnh nào hiện ảnh đó")
        elif len((en.get("waiver") or "").strip()) < 10:
            issues.append(f"'{en['name']}' được nhắc nhưng không có ảnh và không ghi lý do (waiver)")
    if require:
        names = [n.lower() for en in ents for n in [en["name"]] + en.get("aliases", [])]
        ignore = [x.lower() for x in ep.get("entity_ignore", [])]
        for m in sorted(mentions(ep)):
            ml = m.lower()
            if not any(ml in n or n in ml for n in names) and ml not in ignore:
                issues.append(f"nhắc '{m}' nhưng chưa khai báo trong 'entities' (cần ảnh minh hoạ/ảnh có giấy phép "
                              f"hoặc waiver)")
    n_photo = sum(idx[i]["kind"] == "photo" for i in set(used) if i in idx)
    return {"fail": bool(issues), "issues": issues, "warnings": warnings,
            "details": {"ảnh dùng": len(set(used)), "ảnh thật": n_photo, "nhân vật": len(ents)}}


if __name__ == "__main__":
    ep = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = check(ep)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(1 if res["fail"] else 0)
