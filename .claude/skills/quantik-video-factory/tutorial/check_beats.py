"""Quét lời thoại + tiêu đề trong beats.py theo danh sách cụm cấm ở brand/compliance.md. Thoát mã 1 nếu dính."""
import importlib.util, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
bf = os.environ.get("BEATS_FILE") or os.path.join(here, "beats.py")
sp = importlib.util.spec_from_file_location("beats", bf); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
comp = open(os.path.join(here, "..", "brand", "compliance.md"), encoding="utf-8").read()
banned = [l.strip() for l in comp.split("```text")[1].split("```")[0].splitlines() if l.strip()]
text = " ".join(b[1] + " " + b[2] for b in m.BEATS).lower()
hits = [w for w in banned if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text)]
print("Cụm cấm:", hits or "không có"); sys.exit(1 if hits else 0)
