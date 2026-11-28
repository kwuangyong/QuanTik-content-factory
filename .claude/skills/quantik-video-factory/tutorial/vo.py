import asyncio
import importlib.util
import json
import os
import subprocess
from pathlib import Path

from tts import VOICE, VOICE_LABEL, go


async def main():
    beats_path = os.environ.get("BEATS_FILE") or Path(__file__).with_name("beats.py")
    spec = importlib.util.spec_from_file_location("beats", beats_path)
    beats = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(beats)

    voice_dir = Path("vo")
    voice_dir.mkdir(exist_ok=True)
    marker = voice_dir / "voice.txt"
    reuse_audio = marker.is_file() and marker.read_text(encoding="utf-8") == VOICE_LABEL
    if not reuse_audio:
        marker.unlink(missing_ok=True)

    durations = []
    for i, beat in enumerate(beats.BEATS):
        output = voice_dir / f"{i:02d}.mp3"
        if not (reuse_audio and output.is_file() and output.stat().st_size > 1000):
            temporary = output.with_suffix(".tmp.mp3")
            try:
                for attempt in range(4):
                    try:
                        await go(beat[2], str(temporary))
                        break
                    except Exception as exc:
                        if VOICE == "male" or attempt == 3:
                            raise
                        print(i, attempt, exc)
                        await asyncio.sleep(2)
                temporary.replace(output)
            finally:
                temporary.unlink(missing_ok=True)

        duration = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(output)], text=True,
        )
        durations.append(float(duration))

    (voice_dir / "durs.json").write_text(json.dumps(durations), encoding="utf-8")
    marker.write_text(VOICE_LABEL, encoding="utf-8")
    print(durations, sum(durations))


if __name__ == "__main__":
    asyncio.run(main())
