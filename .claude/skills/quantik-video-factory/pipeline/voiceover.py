"""Vietnamese voice-over. Tries engines in order and reports which one was used.

Mặc định (chủ sản phẩm chốt 11/2026): giọng NAM miền Bắc, sáng và thanh (NamMinh, cao độ +8Hz), nhịp nhanh theo
TEMPO trong core.py (1.25 → +25%). "male-deep" (nam trầm) vẫn dùng được khi episode muốn. Ghi đè: QT_VOICE,
QT_RATE, QT_PITCH. Episode "lang": "en" dùng giọng en-US cùng tên hồ sơ.

  edge    — Microsoft Edge neural voices (vi-VN-HoaiMyNeural / vi-VN-NamMinhNeural). Best quality, needs Internet.
  gtts    — Google Translate TTS. Needs Internet.
  espeak  — espeak-ng offline, robotic; last resort before silence.
  silent  — no voice; scene length estimated from text so subtitles carry the message.

Usage: python voiceover.py "Xin chào" out.wav [--engine edge]
"""
from __future__ import annotations

import asyncio
import os
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from core import BRAND, LANG, TEMPO, strip_marks

RATE = f"{round((TEMPO - 1) * 100):+d}%"   # 1.25 → "+25%"
VOICES = {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural", "male-deep": "vi-VN-NamMinhNeural"}
# voice profile → (edge voice, rate, pitch). QT_RATE / QT_PITCH env vars still override.
PROFILES = {"male": ("vi-VN-NamMinhNeural", RATE, "+8Hz"),            # mặc định: nam Bắc, sáng, thanh, nhanh
            "male-deep": ("vi-VN-NamMinhNeural", RATE, "-12Hz"),
            "female": ("vi-VN-HoaiMyNeural", RATE, "+0Hz")}
DEFAULT_VOICE = os.environ.get("QT_VOICE", "male")


# English episodes ("lang": "en"): same profile names, US voices (Andrew: male, bright, clear).
PROFILES_EN = {"male": ("en-US-AndrewNeural", RATE, "+4Hz"), "male-deep": ("en-US-ChristopherNeural", RATE, "-5Hz"),
               "female": ("en-US-AvaNeural", RATE, "+0Hz"), "en-male": ("en-US-AndrewNeural", RATE, "+4Hz")}


def profile(voice):
    if LANG["code"] == "en":
        return PROFILES_EN.get(voice, (voice, "+0%", "+0Hz"))
    return PROFILES.get(voice, (VOICES.get(voice, voice), "+0%", "+0Hz"))
ENGINES = ["edge", "gtts", "espeak", "silent"]
RETRIES = int(os.environ.get("QT_TTS_RETRIES", "5"))


def lexicon():
    p = BRAND / "pronunciation.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def speakable(text: str) -> str:
    """Rewrite symbols/acronyms so Vietnamese TTS reads them naturally (brand/pronunciation.json)."""
    if LANG["code"] == "en":
        return text.replace("−", "minus ").replace("%", " percent").replace(" + ", " plus ").replace(" = ", " equals ")
    out = text
    for k, v in sorted(lexicon().items(), key=lambda kv: -len(kv[0])):
        out = re.sub(r"(?<!\w)" + re.escape(k) + r"(?!\w)", v, out)
    out = out.replace("−", "âm ").replace("%", " phần trăm").replace(" + ", " cộng ").replace(" = ", " bằng ")
    return out


def duration_of(path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def estimate_seconds(text: str) -> float:
    # Vietnamese narration ≈ 3,6 syllables/second at a calm explainer pace; English ≈ 2,6 words/second.
    return 0.4 + len(text.split()) / ((2.6 if LANG["code"] == "en" else 3.6) * TEMPO)


def _to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "44100", str(dst)], check=True)


def _trust_env_ca(edge_tts):
    """edge-tts pins certifi's CA list; behind a TLS-inspecting proxy (SSL_CERT_FILE set) add that bundle too."""
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not ca or not Path(ca).exists():
        return
    import ssl

    import certifi

    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(cafile=ca)
    for mod in ("communicate", "voices"):
        m = getattr(edge_tts, mod, None)
        if m is not None and hasattr(m, "_SSL_CTX"):
            m._SSL_CTX = ctx


def _edge(text, dst, voice, rate, pitch="+0Hz"):
    import edge_tts

    tmp = Path(dst).with_suffix(".mp3")

    _trust_env_ca(edge_tts)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")

    async def go():
        await edge_tts.Communicate(text, voice, rate=os.environ.get("QT_RATE", rate), pitch=os.environ.get("QT_PITCH", pitch),
                                   proxy=proxy).save(str(tmp))

    asyncio.run(asyncio.wait_for(go(), timeout=40))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)


def _atempo(dst):
    """gTTS/espeak cannot change speed: speed the wav up to TEMPO without changing pitch."""
    if abs(TEMPO - 1) < 0.01:
        return
    tmp = Path(dst).with_suffix(".tempo.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dst), "-filter:a", f"atempo={TEMPO:.3f}", str(tmp)],
                   check=True)
    tmp.replace(dst)


def _gtts(text, dst, *_):
    from gtts import gTTS

    tmp = Path(dst).with_suffix(".mp3")
    gTTS(text, lang=LANG["code"], timeout=20).save(str(tmp))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)
    _atempo(dst)


def _espeak(text, dst, *_):
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        raise RuntimeError("espeak-ng not installed")
    subprocess.run([exe, "-v", "en-us" if LANG["code"] == "en" else "vi", "-s", "150", "-w", str(dst), text], check=True, capture_output=True)


def _split_synth(say, dst, voice, rate, pitch="+0Hz"):
    parts = [p for p in re.split(r"(?<=[.!?…])\s+", say) if p.strip()]
    if len(parts) < 2:
        raise RuntimeError("không tách được câu")
    tmp = []
    for i, p in enumerate(parts):
        out = Path(dst).with_name(Path(dst).stem + f"-s{i}.wav")
        for k in range(RETRIES):
            try:
                _edge(p, out, voice, rate, pitch)
                break
            except Exception:
                if k + 1 == RETRIES:
                    raise
                time.sleep(min(8.0, 1.0 * 2 ** k))
        tmp.append(out)
    lst = Path(dst).with_suffix(".txt")
    lst.write_text("".join(f"file '{t.resolve()}'\n" for t in tmp), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(dst)],
                   check=True)
    for t in tmp + [lst]:
        t.unlink(missing_ok=True)


def synth(text, dst, engine="auto", voice=None, rate=None):
    """Write dst (wav). Returns (engine_used, seconds). engine_used == 'silent' means no file was written."""
    order = ENGINES if engine == "auto" else [engine]
    errors = []
    voice = voice or DEFAULT_VOICE
    say = speakable(strip_marks(text))
    vid, prate, pitch = profile(voice)
    rate = rate or prate
    for e in order:
        if e == "silent":
            return "silent", estimate_seconds(text), errors
        # online engines fail intermittently (edge: NoAudioReceived on ~1 in 5 calls) → retry before giving up
        attempts = RETRIES if e in ("edge", "gtts") else 1
        for k in range(attempts):
            try:
                {"edge": lambda *a: _edge(*a, pitch), "gtts": _gtts, "espeak": _espeak}[e](say, dst, vid, rate)
                return e, duration_of(dst), errors
            except Exception as ex:  # network blocked, package missing, transient service error...
                errors.append(f"{e}: {type(ex).__name__}: {str(ex)[:120]}")
                if k + 1 < attempts and "Certificate" not in type(ex).__name__ and not isinstance(ex, ImportError):
                    time.sleep(min(8.0, 1.0 * 2 ** k))
                else:
                    break
        if e == "edge" and errors and "Certificate" not in errors[-1]:
            try:  # one awkward sentence (often an English term) can sink a whole scene: retry sentence by sentence
                _split_synth(say, dst, vid, rate, pitch)
                return e, duration_of(dst), errors
            except Exception as ex:
                errors.append(f"{e} (từng câu): {type(ex).__name__}: {str(ex)[:120]}")
    return "silent", estimate_seconds(text), errors


def probe_engine(engine="auto", voice=None):
    """Pick the first engine that works once, so a whole video uses one consistent voice."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        used, _, errors = synth("Hello." if LANG["code"] == "en" else "Xin chào.", Path(d) / "probe.wav", engine, voice)
    return used, errors


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--engine", default="auto", choices=["auto"] + ENGINES)
    ap.add_argument("--voice", default=DEFAULT_VOICE, help="male (mặc định: nam Bắc sáng) | male-deep | female | edge voice id")
    a = ap.parse_args()
    used, sec, errs = synth(a.text, a.out, a.engine, a.voice)
    print(json.dumps({"engine": used, "seconds": round(sec, 2), "errors": errs}, ensure_ascii=False))
    sys.exit(0)
