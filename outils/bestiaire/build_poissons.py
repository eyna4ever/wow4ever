#!/usr/bin/env python3
"""t354u — Forever fish list draft (no Classic zones)."""
from __future__ import annotations
import json
from pathlib import Path

TREE = Path("/workspace/wowkipedia-v21-elite/bestiaire/test-tree-v37")
OUT = Path("/workspace/wowkipedia-v21-elite/bestiaire/import-batches/poissons-v37.entries.json")
GV = "World of Warcraft: Forever — annonces et notes officielles, état documentaire 2026-11-12"
LICENSE_BZ = ("Droits réservés Blizzard ; référence et synthèse originale (courtes citations), "
              "mention © Blizzard Entertainment conservée ; site non commercial.")
LICENSE_CLIENT = ("Données de tiers (extrait de fichiers client) ; consultation le 12 novembre 2026 ; "
                  "informations à confirmer, non officielles.")
ACCESSED, UPDATED = "2026-11-12", "2026-11-12T06:15:00.000Z"
COOK_FR, COOK_EN = "/fr/metiers/recettes-cuisine/", "/en/professions/cooking-recipes/"
ALCH_FR, ALCH_EN = "/fr/metiers/recettes-alchimie/", "/en/professions/alchemy-recipes/"
FISH_FR, FISH_EN = "/fr/metiers/recettes-peche/", "/en/professions/fishing-recipes/"

def T(fr, en):
    return {"fr": fr, "en": en}

def clip(s, n):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"

def src(key, language, url, title, published=None, undated=False, verification=None):
    official = url.startswith("https://news.blizzard.com")
    out = {"key": key, "language": language, "url": url, "title": title, "accessedAt": ACCESSED,
           "license": LICENSE_BZ if official else LICENSE_CLIENT, "gameVersion": GV}
    if published: out["publishedAt"] = published
    if undated: out["undated"] = True
    if verification: out["verification"] = verification
    return out

SOURCES = [
    src("bz-24303313-fr", "fr",
        "https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever",
        "Récapitulatif de la présentation « Au cœur de World of Warcraft: Forever »", "2026-09-13"),
    src("bz-24303313-en", "en",
        "https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap",
        "World of Warcraft: Forever Deep Dive Panel Recap", "2026-09-13"),
    src("bz-camp-fr", "fr",
        "https://news.blizzard.com/fr-fr/article/24301516/retrouvez-vous-autour-dun-feu-de-camp-dans-world-of-warcraft-forever",
        "Retrouvez-vous autour d’un feu de camp dans World of Warcraft: Forever", "2026-10-21"),
    src("bz-camp-en", "en",
        "https://news.blizzard.com/en-us/article/24301516/gather-around-the-campfire-in-world-of-warcraft-forever",
        "Gather Around the Campfire in World of Warcraft: Forever", "2026-10-21"),
    src("client-guide-kochkunst-fr", "fr", "https://eternadex.com/fr/berufe/kochkunst/",
        "Guide Cuisine — recettes et matériaux (données du jeu, client 1.60.1.70862, à confirmer)",
        undated=True, verification="à confirmer"),
    src("client-guide-kochkunst-en", "en", "https://eternadex.com/en/berufe/kochkunst/",
        "Cooking guide — recipes and materials (game data, client 1.60.1.70862, to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-guide-alchemie-en", "en", "https://eternadex.com/en/berufe/alchemie/",
        "Alchemy guide — recipes and materials (game data, client 1.60.1.70862, to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-datenbank-en", "en", "https://eternadex.com/en/datenbank/",
        "Item database — game data, WoW Forever client build 1.60.1.70862, as of 7 November 2026 (to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-datenbank-fr", "fr", "https://eternadex.com/fr/datenbank/",
        "Base d’objets — données du jeu, client WoW Forever build 1.60.1.70862, au 7 novembre 2026 (à confirmer)",
        undated=True, verification="à confirmer"),
    src("client-handwerk-en", "en", "https://eternadex.com/en/datenbank/items/handwerkswaren/",
        "Trade goods catalog for WoW Forever (to be confirmed)",
        undated=True, verification="à confirmer"),
    src("client-handwerk-fr", "fr", "https://eternadex.com/fr/datenbank/items/handwerkswaren/",
        "Catalogue d’artisanat de WoW Forever (à confirmer)",
        undated=True, verification="à confirmer"),
]
SRC_OFF = ["bz-24303313", "bz-camp"]
SRC_CLIENT = ["client-guide-kochkunst", "client-guide-alchemie", "client-datenbank", "client-handwerk"]
SRC_ALL = SRC_OFF + SRC_CLIENT

def price(copper):
    """copper is int; values over 99 may be silver+copper if passed as (s,c) tuple or total copper."""
    if copper is None:
        return T("non indiqué", "not given")
    if isinstance(copper, tuple):
        s, c = copper
        fr = (f"{s} pièce d’argent" if s == 1 else f"{s} pièces d’argent") + (f" et {c} cuivre" if c else "")
        en = (f"{s} silver" if s == 1 else f"{s} silver") + (f", {c} copper" if c else "")
        return T(fr, en)
    if copper < 100:
        return T(f"{copper} cuivre", f"{copper} copper")
    s, c = divmod(copper, 100)
    return price((s, c))

def cook_cell(recipes):
    # recipes: list of (fr, en)
    if not recipes:
        return T("aucune recette de cuisine dans les 123 recettes consultées",
                 "no cooking recipe in the 123 recipes consulted")
    frs = "; ".join(f"{fr} ({COOK_FR})" for fr, en in recipes)
    ens = "; ".join(f"{en} ({COOK_EN})" for fr, en in recipes)
    return T(clip(frs, 400), clip(ens, 400))

def alch_cell(recipes):
    if not recipes:
        return None
    frs = "; ".join(f"{fr} ({ALCH_FR})" for fr, en in recipes)
    ens = "; ".join(f"{en} ({ALCH_EN})" for fr, en in recipes)
    return T(clip(frs, 400), clip(ens, 400))

# Each row: fr, en, id, sell, cook_recipes list[(fr,en)], alch_recipes, notes_fr, notes_en, new
# sell: int copper or (silver, copper) or None
FISH = [
    # raw / catchable cooking (and Whimsyfin)
    ("Goujon brillant cru", "Raw Brilliant Smallfish", "6291", 1, [("Goujon brillant", "Brilliant Smallfish")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Maquereau ombré cru", "Raw Slitherskin Mackerel", "6303", 1, [("Maquereau ombré", "Slitherskin Mackerel")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Furie du loch crue", "Raw Loch Frenzy", "6317", 2, [("Délice de furie du loch", "Loch Frenzy Delight")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Lutjan à longue mâchoire cru", "Raw Longjaw Mud Snapper", "6289", 1, [("Lutjan à longue mâchoire", "Longjaw Mud Snapper")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Thon arc-en-ciel cru", "Raw Rainbow Fin Albacore", "6361", 2, [("Thon arc-en-ciel", "Rainbow Fin Albacore")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Sagerelle crue", "Raw Sagefish", "21071", 25, [("Sagerelle fumée", "Smoked Sagefish")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Poisson-chat moustachu cru", "Raw Bristle Whisker Catfish", "6308", 2, [("Poisson-chat moustachu", "Bristle Whisker Catfish")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Truite tête-mithril crue", "Raw Mithril Head Trout", "8365", 4, [("Truite tête-mithril", "Mithril Head Trout")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Morue rochécaille crue", "Raw Rockscale Cod", "6362", 4, [("Morue rochécaille", "Rockscale Cod")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Grande sagerelle crue", "Raw Greater Sagefish", "21153", (1, 25), [("Délice de sagerelle", "Sagefish Delight")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Barracuda luisant cru", "Raw Glossy Mightfish", "13754", 6, [("Barracuda luisant cuit", "Cooked Glossy Mightfish")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Lutjan nagenuit cru", "Raw Nightfin Snapper", "13759", 10, [("Soupe de lutjan nagenuit", "Nightfin Soup")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Rouget cru", "Raw Redgill", "13758", 4, [("Filet de rouget", "Filet of Redgill")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Jaune-queue tacheté cru", "Raw Spotted Yellowtail", "4603", 4, [("Jaune-queue tacheté", "Spotted Yellowtail")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Perche estivale crue", "Raw Summer Bass", "13756", 9, [("Perche fumée", "Hot Smoked Bass")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Saumon solécaille cru", "Raw Sunscale Salmon", "13760", 10, [("Saumon solécaille poché", "Poached Sunscale Salmon")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Flétan épineux cru", "Raw Spinefin Halibut", "8959", (1, 60), [("Flétan épineux", "Spinefin Halibut")], [], "poisson cru ; la recette cuisinée est indiquée comme nouvelle dans Forever (apprise auprès du maître)", "raw fish; the cooked recipe is marked new in Forever (from the trainer)", True),
    ("Saumon Blanchécaille cru", "Raw Whitescale Salmon", "13889", 5, [("Pain de saumon", "Baked Salmon")], [], "poisson cru, ingrédient de cuisine", "raw fish, cooking ingredient", False),
    ("Poisson cuirassé cru", "Raw Plated Armorfish", "13890", 70, [("Poisson cuirassé", "Plated Armorfish")], [], "poisson cru ; aussi objet de quête « Crafting Order - Armorfish » ; la recette cuisinée est indiquée comme nouvelle dans Forever", "raw fish; also a quest item for “Crafting Order - Armorfish”; the cooked recipe is marked new in Forever", True),
    ("Calmar hivernal cru", "Raw Winter Squid", "13755", 7, [("Calmar grillé", "Grilled Squid")], [], "calmar cru, ingrédient de cuisine (catalogué comme nourriture)", "raw squid, cooking ingredient (filed as food & drink)", False),
    ("Grand barracuda cru", "Large Raw Mightfish", "13893", 15, [("Steak de barracuda", "Mightfish Steak")], [], "poisson cru, ingrédient de cuisine (catalogué comme nourriture)", "raw fish, cooking ingredient (filed as food & drink)", False),
    ("Homard Pince-noire", "Darkclaw Lobster", "13888", 12, [("Ragoût de homard", "Lobster Stew")], [], "homard, ingrédient de cuisine ; le mode d’obtention n’est pas indiqué", "lobster, cooking ingredient; how it is obtained is not given", False),
    ("Poisson déviant", "Deviate Fish", "6522", 4, [("Délice de déviant", "Savory Deviate Delight")], [("Elixir de croissance géante", "Elixir of Giant Growth")], "catalogué comme nourriture ; sert aussi en alchimie ; le mode d’obtention n’est pas indiqué", "filed as food & drink; also used in alchemy; how it is obtained is not given", False),
    ("Fantaileron", "Whimsyfin", "251524", 4, [("Délice de fantaileron", "Savory Whimsyfin Delight")], [], "objet au numéro élevé, rangé parmi les nouveaux objets de Forever ; ingrédient d’une recette de cuisine nouvelle dans Forever ; le lieu de pêche n’est pas indiqué", "high item id, filed under new items in Forever; reagent for a cooking recipe marked new in Forever; catch location is not given", True),
]

ALCHEMY_ONLY = [
    ("Bouche-noire huileux", "Oily Blackmouth", "6358", 4, [], [("Huile de bouche-noire", "Blackmouth Oil")], "matériau d’alchimie ; le mode d’obtention n’est pas indiqué", "alchemy material; how it is obtained is not given", False),
    ("Lutjan de nagefeu", "Firefin Snapper", "6359", 5, [], [("Huile de feu", "Fire Oil")], "matériau d’alchimie ; le mode d’obtention n’est pas indiqué", "alchemy material; how it is obtained is not given", False),
    ("Anguille pierre-écaille", "Stonescale Eel", "13422", 10, [], [("Huile de pierre-écaille", "Stonescale Oil")], "anguille, matériau d’alchimie ; aussi objet de quête « Craftsman's Writ - Stonescale Eel » ; le lieu de pêche n’est pas indiqué", "eel, alchemy material; also a quest item for “Craftsman's Writ - Stonescale Eel”; catch location is not given", False),
]

OTHER = [
    ("Anguille électrique", "Lightning Eel", "13757", 10, [], [], "anguille au catalogue d’artisanat Forever ; aucune recette de cuisine ni d’alchimie dans les guides 1.60.1.70862 consultés", "eel in the Forever trade-goods catalog; no cooking or alchemy recipe in the 1.60.1.70862 guides consulted", False),
    ("Filets de poisson de saison", "Seasonal Fish Steaks", "273295", 7, [], [], "ingrédient de cuisine au catalogue Forever (numéro d’objet élevé, « nouveaux objets ») ; aucune des 123 recettes de cuisine consultées ne l’utilise ; le mode d’obtention n’est pas indiqué", "cooking ingredient in the Forever catalog (high item id, “new items”); none of the 123 cooking recipes consulted use it; how it is obtained is not given", True),
    ("Chair tendre de Furie", "Soft Frenzy Flesh", "5468", 12, [("Filet de furie", "Fillet of Frenzy")], [], "ingrédient de cuisine (icône de poisson) ; le mode d’obtention n’est pas indiqué", "cooking ingredient (fish icon); how it is obtained is not given", False),
]

CLAMS = [
    ("Petite palourde spiralée", "Small Barnacled Clam", "5523", None, [], [], "cataloguée « autre » ; le mode d’obtention n’est pas indiqué", "filed as “other”; how it is obtained is not given", False),
    ("Palourde à coque épaisse", "Thick-shelled Clam", "5524", None, [], [], "cataloguée « autre » ; le mode d’obtention n’est pas indiqué", "filed as “other”; how it is obtained is not given", False),
    ("Palourde à large bouche", "Big-mouth Clam", "7973", None, [], [], "cataloguée « autre » ; le mode d’obtention n’est pas indiqué", "filed as “other”; how it is obtained is not given", False),
    ("Chair de palourde", "Clam Meat", "5503", None, [("Palourdes bouillies", "Boiled Clams"), ("Soupe de palourdes", "Clam Chowder")], [], "viande, ingrédient de cuisine ; le mode d’obtention n’est pas indiqué", "meat, cooking ingredient; how it is obtained is not given", False),
    ("Chair de palourde relevée", "Tangy Clam Meat", "5504", None, [("Palourdes gobelines", "Goblin Deviled Clams")], [], "viande, ingrédient de cuisine ; le mode d’obtention n’est pas indiqué", "meat, cooking ingredient; how it is obtained is not given", False),
    ("Chair de palourde géante", "Giant Clam Meat", "4655", None, [("Ardeur de palourde géante", "Giant Clam Scorcho")], [], "viande, ingrédient de cuisine ; le mode d’obtention n’est pas indiqué", "meat, cooking ingredient; how it is obtained is not given", False),
    ("Chair de palourde piquante", "Zesty Clam Meat", "7974", None, [("Soupe de palourdes d’Undermine", "Undermine Clam Chowder"), ("Linguines aux palourdes", "Clam Linguine")], [], "viande, ingrédient de cuisine ; Linguines aux palourdes est indiquée comme nouvelle dans Forever", "meat, cooking ingredient; Clam Linguine is marked new in Forever", False),
]

def row(item):
    fr, en, iid, sell, cook, alch, note_fr, note_en, new = item
    # notable column combines cook + alch
    bits_fr, bits_en = [], []
    for cfr, cen in cook:
        bits_fr.append(f"{cfr} (cuisine, {COOK_FR})")
        bits_en.append(f"{cen} (cooking, {COOK_EN})")
    for afr, aen in alch:
        bits_fr.append(f"{afr} (alchimie, {ALCH_FR})")
        bits_en.append(f"{aen} (alchemy, {ALCH_EN})")
    if bits_fr:
        rec = T(clip("; ".join(bits_fr), 400), clip("; ".join(bits_en), 400))
    else:
        rec = T("aucune recette dans les guides de cuisine et d’alchimie consultés",
                "no recipe in the cooking and alchemy guides consulted")
    cat_fr = note_fr
    cat_en = note_en
    return [
        T(fr, en),
        T("non indiqué", "not given"),
        T("non indiqué", "not given"),
        rec,
        price(sell),
        T("non indiqué", "not given"),
        T(clip("à confirmer — " + cat_fr, 400), clip("to be confirmed — " + cat_en, 400)),
    ]

HEAD = [T("Nom", "Name"), T("Compétence de pêche requise", "Required fishing skill"),
        T("Zone / eau", "Zone / water"), T("Recette (cuisine ou alchimie)", "Recipe (cooking or alchemy)"),
        T("Prix de vente", "Sell price"), T("Vendeur", "Vendor"), T("Statut", "Status")]

def table(cap_fr, cap_en, items, src):
    return {"type": "table", "caption": T(clip(cap_fr, 300), clip(cap_en, 300)),
            "head": HEAD, "rows": [row(i) for i in items], "src": src}

def para(fr, en, src):
    return {"type": "p", "fr": clip(fr, 2400), "en": clip(en, 2400), "src": src}

def lst(items, src):
    return {"type": "list", "items": items, "src": src}

def item(fr, en, src=None):
    d = T(clip(fr, 2400), clip(en, 2400))
    if src: d["src"] = src
    return d

n_raw = len(FISH)
n_alch = len(ALCHEMY_ONLY)
n_other = len(OTHER)
n_clam = len(CLAMS)
n_total = n_raw + n_alch + n_other + n_clam
n_new = sum(1 for x in FISH+ALCHEMY_ONLY+OTHER+CLAMS if x[8])
n_with_zone = 0
n_with_skill = 0
n_with_vendor = 0

entry = {
    "id": "forever-professions-fish",
    "title": T("Poissons", "Fish"),
    "description": T(
        f"Liste de {n_total} poissons et prises apparentées relevés dans les données du jeu Forever (client 1.60.1.70862 et catalogue d’objets Forever), à confirmer. "
        "Aucune zone de pêche ni compétence de pêche requise n’est indiquée dans ces données ; les tableaux « Zones (Classic) » n’ont pas été repris.",
        f"List of {n_total} fish and related catches recorded in Forever game data (client 1.60.1.70862 and the Forever item catalog), to be confirmed. "
        "No fishing zone or required fishing skill is given in that data; “Zones (Classic)” tables were not used."
    ),
    "category": "professions",
    "subcategory": "poissons",
    "status": "draft",
    "updatedAt": UPDATED,
    "gameVersion": GV,
    "version": 1,
    "verification": "à confirmer",
    "identityConfirmed": False,
    "relations": [
        "forever-professions-recipes-fishing",
        "forever-professions-recipes-cooking",
        "forever-professions-recipes-alchemy",
        "forever-professions-blueprints",
        "forever-professions-overview",
        "forever-camp-features",
    ],
    "sources": SOURCES,
    "history": [{"actor": "AI-documentary-draft",
                 "note": "Liste de poissons d’après les sources officielles citées et les données du client Forever 1.60.1.70862 (à confirmer). Aucune zone Classic n’est reprise. Brouillon à relire. Pas une validation de publication.",
                 "at": UPDATED, "version": 1}],
    "article": {
        "format": 1,
        "slug": {"fr": "poissons", "en": "fish"},
        "illustration": "professions",
        "lead": {**T(
            "Blizzard n’a pas publié de liste officielle de poissons par zone pour World of Warcraft: Forever. "
            f"Cette fiche rassemble {n_total} poissons et prises apparentées relevés dans les données du jeu "
            "(guide de cuisine et d’alchimie, client build 1.60.1.70862 au 7 novembre 2026, et catalogue d’objets Forever). "
            "Chaque ligne est à confirmer. La zone et la compétence de pêche requise ne sont pas indiquées dans ces données : "
            "elles ne sont pas remplies à partir de tableaux Classic. Les recettes de cuisine déjà documentées sont renvoyées vers "
            f"{COOK_FR}. Les recettes de l’objet de pêche restent sur {FISH_FR}.",
            "Blizzard has not published an official fish-by-zone list for World of Warcraft: Forever. "
            f"This page gathers {n_total} fish and related catches recorded in game data "
            "(cooking and alchemy guides, client build 1.60.1.70862 as of 7 November 2026, and the Forever item catalog). "
            "Every row is to be confirmed. Zone and required fishing skill are not given in that data: "
            "they are not filled from Classic tables. Cooking recipes already documented are linked to "
            f"{COOK_EN}. Fishing profession recipes stay on {FISH_EN}."
        ), "src": SRC_ALL},
        "keyPoints": [
            item(f"{n_total} lignes à confirmer ; {n_with_zone} avec une zone de pêche dans les données Forever consultées ; {n_with_skill} avec une compétence de pêche requise.",
                 f"{n_total} rows to be confirmed; {n_with_zone} with a fishing zone in the Forever data consulted; {n_with_skill} with a required fishing skill.", SRC_CLIENT),
            item("Les noms français viennent de la localisation du catalogue et des guides de métier consultés. Le Fantaileron (Whimsyfin) et les Filets de poisson de saison portent des numéros d’objet élevés, rangés parmi les nouveaux objets de Forever.",
                 "French names come from the localization of the catalog and profession guides consulted. Whimsyfin (Fantaileron) and Seasonal Fish Steaks have high item ids, filed under new items in Forever.", SRC_CLIENT),
            item("Un guide de pêche Forever, consulté le même jour, contient un tableau « Zones (Classic) » et prévient que les emplacements peuvent différer dans Forever : ce tableau n’est pas repris.",
                 "A Forever fishing guide, consulted the same day, contains a “Zones (Classic)” table and warns that locations may differ in Forever: that table is not used.", SRC_CLIENT),
        ],
        "sections": [
            {"id": "lire-cette-liste", "title": T("Comment lire cette liste", "How to read this list"), "blocks": [
                para(f"Les recettes de l’objet Pêche (bocal, râtelier, hutte) restent sur la fiche déjà publiée {FISH_FR}. "
                     "Cette page ajoute les poissons et prises apparentées, pas une seconde liste de recettes de pêche.",
                     f"Fishing profession recipes (bowl, rack, hut) stay on the already published sheet {FISH_EN}. "
                     "This page adds the fish and related catches, not a second fishing-recipe list.", SRC_ALL),
                lst([
                    item("Chaque ligne issue des données du client ou du catalogue d’objets est à confirmer.",
                         "Every row from client data or the item catalog is to be confirmed.", SRC_CLIENT),
                    item("La compétence de pêche requise et la zone (ou le type d’eau) ne figurent pas dans les fiches d’objets ni dans les guides de métier 1.60.1.70862 consultés : les cellules restent à « non indiqué ».",
                         "Required fishing skill and zone (or water type) are not on the item pages or in the 1.60.1.70862 profession guides consulted: those cells stay as “not given”.", SRC_CLIENT),
                    item("Le prix indiqué est le prix de vente de l’objet, quand il figurait sur la fiche Forever. Aucun vendeur d’achat n’était nommé pour ces poissons.",
                         "The price shown is the item’s sell price, when it appeared on the Forever item page. No purchase vendor was named for these fish.", SRC_CLIENT),
                    item("Les liens de recettes pointent vers les fiches de cuisine ou d’alchimie déjà en ligne, sans taux d’obtention.",
                         "Recipe links point to the cooking or alchemy sheets already online, without drop rates.", SRC_CLIENT),
                ], SRC_ALL),
            ]},
            {"id": "perimetre", "title": T("Périmètre et preuves Forever", "Scope and Forever evidence"), "blocks": [
                para("Les guides de cuisine et d’alchimie consultés portent la mention : données du jeu, client WoW Forever build 1.60.1.70862, au 7 novembre 2026. "
                     "La base d’objets de la même documentation reprend le même build. Les fiches d’objets sont libellées « objet de WoW Forever », "
                     "mais n’indiquent pas le lieu d’obtention (« pas encore connu »).",
                     "The cooking and alchemy guides consulted are stamped: game data, WoW Forever client build 1.60.1.70862, as of 7 November 2026. "
                     "The item database in the same documentation uses the same build. Item pages are labelled as items in WoW Forever, "
                     "but they do not give a source location (“not known yet”).", SRC_CLIENT),
                para("Aucune table de prises par zone propre à Forever (y compris l’île de Zéphras et Shen’dralas) n’a été trouvée dans ces sources. "
                     "Les liens « pages liées » de certaines fiches d’objets (par exemple Shen’dralas) sont un pied de page générique, pas un lieu de pêche : ils ne sont pas repris comme zones.",
                     "No Forever-specific catch-by-zone table (including Zephras Isle and Shen’dralas) was found in these sources. "
                     "“Related pages” links on some item pages (for example Shen’dralas) are a generic footer, not a fishing location: they are not used as zones.", SRC_CLIENT),
            ]},
            {"id": "poissons-cuisine", "title": T("Poissons et prises utilisés en cuisine", "Fish and catches used in cooking"), "blocks": [
                table(f"{n_raw} poissons ou prises servant de matériau de cuisine dans le guide 1.60.1.70862 — à confirmer (12/11/2026). Zone et compétence de pêche : non indiquées.",
                      f"{n_raw} fish or catches used as cooking materials in the 1.60.1.70862 guide — to be confirmed (12 November 2026). Zone and fishing skill: not given.",
                      FISH, SRC_CLIENT),
            ]},
            {"id": "poissons-alchimie", "title": T("Poissons utilisés en alchimie", "Fish used in alchemy"), "blocks": [
                table(f"{n_alch} poissons ou anguilles servant de matériau d’alchimie dans le guide 1.60.1.70862 — à confirmer. Le poisson déviant, déjà dans le tableau de cuisine, sert aussi à l’élixir de croissance géante.",
                      f"{n_alch} fish or eels used as alchemy materials in the 1.60.1.70862 guide — to be confirmed. Deviate Fish, already in the cooking table, is also used for Elixir of Giant Growth.",
                      ALCHEMY_ONLY, ["client-guide-alchemie", "client-datenbank", "client-handwerk"]),
            ]},
            {"id": "autres", "title": T("Autres prises ou ingrédients", "Other catches or ingredients"), "blocks": [
                table(f"{n_other} autres lignes du catalogue Forever, sans recette de cuisine dans les 123 recettes, ou dont le mode d’obtention n’est pas précisé — à confirmer.",
                      f"{n_other} other rows from the Forever catalog, with no cooking recipe in the 123 recipes, or whose method of obtainment is not given — to be confirmed.",
                      OTHER, SRC_CLIENT),
            ]},
            {"id": "palourdes", "title": T("Palourdes et viandes de palourde", "Clams and clam meat"), "blocks": [
                para("Ces objets figurent au catalogue Forever (artisanat / cuisine). Les données consultées n’indiquent pas qu’ils se pêchent, ni de quelle palourde vient chaque viande. Ils sont listés ici pour mémoire, sans zone inventée.",
                     "These items appear in the Forever catalog (trade goods / cooking). The data consulted does not say they are fished, nor which clam each meat comes from. They are listed here for the record, with no invented zone.",
                     SRC_CLIENT),
                table(f"{n_clam} palourdes ou viandes de palourde au catalogue Forever — à confirmer. Mode d’obtention et zone : non indiqués.",
                      f"{n_clam} clams or clam meats in the Forever catalog — to be confirmed. How obtained and zone: not given.",
                      CLAMS, SRC_CLIENT),
            ]},
            {"id": "historique-des-corrections", "title": T("Historique des corrections", "Correction history"), "blocks": [
                lst([item("12 novembre 2026 — première rédaction de la liste de poissons, sans tableaux Classic de zones. Brouillon.",
                          "12 November 2026 — first draft of the fish list, without Classic zone tables. Draft.", SRC_ALL)], SRC_ALL),
            ]},
        ],
        "confirmed": [
            item("Blizzard a annoncé plus de 600 nouvelles recettes, sans en publier la liste complète, et n’a pas publié, dans les articles officiels cités, de liste de poissons par zone.",
                 "Blizzard announced over 600 new recipes, without publishing a complete list, and has not, in the official articles cited, published a fish-by-zone list.",
                 SRC_OFF),
        ],
        "pending": [
            T("Zone ou type d’eau, et compétence de pêche requise : non indiqués dans les données Forever consultées (fiches d’objets : obtention « pas encore connue »).",
              "Zone or water type, and required fishing skill: not given in the Forever data consulted (item pages: source “not known yet”)."),
            T("Aucune table de prises pour l’île de Zéphras, Shen’dralas ou une autre zone propre à Forever n’a été trouvée.",
              "No catch table for Zephras Isle, Shen’dralas or another Forever-only zone was found."),
            T("Vendeur d’achat et prix d’achat en jeu : non indiqués pour ces poissons (seul le prix de vente de l’objet l’était, le cas échéant).",
              "Purchase vendor and in-game buy price: not given for these fish (only the item sell price was, when present)."),
            T("Des poissons de quête éventuellement présents dans Forever (par exemple des prises d’évènement) n’ont pas été ajoutés s’ils n’apparaissaient pas dans les guides de métier 1.60.1.70862 ou le catalogue d’artisanat consultés.",
              "Quest or event fish that may exist in Forever were not added if they did not appear in the 1.60.1.70862 profession guides or the trade-goods catalog consulted."),
        ],
        "dates": [
            {"date": "2026-09-13", "fr": "Présentation officielle « Au cœur de Forever » : plus de 600 recettes, sans liste complète.", "en": "Official Deep Dive: over 600 recipes, without a complete list.", "src": ["bz-24303313"]},
            {"date": "2026-11-07", "fr": "Guides cuisine et alchimie, et base d’objets : client WoW Forever build 1.60.1.70862.", "en": "Cooking and alchemy guides, and the item database: WoW Forever client build 1.60.1.70862.", "src": ["client-guide-kochkunst", "client-guide-alchemie", "client-datenbank"]},
            {"date": "2026-11-12", "fr": "Consultation des catalogues et fiches d’objets Forever ; le tableau « Zones (Classic) » du guide de pêche n’est pas repris.", "en": "Consultation of Forever catalogs and item pages; the fishing guide’s “Zones (Classic)” table is not used.", "src": ["client-datenbank", "client-handwerk"]},
        ],
    },
}

# key points / lead length checks at write time
for k in ("fr", "en"):
    assert len(entry["article"]["lead"][k]) <= 1200, (k, len(entry["article"]["lead"][k]))
    assert len(entry["description"][k]) <= 100000

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps([entry], ensure_ascii=False, indent=2) + "\n")
stats = {
    "id": entry["id"], "bytes": OUT.stat().st_size, "total": n_total, "with_zone": n_with_zone,
    "with_skill": n_with_skill, "with_vendor": n_with_vendor, "new_forever": n_new,
    "cooking_group": n_raw, "alchemy_only": n_alch, "other": n_other, "clams": n_clam,
    "slugs": entry["article"]["slug"],
}
Path("/workspace/wowkipedia-v21-elite/bestiaire/import-batches/poissons-v37.stats.json").write_text(json.dumps(stats, indent=2) + "\n")
print(json.dumps(stats, indent=2))
