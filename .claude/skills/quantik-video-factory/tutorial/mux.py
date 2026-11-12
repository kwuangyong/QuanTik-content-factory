"""Ghép video.mp4 (render.py) với từng câu thoại vo/NN.mp3 đặt đúng mốc thời gian, chuẩn hoá -15 LUFS."""
import json, subprocess
tl = json.load(open("out/timeline.json"))
ins, fl = [], []
for k, (st, dur, i) in enumerate(tl["timeline"]):
    ins += ["-i", f"vo/{i:02d}.mp3"]; ms = int(st * 1000)
    fl.append(f"[{k+1}:a]adelay={ms}|{ms}[a{k}]")
n = len(tl["timeline"])
fl.append("".join(f"[a{k}]" for k in range(n)) + f"amix=inputs={n}:normalize=0,apad,atrim=0:{tl['total']:.3f},loudnorm=I=-15:TP=-1.5[aout]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "out/video.mp4", *ins, "-filter_complex", ";".join(fl),
                "-map", "0:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-movflags", "+faststart", "out/final.mp4"], check=True)
print("out/final.mp4")
