"""Fallback photo source when Wikimedia Commons answers HTTP 429: Openverse (api.openverse.org).

Only CC BY / CC BY-SA / CC0 / public-domain photos; downloaded through Openverse's own thumbnail proxy when the
original host refuses. Each photo goes into knowledge/images/ledger.json with author + licence (shown on screen).
People are matched strictly (first AND last name must appear in the title) — still check every new person photo by
eye and delete wrong-person matches (python images.py list; remove the entry + file).

  python openverse_images.py "amos-tversky|Amos Tversky|person" "roulette-wheel|roulette wheel"
"""
import json, sys, time, urllib.parse, urllib.request, ssl, os, datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import images as IMG

CA = "/root/.ccr/ca-bundle.crt"
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
UA = {"User-Agent": "EduVideoPipeline/1.0"}
LIC = {"by": "CC BY", "by-sa": "CC BY-SA", "cc0": "CC0", "pdm": "Public domain"}


def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), context=CTX, timeout=timeout).read()


def main(specs):
    have = {e["id"] for e in IMG.ledger()["images"]}
    WANT, PEOPLE = [], set()
    for s in specs:
        parts = s.split("|")
        img_id, q = parts[0], parts[1]
        WANT.append((img_id, q, q))
        if len(parts) > 2 and parts[2] == "person":
            PEOPLE.add(img_id)
    for img_id, q, subj in WANT:
        if img_id in have:
            print("have", img_id, flush=True); continue
        query = subj if img_id in PEOPLE else q
        try:
            data = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(
                {"q": query, "license": "by,by-sa,cc0,pdm", "page_size": 10, "mature": "false"})))
        except Exception as ex:
            print("search fail", img_id, str(ex)[:60], flush=True); time.sleep(10); continue
        pick = None
        for r in data.get("results", []):
            title = (r.get("title") or "").lower()
            if img_id in PEOPLE:
                if not all(tok.lower() in title for tok in subj.split()[-1:]) or subj.split()[0].lower() not in title:
                    continue
            elif not any(w in title for w in q.lower().split() if len(w) > 3):
                continue
            if (r.get("width") or 0) and r["width"] < 500:
                continue
            pick = r; break
        if not pick:
            print("NONE", img_id, flush=True); time.sleep(3.5); continue
        raw = None
        for u in (pick["url"], f"https://api.openverse.org/v1/images/{pick['id']}/thumb/?full_size=true"):
            try:
                raw = get(u); break
            except Exception as ex:
                print("  dl fail", img_id, u[:60], str(ex)[:40], flush=True)
        if not raw:
            print("NONE", img_id, flush=True); continue
        ext = ".png" if raw[:4] == b"\x89PNG" else ".jpg"
        path = IMG.FILES / f"{img_id}{ext}"; IMG.FILES.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        lic = LIC.get(pick["license"], pick["license"].upper()) + (f" {pick['license_version']}" if pick.get("license_version") and pick["license"] in ("by", "by-sa") else "")
        who = (pick.get("creator") or "unknown author").strip()
        prov = (pick.get("source") or pick.get("provider") or "").replace("wikimedia", "Wikimedia Commons").title() if pick.get("source") != "wikimedia" else "Wikimedia Commons"
        IMG._save_entry({"id": img_id, "kind": "photo", "subject": subj, "depicts": pick.get("title", ""),
                         "file": f"files/{img_id}{ext}", "source_url": pick.get("foreign_landing_url", ""), "author": who,
                         "license": lic, "license_url": pick.get("license_url", ""),
                         "credit": f"Ảnh: {who} · {lic} · {prov} (via Openverse)", "retrieved": datetime.date.today().isoformat()})
        print("OK", img_id, "|", pick.get("title", "")[:50], "|", who[:30], lic, prov, flush=True)
        time.sleep(3.5)


if __name__ == "__main__":
    main(sys.argv[1:])
