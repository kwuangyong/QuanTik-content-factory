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


def build(ep, model, ctx):
    return P.pillar_build(ep, model, ctx, ROLES, VISUALS, takeaway_chip="Ghi nhớ")
