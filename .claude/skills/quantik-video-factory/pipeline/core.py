"""Shared pieces: paths, brand theme, fonts, Vietnamese number formatting, knowledge loader."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
BRAND = SKILL / "brand"
KNOWLEDGE = SKILL / "knowledge"
STYLES = SKILL / "styles"
REPO = SKILL.parent.parent.parent  # .claude/skills/<skill> -> repo root
DEFAULT_OUT = REPO / "social-output"

W, H = 1080, 1920
FPS = 30

# Vertical safe zone for TikTok / Reels / Shorts overlays (in 1080x1920 coordinates).
# Top: status bar + "Following/For you"; bottom: caption, music ticker; right: like/share rail.
SAFE = {"left": 60, "top": 170, "right": 940, "bottom": 1500}

# Colours mirror frontend/src/app/globals.css (dark terminal theme).
THEME = {
    "bg": (8, 13, 11),
    "surface": (13, 25, 19),
    "raised": (23, 39, 31),
    "border": (41, 67, 55),
    "text": (237, 244, 239),
    "muted": (166, 185, 173),
    "accent": (255, 145, 77),
    "positive": (103, 214, 165),
    "negative": (240, 128, 136),
    "neutral": (227, 193, 108),
}


def hex_(c):
    return "#%02x%02x%02x" % c


# ---------------------------------------------------------------- fonts
_FONT_CANDIDATES = {
    "mono": [
        BRAND / "assets/fonts/IBMPlexMono-Regular.ttf",
        Path("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
    ],
    "mono-bold": [
        BRAND / "assets/fonts/IBMPlexMono-Bold.ttf",
        Path("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"),
    ],
    "sans": [
        BRAND / "assets/fonts/BeVietnamPro-Regular.ttf",
        Path("/usr/share/fonts/opentype/inter/Inter-Regular.otf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ],
    "sans-bold": [
        BRAND / "assets/fonts/BeVietnamPro-Bold.ttf",
        Path("/usr/share/fonts/opentype/inter/Inter-Bold.otf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ],
    "sans-black": [
        BRAND / "assets/fonts/BeVietnamPro-ExtraBold.ttf",
        Path("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ],
}


def font_path(kind: str) -> str:
    for p in _FONT_CANDIDATES[kind]:
        if p.exists():
            return str(p)
    raise FileNotFoundError(f"No font for {kind}; add one to brand/assets/fonts/")


@lru_cache(maxsize=256)
def font(kind: str, size: int):
    from PIL import ImageFont

    return ImageFont.truetype(font_path(kind), int(size))


# ---------------------------------------------------------------- numbers (vi-VN)
def _group(intpart: str) -> str:
    out = ""
    while len(intpart) > 3:
        out = "." + intpart[-3:] + out
        intpart = intpart[:-3]
    return intpart + out


# ---------------------------------------------------------------- language
# Episodes default to Vietnamese. "lang": "en" in an episode switches number format, voice, UI labels,
# disclaimer and banned-phrase list to English (for international IG / YouTube Shorts).
LANG = {"code": "vi"}

LABELS = {
    "vi": {"tagline": "quant cho cổ phiếu Việt Nam", "chapter": "Chương", "takeaway": "Mang về",
           "sim_note": "Dữ liệu mô phỏng · giáo dục, không phải khuyến nghị", "real_note": "Dữ liệu thật: ",
           "follow_cta": "Thả tim và theo dõi QuanTik để học một kiến thức quant mỗi ngày",
           "myth": "BẠN NGHĨ", "fact": "THỰC RA", "evidence": "Bằng chứng từ code chạy thật",
           "myth_kicker": "Hiểu lầm phổ biến", "result": "kết quả",
           "thumb_footer": "Dữ liệu mô phỏng • Không phải khuyến nghị"},
    "en": {"tagline": "quant, explained with real code", "chapter": "Chapter", "takeaway": "Takeaway",
           "sim_note": "Simulated data · educational, not financial advice", "real_note": "Real data: ",
           "follow_cta": "Like and follow QuanTik for one quant lesson every day",
           "myth": "YOU THINK", "fact": "ACTUALLY", "evidence": "Evidence from code that really ran",
           "myth_kicker": "Common myth", "result": "output",
           "thumb_footer": "Simulated data • Not financial advice"},
}


def set_lang(code: str | None):
    LANG["code"] = code if code in LABELS else "vi"


def L(key: str) -> str:
    return LABELS[LANG["code"]][key]


def fmt_vi(value, spec: str = "num2") -> str:
    """Format like Vietnamese print: 1.234,5 ; 12,3% ; 149.000 đ. In English mode: 1,234.5 ; 12.3% ; $1,234."""
    if isinstance(value, str):
        return value
    if LANG["code"] == "en":
        return fmt_en(value, spec)
    m = re.fullmatch(r"(pct|num|vnd|int|x)(\d?)", spec or "num2")
    if not m:
        raise ValueError(f"unknown number format {spec!r}")
    kind, digits = m.group(1), int(m.group(2) or 0)
    if kind == "pct":
        value = value * 100
    if kind in ("int", "vnd"):
        digits = 0
    neg = value < 0
    s = f"{abs(value):.{digits}f}"
    if "." in s:
        ip, fp = s.split(".")
    else:
        ip, fp = s, ""
    out = _group(ip) + ("," + fp if fp else "")
    if neg and out.strip("0,.") != "":
        out = "−" + out
    if kind == "pct":
        out += "%"
    elif kind == "vnd":
        out += " đ"
    elif kind == "x":
        out += "x"
    return out


def fmt_en(value, spec: str = "num2") -> str:
    m = re.fullmatch(r"(pct|num|vnd|usd|int|x)(\d?)", spec or "num2")
    if not m:
        raise ValueError(f"unknown number format {spec!r}")
    kind, digits = m.group(1), int(m.group(2) or 0)
    if kind == "pct":
        value = value * 100
    if kind in ("int", "vnd", "usd"):
        digits = 0
    out = f"{abs(value):,.{digits}f}"
    if value < 0 and out.strip("0,.") != "":
        out = "−" + out
    return {"pct": out + "%", "x": out + "x", "usd": "$" + out, "vnd": out + " VND"}.get(kind, out)


_PH = re.compile(r"\{([a-zA-Z_][\w]*)(?::([a-z]+\d?))?\}")


def fill(text: str, values: dict, formats: dict, rendered: set | None = None) -> str:
    """Replace {key} / {key:fmt} with numbers computed by the model code."""

    def rep(m):
        key, spec = m.group(1), m.group(2)
        if key not in values:
            raise KeyError(f"placeholder {{{key}}} has no computed value; available: {sorted(values)}")
        out = fmt_vi(values[key], spec or formats.get(key, "num2"))
        if rendered is not None:
            rendered.add(out)
        return out

    return _PH.sub(rep, text)


_PH_TEX = re.compile(r"<<([a-zA-Z_]\w*)(?::([a-z]+\d?))?>>")


def fill_latex(tex: str, values: dict, formats: dict, rendered: set | None = None) -> str:
    """LaTeX uses braces, so numbers go in as <<key>> / <<key:fmt>>; the decimal comma becomes {,}."""

    def rep(m):
        key, spec = m.group(1), m.group(2)
        out = fmt_vi(values[key], spec or formats.get(key, "num2"))
        if rendered is not None:
            rendered.add(out)
        return out.replace(",", "{,}").replace(".", "{.}").replace("$", r"\$").replace("%", r"\%").replace("−", "-")

    return _PH_TEX.sub(rep, tex)


def fill_tree(obj, values, formats, rendered):
    if isinstance(obj, str):
        return fill(obj, values, formats, rendered)
    if isinstance(obj, list):
        return [fill_tree(x, values, formats, rendered) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in TEX_KEYS:
                out[k] = [fill_latex(x, values, formats, rendered) for x in v] if isinstance(v, list) \
                    else fill_latex(v, values, formats, rendered)
            elif k in RAW_KEYS:
                out[k] = v
            else:
                out[k] = fill_tree(v, values, formats, rendered)
        return out
    return obj


# keys holding LaTeX (filled with <<key>>) or ids/code that are never filled
TEX_KEYS = {"formula", "formula_parts", "formula_numeric", "sym"}
RAW_KEYS = {"id", "topic", "style", "lang", "platforms", "key", "fmt", "hashtags", "format", "allowed_literals", "voice",
            "facts"}


# ---------------------------------------------------------------- knowledge
def load_model_kb(topic: str) -> dict:
    """Read knowledge/models/<topic>.md and return its ```json video_defaults block + raw text."""
    path = KNOWLEDGE / "models" / f"{topic}.md"
    if not path.exists():
        have = sorted(p.stem for p in (KNOWLEDGE / "models").glob("*.md"))
        raise FileNotFoundError(f"knowledge/models/{topic}.md not found. Topics: {have}")
    text = path.read_text(encoding="utf-8")
    m = re.search(r"## video_defaults\s*```json\s*(.*?)```", text, re.S)
    if not m:
        raise ValueError(f"{path} has no '## video_defaults' ```json block")
    kb = json.loads(m.group(1))
    kb["_markdown"] = text
    return kb


def load_banned() -> list[str]:
    """Vietnamese banned phrases always apply; English ones are added on top (mixed-language text is common)."""
    text = (BRAND / "compliance.md").read_text(encoding="utf-8")
    out = []
    for head in ("## Cụm cấm", "## Banned phrases"):
        m = re.search(re.escape(head) + r".*?```text\s*(.*?)```", text, re.S)
        if m:
            out += [ln.strip().lower() for ln in m.group(1).splitlines() if ln.strip() and not ln.startswith("#")]
    return out


def disclaimer(lang: str | None = None) -> str:
    text = (BRAND / "compliance.md").read_text(encoding="utf-8")
    head = "## Disclaimer" if (lang or LANG["code"]) == "en" else "## Câu miễn trừ"
    m = re.search(re.escape(head) + r".*?```text\s*(.*?)```", text, re.S)
    return " ".join(m.group(1).split())


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def save_json(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
