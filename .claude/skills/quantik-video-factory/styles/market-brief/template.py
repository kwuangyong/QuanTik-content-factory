"""market-brief (market intelligence): as-of stamp → breadth → liquidity → sectors → regime → interpretation →
three conditional scenarios → risk. Every scene carries QUAN SÁT / MÔ HÌNH / NHẬN ĐỊNH so facts, model outputs and
editorial reading are never blended. Built only from a market_report.json; never simulated.
"""
import pillar_scenes as P

KIND = "video"
DEFAULTS = {"max_seconds": 75, "kicker": "Nhịp thị trường"}
ROLES = {"asof": "DỮ LIỆU", "breadth": "ĐỘ RỘNG", "liquidity": "THANH KHOẢN", "sectors": "NHÓM NGÀNH",
         "regime": "REGIME", "interpretation": "NHẬN ĐỊNH", "scenarios": "3 KỊCH BẢN", "risk": "QUẢN TRỊ RỦI RO"}
VISUALS = {"asof": "terminal", "breadth": "gauge", "liquidity": "terminal", "sectors": "sectors", "regime": "terminal",
           "interpretation": "statement", "scenarios": "scenarios", "risk": "statement"}

ICONS = {"asof": "hourglass", "breadth": "people", "liquidity": "coins", "sectors": "building", "regime": "magnifier", "interpretation": "eye", "scenarios": "scale", "risk": "shield"}   # pictograms for text-only scenes (pipeline/pictos.py)
SCENES = {"hook": {"cast": [{"who": "analyst", "pose": "present", "face": "surprised", "x": 0.3, "flip": False}], "props": [{"what": "laptop_down", "x": 0.72, "y": 0.62, "s": 0.9}]}, "interpretation": {"cast": [{"who": "analyst", "pose": "think", "face": "focus", "x": 0.3, "flip": False}], "props": [{"what": "laptop_up", "x": 0.72, "y": 0.62, "s": 0.9}]}, "risk": {"cast": [{"who": "investor", "pose": "shrug", "face": "neutral", "x": 0.3, "flip": False}], "props": [{"what": "newspaper", "x": 0.72, "y": 0.6, "s": 0.9}]}}   # characters + props (pipeline/figures.py)


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, icons=ICONS, scenes=SCENES, takeaway_chip="Ghi nhớ")
