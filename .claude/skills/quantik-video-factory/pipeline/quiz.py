"""Quiz hook mở đầu: một câu đố toán / xác suất dễ hiểu, gây tò mò, đặt TRƯỚC nội dung chính.

Mỗi câu đố là một hàm tự TÍNH đáp án (công thức chính xác + mô phỏng kiểm chứng), nên số trên màn hình
có nguồn là code, giống placeholder {key}. Không gõ tay số đáp án.

Cấu trúc 3 nhịp (~7-9 s):
  1. quiz_question: câu hỏi + hai lựa chọn A/B, thanh đếm ngược "Đoán đi!"
  2. quiz_answer:   lật đáp án đúng + một câu giải thích trực giác
  3. (bridge)       câu nối sang chủ đề chính, ví dụ "Rủi ro cổ phiếu cũng ngược trực giác như vậy"

Dùng:
  episode JSON:  "quiz": "birthday"  |  "quiz": "auto" (mặc định)  |  "quiz": "off"
                 "quiz_bridge": "câu nối riêng"
  CLI:           python batch.py ... --quiz coin_streak
  Liệt kê:       python quiz.py
"""
from __future__ import annotations

import math
import random
import zlib

import frames as F
from core import SAFE, THEME as T, fmt_vi
from render import Scene

X0, X1 = SAFE["left"], SAFE["right"]


def _pct(x, d=0):
    return fmt_vi(x, f"pct{d}")


# ------------------------------------------------------------------ bank: mỗi hàm trả dict đã tính số
def birthday():
    n = 23
    p = 1 - math.prod((365 - i) / 365 for i in range(n))
    return dict(q=f"Phòng có {n} người.\nKhả năng có 2 người trùng sinh nhật?",
                a=f"Khoảng {_pct(p)}", b="Dưới 10%", correct="a",
                why="Không so bạn với từng người, mà so mọi cặp với nhau: có tới 253 cặp.",
                say=f"Phòng có {n} người. Khả năng có hai người trùng sinh nhật là bao nhiêu?",
                nums=[str(n), _pct(p), "10%", "253"], topics=["monte_carlo", "var_cvar"])


def coin_streak():
    # P(có ít nhất một chuỗi 5 mặt ngửa liên tiếp trong 50 lần tung) — DP chính xác
    n, k = 50, 5
    st = [1.0] + [0.0] * (k - 1)  # st[j] = xác suất đang có chuỗi j ngửa, chưa từng đạt k
    for _ in range(n):
        new = [0.0] * k
        for j, v in enumerate(st):
            new[0] += v / 2
            if j + 1 < k:
                new[j + 1] += v / 2
        st = new
    p = 1 - sum(st)
    return dict(q=f"Tung đồng xu {n} lần.\nCó chuỗi {k} lần ngửa liên tiếp không?",
                a=f"Có, khoảng {_pct(p)}", b="Hiếm, dưới 20%", correct="a",
                why="Ngẫu nhiên thật lại hay tạo chuỗi dài. Chuỗi tăng giá chưa chắc là xu hướng.",
                say=f"Tung đồng xu {n} lần. Khả năng có chuỗi {k} lần ngửa liên tiếp là bao nhiêu?",
                nums=[str(n), str(k), _pct(p), "20%"], topics=["hurst", "hmm", "ou"])


def loss_recovery():
    loss = 0.5
    need = 1 / (1 - loss) - 1
    return dict(q=f"Tài khoản giảm {_pct(loss)}.\nCần tăng bao nhiêu để về vốn?",
                a=f"{_pct(loss)}", b=f"{_pct(need)}", correct="b",
                why="Giảm tính trên số vốn lớn, tăng lại tính trên số vốn đã nhỏ đi.",
                say=f"Tài khoản giảm {_pct(loss)}. Cần tăng bao nhiêu phần trăm để về lại vốn?",
                nums=[_pct(loss), _pct(need)], topics=["kelly", "sharpe", "var_cvar", "max_drawdown"])


def up_down():
    up = 0.2
    end = (1 + up) * (1 - up) - 1
    return dict(q=f"Tăng {_pct(up)} rồi giảm {_pct(up)}.\nVề lại vốn hay lỗ?",
                a="Về đúng vốn", b=f"Lỗ {_pct(-end)}", correct="b",
                why="Biến động tự nó ăn mòn tài sản: lên xuống bằng nhau vẫn lỗ.",
                say=f"Tăng {_pct(up)} rồi giảm {_pct(up)}. Về lại vốn, hay bị lỗ?",
                nums=[_pct(up), _pct(-end)], topics=["garch", "sharpe", "variance", "kelly"])


def monty_hall():
    rnd = random.Random(7)
    wins = 0
    trials = 20000
    for _ in range(trials):
        car, pick = rnd.randrange(3), rnd.randrange(3)
        wins += car != pick  # đổi cửa thắng khi lần chọn đầu sai
    p = wins / trials
    return dict(q="3 cửa, 1 cửa có xe.\nMở 1 cửa trống. Bạn nên đổi cửa?",
                a="Đổi hay không cũng 50%", b=f"Đổi: thắng khoảng {_pct(p)}", correct="b",
                why="Thông tin mới làm xác suất thay đổi. Mô hình cũng cập nhật như vậy.",
                say="Ba cánh cửa, một cửa có xe. Người dẫn mở một cửa trống. Đổi cửa thì khả năng thắng là bao nhiêu?",
                nums=["50%", _pct(p)], topics=["hmm", "bayes"])


def avg_return():
    # trung bình cộng +50% / −40% là +5% nhưng hai năm liền thì lỗ
    a, b = 0.5, -0.4
    arith = (a + b) / 2
    geo = (1 + a) * (1 + b) - 1
    return dict(q=f"Năm 1 lãi {_pct(a)}, năm 2 lỗ {_pct(-b)}.\nTrung bình lãi {_pct(arith)}. Vậy có lãi?",
                a="Có lãi", b=f"Lỗ {_pct(-geo)}", correct="b",
                why="Trung bình cộng đánh lừa. Tiền lãi kép theo trung bình nhân.",
                say=f"Năm một lãi {_pct(a)}, năm hai lỗ {_pct(-b)}. Trung bình là lãi {_pct(arith)}. Vậy thật sự có lãi không?",
                nums=[_pct(a), _pct(-b), _pct(arith), _pct(-geo)], topics=["sharpe", "monte_carlo", "kelly"])


BANK = {f.__name__: f for f in (birthday, coin_streak, loss_recovery, up_down, monty_hall, avg_return)}


def pick(topic, choice="auto"):
    """Câu đố cho chủ đề; 'auto' = câu đố gắn với chủ đề, không có thì xoay vòng ổn định theo tên chủ đề."""
    if choice in (None, "", "off", False):
        return None, None
    if choice != "auto":
        if choice not in BANK:
            raise SystemExit(f"unknown quiz {choice!r}; có: {list(BANK)}")
        return choice, BANK[choice]()
    built = {k: f() for k, f in BANK.items()}
    match = [k for k, v in built.items() if topic in v["topics"]]
    pool = match or sorted(built)
    k = pool[zlib.crc32(topic.encode()) % len(pool)]
    return k, built[k]


# ------------------------------------------------------------------ scenes
def _choice_box(img, y, label, text, state, a):
    color = {"idle": T["raised"], "right": T["positive"], "wrong": T["surface"]}[state]
    F.panel(img, (X0, y, X1, y + 150), fill=color, outline=T["accent"] if state == "idle" else color)
    fg = T["bg"] if state == "right" else (T["muted"] if state == "wrong" else T["text"])
    F.text_box(img, f"{label} · {text}", (X0 + 36, y, X1 - 36, y + 150), "sans-black", 54, fg, "left", "middle",
               min_size=34, label=f"quiz-{label}", hl_numbers=state == "idle", alpha=a)


def scenes(q, bridge=None):
    def ask(img, t, p):
        a = F.ease_out(F.seg(p, 0, 0.2))
        F.chip(img, (X0, 340), "ĐỐ VUI 3 GIÂY", T["accent"], 30)
        F.text_box(img, q["q"], (X0, 480, X1, 820), "sans-black", 74, T["text"], "left", "middle",
                   min_size=44, label="quiz-q", hl_numbers=True, alpha=a)
        _choice_box(img, 850, "A", q["a"], "idle", F.ease_out(F.seg(p, 0.15, 0.35)))
        _choice_box(img, 1025, "B", q["b"], "idle", F.ease_out(F.seg(p, 0.25, 0.45)))
        w = int((X1 - X0) * (1 - F.seg(p, 0.4, 1.0)))  # đếm ngược
        F.ImageDraw.Draw(img).rounded_rectangle([X0, 1215, X0 + max(w, 12), 1229], radius=7, fill=T["accent"])

    def reveal(img, t, p):
        F.text_box(img, q["q"], (X0, 480, X1, 660), "sans-bold", 50, T["muted"], "left", "middle", min_size=34,
                   label="quiz-q2")
        on = F.seg(p, 0, 0.15) >= 1
        _choice_box(img, 680, "A", q["a"], ("right" if q["correct"] == "a" else "wrong") if on else "idle", 1)
        _choice_box(img, 850, "B", q["b"], ("right" if q["correct"] == "b" else "wrong") if on else "idle", 1)
        F.text_box(img, q["why"], (X0, 1030, X1, 1300), "sans-bold", 46, T["neutral"], "left", "top", min_size=30,
                   label="quiz-why", alpha=F.ease_out(F.seg(p, 0.2, 0.45)))

    right = q["a"] if q["correct"] == "a" else q["b"]
    out = [Scene("quiz_question", q["say"] + " A hay B? Đoán trong ba giây.", ask, 5.0,
                 texts=[q["q"], "A · " + q["a"], "B · " + q["b"]]),
           Scene("quiz_answer", f"Đáp án: {right}. {q['why']}", reveal, 4.0, texts=[q["why"]])]
    if bridge:
        def br(img, t, p):
            F.text_box(img, bridge, (X0, 520, X1, 1200), "sans-black", 70, T["text"], "left", "middle", min_size=40,
                       label="quiz-bridge", hl_numbers=True, alpha=F.ease_out(F.seg(p, 0, 0.25)))
        out.append(Scene("quiz_bridge", bridge, br, 2.2, texts=[bridge]))
    return out


def apply(scene_list, ep, kind="video"):
    """Chèn quiz trước nội dung chính. Trả (scenes, literals đã tính để QA số chấp nhận, quiz id)."""
    # style đã tự là câu đố (ví dụ tập Variance) thì không chèn thêm
    if kind != "video" or "quiz" in ep.get("style", "") or any(x.name == "question" for x in scene_list[:2]):
        return scene_list, [], None
    qid, q = pick(ep["topic"], ep.get("quiz", "auto"))
    if q is None:
        return scene_list, [], None
    bridge = ep.get("quiz_bridge", "Thị trường cũng hay đánh lừa trực giác như vậy. Xem tiếp nhé.")
    return scenes(q, bridge) + scene_list, q["nums"], qid


if __name__ == "__main__":
    for k, f in BANK.items():
        q = f()
        print(f"{k:14s} {q['q'].replace(chr(10), ' ')}  → {q['a'] if q['correct'] == 'a' else q['b']}  "
              f"(chủ đề: {', '.join(q['topics'])})")
