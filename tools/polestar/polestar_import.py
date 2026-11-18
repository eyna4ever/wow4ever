#!/usr/bin/env python3
"""Polestar forever-db importer for Wowkipedia (staging only, never publishes).

Subcommands:
  verify  --src DIR                      check the pinned commit/version, licences and sha256 of every allowed file
  stage   --src DIR --zone-area N --frame FRAME.json --out STAGING.json [--ours-quests F] [--ours-npcs F] [--items-fr F]
  diff    --old STAGING.json --new STAGING.json [--out REPORT.json]
  render  --staging STAGING.json --page ZONE.html --out-dir DIR      (sample pages in a TEST tree)

Rules (see docs/POLESTAR.md):
  * Only the tables listed under "allowed" in UPSTREAM.json are read; everything else is refused.
  * Every staged record carries a provenance block and status "a-confirmer"; Polestar data stays in
    its own staging file and never overwrites Wowkipedia / client data (duplicates are reported).
  * Forever only: the dataset's clientBuild must start with 1.60.1.
  * Python standard library only (no paid or external dependency).
"""
import argparse, hashlib, html, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN_FILE = HERE / "UPSTREAM.json"
SOURCE_ID = "polestar-forever-db"
MAX_POINTS = 40


class ImportError_(Exception):
    pass


def load_pin(path=PIN_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def git_head(src):
    try:
        r = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def verify(src, pin):
    """src = the forever-db folder. Returns {relpath: sha256}. Raises on any mismatch."""
    src = Path(src)
    index = json.loads((src / "index.json").read_text(encoding="utf-8"))
    pkg = json.loads((src / "datapackage.json").read_text(encoding="utf-8"))
    errors = []
    if not str(index.get("clientBuild", "")).startswith(pin["clientBuildPrefix"]):
        errors.append(f"clientBuild {index.get('clientBuild')!r} is not WoW Forever ({pin['clientBuildPrefix']}*)")
    if index.get("version") != pin["version"]:
        errors.append(f"version {index.get('version')!r} != pinned {pin['version']!r}")
    if index.get("dataset") != pin["dataset"]:
        errors.append(f"dataset {index.get('dataset')!r} != {pin['dataset']!r}")
    head = git_head(src)
    if head is not None and head != pin["commit"]:
        errors.append(f"upstream checkout is at {head}, pinned {pin['commit']}")
    res = {r["path"]: r for r in pkg.get("resources", [])}
    out = {}
    for rel, lic in pin["allowed"].items():
        r = res.get(rel)
        if r is None:
            errors.append(f"{rel}: not in datapackage.json")
            continue
        names = [l.get("name") for l in r.get("licenses", [])]
        if names != [lic]:
            errors.append(f"{rel}: licence {names} != expected {lic}")
        p = src / rel
        if not p.is_file():
            errors.append(f"{rel}: missing")
            continue
        h = sha256(p)
        want = r.get("hash") or r.get("sha256")
        if want and want.replace("sha256:", "") != h:
            errors.append(f"{rel}: sha256 {h} != datapackage {want}")
        out[rel] = h
    if errors:
        raise ImportError_("; ".join(errors))
    return {"files": out, "clientBuild": index["clientBuild"], "gitHead": head}


TABLES = ("quest", "quest_start", "quest_end", "quest_objective", "quest_prereq", "quest_reward", "npc", "object",
          "item", "item_source", "spawn", "step")


def read_tables(src, pin):
    return {n: read_table(src, pin, n) for n in TABLES}


def read_table(src, pin, name):
    rel = f"data/{name}.jsonl"
    if rel not in pin["allowed"]:
        raise ImportError_(f"{rel} is not an allowed table")
    with open(Path(src) / rel, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def frame_from_client(path, ui_map):
    """FRAME.json: our own export of UiMapAssignment rows (client 1.60.1.70862):
    {"build": "...", "rows": [{"UiMapID":1411,"MapID":1,"Region":[minX,minY,minZ,maxX,maxY,maxZ], ...}]}"""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    for r in d["rows"]:
        if r["UiMapID"] == ui_map and r.get("OrderIndex", 0) == 0:
            reg = r["Region"]
            return {"ui_map": ui_map, "map": r["MapID"], "area": r.get("AreaID"), "minX": reg[0], "minY": reg[1],
                    "maxX": reg[3], "maxY": reg[4], "source": f"client UiMapAssignment {d.get('build')}"}
    raise ImportError_(f"uiMap {ui_map} not in {path}")


def to_map_pct(frame, x, y):
    """World yards (x north, y west) -> map percent (0..100), or None when outside the map."""
    px = (frame["maxY"] - y) / (frame["maxY"] - frame["minY"])
    py = (frame["maxX"] - x) / (frame["maxX"] - frame["minX"])
    if 0 <= px <= 1 and 0 <= py <= 1:
        return [round(px * 100, 1), round(py * 100, 1)]
    return None


SIDE = {0: "both", 1: "alliance", 2: "horde"}
OURS_SIDE = {"A": "alliance", "H": "horde", "B": "both", "AH": "both"}


def zone_areas(zone_area, parents):
    """The zone and every sub-area under it (client AreaTable parent links)."""
    out = {zone_area}
    changed = True
    while changed:
        changed = False
        for a, p in parents.items():
            if p in out and int(a) not in out:
                out.add(int(a)); changed = True
    return out


def stage(src, pin, zone_area, frame, ours_quests=None, ours_npcs=None, items_fr=None, verified=None, parents=None, items_en=None, tables=None):
    verified = verified or verify(src, pin)
    areas = zone_areas(zone_area, {int(k): int(v) for k, v in (parents or {}).items()})
    T = tables or {n: read_table(src, pin, n) for n in ("quest", "quest_start", "quest_end", "quest_objective", "quest_prereq",
                                              "quest_reward", "npc", "object", "item", "item_source", "spawn", "step")}
    quests = {q["id"]: q for q in T["quest"] if q.get("zone_area") in areas}
    allq = {q["id"]: q for q in T["quest"]}

    def by_quest(rows):
        m = {}
        for r in rows:
            if r["quest"] in allq:
                m.setdefault(r["quest"], []).append(r)
        return m

    starts, ends, objs, pres, rews, steps = (by_quest(T[n]) for n in ("quest_start", "quest_end", "quest_objective",
                                                                       "quest_prereq", "quest_reward", "step"))
    nexts = {}
    for r in T["quest_prereq"]:
        nexts.setdefault(r["pre"], []).append(r["quest"])

    def prov(table):
        rel = f"data/{table}.jsonl"
        return {"source": SOURCE_ID, "dataset": pin["dataset"], "version": pin["version"], "commit": pin["commit"],
                "table": rel, "licence": pin["allowed"][rel], "sha256": verified["files"][rel],
                "clientBuild": verified["clientBuild"]}

    oq = {}
    for r in ours_quests or []:
        oq[r[0]] = {"title": r[1], "zone": r[2], "level": r[3], "min_level": r[4], "side": OURS_SIDE.get(r[5], r[5])}
    on = {int(v["id"]): v for v in (ours_npcs or {}).values() if str(v.get("id", "")).isdigit()}

    need_npc, need_obj, need_item, roles = set(), set(), set(), {}

    def role(kind, i, r):
        roles.setdefault((kind, i), set()).add(r)

    out_q = []
    for qid in sorted(quests):
        q = quests[qid]
        rec = {"id": qid, "title_en": q.get("title"), "level": q.get("level"), "min_level": q.get("min_level"),
               "side": SIDE.get(q.get("side")), "xp": q.get("xp"), "money_copper": q.get("money_copper"),
               "repeatable": bool(q.get("repeatable", False)),
               "start": [{"kind": r["kind"], "id": r["id"]} for r in starts.get(qid, [])],
               "end": [{"kind": r["kind"], "id": r["id"]} for r in ends.get(qid, [])],
               "objectives": [{k: r[k] for k in ("n", "kind", "target", "count") if k in r} for r in sorted(objs.get(qid, []), key=lambda r: r.get("n", 0))],
               "prereq": [{k: r[k] for k in ("pre", "mode", "breadcrumb") if k in r} for r in pres.get(qid, [])],
               "next": sorted(nexts.get(qid, [])),
               "rewards": [{k: r[k] for k in ("kind", "id", "count") if k in r} for r in rews.get(qid, [])],
               "steps_en": [s["text"] for s in sorted(steps.get(qid, []), key=lambda s: s.get("n", 0)) if s.get("text")],
               "status": "a-confirmer", "origin": "third-party", "provenance": prov("quest")}
        if rec["steps_en"]:
            rec["steps_provenance"] = prov("step")
        for s in rec["start"]:
            {"npc": need_npc, "object": need_obj, "item": need_item}[s["kind"]].add(s["id"]); role(s["kind"], s["id"], "giver")
        for s in rec["end"]:
            {"npc": need_npc, "object": need_obj, "item": need_item}[s["kind"]].add(s["id"]); role(s["kind"], s["id"], "ender")
        for o in rec["objectives"]:
            if o.get("target") is None:
                continue
            if o["kind"] == "kill" or o["kind"] == "talk":
                need_npc.add(o["target"]); role("npc", o["target"], "target")
            elif o["kind"] == "item":
                need_item.add(o["target"])
            elif o["kind"] == "object":
                need_obj.add(o["target"]); role("object", o["target"], "target")
        for w in rec["rewards"]:
            if w["kind"] in ("item", "choice"):
                need_item.add(w["id"])
        d = {"status": "nouveau"}
        if qid in oq:
            o = oq[qid]
            conf = []
            for f_ours, f_ps in (("title", "title_en"), ("level", "level"), ("min_level", "min_level"), ("side", "side")):
                if o.get(f_ours) is not None and rec.get(f_ps) is not None and o[f_ours] != rec[f_ps]:
                    conf.append({"field": f_ps, "wowkipedia": o[f_ours], "polestar": rec[f_ps]})
            d = {"status": "doublon-conflit" if conf else "doublon-identique", "match": f"quests-index:{qid}", "conflicts": conf}
        rec["dedupe"] = d
        out_q.append(rec)

    # Droppers / holders of objective items.
    for s in T["item_source"]:
        if s["item"] in need_item and s["kind"] == "npc":
            need_npc.add(s["id"]); role("npc", s["id"], "dropper")
        elif s["item"] in need_item and s["kind"] == "object":
            need_obj.add(s["id"]); role("object", s["id"], "holder")

    pts = {}
    for p in T["spawn"]:
        if p["map"] != frame["map"]:
            continue
        key = (p["kind"], p["id"])
        if (p["kind"] == "npc" and p["id"] in need_npc) or (p["kind"] == "object" and p["id"] in need_obj):
            m = to_map_pct(frame, p["x"], p["y"])
            if m:
                pts.setdefault(key, []).append(m)

    def thin(lst):
        if len(lst) <= MAX_POINTS:
            return lst
        step = len(lst) / MAX_POINTS
        return [lst[int(i * step)] for i in range(MAX_POINTS)]

    out_n = []
    for n in T["npc"]:
        if n["id"] not in need_npc:
            continue
        r_ = roles.get(("npc", n["id"]), set())
        if r_ <= {"dropper"} and not pts.get(("npc", n["id"])):
            continue  # a dropper that never spawns on this map is not about this zone
        rec = {"id": n["id"], "name_en": n.get("name"), "subname_en": n.get("subname"), "level_min": n.get("level_min"),
               "level_max": n.get("level_max"), "rank": n.get("rank"), "roles": sorted(roles.get(("npc", n["id"]), [])),
               "points": thin(pts.get(("npc", n["id"]), [])), "points_total": len(pts.get(("npc", n["id"]), [])),
               "status": "a-confirmer", "origin": "third-party", "provenance": prov("npc"), "points_provenance": prov("spawn")}
        d = {"status": "nouveau"}
        if n["id"] in on:
            o = on[n["id"]]
            conf = []
            if o.get("name") and not o.get("german_only") and o["name"] != rec["name_en"]:
                conf.append({"field": "name_en", "wowkipedia": o["name"], "polestar": rec["name_en"]})
            if o.get("level") and rec["level_min"] is not None:
                lv = str(o["level"]).replace("\u2013", "-")
                ps = str(rec["level_min"]) if rec["level_min"] == rec["level_max"] else f"{rec['level_min']}-{rec['level_max']}"
                if lv != ps:
                    conf.append({"field": "level", "wowkipedia": lv, "polestar": ps})
            d = {"status": "doublon-conflit" if conf else "doublon-identique", "match": f"npc-data:{n['id']}", "conflicts": conf}
        rec["dedupe"] = d
        out_n.append(rec)

    out_o = []
    for o in T["object"]:
        if o["id"] in need_obj:
            out_o.append({"id": o["id"], "name_en": o.get("name"), "roles": sorted(roles.get(("object", o["id"]), [])),
                          "points": thin(pts.get(("object", o["id"]), [])), "points_total": len(pts.get(("object", o["id"]), [])),
                          "status": "a-confirmer", "origin": "third-party", "provenance": prov("object"), "points_provenance": prov("spawn"),
                          "dedupe": {"status": "nouveau"}})

    fr = items_fr or {}
    src_by_item = {}
    for s in T["item_source"]:
        if s["item"] in need_item:
            src_by_item.setdefault(s["item"], []).append({k: s[k] for k in ("kind", "id", "chance") if k in s})
    out_i = []
    for it in T["item"]:
        if it["id"] in need_item:
            rec = {"id": it["id"], "name_en": it.get("name"), "quest_item": bool(it.get("quest_item", False)),
                   "sources": src_by_item.get(it["id"], [])[:20], "status": "a-confirmer", "origin": "third-party",
                   "provenance": prov("item"), "dedupe": {"status": "nouveau"}}
            if str(it["id"]) in fr:
                rec["dedupe"] = {"status": "doublon-identique", "match": "client:ItemSparse:1.60.1.70862", "conflicts": [],
                                 "note": "The item exists in the game files; the client name is used, Polestar only adds where it comes from."}
                rec["name_fr"] = fr[str(it["id"])]
                if items_en and str(it["id"]) in items_en:
                    rec["name_en_client"] = items_en[str(it["id"])]
                rec["name_fr_provenance"] = {"source": "client", "clientBuild": "1.60.1.70862", "table": "ItemSparse.frFR"}
            out_i.append(rec)

    def counts(rows):
        c = {"total": len(rows)}
        for r in rows:
            c[r["dedupe"]["status"]] = c.get(r["dedupe"]["status"], 0) + 1
        return c

    return {
        "meta": {"source": SOURCE_ID, "dataset": pin["dataset"], "version": pin["version"], "commit": pin["commit"],
                 "clientBuild": verified["clientBuild"], "zone_area": zone_area, "areas": sorted(areas), "frame": frame,
                 "attribution": pin["attribution"], "licences": sorted(set(pin["allowed"].values())),
                 "note": "Staging only. Third-party data: every record is 'a-confirmer'. Never overwrites Wowkipedia data."},
        "report": {"quests": counts(out_q), "npcs": counts(out_n), "objects": counts(out_o), "items": counts(out_i),
                   "quest_conflicts": sum(len(q["dedupe"].get("conflicts", [])) for q in out_q),
                   "npc_conflicts": sum(len(n["dedupe"].get("conflicts", [])) for n in out_n),
                   "ours_quests_in_zone_not_in_polestar": sorted(i for i, o in oq.items()
                                                                if o.get("zone") and o["zone"] == (ZONE_NAMES.get(zone_area)) and i not in quests)},
        "quests": out_q, "npcs": out_n, "objects": out_o, "items": out_i,
    }


ZONE_NAMES = {14: "Durotar", 12: "Elwynn Forest", 1: "Dun Morogh", 85: "Tirisfal Glades", 215: "Mulgore", 141: "Teldrassil"}


def diff(old, new):
    """Controlled update report between two staging files (or two pinned versions)."""
    out = {"from": {k: old["meta"].get(k) for k in ("version", "commit")},
           "to": {k: new["meta"].get(k) for k in ("version", "commit")}, "kinds": {}}
    for kind in ("quests", "npcs", "objects", "items"):
        a = {r["id"]: r for r in old.get(kind, [])}
        b = {r["id"]: r for r in new.get(kind, [])}
        changed = []
        for i in sorted(a.keys() & b.keys()):
            fa = {k: v for k, v in a[i].items() if k not in ("provenance", "points_provenance", "steps_provenance", "dedupe")}
            fb = {k: v for k, v in b[i].items() if k not in ("provenance", "points_provenance", "steps_provenance", "dedupe")}
            fields = sorted(k for k in fa.keys() | fb.keys() if fa.get(k) != fb.get(k))
            if fields:
                changed.append({"id": i, "fields": fields})
        out["kinds"][kind] = {"added": sorted(b.keys() - a.keys()), "removed": sorted(a.keys() - b.keys()), "changed": changed}
    return out


# ---------------------------------------------------------------- render (test tree only)
E = html.escape
SIDE_FR = {"both": "les deux", "alliance": "Alliance", "horde": "Horde", None: "non indiqué"}
ROLE_FR = {"giver": "donne une quête", "ender": "reçoit une quête", "target": "cible de quête", "dropper": "porte un objet de quête", "holder": "contient un objet de quête"}
PREVIEW_NOTE_FR = ("Aperçu de test : données communautaires importées automatiquement, non vérifiées en jeu. "
                   "Rien de cette section n’est publié.")


def _name(idx, kind, i):
    r = idx.get((kind, i))
    if not r:
        return f"{kind} {i}"
    return r.get("name_fr") or r.get("name_en") or f"{kind} {i}"


def render_sections(st, source_no, credits_href, map_json_href, tiles):
    idx = {}
    for kind, rows in (("npc", st["npcs"]), ("object", st["objects"]), ("item", st["items"])):
        for r in rows:
            idx[(kind, r["id"])] = r
    qidx = {q["id"]: q for q in st["quests"]}
    cite = f'<sup class="cite"><a href="#source-{source_no}" aria-label="Source {source_no}">[{source_no}]</a></sup>'
    pill = '<span class="status-pill is-draft">À confirmer</span>'
    rep = st["report"]
    # Map section
    tiles_html = "".join(f'<img src="{E(t["src"])}" alt="" width="256" height="256" loading="lazy" decoding="async">' for t in tiles)
    legend = ('<fieldset class="wk-map-filters"><legend>Afficher</legend>'
              '<label><input type="checkbox" data-role="giver" checked> Donneurs de quêtes</label>'
              '<label><input type="checkbox" data-role="ender" checked> Fins de quêtes</label>'
              '<label><input type="checkbox" data-role="target"> Cibles</label>'
              '<label><input type="checkbox" data-role="dropper"> Objets de quête</label></fieldset>')
    nomap_rows = []
    for n in st["npcs"] + st["objects"]:
        if not n["points"]:
            continue
        p = n["points"][0]
        nomap_rows.append(f'<tr><th scope="row">{E(n.get("name_en") or "")}</th><td>{E(", ".join(ROLE_FR.get(r, r) for r in n["roles"]))}</td>'
                          f'<td>{p[0]}, {p[1]}</td><td>{n["points_total"]}</td></tr>')
    map_sec = (
        f'<section class="article-section" id="carte-interactive" aria-labelledby="carte-interactive-title">'
        f'<h2 id="carte-interactive-title">Carte interactive</h2>'
        f'<p class="wk-preview-note">{PREVIEW_NOTE_FR}</p>'
        f'<p>Positions des PNJ et objets liés aux quêtes de la zone, d’après une base de données communautaire Forever (à confirmer en jeu).{cite} {pill} '
        f'Coordonnées en % de la carte de zone (x, y), calculées avec le cadre de carte des fichiers du jeu (client 1.60.1.70862).</p>'
        f'<div class="wk-map" data-map="{E(map_json_href)}">{legend}'
        f'<div class="wk-map-frame" role="group" aria-label="Carte de la zone avec repères"><div class="wk-map-tiles">{tiles_html}</div>'
        f'<div class="wk-map-pins"></div></div>'
        f'<div class="wk-map-card" aria-live="polite" hidden></div>'
        f'<p class="wk-map-credit">Carte : image du jeu World of Warcraft: Forever © Blizzard Entertainment, tirée des fichiers du client 1.60.1.70862, non retouchée (seul le format a été converti).</p></div>'
        f'<details class="wk-map-table"><summary>Liste des repères ({len(nomap_rows)})</summary><div class="table-wrap" role="region" tabindex="0" aria-label="Repères de la carte">'
        f'<table><thead><tr><th scope="col">PNJ ou objet (nom anglais)</th><th scope="col">Rôle</th><th scope="col">Position (x, y)</th><th scope="col">Points connus</th></tr></thead>'
        f'<tbody>{"".join(nomap_rows)}</tbody></table></div></details></section>')
    # Quest chains section
    rows = []
    for q in sorted(st["quests"], key=lambda q: (q.get("level") or 0, q["title_en"] or "")):
        giver = ", ".join(_name(idx, s["kind"], s["id"]) for s in q["start"]) or "non indiqué"
        ender = ", ".join(_name(idx, s["kind"], s["id"]) for s in q["end"]) or "non indiqué"
        pre = ", ".join(E(allq_title(qidx, p["pre"])) + (" (au choix)" if p.get("mode") == "any" else "") for p in q["prereq"]) or "—"
        nxt = ", ".join(E(allq_title(qidx, n)) for n in q["next"]) or "—"
        rw = ", ".join(E(_name(idx, "item", w["id"])) + (" (au choix)" if w["kind"] == "choice" else "") for w in q["rewards"] if w["kind"] in ("item", "choice")) or "—"
        dd = q["dedupe"]["status"]
        flag = {"nouveau": "nouvelle", "doublon-identique": "déjà listée", "doublon-conflit": "déjà listée, écart"}[dd]
        rows.append(f'<tr id="ps-q{q["id"]}"><th scope="row">{E(q["title_en"] or "")}</th><td>{q.get("level") or "—"}</td>'
                    f'<td>{E(SIDE_FR.get(q.get("side")))}</td><td>{E(giver)}</td><td>{E(ender)}</td><td>{pre}</td><td>{nxt}</td><td>{rw}</td><td>{flag}</td></tr>')
    qsec = (
        f'<section class="article-section" id="quetes-suites" aria-labelledby="quetes-suites-title">'
        f'<h2 id="quetes-suites-title">Quêtes : suites, prérequis et récompenses (à confirmer)</h2>'
        f'<p class="wk-preview-note">{PREVIEW_NOTE_FR}</p>'
        f'<p>{rep["quests"]["total"]} quêtes rattachées à cette zone par une base de données communautaire Forever : '
        f'{rep["quests"].get("nouveau", 0)} absentes de notre index, {rep["quests"].get("doublon-identique", 0)} identiques, '
        f'{rep["quests"].get("doublon-conflit", 0)} avec un écart (nom, niveau ou faction) à vérifier. Noms de quêtes et de PNJ en anglais ; '
        f'noms d’objets en français tirés des fichiers du jeu.{cite} {pill}</p>'
        f'<div class="table-wrap" role="region" tabindex="0" aria-label="Suites de quêtes"><table><thead><tr>'
        f'<th scope="col">Quête (nom anglais)</th><th scope="col">Niveau</th><th scope="col">Faction</th><th scope="col">Donneur</th>'
        f'<th scope="col">Rendre à</th><th scope="col">Prérequis</th><th scope="col">Suite</th><th scope="col">Récompenses</th><th scope="col">Dans notre index</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')
    v = st["meta"]["version"]
    src_li = (f'<li id="source-{source_no}"><span class="source-number">[{source_no}]</span> <span class="source-lines">'
              f'<a href="{E(credits_href)}">Base de données communautaire Forever (version {E(v)}), voir « Sources et licences »</a>'
              f' · licences GPL-3.0 et CC BY 4.0 · consultée au commit {E(st["meta"]["commit"][:12])}</span></li>')
    return map_sec, qsec, src_li


def allq_title(qidx, i):
    q = qidx.get(i)
    return (q["title_en"] if q and q.get("title_en") else f"quête {i}")


def map_payload(st):
    pins = []
    for kind, rows in (("npc", st["npcs"]), ("object", st["objects"])):
        for r in rows:
            for p in r["points"]:
                pins.append({"k": kind, "id": r["id"], "n": r.get("name_en"), "r": r["roles"], "x": p[0], "y": p[1]})
    quests_by = {}
    for q in st["quests"]:
        for s in q["start"]:
            quests_by.setdefault(f'{s["kind"]}:{s["id"]}', {}).setdefault("g", []).append(q["title_en"])
        for s in q["end"]:
            quests_by.setdefault(f'{s["kind"]}:{s["id"]}', {}).setdefault("e", []).append(q["title_en"])
    return {"version": st["meta"]["version"], "commit": st["meta"]["commit"], "status": "a-confirmer", "pins": pins, "quests": quests_by}


def credits_page(pin, version, commit, data_href):
    a = pin["attribution"]["fr"].replace("{version}", E(version))
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>Sources et licences — Wowkipedia</title>
<link rel="stylesheet" href="../../v2.css?v=42c"><link rel="stylesheet" href="../../theme-wow.css"><link rel="stylesheet" href="../../wk-map.css"></head>
<body class="v39"><main id="main-content" class="wk-credits"><h1>Sources et licences</h1>
<p class="wk-preview-note">{PREVIEW_NOTE_FR}</p>
<section class="article-section"><h2>Données communautaires (à confirmer)</h2>
<p>{a}</p>
<ul>
<li>Projet d’origine : <a href="{E(pin['repository'])}">Polestar</a>, dossier forever-db, commit <code>{E(commit)}</code>.</li>
<li>Licence de la base : <a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPL version 3</a>. Couche « étapes et mécaniques » : <a href="https://creativecommons.org/licenses/by/4.0/deed.fr">CC BY 4.0</a>.</li>
<li>Données telles qu’utilisées par Wowkipedia (forme modifiable, sous la même licence GPL-3.0) : <a href="{E(data_href)}">fichier JSON</a>.</li>
<li>Ces données sont fournies sans garantie. Elles ne viennent pas de Blizzard Entertainment et restent à confirmer en jeu.</li>
</ul></section>
<section class="article-section"><h2>Images de carte</h2><p>Cartes de zone : images du jeu World of Warcraft: Forever © Blizzard Entertainment, extraites des fichiers du client 1.60.1.70862, non retouchées (conversion de format uniquement).</p></section>
<p class="independence">World of Warcraft et Blizzard Entertainment sont des marques de Blizzard Entertainment, Inc. Site indépendant et non officiel.</p>
</main></body></html>
"""


def render(st, pin, page_html, out_dir, tiles_rel, page_rel_root="../../../"):
    out_dir = Path(out_dir)
    map_json = "donnees-carte-polestar.json"
    credits_href = page_rel_root + "fr/sources-et-licences/"
    page = page_html
    m = re.findall(r'<li id="source-(\d+)"', page)
    source_no = (max(int(x) for x in m) + 1) if m else 1
    tiles = [{"src": t} for t in tiles_rel]
    map_sec, qsec, src_li = render_sections(st, source_no, credits_href, map_json, tiles)
    anchor = '<section class="article-section" id="historique-des-corrections"'
    if anchor not in page:
        anchor = '<section class="article-section status-grid" id="confirme"'
    if anchor not in page:
        raise ImportError_("cannot find where to insert the sections")
    page = page.replace(anchor, map_sec + qsec + anchor, 1)
    page = page.replace('</ol></section>', src_li + '</ol></section>', 1) if '<ol class="source-list">' in page else page
    css = f'<link rel="stylesheet" href="{page_rel_root}wk-map.css">'
    js = f'<script type="module" src="{page_rel_root}wk-map.js"></script>'
    page = page.replace("</head>", css + "</head>", 1).replace("</body>", js + "</body>", 1)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(page, encoding="utf-8")
    (out_dir / map_json).write_text(json.dumps(map_payload(st), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"source_no": source_no, "map_json": map_json}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("verify"); v.add_argument("--src", required=True)
    s = sub.add_parser("stage")
    s.add_argument("--src", required=True); s.add_argument("--zone-area", type=int, required=True)
    s.add_argument("--frame", required=True); s.add_argument("--ui-map", type=int, required=True)
    s.add_argument("--out", required=True); s.add_argument("--ours-quests"); s.add_argument("--ours-npcs"); s.add_argument("--items-fr"); s.add_argument("--area-table")
    d = sub.add_parser("diff"); d.add_argument("--old", required=True); d.add_argument("--new", required=True); d.add_argument("--out")
    a = ap.parse_args(argv)
    pin = load_pin()
    try:
        if a.cmd == "verify":
            print(json.dumps(verify(a.src, pin), indent=1))
        elif a.cmd == "stage":
            oq = json.loads(Path(a.ours_quests).read_text()) if a.ours_quests else None
            on = json.loads(Path(a.ours_npcs).read_text())["npcs"] if a.ours_npcs else None
            fr = json.loads(Path(a.items_fr).read_text()) if a.items_fr else None
            pa = json.loads(Path(a.area_table).read_text())["parent"] if a.area_table else None
            st = stage(a.src, pin, a.zone_area, frame_from_client(a.frame, a.ui_map), oq, on, fr, parents=pa)
            Path(a.out).write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
            print(json.dumps(st["report"], ensure_ascii=False))
        elif a.cmd == "diff":
            r = diff(json.loads(Path(a.old).read_text()), json.loads(Path(a.new).read_text()))
            txt = json.dumps(r, ensure_ascii=False, indent=1)
            Path(a.out).write_text(txt, encoding="utf-8") if a.out else print(txt)
    except ImportError_ as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
