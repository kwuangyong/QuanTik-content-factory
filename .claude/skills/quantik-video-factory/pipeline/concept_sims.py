"""Simulations / closed-form maths behind the YT Shorts + IG Reels lot (channels/yt-ig.md).

An episode names one kind in "sim": {"kind": ..., params}. The code really runs (fixed seed) and returns values
the narration uses as {placeholders}, so QA can prove every number came from this run or a ledger source.
No charts are drawn from it: dark-story shows the numbers as animated counters, crowds and illustrations.

    python concept_sims.py ../episodes/yt/71-monty-hall.json   → print the placeholders
"""
from __future__ import annotations

import inspect
import json
import math
import sys

import numpy as np

# =============================================================== kinds: compute
# Each k_<kind>(p, rng) returns (values, formats, series). p = concept["visual"].

def k_growth(p, rng):
    """Wealth W(t+1) = W(t)·(1+r) + c(t), c(t) = c·(1+g)^t, for each line; optional target milestones."""
    years = p["years"]
    v, f, lines = {"years": years}, {"years": "int"}, []
    for ln in p["lines"]:
        w, c, path, paid = ln.get("start", 0.0), ln.get("contrib", 0.0), [], ln.get("start", 0.0)
        path.append(w)
        for t in range(years):
            w = w * (1 + ln["rate"]) + c * (1 + ln.get("contrib_growth", 0.0)) ** t
            paid += c * (1 + ln.get("contrib_growth", 0.0)) ** t
            path.append(w)
        k = ln["id"]
        v[f"{k}_end"], v[f"{k}_paid"] = path[-1], paid
        v[f"{k}_rate"], v[f"{k}_start"], v[f"{k}_contrib"] = ln["rate"], ln.get("start", 0.0), c
        v[f"{k}_mult"] = path[-1] / paid if paid else 0.0
        f.update({f"{k}_end": "num0", f"{k}_paid": "num0", f"{k}_rate": "pct0", f"{k}_start": "num0",
                  f"{k}_contrib": "num0", f"{k}_mult": "num1"})
        if "target" in p:  # years to reach target, 2×target, 3×target
            prev = 0
            for m in (1, 2, 3):
                yr = next((i for i, x in enumerate(path) if x >= m * p["target"]), None)
                if yr is not None:
                    v[f"{k}_t{m}"], f[f"{k}_t{m}"] = yr - prev, "int"
                    prev = yr
        lines.append((ln["label"], np.array(path), ln.get("color", "accent")))
    if len(p["lines"]) >= 2:
        a, b = p["lines"][0]["id"], p["lines"][1]["id"]
        v["gap_end"], f["gap_end"] = v[f"{a}_end"] - v[f"{b}_end"], "num0"
        v["gap_ratio"], f["gap_ratio"] = (v[f"{a}_end"] / v[f"{b}_end"]) if v[f"{b}_end"] else 0.0, "num1"
    if "target" in p:
        v["target"], f["target"] = p["target"], "num0"
    return v, f, {"lines": lines, "unit": p.get("unit", ""), "years": years}


def k_fi(p, rng):
    """Years until investment income covers spending, by savings rate (real return r, withdrawal rate wr)."""
    r, wr, out = p.get("real_return", 0.05), p.get("withdraw", 0.04), []
    v, f = {"real_return": r, "withdraw": wr}, {"real_return": "pct0", "withdraw": "pct0"}
    for s in p["rates"]:
        w, yr = 0.0, 0
        spend = 1 - s
        while w * wr < spend and yr < 80:
            w = w * (1 + r) + s
            yr += 1
        out.append((s, yr))
        k = f"y{int(round(s * 100))}"
        v[k], f[k] = yr, "int"
        v["s" + k[1:]], f["s" + k[1:]] = s, "pct0"
    return v, f, {"curve": out}


def k_ruin(p, rng):
    """Bankroll random walks per group; stake modes fixed / fraction / martingale / tilt / chase."""
    v, f, groups = {}, {}, []
    n, rounds = p.get("players", 1000), p.get("rounds", 1000)
    for g in p["groups"]:
        q, pay = g.get("p", p.get("p", 0.5)), g.get("payout", p.get("payout", 1.0))
        start, mode, stake = g.get("start", p.get("start", 100.0)), g.get("mode", "fixed"), g.get("stake", 1.0)
        limit = g.get("limit", 1e18)
        bank = np.full(n, float(start))
        bet = np.full(n, float(stake))
        losses = np.zeros(n)
        alive = np.ones(n, bool)
        paths = np.zeros((min(n, 40), rounds + 1)); paths[:, 0] = start
        for t in range(rounds):
            if mode == "fraction":
                b = bank * stake
            else:
                b = np.minimum(bet, bank)
            q_eff = q - g.get("tilt_penalty", 0.0) * (losses >= 2) if mode == "tilt" else q
            win = rng.random(n) < q_eff
            bank = np.where(alive, bank + np.where(win, b * pay, -b), bank)
            if mode == "martingale":
                bet = np.where(win, stake, np.minimum(bet * 2, limit))
            elif mode == "tilt":   # after 2 losses in a row, stake triples until a win
                losses = np.where(win, 0, losses + 1)
                bet = np.where(losses >= 2, stake * 3, stake)
            elif mode == "chase":  # stake grows to win back what is down
                bet = np.maximum(stake, (start - bank) * 0.5)
            alive &= bank > g.get("ruin", 1e-9) * (1 if mode != "fraction" else start)
            bank = np.where(alive, bank, 0.0)
            paths[:, t + 1] = bank[: paths.shape[0]]
        k = g["id"]
        v[f"{k}_ruin"], f[f"{k}_ruin"] = float((~alive).mean()), "pct0"
        v[f"{k}_median"], f[f"{k}_median"] = float(np.median(bank)), "num0"
        v[f"{k}_profit"], f[f"{k}_profit"] = float((bank > start).mean()), "pct0"
        v[f"{k}_start"], f[f"{k}_start"] = start, "num0"
        v[f"{k}_stake"], f[f"{k}_stake"] = stake, ("pct0" if mode == "fraction" else "num0")
        v[f"{k}_p"], f[f"{k}_p"] = q, "pct1"
        v[f"{k}_edge"], f[f"{k}_edge"] = q * (1 + pay) - 1, "pct1"
        groups.append((g["label"], paths, float((~alive).mean())))
    v["players"], v["rounds"] = n, rounds
    f["players"], f["rounds"] = "int", "int"
    return v, f, {"groups": groups, "start": p.get("start", 100.0)}


def k_ev(p, rng):
    """Options with outcome lists; EV per option; simulate N repeats for the first option."""
    v, f, opts = {}, {}, []
    for o in p["options"]:
        ps = np.array([x["p"] for x in o["outcomes"]]); pays = np.array([x["pay"] for x in o["outcomes"]])
        ev = float((ps * pays).sum())
        k = o["id"]
        v[f"{k}_ev"], f[f"{k}_ev"] = ev, p.get("fmt", "num1")
        for i, x in enumerate(o["outcomes"]):
            v[f"{k}_p{i}"], f[f"{k}_p{i}"] = x["p"], "pct0"
            v[f"{k}_pay{i}"], f[f"{k}_pay{i}"] = x["pay"], p.get("pay_fmt", "num0")
            v[f"{k}_abs{i}"], f[f"{k}_abs{i}"] = abs(x["pay"]), p.get("pay_fmt", "num0")
        opts.append((o["label"], ev))
    o0 = p["options"][0]
    n = p.get("trials", 50)
    ps = np.array([x["p"] for x in o0["outcomes"]]); pays = np.array([x["pay"] for x in o0["outcomes"]])
    draws = pays[rng.choice(len(ps), size=n, p=ps / ps.sum())]
    cum = np.cumsum(draws)
    v["trials"], v["sim_total"], v["sim_losses"] = n, float(cum[-1]), int((draws < 0).sum())
    v["sim_loss_pct"] = float((draws < 0).mean())
    f.update({"trials": "int", "sim_total": p.get("fmt", "num0"), "sim_losses": "int", "sim_loss_pct": "pct0"})
    return v, f, {"options": opts, "cum": cum}


def k_coins(p, rng):
    """N people flip a fair coin R times; only those who never miss 'succeed' (survivorship)."""
    n, r = p.get("n", 1024), p.get("rounds", 10)
    alive = np.ones(n, bool); history = [n]
    for _ in range(r):
        alive &= rng.random(n) < 0.5
        history.append(int(alive.sum()))
    v = {"n": n, "rounds": r, "survivors": history[-1], "expected": n / 2 ** r,
         "after3": history[3], "luck_odds": 2 ** r}
    f = {"n": "int", "rounds": "int", "survivors": "int", "expected": "num0", "after3": "int", "luck_odds": "int"}
    return v, f, {"history": history}


def k_bars(p, rng):
    """Values from a published study (each bar carries its own source); nothing is simulated."""
    v, f = {}, {}
    for b in p["bars"]:
        v[b["id"]], f[b["id"]] = b["value"], b.get("fmt", "num0")
    for k, x in (p.get("derived") or {}).items():  # [a, b] ratio a/b, or [a, b, "premium"] = a/b − 1
        if len(x) > 2 and x[2] == "premium":
            v[k], f[k] = v[x[0]] / v[x[1]] - 1, "pct0"
        else:
            v[k], f[k] = v[x[0]] / v[x[1]], "num1"
    return v, f, {"bars": [(b["label"], b["value"], b.get("color", "accent")) for b in p["bars"]],
                  "source": p.get("source", ""), "unit": p.get("unit", "")}


def k_montyhall(p, rng):
    n = p.get("games", 3000)
    car = rng.integers(0, 3, n); pick = rng.integers(0, 3, n)
    stay = car == pick
    v = {"games": n, "stay_win": float(stay.mean()), "switch_win": float((~stay).mean()),
         "doors": 3}
    f = {"games": "int", "stay_win": "pct0", "switch_win": "pct0", "doors": "int"}
    k = np.arange(1, n + 1)
    return v, f, {"stay": np.cumsum(stay) / k, "switch": np.cumsum(~stay) / k}


def k_birthday(p, rng):
    ns = np.arange(1, 81)
    prob = 1 - np.cumprod((365 - ns + 1) / 365)
    n50 = int(ns[np.argmax(prob >= 0.5)])
    sims = rng.integers(0, 365, size=(4000, n50))
    sim = float(np.mean([len(set(r)) < n50 for r in sims]))
    v = {"n50": n50, "p_n50": float(prob[n50 - 1]), "p30": float(prob[29]), "p50": float(prob[49]),
         "p70": float(prob[69]), "sim_n50": sim, "pairs_n50": n50 * (n50 - 1) // 2, "days": 365}
    f = {"n50": "int", "p_n50": "pct1", "p30": "pct0", "p50": "pct0", "p70": "pct1", "sim_n50": "pct0",
         "pairs_n50": "int", "days": "int"}
    return v, f, {"n": ns, "p": prob}


def k_lln(p, rng):
    n = p.get("flips", 5000)
    x = rng.random(n) < 0.5
    run = np.cumsum(x) / np.arange(1, n + 1)
    v = {"flips": n, "at10": float(run[9]), "at100": float(run[99]), "at1000": float(run[999]),
         "at_end": float(run[-1])}
    return v, {"flips": "int", "at10": "pct0", "at100": "pct0", "at1000": "pct1", "at_end": "pct1"}, {"run": run}


def k_regression(p, rng):
    """Score = skill + luck, two rounds; where does round 1's top 10% land in round 2?"""
    n, luck = p.get("n", 2000), p.get("luck_share", 0.5)
    skill = rng.normal(size=n) * math.sqrt(1 - luck)
    r1 = skill + rng.normal(size=n) * math.sqrt(luck)
    r2 = skill + rng.normal(size=n) * math.sqrt(luck)
    pct = lambda a: a.argsort().argsort() / (len(a) - 1)
    p1, p2 = pct(r1), pct(r2)
    top = p1 >= 0.9
    v = {"n": n, "luck_share": luck, "top_r1": float(p1[top].mean()), "top_r2": float(p2[top].mean()),
         "still_top": float((p2[top] >= 0.9).mean())}
    f = {"n": "int", "luck_share": "pct0", "top_r1": "pct0", "top_r2": "pct0", "still_top": "pct0"}
    return v, f, {"r1": p1, "r2": p2, "top": top}


def k_kelly(p, rng):
    q, b = p.get("p", 0.55), p.get("b", 1.0)
    fs = np.linspace(0.0, 0.5, 201)
    g = q * np.log1p(b * fs) + (1 - q) * np.log1p(-np.minimum(fs, 0.999))
    fstar = (q * b - (1 - q)) / b
    gstar = q * math.log1p(b * fstar) + (1 - q) * math.log1p(-fstar)
    f2 = 2 * fstar
    g2 = q * math.log1p(b * f2) + (1 - q) * math.log1p(-f2)
    # 200 bets, 1000 players, full Kelly vs 2× Kelly: median final multiple
    n, t = 1000, p.get("bets", 200)
    w = rng.random((n, t)) < q
    med = lambda fr: float(np.median(np.prod(np.where(w, 1 + b * fr, 1 - fr), axis=1)))
    v = {"p": q, "b": b, "fstar": fstar, "gstar": gstar, "f2": f2, "g2": g2, "bets": t,
         "med_kelly": med(fstar), "med_2kelly": med(f2), "med_half": med(fstar / 2), "fhalf": fstar / 2}
    f = {"p": "pct0", "b": "num0", "fstar": "pct0", "gstar": "pct2", "f2": "pct0", "g2": "pct2", "bets": "int",
         "med_kelly": "num1", "med_2kelly": "num2", "med_half": "num1", "fhalf": "pct0"}
    return v, f, {"f": fs, "g": g, "fstar": fstar}


def k_powerlaw(p, rng):
    a, n = p.get("alpha", 1.16), p.get("n", 10000)
    x = np.sort((rng.pareto(a, n) + 1))[::-1]
    share = np.cumsum(x) / x.sum()
    v = {"alpha": a, "n": n, "top20": float(share[int(0.2 * n) - 1]), "top1": float(share[int(0.01 * n) - 1]),
         "bottom50": float(1 - share[int(0.5 * n) - 1])}
    f = {"alpha": "num2", "n": "int", "top20": "pct0", "top1": "pct0", "bottom50": "pct0"}
    return v, f, {"share": share}


def k_matrix(p, rng):
    """2×2 game: pure Nash equilibria found by best responses; mixed equilibrium if none (zero-sum style)."""
    A = np.array(p["payoffs"], float)   # A[i][j] = (row payoff, col payoff)
    nash = []
    for i in range(2):
        for j in range(2):
            if A[i, j, 0] >= A[1 - i, j, 0] and A[i, j, 1] >= A[i, 1 - j, 1]:
                nash.append((i, j))
    v, f = {"n_nash": len(nash)}, {"n_nash": "int"}
    for i in range(2):
        for j in range(2):
            v[f"r{i}{j}"], v[f"c{i}{j}"] = A[i, j, 0], A[i, j, 1]
            f[f"r{i}{j}"], f[f"c{i}{j}"] = "num0", "num0"
    if not nash:  # mixed: column mixes to make row indifferent and vice versa
        a = A[:, :, 0]; b = A[:, :, 1]
        q = (a[1, 1] - a[0, 1]) / (a[0, 0] - a[0, 1] - a[1, 0] + a[1, 1])
        pr = (b[1, 1] - b[1, 0]) / (b[0, 0] - b[0, 1] - b[1, 0] + b[1, 1])
        v["mix_row"], v["mix_col"] = float(pr), float(q)
        f["mix_row"], f["mix_col"] = "pct0", "pct0"
    if nash:
        i, j = nash[0]
        v["nash_r"], v["nash_c"] = A[i, j, 0], A[i, j, 1]
        f["nash_r"], f["nash_c"] = "num0", "num0"
        best = max(((A[x, y].sum(), (x, y)) for x in range(2) for y in range(2)))
        v["best_total"], v["nash_total"] = best[0], A[i, j].sum()
        f["best_total"], f["nash_total"] = "num0", "num0"
    return v, f, {"A": A, "nash": nash, "rows": p["rows"], "cols": p["cols"], "players": p.get("players", ["You", "Them"])}


def _ipd_play(s1, s2, rounds, rng, noise=0.0):
    T, R, P, S = 5, 3, 1, 0
    h1, h2, sc1, sc2 = [], [], 0, 0
    for t in range(rounds):
        a, b = s1(h1, h2, rng), s2(h2, h1, rng)
        if noise and rng.random() < noise: a = not a
        if noise and rng.random() < noise: b = not b
        if a and b: sc1 += R; sc2 += R
        elif a and not b: sc1 += S; sc2 += T
        elif not a and b: sc1 += T; sc2 += S
        else: sc1 += P; sc2 += P
        h1.append(a); h2.append(b)
    return sc1, sc2


IPD = {  # True = cooperate
    "Tit for Tat": lambda me, op, rng: True if not op else op[-1],
    "Always Defect": lambda me, op, rng: False,
    "Always Cooperate": lambda me, op, rng: True,
    "Random": lambda me, op, rng: bool(rng.random() < 0.5),
    "Grudger": lambda me, op, rng: all(op),
    "Sneaky Defector": lambda me, op, rng: (not op or op[-1]) and rng.random() > 0.1,
}


def k_ipd(p, rng):
    rounds = p.get("rounds", 200)
    names = list(IPD)
    score = {k: 0 for k in names}
    for i, a in enumerate(names):
        for b in names[i:]:
            s1, s2 = _ipd_play(IPD[a], IPD[b], rounds, rng)
            score[a] += s1
            if a != b:
                score[b] += s2
    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    tft_rank = [k for k, _ in ranked].index("Tit for Tat") + 1
    one_c, one_d = _ipd_play(IPD["Tit for Tat"], IPD["Always Defect"], 1, rng)
    rep_t, rep_d = _ipd_play(IPD["Tit for Tat"], IPD["Always Defect"], rounds, rng)
    coop, _ = _ipd_play(IPD["Tit for Tat"], IPD["Tit for Tat"], rounds, rng)
    v = {"rounds": rounds, "n_strats": len(names), "tft_rank": tft_rank, "tft_score": score["Tit for Tat"],
         "defect_score": score["Always Defect"], "top_score": ranked[0][1],
         "rep_defect_gain": rep_d, "coop_pair": coop, "one_shot_defect": one_d, "one_shot_tft": one_c,
         "rep_tft": rep_t}
    f = {k: "int" for k in v}
    return v, f, {"ranked": ranked}


def k_commons(p, rng):
    """Shared fish stock with logistic regrowth; selfish (each takes more) vs quota."""
    K, r, years, users = p.get("K", 1000.0), p.get("growth", 0.3), p.get("years", 40), p.get("users", 10)
    def run(take):
        s, path, caught = K, [K], 0.0
        for _ in range(years):
            h = min(s, users * take)
            s = max(0.0, s - h); caught += h
            s = s + r * s * (1 - s / K)
            path.append(s)
        return np.array(path), caught
    q_take = r * K / 4 / users           # maximum sustainable yield split evenly
    s_take = q_take * p.get("greed", 1.6)
    quota, qc = run(q_take); greedy, gc = run(s_take)
    collapse = next((i for i, x in enumerate(greedy) if x < 0.05 * K), None)
    v = {"users": users, "years": years, "quota_catch": qc, "greedy_catch": gc,
         "collapse_year": collapse if collapse is not None else years, "greed_extra": p.get("greed", 1.6) - 1,
         "quota_end": float(quota[-1] / K), "greedy_end": float(greedy[-1] / K)}
    f = {"users": "int", "years": "int", "quota_catch": "num0", "greedy_catch": "num0", "collapse_year": "int",
         "greed_extra": "pct0", "quota_end": "pct0", "greedy_end": "pct0"}
    return v, f, {"quota": quota / K, "greedy": greedy / K}


def k_fattail(p, rng):
    n, dfree = p.get("days", 10000), p.get("df", 3)
    z = rng.normal(size=n)
    t = rng.standard_t(dfree, size=n); t = t / t.std()
    from math import erf, sqrt
    tail5 = 1 - erf(5 / sqrt(2))
    v = {"days": n, "years": n / 252, "normal_big": int((np.abs(z) > 4).sum()), "fat_big": int((np.abs(t) > 4).sum()),
         "normal_5s_expected_years": 1 / (tail5 * 252), "fat_5s": int((np.abs(t) > 5).sum()),
         "fat_max": float(np.abs(t).max())}
    f = {"days": "int", "years": "num0", "normal_big": "int", "fat_big": "int",
         "normal_5s_expected_years": "num0", "fat_5s": "int", "fat_max": "num1"}
    return v, f, {"z": z, "t": t}


def k_streak(p, rng):
    """After k identical outcomes in a row, how often is the next one different? (fair, independent)."""
    n, k = p.get("n", 200000), p.get("k", 5)
    x = rng.random(n) < p.get("p", 0.5)
    run = np.zeros(n, int)
    for i in range(1, n):
        run[i] = run[i - 1] + 1 if x[i] == x[i - 1] else 1
    run[0] = 1
    idx = np.where(run[:-1] >= k)[0]
    flip = float((x[idx + 1] != x[idx]).mean())
    v = {"n": n, "k": k, "cases": len(idx), "flip": flip, "same": 1 - flip}
    f = {"n": "int", "k": "int", "cases": "int", "flip": "pct1", "same": "pct1"}
    return v, f, {"flip": flip, "k": k, "labels": p.get("labels", ["R", "red again", "switch"])}


def k_simpson(p, rng):
    g = p["groups"]  # [{label, a:[succ, n], b:[succ, n]}]
    v, f = {}, {}
    ta, tb = [0, 0], [0, 0]
    bars = []
    for i, x in enumerate(g):
        ra, rb = x["a"][0] / x["a"][1], x["b"][0] / x["b"][1]
        v[f"g{i}_a"], v[f"g{i}_b"] = ra, rb
        f[f"g{i}_a"], f[f"g{i}_b"] = "pct0", "pct0"
        ta = [ta[0] + x["a"][0], ta[1] + x["a"][1]]; tb = [tb[0] + x["b"][0], tb[1] + x["b"][1]]
        bars.append((x["label"], ra, rb))
    v["all_a"], v["all_b"] = ta[0] / ta[1], tb[0] / tb[1]
    f["all_a"], f["all_b"] = "pct0", "pct0"
    v["n_a"], v["n_b"] = ta[1], tb[1]
    f["n_a"], f["n_b"] = "int", "int"
    bars.append((p.get("total_label", "Total"), v["all_a"], v["all_b"]))
    return v, f, {"bars": bars, "a": p.get("a_label", "A"), "b": p.get("b_label", "B"), "source": p.get("source", "")}


def k_baserate(p, rng):
    n, prev, sens, fpr = p.get("n", 1000), p["prevalence"], p["sensitivity"], p["false_positive"]
    sick = round(n * prev); tp = round(sick * sens); fp = round((n - sick) * fpr)
    v = {"n": n, "prevalence": prev, "sensitivity": sens, "false_positive": fpr, "sick": sick, "tp": tp, "fp": fp,
         "positives": tp + fp, "ppv": tp / (tp + fp)}
    f = {"n": "int", "prevalence": "pct0", "sensitivity": "pct0", "false_positive": "pct0", "sick": "int", "tp": "int",
         "fp": "int", "positives": "int", "ppv": "pct0"}
    return v, f, {"n": n, "tp": tp, "fp": fp, "sick": sick}


def k_discount(p, rng):
    """Hyperbolic V = A/(1+kD): preference reversal between 'now vs later' and the same pair pushed out."""
    k, a, b, gap, shift = p.get("k", 0.1), p.get("small", 100), p.get("large", 150), p.get("gap", 12), p.get("shift", 12)
    hv = lambda amt, d: amt / (1 + k * d)
    now_small, now_large = hv(a, 0), hv(b, gap)
    later_small, later_large = hv(a, shift), hv(b, shift + gap)
    v = {"k": k, "small": a, "large": b, "gap": gap, "shift": shift, "now_small": now_small, "now_large": now_large,
         "later_small": later_small, "later_large": later_large, "implied": (b / a) - 1}
    f = {"k": "num2", "small": "num0", "large": "num0", "gap": "int", "shift": "int", "now_small": "num0",
         "now_large": "num0", "later_small": "num0", "later_large": "num0", "implied": "pct0"}
    d = np.linspace(0, shift + gap, 200)
    return v, f, {"d": d, "small": [(x, hv(a, max(0, 0 - x))) for x in d], "params": (k, a, b, gap, shift)}


def k_lemons(p, rng):
    """Akerlof: buyers pay average quality; sellers above the price leave; repeat."""
    q = np.sort(rng.uniform(0, 100, p.get("cars", 1000)))
    rounds, path, market = p.get("rounds", 8), [], q.copy()
    for _ in range(rounds):
        price = market.mean() * p.get("buyer_premium", 1.0)
        path.append((price, len(market)))
        market = market[market <= price]
        if len(market) < 2:
            break
    v = {"cars": len(q), "first_price": path[0][0], "last_price": path[-1][0], "left": path[-1][1],
         "left_pct": path[-1][1] / len(q), "rounds": len(path)}
    f = {"cars": "int", "first_price": "num0", "last_price": "num0", "left": "int", "left_pct": "pct0", "rounds": "int"}
    return v, f, {"path": path}


def k_combos(p, rng):
    """Poker combinatorics: combos of each hand class in a range (pairs 6, suited 4, offsuit 12)."""
    out, v, f = [], {}, {}
    for h in p["hands"]:
        c = {"pair": 6, "suited": 4, "offsuit": 12, "any": 16}[h["type"]] - h.get("blocked", 0)
        out.append((h["label"], c, h.get("strong", False)))
        v[h["id"]], f[h["id"]] = c, "int"
    total = sum(c for _, c, _ in out); strong = sum(c for _, c, s in out if s)
    v.update({"total": total, "strong": strong, "strong_pct": strong / total})
    f.update({"total": "int", "strong": "int", "strong_pct": "pct0"})
    return v, f, {"hands": out}


def k_potodds(p, rng):
    pot, call = p["pot"], p["call"]
    eq = p["equity"] if "equity" in p else p["outs"] / p["unseen"]
    need = call / (pot + call)
    ev = eq * pot - (1 - eq) * call
    v = {"pot": pot, "call": call, "equity": eq, "need": need, "ev": ev, "odds": pot / call, "outs": p.get("outs", 0), "unseen": p.get("unseen", 0)}
    f = {"pot": "num0", "call": "num0", "equity": "pct0", "need": "pct0", "ev": "num1", "odds": "num1", "outs": "int", "unseen": "int"}
    eqs = np.linspace(0, 0.6, 61)
    return v, f, {"eqs": eqs, "ev": eqs * pot - (1 - eqs) * call, "need": need, "eq": eq}


def k_foldeq(p, rng):
    pot, bet, eq = p["pot"], p["bet"], p["equity"]
    fs = np.linspace(0, 1, 101)
    ev = fs * pot + (1 - fs) * (eq * (pot + 2 * bet) - bet)
    be = (bet - eq * (pot + 2 * bet)) / (pot + bet - eq * (pot + 2 * bet))
    v = {"pot": pot, "bet": bet, "equity": eq, "breakeven_fold": be,
         "ev_no_fold": eq * (pot + 2 * bet) - bet, "fold_ex": p.get("fold_ex", 0.4)}
    v["ev_ex"] = v["fold_ex"] * pot + (1 - v["fold_ex"]) * v["ev_no_fold"]
    f = {"pot": "num0", "bet": "num0", "equity": "pct0", "breakeven_fold": "pct0", "ev_no_fold": "num1",
         "fold_ex": "pct0", "ev_ex": "num1"}
    return v, f, {"fs": fs, "ev": ev, "be": be}


def k_bluff(p, rng):
    """River: bettor bets B into pot P. Caller needs B/(P+2B) equity; GTO bluff share = B/(P+2B) of the betting range.
    Caller's EV of calling vs bettor's bluff share: flat at the GTO share (cannot be exploited)."""
    pot, bet = p["pot"], p["bet"]
    gto = bet / (pot + 2 * bet)
    mdf = pot / (pot + bet)
    bs = np.linspace(0, 0.7, 71)
    call_ev = bs * (pot + bet) - (1 - bs) * bet        # per call: win pot+bet vs bluffs, lose bet vs value
    v = {"pot": pot, "bet": bet, "gto_bluff": gto, "mdf": mdf, "ratio": (1 - gto) / gto,
         "over": p.get("over", 0.5), "under": p.get("under", 0.1),
         "gto_half": 0.5 / (1 + 2 * 0.5), "gto_pot": 1 / 3, "gto_2x": 2 / (1 + 2 * 2)}
    v["call_ev_over"] = v["over"] * (pot + bet) - (1 - v["over"]) * bet
    v["call_ev_under"] = v["under"] * (pot + bet) - (1 - v["under"]) * bet
    f = {"pot": "num0", "bet": "num0", "gto_bluff": "pct0", "mdf": "pct0", "ratio": "num0", "over": "pct0",
         "under": "pct0", "call_ev_over": "num0", "call_ev_under": "num0", "gto_half": "pct0", "gto_pot": "pct0",
         "gto_2x": "pct0"}
    return v, f, {"bs": bs, "ev": call_ev, "gto": gto}


def k_variance(p, rng):
    """Winning player: win rate wr (bb/100 hands), std sd (bb/100). Simulated careers; share losing after N hands."""
    wr, sd, hands, n = p.get("wr", 5.0), p.get("sd", 90.0), p.get("hands", 50000), p.get("players", 1000)
    blocks = hands // 100
    paths = np.cumsum(rng.normal(wr, sd, size=(n, blocks)), axis=1)
    v = {"wr": wr, "sd": sd, "hands": hands, "players": n,
         "losing_10k": float((paths[:, 99] < 0).mean()), "losing_end": float((paths[:, -1] < 0).mean()),
         "worst_dd": float(-(paths - np.maximum.accumulate(paths, axis=1)).max(axis=1).mean() * -1),
         "expected": wr * blocks}
    f = {"wr": "num0", "sd": "num0", "hands": "int", "players": "int", "losing_10k": "pct0", "losing_end": "pct0",
         "worst_dd": "num0", "expected": "num0"}
    return v, f, {"paths": paths[:30], "blocks": blocks}


def k_attrition(p, rng):
    """War of attrition, prize V, cost 1 per round; symmetric equilibrium quit hazard 1/V. Who gains on average?"""
    V, n = p.get("prize", 100.0), p.get("contests", 20000)
    t1, t2 = rng.exponential(V, n), rng.exponential(V, n)
    dur = np.minimum(t1, t2)
    paid = 2 * dur
    v = {"prize": V, "contests": n, "avg_paid": float(paid.mean()), "avg_len": float(dur.mean()),
         "net_avg": float((V - paid.mean()) / 2), "over_prize": float((paid > V).mean())}
    f = {"prize": "num0", "contests": "int", "avg_paid": "num0", "avg_len": "num0", "net_avg": "num0",
         "over_prize": "pct0"}
    return v, f, {"paid": paid, "V": V}


def k_lottery(p, rng):
    n, k = p.get("pool", 45), p.get("pick", 6)
    combos = math.comb(n, k)
    per_year = p.get("per_year", 365)
    v = {"pool": n, "pick": k, "combos": combos, "years": combos / per_year, "per_year": per_year,
         "p_10y": 1 - (1 - 1 / combos) ** (per_year * 10)}
    f = {"pool": "int", "pick": "int", "combos": "int", "years": "int", "per_year": "int", "p_10y": "pct3"}
    return v, f, {"combos": combos}


def k_diagram(p, rng):
    """Hand-drawn concept map (no numbers): nodes and arrows drawn stroke by stroke."""
    return {}, {}, {"nodes": p["nodes"], "edges": p.get("edges", []), "loop": p.get("loop", False)}


KINDS = {k[2:]: g for k, g in dict(globals()).items() if k.startswith("k_")}



KINDS = {k[2:]: g for k, g in dict(globals()).items() if k.startswith("k_")}


class SimModel:
    """Same interface the pipeline expects from a model (values, formats, code, seed); no chart, no 3D."""

    has_chart = has_surface = has_formula = False
    real_data = False

    def __init__(self, sim, seed=None, topic="sim"):
        self.topic, self.family, self.kind = topic, None, sim["kind"]
        self.seed = seed if seed is not None else sim.get("seed", 7)
        vals, self.formats, self.series = KINDS[self.kind](sim, np.random.default_rng(self.seed))
        self.values = {k: (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v)
                       for k, v in vals.items()}
        self.code = inspect.getsource(KINDS[self.kind]).rstrip()
        self.params = {k: v for k, v in sim.items() if k != "kind"}
        self.entry = {"vi": topic, "en": topic}

    def plot2d(self, ax, upto=1.0):
        pass

    def surface(self):
        return None


if __name__ == "__main__":
    from core import fmt_vi, set_lang

    set_lang("en")
    for path in sys.argv[1:]:
        ep = json.load(open(path, encoding="utf-8"))
        m = SimModel(ep["sim"], ep.get("seed"), ep["id"])
        print(f"\n# {ep['id']}  ({m.kind}, seed {m.seed})")
        for k, v in m.values.items():
            print(f"  {{{k}}}".ljust(26), fmt_vi(v, m.formats.get(k, "num2")).ljust(14), f"[{m.formats.get(k, 'num2')}]")
