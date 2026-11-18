"""Mind & game models: psychology, poker theory and game theory, with code that really runs.

Same contract as models.py (imported there and registered in TOPICS):
  <topic>_demo (<= 16 lines, <= 56 chars: shown on screen), compute_<topic> -> (values, formats, series),
  plot2d_<topic>(ax, s, upto), surface_<topic>(s, v).
Every number in the narration comes from `values`. Simulations use fixed seeds.
These topics are about decision-making under uncertainty; they never promote gambling.
"""
from __future__ import annotations

import math

import numpy as np

from core import THEME, hex_

ACC, POS, NEG, NEU, MUT, TXT = (hex_(THEME[k]) for k in ("accent", "positive", "negative", "neutral", "muted", "text"))


def _legend(ax, loc="upper left"):
    ax.legend(loc=loc, fontsize=18, frameon=False, labelcolor=TXT)


# =============================================================== Martingale (gấp thếp)
def martingale_demo(seed=9, players=10000, rounds=200):
    rng = np.random.default_rng(seed)
    p = 18 / 37                    # cửa đỏ của roulette
    bank = np.full(players, 255.0)  # chịu 7 ván thua
    bet = np.ones(players)
    alive = np.ones(players, bool)
    for _ in range(rounds):
        win = rng.random(players) < p
        bet = np.minimum(bet, bank)
        bank += np.where(win, bet, -bet) * alive
        bet = np.where(win, 1, bet * 2)
        alive &= bank > 0
    return bank, alive, p


def compute_martingale(seed=9, returns=None):
    bank, alive, p = martingale_demo(seed)
    # one illustrative path for the chart: sawtooth up, then the crash (first seed whose path busts)
    for k in range(1, 500):
        rng = np.random.default_rng(seed * 1000 + k)
        path, b, bet = [255.0], 255.0, 1.0
        for _ in range(2000):
            bet = min(bet, b)
            w = rng.random() < p
            b += bet if w else -bet
            bet = 1 if w else bet * 2
            path.append(b)
            if b <= 0:
                break
        if b <= 0 and len(path) > 250:
            break
    path = np.array(path)
    win_rounds = float(np.mean(np.diff(path) > 0))
    values = {"p_red": p, "start": 255, "players": len(bank), "rounds": 200,
              "ruined": float(1 - alive.mean()), "survivors": float(alive.mean()),
              "mean_final": float(bank.mean()), "loss_avg": float(255 - bank.mean()),
              "path_peak": float(path.max()), "path_len": int(len(path) - 1), "win_share": win_rounds,
              "streak_needed": 8, "p_streak8": (1 - p) ** 8}
    formats = {"p_red": "pct1", "start": "int", "players": "int", "rounds": "int", "ruined": "pct0",
               "survivors": "pct0", "mean_final": "num0", "loss_avg": "num0", "path_peak": "num0",
               "path_len": "int", "win_share": "pct0", "streak_needed": "int", "p_streak8": "pct2"}
    return values, formats, {"path": path}


def plot2d_martingale(ax, s, upto=1.0):
    y = s["path"]; n = len(y); k = max(2, int(n * upto))
    ax.plot(np.arange(k), y[:k], color=ACC, lw=2.6)
    ax.axhline(255, color=MUT, lw=1, ls="--")
    ax.set_xlim(0, n); ax.set_ylim(-10, y.max() * 1.1)
    ax.set_xlabel("ván"); ax.set_ylabel("vốn (đơn vị)")


def surface_martingale(s, v):
    banks = np.array([2 ** k - 1 for k in range(3, 12)], float)   # survive k-1... losses
    rounds = np.linspace(10, 1000, 40)
    q = 1 - 18 / 37
    B, R = np.meshgrid(np.log2(banks + 1), rounds)
    p_run = q ** B                       # chance a given streak starts and wipes the bank
    Z = 1 - (1 - p_run) ** (R / 2)       # rough ruin probability over R rounds
    return {"X": B, "Y": R, "Z": Z * 100, "xl": "số ván thua chịu được", "yl": "số ván chơi", "zl": "xác suất cháy %"}


# =============================================================== Gambler's ruin
def gambler_ruin_demo(seed=2, start=50, target=100):
    def p_ruin(p):  # công thức đóng
        r = (1 - p) / p
        if abs(r - 1) < 1e-12:
            return 1 - start / target
        return (r**start - r**target) / (1 - r**target)
    rng = np.random.default_rng(seed)
    sims, p = 4000, 0.49
    ruined = 0
    for _ in range(sims):
        x = start
        while 0 < x < target:
            x += 1 if rng.random() < p else -1
        ruined += x == 0
    return p_ruin(0.5), p_ruin(p), ruined / sims, p


def compute_gambler_ruin(seed=2, returns=None):
    fair, edge, sim, p = gambler_ruin_demo(seed)
    r = (1 - p) / p
    targets = np.arange(52, 401, 4)
    pr = (r ** 50 - r ** targets) / (1 - r ** targets)
    values = {"p_player": p, "house_edge": 1 - 2 * p, "ruin_fair": fair, "ruin_edge": edge, "ruin_sim": sim,
              "start": 50, "target": 100, "sims": 4000, "win_edge": 1 - edge, "ruin_far": float(pr[-1]),
              "target_far": int(targets[-1])}
    formats = {"p_player": "pct0", "house_edge": "pct0", "ruin_fair": "pct0", "ruin_edge": "pct0", "ruin_sim": "pct0",
               "start": "int", "target": "int", "sims": "int", "win_edge": "pct0", "ruin_far": "pct0",
               "target_far": "int"}
    return values, formats, {"targets": targets, "pr": pr, "r": r}


def plot2d_gambler_ruin(ax, s, upto=1.0):
    t, pr = s["targets"], s["pr"]; k = max(2, int(len(t) * upto))
    fair = 1 - 50 / t
    ax.plot(t[:k], fair[:k] * 100, color=MUT, lw=2.2, ls="--", label="ván công bằng 50/50")
    ax.plot(t[:k], pr[:k] * 100, color=NEG, lw=3, label="lệch 1% về nhà cái")
    ax.set_xlim(t[0], t[-1]); ax.set_ylim(0, 100)
    ax.set_xlabel("mục tiêu (bắt đầu với 50)"); ax.set_ylabel("xác suất cháy %")
    _legend(ax, "lower right")


def surface_gambler_ruin(s, v):
    p = np.linspace(0.46, 0.5, 30); T = np.linspace(60, 300, 30)
    P, TT = np.meshgrid(p, T)
    r = (1 - P) / P
    with np.errstate(all="ignore"):
        Z = np.where(np.abs(r - 1) < 1e-9, 1 - 50 / TT, (r ** 50 - r ** TT) / (1 - r ** TT))
    return {"X": P * 100, "Y": TT, "Z": Z * 100, "xl": "tỷ lệ thắng mỗi ván %", "yl": "mục tiêu", "zl": "cháy %"}


# =============================================================== Monty Hall
def monty_hall_demo(seed=3, games=10000):
    rng = np.random.default_rng(seed)
    car = rng.integers(0, 3, games)
    pick = rng.integers(0, 3, games)
    stay = car == pick
    switch = ~stay      # đổi thắng khi chọn sai lúc đầu
    return stay, switch


def compute_monty_hall(seed=3, returns=None):
    stay, switch = monty_hall_demo(seed)
    n = np.arange(1, len(stay) + 1)
    values = {"games": len(stay), "p_stay": float(stay.mean()), "p_switch": float(switch.mean()),
              "ratio": float(switch.mean() / stay.mean()), "doors": 3,
              "p_switch_100": 99 / 100, "p_stay_100": 1 / 100}
    formats = {"games": "int", "p_stay": "pct0", "p_switch": "pct0", "ratio": "x1", "doors": "int",
               "p_switch_100": "pct0", "p_stay_100": "pct0"}
    return values, formats, {"stay": np.cumsum(stay) / n, "switch": np.cumsum(switch) / n}


def plot2d_monty_hall(ax, s, upto=1.0):
    n = 2000; k = max(2, int(n * upto)); x = np.arange(1, k + 1)
    ax.plot(x, s["switch"][:k] * 100, color=POS, lw=2.6, label="đổi cửa")
    ax.plot(x, s["stay"][:k] * 100, color=NEG, lw=2.6, label="giữ cửa")
    ax.axhline(100 / 3, color=MUT, lw=1, ls="--"); ax.axhline(200 / 3, color=MUT, lw=1, ls="--")
    ax.set_xscale("log"); ax.set_xlim(1, n); ax.set_ylim(0, 100)
    ax.set_xlabel("số ván (log)"); ax.set_ylabel("tỷ lệ thắng %")
    _legend(ax, "lower right")


def surface_monty_hall(s, v):
    lines = []
    for i, d in enumerate([3, 4, 5, 10]):
        x = np.arange(1, 41)
        rng = np.random.default_rng(d)
        car = rng.integers(0, d, 40); pick = rng.integers(0, d, 40)
        # host opens all but one other door → switching wins when first pick was wrong
        z = np.cumsum(car != pick) / x * 100
        lines.append((x, np.full(len(x), i), z, [POS, ACC, NEU, NEG][i]))
    return {"lines": lines, "xl": "ván", "yl": "", "zl": "thắng khi đổi %", "yticks": ["3 cửa", "4 cửa", "5 cửa", "10 cửa"]}


# =============================================================== Iterated prisoner's dilemma
def prisoners_demo(seed=0, rounds=200):
    P = {(1, 1): 3, (1, 0): 0, (0, 1): 5, (0, 0): 1}
    S = {  # 1 = hợp tác, 0 = phản bội
        "luôn hợp tác": lambda op: 1,
        "luôn phản bội": lambda op: 0,
        "ăn miếng trả miếng": lambda o: (o or [1])[-1],
        "thù dai": lambda op: int(0 not in op),
    }
    score = {k: 0 for k in S}
    for a, b in [(a, b) for a in S for b in S]:
        ha, hb = [], []
        for _ in range(rounds):
            x, y = S[a](hb), S[b](ha)
            ha.append(x); hb.append(y)
            score[a] += P[(x, y)]
    return score, rounds


def compute_prisoners(seed=0, returns=None):
    score, rounds = prisoners_demo()
    names = list(score)
    best = max(score, key=score.get)
    values = {"rounds": rounds, "s_coop": score[names[0]], "s_defect": score[names[1]], "s_tft": score[names[2]],
              "s_grudge": score[names[3]], "pay_cc": 3, "pay_dc": 5, "pay_dd": 1, "pay_cd": 0,
              "tft_vs_defect": float(score[names[2]] / score[names[1]]), "best": best}
    formats = {k: "int" for k in values}; formats["tft_vs_defect"] = "x2"
    return values, formats, {"score": score}


def plot2d_prisoners(ax, s, upto=1.0):
    names = list(s["score"]); vals = np.array([s["score"][k] for k in names], float)
    a = min(1.0, upto * 1.3)
    cols = [POS, NEG, ACC, NEU]
    ax.barh(range(len(names)), vals * a, color=cols, height=0.6)
    ax.set_yticks([])
    for i, nm in enumerate(names):
        ax.text(vals.max() * 0.02, i, nm, va="center", color="#080d0b", fontsize=20, weight="bold")
    ax.set_xlim(0, vals.max() * 1.15); ax.invert_yaxis(); ax.set_xlabel("tổng điểm cả giải")
    for i, v in enumerate(vals * a):
        if a >= 1:
            ax.text(v + vals.max() * 0.02, i, f"{int(v):,}".replace(",", "."), va="center", color=TXT, fontsize=18)


def surface_prisoners(s, v):
    p = np.linspace(0, 1, 40); q = np.linspace(0, 1, 40)
    Pm, Q = np.meshgrid(p, q)   # P(me cooperate), P(opponent cooperate)
    Z = Pm * Q * 3 + Pm * (1 - Q) * 0 + (1 - Pm) * Q * 5 + (1 - Pm) * (1 - Q) * 1
    return {"X": Pm * 100, "Y": Q * 100, "Z": Z, "xl": "mình hợp tác %", "yl": "đối thủ hợp tác %", "zl": "điểm kỳ vọng"}


# =============================================================== Nash mixed strategy: penalty kick
def penalty_demo(seed=0):
    # xác suất ghi bàn: [hướng sút][hướng thủ môn bay]
    G = np.array([[0.58, 0.95],    # sút trái
                  [0.93, 0.70]])   # sút phải
    # chọn p (sút trái) để thủ môn bay đâu cũng như nhau
    d = G[0, 0] - G[1, 0] - G[0, 1] + G[1, 1]
    p = (G[1, 1] - G[1, 0]) / d
    q = (G[1, 1] - G[0, 1]) / d
    v = p * G[0, 0] + (1 - p) * G[1, 0]
    return G, p, q, v


def compute_penalty(seed=0, returns=None):
    G, p, q, v = penalty_demo()
    values = {"p_left": float(p), "p_right": float(1 - p), "q_left": float(q), "score_eq": float(v),
              "ll": G[0, 0], "lr": G[0, 1], "rl": G[1, 0], "rr": G[1, 1],
              "score_always_left": float(min(G[0])), "score_always_right": float(min(G[1])),
              "gain_vs_pure": float(v - max(min(G[0]), min(G[1])))}
    formats = {k: "pct0" for k in values}
    return values, formats, {"G": G, "p": p, "v": v}


def plot2d_penalty(ax, s, upto=1.0):
    G = s["G"]; p = np.linspace(0, 1, 101); k = max(2, int(101 * upto))
    keeper_l = p * G[0, 0] + (1 - p) * G[1, 0]
    keeper_r = p * G[0, 1] + (1 - p) * G[1, 1]
    ax.plot(p[:k] * 100, keeper_l[:k] * 100, color=NEG, lw=2.6, label="thủ môn bay trái")
    ax.plot(p[:k] * 100, keeper_r[:k] * 100, color=POS, lw=2.6, label="thủ môn bay phải")
    worst = np.minimum(keeper_l, keeper_r)
    ax.fill_between(p[:k] * 100, 50, worst[:k] * 100, color=ACC, alpha=0.15)
    if upto >= 0.99:
        ax.scatter([s["p"] * 100], [s["v"] * 100], color=ACC, s=160, zorder=5)
    ax.set_xlim(0, 100); ax.set_ylim(50, 100)
    ax.set_xlabel("tỷ lệ sút trái %"); ax.set_ylabel("xác suất ghi bàn %")
    _legend(ax, "lower center")


def surface_penalty(s, v):
    G = s["G"]; p = np.linspace(0, 1, 40); q = np.linspace(0, 1, 40)
    P, Q = np.meshgrid(p, q)
    Z = P * Q * G[0, 0] + P * (1 - Q) * G[0, 1] + (1 - P) * Q * G[1, 0] + (1 - P) * (1 - Q) * G[1, 1]
    return {"X": P * 100, "Y": Q * 100, "Z": Z * 100, "xl": "sút trái %", "yl": "thủ môn bay trái %", "zl": "ghi bàn %"}


# =============================================================== Poker: pot odds & outs
def pot_odds_demo(seed=6, trials=200000):
    rng = np.random.default_rng(seed)
    outs = 9               # chờ thùng: 9 lá
    one = outs / 46                  # còn 1 lá (river)
    draws = rng.random((trials, 2))
    two = np.mean((draws[:, 0] < outs/47) |
                  (draws[:, 1] < outs/46))
    def need(bet, pot):    # equity cần để theo
        return bet / (pot + 2 * bet)
    return one, two, need(50, 100), need(100, 100), need


def compute_pot_odds(seed=6, returns=None):
    one, two, half, full, need = pot_odds_demo(seed)
    values = {"outs": 9, "eq_one": one, "eq_two": float(two), "need_half": half, "need_pot": full,
              "need_double": need(200, 100), "ev_call_half": one * 250 - 50, "ev_call_pot": one * 300 - 100,
              "rule_4": 9 * 4 / 100, "rule_2": 9 * 2 / 100}
    formats = {"outs": "int", "eq_one": "pct0", "eq_two": "pct0", "need_half": "pct0", "need_pot": "pct0",
               "need_double": "pct0", "ev_call_half": "num0", "ev_call_pot": "num0", "rule_4": "pct0", "rule_2": "pct0"}
    return values, formats, {"one": one}


def plot2d_pot_odds(ax, s, upto=1.0):
    b = np.linspace(0.1, 2.0, 100); k = max(2, int(100 * upto))
    need = b / (1 + 2 * b)
    ax.plot(b[:k] * 100, need[:k] * 100, color=ACC, lw=3, label="equity cần để theo")
    ax.axhline(s["one"] * 100, color=POS, lw=2.4, ls="--", label="equity khi chờ thùng (1 lá)")
    ax.fill_between(b[:k] * 100, s["one"] * 100, need[:k] * 100, where=need[:k] > s["one"], color=NEG, alpha=0.18)
    ax.set_xlim(10, 200); ax.set_ylim(0, 45)
    ax.set_xlabel("cược của đối thủ, % pot"); ax.set_ylabel("equity %")
    _legend(ax, "lower right")


def surface_pot_odds(s, v):
    e = np.linspace(0.05, 0.6, 40); b = np.linspace(0.1, 2.0, 40)
    E, B = np.meshgrid(e, b)
    Z = E * (1 + 2 * B) - B       # EV of calling, in pots
    return {"X": E * 100, "Y": B * 100, "Z": Z * 100, "xl": "equity %", "yl": "cược % pot", "zl": "EV khi theo, % pot"}


# =============================================================== Poker variance: winners lose for months
def poker_variance_demo(seed=8, players=1000,
                        blocks=500):
    rng = np.random.default_rng(seed)
    win, sd = 5.0, 100.0  # bb/100 tay: CÓ lợi thế
    steps = rng.normal(win, sd, (players, blocks))
    bank = steps.cumsum(axis=1)  # 1 bước = 100 tay
    peak = np.maximum.accumulate(bank, axis=1)
    dd = (peak - bank).max(axis=1)  # downswing
    lose_20k = np.mean(bank[:, 199] < 0)
    return bank, dd, lose_20k, win, sd


def compute_poker_variance(seed=8, returns=None):
    bank, dd, lose, win, sd = poker_variance_demo(seed)
    blocks = bank.shape[1]
    lose_50k = float(np.mean(bank[:, -1] < 0))
    values = {"winrate": win, "sd": sd, "players": bank.shape[0], "hands": blocks * 100, "hands_20k": 20000,
              "lose_20k": float(lose), "lose_50k": lose_50k, "dd_median": float(np.median(dd)),
              "dd_p90": float(np.percentile(dd, 90)), "ev_50k": win * blocks}
    formats = {"winrate": "num0", "sd": "num0", "players": "int", "hands": "int", "hands_20k": "int",
               "lose_20k": "pct0", "lose_50k": "pct0", "dd_median": "int", "dd_p90": "int", "ev_50k": "int"}
    return values, formats, {"bank": bank, "win": win}


def plot2d_poker_variance(ax, s, upto=1.0):
    b = s["bank"][:60]; n = b.shape[1]; k = max(2, int(n * upto)); x = np.arange(k) * 100
    for row in b:
        ax.plot(x, row[:k], color=MUT, lw=0.8, alpha=0.45)
    ax.plot(x, (np.arange(k) + 1) * s["win"], color=ACC, lw=3, label="kỳ vọng (EV)")
    ax.axhline(0, color=NEG, lw=1.4)
    ax.set_xlim(0, n * 100); ax.set_ylim(b.min() * 1.05, b.max() * 1.05)
    ax.set_xlabel("số tay"); ax.set_ylabel("lãi/lỗ (big blind)")
    _legend(ax)


def surface_poker_variance(s, v):
    wr = np.linspace(1, 10, 30); hands = np.linspace(1000, 100000, 30)
    W, Hh = np.meshgrid(wr, hands)
    from math import erf
    z = -(W * Hh / 100) / (100 * np.sqrt(Hh / 100))
    Z = 0.5 * (1 + np.vectorize(erf)(z / math.sqrt(2)))
    return {"X": W, "Y": Hh / 1000, "Z": Z * 100, "xl": "winrate bb/100", "yl": "nghìn tay", "zl": "xác suất đang lỗ %"}


# =============================================================== Bluff ratio & MDF (GTO)
def bluff_demo(seed=0):
    def bluff_share(bet, pot):     # tỷ lệ bluff tối ưu
        return bet / (pot + 2 * bet)
    def mdf(bet, pot):     # phải theo ít nhất
        return pot / (pot + bet)
    sizes = [0.33, 0.5, 1.0, 2.0]  # cược theo pot
    return ({b: bluff_share(b, 1) for b in sizes},
            {b: mdf(b, 1) for b in sizes})


def compute_bluff(seed=0, returns=None):
    bl, md = bluff_demo()
    values = {"bluff_third": bl[0.33], "bluff_half": bl[0.5], "bluff_pot": bl[1.0], "bluff_2x": bl[2.0],
              "mdf_third": md[0.33], "mdf_half": md[0.5], "mdf_pot": md[1.0], "mdf_2x": md[2.0],
              "fold_pot": 1 - md[1.0], "value_pot": 1 - bl[1.0]}
    formats = {k: "pct0" for k in values}
    return values, formats, {}


def plot2d_bluff(ax, s, upto=1.0):
    b = np.linspace(0.1, 3, 100); k = max(2, int(100 * upto))
    ax.plot(b[:k] * 100, (b / (1 + 2 * b))[:k] * 100, color=NEG, lw=3, label="tỷ lệ bluff tối ưu")
    ax.plot(b[:k] * 100, (1 / (1 + b))[:k] * 100, color=POS, lw=3, label="MDF: phải theo ít nhất")
    ax.set_xlim(10, 300); ax.set_ylim(0, 100)
    ax.set_xlabel("cỡ cược, % pot"); ax.set_ylabel("%")
    _legend(ax, "center right")


def surface_bluff(s, v):
    b = np.linspace(0.2, 2.0, 40); f = np.linspace(0, 1, 40)
    B, Fq = np.meshgrid(b, f)
    Z = Fq * 1 - (1 - Fq) * B      # EV of a pure bluff, in pots, given opponent fold frequency
    return {"X": B * 100, "Y": Fq * 100, "Z": Z * 100, "xl": "cỡ cược % pot", "yl": "đối thủ bỏ bài %", "zl": "EV bluff, % pot"}


# =============================================================== Loss aversion (prospect theory)
def loss_aversion_demo(seed=0):
    a, lam = 0.88, 2.25    # Tversky & Kahneman (1992)
    def v(x):              # giá trị cảm nhận
        x = np.asarray(x, float); m = np.abs(x)
        return np.where(x >= 0, m**a, -lam * m**a)
    gain, loss = v(100), v(-100)
    # thắng bao nhiêu mới chịu tung đồng xu thua 100?
    need = (lam * 100**a) ** (1 / a)
    return v, float(gain), float(loss), need, lam


def compute_loss_aversion(seed=0, returns=None):
    v, g, l, need, lam = loss_aversion_demo()
    values = {"alpha": 0.88, "lam": lam, "v_gain": g, "v_loss": l, "pain_ratio": -l / g, "need_win": need,
              "stake": 100, "need_ratio": need / 100}
    formats = {"alpha": "num2", "lam": "num2", "v_gain": "num0", "v_loss": "num0", "pain_ratio": "x2",
               "need_win": "num0", "stake": "int", "need_ratio": "x1"}
    return values, formats, {"v": v}


def plot2d_loss_aversion(ax, s, upto=1.0):
    x = np.linspace(-200, 200, 401); k = max(2, int(401 * upto)); y = s["v"](x)
    ax.axhline(0, color=MUT, lw=1); ax.axvline(0, color=MUT, lw=1)
    ax.plot(x[:k], y[:k], color=ACC, lw=3.2)
    ax.plot(x[:k], np.where(x[:k] < 0, x[:k] * 100 ** 0.12, np.nan), color=MUT, lw=1.2, ls="--")
    ax.set_xlim(-200, 200); ax.set_ylim(y.min() * 1.05, y.max() * 1.6)
    ax.set_xlabel("lãi / lỗ thực tế"); ax.set_ylabel("cảm giác")


def surface_loss_aversion(s, v):
    x = np.linspace(-200, 200, 60); lam = np.linspace(1, 3, 30)
    X, L = np.meshgrid(x, lam)
    Z = np.where(X >= 0, np.abs(X) ** 0.88, -L * np.abs(X) ** 0.88)
    return {"X": X, "Y": L, "Z": Z, "xl": "lãi / lỗ thực tế", "yl": "hệ số sợ lỗ λ", "zl": "cảm giác"}


# =============================================================== Survivorship bias
def survivorship_demo(seed=11, funds=10000, years=10):
    rng = np.random.default_rng(seed)
    # quỹ KHÔNG kỹ năng: 50/50 thắng thị trường
    beat = rng.random((funds, years)) < 0.5
    alive = np.cumprod(beat, axis=1).astype(bool)
    left = alive.sum(axis=0)  # thua 1 năm: đóng
    ret = rng.normal(0.0, 0.2, (funds, years))
    ret = np.where(beat, np.abs(ret), -np.abs(ret))
    return beat, alive, left, ret


def compute_survivorship(seed=11, returns=None):
    beat, alive, left, ret = survivorship_demo(seed)
    surv = alive[:, -1]
    values = {"funds": beat.shape[0], "years": beat.shape[1], "survivors": int(left[-1]),
              "after5": int(left[4]), "surv_avg": float(ret[surv].mean()), "all_avg": float(ret.mean()),
              "p_one": 0.5 ** beat.shape[1], "dead": int(beat.shape[0] - left[-1])}
    formats = {"funds": "int", "years": "int", "survivors": "int", "after5": "int", "surv_avg": "pct1",
               "all_avg": "pct1", "p_one": "pct2", "dead": "int"}
    return values, formats, {"left": left, "funds": beat.shape[0]}


def plot2d_survivorship(ax, s, upto=1.0):
    left = np.concatenate([[s["funds"]], s["left"]]); n = len(left); k = max(1, int(round(n * upto)))
    x = np.arange(n)
    ax.bar(x[:k], left[:k], color=[ACC if i == n - 1 else MUT for i in range(k)], width=0.7)
    ax.set_yscale("log"); ax.set_xlim(-0.6, n - 0.4); ax.set_ylim(1, s["funds"] * 2)
    ax.set_xlabel("năm"); ax.set_ylabel("số quỹ còn sống (log)")


def surface_survivorship(s, v):
    lines = []
    left = np.concatenate([[s["funds"]], s["left"]]).astype(float)
    x = np.arange(len(left))
    lines.append((x, np.zeros(len(x)), np.log10(left), ACC))
    lines.append((x, np.ones(len(x)), np.log10(s["funds"] - left + 1), NEG))
    return {"lines": lines, "xl": "năm", "yl": "", "zl": "log10 số quỹ", "yticks": ["còn sống", "đã đóng"]}


# =============================================================== Regression to the mean
def regression_mean_demo(seed=5, n=2000):
    rng = np.random.default_rng(seed)
    skill = rng.normal(0, 0.03, n)        # lợi thế thật
    y1 = skill + rng.normal(0, 0.12, n)  # + may
    y2 = skill + rng.normal(0, 0.12, n)  # may mới
    top = y1 >= np.quantile(y1, 0.9)
    return y1, y2, top, np.corrcoef(y1, y2)[0, 1]


def compute_regression_mean(seed=5, returns=None):
    y1, y2, top, rho = regression_mean_demo(seed)
    values = {"n": len(y1), "top_y1": float(y1[top].mean()), "top_y2": float(y2[top].mean()), "corr": float(rho),
              "kept": float(y2[top].mean() / y1[top].mean()), "luck_share": 0.12 ** 2 / (0.12 ** 2 + 0.03 ** 2),
              "top_rank2": float(np.mean(y2[top] >= np.quantile(y2, 0.9)))}
    formats = {"n": "int", "top_y1": "pct1", "top_y2": "pct1", "corr": "num2", "kept": "pct0", "luck_share": "pct0",
               "top_rank2": "pct0"}
    return values, formats, {"y1": y1, "y2": y2, "top": top}


def plot2d_regression_mean(ax, s, upto=1.0):
    y1, y2, top = s["y1"] * 100, s["y2"] * 100, s["top"]
    k = max(2, int(len(y1) * upto))
    ax.scatter(y1[:k][~top[:k]], y2[:k][~top[:k]], s=8, color=MUT, alpha=0.5)
    ax.scatter(y1[:k][top[:k]], y2[:k][top[:k]], s=14, color=ACC)
    lim = 45
    ax.plot([-lim, lim], [-lim, lim], color=MUT, ls="--", lw=1)
    b = np.polyfit(y1, y2, 1)
    ax.plot([-lim, lim], np.polyval(b, [-lim, lim]), color=POS, lw=2.4)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel("lợi nhuận năm 1 %"); ax.set_ylabel("lợi nhuận năm 2 %")


def surface_regression_mean(s, v):
    sk = np.linspace(0.05, 0.95, 30); pct = np.linspace(0.5, 0.99, 30)
    SK, PC = np.meshgrid(sk, pct)
    from statistics import NormalDist
    zq = np.vectorize(NormalDist().inv_cdf)(PC)
    Z = np.vectorize(NormalDist().cdf)(zq * SK)   # expected next-year percentile ≈ Φ(ρ·z)
    return {"X": SK * 100, "Y": PC * 100, "Z": Z * 100, "xl": "phần kỹ năng %", "yl": "hạng năm 1 %", "zl": "hạng năm 2 %"}


# =============================================================== Streaks / hot hand
def streaks_demo(seed=4, people=20000, flips=100):
    rng = np.random.default_rng(seed)
    x = rng.random((people, flips)) < 0.5
    best = np.zeros(people, int)
    run = np.zeros(people, int)
    prev = np.zeros(people, bool)
    for t in range(flips):
        run = np.where(x[:, t] == prev, run + 1, 1)
        prev = x[:, t]
        best = np.maximum(best, run)
    return best, x


def compute_streaks(seed=4, returns=None):
    best, x = streaks_demo(seed)
    values = {"people": len(best), "flips": x.shape[1], "median_best": float(np.median(best)),
              "p6": float(np.mean(best >= 6)), "p8": float(np.mean(best >= 8)), "p4": float(np.mean(best >= 4)),
              "max_seen": int(best.max())}
    formats = {"people": "int", "flips": "int", "median_best": "int", "p6": "pct0", "p8": "pct0", "p4": "pct0",
               "max_seen": "int"}
    return values, formats, {"best": best, "x": x}


def plot2d_streaks(ax, s, upto=1.0):
    b = s["best"]; ks = np.arange(2, 16); cnt = np.array([np.mean(b == k) for k in ks]) * 100
    a = min(1.0, upto * 1.3)
    ax.bar(ks, cnt * a, color=[ACC if k >= 6 else MUT for k in ks], width=0.75)
    ax.set_xlim(1.4, 15.6); ax.set_ylim(0, cnt.max() * 1.2)
    ax.set_xlabel("chuỗi sấp/ngửa dài nhất trong 100 lần tung"); ax.set_ylabel("% số người")


def surface_streaks(s, v):
    n = np.arange(20, 201, 10); k = np.arange(3, 13)
    N, K = np.meshgrid(n, k)
    Z = 1 - np.exp(-(N - K + 1) / 2 ** K)       # Poisson approx of P(longest run ≥ k)
    return {"X": N, "Y": K, "Z": Z * 100, "xl": "số lần tung", "yl": "độ dài chuỗi", "zl": "xác suất gặp %"}


# =============================================================== Keynes beauty contest (guess 2/3 of the average)
def beauty_demo(seed=7, n=1000):
    rng = np.random.default_rng(seed)
    lv = [50 * (2/3)**k for k in range(6)]  # cấp
    share = [0.25, 0.35, 0.25, 0.1, 0.04, 0.01]
    level = rng.choice(6, n, p=share)
    guess = np.clip(np.array(lv)[level]
                    + rng.normal(0, 4, n), 0, 100)
    target = 2/3 * guess.mean()
    win = guess[np.argmin(abs(guess - target))]
    return lv, guess, target, win


def compute_beauty(seed=7, returns=None):
    lv, guess, target, win = beauty_demo(seed)
    values = {"l0": lv[0], "l1": lv[1], "l2": lv[2], "l3": lv[3], "target": float(target), "winner": float(win),
              "avg": float(guess.mean()), "nash": 0, "n": len(guess)}
    formats = {k: "num0" for k in values}; formats["n"] = "int"
    return values, formats, {"lv": lv, "guess": guess, "target": target}


def plot2d_beauty(ax, s, upto=1.0):
    g = s["guess"]; k = max(2, int(len(g) * upto))
    ax.hist(g[:k], bins=np.arange(0, 70, 2), color=MUT)
    for i, l in enumerate(s["lv"][:4]):
        ax.axvline(l, color=NEU, lw=1, ls="--")
    if upto >= 0.99:
        ax.axvline(s["target"], color=ACC, lw=3.5)
    ax.set_xlim(0, 70); ax.set_ylim(0, 260)
    ax.set_xlabel("con số được đoán"); ax.set_ylabel("số người")


def surface_beauty(s, v):
    a = np.linspace(0, 1, 30); b = np.linspace(0, 1, 30)
    A, B = np.meshgrid(a, b)   # share of level-0 players, share of level-1 players (rest level-2)
    C = np.clip(1 - A - B, 0, 1)
    tot = A + B + C
    avg = (A * 50 + B * 50 * 2 / 3 + C * 50 * 4 / 9) / tot
    return {"X": A * 100, "Y": B * 100, "Z": 2 / 3 * avg, "xl": "% đoán bừa (cấp 0)", "yl": "% nghĩ 1 bước", "zl": "con số thắng"}


# =============================================================== Volatility drag
def vol_drag_demo(seed=10, years=30):
    rng = np.random.default_rng(seed)
    up_down = (1.5 * 0.5) - 1      # +50% rồi −50%
    need = lambda loss: 1 / (1 - loss) - 1
    mu, sig = 0.08, 0.35  # lợi suất TB, biến động
    r = rng.normal(mu, sig, (20000, years))
    wealth = np.prod(1 + r, axis=1)
    geo = np.median(wealth) ** (1 / years) - 1
    return up_down, need(0.5), mu, sig, geo, wealth


def compute_vol_drag(seed=10, returns=None):
    ud, need50, mu, sig, geo, wealth = vol_drag_demo(seed)
    values = {"up_down": ud, "need50": need50, "need30": 1 / 0.7 - 1, "need20": 1 / 0.8 - 1, "mu": mu, "sig": sig,
              "geo": float(geo), "drag": float(mu - geo), "theory_geo": mu - sig ** 2 / 2, "years": 30,
              "p_lose": float(np.mean(wealth < 1))}
    formats = {"up_down": "pct0", "need50": "pct0", "need30": "pct0", "need20": "pct0", "mu": "pct0", "sig": "pct0",
               "geo": "pct1", "drag": "pct1", "theory_geo": "pct1", "years": "int", "p_lose": "pct0"}
    return values, formats, {}


def plot2d_vol_drag(ax, s, upto=1.0):
    l = np.linspace(0, 0.9, 200); k = max(2, int(200 * upto))
    ax.plot(l[:k] * 100, (1 / (1 - l[:k]) - 1) * 100, color=NEG, lw=3, label="phải lãi lại")
    ax.plot(l[:k] * 100, l[:k] * 100, color=MUT, lw=1.6, ls="--", label="mức đã lỗ")
    ax.set_xlim(0, 90); ax.set_ylim(0, 400)
    ax.set_xlabel("mức lỗ %"); ax.set_ylabel("cần lãi bao nhiêu để hoà %")
    _legend(ax)


def surface_vol_drag(s, v):
    mu = np.linspace(0, 0.15, 30); sg = np.linspace(0.05, 0.6, 30)
    M, SG = np.meshgrid(mu, sg)
    return {"X": M * 100, "Y": SG * 100, "Z": np.exp((M - SG ** 2 / 2) * 30), "xl": "lợi suất TB %/năm",
            "yl": "biến động %/năm", "zl": "tài sản sau 30 năm (lần)"}


# =============================================================== Base-rate fallacy (Bayes)
def base_rate_demo(seed=12, n=100000):
    rng = np.random.default_rng(seed)
    crash = rng.random(n) < 0.02  # sự kiện hiếm
    acc = 0.9                     # độ chính xác
    alarm = np.where(crash, rng.random(n) < acc,
                     rng.random(n) < 1 - acc)
    hit = (crash & alarm).sum() / alarm.sum()
    exact = 0.02*acc / (0.02*acc + 0.98*(1-acc))
    return hit, exact, crash, alarm


def compute_base_rate(seed=12, returns=None):
    hit, exact, crash, alarm = base_rate_demo(seed)
    per1000_alarm = 1000 * (0.02 * 0.9 + 0.98 * 0.1)
    values = {"base": 0.02, "acc": 0.9, "hit_sim": float(hit), "hit_exact": exact, "false_share": 1 - exact,
              "n": len(crash), "alarms_1000": per1000_alarm, "true_1000": 1000 * 0.02 * 0.9,
              "false_1000": 1000 * 0.98 * 0.1}
    formats = {"base": "pct0", "acc": "pct0", "hit_sim": "pct0", "hit_exact": "pct0", "false_share": "pct0",
               "n": "int", "alarms_1000": "int", "true_1000": "int", "false_1000": "int"}
    return values, formats, {}


def plot2d_base_rate(ax, s, upto=1.0):
    acc = np.linspace(0.5, 0.999, 200); k = max(2, int(200 * upto))
    for b, c, lab in ((0.01, NEG, "sự kiện 1%"), (0.02, ACC, "sự kiện 2%"), (0.1, POS, "sự kiện 10%")):
        post = b * acc / (b * acc + (1 - b) * (1 - acc))
        ax.plot(acc[:k] * 100, post[:k] * 100, color=c, lw=2.8, label=lab)
    ax.set_xlim(50, 100); ax.set_ylim(0, 100)
    ax.set_xlabel("độ chính xác tín hiệu %"); ax.set_ylabel("báo động là thật %")
    _legend(ax)


def surface_base_rate(s, v):
    b = np.linspace(0.005, 0.3, 40); a = np.linspace(0.6, 0.99, 40)
    B, A = np.meshgrid(b, a)
    Z = B * A / (B * A + (1 - B) * (1 - A))
    return {"X": B * 100, "Y": A * 100, "Z": Z * 100, "xl": "tần suất thật %", "yl": "độ chính xác %", "zl": "báo động đúng %"}


# =============================================================== Winner's curse
def winners_curse_demo(seed=14, auctions=20000):
    rng = np.random.default_rng(seed)
    value = 100.0                        # giá trị thật
    over = {}
    for n in (2, 5, 10, 20):    # số người đấu giá
        est = value + rng.normal(0, 20, (auctions, n))
        over[n] = est.max(axis=1).mean() - value
    return over, value


def compute_winners_curse(seed=14, returns=None):
    over, value = winners_curse_demo(seed)
    values = {"value": value, "noise": 20, "over2": over[2], "over5": over[5], "over10": over[10], "over20": over[20],
              "over10_pct": over[10] / value}
    formats = {k: "num0" for k in values}; formats["over10_pct"] = "pct0"
    return values, formats, {"over": over}


def plot2d_winners_curse(ax, s, upto=1.0):
    ns = np.arange(1, 31); rng = np.random.default_rng(1)
    o = [(100 + rng.normal(0, 20, (4000, n))).max(axis=1).mean() - 100 for n in ns]
    k = max(2, int(30 * upto))
    ax.plot(ns[:k], o[:k], color=NEG, lw=3, marker="o", ms=6)
    ax.axhline(0, color=MUT, lw=1)
    ax.set_xlim(1, 30); ax.set_ylim(-3, 50)
    ax.set_xlabel("số người cùng đấu giá"); ax.set_ylabel("người thắng trả dư (đơn vị)")


def surface_winners_curse(s, v):
    ns = np.arange(1, 21); sd = np.linspace(5, 40, 20)
    N, SD = np.meshgrid(ns, sd)
    # expected max of n standard normals (Blom approximation)
    from statistics import NormalDist
    em = np.array([NormalDist().inv_cdf((n - 0.375) / (n + 0.25)) for n in ns])
    Z = SD * em[None, :]
    return {"X": N, "Y": SD, "Z": Z, "xl": "số người đấu giá", "yl": "độ nhiễu ước lượng", "zl": "trả dư"}


# =============================================================== Overtrading: fees eat edge
def overtrading_demo(seed=15, days=250):
    rng = np.random.default_rng(seed)
    fee = 0.0015 + 0.0015 + 0.001  # mua+bán+thuế
    r = rng.normal(0.0003, 0.015, days)  # 1 danh mục
    out = {}
    for trades in (0, 2, 8, 20):  # vòng/tháng
        cost = fee * trades * 12 / days
        out[trades] = np.prod(1 + r - cost) - 1
    return out, fee, r


def compute_overtrading(seed=15, returns=None):
    out, fee, r = overtrading_demo(seed)
    values = {"fee_round": fee, "ret0": float(out[0]), "ret2": float(out[2]), "ret8": float(out[8]),
              "ret20": float(out[20]), "cost20": float(fee * 20 * 12), "cost8": float(fee * 8 * 12),
              "trades_year20": 240, "days": 250}
    formats = {"fee_round": "pct2", "ret0": "pct1", "ret2": "pct1", "ret8": "pct1", "ret20": "pct1", "cost20": "pct0",
               "cost8": "pct0", "trades_year20": "int", "days": "int"}
    return values, formats, {"r": r, "fee": fee}


def plot2d_overtrading(ax, s, upto=1.0):
    r = s["r"]; n = len(r); k = max(2, int(n * upto)); x = np.arange(k)
    for tr, c, lab in ((0, POS, "giữ nguyên"), (2, MUT, "2 vòng/tháng"), (8, NEU, "8 vòng/tháng"), (20, NEG, "20 vòng/tháng")):
        w = np.cumprod(1 + r - s["fee"] * tr * 12 / n)
        ax.plot(x, (w[:k] - 1) * 100, color=c, lw=2.4, label=lab)
    ax.axhline(0, color=MUT, lw=1)
    ax.set_xlim(0, n); ax.set_ylim(-70, 40); ax.set_xlabel("phiên"); ax.set_ylabel("lãi/lỗ cộng dồn %")
    _legend(ax, "lower left")


def surface_overtrading(s, v):
    t = np.linspace(0, 20, 30); f = np.linspace(0.001, 0.005, 30)
    T, Fe = np.meshgrid(t, f)
    return {"X": T, "Y": Fe * 100, "Z": -T * 12 * Fe * 100, "xl": "vòng giao dịch/tháng", "yl": "phí 1 vòng %",
            "zl": "phí ăn mất %/năm"}


MIND_TOPICS = ["martingale", "gambler_ruin", "monty_hall", "prisoners", "penalty", "pot_odds", "poker_variance",
               "bluff", "loss_aversion", "survivorship", "regression_mean", "streaks", "beauty", "vol_drag",
               "base_rate", "winners_curse", "overtrading"]
