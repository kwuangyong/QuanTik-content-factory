"""Replace the opening of the original 04-variance.mp4 with the TikTok quiz."""
import argparse
import asyncio
import os
import re
import subprocess
import sys
import tempfile
from math import ceil
from pathlib import Path
from statistics import pvariance

import render as R
import voiceover as V
from variance_bus import scenes
from core import DEFAULT_OUT, FPS, SKILL, disclaimer, fill_tree, fmt_vi, load_json, save_json

sys.path.insert(0, str(SKILL / "qa"))
import check_banned
import check_format
import check_numbers
import report


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def record_hook(intro, path):
    """Record the script in one take and find each scene's spoken cue."""
    import edge_tts
    from edge_tts.exceptions import EdgeTTSException

    lines = [V.speakable(scene.say) for scene in intro]
    lines[2] = lines[2].lower()  # Continue the preceding line after its ellipsis.
    words_by_scene = [re.findall(r"\w+", line.casefold()) for line in lines]

    async def record():
        parameters = {
            "rate": os.environ.get("QT_RATE", "+3%"),
            "pitch": os.environ.get("QT_PITCH", "-12Hz"),
        }
        try:
            speech = edge_tts.Communicate(" ".join(lines), V.VOICES["male"],
                                          boundary="WordBoundary", **parameters)
        except TypeError:  # Older edge-tts releases emit word boundaries by default.
            speech = edge_tts.Communicate(" ".join(lines), V.VOICES["male"], **parameters)
        tokens = []
        with path.open("wb") as audio:
            async for packet in speech.stream():
                if packet["type"] == "audio":
                    audio.write(packet["data"])
                elif packet["type"] == "WordBoundary":
                    tokens.append(packet)
        return tokens

    try:
        tokens = asyncio.run(asyncio.wait_for(record(), timeout=40))
    except EdgeTTSException as exc:
        raise RuntimeError(f"Edge voice recording failed: {exc}") from exc
    spoken = [token["text"].casefold() for token in tokens]
    if spoken != [word for words in words_by_scene for word in words]:
        raise RuntimeError("Voice word boundaries did not match the quiz script")
    cues, at = [], 0
    for words in words_by_scene:
        start = max(0, tokens[at]["offset"] / 10_000_000 - 0.06)
        at += len(words)
        last = tokens[at - 1]
        end = (last["offset"] + last["duration"]) / 10_000_000 + 0.16
        if at < len(tokens):
            end = min(end, tokens[at]["offset"] / 10_000_000 - 0.06)
        cues.append((start, end - start))
    return cues


def voice_tracks(intro, work, engine):
    if engine in ("auto", "edge"):
        recording = work / "voice.mp3"
        try:
            cues = record_hook(intro, recording)
        except (OSError, RuntimeError, ImportError, asyncio.TimeoutError) as exc:
            if engine == "edge":
                raise
            print(f"Edge TTS unavailable: {exc}")
        else:
            audio = []
            for scene, (offset, duration) in zip(intro, cues):
                track = work / f"{scene.name}-track.wav"
                scene.duration = ceil(max(scene.min_dur, duration) * FPS) / FPS
                ffmpeg("-ss", offset, "-i", recording,
                       "-af", f"atrim=duration={duration},apad", "-t", scene.duration,
                       "-ar", 48000, "-ac", 2, track)
                audio.append(track)
            return audio, "Edge TTS · Nam Minh (nam trầm)"
    fallback = "espeak" if engine == "auto" else engine
    used, _ = V.probe_engine(fallback, voice="male")
    audio = []
    for scene in intro:
        wav = work / f"{scene.name}.wav"
        actual, duration, errors = V.synth(scene.say, wav, used, voice="male")
        if actual != used:
            raise RuntimeError(f"Voice synthesis failed for {scene.name}: {errors}")
        scene.duration = ceil(max(scene.min_dur, duration + 0.12) * FPS) / FPS
        track = work / f"{scene.name}-track.wav"
        if actual == "silent":
            ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", scene.duration, track)
        else:
            ffmpeg("-i", wav, "-af", "adelay=50:all=1,apad", "-t", scene.duration,
                   "-ar", 48000, "-ac", 2, track)
        audio.append(track)
    return audio, used


def replace(source, out, engine):
    ep = load_json(SKILL / "episodes/04-variance-quiz.json")
    a, b = ep["returns_a"], ep["returns_b"]
    small, large = max(map(abs, a)), max(map(abs, b))
    values = {"small": small, "large": large, "small_squared": small ** 2, "large_squared": large ** 2,
              "weight_ratio": (large / small) ** 2, "var_a": pvariance(a), "var_b": pvariance(b)}
    formats = dict.fromkeys(("small", "large", "small_squared", "large_squared", "weight_ratio"), "int")
    rendered = set()
    ep = fill_tree(ep, values, formats, rendered)
    labels = [[("+" if n > 0 else "") + fmt_vi(n / 100, "pct0") for n in row] for row in (a, b)]
    rendered.update(fmt_vi(n / 100, "pct0") for row in (a, b) for n in row)
    intro = scenes(ep, labels, large)
    texts = [text for scene in intro for text in [scene.say, *scene.texts]] + [ep["title"], ep["caption"]]
    nums = check_numbers.check(texts, values, formats, rendered)
    banned = check_banned.check(texts)
    if nums["fail"] or banned["fail"]:
        raise ValueError(report.summary(nums, banned, None))

    out.mkdir(parents=True, exist_ok=True)
    disc = disclaimer()
    tags = " ".join("#" + tag for tag in ep["hashtags"])
    caption = f'{ep["caption"]}\n\n{tags}\n\n{disc}'
    (out / "captions.md").write_text(
        f'# TikTok\n\n{caption}\n\n# Reels\n\n{caption}\n\n# YouTube Shorts\n\n{ep["title"]}\n\n{caption}\n',
        encoding="utf-8")
    save_json(out / "values.json", {"values": values, "formats": formats, "returns_pct": [a, b]})
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        work = Path(tmp)
        audio, used = voice_tracks(intro, work, engine)
        silent = work / "intro.mp4"
        layout = out / "layout.json"
        R.render(intro, silent, "QUIZ", "Học Quant cùng QuanTik", layout_path=layout,
                 srt_path=out / "quiz.srt")
        draft = work / "final.mp4"
        offset = ep["cut_frame"] / FPS
        tracks = [arg for track in audio for arg in ("-i", track)]
        voice_inputs = "".join(f"[{i}:a]" for i in range(1, len(audio) + 1))
        body = len(audio) + 1
        ffmpeg("-i", silent, *tracks, "-ss", offset, "-i", source,
               "-filter_complex",
               f"{voice_inputs}concat=n={len(audio)}:v=0:a=1[qa];"
               f"[0:v]setsar=1[v0];[{body}:v]setsar=1[v1];"
               f"[v0][qa][v1][{body}:a]concat=n=2:v=1:a=1[v][a]",
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", 19,
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", draft)
        fmt = check_format.check_video(draft, layout)
        verdict = "KHÔNG ĐẠT" if fmt["fail"] else "ĐẠT"
        report.write(out, ep, nums, banned, fmt, verdict, {
            "Giọng đọc quiz": used, "Nguồn hình quiz": "Hoạt họa xe buýt QuanTik vẽ bằng code",
            "Phạm vi kiểm tra số và bố cục": "Phần quiz mới. Phần thân và thẻ cuối từ video nguồn.",
        })
        if fmt["fail"]:
            raise ValueError(fmt["issues"])
        draft.replace(out / "final.mp4")
        R.still(intro[0], 0, "QUIZ", "Học Quant cùng QuanTik", out / "thumbnail.jpg")
    print(report.summary(nums, banned, fmt))
    print(f"{out / 'final.mp4'} | {used} | {fmt['facts']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT / "04-variance")
    parser.add_argument("--voice-engine", choices=["auto", *V.ENGINES], default="auto")
    args = parser.parse_args()
    replace(args.source, args.out, args.voice_engine)
