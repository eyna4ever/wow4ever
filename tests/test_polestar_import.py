"""Tests for tools/polestar (synthetic fixtures only: no third-party data is stored in this repository)."""
import hashlib, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "polestar"))
import polestar_import as pi  # noqa: E402

PIN = pi.load_pin()
FRAME = {"ui_map": 1411, "map": 1, "area": 14, "minX": -1716.667, "minY": -7250.0, "maxX": 1808.333, "maxY": -1962.5, "source": "test"}
TABLES = {
    "quest": [{"id": 1, "title": "Alpha", "level": 2, "min_level": 1, "side": 2, "zone_area": 14},
              {"id": 2, "title": "Beta", "level": 3, "min_level": 1, "side": 2, "zone_area": 363},
              {"id": 3, "title": "Gamma", "level": 5, "min_level": 3, "side": 0, "zone_area": 14},
              {"id": 9, "title": "Elsewhere", "level": 30, "min_level": 25, "side": 1, "zone_area": 12}],
    "quest_start": [{"quest": 1, "kind": "npc", "id": 100}, {"quest": 2, "kind": "npc", "id": 100}, {"quest": 3, "kind": "object", "id": 500}],
    "quest_end": [{"quest": 1, "kind": "npc", "id": 101}, {"quest": 2, "kind": "npc", "id": 100}],
    "quest_objective": [{"quest": 1, "n": 1, "kind": "kill", "target": 102, "count": 8}, {"quest": 2, "n": 1, "kind": "item", "target": 700, "count": 4}],
    "quest_prereq": [{"quest": 2, "pre": 1, "mode": "all"}],
    "quest_reward": [{"quest": 2, "kind": "choice", "id": 701, "count": 1}, {"quest": 2, "kind": "rep", "id": 76, "count": 250}],
    "npc": [{"id": 100, "name": "Giver", "level_min": 10, "level_max": 10}, {"id": 101, "name": "Ender", "level_min": 5, "level_max": 6},
            {"id": 102, "name": "Boar", "level_min": 1, "level_max": 2}, {"id": 103, "name": "Far Dropper", "level_min": 40, "level_max": 41},
            {"id": 104, "name": "Near Dropper", "level_min": 4, "level_max": 4}],
    "object": [{"id": 500, "name": "Wanted Poster", "type": 2}],
    "item": [{"id": 700, "name": "Tusk", "quest_item": True}, {"id": 701, "name": "Belt"}],
    "item_source": [{"item": 700, "kind": "npc", "id": 103}, {"item": 700, "kind": "npc", "id": 104, "chance": 50}],
    "spawn": [{"kind": "npc", "id": 100, "map": 1, "n": 1, "x": -400.0, "y": -4700.0},
              {"kind": "npc", "id": 101, "map": 1, "n": 1, "x": -300.0, "y": -4600.0},
              {"kind": "npc", "id": 101, "map": 0, "n": 2, "x": -300.0, "y": -4600.0},
              {"kind": "npc", "id": 102, "map": 1, "n": 1, "x": 5000.0, "y": -4600.0},
              {"kind": "npc", "id": 104, "map": 1, "n": 1, "x": 0.0, "y": -5000.0},
              {"kind": "object", "id": 500, "map": 1, "n": 1, "x": -200.0, "y": -4650.0}],
    "step": [{"quest": 1, "n": 1, "id": "1:s:abcd", "action": "kill", "text": "Kill boars near the farm."}],
    "mechanic": [],
}


def make_db(tmp, client_build="1.60.1.70532", break_sha=None, licence_override=None):
    src = Path(tmp) / "forever-db"
    (src / "data").mkdir(parents=True)
    res = []
    for name, rows in TABLES.items():
        rel = f"data/{name}.jsonl"
        p = src / rel
        p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if break_sha == rel:
            h = "0" * 64
        lic = (licence_override or {}).get(rel, PIN["allowed"][rel])
        res.append({"path": rel, "hash": "sha256:" + h, "licenses": [{"name": lic}]})
    (src / "datapackage.json").write_text(json.dumps({"resources": res}))
    (src / "index.json").write_text(json.dumps({"dataset": PIN["dataset"], "version": PIN["version"], "clientBuild": client_build}))
    return src


OURS_Q = [[1, "Alpha", "Durotar", 2, 1, "H", 0], [2, "Beta (old name)", "Durotar", 3, 1, "H", 0], [77, "Ours only", "Durotar", 4, 1, "H", 0]]
OURS_N = {"giver": {"id": 100, "name": "Giver", "level": "10"}, "ender": {"id": 101, "name": "Ender", "level": "5\u20136"}}


class VerifyTests(unittest.TestCase):
    def test_ok(self):
        with tempfile.TemporaryDirectory() as t:
            v = pi.verify(make_db(t), PIN)
            self.assertEqual(set(v["files"]), set(PIN["allowed"]))

    def test_refuses_classic_build(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(pi.ImportError_, "not WoW Forever"):
                pi.verify(make_db(t, client_build="1.15.9.70576"), PIN)

    def test_refuses_bad_sha(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(pi.ImportError_, "sha256"):
                pi.verify(make_db(t, break_sha="data/npc.jsonl"), PIN)

    def test_refuses_changed_licence(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(pi.ImportError_, "licence"):
                pi.verify(make_db(t, licence_override={"data/quest.jsonl": "LicenseRef-AllRightsReserved"}), PIN)

    def test_refuses_table_not_allowed(self):
        with tempfile.TemporaryDirectory() as t:
            src = make_db(t)
            for name in ("ui_map", "note", "secret"):
                with self.assertRaises(pi.ImportError_):
                    pi.read_table(src, PIN, name)

    def test_excluded_sources_are_documented(self):
        for k in ("addon/Polestar_QuestDB", "addon/Polestar_ItemDB/Items.lua", "guides/"):
            self.assertIn(k, PIN["excluded"])
            self.assertNotIn(k, PIN["allowed"])


class StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.src = make_db(cls.tmp.name)
        cls.st = pi.stage(cls.src, PIN, 14, FRAME, OURS_Q, OURS_N, {"701": "Ceinture"}, parents={363: 14, 12: 0})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_zone_and_sub_areas_only(self):
        self.assertEqual([q["id"] for q in self.st["quests"]], [1, 2, 3])

    def test_every_record_has_provenance_and_is_unconfirmed(self):
        for kind in ("quests", "npcs", "objects", "items"):
            for r in self.st[kind]:
                self.assertEqual(r["status"], "a-confirmer")
                self.assertEqual(r["origin"], "third-party")
                p = r["provenance"]
                self.assertEqual(p["source"], "polestar-forever-db")
                self.assertEqual(p["commit"], PIN["commit"])
                self.assertRegex(p["sha256"], r"^[0-9a-f]{64}$")
                self.assertIn(p["licence"], ("GPL-3.0-only", "CC-BY-4.0"))

    def test_dedupe(self):
        q = {r["id"]: r["dedupe"] for r in self.st["quests"]}
        self.assertEqual(q[1]["status"], "doublon-identique")
        self.assertEqual(q[2]["status"], "doublon-conflit")
        self.assertEqual(q[2]["conflicts"][0], {"field": "title_en", "wowkipedia": "Beta (old name)", "polestar": "Beta"})
        self.assertEqual(q[3]["status"], "nouveau")
        n = {r["id"]: r["dedupe"]["status"] for r in self.st["npcs"]}
        self.assertEqual(n[100], "doublon-identique")
        self.assertEqual(n[101], "doublon-identique")  # en dash in our level is normalised
        self.assertEqual(self.st["report"]["ours_quests_in_zone_not_in_polestar"], [77])

    def test_chains_rewards_and_steps(self):
        q = {r["id"]: r for r in self.st["quests"]}
        self.assertEqual(q[1]["next"], [2])
        self.assertEqual(q[2]["prereq"], [{"pre": 1, "mode": "all"}])
        self.assertIn({"kind": "choice", "id": 701, "count": 1}, q[2]["rewards"])
        self.assertEqual(q[1]["steps_en"], ["Kill boars near the farm."])
        self.assertEqual(q[1]["steps_provenance"]["licence"], "CC-BY-4.0")

    def test_points_inside_frame_and_map_only(self):
        n = {r["id"]: r for r in self.st["npcs"]}
        self.assertEqual(len(n[101]["points"]), 1)  # the map-0 spawn is ignored
        self.assertEqual(n[102]["points"], [])      # outside the frame
        for r in self.st["npcs"] + self.st["objects"]:
            for x, y in r["points"]:
                self.assertTrue(0 <= x <= 100 and 0 <= y <= 100)

    def test_far_dropper_left_out(self):
        ids = {r["id"] for r in self.st["npcs"]}
        self.assertIn(104, ids)
        self.assertNotIn(103, ids)

    def test_french_item_names_are_client_data(self):
        it = {r["id"]: r for r in self.st["items"]}
        self.assertEqual(it[701]["name_fr"], "Ceinture")
        self.assertEqual(it[701]["name_fr_provenance"]["source"], "client")
        self.assertNotIn("name_fr", it[700])
        self.assertEqual(it[701]["dedupe"]["status"], "doublon-identique")
        self.assertEqual(it[700]["dedupe"]["status"], "nouveau")

    def test_diff(self):
        new = json.loads(json.dumps(self.st))
        new["meta"]["version"] = "2026.12.1"
        new["quests"][0]["level"] = 4
        new["quests"].pop()
        new["items"].append({"id": 999, "name_en": "New"})
        d = pi.diff(self.st, new)
        self.assertEqual(d["kinds"]["quests"]["removed"], [3])
        self.assertEqual(d["kinds"]["quests"]["changed"], [{"id": 1, "fields": ["level"]}])
        self.assertEqual(d["kinds"]["items"]["added"], [999])

    def test_render_preserves_page_and_respects_rules(self):
        page = ('<html><head><title>x</title></head><body><section class="article-section" id="quetes-liste">KEEP-ME</section>'
                '<section class="article-section" id="historique-des-corrections">h</section>'
                '<section class="article-section sources-block" id="sources"><ol class="source-list"><li id="source-1">s</li></ol></section></body></html>')
        with tempfile.TemporaryDirectory() as t:
            info = pi.render(self.st, PIN, page, t, [f"t{i}.webp" for i in range(12)])
            out = (Path(t) / "index.html").read_text()
            self.assertIn("KEEP-ME", out)
            self.assertEqual(info["source_no"], 2)
            self.assertIn('id="source-2"', out)
            self.assertIn('id="carte-interactive"', out)
            self.assertIn("À confirmer", out)
            self.assertNotRegex(out, r"\sstyle=")              # CSP style-src 'self'
            self.assertNotRegex(out, r"<script(?![^>]*\bsrc=)")  # CSP script-src 'self'
            body = re.sub(r'<li id="source-\d+">.*?</li>', "", out, flags=re.S)
            body = re.sub(r"<[^>]+>", " ", body)
            for name in ("Polestar", "QuestieDB", "pfQuest", "CMaNGOS", "EG Link", "github"):
                self.assertNotIn(name, body, f"third-party name {name!r} in page text")
            payload = json.loads((Path(t) / info["map_json"]).read_text())
            self.assertEqual(payload["status"], "a-confirmer")
            self.assertTrue(payload["pins"])

    def test_credits_page_honours_licences(self):
        html = pi.credits_page(PIN, PIN["version"], PIN["commit"], "data.json")
        for need in ("GPL", "CC BY 4.0", "pfQuest", "Eric Mauser", "Efficient Games", PIN["commit"], 'href="data.json"', "noindex"):
            self.assertIn(need, html)


class FrontEndTests(unittest.TestCase):
    def test_map_js_is_csp_safe(self):
        js = (ROOT / "tools" / "polestar" / "frontend" / "wk-map.js").read_text()
        self.assertNotRegex(js, r"innerHTML|eval\(|new Function|https?://|setAttribute\('style'")
        css = (ROOT / "tools" / "polestar" / "frontend" / "wk-map.css").read_text()
        self.assertNotRegex(css, r"@import|url\(\s*['\"]?https?:")


if __name__ == "__main__":
    unittest.main()
