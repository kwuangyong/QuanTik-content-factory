"""Stage 2 — analysis. Reads one data bundle, writes market_report.json (schemas/market_report.schema.json).

Three kinds of output, never mixed:
  observed     numbers read straight from the feed (index level, advancers, traded value…), each tagged with its dataset
  model        numbers computed by a stated method (breadth %, concentration, sector medians, regime rules)
  limitations  what could not be computed and why (no history → no regime; failed download → no breadth…)
Interpretation is NOT written here: that is the editorial stage.
"""
from __future__ import annotations

import csv
import datetime as dt
import math
import statistics
from pathlib import Path

from .common import CLOSE_TIME, ICT, PILLAR_DIR, iso, load, now_ict, parse_iso, save, sessions_behind

MIN_HISTORY = 200        # sessions needed for MA200-based regime
BREADTH_POS, BREADTH_NEG = 0.60, 0.40
MIN_SECTOR = 5         # traded members needed before a group is ranked


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _date(s):  # "13/11/2026" → date
    d, m, y = s.split("/")
    return dt.date(int(y), int(m), int(d))


def _obs(value, fmt, dataset, desc, unit=""):
    return {"value": value, "fmt": fmt, "dataset": dataset, "desc": desc, "unit": unit}


def _mod(value, fmt, method, inputs):
    return {"value": value, "fmt": fmt, "method": method, "inputs": inputs}


def _history_series(bundle, man, data_root):
    """Closes by date from a user history CSV in the bundle, else from archived AGR snapshots (own history)."""
    ds = next((d for d in man["datasets"] if d["name"] == "history" and d["status"] in ("ok", "sample")), None)
    if ds:
        with open(bundle / "history.csv", newline="", encoding="utf-8") as fh:
            rows = [(r["date"], float(r["close"]), _num(r.get("value"))) for r in csv.DictReader(fh) if r.get("close")]
        return sorted(rows), f"{ds['source_id']} ({ds.get('source_note') or ds.get('url', '')}), {ds.get('period')}"
    seen = {}
    for b in sorted(Path(data_root).glob("bundle-*")):
        f = b / "indexsnaps.json"
        if not f.exists():
            continue
        try:
            hose = next(x for x in load(f)["d"] if x["marketCode"] == "HOSE")
            if hose.get("indexTime", "00:00:00") >= "15:00:00":
                seen[_date(hose["tradingdate"]).isoformat()] = (float(hose["marketIndex"]), _num(hose["totalValue"]))
        except Exception:
            continue
    rows = sorted((d, c, v) for d, (c, v) in seen.items())
    return rows, f"lưu trữ snapshot AGR cuối phiên ({len(rows)} phiên)"


def regime(rows):
    """Rule-based regime from daily closes. Returns None if fewer than MIN_HISTORY sessions."""
    if len(rows) < MIN_HISTORY:
        return None
    c = [r[1] for r in rows]
    ma = lambda n, end=None: statistics.fmean(c[(end or len(c)) - n:(end or len(c))])
    ma50, ma200, ma200_prev = ma(50), ma(200), ma(200, len(c) - 20)
    rets = [c[i] / c[i - 1] - 1 for i in range(1, len(c))]
    vol20 = statistics.pstdev(rets[-20:]) * math.sqrt(252)
    vols = [statistics.pstdev(rets[i - 20:i]) * math.sqrt(252) for i in range(20, len(rets) + 1)][-252:]
    vol_pct = sum(v <= vol20 for v in vols) / len(vols)
    hi = max(c[-252:])
    dd = c[-1] / hi - 1
    slope = ma200 / ma200_prev - 1
    if c[-1] > ma200 and ma50 > ma200 and slope > 0:
        trend = "xu hướng tăng"
    elif c[-1] < ma200 and ma50 < ma200 and slope < 0:
        trend = "xu hướng giảm"
    else:
        trend = "đi ngang / chuyển tiếp"
    volr = "biến động cao" if vol_pct >= 0.8 else "biến động thấp" if vol_pct <= 0.2 else "biến động bình thường"
    return {"trend": trend, "vol_regime": volr, "ma50": ma50, "ma200": ma200, "ma200_slope_20d": slope,
            "vol20": vol20, "vol20_percentile_1y": vol_pct, "drawdown_52w": dd, "sessions": len(c),
            "rule": "tăng: giá > MA200, MA50 > MA200, MA200 dốc lên 20 phiên; giảm: ngược lại cả ba; còn lại đi ngang. "
                    "Biến động: σ 20 phiên năm hoá so với 252 giá trị gần nhất (≥ 80% cao, ≤ 20% thấp)."}


def analyze(bundle, now=None, data_root=None, sector_map=None):
    bundle = Path(bundle)
    data_root = Path(data_root or bundle.parent)
    now = now or now_ict()
    man = load(bundle / "manifest.json")
    by = {d["name"]: d for d in man["datasets"]}
    report = {"id": man["bundle_id"], "generated_at": iso(now), "data_status": "unavailable", "as_of": None,
              "sessions_behind": None, "bundle": {"path": str(bundle), "datasets": man["datasets"]},
              "observed": {}, "model": {}, "regime": None, "sectors": None, "limitations": [], "universe": []}
    lim = report["limitations"]
    idx = by.get("indexsnaps")
    if not idx or idx["status"] not in ("ok", "sample"):
        lim.append("Không lấy được dữ liệu chỉ số (" + ((idx or {}).get("error") or "thiếu dataset") +
                   "). Không có số thị trường nào được báo cáo; không dựng video nhịp thị trường.")
        save(bundle / "market_report.json", report)
        return report

    snaps = {x["marketCode"]: x for x in load(bundle / idx["file"])["d"]}
    hose = snaps["HOSE"]
    as_of = _date(hose["tradingdate"])
    report["as_of"] = as_of.isoformat()
    behind = sessions_behind(as_of, now)
    report["sessions_behind"] = behind
    intraday = hose.get("indexTime", "") < CLOSE_TIME.strftime("%H:%M:%S") and behind == 0 and as_of == now.astimezone(ICT).date()
    if idx["status"] == "sample":
        report["data_status"] = "sample"
        lim.append("Dữ liệu mẫu (fixture) — chỉ để kiểm thử, không phải thị trường thật, không được đăng.")
    elif behind > 0:
        report["data_status"] = "stale"
        lim.append(f"Dữ liệu cũ: phiên gần nhất trong gói là {as_of:%d/%m/%Y}, đã có {behind} phiên đóng cửa sau đó.")
    else:
        report["data_status"] = "intraday" if intraday else "fresh"
    if intraday:
        lim.append(f"Snapshot trong phiên lúc {hose['indexTime']}: số liệu còn thay đổi đến hết phiên.")

    O, M = report["observed"], report["model"]
    ds = "indexsnaps"
    names = {"HOSE": "vnindex", "30": "vn30", "HNX": "hnx", "UPCOM": "upcom"}
    for code, key in names.items():
        s = snaps.get(code)
        if not s:
            lim.append(f"Thiếu snapshot {code}.")
            continue
        O[key] = _obs(float(s["marketIndex"]), "num2", ds, f"{code} điểm", "điểm")
        O[key + "_chg"] = _obs(float(s["indexPercentChange"]) / 100, "pct2", ds, f"{code} % thay đổi")
        O[key + "_pts"] = _obs(float(s["indexChange"]), "num2", ds, f"{code} điểm thay đổi", "điểm")
    ch = O["vnindex_chg"]["value"]
    M["vnindex_dir"] = _mod("tăng" if ch > 0 else "giảm" if ch < 0 else "đứng giá", None, "dấu của vnindex_chg", ["vnindex_chg"])
    M["vnindex_chg_abs"] = _mod(abs(ch), "pct2", "trị tuyệt đối của vnindex_chg", ["vnindex_chg"])
    O["adv"] = _obs(int(hose["advances"]), "int", ds, "HOSE số mã tăng")
    O["dec"] = _obs(int(hose["declines"]), "int", ds, "HOSE số mã giảm")
    O["unch"] = _obs(int(hose["noChange"]), "int", ds, "HOSE số mã đứng giá")
    O["value_bn"] = _obs(float(hose["totalValue"]) / 1e9, "int", ds, "HOSE giá trị giao dịch", "tỷ đồng")
    O["volume_m"] = _obs(float(hose["totalVolume"]) / 1e6, "int", ds, "HOSE khối lượng", "triệu cp")
    O["snapshot_time"] = _obs(hose.get("indexTime", ""), None, ds, "giờ snapshot")
    adv, dec = O["adv"]["value"], O["dec"]["value"]
    br = adv / (adv + dec) if adv + dec else None
    M["breadth_pct"] = _mod(br, "pct0", "mã tăng / (mã tăng + mã giảm), HOSE", ["adv", "dec"])
    M["breadth_state"] = _mod("rộng, nghiêng tăng" if br >= BREADTH_POS else "hẹp, nghiêng giảm" if br <= BREADTH_NEG
                              else "trung tính", None, f"≥ {BREADTH_POS:.0%} tích cực, ≤ {BREADTH_NEG:.0%} tiêu cực", ["breadth_pct"])
    av, dv = _num(hose.get("advancesVolumn")), _num(hose.get("declinesVolumn"))
    if av and dv:
        M["updown_vol"] = _mod(av / dv, "num2", "KL mã tăng / KL mã giảm, HOSE", ["advancesVolumn", "declinesVolumn"])

    inst = by.get("instruments")
    if inst and inst["status"] in ("ok", "sample"):
        recs = load(bundle / inst["file"])["d"]
        report["universe"] = sorted({r["symbol"] for r in recs if r.get("symbol")})
        stocks = [r for r in recs if r.get("FloorCode") == "10" and str(r.get("StockType")) == "2"]
        traded = [r for r in stocks if (_num(r.get("closePrice")) or 0) > 0 and (_num(r.get("reference")) or 0) > 0]
        chg = {r["symbol"]: _num(r["closePrice"]) / _num(r["reference"]) - 1 for r in traded}
        val = {r["symbol"]: _num(r.get("totalTradingValue")) or 0.0 for r in traded}
        tot = sum(val.values()) or 1
        M["top10_share"] = _mod(sum(sorted(val.values())[-10:]) / tot, "pct0",
                                "tỷ trọng 10 mã giá trị lớn nhất / tổng giá trị cổ phiếu HOSE (khớp lệnh)", ["instruments"])
        fnet = sum(((_num(r.get("foreignBuy")) or 0) - (_num(r.get("foreignSell")) or 0)) * (_num(r.get("averagePrice")) or 0)
                   for r in traded) / 1e9
        M["foreign_net_bn"] = _mod(fnet, "int", "ước tính: Σ (KL ngoại mua − KL ngoại bán) × giá bình quân, cổ phiếu HOSE",
                                   ["instruments"])
        M["foreign_net_abs_bn"] = _mod(abs(fnet), "int", "trị tuyệt đối của foreign_net_bn", ["foreign_net_bn"])
        M["foreign_side"] = _mod("mua ròng" if fnet > 0 else "bán ròng", None, "dấu của foreign_net_bn", ["foreign_net_bn"])
        O["n_stocks_traded"] = _obs(len(traded), "int", "instruments", "số cổ phiếu HOSE có khớp")
        smap = load(sector_map or PILLAR_DIR / "sector_map.json")
        vchg = O["vnindex_chg"]["value"]
        secs = []
        for g in smap["groups"]:
            if g["kind"] != "sector":
                continue
            mem = [s for s in g["symbols"] if s in chg]
            if len(mem) < MIN_SECTOR:
                continue
            med = statistics.median(chg[s] for s in mem)
            secs.append({"name": g["name"], "n": len(g["symbols"]), "n_traded": len(mem), "median_change": med,
                         "pct_adv": sum(chg[s] > 0 for s in mem) / len(mem),
                         "value_share": sum(val[s] for s in mem) / tot, "rs_1d": med - vchg})
        if secs:
            report["sectors"] = secs
            lead, lag = max(secs, key=lambda s: s["median_change"]), min(secs, key=lambda s: s["median_change"])
            M["lead_sector"] = _mod(lead["name"], None, "nhóm có trung vị % thay đổi cao nhất (≥ 5 mã có khớp)", ["sectors"])
            M["lead_chg"] = _mod(lead["median_change"], "pct2", "trung vị % thay đổi của lead_sector", ["sectors"])
            M["lag_sector"] = _mod(lag["name"], None, "nhóm có trung vị % thay đổi thấp nhất", ["sectors"])
            M["lag_chg"] = _mod(lag["median_change"], "pct2", "trung vị % thay đổi của lag_sector", ["sectors"])
            M["n_sectors_up"] = _mod(sum(s["median_change"] > 0 for s in secs), "int", "số nhóm có trung vị dương", ["sectors"])
            M["n_sectors"] = _mod(len(secs), "int", "số nhóm ngành đủ dữ liệu", ["sectors"])
        lim.append("Nhóm ngành theo danh sách tham chiếu của QuanTik (không phải ICB); sức mạnh tương đối chỉ của 1 phiên.")
    else:
        lim.append("Không lấy được bảng giá từng mã → không có nhóm ngành, độ tập trung thanh khoản, khối ngoại.")

    rows, hist_src = _history_series(bundle, man, data_root)
    rg = regime(rows)
    if rg:
        report["regime"] = dict(rg, source=hist_src)
        for k, f in (("ma50", "num0"), ("ma200", "num0"), ("vol20", "pct0"), ("vol20_percentile_1y", "pct0"),
                     ("drawdown_52w", "pct1")):
            M[k] = _mod(rg[k], f, rg["rule"], [hist_src])
        M["trend"] = _mod(rg["trend"], None, rg["rule"], [hist_src])
        M["vol_regime"] = _mod(rg["vol_regime"], None, rg["rule"], [hist_src])
    else:
        lim.append(f"Chưa đủ lịch sử có nguồn ({len(rows)}/{MIN_HISTORY} phiên) → không phân loại regime, không tính "
                   "biến động thực hiện, sụt giảm từ đỉnh hay thanh khoản so với trung bình.")
    save(bundle / "market_report.json", report)
    return report
