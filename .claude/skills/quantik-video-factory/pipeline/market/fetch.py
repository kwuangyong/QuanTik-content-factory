"""Stage 1 — data retrieval. Writes a data bundle: raw files + manifest.json (source, URL, retrieval time, period,
row count, sha256, status). Never fills a gap: a failed download is recorded as status "failed" with the error.

  python market.py fetch                                  # live AGR snapshot (indices + every instrument)
  python market.py fetch --history vnindex.csv --history-manifest vnindex.manifest.json   # + user history
  python market.py fetch --fixture ../tests/fixtures/market_stale                          # copy a test fixture

History CSV: columns date (YYYY-MM-DD), close, optional volume/value. The manifest must say where it came from:
{"source": "...", "retrieved_at": "2026-11-14T09:00:00+07:00", "period": "2025-11-13..2026-11-13"}.
"""
from __future__ import annotations

import csv
import shutil
import urllib.request
from pathlib import Path

from .common import AGR_INDEX_URL, AGR_INSTRUMENTS_URL, DEFAULT_DATA, iso, load, now_ict, save, sha256

UA = "quantik-content-factory/1.0 (market research; educational)"


def _get(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _dataset(bundle, name, source_id, url, filename, timeout):
    t = now_ict()
    ds = {"name": name, "source_id": source_id, "url": url, "retrieved_at": iso(t), "file": filename}
    try:
        raw = _get(url, timeout)
        import json

        data = json.loads(raw)
        if data.get("s") != "ok" or not data.get("d"):
            raise ValueError(f"feed returned s={data.get('s')!r} em={data.get('em')!r}")
        (bundle / filename).write_bytes(raw)
        dates = sorted({r.get("tradingdate", "") for r in data["d"] if r.get("tradingdate")})
        ds.update(status="ok", rows=len(data["d"]), sha256=sha256(bundle / filename),
                  period=("phiên " + ", ".join(dates)) if dates else None)
    except Exception as ex:  # network, proxy, malformed feed: record, never invent
        ds.update(status="failed", rows=0, period=None, error=f"{type(ex).__name__}: {str(ex)[:200]}")
    return ds


def _history(bundle, csv_path, manifest_path):
    ds = {"name": "history", "source_id": "user-history-csv", "file": "history.csv"}
    if not manifest_path or not Path(manifest_path).exists():
        ds.update(status="failed", rows=0, retrieved_at=None, period=None,
                  error="history CSV has no manifest (source, retrieved_at, period) — refused as untraceable")
        return ds
    man = load(manifest_path)
    shutil.copy(csv_path, bundle / "history.csv")
    with open(bundle / "history.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    ds.update(status="ok", rows=len(rows), url=man.get("source", ""), retrieved_at=man.get("retrieved_at"),
              period=man.get("period") or (f"{rows[0]['date']}..{rows[-1]['date']}" if rows else None),
              sha256=sha256(bundle / "history.csv"), source_note=man.get("source", ""))
    return ds


def fetch(data_root=DEFAULT_DATA, history=None, history_manifest=None, timeout=120, index_url=AGR_INDEX_URL,
          instruments_url=AGR_INSTRUMENTS_URL, skip_instruments=False, fixture=None, log=print):
    t = now_ict()
    bundle = Path(data_root) / f"bundle-{t:%Y%m%d-%H%M%S}"
    bundle.mkdir(parents=True, exist_ok=True)
    if fixture:  # test fixtures are copied verbatim and always marked "sample"
        for f in Path(fixture).iterdir():
            shutil.copy(f, bundle / f.name)
        man = load(bundle / "manifest.json")
        for ds in man["datasets"]:
            ds["status"] = "sample" if ds.get("status") == "ok" else ds.get("status")
        man.update(bundle_id=bundle.name, created_at=iso(t), fixture=str(fixture))
        save(bundle / "manifest.json", man)
        log(f"  fixture → {bundle}")
        return bundle
    datasets = [_dataset(bundle, "indexsnaps", "agr-indexsnaps", index_url, "indexsnaps.json", min(timeout, 30))]
    if not skip_instruments:
        datasets.append(_dataset(bundle, "instruments", "agr-instruments", instruments_url, "instruments.json", timeout))
    if history:
        datasets.append(_history(bundle, history, history_manifest))
    save(bundle / "manifest.json", {"bundle_id": bundle.name, "created_at": iso(t), "datasets": datasets})
    for ds in datasets:
        log(f"  {ds['name']:<12} {ds['status']:<7} rows={ds.get('rows', 0)}  {ds.get('period') or ''} {ds.get('error', '')}")
    return bundle
