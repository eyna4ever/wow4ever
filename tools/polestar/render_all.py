#!/usr/bin/env python3
"""Render every Forever zone page (FR and EN) of a COPY of the wiki tree with the interactive map and the merged
quest table. Test only: never touches the live site, never uploads anything.

usage: render_all.py --src FOREVER_DB --tree TREE --zones zones.json --maps MAPS_DIR --frame UIMAP.json
                     --area-table AREA.json --ours-quests Q.json --ours-npcs N.json --items-fr F.json --items-en E.json
                     [--classic-items STAGING.json] --report OUT.json
"""
import argparse, gzip, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import polestar_import as pi  # noqa: E402
import render_zone as rz  # noqa: E402

HERE = Path(__file__).resolve().parent


def credits_html(pin, lang, version, commit, data_href, classic):
    fr = lang == "fr"
    a = pin["attribution"][lang].replace("{version}", rz.E(version))
    t = (lambda f, e: f if fr else e)
    cl = ""
    if classic:
        cl = t(f"<li>Valeurs d’objets de World of Warcraft Classic (client {rz.E(classic)}), reprises du même projet, utilisées seulement pour les objets présents dans le client Forever et identiques sur tous les champs connus ; marquées « à confirmer ».</li>",
               f"<li>Item values from World of Warcraft Classic (client {rz.E(classic)}), taken from the same project, used only for items present in the Forever client and identical on every known field; marked “to be confirmed”.</li>")
    return f"""<!doctype html><html lang="{lang}" data-theme="wow"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>{t('Sources et licences', 'Sources and licences')} — Wowkipedia</title>
<link rel="stylesheet" href="../../v2.css?v=42c"><link rel="stylesheet" href="../../theme-wow.css"><link rel="stylesheet" href="../../wk-map.css?v=43"></head>
<body class="v39"><main id="main-content" class="wk-credits"><h1>{t('Sources et licences', 'Sources and licences')}</h1>
<section class="article-section"><h2>{t('Données communautaires (à confirmer)', 'Community data (to be confirmed)')}</h2><p>{a}</p><ul>
<li>{t('Projet d’origine', 'Original project')} : <a href="{rz.E(pin['repository'])}">Polestar</a>, forever-db, commit <code>{rz.E(commit)}</code>.</li>
<li>{t('Licence de la base', 'Database licence')} : <a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPL v3</a> ; {t('étapes et mécaniques', 'steps and mechanics')} : <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</li>
<li>{t('Données telles qu’utilisées par Wowkipedia (forme modifiable, même licence GPL-3.0)', 'Data as used by Wowkipedia (modifiable form, same GPL-3.0 licence)')} : <a href="{rz.E(data_href)}">JSON (gzip)</a>.</li>
{cl}<li>{t('Sans garantie. Ces données ne viennent pas de Blizzard Entertainment et restent à confirmer en jeu.', 'No warranty. This data does not come from Blizzard Entertainment and is to be confirmed in game.')}</li></ul></section>
<section class="article-section"><h2>{t('Images de carte', 'Map images')}</h2><p>{t('Cartes de zone : images du jeu World of Warcraft: Forever © Blizzard Entertainment, extraites des fichiers du client 1.60.1.70862, non retouchées (format et compression seulement).', 'Zone maps: World of Warcraft: Forever in-game images © Blizzard Entertainment, from the client 1.60.1.70862 files, not retouched (format and compression only).')}</p></section>
<p class="independence">{t('World of Warcraft et Blizzard Entertainment sont des marques de Blizzard Entertainment, Inc. Site indépendant et non officiel.', 'World of Warcraft and Blizzard Entertainment are trademarks of Blizzard Entertainment, Inc. Independent, unofficial site.')}</p>
</main></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("src", "tree", "zones", "maps", "frame", "area-table", "ours-quests", "ours-npcs", "items-fr", "items-en", "report"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--classic-items")
    a = ap.parse_args(argv)
    pin = pi.load_pin()
    verified = pi.verify(a.src, pin)
    tables = pi.read_tables(a.src, pin)
    J = lambda p: json.loads(Path(p).read_text(encoding="utf-8"))
    zones, area, ours = J(a.zones), J(a.area_table), J(a.ours_quests)
    npcs, fr, en = J(a.ours_npcs)["npcs"], J(a.items_fr), J(a.items_en)
    parents = {int(k): int(v) for k, v in area["parent"].items()}
    names = {int(k): v for k, v in area["name"].items()}
    wiki = Path(a.tree) / "wiki"
    for f in ("wk-map.js", "wk-map.css"):
        shutil.copy2(HERE / "frontend" / f, wiki / f)
    report, all_staging = {"zones": [], "totals": {}}, {}
    for z in zones:
        area_id = z.get("areaID") or next((k for k, v in names.items() if v == z["name_en"] and parents.get(k, 0) == 0), None)
        frame = pi.frame_from_client(a.frame, z["uiMap"])
        st = pi.stage(a.src, pin, area_id, frame, ours, npcs, fr, verified=verified, parents=parents, items_en=en, tables=tables)
        all_staging[z["fr"]] = st
        ours_rows = [r for r in ours if r[2] == z["name_en"]]
        mdir = Path(a.maps) / str(z["uiMap"])
        layout = J(mdir / "manifest.json") if (mdir / "manifest.json").exists() else None
        adir = wiki / "assets" / "carte" / str(z["uiMap"])
        adir.mkdir(parents=True, exist_ok=True)
        if layout:
            for t in layout["tiles"]:
                shutil.copy2(mdir / t["file"], adir / t["file"])
            shutil.copy2(mdir / "manifest.json", adir / "manifest.json")
        (adir / "donnees.json").write_text(json.dumps(rz.map_payload(st), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        zr = {"fr": z["fr"], "en": z["en"], "uiMap": z["uiMap"], "areaID": area_id, "tiles": len(layout["tiles"]) if layout else 0,
              "staging": st["report"], "pins": sum(len(n["points"]) for n in st["npcs"] + st["objects"])}
        for lang, slug, zname in (("fr", z["fr"], None), ("en", z["en"], z["name_en"])):
            p = wiki / lang / "zones" / slug / "index.html"
            page = p.read_text(encoding="utf-8")
            if zname is None:
                import re
                h = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
                zname = rz.html.unescape(re.sub(r"<[^>]+>", "", h.group(1)).strip())
            href = f"../../../assets/carte/{z['uiMap']}/"
            credits = "../../../fr/sources-et-licences/" if lang == "fr" else "../../../en/sources-and-licences/"
            new, qs = rz.render_page(page, st, ours_rows, lang, zname, layout, href, href + "donnees.json", credits)
            p.write_text(new, encoding="utf-8")
            zr["page_" + lang] = qs
        report["zones"].append(zr)
    blob = json.dumps({"meta": {"source": "polestar-forever-db", "version": pin["version"], "commit": pin["commit"]}, "zones": all_staging}, ensure_ascii=False, separators=(",", ":")).encode()
    classic = None
    for lang, d in (("fr", "sources-et-licences"), ("en", "sources-and-licences")):
        cdir = wiki / lang / d
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "donnees-polestar.json.gz").write_bytes(gzip.compress(blob, 9, mtime=0))
        if a.classic_items:
            cdat = Path(a.classic_items).read_bytes()
            (cdir / "objets-classic.json.gz").write_bytes(gzip.compress(cdat, 9, mtime=0))
            classic = json.loads(cdat)["meta"]["classic_build"]
        (cdir / "index.html").write_text(credits_html(pin, lang, pin["version"], pin["commit"], "donnees-polestar.json.gz", classic), encoding="utf-8")
    tot = report["totals"]
    for zr in report["zones"]:
        for k in ("rows", "both", "ours", "ps", "conflicts"):
            tot[k] = tot.get(k, 0) + zr["page_fr"][k]
        tot["pins"] = tot.get("pins", 0) + zr["pins"]
        tot["lost_anchors"] = tot.get("lost_anchors", 0) + len(zr["page_fr"]["lost_anchors"]) + len(zr["page_en"]["lost_anchors"])
        for kind in ("npcs", "objects", "items"):
            tot[kind] = tot.get(kind, 0) + zr["staging"][kind]["total"]
    tot["zones"] = len(report["zones"])
    Path(a.report).write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(tot))
    return 0


if __name__ == "__main__":
    sys.exit(main())
