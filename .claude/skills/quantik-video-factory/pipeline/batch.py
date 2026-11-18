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
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qa"))

from core import (DEFAULT_OUT, KNOWLEDGE, STYLES, TEMPO, L, set_lang, disclaimer, fill_tree, load_json,  # noqa: E402
                  load_model_kb, save_json, strip_marks)
import illustrate as I  # noqa: E402
import scenes as SC  # noqa: E402
from models import TOPICS, Model, load_returns  # noqa: E402
import catalog as C  # noqa: E402
import term_topic as TT  # noqa: E402
import render as R  # noqa: E402
import voiceover as V  # noqa: E402
from assemble import assemble  # noqa: E402
import check_banned, check_format, check_numbers, report  # noqa: E402
import check_images, check_market, check_script, check_sources  # noqa: E402
import pillar_models as PM  # noqa: E402
import pillar_registry as PR  # noqa: E402

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


def captions(ep, disc, credits=""):
    tags = " ".join("#" + h.lstrip("#") for h in ep.get("hashtags", []))
    hook = strip_marks(ep["hook"])
    title = strip_marks(ep.get("title", hook))
    # caption mở bằng chính câu hook (ragebait) để giữ người lướt feed, rồi mới tới nội dung
    cap = strip_marks(ep.get("caption", hook))
    if ep.get("caption_hook", True) and not cap.startswith(hook):
        cap = hook + "\n\n" + cap
    if credits:
        disc = disc + "\n\n" + credits
    yt_title = (title[:90] + " #Shorts") if len(title) <= 90 else title[:88] + "… #Shorts"
    return f"""# Caption — {ep['id']}

## TikTok
{cap}

{tags}

{disc}

## Facebook / Reels
{title}

{cap}

{('👉 ' + ep['cta_link'] + chr(10) + chr(10)) if ep.get('cta_link') else ''}{ep.get('cta', '')}

{tags}

{disc}

## YouTube Shorts
**Tiêu đề:** {yt_title}

**Mô tả:**
{cap}

{ep.get('cta_link', '')}\n{ep.get('cta', '')}

{disc}

{tags} #Shorts
"""


def log_episode(ep, out_dir, status, duration):
    path = KNOWLEDGE / "episodes.csv"
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["id", "date", "topic", "style", "title", "hook", "duration_s", "status", "file",
                        "views_tiktok", "views_reels", "views_youtube", "notes"])
        w.writerow([ep["id"], dt.date.today().isoformat(), ep["topic"], ep["style"], ep.get("title", ""), strip_marks(ep["hook"]),
                    f"{duration:.0f}", status, str(out_dir), "", "", "",
                    f"pillar={ep['pillar']}" if ep.get("pillar") else ""])


# Thẻ cuối mọi video: kêu gọi theo dõi kênh (yêu cầu của chủ sản phẩm, áp dụng cho mọi video).
# Episode muốn CTA khác (video quảng bá) thì ghi "cta" trong episode JSON. CTA tính năng cũ chuyển xuống caption.
FOLLOW_CTA = "Thả tim và theo dõi QuanTik để học một kiến thức quant mỗi ngày"


def _follow_cta(ep, override):
    ep["cta_link"] = ep.get("cta_link") or ep.get("cta", "")
    if not (override or {}).get("cta"):
        ep["cta"] = L("follow_cta")
    return ep


def prepare(topic, style, override=None, returns=None):
    ep, mod, model = _prepare(topic, style, override, returns)
    return _follow_cta(ep, override), mod, model


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
        return ep, mod, Model(topic, ep.get("seed"), returns, ep.get("params"))
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


def insert_cold_open(scenes, ep, kind, style):
    """Mở bằng chuyện kể (giáo sư vào casino, Titanic…) sau hook: mỗi câu một cảnh B-roll có hình khớp lời.
    ep["cold_open"] = [{"say": ..., "visual": tag | bỏ trống = tự khớp, "caption": chữ ngắn trên màn hình}]."""
    items = ep.get("cold_open") or []
    # story-mix tự xếp cảnh (loại "broll"): không chèn cold_open mặc định của chủ đề vào giữa câu chuyện riêng
    if kind != "video" or not items or style in ("talking-head-script", "meme-quant", "story-mix"):
        return scenes
    at = 1 if scenes and scenes[0].name == "hook" else 0
    extra = [SC.broll(it["say"], it.get("visual"), it.get("caption"), name=f"story{i + 1}", slot=i,
                      image=it.get("image"), label=it.get("label")) for i, it in enumerate(items)]
    for sc in extra:
        sc.optional = True
    return scenes[:at] + extra + scenes[at:]


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
    if not pillar:  # video thường: vẫn phải ghi công ảnh thật (CC BY/BY-SA bắt buộc)
        credits = sorted({iidx[i]["credit"] for i in imgs_used if i in iidx})
        return ("\n## Ảnh\n" + "\n".join("- " + c for c in credits) + "\n") if credits else ""
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


def make(topic, style, override=None, out_root=DEFAULT_OUT, engine="auto", voice=None, music=None,
         scale=1.0, fps=30, returns=None, data_label=None, force=False, log=True, check_only=False, broll_mode="auto"):
    t_start = time.time()
    # language must be set before the model's numbers are formatted and before the voice is chosen
    lang = (override or {}).get("lang")
    if lang is None and topic in TOPICS:
        lang = load_model_kb(topic).get("lang")
    set_lang(lang)
    ep, mod, model = prepare(topic, style, override, returns)
    I.configure(broll_mode, fetch=broll_mode != "draw", topic=getattr(model, "family", None) or topic,
                board=ep.get("board"))
    out = Path(out_root) / ep["id"]
    work = out / "_work"
    work.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {ep['id']}  ({topic} × {style}) → {out}")

    save_json(out / "values.json", {"topic": topic, "seed": model.seed, "params": getattr(model, "params", {}), "real_data": model.real_data,
                                    "values": model.values, "formats": model.formats, "code": model.code})
    # story-mix: hook thật là cảnh hook đầu tiên của episode, không phải hook mặc định của chủ đề
    first = (ep.get("scenes") or [{}])[0]
    if first.get("type") == "hook":
        ep["hook"] = first["text"]
    rendered = set()
    # sourced facts can be used as {placeholders} too (pillar episodes: "{pgr}" → "0,148"); model values win on clashes
    for k, f in (ep.get("facts") or {}).items():
        if isinstance(f, dict) and k not in model.values:
            model.values[k] = str(f["value"])
    filled = fill_tree(ep, model.values, model.formats, rendered)
    disc = disclaimer()
    note = data_label or filled.get("note") or (L("real_note") + filled.get("data_source", "CSV")
                                                if model.real_data else L("sim_note"))
    ctx = {"tag": filled.get("tag", topic.upper()), "note": note, "disclaimer": disc, "out": out}
    save_json(out / "episode.filled.json", filled)

    result = mod.build(filled, model, ctx)
    kind = getattr(mod, "KIND", "video")

    # ---- pre-render QA on every word that will be heard or seen
    texts = result.get("texts", []) if isinstance(result, dict) else []
    scenes = result["scenes"] if isinstance(result, dict) else result
    scenes = insert_cold_open(scenes, filled, kind, style)
    if isinstance(result, dict):
        result["scenes"] = scenes
    corpus = [s.say for s in scenes] + [x for s in scenes for x in s.texts] + texts
    corpus += [strip_marks(filled.get("caption", "")), strip_marks(filled.get("title", "")),
               strip_marks(filled.get("hook", ""))]  # caption mở bằng hook → QA cả dòng đó
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
        # nhịp nhanh: cảnh ngắn lại theo TEMPO, chỉ chừa khoảng thở rất ngắn sau lời
        s.duration = max(s.min_dur / TEMPO, sec + 0.3)
    # giữ dưới giới hạn nền tảng: bớt cảnh kể chuyện cuối (cold_open) trước, không bao giờ cắt nội dung chính
    limit = filled.get("max_seconds", 60) - 0.5
    while kind == "video" and sum(sc.duration for sc in scenes) > limit:
        story = [sc for sc in scenes if getattr(sc, "optional", False)]
        if not story:
            break
        print(f"  quá {limit + 0.5:.0f}s → bỏ cảnh {story[-1].name}")
        scenes.remove(story[-1])
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
        style_music = getattr(mod, "MUSIC", True)
        if style_music is False:
            music = "none"
        elif music is None and isinstance(style_music, str):
            music = style_music  # e.g. dark-story → "drone"
        assemble(silent, scenes, final, work, music=music)
        R.still(scenes[0], scenes[0].duration * 0.9, ctx["tag"], note, out / "thumbnail.jpg")
        fmt = check_format.check_video(final, out / "layout.json", platform_max=filled.get("max_seconds", 60),
                                       expect_audio=True)
        if hasattr(mod, "export"):
            mod.export(scenes, filled, model, ctx)
    src_block = _write_provenance(out, filled, scenes, model, kind, pillar)
    credits = __import__("broll").credit_line(I.USED)
    (out / "captions.md").write_text(captions(filled, disc, credits) + src_block, encoding="utf-8")
    if used != "silent":  # a scene whose TTS call failed would otherwise ship with no voice and pass QA
        mute = [s.name for s in scenes if s.say and not s.audio]
        if mute:
            fmt["issues"].append(f"cảnh không có giọng đọc (TTS lỗi): {', '.join(mute)} — dựng lại")
            fmt["fail"] = True
    status = "ĐẠT" if not (blocked or fmt["fail"]) else "KHÔNG ĐẠT"
    report.write(out, dict(ep, pillar=filled.get("pillar")), nums, banned, fmt, status=status, more=more, extra={
        "Giọng đọc": used + f" ({voice or V.DEFAULT_VOICE}, tốc độ {V.RATE})" + (" — " + "; ".join(errors) if errors else ""),
        "Ảnh thật / B-roll": credits or "không dùng — toàn bộ hình tự vẽ",
                                                                   "Thời lượng": f"{duration:.1f}s",
                                                                   "Thời gian dựng": f"{time.time() - t_start:.0f}s"})
    print(report.summary(nums, banned, fmt, more))
    if log:
        log_episode(filled, out, status, duration)
    shutil.rmtree(work, ignore_errors=True)
    return {"id": ep["id"], "ok": status == "ĐẠT", "out": str(out), "voice": used, "duration": duration}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--topics", default="")
    ap.add_argument("--styles", default="")
    ap.add_argument("--episode", action="append", default=[], help="episode JSON (needs topic + style)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--voice-engine", default="auto", choices=["auto"] + V.ENGINES)
    ap.add_argument("--voice", default=V.DEFAULT_VOICE, help="male (mặc định: nam Bắc sáng) | male-deep | female | edge voice id; "
                                                           "episode \"lang\": \"en\" dùng giọng en-US cùng tên")
    ap.add_argument("--broll", default="auto", choices=["auto", "draw", "photo"],
                    help="auto = xen kẽ ảnh thật/video Pexels và hoạt hoạ tự vẽ; draw = chỉ vẽ; photo = ưu tiên ảnh thật")
    ap.add_argument("--music", default=None, help="path to a licensed track, 'drone' (synth dark bed), or 'none'")
    ap.add_argument("--scale", type=float, default=1.0, help="0.5 = fast 540x960 preview")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--prices", help="CSV with a close column → real data instead of simulation")
    ap.add_argument("--data-source", help="label shown on screen for real data, e.g. 'FPT, HOSE, 2023–2025'")
    ap.add_argument("--force", action="store_true", help="render even if pre-render QA fails (never publish that)")
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
                                not a.no_log, a.check_only, a.broll))
        except SystemExit as ex:  # unsupported topic × style: report and keep going with the batch
            print(f"  ✗ {ex}")
            results.append({"id": f"{topic}-{style}", "ok": False, "error": str(ex)})
    print("\n" + json.dumps(results, ensure_ascii=False, indent=2))
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
