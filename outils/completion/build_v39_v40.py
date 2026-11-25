#!/usr/bin/env python3
"""Build v39 zone-sheet import batches and the v40 cross-link list. No import, no publish."""
from __future__ import annotations
import csv
import json, re, copy
from collections import defaultdict
from pathlib import Path

ROOT = Path("/workspace/wowkipedia-v21-elite")
SRC = ROOT / "bestiaire/sources"
ENTRIES = json.loads((ROOT / "bestiaire/test-tree-v37/pipeline/runtime/entries.json").read_text())
OUT = ROOT / "completion/import-batches"
OUT.mkdir(parents=True, exist_ok=True)

GV = "World of Warcraft: Forever — annonces officielles et données de jeu, état documentaire 2026-11-13"
ACCESSED = "2026-11-12"
UPDATED = "2026-11-13T02:00:00.000Z"
LIC_BZ = ("Droits réservés Blizzard ; référence et synthèse originale (courtes citations), "
          "mention © Blizzard Entertainment conservée ; site non commercial.")
LIC_CLIENT = ("Données de jeu extraites des fichiers du client World of Warcraft: Forever "
              "(build 1.60.1.70862) ; consultation le 12 novembre 2026 ; site non commercial. "
              "Contenus de jeu © Blizzard Entertainment.")
ACTOR = "Koa"
NOTE_NEW = ("Brouillon v39 : fiche de zone d’après la liste de PNJ des fichiers du jeu Forever "
            "(build 1.60.1.70862, consultation 12/11/2026), à la demande de Mathieu (t360u). "
            "Pas une validation de publication.")
NOTE_REV = ("Brouillon v39 : ajout de la liste de PNJ issue des fichiers du jeu Forever "
            "(build 1.60.1.70862, consultation 12/11/2026), à la demande de Mathieu (t360u). "
            "Le texte officiel déjà publié est conservé. Pas une validation de publication.")

MERGE = {
    "Insel Zephras": "Zephras Isle",
    "The Hall of Thanes": "Hall of Thanes",
    "Temple of Ahn'Qiraj": "Ahn'Qiraj Temple",
}
OFFICIAL_TITLE = {
    "Zephras Isle": ("Île de Zéphras", "Zephras Isle"),
    "Shen'dralas": ("Shen’dralas", "Shen’dralas"),
    "Riverglades": ("Rives Claires", "Riverglades"),
    "Mount Hyjal": ("Mont Hyjal", "Mount Hyjal"),
    "Hall of Thanes": ("Salle des Thanes", "Hall of Thanes"),
    "Ruins of Lordaeron": ("Ruines de Lordaeron", "Ruins of Lordaeron"),
    "Excavation Site: Wetlands": ("Excavations", "Excavation Site: Wetlands"),
    "City of Dalaran": ("Cité de Dalaran", "City of Dalaran"),
    "The Drowned City": ("La cité Submergée", "The Drowned City"),
    "Krol'dok Stronghold": ("Bastion Krol’dok", "Krol’dok Stronghold"),
    "Alcaz Prison": ("Prison d’Alcaz", "Alcaz Prison"),
    "Blackmaw Hold": ("Repaire des Noiregueules", "Blackmaw Hold"),
    "The Shaper's Terrace": ("La terrasse du Façonneur", "The Shaper’s Terrace"),
    "Barrow Deeps": ("Profondeurs des Saisons", "Barrow Deeps"),
    "Hyjal Summit": ("Sommet d’Hyjal", "Hyjal Summit"),
    "Onyxia's Lair": ("Repaire d’Onyxia", "Onyxia’s Lair"),
}
EXISTING_ID = {
    "Zephras Isle": "forever-zone-zephras-isle",
    "Shen'dralas": "forever-zone-shendralas",
    "Riverglades": "forever-zone-riverglades",
    "Mount Hyjal": "forever-zone-mount-hyjal",
}
EXISTING_SLUG = {
    "Zephras Isle": {"fr": "ile-de-zephras", "en": "zephras-isle"},
    "Shen'dralas": {"fr": "shen-dralas", "en": "shen-dralas"},
    "Riverglades": {"fr": "rives-claires", "en": "riverglades"},
    "Mount Hyjal": {"fr": "mont-hyjal", "en": "mount-hyjal"},
}
INSTANCE_WIKI = {
    "Hall of Thanes": ("forever-dungeon-hall-of-thanes", "/fr/donjons-raids/salle-des-thanes/", "/en/dungeons-raids/hall-of-thanes/"),
    "Ruins of Lordaeron": ("forever-dungeon-ruins-of-lordaeron", "/fr/donjons-raids/ruines-de-lordaeron/", "/en/dungeons-raids/ruins-of-lordaeron/"),
    "Excavation Site: Wetlands": ("forever-dungeon-excavation-site", "/fr/donjons-raids/excavations/", "/en/dungeons-raids/excavation-site/"),
    "City of Dalaran": ("forever-dungeon-city-of-dalaran", "/fr/donjons-raids/cite-de-dalaran/", "/en/dungeons-raids/city-of-dalaran/"),
    "The Drowned City": ("forever-dungeon-drowned-city", "/fr/donjons-raids/la-cite-submergee/", "/en/dungeons-raids/the-drowned-city/"),
    "Krol'dok Stronghold": ("forever-dungeon-kroldok-stronghold", "/fr/donjons-raids/bastion-krol-dok/", "/en/dungeons-raids/krol-dok-stronghold/"),
    "Alcaz Prison": ("forever-dungeon-alcaz-prison", "/fr/donjons-raids/prison-d-alcaz/", "/en/dungeons-raids/alcaz-prison/"),
    "Blackmaw Hold": ("forever-dungeon-blackmaw-hold", "/fr/donjons-raids/repaire-des-noiregueules/", "/en/dungeons-raids/blackmaw-hold/"),
    "The Shaper's Terrace": ("forever-dungeon-shapers-terrace", "/fr/donjons-raids/la-terrasse-du-faconneur/", "/en/dungeons-raids/shaper-s-terrace/"),
    "Barrow Deeps": ("forever-raid-barrow-deeps", "/fr/donjons-raids/profondeurs-des-saisons/", "/en/dungeons-raids/barrow-deeps/"),
    "Hyjal Summit": ("forever-raid-hyjal-summit", "/fr/donjons-raids/sommet-d-hyjal/", "/en/dungeons-raids/hyjal-summit/"),
    "Onyxia's Lair": ("forever-raid-onyxias-lair", "/fr/donjons-raids/repaire-d-onyxia/", "/en/dungeons-raids/onyxia-s-lair/"),
    "Dalaran": ("forever-bestiary-forever-dungeons", "/fr/creatures/bestiaire-donjons-forever/", "/en/creatures/bestiary-forever-dungeons/"),
}
INSTANCE_LABELS = {
    "Hall of Thanes", "Ruins of Lordaeron", "Excavation Site: Wetlands",
    "City of Dalaran", "Dalaran", "The Drowned City", "Krol'dok Stronghold",
    "Alcaz Prison", "Blackmaw Hold", "The Shaper's Terrace",
    "Ragefire Chasm", "The Deadmines", "Wailing Caverns", "Shadowfang Keep",
    "Blackfathom Deeps", "The Stockade", "Gnomeregan", "Razorfen Kraul",
    "Razorfen Downs", "Scarlet Monastery", "Scarlet Monastery: Graveyard",
    "Scarlet Monastery: Library", "Scarlet Monastery: Armory", "Scarlet Monastery: Cathedral",
    "Zul'Farrak", "Scholomance", "Stratholme", "Maraudon", "Dire Maul",
    "Uldaman", "Sunken Temple", "Blackrock Depths", "Blackrock Spire",
    "Molten Core", "Blackwing Lair", "Zul'Gurub", "Ruins of Ahn'Qiraj",
    "Ahn'Qiraj Temple", "Naxxramas", "Onyxia's Lair", "Barrow Deeps", "Hyjal Summit",
}
KALIMDOR = {
    "The Barrens", "Orgrimmar", "Durotar", "Mulgore", "Teldrassil", "Ashenvale", "Silithus",
    "Feralas", "Desolace", "Tanaris", "Felwood", "Thousand Needles", "Darkshore", "Thunder Bluff",
    "Stonetalon Mountains", "Winterspring", "Dustwallow Marsh", "Darnassus", "Un'Goro Crater",
    "Azshara", "Moonglade", "Shen'dralas",
}
EASTERN = {
    "Dun Morogh", "Elwynn Forest", "Tirisfal Glades", "Stormwind City", "Hillsbrad Foothills",
    "Stranglethorn Vale", "Wetlands", "Loch Modan", "Duskwood", "Eastern Plaguelands", "Undercity",
    "Arathi Highlands", "The Hinterlands", "Badlands", "Burning Steppes", "Western Plaguelands",
    "Redridge Mountains", "Alterac Valley", "Alterac Mountains", "Silverpine Forest", "Searing Gorge",
    "Westfall", "Swamp of Sorrows", "Blasted Lands", "Ironforge", "Blackrock Mountain",
}
FOREVER_NEW = {"Zephras Isle", "Shen'dralas", "Riverglades", "Mount Hyjal"}
ROLE_FR = {"x": "boss", "h": "vendeur", "l": "formateur", "b": "butin indiqué", "t": "vol à la tire",
           "z": "objectif de quête", "q": "donneur de quête"}
ROLE_EN = {"x": "boss", "h": "vendor", "l": "trainer", "b": "loot flagged", "t": "pick pocket",
           "z": "quest objective", "q": "quest giver"}
BESTIARY = {
    "fr": "/fr/creatures/bestiaire/", "en": "/en/creatures/bestiary/",
    "kal_fr": "/fr/creatures/bestiaire-kalimdor/", "kal_en": "/en/creatures/bestiary-kalimdor/",
    "ek_fr": "/fr/creatures/bestiaire-royaumes-de-lest/", "ek_en": "/en/creatures/bestiary-eastern-kingdoms/",
    "zeph_fr": "/fr/creatures/bestiaire-ile-de-zephras/", "zeph_en": "/en/creatures/bestiary-zephras-isle/",
    "shen_fr": "/fr/creatures/bestiaire-shen-dralas/", "shen_en": "/en/creatures/bestiary-shen-dralas/",
    "un_fr": "/fr/creatures/bestiaire-zone-non-indiquee/", "un_en": "/en/creatures/bestiary-unlocated-zone/",
    "cd_fr": "/fr/creatures/bestiaire-donjons-classiques/", "cd_en": "/en/creatures/bestiary-classic-dungeons/",
    "fd_fr": "/fr/creatures/bestiaire-donjons-forever/", "fd_en": "/en/creatures/bestiary-forever-dungeons/",
    "raid_fr": "/fr/creatures/bestiaire-raids/", "raid_en": "/en/creatures/bestiary-raids/",
    "boss_fr": "/fr/creatures/bestiaire-bosses/", "boss_en": "/en/creatures/bestiary-bosses/",
    "fish_fr": "/fr/metiers/poissons/", "fish_en": "/en/professions/fish/",
    "cook_fr": "/fr/metiers/recettes-cuisine/", "cook_en": "/en/professions/cooking-recipes/",
    "alc_fr": "/fr/metiers/recettes-alchimie/", "alc_en": "/en/professions/alchemy-recipes/",
    "bp_fr": "/fr/metiers/recettes-et-plans-avances/", "bp_en": "/en/professions/recipes-and-advanced-blueprints/",
}
OFFICIAL_SOURCES = [
    {"key": "bz-24315643-fr", "language": "fr",
     "url": "https://news.blizzard.com/fr-fr/article/24315643/retournez-sur-azeroth-dans-world-of-warcraft-forever",
     "title": "Retournez sur Azeroth dans World of Warcraft: Forever",
     "publishedAt": "2026-10-29", "accessedAt": "2026-11-04", "license": LIC_BZ, "gameVersion": GV},
    {"key": "bz-24315643-en", "language": "en",
     "url": "https://news.blizzard.com/en-us/article/24315643/return-to-azeroth-in-world-of-warcraft-forever",
     "title": "Return to Azeroth in World of Warcraft: Forever",
     "publishedAt": "2026-10-29", "accessedAt": "2026-11-04", "license": LIC_BZ, "gameVersion": GV},
]
SRC_OFF = ["bz-24315643"]
CLIENT_SOURCES = [
    {"key": "client-npc-liste-fr", "language": "fr",
     "url": "https://eternadex.com/fr/daten/npc-liste.json",
     "title": "Liste JSON des PNJ, français (extrait des fichiers du client Forever, build 1.60.1.70862)",
     "accessedAt": ACCESSED, "undated": True, "license": LIC_CLIENT, "gameVersion": GV},
    {"key": "client-npc-liste-en", "language": "en",
     "url": "https://eternadex.com/en/daten/npc-liste.json",
     "title": "NPC list JSON, English (Forever client-file extract, build 1.60.1.70862)",
     "accessedAt": ACCESSED, "undated": True, "license": LIC_CLIENT, "gameVersion": GV},
]
SRC_CLIENT = ["client-npc-liste"]


def T(fr, en):
    return {"fr": fr, "en": en}


def clip(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def slugify(value):
    s = str(value or "").replace("’", "-").replace("'", "-").replace("`", "-")
    s = s.encode("utf-8").decode("utf-8")
    import unicodedata
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")[:80].rstrip("-")
    return s


def roles_of(tags):
    tags = tags or ""
    fr, en = [], []
    for ch in "xhlbtzq":
        if ch in tags:
            fr.append(ROLE_FR[ch]); en.append(ROLE_EN[ch])
    return (", ".join(fr), ", ".join(en)) if fr else ("non indiqué", "not given")


def load_npcs():
    en = json.loads((SRC / "npc-liste-en.json").read_text())
    fr = json.loads((SRC / "npc-liste-fr.json").read_text())
    assert len(en) == len(fr) == 3284
    fr_zone = {}
    rows = []
    for a, b in zip(en, fr):
        raw = a[3] or ""
        canon = MERGE.get(raw, raw) if raw else ""
        if raw and raw not in MERGE:
            fr_zone.setdefault(canon or raw, b[3] or raw)
        elif raw in MERGE:
            # prefer official / already-set FR, keep both raw labels
            fr_zone.setdefault(canon, OFFICIAL_TITLE.get(canon, (b[3] or canon, canon))[0])
        rows.append({
            "slug": a[0], "name": a[1], "raw": raw, "canon": canon,
            "zone_fr_extract": b[3] or "", "level": (a[4] or "").strip(),
            "tags": a[5] or "", "quests": a[6] if isinstance(a[6], int) else 0,
        })
    return rows, fr_zone


def recipe_drops():
    """Monster name (EN lower) -> list of {fr, en, kind, zone_en}."""
    e = next(x for x in ENTRIES if x["id"] == "forever-professions-blueprints")
    drops = defaultdict(list)
    for section in e["article"]["sections"]:
        kind = "vendor" if section["id"] == "vendeurs-a-confirmer" else (
            "drop" if section["id"].startswith("butin-") else None)
        if not kind:
            continue
        for block in section["blocks"]:
            if block.get("type") != "table":
                continue
            for row in block["rows"]:
                rec_fr, rec_en = row[0]["fr"], row[0]["en"]
                mon_en = row[2]["en"]
                zone_en = row[3]["en"] if len(row) > 3 else ""
                for mon in re.split(r"[,;]+", mon_en):
                    mon = mon.strip()
                    if not mon:
                        continue
                    # also split "Fel Steed / Shadow Charger" into two aliases + the combo
                    aliases = [mon]
                    if " / " in mon:
                        aliases += [p.strip() for p in mon.split(" / ") if p.strip()]
                    for al in aliases:
                        drops[al.lower()].append({
                            "fr": rec_fr, "en": rec_en, "kind": kind, "zone_en": zone_en,
                            "monster_en": mon,
                        })
    out = {}
    for k, items in drops.items():
        seen, uniq = set(), []
        for it in items:
            key = (it["en"], it["kind"], it["monster_en"])
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
    for it in items:
        verb_fr = "vendu" if it["kind"] == "vendor" else "butin"
        verb_en = "sold" if it["kind"] == "vendor" else "drop"
        fr_bits.append(f"{it['fr']} ({verb_fr})")
        en_bits.append(f"{it['en']} ({verb_en})")
    return T(clip("; ".join(fr_bits) + f" — {BESTIARY['bp_fr']}", 400),
             clip("; ".join(en_bits) + f" — {BESTIARY['bp_en']}", 400))


def zone_titles(canon, fr_zone):
    if canon in OFFICIAL_TITLE:
        return OFFICIAL_TITLE[canon]
    fr = fr_zone.get(canon) or canon
    # If FR extract left a German leftover as the only label, keep it as-is (do not invent).
    return (fr, canon)


def continent(canon):
    if canon in FOREVER_NEW:
        return ("nouvelle zone Forever", "new Forever zone")
    if canon in KALIMDOR:
        return ("Kalimdor", "Kalimdor")
    if canon in EASTERN:
        return ("Royaumes de l’Est", "Eastern Kingdoms")
    return ("non indiqué", "not given")


def counts(npcs):
    n = len(npcs)
    n_q = sum(1 for p in npcs if "q" in p["tags"])
    n_z = sum(1 for p in npcs if "z" in p["tags"])
    n_x = sum(1 for p in npcs if "x" in p["tags"])
    n_h = sum(1 for p in npcs if "h" in p["tags"])
    n_b = sum(1 for p in npcs if "b" in p["tags"])
    n_lvl = sum(1 for p in npcs if p["level"])
    return n, n_q, n_z, n_x, n_h, n_b, n_lvl


def npc_table(npcs, drops, caption_fr, caption_en):
    # bosses first, then vendors, then name
    def sort_key(p):
        return (0 if "x" in p["tags"] else 1 if "h" in p["tags"] else 2, p["name"].lower())
    rows = []
    for p in sorted(npcs, key=sort_key):
        lvl_fr = p["level"] or "non indiqué"
        lvl_en = p["level"] or "not given"
        ro_fr, ro_en = roles_of(p["tags"])
        # quest count is in the extract (int, including 0)
        q = str(p["quests"])
        rows.append([
            T(p["name"], p["name"]),
            T(lvl_fr, lvl_en),
            T(ro_fr, ro_en),
            T(q, q),
            loot_cell(p["name"], drops),
        ])
    raw_notes = sorted({p["raw"] for p in npcs if p["raw"] and p["raw"] != p["canon"]})
    extra_fr = extra_en = ""
    if raw_notes:
        extra_fr = " Étiquettes extraites distinctes regroupées ici : " + ", ".join(raw_notes) + "."
        extra_en = " Distinct extract labels grouped here: " + ", ".join(raw_notes) + "."
    cap_fr = clip(caption_fr + extra_fr, 300)
    cap_en = clip(caption_en + extra_en, 300)
    return {
        "type": "table",
        "caption": T(cap_fr, cap_en),
        "head": [T("Nom", "Name"), T("Niveau", "Level"), T("Rôle", "Role"),
                 T("Quêtes (liste)", "Quests (list)"), T("Butin ou recettes", "Loot or recipes")],
        "rows": rows,
        "src": SRC_CLIENT,
    }


def para(fr, en, src):
    return {"type": "p", "fr": clip(fr, 2400), "en": clip(en, 2400), "src": src}


def lst(items, src=None):
    d = {"type": "list", "items": items}
    if src:
        d["src"] = src
    return d


def item(fr, en, src=None):
    d = T(clip(fr, 2400), clip(en, 2400))
    if src:
        d["src"] = src
    return d


def new_id(canon):
    if canon in EXISTING_ID:
        return EXISTING_ID[canon]
    s = slugify(canon)
    return "forever-zone-" + s


def new_slug(canon, fr_title, en_title):
    if canon in EXISTING_SLUG:
        return EXISTING_SLUG[canon]
    return {"fr": slugify(fr_title), "en": slugify(en_title)}


def missing_section():
    return {
        "id": "informations-non-indiquees",
        "title": T("Informations non indiquées", "Information not given"),
        "blocks": [
            lst([
                item("Niveau de la zone (fourchette) : non indiqué dans la liste de PNJ, sauf mention officielle déjà présente sur cette fiche.",
                     "Zone level range: not given in the NPC list, except an official figure already on this sheet.", SRC_CLIENT),
                item("Points de vol : non indiqué.",
                     "Flight points: not given.", SRC_CLIENT),
                item("Type de créature, élite ou rare, faction, sous-zone : non indiqué dans cette liste.",
                     "Creature type, elite or rare, faction, sub-zone: not given in this list.", SRC_CLIENT),
                item("Les vendeurs ne sont repris que s’ils portent l’étiquette correspondante dans la liste (30 étiquettes au total sur 3 284 PNJ) : l’absence d’étiquette ne prouve pas l’absence de vendeur.",
                     "Vendors are listed only when the extract tags them as such (30 tags in all among 3,284 NPCs): a missing tag is not proof that there is no vendor.", SRC_CLIENT),
                item("Inventaire des vendeurs, formateurs (aucune étiquette « formateur » dans la liste) et quêtes détaillées : non indiqué.",
                     "Vendor inventories, trainers (no “trainer” tag in the list) and detailed quests: not given.", SRC_CLIENT),
                item("Les noms des PNJ sont ceux de la liste consultée ; les noms français distincts n’y figurent pas.",
                     "NPC names are those of the list consulted; distinct French names are not in it.", SRC_CLIENT),
            ], SRC_CLIENT),
        ],
    }


def npc_section(canon, title_fr, title_en, npcs, drops):
    n, n_q, n_z, n_x, n_h, n_b, n_lvl = counts(npcs)
    blocks = [
        para(f"La liste de PNJ des fichiers du jeu Forever (build 1.60.1.70862), consultée le 12 novembre 2026, compte {n} PNJ pour {title_fr} : "
             f"{n_q} donneur{'' if n_q==1 else 's'} de quête, {n_z} objectif{'' if n_z==1 else 's'} de quête, {n_x} boss, {n_h} vendeur{'' if n_h==1 else 's'} étiqueté{'' if n_h==1 else 's'}, "
             f"{n_b} avec butin indiqué, {n_lvl} avec un niveau renseigné. "
             f"Cette liste complète celle du bestiaire ({BESTIARY['fr']}).",
             f"The Forever game-file NPC list (build 1.60.1.70862), consulted on 12 November 2026, has {n} NPCs for {title_en}: "
             f"{n_q} quest giver{'s' if n_q!=1 else ''}, {n_z} quest objective{'s' if n_z!=1 else ''}, {n_x} boss{'es' if n_x!=1 else ''}, {n_h} tagged vendor{'s' if n_h!=1 else ''}, "
             f"{n_b} loot-flagged, {n_lvl} with a recorded level. "
             f"This list complements the bestiary ({BESTIARY['en']}).",
             SRC_CLIENT),
    ]
    if n == 0:
        blocks.append(para(
            f"Aucun PNJ de cette liste n’est rattaché à {title_fr}. Les points de vol, vendeurs et formateurs restent : non indiqué.",
            f"No NPC in that list is attached to {title_en}. Flight points, vendors and trainers remain: not given.",
            SRC_CLIENT))
    else:
        blocks.append(npc_table(
            npcs, drops,
            f"{title_fr} : {n} PNJ — données des fichiers du jeu Forever, consultation du 12/11/2026.",
            f"{title_en}: {n} NPCs — Forever game-file data, consulted 12 November 2026.",
        ))
    return {
        "id": "pnj-donnees-du-jeu",
        "title": T("PNJ (données du jeu)", "NPCs (game data)"),
        "blocks": blocks,
    }


def history_entry(note, version):
    return {"at": UPDATED, "actor": ACTOR, "note": note, "version": version}


def base_sources():
    return [dict(s) for s in OFFICIAL_SOURCES] + [dict(s) for s in CLIENT_SOURCES]


def build_new_zone(canon, title_fr, title_en, npcs, drops, fr_zone, directory_id):
    n, n_q, n_z, n_x, n_h, n_b, n_lvl = counts(npcs)
    cont_fr, cont_en = continent(canon)
    zid = new_id(canon)
    slug = new_slug(canon, title_fr, title_en)
    # slug segment limit: 13
    for lang, s in slug.items():
        if s.count("-") > 12:
            raise ValueError(f"slug too many segments: {s}")
    desc_fr = (f"{title_fr} ({cont_fr}) : {n} PNJ dans la liste des fichiers du jeu Forever "
               f"(build 1.60.1.70862), consultée le 12 novembre 2026. "
               f"Niveau de zone, points de vol : non indiqué.")
    desc_en = (f"{title_en} ({cont_en}): {n} NPCs in the Forever game-file list "
               f"(build 1.60.1.70862), consulted on 12 November 2026. "
               f"Zone level and flight points: not given.")
    return {
        "id": zid,
        "title": T(title_fr, title_en),
        "category": "zones",
        "subcategory": "zone",
        "description": T(clip(desc_fr, 1000), clip(desc_en, 1000)),
        "sources": base_sources(),
        "status": "draft",
        "identityConfirmed": False,
        "updatedAt": UPDATED,
        "version": 1,
        "gameVersion": GV,
        "relations": [directory_id],
        "article": {
            "format": 1,
            "slug": slug,
            "illustration": "zones",
            "lead": T(clip(desc_fr, 1200), clip(desc_en, 1200)) | {"src": SRC_CLIENT},
            "keyPoints": [
                item(f"{n} PNJ dans la liste des fichiers du jeu : {n_q} donneurs de quête, {n_x} boss, {n_h} vendeurs étiquetés.",
                     f"{n} NPCs in the game-file list: {n_q} quest givers, {n_x} bosses, {n_h} tagged vendors.",
                     SRC_CLIENT),
                item("Niveau de la zone, points de vol, type de créature, élite ou rare : non indiqué dans cette liste.",
                     "Zone level, flight points, creature type, elite or rare: not given in this list.",
                     SRC_CLIENT),
            ],
            "sections": [
                npc_section(canon, title_fr, title_en, npcs, drops),
                missing_section(),
                {
                    "id": "historique-des-corrections",
                    "title": T("Historique des corrections", "Correction history"),
                    "blocks": [lst([
                        item("13 novembre 2026 — première rédaction de la fiche d’après la liste de PNJ des fichiers du jeu. Brouillon, non publié.",
                             "13 November 2026 — first draft of the sheet from the game-file NPC list. Draft, unpublished.",
                             SRC_CLIENT),
                    ], SRC_CLIENT)],
                },
            ],
            "confirmed": [
                item(f"Dans les articles officiels cités, Blizzard ne publie pas de fiche dédiée à {title_fr}, ni de liste de PNJ, de points de vol ou de niveaux pour cette zone.",
                     f"In the official articles cited, Blizzard does not publish a dedicated sheet for {title_en}, nor an NPC list, flight points or level range for this zone.",
                     SRC_OFF),
            ],
            "pending": [
                T("Niveau de zone, points de vol, inventaires de vendeurs, formateurs, type de créature, noms français distincts des PNJ : non indiqué dans la liste consultée. "
                  "Blizzard n’a pas publié de fiche officielle pour cette zone dans les sources déjà citées par le wiki.",
                  "Zone level, flight points, vendor inventories, trainers, creature type, distinct French NPC names: not given in the list consulted. "
                  "Blizzard has not published an official sheet for this zone in the sources already cited by the wiki."),
            ],
        },
        "history": [history_entry(NOTE_NEW, 1)],
    }


def revise_official(canon, title_fr, title_en, npcs, drops, directory_id):
    eid = EXISTING_ID[canon]
    orig = next(x for x in ENTRIES if x["id"] == eid)
    e = copy.deepcopy(orig)
    e.pop("importMeta", None)
    e.pop("review", None)
    e["status"] = "draft"
    e["version"] = int(orig["version"]) + 1
    e["updatedAt"] = UPDATED
    e["gameVersion"] = GV
    e["identityConfirmed"] = True
    # unify gameVersion on existing sources
    for s in e["sources"]:
        s["gameVersion"] = GV
    # add client sources if missing
    have = {s["key"] for s in e["sources"]}
    for s in CLIENT_SOURCES:
        if s["key"] not in have:
            e["sources"].append(dict(s))
    rel = list(e.get("relations") or [])
    if directory_id not in rel:
        rel.append(directory_id)
    e["relations"] = rel
    art = e["article"]
    # insert NPC + missing sections before correction history if present
    new_secs = [npc_section(canon, title_fr, title_en, npcs, drops), missing_section()]
    secs = art.get("sections") or []
    out_secs = []
    inserted = False
    for sec in secs:
        if sec.get("id") == "historique-des-corrections" and not inserted:
            out_secs.extend(new_secs)
            inserted = True
        # skip if we already had these ids from a previous draft attempt
        if sec.get("id") in ("pnj-donnees-du-jeu", "informations-non-indiquees"):
            continue
        out_secs.append(sec)
    if not inserted:
        out_secs.extend(new_secs)
    # append a history line to the correction-history section
    for sec in out_secs:
        if sec.get("id") == "historique-des-corrections":
            for block in sec.get("blocks") or []:
                if block.get("type") == "list":
                    block["items"] = list(block.get("items") or []) + [
                        item("13 novembre 2026 — ajout de la liste de PNJ issue des fichiers du jeu (build 1.60.1.70862). Brouillon, non publié.",
                             "13 November 2026 — added the NPC list from the game files (build 1.60.1.70862). Draft, unpublished.",
                             SRC_CLIENT),
                    ]
    art["sections"] = out_secs
    # pending: keep previous, add gaps if not already said
    pending = list(art.get("pending") or [])
    pending.append(T(
        "Points de vol, inventaires de vendeurs et formateurs : non indiqué dans la liste de PNJ consultée le 12 novembre 2026.",
        "Flight points, vendor inventories and trainers: not given in the NPC list consulted on 12 November 2026.",
    ))
    art["pending"] = pending
    # Client-file NPC counts stay in the body section, not in article.confirmed
    # (confirmed is reserved for official Blizzard sources).
    hist = list(e.get("history") or [])
    hist.append(history_entry(NOTE_REV, e["version"]))
    e["history"] = hist
    return e


def build_directory(world, instance_rows, unlocated_n, drops):
    """world: list of (canon, title_fr, title_en, npcs, id, slug)."""
    # tables
    def row_world(canon, tfr, ten, npcs, zid, slug):
        n, n_q, n_z, n_x, n_h, n_b, n_lvl = counts(npcs)
        cont_fr, cont_en = continent(canon)
        path_fr = f"/fr/zones/{slug['fr']}/"
        path_en = f"/en/zones/{slug['en']}/"
        return [
            T(f"{tfr} ({path_fr})", f"{ten} ({path_en})"),
            T(cont_fr, cont_en),
            T(str(n), str(n)),
            T(str(n_q), str(n_q)),
            T(str(n_h), str(n_h)),
            T(str(n_x), str(n_x)),
        ]

    wrows = [row_world(*w) for w in world]
    irows = []
    for canon, tfr, ten, npcs in instance_rows:
        n, n_q, n_z, n_x, n_h, n_b, n_lvl = counts(npcs)
        wiki = INSTANCE_WIKI.get(canon)
        if wiki:
            _, pfr, pen = wiki
            fiche_fr, fiche_en = pfr, pen
        else:
            fiche_fr, fiche_en = BESTIARY["cd_fr"], BESTIARY["cd_en"]
        irows.append([
            T(tfr, ten),
            T(str(n), str(n)),
            T(str(n_x), str(n_x)),
            T(fiche_fr, fiche_en),
        ])

    n_world = len(world)
    n_world_npcs = sum(len(w[3]) for w in world)
    n_inst = len(instance_rows)
    n_inst_npcs = sum(len(r[3]) for r in instance_rows)
    lead_fr = (f"Index des zones présentes dans la liste de PNJ des fichiers du jeu Forever "
               f"(build 1.60.1.70862), consultée le 12 novembre 2026 : {n_world} zones avec une fiche, "
               f"{n_world_npcs} PNJ, plus {n_inst} donjons ou raids déjà couverts par une fiche d’instance ou le bestiaire "
               f"({n_inst_npcs} PNJ), et {unlocated_n} PNJ sans zone indiquée.")
    lead_en = (f"Index of zones present in the Forever game-file NPC list "
               f"(build 1.60.1.70862), consulted on 12 November 2026: {n_world} zones with a sheet, "
               f"{n_world_npcs} NPCs, plus {n_inst} dungeons or raids already covered by an instance sheet or the bestiary "
               f"({n_inst_npcs} NPCs), and {unlocated_n} NPCs with no zone given.")
    rels = [w[4] for w in world]
    return {
        "id": "forever-zones-directory",
        "title": T("Liste des zones", "Zone list"),
        "category": "zones",
        "subcategory": "index",
        "description": T(clip(lead_fr, 1000), clip(lead_en, 1000)),
        "sources": base_sources(),
        "status": "draft",
        "identityConfirmed": False,
        "updatedAt": UPDATED,
        "version": 1,
        "gameVersion": GV,
        "relations": rels,
        "article": {
            "format": 1,
            "slug": {"fr": "liste-des-zones", "en": "zone-list"},
            "illustration": "zones",
            "lead": T(clip(lead_fr, 1200), clip(lead_en, 1200)) | {"src": SRC_CLIENT},
            "keyPoints": [
                item(f"{n_world} fiches de zone, dont les quatre déjà en ligne (Île de Zéphras, Rives Claires, mont Hyjal, Shen’dralas) révisées plutôt que dupliquées.",
                     f"{n_world} zone sheets, including the four already online (Zephras Isle, Riverglades, Mount Hyjal, Shen’dralas) revised rather than duplicated.",
                     SRC_CLIENT),
                item(f"Niveau de zone et points de vol : non indiqué. {unlocated_n} PNJ sans zone : voir {BESTIARY['un_fr']}.",
                     f"Zone level and flight points: not given. {unlocated_n} NPCs with no zone: see {BESTIARY['un_en']}.",
                     SRC_CLIENT),
            ],
            "sections": [
                {
                    "id": "zones",
                    "title": T("Zones", "Zones"),
                    "blocks": [
                        para("Chaque fiche reprend les PNJ de la liste des fichiers du jeu. Les quatre zones déjà présentées par Blizzard conservent leur texte officiel, complété par cette liste. "
                             "Les donjons et raids ont leur propre fiche ; ils figurent dans le tableau suivant, sans seconde fiche « zone ».",
                             "Each sheet lists the NPCs from the game-file list. The four zones already presented by Blizzard keep their official text, completed by this list. "
                             "Dungeons and raids have their own sheets; they appear in the next table, without a second “zone” sheet.",
                             SRC_CLIENT),
                        {
                            "type": "table",
                            "caption": T(clip(f"{n_world} zones — {n_world_npcs} PNJ — données des fichiers du jeu, 12/11/2026.", 300),
                                         clip(f"{n_world} zones — {n_world_npcs} NPCs — game-file data, 12 November 2026.", 300)),
                            "head": [T("Zone", "Zone"), T("Région", "Region"), T("PNJ", "NPCs"),
                                     T("Donneurs de quête", "Quest givers"), T("Vendeurs étiquetés", "Tagged vendors"),
                                     T("Boss", "Bosses")],
                            "rows": wrows,
                            "src": SRC_CLIENT,
                        },
                    ],
                },
                {
                    "id": "donjons-et-raids",
                    "title": T("Donjons et raids (dans la liste de PNJ)", "Dungeons and raids (in the NPC list)"),
                    "blocks": [
                        para("Ces étiquettes de zone figurent dans la même liste de PNJ. Aucune fiche « zone » n’est créée : on renvoie vers la fiche d’instance déjà en ligne, ou vers le bestiaire lorsqu’il n’y a pas encore de fiche dédiée.",
                             "These zone labels appear in the same NPC list. No “zone” sheet is created: we point to the instance sheet already online, or to the bestiary when there is not yet a dedicated sheet.",
                             SRC_CLIENT),
                        {
                            "type": "table",
                            "caption": T(clip(f"{n_inst} donjons ou raids, {n_inst_npcs} PNJ — données des fichiers du jeu, 12/11/2026.", 300),
                                         clip(f"{n_inst} dungeons or raids, {n_inst_npcs} NPCs — game-file data, 12 November 2026.", 300)),
                            "head": [T("Nom", "Name"), T("PNJ", "NPCs"), T("Boss", "Bosses"), T("Fiche", "Sheet")],
                            "rows": irows,
                            "src": SRC_CLIENT,
                        },
                    ],
                },
                {
                    "id": "zone-non-indiquee",
                    "title": T("Zone non indiquée", "Zone not given"),
                    "blocks": [
                        para(f"{unlocated_n} PNJ de la liste n’ont pas de zone. Ils sont déjà regroupés dans le bestiaire : {BESTIARY['un_fr']}. "
                             f"Aucune fiche de zone n’est créée pour cette absence.",
                             f"{unlocated_n} NPCs in the list have no zone. They are already grouped in the bestiary: {BESTIARY['un_en']}. "
                             f"No zone sheet is created for that absence.",
                             SRC_CLIENT),
                    ],
                },
                {
                    "id": "historique-des-corrections",
                    "title": T("Historique des corrections", "Correction history"),
                    "blocks": [lst([
                        item("13 novembre 2026 — première rédaction de l’index. Brouillon, non publié.",
                             "13 November 2026 — first draft of the index. Draft, unpublished.",
                             SRC_CLIENT),
                    ], SRC_CLIENT)],
                },
            ],
            "confirmed": [
                item("Les quatre zones déjà en ligne (Île de Zéphras, Rives Claires, mont Hyjal, Shen’dralas) sont celles que Blizzard a présentées dans les articles officiels cités ; les autres zones de cet index n’ont pas de fiche officielle dans ces mêmes articles.",
                     "The four zones already online (Zephras Isle, Riverglades, Mount Hyjal, Shen’dralas) are the ones Blizzard presented in the official articles cited; the other zones in this index have no official sheet in those same articles.",
                     SRC_OFF),
            ],
            "pending": [
                T("Niveau de chaque zone et points de vol : non indiqué. Les vendeurs étiquetés sont incomplets (30 étiquettes au total). "
                  "Rives Claires et le mont Hyjal n’ont aucun PNJ dans cette liste.",
                  "Each zone’s level and flight points: not given. Tagged vendors are incomplete (30 tags in all). "
                  "Riverglades and Mount Hyjal have no NPC in this list."),
            ],
        },
        "history": [history_entry(
            "Brouillon v39 : index des zones d’après la liste de PNJ des fichiers du jeu Forever, à la demande de Mathieu (t360u). Pas une validation de publication.",
            1)],
    }


def build_v39():
    rows, fr_zone = load_npcs()
    drops = recipe_drops()
    by = defaultdict(list)
    unlocated = []
    for p in rows:
        if not p["canon"]:
            unlocated.append(p)
        else:
            by[p["canon"]].append(p)

    # Official world zones with 0 NPCs still get a revise
    world_canons = sorted({z for z in by if z not in INSTANCE_LABELS} | set(FOREVER_NEW),
                          key=lambda z: (-len(by.get(z, [])), z))
    instance_canons = sorted([z for z in by if z in INSTANCE_LABELS],
                             key=lambda z: (-len(by[z]), z))

    directory_id = "forever-zones-directory"
    world_meta = []
    entries = []
    revises = []
    news = []
    for canon in world_canons:
        tfr, ten = zone_titles(canon, fr_zone)
        npcs = by.get(canon, [])
        zid = new_id(canon)
        slug = new_slug(canon, tfr, ten)
        world_meta.append((canon, tfr, ten, npcs, zid, slug))
        if canon in EXISTING_ID:
            e = revise_official(canon, tfr, ten, npcs, drops, directory_id)
            revises.append(e)
        else:
            e = build_new_zone(canon, tfr, ten, npcs, drops, fr_zone, directory_id)
            news.append(e)
        entries.append(e)

    inst_rows = []
    for canon in instance_canons:
        tfr, ten = zone_titles(canon, fr_zone)
        inst_rows.append((canon, tfr, ten, by[canon]))

    directory = build_directory(world_meta, inst_rows, len(unlocated), drops)
    # directory first
    batch = [directory] + entries

    # pair count used in loot cells
    n_loot_cells = 0
    monsters_with_loot = set()
    for p in rows:
        if drops.get(p["name"].lower()):
            n_loot_cells += 1
            monsters_with_loot.add(p["name"])

    stats = {
        "entries": len(batch),
        "directory": 1,
        "revised_official": len(revises),
        "revised_ids": [e["id"] for e in revises],
        "new_zone_sheets": len(news),
        "world_zones": len(world_canons),
        "world_npcs": sum(len(by.get(z, [])) for z in world_canons),
        "instance_labels": len(instance_canons),
        "instance_npcs": sum(len(by[z]) for z in instance_canons),
        "unlocated": len(unlocated),
        "npcs_with_recipe_loot": len(monsters_with_loot),
        "official_zero_npc": [z for z in FOREVER_NEW if not by.get(z)],
        "ids": [e["id"] for e in batch],
        "slugs": {e["id"]: e["article"]["slug"] for e in batch},
    }
    # Compact JSON: pretty-print exceeds the 2 MB import limit; compact stays under it.
    (OUT / "v39-zones.entries.json").write_text(json.dumps(batch, ensure_ascii=False, separators=(",", ":")) + "\n")
    (OUT / "v39-zones.stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    return batch, stats, drops, rows, by, fr_zone


def fish_cooking_links():
    fish = next(x for x in ENTRIES if x["id"] == "forever-professions-fish")
    links = []
    for sec in fish["article"]["sections"]:
        for block in sec.get("blocks") or []:
            if block.get("type") != "table":
                continue
            head = [h["en"].lower() for h in block["head"]]
            # name col 0, recipe col typically 3
            for row in block["rows"]:
                name = {"fr": row[0]["fr"], "en": row[0]["en"]}
                rec = row[3] if len(row) > 3 else None
                rec_fr = rec["fr"] if rec else ""
                rec_en = rec["en"] if rec else ""
                has_recipe = rec_fr and not rec_fr.lower().startswith("aucune") and "non indiqué" not in rec_fr.lower()
                kind = "cooking" if "cuisine" in rec_fr.lower() or "cooking" in rec_en.lower() else (
                    "alchemy" if "alchim" in rec_fr.lower() or "alchem" in rec_en.lower() else "other")
                links.append({
                    "fish_fr": name["fr"], "fish_en": name["en"],
                    "recipe_cell_fr": rec_fr, "recipe_cell_en": rec_en,
                    "has_recipe": bool(has_recipe),
                    "kind": kind if has_recipe else "none",
                    "already_linked_on_fish_page": bool(has_recipe and ("/fr/metiers/" in rec_fr or "/en/professions/" in rec_en)),
                    "section": sec["id"],
                })
    return links


def build_v40(drops, rows, by, fr_zone):
    # 121 pairs from blueprints: reconstruct exact pairs (recipe, monster, zone) without alias split double-count
    # Authoritative 121 pairs: explode source_butin of the 55 "butin monstre" CSV rows
    # (consultation 12 Nov 2026). Published blueprints tables have 96 rows: one monster
    # per (recipe, zone); the other 25 same-zone additional monsters are not yet in the tables.
    # "Fel Steed / Shadow Charger" stays one name (Shadowfang 20 recipes / 20 pairs).
    e = next(x for x in ENTRIES if x["id"] == "forever-professions-blueprints")
    table_rows = []
    table_by_ruz = {}
    table_by_rmz = set()
    section_for_zone = {}
    for section in e["article"]["sections"]:
        if not section["id"].startswith("butin-"):
            continue
        for block in section["blocks"]:
            if block.get("type") != "table":
                continue
            for row in block["rows"]:
                rec_fr, rec_en = row[0]["fr"], row[0]["en"]
                prof_fr, prof_en = row[1]["fr"], row[1]["en"]
                mon_fr, mon_en = row[2]["fr"], row[2]["en"]
                zone_fr, zone_en = row[3]["fr"], row[3]["en"]
                rec = {
                    "recipe_fr": rec_fr, "recipe_en": rec_en,
                    "profession_fr": prof_fr, "profession_en": prof_en,
                    "monster_fr": mon_fr, "monster_en": mon_en,
                    "zone_fr": zone_fr, "zone_en": zone_en,
                    "blueprint_section": section["id"],
                }
                table_rows.append(rec)
                table_by_ruz[(rec_en, zone_en)] = rec
                # A cell may list several same-zone monsters: "Gelihast, Baron Aquanis, Aku'mai"
                for token in [x.strip() for x in mon_en.split(",") if x.strip()]:
                    table_by_rmz.add((rec_en, token, zone_en))
                section_for_zone[zone_en] = section["id"]

    METIER = {
        "Alchimie": ("Alchimie", "Alchemy"),
        "Forge": ("Forge", "Blacksmithing"),
        "Cuisine": ("Cuisine", "Cooking"),
        "Enchantement": ("Enchantement", "Enchanting"),
        "Ingénierie": ("Ingénierie", "Engineering"),
        "Travail du cuir": ("Travail du cuir", "Leatherworking"),
        "Couture": ("Couture", "Tailoring"),
        "Secourisme": ("Secourisme", "First Aid"),
    }

    def explode_butin(sb, zone):
        out = []
        for part in re.split(r"\s*;\s*", sb):
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", part)
            if m:
                names, z = m.group(1).strip(), m.group(2).strip()
            else:
                names, z = part, zone
            # Do not split "Fel Steed / Shadow Charger"; do split "A et B" if it ever appears.
            out.append((names, z))
        return out

    csv_path = Path("/workspace/wowkipedia-v21-elite/recettes-pnj/RECETTES_PNJ.csv")
    pairs = []
    with csv_path.open(encoding="utf-8") as fh:
        for crow in csv.DictReader(fh):
            if crow.get("type_obtention", "").strip() != "butin monstre":
                continue
            rec_en = crow["recette_en"].strip()
            rec_fr_csv = (crow.get("recette_fr_officiel") or rec_en).strip()
            prof = METIER.get(crow["metier"].strip(), (crow["metier"], crow["metier"]))
            for mon, zone in explode_butin(crow.get("source_butin") or "", crow.get("zone") or ""):
                known = table_by_ruz.get((rec_en, zone))
                in_table = (rec_en, mon, zone) in table_by_rmz
                pairs.append({
                    "recipe_fr": known["recipe_fr"] if known else rec_fr_csv,
                    "recipe_en": rec_en,
                    "profession_fr": known["profession_fr"] if known else prof[0],
                    "profession_en": known["profession_en"] if known else prof[1],
                    "monster_fr": mon,
                    "monster_en": mon,
                    "zone_fr": known["zone_fr"] if known else zone,
                    "zone_en": zone,
                    "blueprint_section": (known["blueprint_section"] if known
                                          else section_for_zone.get(zone, "")),
                    "already_a_table_row": in_table,
                    "recipe_zone_already_in_table": known is not None,
                    "table_monster_en": known["monster_en"] if known and not in_table else None,
                })
    if len(pairs) != 121:
        raise SystemExit(f"expected 121 pairs from CSV, got {len(pairs)}")
    vendors = []
    for section in e["article"]["sections"]:
        if section["id"] != "vendeurs-a-confirmer":
            continue
        for block in section["blocks"]:
            if block.get("type") != "table":
                continue
            for row in block["rows"]:
                vendors.append({
                    "recipe_fr": row[0]["fr"], "recipe_en": row[0]["en"],
                    "npc_fr": row[2]["fr"] if len(row) > 2 else row[1]["fr"],
                    "npc_en": row[2]["en"] if len(row) > 2 else row[1]["en"],
                    "zone_fr": row[3]["fr"] if len(row) > 3 else "",
                    "zone_en": row[3]["en"] if len(row) > 3 else "",
                })

    # insertions per page
    # 1) forever-professions-blueprints: already has the tables; insertions are FROM those rows TO zone/dungeon/bestiary
    # 2) zone/dungeon pages: add recipe links (v39 already puts loot cells on world zones; instances need insertions)
    # 3) fish <-> cooking
    # 4) bosses <-> dungeons

    PROF_PAGE = {
        "Alchemy": ("forever-professions-recipes-alchemy", "/fr/metiers/recettes-alchimie/", "/en/professions/alchemy-recipes/"),
        "Alchimie": ("forever-professions-recipes-alchemy", "/fr/metiers/recettes-alchimie/", "/en/professions/alchemy-recipes/"),
        "Blacksmithing": ("forever-professions-recipes-blacksmithing", "/fr/metiers/recettes-forge/", "/en/professions/blacksmithing-recipes/"),
        "Forge": ("forever-professions-recipes-blacksmithing", "/fr/metiers/recettes-forge/", "/en/professions/blacksmithing-recipes/"),
        "Leatherworking": ("forever-professions-recipes-leatherworking", "/fr/metiers/recettes-travail-du-cuir/", "/en/professions/leatherworking-recipes/"),
        "Travail du cuir": ("forever-professions-recipes-leatherworking", "/fr/metiers/recettes-travail-du-cuir/", "/en/professions/leatherworking-recipes/"),
        "Tailoring": ("forever-professions-recipes-tailoring", "/fr/metiers/recettes-couture/", "/en/professions/tailoring-recipes/"),
        "Couture": ("forever-professions-recipes-tailoring", "/fr/metiers/recettes-couture/", "/en/professions/tailoring-recipes/"),
        "Engineering": ("forever-professions-recipes-engineering", "/fr/metiers/recettes-ingenierie/", "/en/professions/engineering-recipes/"),
        "Ingénierie": ("forever-professions-recipes-engineering", "/fr/metiers/recettes-ingenierie/", "/en/professions/engineering-recipes/"),
        "Enchanting": ("forever-professions-recipes-enchanting", "/fr/metiers/recettes-enchantement/", "/en/professions/enchanting-recipes/"),
        "Enchantement": ("forever-professions-recipes-enchanting", "/fr/metiers/recettes-enchantement/", "/en/professions/enchanting-recipes/"),
        "Cooking": ("forever-professions-recipes-cooking", "/fr/metiers/recettes-cuisine/", "/en/professions/cooking-recipes/"),
        "Cuisine": ("forever-professions-recipes-cooking", "/fr/metiers/recettes-cuisine/", "/en/professions/cooking-recipes/"),
    }

    def dungeon_or_zone_for(zone_en):
        # official forever instance?
        if zone_en in INSTANCE_WIKI:
            iid, pfr, pen = INSTANCE_WIKI[zone_en]
            return {"id": iid, "path_fr": pfr, "path_en": pen, "kind": "instance-sheet"}
        # world zone in v39?
        # Ruins of Lordaeron is instance. Classic-named dungeons: bestiary
        if zone_en in INSTANCE_LABELS:
            return {
                "id": "forever-bestiary-classic-dungeons",
                "path_fr": BESTIARY["cd_fr"], "path_en": BESTIARY["cd_en"],
                "kind": "bestiary-classic-dungeons",
            }
        # world
        zid = new_id(zone_en) if zone_en else None
        if zid and zone_en:
            tfr, ten = zone_titles(zone_en, fr_zone)
            slug = new_slug(zone_en, tfr, ten)
            return {"id": zid, "path_fr": f"/fr/zones/{slug['fr']}/", "path_en": f"/en/zones/{slug['en']}/", "kind": "v39-zone"}
        return None

    insertions = defaultdict(lambda: {"page_id": "", "paths": {}, "insertions": []})

    def page(pid, path_fr, path_en, title=""):
        p = insertions[pid]
        p["page_id"] = pid
        p["paths"] = {"fr": path_fr, "en": path_en}
        if title:
            p["title"] = title
        return p

    # Blueprint page: each pair already listed; propose adding hyperlinks on monster and zone cells
    bp = page("forever-professions-blueprints", BESTIARY["bp_fr"], BESTIARY["bp_en"], "Recettes et plans avancés")
    n_in = sum(1 for p in pairs if p["already_a_table_row"])
    n_miss = len(pairs) - n_in
    n_multi = sum(1 for r in table_rows if "," in r["monster_en"])
    bp["note"] = (
        f"The original consultation (12 Nov 2026) has {len(pairs)} monster–recipe pairs across 55 recipes. "
        f"The published blueprints tables have {len(table_rows)} rows; {n_multi} of those rows "
        f"list several same-zone monsters in one cell, covering all {n_in} pairs"
        + (f". {n_miss} pairs are not yet in the tables — add a row or append the monster, then link."
           if n_miss else
           ". Insertions: turn each individual monster name, zone name and recipe name into a link.")
    )
    for pair in pairs:
        dest = dungeon_or_zone_for(pair["zone_en"])
        prof = PROF_PAGE.get(pair["profession_en"]) or PROF_PAGE.get(pair["profession_fr"])
        if pair["already_a_table_row"]:
            where = (f"section {pair['blueprint_section']}, existing row "
                     f"« {pair['recipe_en']} » / monster « {pair['monster_en']} »")
        elif pair["recipe_zone_already_in_table"]:
            where = (f"section {pair['blueprint_section']}, recipe « {pair['recipe_en']} » "
                     f"already has a row for {pair['zone_en']} with monster "
                     f"« {pair['table_monster_en']} » — add « {pair['monster_en']} » "
                     f"to that cell or add a new row")
        else:
            where = (f"section {pair['blueprint_section']}: add a row "
                     f"« {pair['recipe_en']} » / monster « {pair['monster_en']} » / {pair['zone_en']}")
        ins = {
            "where": where,
            "already_a_table_row": pair["already_a_table_row"],
            "add_links": [],
        }
        if dest:
            ins["add_links"].append({
                "on_text_en": pair["monster_en"],
                "on_text_fr": pair["monster_fr"],
                "to_id": dest["id"], "to_fr": dest["path_fr"], "to_en": dest["path_en"],
                "reason": "recipe drop → monster / dungeon or zone",
            })
            ins["add_links"].append({
                "on_text_en": pair["zone_en"],
                "on_text_fr": pair["zone_fr"],
                "to_id": dest["id"], "to_fr": dest["path_fr"], "to_en": dest["path_en"],
                "reason": "recipe drop → zone or dungeon",
            })
        if prof:
            ins["add_links"].append({
                "on_text_en": pair["recipe_en"],
                "on_text_fr": pair["recipe_fr"],
                "to_id": prof[0], "to_fr": prof[1], "to_en": prof[2],
                "reason": "recipe → profession recipe list",
            })
        bp["insertions"].append(ins)

    # Reverse: on each dungeon/zone/bestiary page, add a “recipes dropped here” list
    by_dest = defaultdict(list)
    for pair in pairs:
        dest = dungeon_or_zone_for(pair["zone_en"])
        if not dest:
            continue
        by_dest[dest["id"]].append((pair, dest))
    for pid, items in by_dest.items():
        dest = items[0][1]
        p = page(pid, dest["path_fr"], dest["path_en"])
        p["note"] = p.get("note") or (
            "Add a short section « Recettes au butin » / “Recipes from loot” listing these pairs, "
            "each linking back to the blueprints page and the profession list. "
            "World-zone v39 drafts already have a loot cell on the NPC row when a pair matches the NPC name."
        )
        for pair, _ in items:
            p["insertions"].append({
                "where": "new section recettes-au-butin (or loot cell on the matching NPC in a v39 zone sheet)",
                "text_fr": f"{pair['recipe_fr']} — {pair['monster_fr']} — {BESTIARY['bp_fr']}",
                "text_en": f"{pair['recipe_en']} — {pair['monster_en']} — {BESTIARY['bp_en']}",
                "to_id": "forever-professions-blueprints",
            })

    # Profession recipe pages: link drop recipes to monster/zone
    by_prof = defaultdict(list)
    for pair in pairs:
        prof = PROF_PAGE.get(pair["profession_en"]) or PROF_PAGE.get(pair["profession_fr"])
        if prof:
            by_prof[prof[0]].append((pair, prof))
    for pid, items in by_prof.items():
        prof = items[0][1]
        p = page(pid, prof[1], prof[2])
        p["note"] = "On each drop-recipe row, link the source cell to the monster’s dungeon or zone and to the blueprints page."
        for pair, _ in items:
            dest = dungeon_or_zone_for(pair["zone_en"])
            p["insertions"].append({
                "where": f"recipe row « {pair['recipe_en']} », source / zone cell",
                "add_links": ([
                    {"to_id": dest["id"], "to_fr": dest["path_fr"], "to_en": dest["path_en"],
                     "on_text_en": f"{pair['monster_en']} ({pair['zone_en']})",
                     "on_text_fr": f"{pair['monster_fr']} ({pair['zone_fr']})"}
                ] if dest else []) + [
                    {"to_id": "forever-professions-blueprints", "to_fr": BESTIARY["bp_fr"], "to_en": BESTIARY["bp_en"],
                     "on_text_en": "blueprints by zone", "on_text_fr": "plans par zone"}
                ],
            })

    # Fish → cooking (and reverse)
    flinks = fish_cooking_links()
    fish_page = page("forever-professions-fish", BESTIARY["fish_fr"], BESTIARY["fish_en"], "Poissons")
    fish_page["note"] = ("The fish sheet already points at cooking/alchemy recipe pages in the recipe cell. "
                         "Insertions below are the reverse links still to add on those recipe pages, "
                         "and a confirmation of what is already on the fish page.")
    cook_page = page("forever-professions-recipes-cooking", BESTIARY["cook_fr"], BESTIARY["cook_en"], "Recettes de cuisine")
    cook_page["note"] = "Add a « Poissons » / “Fish” column or a linked mention on each cooking recipe that uses a fish from the list."
    alc_page = page("forever-professions-recipes-alchemy", BESTIARY["alc_fr"], BESTIARY["alc_en"], "Recettes d’alchimie")
    alc_page["note"] = "Same for the three alchemy oils that use a fish from the list."
    n_fish_already = 0
    n_cook = n_alc = 0
    for fl in flinks:
        if fl["already_linked_on_fish_page"]:
            n_fish_already += 1
            fish_page["insertions"].append({
                "where": f"section {fl['section']}, already present",
                "status": "already-on-page",
                "fish_fr": fl["fish_fr"], "fish_en": fl["fish_en"],
                "recipe_cell_fr": fl["recipe_cell_fr"], "recipe_cell_en": fl["recipe_cell_en"],
            })
        if fl["kind"] == "cooking":
            n_cook += 1
            cook_page["insertions"].append({
                "where": f"recipe mentioned in « {fl['recipe_cell_fr']} »",
                "add_links": [{
                    "on_text_fr": fl["fish_fr"], "on_text_en": fl["fish_en"],
                    "to_id": "forever-professions-fish",
                    "to_fr": BESTIARY["fish_fr"], "to_en": BESTIARY["fish_en"],
                    "reason": "cooking ingredient → fish sheet",
                }],
            })
        elif fl["kind"] == "alchemy":
            n_alc += 1
            alc_page["insertions"].append({
                "where": f"recipe mentioned in « {fl['recipe_cell_fr']} »",
                "add_links": [{
                    "on_text_fr": fl["fish_fr"], "on_text_en": fl["fish_en"],
                    "to_id": "forever-professions-fish",
                    "to_fr": BESTIARY["fish_fr"], "to_en": BESTIARY["fish_en"],
                    "reason": "alchemy ingredient → fish sheet",
                }],
            })

    # Bosses → dungeons
    bosses = [p for p in rows if "x" in p["tags"]]
    boss_page = page("forever-bestiary-bosses", BESTIARY["boss_fr"], BESTIARY["boss_en"], "Bestiaire : boss")
    boss_page["note"] = "On the bosses bestiary table, turn the zone cell into a link to the instance sheet or bestiary group."
    # also on each dungeon sheet, link boss names to the bosses bestiary (and official Onyxia)
    dungeon_bosses = defaultdict(list)
    for p in bosses:
        dest = dungeon_or_zone_for(p["canon"]) if p["canon"] else None
        # Hall of Thanes etc.
        if p["canon"] in INSTANCE_WIKI:
            dest = {
                "id": INSTANCE_WIKI[p["canon"]][0],
                "path_fr": INSTANCE_WIKI[p["canon"]][1],
                "path_en": INSTANCE_WIKI[p["canon"]][2],
                "kind": "instance-sheet",
            }
        elif p["canon"] in INSTANCE_LABELS:
            # raids in extract
            raid_names = {"Molten Core", "Blackwing Lair", "Zul'Gurub", "Ruins of Ahn'Qiraj",
                          "Ahn'Qiraj Temple", "Naxxramas", "Onyxia's Lair", "Barrow Deeps", "Hyjal Summit"}
            if p["canon"] in raid_names:
                if p["canon"] in INSTANCE_WIKI:
                    dest = {"id": INSTANCE_WIKI[p["canon"]][0],
                            "path_fr": INSTANCE_WIKI[p["canon"]][1],
                            "path_en": INSTANCE_WIKI[p["canon"]][2], "kind": "instance-sheet"}
                else:
                    dest = {"id": "forever-bestiary-raids", "path_fr": BESTIARY["raid_fr"],
                            "path_en": BESTIARY["raid_en"], "kind": "bestiary-raids"}
            else:
                forever_d = {"Hall of Thanes", "Ruins of Lordaeron", "Excavation Site: Wetlands",
                             "City of Dalaran", "Dalaran", "The Drowned City", "Krol'dok Stronghold",
                             "Alcaz Prison", "Blackmaw Hold", "The Shaper's Terrace"}
                if p["canon"] in forever_d:
                    dest = {"id": "forever-bestiary-forever-dungeons",
                            "path_fr": BESTIARY["fd_fr"], "path_en": BESTIARY["fd_en"],
                            "kind": "bestiary-forever-dungeons"}
                else:
                    dest = {"id": "forever-bestiary-classic-dungeons",
                            "path_fr": BESTIARY["cd_fr"], "path_en": BESTIARY["cd_en"],
                            "kind": "bestiary-classic-dungeons"}
        boss_page["insertions"].append({
            "where": f"boss row « {p['name']} », zone cell",
            "boss": p["name"], "zone_en": p["canon"] or "(unlocated)",
            "level": p["level"] or "not given",
            "add_links": ([{
                "on_text_en": p["canon"], "on_text_fr": zone_titles(p["canon"], fr_zone)[0] if p["canon"] else "non indiqué",
                "to_id": dest["id"], "to_fr": dest["path_fr"], "to_en": dest["path_en"],
                "reason": "boss → dungeon or bestiary group",
            }] if dest else []),
        })
        if dest:
            dungeon_bosses[dest["id"]].append((p, dest))
    # Official Onyxia
    onyxia = page("forever-creature-onyxia", "/fr/creatures/onyxia/", "/en/creatures/onyxia/", "Onyxia")
    onyxia["note"] = "Official sheet already exists. Add a reciprocal link from the raid sheet and from the bosses bestiary."
    onyxia["insertions"].append({
        "where": "relations / related pages",
        "add_links": [
            {"to_id": "forever-raid-onyxias-lair", "to_fr": "/fr/donjons-raids/repaire-d-onyxia/",
             "to_en": "/en/dungeons-raids/onyxia-s-lair/", "reason": "Onyxia → her raid sheet"},
            {"to_id": "forever-bestiary-bosses", "to_fr": BESTIARY["boss_fr"],
             "to_en": BESTIARY["boss_en"], "reason": "Onyxia → bosses bestiary"},
        ],
    })
    raid_ony = page("forever-raid-onyxias-lair", "/fr/donjons-raids/repaire-d-onyxia/",
                    "/en/dungeons-raids/onyxia-s-lair/", "Repaire d’Onyxia")
    raid_ony["insertions"].append({
        "where": "relations / encounter section",
        "add_links": [{
            "on_text_fr": "Onyxia", "on_text_en": "Onyxia",
            "to_id": "forever-creature-onyxia",
            "to_fr": "/fr/creatures/onyxia/", "to_en": "/en/creatures/onyxia/",
            "reason": "raid → official boss sheet",
        }],
    })
    for pid, items in dungeon_bosses.items():
        dest = items[0][1]
        p = page(pid, dest["path_fr"], dest["path_en"])
        if "note" not in p:
            p["note"] = "Link each named boss on the instance or bestiary page to the bosses bestiary (and back)."
        for bp_, dest_ in items:
            p["insertions"].append({
                "where": f"boss name « {bp_['name']} »",
                "add_links": [{
                    "on_text_en": bp_["name"], "on_text_fr": bp_["name"],
                    "to_id": "forever-bestiary-bosses",
                    "to_fr": BESTIARY["boss_fr"], "to_en": BESTIARY["boss_en"],
                    "reason": "dungeon or group → bosses bestiary",
                }],
            })

    # flatten
    pages = list(insertions.values())
    # counts
    n_pages = len(pages)
    n_ins = sum(len(p["insertions"]) for p in pages)
    out = {
        "id": "v40-cross-links",
        "status": "draft-list",
        "updatedAt": UPDATED,
        "note": ("Not an import batch of full entries: a list of link insertions to apply per page when a later "
                 "revise is authorised. No publication. Game-file pairs are unmarked; they already live on the "
                 "blueprints page. Third-party site names must stay out of page text (source hrefs only)."),
        "counts": {
            "recipe_monster_pairs": len(pairs),
            "pairs_already_a_table_row": sum(1 for p in pairs if p["already_a_table_row"]),
            "pairs_missing_from_published_tables": sum(1 for p in pairs if not p["already_a_table_row"]),
            "published_table_rows": len(table_rows),
            "distinct_recipes": len({p["recipe_en"] for p in pairs}),
            "distinct_monsters": len({p["monster_en"] for p in pairs}),
            "distinct_drop_zones": len({p["zone_en"] for p in pairs}),
            "vendor_rows": len(vendors),
            "fish_rows": len(flinks),
            "fish_already_linked_to_recipe_page": n_fish_already,
            "cooking_reverse_links": n_cook,
            "alchemy_reverse_links": n_alc,
            "bosses_tagged": len(bosses),
            "pages_touched": n_pages,
            "insertion_records": n_ins,
        },
        "pairs": pairs,
        "vendors": vendors,
        "fish": flinks,
        "pages": pages,
    }
    (OUT / "v40-cross-links.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return out


def main():
    batch, stats, drops, rows, by, fr_zone = build_v39()
    v40 = build_v40(drops, rows, by, fr_zone)
    print("V39 entries", stats["entries"], "bytes", (OUT / "v39-zones.entries.json").stat().st_size)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("V40 pairs", v40["counts"])


if __name__ == "__main__":
    main()
