"""Make one or many QuanTik videos: topic × style → final.mp4 + captions + QA report.

Examples
  python batch.py --topics garch --styles code-reel
  python batch.py --topics garch,hurst,kelly --styles kinetic-text,myth-buster --scale 0.5
  python batch.py --episode ../episodes/garch-myth.json
  python batch.py --topics var_cvar --styles code-reel --prices ~/data/FPT.csv   # real prices (column 'close')

Each episode = knowledge/models/<topic>.md video_defaults, overridden by styles/<style>/template.py DEFAULTS,
overridden by an episode JSON if given. Numbers in text use {key} / {key:fmt} placeholders filled from the
model run, so what is said always matches what the code computed.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
import json
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

import core as Core  # noqa: E402
from core import DEFAULT_OUT, KNOWLEDGE, STYLES, disclaimer, fill_tree, load_json, load_model_kb, save_json  # noqa: E402
from models import TOPICS, Model, load_returns  # noqa: E402
import broll as BR  # noqa: E402
import illustrations as ILL  # noqa: E402
import catalog as C  # noqa: E402
import term_topic as TT  # noqa: E402
import render as R  # noqa: E402
import voiceover as V  # noqa: E402
from assemble import assemble  # noqa: E402
import check_banned, check_format, check_numbers, report  # noqa: E402
import check_images, check_market, check_script, check_sources  # noqa: E402
import pillar_models as PM  # noqa: E402
import pillar_registry as PR  # noqa: E402

VI_CHARS = re.compile(r"[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]", re.I)
PLATFORMS = {k: v for k, v in load_json(HERE.parent / "platforms" / "profiles.json").items() if not k.startswith("_")}
STYLE_NAMES = sorted(p.name for p in STYLES.iterdir() if (p / "template.py").exists())
PILLAR_STYLES = {"bias-lab", "history-story", "market-brief", "decision-lab"}  # need pillar segments


def load_style(style):
    path = STYLES / style / "template.py"
    if not path.exists():
        raise SystemExit(f"unknown style {style!r}; styles: {STYLE_NAMES}")
    spec = importlib.util.spec_from_file_location(f"style_{style.replace('-', '_')}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def merge(*dicts):
    out = {}
    for d in dicts:
        for k, v in (d or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = merge(out[k], v)
            else:
                out[k] = v
    return out


def build_episode(topic, style, override=None):
    kb = load_model_kb(topic)
    mod = load_style(style)
    # lowest → highest priority: style defaults, topic defaults, topic×style overrides, episode JSON
    ep = merge(getattr(mod, "DEFAULTS", {}), {k: v for k, v in kb.items() if not k.startswith("_")},
               (kb.get("styles") or {}).get(style, {}), override or {})
    ep.pop("styles", None)
    ep["topic"], ep["style"] = topic, style
    ep.setdefault("id", f"{topic}-{style}")
    return ep, mod


def captions(ep, disc, platform=None):
    """captions.md: only the sections of `platform` (platforms/profiles.json), or every section if None."""
    tags = " ".join("#" + h.lstrip("#") for h in ep.get("hashtags", []))
    title = ep.get("title", ep["hook"])
    cap = ep.get("caption", ep["hook"])
    link, cta = ep.get("cta_link", ""), ep.get("cta", "")
    fb_link = link if link and link != cta else "quantik.io.vn"
    yt_title = (title[:90] + " #Shorts") if len(title) <= 90 else title[:88] + "… #Shorts"
    sections = {
        "tiktok": f"## TikTok\n{cap}\n\n{tags}\n\n{disc}\n",
        # Facebook = conversion: what you can do → link early → CTA
        "facebook": f"## Facebook\n{title}\n\n{cap}\n\n👉 {fb_link}\n\n{cta}\n\n{tags}\n\n{disc}\n",
        "instagram": f"## Instagram Reels\n{cap}\n\n{cta}\n\n{disc}\n\n{tags}\n",
        "instagram_en": f"## Instagram Reels (English)\n{cap}\n\n{cta}\n\n{disc}\n\n{tags}\n",
        "youtube": f"## YouTube Shorts\n**Tiêu đề:** {yt_title}\n\n**Mô tả:**\n{cap}\n\n{link}\n{cta}\n\n{disc}\n\n{tags} #Shorts\n",
        # English Shorts: English labels, no Vietnamese hashtags unless the episode gives them
        "youtube_en": f"## YouTube Shorts (English)\n**Title:** {yt_title}\n\n**Description:**\n{cap}\n\n{cta}\n\n{disc}\n\n{tags} #Shorts\n",
    }
    keys = PLATFORMS[platform]["captions"] if platform else list(sections)
    head = f"# Caption — {ep['id']}" + (f" ({PLATFORMS[platform]['name']})" if platform else "")
    return head + "\n\n" + "\n".join(sections[k] for k in keys)


def log_episode(ep, out_dir, status, duration, platform=None):
    path = KNOWLEDGE / "episodes.csv"
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["id", "date", "topic", "style", "title", "hook", "duration_s", "status", "file",
                        "views_tiktok", "views_reels", "views_youtube", "notes"])
        w.writerow([ep["id"], dt.date.today().isoformat(), ep["topic"], ep["style"], ep.get("title", ""), ep["hook"],
                    f"{duration:.0f}", status, str(out_dir), "", "", "",
                    "; ".join(x for x in (f"platform={platform}" if platform else "",
                                          f"pillar={ep['pillar']}" if ep.get("pillar") else "") if x)])


# Thẻ cuối mọi video: kêu gọi theo dõi kênh (yêu cầu của chủ sản phẩm, áp dụng cho mọi video).
# Episode muốn CTA khác (video quảng bá) thì ghi "cta" trong episode JSON. CTA tính năng cũ chuyển xuống caption.
FOLLOW_CTA = "Thả tim và theo dõi QuanTik để học một kiến thức quant mỗi ngày"


def _follow_cta(ep, override, platform=None):
    ep["cta_link"] = ep.get("cta_link") or ep.get("cta", "")
    if not (override or {}).get("cta"):
        ep["cta"] = PLATFORMS[platform]["cta"] if platform else FOLLOW_CTA
    return ep


def check_platform(platform, style, override):
    """None if topic × style may be made for this platform, else the reason (see platforms/<name>/README.md)."""
    if not platform:
        return None
    prof = PLATFORMS.get(platform)
    if prof is None:
        return f"unknown platform {platform!r}; choose {sorted(PLATFORMS)}"
    if style not in prof["styles"]:
        return f"{prof['name']} không dùng style {style} (được dùng: {', '.join(prof['styles'])}). Xem platforms/{platform}/README.md"
    if prof.get("requires_episode") and not override:
        return prof.get("requires_episode_reason", f"{prof['name']} cần episode JSON")
    return None


def prepare(topic, style, override=None, returns=None, platform=None):
    why = check_platform(platform, style, override)
    if why:
        raise SystemExit(why)
    ep, mod, model = _prepare(topic, style, override, returns)
    if platform:
        if not (override or {}).get("id"):
            ep["id"] = f"{ep['id']}-{platform}"
        ep["max_seconds"] = PLATFORMS[platform].get("max_seconds", ep.get("max_seconds", 60))  # platform decides
    return _follow_cta(ep, override, platform), mod, model


def _prepare(topic, style, override=None, returns=None):
    """(episode, style module, model) for a pillar topic, a hand-written topic or any catalog topic."""
    pil = None if (topic in TOPICS and not (override or {}).get("pillar")) else PR.resolve(topic, override)
    if pil:
        return _prepare_pillar(pil, topic, style, override or {}, returns)
    if style in PILLAR_STYLES:
        raise SystemExit(f"{style} dựng episode của trụ cột (pillars/registry.json), cần episode JSON có 'pillar' và "
                         f"'segments' — xem pillars/README.md")
    if topic in TOPICS:
        ep, mod = build_episode(topic, style, override)
        return ep, mod, Model(topic, ep.get("seed"), returns)
    entry = C.get(topic)
    if entry is None:
        raise SystemExit(f"unknown topic {topic!r}. Hand-written: {TOPICS}. Catalog: python catalog.py --list")
    mod = load_style(style)
    model = TT.TermModel(entry, (override or {}).get("seed"), returns)
    why = TT.supports(model, style)
    if why:
        raise SystemExit(f"{topic} × {style}: {why}")
    ep = merge(getattr(mod, "DEFAULTS", {}), TT.episode(entry, model), override or {})
    ep["topic"], ep["style"] = topic, style
    ep.setdefault("id", f"{topic}-{style}")
    return ep, mod, model


def attach_broll(scenes, ep, model, topic, disabled=False):
    """Give scenes real imagery. Episode "broll" may be a list of searches (cycled over scenes) or a dict
    {scene_name: search}; otherwise topic defaults + generic people/places. Returns the items used."""
    targets = [s for s in scenes if s.name != "end"]
    if disabled or not targets:
        return []
    # code-drawn illustrations (English branches by default, any video if the episode asks): every third scene,
    # starting with the second, so real photos stay the majority
    art = ep.get("art")
    family = getattr(model, "family", None) or topic
    if isinstance(art, dict):
        for s in targets:
            if art.get(s.name):
                s.bg = {"kind": "art", "motif": art[s.name]}
    elif art is not False and (art or Core.lang() == "en"):
        motifs = list(art or []) or ILL.TOPIC_ART.get(family, []) + ILL.GENERIC_ART
        for j, s in enumerate(targets[1::3]):
            s.bg = {"kind": "art", "motif": motifs[j % len(motifs)]}
    photo_targets = [s for s in targets if not s.bg]
    spec = ep.get("broll")
    defaults = BR.TOPIC_QUERIES.get(family, []) + BR.GENERIC
    if isinstance(spec, dict):
        order = [spec.get(s.name) for s in photo_targets]
        queries = [q for q in order if q] + defaults
    else:
        queries = list(spec or []) + defaults
    items, _ = BR.pick(queries, len(photo_targets)) if photo_targets else ([], [])
    if not items:
        return []
    for i, s in enumerate(photo_targets):
        it = items[i % len(items)]
        s.bg = dict(it, credit=BR.credit_line(it))
    return items


def imagery_check(scenes):
    """≥ 60% of scenes carry imagery (photo, B-roll or illustration) and ≥ 1/3 carry REAL photos/B-roll."""
    targets = [s for s in scenes if s.name != "end"]
    real = sum(1 for s in targets if s.bg and s.bg.get("kind") != "art")
    art = sum(1 for s in targets if s.bg and s.bg.get("kind") == "art")
    n = len(targets) or 1
    ok = (real + art) / n >= 0.6 and real / n >= 1 / 3
    msg = f"{real}/{len(targets)} cảnh ảnh thật/B-roll, {art} cảnh hình hoạ"
    return {"fail": not ok, "msg": msg + ("" if ok else " — THIẾU (cần ≥ 60% có hình, ≥ 1/3 ảnh thật; kiểm tra mạng tới Openverse/Pexels)")}


def contact_sheet(items, path):
    from PIL import Image
    thumbs = []
    for it in items:
        try:
            src = sorted(Path(it["frames"]).glob("*.jpg"))[0] if it.get("frames") else it["path"]
            im = Image.open(src).convert("RGB")
            thumbs.append(im.resize((max(1, int(300 * im.width / im.height)), 300)))
        except Exception:
            pass
    if thumbs:
        sheet = Image.new("RGB", (sum(t.width for t in thumbs), 300))
        x = 0
        for t in thumbs:
            sheet.paste(t, (x, 0)); x += t.width
        sheet.save(path, quality=85)


def _prepare_pillar(pil, topic, style, ov, returns):
    pillar, entry = pil
    if style not in pillar["styles"]:
        raise SystemExit(f"{topic} × {style}: trụ cột {pillar['id']} dùng các style {pillar['styles']}")
    mod = load_style(style)
    if style in PILLAR_STYLES and not ov.get("segments"):
        raise SystemExit(f"{topic} × {style}: cần episode JSON có 'segments' (python pillar.py scaffold …)")
    model = PM.make_model(ov.get("model") or entry.get("model"), ov.get("seed"), returns, ov)
    ep = merge(getattr(mod, "DEFAULTS", {}), PR.episode_defaults(pillar, entry, ov), ov)
    ep["topic"], ep["style"], ep["pillar"] = topic, style, pillar["id"]
    ep.setdefault("id", f"{topic}-{style}")
    if isinstance(model, PM.MarketModel):
        r = model.report
        ep.setdefault("note", f"Dữ liệu: AGR datafeed · phiên {model.values['as_of']} · {r['data_status']}")
    return ep, mod, model


def _pillar_gates(filled, pillar, model, corpus):
    """Pre-render gates for pillar episodes: script structure, sources & fact-check, market discipline."""
    more = [("Kịch bản trụ cột", check_script.check(filled, pillar)),
            ("Nguồn & fact-check", check_sources.check(filled, pillar))]
    if isinstance(model, PM.MarketModel):
        more.append(("Dữ liệu thị trường", check_market.check(filled, model.report, pillar, corpus=corpus)))
    if pillar.get("require_entity_images") or filled.get("entities") or check_images.used_images(filled):
        more.append(("Ảnh nhân vật & bản quyền", check_images.check(filled, pillar.get("require_entity_images", False))))
    return more


def _write_provenance(out, filled, scenes, model, kind, pillar):
    """sources.md + storyboard.json + visual_assets.json: source references survive to the published package."""
    import pillar_scenes as PS

    led = PS.ledger()
    claims = {c["id"]: c for c in filled.get("claims", [])}
    t, board = 0.0, []
    for s in scenes:
        board.append({"name": s.name, "role": getattr(s, "role", None), "start": round(t, 2),
                      "duration": round(s.duration, 2), "say": s.say, "texts": [x for x in s.texts if x],
                      "label": getattr(s, "status", None), "claims": getattr(s, "claims", []),
                      "sources": getattr(s, "sources", []), "visual": getattr(s, "visual", None),
                      "audio": Path(s.audio).name if s.audio else None})
        t += s.duration if kind == "video" else 0
    save_json(out / "storyboard.json", {"id": filled["id"], "style": filled["style"], "pillar": filled.get("pillar"),
                                        "scenes": board})
    prov = (f"market_report {getattr(model, 'path', '')}" if isinstance(model, PM.MarketModel)
            else f"model {model.topic} seed {model.seed}" + (" (dữ liệu thật)" if model.real_data else " (mô phỏng)"))
    assets = [{"path": p.name, "kind": k, "provenance": prov} for p, k in
              [(out / "final.mp4", "video"), (out / "thumbnail.jpg", "thumbnail"), (out / "subtitles.srt", "subtitles")]
              if p.exists()]
    assets += [{"path": str(p.relative_to(out)), "kind": "slide", "provenance": prov} for p in sorted(out.glob("slides/*/*.png"))]
    import images as IMG

    imgs_used = []
    for s in scenes:
        imgs_used += [i for i in getattr(s, "images", []) if i not in imgs_used]
    iidx = IMG.index()
    assets += [{"path": f"knowledge/images/{iidx[i]['file']}", "kind": "still",
                "provenance": iidx[i].get("source_url") or iidx[i].get("generator", ""), "license": iidx[i]["license"]}
               for i in imgs_used if i in iidx]
    save_json(out / "visual_assets.json", {"id": filled["id"], "assets": assets})
    if not pillar:
        return ""
    used = []
    for s in filled.get("segments", []):
        for c in s.get("claims", []):
            if c not in used:
                used.append(c)
    lines = [f"# Nguồn — {filled['id']}", "", f"Trụ cột: {pillar['name']}", ""]
    if filled.get("brief"):
        lines.append(f"- Research brief: `{filled['brief']}`")
    if filled.get("factcheck"):
        lines.append(f"- Fact-check: `{filled['factcheck']}`")
    if filled.get("market_report"):
        lines.append(f"- Market report: `{filled['market_report']}`")
        for ds in model.report["bundle"]["datasets"]:
            lines.append(f"  - {ds['name']}: {ds['status']} · {ds.get('url', '')} · lấy lúc {ds.get('retrieved_at')} · "
                         f"{ds.get('period') or ''} {ds.get('error', '')}")
        for lim in model.report["limitations"]:
            lines.append(f"  - Giới hạn: {lim}")
    lines += ["", "| Claim | Trạng thái | Nội dung | Nguồn |", "| --- | --- | --- | --- |"]
    sids = []
    for cid in used:
        c = claims.get(cid, {})
        lines.append(f"| `{cid}` | {c.get('status')} | {c.get('text', '')} | {', '.join(c.get('source_ids', [])) or '—'} |")
        sids += [x for x in c.get("source_ids", []) if x not in sids]
    lines += ["", "## Tài liệu", ""]
    short = []
    for sid in sids:
        src = led.get(sid, {})
        ref = src.get("doi") and f"doi:{src['doi']}" or src.get("isbn") and f"ISBN {src['isbn']}" or src.get("url", "")
        lines.append(f"- **{src.get('cite_short', sid)}** — {', '.join(src.get('authors', []))}. *{src.get('title', '')}*. "
                     f"{src.get('venue', '')} {ref} (cấp {src.get('tier')})")
        short.append(f"{src.get('cite_short', sid)} {ref}".strip())
    if imgs_used:
        lines += ["", "## Ảnh", "", "| Ảnh | Loại | Chủ thể | Tác giả · giấy phép | Nguồn |", "| --- | --- | --- | --- | --- |"]
        for i in imgs_used:
            e = iidx.get(i, {})
            lines.append(f"| `{i}` | {e.get('kind')} | {e.get('subject')} | {e.get('author')} · {e.get('license')} | "
                         f"{e.get('source_url') or e.get('generator', '')} |")
    (out / "sources.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    credits = sorted({iidx[i]["credit"] for i in imgs_used if i in iidx})
    img_block = ("\n## Ảnh\n" + "\n".join("- " + c for c in credits) + "\n") if credits else ""
    return ("\n## Nguồn (dán vào mô tả YouTube / bình luận ghim)\n" + "\n".join("- " + x for x in short) + "\n"
            + img_block)


def make(topic, style, override=None, out_root=DEFAULT_OUT, engine="auto", voice="male-deep", music=None,
         scale=1.0, fps=30, returns=None, data_label=None, force=False, log=True, check_only=False, platform=None,
         no_broll=False):
    t_start = time.time()
    platform = (override or {}).get("platform") or platform
    Core.set_lang((override or {}).get("lang") or (PLATFORMS[platform].get("lang", "vi") if platform in PLATFORMS else "vi"))
    ep, mod, model = prepare(topic, style, override, returns, platform)
    out = Path(out_root) / ep["id"]
    work = out / "_work"
    work.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {ep['id']}  ({topic} × {style}) → {out}")

    save_json(out / "values.json", {"topic": topic, "seed": model.seed, "real_data": model.real_data,
                                    "values": model.values, "formats": model.formats, "code": model.code})
    rendered = set()
    # sourced facts can be used as {placeholders} too (pillar episodes: "{pgr}" → "0,148"); model values win on clashes
    for k, f in (ep.get("facts") or {}).items():
        if isinstance(f, dict) and k not in model.values:
            model.values[k] = str(f["value"])
    filled = fill_tree(ep, model.values, model.formats, rendered)
    disc = disclaimer()
    if data_label:
        data_label = data_label.replace("Dữ liệu thật: ", Core.L("real_note"))
    note = data_label or filled.get("note") or (Core.L("real_note") + filled.get("data_source", "CSV")
                                                if model.real_data else Core.L("sim_note"))
    ctx = {"tag": filled.get("tag", topic.upper()), "note": note, "disclaimer": disc, "out": out}
    save_json(out / "episode.filled.json", filled)

    result = mod.build(filled, model, ctx)
    kind = getattr(mod, "KIND", "video")

    # ---- pre-render QA on every word that will be heard or seen
    texts = result.get("texts", []) if isinstance(result, dict) else []
    scenes = result["scenes"] if isinstance(result, dict) else result
    corpus = [s.say for s in scenes] + [x for s in scenes for x in s.texts] + texts
    corpus += [filled.get("caption", ""), filled.get("title", "")]
    save_json(out / "narration.json", {"scenes": [{"name": s.name, "say": s.say, "texts": s.texts} for s in scenes],
                                       "extra": texts})
    pillar = PR.pillar_of(filled)
    lits = list(filled.get("allowed_literals", []))
    if pillar:  # citations ("Odean (1998)") and source titles on screen are sourced by the ledger itself
        import pillar_scenes as PS

        led = PS.ledger()
        lits += [c for s in scenes for c in getattr(s, "sources", [])]
        lits += [led[x]["title"] for c in filled.get("claims", []) for x in c.get("source_ids", []) if x in led]
        lits += [PS.credit_text(getattr(s, "images", [])) for s in scenes]   # "CC BY-SA 4.0" etc. come from the image ledger
    nums = check_numbers.check(corpus, model.values, model.formats, rendered, lits, filled.get("facts", {}))
    banned = check_banned.check(corpus, (pillar or {}).get("extra_banned", []))
    if Core.lang() == "en":  # English video: any Vietnamese left over from topic defaults is a bug
        vi = [t for t in corpus if t and VI_CHARS.search(t)]
        if vi:
            banned["fail"] = True
            banned["hits"] += [{"phrase": "(chữ tiếng Việt trong video tiếng Anh)", "in": t[:100]} for t in vi[:5]]
    more = _pillar_gates(filled, pillar, model, corpus) if pillar else []
    blocked = nums["fail"] or banned["fail"] or any(r["fail"] for _, r in more)
    if (blocked and not force) or check_only:
        ep_r = dict(ep, pillar=filled.get("pillar"))
        report.write(out, ep_r, nums, banned, None, more=more,
                     status="CHẶN TRƯỚC KHI RENDER" if blocked else "ĐẠT")
        print(report.summary(nums, banned, None, more))
        if check_only:
            print(f"  {'✗' if blocked else '✓'} pre-render QA only (--check-only) → {out/'qa_report.md'}")
            return {"id": ep["id"], "ok": not blocked, "out": str(out), "checked_only": True}
        print(f"  ✗ blocked — fix the episode text (see {out/'qa_report.md'}) or pass --force")
        return {"id": ep["id"], "ok": False, "out": str(out)}

    # ---- real imagery: every scene but the end card gets a photo / B-roll (rule: brand/identity.md › Hình ảnh thật)
    broll_items = attach_broll(scenes, filled, model, topic, no_broll)
    if broll_items:
        (out / "credits.md").write_text(BR.credits_md(broll_items), encoding="utf-8")
        contact_sheet(broll_items, out / "broll.jpg")

    # ---- voice
    used = "silent"; errors = []
    if kind == "video" and getattr(mod, "VOICE", True):
        used, errors = V.probe_engine(engine, voice)
        print(f"  voice engine: {used}" + (f"  (fallback; {errors[0]})" if errors and used != engine else ""))
    for i, s in enumerate(scenes):
        sec = V.estimate_seconds(s.say) if s.say else 0
        if used != "silent" and s.say:
            wav = work / f"{i:02d}-{s.name}.wav"
            u, sec, _ = V.synth(s.say, wav, used, voice)
            s.audio = str(wav) if u != "silent" else None
        s.duration = max(s.min_dur, sec + 0.45)
    if hasattr(mod, "after_timing"):
        mod.after_timing(scenes, filled, model, ctx)

    fmt = None
    if kind == "carousel":
        files = mod.export(scenes, filled, model, ctx)
        fmt = check_format.check_images(files, out / "layout.json")
        duration = 0
    else:
        silent = work / "video_silent.mp4"
        duration = R.render(scenes, silent, ctx["tag"], note, fps=fps, layout_path=out / "layout.json",
                            srt_path=out / "subtitles.srt", scale=scale)
        final = out / "final.mp4"
        assemble(silent, scenes, final, work, music=("none" if getattr(mod, "MUSIC", True) is False else music))
        R.still(scenes[0], scenes[0].duration * 0.9, ctx["tag"], note, out / "thumbnail.jpg")
        fmt = check_format.check_video(final, out / "layout.json", platform_max=filled.get("max_seconds", 60),
                                       expect_audio=True)
    imagery = imagery_check(scenes)
    if imagery["fail"]:
        fmt["fail"] = True
        fmt.setdefault("issues", []).append(imagery["msg"])
        if hasattr(mod, "export"):
            mod.export(scenes, filled, model, ctx)
    src_block = _write_provenance(out, filled, scenes, model, kind, pillar)
    cap_md = captions(filled, disc, platform)
    if broll_items:  # CC BY needs credit where the video is published: one short line per caption section
        names = sorted({BR.credit_line(it) for it in broll_items})
        label = "Images" if Core.lang() == "en" else "Ảnh"
        cap_md = cap_md.replace(disc, disc + f"\n\n{label}: " + "; ".join(names))
    (out / "captions.md").write_text(cap_md + src_block, encoding="utf-8")
    if used != "silent":  # a scene whose TTS call failed would otherwise ship with no voice and pass QA
        mute = [s.name for s in scenes if s.say and not s.audio]
        if mute:
            fmt["issues"].append(f"cảnh không có giọng đọc (TTS lỗi): {', '.join(mute)} — dựng lại")
            fmt["fail"] = True
    status = "ĐẠT" if not (blocked or fmt["fail"]) else "KHÔNG ĐẠT"
    report.write(out, dict(ep, pillar=filled.get("pillar")), nums, banned, fmt, status=status, more=more,
                 extra={"Hình ảnh thật": imagery["msg"],
                        "Giọng đọc": used + (" — " + "; ".join(errors) if errors else ""),
                        "Thời lượng": f"{duration:.1f}s",
                        "Thời gian dựng": f"{time.time() - t_start:.0f}s"})
    print(report.summary(nums, banned, fmt, more))
    if log:
        log_episode(filled, out, status, duration, platform)
    shutil.rmtree(work, ignore_errors=True)
    return {"id": ep["id"], "ok": status == "ĐẠT", "out": str(out), "voice": used, "duration": duration}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topics", default="")
    ap.add_argument("--styles", default="")
    ap.add_argument("--episode", action="append", default=[], help="episode JSON (needs topic + style)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--voice-engine", default="auto", choices=["auto"] + V.ENGINES)
    ap.add_argument("--voice", default="male-deep", help="male-deep (mặc định, nam trầm) | male | female | edge voice id")
    ap.add_argument("--music", default=None, help="path to a licensed track, or 'none'")
    ap.add_argument("--scale", type=float, default=1.0, help="0.5 = fast 540x960 preview")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--prices", help="CSV with a close column → real data instead of simulation")
    ap.add_argument("--data-source", help="label shown on screen for real data, e.g. 'FPT, HOSE, 2023–2025'")
    ap.add_argument("--force", action="store_true", help="render even if pre-render QA fails (never publish that)")
    ap.add_argument("--platform", choices=sorted(PLATFORMS),
                    help="tiktok | facebook | instagram | youtube-shorts: CTA, captions, allowed styles from platforms/profiles.json")
    ap.add_argument("--no-broll", action="store_true", help="skip real imagery (preview only: QA will fail it)")
    ap.add_argument("--no-log", action="store_true", help="do not append to knowledge/episodes.csv")
    ap.add_argument("--check-only", action="store_true", help="run every pre-render QA gate, write qa_report, do not render")
    a = ap.parse_args()

    returns = load_returns(a.prices) if a.prices else None
    jobs = []
    for p in a.episode:
        e = load_json(p)
        jobs.append((e["topic"], e["style"], e))
    topics = [t.strip() for t in a.topics.split(",") if t.strip()]
    if a.topics.strip() in ("all", "catalog"):
        topics = [t["id"] for t in C.load()["topics"] if t["kind"] != "field"]
    for t in topics:
        for s in filter(None, a.styles.split(",")):
            jobs.append((t.strip(), s.strip(), None))
    if not jobs:
        ap.error("give --topics and --styles, or --episode")
    results = []
    for topic, style, override in jobs:
        if a.data_source and override is not None:
            override.setdefault("data_source", a.data_source)
        try:
            results.append(make(topic, style, override, a.out, a.voice_engine, a.voice, a.music, a.scale, a.fps,
                                returns, ("Dữ liệu thật: " + a.data_source) if a.data_source else None, a.force,
                                not a.no_log, check_only=a.check_only, platform=a.platform, no_broll=a.no_broll))
        except SystemExit as ex:  # unsupported topic × style: report and keep going with the batch
            print(f"  ✗ {ex}")
            results.append({"id": f"{topic}-{style}", "ok": False, "error": str(ex)})
    print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
