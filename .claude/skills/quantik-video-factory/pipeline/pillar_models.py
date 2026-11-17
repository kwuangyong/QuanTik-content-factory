"""Runnable models for the new content pillars (behavioral finance, decision science, market intelligence).

Same contract as models.py: ``<topic>_demo`` is the exact code shown on screen (keep it short), ``compute_<topic>``
returns (values, formats, series), ``plot2d_<topic>(ax, series, upto)`` and ``surface_<topic>(series, values)``.
Every number a pillar episode says must come from these values, from the market report, or from a sourced fact.

  prospect_theory  Tversky–Kahneman (1992) value function; parameters are sourced facts, results are computed.
  ev_variance      a winning poker player's results: EV vs variance, % still losing after n hands, risk of ruin.
  kuhn_poker       counterfactual regret minimisation on Kuhn (1950) poker → Nash equilibrium, game value −1/18.
  escape_velocity  dark-truth: 2,000 simulated careers, spend vs save each raise → how many ever break free.
  market_snapshot  built from a market_report.json (pipeline/market/analyze.py); never simulated.

python pillar_models.py prospect_theory   → print the placeholders an episode can use.
"""
from __future__ import annotations

import inspect
import json
import math
from pathlib import Path

import numpy as np

from core import THEME, hex_
from models import TOPICS as BASE_TOPICS, Model as BaseModel, _style

ACC, POS, NEG, NEU, MUT, TXT = (hex_(THEME[k]) for k in ("accent", "positive", "negative", "neutral", "muted", "text"))


def _phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


# =============================================================== prospect theory
def prospect_theory_demo(seed=0, a=0.88, lam=2.25):
    x = np.linspace(-10, 10, 401)     # triệu đồng
    v = np.where(x >= 0, np.abs(x) ** a,
                 -lam * np.abs(x) ** a)
    pain = lam                        # |v(-1)| / v(+1)
    # cược 50/50 mất 1: lãi tối thiểu để chịu chơi
    g_min = lam ** (1 / a)
    return x, v, pain, g_min


def compute_prospect_theory(seed=0, returns=None):
    x, v, pain, g_min = prospect_theory_demo(seed)
    a, lam = 0.88, 2.25
    values = {"alpha": a, "lam": lam, "pain": pain, "g_min": g_min,
              "v_gain10": 10 ** a, "v_loss10": -lam * 10 ** a, "ref_point": 0}
    formats = {"alpha": "num2", "lam": "num2", "pain": "num2", "g_min": "num2", "v_gain10": "num1",
               "v_loss10": "num1", "ref_point": "int"}
    return values, formats, {"x": x, "v": v, "g_min": g_min}


def plot2d_prospect_theory(ax, s, upto=1.0):
    x, v = s["x"], s["v"]
    k = max(2, int(len(x) * upto))
    m = len(x) // 2
    lo, hi = x[:m + 1], v[:m + 1]
    ax.axhline(0, color=MUT, lw=1); ax.axvline(0, color=MUT, lw=1)
    ax.plot(x[m:k] if k > m else x[m:m + 1], v[m:k] if k > m else v[m:m + 1], color=POS, lw=4, label="lãi")
    kk = min(k, m + 1)
    ax.plot(lo[m + 1 - kk:], hi[m + 1 - kk:], color=NEG, lw=4, label="lỗ")
    ax.plot(x, x, color=MUT, lw=1.5, ls="--", label="trung tính")
    ax.set_xlim(-10.5, 10.5); ax.set_ylim(v.min() * 1.05, -v.min() * 0.6)
    ax.set_xlabel("lãi / lỗ (triệu đồng)"); ax.set_ylabel("giá trị cảm nhận")
    ax.legend(loc="upper left", fontsize=18, frameon=False, labelcolor=TXT)


def surface_prospect_theory(s, v):
    """Value function across loss-aversion levels: the loss side steepens as λ grows (the kink at 0 deepens)."""
    a = v["alpha"]
    x = np.linspace(-10, 10, 61); lam = np.linspace(1.0, 3.0, 41)
    X, L = np.meshgrid(x, lam)
    Z = np.where(X >= 0, np.abs(X) ** a, -L * np.abs(X) ** a)
    return {"X": X, "Y": L, "Z": Z, "xl": "lãi / lỗ (triệu)", "yl": "hệ số né lỗ λ", "zl": "giá trị cảm nhận"}


# =============================================================== EV vs variance (poker)
def ev_variance_demo(seed=9, players=2000, blocks=1000):
    rng = np.random.default_rng(seed)
    mu, sd = 5.0, 100.0        # bb mỗi 100 tay
    x = rng.normal(mu, sd, (players, blocks))
    bank = x.cumsum(axis=1)    # lãi lỗ luỹ kế
    behind = (bank < 0).mean(axis=0)
    B = 1000                   # vốn 1.000 bb
    ruined = (bank.min(axis=1) <= -B).mean()
    ror = math.exp(-2 * mu * B / sd ** 2)
    return bank, behind, ruined, ror, mu, sd, B


def compute_ev_variance(seed=9, returns=None):
    bank, behind, ruined, ror, mu, sd, B = ev_variance_demo(seed)
    n = bank.shape[0]
    values = {
        "players": n, "mu": mu, "sd": sd, "bankroll": B, "hands_total": bank.shape[1] * 100,
        "behind_1k": float(behind[9]), "behind_10k": float(behind[99]), "behind_100k": float(behind[-1]),
        "theory_10k": _phi(-mu * math.sqrt(100) / sd), "theory_100k": _phi(-mu * math.sqrt(1000) / sd),
        "ruined": float(ruined), "ror": ror, "ev_100k": mu * bank.shape[1],
        "worst_100k": float(bank[:, -1].min()), "best_100k": float(bank[:, -1].max()),
        "median_100k": float(np.median(bank[:, -1])),
    }
    formats = {"players": "int", "mu": "num0", "sd": "num0", "bankroll": "int", "hands_total": "int",
               "behind_1k": "pct0", "behind_10k": "pct0", "behind_100k": "pct0", "theory_10k": "pct0",
               "theory_100k": "pct0", "ruined": "pct0", "ror": "pct0", "ev_100k": "int", "worst_100k": "int",
               "best_100k": "int", "median_100k": "int"}
    return values, formats, {"bank": bank, "mu": mu}


def plot2d_ev_variance(ax, s, upto=1.0):
    bank = s["bank"]; T = bank.shape[1]; k = max(2, int(T * upto)); x = np.arange(1, T + 1) * 100 / 1000
    for i in range(60):
        ax.plot(x[:k], bank[i, :k], color=POS if bank[i, -1] >= 0 else NEG, lw=1, alpha=0.35)
    ax.plot(x[:k], (s["mu"] * np.arange(1, T + 1))[:k], color=ACC, lw=4, label="kỳ vọng (EV)")
    ax.axhline(0, color=MUT, lw=1.5)
    lim = np.abs(bank[:60]).max() * 1.05
    ax.set_xlim(0, x[-1]); ax.set_ylim(-lim, lim)
    ax.set_xlabel("nghìn ván"); ax.set_ylabel("lãi/lỗ luỹ kế (bb)")
    ax.legend(loc="upper left", fontsize=18, frameon=False, labelcolor=TXT)


def surface_ev_variance(s, v):
    wr = np.linspace(1, 10, 40); n = np.linspace(1, 200, 50)       # bb/100, nghìn ván
    W, N = np.meshgrid(wr, n)
    Z = np.vectorize(_phi)(-W * np.sqrt(N * 10) / v["sd"])
    return {"X": W, "Y": N, "Z": Z * 100, "xl": "lợi thế bb/100", "yl": "nghìn ván", "zl": "% vẫn đang lỗ"}


# =============================================================== Kuhn poker (Nash via CFR)
def kuhn_poker_demo(seed=0, iters=3000):
    R, S = {}, {}          # hối tiếc, tổng chiến lược
    def cfr(c, h, p):      # p: xác suất tới đây, 2 bên
        pl = len(h) % 2; me, op = c[pl], c[1 - pl]
        if h in ("bp", "pbp"): return 1   # đối thủ bỏ
        if h in ("pp", "bb", "pbb"):           # lật bài
            w = 1 if me > op else -1
            return (1 if h == "pp" else 2) * w
        k = str(me) + h
        r = R.setdefault(k, np.zeros(2))
        s = np.maximum(r, 0)
        s = s / s.sum() if s.sum() else np.full(2, .5)
        S[k] = S.get(k, 0) + p[pl] * s
        u = np.zeros(2)
        for i, a in enumerate("pb"):      # xem / tố
            q = list(p); q[pl] *= s[i]
            u[i] = -cfr(c, h + a, q)
        R[k] += p[1 - pl] * (u - s @ u)
        return s @ u
    deals = [(a, b) for a in range(3)
             for b in range(3) if a != b]  # 6 cách
    v = np.mean([cfr(d, "", [1, 1])
                 for _ in range(iters) for d in deals])
    return v, {k: S[k] / S[k].sum() for k in S}


def compute_kuhn_poker(seed=0, returns=None):
    v, strat = kuhn_poker_demo(seed)
    bet = lambda k: float(strat[k][1])
    values = {"game_value": v, "theory_value": -1 / 18, "j_bluff": bet("0"), "k_bet": bet("2"),
              "q_call": bet("1b"), "j_call": bet("0b"), "k_call": bet("2b"), "ratio_k_j": bet("2") / max(bet("0"), 1e-9)}
    formats = {"game_value": "num3", "theory_value": "num3", "j_bluff": "pct0", "k_bet": "pct0", "q_call": "pct0",
               "j_call": "pct0", "k_call": "pct0", "ratio_k_j": "num1"}
    return values, formats, {"strat": strat}


def plot2d_kuhn_poker(ax, s, upto=1.0):
    st = s["strat"]
    keys = [("0", "J, đi trước: tố"), ("1", "Q, đi trước: tố"), ("2", "K, đi trước: tố"),
            ("0b", "J, bị tố: theo"), ("1b", "Q, bị tố: theo"), ("2b", "K, bị tố: theo")]
    k = max(1, int(round(len(keys) * upto)))
    ys = np.arange(len(keys))[::-1]
    for (key, lab), y in list(zip(keys, ys))[:k]:
        p = float(st[key][1]) * 100
        ax.barh(y, p, color=ACC if "bị" not in lab else POS, height=0.6)
        ax.text(-3, y, lab, va="center", ha="right", fontsize=17, color=TXT)   # label inside the axes: never clipped
        ax.text(p + 2, y, f"{p:.0f}%", va="center", fontsize=17, color=TXT)
    ax.set_yticks([]); ax.set_xlim(-68, 118); ax.set_xticks([0, 50, 100]); ax.axvline(0, color=MUT, lw=1)
    ax.set_xlabel("tần suất (%) ở cân bằng")


def surface_kuhn_poker(s, v):
    return None   # no computed 3D view for Kuhn poker: scenes fall back to text rather than show an illustrative surface


# =============================================================== Escape velocity (dark-truth pillar: savings vs lifestyle creep)
def escape_velocity_demo(seed=9, years=40, n=2000):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.05, 0.15, (n, years))  # real
    pay = 1.02 ** np.arange(years)   # +2%/yr raises
    def career(save, creep):
        spend = pay * (1 - save) if creep \
            else np.full(years, 1 - save)
        nest, cover = np.zeros(n), []
        for t in range(years):
            nest = nest*(1+r[:, t]) + pay[t] - spend[t]
            cover.append(0.04 * nest / spend[t])
        return np.array(cover).T     # paths x years
    a = career(0.10, creep=True)     # spend raises
    b = career(0.10, creep=False)    # save raises
    return a, b, pay


def compute_escape_velocity(seed=9, returns=None):
    a, b, pay = escape_velocity_demo(seed)
    n, years = a.shape
    ma, mb = np.median(a, 0), np.median(b, 0)
    yr_b = int(np.argmax(mb >= 1) + 1) if (mb >= 1).any() else years
    values = {
        "years": years, "n_paths": n, "save": 0.10, "raise": 0.02, "ret": 0.05, "vol": 0.15, "wr": 0.04,
        "target_x": 1 / 0.04,
        "cover_a10": ma[9], "cover_a20": ma[19], "cover_a40": ma[-1],
        "cover_b10": mb[9], "cover_b20": mb[19], "cover_b40": mb[-1],
        "esc_a": float((a >= 1).any(1).mean()), "esc_b": float((b >= 1).any(1).mean()),
        "esc_a_n": int((a >= 1).any(1).sum()), "trapped_a_n": int((~(a >= 1).any(1)).sum()),
        "yr_b": yr_b, "pay_growth": float(pay[-1] / pay[0] - 1),
        "save_b_end": float(1 - 0.9 / pay[-1]), "gap": float(mb[-1] / ma[-1]),
    }
    formats = {"years": "int", "n_paths": "int", "save": "pct0", "raise": "pct0", "ret": "pct0", "vol": "pct0",
               "wr": "pct0", "target_x": "int", "esc_a": "pct1", "esc_b": "pct0", "esc_a_n": "int",
               "trapped_a_n": "int", "yr_b": "int", "pay_growth": "pct0", "save_b_end": "pct0", "gap": "x1"}
    formats.update({k: "pct0" for k in values if k.startswith("cover_")})
    return values, formats, {"a": a, "b": b}


def plot2d_escape_velocity(ax, s, upto=1.0):
    a, b = s["a"] * 100, s["b"] * 100
    years = a.shape[1]; x = np.arange(1, years + 1); k = max(2, int(round(years * upto)))
    ax.axhline(100, color=TXT, lw=2, ls="--", alpha=0.8)
    ax.text(1.2, 106, "ESCAPE VELOCITY · investments pay all bills", color=TXT, fontsize=17, fontweight="bold")
    for arr, c, name in ((b, POS, "save the raises"), (a, NEG, "spend the raises")):
        lo, mid, hi = (np.percentile(arr, q, axis=0) for q in (10, 50, 90))
        ax.fill_between(x[:k], lo[:k], np.minimum(hi[:k], 250), color=c, alpha=0.14, lw=0)
        ax.plot(x[:k], mid[:k], color=c, lw=3.4, label=name)
    ax.set_xlim(1, years); ax.set_ylim(0, 250)
    ax.set_xlabel("years of 9-to-5 work"); ax.set_ylabel("% of yearly spending your money pays")
    ax.legend(loc="upper left", bbox_to_anchor=(0, 0.93), fontsize=18, frameon=False, labelcolor=TXT)


def surface_escape_velocity(s, v):
    """Median-growth (deterministic) coverage after 40 years over savings rate × share of each raise spent."""
    g = 0.05 - 0.15 ** 2 / 2
    sr = np.linspace(0.05, 0.5, 30); cr = np.linspace(0, 1, 25)
    S_, C_ = np.meshgrid(sr, cr)
    pay = 1.02 ** np.arange(40)
    nest = np.zeros_like(S_)
    for t in range(40):
        spend = (1 - S_) * (1 + C_ * (pay[t] - 1))
        nest = nest * np.exp(g) + pay[t] - spend
    Z = np.minimum(0.04 * nest / spend * 100, 300)
    return {"X": S_ * 100, "Y": C_ * 100, "Z": Z, "xl": "savings rate %", "yl": "% of raises spent",
            "zl": "% of bills paid"}


# =============================================================== Same salary, three futures (dark-truth #2)
def same_salary_demo(seed=9, years=10, n=2000):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.05, 0.15, (n, years))  # real
    save = {"spender": 0.0, "middle": 0.10,
            "builder": 0.25}         # same pay
    runway = {}
    for who, s in save.items():
        nest = np.zeros(n)
        for t in range(years):
            nest = nest * (1 + r[:, t]) + s
        # months you could live with no paycheck
        runway[who] = nest / (1 - s) * 12
    return runway


def compute_same_salary(seed=9, returns=None):
    rw = same_salary_demo(seed)
    n = len(rw["builder"])
    values = {"years": 10, "n_paths": n, "ret": 0.05, "vol": 0.15,
              "save_s": 0.0, "save_m": 0.10, "save_b": 0.25,
              "months_s": float(np.median(rw["spender"])), "months_m": float(np.median(rw["middle"])),
              "months_b": float(np.median(rw["builder"])),
              "esc_a_n": int((rw["builder"] >= 36).sum())}
    formats = {"years": "int", "n_paths": "int", "ret": "pct0", "vol": "pct0", "save_s": "pct0",
               "save_m": "pct0", "save_b": "pct0", "months_s": "int", "months_m": "int", "months_b": "int",
               "esc_a_n": "int"}
    return values, formats, rw


def plot2d_same_salary(ax, s, upto=1.0):
    names = [("spender", NEG), ("middle", TXT), ("builder", POS)]
    for i, (k, c) in enumerate(names):
        ax.bar(i, np.median(s[k]) * upto, color=c, width=0.6)
    ax.set_xticks(range(3)); ax.set_xticklabels([k for k, _ in names])
    ax.set_ylabel("months you could live with no paycheck")


def surface_same_salary(s, v):
    return None


# =============================================================== LARP: the cost of looking rich (dark-truth #3)
def larp_demo(seed=9, years=10, n=2000, flex=0.25, dep=0.30):
    rng = np.random.default_rng(seed)
    r = rng.normal(0.05, 0.15, (n, years))  # real
    stuff, kept = 0.0, np.zeros(n)  # in years of pay
    for t in range(years):
        # what the flex is worth on resale
        stuff = stuff * (1 - dep) + flex
        # same money, owned quietly instead
        kept = kept * (1 + r[:, t]) + flex
    return flex * years, stuff, kept


def compute_larp(seed=9, returns=None):
    spent, stuff, kept = larp_demo(seed)
    values = {"years": 10, "n_paths": len(kept), "flex": 0.25, "dep": 0.30, "ret": 0.05, "vol": 0.15,
              "spent": float(spent), "stuff_left": float(stuff), "kept_med": float(np.median(kept)),
              "esc_a_n": 0}
    formats = {"years": "int", "n_paths": "int", "flex": "pct0", "dep": "pct0", "ret": "pct0", "vol": "pct0",
               "spent": "num1", "stuff_left": "num1", "kept_med": "num1", "esc_a_n": "int"}
    return values, formats, {"kept": kept, "spent": spent, "stuff": stuff}


def plot2d_larp(ax, s, upto=1.0):
    ax.bar([0, 1, 2], [s["spent"] * upto, s["stuff"] * upto, np.median(s["kept"]) * upto],
           color=[TXT, NEG, POS], width=0.6)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["spent", "resale", "owned"])
    ax.set_ylabel("years of salary")


def surface_larp(s, v):
    return None


# =============================================================== Credit, the double-edged blade (dark-truth #4)
def credit_demo(seed=0, apr=0.24, grow=0.05):
    b, paid, months = 1.0, 0.0, 0  # owe 1 month's pay
    while b > 1e-9:
        i = b * apr / 12
        # minimum: interest + 1% of balance,
        # never below 2.5% of what you borrowed
        pay = min(b + i, max(i + 0.01 * b, 0.025))
        b, paid, months = b + i - pay, paid + pay, months + 1
    # same compounding, the other edge
    double_debt = np.log(2) / np.log(1 + apr / 12) / 12
    double_asset = np.log(2) / np.log(1 + grow)
    return months, paid, double_debt, double_asset


def compute_credit(seed=0, returns=None):
    months, paid, dd, da = credit_demo(seed)
    values = {"apr": 0.24, "grow": 0.05, "min_pct": 0.01, "floor": 0.025, "payoff_years": months / 12, "payoff_months": months, "paid_x": paid,
              "interest_x": paid - 1, "double_debt": dd, "double_asset": da, "esc_a_n": 0, "n_paths": 1}
    formats = {"apr": "pct0", "grow": "pct0", "min_pct": "pct0", "floor": "pct1", "payoff_years": "num1", "payoff_months": "int", "paid_x": "x1",
               "interest_x": "pct0", "double_debt": "num1", "double_asset": "num0", "esc_a_n": "int",
               "n_paths": "int"}
    return values, formats, {"months": months}


def plot2d_credit(ax, s, upto=1.0):
    ax.text(0.5, 0.5, "minimum payments", ha="center", color=TXT)


def surface_credit(s, v):
    return None


TOPICS = ["prospect_theory", "ev_variance", "kuhn_poker", "escape_velocity", "same_salary", "larp", "credit"]


class Model(BaseModel):
    """models.Model with this module's registry."""

    def __init__(self, topic, seed=None, returns=None):
        if topic not in TOPICS:
            raise ValueError(f"unknown pillar model {topic}; known: {TOPICS}")
        g = globals()
        self.topic = topic
        demo = g[f"{topic}_demo"]
        self.seed = seed if seed is not None else inspect.signature(demo).parameters["seed"].default
        self.values, self.formats, self.series = g[f"compute_{topic}"](self.seed, returns)
        self.values = {k: (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int))
                           else v) for k, v in self.values.items()}
        self.code = inspect.getsource(demo).rstrip()
        self._plot2d = g[f"plot2d_{topic}"]
        self._surface = g[f"surface_{topic}"]
        self.real_data = False
        self.has_surface = self._surface(self.series, self.values) is not None


# =============================================================== market snapshot (from a report, never simulated)
class MarketModel:
    """Exposes a market_report.json as values/formats + a sector/breadth chart. No surface, no code."""

    has_surface = False
    code = ""

    def __init__(self, report_path):
        self.path = Path(report_path)
        self.report = json.loads(self.path.read_text(encoding="utf-8"))
        self.topic = "market_snapshot"
        self.seed = 0
        self.real_data = self.report["data_status"] in ("fresh", "intraday", "stale")
        self.values, self.formats = {}, {}
        for group in ("observed", "model"):
            for k, item in self.report.get(group, {}).items():
                if item.get("value") is None:
                    continue
                self.values[k] = item["value"]
                if item.get("fmt"):
                    self.formats[k] = item["fmt"]
        self.values["as_of"] = _vi_date(self.report.get("as_of"))
        self.sectors = [s for s in (self.report.get("sectors") or []) if s.get("median_change") is not None]
        self.has_chart = bool(self.sectors) or "adv" in self.values
        self.run_title = "dữ liệu quan sát · " + (self.values["as_of"] or "không có ngày")
        self.series = {}

    def plot2d(self, ax, upto=1.0):
        if self.sectors:
            sec = sorted(self.sectors, key=lambda s: s["median_change"])
            if len(sec) > 12:                      # keep both ends: the leader and laggard named in the narration
                sec = sec[:6] + sec[-6:]
            k = max(1, int(round(len(sec) * upto)))
            ys = np.arange(len(sec))
            lim = max(abs(s["median_change"]) for s in sec) * 100 * 2.6 or 1
            for (s, y) in list(zip(sec, ys))[:k]:
                val = s["median_change"] * 100
                ax.barh(y, val, color=POS if val >= 0 else NEG, height=0.62)
                name = s["name"].split(" (")[0][:20]
                # name on the opposite side of zero, value at the bar end: nothing is clipped by the axes
                ax.text(-0.04 * lim if val >= 0 else 0.04 * lim, y, name, va="center", ha="right" if val >= 0 else "left",
                        fontsize=15, color=TXT)
                ax.text(val + (0.03 * lim if val >= 0 else -0.03 * lim), y, f"{val:+.2f}%".replace(".", ","),
                        va="center", ha="left" if val >= 0 else "right", fontsize=15, color=MUT)
            ax.set_yticks([]); ax.set_xlim(-lim, lim); ax.set_ylim(-0.7, len(sec) - 0.3); ax.axvline(0, color=MUT, lw=1)
            ax.set_xlabel("trung vị % thay đổi trong nhóm")
        else:
            v = self.values
            ax.bar([0, 1, 2], [v.get("adv", 0), v.get("dec", 0), v.get("unch", 0)], color=[POS, NEG, NEU])
            ax.set_xticks([0, 1, 2]); ax.set_xticklabels(["tăng", "giảm", "đứng"], fontsize=18, color=TXT)
        _style(ax)

    def surface(self):
        return None


def _vi_date(iso):
    if not iso:
        return ""
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


class NullModel:
    """Pillar topic with no runnable model: narration-only scenes; any number must be a sourced fact."""

    has_chart = has_surface = False
    code = ""

    def __init__(self, topic):
        self.topic, self.seed, self.real_data = topic, 0, False
        self.values, self.formats, self.series, self.entry = {}, {}, {}, {"vi": topic}

    def plot2d(self, ax, upto=1.0):
        pass

    def surface(self):
        return None


def make_model(name, seed=None, returns=None, ep=None):
    """Dispatch a model name from a pillar catalog / episode to the right implementation."""
    if name == "market_snapshot":
        if not (ep or {}).get("market_report"):
            raise SystemExit("market episode needs 'market_report' (path to market_report.json)")
        return MarketModel(ep["market_report"])
    if name in TOPICS:
        return Model(name, seed, returns)
    if name in BASE_TOPICS:
        return BaseModel(name, seed, returns)
    return NullModel((ep or {}).get("topic", "topic"))


if __name__ == "__main__":
    import sys

    from core import fmt_vi

    for t in (sys.argv[1:] or TOPICS):
        m = Model(t)
        print(f"\n# {t}  (seed {m.seed})")
        for k, v in m.values.items():
            print(f"  {{{k}}}".ljust(22), fmt_vi(v, m.formats.get(k, "num2")).ljust(12), f"[{m.formats.get(k, 'num2')}]")
