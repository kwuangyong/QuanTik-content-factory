"""Gather one lot into a copy-paste sheet: path, duration, QA, voice and the platform caption of every video.

  python collect.py --dir ../episodes/yt-shorts --platform "YouTube Shorts" --title "50 YouTube Shorts"
  python collect.py --dir ../episodes/yt-shorts --platform "YouTube Shorts" --title "50 YouTube Shorts"
Writes social-output/<dir name>-ALL.md.
"""
import argparse, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from core import DEFAULT_OUT  # noqa: E402


def section(md, name):
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--platform", required=True); ap.add_argument("--title", default="")
    a = ap.parse_args()
    rows, body = [], []
    for p in sorted(q for q in Path(a.dir).glob("*.json") if not q.name.startswith("_")):
        ep = json.loads(p.read_text(encoding="utf-8"))
        out = DEFAULT_OUT / ep["id"]
        rep = (out / "qa_report.md").read_text(encoding="utf-8") if (out / "qa_report.md").exists() else ""
        st = re.search(r"Kết luận: ([^*]+)\*\*", rep); dur = re.search(r"Thời lượng: ([\d.]+)s", rep)
        voice = re.search(r"Giọng đọc: (\S+)", rep)
        st, dur, voice = (st.group(1).strip() if st else "CHƯA DỰNG"), (dur.group(1) if dur else "-"), (voice.group(1) if voice else "-")
        cap = (out / "captions.md").read_text(encoding="utf-8") if (out / "captions.md").exists() else ""
        filled = json.loads((out / "episode.filled.json").read_text(encoding="utf-8")) if (out / "episode.filled.json").exists() else {}
        title = filled.get("title", ep["id"])
        rows.append(f"| {ep['id']} | {title} | {dur}s | {st} | {voice} |")
        body.append(f"### {ep['id']} · {title}\n\n`social-output/{ep['id']}/final.mp4` · {dur}s · QA {st} · giọng {voice}\n\n"
                    f"Hook: {filled.get('hook', '')}\n\n```text\n{section(cap, a.platform)}\n```\n")
    head = f"# {a.title}\n\n| id | tiêu đề | thời lượng | QA | giọng |\n| --- | --- | --- | --- | --- |\n" + "\n".join(rows)
    dst = DEFAULT_OUT / f"{Path(a.dir).name}-ALL.md"
    dst.write_text(head + "\n\n## Caption từng video\n\n" + "\n".join(body), encoding="utf-8")
    print(dst, sum("ĐẠT" == r.split("|")[4].strip() for r in rows), "/", len(rows), "ĐẠT")


if __name__ == "__main__":
    main()
