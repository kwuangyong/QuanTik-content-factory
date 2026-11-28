"""Replace the opening of the original 04-variance.mp4 with the TikTok quiz."""
import argparse
import subprocess
import sys
import tempfile
from math import ceil
from pathlib import Path

import render as R
import voiceover as V
from variance_squares import scenes
from core import DEFAULT_OUT, FPS, SKILL, disclaimer, fill_tree, load_json, save_json

sys.path.insert(0, str(SKILL / "qa"))
import check_banned
import check_format
import check_numbers
import report


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *map(str, args)], check=True)


def voice_tracks(intro, work, engine):
    used, _ = V.probe_engine(engine, voice="male")
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
    return audio, V.VIENEU_LABEL if used == "vieneu" else used


def replace(source, out, engine):
    ep = load_json(SKILL / "episodes/04-variance-quiz.json")
    small, large = ep["deviations"]
    values = {"small": small, "large": large, "small_squared": small ** 2, "large_squared": large ** 2,
              "amplitude_ratio": large / small, "weight_ratio": (large / small) ** 2}
    formats = dict.fromkeys(values, "int")
    rendered = set()
    ep = fill_tree(ep, values, formats, rendered)
    intro = scenes(ep)
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
    save_json(out / "values.json", {"values": values, "formats": formats, "deviations_pp": [small, large]})
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
            "Giọng đọc quiz": used, "Nguồn hình quiz": "Hoạt họa ô vuông QuanTik vẽ bằng code",
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
    parser.add_argument("--voice-engine", choices=["auto", "vieneu", "gtts", "espeak", "silent"], default="auto")
    args = parser.parse_args()
    replace(args.source, args.out, args.voice_engine)
