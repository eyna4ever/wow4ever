#!/usr/bin/env python3
"""v42 (t407u) — fiches : 1 accueil « Matériaux » + 9 familles (nouvelles), 52 zones révisées (« PNJ : où les trouver »,
étiquette « fichiers du jeu » corrigée en « base non officielle, à confirmer »), 12 pages de recettes révisées (matériaux liés),
2 fiches Collections révisées (4 montures vendues par un PNJ, à confirmer). Écrit out/entries/{new,rev}-*.json (brouillons)."""
import json, copy, re, sys, shutil
from pathlib import Path
PIPE = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/v42-pipeline')
HERE = Path('/workspace/wowkipedia-v21-elite/v42-test')
OUT = HERE / 'out/entries'; shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir(parents=True)
ENT = {e['id']: e for e in json.load(open(PIPE / 'runtime/entries.json'))}
CNT = json.load(open(HERE / 'out/counts42.json')); FAM = CNT['fam']; ZS = CNT['zones']; RS = CNT['recipes']
NOW = '2026-11-17T21:00:00.000Z'; ACC = '2026-11-17'
GV = 'World of Warcraft: Forever — annonces officielles et fichiers du jeu (client 1.60.1.70862), état documentaire 2026-11-17'
FAN = 'Base de fans sans licence de réutilisation : faits courts repris avec lien, à confirmer ; site non commercial. Contenus de jeu © Blizzard Entertainment.'
def fan(key, url, title): return dict(key=key + '-en', language='en', url=url, title=title, accessedAt=ACC, undated=True, license=FAN, gameVersion=GV)
mounts = ENT['forever-items-mounts']
S = {'client-fichiers': [copy.deepcopy(s) for s in mounts['sources'] if s['key'].startswith('client-fichiers')],
     'client-quetes': [copy.deepcopy(s) for s in mounts['sources'] if s['key'].startswith('client-quetes')],
     'bz-24303313': [copy.deepcopy(s) for s in ENT['forever-professions-recipes-mining']['sources'] if s['key'].startswith('bz-24303313')],
     'tiers-pnj-liste': [fan('tiers-pnj-liste', 'https://eternadex.com/en/daten/npc-liste.json', 'WoW Forever NPC list (unofficial fan database: names, zones, roles; partly completed by players)')],
     'tiers-pnj-fiches': [fan('tiers-pnj-fiches', 'https://eternadex.com/en/npc/', 'WoW Forever NPC pages (unofficial fan database): vendors and their stock, trainers, observed loot, positions — 501 pages consulted')],
     'tiers-cartes': [fan('tiers-cartes', 'https://eternadex.com/en/karte/', 'WoW Forever zone maps (unofficial fan database): positions of quest givers, vendors and trainers — 45 maps consulted')],
     'tiers-classes': [fan('tiers-classes', 'https://eternadex.com/en/lehrer/', 'WoW Forever class trainers and class quests by zone (unofficial fan database) — 9 class pages consulted')]}
for k, v in S.items(): assert v, k
for s in S['client-fichiers'] + S['client-quetes'] + S['bz-24303313']: s['gameVersion'] = GV
def srcs(*keys): return [copy.deepcopy(s) for k in keys for s in S[k]]
def add_srcs(lst, *keys):
    have = {s['key'] for s in lst}
    return lst + [s for s in srcs(*keys) if s['key'] not in have]
def t(fr, en, *src): return {'fr': fr, 'en': en, 'src': list(src)}
def coll(ref, fr, en, *src): return {'type': 'collection', 'ref': ref, 'fr': fr, 'en': en, 'src': list(src)}
def sec(id_, fr, en, blocks): return {'id': id_, 'title': {'fr': fr, 'en': en}, 'blocks': [b if 'type' in b else {'type': 'p', **b} for b in blocks]}
def revise(e, note):
    e = copy.deepcopy(e); e['gameVersion'] = GV; e['updatedAt'] = NOW
    e.pop('verification', None); return e
def hist_add(art, item):
    for s in art['sections']:
        if s['id'] == 'historique-des-corrections':
            b = next((b for b in s['blocks'] if b.get('type') == 'list'), None)
            if b: b['items'].append(item); return
            s['blocks'].append(item | {'type': 'p'}); return
    art['sections'].append(sec('historique-des-corrections', 'Historique des corrections', 'Correction history', [item]))
CAT = lambda l: 'metiers' if l == 'fr' else 'professions'
out = []
FAMS = [('minerais', 'mining', 'ores'), ('herbes', 'herbalism', 'herbs'), ('cuirs', 'skinning', 'hides'), ('tissus', None, None), ('viandes', None, None),
        ('elements', None, None), ('pieces', None, None), ('divers', None, None), ('objets', None, None)]
GATHER_KP = {'minerais': ('Où se trouvent les gisements de minerai et de pierre dans Forever : non indiqué. Aucune source Forever autorisée ne donne leur position ; la fiche le dit au lieu d’inventer une zone.',
                          'Where ore and stone nodes are in Forever: not given. No allowed Forever source gives their location; the card says so instead of making up a zone.'),
             'herbes': ('Où poussent les plantes dans Forever : non indiqué. Aucune source Forever autorisée ne donne leur position ; la fiche le dit au lieu d’inventer une zone.',
                        'Where herbs grow in Forever: not given. No allowed Forever source gives their location; the card says so instead of making up a zone.'),
             'cuirs': ('Quelles créatures dépecer dans Forever : non indiqué en général. Seul le butin observé sur certaines créatures est repris, à confirmer.',
                       'Which creatures to skin in Forever: generally not given. Only loot observed on some creatures is listed, to be confirmed.')}
READ_FR = ('Chaque fiche dit où trouver le matériau, à quoi il sert et quelles quêtes le demandent. Les noms français et anglais, la qualité, le niveau d’objet, les recettes de fabrication, '
           'les composants, les métiers qui l’utilisent, le prix de revente et l’icône viennent des fichiers du jeu (client 1.60.1.70862). Les vendeurs et leur prix, le butin observé, '
           'les quêtes et les positions (x, y en % de la carte de zone) viennent d’une base de données Forever non officielle : ils portent la mention « à confirmer ». '
           'Quand une information manque, la fiche écrit « non indiqué » : rien n’est ajouté de mémoire ni d’après une autre version du jeu.')
READ_EN = ('Each card says where to find the material, what it is used for and which quests ask for it. French and English names, quality, item level, crafting recipes, reagents, '
           'the professions using it, vendor sell price and icon come from the game files (client 1.60.1.70862). Vendors and their prices, observed loot, quests and positions '
           '(x, y in % of the zone map) come from an unofficial Forever database: they are marked “to be confirmed”. When information is missing, the card says “not given”: '
           'nothing is added from memory or from another version of the game.')
HORDE = t('Vendeurs : la base de données consultée liste surtout des vendeurs de la Horde (Orgrimmar, Durotar, Les Tarides, Fossoyeuse, Les Pitons-du-Tonnerre…). Les vendeurs de l’Alliance manquent presque tous : l’absence de vendeur sur une fiche ne prouve pas que personne ne le vend. Les noms allemands présents dans la source sont signalés comme tels.',
          'Vendors: the database consulted lists mostly Horde vendors (Orgrimmar, Durotar, The Barrens, Undercity, Thunder Bluff…). Alliance vendors are almost all missing: no vendor on a card does not prove nobody sells it. German names found in the source are flagged as such.', 'tiers-pnj-fiches')
PEND = [{'fr': 'Positions des gisements de minerai, des plantes et des créatures à dépecer : non indiqué dans les sources Forever autorisées.', 'en': 'Locations of ore nodes, herbs and creatures to skin: not given in the allowed Forever sources.'},
        {'fr': 'Vendeurs de l’Alliance, prix réels en jeu et taux de butin : non indiqués ; seuls des nombres d’observations de butin sont connus.', 'en': 'Alliance vendors, real in-game prices and drop rates: not given; only loot observation counts are known.'},
        {'fr': 'Vendeurs, butin observé, quêtes et positions : base de données Forever non officielle, à confirmer en jeu.', 'en': 'Vendors, observed loot, quests and positions: unofficial Forever database, to be confirmed in game.'}]
CONFIRMED = [t('Blizzard a annoncé plus de 600 nouvelles recettes, sans en publier la liste complète.', 'Blizzard announced over 600 new recipes, without publishing a complete list.', 'bz-24303313')]
HIST_NEW = lambda: sec('historique-des-corrections', 'Historique des corrections', 'Correction history', [{'type': 'list', 'items': [t(
    '17 novembre 2026 (v42, test) : création de la fiche — matériaux de métiers avec « où le trouver » (fabrication et composants : fichiers du jeu ; vendeurs, butin et quêtes : base non officielle, à confirmer). Pas une mise en ligne.',
    '17 November 2026 (v42, test): sheet created — profession materials with “where to find it” (crafting and reagents: game files; vendors, loot and quests: unofficial database, to be confirmed). Not a publication.', 'client-fichiers')], 'src': ['client-fichiers']}])
def new_entry(id_, title, desc, slug, lead, kps, sections, relations, sources):
    return {'id': id_, 'title': title, 'category': 'professions', 'subcategory': 'materiaux', 'description': desc, 'sources': sources, 'status': 'draft', 'identityConfirmed': False,
            'updatedAt': NOW, 'version': 1, 'gameVersion': GV, 'relations': relations,
            'history': [{'at': NOW, 'actor': 'GrokBot', 'note': 'v42 (t407u) : brouillon (test, non publié).', 'version': 1}],
            'article': {'format': 1, 'slug': slug, 'illustration': 'professions', 'noAmbiance': True, 'lead': lead, 'keyPoints': kps, 'sections': sections,
                        'confirmed': copy.deepcopy(CONFIRMED), 'pending': copy.deepcopy(PEND)}}
SRC_MAT = ('client-fichiers', 'tiers-pnj-fiches', 'client-quetes')
PROF_OF_FAM = {}
tot = dict(n=0, has=0, made=0, sold=0, drop=0, quest=0, named=0)
for key, _, _ in FAMS:
    f = FAM[key]; st = f['stats']; n = st['n']
    for k in tot: tot[k] += st.get(k, 0)
    fr_l = f['fr'][0].lower() + f['fr'][1:]; en_l = f['en'][0].lower() + f['en'][1:]
    lead = t(f'{f["fr"]} : les {n} matériaux de cette famille utilisés par les recettes de métier de Forever, avec pour chacun où le trouver, à quoi il sert et quelles quêtes le demandent. '
             'Noms, recettes, composants et icônes : fichiers du jeu (client 1.60.1.70862). Vendeurs, butin observé et quêtes : base de données Forever non officielle, à confirmer.',
             f'{f["en"]}: the {n} materials of this family used by Forever profession recipes, each with where to find it, what it is used for and which quests ask for it. '
             'Names, recipes, reagents and icons: game files (client 1.60.1.70862). Vendors, observed loot and quests: unofficial Forever database, to be confirmed.', *SRC_MAT)
    kps = [t(f'{n} matériaux, dont {st["has"]} avec au moins une source : {st["made"]} fabriqués par une recette des fichiers du jeu, {st["sold"]} vendus par un PNJ, {st["drop"]} vus en butin, {st["quest"]} liés à une quête (vendeurs, butin et quêtes à confirmer).',
             f'{n} materials, {st["has"]} with at least one source: {st["made"]} crafted by a game-file recipe, {st["sold"]} sold by an NPC, {st["drop"]} seen as loot, {st["quest"]} tied to a quest (vendors, loot and quests to be confirmed).', *SRC_MAT),
           t(f'{st["asked"]} matériaux sont demandés par au moins une quête (à confirmer).', f'{st["asked"]} materials are asked for by at least one quest (to be confirmed).', 'client-quetes')]
    if key in GATHER_KP: kps.append(t(*GATHER_KP[key], 'tiers-cartes'))
    if n - st['named']: kps.append(t(f'{n - st["named"]} objet{"s" if n - st["named"] > 1 else ""} sans nom lisible dans les fichiers du jeu : seul le numéro d’objet est affiché.', f'{n - st["named"]} item{"s" if n - st["named"] > 1 else ""} with no readable name in the game files: only the item number is shown.', 'client-fichiers'))
    secs = [sec('lire-cette-liste', 'Comment lire cette liste', 'How to read this list', [t(READ_FR, READ_EN, *SRC_MAT), HORDE,
             t('Toutes les familles de matériaux : [Matériaux : où les trouver](/fr/metiers/materiaux/).', 'All material families: [Materials: where to find them](/en/professions/materials/).', 'client-fichiers')])]
    for g in f['groups']:
        secs.append(sec(g['id'], f'{g["fr"]} — {g["n"]}', f'{g["en"]} — {g["n"]}', [coll(g['ref'],
            'Fabrication et composants : fichiers du jeu. Vendeurs, butin observé et quêtes : à confirmer.', 'Crafting and reagents: game files. Vendors, observed loot and quests: to be confirmed.', *SRC_MAT)]))
    secs.append(HIST_NEW())
    srcl = srcs('bz-24303313', 'client-fichiers', 'client-quetes', 'tiers-pnj-fiches', 'tiers-cartes')
    e = new_entry(f'forever-professions-materials-{key}', {'fr': f'{f["fr"]} : où les trouver', 'en': f'{f["en"]}: where to find them'},
                  {'fr': f'{f["fr"]} de WoW Forever : {n} matériaux de métier, où les trouver (fabrication, vendeurs, butin, quêtes), à quoi ils servent et quelles quêtes les demandent.',
                   'en': f'WoW Forever {en_l}: {n} profession materials, where to find them (crafting, vendors, loot, quests), what they are used for and which quests ask for them.'},
                  {'fr': f['slug_fr'], 'en': f['slug_en']}, lead, kps, secs, ['forever-professions-materials', 'forever-professions-overview'], srcl)
    e['updatedAt'] = '2026-11-17T21:05:00.000Z'  # accueil « Dernières mises à jour » : l’accueil Matériaux puis les familles
    out.append(('new', e))
# hub
rows = []
for key, _, _ in FAMS:
    f = FAM[key]; st = f['stats']
    rows.append([{'fr': f'[{f["fr"]}](/fr/metiers/{f["slug_fr"]}/)', 'en': f'[{f["en"]}](/en/professions/{f["slug_en"]}/)'}] + [{'fr': str(st.get(k, 0)), 'en': str(st.get(k, 0))} for k in ('n', 'has', 'made', 'sold', 'drop', 'quest')])
rows.append([{'fr': 'Total', 'en': 'Total'}] + [{'fr': str(tot[k]), 'en': str(tot[k])} for k in ('n', 'has', 'made', 'sold', 'drop', 'quest')])
PRO = [('alchemy', 'Alchimie', 'Alchemy', 'recettes-alchimie', 'alchemy-recipes'), ('blacksmithing', 'Forge', 'Blacksmithing', 'recettes-forge', 'blacksmithing-recipes'),
       ('enchanting', 'Enchantement', 'Enchanting', 'recettes-enchantement', 'enchanting-recipes'), ('engineering', 'Ingénierie', 'Engineering', 'recettes-ingenierie', 'engineering-recipes'),
       ('leatherworking', 'Travail du cuir', 'Leatherworking', 'recettes-travail-du-cuir', 'leatherworking-recipes'), ('tailoring', 'Couture', 'Tailoring', 'recettes-couture', 'tailoring-recipes'),
       ('cooking', 'Cuisine', 'Cooking', 'recettes-cuisine', 'cooking-recipes'), ('first-aid', 'Secourisme', 'First Aid', 'recettes-secourisme', 'first-aid-recipes'),
       ('mining', 'Minage', 'Mining', 'recettes-minage', 'mining-recipes'), ('herbalism', 'Herboristerie', 'Herbalism', 'recettes-herboristerie', 'herbalism-recipes'),
       ('skinning', 'Dépeçage', 'Skinning', 'recettes-depecage', 'skinning-recipes'), ('fishing', 'Pêche', 'Fishing', 'recettes-peche', 'fishing-recipes')]
prow = [[{'fr': f'[{fr}](/fr/metiers/{sfr}/)', 'en': f'[{en}](/en/professions/{sen}/)'}, {'fr': str(RS[k]['recipes']), 'en': str(RS[k]['recipes'])}, {'fr': str(RS[k]['materials']), 'en': str(RS[k]['materials'])}] for k, fr, en, sfr, sen in PRO]
hub = new_entry('forever-professions-materials', {'fr': 'Matériaux de métier : où les trouver', 'en': 'Profession materials: where to find them'},
    {'fr': f'Les {tot["n"]} matériaux utilisés par les recettes de métier de WoW Forever, rangés en 9 familles : où les trouver, à quoi ils servent, quelles quêtes les demandent.',
     'en': f'The {tot["n"]} materials used by WoW Forever profession recipes, sorted into 9 families: where to find them, what they are for, which quests ask for them.'},
    {'fr': 'materiaux', 'en': 'materials'},
    t(f'Tous les matériaux demandés par les recettes de métier de Forever — {tot["n"]} au total — rangés en 9 familles. Pour chacun : où le trouver (fabrication, vendeur, butin observé, quête), quels métiers l’utilisent et quelles quêtes le demandent. '
      'Les recettes et les composants viennent des fichiers du jeu (client 1.60.1.70862) ; les vendeurs, le butin et les quêtes viennent d’une base de données Forever non officielle et restent à confirmer.',
      f'Every material asked for by Forever profession recipes — {tot["n"]} in all — sorted into 9 families. For each one: where to find it (crafting, vendor, observed loot, quest), which professions use it and which quests ask for it. '
      'Recipes and reagents come from the game files (client 1.60.1.70862); vendors, loot and quests come from an unofficial Forever database and remain to be confirmed.', *SRC_MAT),
    [t(f'{tot["has"]} matériaux sur {tot["n"]} ont au moins une source : {tot["made"]} fabriqués (fichiers du jeu), {tot["sold"]} vendus, {tot["drop"]} vus en butin, {tot["quest"]} liés à une quête (à confirmer).',
       f'{tot["has"]} of {tot["n"]} materials have at least one source: {tot["made"]} crafted (game files), {tot["sold"]} sold, {tot["drop"]} seen as loot, {tot["quest"]} tied to a quest (to be confirmed).', *SRC_MAT),
     t('Positions des gisements de minerai, des plantes et des créatures à dépecer : non indiqué (aucune source Forever autorisée).', 'Locations of ore nodes, herbs and creatures to skin: not given (no allowed Forever source).', 'tiers-cartes'),
     t('Chaque page de recettes liste maintenant ses matériaux et les composants de chaque recette, avec un lien vers la fiche du matériau.', 'Each recipe page now lists its materials and the reagents of each recipe, with a link to the material card.', 'client-fichiers'),
     t('Les PNJ de chaque zone (formateurs, vendeurs, donneurs de quêtes avec position, objets de quête) sont sur les fiches de zone, section « PNJ : où les trouver ».', 'Each zone’s NPCs (trainers, vendors, quest givers with position, quest items) are on the zone sheets, section “NPCs: where to find them”.', 'tiers-pnj-liste', 'tiers-cartes')],
    [sec('familles', 'Les 9 familles de matériaux', 'The 9 material families', [coll('mat-hub', 'Choisissez une famille : chaque page regroupe les fiches « où le trouver ».', 'Pick a family: each page groups the “where to find it” cards.', *SRC_MAT)]),
     sec('couverture', 'Ce que l’on sait par famille', 'What is known per family', [{'type': 'table', 'caption': {'fr': 'Matériaux par famille et sources connues (vendeurs, butin et quêtes à confirmer)', 'en': 'Materials per family and known sources (vendors, loot and quests to be confirmed)'},
        'head': [{'fr': 'Famille', 'en': 'Family'}, {'fr': 'Matériaux', 'en': 'Materials'}, {'fr': 'Au moins une source', 'en': 'At least one source'}, {'fr': 'Fabriqués', 'en': 'Crafted'}, {'fr': 'Vendus', 'en': 'Sold'}, {'fr': 'Butin observé', 'en': 'Observed loot'}, {'fr': 'Quête', 'en': 'Quest'}],
        'rows': rows, 'src': list(SRC_MAT)}]),
     sec('par-metier', 'Par métier', 'By profession', [{'type': 'table', 'caption': {'fr': 'Recettes de chaque page et matériaux qu’elles demandent (fichiers du jeu)', 'en': 'Recipes of each page and the materials they ask for (game files)'},
        'head': [{'fr': 'Métier', 'en': 'Profession'}, {'fr': 'Recettes avec composants', 'en': 'Recipes with reagents'}, {'fr': 'Matériaux différents', 'en': 'Distinct materials'}], 'rows': prow, 'src': ['client-fichiers']}]),
     sec('lire-ces-fiches', 'Comment lire ces fiches', 'How to read these cards', [t(READ_FR, READ_EN, *SRC_MAT), HORDE]),
     HIST_NEW()],
    ['forever-professions-overview'] + [f'forever-professions-materials-{k}' for k, _, _ in FAMS] + [f'forever-professions-recipes-{k}' for k, *_ in PRO],
    srcs('bz-24303313', 'client-fichiers', 'client-quetes', 'tiers-pnj-fiches', 'tiers-cartes', 'tiers-pnj-liste'))
hub['updatedAt'] = '2026-11-17T21:10:00.000Z'
out.append(('new', hub))
for i, (k, e) in enumerate(out[:-1]):
    pass
# ---------------- recettes ----------------
for k, fr, en, sfr, sen in PRO:
    e = revise(ENT[f'forever-professions-recipes-{k}'], 'v42'); a = e['article']; r = RS[k]
    s = sec('materiaux', 'Matériaux : où les trouver', 'Materials: where to find them', [coll(f'mat-recettes-{k}',
        f'Les {r["materials"]} matériaux demandés par les {r["recipes"]} recettes de cette page, rangés par famille, avec le nombre de recettes qui les utilisent. Chaque matériau mène à sa fiche « où le trouver » ; le tableau repliable donne les composants de chaque recette. Composants lus dans les fichiers du jeu (client 1.60.1.70862). Toutes les familles : [Matériaux : où les trouver](/fr/metiers/materiaux/).',
        f'The {r["materials"]} materials asked for by the {r["recipes"]} recipes on this page, sorted by family, with the number of recipes using each. Each material leads to its “where to find it” card; the folding table gives the reagents of each recipe. Reagents read from the game files (client 1.60.1.70862). All families: [Materials: where to find them](/en/professions/materials/).', 'client-fichiers')])
    idx = next(i for i, x in enumerate(a['sections']) if x['id'] == 'historique-des-corrections')
    a['sections'].insert(idx, s)
    a['keyPoints'] = a['keyPoints'] + [t(f'Composants de {r["recipes"]} recettes et {r["materials"]} matériaux liés à leur fiche « où le trouver » (fichiers du jeu).', f'Reagents of {r["recipes"]} recipes and {r["materials"]} materials linked to their “where to find it” card (game files).', 'client-fichiers')]
    hist_add(a, t('17 novembre 2026 (v42, test) : ajout de la section « Matériaux : où les trouver » (composants de chaque recette, lus dans les fichiers du jeu, client 1.60.1.70862). Pas une mise en ligne.',
                  '17 November 2026 (v42, test): added the “Materials: where to find them” section (reagents of each recipe, read from the game files, client 1.60.1.70862). Not a publication.', 'client-fichiers'))
    e['sources'] = add_srcs(e['sources'], 'client-fichiers')
    e['relations'] = list(dict.fromkeys(e.get('relations', []) + ['forever-professions-materials']))
    out.append(('rev', e))
# ---------------- zones ----------------
REPL = [(r'dans la liste des fichiers du jeu Forever \(build 1\.60\.1\.70862\)', 'dans la base de données Forever non officielle (à confirmer)'),
        (r'La liste de PNJ des fichiers du jeu Forever \(build 1\.60\.1\.70862\)', 'La liste de PNJ de la base de données Forever non officielle'),
        (r'la liste de PNJ des fichiers du jeu Forever \(build 1\.60\.1\.70862\)', 'la liste de PNJ de la base de données Forever non officielle'),
        (r'issue des fichiers du jeu \(build 1\.60\.1\.70862\)', 'issue de la base de données Forever non officielle (à confirmer)'),
        (r'liste de PNJ des fichiers du jeu', 'liste de PNJ de la base de données Forever non officielle'),
        (r'données des fichiers du jeu Forever', 'base de données Forever non officielle (à confirmer)'),
        (r'données des fichiers du jeu', 'base de données Forever non officielle (à confirmer)'),
        (r'dans la liste des fichiers du jeu', 'dans la base de données Forever non officielle'),
        (r'de la liste des fichiers du jeu', 'de la base de données Forever non officielle'),
        (r'\(données du jeu\)', '(base non officielle, à confirmer)'),
        (r'Étiquettes extraites', 'Étiquettes de la base'),
        (r'in the Forever game-file list \(build 1\.60\.1\.70862\)', 'in the unofficial Forever database (to be confirmed)'),
        (r'The Forever game-file NPC list \(build 1\.60\.1\.70862\)', 'The NPC list of the unofficial Forever database'),
        (r'the Forever game-file NPC list \(build 1\.60\.1\.70862\)', 'the NPC list of the unofficial Forever database'),
        (r'NPC list from the game files \(build 1\.60\.1\.70862\)', 'NPC list from the unofficial Forever database (to be confirmed)'),
        (r'the game-file NPC list', 'the NPC list of the unofficial Forever database'),
        (r'Forever game-file data', 'unofficial Forever database (to be confirmed)'),
        (r'game-file data', 'unofficial Forever database (to be confirmed)'),
        (r'in the game-file list', 'in the unofficial Forever database'),
        (r'from the game-file list', 'from the unofficial Forever database'),
        (r'\(game data\)', '(unofficial database, to be confirmed)'),
        (r'when the extract tags them', 'when the database tags them'),
        (r'extract labels', 'database labels')]
def fix(x):
    if isinstance(x, dict): return {k: (v if k in ('src', 'key', 'url', 'ref', 'id', 'type') else fix(v)) for k, v in x.items()}
    if isinstance(x, list): return [fix(v) for v in x]
    if isinstance(x, str):
        for a, b in REPL: x = re.sub(a, b, x)
    return x
LEFT = re.compile(r'fichiers du jeu|game-file|game files|données du jeu|game data', re.I)
leftovers = []
NPC_SRC = ('tiers-pnj-liste', 'tiers-pnj-fiches', 'tiers-cartes', 'tiers-classes', 'client-quetes', 'client-fichiers')
zone_ids = [e['id'] for e in ENT.values() if e['category'] == 'zones' and any((s.get('key') or '').startswith('client-npc-liste') for s in e['sources'])]
for zid in zone_ids:
    e0 = ENT[zid]; e = revise(e0, 'v42')
    hist = e['history']; e2 = fix({k: v for k, v in e.items() if k not in ('sources', 'history')}); e2['history'] = hist; e2['sources'] = e['sources']; e = e2
    for s in e['sources']:
        if s['key'].startswith('client-npc-liste'):
            s.pop('verification', None); s.pop('clientBuild', None); s['license'] = FAN; s['gameVersion'] = GV
            s['title'] = ('Liste JSON des PNJ (base de données Forever non officielle, en partie complétée par des joueurs)' if s['language'] == 'fr' else 'NPC list JSON (unofficial Forever database, partly completed by players)')
    # leftovers check (before adding new texts)
    def walk(x, path):
        if isinstance(x, dict):
            for k, v in x.items():
                if k not in ('src', 'key', 'url', 'ref', 'history', 'sources', 'gameVersion'): walk(v, path + '.' + k)
        elif isinstance(x, list):
            for v in x: walk(v, path)
        elif isinstance(x, str) and LEFT.search(x): leftovers.append((zid, path, x[:160]))
    walk(e, '')
    a = e['article']; z = ZS.get(zid)
    if z and not z.get('empty'):
        intro = (f'Où trouver les PNJ utiles de cette zone : formateurs et maîtres de classe, vendeurs et leur stock, donneurs et receveurs de quêtes avec leur position, objets demandés par les quêtes et où les obtenir. '
                 'Les positions sont les coordonnées de la carte de zone (x, y en %). Tout vient d’une base de données Forever non officielle et reste à confirmer ; la base liste surtout des vendeurs de la Horde. '
                 'Les noms des objets viennent des fichiers du jeu ; les matériaux de métier mènent à leur fiche [Matériaux : où les trouver](/fr/metiers/materiaux/).',
                 'Where to find this zone’s useful NPCs: trainers and class trainers, vendors and their stock, quest givers and turn-ins with their position, items quests ask for and where to get them. '
                 'Positions are zone map coordinates (x, y in %). Everything comes from an unofficial Forever database and is still to be confirmed; the database lists mostly Horde vendors. '
                 'Item names come from the game files; profession materials lead to their card in [Materials: where to find them](/en/professions/materials/).')
        news = sec('pnj-ou-les-trouver', 'PNJ : où les trouver', 'NPCs: where to find them', [coll(z['ref'], intro[0], intro[1], *NPC_SRC)])
        ids = [s['id'] for s in a['sections']]
        if 'pnj-donnees-du-jeu' in ids: a['sections'][ids.index('pnj-donnees-du-jeu')] = news
        else: a['sections'].insert(len([i for i in ids if i in ('presentation-officielle',)]), news)
        kp = t(f'{z["npcs_list"]} PNJ dans la base de données Forever non officielle : {z.get("trainers", 0)} formateurs ou maîtres de classe, {z.get("vendors", 0)} vendeurs avec leur stock, {z.get("questnpcs", 0)} donneurs ou receveurs de quêtes avec leur position, {z.get("qitems", 0)} objets de quête dont {z.get("qitems_src", 0)} avec leur source (à confirmer).',
               f'{z["npcs_list"]} NPCs in the unofficial Forever database: {z.get("trainers", 0)} trainers or class trainers, {z.get("vendors", 0)} vendors with their stock, {z.get("questnpcs", 0)} quest givers or turn-ins with their position, {z.get("qitems", 0)} quest items, {z.get("qitems_src", 0)} with their source (to be confirmed).', 'tiers-pnj-liste', 'tiers-pnj-fiches', 'tiers-cartes', 'client-quetes')
        j = next((i for i, k in enumerate(a['keyPoints']) if re.search(r'PNJ dans la (liste|base)', k['fr'])), None)
        if j is None: a['keyPoints'].append(kp)
        else: a['keyPoints'][j] = kp
    ni = next((s for s in a['sections'] if s['id'] == 'informations-non-indiquees'), None)
    nvend = (z or {}).get('vendors', 0)
    items = [t('Niveau de la zone (fourchette) et points de vol : non indiqué, sauf mention officielle déjà présente sur cette fiche.', 'Zone level range and flight points: not given, except an official figure already on this sheet.', 'client-npc-liste'),
             t('Positions des gisements de minerai, des plantes et des créatures à dépecer : non indiqué (aucune source Forever autorisée).', 'Locations of ore nodes, herbs and creatures to skin: not given (no allowed Forever source).', 'tiers-cartes'),
             t(f'Vendeurs : la base consultée en liste surtout pour la Horde ({nvend} dans cette zone) ; l’absence de vendeur ne prouve pas qu’il n’y en a pas. La position de la plupart des vendeurs n’est pas indiquée.',
               f'Vendors: the database consulted lists mostly Horde ones ({nvend} in this zone); no vendor listed is not proof that there is none. Most vendor positions are not given.', 'tiers-pnj-fiches'),
             t('Noms français des PNJ : repris seulement quand les données de quêtes françaises en donnent un ; sinon le nom anglais est gardé. Les noms allemands présents dans la source sont signalés comme tels.',
               'French NPC names: used only when the French quest data give one; otherwise the English name is kept. German names found in the source are flagged as such.', 'client-quetes', 'tiers-pnj-liste'),
             t('Taux de butin : non indiqué ; seuls des nombres d’observations sont connus.', 'Drop rates: not given; only observation counts are known.', 'tiers-pnj-fiches')]
    if ni:
        ni['blocks'] = [{'type': 'list', 'items': items, 'src': ['client-npc-liste']}]
    a['pending'] = [{'fr': re.sub(r'inventaires de vendeurs, formateurs, ', '', p['fr']), 'en': re.sub(r'vendor inventories, trainers, ', '', p['en'])} | ({'src': p['src']} if 'src' in p else {}) for p in a.get('pending', [])]
    a['pending'].append({'fr': 'PNJ, vendeurs, formateurs, positions et objets de quête : base de données Forever non officielle, à confirmer en jeu.', 'en': 'NPCs, vendors, trainers, positions and quest items: unofficial Forever database, to be confirmed in game.'})
    hist_add(a, t('17 novembre 2026 (v42, test) : la liste de PNJ est désormais marquée comme venant d’une base de données Forever non officielle, à confirmer (elle était présentée à tort comme « fichiers du jeu »)'
                  + ('. Ajout de la section « PNJ : où les trouver » : formateurs, vendeurs et leur stock, donneurs de quêtes avec leur position, objets de quête et leur source.' if z and not z.get('empty') else '.') + ' Pas une mise en ligne.',
                  '17 November 2026 (v42, test): the NPC list is now marked as coming from an unofficial Forever database, to be confirmed (it was wrongly shown as “game files”)'
                  + ('. Added the “NPCs: where to find them” section: trainers, vendors and their stock, quest givers with position, quest items and their source.' if z and not z.get('empty') else '.') + ' Not a publication.', 'tiers-pnj-liste'))
    e = json.loads(json.dumps(e, ensure_ascii=False).replace('"tiers-pnj-liste"', '"client-npc-liste"'))  # même liste de PNJ : une seule source
    e['sources'] = add_srcs(e['sources'], *[k for k in NPC_SRC if k != 'tiers-pnj-liste'])
    if z and not z.get('empty'): e['relations'] = list(dict.fromkeys(e.get('relations', []) + ['forever-professions-materials']))
    out.append(('rev', e))
# ---------------- Collections : 4 montures vendues par un PNJ (à confirmer) ----------------
m = revise(ENT['forever-items-mounts'], 'v42'); a = m['article']
def rep(o, a_, b_):
    s = json.dumps(o, ensure_ascii=False); assert a_ in s, a_; return json.loads(s.replace(a_, b_))
a['lead'] = rep(a['lead'], 'L’obtention est indiquée pour 28 d’entre elles (héritage, pack boutique, sort de classe, quête d’échange)', 'L’obtention est indiquée pour 32 d’entre elles (héritage, pack boutique, sort de classe, quête d’échange, vendeur à confirmer)')
a['lead'] = rep(a['lead'], 'Acquisition is given for 28 of them (Legacy, shop pack, class spell, exchange quest)', 'Acquisition is given for 32 of them (Legacy, shop pack, class spell, exchange quest, vendor to be confirmed)')
a['lead']['src'] = list(dict.fromkeys(a['lead']['src'] + ['tiers-pnj-fiches']))
m['description'] = rep(m['description'], '(28)', '(32)')
ids = [s['id'] for s in a['sections']]
vs = sec('vendues-par-un-pnj', 'Vendues par un PNJ (à confirmer) — 4', 'Sold by an NPC (to be confirmed) — 4', [coll('montures-vendeur',
    'Montures de la Horde vendues par Ogunaro Wolfrunner à Orgrimmar (69.4, 12.2) d’après une base de données Forever non officielle : à confirmer en jeu. Nom, prix inscrit et effet : fichiers du jeu.',
    'Horde mounts sold by Ogunaro Wolfrunner in Orgrimmar (69.4, 12.2) according to an unofficial Forever database: to be confirmed in game. Name, recorded price and effect: game files.', 'client-fichiers', 'tiers-pnj-fiches')])
a['sections'].insert(ids.index('echanges-montures-rapides') + 1, vs)
for s in a['sections']:
    if s['id'] == 'horde-niveau-40':
        assert s['title']['fr'].endswith('— 21'), s['title']; s['title'] = {'fr': s['title']['fr'][:-2] + '17', 'en': s['title']['en'][:-2] + '17'}
    if s['id'] == 'par-obtention':
        tb = s['blocks'][0]
        for r in tb['rows']:
            if r[0]['fr'] == 'Horde — niveau 40': assert r[1]['fr'] == '21'; r[1] = {'fr': '17', 'en': '17'}
        k = next(i for i, r in enumerate(tb['rows']) if r[0]['fr'] == 'Montures rapides par quête d’échange')
        tb['rows'].insert(k + 1, [{'fr': 'Vendues par un PNJ (à confirmer)', 'en': 'Sold by an NPC (to be confirmed)'}, {'fr': '4', 'en': '4'}])
        tb['src'] = list(dict.fromkeys(tb['src'] + ['tiers-pnj-fiches']))
a['keyPoints'].append(t('4 montures de la Horde (cors de loup) vendues par Ogunaro Wolfrunner à Orgrimmar, d’après une base non officielle : à confirmer.', '4 Horde mounts (wolf horns) sold by Ogunaro Wolfrunner in Orgrimmar, according to an unofficial database: to be confirmed.', 'tiers-pnj-fiches'))
hist_add(a, t('17 novembre 2026 (v42, test) : 4 cors de loup déplacés dans « Vendues par un PNJ (à confirmer) » d’après une base non officielle. Pas une mise en ligne.', '17 November 2026 (v42, test): 4 wolf horns moved to “Sold by an NPC (to be confirmed)” from an unofficial database. Not a publication.', 'tiers-pnj-fiches'))
m['sources'] = add_srcs(m['sources'], 'tiers-pnj-fiches'); out.append(('rev', m))
h = revise(ENT['forever-items-collections'], 'v42'); a = h['article']
a['keyPoints'] = rep(a['keyPoints'], 'Obtention indiquée pour 28 montures', 'Obtention indiquée pour 32 montures'); a['keyPoints'] = rep(a['keyPoints'], 'Acquisition given for 28 mounts', 'Acquisition given for 32 mounts')
for s in a['sections']:
    if s['id'] == 'obtention':
        tb = s['blocks'][0]
        k = next(i for i, r in enumerate(tb['rows']) if r[0]['fr'] == 'Quête (à confirmer)')
        tb['rows'].insert(k + 1, [{'fr': 'Vendeur PNJ (à confirmer)', 'en': 'NPC vendor (to be confirmed)'}, {'fr': '4', 'en': '4'}, {'fr': '0', 'en': '0'}, {'fr': '0', 'en': '0'}])
        nr = next(r for r in tb['rows'] if r[0]['fr'] == 'Non indiquée'); assert nr[1]['fr'] == '99'; nr[1] = {'fr': '95', 'en': '95'}
        tb['src'] = list(dict.fromkeys(tb['src'] + ['tiers-pnj-fiches']))
hist_add(a, t('17 novembre 2026 (v42, test) : 4 montures vendues par un PNJ ajoutées au décompte, à confirmer. Pas une mise en ligne.', '17 November 2026 (v42, test): 4 NPC-sold mounts added to the count, to be confirmed. Not a publication.', 'tiers-pnj-fiches'))
h['sources'] = add_srcs(h['sources'], 'tiers-pnj-fiches'); out.append(('rev', h))
# ---------------- décision 1 (t407u) : bestiaire, donjons (et maîtres de classe) : base tierce -> « à confirmer » ----------------
U = r'(?:client|build) 1\.60\.1\.70862'
REPL2 = [(r'indique : données de jeu, client WoW Forever', 'se dit tirée du client WoW Forever'), (r'states: game data, WoW Forever client', 'claims to be drawn from WoW Forever client'),
         (r'(L|l)a même documentation de jeu', r'\1a même base non officielle'), (r'the same game documentation', 'the same unofficial database'), (r'The same game documentation', 'The same unofficial database'),
         (r' avec des données du jeu', ', base non officielle, à confirmer'),
         (r'\(extrait Forever', '(base Forever non officielle'), (r'\(Forever extract', '(unofficial Forever database'),
         (r'(dans|de) cet extrait', r'\1 cette base non officielle'), (r'in this extract', 'in this unofficial database'),
         (r'the NPC extract', 'the NPC list of the unofficial database'), (r"(dans|de) l['’]extrait", r'\1 la base non officielle'), (r"étiquettes d['’]extrait", 'étiquettes de la base'),
         (rf'des données du jeu \({U}\)', 'de la base de données Forever non officielle (à confirmer)'),
         (rf'les données du jeu \({U}\)', 'la base de données Forever non officielle (à confirmer)'),
         (rf'les données du jeu Forever \({U}\)', 'la base de données Forever non officielle (à confirmer)'),
         (rf'des données du jeu Forever \({U}\)', 'de la base de données Forever non officielle (à confirmer)'),
         (rf'des fichiers du jeu(?: Forever)? \({U}\)', 'de la base de données Forever non officielle (à confirmer)'),
         (rf'les fichiers du jeu(?: Forever)? \({U}\)', 'la base de données Forever non officielle (à confirmer)'),
         (rf'\(données d[eu] jeu,? {U}\)', '(base non officielle, à confirmer)'),
         (rf'Données du jeu,? {U}', 'Base non officielle, à confirmer'),
         (rf'\((?i:game data),? {U}\)', '(unofficial database, to be confirmed)'),
         (rf'Game data,? {U}', 'Unofficial database, to be confirmed'),
         (rf'données du jeu Forever \({U}\)', 'base de données Forever non officielle (à confirmer)'),
         (rf'fichiers du jeu Forever \({U}\)', 'base de données Forever non officielle (à confirmer)'),
         (rf'fichiers du jeu \({U}\)', 'base de données Forever non officielle (à confirmer)'),
         (rf'(?i)données du jeu,? \(?{U}\)?', 'base non officielle, à confirmer'),
         (rf'données de jeu,? \(?{U}\)?', 'base non officielle, à confirmer'),
         (r'(d’après|selon|dans|sur) les données du jeu Forever', r'\1 la base de données Forever non officielle'),
         (r'(d’après|selon|dans|sur) les données du jeu', r'\1 la base de données Forever non officielle'),
         (r'des données du jeu', 'de la base de données Forever non officielle'),
         (r'les données du jeu', 'la base de données Forever non officielle'),
         (r'\(données du jeu\)', '(base non officielle, à confirmer)'),
         (r'Données du jeu', 'Base non officielle, à confirmer'),
         (r'données du jeu', 'à confirmer'),
         (r'(la|les|des) fichiers du jeu', r'\1 base de données Forever non officielle'),
         (r'liste de PNJ des fichiers du jeu', 'liste de PNJ de la base de données Forever non officielle'),
         (r'fichiers du jeu', 'base de données Forever non officielle'),
         (rf'Noms extraits de la liste de PNJ du {U}', 'Noms tirés de la liste de PNJ de la base de données Forever non officielle'),
         (r'(dans|de) l’extrait', r'\1 la base non officielle'), (r'l’extrait', 'la base non officielle'),
         (r'étiquettes? extraites?', 'étiquette de la base'), (r'Étiquettes extraites', 'Étiquettes de la base'),
         (r'liste de jeu', 'liste de la base non officielle'),
         (rf'Forever game data \({U}\)', 'unofficial Forever database (to be confirmed)'),
         (rf'game files \({U}\)', 'unofficial Forever database (to be confirmed)'),
         (rf'(?i)game data,? \(?{U}\)?', 'unofficial database, to be confirmed'),
         (rf'(?i)game data: {U}', 'unofficial database, to be confirmed'),
         (r'(from|according to|in|on) the Forever game data', r'\1 the unofficial Forever database'),
         (r'(from|according to|in|on) the game data', r'\1 the unofficial Forever database'),
         (r'the game data', 'the unofficial Forever database'),
         (r'\(game data\)', '(unofficial database, to be confirmed)'),
         (r'Game data', 'Unofficial database, to be confirmed'),
         (r'game data', 'to be confirmed'),
         (rf'The Forever game-file NPC list \({U}\)', 'The NPC list of the unofficial Forever database'),
         (r'the game files', 'the unofficial Forever database'), (r'game files', 'unofficial Forever database'), (r'game-file', 'unofficial Forever database'),
         (rf'Names extracted from the {U} NPC list', 'Names taken from the NPC list of the unofficial Forever database'),
         (r'(in|from) the extract', r'\1 the unofficial database'), (r'the extract', 'the unofficial database'),
         (r'extract labels?', 'database label'), (r'the game list', 'the unofficial database list')]
def fix2(x, skip=False):
    if isinstance(x, dict):
        if x.get('id') == 'historique-des-corrections': return x
        return {k: (v if k in ('src', 'key', 'url', 'ref', 'id', 'type') else fix2(v)) for k, v in x.items()}
    if isinstance(x, list): return [fix2(v) for v in x]
    if isinstance(x, str):
        for a_, b_ in REPL2: x = re.sub(a_, b_, x)
    return x
LEFT2 = re.compile(r'fichiers? du (jeu|client)|données du jeu|données de jeu|game[- ]files?|game data|client[- ]file|extrait|extract', re.I)
d1_ids = [i for i, e in ENT.items() if e['category'] in ('creatures', 'instances', 'classes') and any('eternadex' in (s.get('url') or '') and s.get('verification') == 'données du jeu' for s in e['sources'])]
d1_left = []; d1_src = 0
for did in d1_ids:
    e = revise(ENT[did], 'v42')
    hist = e['history']; srcs_ = e['sources']; e2 = fix2({k: v for k, v in e.items() if k not in ('sources', 'history')}); e2['history'] = hist; e2['sources'] = srcs_; e = e2
    for s in e['sources']:
        if 'eternadex' in (s.get('url') or '') and s.get('verification') == 'données du jeu':
            d1_src += 1
            s.pop('verification', None); s.pop('clientBuild', None); s['license'] = FAN
            s['title'] = fix2(re.sub(r'\s*\((?:données du jeu|game data|extrait des fichiers du client|Forever client-file extract)[^)]*\)+\s*$', '', s['title']))
            s['title'] += ' (base de données Forever non officielle, à confirmer)' if s['language'] == 'fr' else ' (unofficial Forever database, to be confirmed)'
    def walk2(x, path):
        if isinstance(x, dict):
            if x.get('id') == 'historique-des-corrections': return
            for k, v in x.items():
                if k not in ('src', 'key', 'url', 'ref', 'history', 'sources', 'gameVersion', 'id'): walk2(v, path + '.' + k)
        elif isinstance(x, list):
            for v in x: walk2(v, path)
        elif isinstance(x, str) and LEFT2.search(x): d1_left.append((did, path, x[:160]))
    walk2(e, '')
    a = e['article']
    hist_add(a, t('17 novembre 2026 (v42, test) : les PNJ, boss, niveaux et recettes repris d’une base de données Forever non officielle sont désormais marqués « à confirmer » (ils étaient présentés à tort comme « données du jeu »). Pas une mise en ligne.',
                  '17 November 2026 (v42, test): NPCs, bosses, levels and recipes taken from an unofficial Forever database are now marked “to be confirmed” (they were wrongly shown as “game data”). Not a publication.',
                  next(s['key'].rsplit('-', 1)[0] for s in e['sources'] if 'eternadex' in (s.get('url') or ''))))
    out.append(('rev', e))
print('D1 entries', len(d1_ids), 'sources relabelled', d1_src, 'leftovers', len(d1_left))
for x in d1_left[:60]: print('  D1LEFT', x)
# ---------------- t408u : Oui de Mathieu (17/11/2026 22:45 Europe/Paris) — publication v42 (inclut v41) : l’historique visible ne dit plus « test » ----------------
def pubfix(x):
    if isinstance(x, dict): return {k: pubfix(v) for k, v in x.items()}
    if isinstance(x, list): return [pubfix(v) for v in x]
    if isinstance(x, str) and ('(v42, test)' in x or '(v41, test)' in x):
        x = x.replace('(v42, test)', '(v42)').replace('(v41, test)', '(v41, publiée avec la v42)' if '17 novembre' in x else '(v41, published with v42)')
        x = x.replace(' Pas une mise en ligne.', '').replace(' Not a publication.', '')
    return x
have = {e['id'] for _, e in out}
for vid in ('forever-items-pets', 'forever-items-toys', 'forever-legacy-rewards', 'forever-items-mounts', 'forever-items-collections'):
    if vid not in have and '(v41, test)' in json.dumps(ENT[vid]['article'], ensure_ascii=False):
        out.append(('rev', revise(ENT[vid], 'v42')))
out = [(k, {**e, 'article': pubfix(e['article'])}) for k, e in out]
assert not any('(v41, test)' in json.dumps(e['article'], ensure_ascii=False) or '(v42, test)' in json.dumps(e['article'], ensure_ascii=False) for _, e in out)
for kind, e in out:
    for x in e['sources']: x['gameVersion'] = e['gameVersion']
    (OUT / f'{kind}-{e["id"]}.json').write_text(json.dumps(e, ensure_ascii=False, indent=1))
print('new', sum(1 for k, _ in out if k == 'new'), 'rev', sum(1 for k, _ in out if k == 'rev'), 'tot', tot)
print('LEFTOVERS', len(leftovers))
for x in leftovers:
    if "player-addon" not in x[2]: print(x)
