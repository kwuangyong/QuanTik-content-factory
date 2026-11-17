"""Stage 4a — market report + editorial → episode script for the market-brief style.

Each segment's claims say what kind of statement it is (observed / model_output / interpretation) and which dataset
it rests on, so the badge on screen and the source footer are derived, not typed.
"""
from __future__ import annotations

from .common import load
from .editorial import THRESHOLDS

SRC = {"indexsnaps": "agr-indexsnaps", "instruments": "agr-instruments", "history": "user-history-csv"}


def _claim(cid, text, status, sources):
    return {"id": cid, "text": text, "status": status, "source_ids": sources}


def build(report, editorial, report_path, style="market-brief", allow_stale=False):
    O, M = report["observed"], report["model"]
    has = lambda k: (k in M and M[k]["value"] is not None) or (k in O and O[k]["value"] is not None)
    ds_ok = {d["name"] for d in report["bundle"]["datasets"] if d["status"] in ("ok", "sample")}
    idx_src = [SRC["indexsnaps"]]
    inst_src = [SRC["instruments"]] if "instruments" in ds_ok else []
    stale = report["data_status"] == "stale"
    claims = [
        _claim("obs_index", "Mức và % thay đổi các chỉ số trong snapshot", "observed", idx_src),
        _claim("obs_breadth", "Số mã tăng, giảm, đứng giá HOSE", "observed", idx_src),
        _claim("mod_breadth", "Tỷ lệ mã tăng và trạng thái độ rộng theo ngưỡng 60%/40%", "model_output", idx_src),
        _claim("obs_value", "Giá trị khớp HOSE", "observed", idx_src),
    ]
    segs = []
    asof_say = "Dữ liệu phiên {as_of}, nguồn AGR. VN-INDEX {vnindex:num0} điểm, {vnindex_dir} {vnindex_chg_abs}."
    if stale:
        asof_say = "Lưu ý: đây là dữ liệu cũ, không phải hôm nay. " + asof_say
    segs.append({"role": "asof", "say": asof_say, "claims": ["obs_index"],
                 "visual": {"kind": "terminal", "title": "AGR datafeed · phiên {as_of}",
                            "rows": [{"label": "VN-INDEX", "key": "vnindex"}, {"label": "VN-INDEX %", "key": "vnindex_chg"},
                                     {"label": "VN30 %", "key": "vn30_chg"}, {"label": "HNX %", "key": "hnx_chg"},
                                     {"label": "UPCOM %", "key": "upcom_chg"}]},
                 "screen": "DỮ LIỆU CŨ · phiên {as_of}" if stale else "Phiên {as_of} · lúc {snapshot_time}"})
    segs.append({"role": "breadth", "say": "{adv} mã tăng, {dec} mã giảm. Tỷ lệ mã tăng {breadth_pct}: độ rộng {breadth_state}.",
                 "claims": ["obs_breadth", "mod_breadth"], "visual": {"kind": "gauge"},
                 "screen": "Tỷ lệ mã tăng {breadth_pct} · {breadth_state}"})
    liq_rows = [{"label": "Giá trị khớp (tỷ đ)", "key": "value_bn"}]
    liq_say = "Giá trị khớp lệnh HOSE {value_bn} tỷ đồng."
    liq_claims = ["obs_value"]
    if has("top10_share"):
        claims += [_claim("mod_conc", "Tỷ trọng 10 mã giá trị lớn nhất", "model_output", inst_src),
                   _claim("mod_foreign", "Khối ngoại ròng ước tính từ khối lượng × giá bình quân", "model_output", inst_src)]
        liq_rows += [{"label": "10 mã lớn nhất", "key": "top10_share"}, {"label": "Ngoại ròng ước tính (tỷ đ)", "key": "foreign_net_bn"}]
        liq_say += " Mười mã lớn nhất chiếm {top10_share}. Khối ngoại ước tính {foreign_side} {foreign_net_abs_bn} tỷ."
        liq_claims += ["mod_conc", "mod_foreign"]
    segs.append({"role": "liquidity", "say": liq_say, "claims": liq_claims,
                 "visual": {"kind": "terminal", "title": "thanh khoản · HOSE", "rows": liq_rows}})
    if has("lead_sector"):
        claims.append(_claim("mod_sectors", "Trung vị % thay đổi theo nhóm ngành tham chiếu QuanTik", "model_output",
                             inst_src + ["quantik-industry-watchlist"]))
        segs.append({"role": "sectors", "say": "{n_sectors_up} trên {n_sectors} nhóm ngành tăng. Mạnh nhất {lead_sector}, "
                                              "yếu nhất {lag_sector}.",
                     "claims": ["mod_sectors"], "visual": {"kind": "sectors", "title": "trung vị % theo nhóm ngành"},
                     "screen": "Chỉ 1 phiên: chưa đủ để gọi là luân chuyển ngành"})
    if report.get("regime"):
        claims.append(_claim("mod_regime", "Regime theo luật MA50/MA200 và phân vị biến động", "model_output",
                             [SRC["history"]] if "history" in ds_ok else idx_src))
        segs.append({"role": "regime", "say": "Theo luật MA50, MA200, VN-INDEX đang {trend}, {vol_regime}; cách đỉnh "
                                             "52 tuần {drawdown_52w}.", "claims": ["mod_regime"],
                     "visual": {"kind": "terminal", "title": "regime · luật cố định",
                                "rows": [{"label": "MA50", "key": "ma50"}, {"label": "MA200", "key": "ma200"},
                                         {"label": "σ 20 phiên năm hoá", "key": "vol20"},
                                         {"label": "từ đỉnh 52 tuần", "key": "drawdown_52w"}]}})
    else:
        segs.append({"role": "regime", "limitation": True, "claims": [],
                     "say": "Giới hạn: chưa đủ lịch sử để phân loại regime, nên không gọi tên xu hướng.",
                     "screen": "Chưa đủ lịch sử để phân loại regime"})
    for i, it in enumerate(editorial["interpretations"]):
        claims.append(_claim(f"int{i}", it["text"], "interpretation", []))
    segs.append({"role": "interpretation", "say": editorial["interpretations"][0]["text"], "claims": ["int0"],
                 "screen": editorial["interpretations"][1]["text"] if len(editorial["interpretations"]) > 1 else None})
    if segs[-1]["screen"] is None:
        segs[-1].pop("screen")
    else:
        segs[-1]["claims"].append("int1")
    sc = {s["name"]: s for s in editorial["scenarios"]}
    claims.append(_claim("int_scen", "Ba kịch bản có điều kiện xác nhận và vô hiệu", "interpretation", []))
    segs.append({"role": "scenarios", "claims": ["int_scen"], "visual": {"kind": "scenarios"}, "min_dur": 7.0,
                 "say": "Ba kịch bản có thể xảy ra, để theo dõi chứ không phải dự báo. Tích cực: " + _low(sc["bull"]["description"]) +
                        " Cơ sở: " + _low(sc["base"]["description"]) + " Tiêu cực: " + _low(sc["bear"]["description"]) +
                        " Điều kiện xác nhận và vô hiệu nằm trên màn hình."})
    claims.append(_claim("int_risk", "Hành động quản trị rủi ro chung", "interpretation", []))
    segs.append({"role": "risk", "claims": ["int_risk"],
                 "say": "Có thể làm gì? " + sc["base"]["investor_actions"][0] + ".",
                 "screen": sc["bear"]["investor_actions"][0]})
    up = O["vnindex_chg"]["value"] >= 0
    wide = (M["breadth_pct"]["value"] or 0) >= 0.5
    joint = "và" if up == wide else "nhưng"
    lim = report["limitations"]
    return {
        "id": f"mi-{report['as_of']}-{style}", "pillar": "market-intelligence", "topic": "mi_daily_pulse", "style": style,
        "model": "market_snapshot", "market_report": str(report_path), "allow_stale": allow_stale,
        "tag": "NHỊP THỊ TRƯỜNG",
        "title": "Nhịp thị trường {as_of}: chỉ số, độ rộng và 3 kịch bản",
        "hook": ("Dữ liệu cũ phiên {as_of}: " if stale else "") + "VN-INDEX {vnindex_dir} {vnindex_chg_abs}, " + joint + " chỉ {breadth_pct} số mã tăng. Thị trường thật sự ra sao?",
        "segments": segs, "claims": claims, "scenarios": editorial["scenarios"],
        "takeaway": "Đọc thị trường bằng độ rộng và điều kiện, không bằng một con số điểm.",
        "caption": "Nhịp thị trường phiên {as_of} bằng dữ liệu: độ rộng, thanh khoản, nhóm ngành và ba kịch bản có điều "
                   "kiện xác nhận/vô hiệu. Dữ liệu AGR datafeed. Giới hạn: " + " ".join(lim),
        "hashtags": ["vnindex", "thitruong", "chungkhoan", "quant", "QuanTik"],
        "allowed_literals": THRESHOLDS + ["MA50", "MA200", "52 tuần", "20 phiên", "10 mã", "200 phiên"],
        "editorial_author": editorial["author"], "limitations": lim,
        "cta": "", "max_seconds": 90,
    }


def _low(s):
    return s[:1].lower() + s[1:] if s else s


def load_report(p):
    return load(p)
