#!/usr/bin/env python3
"""Build Wowkipedia bestiary draft entries from the Forever NPC list (t352u)."""
from __future__ import annotations
import json, re
from collections import defaultdict
from pathlib import Path

ROOT = Path("/workspace/wowkipedia-v21-elite/bestiaire")
TREE = ROOT / "test-tree-v37"
SRC = ROOT / "sources"
OUT = ROOT / "import-batches"
ENTRIES = json.loads((TREE / "pipeline/runtime/entries.json").read_text())

GV = "World of Warcraft: Forever — annonces et notes officielles, état documentaire 2026-11-12"
LICENSE_BZ = ("Droits réservés Blizzard ; référence et synthèse originale (courtes citations), "
              "mention © Blizzard Entertainment conservée ; site non commercial.")
LICENSE_CLIENT = ("Données de tiers (extrait de fichiers client) ; consultation des listes de PNJ "
                  "le 12 novembre 2026 ; informations à confirmer, non officielles.")
ACCESSED = "2026-11-12"
UPDATED = "2026-11-12T05:50:00.000Z"
ACTOR_NOTE = ("Bestiaire d’après les sources officielles citées et la liste des PNJ extraite "
              "des données du jeu Forever (à confirmer). Brouillon à relire. Périmètre du wiki, "
              "droits et traductions non confirmés par un humain. Pas une validation de publication.")

OFFICIAL_ZONE = {
    "Zephras Isle": ("Île de Zéphras", "Zephras Isle"),
    "Insel Zephras": ("Île de Zéphras", "Zephras Isle"),
    "Shen'dralas": ("Shen’dralas", "Shen’dralas"),
    "Hall of Thanes": ("Salle des Thanes", "Hall of Thanes"),
    "The Hall of Thanes": ("Salle des Thanes", "Hall of Thanes"),
    "Ruins of Lordaeron": ("Ruines de Lordaeron", "Ruins of Lordaeron"),
    "Excavation Site: Wetlands": ("Excavations : les Paluns", "Excavation Site: Wetlands"),
    "City of Dalaran": ("Cité de Dalaran", "City of Dalaran"),
    "Dalaran": ("Dalaran", "Dalaran"),
    "The Drowned City": ("La cité Submergée", "The Drowned City"),
    "Krol'dok Stronghold": ("Bastion Krol’dok", "Krol’dok Stronghold"),
    "Alcaz Prison": ("Prison d’Alcaz", "Alcaz Prison"),
    "Blackmaw Hold": ("Repaire des Noiregueules", "Blackmaw Hold"),
    "The Shaper's Terrace": ("La terrasse du Façonneur", "The Shaper’s Terrace"),
    "Barrow Deeps": ("Profondeurs des Saisons", "Barrow Deeps"),
    "Hyjal Summit": ("Sommet d’Hyjal", "Hyjal Summit"),
    "Mount Hyjal": ("Mont Hyjal", "Mount Hyjal"),
    "Onyxia's Lair": ("Repaire d’Onyxia", "Onyxia’s Lair"),
    "Riverglades": ("Rives Claires", "Riverglades"),
}
MERGE_ZONE = {
    "Insel Zephras": "Zephras Isle",
    "The Hall of Thanes": "Hall of Thanes",
    "Temple of Ahn'Qiraj": "Ahn'Qiraj Temple",
}
FOREVER_DUNGEON_CANON = {
    "Hall of Thanes", "Ruins of Lordaeron", "Excavation Site: Wetlands",
    "City of Dalaran", "Dalaran",
}
CLASSIC_DUNGEON = {
    "Ragefire Chasm", "The Deadmines", "Wailing Caverns", "Shadowfang Keep",
    "Blackfathom Deeps", "The Stockade", "Gnomeregan", "Razorfen Kraul",
    "Razorfen Downs", "Scarlet Monastery", "Scarlet Monastery: Graveyard",
    "Scarlet Monastery: Library", "Zul'Farrak", "Scholomance", "Stratholme",
}
RAID = {
    "Molten Core", "Blackwing Lair", "Zul'Gurub", "Ruins of Ahn'Qiraj",
    "Ahn'Qiraj Temple", "Naxxramas",
}
KALIMDOR = {
    "The Barrens", "Orgrimmar", "Durotar", "Mulgore", "Teldrassil", "Ashenvale", "Silithus",
    "Feralas", "Desolace", "Tanaris", "Felwood", "Thousand Needles", "Darkshore", "Thunder Bluff",
    "Stonetalon Mountains", "Winterspring", "Dustwallow Marsh", "Darnassus", "Un'Goro Crater",
    "Azshara", "Moonglade",
}
EASTERN = {
    "Dun Morogh", "Elwynn Forest", "Tirisfal Glades", "Stormwind City", "Hillsbrad Foothills",
    "Stranglethorn Vale", "Wetlands", "Loch Modan", "Duskwood", "Eastern Plaguelands", "Undercity",
    "Arathi Highlands", "The Hinterlands", "Badlands", "Burning Steppes", "Western Plaguelands",
    "Redridge Mountains", "Alterac Valley", "Alterac Mountains", "Silverpine Forest", "Searing Gorge",
    "Westfall", "Swamp of Sorrows", "Blasted Lands", "Ironforge", "Blackrock Mountain",
}
WIKI_ZONE = {
    "Zephras Isle": ("/fr/zones/ile-de-zephras/", "/en/zones/zephras-isle/"),
    "Shen'dralas": ("/fr/zones/shen-dralas/", "/en/zones/shen-dralas/"),
    "Hall of Thanes": ("/fr/donjons-raids/salle-des-thanes/", "/en/dungeons-raids/hall-of-thanes/"),
    "Ruins of Lordaeron": ("/fr/donjons-raids/ruines-de-lordaeron/", "/en/dungeons-raids/ruins-of-lordaeron/"),
    "Excavation Site: Wetlands": ("/fr/donjons-raids/excavations/", "/en/dungeons-raids/excavation-site/"),
    "City of Dalaran": ("/fr/donjons-raids/cite-de-dalaran/", "/en/dungeons-raids/city-of-dalaran/"),
}
WIKI = {
    "notes": ("/fr/creatures/creatures-notes-officielles/", "/en/creatures/creatures-official-notes/"),
    "onyxia": ("/fr/creatures/onyxia/", "/en/creatures/onyxia/"),
    "foxes": ("/fr/creatures/renards/", "/en/creatures/foxes/"),
    "documented": ("/fr/creatures/creatures-documentees/", "/en/creatures/documented-creatures/"),
    "blueprints": ("/fr/metiers/recettes-et-plans-avances/", "/en/professions/recipes-and-advanced-blueprints/"),
}
OFFICIAL_NPC = {
    "the baron": {
        "note_fr": "Nommé par les correctifs officiels (tête « Abominable Head » / quête « Unending Torment », Horde).",
        "note_en": "Named in official hotfixes (the “Abominable Head” / “Unending Torment” quest, Horde).",
    },
    "onyxia": {
        "note_fr": "Rencontre officielle (raid 40, 9 décembre 2026). Fiche déjà en ligne.",
        "note_en": "Official encounter (40-player raid, 9 December 2026). Existing sheet.",
    },
}
ROLE_FR = {"x": "boss", "h": "vendeur", "l": "formateur", "b": "butin indiqué", "t": "vol à la tire", "z": "objectif de quête", "q": "donneur de quête"}
ROLE_EN = {"x": "boss", "h": "vendor", "l": "trainer", "b": "loot flagged", "t": "pick pocket", "z": "quest objective", "q": "quest giver"}

def T(fr, en):
    return {"fr": fr, "en": en}

def clip(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"

def zone_label(canon, fr_extract, lang):
    if canon in OFFICIAL_ZONE:
        return OFFICIAL_ZONE[canon][0 if lang == "fr" else 1]
    if lang == "fr":
        return fr_extract.get(canon) or canon
    return canon

def roles_of(tags):
    tags = tags or ""
    fr, en = [], []
    for ch in "xhlbtzq":
        if ch in tags:
            fr.append(ROLE_FR[ch]); en.append(ROLE_EN[ch])
    return (", ".join(fr), ", ".join(en)) if fr else ("non indiqué", "not given")

def classification(tags):
    return ("boss", "boss") if "x" in (tags or "") else ("non indiqué", "not given")

def load_lists():
    en = json.loads((SRC / "npc-liste-en.json").read_text())
    fr = json.loads((SRC / "npc-liste-fr.json").read_text())
    assert len(en) == len(fr) == 3284
    fr_zone_by_en = {}
    rows = []
    for a, b in zip(en, fr):
        assert a[0] == b[0] and a[1] == b[1]
        raw_zone = a[3] or ""
        canon = MERGE_ZONE.get(raw_zone, raw_zone) if raw_zone else ""
        if raw_zone and raw_zone not in MERGE_ZONE:
            fr_zone_by_en.setdefault(canon or raw_zone, b[3] or raw_zone)
        elif raw_zone in MERGE_ZONE:
            fr_zone_by_en.setdefault(canon, b[3] or canon)
        rows.append({
            "slug": a[0], "name": a[1], "raw_zone": raw_zone, "canon": canon,
            "zone_fr_extract": b[3] or "", "level": (a[4] or "").strip(),
            "tags": a[5] or "", "quests": a[6] if isinstance(a[6], int) else 0,
        })
    return rows, fr_zone_by_en

def recipe_drops():
    e = next(x for x in ENTRIES if x["id"] == "forever-professions-blueprints")
    drops = defaultdict(list)
    for section in e["article"]["sections"]:
        kind = "vendor" if section["id"] == "vendeurs-a-confirmer" else "drop" if section["id"].startswith("butin-") else None
        if not kind:
            continue
        for block in section["blocks"]:
            if block.get("type") != "table":
                continue
            for row in block["rows"]:
                rec_fr, rec_en = row[0]["fr"], row[0]["en"]
                for mon in re.split(r"[,;/]+", row[2]["en"]):
                    mon = mon.strip()
                    if mon:
                        drops[mon.lower()].append({"fr": rec_fr, "en": rec_en, "kind": kind})
    out = {}
    for k, items in drops.items():
        seen, uniq = set(), []
        for it in items:
            key = (it["en"], it["kind"])
            if key in seen:
                continue
            seen.add(key); uniq.append(it)
        out[k] = uniq
    return out

def loot_cell(name, drops):
    items = drops.get(name.lower(), [])
    if not items:
        return T("non indiqué", "not given")
    fr_bits, en_bits = [], []
    link_fr, link_en = WIKI["blueprints"]
    for it in items:
        verb_fr = "vendu" if it["kind"] == "vendor" else "butin"
        verb_en = "sold" if it["kind"] == "vendor" else "drop"
        fr_bits.append(f"{it['fr']} ({verb_fr})")
        en_bits.append(f"{it['en']} ({verb_en})")
    return T(clip("; ".join(fr_bits) + f" — {link_fr}", 400),
             clip("; ".join(en_bits) + f" — {link_en}", 400))

def status_cell(name):
    info = OFFICIAL_NPC.get(name.lower())
    if info:
        return T(clip("officiel confirmé — " + info["note_fr"], 400),
                 clip("official, confirmed — " + info["note_en"], 400))
    return T("à confirmer", "to be confirmed")

def npc_row(npc, drops, fr_zones, zone_override=None):
    zone = npc["canon"] if zone_override is None else zone_override
    level_fr = npc["level"] or "non indiqué"
    level_en = npc["level"] or "not given"
    cl_fr, cl_en = classification(npc["tags"])
    ro_fr, ro_en = roles_of(npc["tags"])
    if not zone:
        z_fr, z_en = "non indiqué", "not given"
    else:
        z_fr = zone_label(zone, fr_zones, "fr")
        z_en = zone_label(zone, fr_zones, "en")
        if npc["raw_zone"] and npc["raw_zone"] != zone:
            z_fr = clip(f"{z_fr} (étiquette extraite : {npc['raw_zone']})", 400)
            z_en = clip(f"{z_en} (extract label: {npc['raw_zone']})", 400)
    return [
        T(npc["name"], npc["name"]), T(level_fr, level_en),
        T("non indiqué", "not given"), T(cl_fr, cl_en), T(ro_fr, ro_en),
        T(z_fr, z_en), loot_cell(npc["name"], drops), status_cell(npc["name"]),
    ]

HEAD = [T("Nom", "Name"), T("Niveau", "Level"), T("Type", "Type"), T("Classification", "Classification"),
        T("Rôle", "Role"), T("Zone", "Zone"), T("Butin ou recettes notables", "Notable loot or recipes"), T("Statut", "Status")]

def table(caption_fr, caption_en, rows, src):
    return any_table(caption_fr, caption_en, HEAD, rows, src)

def any_table(caption_fr, caption_en, head, rows, src):
    return {"type": "table", "caption": T(clip(caption_fr, 300), clip(caption_en, 300)),
            "head": head, "rows": rows, "src": src}

def para(fr, en, src):
    return {"type": "p", "fr": clip(fr, 2400), "en": clip(en, 2400), "src": src}

def lst(items, src):
    return {"type": "list", "items": items, "src": src}

def item(fr, en, src=None):
    d = T(clip(fr, 2400), clip(en, 2400))
    if src:
        d["src"] = src
    return d

def src(key, language, url, title, published=None, undated=False, verification=None):
    official = url.startswith("https://news.blizzard.com") or "forums.blizzard.com" in url
    out = {"key": key, "language": language, "url": url, "title": title, "accessedAt": ACCESSED,
           "license": LICENSE_BZ if official else LICENSE_CLIENT, "gameVersion": GV}
    if published:
        out["publishedAt"] = published
    if undated:
        out["undated"] = True
    if verification:
        out["verification"] = verification
    return out

SOURCES_CORE = [
    src("bz-dungeons-fr", "fr",
        "https://news.blizzard.com/fr-fr/article/24301455/decouvrez-les-nouveaux-donjons-de-world-of-warcraft-forever",
        "Découvrez les nouveaux donjons de World of Warcraft: Forever", "2026-10-20"),
    src("bz-dungeons-en", "en",
        "https://news.blizzard.com/en-us/article/24301455/explore-the-new-dungeons-of-world-of-warcraft-forever",
        "Explore the New Dungeons of World of Warcraft: Forever", "2026-10-20"),
    src("bz-raids-fr", "fr",
        "https://news.blizzard.com/fr-fr/article/24303009/apercu-des-raids-de-world-of-warcraft-forever-emplacements-taille-des-raids-et-harmonisation",
        "Aperçu des raids de World of Warcraft: Forever – Emplacements, taille des raids et harmonisation", "2026-10-20"),
    src("bz-raids-en", "en",
        "https://news.blizzard.com/en-us/article/24303009/world-of-warcraft-forever-raid-overviewlocations-raid-sizes-and-attunement",
        "World of Warcraft: Forever Raid Overview—Locations, Raid Sizes, and Attunement", "2026-10-20"),
    src("bz-hotfixes-en", "en",
        "https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-6-2026",
        "WoW: Forever Hotfixes - November 6, 2026 (correctifs des 5 et 6 novembre)", "2026-11-06"),
    src("bz-hotfixes-eu", "en",
        "https://eu.forums.blizzard.com/en/wow/t/639885",
        "WoW: Forever Hotfixes - November 6, 2026 — forum officiel EU (Kaivax)", "2026-11-06"),
    src("bz-dive-fr", "fr",
        "https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever",
        "Récapitulatif de la présentation « Au cœur de World of Warcraft: Forever »", "2026-09-13"),
    src("bz-dive-en", "en",
        "https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap",
        "World of Warcraft: Forever Deep Dive Panel Recap", "2026-09-13"),
    src("client-npc-hub-en", "en", "https://eternadex.com/en/npc/",
        "NPC database for WoW Forever (client-extracted data, to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-npc-hub-fr", "fr", "https://eternadex.com/fr/npc/",
        "Base de PNJ de WoW Forever (données extraites du client, à confirmer)",
        undated=True, verification="à confirmer"),
    src("client-npc-liste-en", "en", "https://eternadex.com/en/daten/npc-liste.json",
        "NPC list JSON, English (client-extracted data, to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-npc-liste-fr", "fr", "https://eternadex.com/fr/daten/npc-liste.json",
        "Liste JSON des PNJ, français (données extraites du client, à confirmer)",
        undated=True, verification="à confirmer"),
    src("client-datenbank-en", "en", "https://eternadex.com/en/datenbank/",
        "Item database — game data, WoW Forever client build 1.60.1.70862, as of 7 November 2026 (to be confirmed)",
        undated=True, verification="à confirmer"),
]
SRC_OFF = ["bz-dungeons", "bz-raids", "bz-hotfixes", "bz-dive"]
SRC_CLIENT = ["client-npc-hub", "client-npc-liste", "client-datenbank"]
SRC_ALL = SRC_OFF + SRC_CLIENT

def history():
    return [{"actor": "AI-documentary-draft", "note": ACTOR_NOTE, "at": UPDATED, "version": 1}]

def entry(eid, title, description, sub, slug, lead, key_points, sections, confirmed, pending, dates, relations):
    lead_block = dict(lead) if "fr" in lead else lead
    if "src" not in lead_block:
        lead_block = {**lead_block, "src": SRC_ALL}
    return {
        "id": eid, "title": title, "description": description, "category": "creatures",
        "subcategory": sub, "status": "draft", "updatedAt": UPDATED, "gameVersion": GV,
        "version": 1, "verification": "à confirmer", "identityConfirmed": False,
        "relations": relations, "sources": SOURCES_CORE, "history": history(),
        "article": {
            "format": 1, "slug": slug, "illustration": "creatures",
            "lead": lead_block, "keyPoints": key_points, "sections": sections,
            "confirmed": confirmed, "pending": pending, "dates": dates,
        },
    }

def sort_npcs(rows):
    return sorted(rows, key=lambda r: (0 if "x" in r["tags"] else 1, r["name"].casefold()))

def group_by_canon(rows):
    g = defaultdict(list)
    for r in rows:
        g[r["canon"]].append(r)
    return g

def page_tables_by_zone(npcs_by_zone, drops, fr_zones, src_keys):
    sections = []
    for canon in sorted(npcs_by_zone, key=lambda z: zone_label(z, fr_zones, "fr").casefold()):
        chunk = sort_npcs(npcs_by_zone[canon])
        zfr = zone_label(canon, fr_zones, "fr")
        zen = zone_label(canon, fr_zones, "en")
        n = len(chunk)
        n_boss = sum(1 for r in chunk if "x" in r["tags"])
        sid = re.sub(r"[^a-z0-9]+", "-", canon.lower()).strip("-")[:60] or "zone"
        extra_fr = f", dont {n_boss} boss" if n_boss else ""
        extra_en = f", including {n_boss} bosses" if n_boss else ""
        cap_fr = f"{zfr} : {n} PNJ{extra_fr} — données extraites du client, à confirmer (12/11/2026)."
        cap_en = f"{zen}: {n} NPCs{extra_en} — client-extracted data, to be confirmed (12 November 2026)."
        sections.append({"id": sid, "title": T(zfr, zen),
                         "blocks": [table(cap_fr, cap_en, [npc_row(r, drops, fr_zones) for r in chunk], src_keys)]})
    return sections

def how_to_read_section():
    n0, n1 = WIKI["notes"]; o0, o1 = WIKI["onyxia"]; f0, f1 = WIKI["foxes"]; d0, d1 = WIKI["documented"]
    return {"id": "lire-cette-liste", "title": T("Comment lire cette liste", "How to read this list"), "blocks": [
        para(
            "Blizzard ne publie pas de bestiaire complet de World of Warcraft: Forever. "
            "Les noms officiels déjà traités sur ce wiki (correctifs, Onyxia, famille des renards) restent sur leurs fiches : "
            f"créatures des notes officielles ({n0}), Onyxia ({o0}), renards ({f0}), créatures documentées ({d0}). "
            "Cette série de pages ajoute la liste des 3 284 PNJ de la base Forever consultée le 12 novembre 2026.",
            "Blizzard does not publish a complete bestiary for World of Warcraft: Forever. "
            "Official names already covered on this wiki (hotfixes, Onyxia, the fox family) stay on their sheets: "
            f"creatures in official notes ({n1}), Onyxia ({o1}), foxes ({f1}), documented creatures ({d1}). "
            "These pages add the 3,284 NPCs from the Forever database consulted on 12 November 2026.",
            SRC_ALL),
        lst([
            item("Chaque ligne issue de la liste de PNJ est à confirmer. Aucun nom français officiel n’apparaît dans cette liste : le nom anglais est conservé.",
                 "Every row from the NPC list is to be confirmed. No official French name appears in that list: the English name is kept.", SRC_CLIENT),
            item("Type (bête, humanoïde, démon…), classification normal/élite/rare, faction, sous-zone et drapeau « dépeçable » ne figurent pas dans cette liste : la colonne Type reste « non indiqué ». Un PNJ est classé « boss » seulement si la liste le marque ainsi (étiquette x). Aucune étiquette « rare » n’y figure.",
                 "Type (beast, humanoid, demon…), normal/elite/rare classification, faction, sub-zone and a “skinnable” flag are not in this list: the Type column stays “not given”. An NPC is classed as “boss” only when the list marks it so (tag x). There is no “rare” tag in the list.", SRC_CLIENT),
            item("Le rôle reprend les étiquettes de la liste : boss, vendeur, donneur de quête, objectif de quête, butin indiqué. L’absence d’étiquette « butin indiqué » ne signifie pas que le PNJ n’a pas de butin.",
                 "Role follows the list tags: boss, vendor, quest giver, quest objective, loot flagged. The absence of a “loot flagged” tag does not mean the NPC has no loot.", SRC_CLIENT),
            item("Les recettes déjà documentées sur Recettes et plans avancés sont rappelées, avec un lien vers cette fiche, sans taux d’obtention.",
                 "Recipes already documented on Recipes and advanced blueprints are recalled, with a link to that sheet, and without drop rates.", SRC_CLIENT),
        ], SRC_ALL),
    ]}

def history_section():
    return {"id": "historique-des-corrections", "title": T("Historique des corrections", "Correction history"), "blocks": [
        lst([item("12 novembre 2026 — première rédaction du bestiaire à partir de la liste de 3 284 PNJ et des sources officielles déjà citées. Brouillon.",
                  "12 November 2026 — first draft of the bestiary from the 3,284-NPC list and the official sources already cited. Draft.", SRC_ALL)], SRC_ALL),
    ]}

COMMON_CONFIRMED = [item(
    "Blizzard ne publie pas de bestiaire complet de World of Warcraft: Forever ; ses textes officiels nomment toutefois certaines créatures et les neuf nouveaux donjons, ainsi que les raids du 9 décembre 2026.",
    "Blizzard does not publish a complete bestiary for World of Warcraft: Forever; its official texts do name some creatures and the nine new dungeons, as well as the raids of 9 December 2026.",
    SRC_OFF)]
COMMON_PENDING = [
    T("Type, élite, rare, faction, hostilité, sous-zone et drapeau de dépeçage : non indiqués dans la liste de PNJ consultée.",
      "Type, elite, rare, faction, hostility, sub-zone and skinnable flag: not given in the NPC list consulted."),
    T("La liste française de PNJ reprend les mêmes noms anglais que la liste anglaise (aucune traduction officielle française dans ce fichier).",
      "The French NPC list uses the same English names as the English list (no official French names in that file)."),
    T("Les créatures anonymes ou les mobs réguliers absents de ces 3 284 lignes ne sont pas inventoriés ici.",
      "Unnamed creatures or regular mobs missing from these 3,284 rows are not listed here."),
]
COMMON_DATES = [
    {"date": "2026-09-13", "fr": "Présentation officielle « Au cœur de Forever ».", "en": "Official Deep Dive presentation.", "src": ["bz-dive"]},
    {"date": "2026-10-20", "fr": "Articles officiels : nouveaux donjons et aperçu des raids.", "en": "Official articles: new dungeons and raid overview.", "src": ["bz-dungeons", "bz-raids"]},
    {"date": "2026-11-07", "fr": "Mention, sur la base d’objets de la même documentation de jeu, du client WoW Forever build 1.60.1.70862.", "en": "The item database in the same game documentation cites WoW Forever client build 1.60.1.70862.", "src": ["client-datenbank"]},
    {"date": "2026-11-12", "fr": "Consultation de la liste de 3 284 PNJ de la base Forever (hub et fichiers JSON).", "en": "Consultation of the 3,284-NPC list from the Forever database (hub and JSON files).", "src": ["client-npc-hub", "client-npc-liste"]},
]

def rels(*extra):
    out = []
    for i in ["forever-bestiary", *extra, "forever-creatures-official-notes", "forever-creature-onyxia",
              "article-forever-creatures", "forever-professions-blueprints"]:
        if i not in out:
            out.append(i)
    return out

def dedupe_rel(e):
    seen, rel = set(), []
    for r in e["relations"]:
        if r != e["id"] and r not in seen:
            seen.add(r); rel.append(r)
    e["relations"] = rel
    return e

def counts_block(rows):
    return (len(rows),
            sum(1 for r in rows if "x" in r["tags"]),
            sum(1 for r in rows if "h" in r["tags"]),
            sum(1 for r in rows if "q" in r["tags"]),
            sum(1 for r in rows if "z" in r["tags"]),
            sum(1 for r in rows if "b" in r["tags"]))

def build():
    rows, fr_zones = load_lists()
    drops = recipe_drops()
    by_zone = group_by_canon(rows)
    unlocated = by_zone.pop("", [])
    zephras = by_zone.pop("Zephras Isle", [])
    shen = by_zone.pop("Shen'dralas", [])
    forever_d_zones, classic_d_zones, raid_zones = {}, {}, {}
    kalimdor_zones, ek_zones, leftover = {}, {}, {}
    for z in list(by_zone):
        if z in FOREVER_DUNGEON_CANON:
            forever_d_zones[z] = by_zone.pop(z)
        elif z in CLASSIC_DUNGEON:
            classic_d_zones[z] = by_zone.pop(z)
        elif z in RAID:
            raid_zones[z] = by_zone.pop(z)
    for z, chunk in list(by_zone.items()):
        if z in KALIMDOR:
            kalimdor_zones[z] = chunk
        elif z in EASTERN:
            ek_zones[z] = chunk
        else:
            leftover[z] = chunk
    if leftover:
        raise SystemExit(f"unclassified zones: {sorted(leftover)}")
    bosses = [r for r in rows if "x" in r["tags"]]
    n, n_boss, n_vend, n_q, n_obj, n_loot = counts_block(rows)
    n_zones_raw = 79
    n_zones_canon = len({r["canon"] for r in rows if r["canon"]}) + (1 if unlocated else 0)
    paths = {
        "bosses": ("/fr/creatures/bestiaire-bosses/", "/en/creatures/bestiary-bosses/"),
        "zephras": ("/fr/creatures/bestiaire-ile-de-zephras/", "/en/creatures/bestiary-zephras-isle/"),
        "shen": ("/fr/creatures/bestiaire-shen-dralas/", "/en/creatures/bestiary-shen-dralas/"),
        "fd": ("/fr/creatures/bestiaire-donjons-forever/", "/en/creatures/bestiary-forever-dungeons/"),
        "cd": ("/fr/creatures/bestiaire-donjons-classiques/", "/en/creatures/bestiary-classic-dungeons/"),
        "raids": ("/fr/creatures/bestiaire-raids/", "/en/creatures/bestiary-raids/"),
        "kal": ("/fr/creatures/bestiaire-kalimdor/", "/en/creatures/bestiary-kalimdor/"),
        "ek": ("/fr/creatures/bestiaire-royaumes-de-lest/", "/en/creatures/bestiary-eastern-kingdoms/"),
        "unk": ("/fr/creatures/bestiaire-zone-non-indiquee/", "/en/creatures/bestiary-unlocated-zone/"),
    }
    index_zone_rows = []
    def add_index_row(group_fr, group_en, canon, chunk, page_fr, page_en):
        zfr = zone_label(canon, fr_zones, "fr") if canon else "Zone non indiquée"
        zen = zone_label(canon, fr_zones, "en") if canon else "Zone not given"
        nb = sum(1 for r in chunk if "x" in r["tags"])
        index_zone_rows.append([
            T(group_fr, group_en), T(zfr, zen), T(str(len(chunk)), str(len(chunk))),
            T(str(nb), str(nb)), T(page_fr, page_en),
        ])
    add_index_row("Forever, zone", "Forever zone", "Zephras Isle", zephras, *paths["zephras"])
    add_index_row("Forever, zone", "Forever zone", "Shen'dralas", shen, *paths["shen"])
    for z, chunk in sorted(forever_d_zones.items(), key=lambda kv: zone_label(kv[0], fr_zones, "fr")):
        add_index_row("Donjons Forever", "Forever dungeons", z, chunk, *paths["fd"])
    for z, chunk in sorted(classic_d_zones.items(), key=lambda kv: zone_label(kv[0], fr_zones, "fr")):
        add_index_row("Donjons classiques (présents dans l’extrait)", "Classic-named dungeons (in the extract)", z, chunk, *paths["cd"])
    for z, chunk in sorted(raid_zones.items(), key=lambda kv: zone_label(kv[0], fr_zones, "fr")):
        add_index_row("Raids (présents dans l’extrait)", "Raids (in the extract)", z, chunk, *paths["raids"])
    for z, chunk in sorted(kalimdor_zones.items(), key=lambda kv: zone_label(kv[0], fr_zones, "fr")):
        add_index_row("Kalimdor (extérieur)", "Kalimdor (overworld)", z, chunk, *paths["kal"])
    for z, chunk in sorted(ek_zones.items(), key=lambda kv: zone_label(kv[0], fr_zones, "fr")):
        add_index_row("Royaumes de l’Est (extérieur)", "Eastern Kingdoms (overworld)", z, chunk, *paths["ek"])
    add_index_row("Sans zone", "No zone", "", unlocated, *paths["unk"])

    role_rows = []
    for tag, fr_l, en_l in [
        ("x", "Boss (étiquette x)", "Boss (tag x)"),
        ("h", "Vendeur (h)", "Vendor (h)"),
        ("b", "Butin indiqué (b)", "Loot flagged (b)"),
        ("z", "Objectif de quête (z)", "Quest objective (z)"),
        ("q", "Donneur de quête (q)", "Quest giver (q)"),
        ("l", "Formateur (l)", "Trainer (l)"),
        ("t", "Vol à la tire (t)", "Pick pocket (t)"),
    ]:
        c = sum(1 for r in rows if tag in r["tags"])
        role_rows.append([T(fr_l, en_l), T(str(c), str(c)), T("à confirmer", "to be confirmed")])

    notes = WIKI["notes"]
    official_missing = [
        ["Krek the Noxious", "Rives Claires", "Butin corrigé (06/11/2026)"],
        ["Ridgeshade Lurkers", "Durotar", "Ont désormais du butin (06/11/2026)"],
        ["Pelluk", "Marais des Chagrins", "Apparition corrigée (05–06/11/2026)"],
        ["Yarrog Baneshadow", "Durotar", "Réapparition corrigée (05/11/2026)"],
        ["Troggs de la carrière Grol’bolar", "Dun Morogh", "Réapparition corrigée (06/11/2026)"],
        ["Lasher Sproutlings, Blooming Lashers, Wrathvine", "Teldrassil", "Sensibilité à la nature corrigée (06/11/2026)"],
        ["Murlocs (certains)", "Marécage d’Âprefange", "Réapparition corrigée (05/11/2026)"],
    ]
    off_rows = [[T(name, name), T(zone, zone), T(what, what), T(f"voir {notes[0]}", f"see {notes[1]}")]
                for name, zone, what in official_missing]

    index_head = [T("Groupe", "Group"), T("Zone", "Zone"), T("PNJ", "NPCs"), T("Boss", "Bosses"), T("Page", "Page")]
    def index_table(caption_fr, caption_en, head, rows, src_keys):
        return {"type": "table", "caption": T(clip(caption_fr, 300), clip(caption_en, 300)),
                "head": head, "rows": rows, "src": src_keys}

    index = entry(
        "forever-bestiary",
        T("Bestiaire", "Bestiary"),
        T(f"Index du bestiaire Forever : {n} PNJ de la liste de jeu (à confirmer), plus les créatures déjà nommées officiellement. Par zone et par rôle ; les boss sont mis en avant. Type, rares et faction : souvent non indiqués.",
          f"Index of the Forever bestiary: {n} NPCs from the game list (to be confirmed), plus creatures already officially named. By zone and by role; bosses are highlighted. Type, rares and faction: often not given."),
        "bestiaire", {"fr": "bestiaire", "en": "bestiary"},
        T("Blizzard ne publie pas de bestiaire complet. Ce wiki rassemble d’abord les créatures déjà nommées dans les textes officiels "
          f"(fiche dédiée : {notes[0]}), puis la liste de {n} PNJ de la base Forever consultée le 12 novembre 2026, "
          "chaque ligne de cette liste restant à confirmer. Les mobs réguliers absents de cette liste ne sont pas inventés.",
          "Blizzard does not publish a complete bestiary. This wiki gathers first the creatures already named in official texts "
          f"(dedicated sheet: {notes[1]}), then the {n} NPCs from the Forever database consulted on 12 November 2026, "
          "each row from that list remaining to be confirmed. Regular mobs missing from that list are not invented."),
        [
            item(f"{n} PNJ dans la liste consultée, répartis en {n_zones_canon} zones après regroupement d’étiquettes identiques.",
                 f"{n} NPCs in the list consulted, across {n_zones_canon} zones after merging identical labels.", SRC_CLIENT),
            item(f"{n_boss} boss étiquetés dans la liste (plus Onyxia, officielle, non étiquetée « boss » dans cette liste). Aucune étiquette « rare ».",
                 f"{n_boss} bosses tagged in the list (plus Onyxia, official, not tagged as a boss in this list). No “rare” tag.", SRC_ALL),
            item("Type, élite, faction, sous-zone et dépeçage : non indiqués dans cette liste.",
                 "Type, elite, faction, sub-zone and skinning: not given in this list.", SRC_CLIENT),
        ],
        [
            how_to_read_section(),
            {"id": "perimetre", "title": T("Périmètre et preuves Forever", "Scope and Forever evidence"), "blocks": [
                para("La liste est publiée comme base de PNJ de WoW Forever (3 284 PNJ avec des données du jeu). "
                     "Elle contient des zones propres à Forever (île de Zéphras, Shen’dralas, salle des Thanes, "
                     "ruines de Lordaeron, excavations des Paluns, cité de Dalaran). "
                     "La même documentation de jeu, sur sa base d’objets, indique : données de jeu, client WoW Forever "
                     "build 1.60.1.70862, au 7 novembre 2026. La page d’accueil des PNJ elle-même ne répète pas ce numéro de build.",
                     "The list is published as the WoW Forever NPC database (3,284 NPCs with in-game data). "
                     "It includes zones unique to Forever (Zephras Isle, Shen’dralas, Hall of Thanes, "
                     "Ruins of Lordaeron, Excavation Site: Wetlands, City of Dalaran). "
                     "The same game documentation, on its item database, states: game data, WoW Forever client "
                     "build 1.60.1.70862, as of 7 November 2026. The NPC hub page itself does not repeat that build number.",
                     SRC_ALL),
                para("N’ont pas été repris : les donjons Forever officiels dont aucun PNJ n’apparaît dans cette liste "
                     "(cité Submergée, bastion Krol’dok, prison d’Alcaz, repaire des Noiregueules, terrasse du Façonneur), "
                     "ni les raids officiels encore sans roster dans l’extrait (profondeurs des Saisons, sommet d’Hyjal — "
                     "Onyxia a une fiche officielle). Rives Claires et le mont Hyjal n’ont aucun PNJ dans cette liste. "
                     "Deux étiquettes d’extrait ont été regroupées avec mention : « Insel Zephras » avec l’île de Zéphras, "
                     "« The Hall of Thanes » avec la salle des Thanes, « Temple of Ahn'Qiraj » avec « Ahn'Qiraj Temple ». "
                     "« Dalaran » (4 PNJ) n’a pas été fusionné avec la cité de Dalaran (9 boss).",
                     "Not included as rosters: official Forever dungeons with no NPC in this list "
                     "(The Drowned City, Krol’dok Stronghold, Alcaz Prison, Blackmaw Hold, The Shaper’s Terrace), "
                     "and official raids still without a roster in the extract (Barrow Deeps, Hyjal Summit — "
                     "Onyxia has an official sheet). Riverglades and Mount Hyjal have no NPC in this list. "
                     "Two extract labels were grouped with a note: “Insel Zephras” with Zephras Isle, "
                     "“The Hall of Thanes” with Hall of Thanes, “Temple of Ahn'Qiraj” with “Ahn'Qiraj Temple”. "
                     "“Dalaran” (4 NPCs) was not merged with City of Dalaran (9 bosses).",
                     SRC_ALL),
            ]},
            {"id": "par-zone", "title": T("Par zone", "By zone"), "blocks": [
                index_table(f"Index par zone : {n} PNJ, {n_zones_canon} lignes de zone (liste du 12/11/2026, à confirmer).",
                            f"Index by zone: {n} NPCs, {n_zones_canon} zone rows (list of 12 November 2026, to be confirmed).",
                            index_head, index_zone_rows, SRC_CLIENT),
            ]},
            {"id": "par-role", "title": T("Par rôle (boss mis en avant)", "By role (bosses highlighted)"), "blocks": [
                para(f"La liste ne donne pas le type de créature (bête, humanoïde, démon…). Le classement ci-dessous suit les étiquettes de rôle. "
                     f"Les {n_boss} boss ont une page dédiée ({paths['bosses'][0]}). Aucune créature n’est étiquetée « rare » dans l’extrait ; "
                     "Blizzard a évoqué des butins de créatures rares sans en publier la liste (voir la fiche des notes officielles).",
                     f"The list does not give creature type (beast, humanoid, demon…). The table below follows role tags. "
                     f"The {n_boss} bosses have a dedicated page ({paths['bosses'][1]}). No creature is tagged “rare” in the extract; "
                     "Blizzard mentioned rare-creature loot without publishing a list (see the official-notes sheet).",
                     SRC_ALL),
                index_table("Effectifs par étiquette de rôle dans la liste de 3 284 PNJ (à confirmer). Un même PNJ peut porter plusieurs étiquettes.",
                            "Counts by role tag in the 3,284-NPC list (to be confirmed). One NPC may carry several tags.",
                            [T("Rôle", "Role"), T("Effectif", "Count"), T("Statut", "Status")], role_rows, SRC_CLIENT),
            ]},
            {"id": "officiel-hors-liste", "title": T("Créatures officielles absentes de l’extrait PNJ", "Official creatures missing from the NPC extract"), "blocks": [
                para(f"Ces noms viennent des correctifs officiels des 5 et 6 novembre 2026. Ils n’apparaissent pas dans la liste de 3 284 PNJ. "
                     f"Le détail reste sur la fiche déjà publiée ({notes[0]}), sans statut « rare » inventé. The Baron, lui, figure dans l’extrait "
                     "(ruines de Lordaeron, boss) et est aussi nommé officiellement.",
                     f"These names come from the official hotfixes of 5 and 6 November 2026. They do not appear in the 3,284-NPC list. "
                     f"The detail stays on the already published sheet ({notes[1]}), with no invented “rare” status. The Baron does appear "
                     "in the extract (Ruins of Lordaeron, boss) and is also officially named.",
                     SRC_OFF),
                index_table("Créatures nommées par les correctifs officiels et absentes de la liste de PNJ — renvoyer à la fiche officielle.",
                            "Creatures named in official hotfixes and absent from the NPC list — see the official sheet.",
                            [T("Créature", "Creature"), T("Zone", "Zone"), T("Ce que dit Blizzard", "What Blizzard says"), T("Fiche", "Sheet")],
                            off_rows, ["bz-hotfixes"]),
            ]},
            history_section(),
        ],
        COMMON_CONFIRMED + [item(
            "Les neuf nouveaux donjons et les raids du 9 décembre 2026 (profondeurs des Saisons, sommet d’Hyjal, repaire d’Onyxia) sont officiellement nommés, avec des tranches de niveaux pour les donjons nouveaux.",
            "The nine new dungeons and the 9 December 2026 raids (Barrow Deeps, Hyjal Summit, Onyxia’s Lair) are officially named, with level ranges for the new dungeons.",
            ["bz-dungeons", "bz-raids"])],
        COMMON_PENDING + [T(
            "Le hub des PNJ est bien libellé Forever et contient des zones propres à Forever, mais il ne reprend pas le numéro de build 1.60.1.70862 que porte la base d’objets de la même documentation.",
            "The NPC hub is labelled Forever and contains Forever-only zones, but it does not repeat build number 1.60.1.70862, which appears on the item database in the same documentation.")],
        COMMON_DATES,
        [i for i in ["forever-bestiary-bosses", "forever-bestiary-zephras", "forever-bestiary-shendralas",
                     "forever-bestiary-forever-dungeons", "forever-bestiary-classic-dungeons", "forever-bestiary-raids",
                     "forever-bestiary-kalimdor", "forever-bestiary-eastern-kingdoms", "forever-bestiary-unlocated",
                     "forever-creatures-official-notes", "forever-creature-onyxia", "forever-creature-family-fox",
                     "article-forever-creatures", "forever-professions-blueprints", "forever-zone-zephras-isle",
                     "forever-zone-shendralas", "forever-zone-riverglades", "article-forever-raids"]],
    )
    return {
        "rows": rows, "fr_zones": fr_zones, "drops": drops, "unlocated": unlocated, "zephras": zephras, "shen": shen,
        "forever_d_zones": forever_d_zones, "classic_d_zones": classic_d_zones, "raid_zones": raid_zones,
        "kalimdor_zones": kalimdor_zones, "ek_zones": ek_zones, "bosses": bosses,
        "n": n, "n_boss": n_boss, "n_vend": n_vend, "n_q": n_q, "n_obj": n_obj, "n_loot": n_loot,
        "n_zones_raw": n_zones_raw, "n_zones_canon": n_zones_canon, "index": index, "paths": paths,
    }

def finish(ctx):
    drops, fr_zones = ctx["drops"], ctx["fr_zones"]
    bosses, n_boss = ctx["bosses"], ctx["n_boss"]
    notes = WIKI["notes"]; ony = WIKI["onyxia"]
    boss_table_rows = [npc_row(r, drops, fr_zones) for r in sort_npcs(bosses)]
    ony_extra = [
        T("Onyxia", "Onyxia"), T("non indiqué dans la liste", "not given in the list"),
        T("non indiqué", "not given"), T("boss (officiel)", "boss (official)"),
        T("rencontre de raid officielle", "official raid encounter"),
        T("Repaire d’Onyxia (officiel) — zone vide dans la liste de PNJ", "Onyxia’s Lair (official) — empty zone in the NPC list"),
        T(f"voir {ony[0]}", f"see {ony[1]}"),
        T("officiel confirmé — fiche déjà en ligne ; dans la liste de PNJ : zone vide, étiquette objectif de quête, pas « boss ».",
          "official, confirmed — existing sheet; in the NPC list: empty zone, quest-objective tag, not “boss”."),
    ]
    bosses_entry = entry(
        "forever-bestiary-bosses", T("Bestiaire : boss", "Bestiary: bosses"),
        T(f"{n_boss} boss étiquetés dans la liste de PNJ Forever (à confirmer), plus Onyxia (officielle). Rares : aucune étiquette dans l’extrait.",
          f"{n_boss} bosses tagged in the Forever NPC list (to be confirmed), plus Onyxia (official). Rares: no tag in the extract."),
        "bestiaire-bosses", {"fr": "bestiaire-bosses", "en": "bestiary-bosses"},
        T(f"Cette page recense les {n_boss} PNJ que la liste Forever marque comme boss (étiquette x), tous à confirmer, "
          f"ainsi qu’Onyxia, rencontre officielle déjà documentée ({ony[0]}). "
          "The Baron, boss des ruines de Lordaeron dans l’extrait, est aussi nommé par les correctifs officiels.",
          f"This page lists the {n_boss} NPCs that the Forever list marks as bosses (tag x), all to be confirmed, "
          f"plus Onyxia, an official encounter already documented ({ony[1]}). "
          "The Baron, a Ruins of Lordaeron boss in the extract, is also named in official hotfixes."),
        [
            item(f"{n_boss} boss étiquetés dans la liste, répartis dans les donjons présents dans l’extrait.",
                 f"{n_boss} bosses tagged in the list, in the dungeons present in the extract.", SRC_CLIENT),
            item("Onyxia est une rencontre officielle ; elle n’est pas étiquetée boss dans la liste de PNJ.",
                 "Onyxia is an official encounter; she is not tagged as a boss in the NPC list.", SRC_OFF),
            item("The Baron est nommé officiellement (correctifs) et figure dans l’extrait comme boss des ruines de Lordaeron.",
                 "The Baron is officially named (hotfixes) and appears in the extract as a Ruins of Lordaeron boss.", SRC_ALL),
        ],
        [how_to_read_section(),
         {"id": "boss-officiels", "title": T("Rencontre officielle : Onyxia", "Official encounter: Onyxia"), "blocks": [
             table("Onyxia — identité et raid officiels ; le niveau et la zone ne sont pas remplis dans la liste de PNJ.",
                   "Onyxia — official identity and raid; level and zone are not filled in the NPC list.",
                   [ony_extra], SRC_OFF)]},
         {"id": "boss-extrait", "title": T("Boss de la liste de PNJ", "Bosses in the NPC list"), "blocks": [
             table(f"{n_boss} boss étiquetés dans la liste de PNJ Forever — données extraites du client, à confirmer (12/11/2026). The Baron : nom aussi officiel.",
                   f"{n_boss} bosses tagged in the Forever NPC list — client-extracted data, to be confirmed (12 November 2026). The Baron: name also official.",
                   boss_table_rows, SRC_ALL)]},
         history_section()],
        COMMON_CONFIRMED,
        COMMON_PENDING + [T("Cinq donjons Forever officiels n’ont aucun boss dans cette liste (cité Submergée, bastion Krol’dok, prison d’Alcaz, repaire des Noiregueules, terrasse du Façonneur) : aucun roster n’est inventé.",
                            "Five official Forever dungeons have no boss in this list (The Drowned City, Krol’dok Stronghold, Alcaz Prison, Blackmaw Hold, The Shaper’s Terrace): no roster is invented.")],
        COMMON_DATES,
        rels("forever-bestiary-forever-dungeons", "forever-bestiary-classic-dungeons", "forever-bestiary-raids",
             "forever-dungeon-ruins-of-lordaeron", "forever-raid-onyxias-lair", "forever-creature-onyxia"),
    )

    zephras, shen = ctx["zephras"], ctx["shen"]
    zeph_n = len(zephras)
    zpath = WIKI_ZONE["Zephras Isle"]
    zeph_page = entry(
        "forever-bestiary-zephras", T("Bestiaire : île de Zéphras", "Bestiary: Zephras Isle"),
        T(f"{zeph_n} PNJ de l’île de Zéphras dans la liste Forever (à confirmer), dont des lignes étiquetées « Insel Zephras » dans l’extrait.",
          f"{zeph_n} NPCs of Zephras Isle in the Forever list (to be confirmed), including rows labelled “Insel Zephras” in the extract."),
        "bestiaire-zone", {"fr": "bestiaire-ile-de-zephras", "en": "bestiary-zephras-isle"},
        T(f"L’île de Zéphras est une zone officielle de Forever (fiche : {zpath[0]}). "
          f"Cette page liste les {zeph_n} PNJ qui lui sont rattachés dans la liste consultée, à confirmer. "
          "Neuf lignes portent l’étiquette allemande « Insel Zephras » dans l’extrait : elles sont regroupées ici, sans traduction inventée des noms.",
          f"Zephras Isle is an official Forever zone (sheet: {zpath[1]}). "
          f"This page lists the {zeph_n} NPCs attached to it in the list consulted, to be confirmed. "
          "Nine rows carry the German label “Insel Zephras” in the extract: they are grouped here, without invented name translations."),
        [item(f"{zeph_n} PNJ rattachés à l’île de Zéphras après regroupement de l’étiquette « Insel Zephras ».",
              f"{zeph_n} NPCs attached to Zephras Isle after grouping the “Insel Zephras” label.", SRC_CLIENT),
         item("Zerril Softbreeze vend des recettes de cuisine déjà documentées (à confirmer) sur la fiche des plans avancés.",
              "Zerril Softbreeze sells cooking recipes already documented (to be confirmed) on the advanced-blueprints sheet.", SRC_CLIENT)],
        [how_to_read_section(),
         {"id": "liste", "title": T("PNJ de l’île de Zéphras", "NPCs of Zephras Isle"), "blocks": [
             table(f"Île de Zéphras : {zeph_n} PNJ — données extraites du client, à confirmer (12/11/2026). Neuf lignes : étiquette extraite « Insel Zephras ».",
                   f"Zephras Isle: {zeph_n} NPCs — client-extracted data, to be confirmed (12 November 2026). Nine rows: extract label “Insel Zephras”.",
                   [npc_row(r, drops, fr_zones, zone_override="Zephras Isle") for r in sort_npcs(zephras)], SRC_CLIENT)]},
         history_section()],
        COMMON_CONFIRMED, COMMON_PENDING, COMMON_DATES, rels("forever-zone-zephras-isle"),
    )

    spath = WIKI_ZONE["Shen'dralas"]
    shen_page = entry(
        "forever-bestiary-shendralas", T("Bestiaire : Shen’dralas", "Bestiary: Shen’dralas"),
        T(f"{len(shen)} PNJ de Shen’dralas dans la liste Forever (à confirmer).",
          f"{len(shen)} NPCs of Shen’dralas in the Forever list (to be confirmed)."),
        "bestiaire-zone", {"fr": "bestiaire-shen-dralas", "en": "bestiary-shen-dralas"},
        T(f"Shen’dralas est une zone officielle de Forever (fiche : {spath[0]}). "
          f"Cette page liste les {len(shen)} PNJ qui lui sont rattachés dans la liste consultée, à confirmer.",
          f"Shen’dralas is an official Forever zone (sheet: {spath[1]}). "
          f"This page lists the {len(shen)} NPCs attached to it in the list consulted, to be confirmed."),
        [item(f"{len(shen)} PNJ rattachés à Shen’dralas dans la liste consultée.",
              f"{len(shen)} NPCs attached to Shen’dralas in the list consulted.", SRC_CLIENT),
         item("Aucun de ces noms n’a de traduction française officielle dans la liste consultée ; le nom anglais est conservé, à confirmer.",
              "None of these names has an official French translation in the list consulted; the English name is kept, to be confirmed.", SRC_CLIENT)],
        [how_to_read_section(),
         {"id": "liste", "title": T("PNJ de Shen’dralas", "NPCs of Shen’dralas"), "blocks": [
             table(f"Shen’dralas : {len(shen)} PNJ — données extraites du client, à confirmer (12/11/2026).",
                   f"Shen’dralas: {len(shen)} NPCs — client-extracted data, to be confirmed (12 November 2026).",
                   [npc_row(r, drops, fr_zones) for r in sort_npcs(shen)], SRC_CLIENT)]},
         history_section()],
        COMMON_CONFIRMED, COMMON_PENDING, COMMON_DATES, rels("forever-zone-shendralas"),
    )

    forever_d_zones = ctx["forever_d_zones"]
    fd_n = sum(len(v) for v in forever_d_zones.values())
    fd_boss = sum(1 for chunk in forever_d_zones.values() for r in chunk if "x" in r["tags"])
    missing_fd = [
        ("La cité Submergée", "The Drowned City", "35–40", "/fr/donjons-raids/la-cite-submergee/", "/en/dungeons-raids/the-drowned-city/"),
        ("Bastion Krol’dok", "Krol’dok Stronghold", "40–45", "/fr/donjons-raids/bastion-krol-dok/", "/en/dungeons-raids/krol-dok-stronghold/"),
        ("Prison d’Alcaz", "Alcaz Prison", "48–53", "/fr/donjons-raids/prison-d-alcaz/", "/en/dungeons-raids/alcaz-prison/"),
        ("Repaire des Noiregueules", "Blackmaw Hold", "55–60", "/fr/donjons-raids/repaire-des-noiregueules/", "/en/dungeons-raids/blackmaw-hold/"),
        ("La terrasse du Façonneur", "The Shaper’s Terrace", "58–60", "/fr/donjons-raids/la-terrasse-du-faconneur/", "/en/dungeons-raids/shaper-s-terrace/"),
    ]
    miss_rows = [[T(a, b), T(c, c), T("aucun PNJ dans l’extrait", "no NPC in the extract"), T(d, e),
                  T("officiel confirmé (nom et niveaux) ; roster non publié", "official, confirmed (name and levels); roster not published")]
                 for a, b, c, d, e in missing_fd]
    fd_page = entry(
        "forever-bestiary-forever-dungeons", T("Bestiaire : donjons Forever", "Bestiary: Forever dungeons"),
        T(f"PNJ des donjons nouveaux déjà présents dans la liste ({fd_n}, dont {fd_boss} boss, à confirmer), et rappel des cinq donjons officiels encore sans roster dans l’extrait.",
          f"NPCs of the new dungeons already present in the list ({fd_n}, including {fd_boss} bosses, to be confirmed), plus the five official dungeons still without a roster in the extract."),
        "bestiaire-donjons", {"fr": "bestiaire-donjons-forever", "en": "bestiary-forever-dungeons"},
        T("Quatre donjons nouveaux de Forever ont des PNJ dans la liste consultée : salle des Thanes, ruines de Lordaeron, "
          "excavations des Paluns et cité de Dalaran (plus 4 PNJ étiquetés seulement « Dalaran »). "
          "The Baron y est aussi nommé officiellement. Cinq autres donjons officiels n’ont aucun PNJ dans cette liste : aucun boss n’est inventé.",
          "Four new Forever dungeons have NPCs in the list consulted: Hall of Thanes, Ruins of Lordaeron, "
          "Excavation Site: Wetlands and City of Dalaran (plus 4 NPCs labelled only “Dalaran”). "
          "The Baron is also officially named there. Five other official dungeons have no NPC in this list: no boss is invented."),
        [item(f"{fd_n} PNJ, dont {fd_boss} boss, dans les donjons Forever présents dans l’extrait.",
              f"{fd_n} NPCs, including {fd_boss} bosses, in the Forever dungeons present in the extract.", SRC_CLIENT),
         item("Cinq donjons Forever officiels (niveaux publiés le 20 octobre 2026) n’ont pas de liste de PNJ dans cet extrait.",
              "Five official Forever dungeons (levels published on 20 October 2026) have no NPC list in this extract.", SRC_OFF)],
        [how_to_read_section(),
         *page_tables_by_zone(forever_d_zones, drops, fr_zones, SRC_ALL),
         {"id": "donjons-sans-extrait", "title": T("Donjons officiels encore sans liste de PNJ", "Official dungeons still without an NPC list"), "blocks": [
             any_table("Donjons Forever officiels sans aucun PNJ dans la liste consultée le 12/11/2026. Noms et niveaux : sources officielles. Roster : non publié.",
                       "Official Forever dungeons with no NPC in the list consulted on 12 November 2026. Names and levels: official sources. Roster: not published.",
                       [T("Donjon", "Dungeon"), T("Niveaux officiels", "Official levels"), T("PNJ dans l’extrait", "NPCs in the extract"), T("Fiche déjà en ligne", "Existing sheet"), T("Statut", "Status")],
                       miss_rows, ["bz-dungeons"])]},
         history_section()],
        COMMON_CONFIRMED,
        COMMON_PENDING + [T("L’étiquette « Dalaran » (4 PNJ) n’a pas été fusionnée avec « City of Dalaran » (9 boss) : ce sont deux libellés distincts dans l’extrait.",
                            "The “Dalaran” label (4 NPCs) was not merged with “City of Dalaran” (9 bosses): they are two distinct labels in the extract.")],
        COMMON_DATES,
        rels("forever-bestiary-bosses", "forever-dungeon-hall-of-thanes", "forever-dungeon-ruins-of-lordaeron",
             "forever-dungeon-excavation-site", "forever-dungeon-city-of-dalaran", "forever-dungeon-drowned-city",
             "forever-dungeon-kroldok-stronghold", "forever-dungeon-alcaz-prison", "forever-dungeon-blackmaw-hold",
             "forever-dungeon-shapers-terrace"),
    )

    classic_d_zones = ctx["classic_d_zones"]
    cd_n = sum(len(v) for v in classic_d_zones.values())
    cd_boss = sum(1 for chunk in classic_d_zones.values() for r in chunk if "x" in r["tags"])
    cd_page = entry(
        "forever-bestiary-classic-dungeons",
        T("Bestiaire : donjons classiques (extrait Forever)", "Bestiary: classic-named dungeons (Forever extract)"),
        T(f"{cd_n} PNJ, dont {cd_boss} boss, dans les donjons au nom classique présents dans la liste Forever (à confirmer). Le butin a été retravaillé pour Forever ; cette page ne reprend pas de tables Classic Era.",
          f"{cd_n} NPCs, including {cd_boss} bosses, in classic-named dungeons present in the Forever list (to be confirmed). Loot was reworked for Forever; this page does not reuse Classic Era tables."),
        "bestiaire-donjons", {"fr": "bestiaire-donjons-classiques", "en": "bestiary-classic-dungeons"},
        T(f"Les donjons au nom classique restent dans Forever, avec un butin retravaillé selon Blizzard. "
          f"Cette page ne liste que les {cd_n} PNJ de ces instances qui figurent dans la liste Forever consultée, à confirmer. "
          "Les recettes de boss déjà relevées sont renvoyées vers Recettes et plans avancés, sans taux.",
          f"Classic-named dungeons remain in Forever, with reworked loot according to Blizzard. "
          f"This page lists only the {cd_n} NPCs of these instances that appear in the Forever list consulted, to be confirmed. "
          "Boss recipes already recorded are linked to Recipes and advanced blueprints, without rates."),
        [item(f"{cd_n} PNJ, dont {cd_boss} boss, dans les donjons classiques présents dans l’extrait.",
              f"{cd_n} NPCs, including {cd_boss} bosses, in classic-named dungeons present in the extract.", SRC_CLIENT),
         item("Blizzard a indiqué que le butin des donjons connus a été retravaillé pour Forever ; aucune table Classic Era n’est recopiée ici.",
              "Blizzard stated that loot in familiar dungeons was reworked for Forever; no Classic Era table is copied here.", SRC_OFF)],
        [how_to_read_section(), *page_tables_by_zone(classic_d_zones, drops, fr_zones, SRC_CLIENT), history_section()],
        COMMON_CONFIRMED,
        COMMON_PENDING + [T("Plusieurs donjons classiques (par exemple les ailes Armurerie et Cathédrale du Monastère écarlate, Hache-tripes, Uldaman, profondeurs de Rochenoire) n’ont aucun PNJ dans cette liste.",
                            "Several classic-named dungeons (for example Scarlet Monastery Armory and Cathedral, Dire Maul, Uldaman, Blackrock Depths) have no NPC in this list.")],
        COMMON_DATES,
        rels("forever-bestiary-bosses", "forever-professions-blueprints", "article-forever-raids"),
    )

    raid_zones = ctx["raid_zones"]
    raid_n = sum(len(v) for v in raid_zones.values())
    raid_miss = [
        [T("Profondeurs des Saisons", "Barrow Deeps"), T("10 joueurs, ouverture le 9 décembre 2026", "10 players, opens 9 December 2026"),
         T("8 boss annoncés officiellement, non listés dans l’extrait PNJ", "8 bosses officially announced, not listed in the NPC extract"),
         T("officiel confirmé (annonce) ; roster non dans l’extrait", "official, confirmed (announcement); roster not in the extract")],
        [T("Sommet d’Hyjal", "Hyjal Summit"), T("20 joueurs, ouverture le 9 décembre 2026", "20 players, opens 9 December 2026"),
         T("13 boss annoncés officiellement, non listés dans l’extrait PNJ", "13 bosses officially announced, not listed in the NPC extract"),
         T("officiel confirmé (annonce) ; roster non dans l’extrait", "official, confirmed (announcement); roster not in the extract")],
        [T("Repaire d’Onyxia", "Onyxia’s Lair"), T("40 joueurs, ouverture le 9 décembre 2026", "40 players, opens 9 December 2026"),
         T(f"Onyxia : fiche {ony[0]} ; dans la liste de PNJ, zone vide", f"Onyxia: sheet {ony[1]}; in the NPC list, empty zone"),
         T("officiel confirmé", "official, confirmed")],
    ]
    rd_page = entry(
        "forever-bestiary-raids", T("Bestiaire : raids (extrait Forever et annonces)", "Bestiary: raids (Forever extract and announcements)"),
        T(f"{raid_n} PNJ rattachés à des raids au nom classique dans la liste Forever (à confirmer), plus les trois raids officiels du 9 décembre 2026.",
          f"{raid_n} NPCs attached to classic-named raids in the Forever list (to be confirmed), plus the three official raids of 9 December 2026."),
        "bestiaire-raids", {"fr": "bestiaire-raids", "en": "bestiary-raids"},
        T("Blizzard a annoncé pour le 9 décembre 2026 trois raids : profondeurs des Saisons (10), sommet d’Hyjal (20) et repaire d’Onyxia (40). "
          "Aucun roster de ces trois raids n’est dressé ici hors Onyxia, déjà documentée. "
          f"Cette page liste aussi les {raid_n} PNJ que la liste Forever rattache à Cœur du Magma, repaire de l’Aile noire, Zul’Gurub, Ahn’Qiraj et Naxxramas, à confirmer.",
          "Blizzard announced three raids for 9 December 2026: Barrow Deeps (10), Hyjal Summit (20) and Onyxia’s Lair (40). "
          "No roster for those three is compiled here except Onyxia, already documented. "
          f"This page also lists the {raid_n} NPCs that the Forever list attaches to Molten Core, Blackwing Lair, Zul’Gurub, Ahn’Qiraj and Naxxramas, to be confirmed."),
        [item("Trois raids officiels ouvrent le 9 décembre 2026 : profondeurs des Saisons, sommet d’Hyjal, repaire d’Onyxia.",
              "Three official raids open on 9 December 2026: Barrow Deeps, Hyjal Summit, Onyxia’s Lair.", SRC_OFF),
         item(f"{raid_n} PNJ rattachés aux raids au nom classique présents dans l’extrait, à confirmer.",
              f"{raid_n} NPCs attached to classic-named raids present in the extract, to be confirmed.", SRC_CLIENT)],
        [how_to_read_section(),
         {"id": "raids-officiels-decembre", "title": T("Raids officiels du 9 décembre 2026", "Official raids of 9 December 2026"), "blocks": [
             any_table("Raids officiellement annoncés pour le 9 décembre 2026. Les tailles et, pour les deux raids nouveaux, le nombre de boss viennent de Blizzard. Pas de liste de PNJ dans l’extrait, hors Onyxia.",
                       "Raids officially announced for 9 December 2026. Sizes and, for the two new raids, the boss counts come from Blizzard. No NPC list in the extract, except Onyxia.",
                       [T("Raid", "Raid"), T("Taille et date", "Size and date"), T("Boss / PNJ", "Bosses / NPCs"), T("Statut", "Status")],
                       raid_miss, ["bz-raids"])]},
         *page_tables_by_zone(raid_zones, drops, fr_zones, SRC_CLIENT),
         history_section()],
        COMMON_CONFIRMED,
        COMMON_PENDING + [T("Les libellés « Ahn'Qiraj Temple » et « Temple of Ahn'Qiraj » ont été regroupés. Blizzard n’a pas, dans les sources citées ici, confirmé le statut en jeu de Cœur du Magma, de l’Aile noire, de Zul’Gurub, d’Ahn’Qiraj ou de Naxxramas dans Forever.",
                            "The labels “Ahn'Qiraj Temple” and “Temple of Ahn'Qiraj” were grouped. Blizzard has not, in the sources cited here, confirmed the in-game status of Molten Core, Blackwing Lair, Zul’Gurub, Ahn’Qiraj or Naxxramas in Forever.")],
        COMMON_DATES,
        rels("forever-bestiary-bosses", "forever-raid-onyxias-lair", "forever-raid-barrow-deeps",
             "forever-raid-hyjal-summit", "forever-creature-onyxia", "article-forever-raids"),
    )

    kalimdor_zones, ek_zones, unlocated = ctx["kalimdor_zones"], ctx["ek_zones"], ctx["unlocated"]
    kal_n = sum(len(v) for v in kalimdor_zones.values())
    ek_n = sum(len(v) for v in ek_zones.values())
    kal_page = entry(
        "forever-bestiary-kalimdor", T("Bestiaire : Kalimdor (extérieur)", "Bestiary: Kalimdor (overworld)"),
        T(f"{kal_n} PNJ nommés des zones extérieures de Kalimdor dans la liste Forever (à confirmer). Surtout des donneurs de quête ; les mobs réguliers absents de la liste ne sont pas ajoutés.",
          f"{kal_n} named NPCs of Kalimdor overworld zones in the Forever list (to be confirmed). Mostly quest givers; regular mobs missing from the list are not added."),
        "bestiaire-continent", {"fr": "bestiaire-kalimdor", "en": "bestiary-kalimdor"},
        T(f"Cette page rassemble les {kal_n} PNJ que la liste Forever rattache aux zones extérieures de Kalimdor (y compris les capitales), à confirmer. "
          "Ce n’est pas un inventaire de tous les mobs de ces zones. Les créatures officielles de Durotar ou de Teldrassil absentes de la liste restent sur la fiche des notes officielles.",
          f"This page gathers the {kal_n} NPCs that the Forever list attaches to Kalimdor overworld zones (including capitals), to be confirmed. "
          "It is not an inventory of every mob in those zones. Official creatures of Durotar or Teldrassil missing from the list stay on the official-notes sheet."),
        [item(f"{kal_n} PNJ répartis dans {len(kalimdor_zones)} zones de Kalimdor, d’après la liste consultée.",
              f"{kal_n} NPCs across {len(kalimdor_zones)} Kalimdor zones, according to the list consulted.", SRC_CLIENT),
         item("Ce n’est pas un recensement de tous les mobs : seuls les PNJ de la liste Forever sont repris, à confirmer.",
              "This is not a census of every mob: only NPCs from the Forever list are included, to be confirmed.", SRC_CLIENT)],
        [how_to_read_section(), *page_tables_by_zone(kalimdor_zones, drops, fr_zones, SRC_CLIENT), history_section()],
        COMMON_CONFIRMED, COMMON_PENDING, COMMON_DATES,
        rels("forever-creatures-official-notes", "forever-zone-riverglades", "forever-zone-mount-hyjal"),
    )
    ek_page = entry(
        "forever-bestiary-eastern-kingdoms",
        T("Bestiaire : royaumes de l’Est (extérieur)", "Bestiary: Eastern Kingdoms (overworld)"),
        T(f"{ek_n} PNJ nommés des zones extérieures des royaumes de l’Est dans la liste Forever (à confirmer), y compris les capitales, Alterac Valley et le mont Rochenoire.",
          f"{ek_n} named NPCs of Eastern Kingdoms overworld zones in the Forever list (to be confirmed), including capitals, Alterac Valley and Blackrock Mountain."),
        "bestiaire-continent", {"fr": "bestiaire-royaumes-de-lest", "en": "bestiary-eastern-kingdoms"},
        T(f"Cette page rassemble les {ek_n} PNJ que la liste Forever rattache aux zones extérieures des royaumes de l’Est, à confirmer. "
          "Ce n’est pas un inventaire de tous les mobs. Dun Morogh apparaît aussi dans les notes officielles (troggs de la carrière Grol’bolar), absents de cette liste.",
          f"This page gathers the {ek_n} NPCs that the Forever list attaches to Eastern Kingdoms overworld zones, to be confirmed. "
          "It is not an inventory of every mob. Dun Morogh also appears in the official notes (Grol’bolar quarry troggs), which are absent from this list."),
        [item(f"{ek_n} PNJ répartis dans {len(ek_zones)} zones des royaumes de l’Est, d’après la liste consultée.",
              f"{ek_n} NPCs across {len(ek_zones)} Eastern Kingdoms zones, according to the list consulted.", SRC_CLIENT),
         item("Ce n’est pas un recensement de tous les mobs : seuls les PNJ de la liste Forever sont repris, à confirmer.",
              "This is not a census of every mob: only NPCs from the Forever list are included, to be confirmed.", SRC_CLIENT)],
        [how_to_read_section(), *page_tables_by_zone(ek_zones, drops, fr_zones, SRC_CLIENT), history_section()],
        COMMON_CONFIRMED, COMMON_PENDING, COMMON_DATES, rels("forever-creatures-official-notes"),
    )
    unk_page = entry(
        "forever-bestiary-unlocated", T("Bestiaire : zone non indiquée", "Bestiary: zone not given"),
        T(f"{len(unlocated)} PNJ de la liste Forever sans zone renseignée (à confirmer), dont Onyxia (rencontre officielle, fiche déjà en ligne).",
          f"{len(unlocated)} NPCs in the Forever list with no zone given (to be confirmed), including Onyxia (official encounter, existing sheet)."),
        "bestiaire-zone", {"fr": "bestiaire-zone-non-indiquee", "en": "bestiary-unlocated-zone"},
        T(f"Dans la liste consultée, {len(unlocated)} PNJ n’ont pas de zone. Ils sont listés ici tels quels, à confirmer, "
          f"sans localisation inventée. Onyxia fait exception pour le statut officiel : voir {ony[0]}.",
          f"In the list consulted, {len(unlocated)} NPCs have no zone. They are listed here as they stand, to be confirmed, "
          f"with no invented location. Onyxia is the exception for official status: see {ony[1]}."),
        [item(f"{len(unlocated)} PNJ sans zone dans la liste consultée.",
              f"{len(unlocated)} NPCs with no zone in the list consulted.", SRC_CLIENT),
         item("Aucune zone n’est inventée pour ces lignes. Onyxia, présente ici sans zone dans l’extrait, a une fiche officielle séparée.",
              "No zone is invented for these rows. Onyxia, present here without a zone in the extract, has a separate official sheet.", SRC_ALL)],
        [how_to_read_section(),
         {"id": "liste", "title": T("PNJ sans zone dans l’extrait", "NPCs with no zone in the extract"), "blocks": [
             table(f"Zone non indiquée : {len(unlocated)} PNJ — données extraites du client, à confirmer (12/11/2026). Onyxia : aussi officielle.",
                   f"Zone not given: {len(unlocated)} NPCs — client-extracted data, to be confirmed (12 November 2026). Onyxia: also official.",
                   [npc_row(r, drops, fr_zones) for r in sort_npcs(unlocated)], SRC_ALL)]},
         history_section()],
        COMMON_CONFIRMED, COMMON_PENDING, COMMON_DATES, rels("forever-creature-onyxia", "forever-raid-onyxias-lair"),
    )

    pages = [ctx["index"], bosses_entry, zeph_page, shen_page, fd_page, cd_page, rd_page, kal_page, ek_page, unk_page]
    for e in pages:
        dedupe_rel(e)
    OUT.mkdir(parents=True, exist_ok=True)
    batch_path = OUT / "bestiaire-v37.entries.json"
    batch_path.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n")
    stats = {
        "entries": len(pages), "bytes": batch_path.stat().st_size,
        "npcs": ctx["n"], "bosses_tagged": n_boss, "vendors": ctx["n_vend"],
        "quest_givers": ctx["n_q"], "objectives": ctx["n_obj"], "loot_flagged": ctx["n_loot"],
        "zones_raw": ctx["n_zones_raw"], "zones_canon": ctx["n_zones_canon"],
        "zephras": zeph_n, "shendralas": len(shen),
        "forever_dungeon_npcs": fd_n, "forever_dungeon_bosses": fd_boss,
        "classic_dungeon_npcs": cd_n, "classic_dungeon_bosses": cd_boss,
        "raid_extract_npcs": raid_n, "kalimdor": kal_n, "eastern": ek_n, "unlocated": len(unlocated),
        "ids": [e["id"] for e in pages], "slugs": {e["id"]: e["article"]["slug"] for e in pages},
    }
    (OUT / "bestiaire-v37.stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))
    return pages, stats

if __name__ == "__main__":
    finish(build())
