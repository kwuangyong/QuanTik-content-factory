"""Shared bits for the market-intelligence pipeline: paths, Vietnam time, trading-session arithmetic, hashing."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
PILLAR_DIR = SKILL / "pillars" / "market-intelligence"
REPO = SKILL.parent.parent.parent
DEFAULT_DATA = REPO / "social-output" / "_market"      # gitignored: raw third-party data stays local
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
CLOSE_TIME = dt.time(15, 0)                            # HOSE ATC ends 14:45; snapshot after 15:00 is end-of-day

AGR_INDEX_URL = "https://trading.agr.vn/datafeed/indexsnaps/HOSE,30,UPCOM,HNX"
AGR_INSTRUMENTS_URL = "https://trading.agr.vn/datafeed/instruments"


def now_ict():
    return dt.datetime.now(ICT)


def iso(t):
    return t.astimezone(ICT).isoformat(timespec="seconds")


def parse_iso(s):
    t = dt.datetime.fromisoformat(s)
    return t if t.tzinfo else t.replace(tzinfo=ICT)


def holidays():
    p = PILLAR_DIR / "holidays.json"
    return {dt.date.fromisoformat(d) for d in json.loads(p.read_text(encoding="utf-8")).get("dates", [])} if p.exists() else set()


def is_session(d):
    return d.weekday() < 5 and d not in holidays()


def sessions_behind(as_of: dt.date, now: dt.datetime) -> int:
    """Trading sessions that have closed after `as_of` up to `now` (0 = data is the latest closed session)."""
    n, d = 0, as_of + dt.timedelta(days=1)
    today = now.astimezone(ICT).date()
    while d <= today:
        if is_session(d) and (d < today or now.astimezone(ICT).time() >= CLOSE_TIME):
            n += 1
        d += dt.timedelta(days=1)
    return n


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def save(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def vi_date(d: dt.date):
    return f"{d.day:02d}/{d.month:02d}/{d.year}"
