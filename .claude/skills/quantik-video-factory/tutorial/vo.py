import asyncio, json, subprocess
from tts import go
import importlib.util as _iu, os as _o
_bf = _o.environ.get("BEATS_FILE") or _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), "beats.py")
_sp = _iu.spec_from_file_location("beats", _bf); _bm = _iu.module_from_spec(_sp); _sp.loader.exec_module(_bm); BEATS = _bm.BEATS
os = _o; os.makedirs("vo", exist_ok=True)
async def main():
    for i, b in enumerate(BEATS):
        import os
        if os.path.exists(f"vo/{i:02d}.mp3") and os.path.getsize(f"vo/{i:02d}.mp3")>1000: continue
        for t in range(4):
            try: await go(b[2], f"vo/{i:02d}.mp3"); break
            except Exception as e: print(i, t, e); await asyncio.sleep(2)
asyncio.run(main())
d=[float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"vo/{i:02d}.mp3"],capture_output=True,text=True).stdout) for i in range(len(BEATS))]
json.dump(d,open("vo/durs.json","w")); print(d, sum(d))
