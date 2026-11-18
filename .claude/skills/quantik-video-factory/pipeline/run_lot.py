"""Render many episode JSONs in parallel worker processes (one batch.py per episode), resumable.

  python run_lot.py --dir ../episodes/yt-shorts --jobs 3 --voice male --env QT_PITCH=-10Hz
  python run_lot.py --dir ../episodes/yt-shorts --voice male --env QT_PITCH=-10Hz --env QT_RATE=+6%
Skips episodes whose social-output/<id>/qa_report.md already says ĐẠT. Writes <dir>/_lot.json.
"""
import argparse, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core import DEFAULT_OUT  # noqa: E402


def run(p, a, env):
    ep = json.loads(Path(p).read_text(encoding="utf-8"))
    out = Path(a.out) / ep["id"]
    rep = out / "qa_report.md"
    done = out / ("final.mp4" if ep["style"] != "carousel" else "captions.md")
    if rep.exists() and "Kết luận: ĐẠT" in rep.read_text(encoding="utf-8") and done.exists():
        return ep["id"], "skip", 0
    cmd = [sys.executable, "batch.py", "--episode", str(p), "--out", a.out, "--voice", a.voice, "--scale", str(a.scale)]
    if a.no_log:
        cmd.append("--no-log")
    log = Path(a.out) / "_logs"; log.mkdir(parents=True, exist_ok=True)
    with open(log / f"{ep['id']}.log", "w") as fh:
        r = subprocess.run(cmd, cwd=HERE, env=env, stdout=fh, stderr=subprocess.STDOUT)
    print(("OK  " if r.returncode == 0 else "FAIL") + " " + ep["id"], flush=True)
    return ep["id"], "ok" if r.returncode == 0 else "fail", r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--voice", default="female"); ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--env", action="append", default=[]); ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--no-log", action="store_true")
    a = ap.parse_args()
    env = dict(os.environ, MPLBACKEND="Agg")
    for kv in a.env:
        k, v = kv.split("=", 1); env[k] = v
    eps = sorted(p for p in Path(a.dir).glob("*.json") if not p.name.startswith("_"))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda p: run(p, a, env), eps))
    Path(a.out, f"_lot-{Path(a.dir).name}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"ok": sum(r[1] in ("ok", "skip") for r in res), "fail": [r[0] for r in res if r[1] == "fail"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
