"""Content pillars: registry, catalogs, topic resolution and episode defaults.

pillars/registry.json defines each pillar (roles, styles, claim statuses, hedge markers, extra banned phrases).
batch.py calls `resolve()` before its old hand-written/catalog lookup, so existing commands behave exactly as before
and pillar topics (bf_*, mi_*, qh_*, ds_*) gain a model, defaults and pillar QA.
"""
from __future__ import annotations

import json
from functools import lru_cache

from core import SKILL


@lru_cache(maxsize=1)
def registry():
    return json.loads((SKILL / "pillars/registry.json").read_text(encoding="utf-8"))


def pillars():
    return registry()["pillars"]


def get(pid):
    for p in pillars():
        if p["id"] == pid:
            return p
    raise SystemExit(f"unknown pillar {pid!r}; pillars: {[p['id'] for p in pillars()]}")


@lru_cache(maxsize=16)
def catalog(pid):
    p = get(pid)
    path = SKILL / p["catalog"]
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["topics"] if "pillar" in data else data.get("topics", [])


def find_topic(topic):
    for p in pillars():
        if p["id"] == "quant-education":
            continue
        for t in catalog(p["id"]):
            if t["id"] == topic:
                return p, t
    return None


def resolve(topic, override=None):
    """(pillar, catalog entry) for a pillar episode/topic, or None for the legacy quant-education paths."""
    ov = override or {}
    pid = ov.get("pillar")
    if pid and pid != "quant-education":
        p = get(pid)
        entry = next((t for t in catalog(pid) if t["id"] == topic), {"id": topic, "name": topic, "model": ov.get("model")})
        return p, entry
    if pid == "quant-education":
        return None
    return find_topic(topic)


def pillar_of(ep):
    pid = ep.get("pillar")
    return get(pid) if pid and pid != "quant-education" else None


def episode_defaults(pillar, entry, ep):
    """Fields legacy styles need (beats, takeaway, myth/fact, story…) derived from the pillar segments,
    so a pillar episode can also be rendered as kinetic-text / carousel / myth-buster."""
    segs = ep.get("segments") or []
    says = [s["say"] for s in segs]
    beats = (says + [ep.get("takeaway", "")] * 4)[:4]
    d = {"pillar": pillar["id"], "max_seconds": pillar.get("max_seconds", 60), "beats": beats,
         "tag": entry.get("name", entry["id"])[:22].upper(), "kicker": pillar["name"].split(" — ")[-1],
         "outputs": [], "symbols": [], "formula": r"\mathrm{" + entry["id"].replace("_", r"\ ") + "}"}
    if says:
        d["symbols"] = [{"sym": d["formula"], "say": says[0]}]
        d["myth"] = says[0]
        d["fact"] = says[min(2, len(says) - 1)]
        d["story"] = [{"at": round((i + 1) / len(says), 2), "label": s["role"][:20], "say": s["say"]} for i, s in enumerate(segs)]
        d["meme"] = {"format": "nobody-quant", "setup": says[0], "punch": says[1] if len(says) > 1 else says[0],
                     "truth": ep.get("takeaway", says[-1])}
    return d
