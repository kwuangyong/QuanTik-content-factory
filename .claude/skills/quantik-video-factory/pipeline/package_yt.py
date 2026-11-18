"""Package rendered YT/IG episodes for hand-off: per-group folders (mp4 + thumbnail + caption.txt), ALL-CAPTIONS.md,
INDEX.md, then zips under 500 MB each (upload limit of chat attachments).

  python package_yt.py 43-55 59-70 73-76 79 --name yt-ig-lot-30     # episode numbers or ranges
"""
import json, os, shutil, glob, zipfile, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import DEFAULT_OUT, SKILL

def _nums(args):
    out = []
    for a in args:
        if "-" in a:
            x, y = a.split("-"); out += list(range(int(x), int(y) + 1))
        else:
            out.append(int(a))
    return out

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
NAME = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else "yt-ig-lot"
if "--name" in sys.argv:
    ARGS.remove(NAME)
SO = str(DEFAULT_OUT)
SK = str(SKILL)
OUT = f"{SO}/_zip/{NAME}"
chosen = _nums(ARGS)
ledger = {s["id"]: s for s in json.load(open(f"{SK}/knowledge/sources/ledger.json"))["sources"]}
imgs = {i["id"]: i for i in json.load(open(f"{SK}/knowledge/images/ledger.json"))["images"]}
disc = "Educational content about quantitative thinking, not financial advice or a recommendation to buy or sell any security. Model results depend on assumptions and data; past performance does not guarantee future results."
GROUPS = {"dark-truth": "1-dark-truth-finance", "poker": "2-poker-theory", "psychology": "3-psychology",
          "game-theory": "4-game-theory", "quant-mindset": "5-behavioral-econ-probability"}
shutil.rmtree(OUT, ignore_errors=True)
allcap, rows, missing = [], [], []
for n in chosen:
    d = glob.glob(f"{SO}/yt{n:02d}-*")
    if not d or not os.path.exists(f"{d[0]}/final.mp4"):
        missing.append(n); continue
    d = d[0]; slug = os.path.basename(d)
    ep = json.load(open(f"{d}/episode.filled.json"))
    qa = open(f"{d}/qa_report.md", encoding="utf-8").read()
    ok = "**Kết luận: ĐẠT**" in qa
    dur = re.search(r"Thời lượng: ([\d.]+)s", qa)
    sub = f"{OUT}/{GROUPS[ep['group']]}"
    os.makedirs(sub, exist_ok=True)
    shutil.copy(f"{d}/final.mp4", f"{sub}/{slug}.mp4")
    shutil.copy(f"{d}/thumbnail.jpg", f"{sub}/{slug}-thumbnail.jpg")
    tags = " ".join("#" + h.lstrip("#") for h in ep.get("hashtags", []))
    title = ep["title"]
    yt_title = (title[:90] + " #Shorts") if len(title) <= 90 else title[:88] + "… #Shorts"
    srcs = []
    for c in ep.get("claims", []):
        for sid in c.get("source_ids", []):
            if sid in ledger and ledger[sid]["cite_short"] not in srcs:
                srcs.append(ledger[sid]["cite_short"])
    used = {s["image"] for s in ep["scenes"] if s.get("image")} | ({ep["thumb"]["image"]} if ep.get("thumb", {}).get("image") else set())
    credits = [imgs[i]["credit"].replace("Ảnh: ", "Photo: ") for i in sorted(used) if i in imgs and imgs[i]["kind"] == "photo"]
    tail = ""
    if srcs: tail += "\n\nSources: " + "; ".join(srcs)
    if credits: tail += "\n" + "\n".join(credits)
    body = f"{ep['hook']}\n\n{ep['caption']}\n\n{ep['cta']}{tail}\n\n{disc}"
    txt = f"""# {slug}  ({ep['tag']})

## YouTube Shorts
Title: {yt_title}

Description:
{body}

{tags} #Shorts

## Instagram Reels
{body}

{tags} #reels
"""
    open(f"{sub}/{slug}-caption.txt", "w", encoding="utf-8").write(txt)
    allcap.append(txt)
    rows.append(f"| {ep['tag']} | {slug} | {dur.group(1) if dur else '?'}s | {'PASS' if ok else 'CHECK'} | {len(credits)} |")
open(f"{OUT}/ALL-CAPTIONS.md", "w", encoding="utf-8").write("\n\n---\n\n".join(allcap))
open(f"{OUT}/INDEX.md", "w", encoding="utf-8").write("| # | file | duration | QA | real photos |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
print("missing", missing, "packaged", len(rows))
print("\n".join(r for r in rows if "CHECK" in r))

# zips under ~480 MB: split a group folder into numbered parts when needed
LIMIT = 480 * 1024 * 1024
for g in sorted(os.listdir(OUT)):
    gp = os.path.join(OUT, g)
    if not os.path.isdir(gp):
        continue
    files = sorted(os.listdir(gp)); part, size, k = [], 0, 1
    def flush(part, k):
        with zipfile.ZipFile(f"{SO}/_zip/{NAME}-{g}-part{k}.zip", "w", zipfile.ZIP_STORED) as z:
            for f in part:
                z.write(os.path.join(gp, f), f"{g}/{f}")
    for f in files:
        sz = os.path.getsize(os.path.join(gp, f))
        if part and size + sz > LIMIT:
            flush(part, k); part, size, k = [], 0, k + 1
        part.append(f); size += sz
    if part:
        flush(part, k)
with zipfile.ZipFile(f"{SO}/_zip/{NAME}-captions.zip", "w") as z:
    z.write(f"{OUT}/ALL-CAPTIONS.md", "ALL-CAPTIONS.md"); z.write(f"{OUT}/INDEX.md", "INDEX.md")
print("zips in", f"{SO}/_zip/")
