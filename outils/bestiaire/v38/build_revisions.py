#!/usr/bin/env python3
"""t359u — drop « à confirmer » on fields found in Forever client files (build 1.60.1.70862)."""
from __future__ import annotations
import json, re, copy
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/workspace/wowkipedia-v21-elite/bestiaire")
ENTRIES = ROOT / "test-tree-v38/pipeline/runtime/entries.json"
OUT = ROOT / "v38-t359u/revisions"
STATS = ROOT / "v38-t359u/revision-stats.json"
BUILD = "1.60.1.70862"
GAME_FR = "données du jeu"
GAME_EN = "game data"
GAME_FR_FULL = f"données du jeu (client {BUILD})"
GAME_EN_FULL = f"game data (client {BUILD})"
HIST_FR = (
    f"13 novembre 2026 : « à confirmer » retiré des faits trouvés dans les fichiers du jeu "
    f"(client {BUILD}), décision t359u. L’obtention « inconnu », les zones non indiquées, "
    f"les sources sans tampon de build et les valeurs seulement déduites restent à confirmer. "
    f"Ce n’est pas une confirmation officielle de Blizzard, ni une mise en ligne."
)
HIST_EN = (
    f"13 November 2026: “to be confirmed” removed from facts found in the game files "
    f"(client {BUILD}), t359u decision. Acquisition marked “unknown”, zones not given, "
    f"sources without a build stamp, and inferred values remain to be confirmed. "
    f"This is not an official Blizzard confirmation, and not a publication."
)
HIST_FISH_FR = (
    f"13 novembre 2026 : la mention « à confirmer » est conservée sur cette fiche. "
    f"Le guide Pêche consulté n’est pas tamponné du client {BUILD} (contrairement aux autres "
    f"guides de métier). Décision t359u. Pas une mise en ligne."
)
HIST_FISH_EN = (
    f"13 November 2026: the “to be confirmed” mark is kept on this page. "
    f"The Fishing guide consulted is not stamped with client {BUILD} (unlike the other "
    f"profession guides). t359u decision. Not a publication."
)
HIST_TOYS_FR = (
    "13 novembre 2026 : la mention « à confirmer » est retirée. Cette fiche ne contient que "
    "les jouets nommés par Blizzard ; aucune liste client de jouets n’a été trouvée. "
    "Décision t359u. Pas une mise en ligne."
)
HIST_TOYS_EN = (
    "13 November 2026: the “to be confirmed” mark is removed. This page only contains toys "
    "named by Blizzard; no client-extracted toy list was found. t359u decision. Not a publication."
)
HIST_LEGACY_FR = (
    f"13 novembre 2026 : le renvoi vers les listes de jouets, mascottes et montures ne présente "
    f"plus les noms issus des fichiers du jeu comme « à confirmer » par principe ; les quatre "
    f"récompenses officielles restent officielles. Décision t359u. Pas une mise en ligne."
)
HIST_LEGACY_EN = (
    "13 November 2026: the link to the toy, companion-pet and mount lists no longer treats "
    "names from the game files as “to be confirmed” by default; the four official rewards stay "
    "official. t359u decision. Not a publication."
)

# Profession fishing recipes: guide not stamped.
KEEP_PAGE_UNCONFIRMED = {"forever-professions-recipes-fishing"}
# Official-only toys page (no client list).
TOYS_ID = "forever-items-toys"
LEGACY_ID = "forever-legacy-rewards"
BLUEPRINTS_ID = "forever-professions-blueprints"

# Client sources to stamp (70862 extraction). Fishing guides excluded.
UNSTAMPED_KEYS = {
    "client-guide-angeln-fr",
    "client-guide-angeln-en",
    "client-guide-angeln",
}

stats = {
    "pages_revised": [],
    "pages_lose_entry_mark": [],
    "pages_keep_entry_mark": [],
    "statut_cells_to_game_data": 0,
    "statut_cells_game_data_obtention_unconfirmed": 0,
    "statut_cells_kept_unconfirmed": 0,
    "statut_cells_official_kept": 0,
    "sources_stamped": 0,
    "sources_kept_unconfirmed": 0,
    "why_keep": defaultdict(list),
}

def is_unstamped_source(src: dict) -> bool:
    key = src.get("key") or ""
    if key in UNSTAMPED_KEYS or key.startswith("client-guide-angeln"):
        return True
    url = src.get("url") or ""
    if "/berufe/angeln" in url:
        return True
    return False

def is_client_source(src: dict) -> bool:
    url = (src.get("url") or "").lower()
    key = src.get("key") or ""
    return "eternadex.com" in url or key.startswith("client-")

def clean_source_title(title: str) -> str:
    if not title:
        return title
    t = title
    t = re.sub(r",?\s*à confirmer\)?", "", t)
    t = re.sub(r",?\s*to be confirmed\)?", "", t, flags=re.I)
    t = re.sub(r"\s*\(à confirmer\)", "", t)
    t = re.sub(r"\s*\(to be confirmed\)", "", t, flags=re.I)
    t = re.sub(r"données extraites du client", "données du jeu", t)
    t = re.sub(r"client-extracted data", "game data", t, flags=re.I)
    t = re.sub(r"[ \t]+", " ", t).strip(" ,;—-")
    # tidy leftover empty parens
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"\s+([,.;])", r"\1", t)
    return t.strip()

def stamp_sources(entry: dict) -> None:
    for src in entry.get("sources") or []:
        if not is_client_source(src):
            continue
        if is_unstamped_source(src):
            src["verification"] = "à confirmer"
            stats["sources_kept_unconfirmed"] += 1
            stats["why_keep"]["source_unstamped_fishing_guide"].append(src.get("key"))
            continue
        src["clientBuild"] = BUILD
        src["verification"] = "données du jeu"
        if isinstance(src.get("title"), str):
            src["title"] = clean_source_title(src["title"])
            # mention the build once if missing
            if BUILD not in src["title"]:
                # keep titles reasonably short
                if src.get("language") == "fr" or (isinstance(src.get("title"), str) and "données" in src["title"].lower()):
                    if "client" not in src["title"]:
                        src["title"] = src["title"].rstrip(" .") + f" (client {BUILD})"
                else:
                    if "client" not in src["title"].lower():
                        src["title"] = src["title"].rstrip(" .") + f" (client {BUILD})"
        stats["sources_stamped"] += 1

# --- prose replacements for stamped pages (not history) ---
# Longer / more specific first.
PROSE = [
    (
        "Tout le contenu de cette liste est à confirmer : ce n’est pas une publication officielle de Blizzard.",
        f"Les noms, les compétences et l’obtention indiquée (hors « inconnu ») viennent des fichiers du jeu (client {BUILD}). Ce n’est pas une publication officielle de Blizzard. L’obtention « inconnu » reste à confirmer.",
    ),
    (
        "Everything in this list is to be confirmed: it is not an official Blizzard publication.",
        f"Names, skills and given acquisition methods (other than “unknown”) come from the game files (client {BUILD}). This is not an official Blizzard publication. An acquisition marked “unknown” remains to be confirmed.",
    ),
    (
        "Les lignes ci-dessous viennent de données extraites du client et restent à confirmer.",
        f"Les noms et les compétences ci-dessous viennent des fichiers du jeu (client {BUILD}). L’obtention « inconnu » reste à confirmer.",
    ),
    (
        "The rows below come from client-extracted data and remain to be confirmed.",
        f"The names and skills below come from the game files (client {BUILD}). An acquisition marked “unknown” remains to be confirmed.",
    ),
    (
        "Les autres lignes viennent de données extraites du client (consultées le 12 novembre 2026) et restent à confirmer.",
        f"Les autres lignes viennent des fichiers du jeu (client {BUILD}, consultés le 12 novembre 2026) : les noms, identifiants et prix indiqués sont des données du jeu ; l’obtention, la zone et le PNJ, s’ils ne sont pas indiqués, restent à confirmer.",
    ),
    (
        "Other rows come from client-extracted data (consulted on 12 November 2026) and remain to be confirmed.",
        f"Other rows come from the game files (client {BUILD}, consulted on 12 November 2026): names, identifiers and given prices are game data; acquisition, zone and NPC, when not given, remain to be confirmed.",
    ),
    (
        "Chaque ligne est à confirmer.",
        "Les noms et les compétences requises viennent des fichiers du jeu. L’obtention indiquée « inconnu » reste à confirmer.",
    ),
    (
        "Every row is to be confirmed.",
        "Names and required skills come from the game files. An acquisition marked “unknown” remains to be confirmed.",
    ),
    (
        "toutes à confirmer (données extraites du client, 12 novembre 2026)",
        f"d’après les fichiers du jeu (client {BUILD}, 12 novembre 2026) ; l’obtention « inconnu » reste à confirmer",
    ),
    (
        "all to be confirmed (client-extracted data, 12 November 2026)",
        f"from the game files (client {BUILD}, 12 November 2026); acquisition marked “unknown” remains to be confirmed",
    ),
    (
        "Obtention indiquée (à confirmer) :",
        "Obtention indiquée dans les fichiers du jeu :",
    ),
    (
        "Acquisition given (to be confirmed):",
        "Acquisition given in the game files:",
    ),
    (
        "Répartition (à confirmer) :",
        "Répartition dans les fichiers du jeu :",
    ),
    (
        "Breakdown (to be confirmed):",
        "Breakdown in the game files:",
    ),
    (
        "relevées dans des données extraites du client le 12 novembre 2026",
        f"relevées dans les fichiers du jeu (client {BUILD}) le 12 novembre 2026",
    ),
    (
        "relevées dans des données extraites du client (consultées le 12 novembre 2026)",
        f"relevées dans les fichiers du jeu (client {BUILD}, consultés le 12 novembre 2026)",
    ),
    (
        "recorded in client-extracted data on 12 November 2026",
        f"recorded in the game files (client {BUILD}) on 12 November 2026",
    ),
    (
        "recorded in client-extracted data (consulted on 12 November 2026)",
        f"recorded in the game files (client {BUILD}, consulted on 12 November 2026)",
    ),
    (
        "Toutes les lignes de ces listes restent à confirmer.",
        "Les noms et compétences de ces listes viennent des fichiers du jeu ; l’obtention « inconnu » reste à confirmer.",
    ),
    (
        "Every row on those lists remains to be confirmed.",
        "Names and skills on those lists come from the game files; acquisition marked “unknown” remains to be confirmed.",
    ),
    (
        "Tout ce qui suit reste à confirmer.",
        f"Les monstre et zones ci-dessous viennent des fiches item des fichiers du jeu (client {BUILD}). Les taux de butin, non indiqués, restent non remplis. Ce n’est pas une confirmation officielle de Blizzard.",
    ),
    (
        "Everything that follows remains to be confirmed.",
        f"The monsters and zones below come from the item pages in the game files (client {BUILD}). Drop rates, which were not given, are left blank. This is not an official Blizzard confirmation.",
    ),
    (
        "Une section à confirmer regroupe 55 recettes à butin, par zone, d’après des données extraites du client (consultation du 12 novembre 2026).",
        f"Une section reprend 55 recettes à butin, par zone, d’après les fichiers du jeu (client {BUILD}, consultation du 12 novembre 2026). Les taux de butin, non indiqués, ne sont pas remplis.",
    ),
    (
        "données extraites du client, à confirmer",
        GAME_FR_FULL,
    ),
    (
        "client-extracted data, to be confirmed",
        GAME_EN_FULL,
    ),
    (
        "données extraites du client",
        GAME_FR_FULL,
    ),
    (
        "client-extracted data",
        GAME_EN_FULL,
    ),
    # bestiary
    (
        "Chaque ligne issue de la liste de PNJ est à confirmer.",
        f"Chaque ligne issue de la liste de PNJ vient des fichiers du jeu (client {BUILD}). Ce n’est pas une confirmation officielle de Blizzard.",
    ),
    (
        "Every row from the NPC list is to be confirmed.",
        f"Every row from the NPC list comes from the game files (client {BUILD}). This is not an official Blizzard confirmation.",
    ),
    (
        "chaque ligne de cette liste restant à confirmer",
        f"chaque ligne de cette liste venant des fichiers du jeu (client {BUILD})",
    ),
    (
        "each row from that list remaining to be confirmed",
        f"each row from that list coming from the game files (client {BUILD})",
    ),
    (
        "tous à confirmer",
        f"tous issus des fichiers du jeu (client {BUILD})",
    ),
    (
        "all to be confirmed",
        f"all from the game files (client {BUILD})",
    ),
    (
        "dans la liste consultée, à confirmer",
        f"dans la liste consultée (données du jeu, client {BUILD})",
    ),
    (
        "in the list consulted, to be confirmed",
        f"in the list consulted (game data, client {BUILD})",
    ),
    (
        "liste de jeu (à confirmer)",
        f"liste de jeu (données du jeu, client {BUILD})",
    ),
    (
        "game list (to be confirmed)",
        f"game list (game data, client {BUILD})",
    ),
    (
        "liste Forever (à confirmer)",
        f"liste Forever (données du jeu, client {BUILD})",
    ),
    (
        "Forever list (to be confirmed)",
        f"Forever list (game data, client {BUILD})",
    ),
    (
        "liste de PNJ Forever (à confirmer)",
        f"liste de PNJ Forever (données du jeu, client {BUILD})",
    ),
    (
        "Forever NPC list (to be confirmed)",
        f"Forever NPC list (game data, client {BUILD})",
    ),
    (
        "(liste du 12/11/2026, à confirmer)",
        f"(liste du 12/11/2026, données du jeu, client {BUILD})",
    ),
    (
        "(list of 12 November 2026, to be confirmed)",
        f"(list of 12 November 2026, game data, client {BUILD})",
    ),
    (
        "dans la liste de 3 284 PNJ (à confirmer)",
        f"dans la liste de 3 284 PNJ (données du jeu, client {BUILD})",
    ),
    (
        "in the 3,284-NPC list (to be confirmed)",
        f"in the 3,284-NPC list (game data, client {BUILD})",
    ),
    (
        "le nom anglais est conservé, à confirmer",
        "le nom anglais est conservé (pas de traduction officielle)",
    ),
    (
        "the English name is kept, to be confirmed",
        "the English name is kept (no official translation)",
    ),
    (
        "déjà documentées (à confirmer)",
        "déjà documentées (données du jeu)",
    ),
    (
        "already documented (to be confirmed)",
        "already documented (game data)",
    ),
    # collections leftover
    (
        "puis les noms relevés dans des données extraites du client le 12 novembre 2026, à confirmer",
        f"puis les noms relevés dans les fichiers du jeu (client {BUILD}) le 12 novembre 2026 ; l’obtention, s’il n’est pas indiqué, reste à confirmer",
    ),
    (
        "then names recorded in client-extracted data on 12 November 2026, to be confirmed",
        f"then names recorded in the game files (client {BUILD}) on 12 November 2026; acquisition, when not given, remains to be confirmed",
    ),
    (
        "relevé(s) dans des données extraites du client, à confirmer, sans zone ni PNJ indiqués",
        f"relevé(s) dans les fichiers du jeu (client {BUILD}), sans zone ni PNJ indiqués ; l’obtention reste à confirmer lorsqu’elle n’est pas indiquée",
    ),
    (
        "recorded in client-extracted data, to be confirmed, with no zone or NPC given",
        f"recorded in the game files (client {BUILD}), with no zone or NPC given; acquisition remains to be confirmed when it is not given",
    ),
    # fish-style leftover in captions
    (
        ", à confirmer",
        "",  # only as last-resort on leftover caption tails — applied carefully
    ),
]

# The last empty replacement is dangerous; handle captions separately, do not use generic strip of ", à confirmer" on all prose.
PROSE = [p for p in PROSE if p[1] != ""]

# leftover generic in titles/captions after specific ones
CAPTION_EXTRA = [
    ("à confirmer (12/11/2026)", f"données du jeu, client {BUILD} (12/11/2026)"),
    ("to be confirmed (12 Nov 2026)", f"game data, client {BUILD} (12 Nov 2026)"),
    ("to be confirmed (12 November 2026)", f"game data, client {BUILD} (12 November 2026)"),
    ("(à confirmer)", f"(données du jeu, client {BUILD})"),
    ("(to be confirmed)", f"(game data, client {BUILD})"),
]

SECTION_TITLE_EXTRA = [
    ("Vendeurs à confirmer (données extraites du client)", f"Vendeurs (données du jeu, client {BUILD})"),
    ("Vendors to be confirmed (client-extracted data)", f"Vendors (game data, client {BUILD})"),
    ("Recettes à butin par zone (à confirmer)", f"Recettes à butin par zone (données du jeu, client {BUILD})"),
    ("Lootable recipes by zone (to be confirmed)", f"Lootable recipes by zone (game data, client {BUILD})"),
    ("Listes par métier (à confirmer)", f"Listes par métier (données du jeu, client {BUILD})"),
    ("Lists by profession (to be confirmed)", f"Lists by profession (game data, client {BUILD})"),
    (" recettes à confirmer", " recettes (données du jeu)"),
    (" recette à confirmer", " recette (données du jeu)"),
    (" recipes to be confirmed", " recipes (game data)"),
    (" recipe to be confirmed", " recipe (game data)"),
]

def apply_pairs(text: str, pairs) -> str:
    if not isinstance(text, str):
        return text
    out = text
    for a, b in pairs:
        if a in out:
            out = out.replace(a, b)
    return out

def rewrite_prose(text: str) -> str:
    if not isinstance(text, str):
        return text
    out = apply_pairs(text, PROSE)
    # avoid double build stamps
    out = re.sub(rf"\(client {re.escape(BUILD)}\) \(client {re.escape(BUILD)}\)", f"(client {BUILD})", out)
    out = re.sub(rf"client {re.escape(BUILD)}, client {re.escape(BUILD)}", f"client {BUILD}", out)
    out = re.sub(rf"données du jeu \(client {re.escape(BUILD)}\) \(client {re.escape(BUILD)}\)", GAME_FR_FULL, out)
    return out

def is_history_section(section: dict) -> bool:
    return (section or {}).get("id") == "historique-des-corrections"

def walk_rewrite(obj, skip_history=False, in_history=False):
    if isinstance(obj, dict):
        if obj.get("id") == "historique-des-corrections":
            in_history = True
        for k, v in obj.items():
            if k in ("history", "importMeta", "review", "sources", "id", "slug"):
                continue
            obj[k] = walk_rewrite(v, skip_history, in_history)
        return obj
    if isinstance(obj, list):
        return [walk_rewrite(v, skip_history, in_history) for v in obj]
    if isinstance(obj, str) and not in_history:
        return rewrite_prose(obj)
    return obj

def rewrite_section_titles(entry: dict):
    art = entry.get("article") or {}
    for sec in art.get("sections") or []:
        if is_history_section(sec):
            continue
        title = sec.get("title") or {}
        for lang in ("fr", "en"):
            if lang in title:
                t = apply_pairs(rewrite_prose(title[lang]), SECTION_TITLE_EXTRA)
                if len(t) > 200:
                    # shorten
                    t = t.replace(f", client {BUILD}", "").replace(f"client {BUILD}", "jeu" if lang=="fr" else "game")
                title[lang] = t

def rewrite_captions(entry: dict):
    art = entry.get("article") or {}
    for sec in art.get("sections") or []:
        if is_history_section(sec):
            continue
        for b in sec.get("blocks") or []:
            cap = b.get("caption")
            if not isinstance(cap, dict):
                continue
            for lang in ("fr", "en"):
                if lang in cap:
                    t = apply_pairs(rewrite_prose(cap[lang]), CAPTION_EXTRA)
                    if len(t) > 300:
                        t = t.replace(f" (client {BUILD})", "")
                    cap[lang] = t

OFFICIAL_STATUT_PREFIXES = (
    "confirmé officiel",
    "officiel confirmé",
    "official",
    "officially confirmed",
)

def cell_fr(cell):
    if isinstance(cell, dict):
        return cell.get("fr") or ""
    return str(cell or "")

def set_cell(cell, fr, en):
    if isinstance(cell, dict):
        cell["fr"] = fr
        cell["en"] = en
        return cell
    return {"fr": fr, "en": en}

def looks_unknown_obtention(fr: str) -> bool:
    s = (fr or "").strip().lower()
    return s.startswith("inconnu") or s == "unknown" or s.startswith("unknown")

def looks_unconfirmed_statut(fr: str) -> bool:
    s = (fr or "").strip().lower()
    return s.startswith("à confirmer") or s.startswith("to be confirmed")

def looks_official_statut(fr: str) -> bool:
    s = (fr or "").strip().lower()
    return any(s.startswith(p) for p in OFFICIAL_STATUT_PREFIXES)

def update_tables(entry: dict, page_keep_unconfirmed: bool, kind: str):
    art = entry.get("article") or {}
    for sec in art.get("sections") or []:
        for b in sec.get("blocks") or []:
            if b.get("type") != "table":
                continue
            head = b.get("head") or []
            def col(*names):
                for i, h in enumerate(head):
                    label = (h.get("fr") if isinstance(h, dict) else h) or ""
                    label_en = (h.get("en") if isinstance(h, dict) else "") or ""
                    blob = f"{label} {label_en}".lower()
                    if any(n.lower() in blob for n in names):
                        return i
                return None
            i_stat = col("Statut", "Status")
            i_obt = col("Obtention", "How obtained", "Acquisition", "Méthode")
            if i_stat is None:
                continue
            for row in b.get("rows") or []:
                if i_stat >= len(row):
                    continue
                fr = cell_fr(row[i_stat])
                obt = cell_fr(row[i_obt]) if i_obt is not None and i_obt < len(row) else ""
                if looks_official_statut(fr):
                    stats["statut_cells_official_kept"] += 1
                    continue
                if page_keep_unconfirmed:
                    # keep à confirmer (fishing recipes)
                    stats["statut_cells_kept_unconfirmed"] += 1
                    continue
                if not looks_unconfirmed_statut(fr) and GAME_FR not in fr.lower() and "données du jeu" not in fr.lower():
                    # unexpected statut, leave it
                    continue
                # Fish: keep explanatory tail, change prefix
                if kind == "fish" and (fr.startswith("à confirmer") or fr.startswith("À confirmer")):
                    rest = re.sub(r"^[Àà] confirmer(\s*—\s*)?", "", fr).strip()
                    rest_en = cell_fr({"fr": "", "en": row[i_stat].get("en") if isinstance(row[i_stat], dict) else ""})
                    if isinstance(row[i_stat], dict):
                        rest_en = re.sub(r"^(to be confirmed)(\s*—\s*)?", "", row[i_stat].get("en") or "", flags=re.I).strip()
                    fr_new = f"données du jeu — {rest}" if rest else "données du jeu"
                    en_new = f"game data — {rest_en}" if rest_en else "game data"
                    # obtention/zone already mentioned in many tails
                    if len(fr_new) > 400:
                        fr_new = fr_new[:397] + "…"
                    if len(en_new) > 400:
                        en_new = en_new[:397] + "…"
                    row[i_stat] = set_cell(row[i_stat], fr_new, en_new)
                    if "non indiqué" in rest.lower() or "n’est pas indiqué" in rest or "pas indiqué" in rest:
                        stats["statut_cells_game_data_obtention_unconfirmed"] += 1
                    else:
                        stats["statut_cells_to_game_data"] += 1
                    continue
                if looks_unknown_obtention(obt):
                    row[i_stat] = set_cell(
                        row[i_stat],
                        "données du jeu — obtention à confirmer",
                        "game data — acquisition to be confirmed",
                    )
                    stats["statut_cells_game_data_obtention_unconfirmed"] += 1
                else:
                    # unlocated bestiary: zone not given
                    if kind == "unlocated":
                        row[i_stat] = set_cell(
                            row[i_stat],
                            "données du jeu — zone non indiquée",
                            "game data — zone not given",
                        )
                        stats["statut_cells_game_data_obtention_unconfirmed"] += 1
                    else:
                        row[i_stat] = set_cell(row[i_stat], "données du jeu", "game data")
                        stats["statut_cells_to_game_data"] += 1
            # also clean "à confirmer" inside obtention price notes (pets/mounts)
            if i_obt is not None:
                for row in b.get("rows") or []:
                    if i_obt >= len(row):
                        continue
                    cell = row[i_obt]
                    if not isinstance(cell, dict):
                        continue
                    for lang, needle, repl in (
                        ("fr", " (à confirmer)", ""),
                        ("en", " (to be confirmed)", ""),
                    ):
                        if needle in (cell.get(lang) or ""):
                            cell[lang] = cell[lang].replace(needle, repl)

def append_history(entry: dict, fr: str, en: str, src_keys: list[str] | None):
    art = entry.get("article") or {}
    sec = next((s for s in art.get("sections") or [] if s.get("id") == "historique-des-corrections"), None)
    if not sec:
        # some pages may use a different id
        for s in art.get("sections") or []:
            title = (s.get("title") or {}).get("fr") or ""
            if "historique" in title.lower() or "correction" in title.lower():
                sec = s
                break
    item = {"fr": fr, "en": en}
    if src_keys:
        item["src"] = src_keys
    if not sec:
        art.setdefault("sections", []).append({
            "id": "historique-des-corrections",
            "title": {"fr": "Historique des corrections", "en": "Correction history"},
            "blocks": [{"type": "list", "items": [item]}],
        })
        return
    # find list block
    for b in sec.get("blocks") or []:
        if b.get("type") == "list":
            b.setdefault("items", []).append(item)
            return
    sec.setdefault("blocks", []).append({"type": "list", "items": [item]})

def client_src_keys(entry: dict) -> list[str]:
    keys = []
    for s in entry.get("sources") or []:
        if is_client_source(s) and not is_unstamped_source(s):
            k = s.get("key") or ""
            base = re.sub(r"-(fr|en)$", "", k)
            if base and base not in keys:
                keys.append(base)
    return keys[:8]

def rewrite_legacy(entry: dict):
    art = entry.get("article") or {}
    for sec in art.get("sections") or []:
        for b in sec.get("blocks") or []:
            if not isinstance(b, dict):
                continue
            if "données extraites du client, à confirmer" in (b.get("fr") or ""):
                b["fr"] = b["fr"].replace(
                    "puis les noms relevés dans des données extraites du client, à confirmer.",
                    f"puis les noms relevés dans les fichiers du jeu (client {BUILD}) ; l’obtention, quand elle n’est pas indiquée, reste à confirmer.",
                )
            if "client-extracted data, to be confirmed" in (b.get("en") or ""):
                b["en"] = b["en"].replace(
                    "then names recorded in client-extracted data, to be confirmed.",
                    f"then names recorded in the game files (client {BUILD}); acquisition, when not given, remains to be confirmed.",
                )

def rewrite_toys(entry: dict):
    # Official only. Remove false client-list claims.
    entry.pop("verification", None)
    desc = entry.get("description") or {}
    desc["fr"] = (
        "Liste des 2 jouets nommés par Blizzard pour le lancement. Zone, PNJ et palier d’héritage "
        "ne sont remplis que lorsqu’une source officielle le dit. Aucune liste client de jouets n’a été trouvée. "
        "Blizzard n’a pas publié de liste complète."
    )
    desc["en"] = (
        "List of the 2 toys named by Blizzard at launch. Zone, NPC and Legacy threshold are filled "
        "only when an official source states them. No client-extracted toy list was found. "
        "Blizzard has not published a complete list."
    )
    art = entry.get("article") or {}
    lead = art.get("lead") or {}
    lead["fr"] = (
        "Blizzard a nommé pour le lancement un petit nombre de jouets (héritage, packs boutique, et le cas échéant un bonus d’abonnement). "
        "Le détail (zone, PNJ, palier d’héritage, prix d’achat en jeu) n’est souvent pas publié. "
        "Cette fiche ne reprend que les noms officiels. Aucune liste de jouets n’a été trouvée dans les fichiers du jeu consultés."
    )
    lead["en"] = (
        "Blizzard has named a small number of toys at launch (Legacy, shop packs, and where relevant a subscription bonus). "
        "Details (zone, NPC, Legacy threshold, in-game purchase price) are often unpublished. "
        "This page only keeps the official names. No toy list was found in the game files consulted."
    )
    # key points: drop "0 additional client names à confirmer"
    kps = art.get("keyPoints") or []
    new_kps = []
    for k in kps:
        fr = k.get("fr") or ""
        if "nom(s) supplémentaire(s)" in fr or "additional name" in (k.get("en") or ""):
            continue
        new_kps.append(k)
    if len(new_kps) < 2:
        new_kps.append({
            "fr": "Aucune liste client de jouets n’a été trouvée (pas de rubrique équivalente aux mascottes et montures).",
            "en": "No client-extracted toy list was found (no section equivalent to the pet and mount lists).",
        })
    art["keyPoints"] = new_kps
    # lire-cette-liste paragraph: remove "other rows from client"
    for sec in art.get("sections") or []:
        if is_history_section(sec):
            continue
        for b in sec.get("blocks") or []:
            if b.get("type") == "p":
                if "restent à confirmer" in (b.get("fr") or "") or "extracted" in (b.get("en") or ""):
                    b["fr"] = (
                        "Les lignes « confirmé officiel » viennent uniquement d’articles Blizzard cités. "
                        "Aucune liste de jouets n’a été trouvée dans les fichiers du jeu consultés. "
                        "Quand la zone, le PNJ ou le palier d’héritage n’est pas publié, la cellule le dit. "
                        "Aucun tarif, vendeur ou lieu Classic n’est ajouté de mémoire."
                    )
                    b["en"] = (
                        "Rows marked “officially confirmed” come only from the cited Blizzard articles. "
                        "No toy list was found in the game files consulted. "
                        "When zone, NPC or Legacy threshold is not published, the cell says so. "
                        "No Classic vendor, price or location is added from memory."
                    )
    # pending: keep official unpublished details; the "client list / not known yet" items can stay if still true
    # PEND about no client list is still true. The "for rows from client data" can be removed if no such rows.
    pending = []
    for p in art.get("pending") or []:
        fr = p.get("fr") or ""
        if "Pour les lignes issues des données du client" in fr:
            continue
        if "la liste « à confirmer » reprend" in fr:
            continue
        pending.append(p)
    art["pending"] = pending or art.get("pending")

def rewrite_collections_lead(entry: dict):
    """Pets / mounts: official first, game-file names, obtention often unknown."""
    art = entry.get("article") or {}
    lead = art.get("lead") or {}
    for lang, old, new in (
        (
            "fr",
            "Une liste plus longue apparaît dans des données extraites du client ; leur présence dans ces fichiers ne prouve pas qu’on puisse les obtenir en jeu. Tous ces ajouts restent à confirmer.",
            f"Une liste plus longue apparaît dans les fichiers du jeu (client {BUILD}). Les noms, identifiants et prix éventuellement indiqués viennent de ces fichiers ; l’obtention, la zone et le PNJ, souvent non indiqués, restent à confirmer. La présence dans ces fichiers ne prouve pas qu’on puisse les obtenir en jeu. Ce n’est pas une confirmation officielle de Blizzard.",
        ),
        (
            "en",
            "A longer list appears in client-extracted data; presence in those files does not prove the item can be obtained in game. All such additions remain to be confirmed.",
            f"A longer list appears in the game files (client {BUILD}). Names, identifiers and any given prices come from those files; acquisition, zone and NPC, often not given, remain to be confirmed. Presence in those files does not prove the item can be obtained in game. This is not an official Blizzard confirmation.",
        ),
    ):
        if old in (lead.get(lang) or ""):
            lead[lang] = lead[lang].replace(old, new)
    # pending wording: list « à confirmer » → list from game files, obtention still unconfirmed
    for p in art.get("pending") or []:
        if "la liste « à confirmer » reprend" in (p.get("fr") or ""):
            p["fr"] = (
                "Blizzard a indiqué que des données du client ne sont pas destinées à Forever ; "
                "cette liste reprend uniquement ce que la source consultée range encore pour Forever. "
                "Les noms viennent des fichiers du jeu ; l’obtention, souvent non indiquée, reste à confirmer. "
                "Sans vérification en jeu."
            )
            p["en"] = (
                "Blizzard has said that some client data is not meant for Forever; "
                "this list keeps only what the consulted source still files for Forever. "
                "Names come from the game files; acquisition, often not given, remains to be confirmed. "
                "Without in-game checks."
            )

def kind_of(eid: str) -> str:
    if eid == "forever-professions-fish":
        return "fish"
    if eid == "forever-bestiary-unlocated":
        return "unlocated"
    if eid.startswith("forever-bestiary"):
        return "bestiary"
    if eid.startswith("forever-items-"):
        return "collection"
    if eid.startswith("forever-professions-recipes-"):
        return "recipes"
    if eid == BLUEPRINTS_ID:
        return "blueprints"
    if eid == LEGACY_ID:
        return "legacy"
    return "other"

def check_lengths(entry: dict, issues: list):
    art = entry.get("article") or {}
    lead = art.get("lead") or {}
    for lang in ("fr", "en"):
        if lead.get(lang) and len(lead[lang]) > 1200:
            issues.append(f"{entry['id']} lead.{lang} {len(lead[lang])}>1200")
    for i, k in enumerate(art.get("keyPoints") or []):
        for lang in ("fr", "en"):
            if k.get(lang) and len(k[lang]) > 2400:
                issues.append(f"{entry['id']} key[{i}].{lang} {len(k[lang])}>2400")
    for s in art.get("sections") or []:
        title = s.get("title") or {}
        for lang in ("fr", "en"):
            if title.get(lang) and len(title[lang]) > 200:
                issues.append(f"{entry['id']} section {s.get('id')} title.{lang} {len(title[lang])}>200")
        for b in s.get("blocks") or []:
            cap = b.get("caption")
            if isinstance(cap, dict):
                for lang in ("fr", "en"):
                    if cap.get(lang) and len(cap[lang]) > 300:
                        issues.append(f"{entry['id']} caption {s.get('id')} {lang} {len(cap[lang])}>300")
            if b.get("type") == "table":
                for ri, row in enumerate(b.get("rows") or []):
                    for ci, cell in enumerate(row):
                        if isinstance(cell, dict):
                            for lang in ("fr", "en"):
                                if cell.get(lang) and len(cell[lang]) > 400:
                                    issues.append(f"{entry['id']} cell {s.get('id')} r{ri}c{ci}.{lang} {len(cell[lang])}>400")

def transform(entry: dict) -> dict:
    e = copy.deepcopy(entry)
    # drop review so incoming is clean; reviseRecord will anyway
    e.pop("review", None)
    eid = e["id"]
    kind = kind_of(eid)
    keep = eid in KEEP_PAGE_UNCONFIRMED
    stamp_sources(e)

    if eid == TOYS_ID:
        rewrite_toys(e)
        append_history(e, HIST_TOYS_FR, HIST_TOYS_EN, ["bz-legacy", "bz-pack"])
        e.pop("verification", None)
        stats["pages_lose_entry_mark"].append(eid)
        stats["why_keep"]["toys_official_only_no_client_list"]  # just a note
        return e

    if eid == LEGACY_ID:
        rewrite_legacy(e)
        append_history(e, HIST_LEGACY_FR, HIST_LEGACY_EN, ["bz-legacy"])
        # stays officiel confirmé
        stats["pages_lose_entry_mark"].append(eid + " (field wording only; entry stays officiel confirmé)")
        return e

    if keep:
        # Clarify in lead why the mark stays, without dropping it.
        lead = (e.get("article") or {}).get("lead") or {}
        note_fr = f" Le guide Pêche consulté n’est pas tamponné du client {BUILD} : la mention « à confirmer » est donc conservée."
        note_en = f" The Fishing guide consulted is not stamped with client {BUILD}, so the “to be confirmed” mark is kept."
        if lead.get("fr") and note_fr.strip() not in lead["fr"]:
            if len(lead["fr"]) + len(note_fr) <= 1200:
                lead["fr"] = lead["fr"].rstrip() + note_fr
        if lead.get("en") and note_en.strip() not in lead["en"]:
            if len(lead["en"]) + len(note_en) <= 1200:
                lead["en"] = lead["en"].rstrip() + note_en
        e["verification"] = "à confirmer"
        append_history(e, HIST_FISH_FR, HIST_FISH_EN, ["client-guide-angeln", "bz-24303313"])
        stats["pages_keep_entry_mark"].append(eid)
        stats["why_keep"]["unstamped_fishing_guide"].append(eid)
        update_tables(e, True, "recipes")
        return e

    # stamped pages
    walk_rewrite(e.get("article"))
    walk_rewrite(e.get("description"))
    rewrite_section_titles(e)
    rewrite_captions(e)
    if kind == "collection":
        rewrite_collections_lead(e)
    update_tables(e, False, kind)
    e["verification"] = "données du jeu"
    append_history(e, HIST_FR, HIST_EN, client_src_keys(e) or None)
    stats["pages_lose_entry_mark"].append(eid)
    return e

def remaining_marks(entry: dict) -> list[str]:
    hits = []
    def walk(o, path, in_hist=False):
        if isinstance(o, dict):
            if o.get("id") == "historique-des-corrections":
                in_hist = True
            for k, v in o.items():
                if k in ("history", "importMeta", "review"):
                    continue
                walk(v, f"{path}.{k}", in_hist)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]", in_hist)
        elif isinstance(o, str) and not in_hist:
            if re.search(r"à confirmer|to be confirmed", o, re.I):
                hits.append((path, o[:180]))
    walk(entry.get("article"), "article")
    walk(entry.get("description"), "description")
    if entry.get("verification") == "à confirmer":
        hits.append(("verification", "à confirmer"))
    return hits

def main():
    records = json.loads(ENTRIES.read_text())
    target_ids = [e["id"] for e in records if e.get("verification") == "à confirmer"]
    target_ids += ["forever-professions-blueprints", "forever-legacy-rewards"]
    # unique preserve order
    seen = set()
    ids = []
    for i in target_ids:
        if i not in seen:
            ids.append(i)
            seen.add(i)
    by = {e["id"]: e for e in records}
    issues = []
    remaining = {}
    OUT.mkdir(parents=True, exist_ok=True)
    for eid in ids:
        src = by[eid]
        out = transform(src)
        check_lengths(out, issues)
        remaining[eid] = remaining_marks(out)
        path = OUT / f"{eid}.json"
        # incoming for revise: full entry
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
        stats["pages_revised"].append(eid)
        print(f"wrote {path.name}  ver={out.get('verification')}  remain={len(remaining[eid])}")
    report = {
        "pages_revised": stats["pages_revised"],
        "pages_lose_entry_mark": stats["pages_lose_entry_mark"],
        "pages_keep_entry_mark": stats["pages_keep_entry_mark"],
        "statut_cells_to_game_data": stats["statut_cells_to_game_data"],
        "statut_cells_game_data_obtention_unconfirmed": stats["statut_cells_game_data_obtention_unconfirmed"],
        "statut_cells_kept_unconfirmed": stats["statut_cells_kept_unconfirmed"],
        "statut_cells_official_kept": stats["statut_cells_official_kept"],
        "sources_stamped": stats["sources_stamped"],
        "sources_kept_unconfirmed": stats["sources_kept_unconfirmed"],
        "why_keep": {k: v for k, v in stats["why_keep"].items()},
        "issues": issues,
        "remaining_preview": {k: v[:8] for k, v in remaining.items()},
        "remaining_counts": {k: len(v) for k, v in remaining.items()},
    }
    STATS.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print("ISSUES", issues)
    print("STATUT game", stats["statut_cells_to_game_data"], "game+obtention", stats["statut_cells_game_data_obtention_unconfirmed"], "kept", stats["statut_cells_kept_unconfirmed"], "official", stats["statut_cells_official_kept"])
    print("sources stamped", stats["sources_stamped"], "kept", stats["sources_kept_unconfirmed"])

if __name__ == "__main__":
    main()
