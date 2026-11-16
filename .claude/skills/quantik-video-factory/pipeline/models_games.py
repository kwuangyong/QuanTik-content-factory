"""Game theory, poker maths and "cold truths about money" — 10 hand-written topics (English series).

Same contract as models.py: ``<topic>_demo`` (shown on screen, <= 16 lines, <= 48 chars wide),
``compute_<topic>`` → (values, formats, series), ``plot2d_<topic>``, ``surface_<topic>``.
Every number in these videos comes from ``values``. Poker / lottery / roulette appear only as probability
problems: the scripts never encourage gambling (see brand/compliance.md, "Gambling topics").
"""
from __future__ import annotations

import math

import numpy as np

from core import THEME, hex_

ACC, POS, NEG, NEU, MUT, TXT = (hex_(THEME[k]) for k in ("accent", "positive", "negative", "neutral", "muted", "text"))


def _hist_surface(paths, xs, bins, xl, yl, zl, log=False):
    """Density of many paths over time → 3D surface (X = time, Y = level, Z = share of paths)."""
    data = np.log10(np.clip(paths, 1e-9, None)) if log else paths
    lo, hi = np.percentile(data, 1), np.percentile(data, 99)
    edges = np.linspace(lo, hi, bins + 1)
    Z = np.array([np.histogram(data[:, i], edges)[0] / len(data) for i in xs]).T
    X, Y = np.meshgrid(np.array(xs), (edges[:-1] + edges[1:]) / 2)
    return {"X": X, "Y": Y, "Z": Z * 100, "xl": xl, "yl": yl, "zl": zl}


# =============================================================== 1. ergodicity (Peters coin game)
def ergodicity_demo(seed=11, people=1000, rounds=50):
    rng = np.random.default_rng(seed)
    heads = rng.random((people, rounds)) < 0.5
    step = np.where(heads, 1.5, 0.6)  # +50% / -40%
    wealth = np.cumprod(step, axis=1)  # start = 1
    avg_step = 0.5 * 1.5 + 0.5 * 0.6   # 1.05
    typical = math.sqrt(1.5 * 0.6)     # 0.949
    return wealth, avg_step, typical


def compute_ergodicity(seed=11, returns=None):
    w, avg, typ = ergodicity_demo(seed)
    end = w[:, -1]
    values = {"people": w.shape[0], "rounds": w.shape[1], "up": 0.5, "down": 0.4,
              "avg_gain": avg - 1, "typical_loss": 1 - typ,
              "expected_x": avg ** w.shape[1], "median_left": float(np.median(end)),
              "share_poorer": float((end < 1).mean()), "share_wiped": float((end < 0.1).mean()),
              "share_richer": float((end > 1).mean()), "top_share": float(np.sort(end)[-10:].sum() / end.sum())}
    formats = {"people": "int", "rounds": "int", "up": "pct0", "down": "pct0", "avg_gain": "pct0",
               "typical_loss": "pct1", "expected_x": "x1", "median_left": "pct0", "share_poorer": "pct0",
               "share_wiped": "pct0", "share_richer": "pct0", "top_share": "pct0"}
    return values, formats, {"w": w, "avg": avg}


def plot2d_ergodicity(ax, s, upto=1.0):
    w = s["w"]; n = w.shape[1]; k = max(2, int(n * upto)); x = np.arange(1, k + 1)
    for i in range(25):
        ax.plot(x, w[i, :k], color=MUT, lw=0.7, alpha=0.22)
    ax.plot(x, s["avg"] ** x, color=POS, lw=3, label="'average' (expected value)")
    ax.plot(x, np.median(w[:, :k], axis=0), color=NEG, lw=3.4, label="typical person (median)")
    ax.axhline(1, color=TXT, lw=1, ls="--", alpha=0.6)
    ax.set_yscale("log"); ax.set_xlim(1, n); ax.set_ylim(1e-3, 1e2)
    ax.set_xlabel("round"); ax.set_ylabel("wealth (start = 1, log)")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_ergodicity(s, v):
    return _hist_surface(s["w"], list(range(0, s["w"].shape[1], 2)), 30, "round", "log10 wealth", "% of people",
                         log=True)


# =============================================================== 2. yard-sale model (wealth condensation)
def yard_sale_demo(seed=3, n=1000, trades=400_000, frac=0.1):
    rng = np.random.default_rng(seed)
    w = np.full(n, 100.0)           # everyone equal
    pairs = rng.integers(n, size=(trades, 2))
    coin = rng.random(trades) < 0.5  # fair coin
    top1 = []
    for t, (i, j) in enumerate(pairs):
        bet = frac * min(w[i], w[j])  # poorer side
        w[i] += bet if coin[t] else -bet
        w[j] -= bet if coin[t] else -bet
        if t % 10_000 == 0:
            top1.append(np.sort(w)[-n // 100:].sum() / w.sum())
    return w, np.array(top1)


def _gini(w):
    w = np.sort(w); n = len(w)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(w) / (n * w.sum()))


def compute_yard_sale(seed=3, returns=None):
    w, top1 = yard_sale_demo(seed)
    ws = np.sort(w); n = len(w)
    values = {"people": n, "start_cash": 100, "bet_frac": 0.1, "trades": 400_000,
              "top1_start": 0.01, "top1_end": float(ws[-n // 100:].sum() / ws.sum()),
              "top10_end": float(ws[-n // 10:].sum() / ws.sum()),
              "bottom50_end": float(ws[: n // 2].sum() / ws.sum()),
              "gini_end": _gini(w), "richest_x": float(ws[-1] / 100), "under_10": float((w < 10).mean())}
    formats = {"people": "int", "start_cash": "int", "bet_frac": "pct0", "trades": "int", "top1_start": "pct0",
               "top1_end": "pct0", "top10_end": "pct0", "bottom50_end": "pct1", "gini_end": "num2",
               "richest_x": "x0", "under_10": "pct0"}
    return values, formats, {"top1": top1, "w": w}


def plot2d_yard_sale(ax, s, upto=1.0):
    y = s["top1"] * 100; n = len(y); k = max(2, int(n * upto)); x = np.arange(n) * 10_000 / 1000
    ax.fill_between(x[:k], 0, y[:k], color=ACC, alpha=0.2)
    ax.plot(x[:k], y[:k], color=ACC, lw=3.2)
    ax.axhline(1, color=POS, lw=1.6, ls="--")
    ax.text(x[-1] * 0.98, 3, "fair share = 1%", color=POS, fontsize=17, ha="right")
    ax.set_xlim(0, x[-1]); ax.set_ylim(0, max(y) * 1.15)
    ax.set_xlabel("trades (thousands)"); ax.set_ylabel("wealth held by top 1%  (%)")


def surface_yard_sale(s, v):
    # Lorenz curves re-simulated at checkpoints (cheap: same seed, shorter runs)
    pts = np.linspace(0, 1, 41); X, Y, Z = [], [], []
    for k, tr in enumerate([1, 25_000, 50_000, 100_000, 200_000, 400_000]):
        w, _ = yard_sale_demo(3, trades=tr)
        c = np.concatenate([[0], np.cumsum(np.sort(w)) / w.sum()])
        Z.append(np.interp(pts, np.linspace(0, 1, len(c)), c) * 100); X.append(np.full_like(pts, k)); Y.append(pts * 100)
    return {"X": np.array(X), "Y": np.array(Y), "Z": np.array(Z), "xl": "time →", "yl": "poorest → richest %",
            "zl": "cumulative wealth %"}


# =============================================================== 3. survivorship bias (coin-flip fund managers)
def survivorship_demo(seed=8, managers=10_000, years=10):
    rng = np.random.default_rng(seed)
    beat = rng.random((managers, years)) < 0.5  # pure luck
    alive = np.cumprod(beat, axis=1)  # beat it every year so far
    survivors = alive.sum(axis=0)
    wins = beat.sum(axis=1)
    p_perfect = 0.5 ** years           # 1 / 1024
    return survivors, wins, p_perfect


def compute_survivorship(seed=8, returns=None):
    surv, wins, p = survivorship_demo(seed)
    m = len(wins)
    values = {"managers": m, "years": 10, "p_perfect": p, "one_in": int(round(1 / p)),
              "expected_perfect": m * p, "perfect": int(surv[-1]), "after3": int(surv[2]), "after5": int(surv[4]),
              "eight_plus": int((wins >= 8).sum()), "letters": 1024}
    formats = {"managers": "int", "years": "int", "p_perfect": "pct2", "one_in": "int", "expected_perfect": "num0",
               "perfect": "int", "after3": "int", "after5": "int", "eight_plus": "int", "letters": "int"}
    return values, formats, {"surv": surv, "m": m, "wins": wins}


def plot2d_survivorship(ax, s, upto=1.0):
    y = np.concatenate([[s["m"]], s["surv"]]); n = len(y); k = max(1, int(round(n * upto)))
    x = np.arange(n)
    ax.bar(x[:k], y[:k], color=[ACC if i == n - 1 else MUT for i in range(k)], width=0.7)
    for i in range(k):
        ax.text(i, y[i] * 1.15, f"{y[i]:,}", ha="center", color=TXT, fontsize=15)
    ax.set_yscale("log"); ax.set_ylim(1, s["m"] * 4); ax.set_xlim(-0.6, n - 0.4)
    ax.set_xlabel("years in a row beating the market"); ax.set_ylabel("managers still 'perfect' (log)")
    ax.grid(axis="x", visible=False)


def surface_survivorship(s, v):
    m = 10_000; yrs = np.arange(1, 16); ps = np.linspace(0.40, 0.60, 30)
    Y, X = np.meshgrid(ps, yrs)
    Z = np.log10(np.maximum(m * Y ** X, 1e-2))
    return {"X": X, "Y": Y * 100, "Z": Z, "xl": "years", "yl": "skill: chance to beat %", "zl": "log10 survivors"}


# =============================================================== 4. pot odds & expected value
def pot_odds_demo(seed=5, pot=100, bet=50, hands=1000):
    rng = np.random.default_rng(seed)
    outs, unseen = 9, 47                # flush draw
    miss = (unseen - outs) / unseen * (unseen - 1 - outs) / (unseen - 1)
    equity = 1 - miss                   # hit by river
    need = bet / (pot + 2 * bet)        # break-even
    ev = equity * (pot + bet) - (1 - equity) * bet
    win = rng.random(hands) < equity
    pnl = np.where(win, pot + bet, -bet)
    return equity, need, ev, pnl


def compute_pot_odds(seed=5, returns=None):
    eq, need, ev, pnl = pot_odds_demo(seed)
    streak = cur = 0
    for v in pnl:
        cur = cur + 1 if v < 0 else 0; streak = max(streak, cur)
    values = {"pot": 100, "bet": 50, "win_amt": 150, "outs": 9, "equity": eq, "need": need, "ev": ev,
              "hands": len(pnl), "lose_rate": float((pnl < 0).mean()), "total": float(pnl.sum()),
              "expected_total": ev * len(pnl), "worst_streak": streak}
    formats = {"pot": "int", "bet": "int", "win_amt": "int", "outs": "int", "equity": "pct0", "need": "pct0",
               "ev": "num0", "hands": "int", "lose_rate": "pct0", "total": "int", "expected_total": "int",
               "worst_streak": "int"}
    return values, formats, {"pnl": pnl, "ev": ev}


def plot2d_pot_odds(ax, s, upto=1.0):
    c = np.cumsum(s["pnl"]); n = len(c); k = max(2, int(n * upto)); x = np.arange(1, n + 1)
    ax.plot(x[:k], s["ev"] * x[:k], color=POS, lw=2, ls="--", label="expected value")
    ax.plot(x[:k], c[:k], color=ACC, lw=2.6, label="actual result")
    ax.axhline(0, color=TXT, lw=1, alpha=0.5)
    ax.set_xlim(0, n); ax.set_ylim(min(c.min(), 0) - 500, max(c.max(), s["ev"] * n) * 1.1)
    ax.set_xlabel("times you make the same call"); ax.set_ylabel("cumulative chips")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_pot_odds(s, v):
    eq = np.linspace(0.05, 0.6, 40); b = np.linspace(0.25, 2.0, 40)  # bet as fraction of pot
    E, B = np.meshgrid(eq, b)
    Z = E * (1 + B) - (1 - E) * B     # EV of calling, in pots
    return {"X": E * 100, "Y": B * 100, "Z": Z * 100, "xl": "your equity %", "yl": "bet size, % of pot",
            "zl": "EV of calling, % of pot"}


# =============================================================== 5. poker variance (winning player, long downswings)
def poker_variance_demo(seed=9, players=1000, blocks=1000):
    rng = np.random.default_rng(seed)
    winrate, sd = 5.0, 100.0  # big blinds per 100 hands
    per_block = rng.normal(winrate, sd, (players, blocks))
    bankroll = np.cumsum(per_block, axis=1)
    peak = np.maximum.accumulate(bankroll, axis=1)
    drawdown = (peak - bankroll).max(axis=1)
    return bankroll, drawdown, winrate, sd


def compute_poker_variance(seed=9, returns=None):
    br, dd, wr, sd = poker_variance_demo(seed)
    # longest stretch (in hands) without a new high
    longest = []
    for row in br:
        best = -1e18; run = top = 0
        for v in row:
            if v > best: best, run = v, 0
            else: run += 1; top = max(top, run)
        longest.append(top * 100)
    longest = np.array(longest)
    values = {"players": br.shape[0], "hands": br.shape[1] * 100, "winrate": wr, "sd": sd,
              "behind_10k": float((br[:, 99] < 0).mean()), "behind_50k": float((br[:, 499] < 0).mean()),
              "behind_100k": float((br[:, -1] < 0).mean()),
              "median_dd": float(np.median(dd)), "median_flat": float(np.median(longest)),
              "worst_flat": float(longest.max())}
    formats = {"players": "int", "hands": "int", "winrate": "num0", "sd": "num0", "behind_10k": "pct0",
               "behind_50k": "pct0", "behind_100k": "pct0", "median_dd": "int", "median_flat": "int",
               "worst_flat": "int"}
    return values, formats, {"br": br, "wr": wr}


def plot2d_poker_variance(ax, s, upto=1.0):
    br = s["br"]; n = br.shape[1]; k = max(2, int(n * upto)); x = np.arange(1, n + 1) * 100 / 1000
    for i in range(40):
        ax.plot(x[:k], br[i, :k], color=MUT, lw=0.8, alpha=0.4)
    ax.plot(x[:k], s["wr"] * np.arange(1, k + 1), color=POS, lw=3, label="true skill edge")
    ax.plot(x[:k], br[3, :k], color=ACC, lw=2.6, label="one winning player")
    ax.axhline(0, color=TXT, lw=1, alpha=0.6)
    ax.set_xlim(0, x[-1]); ax.set_ylim(np.percentile(br[:40], 1) * 1.05, np.percentile(br[:40], 99.5) * 1.05)
    ax.set_xlabel("hands played (thousands)"); ax.set_ylabel("big blinds won")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_poker_variance(s, v):
    return _hist_surface(s["br"], list(range(0, s["br"].shape[1], 25)), 36, "hands (×100)", "big blinds",
                         "% of players")


# =============================================================== 6. game-theory optimal bluffing
def bluff_gto_demo(seed=0, pot=1.0, bet=1.0):
    # caller pays `bet` to win `pot + bet`
    need = bet / (pot + 2 * bet)       # equity to call
    bluff_share = need                 # GTO: bluffs in bet
    mdf = pot / (pot + bet)            # defend this often
    x = np.linspace(0, 1, 101)         # your bluff share
    ev_call = x * (pot + bet) - (1 - x) * bet
    return need, bluff_share, mdf, x, ev_call


def compute_bluff_gto(seed=0, returns=None):
    need, bs, mdf, x, ev = bluff_gto_demo(seed)
    half = bluff_gto_demo(seed, bet=0.5)
    over = bluff_gto_demo(seed, bet=2.0)
    values = {"bluff_share": bs, "need": need, "mdf": mdf, "value_share": 1 - bs,
              "bluff_half": half[1], "bluff_over": over[1], "mdf_half": half[2], "mdf_over": over[2],
              "ev_never": float(ev[0]), "ev_always": float(ev[-1]), "ratio_value": int(round((1 - bs) / bs))}
    formats = {"bluff_share": "pct0", "need": "pct0", "mdf": "pct0", "value_share": "pct0", "bluff_half": "pct0",
               "bluff_over": "pct0", "mdf_half": "pct0", "mdf_over": "pct0", "ev_never": "num1",
               "ev_always": "num1", "ratio_value": "int"}
    return values, formats, {"x": x, "ev": ev, "bs": bs}


def plot2d_bluff_gto(ax, s, upto=1.0):
    x, ev = s["x"] * 100, s["ev"]; k = max(2, int(len(x) * upto))
    ax.fill_between(x[:k], 0, ev[:k], where=ev[:k] < 0, color=NEG, alpha=0.25)
    ax.fill_between(x[:k], 0, ev[:k], where=ev[:k] >= 0, color=POS, alpha=0.25)
    ax.plot(x[:k], ev[:k], color=ACC, lw=3.2)
    ax.axhline(0, color=TXT, lw=1, alpha=0.6)
    if upto > 0.4:
        ax.axvline(s["bs"] * 100, color=NEU, lw=2, ls="--")
        ax.text(s["bs"] * 100 + 2, 1.2, "balanced", color=NEU, fontsize=18)
    ax.text(4, -0.85, "opponent folds\nto bluffs: you rarely bluff", color=NEG, fontsize=14)
    ax.text(58, 0.6, "opponent calls:\nyou bluff too much", color=POS, fontsize=14)
    ax.set_xlim(0, 100); ax.set_ylim(-1.1, 2.1)
    ax.set_xlabel("share of your bets that are bluffs (%)"); ax.set_ylabel("opponent's EV of calling (pots)")


def surface_bluff_gto(s, v):
    x = np.linspace(0, 1, 40); b = np.linspace(0.25, 2.0, 40)
    X, B = np.meshgrid(x, b)
    Z = X * (1 + B) - (1 - X) * B
    return {"X": X * 100, "Y": B * 100, "Z": Z, "xl": "bluff share %", "yl": "bet, % of pot",
            "zl": "caller EV (pots)"}


# =============================================================== 7. iterated prisoner's dilemma tournament
def prisoners_dilemma_demo(seed=2, rounds=200):
    rng = np.random.default_rng(seed)
    PAY = {(1, 1): 3, (1, 0): 0, (0, 1): 5, (0, 0): 1}
    S = {"Tit for Tat": lambda op: op[-1] if op else 1,
         "Always Defect": lambda op: 0,
         "Always Cooperate": lambda op: 1,
         "Grudger": lambda op: int(0 not in op),
         "Random": lambda op: int(rng.random() < 0.5)}
    score = {k: 0 for k in S}
    for a in S:
        for b in S:                     # incl. self-play
            ha, hb = [], []
            for _ in range(rounds):
                x, y = S[a](hb), S[b](ha)
                ha.append(x); hb.append(y)
                score[a] += PAY[(x, y)]
    return score


def compute_prisoners_dilemma(seed=2, returns=None):
    score = prisoners_dilemma_demo(seed)
    # head-to-head record of Tit for Tat (does it ever outscore a single opponent?)
    import itertools  # noqa: F401
    rounds = 200
    PAY = {(1, 1): 3, (1, 0): 0, (0, 1): 5, (0, 0): 1}
    rng = np.random.default_rng(seed)
    S = {"Tit for Tat": lambda op: op[-1] if op else 1, "Always Defect": lambda op: 0,
         "Always Cooperate": lambda op: 1, "Grudger": lambda op: int(0 not in op),
         "Random": lambda op: int(rng.random() < 0.5)}
    tft_beats = 0
    for b in S:
        if b == "Tit for Tat":
            continue
        ha, hb, sa, sb = [], [], 0, 0
        for _ in range(rounds):
            x, y = S["Tit for Tat"](hb), S[b](ha); ha.append(x); hb.append(y)
            sa += PAY[(x, y)]; sb += PAY[(y, x)]
        tft_beats += sa > sb
    rank = sorted(score, key=score.get, reverse=True)
    values = {"rounds": rounds, "n_strats": len(score), "tft_score": score["Tit for Tat"],
              "defect_score": score["Always Defect"], "coop_score": score["Always Cooperate"],
              "top_score": score[rank[0]], "tft_rank": rank.index("Tit for Tat") + 1,
              "defect_rank": rank.index("Always Defect") + 1, "tft_beats": tft_beats,
              "t": 5, "r": 3, "p": 1, "s": 0}
    formats = {k: "int" for k in values}
    return values, formats, {"score": score, "rank": rank}


def plot2d_prisoners_dilemma(ax, s, upto=1.0):
    rank = s["rank"][::-1]; vals = [s["score"][r] for r in rank]
    shown = [v * min(1, upto * 1.4) for v in vals]
    cols = [ACC if r == "Tit for Tat" else NEG if r == "Always Defect" else MUT for r in rank]
    ax.barh(range(len(rank)), shown, color=cols, height=0.62)
    ax.set_yticks(range(len(rank))); ax.set_yticklabels(rank, fontsize=17, color=TXT)
    for i, v in enumerate(shown):
        ax.text(v + max(vals) * 0.01, i, f"{int(v):,}", va="center", color=TXT, fontsize=16)
    ax.set_xlim(0, max(vals) * 1.18); ax.set_xlabel("total tournament points"); ax.grid(axis="y", visible=False)


def surface_prisoners_dilemma(s, v):
    # payoff to Tit for Tat vs a population with share q of defectors, over game length
    q = np.linspace(0, 1, 40); L = np.linspace(1, 200, 40)
    Q, Ln = np.meshgrid(q, L)
    tft = (1 - Q) * 3 * Ln + Q * (0 + 1 * (Ln - 1))
    alld = (1 - Q) * (5 + 1 * (Ln - 1)) + Q * 1 * Ln
    return {"X": Q * 100, "Y": Ln, "Z": (tft - alld) / Ln, "xl": "defectors in population %", "yl": "game length",
            "zl": "TFT advantage / round"}


# =============================================================== 8. dollar auction (escalation)
def dollar_auction_demo(seed=6, prize=100, step=5):
    rng = np.random.default_rng(seed)
    wallet = rng.integers(150, 300, size=2)  # cash on hand
    bids, turn = [0, 0], 0
    hist = []
    while True:
        new = max(bids) + step
        quit_loss = bids[turn]        # pay your bid anyway
        win_loss = new - prize        # if you top it
        if new > wallet[turn] or win_loss >= quit_loss:
            break
        bids[turn] = new; hist.append(tuple(bids))
        turn = 1 - turn
    return bids, hist, prize


def compute_dollar_auction(seed=6, returns=None):
    bids, hist, prize = dollar_auction_demo(seed)
    win, lose = max(bids), min(bids)
    first_over = next(i for i, h in enumerate(hist) if max(h) > prize) + 1
    values = {"prize": prize, "step": 5, "win_bid": win, "lose_bid": lose, "collected": win + lose,
              "profit": win + lose - prize, "winner_loss": win - prize, "rounds": len(hist),
              "first_over": first_over, "ratio": (win + lose) / prize}
    formats = {"prize": "int", "step": "int", "win_bid": "int", "lose_bid": "int", "collected": "int",
               "profit": "int", "winner_loss": "int", "rounds": "int", "first_over": "int", "ratio": "x1"}
    return values, formats, {"hist": np.array(hist), "prize": prize}


def plot2d_dollar_auction(ax, s, upto=1.0):
    h = s["hist"]; n = len(h); k = max(2, int(n * upto)); x = np.arange(1, n + 1)
    ax.plot(x[:k], h[:k, 0], color=ACC, lw=3, label="bidder A", drawstyle="steps-post")
    ax.plot(x[:k], h[:k, 1], color=NEU, lw=3, label="bidder B", drawstyle="steps-post")
    ax.axhline(s["prize"], color=POS, lw=2, ls="--")
    ax.text(n * 0.02, s["prize"] + 6, "the prize: $100", color=POS, fontsize=18)
    ax.set_xlim(0, n + 1); ax.set_ylim(0, h.max() * 1.15)
    ax.set_xlabel("bid number"); ax.set_ylabel("bid ($)")
    ax.legend(loc="lower right", fontsize=17, frameon=False, labelcolor=TXT)


def surface_dollar_auction(s, v):
    import numpy as _np
    wa = _np.arange(100, 301, 10); X, Y = _np.meshgrid(wa, wa); Z = _np.zeros_like(X, float)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            bids, turn = [0, 0], 0; wl = (X[i, j], Y[i, j])
            while True:
                new = max(bids) + 5
                if new > wl[turn] or new - 100 >= bids[turn]:
                    break
                bids[turn] = new; turn = 1 - turn
            Z[i, j] = sum(bids)
    return {"X": X, "Y": Y, "Z": Z, "xl": "wallet A ($)", "yl": "wallet B ($)", "zl": "total paid ($)"}


# =============================================================== 9. lottery odds
def lottery_demo(seed=4, players=1_000_000, years=50):
    rng = np.random.default_rng(seed)
    combos = math.comb(49, 6)          # 6 of 49
    p = 1 / combos
    tickets = 52 * years               # one a week
    hits = rng.binomial(tickets, p, size=players)
    winners = int((hits > 0).sum())
    years_daily = combos / 365.25      # 1 ticket/day
    return combos, p, tickets, winners, years_daily


def compute_lottery(seed=4, returns=None):
    combos, p, tickets, winners, yd = lottery_demo(seed)
    p_life = 1 - (1 - p) ** tickets
    values = {"combos": combos, "tickets": tickets, "years": 50, "players": 1_000_000, "winners": winners,
              "never": 1 - winners / 1_000_000, "p_life": p_life, "one_in_life": int(round(1 / p_life)),
              "years_daily": yd, "pick": 6, "pool": 49}
    formats = {"combos": "int", "tickets": "int", "years": "int", "players": "int", "winners": "int",
               "never": "pct2", "p_life": "pct3", "one_in_life": "int", "years_daily": "int", "pick": "int",
               "pool": "int"}
    return values, formats, {"p": p, "combos": combos}


def plot2d_lottery(ax, s, upto=1.0):
    yrs = np.linspace(0, 1000, 400); k = max(2, int(len(yrs) * upto))
    for per_week, c, lab in [(1, ACC, "1 ticket / week"), (7, NEU, "1 ticket / day"), (70, NEG, "10 tickets / day")]:
        pr = 1 - (1 - s["p"]) ** (52 * per_week * yrs)
        ax.plot(yrs[:k], pr[:k] * 100, color=c, lw=3, label=lab)
    ax.axvline(80, color=POS, lw=1.6, ls="--"); ax.text(90, 0.9, "a long life ≈ 80 years", color=POS, fontsize=15)
    ax.set_xlim(0, 1000); ax.set_ylim(0, 1.2)
    ax.set_xlabel("years of playing"); ax.set_ylabel("chance of EVER hitting the jackpot (%)")
    ax.legend(loc="upper left", fontsize=17, frameon=False, labelcolor=TXT)


def surface_lottery(s, v):
    yrs = np.linspace(1, 80, 40); per_week = np.linspace(1, 50, 40)
    Y, P = np.meshgrid(yrs, per_week)
    Z = 1 - (1 - s["p"]) ** (52 * P * Y)
    return {"X": Y, "Y": P, "Z": Z * 100, "xl": "years", "yl": "tickets / week", "zl": "chance of jackpot %"}


# =============================================================== 10. gambler's ruin (house edge)
def gamblers_ruin_demo(seed=10, players=1000, cash=100, goal=200):
    rng = np.random.default_rng(seed)
    p = 18 / 37                        # red, single-zero wheel
    edge = 1 - 2 * p                   # 1/37 = 2.7%
    w = np.full(players, cash); spins = np.zeros(players)
    live = np.ones(players, bool)
    while live.any():
        win = rng.random(players) < p
        w = np.where(live, w + np.where(win, 1, -1), w)
        spins += live
        live &= (w > 0) & (w < goal)
    return w, spins, p, edge


def compute_gamblers_ruin(seed=10, returns=None):
    w, spins, p, edge = gamblers_ruin_demo(seed)
    q = 1 - p; r = q / p
    theory = (r ** 100 - 1) / (r ** 200 - 1)
    # a few bankroll paths for the chart (same rules, separate seed so the demo stays 16 lines)
    rng = np.random.default_rng(seed + 1); paths = []
    for _ in range(30):
        x, path = 100, [100]
        while 0 < x < 200 and len(path) < 20000:
            x += 1 if rng.random() < p else -1; path.append(x)
        paths.append(np.array(path))
    values = {"players": len(w), "cash": 100, "goal": 200, "p_win": p, "edge": edge,
              "busted": float((w <= 0).mean()), "doubled": float((w >= 200).mean()),
              "theory_double": theory, "median_spins": float(np.median(spins)),
              "fair_double": 0.5, "pockets": 37}
    formats = {"players": "int", "cash": "int", "goal": "int", "p_win": "pct1", "edge": "pct1", "busted": "pct1",
               "doubled": "pct1", "theory_double": "pct1", "median_spins": "int", "fair_double": "pct0",
               "pockets": "int"}
    return values, formats, {"paths": paths}


def plot2d_gamblers_ruin(ax, s, upto=1.0):
    L = max(len(p) for p in s["paths"]); k = max(2, int(min(L, 12000) * upto))
    for i, p in enumerate(s["paths"]):
        c = POS if p[-1] >= 200 else (ACC if i == 0 else MUT)
        ax.plot(np.arange(min(k, len(p))), p[:k], color=c, lw=2.4 if i == 0 or p[-1] >= 200 else 0.9,
                alpha=1 if i == 0 or p[-1] >= 200 else 0.5)
    ax.axhline(200, color=POS, lw=1.6, ls="--"); ax.text(200, 206, "goal: double up", color=POS, fontsize=16)
    ax.axhline(0, color=NEG, lw=1.6)
    ax.set_xlim(0, min(L, 12000)); ax.set_ylim(-5, 230)
    ax.set_xlabel("spins"); ax.set_ylabel("chips left")


def surface_gamblers_ruin(s, v):
    edge = np.linspace(0.0, 0.06, 40); cash = np.linspace(5, 200, 40)
    E, C = np.meshgrid(edge, cash)
    p = (1 - E) / 2; r = (1 - p) / p
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        Z = np.where(E < 1e-9, 0.5, (r ** C - 1) / (r ** (2 * C) - 1))
    return {"X": E * 100, "Y": C, "Z": np.nan_to_num(Z) * 100, "xl": "house edge %", "yl": "starting chips (1/bet)",
            "zl": "chance to double %"}


GAME_TOPICS = ["ergodicity", "yard_sale", "survivorship", "pot_odds", "poker_variance", "bluff_gto",
               "prisoners_dilemma", "dollar_auction", "lottery", "gamblers_ruin"]
