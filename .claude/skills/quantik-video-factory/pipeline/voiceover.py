"""Vietnamese voice-over. Tries engines in order and reports which one was used.

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
from pathlib import Path

from core import BRAND

VOICES = {"female": "vi-VN-HoaiMyNeural", "male": "vi-VN-NamMinhNeural", "male-deep": "vi-VN-NamMinhNeural"}
# Mặc định kênh (yêu cầu chủ sản phẩm): giọng nam miền Bắc, sáng, tempo x1.25 cho cảm giác hồi hộp, dồn dập.
# (rate, pitch) theo edge-tts; biến môi trường QT_RATE / QT_PITCH ghi đè.
PRESETS = {"male": ("+25%", "+6Hz"), "female": ("+25%", "+0Hz"), "male-deep": ("+0%", "-12Hz")}
DEFAULT_VOICE = "male"
TEMPO = 1.25  # dùng để ước thời lượng khi không có giọng
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
    # Vietnamese narration ≈ 3,6 syllables/second at a calm pace, x TEMPO for the channel's fast delivery.
    return 0.5 + len(text.split()) / (3.6 * TEMPO)


def _to_wav(src, dst):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-ac", "1", "-ar", "44100", str(dst)], check=True)


def _edge(text, dst, voice, rate, pitch="+0Hz"):
    import edge_tts

    ca = os.environ.get("SSL_CERT_FILE")
    if ca and os.path.exists(ca):  # behind a TLS-inspecting proxy: trust its CA as well (edge-tts pins certifi)
        import ssl
        import edge_tts.communicate as ec

        ctx = ssl.create_default_context(cafile=ca)
        try:
            import certifi
            ctx.load_verify_locations(certifi.where())
        except Exception:
            pass
        ec._SSL_CTX = ctx

    tmp = Path(dst).with_suffix(".mp3")

    async def go():
        await edge_tts.Communicate(text, voice, rate=os.environ.get("QT_RATE", rate),
                                   pitch=os.environ.get("QT_PITCH", pitch)).save(str(tmp))

    asyncio.run(asyncio.wait_for(go(), timeout=40))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)


def _gtts(text, dst, *_):  # gTTS has no rate control; assemble.py speeds the clip up (atempo)
    from gtts import gTTS

    tmp = Path(dst).with_suffix(".mp3")
    gTTS(text, lang="vi", timeout=20).save(str(tmp))
    _to_wav(tmp, dst); tmp.unlink(missing_ok=True)


def _espeak(text, dst, *_):  # sped up afterwards like gTTS
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        raise RuntimeError("espeak-ng not installed")
    subprocess.run([exe, "-v", "vi", "-s", "150", "-w", str(dst), text], check=True, capture_output=True)


def synth(text, dst, engine="auto", voice=DEFAULT_VOICE, rate=None):
    """Write dst (wav). Returns (engine_used, seconds). engine_used == 'silent' means no file was written."""
    order = ENGINES if engine == "auto" else [engine]
    errors = []
    say = speakable(text)
    for e in order:
        if e == "silent":
            return "silent", estimate_seconds(text), errors
        try:
            r, pitch = PRESETS.get(voice, ("+25%", "+0Hz"))
            {"edge": _edge, "gtts": _gtts, "espeak": _espeak}[e](say, dst, VOICES.get(voice, voice), rate or r, pitch)
            if e != "edge":
                _speed_up(dst, TEMPO)
            return e, duration_of(dst), errors
        except Exception as ex:  # network blocked, package missing...
            errors.append(f"{e}: {type(ex).__name__}: {str(ex)[:120]}")
    return "silent", estimate_seconds(text), errors


def _speed_up(wav, factor):
    tmp = Path(wav).with_name(Path(wav).stem + ".fast.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-filter:a", f"atempo={factor}", str(tmp)],
                   check=True)
    tmp.replace(wav)


def probe_engine(engine="auto", voice=DEFAULT_VOICE):
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
