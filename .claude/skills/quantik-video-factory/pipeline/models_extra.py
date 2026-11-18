"""Mô hình viết tay bổ sung (cùng giao diện với models.py): <topic>_demo · compute_<topic> · plot2d_<topic> · surface_<topic>.

Code trong ``<topic>_demo`` hiện nguyên văn trên màn hình: ≤ 16 dòng, ≤ 56 ký tự/dòng.
Mọi số nói hoặc hiện trong video lấy từ ``values``. Dữ liệu mô phỏng với seed cố định.
"""
from __future__ import annotations

import math

import numpy as np

from core import THEME, hex_

ACC, POS, NEG, NEU, MUT, TXT = (hex_(THEME[k]) for k in ("accent", "positive", "negative", "neutral", "muted", "text"))


def _skew(v):
    v = np.asarray(v, float)
    return float(((v - v.mean()) ** 3).mean() / v.std() ** 3)


def _ncdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _ninv(p, lo=-10.0, hi=10.0):
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _ncdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


# =============================================================== RSI (Wilder 1978)
def rsi_demo(seed=5, n=2000, period=14):
    rng = np.random.default_rng(seed)
    p = 100 * np.exp(np.cumsum(rng.normal(0, .02, n)))
    d = np.diff(p)
    up, dn = np.clip(d, 0, None), np.clip(-d, 0, None)
    au, ad = up[:period].mean(), dn[:period].mean()
    rsi = np.full(n, np.nan)
    for t in range(period, n - 1):
        au = (au*(period-1) + up[t]) / period  # Wilder
        ad = (ad*(period-1) + dn[t]) / period
        rsi[t + 1] = 100 - 100 / (1 + au/ad)
    return p, rsi


def compute_rsi(seed=5, returns=None, **kw):
    p, rsi = rsi_demo(seed, **kw)
    h = 10
    fwd = np.full(len(p), np.nan)
    fwd[:-h] = p[h:] / p[:-h] - 1
    ok = ~np.isnan(rsi) & ~np.isnan(fwd)
    ob, os_ = ok & (rsi > 70), ok & (rsi < 30)
    values = {"rsi_last": float(rsi[-1]), "rsi_max": float(np.nanmax(rsi)), "rsi_min": float(np.nanmin(rsi)),
              "days_ob": int(ob.sum()), "days_os": int(os_.sum()), "hi": 70, "lo": 30,
              "period": kw.get("period", 14), "fwd_days": h, "n_days": len(p),
              "fwd_ob": float(fwd[ob].mean()) if ob.any() else 0.0,
              "up_after_ob": float((fwd[ob] > 0).mean()) if ob.any() else 0.0,
              "fwd_all": float(fwd[ok].mean())}
    formats = {"rsi_last": "num0", "rsi_max": "num0", "rsi_min": "num0", "days_ob": "int", "days_os": "int", "hi": "int",
               "lo": "int", "period": "int", "fwd_days": "int", "n_days": "int", "fwd_ob": "pct1", "up_after_ob": "pct0",
               "fwd_all": "pct1"}
    return values, formats, {"p": p, "rsi": rsi}


def plot2d_rsi(ax, s, upto=1.0):
    p, rsi = s["p"], s["rsi"]; n = len(p); k = max(2, int(n * upto)); x = np.arange(n)
    pn = 110 + 80 * (p - p.min()) / (p.max() - p.min())       # giá vẽ ở nửa trên (thang riêng)
    ax.plot(x[:k], pn[:k], color=MUT, lw=1.8)
    ax.axhspan(70, 100, color=NEG, alpha=0.10); ax.axhspan(0, 30, color=POS, alpha=0.10)
    ax.axhline(70, color=NEG, lw=1, ls="--"); ax.axhline(30, color=POS, lw=1, ls="--")
    ax.plot(x[:k], rsi[:k], color=ACC, lw=2.2)
    ax.set_xlim(0, n); ax.set_ylim(0, 195); ax.set_yticks([0, 30, 70, 100])
    ax.set_xlabel("phiên"); ax.set_ylabel("RSI (dưới) · giá (trên, xám)")


def surface_rsi(s, v):
    rsi = s["rsi"]; n = len(rsi)
    bins = np.linspace(0, 100, 41); t = np.arange(40, n, 8)
    Z = np.array([np.histogram(rsi[max(0, i - 60):i][~np.isnan(rsi[max(0, i - 60):i])], bins, density=True)[0] for i in t]).T
    T, Y = np.meshgrid(t, (bins[:-1] + bins[1:]) / 2)
    return {"X": T, "Y": Y, "Z": Z, "xl": "phiên", "yl": "RSI", "zl": "tần suất"}


# =============================================================== Max drawdown
def max_drawdown_demo(seed=3, n=750, mu=.0004, sd=.018):
    rng = np.random.default_rng(seed)
    p = 100 * np.exp(np.cumsum(rng.normal(mu, sd, n)))
    peak = np.maximum.accumulate(p)
    dd = p / peak - 1            # sụt giảm từ đỉnh
    mdd = -dd.min()
    need = mdd / (1 - mdd)       # phải tăng để về đỉnh
    return p, dd, mdd, need


def compute_max_drawdown(seed=3, returns=None, **kw):
    p, dd, mdd, need = max_drawdown_demo(seed, **kw)
    under, longest = 0, 0
    for x in dd:
        under = under + 1 if x < 0 else 0
        longest = max(longest, under)
    values = {"mdd": float(mdd), "need_mdd": float(need), "underwater_days": int(longest), "n_days": len(p),
              "total_return": float(p[-1] / p[0] - 1)}
    for L in (0.1, 0.3, 0.5, 0.8):
        values[f"loss_{int(L*100)}"] = L
        values[f"need_{int(L*100)}"] = L / (1 - L)
    formats = {k: "pct0" for k in values}
    formats.update({"mdd": "pct1", "need_mdd": "pct0", "underwater_days": "int", "n_days": "int", "total_return": "pct0"})
    return values, formats, {"p": p, "dd": dd}


def plot2d_max_drawdown(ax, s, upto=1.0):
    p, dd = s["p"], s["dd"]; n = len(p); k = max(2, int(n * upto)); x = np.arange(n)
    lo = dd.min() * 100
    ax.fill_between(x[:k], 0, dd[:k] * 100, color=NEG, alpha=0.35)
    ax.plot(x[:k], dd[:k] * 100, color=NEG, lw=1.6)
    pn = 5 + (-lo) * 0.9 * (p - p.min()) / (p.max() - p.min())          # giá ở nửa trên, thang riêng
    ax.plot(x[:k], pn[:k], color=POS, lw=2.2)
    i = int(np.argmin(dd[:k]))
    ax.scatter([i], [dd[i] * 100], color=ACC, s=120, zorder=5)
    ax.set_xlim(0, n); ax.set_ylim(lo * 1.1, -lo + 10); ax.axhline(0, color=MUT, lw=1)
    ax.set_xlabel("phiên"); ax.set_ylabel("sụt giảm từ đỉnh % (dưới) · giá (trên)")


def surface_max_drawdown(s, v):
    L = np.linspace(0.05, 0.6, 40); r = np.linspace(0.05, 0.3, 40)
    Lm, R = np.meshgrid(L, r)
    Y = np.log(1 / (1 - Lm)) / np.log(1 + R)        # số năm để về đỉnh
    return {"X": Lm * 100, "Y": R * 100, "Z": Y, "xl": "mức sụt %", "yl": "lãi/năm %", "zl": "số năm về đỉnh"}


# =============================================================== Beta
def beta_demo(seed=5, n=500, b_a=0.6, b_b=1.8):
    rng = np.random.default_rng(seed)
    m = rng.normal(.0004, .012, n)       # thị trường
    a = b_a*m + rng.normal(0, .010, n)   # mã A
    b = b_b*m + rng.normal(0, .012, n)   # mã B
    C = np.cov([m, a, b])
    beta_a = C[0, 1] / C[0, 0]           # cov / var
    beta_b = C[0, 2] / C[0, 0]
    return m, a, b, beta_a, beta_b


def compute_beta(seed=5, returns=None, **kw):
    m, a, b, ba, bb = beta_demo(seed, **kw)
    i = int(np.argmin(m))
    values = {"beta_a": float(ba), "beta_b": float(bb), "corr_a": float(np.corrcoef(m, a)[0, 1]),
              "corr_b": float(np.corrcoef(m, b)[0, 1]), "mkt_worst": float(m[i]), "a_worst": float(a[i]), "b_worst": float(b[i]),
              "vol_m": float(m.std() * math.sqrt(252)), "vol_a": float(a.std() * math.sqrt(252)),
              "vol_b": float(b.std() * math.sqrt(252)), "n_days": len(m)}
    formats = {"beta_a": "num2", "beta_b": "num2", "corr_a": "num2", "corr_b": "num2", "mkt_worst": "pct1", "a_worst": "pct1",
               "b_worst": "pct1", "vol_m": "pct0", "vol_a": "pct0", "vol_b": "pct0", "n_days": "int"}
    return values, formats, {"m": m, "a": a, "b": b, "ba": ba, "bb": bb}


def plot2d_beta(ax, s, upto=1.0):
    m, a, b = s["m"] * 100, s["a"] * 100, s["b"] * 100; n = len(m); k = max(2, int(n * upto))
    ax.scatter(m[:k], a[:k], s=14, color=POS, alpha=0.55, label=f"A · β {s['ba']:.2f}".replace(".", ","))
    ax.scatter(m[:k], b[:k], s=14, color=NEG, alpha=0.55, label=f"B · β {s['bb']:.2f}".replace(".", ","))
    xx = np.linspace(m.min(), m.max(), 10)
    if upto > 0.5:
        ax.plot(xx, s["ba"] * xx, color=POS, lw=3); ax.plot(xx, s["bb"] * xx, color=NEG, lw=3)
    lim = max(abs(b).max(), abs(a).max()) * 1.05
    ax.set_xlim(m.min() * 1.1, m.max() * 1.1); ax.set_ylim(-lim, lim)
    ax.axhline(0, color=MUT, lw=1); ax.axvline(0, color=MUT, lw=1)
    ax.set_xlabel("lợi suất thị trường %"); ax.set_ylabel("lợi suất cổ phiếu %")
    ax.legend(loc="upper left", fontsize=18, frameon=False, labelcolor=TXT)


def surface_beta(s, v):
    x = np.arange(len(s["m"]))[::3]
    lines = []
    for i, (key, c) in enumerate((("a", POS), ("m", MUT), ("b", NEG))):
        z = np.cumsum(s[key])[::3] * 100
        lines.append((x, np.full(len(x), i), z, c))
    return {"lines": lines, "xl": "phiên", "yl": "", "zl": "lợi suất cộng dồn %", "yticks": ["A", "thị trường", "B"]}


# =============================================================== OLS
def ols_demo(seed=2, n=120, b=0.8):
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    y = 0.2 + b*x + rng.normal(0, .6, n)
    X = np.column_stack([np.ones(n), x])
    a_hat, b_hat = np.linalg.solve(X.T @ X, X.T @ y)
    res = y - (a_hat + b_hat*x)          # phần dư
    r2 = 1 - res.var() / y.var()
    return x, y, a_hat, b_hat, r2


def compute_ols(seed=2, returns=None, **kw):
    x, y, a, b, r2 = ols_demo(seed, **kw)
    xo, yo = np.append(x, 4.0), np.append(y, -5.0)          # thêm đúng một điểm ngoại lai
    b_out, a_out = np.polyfit(xo, yo, 1)
    values = {"b_true": kw.get("b", 0.8), "a_hat": float(a), "b_hat": float(b), "r2": float(r2), "n": len(x),
              "b_out": float(b_out), "res_sd": float(np.std(y - a - b * x))}
    formats = {"b_true": "num1", "a_hat": "num2", "b_hat": "num2", "r2": "pct0", "n": "int", "b_out": "num2", "res_sd": "num2"}
    return values, formats, {"x": x, "y": y, "a": a, "b": b, "b_out": b_out, "a_out": a_out}


def plot2d_ols(ax, s, upto=1.0):
    x, y = s["x"], s["y"]; n = len(x); k = max(2, int(n * min(1, upto / 0.6)))
    ax.scatter(x[:k], y[:k], s=40, color=POS, alpha=0.8)
    if upto > 0.6:
        xx = np.linspace(-3.2, 4.2, 10)
        f = s["a"] + s["b"] * x
        ax.vlines(x, np.minimum(y, f), np.maximum(y, f), color=MUT, lw=0.8, alpha=0.6)
        ax.plot(xx, s["a"] + s["b"] * xx, color=ACC, lw=3.2, label="OLS")
    if upto > 0.85:
        ax.scatter([4.0], [-5.0], s=180, color=NEG, zorder=5)
        ax.plot(xx, s["a_out"] + s["b_out"] * xx, color=NEG, lw=2.4, ls="--", label="+1 điểm ngoại lai")
        ax.legend(loc="upper left", fontsize=18, frameon=False, labelcolor=TXT)
    ax.set_xlim(-3.2, 4.4); ax.set_ylim(-5.8, 4.5); ax.set_xlabel("x (biến giải thích)"); ax.set_ylabel("y")


def surface_ols(s, v):
    x, y = s["x"], s["y"]
    A, B = np.meshgrid(np.linspace(s["a"] - 1.5, s["a"] + 1.5, 50), np.linspace(s["b"] - 1.5, s["b"] + 1.5, 50))
    sse = ((y[None, None, :] - A[..., None] - B[..., None] * x[None, None, :]) ** 2).mean(-1)
    return {"X": A, "Y": B, "Z": sse, "xl": "hệ số chặn a", "yl": "độ dốc b", "zl": "sai số bình phương"}


# =============================================================== Luật số lớn & định lý giới hạn trung tâm
def lln_clt_demo(seed=8, n=5000, k=30):
    rng = np.random.default_rng(seed)
    x = rng.exponential(1.0, n)          # lệch phải, TB = 1
    run = np.cumsum(x) / np.arange(1, n + 1)
    means = rng.exponential(1, (4000, k)).mean(1)
    sk = lambda v: ((v-v.mean())**3).mean() / v.std()**3
    return x, run, means, sk(x), sk(means)


def compute_lln_clt(seed=8, returns=None, **kw):
    x, run, means, s1, sk = lln_clt_demo(seed, **kw)
    k = kw.get("k", 30)
    values = {"true_mean": 1.0, "mean_10": float(run[9]), "mean_100": float(run[99]), "mean_1000": float(run[999]),
              "mean_n": float(run[-1]), "n": len(x), "k": k, "skew_raw": float(s1), "skew_means": float(sk),
              "sd_means": float(means.std()), "sd_theory": 1 / math.sqrt(k)}
    formats = {"true_mean": "num1", "mean_10": "num2", "mean_100": "num2", "mean_1000": "num2", "mean_n": "num3",
               "n": "int", "k": "int", "skew_raw": "num1", "skew_means": "num2", "sd_means": "num2", "sd_theory": "num2"}
    return values, formats, {"run": run, "x": x, "seed": seed}


def plot2d_lln_clt(ax, s, upto=1.0):
    run = s["run"]; n = len(run); k = max(3, int(n ** max(0.3, upto)))
    t = np.arange(1, n + 1)
    ax.fill_between(t, 1 - 2 / np.sqrt(t), 1 + 2 / np.sqrt(t), color=POS, alpha=0.12)
    ax.axhline(1, color=POS, lw=1.4, ls="--")
    ax.plot(t[:k], run[:k], color=ACC, lw=2.4)
    ax.set_xscale("log"); ax.set_xlim(1, n); ax.set_ylim(0, 2.6)
    ax.set_xlabel("số quan sát (thang log)"); ax.set_ylabel("trung bình mẫu")


def surface_lln_clt(s, v):
    rng = np.random.default_rng(s["seed"] + 1)
    ks = np.arange(1, 31); bins = np.linspace(0, 3, 50)
    Z = np.array([np.histogram(rng.exponential(1.0, (3000, k)).mean(1), bins, density=True)[0] for k in ks]).T
    K, Y = np.meshgrid(ks, (bins[:-1] + bins[1:]) / 2)
    return {"X": K, "Y": Y, "Z": Z, "xl": "cỡ mẫu k", "yl": "trung bình mẫu", "zl": "mật độ"}


# =============================================================== EGARCH: tin xấu và tin tốt
def egarch_demo(seed=4, n=600, g=-0.12):
    rng = np.random.default_rng(seed)
    w, a, b = -0.17, 0.12, 0.98      # ω, α, β
    ls2 = np.full(n, w / (1 - b)); r = np.zeros(n)
    for t in range(1, n):
        z = r[t-1] / np.exp(ls2[t-1] / 2)
        ls2[t] = (w + b*ls2[t-1]
                  + a*(abs(z) - .8) + g*z)   # γ·z
        r[t] = np.exp(ls2[t] / 2) * rng.normal()
    vol = np.sqrt(np.exp(ls2) * 252)
    return r, vol, w, a, b


def _egarch_next(z, g, w=-0.17, a=0.12, b=0.98):
    base = w / (1 - b)
    return math.sqrt(math.exp(w + b * base + a * (abs(z) - .8) + g * z) * 252)


def compute_egarch(seed=4, returns=None, **kw):
    r, vol, w, a, b = egarch_demo(seed, **kw)
    g = kw.get("g", -0.12)
    down, up, base = _egarch_next(-2, g), _egarch_next(2, g), math.sqrt(math.exp(w / (1 - b)) * 252)
    values = {"gamma": g, "vol_base": base, "vol_down": down, "vol_up": up, "ratio": down / up,
              "vol_peak": float(vol.max()), "vol_min": float(vol.min()), "n_days": len(r), "shock": 2}
    formats = {"gamma": "num2", "vol_base": "pct1", "vol_down": "pct1", "vol_up": "pct1", "ratio": "x1",
               "vol_peak": "pct1", "vol_min": "pct1", "n_days": "int", "shock": "int"}
    return values, formats, {"r": r, "vol": vol, "g": g}


def plot2d_egarch(ax, s, upto=1.0):
    z = np.linspace(-4, 4, 200); k = max(2, int(len(z) * upto))
    e = np.array([_egarch_next(q, s["g"]) for q in z]) * 100
    sym = np.array([_egarch_next(q, 0.0) for q in z]) * 100
    ax.plot(z, sym, color=MUT, lw=2, ls="--", label="đối xứng (γ = 0)")
    ax.plot(z[:k], e[:k], color=ACC, lw=3.2, label="EGARCH (γ < 0)")
    ax.axvline(0, color=MUT, lw=1)
    ax.fill_between(z[:k], sym[:k], e[:k], where=z[:k] < 0, color=NEG, alpha=0.18)
    ax.set_xlim(-4, 4); ax.set_ylim(0, max(e.max(), sym.max()) * 1.1)
    ax.set_xlabel("cú sốc hôm qua (đơn vị σ)  ←  tin xấu · tin tốt  →"); ax.set_ylabel("biến động hôm nay % năm")
    ax.legend(loc="upper center", fontsize=18, frameon=False, labelcolor=TXT)


def surface_egarch(s, v):
    z = np.linspace(-4, 4, 50); g = np.linspace(-0.3, 0.05, 40)
    Zm, G = np.meshgrid(z, g)
    V = np.vectorize(_egarch_next)(Zm, G) * 100
    return {"X": Zm, "Y": G, "Z": V, "xl": "cú sốc (σ)", "yl": "γ", "zl": "biến động %"}


# =============================================================== Phân phối chuẩn, log-normal, đuôi dày
def fat_tails_demo(seed=6, n=2500, df=3):
    rng = np.random.default_rng(seed)
    t = rng.standard_t(df, n)
    t = t / t.std()                   # cùng σ = 1
    z = rng.normal(0, 1, n)
    k = lambda v: (v**4).mean() / v.var()**2 - 3
    big_t = (np.abs(t) > 4).sum()     # ngày "4 sigma"
    big_z = (np.abs(z) > 4).sum()
    px = 100 * np.exp(np.cumsum(.01 * t))   # log-normal
    return t, z, k(t), k(z), big_t, big_z, px


def compute_fat_tails(seed=6, returns=None, **kw):
    t, z, kt, kz, bt, bz, px = fat_tails_demo(seed, **kw)
    n = len(t)
    p4 = 2 * (1 - _ncdf(4))
    values = {"kurt_t": float(kt), "kurt_z": float(kz), "big_t": int(bt), "big_z": int(bz), "n_days": n,
              "years": n / 252, "expect_normal": n * p4, "once_every_years": 1 / (p4 * 252), "sigma_k": 4,
              "worst_t": float(np.abs(t).max()), "worst_z": float(np.abs(z).max()), "px_min": float(px.min())}
    formats = {"kurt_t": "num1", "kurt_z": "num1", "big_t": "int", "big_z": "int", "n_days": "int", "years": "num0",
               "expect_normal": "num1", "once_every_years": "num0", "sigma_k": "int", "worst_t": "num1", "worst_z": "num1",
               "px_min": "num0"}
    return values, formats, {"t": t, "z": z, "px": px}


def plot2d_fat_tails(ax, s, upto=1.0):
    bins = np.linspace(-8, 8, 81)
    hz, _ = np.histogram(s["z"], bins, density=True); ht, _ = np.histogram(s["t"], bins, density=True)
    c = (bins[:-1] + bins[1:]) / 2
    ax.plot(c, np.exp(-c ** 2 / 2) / math.sqrt(2 * math.pi), color=MUT, lw=2, ls="--", label="chuẩn (lý thuyết)")
    ax.bar(c, hz, width=0.2, color=POS, alpha=0.55, label="mẫu chuẩn")
    if upto > 0.4:
        ax.bar(c, ht, width=0.2, color=NEG, alpha=0.55, label="đuôi dày (t)")
    ax.axvline(-4, color=ACC, lw=1.2, ls=":"); ax.axvline(4, color=ACC, lw=1.2, ls=":")
    ax.set_yscale("log"); ax.set_ylim(1e-4, 1); ax.set_xlim(-8, 8)
    ax.set_xlabel("lợi suất (đơn vị σ)"); ax.set_ylabel("tần suất (thang log)")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_fat_tails(s, v):
    x = np.linspace(-6, 6, 80); dfs = np.linspace(2.5, 30, 40)
    X, D = np.meshgrid(x, dfs)
    lg = (np.vectorize(math.lgamma)((D + 1) / 2) - np.vectorize(math.lgamma)(D / 2)
          - 0.5 * np.log(D * math.pi) - (D + 1) / 2 * np.log1p(X ** 2 / D))
    return {"X": X, "Y": D, "Z": np.maximum(lg / math.log(10), -6), "xl": "lợi suất", "yl": "bậc tự do (đuôi mỏng →)",
            "zl": "log₁₀ mật độ"}


# =============================================================== Momentum
def momentum_demo(seed=9, n=200, look=120, hold=20,
                  s=.0006):
    rng = np.random.default_rng(seed)
    mu = rng.normal(0, s, n)          # lợi thế riêng mỗi mã
    r = mu + rng.normal(0, .02, (look + hold, n))
    past = r[:look].sum(0)            # lợi suất quá khứ
    fwd = r[look:].sum(0)             # lợi suất kế tiếp
    q = np.argsort(past)
    top, bot = q[-n // 5:], q[:n // 5]
    spread = fwd[top].mean() - fwd[bot].mean()
    return past, fwd, top, bot, spread


def compute_momentum(seed=9, returns=None, **kw):
    past, fwd, top, bot, spread = momentum_demo(seed, **kw)
    reps = 60   # lặp nhiều thế giới mô phỏng: một lần chạy có thể may
    sp_avg = float(np.mean([momentum_demo(seed + i, **kw)[4] for i in range(reps)]))
    sp0 = float(np.mean([momentum_demo(seed + i, **{**kw, "s": 0.0})[4] for i in range(reps)]))
    values = {"spread": float(spread), "top_fwd": float(fwd[top].mean()), "bot_fwd": float(fwd[bot].mean()),
              "corr": float(np.corrcoef(past, fwd)[0, 1]), "spread_noise": sp0, "spread_avg": sp_avg, "reps": reps, "n_stocks": len(past),
              "look": kw.get("look", 120), "hold": kw.get("hold", 20), "top_n": len(top)}
    formats = {"spread": "pct1", "top_fwd": "pct1", "bot_fwd": "pct1", "corr": "num2", "spread_noise": "pct1",
               "spread_avg": "pct1", "reps": "int",
               "n_stocks": "int", "look": "int", "hold": "int", "top_n": "int"}
    grid = []
    looks, holds = [20, 60, 120, 180, 250], [5, 10, 20, 40, 60]
    for L in looks:
        grid.append([np.mean([momentum_demo(seed + i, look=L, hold=H, s=kw.get("s", .0006))[4] for i in range(12)])
                     for H in holds])
    return values, formats, {"past": past, "fwd": fwd, "top": top, "bot": bot, "grid": np.array(grid), "looks": looks,
                             "holds": holds}


def plot2d_momentum(ax, s, upto=1.0):
    past, fwd = s["past"] * 100, s["fwd"] * 100; n = len(past); k = max(2, int(n * upto))
    idx = np.arange(n)[:k]
    ax.scatter(past[idx], fwd[idx], s=26, color=MUT, alpha=0.5)
    if upto > 0.5:
        ax.scatter(past[s["top"]], fwd[s["top"]], s=40, color=POS, label="nhóm mạnh nhất")
        ax.scatter(past[s["bot"]], fwd[s["bot"]], s=40, color=NEG, label="nhóm yếu nhất")
        ax.axhline(fwd[s["top"]].mean(), color=POS, lw=2.4); ax.axhline(fwd[s["bot"]].mean(), color=NEG, lw=2.4)
        ax.legend(loc="upper left", fontsize=18, frameon=False, labelcolor=TXT)
    ax.set_xlabel("lợi suất quá khứ %"); ax.set_ylabel("lợi suất giai đoạn sau %")


def surface_momentum(s, v):
    """Lưới đo được còn thưa (vài cửa sổ × vài thời gian giữ): nội suy song tuyến tính cho mặt mượt, giữ nguyên các
    điểm đo thật (chấm cam) để người xem thấy đâu là số tính thật, đâu là nội suy."""
    lk, hd, G = np.asarray(s["looks"], float), np.asarray(s["holds"], float), np.asarray(s["grid"], float) * 100
    xi, yi = np.linspace(lk[0], lk[-1], 40), np.linspace(hd[0], hd[-1], 40)
    tmp = np.array([np.interp(xi, lk, G[:, j]) for j in range(len(hd))]).T      # (40, len(hd))
    Z = np.array([np.interp(yi, hd, tmp[i]) for i in range(len(xi))])          # (40, 40)
    X, Y = np.meshgrid(xi, yi, indexing="ij")
    Lp, Hp = np.meshgrid(lk, hd, indexing="ij")
    return {"X": X, "Y": Y, "Z": Z, "xl": "cửa sổ nhìn lại (phiên)", "yl": "thời gian giữ (phiên)", "zl": "chênh lệch %",
            "dots": (Lp.ravel(), Hp.ravel(), G.ravel() + 0.05)}


# =============================================================== Martingale (gấp thếp)
def martingale_demo(seed=3, players=2000, rounds=300,
                    p=0.486, cap=1023):
    rng = np.random.default_rng(seed)
    pnl = np.zeros(players)
    bust = np.zeros(players, bool)
    for i in range(players):
        w, bet = cap, 1
        for win in rng.random(rounds) < p:
            if bet > w:              # không đủ tiền gấp đôi
                bust[i] = True; break
            w += bet if win else -bet
            bet = 1 if win else bet * 2
        pnl[i] = w - cap
    return pnl, bust


def _mart_paths(seed, p, cap, rounds, k=6):
    rng = np.random.default_rng(seed + 100)
    out = []
    while len(out) < k:
        w, bet, path = cap, 1, [0]
        for win in rng.random(rounds) < p:
            if bet > w:
                break
            w += bet if win else -bet
            bet = 1 if win else bet * 2
            path.append(w - cap)
        out.append(np.array(path))
    return out


def compute_martingale(seed=3, returns=None, **kw):
    pnl, bust = martingale_demo(seed, **kw)
    p, cap, rounds = kw.get("p", 0.486), kw.get("cap", 1023), kw.get("rounds", 300)
    k = int(math.log2(cap + 1))
    values = {"p_win": p, "players": len(pnl), "rounds": rounds, "cap": cap, "max_losses": k,
              "pct_bust": float(bust.mean()), "pct_up": float((pnl > 0).mean()), "mean_pnl": float(pnl.mean()),
              "median_pnl": float(np.median(pnl)), "worst": float(pnl.min()), "best": float(pnl.max()),
              "p_streak": (1 - p) ** k}
    formats = {"p_win": "pct1", "players": "int", "rounds": "int", "cap": "int", "max_losses": "int", "pct_bust": "pct0",
               "pct_up": "pct0", "mean_pnl": "num0", "median_pnl": "num0", "worst": "int", "best": "int", "p_streak": "pct2"}
    return values, formats, {"paths": _mart_paths(seed, p, cap, rounds), "cap": cap, "p": p, "rounds": rounds}


def plot2d_martingale(ax, s, upto=1.0):
    cols = [POS, NEU, ACC, MUT, NEG, POS]
    L = max(len(q) for q in s["paths"]); k = max(2, int(L * upto))
    for q, c in zip(s["paths"], cols):
        ax.plot(np.arange(min(k, len(q))), q[:k], color=c, lw=2)
        if len(q) <= k and len(q) < s["rounds"] + 1:
            ax.scatter([len(q) - 1], [q[-1]], color=NEG, s=90, zorder=5)
    ax.axhline(0, color=MUT, lw=1); ax.axhline(-s["cap"], color=NEG, lw=1, ls="--")
    ax.set_xlim(0, s["rounds"]); ax.set_ylim(-s["cap"] * 1.15, max(max(q.max() for q in s["paths"]) * 1.3, 50))
    ax.set_xlabel("ván"); ax.set_ylabel("lãi/lỗ (đơn vị cược)")


def surface_martingale(s, v):
    q = 1 - s["p"]; ks = np.arange(4, 16); n = np.linspace(50, 1000, 40)
    K, N = np.meshgrid(ks, n)
    P = 1 - (1 - q ** K) ** (N * q)          # xấp xỉ: xác suất gặp chuỗi thua dài ≥ k
    return {"X": K, "Y": N, "Z": P * 100, "xl": "số lần thua chịu được", "yl": "số ván", "zl": "xác suất cháy %"}


# =============================================================== PSR: Sharpe có phải do may?
def psr_demo(seed=1, trials=200, T=500):
    rng = np.random.default_rng(seed)
    r = rng.normal(0, .01, (trials, T))  # lợi thế = 0
    sr = r.mean(1) / r.std(1)            # Sharpe ngày
    best = r[sr.argmax()]; s = sr.max()
    e = best - best.mean()
    g3 = (e**3).mean() / best.std()**3
    g4 = (e**4).mean() / best.std()**4
    z = s * np.sqrt(T - 1) / np.sqrt(
        1 - g3*s + (g4 - 1) / 4 * s**2)
    return sr, best, s, z


def compute_psr(seed=1, returns=None, **kw):
    sr, best, s, z = psr_demo(seed, **kw)
    T = kw.get("T", 500); n = len(sr); ann = sr * math.sqrt(252)
    e = best - best.mean(); g3 = (e ** 3).mean() / best.std() ** 3; g4 = (e ** 4).mean() / best.std() ** 4
    gam = 0.5772156649
    s_star = sr.std() * ((1 - gam) * _ninv(1 - 1 / n) + gam * _ninv(1 - 1 / (n * math.e)))
    dsr = _ncdf((s - s_star) * math.sqrt(T - 1) / math.sqrt(1 - g3 * s + (g4 - 1) / 4 * s ** 2))
    values = {"trials": n, "T": T, "years": T / 252, "best_sr": float(s * math.sqrt(252)), "psr_best": _ncdf(float(z)),
              "share_over1": float((ann > 1).mean()), "n_over1": int((ann > 1).sum()), "true_sr": 0,
              "median_sr": float(np.median(ann)), "best_ret": float(best.sum()), "dsr_best": dsr,
              "sr_star": s_star * math.sqrt(252)}
    formats = {"trials": "int", "T": "int", "years": "num0", "best_sr": "num2", "psr_best": "pct1", "dsr_best": "pct0",
               "sr_star": "num2", "share_over1": "pct0",
               "n_over1": "int", "true_sr": "int", "median_sr": "num2", "best_ret": "pct0"}
    return values, formats, {"ann": ann, "best": best}


def plot2d_psr(ax, s, upto=1.0):
    ann = s["ann"]; k = max(2, int(len(ann) * upto))
    bins = np.linspace(ann.min() - 0.1, ann.max() + 0.1, 30)
    ax.hist(ann[:k], bins, color=MUT, alpha=0.7)
    ax.hist(ann[:k][ann[:k] > 1], bins, color=NEG, alpha=0.9, label="Sharpe > 1 do may")
    if upto > 0.95:
        ax.axvline(ann.max(), color=ACC, lw=3, label="chiến lược 'tốt nhất'")
    ax.axvline(0, color=POS, lw=2, ls="--", label="lợi thế thật = 0")
    ax.set_xlabel("Sharpe năm hoá của từng backtest"); ax.set_ylabel("số chiến lược")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_psr(s, v):
    srs = np.linspace(0.0, 2.0, 40); Ts = np.linspace(60, 1500, 40)
    S_, T_ = np.meshgrid(srs, Ts)
    sd = S_ / math.sqrt(252)
    Z = np.vectorize(_ncdf)(sd * np.sqrt(T_ - 1) / np.sqrt(1 + sd ** 2 / 2))
    return {"X": S_, "Y": T_, "Z": Z * 100, "xl": "Sharpe năm quan sát", "yl": "số phiên backtest", "zl": "PSR %"}


# =============================================================== CMF (Chaikin Money Flow)
def cmf_demo(seed=11, n=300, w=20):
    rng = np.random.default_rng(seed)
    c = 100*np.exp(np.cumsum(rng.normal(.0005, .015, n)))
    span = c * rng.uniform(.01, .03, n)
    h = c + span*rng.uniform(0, 1, n)   # giá cao
    l = h - span                        # giá thấp
    v = rng.lognormal(13, .4, n)        # khối lượng
    mfm = ((c-l) - (h-c)) / (h-l)       # vị trí đóng cửa
    s = lambda x: np.convolve(x, np.ones(w), "valid")
    cmf = s(mfm * v) / s(v)
    return c, h, l, v, cmf


def compute_cmf(seed=11, returns=None, **kw):
    c, h, l, v, cmf = cmf_demo(seed, **kw)
    w = kw.get("w", 20)
    cc = c[w - 1:]
    up20 = np.r_[np.zeros(w), cc[w:] / cc[:-w] - 1]
    div = int(((up20 > 0) & (cmf < 0)).sum())
    values = {"cmf_last": float(cmf[-1]), "cmf_max": float(cmf.max()), "cmf_min": float(cmf.min()), "w": w,
              "div_days": div, "n_days": len(cmf), "pct_pos": float((cmf > 0).mean())}
    formats = {"cmf_last": "num2", "cmf_max": "num2", "cmf_min": "num2", "w": "int", "div_days": "int", "n_days": "int",
               "pct_pos": "pct0"}
    return values, formats, {"c": cc, "cmf": cmf, "seed": seed, "w": w}


def plot2d_cmf(ax, s, upto=1.0):
    c, cmf = s["c"], s["cmf"]; n = len(c); k = max(2, int(n * upto)); x = np.arange(n)
    lim = max(abs(cmf).max(), 0.05) * 1.1
    ax.bar(x[:k], cmf[:k], width=1.0, color=[POS if q >= 0 else NEG for q in cmf[:k]], alpha=0.85)
    cn = lim * 1.2 + lim * 1.6 * (c - c.min()) / (c.max() - c.min())
    ax.plot(x[:k], cn[:k], color=MUT, lw=2)
    ax.axhline(0, color=MUT, lw=1); ax.set_xlim(0, n); ax.set_ylim(-lim, lim * 3)
    ax.set_xlabel("phiên"); ax.set_ylabel("CMF (dưới) · giá (trên)")


def surface_cmf(s, v):
    """Năm dải CMF với cửa sổ khác nhau (ngắn → dài): thấy ngay cửa sổ ngắn giật, cửa sổ dài mượt nhưng trễ."""
    c, h, l, vol, _ = cmf_demo(s["seed"])
    mfv = ((c - l) - (h - c)) / (h - l) * vol
    ws = [5, 10, 20, 40, 60]; n = len(c) - 60
    cols = [NEG, ACC, NEU, POS, MUT]
    lines = []
    for i, (w, col) in enumerate(zip(ws, cols)):
        z = (np.convolve(mfv, np.ones(w), "valid") / np.convolve(vol, np.ones(w), "valid"))[-n:]
        lines.append((np.arange(n), np.full(n, i), z, col))
    return {"lines": lines, "xl": "phiên", "yl": "", "zl": "CMF", "yticks": [f"{w} phiên" for w in ws]}


EXTRA_TOPICS = ["rsi", "max_drawdown", "beta", "ols", "lln_clt", "egarch", "fat_tails", "momentum", "martingale", "psr", "cmf"]
