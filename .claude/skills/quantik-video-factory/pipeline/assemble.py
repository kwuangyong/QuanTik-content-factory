"""Mux silent video + per-scene voice clips + background music into the final mp4.

Music: brand/assets/music/*.(mp3|wav|m4a) if present (must be licensed — see brand/assets/README.md),
otherwise a soft pad synthesised here from sine waves (original, royalty-free).
Voice is placed at each scene's start time; music is ducked under the voice with a sidechain compressor.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path

from core import BRAND

SR = 44100


def synth_pad(path, seconds, seed_chord=0):
    """Generate a calm minor-key pad (Am → F → C → G), quiet, original and royalty-free."""
    import numpy as np

    chords = [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [196.0, 261.63, 329.63], [196.0, 246.94, 293.66]]
    chords = chords[seed_chord % 4:] + chords[: seed_chord % 4]
    bar = 4.0
    t = np.arange(int(seconds * SR)) / SR
    ci = (t // bar).astype(int) % len(chords)
    local = (t % bar) / bar
    env = np.minimum(1, local * 6) * np.minimum(1, (1 - local) * 6)
    sig = np.zeros_like(t)
    for k in range(3):
        f = np.array([c[k] for c in chords])[ci]
        sig += np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
    sig += 0.5 * np.sin(np.pi * np.array([c[0] for c in chords])[ci] * t)
    fade = np.minimum(1, np.minimum(t / 1.5, (seconds - t) / 1.5))
    pcm = (np.clip(sig / 6 * env * fade, -1, 1) * 9000).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def synth_tense(path, seconds, bpm=112):
    """Suspense bed (original, royalty-free): low minor drone, heartbeat kick, ticking clock, rising riser."""
    import numpy as np

    t = np.arange(int(seconds * SR)) / SR
    beat = 60.0 / bpm
    drone = sum(np.sin(2 * np.pi * f * t + ph) for f, ph in [(55.0, 0), (65.41, 1.1), (82.41, 2.3)])  # A1 C2 E2
    drone *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 8.0) ** 2
    pos = t % beat
    kick_env = np.exp(-pos * 28)
    kick = np.sin(2 * np.pi * (48 + 90 * np.exp(-pos * 40)) * pos) * kick_env       # thump
    pos2 = (t - 0.22 * beat) % beat                                                  # "lub-dub" second hit
    kick += 0.6 * np.sin(2 * np.pi * (44 + 70 * np.exp(-pos2 * 40)) * pos2) * np.exp(-pos2 * 30)
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(len(t))
    tpos = t % (beat / 2)
    tick = noise * np.exp(-tpos * 160) * 0.35
    rise = (t % 16.0) / 16.0
    riser = np.sin(2 * np.pi * (220 + 660 * rise ** 2) * t) * rise ** 3 * 0.25
    sig = 0.28 * drone + 0.9 * kick + tick + riser
    fade = np.minimum(1, np.minimum(t / 0.6, (seconds - t) / 1.5))
    pcm = (np.clip(sig / 2.2 * fade, -1, 1) * 12000).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def pick_music(work: Path, seconds: float, music: str | None):
    if music == "none":
        return None
    if music:
        return Path(music)
    lib = sorted((BRAND / "assets/music").glob("*.*")) if (BRAND / "assets/music").exists() else []
    lib = [p for p in lib if p.suffix.lower() in (".mp3", ".wav", ".m4a")]
    if lib:
        return lib[0]
    if music == "calm":
        return synth_pad(work / "pad.wav", seconds + 1)
    return synth_tense(work / "tense.wav", seconds + 1)  # mặc định kênh: nhạc nền hồi hộp


def assemble(video, scenes, out, work: Path, music=None, music_db=-17):
    """scenes: list with .duration and optional .audio (wav path)."""
    total = sum(s.duration for s in scenes)
    inputs = ["-i", str(video)]
    filters, labels, t0 = [], [], 0.0
    idx = 1
    for s in scenes:
        if s.audio and Path(s.audio).exists():
            inputs += ["-i", str(s.audio)]
            ms = int((t0 + 0.15) * 1000)
            filters.append(f"[{idx}:a]adelay={ms}|{ms},apad[v{idx}]")
            labels.append(f"[v{idx}]"); idx += 1
        t0 += s.duration
    mpath = pick_music(work, total, music)
    has_voice = bool(labels)
    if has_voice:
        filters.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,atrim=0:{total:.3f}[voice]")
    if mpath:
        inputs += ["-stream_loop", "-1", "-i", str(mpath)]
        vol = 10 ** (music_db / 20)
        filters.append(f"[{idx}:a]atrim=0:{total:.3f},volume={vol:.3f},afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5[m]")
        if has_voice:
            filters.append("[voice]asplit=2[vo][sc]")
            filters.append("[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md]")
            filters.append("[vo][md]amix=inputs=2:normalize=0[aout]")
        else:
            filters.append("[m]anull[aout]")
    elif has_voice:
        filters.append("[voice]anull[aout]")
    else:
        filters.append(f"anullsrc=r={SR}:cl=mono,atrim=0:{total:.3f}[aout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
           "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", str(SR),
           "-t", f"{total:.3f}", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    return out
