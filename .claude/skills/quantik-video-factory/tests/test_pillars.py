"""Tests for the multi-pillar architecture. Run from the skill folder:

    python -m unittest discover -s tests -v                 # fast: no network, no video render (~20 s)
    QT_RENDER_TESTS=1 python -m unittest tests.test_pillars.RenderTests -v   # + real renders (~3 min)

Network-free by design: market tests use tests/fixtures (synthetic, fake tickers QTA…/QTB…) and an unreachable URL.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "pipeline"))
sys.path.insert(0, str(SKILL / "qa"))

import batch  # noqa: E402
import check_market  # noqa: E402
import check_script  # noqa: E402
import check_sources  # noqa: E402
import models  # noqa: E402
import pillar_models as PM  # noqa: E402
import pillar_registry as PR  # noqa: E402
from market import analyze as AN, editorial as ED, fetch as FE, script as SC  # noqa: E402
from market.common import ICT, sessions_behind  # noqa: E402

FIX = SKILL / "tests/fixtures"
EPISODES = {"behavioral-finance": "bf-disposition-bias-lab", "quant-history": "qh-thorp-history-story",
            "decision-science": "ds-ev-variance-decision-lab"}


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ep(name):
    return load(SKILL / "episodes" / f"{name}.json")


class Contracts(unittest.TestCase):
    def test_registry_matches_schema(self):
        for p in PR.pillars():
            self.assertEqual(check_script.validate(p, "content_pillar"), [], p["id"])
        self.assertEqual({p["id"] for p in PR.pillars()},
                         {"quant-education", "behavioral-finance", "market-intelligence", "quant-history", "decision-science",
                          "dark-truth"})

    def test_ledger_matches_schema_and_ids_unique(self):
        led = load(SKILL / "knowledge/sources/ledger.json")
        self.assertEqual(check_script.validate(led, "source_ledger"), [])
        ids = [s["id"] for s in led["sources"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_briefs_and_factchecks_match_schema(self):
        for name in EPISODES.values():
            self.assertEqual(check_script.validate(load(SKILL / f"research/{name}/brief.json"), "research_brief"), [])
            self.assertEqual(check_script.validate(load(SKILL / f"research/{name}/factcheck.json"), "factcheck"), [])

    def test_catalog_models_resolve(self):
        for p in PR.pillars():
            if p["id"] == "quant-education":
                continue
            for t in PR.catalog(p["id"]):
                m = t.get("model")
                self.assertTrue(m is None or m in PM.TOPICS or m in models.TOPICS or m == "market_snapshot", t["id"])

    def test_pillar_styles_exist(self):
        for p in PR.pillars():
            for s in p["styles"]:
                self.assertTrue((SKILL / "styles" / s / "template.py").exists(), s)


class DarkTruth(unittest.TestCase):
    """Pillar 5: English, animated dark-story; must stay separate from the quant registry and pass pre-render QA."""

    def test_episode_prepares_in_english_and_passes_gates(self):
        import core
        import check_banned, check_numbers, check_sources
        import make
        ep_json = make.resolve(load(SKILL / "episodes/escape-velocity.json"), "dark-story")
        self.assertEqual(ep_json["id"], "escape-velocity-dark-story")
        core.set_lang("en")
        try:
            ep, mod, model = batch.prepare(ep_json["topic"], ep_json["style"], ep_json)
            self.assertEqual(ep["pillar"], "dark-truth")
            self.assertNotIn("escape_velocity", models.TOPICS)
            rendered = set()
            filled = core.fill_tree(ep, model.values, model.formats, rendered)
            self.assertIn("2,000", filled["scenes"][6]["show"])          # English number format
            ctx = {"tag": "DARK TRUTH", "note": "", "disclaimer": core.disclaimer(), "out": Path(tempfile.mkdtemp())}
            scenes = mod.build(filled, model, ctx)
            corpus = [s.say for s in scenes] + [x for s in scenes for x in s.texts] + [filled["caption"]]
            self.assertFalse(check_numbers.check(corpus, model.values, model.formats, rendered)["fail"])
            self.assertFalse(check_banned.check(corpus)["fail"])
            self.assertFalse(check_sources.check(filled, PR.get("dark-truth"))["fail"])
        finally:
            core.set_lang("vi")


    def test_every_version_of_every_look_episode_resolves(self):
        import make
        for p in sorted((SKILL / "episodes").glob("*.json")):
            ep = load(p)
            for st in make.variants_of(ep):
                ov = make.resolve(ep, st)
                self.assertEqual(ov["style"], st)
                self.assertNotIn("variants", ov)
        lk = make.looks()["looks"]
        for name, l in lk.items():
            for key in ("pillar", "lang", "styles", "default_style", "tone", "content", "thumbnail"):
                self.assertIn(key, l, name)
            for st in l["styles"]:
                self.assertTrue((SKILL / "styles" / st / "template.py").exists(), st)


class BackwardCompat(unittest.TestCase):
    def test_hand_written_topic_unchanged(self):
        e, mod, m = batch.prepare("kelly", "kinetic-text")
        self.assertNotIn("pillar", e)
        self.assertEqual(e["id"], "kelly-kinetic-text")
        self.assertEqual(type(m), models.Model)

    def test_catalog_topic_unchanged(self):
        e, mod, m = batch.prepare("sortino", "carousel")
        self.assertNotIn("pillar", e)

    def test_models_registry_unchanged(self):
        self.assertEqual(models.TOPICS, ["garch", "hurst", "ou", "hmm", "monte_carlo", "sharpe", "sortino", "var_cvar", "kelly"])

    def test_pillar_style_refused_for_legacy_topic(self):
        with self.assertRaises(SystemExit):
            batch.prepare("garch", "bias-lab")

    def test_legacy_example_episode_still_checks(self):
        r = batch.make("sharpe", "myth-buster", ep("sharpe-myth-example"), tempfile.mkdtemp(), log=False, check_only=True)
        self.assertTrue(r["ok"])


class PillarModels(unittest.TestCase):
    def test_prospect_theory_breakeven(self):
        m = PM.Model("prospect_theory")
        self.assertAlmostEqual(m.values["g_min"], 2.25 ** (1 / 0.88), places=9)

    def test_ev_variance_matches_theory(self):
        v = PM.Model("ev_variance").values
        self.assertLess(abs(v["behind_10k"] - v["theory_10k"]), 0.03)
        self.assertLess(abs(v["behind_100k"] - v["theory_100k"]), 0.03)
        self.assertLessEqual(v["ruined"], v["ror"] + 0.03)   # finite horizon ≤ infinite-horizon formula

    def test_kuhn_poker_reaches_nash(self):
        v = PM.Model("kuhn_poker").values
        self.assertLess(abs(v["game_value"] + 1 / 18), 0.005)
        self.assertLess(abs(v["q_call"] - 1 / 3), 0.05)
        self.assertLess(abs(v["k_bet"] - 3 * v["j_bluff"]), 0.06)


class RepresentativeEpisodes(unittest.TestCase):
    """One episode per new research pillar passes every pre-render gate (numbers, banned, structure, sources)."""

    def test_each_pillar_episode_passes_pre_render_qa(self):
        for pillar, name in EPISODES.items():
            e = ep(name)
            r = batch.make(e["topic"], e["style"], e, tempfile.mkdtemp(), log=False, check_only=True)
            self.assertTrue(r["ok"], f"{pillar}: {r}")

    def test_pillar_episode_also_renders_in_legacy_style_shape(self):
        e = ep(EPISODES["behavioral-finance"])
        e2 = dict(e, style="carousel", id="bf-carousel-shape")
        filled, mod, model = batch.prepare(e2["topic"], "carousel", e2)
        self.assertEqual(len(filled["beats"]), 4)
        self.assertTrue(filled["symbols"])


class SourceTraceability(unittest.TestCase):
    def setUp(self):
        self.p = PR.get("quant-history")
        self.e = ep(EPISODES["quant-history"])

    def gate(self, e, fc=None):
        return check_sources.check(e, self.p, factcheck=fc)

    def test_baseline_passes(self):
        self.assertFalse(self.gate(self.e)["fail"])

    def test_unknown_source_id_fails(self):
        e = copy.deepcopy(self.e)
        e["claims"][0]["source_ids"] = ["no-such-source"]
        self.assertTrue(any("không có trong ledger" in i for i in self.gate(e)["issues"]))

    def test_documented_on_memoir_only_fails(self):
        e = copy.deepcopy(self.e)
        c = next(c for c in e["claims"] if c["id"] == "c_bs_self")
        c["status"] = "documented"          # upgrading Thorp's own account to a fact
        res = self.gate(e)
        self.assertTrue(res["fail"])

    def test_self_reported_without_hedge_fails(self):
        e = copy.deepcopy(self.e)
        seg = next(s for s in e["segments"] if s["role"] == "consequences")
        seg["say"] = seg["say"].replace("Theo lời kể của chính ông, ông", "Ông")
        self.assertTrue(any("không nói rõ" in i for i in self.gate(e)["issues"]))

    def test_rejected_factcheck_blocks(self):
        fc = load(SKILL / "research/qh-thorp-history-story/factcheck.json")
        fc["verdicts"][0]["verdict"] = "rejected"
        self.assertTrue(self.gate(self.e, fc)["fail"])

    def test_factcheck_status_mismatch_blocks(self):
        fc = load(SKILL / "research/qh-thorp-history-story/factcheck.json")
        next(v for v in fc["verdicts"] if v["claim"] == "c_bs_self")["status"] = "disputed"
        self.assertTrue(self.gate(self.e, fc)["fail"])

    def test_missing_factcheck_blocks(self):
        e = copy.deepcopy(self.e)
        e.pop("factcheck")
        self.assertTrue(self.gate(e)["fail"])

    def test_fact_without_ledger_source_fails(self):
        e = copy.deepcopy(self.e)
        e["facts"]["y_kelly"] = {"value": "1956", "source": "Wikipedia"}
        self.assertTrue(any("y_kelly" in i for i in self.gate(e)["issues"]))

    def test_segment_without_claim_fails(self):
        e = copy.deepcopy(self.e)
        e["segments"][1]["claims"] = []
        self.assertTrue(self.gate(e)["fail"])

    def test_hand_typed_number_blocked_end_to_end(self):
        e = ep(EPISODES["behavioral-finance"])
        e["segments"][2]["say"] += " Mã đã bán sau đó vượt mã giữ lại 3,41% một năm."   # the claim we rejected
        r = batch.make(e["topic"], e["style"], e, tempfile.mkdtemp(), log=False, check_only=True)
        self.assertFalse(r["ok"])

    def test_role_order_enforced(self):
        e = copy.deepcopy(ep(EPISODES["behavioral-finance"]))
        e["segments"][0], e["segments"][1] = e["segments"][1], e["segments"][0]
        self.assertTrue(check_script.check(e, PR.get("behavioral-finance"))["fail"])

    def test_decision_science_requires_analogy_breaks(self):
        e = copy.deepcopy(ep(EPISODES["decision-science"]))
        e["analogy"]["breaks"] = []
        self.assertTrue(check_script.check(e, PR.get("decision-science"))["fail"])


class MarketPipeline(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.pillar = PR.get("market-intelligence")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def bundle(self, history=None):
        b = self.root / "bundle-fixture"
        shutil.copytree(FIX / "market_snapshot", b)
        if history:
            shutil.copy(history, b / "history.csv")
            man = load(b / "manifest.json")
            man["datasets"].append({"name": "history", "source_id": "synthetic-fixture", "file": "history.csv", "status": "ok",
                                    "rows": 300, "retrieved_at": "2026-11-05T15:30:00+07:00", "period": "tổng hợp"})
            (b / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
        return b

    def report(self, now, **kw):
        return AN.analyze(self.bundle(**kw), now=now, data_root=self.root, sector_map=FIX / "market_snapshot/sector_map.json")

    def test_unavailable_data_is_marked_and_refused(self):
        b = FE.fetch(self.root, index_url="http://127.0.0.1:9/indexsnaps", skip_instruments=True, timeout=3, log=lambda *_: None)
        man = load(b / "manifest.json")
        self.assertEqual(man["datasets"][0]["status"], "failed")
        self.assertIn("error", man["datasets"][0])
        rep = AN.analyze(b, data_root=self.root)
        self.assertEqual(rep["data_status"], "unavailable")
        self.assertEqual(rep["observed"], {})            # nothing invented
        self.assertTrue(rep["limitations"])
        self.assertEqual(check_script.validate(rep, "market_report"), [])
        with self.assertRaises(ED.EditorialRefused):
            ED.draft(rep)
        self.assertTrue(check_market.check({"segments": [], "caption": "Giới hạn"}, rep, self.pillar)["fail"])

    def test_stale_data_requires_explicit_allow_and_label(self):
        now = dt.datetime(2026, 11, 12, 16, 0, tzinfo=ICT)      # 5 sessions after 05/11
        rep = self.report(now)
        self.assertEqual(rep["data_status"], "stale")
        self.assertEqual(rep["sessions_behind"], 5)
        with self.assertRaises(ED.EditorialRefused):
            ED.draft(rep)
        ed = ED.draft(rep, allow_stale=True)
        e = SC.build(rep, ed, "x.json", allow_stale=True)
        self.assertIn("dữ liệu cũ", e["segments"][0]["say"].lower())
        filled, _, model = self._fill(e, rep)
        res = check_market.check(filled, rep, self.pillar, now=now)
        self.assertFalse(res["fail"], res)
        filled["allow_stale"] = False
        self.assertTrue(check_market.check(filled, rep, self.pillar, now=now)["fail"])

    def test_fresh_fixture_passes_and_missing_regime_is_a_limitation(self):
        now = dt.datetime(2026, 11, 5, 16, 0, tzinfo=ICT)
        rep = self.report(now)
        self.assertEqual(rep["data_status"], "fresh")
        self.assertIsNone(rep["regime"])
        e = SC.build(rep, ED.draft(rep), "x.json")
        reg = next(s for s in e["segments"] if s["role"] == "regime")
        self.assertTrue(reg.get("limitation"))
        filled, _, _ = self._fill(e, rep)
        self.assertFalse(check_market.check(filled, rep, self.pillar, now=now)["fail"])
        self.assertEqual(rep["model"]["lead_sector"]["value"], "Nhóm A")   # 8-stock group up 2%
        self.assertNotIn("Nhóm C", [s["name"] for s in rep["sectors"]])    # < 5 traded members: not ranked

    def test_regime_with_history(self):
        now = dt.datetime(2026, 11, 5, 16, 0, tzinfo=ICT)
        up = self.report(now, history=FIX / "history_up.csv")
        self.assertEqual(up["regime"]["trend"], "xu hướng tăng")
        shutil.rmtree(self.root / "bundle-fixture")
        down = self.report(now, history=FIX / "history_down.csv")
        self.assertEqual(down["regime"]["trend"], "xu hướng giảm")

    def test_history_without_manifest_is_refused(self):
        b = FE.fetch(self.root, index_url="http://127.0.0.1:9/x", skip_instruments=True, timeout=2,
                     history=FIX / "history_up.csv", history_manifest=None, log=lambda *_: None)
        hist = next(d for d in load(b / "manifest.json")["datasets"] if d["name"] == "history")
        self.assertEqual(hist["status"], "failed")

    def test_ticker_and_certainty_language_blocked(self):
        now = dt.datetime(2026, 11, 5, 16, 0, tzinfo=ICT)
        rep = self.report(now)
        e = SC.build(rep, ED.draft(rep), "x.json")
        filled, _, _ = self._fill(e, rep)
        res = check_market.check(filled, rep, self.pillar, now=now, corpus=["Nhóm A dẫn đầu nhờ QTV."])
        self.assertTrue(any("mã cụ thể" in i for i in res["issues"]))
        import check_banned
        self.assertTrue(check_banned.check(["VN-INDEX sẽ tăng tuần tới"], self.pillar["extra_banned"])["fail"])
        self.assertFalse(check_banned.check(["Không ai biết chỉ số sẽ tăng hay giảm"], self.pillar["extra_banned"])["fail"])

    def test_sample_fixture_never_publishable(self):
        b = FE.fetch(self.root, fixture=FIX / "market_snapshot", log=lambda *_: None)
        rep = AN.analyze(b, now=dt.datetime(2026, 11, 5, 16, 0, tzinfo=ICT), data_root=self.root,
                         sector_map=FIX / "market_snapshot/sector_map.json")
        self.assertEqual(rep["data_status"], "sample")
        with self.assertRaises(ED.EditorialRefused):
            ED.draft(rep)

    def test_scenarios_need_confirmation_and_invalidation(self):
        now = dt.datetime(2026, 11, 5, 16, 0, tzinfo=ICT)
        rep = self.report(now)
        e = SC.build(rep, ED.draft(rep), "x.json")
        filled, _, _ = self._fill(e, rep)
        filled["scenarios"][0]["invalidation"] = []
        self.assertTrue(check_market.check(filled, rep, self.pillar, now=now)["fail"])

    def test_session_calendar(self):
        fri = dt.date(2026, 11, 13)
        self.assertEqual(sessions_behind(fri, dt.datetime(2026, 11, 15, 9, 0, tzinfo=ICT)), 0)   # Sunday
        self.assertEqual(sessions_behind(fri, dt.datetime(2026, 11, 16, 10, 0, tzinfo=ICT)), 0)  # Monday, open
        self.assertEqual(sessions_behind(fri, dt.datetime(2026, 11, 16, 15, 30, tzinfo=ICT)), 1)  # Monday closed

    def _fill(self, e, rep):
        p = self.root / "market_report.json"
        p.write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
        e["market_report"] = str(p)
        from core import fill_tree

        model = PM.MarketModel(p)
        return fill_tree(e, model.values, model.formats, set()), None, model


class Images(unittest.TestCase):
    """People/events named in an episode get a licensed photo or a labelled illustration; Commons licences are enforced."""

    def setUp(self):
        import check_images
        self.ci = check_images
        self.e = ep(EPISODES["quant-history"])

    def test_representative_episodes_cover_every_mention(self):
        for name in list(EPISODES.values()) + ["ds-kuhn-nash-decision-lab"]:
            self.assertFalse(self.ci.check(ep(name))["fail"], name)

    def test_undeclared_person_fails(self):
        e = copy.deepcopy(self.e)
        e["entities"] = [x for x in e["entities"] if x["name"] != "Jay Regan"]
        self.assertTrue(any("Regan" in i for i in self.ci.check(e)["issues"]))

    def test_short_waiver_fails(self):
        e = copy.deepcopy(self.e)
        e["entities"][-1]["waiver"] = "không"
        self.assertTrue(self.ci.check(e)["fail"])

    def test_declared_image_must_be_shown(self):
        e = ep("ds-kuhn-nash-decision-lab")           # Kuhn's card is shown only in the setup scene
        e["segments"][0].pop("visual")
        self.assertTrue(any("không cảnh nào hiện" in i for i in self.ci.check(e)["issues"]))

    def test_unknown_image_fails(self):
        e = copy.deepcopy(self.e)
        e["timeline"][0]["image"] = "no-such-image"
        self.assertTrue(self.ci.check(e)["fail"])

    def test_ledger_matches_schema(self):
        self.assertEqual(check_script.validate(load(SKILL / "knowledge/images/ledger.json"), "image_ledger"), [])

    def _fake_commons(self, license_name):
        import io

        meta = {"LicenseShortName": {"value": license_name}, "Artist": {"value": "<a>Jane Doe</a>"},
                "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0"}}
        info = {"query": {"pages": [{"title": "File:X.jpg", "imageinfo": [{"url": "https://upload.example/X.jpg",
                "thumburl": "https://upload.example/X.jpg", "descriptionurl": "https://commons.wikimedia.org/wiki/File:X.jpg",
                "extmetadata": meta}]}]}}

        class R(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *a): pass

        def opener(req, timeout=0):
            return R(json.dumps(info).encode() if "api.php" in req.full_url else b"\xff\xd8fakejpeg")
        return opener

    def _sandbox(self):
        import images
        d = Path(tempfile.mkdtemp())
        old = images.IMG_DIR, images.FILES, images.LEDGER
        images.IMG_DIR, images.FILES, images.LEDGER = d, d / "files", d / "ledger.json"
        self.addCleanup(lambda: setattr(images, "IMG_DIR", old[0]) or setattr(images, "FILES", old[1])
                        or setattr(images, "LEDGER", old[2]))
        return images

    def test_commons_free_licence_is_fetched_with_credit(self):
        images = self._sandbox()
        e = images.fetch("File:X.jpg", "x", "Someone", opener=self._fake_commons("CC BY-SA 4.0"))
        self.assertEqual(e["kind"], "photo")
        self.assertIn("CC BY-SA 4.0", e["credit"])
        self.assertIn("Jane Doe", e["credit"])
        self.assertTrue((images.IMG_DIR / e["file"]).exists())

    def test_commons_non_free_licence_refused(self):
        images = self._sandbox()
        for lic in ("CC BY-NC-SA 4.0", "CC BY-ND 2.0", "Fair use", ""):
            with self.assertRaises(SystemExit):
                images.fetch("File:X.jpg", "x", "Someone", opener=self._fake_commons(lic))

    def test_licence_classifier(self):
        import images
        for ok in ("Public domain", "PD-US", "CC0", "CC BY 2.0", "CC BY-SA 3.0", "CC BY-SA 4.0"):
            self.assertTrue(images.is_free(ok), ok)
        for bad in ("CC BY-NC 2.0", "CC BY-NC-ND 4.0", "Fair use", "All rights reserved"):
            self.assertFalse(images.is_free(bad), bad)


class Figures(unittest.TestCase):
    """Characters / props used by style defaults and episodes exist and render."""

    def _specs(self):
        out = []
        for st in ("bias-lab", "history-story", "decision-lab", "market-brief"):
            out += list(batch.load_style(st).SCENES.values())
        for name in list(EPISODES.values()) + ["ds-kuhn-nash-decision-lab"]:
            out += [s["visual"]["scene"] for s in ep(name)["segments"] if (s.get("visual") or {}).get("scene")]
        return out

    def test_every_scene_spec_is_valid_and_renders(self):
        import figures as G
        for spec in self._specs():
            for c in spec.get("cast", []):
                self.assertIn(c["who"], G.CHARACTERS); self.assertIn(c.get("pose", "stand"), G.POSES)
                self.assertIn(c.get("face", "neutral"), G.FACES)
            for pr in spec.get("props", []):
                self.assertIn(pr["what"], G.PROPS)
            im = G.stage(spec, 880, 456, 1.0, 1.0)
            self.assertEqual(im.size, (880, 456))
            self.assertGreater(im.getbbox()[3] - im.getbbox()[1], 100)   # something visible was drawn

    def test_bubble_text_reaches_qa(self):
        e = ep("ds-kuhn-nash-decision-lab")
        filled, mod, model = batch.prepare(e["topic"], e["style"], e)
        from pathlib import Path as _P
        scenes = mod.build(filled, model, {"tag": "T", "note": "", "disclaimer": "d", "out": _P(tempfile.mkdtemp())})
        self.assertTrue(any("Tôi bỏ" in t for s in scenes for t in s.texts))


class VisualsAuto(unittest.TestCase):
    """visuals.py auto: every name in the script gets an image (offline → illustration) placed where it is named."""

    def setUp(self):
        import images
        d = Path(tempfile.mkdtemp())
        shutil.copytree(images.IMG_DIR, d / "images")
        old = images.IMG_DIR, images.FILES, images.LEDGER
        images.IMG_DIR, images.FILES, images.LEDGER = d / "images", d / "images/files", d / "images/ledger.json"
        images.LEDGER.write_text(json.dumps({"version": 1, "images": []}))
        self.addCleanup(lambda: [setattr(images, k, v) for k, v in zip(("IMG_DIR", "FILES", "LEDGER"), old)])
        self.d = d

    def _bare(self, name):
        e = ep(name)
        e.pop("entities", None)
        for t in e.get("timeline", []):
            t.pop("image", None); t.pop("images", None)
        for s in e["segments"]:
            if (s.get("visual") or {}).get("kind") == "image":
                s.pop("visual")
            elif (s.get("visual") or {}).get("image"):
                s["visual"].pop("image")
        p = self.d / f"{name}.json"
        p.write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")
        return p

    def test_history_episode_rebuilt_from_nothing(self):
        import visuals
        r = visuals.auto(self._bare("qh-thorp-history-story"), write=True, offline=True, log=lambda *_: None)
        names = {ent["name"] for ent, in [(x[1],) for x in r["plan"]]}
        self.assertTrue({"Edward Thorp", "Jay Regan", "Myron Scholes", "Fischer Black"} <= names)
        issues = r["check"]["issues"]
        self.assertTrue(all("Bell Labs" in i for i in issues), issues)   # only the place with no slot is left

    def test_citation_author_gets_picture(self):
        import visuals
        p = self._bare("bf-disposition-bias-lab")
        r = visuals.auto(p, write=True, offline=True, log=lambda *_: None)
        self.assertFalse(r["check"]["fail"], r["check"])
        e = json.loads(p.read_text(encoding="utf-8"))
        ev = next(s for s in e["segments"] if s["role"] == "evidence")
        self.assertEqual(ev["visual"]["kind"], "citation")
        self.assertTrue(ev["visual"]["image"])

    def test_portrait_filter(self):
        import visuals
        self.assertTrue(visuals.NOT_PORTRAIT.search("File:Claude Shannon Centenary Logo.jpg"))
        self.assertFalse(visuals.NOT_PORTRAIT.search("File:ClaudeShannon MFO3807.jpg"))


class VoiceRetry(unittest.TestCase):
    """edge-tts fails intermittently (NoAudioReceived); one failed call must not leave a scene voiceless."""

    def test_transient_failures_are_retried(self):
        import voiceover as V

        calls = {"n": 0}

        def flaky(text, dst, voice, rate, pitch="+0Hz"):
            calls["n"] += 1
            if calls["n"] < 3:
                raise RuntimeError("NoAudioReceived")
            Path(dst).write_bytes(b"")

        orig, orig_sleep, orig_dur = V._edge, V.time.sleep, V.duration_of
        V._edge, V.time.sleep, V.duration_of = flaky, (lambda s: None), (lambda p: 1.0)
        try:
            used, sec, errs = V.synth("Xin chào.", Path(tempfile.mkdtemp()) / "a.wav", "edge")
        finally:
            V._edge, V.time.sleep, V.duration_of = orig, orig_sleep, orig_dur
        self.assertEqual(used, "edge")
        self.assertEqual(calls["n"], 3)
        self.assertEqual(len(errs), 2)


@unittest.skipUnless(os.environ.get("QT_RENDER_TESTS"), "set QT_RENDER_TESTS=1 to render videos")
class RenderTests(unittest.TestCase):
    def test_render_each_new_pillar_style(self):
        out = Path(tempfile.mkdtemp())
        for name in EPISODES.values():
            e = ep(name)
            r = batch.make(e["topic"], e["style"], e, out, engine="silent", scale=0.5, log=False)
            self.assertTrue(r["ok"], r)
            for f in ("final.mp4", "sources.md", "storyboard.json", "visual_assets.json", "qa_report.json"):
                self.assertTrue((out / name / f).exists(), f)
            qa = load(out / name / "qa_report.json")
            self.assertEqual(check_script.validate(qa, "qa_report"), [])
            self.assertEqual(check_script.validate(load(out / name / "storyboard.json"), "storyboard"), [])


if __name__ == "__main__":
    unittest.main()
