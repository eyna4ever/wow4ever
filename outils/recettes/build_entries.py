#!/usr/bin/env python3
"""Build draft profession recipe entries from client-extracted guides + official names.
Research date: 2026-11-12 (Europe/Paris). Does not invent facts. No third-party site names in page text.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources-brutes"
CSV_PATH = Path("/workspace/wowkipedia-v21-elite/recettes-pnj/RECETTES_PNJ.csv")
TREE = HERE / "test-tree-v36"
OUT = HERE / "brouillons"
ACC = "2026-11-12"
NOW = "2026-11-12T04:55:00.000Z"
GV = "World of Warcraft: Forever — annonces et notes officielles, état documentaire 2026-11-12"
ACTOR = "AI-documentary-draft"
HIST_NOTE = (
    "Listes de recettes par métier, d’après les sources officielles citées et des données "
    "extraites du client (à confirmer). Brouillon à relire. Périmètre du wiki, droits et "
    "traductions non confirmés par un humain. Pas une validation de publication."
)
CLIENT_LICENSE = (
    "Données de tiers (extrait de fichiers client) ; consultation des guides métier le 12 novembre 2026 ; "
    "informations à confirmer, non officielles."
)
BZ_LICENSE = (
    "Droits réservés Blizzard ; référence et synthèse originale (courtes citations), "
    "mention © Blizzard Entertainment conservée ; site non commercial."
)

PREFIXES = (
    "recipe: ", "pattern: ", "plans: ", "formula: ", "schematic: ", "blueprint: ",
    "recette : ", "recette: ", "patron : ", "patron: ", "plans : ", "formule : ",
    "formule: ", "schéma : ", "schema : ", "plan : ", "plan: ",
)

# Official names published by Blizzard (articles / hotfixes). EN key -> (fr, en)
OFFICIAL_NAMES = {
    "basic campfire": ("Feu de camp basique", "Basic Campfire"),
    "first aid kit": ("Trousse de premiers soins", "First Aid Kit"),
    "fishing bowl": ("Bocal à poisson", "Fishing Bowl"),
    "fish bowl": ("Bocal à poisson", "Fishing Bowl"),
    "mana well": ("Puits de mana", "Mana Well"),
    "sharpening wheel": ("Meule à aiguiser", "Sharpening Wheel"),
    "enchanted lute": ("Luth enchanté", "Enchanted Lute"),
    "reagent bot": ("Robot vendeur de composants", "Reagent Bot"),
    "incense candle": ("Bougie d’encens", "Incense Candle"),
    "camp tent": ("Tente du camp", "Camp Tent"),
    "camp chair": ("Chaise du camp", "Camp Chair"),
    "faction banner": ("Bannière de faction", "Faction Banner"),
    "tanning rack": ("râtelier de tannage", "Tanning Rack"),
    "alchemy lab": ("laboratoire d’alchimie", "Alchemy Lab"),
    "alchemy laboratory": ("laboratoire d’alchimie", "Alchemy Laboratory"),
}

# First camp objects officially learned at skill 20 via starter-zone quests or a profession trainer.
OFFICIAL_FIRST_CAMP = {
    "first aid kit", "fishing bowl", "fish bowl", "mana well", "sharpening wheel",
    "enchanted lute", "reagent bot", "incense candle", "camp tent", "camp chair",
    "faction banner",
}

OFFICIAL_ZONE_FR = {
    "ruins of lordaeron": "Ruines de Lordaeron",
    "île de zéphras": "île de Zéphras",
    "ile de zephras": "île de Zéphras",
}

PROFESSIONS = [
    dict(key="alchemie", kind="full", id="forever-professions-recipes-alchemy",
         title={"fr": "Recettes d’alchimie", "en": "Alchemy recipes"},
         prof={"fr": "Alchimie", "en": "Alchemy"},
         slug={"fr": "recettes-alchimie", "en": "alchemy-recipes"}),
    dict(key="schmiedekunst", kind="full", id="forever-professions-recipes-blacksmithing",
         title={"fr": "Recettes de forge", "en": "Blacksmithing recipes"},
         prof={"fr": "Forge", "en": "Blacksmithing"},
         slug={"fr": "recettes-forge", "en": "blacksmithing-recipes"}),
    dict(key="verzauberkunst", kind="full", id="forever-professions-recipes-enchanting",
         title={"fr": "Recettes d’enchantement", "en": "Enchanting recipes"},
         prof={"fr": "Enchantement", "en": "Enchanting"},
         slug={"fr": "recettes-enchantement", "en": "enchanting-recipes"}),
    dict(key="ingenieurskunst", kind="full", id="forever-professions-recipes-engineering",
         title={"fr": "Recettes d’ingénierie", "en": "Engineering recipes"},
         prof={"fr": "Ingénierie", "en": "Engineering"},
         slug={"fr": "recettes-ingenierie", "en": "engineering-recipes"}),
    dict(key="lederverarbeitung", kind="full", id="forever-professions-recipes-leatherworking",
         title={"fr": "Recettes de travail du cuir", "en": "Leatherworking recipes"},
         prof={"fr": "Travail du cuir", "en": "Leatherworking"},
         slug={"fr": "recettes-travail-du-cuir", "en": "leatherworking-recipes"}),
    dict(key="schneiderei", kind="full", id="forever-professions-recipes-tailoring",
         title={"fr": "Recettes de couture", "en": "Tailoring recipes"},
         prof={"fr": "Couture", "en": "Tailoring"},
         slug={"fr": "recettes-couture", "en": "tailoring-recipes"}),
    dict(key="kochkunst", kind="full", id="forever-professions-recipes-cooking",
         title={"fr": "Recettes de cuisine", "en": "Cooking recipes"},
         prof={"fr": "Cuisine", "en": "Cooking"},
         slug={"fr": "recettes-cuisine", "en": "cooking-recipes"}),
    dict(key="erste-hilfe", kind="full", id="forever-professions-recipes-first-aid",
         title={"fr": "Recettes de secourisme", "en": "First Aid recipes"},
         prof={"fr": "Secourisme", "en": "First Aid"},
         slug={"fr": "recettes-secourisme", "en": "first-aid-recipes"}),
    dict(key="bergbau", kind="gather", id="forever-professions-recipes-mining",
         title={"fr": "Recettes de minage", "en": "Mining recipes"},
         prof={"fr": "Minage", "en": "Mining"},
         slug={"fr": "recettes-minage", "en": "mining-recipes"}),
    dict(key="kraeuterkunde", kind="gather", id="forever-professions-recipes-herbalism",
         title={"fr": "Recettes d’herboristerie", "en": "Herbalism recipes"},
         prof={"fr": "Herboristerie", "en": "Herbalism"},
         slug={"fr": "recettes-herboristerie", "en": "herbalism-recipes"}),
    dict(key="kuerschnerei", kind="gather", id="forever-professions-recipes-skinning",
         title={"fr": "Recettes de dépeçage", "en": "Skinning recipes"},
         prof={"fr": "Dépeçage", "en": "Skinning"},
         slug={"fr": "recettes-depecage", "en": "skinning-recipes"}),
    dict(key="angeln", kind="gather", id="forever-professions-recipes-fishing",
         title={"fr": "Recettes de pêche", "en": "Fishing recipes"},
         prof={"fr": "Pêche", "en": "Fishing"},
         slug={"fr": "recettes-peche", "en": "fishing-recipes"}),
]

TYPE_LABEL = {
    "formateur": {"fr": "formateur", "en": "trainer"},
    "vendeur": {"fr": "vendeur", "en": "vendor"},
    "butin": {"fr": "butin", "en": "drop"},
    "quete": {"fr": "quête", "en": "quest"},
    "reputation": {"fr": "réputation", "en": "reputation"},
    "inconnu": {"fr": "inconnu", "en": "unknown"},
}

BRACKETS = [
    ("competence-1-75", 1, 75, {"fr": "Compétence 1–75", "en": "Skill 1–75"}),
    ("competence-76-150", 76, 150, {"fr": "Compétence 76–150", "en": "Skill 76–150"}),
    ("competence-151-225", 151, 225, {"fr": "Compétence 151–225", "en": "Skill 151–225"}),
    ("competence-226-300", 226, 300, {"fr": "Compétence 226–300", "en": "Skill 226–300"}),
]

FORBIDDEN = re.compile(r"Eternadex|Wowhead|wiki\.gg", re.I)


def clip(text: str, n: int) -> str:
    text = " ".join((text or "").split())
    if not text:
        text = "—"
    if len(text) <= n:
        return text
    return text[: n - 1].rstrip() + "…"


def norm_name(name: str) -> str:
    n = " ".join((name or "").lower().replace("’", "'").split())
    for p in PREFIXES:
        if n.startswith(p):
            n = n[len(p) :].strip()
            break
    return n


def soup_file(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")


def extract_id(el) -> str | None:
    if el is None:
        return None
    href = el.get("href") or ""
    m = re.search(r"/item/(\d+)/?", href)
    if m:
        return m.group(1)
    data = el.get("data-item")
    return str(data) if data else None


def main_itm(td):
    for el in td.find_all(class_=lambda c: c and "itm" in (c or [])):
        if el.find_parent("small"):
            continue
        return el
    return None


def first_int(text: str) -> int | None:
    m = re.search(r"\d+", text or "")
    return int(m.group(0)) if m else None


def classify_en(text: str) -> tuple[str, str, str]:
    """Return (type_key, source_en, extra)."""
    raw = " ".join((text or "").split())
    low = raw.lower()
    if "learned automatically with the profession" in low:
        return "formateur", "learned automatically with the profession", "auto"
    if "from the trainer" in low or re.search(r"\btrainer\b", low):
        return "formateur", "profession trainer (unnamed)", ""
    if "quest reward" in low:
        m = re.search(r"quest reward:\s*(.+)$", raw, re.I)
        src = (m.group(1).strip(" ·") if m else "") or "quest (name not given)"
        return "quete", src, ""
    if "sold by" in low:
        m = re.search(r"sold by:\s*(.+)$", raw, re.I)
        src = (m.group(1).strip(" ·") if m else "") or "vendor (name not given)"
        return "vendeur", src, ""
    if "dropped by" in low or re.search(r"\bdrop(?:ped)?\b", low):
        m = re.search(r"dropped by:\s*(.+)$", raw, re.I)
        src = (m.group(1).strip(" ·") if m else "") or "drop (source not named)"
        return "butin", src, ""
    if "reputation:" in low or re.search(r"\breputation\b", low):
        m = re.search(r"reputation:\s*(.+)$", raw, re.I)
        src = (m.group(1).strip(" ·") if m else "") or "reputation (faction not named)"
        return "reputation", src, ""
    if "source not recorded" in low or "source isn't known" in low or "source is not known" in low:
        return "inconnu", "not recorded", ""
    # leftover recipe-item name only, no source phrase
    if raw and not re.fullmatch(r"[×x]\d+", raw):
        # e.g. only "Recipe: Mithril Head Trout"
        return "inconnu", "not recorded", ""
    return "inconnu", "not recorded", ""


def classify_fr_source(text: str) -> tuple[str, str]:
    raw = " ".join((text or "").split())
    low = raw.lower()
    if "automatiquement" in low and "métier" in low:
        return "formateur", "appris automatiquement avec le métier"
    if "auprès du maître" in low or "auprès d’un maître" in low or "auprès d'un maître" in low:
        return "formateur", "maître de métier (non nommé)"
    if "récompense de quête" in low:
        m = re.search(r"récompense de quêtes?:\s*(.+)$", raw, re.I)
        return "quete", (m.group(1).strip(" ·") if m else "") or "quête (nom non indiqué)"
    if "vendu par" in low:
        m = re.search(r"vendu par\s*:\s*(.+)$", raw, re.I)
        return "vendeur", (m.group(1).strip(" ·") if m else "") or "vendeur (nom non indiqué)"
    if "butin de" in low:
        m = re.search(r"butin de\s*:\s*(.+)$", raw, re.I)
        return "butin", (m.group(1).strip(" ·") if m else "") or "butin (source non nommée)"
    if "réputation:" in low or "reputation:" in low:
        m = re.search(r"réputation:\s*(.+)$", raw, re.I)
        return "reputation", (m.group(1).strip(" ·") if m else "") or "réputation (faction non nommée)"
    if "source pas encore" in low or "source n’est pas" in low or "source n'est pas" in low or "pas encore enregistré" in low or "source inconnue" in low:
        return "inconnu", "non indiqué"
    return "", ""


def small_source_text(td) -> str:
    parts = []
    for small in td.find_all("small"):
        t = " ".join(small.get_text(" ", strip=True).split())
        if re.fullmatch(r"[×x]\d+", t or ""):
            continue
        if t:
            parts.append(t)
    return " | ".join(parts)


def find_all_recipes_table(soup: BeautifulSoup, lang: str):
    for t in soup.find_all("table"):
        prev = t.find_previous(["h2", "h1"])
        if not prev:
            continue
        ht = prev.get_text(" ", strip=True)
        low = ht.lower()
        if lang == "en" and re.search(r"^all \d+ recipes", low):
            return t, ht
        if lang == "fr" and re.search(r"^(les|toutes les) \d+ recettes", low):
            return t, ht
    return None, None


def parse_full_table(path: Path, lang: str) -> list[dict]:
    soup = soup_file(path)
    table, _ = find_all_recipes_table(soup, lang)
    if table is None:
        return []
    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        skill_td, name_td = tds[0], tds[1]
        skill = None
        b = skill_td.find("b")
        if b:
            skill = first_int(b.get_text())
        if skill is None:
            skill = first_int(skill_td.get_text())
        itm = main_itm(name_td)
        name = " ".join((itm.get_text(" ", strip=True) if itm else name_td.get_text(" ", strip=True)).split())
        # strip trailing source crumbs if we fell back to full cell text
        name = re.split(r"\s{2,}|\s·\s", name)[0].strip()
        # if yield marker stuck to name, the main itm text shouldn't include it
        if itm:
            name = " ".join(itm.get_text(" ", strip=True).split())
        iid = extract_id(itm)
        src_txt = small_source_text(name_td)
        rec = {"skill": skill, "item_id": iid, "name": name, "src_txt": src_txt}
        if lang == "en":
            typ, source, flag = classify_en(src_txt)
            rec.update(typ=typ, source_en=source, flag=flag)
        else:
            typ, source = classify_fr_source(src_txt)
            rec.update(typ_fr=typ, source_fr=source)
        rows.append(rec)
    return rows


def parse_smelting(path: Path, lang: str) -> list[dict]:
    soup = soup_file(path)
    table = None
    for t in soup.find_all("table"):
        prev = t.find_previous(["h2", "h1"])
        if not prev:
            continue
        ht = prev.get_text(" ", strip=True).lower()
        if ht in {"smelting", "fonte"}:
            table = t
            break
    if table is None:
        return []
    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        # Recipe name is plain text in first cell (not an item link)
        name = " ".join(tds[0].get_text(" ", strip=True).split())
        skill = first_int(tds[1].get_text(" ", strip=True))
        rows.append({
            "skill": skill, "item_id": None, "name": name, "src_txt": "",
            "typ": "inconnu", "source_en": "not recorded", "flag": "",
            "typ_fr": "inconnu", "source_fr": "non indiqué",
        })
    return rows


def parse_camp(path: Path, lang: str) -> list[dict]:
    soup = soup_file(path)
    table = None
    for t in soup.find_all("table"):
        prev = t.find_previous(["h2", "h1"])
        if not prev:
            continue
        ht = prev.get_text(" ", strip=True).lower()
        if "camp" in ht or "campement" in ht:
            table = t
            break
    if table is None:
        return []
    heads = [th.get_text(" ", strip=True).lower() for th in table.find_all("th")]
    # detect skill vs level column
    has_skill = any("skill" in h or "compétence" in h or "competence" in h for h in heads)
    # columns vary: Object|Skill|Materials  OR  Level|Object|Materials
    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        if heads and heads[0].startswith("level") or (heads and heads[0].startswith("niveau")):
            obj_td = tds[1]
            skill = None  # level is a camp tier, not a published skill
        elif has_skill and len(tds) >= 2:
            # Object | Skill | Materials  OR Skill? 
            # EN first aid: Object | Skill | Materials
            # some: Level | Object | Materials already handled
            if "object" in heads[0] or "objet" in heads[0]:
                obj_td = tds[0]
                skill = first_int(tds[1].get_text())
            else:
                obj_td = tds[1]
                skill = first_int(tds[0].get_text())
        else:
            obj_td = tds[0]
            skill = first_int(tds[1].get_text()) if len(tds) > 1 else None
        itm = main_itm(obj_td) or obj_td.find(class_=lambda c: c and "itm" in (c or []))
        name = " ".join((itm.get_text(" ", strip=True) if itm else obj_td.get_text(" ", strip=True)).split())
        iid = extract_id(itm)
        rows.append({
            "skill": skill, "item_id": iid, "name": name, "src_txt": "",
            "typ": "inconnu", "source_en": "not recorded", "flag": "",
            "typ_fr": "inconnu", "source_fr": "non indiqué",
        })
    return rows


def load_csv_maps():
    drop, quest, vendor = {}, {}, {}
    if not CSV_PATH.exists():
        return drop, quest, vendor
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            keys = {norm_name(r.get("recette_en") or ""), norm_name(r.get("recette_fr_officiel") or "")}
            keys.discard("")
            typ = (r.get("type_obtention") or "").lower()
            if typ == "butin monstre" or r.get("source_butin"):
                payload = {
                    "source": r.get("source_butin") or "",
                    "zone": r.get("zone") or "",
                }
                if typ == "butin monstre" or "butin" in typ:
                    for k in keys:
                        drop[k] = payload
            if typ == "quête":
                payload = {"zone": r.get("zone") or "", "notes": r.get("notes") or ""}
                for k in keys:
                    quest[k] = payload
            if typ == "vendeur":
                payload = {"npc": r.get("pnj_vendeur") or "", "zone": r.get("zone") or ""}
                for k in keys:
                    vendor[k] = payload
    return drop, quest, vendor


def clean_zone(zone: str) -> str:
    z = " ".join((zone or "").split())
    if not z or z.lower().startswith("non renseign") or z.lower().startswith("non précisé") or z.lower().startswith("non precise") or z.lower() in {"non publié", "non indique", "non indiqué"}:
        return ""
    # strip any URL
    z = re.sub(r"https?://\S+", "", z).strip(" ,;")
    # shorten known verbose values
    if z.lower().startswith("île de zéphras") or z.lower().startswith("ile de zephras"):
        return "île de Zéphras"
    if z.lower().startswith("dun morogh"):
        return "Dun Morogh (Alliance)"
    return z


def zone_pair(zone: str) -> tuple[str, str]:
    z = clean_zone(zone)
    if not z:
        return "non indiqué", "not recorded"
    key = z.lower().replace("’", "'")
    fr = OFFICIAL_ZONE_FR.get(key, z)
    en = z
    if z == "île de Zéphras":
        en = "Isle of Zephras"
    if z == "Ruines de Lordaeron" or key == "ruins of lordaeron":
        fr, en = "Ruines de Lordaeron", "Ruins of Lordaeron"
    # split lists with official rename
    parts = [p.strip() for p in re.split(r"\s*;\s*", z) if p.strip()]
    if len(parts) > 1:
        fr_parts, en_parts = [], []
        for p in parts:
            pk = p.lower()
            if pk == "ruins of lordaeron":
                fr_parts.append("Ruines de Lordaeron")
                en_parts.append("Ruins of Lordaeron")
            else:
                fr_parts.append(p)
                en_parts.append(p)
        fr, en = " ; ".join(fr_parts), " ; ".join(en_parts)
    return fr, en


def monsters_from_csv(source: str) -> str:
    """'Gelihast (Blackfathom Deeps) ; Baron Aquanis (...)' -> 'Gelihast ; Baron Aquanis'."""
    parts = []
    for chunk in re.split(r"\s*;\s*", source or ""):
        chunk = chunk.strip()
        if not chunk:
            continue
        name = re.sub(r"\s*\([^)]*\)\s*$", "", chunk).strip()
        if name:
            parts.append(name)
    return " ; ".join(parts)


def apply_enrichment(rec: dict, drop_map, quest_map, vendor_map):
    keys = [norm_name(rec["name_en"]), norm_name(rec["name_fr"])]
    typ = rec["typ"]
    if typ == "butin":
        for k in keys:
            if k in drop_map:
                d = drop_map[k]
                monsters = monsters_from_csv(d["source"])
                if monsters:
                    rec["source_en"] = monsters
                    rec["source_fr"] = monsters
                zfr, zen = zone_pair(d["zone"])
                rec["zone_fr"], rec["zone_en"] = zfr, zen
                break
    elif typ == "quete":
        for k in keys:
            if k in quest_map:
                zfr, zen = zone_pair(quest_map[k]["zone"])
                rec["zone_fr"], rec["zone_en"] = zfr, zen
                break
        # Restocking the Larders / Skywall Souffle
        if "restocking the larders" in (rec.get("source_en") or "").lower() or "restocking the larders" in (rec.get("source_fr") or "").lower():
            rec["zone_fr"], rec["zone_en"] = "île de Zéphras", "Isle of Zephras"
    elif typ == "vendeur":
        for k in keys:
            if k in vendor_map:
                v = vendor_map[k]
                if v["npc"]:
                    rec["source_en"] = v["npc"]
                    if not rec.get("source_fr") or rec["source_fr"] in {"non indiqué", ""}:
                        rec["source_fr"] = v["npc"]
                zfr, zen = zone_pair(v["zone"])
                rec["zone_fr"], rec["zone_en"] = zfr, zen
                break
        if "zerril" in (rec.get("source_en") or "").lower() or "zerril" in (rec.get("source_fr") or "").lower():
            rec["zone_fr"], rec["zone_en"] = "île de Zéphras", "Isle of Zephras"
    # official first camp objects: if still unknown, use official rule (skill 20)
    nk = norm_name(rec["name_en"])
    if nk in OFFICIAL_FIRST_CAMP and typ == "inconnu":
        rec["typ"] = "formateur"
        rec["source_en"] = "starter-zone quests or a profession trainer (unnamed)"
        rec["source_fr"] = "quêtes des zones de départ ou maître de métier (non nommé)"
        rec["official_acq"] = True
        if rec.get("skill") is None:
            rec["skill"] = 20
    return rec


def display_names(name_en: str, name_fr: str) -> tuple[str, str]:
    off = OFFICIAL_NAMES.get(norm_name(name_en)) or OFFICIAL_NAMES.get(norm_name(name_fr))
    if off:
        return off
    fr = (name_fr or "").strip()
    en = (name_en or "").strip() or fr
    if not fr or norm_name(fr) == norm_name(en):
        # no distinct FR translation: use English in both, per the brief
        return en, en
    return fr, en


def merge_profession(meta, drop_map, quest_map, vendor_map) -> list[dict]:
    key, kind = meta["key"], meta["kind"]
    en_path, fr_path = SRC / "en" / f"{key}.html", SRC / "fr" / f"{key}.html"
    if kind == "full":
        en_rows = parse_full_table(en_path, "en")
        fr_rows = parse_full_table(fr_path, "fr")
    else:
        en_rows = parse_smelting(en_path, "en") + parse_camp(en_path, "en")
        fr_rows = parse_smelting(fr_path, "fr") + parse_camp(fr_path, "fr")
    if len(fr_rows) != len(en_rows):
        # align by item_id then leftover by order
        fr_by_id = {r["item_id"]: r for r in fr_rows if r.get("item_id")}
        used = set()
        aligned = []
        extras = [r for r in fr_rows]
        for er in en_rows:
            match = None
            if er.get("item_id") and er["item_id"] in fr_by_id:
                match = fr_by_id[er["item_id"]]
            aligned.append(match)
            if match is not None and id(match) not in used:
                used.add(id(match))
        # fallback positional if none matched (smelting has no ids)
        if all(m is None for m in aligned) and len(fr_rows) == len(en_rows):
            aligned = fr_rows
        elif any(m is None for m in aligned) and len(fr_rows) == len(en_rows):
            aligned = [m if m is not None else fr_rows[i] for i, m in enumerate(aligned)]
        fr_rows_aligned = aligned
    else:
        fr_rows_aligned = fr_rows

    out = []
    for i, er in enumerate(en_rows):
        fr = fr_rows_aligned[i] if i < len(fr_rows_aligned) and fr_rows_aligned[i] is not None else {}
        name_fr, name_en = display_names(er["name"], (fr or {}).get("name") or "")
        typ = er.get("typ") or "inconnu"
        source_en = er.get("source_en") or "not recorded"
        source_fr = (fr or {}).get("source_fr") or ""
        if typ == "formateur":
            if er.get("flag") == "auto":
                source_en = "learned automatically with the profession"
                source_fr = "appris automatiquement avec le métier"
            else:
                source_en = "profession trainer (unnamed)"
                source_fr = "maître de métier (non nommé)"
        elif typ == "inconnu":
            source_en = "not recorded"
            source_fr = "non indiqué"
        else:
            # prefer FR source names from the FR guide when present
            if not source_fr:
                source_fr = source_en
        rec = {
            "skill": er.get("skill"),
            "item_id": er.get("item_id") or (fr or {}).get("item_id"),
            "name_en": name_en,
            "name_fr": name_fr,
            "typ": typ,
            "source_en": source_en,
            "source_fr": source_fr,
            "zone_fr": "non indiqué",
            "zone_en": "not recorded",
            "official_acq": False,
        }
        apply_enrichment(rec, drop_map, quest_map, vendor_map)
        out.append(rec)
    return out


def bz_sources():
    return [
        {"key": "bz-24303313-fr", "language": "fr", "url": "https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever", "title": "Récapitulatif de la présentation « Au cœur de World of Warcraft: Forever »", "publishedAt": "2026-09-13", "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV},
        {"key": "bz-24303313-en", "language": "en", "url": "https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap", "title": "World of Warcraft: Forever Deep Dive Panel Recap", "publishedAt": "2026-09-13", "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV},
        {"key": "bz-camp-fr", "language": "fr", "url": "https://news.blizzard.com/fr-fr/article/24301516/retrouvez-vous-autour-dun-feu-de-camp-dans-world-of-warcraft-forever", "title": "Retrouvez-vous autour d’un feu de camp dans World of Warcraft: Forever", "publishedAt": "2026-10-21", "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV},
        {"key": "bz-camp-en", "language": "en", "url": "https://news.blizzard.com/en-us/article/24301516/gather-around-the-campfire-in-world-of-warcraft-forever", "title": "Gather Around the Campfire in World of Warcraft: Forever", "publishedAt": "2026-10-21", "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV},
        {"key": "bz-hotfixes-en", "language": "en", "url": "https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-11-2026", "title": "WoW: Forever Hotfixes - November 11, 2026", "publishedAt": "2026-11-11", "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV},
    ]


def client_sources(key: str, prof: dict):
    title_en = f"{prof['en']} profession guide — full recipe list (client-extracted data, to be confirmed)"
    title_fr = f"Guide {prof['fr']} — liste des recettes (données extraites du client, à confirmer)"
    return [
        {"key": f"client-guide-{key}-fr", "language": "fr", "url": f"https://eternadex.com/fr/berufe/{key}/", "title": title_fr, "accessedAt": ACC, "license": CLIENT_LICENSE, "gameVersion": GV, "verification": "à confirmer", "undated": True},
        {"key": f"client-guide-{key}-en", "language": "en", "url": f"https://eternadex.com/en/berufe/{key}/", "title": title_en, "accessedAt": ACC, "license": CLIENT_LICENSE, "gameVersion": GV, "verification": "à confirmer", "undated": True},
    ]


def counts(recipes):
    c = Counter(r["typ"] for r in recipes)
    return c


def skill_cell(skill):
    if skill is None:
        return {"fr": "non indiqué", "en": "not recorded"}
    s = str(int(skill))
    return {"fr": s, "en": s}


def row_cells(r):
    typ = r["typ"]
    return [
        {"fr": clip(r["name_fr"], 400), "en": clip(r["name_en"], 400)},
        skill_cell(r["skill"]),
        {"fr": TYPE_LABEL[typ]["fr"], "en": TYPE_LABEL[typ]["en"]},
        {"fr": clip(r["source_fr"], 400), "en": clip(r["source_en"], 400)},
        {"fr": clip(r["zone_fr"], 400), "en": clip(r["zone_en"], 400)},
        {"fr": "à confirmer", "en": "to be confirmed"},
    ]


HEAD = [
    {"fr": "Recette", "en": "Recipe"},
    {"fr": "Compétence requise", "en": "Required skill"},
    {"fr": "Obtention", "en": "How obtained"},
    {"fr": "Source", "en": "Source"},
    {"fr": "Zone", "en": "Zone"},
    {"fr": "Statut", "en": "Status"},
]


def in_bracket(skill, lo, hi):
    return skill is not None and lo <= skill <= hi


def build_entry(meta, recipes, all_ids):
    key = meta["key"]
    c = counts(recipes)
    n = len(recipes)
    known_zone = sum(1 for r in recipes if r["zone_en"] not in {"not recorded", ""})
    src_client = f"client-guide-{key}"
    src_all = ["bz-24303313", "bz-camp", src_client]
    # include hotfixes when relevant names appear
    use_hf = any(norm_name(r["name_en"]) in {"tanning rack", "journeyman campfire kit", "arcane salvager", "fishing rack", "elixir of holy power", "elixir of greater firepower"} or "bag" in norm_name(r["name_en"]) and meta["key"] == "schneiderei" for r in recipes)
    if use_hf:
        src_all.append("bz-hotfixes")

    missing = n - known_zone
    typ_fr = ", ".join(f"{TYPE_LABEL[k]['fr']} {c[k]}" for k in ["formateur", "vendeur", "butin", "quete", "reputation", "inconnu"] if c[k])
    typ_en = ", ".join(f"{TYPE_LABEL[k]['en']} {c[k]}" for k in ["formateur", "vendeur", "butin", "quete", "reputation", "inconnu"] if c[k])

    desc_fr = (
        f"Liste des {n} recettes de {meta['prof']['fr']} relevées dans des données extraites du client le 12 novembre 2026. "
        f"Tout le contenu de cette liste est à confirmer : ce n’est pas une publication officielle de Blizzard. "
        f"Répartition indiquée : {typ_fr}. Les noms français viennent de la localisation du jeu lorsqu’elle est disponible ; sinon le nom anglais est conservé."
    )
    desc_en = (
        f"List of the {n} {meta['prof']['en']} recipes recorded in client-extracted data on 12 November 2026. "
        f"Everything in this list is to be confirmed: it is not an official Blizzard publication. "
        f"Breakdown given: {typ_en}. French names come from in-game localization when available; otherwise the English name is kept."
    )

    lead_fr = (
        f"Blizzard a annoncé plus de 600 nouvelles recettes, sans publier la liste complète. "
        f"Cette fiche rassemble les {n} recettes de {meta['prof']['fr']} relevées dans des données extraites du client (consultées le 12 novembre 2026). "
        f"Chaque ligne est à confirmer. Les tableaux sont groupés par palier de compétence requise. "
        f"Quand l’obtention, la source ou la zone n’est pas indiquée dans les données consultées, la cellule le dit clairement. Aucun taux de butin n’est repris, aucun n’était indiqué."
    )
    lead_en = (
        f"Blizzard announced over 600 new recipes without publishing a complete list. "
        f"This page gathers the {n} {meta['prof']['en']} recipes recorded in client-extracted data (consulted on 12 November 2026). "
        f"Every row is to be confirmed. Tables are grouped by required skill bracket. "
        f"When acquisition, source or zone is not given in the data consulted, the cell says so. No drop rates are repeated; none were given."
    )

    relations = ["forever-professions-blueprints", "forever-professions-overview", "forever-camp-features"]
    relations += [p for p in all_ids if p != meta["id"]]

    sections = []
    sections.append({
        "id": "lire-cette-liste",
        "title": {"fr": "Comment lire cette liste", "en": "How to read this list"},
        "blocks": [
            {"type": "p", "fr": clip(
                "Cette liste n’est pas officielle. Blizzard n’a pas publié le détail des recettes de ce métier (vendeurs, formateurs, monstres, zones, prix, taux de butin). "
                "Les lignes ci-dessous viennent de données extraites du client et restent à confirmer. "
                "Le nom français est celui de la localisation du jeu lorsqu’il a été trouvé ; à défaut, le nom anglais est utilisé dans les deux langues. "
                "« Formateur » couvre aussi les recettes indiquées comme apprises automatiquement avec le métier. "
                "Une page d’ensemble déjà en ligne, Recettes et plans avancés (/fr/metiers/recettes-et-plans-avances/), rappelle les règles officielles d’obtention et les recettes à butin déjà présentées par zone.",
                2400), "en": clip(
                "This list is not official. Blizzard has not published the details of this profession’s recipes (vendors, trainers, monsters, zones, prices, drop rates). "
                "The rows below come from client-extracted data and remain to be confirmed. "
                "The French name is the in-game localization when one was found; otherwise the English name is used in both languages. "
                "“Trainer” also covers recipes listed as learned automatically with the profession. "
                "An overview page already online, Recipes and advanced blueprints (/en/professions/recipes-and-advanced-blueprints/), restates the official acquisition rules and the lootable recipes already shown by zone.",
                2400), "src": src_all},
            {"type": "list", "items": [
                {"fr": f"{n} recettes listées pour {meta['prof']['fr']}.", "en": f"{n} recipes listed for {meta['prof']['en']}.", "src": [src_client]},
                {"fr": f"Répartition (à confirmer) : {typ_fr}.", "en": f"Breakdown (to be confirmed): {typ_en}.", "src": [src_client]},
                {"fr": f"Zone renseignée pour {known_zone} recette(s) ; non indiquée pour les autres.", "en": f"Zone recorded for {known_zone} recipe(s); not recorded for the others.", "src": [src_client]},
            ]},
        ],
    })

    grouped = defaultdict(list)
    unknown = []
    for r in recipes:
        placed = False
        for sid, lo, hi, _title in BRACKETS:
            if in_bracket(r["skill"], lo, hi):
                grouped[sid].append(r)
                placed = True
                break
        if not placed:
            unknown.append(r)
    for sid, lo, hi, title in BRACKETS:
        rows = grouped.get(sid) or []
        if not rows:
            continue
        rows = sorted(rows, key=lambda r: (r["skill"] is None, r["skill"] or 0, r["name_en"]))
        cap_fr = clip(f"{title['fr']} : {len(rows)} recettes de {meta['prof']['fr']} — données extraites du client, à confirmer (12/11/2026). Taux de butin non indiqués.", 300)
        cap_en = clip(f"{title['en']}: {len(rows)} {meta['prof']['en']} recipes — client-extracted data, to be confirmed (12 Nov 2026). Drop rates not given.", 300)
        sections.append({
            "id": sid,
            "title": {"fr": f"{title['fr']} — {len(rows)} recettes à confirmer", "en": f"{title['en']} — {len(rows)} recipes to be confirmed"},
            "blocks": [{
                "type": "table",
                "caption": {"fr": cap_fr, "en": cap_en},
                "head": HEAD,
                "rows": [row_cells(r) for r in rows],
                "src": [src_client] + (["bz-camp"] if any(r.get("official_acq") for r in rows) else []),
            }],
        })
    if unknown:
        unknown = sorted(unknown, key=lambda r: r["name_en"])
        cap_fr = clip(f"Compétence non indiquée : {len(unknown)} recettes de {meta['prof']['fr']} — données extraites du client, à confirmer (12/11/2026).", 300)
        cap_en = clip(f"Required skill not recorded: {len(unknown)} {meta['prof']['en']} recipes — client-extracted data, to be confirmed (12 Nov 2026).", 300)
        sections.append({
            "id": "competence-non-indiquee",
            "title": {"fr": f"Compétence non indiquée — {len(unknown)} recettes à confirmer", "en": f"Skill not recorded — {len(unknown)} recipes to be confirmed"},
            "blocks": [{
                "type": "table",
                "caption": {"fr": cap_fr, "en": cap_en},
                "head": HEAD,
                "rows": [row_cells(r) for r in unknown],
                "src": [src_client] + (["bz-camp"] if any(r.get("official_acq") for r in unknown) else []),
            }],
        })

    sections.append({
        "id": "historique-des-corrections",
        "title": {"fr": "Historique des corrections", "en": "Correction history"},
        "blocks": [{"type": "list", "items": [
            {"fr": "12 novembre 2026 (brouillon, non validé) : première liste complète des recettes de ce métier, d’après des données extraites du client, avec mention « à confirmer ». Aucune publication.",
             "en": "12 November 2026 (draft, not approved): first complete list of this profession’s recipes, from client-extracted data, marked “to be confirmed”. No publication.",
             "src": [src_client, "bz-24303313"]},
        ]}],
    })

    pending = [
        {"fr": "Liste officielle complète des recettes, matériaux, prix et formateurs nommés : non publiée par Blizzard.",
         "en": "Complete official list of recipes, materials, prices and named trainers: not published by Blizzard."},
        {"fr": "Pour une partie des recettes, l’obtention, la source ou la zone n’était pas indiquée dans les données consultées ; ces cellules restent à « non indiqué ».",
         "en": "For some recipes, acquisition, source or zone was not given in the data consulted; those cells stay as “not recorded”."},
        {"fr": "Taux de butin : non indiqués dans les données consultées, et non publiés officiellement.",
         "en": "Drop rates: not given in the data consulted, and not officially published."},
    ]
    if any(r["name_fr"] == r["name_en"] for r in recipes):
        pending.append({"fr": "Certaines recettes n’ont pas de nom français distinct dans les données consultées : le nom anglais est alors utilisé.",
                        "en": "Some recipes have no distinct French name in the data consulted: the English name is then used."})

    confirmed = [
        {"fr": "Blizzard a annoncé plus de 600 nouvelles recettes, sans en publier la liste complète.",
         "en": "Blizzard announced over 600 new recipes, without publishing a complete list.",
         "src": ["bz-24303313"]},
        {"fr": "Premier objet de campement : compétence 20, via des quêtes des zones de départ ou l’achat auprès d’un maître de métier (PNJ, quêtes, zones précises et prix non nommés).",
         "en": "First campsite object: skill 20, via starter-zone quests or purchase from a profession trainer (NPCs, quests, exact zones and prices unnamed).",
         "src": ["bz-camp"]},
    ]

    dates = [
        {"date": "2026-09-13", "fr": "Deep Dive : plus de 600 recettes, plans de boss de donjon.", "en": "Deep Dive: over 600 recipes, dungeon-boss blueprints.", "src": ["bz-24303313"]},
        {"date": "2026-10-21", "fr": "Article campement : règles d’obtention (20 / 140+) et onze exemples nommés.", "en": "Camping article: acquisition rules (20 / 140+) and eleven named examples.", "src": ["bz-camp"]},
        {"date": "2026-11-12", "fr": f"Consultation des données extraites du client pour les {n} recettes de {meta['prof']['fr']}.", "en": f"Client-extracted data consulted for the {n} {meta['prof']['en']} recipes.", "src": [src_client]},
    ]

    entry = {
        "id": meta["id"],
        "title": meta["title"],
        "category": "professions",
        "subcategory": "recettes",
        "description": {"fr": clip(desc_fr, 1000), "en": clip(desc_en, 1000)},
        "sources": bz_sources() + client_sources(key, meta["prof"]),
        "status": "draft",
        "identityConfirmed": False,
        "updatedAt": NOW,
        "version": 1,
        "gameVersion": GV,
        "verification": "à confirmer",
        "relations": relations,
        "article": {
            "format": 1,
            "slug": meta["slug"],
            "illustration": "professions",
            "lead": {"fr": clip(lead_fr, 1200), "en": clip(lead_en, 1200), "src": src_all},
            "keyPoints": [
                {"fr": f"{n} recettes de {meta['prof']['fr']} listées ci-dessous, toutes à confirmer (données extraites du client, 12 novembre 2026).",
                 "en": f"{n} {meta['prof']['en']} recipes listed below, all to be confirmed (client-extracted data, 12 November 2026).",
                 "src": [src_client]},
                {"fr": f"Obtention indiquée (à confirmer) : {typ_fr}.",
                 "en": f"Acquisition given (to be confirmed): {typ_en}.",
                 "src": [src_client]},
                {"fr": "Blizzard n’a pas publié la liste complète des recettes, ni les formateurs, vendeurs, prix ou taux de butin.",
                 "en": "Blizzard has not published the complete recipe list, nor trainers, vendors, prices or drop rates.",
                 "src": ["bz-24303313", "bz-camp"]},
            ],
            "sections": sections,
            "confirmed": confirmed,
            "pending": pending,
            "dates": dates,
        },
        "history": [{"actor": ACTOR, "note": HIST_NOTE, "at": NOW, "version": 1}],
    }
    return entry, {"id": meta["id"], "n": n, "counts": dict(c), "known_zone": known_zone, "samples": recipes[:3] + recipes[max(0, n // 2) : max(0, n // 2) + 1] + recipes[-2:], "slug": meta["slug"], "title": meta["title"], "prof": meta["prof"], "recipes": recipes}


def forbidden_scan(obj, where=""):
    hits = []
    if isinstance(obj, dict):
        # skip urls
        for k, v in obj.items():
            if k == "url":
                continue
            hits += forbidden_scan(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += forbidden_scan(v, f"{where}[{i}]")
    elif isinstance(obj, str) and FORBIDDEN.search(obj):
        hits.append((where, FORBIDDEN.search(obj).group(0), obj[:120]))
    return hits


def build_blueprints_revise(entries_meta):
    records = json.loads((TREE / "pipeline/runtime/entries.json").read_text())
    bp = deepcopy(next(e for e in records if e["id"] == "forever-professions-blueprints"))
    rows = []
    for m in entries_meta:
        rows.append([
            {"fr": m["prof"]["fr"], "en": m["prof"]["en"]},
            {"fr": m["title"]["fr"], "en": m["title"]["en"]},
            {"fr": str(m["n"]), "en": str(m["n"])},
            {"fr": f"/fr/metiers/{m['slug']['fr']}/", "en": f"/en/professions/{m['slug']['en']}/"},
            {"fr": "à confirmer (brouillon)", "en": "to be confirmed (draft)"},
        ])
    section = {
        "id": "listes-par-metier",
        "title": {"fr": "Listes par métier (brouillons, à confirmer)", "en": "Lists by profession (drafts, to be confirmed)"},
        "blocks": [
            {"type": "p",
             "fr": "Les pages ci-dessous rassemblent, métier par métier, les recettes relevées dans des données extraites du client le 12 novembre 2026. Toutes les lignes de ces listes restent à confirmer. Ces pages sont des brouillons, non publiés. Blizzard n’a pas publié de liste officielle complète.",
             "en": "The pages below gather, profession by profession, the recipes recorded in client-extracted data on 12 November 2026. Every row on those lists remains to be confirmed. These pages are drafts and are not published. Blizzard has not issued a complete official list.",
             "src": ["bz-24303313", "client-guide-alchemie", "client-guide-kochkunst"]},
            {"type": "table",
             "caption": {"fr": "Pages de listes par métier — brouillons, données extraites du client, à confirmer (12/11/2026).",
                         "en": "Per-profession list pages — drafts, client-extracted data, to be confirmed (12 Nov 2026)."},
             "head": [{"fr": "Métier", "en": "Profession"}, {"fr": "Page", "en": "Page"}, {"fr": "Recettes", "en": "Recipes"}, {"fr": "Adresse", "en": "Path"}, {"fr": "Statut", "en": "Status"}],
             "rows": rows,
             "src": ["client-guide-alchemie", "client-guide-schmiedekunst", "client-guide-kochkunst", "bz-24303313"]},
        ],
    }
    secs = bp["article"]["sections"]
    # insert before correction history
    idx = next((i for i, s in enumerate(secs) if s["id"] == "historique-des-corrections"), len(secs))
    secs.insert(idx, section)
    # add history bullet
    hist = secs[idx + 0 if secs[idx]["id"] == "historique-des-corrections" else idx]
    # find history section after insert
    hist = next(s for s in secs if s["id"] == "historique-des-corrections")
    hist["blocks"][0]["items"].append({
        "fr": "12 novembre 2026 (brouillon, non validé) : renvoi vers les listes de recettes par métier, toutes marquées « à confirmer ». Cette révision n’est pas une publication.",
        "en": "12 November 2026 (draft, not approved): links to the per-profession recipe lists, all marked “to be confirmed”. This revision is not a publication.",
        "src": ["bz-24303313", "client-guide-alchemie"],
    })
    for p in entries_meta:
        if p["id"] not in bp["relations"]:
            bp["relations"].append(p["id"])
    bp["status"] = "draft"
    bp["identityConfirmed"] = False
    bp["updatedAt"] = NOW
    bp["version"] = int(bp.get("version") or 12) + 1
    bp["gameVersion"] = GV
    bp.setdefault("history", []).append({"actor": ACTOR, "note": HIST_NOTE, "at": NOW, "version": bp["version"]})
    # keep existing sources; they already include client guides for the 7 crafts. Add first-aid + gathering if missing.
    have = {s["key"] for s in bp["sources"]}
    extras = [
        ("erste-hilfe", "Secourisme", "First Aid"),
        ("bergbau", "Minage", "Mining"),
        ("kraeuterkunde", "Herboristerie", "Herbalism"),
        ("kuerschnerei", "Dépeçage", "Skinning"),
        ("angeln", "Pêche", "Fishing"),
    ]
    for key, fr, en in extras:
        for s in client_sources(key, {"fr": fr, "en": en}):
            if s["key"] not in have and len(bp["sources"]) < 20:
                bp["sources"].append(s)
                have.add(s["key"])
    return bp


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    drop_map, quest_map, vendor_map = load_csv_maps()
    all_ids = [p["id"] for p in PROFESSIONS]
    entries = []
    summary = []
    for meta in PROFESSIONS:
        recipes = merge_profession(meta, drop_map, quest_map, vendor_map)
        if not recipes:
            print(f"SKIP {meta['key']}: 0 recipes")
            continue
        entry, info = build_entry(meta, recipes, all_ids)
        hits = forbidden_scan(entry)
        if hits:
            raise SystemExit(f"forbidden text in {meta['id']}: {hits[:3]}")
        path = OUT / f"{meta['id']}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"WROTE {path.name} n={info['n']} counts={info['counts']}")
        entries.append(entry)
        # store lighter summary (no full recipe list in samples only)
        summary.append({k: v for k, v in info.items() if k != "recipes"} | {
            "unknown_source": info["counts"].get("inconnu", 0),
            "unknown_zone": info["n"] - info["known_zone"],
            "no_fr_distinct": sum(1 for r in recipes if r["name_fr"] == r["name_en"]),
            "skill_missing": sum(1 for r in recipes if r["skill"] is None),
            "sample_rows": [
                {"fr": r["name_fr"], "en": r["name_en"], "skill": r["skill"], "typ": r["typ"],
                 "source_fr": r["source_fr"], "source_en": r["source_en"], "zone_fr": r["zone_fr"], "zone_en": r["zone_en"]}
                for r in info["samples"]
            ],
        })

    batch_path = OUT / "batch-recettes-metiers.json"
    batch_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BATCH", batch_path, "bytes", batch_path.stat().st_size, "entries", len(entries))

    bp = build_blueprints_revise(summary)
    hits = forbidden_scan(bp)
    if hits:
        raise SystemExit(f"forbidden text in blueprints revise: {hits[:3]}")
    rp = OUT / "forever-professions-blueprints.revise.json"
    rp.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("REVISE", rp, "version", bp["version"], "sources", len(bp["sources"]))

    (OUT / "SUMMARY.json").write_text(json.dumps({
        "accessedAt": ACC,
        "total_recipes": sum(s["n"] for s in summary),
        "pages": summary,
        "by_type": {k: sum(s["counts"].get(k, 0) for s in summary) for k in TYPE_LABEL},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("TOTAL", sum(s["n"] for s in summary))


if __name__ == "__main__":
    main()
