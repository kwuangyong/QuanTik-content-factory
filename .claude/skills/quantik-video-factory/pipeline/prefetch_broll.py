"""Warm the B-roll cache for every lesson/episode (slow and polite: Wikimedia rate-limits shared IPs).

python prefetch_broll.py [--rounds 6]   → retries rate-limited queries with growing pauses; misses are cached
"""
import json
import sys
import time
from pathlib import Path

import broll as B
import lesson as L
from core import SKILL

specs = []
for les in L.load_all().values():
    ep = les.get("episode", {})
    specs += [s for s in [ep.get("hook_broll")] + ep.get("broll", []) if s and (s.get("query") or s.get("file"))]
for p in (SKILL / "episodes").glob("*.json"):
    ep = json.loads(p.read_text(encoding="utf-8"))
    specs += [s for s in [ep.get("hook_broll")] + ep.get("broll", []) if s and (s.get("query") or s.get("file"))]
todo = list({(s.get("file") or s["query"]): s for s in specs}.values())
rounds = int(sys.argv[sys.argv.index("--rounds") + 1]) if "--rounds" in sys.argv else 6
for rnd in range(rounds):
    left = []
    for s in todo:
        r = B.fetch(s)
        key = s.get("file") or s["query"]
        if r.get("path"):
            print(f"OK   {key} → {r['title']} [{r['license']}]", flush=True)
        elif "429" in r.get("error", "") or "Error" in r.get("error", ""):
            print(f"WAIT {key}: {r['error'][:60]}", flush=True); left.append(s)
        else:
            print(f"MISS {key}: {r['error']}", flush=True)
        time.sleep(3)
    if not left:
        break
    todo = left
    print(f"-- round {rnd + 1}: {len(left)} rate-limited, pause {60 * (rnd + 1)}s", flush=True)
    time.sleep(60 * (rnd + 1))
print("done")
