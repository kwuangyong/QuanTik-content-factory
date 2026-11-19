"""Package rendered YT/IG episodes for hand-off: per-group folders (mp4 + thumbnail + caption.txt), ALL-CAPTIONS.md,
INDEX.md, then zips under ~370 MB each (chat attachment limit 400 MB).

  python package_yt.py 43-55 59-70 73-76 79 --name yt-ig-lot-30     # episode numbers or ranges
  add --plain: flat folder, file names without episode number or category (for posting as standalone videos)
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
PLAIN = "--plain" in sys.argv
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
    name = re.sub(r"^yt\d+-", "", slug) if PLAIN else slug
    ep = json.load(open(f"{d}/episode.filled.json"))
    qa = open(f"{d}/qa_report.md", encoding="utf-8").read()
    ok = "**Kết luận: ĐẠT**" in qa
    dur = re.search(r"Thời lượng: ([\d.]+)s", qa)
    sub = OUT if PLAIN else f"{OUT}/{GROUPS[ep['group']]}"
    os.makedirs(sub, exist_ok=True)
    shutil.copy(f"{d}/final.mp4", f"{sub}/{name}.mp4")
    shutil.copy(f"{d}/thumbnail.jpg", f"{sub}/{name}-thumbnail.jpg")
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
    import clips as CL
    for sc in ep["scenes"]:
        k = sc.get("clip")
        if k and k in CL.manifest()["clips"]:
            c = CL.manifest()["clips"][k]
            line = f"Video: {c['credit']} (Pexels) {c['page']}"
            if line not in credits:
                credits.append(line)
    if credits: tail += "\n" + "\n".join(credits)
    body = f"{ep['hook']}\n\n{ep['caption']}\n\n{ep['cta']}{tail}\n\n{disc}"
    head = f"# {name}" if PLAIN else f"# {slug}  ({ep['tag']})"
    txt = head + f"""

## YouTube Shorts
Title: {yt_title}

Description:
{body}

{tags} #Shorts

## Instagram Reels
{body}

{tags} #reels
"""
    open(f"{sub}/{name}-caption.txt", "w", encoding="utf-8").write(txt)
    allcap.append(txt)
    rows.append(f"| {ep['concept'] if PLAIN else ep['tag']} | {name} | {dur.group(1) if dur else '?'}s | {'PASS' if ok else 'CHECK'} | {len(credits)} |")
open(f"{OUT}/ALL-CAPTIONS.md", "w", encoding="utf-8").write("\n\n---\n\n".join(allcap))
open(f"{OUT}/INDEX.md", "w", encoding="utf-8").write("| # | file | duration | QA | real photos |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
print("missing", missing, "packaged", len(rows))
print("\n".join(r for r in rows if "CHECK" in r))

# zips under ~370 MB (chat attachment limit 400 MB); an episode's mp4 + thumbnail + caption always stay together
LIMIT = 370 * 1024 * 1024
groups = ["."] if PLAIN else sorted(x for x in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, x)))
for g in groups:
    gp = os.path.join(OUT, g)
    eps = sorted(f[:-4] for f in os.listdir(gp) if f.endswith(".mp4"))
    parts, cur, size = [], [], 0
    for e in eps:
        fs = [f for f in (f"{e}.mp4", f"{e}-thumbnail.jpg", f"{e}-caption.txt") if os.path.exists(os.path.join(gp, f))]
        sz = sum(os.path.getsize(os.path.join(gp, f)) for f in fs)
        if cur and size + sz > LIMIT:
            parts.append(cur); cur, size = [], 0
        cur.append((e, fs)); size += sz
    if cur:
        parts.append(cur)
    tagname = "" if g == "." else f"{g}-"
    for k, ps in enumerate(parts, 1):
        zname = f"{SO}/_zip/{NAME}-{tagname}{k}of{len(parts)}-{ps[0][0]}--to--{ps[-1][0]}.zip"
        with zipfile.ZipFile(zname, "w", zipfile.ZIP_STORED) as z:
            for e, fs in ps:
                for f in fs:
                    z.write(os.path.join(gp, f), f"{e}/{f}" if g == "." else f"{g}/{e}/{f}")
with zipfile.ZipFile(f"{SO}/_zip/{NAME}-0-ALL-CAPTIONS-and-INDEX.zip", "w") as z:
    z.write(f"{OUT}/ALL-CAPTIONS.md", "ALL-CAPTIONS.md"); z.write(f"{OUT}/INDEX.md", "INDEX.md")
print("zips in", f"{SO}/_zip/")
