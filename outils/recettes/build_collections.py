#!/usr/bin/env python3
"""Draft toy / pet / mount sheets. Official Blizzard first; client lists as à confirmer. No invented facts."""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources-brutes" / "collections"
OUT = HERE / "brouillons"
TREE = HERE / "test-tree-v36"
ACC = "2026-11-12"
NOW = "2026-11-12T05:00:00.000Z"
GV = "World of Warcraft: Forever — annonces et notes officielles, état documentaire 2026-11-12"
ACTOR = "AI-documentary-draft"
HIST_NOTE = (
    "Listes de jouets, mascottes et montures, d’après les sources officielles citées et des données "
    "extraites du client (à confirmer). Brouillon à relire. Pas une validation de publication."
)
BZ_LICENSE = (
    "Droits réservés Blizzard ; référence et synthèse originale (courtes citations), "
    "mention © Blizzard Entertainment conservée ; site non commercial."
)
CLIENT_LICENSE = (
    "Données de tiers (extrait de fichiers client) ; consultation des listes le 12 novembre 2026 ; "
    "informations à confirmer, non officielles."
)
FORBIDDEN = re.compile(r"Eternadex|Wowhead|wiki\.gg", re.I)

def clip(text, n):
    text = " ".join((text or "").split())
    if not text:
        text = "—"
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"

def bz(key, lang, url, title, published):
    return {"key": key, "language": lang, "url": url, "title": title,
            "publishedAt": published, "accessedAt": ACC, "license": BZ_LICENSE, "gameVersion": GV}

def client_src(key, lang, url, title):
    return {"key": key, "language": lang, "url": url, "title": title,
            "accessedAt": ACC, "license": CLIENT_LICENSE, "gameVersion": GV,
            "verification": "à confirmer", "undated": True}

SOURCES_COMMON = [
    bz("bz-legacy-fr", "fr", "https://news.blizzard.com/fr-fr/article/24307383/decouvrez-le-systeme-dheritage-de-world-of-warcraft-forever",
       "Découvrez le système d’héritage de World of Warcraft: Forever", "2026-09-23"),
    bz("bz-legacy-en", "en", "https://news.blizzard.com/en-us/article/24307383/get-to-know-the-world-of-warcraft-forever-legacy-system",
       "Get to Know the World of Warcraft: Forever Legacy System", "2026-09-23"),
    bz("bz-pack-fr", "fr", "https://news.blizzard.com/fr-fr/article/24301508/achetez-les-avantages-de-world-of-warcraft-forever-et-lancez-vous-dans-vos-prochaines-aventures-sur-azeroth",
       "Achetez les avantages de World of Warcraft: Forever et lancez-vous dans vos prochaines aventures sur Azeroth", "2026-09-12"),
    bz("bz-pack-en", "en", "https://news.blizzard.com/en-us/article/24301508/purchase-world-of-warcraft-forever-upgrades-and-begin-your-next-journey-in-azeroth",
       "Purchase World of Warcraft: Forever Upgrades and Begin Your Next Journey in Azeroth", "2026-09-12"),
    bz("bz-sub-year-fr", "fr", "https://news.blizzard.com/fr-fr/article/24310658/debloquez-un-an-de-world-of-warcraft-et-recevez-des-tresors-bonus",
       "Débloquez un an de World of Warcraft® et recevez des trésors bonus", "2026-10-15"),
    bz("bz-sub-year-en", "en", "https://news.blizzard.com/en-us/article/24310658/unlock-a-year-of-world-of-warcraft-and-get-bonus-treasures",
       "Unlock a Year of World of Warcraft® and Get Bonus Treasures", "2026-10-15"),
    bz("bz-hotfixes-en", "en", "https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-11-2026",
       "WoW: Forever Hotfixes - November 11, 2026", "2026-11-11"),
]
CLIENT_PET = client_src("client-haustiere-en", "en", "https://eternadex.com/en/haustiere/",
    "Pets list (client-extracted data, to be confirmed)")
CLIENT_MOUNT = client_src("client-reittiere-en", "en", "https://eternadex.com/en/reittiere/",
    "Mounts list (client-extracted data, to be confirmed)")

HEAD = [
    {"fr": "Nom", "en": "Name"},
    {"fr": "Héritage", "en": "Legacy"},
    {"fr": "Zone", "en": "Zone"},
    {"fr": "PNJ", "en": "NPC"},
    {"fr": "Obtention", "en": "How obtained"},
    {"fr": "Faction", "en": "Faction"},
    {"fr": "Statut", "en": "Status"},
]

# Official rows
HERITAGE_FR = "Récompense d’héritage du lancement (palier de points, défi et rang : non publiés)"
HERITAGE_EN = "Launch Legacy reward (point threshold, challenge and tier: not published)"
PACK_FR = "Pack héroïque des Éolides (inclus aussi dans le pack épique des Éolides et la Warcraft Forever Collection)"
PACK_EN = "Skyborne Heroic Pack (also included in the Skyborne Epic Pack and the Warcraft Forever Collection)"
NA = {"fr": "non indiqué", "en": "not recorded"}
BOTH = {"fr": "non indiqué", "en": "not recorded"}  # official texts don't assign a faction
OK = {"fr": "confirmé officiel", "en": "officially confirmed"}
AC = {"fr": "à confirmer", "en": "to be confirmed"}

def R(name_fr, name_en, typ, heritage=None, zone=None, npc=None, how_fr="", how_en="", faction=None, official=False, extra_src=None, item_id=None, price_fr="", price_en=""):
    return {
        "name_fr": name_fr, "name_en": name_en, "typ": typ,
        "heritage_fr": heritage["fr"] if heritage else "aucun",
        "heritage_en": heritage["en"] if heritage else "none",
        "zone_fr": (zone or NA)["fr"], "zone_en": (zone or NA)["en"],
        "npc_fr": (npc or NA)["fr"], "npc_en": (npc or NA)["en"],
        "how_fr": how_fr, "how_en": how_en,
        "faction_fr": (faction or NA)["fr"], "faction_en": (faction or NA)["en"],
        "official": official, "src": extra_src or [],
        "item_id": item_id, "price_fr": price_fr, "price_en": price_en,
    }

OFFICIAL_TOYS = [
    R("Réplique de carabine à air comprimé de Forgefer", "Replica Ironforge Air Rifle", "héritage",
      heritage={"fr": HERITAGE_FR, "en": HERITAGE_EN},
      how_fr="héritage (points d’héritage cumulés sur le compte)",
      how_en="Legacy (Legacy points accumulated on the account)",
      official=True, extra_src=["bz-legacy"]),
    R("Puits de vent shen’dorei", "Shen’dorei Windwell", "pack",
      how_fr=f"pack boutique — {PACK_FR}",
      how_en=f"shop pack — {PACK_EN}",
      official=True, extra_src=["bz-pack"]),
]
OFFICIAL_PETS = [
    R("Ourson spectral", "Spectral Bear Cub", "héritage",
      heritage={"fr": HERITAGE_FR, "en": HERITAGE_EN},
      how_fr="héritage (points d’héritage cumulés sur le compte)",
      how_en="Legacy (Legacy points accumulated on the account)",
      official=True, extra_src=["bz-legacy"], item_id="277714"),
    R("Azurbie", "Azurky", "abonnement",
      how_fr="abonnement : offre spéciale 6 ou 12 mois (bonus à récupérer avant le 30 avril 2027 ; arrivée au plus tard le 31 octobre 2026)",
      how_en="subscription: 6- or 12-month special offer (redeem by 30 April 2027; granted by 31 October 2026 at the latest)",
      official=True, extra_src=["bz-sub-year"]),
]
OFFICIAL_MOUNTS = [
    R("Rênes d’ours spectral", "Reins of the Spectral Bear", "héritage",
      heritage={"fr": HERITAGE_FR, "en": HERITAGE_EN},
      how_fr="héritage (points d’héritage cumulés sur le compte)",
      how_en="Legacy (Legacy points accumulated on the account)",
      official=True, extra_src=["bz-legacy"], item_id="277718"),
    R("Fièregriffe céruléenne", "Cerulean Prideclaw", "pack",
      how_fr=f"pack boutique — {PACK_FR} ; la compétence de monte doit être achetée en jeu pour l’utiliser",
      how_en=f"shop pack — {PACK_EN}; the riding skill must be purchased in-game before it can be used",
      official=True, extra_src=["bz-pack"], item_id="280544"),
]

def parse_money(td):
    if td is None:
        return "", ""
    g = td.find(class_="g")
    s = td.find(class_="s")
    parts_fr, parts_en = [], []
    if g and g.get_text(strip=True):
        n = g.get_text(strip=True)
        parts_fr.append(f"{n} po")
        parts_en.append(f"{n} gold")
    if s and s.get_text(strip=True):
        n = s.get_text(strip=True)
        if n != "0" or not parts_fr:
            parts_fr.append(f"{n} pa")
            parts_en.append(f"{n} silver")
    if not parts_fr:
        return "", ""
    return ("prix dans les données du client : " + " ".join(parts_fr) + " (à confirmer)",
            "price in client data: " + " ".join(parts_en) + " (to be confirmed)")

def faction_pair(text):
    t = (text or "").strip().lower()
    if t in {"both", "les deux", "both factions"}:
        return {"fr": "les deux", "en": "both"}
    if t == "alliance":
        return {"fr": "Alliance", "en": "Alliance"}
    if t == "horde":
        return {"fr": "Horde", "en": "Horde"}
    if not t or t in {"–", "-", "—"}:
        return NA
    return {"fr": text.strip(), "en": text.strip()}

def extract_id(el):
    if not el:
        return None
    href = el.get("href") or ""
    m = re.search(r"/item/(\d+)/?", href)
    return m.group(1) if m else (str(el.get("data-item")) if el.get("data-item") else None)

def parse_list_table(path, kind):
    """Parse 'Known from Classic' table. kind: pet|mount."""
    soup = BeautifulSoup(Path(path).read_text(encoding="utf-8", errors="replace"), "html.parser")
    table = None
    for t in soup.find_all("table"):
        prev = t.find_previous(["h2", "h1"])
        if prev and "classic" in prev.get_text().lower():
            table = t
            break
    if table is None:
        return []
    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if kind == "pet":
            if len(tds) < 4:
                continue
            name_td, fac_td, price_td, src_td = tds[0], tds[1], tds[2], tds[3]
            item_el = name_td.find("a") or name_td
            name = " ".join((item_el.get_text(" ", strip=True) or name_td.get_text(" ", strip=True)).split())
            item_id = extract_id(name_td.find("a"))
            level = None
        else:
            if len(tds) < 6:
                continue
            name_td, item_td, fac_td, lvl_td, price_td, src_td = tds
            item_el = item_td.find("a") or item_td
            item_name = " ".join(item_el.get_text(" ", strip=True).split())
            display = " ".join(name_td.get_text(" ", strip=True).split())
            no_item = (not item_name) or item_name.lower().startswith("no item")
            if no_item:
                name = display or item_name
            elif display and display != item_name and display not in item_name:
                name = f"{item_name} ({display})"
            else:
                name = item_name or display
            item_id = extract_id(item_td.find("a"))
            if no_item:
                # carried via a flag on the upcoming row
                pass
            try:
                level = int(re.search(r"\d+", lvl_td.get_text()).group(0)) if lvl_td.get_text(strip=True) else None
            except Exception:
                level = None
        src = " ".join(src_td.get_text(" ", strip=True).split())
        price_fr, price_en = parse_money(price_td)
        fac = faction_pair(fac_td.get_text(" ", strip=True))
        known = src and "not known" not in src.lower() and src not in {"–", "-", "—"}
        how_fr = "inconnu"
        how_en = "unknown"
        if known:
            how_fr = src
            how_en = src
        if price_fr and not known:
            how_fr = "inconnu"  # keep method unknown; price stored separately and can be shown in obtention as extra
            how_en = "unknown"
        # Append client price in obtention only as a note when no source, still "inconnu" as method
        obt_fr = "inconnu"
        obt_en = "unknown"
        if known:
            obt_fr, obt_en = src, src
        if price_fr:
            obt_fr = f"{obt_fr} — {price_fr}" if obt_fr != "inconnu" else f"inconnu — {price_fr}"
            obt_en = f"{obt_en} — {price_en}" if obt_en != "unknown" else f"unknown — {price_en}"
        if level:
            obt_fr += f" ; niveau indiqué dans les données du client : {level}"
            obt_en += f"; level in client data: {level}"
        if kind == "mount" and (not item_id) and ("no item" in (item_name if "item_name" in dir() else "").lower() if kind=="mount" else False):
            pass
        # item_name only defined for mounts; bind safely
        if kind == "mount":
            _iname = locals().get("item_name") or ""
            if _iname.lower().startswith("no item"):
                obt_fr += " — pas d’objet (monture de classe, données du client)"
                obt_en += " — no item (class mount, client data)"
        if item_id:
            sep_fr = " — " if obt_fr in {"inconnu", "unknown"} else " ; "
            sep_en = " — " if obt_en in {"inconnu", "unknown"} else "; "
            obt_fr += f"{sep_fr}identifiant dans les données du client : {item_id}"
            obt_en += f"{sep_en}identifier in client data: {item_id}"
        rows.append(R(name, name, "inconnu",
                      how_fr=obt_fr, how_en=obt_en, faction=fac, official=False,
                      extra_src=["client-haustiere" if kind == "pet" else "client-reittiere"],
                      item_id=item_id, price_fr=price_fr, price_en=price_en))
        if level:
            rows[-1]["level"] = level
    return rows

def method_key(r):
    if r["official"] and r["typ"] == "héritage":
        return "héritage"
    if r["official"] and r["typ"] == "pack":
        return "pack"
    if r["official"] and r["typ"] == "abonnement":
        return "abonnement"
    return "inconnu"

METHOD_SECTIONS = [
    ("heritage", "héritage", {"fr": "Héritage", "en": "Legacy"}),
    ("pack-boutique", "pack", {"fr": "Pack boutique", "en": "Shop pack"}),
    ("abonnement", "abonnement", {"fr": "Abonnement", "en": "Subscription"}),
    ("inconnu", "inconnu", {"fr": "Obtention inconnue (données du client)", "en": "Unknown acquisition (client data)"}),
]

def cells(r):
    return [
        {"fr": clip(r["name_fr"], 400), "en": clip(r["name_en"], 400)},
        {"fr": clip(r["heritage_fr"], 400), "en": clip(r["heritage_en"], 400)},
        {"fr": clip(r["zone_fr"], 400), "en": clip(r["zone_en"], 400)},
        {"fr": clip(r["npc_fr"], 400), "en": clip(r["npc_en"], 400)},
        {"fr": clip(r["how_fr"], 400), "en": clip(r["how_en"], 400)},
        {"fr": clip(r["faction_fr"], 200), "en": clip(r["faction_en"], 200)},
        OK if r["official"] else AC,
    ]

def build_entry(meta, official, client, sources, src_keys):
    all_rows = official + client
    n, n_off, n_cli = len(all_rows), len(official), len(client)
    n_herit = sum(1 for r in all_rows if r["typ"] == "héritage")
    typ_fr = f"{n_off} confirmée(s) officiellement, {n_cli} présente(s) dans les données du client avec obtention non indiquée"
    typ_en = f"{n_off} officially confirmed, {n_cli} present in client data with acquisition not recorded"

    desc_fr = (
        f"Liste des {n} {meta['kind_fr']} : d’abord ce que Blizzard a nommé, puis les noms relevés dans des données "
        f"extraites du client le 12 novembre 2026, à confirmer. Zone, PNJ et moyen d’obtention ne sont remplis que "
        f"lorsqu’une source le dit. Blizzard n’a pas publié de liste complète."
    )
    desc_en = (
        f"List of {n} {meta['kind_en']}: first what Blizzard has named, then names recorded in client-extracted data "
        f"on 12 November 2026, to be confirmed. Zone, NPC and acquisition are filled only when a source states them. "
        f"Blizzard has not published a complete list."
    )
    lead_fr = (
        f"Blizzard a nommé pour le lancement un petit nombre de {meta['kind_fr']} (héritage, packs boutique, "
        f"et le cas échéant un bonus d’abonnement). Le détail (zone, PNJ, palier d’héritage, prix d’achat en jeu) "
        f"n’est souvent pas publié. Cette fiche sépare clairement le confirmé officiel de ce qui reste à confirmer. "
        f"Une liste plus longue apparaît dans des données extraites du client ; leur présence dans ces fichiers "
        f"ne prouve pas qu’on puisse les obtenir en jeu. Tous ces ajouts restent à confirmer."
    )
    lead_en = (
        f"Blizzard has named a small number of {meta['kind_en']} at launch (Legacy, shop packs, and where relevant a "
        f"subscription bonus). Details (zone, NPC, Legacy threshold, in-game purchase price) are often unpublished. "
        f"This page keeps officially confirmed facts separate from what remains to be confirmed. A longer list appears "
        f"in client-extracted data; presence in those files does not prove the item can be obtained in game. All such "
        f"additions remain to be confirmed."
    )

    sections = [{
        "id": "lire-cette-liste",
        "title": {"fr": "Comment lire cette liste", "en": "How to read this list"},
        "blocks": [
            {"type": "p", "fr": clip(
                "Les lignes « confirmé officiel » viennent uniquement d’articles Blizzard cités. "
                "Les autres lignes viennent de données extraites du client (consultées le 12 novembre 2026) et restent à confirmer. "
                "Quand la zone, le PNJ ou le moyen d’obtention n’est pas indiqué, la cellule le dit. "
                "Aucun tarif, vendeur ou lieu Classic n’est ajouté de mémoire. "
                f"Une fiche déjà en ligne, Récompenses d’héritage (/fr/quetes/recompenses-heritage/), décrit les quatre récompenses du lancement. "
                f"{typ_fr}.", 2400),
             "en": clip(
                "Rows marked “officially confirmed” come only from the cited Blizzard articles. "
                "Other rows come from client-extracted data (consulted on 12 November 2026) and remain to be confirmed. "
                "When zone, NPC or acquisition is not given, the cell says so. "
                "No Classic vendor, price or location is added from memory. "
                f"An existing page, Legacy Rewards (/en/quests/legacy-rewards/), describes the four launch rewards. "
                f"{typ_en}.", 2400),
             "src": src_keys},
            {"type": "list", "items": [
                {"fr": f"{n} {meta['kind_fr']} listé(e)s, dont {n_herit} lié(e)s à l’héritage.",
                 "en": f"{n} {meta['kind_en']} listed, of which {n_herit} tied to Legacy.", "src": src_keys},
                {"fr": typ_fr + ".", "en": typ_en + ".", "src": src_keys},
            ]},
        ],
    }]

    # group official + client by method
    buckets = defaultdict(list)
    for r in all_rows:
        buckets[method_key(r)].append(r)
    for sid, key, title in METHOD_SECTIONS:
        rows = buckets.get(key) or []
        if not rows:
            continue
        if key == "inconnu":
            rows = sorted(rows, key=lambda r: r["name_en"].lower())
        cap_fr = clip(f"{title['fr']} : {len(rows)} {meta['kind_fr']} — " +
                      ("sources officielles Blizzard." if key != "inconnu" else "données extraites du client, à confirmer (12/11/2026). Obtention, zone et PNJ non indiqués, sauf un prix éventuellement relevé dans les données du client."), 300)
        cap_en = clip(f"{title['en']}: {len(rows)} {meta['kind_en']} — " +
                      ("official Blizzard sources." if key != "inconnu" else "client-extracted data, to be confirmed (12 Nov 2026). Acquisition, zone and NPC not recorded, except a price when one appears in the client data."), 300)
        src = (["bz-legacy"] if key == "héritage" else ["bz-pack"] if key == "pack" else ["bz-sub-year"] if key == "abonnement" else [s for s in src_keys if s.startswith("client")])
        sections.append({
            "id": sid,
            "title": {"fr": f"{title['fr']} — {len(rows)}", "en": f"{title['en']} — {len(rows)}"},
            "blocks": [{"type": "table", "caption": {"fr": cap_fr, "en": cap_en}, "head": HEAD,
                        "rows": [cells(r) for r in rows], "src": src}],
        })

    # par héritage
    herit = [r for r in all_rows if r["typ"] == "héritage"]
    if herit:
        cap_fr = clip("Vue par héritage : récompenses du lancement liées à cette fiche. Palier de points, défi et rang : non publiés par Blizzard.", 300)
        cap_en = clip("Legacy view: launch rewards on this page. Point threshold, challenge and tier: not published by Blizzard.", 300)
        sections.append({
            "id": "par-heritage",
            "title": {"fr": "Par héritage", "en": "By Legacy"},
            "blocks": [
                {"type": "p",
                 "fr": "Blizzard a annoncé quatre récompenses d’héritage au lancement (jouet, mascotte, tabard, monture), débloquées par les points d’héritage cumulés sur le compte. Le nombre de points, le défi et le rang requis n’ont pas été publiés. Le tabard d’ours spectral n’est pas repris dans cette fiche (ce n’est ni un jouet, ni une mascotte, ni une monture) ; il figure sur Récompenses d’héritage.",
                 "en": "Blizzard announced four launch Legacy rewards (toy, pet, tabard, mount), unlocked by Legacy points accumulated on the account. The number of points, the challenge and the required tier have not been published. The Spectral Bear Tabard is not listed on this page (it is neither a toy, a pet nor a mount); it appears on Legacy Rewards.",
                 "src": ["bz-legacy"]},
                {"type": "table", "caption": {"fr": cap_fr, "en": cap_en}, "head": HEAD,
                 "rows": [cells(r) for r in herit], "src": ["bz-legacy"]},
            ],
        })

    # mounts-only official note on racial vendors
    if meta["id"] == "forever-items-mounts":
        sections.insert(-1 if herit else len(sections), {
            "id": "montures-raciales-officiel",
            "title": {"fr": "Montures de vendeur racial (règle officielle)", "en": "Racial vendor mounts (official rule)"},
            "blocks": [{"type": "p",
                        "fr": "Correctif officiel du 10 novembre 2026 : toutes les montures de vendeur racial sont désormais liées quand ramassées. L’article ne nomme pas les montures, ni les vendeurs, ni les zones, ni les prix. Aucun nom n’est donc ajouté ici à partir d’une autre version du jeu.",
                        "en": "Official hotfix of 10 November 2026: all racial vendor mounts are now Bind-on-Pickup. The article does not name the mounts, vendors, zones or prices. No names are added here from another version of the game.",
                        "src": ["bz-hotfixes"]}],
        })

    sections.append({
        "id": "historique-des-corrections",
        "title": {"fr": "Historique des corrections", "en": "Correction history"},
        "blocks": [{"type": "list", "items": [{
            "fr": "12 novembre 2026 (brouillon, non validé) : première liste, officielles d’abord, puis données extraites du client marquées « à confirmer ». Aucune publication.",
            "en": "12 November 2026 (draft, not approved): first list, official names first, then client-extracted data marked “to be confirmed”. No publication.",
            "src": src_keys[:2],
        }]}],
    })

    pending = [
        {"fr": "Liste officielle complète, avec zones, PNJ, prix d’achat en jeu et paliers d’héritage : non publiée par Blizzard.",
         "en": "A complete official list, with zones, NPCs, in-game prices and Legacy thresholds: not published by Blizzard."},
        {"fr": "Pour les lignes issues des données du client, l’obtention, la zone et le PNJ n’étaient pas indiqués (« not known yet » sur la liste consultée).",
         "en": "For rows from client data, acquisition, zone and NPC were not given (“not known yet” on the list consulted)."},
        {"fr": "Blizzard a indiqué que des données du client ne sont pas destinées à Forever ; la liste « à confirmer » reprend uniquement ce que la source consultée range encore pour Forever, sans vérification en jeu.",
         "en": "Blizzard has said that some client data is not meant for Forever; the “to be confirmed” list keeps only what the consulted source still files for Forever, without in-game checks."},
    ]
    if meta["id"] == "forever-items-pets":
        pending.append({"fr": "Le pack épique des Éolides (et la Warcraft Forever Collection) inclut « des mascottes » pour la collection Forever, sans en publier les noms.",
                        "en": "The Skyborne Epic Pack (and the Warcraft Forever Collection) includes “pets” for the Forever collection, without publishing their names."})
    if any(r["name_fr"] == r["name_en"] and not r["official"] for r in all_rows):
        pending.append({"fr": "Aucun nom français officiel n’a été trouvé pour la plupart des noms issus des données du client : le nom anglais est conservé.",
                        "en": "No official French name was found for most client-data names: the English name is kept."})
    if meta["id"] == "forever-items-toys":
        pending.append({"fr": "Aucune liste client de jouets n’a été trouvée (pas de rubrique équivalente aux mascottes et montures).",
                        "en": "No client-extracted toy list was found (no section equivalent to the pet and mount lists)."})
    if meta["id"] == "forever-items-mounts":
        pending.append({"fr": "La liste consultée répétait deux fois la même ligne « Summon Black Qiraji Battle Tank » (pas d’objet, monture de classe) : une seule ligne est conservée ici.",
                        "en": "The consulted list repeated the same “Summon Black Qiraji Battle Tank” row twice (no item, class mount): only one row is kept here."})

    confirmed = []
    if official:
        confirmed.append({"fr": "Noms officiels cités par Blizzard pour cette fiche, avec le moyen d’obtention publié (héritage, pack boutique ou abonnement).",
                          "en": "Official names cited by Blizzard on this page, with the published acquisition method (Legacy, shop pack or subscription).",
                          "src": src_keys[:2]})
    if meta["id"] == "forever-items-mounts":
        confirmed.append({"fr": "Correctif du 10 novembre 2026 : les montures de vendeur racial sont liées quand ramassées (noms non publiés dans ce correctif).",
                          "en": "10 November 2026 hotfix: racial vendor mounts are Bind-on-Pickup (names not published in that hotfix).",
                          "src": ["bz-hotfixes"]})
    if not confirmed:
        confirmed.append({"fr": "Blizzard n’a pas publié de liste complète de cette catégorie.",
                          "en": "Blizzard has not published a complete list for this category.",
                          "src": ["bz-legacy"]})

    dates = [
        {"date": "2026-09-12", "fr": "Packs Éolides : Fièregriffe céruléenne, Puits de vent shen’dorei ; mascottes du pack épique non nommées.",
         "en": "Skyborne packs: Cerulean Prideclaw, Shen’dorei Windwell; Epic Pack pets unnamed.", "src": ["bz-pack"]},
        {"date": "2026-09-23", "fr": "Article héritage : les 4 récompenses du lancement (dont jouet, mascotte et monture).",
         "en": "Legacy article: the 4 launch rewards (including a toy, a pet and a mount).", "src": ["bz-legacy"]},
        {"date": "2026-10-15", "fr": "Bonus d’abonnement 6 ou 12 mois : mascotte Azurbie.",
         "en": "6- or 12-month subscription bonus: Azurky pet.", "src": ["bz-sub-year"]},
        {"date": "2026-11-10", "fr": "Correctif : montures de vendeur racial liées quand ramassées.",
         "en": "Hotfix: racial vendor mounts are Bind-on-Pickup.", "src": ["bz-hotfixes"]},
        {"date": "2026-11-12", "fr": "Consultation des listes extraites du client (mascottes et montures).",
         "en": "Client-extracted pet and mount lists consulted.", "src": [k for k in src_keys if k.startswith("client")] or src_keys[-1:]},
    ]

    relations = ["forever-legacy-rewards", "article-forever-items", "forever-legacy-challenges"]
    for other in ["forever-items-toys", "forever-items-pets", "forever-items-mounts"]:
        if other != meta["id"]:
            relations.append(other)

    entry = {
        "id": meta["id"],
        "title": meta["title"],
        "category": "items",
        "subcategory": "collections",
        "description": {"fr": clip(desc_fr, 1000), "en": clip(desc_en, 1000)},
        "sources": sources,
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
            "illustration": "items",
            "lead": {"fr": clip(lead_fr, 1200), "en": clip(lead_en, 1200), "src": src_keys},
            "keyPoints": [
                {"fr": f"{n_off} {meta['kind_fr']} nommé(e)s officiellement par Blizzard sur cette fiche.",
                 "en": f"{n_off} {meta['kind_en']} officially named by Blizzard on this page.",
                 "src": [k for k in src_keys if k.startswith("bz-")][:2] or src_keys[:1]},
                {"fr": f"{n_cli} nom(s) supplémentaire(s) relevé(s) dans des données extraites du client, à confirmer, sans zone ni PNJ indiqués.",
                 "en": f"{n_cli} additional name(s) recorded in client-extracted data, to be confirmed, with no zone or NPC given.",
                 "src": src_keys},
                {"fr": f"{n_herit} lié(e)s à l’héritage ; palier de points et défi : non publiés.",
                 "en": f"{n_herit} tied to Legacy; point threshold and challenge: not published.",
                 "src": ["bz-legacy"]},
            ],
            "sections": sections,
            "confirmed": confirmed,
            "pending": pending,
            "dates": dates,
        },
        "history": [{"actor": ACTOR, "note": HIST_NOTE, "at": NOW, "version": 1}],
    }
    return entry, {"id": meta["id"], "n": n, "official": n_off, "client": n_cli, "heritage": n_herit,
                   "title": meta["title"], "slug": meta["slug"], "kind": meta["kind_fr"],
                   "methods": dict(Counter(method_key(r) for r in all_rows)),
                   "samples_official": official[:3],
                   "samples_client": client[:2]}

def forbidden_scan(obj, where=""):
    hits = []
    if isinstance(obj, dict):
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

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pets_client = parse_list_table(SRC / "try-en-haustiere.html", "pet")
    mounts_client = parse_list_table(SRC / "try-en-reittiere.html", "mount")
    def dedupe(rows):
        seen, out, n_dup = set(), [], 0
        for r in rows:
            key = (r["name_en"], r["how_en"], r["faction_en"], r.get("item_id"))
            if key in seen:
                n_dup += 1
                continue
            seen.add(key)
            out.append(r)
        return out, n_dup
    mounts_client, mount_dups = dedupe(mounts_client)
    pets_client, pet_dups = dedupe(pets_client)
    print("client pets", len(pets_client), "dups dropped", pet_dups, "client mounts", len(mounts_client), "dups dropped", mount_dups)

    metas = [
        dict(id="forever-items-toys", kind_fr="jouets", kind_en="toys",
             title={"fr": "Jouets", "en": "Toys"},
             slug={"fr": "jouets", "en": "toys"},
             official=OFFICIAL_TOYS, client=[], sources=SOURCES_COMMON,
             src_keys=["bz-legacy", "bz-pack"]),
        dict(id="forever-items-pets", kind_fr="mascottes", kind_en="companion pets",
             title={"fr": "Mascottes", "en": "Companion pets"},
             slug={"fr": "mascottes", "en": "companion-pets"},
             official=OFFICIAL_PETS, client=pets_client,
             sources=SOURCES_COMMON + [CLIENT_PET],
             src_keys=["bz-legacy", "bz-sub-year", "client-haustiere"]),
        dict(id="forever-items-mounts", kind_fr="montures", kind_en="mounts",
             title={"fr": "Montures", "en": "Mounts"},
             slug={"fr": "montures", "en": "mounts"},
             official=OFFICIAL_MOUNTS, client=mounts_client,
             sources=SOURCES_COMMON + [CLIENT_MOUNT],
             src_keys=["bz-legacy", "bz-pack", "bz-hotfixes", "client-reittiere"]),
    ]
    entries, summary = [], []
    for m in metas:
        entry, info = build_entry(m, m["official"], m["client"], m["sources"], m["src_keys"])
        hits = forbidden_scan(entry)
        if hits:
            raise SystemExit(f"forbidden in {m['id']}: {hits[:3]}")
        path = OUT / f"{m['id']}.json"
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("WROTE", path.name, "n=", info["n"], "off", info["official"], "client", info["client"], "herit", info["heritage"])
        entries.append(entry)
        # lighter samples
        def samp(r):
            return {"fr": r["name_fr"], "en": r["name_en"], "how_fr": r["how_fr"], "herit_fr": r["heritage_fr"],
                    "zone_fr": r["zone_fr"], "npc_fr": r["npc_fr"], "faction_fr": r["faction_fr"],
                    "statut": "confirmé officiel" if r["official"] else "à confirmer"}
        summary.append({**{k: v for k, v in info.items() if k not in {"samples_official", "samples_client"}},
                        "samples": [samp(r) for r in info["samples_official"] + info["samples_client"]]})

    batch = OUT / "batch-collections.json"
    batch.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("BATCH", batch, "bytes", batch.stat().st_size)
    (OUT / "SUMMARY-COLLECTIONS.json").write_text(json.dumps({
        "accessedAt": ACC, "pages": summary,
        "totals": {"toys": summary[0]["n"], "pets": summary[1]["n"], "mounts": summary[2]["n"],
                   "official": sum(s["official"] for s in summary),
                   "client": sum(s["client"] for s in summary),
                   "heritage": sum(s["heritage"] for s in summary)},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # revise JSON for legacy-rewards (not applied)
    recs = json.loads((TREE / "pipeline/runtime/entries.json").read_text())
    bp = deepcopy(next(e for e in recs if e["id"] == "forever-legacy-rewards"))
    section = {
        "id": "listes-jouets-mascottes-montures",
        "title": {"fr": "Listes de jouets, mascottes et montures (brouillons)", "en": "Toy, pet and mount lists (drafts)"},
        "blocks": [{"type": "p",
                    "fr": "Des brouillons, non publiés, rassemblent les jouets, mascottes et montures : d’abord les noms officiels (dont les quatre récompenses d’héritage du lancement), puis les listes extraites du client, à confirmer. Adresses prévues : /fr/objets/jouets/, /fr/objets/mascottes/, /fr/objets/montures/.",
                    "en": "Unpublished drafts gather toys, companion pets and mounts: official names first (including the four launch Legacy rewards), then client-extracted lists, to be confirmed. Planned paths: /en/items/toys/, /en/items/companion-pets/, /en/items/mounts/.",
                    "src": ["bz-legacy"]}],
    }
    secs = bp["article"]["sections"]
    idx = next((i for i, s in enumerate(secs) if s["id"] in {"historique-des-corrections", "limites"}), len(secs))
    # find history or append before last
    hist = next((i for i, s in enumerate(secs) if "historique" in s["id"] or "correction" in s["id"]), None)
    secs.insert(hist if hist is not None else len(secs), section)
    for oid in ["forever-items-toys", "forever-items-pets", "forever-items-mounts"]:
        if oid not in bp["relations"]:
            bp["relations"].append(oid)
    bp["status"] = "draft"
    bp["identityConfirmed"] = False
    bp["updatedAt"] = NOW
    bp["version"] = int(bp.get("version") or 1) + 1
    bp.setdefault("history", []).append({"actor": ACTOR, "note": HIST_NOTE, "at": NOW, "version": bp["version"]})
    rp = OUT / "forever-legacy-rewards.revise.json"
    hits = forbidden_scan(bp)
    if hits:
        raise SystemExit(f"forbidden in legacy revise: {hits[:3]}")
    rp.write_text(json.dumps(bp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("REVISE ready", rp, "v", bp["version"], "(not applied)")

if __name__ == "__main__":
    main()
