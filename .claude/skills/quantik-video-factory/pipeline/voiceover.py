"""Vietnamese voice-over. Tries engines in order and reports which one was used.

Mặc định: giọng NAM miền Bắc (vi-VN-NamMinhNeural), nâng cao độ nhẹ cho sáng và thanh, đọc nhanh +25%
(đồng bộ TEMPO trong core.py). Ghi đè: QT_VOICE, QT_PITCH (vd "+8Hz"), QT_RATE (vd "+25%").

  edge    — Microsoft Edge neural voices (vi-VN-NamMinhNeural / vi-VN-HoaiMyNeural). Best quality, needs Internet.
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
from pathlib import Path

from core import BRAND, TEMPO

# NamMinh = nam, giọng Hà Nội. "en-male" dành cho bản tiếng Anh (Andrew: nam, sáng, rõ).
VOICES = {"male": "vi-VN-NamMinhNeural", "female": "vi-VN-HoaiMyNeural",
          "en-male": "en-US-AndrewNeural", "en-female": "en-US-AvaNeural"}
DEFAULT_VOICE = os.environ.get("QT_VOICE", "male")
# Giọng nam sáng, thanh: nâng cao độ một chút; tốc độ theo TEMPO (1.25 → +25%).
PITCH = {"male": "+8Hz", "en-male": "+4Hz"}
RATE = f"{round((TEMPO - 1) * 100):+d}%"
ENGINES = ["edge", "gtts", "espeak", "silent"]


def lexicon():
    p = BRAND / "pronunciation.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def speakable(text: str) -> str:
    """Rewrite symbols/acronyms so Vietnamese TTS reads them naturally (brand/pronunciation.json)."""
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
    # Vietnamese narration ≈ 3,6 syllables/second at a calm explainer pace, sped up by TEMPO.
    return 0.4 + len(text.split()) / (3.6 * TEMPO)


def _to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "44100", str(dst)], check=True)


def _edge(text, dst, voice, rate, pitch="+0Hz"):
    import ssl

    import edge_tts
    import edge_tts.communicate as EC

    # Behind an HTTPS-inspecting proxy (cloud sandbox) edge-tts needs the proxy and its CA passed explicitly.
    ca = os.environ.get("TTS_CA_BUNDLE") or ("/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None)
    if ca and hasattr(EC, "_SSL_CTX"):
        EC._SSL_CTX = ssl.create_default_context(cafile=ca)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    tmp = Path(dst).with_suffix(".mp3")

    async def go():
        await edge_tts.Communicate(text, voice, rate=os.environ.get("QT_RATE", rate),
                                   pitch=os.environ.get("QT_PITCH", pitch), proxy=proxy).save(str(tmp))

    asyncio.run(asyncio.wait_for(go(), timeout=40))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)


def _atempo(dst):
    """gTTS/espeak cannot change speed themselves: speed the wav up to TEMPO without changing pitch."""
    if abs(TEMPO - 1) < 0.01:
        return
    tmp = Path(dst).with_suffix(".tempo.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(dst), "-filter:a", f"atempo={TEMPO:.3f}",
                    str(tmp)], check=True)
    tmp.replace(dst)


def _gtts(text, dst, voice="", *_):
    from gtts import gTTS

    tmp = Path(dst).with_suffix(".mp3")
    gTTS(text, lang="en" if str(voice).startswith("en") else "vi", timeout=20).save(str(tmp))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)
    _atempo(dst)


def _espeak(text, dst, *_):
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        raise RuntimeError("espeak-ng not installed")
    lang = "en" if str(_[0] if _ else "").startswith("en") else "vi"
    subprocess.run([exe, "-v", lang + "+m3", "-p", "60", "-s", str(int(150 * TEMPO)), "-w", str(dst), text],
                   check=True, capture_output=True)


def synth(text, dst, engine="auto", voice=None, rate=None):
    """Write dst (wav). Returns (engine_used, seconds). engine_used == 'silent' means no file was written."""
    from core import strip_marks

    voice = voice or DEFAULT_VOICE
    rate = rate or RATE
    order = ENGINES if engine == "auto" else [engine]
    errors = []
    say = speakable(strip_marks(text)) if not str(voice).startswith("en") else strip_marks(text)
    for e in order:
        if e == "silent":
            return "silent", estimate_seconds(text), errors
        try:
            vid = VOICES.get(voice, voice)
            if e == "edge":
                _edge(say, dst, vid, rate, PITCH.get(voice, "+0Hz"))
            else:
                {"gtts": _gtts, "espeak": _espeak}[e](say, dst, vid)
            return e, duration_of(dst), errors
        except Exception as ex:  # network blocked, package missing...
            errors.append(f"{e}: {type(ex).__name__}: {str(ex)[:120]}")
    return "silent", estimate_seconds(text), errors


def probe_engine(engine="auto", voice=None):
    """Pick the first engine that works once, so a whole video uses one consistent voice."""
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        used, _, errors = synth("Xin chào.", Path(d) / "probe.wav", engine, voice)
    return used, errors


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--engine", default="auto", choices=["auto"] + ENGINES)
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    a = ap.parse_args()
    used, sec, errs = synth(a.text, a.out, a.engine, a.voice)
    print(json.dumps({"engine": used, "seconds": round(sec, 2), "errors": errs}, ensure_ascii=False))
    sys.exit(0)
