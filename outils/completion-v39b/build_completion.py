#!/usr/bin/env python3
"""t388u — compléter les rubriques (brouillons uniquement). Écrit un lot d'import (nouvelles fiches, statut draft)
et des fichiers de révision (fiches publiées enrichies). N'importe rien, ne publie rien."""
import json, re, html, copy, unicodedata
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path('/workspace/wowkipedia-v21-elite')
TREE = ROOT / 'ui-v39-test/tree/pipeline'
OUT = ROOT / 'completion-v39b'
SRCDIR = ROOT / 'completion/sources'
E = {e['id']: e for e in json.loads((TREE / 'runtime/entries.json').read_text())}
NPC_EN = json.loads((ROOT / 'bestiaire/sources/npc-liste-en.json').read_text())
NPC_FR = json.loads((ROOT / 'bestiaire/sources/npc-liste-fr.json').read_text())
QIDX = json.loads((OUT / 'sources/quests-index.json').read_text())
B = '1.60.1.70862'
GV = 'World of Warcraft: Forever — annonces officielles et données de jeu, état documentaire 2026-11-15'
NOW = '2026-11-15T21:00:00.000Z'
ACTOR = 'GrokBot'
NOTE_NEW = ('Brouillon t388u (15/11/2026) : nouvelle fiche à la demande de Mathieu (« compléter chaque catégorie »). '
            'Données du client 1.60.1.70862 sans mention ; index de quêtes bêta et pages sans tampon de build : à confirmer. '
            'Pas une validation de publication.')
LIC_BZ = ('Droits réservés Blizzard ; référence et synthèse originale (courtes citations), mention © Blizzard Entertainment '
          'conservée ; site non commercial.')
LIC_CLIENT = ('Données de jeu extraites des fichiers du client World of Warcraft: Forever (build 1.60.1.70862) ; site non '
              'commercial. Contenus de jeu © Blizzard Entertainment.')
LIC_TP = ('Base de fans sans licence de réutilisation : faits courts repris avec lien, à confirmer ; site non commercial. '
          'Contenus de jeu © Blizzard Entertainment.')

def T(fr, en): return {'fr': fr, 'en': en}
def clip(s, n):
    s = ' '.join(str(s).split()); return s if len(s) <= n else s[:n-1].rstrip() + '…'
def slugify(v):
    s = unicodedata.normalize('NFD', str(v).replace('’', '-').replace("'", '-'))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s)).strip('-')[:80].rstrip('-')
def para(fr, en, src): return {'type': 'p', 'fr': clip(fr, 2400), 'en': clip(en, 2400), 'src': src}
def item(fr, en, src): return {'fr': clip(fr, 2400), 'en': clip(en, 2400), 'src': src}
def lst(items, src): return {'type': 'list', 'items': items, 'src': src}
def table(cap_fr, cap_en, head, rows, src):
    return {'type': 'table', 'caption': T(clip(cap_fr, 300), clip(cap_en, 300)), 'head': [T(a, b) for a, b in head],
            'rows': [[T(clip(c[0], 400), clip(c[1], 400)) for c in r] for r in rows], 'src': src}
def sec(id_, fr, en, blocks): return {'id': id_, 'title': T(fr, en), 'blocks': blocks}
def norm(s): return s.replace('’', "'")

def stamped(s):
    return s.get('clientBuild') == B or s.get('build') == B or B in f"{s.get('title','')} {s.get('gameVersion','')}"
def reuse(src):
    s = copy.deepcopy(src); was = stamped(s); s['gameVersion'] = GV
    if was and 'clientBuild' not in s: s['clientBuild'] = B
    return s
def src_of(eid, *keys):
    return [reuse(s) for s in E[eid]['sources'] if any(s['key'] == k or s['key'].startswith(k + '-') for k in keys)]

# --- sources ---
S_NPC = src_of('forever-zone-tanaris', 'client-npc-liste')
for s in S_NPC: s.update(verification='données du jeu', clientBuild=B)
S_HOT = src_of('forever-news-hotfixes-nov5-6', 'bz-hotfixes-en', 'bz-kaivax-1113', 'bz-dungeonxp-us', 'bz-dungeonxp-eu', 'bz-xp-us')
S_K14 = [
    {'key': 'bz-kaivax-1114-us', 'language': 'en', 'url': 'https://us.forums.blizzard.com/en/wow/t/2416343',
     'title': 'Player-Level Dungeon XP Adjustment - November 14 (Kaivax, forum officiel US)', 'publishedAt': '2026-11-15',
     'accessedAt': '2026-11-15', 'license': LIC_BZ, 'gameVersion': GV},
    {'key': 'bz-kaivax-1114-eu', 'language': 'en', 'url': 'https://eu.forums.blizzard.com/en/wow/t/642962',
     'title': 'Player-Level Dungeon XP Adjustment - 15 November (Kaivax, forum officiel EU)', 'publishedAt': '2026-11-15',
     'accessedAt': '2026-11-15', 'license': LIC_BZ, 'gameVersion': GV}]
S_Q = [{'key': 'client-quetes-index-en', 'language': 'en', 'url': 'https://eternadex.com/en/daten/quests/index.json',
        'title': 'Quest index JSON (Forever beta game data 1.60.1 completed by player-addon contributions; file dated 20 October 2026)',
        'accessedAt': '2026-11-15', 'undated': True, 'license': LIC_TP, 'gameVersion': GV}]
S_LEHRER = [{'key': 'client-formateurs-en', 'language': 'en', 'url': 'https://eternadex.com/en/lehrer/',
             'title': 'Trainers in WoW Forever (game data: client build 1.60.1.70862, as of 7 November 2026; coordinates from beta quest data)',
             'accessedAt': '2026-11-13', 'undated': True, 'license': LIC_CLIENT, 'gameVersion': GV, 'clientBuild': B,
             'verification': 'données du jeu'}]
S_QHUB = [{'key': 'client-quetes-hub-en', 'language': 'en', 'url': 'https://eternadex.com/en/quests/',
           'title': 'Quest database hub (states that coordinates come from beta game data)', 'accessedAt': '2026-11-13',
           'undated': True, 'license': LIC_TP, 'gameVersion': GV}]
S_SETS = [{'key': 'client-ensembles-en', 'language': 'en', 'url': 'https://eternadex.com/en/sets/',
           'title': 'Armor sets in WoW Forever: pieces and set bonuses “as they appear in the game data” (no build stamp on the page)',
           'accessedAt': '2026-11-13', 'undated': True, 'license': LIC_TP, 'gameVersion': GV}]
S_RAIDS = src_of('article-forever-raids', *[s['key'].rsplit('-', 1)[0] for s in E['article-forever-raids']['sources'][:2]])
S_RETURN = src_of('forever-zone-tanaris', 'bz-24315643')

def mk(id_, cat, sub, title, desc, slug, lead, kps, sections, sources, relations, pending=None, confirmed=None, tags=None, illu=None):
    a = {'format': 1, 'slug': slug, 'illustration': illu or cat, 'lead': lead, 'keyPoints': kps, 'sections': sections}
    if confirmed: a['confirmed'] = confirmed
    if pending: a['pending'] = pending
    e = {'id': id_, 'title': title, 'category': cat, 'subcategory': sub, 'description': desc, 'sources': sources,
         'status': 'draft', 'identityConfirmed': False, 'updatedAt': NOW, 'version': 1, 'gameVersion': GV,
         'relations': [r for r in dict.fromkeys(relations) if r in E or r in NEW_IDS], 'article': a,
         'history': [{'at': NOW, 'actor': ACTOR, 'note': NOTE_NEW, 'version': 1}]}
    if tags: e['tags'] = tags
    return e

# --- quest index helpers ---
FAC = {'A': ('Alliance', 'Alliance'), 'H': ('Horde', 'Horde'), '': ('les deux', 'both')}
QBY = defaultdict(list)
for r in QIDX: QBY[r[2]].append(r)
def quest_rows(label_list):
    rows = []
    for lab in label_list:
        for r in QBY.get(lab, []):
            f = FAC.get(r[5], (r[5], r[5]))
            ch = ('oui', 'yes') if r[6] else ('non', 'no')
            rows.append((r[3], r[1], [(r[1], r[1]), (str(r[3]), str(r[3])), (str(r[4]), str(r[4])), f, ch]))
    rows.sort(key=lambda x: (x[0], x[1].lower()))
    return [x[2] for x in rows]
QHEAD = [('Quête (nom anglais)', 'Quest'), ('Niveau', 'Level'), ('Niveau requis', 'Required level'), ('Faction', 'Faction'), ('Fait partie d’une suite', 'Part of a chain')]
def quest_section(title_fr, title_en, labels, sid='quetes-liste'):
    rows = quest_rows(labels)
    if not rows: return None, 0
    n = len(rows); nA = sum(1 for r in rows if r[3][1] == 'Alliance'); nH = sum(1 for r in rows if r[3][1] == 'Horde'); nB = n - nA - nH
    blocks = [para(
        f'L’index de quêtes consulté le 15 novembre 2026 (données de la bêta Forever 1.60.1 complétées par des contributions d’add-on de joueurs, fichier daté du 20 octobre 2026) rattache {n} quête{"s" if n>1 else ""} à {title_fr} : {nA} Alliance, {nH} Horde, {nB} pour les deux factions. Ces données ne portent pas le tampon du client 1.60.1.70862 : à confirmer en jeu. Noms en anglais (pas de traduction française officielle dans la source).',
        f'The quest index consulted on 15 November 2026 (Forever beta 1.60.1 game data completed by player-addon contributions, file dated 20 October 2026) attaches {n} quest{"s" if n>1 else ""} to {title_en}: {nA} Alliance, {nH} Horde, {nB} for both factions. This data is not stamped with client 1.60.1.70862: to be confirmed in game.', ['client-quetes-index']),
        table(f'{title_fr} : {n} quêtes — index bêta, à confirmer.', f'{title_en}: {n} quests — beta index, to be confirmed.', QHEAD, rows, ['client-quetes-index'])]
    return sec(sid, 'Quêtes (index bêta, à confirmer)', 'Quests (beta index, to be confirmed)', blocks), n

# --- NPC helpers ---
ROLE = {'x': ('boss', 'boss'), 'h': ('vendeur', 'vendor'), 'z': ('objectif de quête', 'quest objective'), 'q': ('donneur de quête', 'quest giver'), 'b': ('butin indiqué', 'loot flagged'), 't': ('vol à la tire', 'pick pocket'), 'l': ('formateur', 'trainer')}
def roles(t):
    r = [ROLE[c] for c in 'xhlbtzq' if c in (t or '')]
    return (', '.join(a for a, _ in r), ', '.join(b for _, b in r)) if r else ('non indiqué', 'not given')
NPCS = defaultdict(list); FRZ = {}
for a, f in zip(NPC_EN, NPC_FR):
    NPCS[a[3]].append({'name': a[1], 'level': (a[4] or '').strip(), 'tags': a[5] or '', 'q': a[6] if isinstance(a[6], int) else 0}); FRZ[a[3]] = f[3]

NEW_IDS = set(); NEW = []; REV = []; LOG = defaultdict(list)

# ============ A. classic dungeons ============
DUNGEONS = [
    ('Ragefire Chasm', ['Ragefire Chasm'], 'butin-ragefire-chasm', []),
    ('The Deadmines', ['The Deadmines'], 'butin-the-deadmines', []),
    ('Wailing Caverns', ['Wailing Caverns'], 'butin-wailing-caverns', []),
    ('Shadowfang Keep', ['Shadowfang Keep'], 'butin-shadowfang-keep', []),
    ('Blackfathom Deeps', ['Blackfathom Deeps'], 'butin-blackfathom-deeps', []),
    ('The Stockade', ['The Stockade'], 'butin-the-stockade', []),
    ('Gnomeregan', ['Gnomeregan'], None, []),
    ('Razorfen Kraul', ['Razorfen Kraul'], 'butin-razorfen-kraul', ['Razorfen Kraul']),
    ('Scarlet Monastery', ['Scarlet Monastery', 'Scarlet Monastery: Graveyard', 'Scarlet Monastery: Library'], 'butin-scarlet-monastery-graveyard', ['Scarlet Monastery']),
    ('Razorfen Downs', ['Razorfen Downs'], None, ['Razorfen Downs']),
    ("Zul'Farrak", ["Zul'Farrak"], None, []),
    ('Stratholme', ['Stratholme'], None, ['Stratholme']),
    ('Scholomance', ['Scholomance'], None, []),
]
FR_FIX = {'Scarlet Monastery': 'Monastère Écarlate'}
OFFICIAL_DUNGEON = {
    'The Deadmines': ('Correctif officiel du 13 novembre 2026 : Sneed est désormais correctement éjecté si la Déchiqueteuse de Sneed (Sneed’s Shredder) est étourdie au moment d’atteindre 0 % de points de vie.',
                      'Official hotfix of November 13, 2026: Sneed should now properly eject if Sneed’s Shredder is stunned when reaching 0% health.'),
    'Stratholme': ('Correctif officiel du 13 novembre 2026 : vaincre Balnazzar compte désormais pour le défi d’héritage Master Spelunker. Le lot du 9 novembre a aussi rendu impossible de monter à cheval dans Stratholme.',
                   'Official hotfix of November 13, 2026: defeating Balnazzar now correctly counts toward the Legacy Challenge Master Spelunker. The November 9 batch also made mounting inside Stratholme impossible.'),
    'Gnomeregan': ('Correctif officiel du 13 novembre 2026 : le temps de réapparition de Techbot est réduit pour la quête « Save Techbot’s Brain! ».',
                   'Official hotfix of November 13, 2026: Techbot’s respawn time reduced for the quest “Save Techbot’s Brain!”.'),
    'Blackfathom Deeps': ('Le lot de correctifs officiel du 9 novembre 2026 cite des corrections de blocages dans les Profondeurs de Brassenoire (Blackfathom Deeps).',
                          'The official November 9, 2026 hotfix batch lists blocker fixes in Blackfathom Deeps.'),
}
XP_FR = ('Règles d’expérience valables pour tous les donjons de Forever, selon Blizzard : le 8 novembre, l’XP des ennemis de donjon a été augmentée de 50 % (de 40 % à 60 % des valeurs de Classic Era, d’après Kaivax le 10 novembre). '
         'Le 13 novembre, tuer un ennemi n’a plus rapporté d’XP au groupe si l’ennemi était insignifiant pour un membre ; le 14 novembre (heure du Pacifique), Blizzard a assoupli cette règle : l’XP n’est annulée que si le joueur de haut niveau dépasse de plus de 12 niveaux celui des ennemis. Les instances déjà en cours au moment du déploiement ne sont pas concernées.')
XP_EN = ('Experience rules for every Forever dungeon, according to Blizzard: on November 8, dungeon enemy XP was raised by 50% (from 40% to 60% of Classic Era values, per Kaivax on November 10). '
         'On November 13, killing an enemy awarded no XP to the party if the enemy was trivial to any member; on November 14 (Pacific time), Blizzard relaxed the rule: XP is nullified only when the high-level player is more than 12 levels above the enemies. Instances already underway when it was deployed are not affected.')
XP_SRC = ['bz-dungeonxp-us', 'bz-dungeonxp-eu', 'bz-xp-us', 'bz-hotfixes-en', 'bz-kaivax-1114-us', 'bz-kaivax-1114-eu']
BP = E['forever-professions-blueprints']
BP_SEC = {s['id']: s for s in BP['article']['sections']}
def eslug(e, lang): return e.get('article', {}).get('slug', {}).get(lang) or slugify(e['title'][lang])
inst_slugs = {(eslug(e,'fr'), eslug(e,'en')) for e in E.values() if e['category'] == 'instances'}
all_slugs = {(e['category'], l, eslug(e,l)) for e in E.values() for l in ('fr','en')}

for en_name, labels, bp_id, qlabels in DUNGEONS:
    fr_name = FR_FIX.get(en_name, FRZ.get(labels[-1] if en_name == 'Scarlet Monastery' else labels[0], en_name))
    fr_name = fr_name.replace("'", '’')
    en_t = en_name.replace("'", '’')
    id_ = 'forever-dungeon-' + slugify(en_name.replace('The ', ''))
    NEW_IDS.add(id_)
for en_name, labels, bp_id, qlabels in DUNGEONS:
    fr_name = FR_FIX.get(en_name, FRZ.get(labels[0], en_name)).replace("'", '’')
    en_t = en_name.replace("'", '’')
    id_ = 'forever-dungeon-' + slugify(en_name.replace('The ', ''))
    slug = {'fr': slugify(fr_name), 'en': slugify(en_name)}
    assert (slug['fr'], slug['en']) not in inst_slugs, slug
    npcs = [dict(p, label=l) for l in labels for p in NPCS[l]]
    bosses = [p for p in npcs if 'x' in p['tags']]
    others = [p for p in npcs if 'x' not in p['tags']]
    lv = sorted({int(x) for p in bosses for x in re.findall(r'\d+', p['level'])})
    lvtxt = (f'{lv[0]}–{lv[-1]}' if lv and lv[0] != lv[-1] else (str(lv[0]) if lv else ''))
    sources = list(S_NPC); src_keys = ['client-npc-liste']
    sections = []
    sub_note_fr = sub_note_en = ''
    if len(labels) > 1:
        sub_note_fr = ' Étiquettes regroupées : ' + ', '.join(f'{FRZ[l]} ({l})' for l in labels) + '.'
        sub_note_en = ' Labels grouped here: ' + ', '.join(labels) + '.'
    if bosses:
        rows = [[(p['name'], p['name']), (p['level'] or 'non indiqué', p['level'] or 'not given'), (FRZ[p['label']], p['label'])] for p in sorted(bosses, key=lambda p: (p['level'] or '99', p['name']))]
        sections.append(sec('boss-donnees-du-jeu', 'Boss (données du jeu)', 'Bosses (game data)', [
            para(f'La liste de PNJ des fichiers du jeu Forever (build 1.60.1.70862) rattache {len(npcs)} PNJ à {fr_name}, dont {len(bosses)} portent l’étiquette « boss »' + (f', de niveau {lvtxt}' if lvtxt else '') + '.' + sub_note_fr + ' L’ordre de rencontre n’est pas indiqué.',
                 f'The Forever game-file NPC list (build 1.60.1.70862) attaches {len(npcs)} NPCs to {en_t}, {len(bosses)} of them tagged “boss”' + (f', level {lvtxt}' if lvtxt else '') + '.' + sub_note_en + ' Encounter order is not given.', ['client-npc-liste']),
            table(f'{fr_name} : {len(bosses)} boss — données du jeu (client 1.60.1.70862).', f'{en_t}: {len(bosses)} bosses — game data (client 1.60.1.70862).',
                  [('Boss', 'Boss'), ('Niveau', 'Level'), ('Étiquette de zone', 'Zone label')], rows, ['client-npc-liste'])]))
    if others:
        rows = [[(p['name'], p['name']), (p['level'] or 'non indiqué', p['level'] or 'not given'), roles(p['tags']), (str(p['q']), str(p['q']))] for p in sorted(others, key=lambda p: p['name'].lower())]
        intro = [] if bosses else [para(f'La liste de PNJ des fichiers du jeu Forever (build 1.60.1.70862) rattache {len(npcs)} PNJ à {fr_name} ; aucun ne porte l’étiquette « boss » dans cette liste (l’absence d’étiquette ne prouve pas l’absence de boss).' + sub_note_fr,
                                        f'The Forever game-file NPC list (build 1.60.1.70862) attaches {len(npcs)} NPCs to {en_t}; none is tagged “boss” in that list (a missing tag does not prove there is no boss).' + sub_note_en, ['client-npc-liste'])]
        sections.append(sec('pnj-donnees-du-jeu', 'Autres PNJ (données du jeu)', 'Other NPCs (game data)', intro + [
            table(f'{fr_name} : {len(others)} PNJ hors boss — données du jeu.', f'{en_t}: {len(others)} non-boss NPCs — game data.',
                  [('Nom', 'Name'), ('Niveau', 'Level'), ('Rôle', 'Role'), ('Quêtes (liste)', 'Quests (list)')], rows, ['client-npc-liste'])]))
    nrec = 0
    if bp_id and bp_id in BP_SEC:
        tb = [b for b in BP_SEC[bp_id]['blocks'] if b['type'] == 'table'][0]
        tb = copy.deepcopy(tb); nrec = len(tb['rows'])
        need = set(tb['src'])
        sources += [reuse(s) for s in BP['sources'] if any(s['key'] == k or s['key'].startswith(k + '-') for k in need) and s['key'] not in {x['key'] for x in sources}]
        sections.append(sec('recettes-lootables', 'Recettes à récupérer sur place (données du jeu)', 'Recipes that drop here (game data)', [
            para(f'{nrec} recette{"s" if nrec>1 else ""} de métier tombent dans {fr_name} selon les données du jeu déjà publiées sur la page Recettes et plans avancés (/fr/metiers/recettes-et-plans-avances/). Taux d’obtention : non indiqué.',
                 f'{nrec} profession recipe{"s" if nrec>1 else ""} drop in {en_t} according to the game data already published on the Recipes and advanced blueprints page (/en/professions/recipes-and-advanced-blueprints/). Drop rate: not given.', list(need)), tb]))
    qs, nq = quest_section(fr_name, en_t, qlabels)
    if qs:
        sources += [s for s in S_Q]; sections.append(qs)
    official = OFFICIAL_DUNGEON.get(en_name)
    sources += S_HOT + S_K14
    blocks = []
    if official: blocks.append(para(official[0], official[1], ['bz-hotfixes-en']))
    blocks.append(para(XP_FR, XP_EN, XP_SRC))
    sections.append(sec('ce-que-blizzard-en-dit', 'Ce que Blizzard en dit', 'What Blizzard says', blocks))
    sections.append(sec('informations-non-indiquees', 'Informations non indiquées', 'Information not given', [lst([
        item('Fourchette de niveaux recommandée du donjon, emplacement de l’entrée, taille de groupe : non indiqués par Blizzard pour Forever ; les niveaux de boss ci-dessus viennent des données du jeu.', 'Recommended level range, entrance location, group size: not given by Blizzard for Forever; boss levels above come from the game data.', ['client-npc-liste']),
        item('Table de butin des boss, statistiques des objets et taux d’obtention : non indiqués (les tables de Classic ne sont pas reprises).', 'Boss loot tables, item stats and drop rates: not given (Classic tables are not reused).', ['client-npc-liste']),
        item('Noms français des PNJ : absents de la liste consultée ; les noms anglais sont conservés.', 'French NPC names: not in the list consulted; English names are kept.', ['client-npc-liste'])], ['client-npc-liste'])]))
    sections.append(sec('historique-des-corrections', 'Historique des corrections', 'Correction history', [lst([
        item('15 novembre 2026 : création de la fiche (brouillon) à partir de la liste de PNJ du client 1.60.1.70862, des recettes déjà publiées, de l’index de quêtes bêta (à confirmer) et des correctifs officiels.', 'November 15, 2026: sheet created (draft) from the client 1.60.1.70862 NPC list, recipes already published, the beta quest index (to be confirmed) and official hotfixes.', ['client-npc-liste'])], ['client-npc-liste'])]))
    kps = [item(f'{len(bosses)} boss étiquetés dans les données du jeu' + (f' (niveau {lvtxt})' if lvtxt else '') + f', {len(npcs)} PNJ au total.', f'{len(bosses)} tagged bosses in the game data' + (f' (level {lvtxt})' if lvtxt else '') + f', {len(npcs)} NPCs in all.', ['client-npc-liste']),
           item('XP en donjon : +50 % le 8 novembre ; depuis le 14 novembre, annulée seulement si un membre dépasse les ennemis de plus de 12 niveaux.', 'Dungeon XP: +50% on November 8; since November 14, nullified only when a member is more than 12 levels above the enemies.', XP_SRC)]
    if nrec: kps.append(item(f'{nrec} recettes de métier à récupérer (données du jeu).', f'{nrec} profession recipes drop here (game data).', list(need)))
    desc_fr = f'{fr_name} : donjon présent dans les données du jeu Forever (client 1.60.1.70862) — {len(bosses)} boss étiquetés' + (f' de niveau {lvtxt}' if lvtxt else '') + f', {len(npcs)} PNJ' + (f', {nrec} recettes' if nrec else '') + (f', {nq} quêtes (index bêta, à confirmer)' if nq else '') + '.'
    desc_en = f'{en_t}: dungeon present in the Forever game data (client 1.60.1.70862) — {len(bosses)} tagged bosses' + (f' level {lvtxt}' if lvtxt else '') + f', {len(npcs)} NPCs' + (f', {nrec} recipes' if nrec else '') + (f', {nq} quests (beta index, to be confirmed)' if nq else '') + '.'
    lead = item(desc_fr + ' Blizzard n’a pas publié de fiche dédiée ; les règles d’expérience des donjons de Forever s’y appliquent.', desc_en + ' Blizzard has not published a dedicated sheet; Forever’s dungeon XP rules apply.', ['client-npc-liste'])
    seen = set(); sources = [s for s in sources if not (s['key'] in seen or seen.add(s['key']))]
    e = mk(id_, 'instances', 'donjon-classique', T(fr_name, en_t), T(desc_fr, desc_en), slug, lead, kps, sections, sources,
           ['forever-bestiary-classic-dungeons', 'article-forever-raids', 'forever-professions-blueprints' if nrec else 'forever-bestiary-bosses', 'forever-news-hotfixes-nov5-6', 'forever-quests-by-zone' if nq else 'forever-bestiary-bosses'],
           pending=[T('Niveaux recommandés, entrée, butin des boss et taux : non indiqués ; quêtes issues d’un index bêta à confirmer.', 'Recommended levels, entrance, boss loot and rates: not given; quests from a beta index, to be confirmed.')],
           confirmed=[item(XP_FR, XP_EN, XP_SRC)] + ([item(official[0], official[1], ['bz-hotfixes-en'])] if official else []))
    NEW.append(e); LOG['instances'].append((fr_name, f'/fr/donjons-raids/{slug["fr"]}/', f'données du jeu (70862) + {"officiel" if official else "règles XP officielles"}' + (' + index bêta (à confirmer)' if nq else '')))

# ============ D. quests: by-zone index, class quests, profession quests ============
ZONE_ENTRY = {}
for e in E.values():
    if e['category'] == 'zones' and e['subcategory'] in ('zone', 'region-annoncee', 'zone-de-depart-annoncee'):
        ZONE_ENTRY[norm(e['title']['en'])] = e
ZONE_ENTRY["Zephras Isle"] = E.get('forever-zone-zephras-isle', ZONE_ENTRY.get('Zephras Isle'))
FD = {'The Hall of Thanes': 'forever-dungeon-hall-of-thanes', 'Ruins of Lordaeron': 'forever-dungeon-ruins-of-lordaeron', 'Excavation Site: Wetlands': 'forever-dungeon-excavation-site', 'Dalaran': 'forever-dungeon-city-of-dalaran'}
CLASSES = ['Warrior', 'Paladin', 'Hunter', 'Rogue', 'Priest', 'Shaman', 'Mage', 'Warlock', 'Druid']
CLASS_ID = {c: f'forever-class-{c.lower()}' for c in CLASSES}
PROF_LABELS = ['Crafting', 'Blacksmithing', 'Leatherworking', 'Engineering', 'Tailoring', 'Alchemy', 'Herbalism', 'Cooking', 'First Aid', 'Fishing']
PROF_FR = {'Crafting': 'Artisanat (général)', 'Blacksmithing': 'Forge', 'Leatherworking': 'Travail du cuir', 'Engineering': 'Ingénierie', 'Tailoring': 'Couture', 'Alchemy': 'Alchimie', 'Herbalism': 'Herboristerie', 'Cooking': 'Cuisine', 'First Aid': 'Secourisme', 'Fishing': 'Pêche'}
EXCLUDED = {'Camping': 'campement : reste non publié (décision de Mathieu)', 'Darkspear Islands': 'JcJ / réputations : étape 05',
            'Alterac Valley': 'champ de bataille non confirmé par Blizzard pour Forever', 'Warsong Gulch': 'champ de bataille : étape 05', 'Arathi Basin': 'champ de bataille non confirmé',
            'Naxxramas': 'raid non annoncé (Forever se situe avant le Cœur du Magma)', "Ahn'Qiraj": 'raid non annoncé', "Ahn'Qiraj War": 'événement non annoncé', "Zul'Gurub": 'raid non annoncé', 'Molten Core': 'raid non annoncé', 'Blackwing Lair': 'raid non annoncé', "Ruins of Ahn'Qiraj": 'raid non annoncé', "Onyxia's Lair": 'harmonisation déjà couverte par une fiche officielle',
            'Lunar Festival': 'fête saisonnière non annoncée', 'Midsummer Fire Festival': 'fête saisonnière non annoncée', 'Seasonal': 'fêtes non annoncées', 'Darkmoon Faire': 'foire non annoncée', 'Scourge Invasion': 'événement non annoncé',
            'Reputation': 'réputations : étape 05', 'Legendary': 'catégorie fourre-tout de la source', 'Epic': 'catégorie fourre-tout', 'Special': 'catégorie fourre-tout', 'Treasure Map': 'catégorie fourre-tout', '': 'sans zone dans la source',
            'Night Elf': 'quête raciale isolée', 'Deeprun Tram': 'pas de fiche de zone', "Thoradin's Wall": 'pas de fiche de zone', 'Blackrock Mountain': 'pas de fiche de zone (instances non annoncées)'}
for c in CLASSES: NEW_IDS.add(f'forever-quests-class-{c.lower()}')
NEW_IDS |= {'forever-quests-by-zone', 'forever-quests-professions', 'forever-class-trainers', 'forever-items-armor-sets'}

def path_of(e, lang):
    from_cat = {'zones': ('zones', 'zones'), 'instances': ('donjons-raids', 'dungeons-raids'), 'classes': ('classes', 'classes'), 'quests': ('quetes', 'quests')}[e['category']]
    return f"/{lang}/{from_cat[0 if lang=='fr' else 1]}/{eslug(e, lang)}/"

# class quests
for c in CLASSES:
    ce = E[CLASS_ID[c]]; cfr = ce['title']['fr']
    qs, n = quest_section(cfr, c, [c])
    id_ = f'forever-quests-class-{c.lower()}'
    slug = {'fr': 'quetes-de-classe-' + slugify(eslug(ce,'fr')), 'en': slugify(c) + '-class-quests'}
    lead = item(f'Quêtes de classe du {cfr.split(" /")[0].lower()} : {n} quêtes dans l’index de quêtes bêta (à confirmer). La fiche de la classe : {path_of(ce,"fr")}.',
                f'{c} class quests: {n} quests in the beta quest index (to be confirmed). The class sheet: {path_of(ce,"en")}.', ['client-quetes-index'])
    nchain = sum(1 for r in QBY[c] if r[6])
    kps = [item(f'{n} quêtes, dont {nchain} dans une suite de quêtes.', f'{n} quests, {nchain} of them part of a chain.', ['client-quetes-index']),
           item('Noms anglais ; objectifs, récompenses et donneurs : non repris ici (index seulement).', 'English names; objectives, rewards and givers: not included (index only).', ['client-quetes-index'])]
    NEW.append(mk(id_, 'quests', 'quetes-de-classe', T(f'Quêtes de classe : {cfr}', f'{c} class quests'), T(lead['fr'], lead['en']), slug, lead, kps, [qs], list(S_Q), [CLASS_ID[c], 'forever-quests-by-zone'],
                  pending=[T('Index de quêtes de la bêta (20 octobre 2026), complété par des add-ons : à confirmer en jeu.', 'Beta quest index (20 October 2026) completed by addons: to be confirmed in game.')]))
    LOG['quests'].append((f'Quêtes de classe : {cfr}', f'/fr/quetes/{slug["fr"]}/', 'index bêta (à confirmer)'))

# professions quests
rows = []
for lab in PROF_LABELS:
    for r in quest_rows([lab]): rows.append([(PROF_FR[lab], lab)] + r)
slug = {'fr': 'quetes-de-metiers', 'en': 'profession-quests'}
cnt = Counter(); [cnt.update([r[0][1]]) for r in rows]
lead = item(f'{len(rows)} quêtes de métiers dans l’index de quêtes bêta (à confirmer) : ' + ', '.join(f'{PROF_FR[k].lower()} {v}' for k, v in cnt.items()) + '. Les quêtes du campement ne sont pas reprises.',
            f'{len(rows)} profession quests in the beta quest index (to be confirmed): ' + ', '.join(f'{k} {v}' for k, v in cnt.items()) + '. Camping quests are not included.', ['client-quetes-index'])
NEW.append(mk('forever-quests-professions', 'quests', 'quetes-de-metiers', T('Quêtes de métiers', 'Profession quests'), T(lead['fr'], lead['en']), slug, lead,
              [item('« Artisanat » est la catégorie générale de la source (150 quêtes), distincte des métiers nommés.', '“Crafting” is the source’s general category (150 quests), separate from named professions.', ['client-quetes-index']),
               item('Niveaux, faction et appartenance à une suite : index bêta, à confirmer.', 'Levels, faction and chain membership: beta index, to be confirmed.', ['client-quetes-index'])],
              [sec('quetes-liste', 'Quêtes (index bêta, à confirmer)', 'Quests (beta index, to be confirmed)', [table(f'{len(rows)} quêtes de métiers — index bêta, à confirmer.', f'{len(rows)} profession quests — beta index, to be confirmed.', [('Métier', 'Profession')] + QHEAD, rows, ['client-quetes-index'])])],
              list(S_Q), ['forever-professions-overview', 'forever-professions-blueprints', 'forever-quests-by-zone'],
              pending=[T('Index de quêtes de la bêta complété par des add-ons : à confirmer en jeu.', 'Beta quest index completed by addons: to be confirmed in game.')]))
LOG['quests'].append(('Quêtes de métiers', '/fr/quetes/quetes-de-metiers/', 'index bêta (à confirmer)'))

# by-zone index + zone revisions
zrows = []; zone_rev = 0
for lab, rs in sorted(QBY.items(), key=lambda kv: kv[0]):
    target = None
    if norm(lab) in ZONE_ENTRY: target = ZONE_ENTRY[norm(lab)]
    elif lab in FD: target = E[FD[lab]]
    if not target: continue
    nA = sum(1 for r in rs if r[5] == 'A'); nH = sum(1 for r in rs if r[5] == 'H')
    zrows.append([(target['title']['fr'], target['title']['en']), (str(len(rs)), str(len(rs))), (str(nA), str(nA)), (str(nH), str(nH)), (str(len(rs)-nA-nH),)*2,
                  (path_of(target, 'fr') + '#quetes-liste', path_of(target, 'en') + '#quetes-liste')])
    # revision
    rv = copy.deepcopy(target)
    qs, n = quest_section(target['title']['fr'], target['title']['en'], [lab])
    secs = rv['article']['sections']
    hist = next((i for i, s in enumerate(secs) if s['id'] == 'historique-des-corrections'), len(secs))
    secs.insert(hist, qs)
    hitem = item(f'15 novembre 2026 : ajout de la liste des {n} quêtes de l’index bêta (à confirmer).', f'November 15, 2026: added the list of {n} quests from the beta quest index (to be confirmed).', ['client-quetes-index'])
    if hist < len(secs) and secs[-1]['id'] == 'historique-des-corrections':
        blk = next((b for b in secs[-1]['blocks'] if b['type'] == 'list'), None)
        if blk: blk['items'].append(hitem)
        else: secs[-1]['blocks'].append(lst([hitem], ['client-quetes-index']))
    else:
        secs.append(sec('historique-des-corrections', 'Historique des corrections', 'Correction history', [lst([hitem], ['client-quetes-index'])]))
    rv['article']['keyPoints'].append(item(f'{n} quêtes rattachées à cette zone dans l’index de quêtes bêta (à confirmer).', f'{n} quests attached to this zone in the beta quest index (to be confirmed).', ['client-quetes-index']))
    if lab in FD:
        for p in rv['article'].get('pending', []):
            if 'données extraites du client' in p['fr']:
                p['fr'] = 'Table de butin et taux d’obtention : non publiés par Blizzard. Les boss viennent des données du jeu (client 1.60.1.70862) ; les quêtes, d’un index bêta à confirmer.'
                p['en'] = 'Loot table and drop rates: not published by Blizzard. Bosses come from the game data (client 1.60.1.70862); quests from a beta index, to be confirmed.'
    for s in S_Q:
        s2 = dict(s); s2['gameVersion'] = rv['gameVersion']
        if s2['key'] not in {x['key'] for x in rv['sources']}: rv['sources'].append(s2)
    if 'forever-quests-by-zone' not in rv['relations']: rv['relations'].append('forever-quests-by-zone')
    REV.append(rv); zone_rev += 1
    LOG['revisions'].append((target['title']['fr'], path_of(target, 'fr'), f'+{n} quêtes (index bêta, à confirmer)'))
zrows.sort(key=lambda r: r[0][0])
tot = sum(int(r[1][0]) for r in zrows)
lead = item(f'Quêtes par zone : {tot} quêtes de l’index de quêtes bêta (à confirmer) rattachées à {len(zrows)} zones ou donjons qui ont une fiche sur ce wiki. Chaque fiche de zone porte la liste complète.',
            f'Quests by zone: {tot} quests from the beta quest index (to be confirmed) attached to {len(zrows)} zones or dungeons with a sheet on this wiki. Each zone sheet carries the full list.', ['client-quetes-index'])
exc = sorted(((k or '(sans zone)', len(QBY.get(k, [])), v) for k, v in EXCLUDED.items() if QBY.get(k)), key=lambda x: -x[1])
NEW.append(mk('forever-quests-by-zone', 'quests', 'quetes-par-zone', T('Quêtes par zone', 'Quests by zone'), T(lead['fr'], lead['en']), {'fr': 'quetes-par-zone', 'en': 'quests-by-zone'}, lead,
              [item('Ces totaux ne sont pas un recensement officiel : Blizzard annonce seulement « plus de 1 000 nouvelles quêtes ».', 'These totals are not an official census: Blizzard only announces “more than 1,000 new quests”.', ['client-quetes-index', 'bz-24315643']),
               item('Catégories de la source non reprises : campement, JcJ, raids et événements non annoncés, fêtes, quêtes sans zone.', 'Source categories not included: camping, PvP, unannounced raids and events, holidays, quests without a zone.', ['client-quetes-index'])],
              [sec('quetes-par-zone', 'Quêtes par zone', 'Quests by zone', [table(f'{len(zrows)} zones et donjons — index bêta, à confirmer.', f'{len(zrows)} zones and dungeons — beta index, to be confirmed.',
                    [('Zone ou donjon', 'Zone or dungeon'), ('Quêtes', 'Quests'), ('Alliance', 'Alliance'), ('Horde', 'Horde'), ('Les deux', 'Both'), ('Liste', 'List')], zrows, ['client-quetes-index'])]),
               sec('non-repris', 'Catégories non reprises', 'Categories not included', [table('Catégories de l’index non reprises et pourquoi.', 'Index categories not included and why.',
                    [('Catégorie (source)', 'Category (source)'), ('Quêtes', 'Quests'), ('Raison', 'Reason')], [[(a, a), (str(b), str(b)), (c, c)] for a, b, c in exc], ['client-quetes-index'])])],
              list(S_Q) + [s for s in S_RETURN], ['article-forever-quests', 'forever-quests-new-adventures', 'forever-zones-directory', 'forever-quests-professions'],
              pending=[T('Index de quêtes de la bêta complété par des add-ons : à confirmer en jeu.', 'Beta quest index completed by addons: to be confirmed in game.')]))
LOG['quests'].append(('Quêtes par zone', '/fr/quetes/quetes-par-zone/', 'index bêta (à confirmer)'))

# ============ E. class trainers ============
def text_of(f):
    t = open(SRCDIR / f, encoding='utf-8', errors='replace').read()
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', t, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
lt = text_of('lehrer-hub.body')
seg = lt[lt.find('Class trainers in the starting zones'):lt.find('Weapon masters Weapon masters teach')]
ZFR = {'Durotar': 'Durotar', 'Mulgore': 'Mulgore', 'Tirisfal Glades': 'Clairières de Tirisfal', 'Zephras Isle': 'Île de Zéphras', 'Dun Morogh': 'Dun Morogh', 'Elwynn Forest': 'Forêt d’Elwynn', 'Teldrassil': 'Teldrassil'}
FACFR = {'Horde': 'Horde', 'Alliance': 'Alliance', 'Both factions': 'Les deux factions'}
CFR = {c: E[CLASS_ID[c]]['title']['fr'] for c in CLASSES}
trows = []
for m in re.finditer(r'(Horde|Alliance|Both factions) (' + '|'.join(ZFR) + r') (.*?)(?=(?: (?:Horde|Alliance|Both factions) (?:' + '|'.join(ZFR) + r') )|$)', seg):
    fac, zone, body = m.groups()
    for c, name, x, y in re.findall(r'(' + '|'.join(CLASSES) + r') : (.+?) (\d+(?:\.\d+)?), (\d+(?:\.\d+)?)', body):
        trows.append([(FACFR[fac], fac), (ZFR[zone], zone), (CFR[c], c), (name.strip(), name.strip()), (f'{x}, {y}', f'{x}, {y}')])
assert len(trows) == 43, len(trows)
wseg = lt[lt.find('Weapon Classes Weapon masters and cost'):lt.find('Where can I learn staves')]
WFR = {'Axes': 'Haches', 'Bows': 'Arcs', 'Crossbows': 'Arbalètes', 'Daggers': 'Dagues', 'Fist Weapons': 'Armes de pugilat', 'Guns': 'Armes à feu', 'Maces': 'Masses', 'Polearms': 'Armes d’hast', 'Staves': 'Bâtons', 'Swords': 'Épées', 'Thrown': 'Armes de jet', 'Two-Handed Axes': 'Haches à deux mains', 'Two-Handed Maces': 'Masses à deux mains', 'Two-Handed Swords': 'Épées à deux mains', 'Wands': 'Baguettes'}
wrows = []
names = sorted(WFR, key=len, reverse=True)
body = wseg.replace('Weapon Classes Weapon masters and cost', '')
for m in re.finditer(r'(' + '|'.join(re.escape(n) for n in names) + r') ((?:(?!' + '|'.join(re.escape(n) + ' ' for n in names) + r').)*?) –', body):
    w, cl = m.groups()
    unsure = '?' in cl
    cl = re.sub(r'\(\? per game data, not yet confirmed in game\)', '(?)', cl).replace(' ,', ',').strip()
    cl_fr = cl
    for c in CLASSES: cl_fr = re.sub(rf'\b{c}\b', CFR[c].split(' /')[0], cl_fr)
    cl_fr = cl_fr.replace('level 20+', 'niveau 20+')
    wrows.append([(WFR[w], w), (cl_fr, cl), ('à confirmer en jeu (« ? » dans la source)', 'to be confirmed in game (“?” in the source)') if unsure else ('données du jeu', 'game data')])
assert len(wrows) == 15, len(wrows)
lead = item('Maîtres de classe des zones de départ (43 PNJ dans 7 zones, dont l’île de Zéphras) et armes utilisables par classe, d’après les données du jeu Forever (client 1.60.1.70862, état du 7 novembre 2026). Coordonnées issues des données de quêtes de la bêta : à confirmer.',
            'Class trainers in the starting zones (43 NPCs in 7 zones, including Zephras Isle) and usable weapons by class, from the Forever game data (client 1.60.1.70862, as of November 7, 2026). Coordinates come from beta quest data: to be confirmed.', ['client-formateurs'])
NEW.append(mk('forever-class-trainers', 'classes', 'formateurs', T('Maîtres de classe et armes par classe', 'Class trainers and weapons by class'), T(lead['fr'], lead['en']), {'fr': 'maitres-de-classe-et-armes', 'en': 'class-trainers-and-weapons'}, lead,
              [item('Les maîtres d’armes (lieux, prix) et les formateurs de métiers ne sont pas localisés pour Forever : non indiqué.', 'Weapon masters (locations, costs) and profession trainers are not located for Forever: not given.', ['client-formateurs']),
               item('Trois combinaisons arme/classe portent un « ? » dans la source : à confirmer en jeu.', 'Three weapon/class combinations carry a “?” in the source: to be confirmed in game.', ['client-formateurs'])],
              [sec('maitres-des-zones-de-depart', 'Maîtres de classe des zones de départ', 'Starting-zone class trainers', [
                   table('43 maîtres de classe — noms et zones : données du jeu ; coordonnées : à confirmer.', '43 class trainers — names and zones: game data; coordinates: to be confirmed.',
                         [('Faction', 'Faction'), ('Zone', 'Zone'), ('Classe', 'Class'), ('Maître de classe (nom anglais)', 'Trainer'), ('Coordonnées (à confirmer)', 'Coordinates (to be confirmed)')], trows, ['client-formateurs', 'client-quetes-hub'])]),
               sec('armes-par-classe', 'Armes utilisables par classe', 'Weapons by class', [
                   table('15 types d’armes — données du jeu (client 1.60.1.70862).', '15 weapon types — game data (client 1.60.1.70862).', [('Arme', 'Weapon'), ('Classes', 'Classes'), ('Statut', 'Status')], wrows, ['client-formateurs'])]),
               sec('informations-non-indiquees', 'Informations non indiquées', 'Information not given', [lst([
                   item('Emplacement et coût des maîtres d’armes pour Forever : non indiqués.', 'Weapon master locations and costs for Forever: not given.', ['client-formateurs']),
                   item('Formateurs de métiers et coût des rangs : non indiqués.', 'Profession trainers and rank costs: not given.', ['client-formateurs'])], ['client-formateurs'])])],
              S_LEHRER + S_QHUB, ['article-forever-classes'] + [CLASS_ID[c] for c in CLASSES][:5],
              pending=[T('Coordonnées des maîtres de classe : à confirmer en jeu.', 'Class trainer coordinates: to be confirmed in game.')], illu='classes'))
LOG['classes'].append(('Maîtres de classe et armes par classe', '/fr/classes/maitres-de-classe-et-armes/', 'données du jeu (70862) ; coordonnées à confirmer'))

# ============ F. armor sets ============
st = text_of('sets-hub.body')
st = st[st.find('Level Set Contents') + len('Level Set Contents'):st.find('Eterna dex Database')]
srows = []
for lv, name, p, b in re.findall(r'(\d+(?:–\d+)?|–) (.+?) (\d+) pieces, (\d+) bonus(?:es)?', st):
    name = name.strip()
    srows.append([(lv if lv != '–' else 'non indiqué', lv if lv != '–' else 'not given'), (name, name), (p, p), (b, b)])
assert len(srows) == 154, len(srows)
lead = item('154 ensembles d’armure avec leur nombre de pièces et de bonus d’ensemble, classés par niveau, d’après une base qui indique les reprendre « tels qu’ils apparaissent dans les données du jeu » sans tampon de build : à confirmer. Noms en anglais.',
            '154 armor sets with their number of pieces and set bonuses, sorted by level, from a database that says they are shown “as they appear in the game data”, with no build stamp: to be confirmed.', ['client-ensembles'])
NEW.append(mk('forever-items-armor-sets', 'items', 'ensembles', T('Ensembles d’armure', 'Armor sets'), T(lead['fr'], lead['en']), {'fr': 'ensembles-d-armure', 'en': 'armor-sets'}, lead,
              [item('Le détail des pièces et le texte des bonus ne sont pas repris ici.', 'Individual pieces and bonus texts are not included here.', ['client-ensembles']),
               item('Blizzard indique que les bonus d’ensemble ont été améliorés dans Forever ; la liste ci-dessus reste à confirmer.', 'Blizzard says set bonuses were improved in Forever; the list above remains to be confirmed.', ['client-ensembles'])],
              [sec('liste-des-ensembles', 'Liste des ensembles', 'Set list', [table('154 ensembles — à confirmer (pas de tampon de build).', '154 sets — to be confirmed (no build stamp).', [('Niveau', 'Level'), ('Ensemble (nom anglais)', 'Set'), ('Pièces', 'Pieces'), ('Bonus', 'Bonuses')], srows, ['client-ensembles'])])],
              S_SETS, ['forever-items-loot-appearances', 'article-forever-items'],
              pending=[T('Pièces, statistiques et texte des bonus : non repris ; source sans tampon de build, à confirmer.', 'Pieces, stats and bonus texts: not included; source without build stamp, to be confirmed.')]))
LOG['items'].append(('Ensembles d’armure', '/fr/objets/ensembles-d-armure/', 'base de données du jeu sans tampon (à confirmer)'))
# set-bonus claim must cite an official source: check loot-appearances
la = E['forever-items-loot-appearances']
lak = [s['key'] for s in la['sources'] if s['key'].startswith('bz-')]
NEW[-1]['article']['keyPoints'][1] = item('Le butin des donjons classiques a été retravaillé dans Forever (fiche Objets : butin de donjon, apparences et itemisation) ; la liste ci-dessus reste à confirmer.', 'Classic dungeon loot was reworked in Forever (see Items: dungeon loot, appearances and itemization); the list above remains to be confirmed.', ['client-ensembles'])

# ---- borrowed official facts (confirmed list) ----
def borrow(eid, idx, target):
    c = copy.deepcopy(E[eid]['article']['confirmed'][idx])
    have = {x['key'] for x in target['sources']}
    for x in E[eid]['sources']:
        if any(x['key'] == k or x['key'].startswith(k + '-') for k in c['src']) and x['key'] not in have:
            target['sources'].append(reuse(x))
    target['article'].setdefault('confirmed', []).append(c)
for e in NEW:
    if e['article'].get('confirmed'): continue
    if e['id'].startswith('forever-quests-class-') or e['id'] == 'forever-class-trainers': borrow('article-forever-classes', 0, e)
    elif e['id'] in ('forever-quests-by-zone', 'forever-quests-professions'): borrow('article-forever-quests', 0, e)
    elif e['id'] == 'forever-items-armor-sets':
        borrow('forever-items-loot-appearances', 0, e)
        c = e['article']['confirmed'][0]
        e['article']['keyPoints'][1] = item('Blizzard indique des objets uniques de boss de donjon en qualité bleue et des bonus d’ensemble améliorés dans Forever.', 'Blizzard says unique dungeon boss items are blue quality and set bonuses are improved in Forever.', c['src'])
    assert len(e['sources']) <= 20, (e['id'], len(e['sources']))

# ============ G. news revision (Nov 14) ============
nv = copy.deepcopy(E['forever-news-hotfixes-nov5-6'])
for s in S_K14:
    s2 = dict(s); s2['gameVersion'] = nv['gameVersion']; nv['sources'].append(s2)
nv['article']['sections'].insert(0, sec('details-nov14', '14 novembre : XP en donjon assouplie', 'November 14: dungeon XP rule relaxed', [
    para('Kaivax (forums officiels US et EU, message publié le 15 novembre à 02:18 heure de Paris) : la règle du 13 novembre « manquait sa cible » dans certains donjons à cause de l’écart de niveau des ennemis. Avec des correctifs désormais en ligne, l’annulation de l’XP ne s’applique plus que si le joueur de haut niveau dépasse de plus de 12 niveaux celui des ennemis. Les instances déjà en cours au moment du déploiement ne sont pas concernées.',
         'Kaivax (official US and EU forums, posted November 15 at 02:18 Paris time): the November 13 rule “missed the mark” in some dungeons because of the enemies’ level range. With hotfixes now live, XP nullification only applies when the high-level player is more than 12 levels above the enemies. Instances already underway when it was deployed are not affected.', ['bz-kaivax-1114-us', 'bz-kaivax-1114-eu'])]))
nv['title'] = T('Correctifs Forever du 5 au 14 novembre : XP en donjon, classes, objets et quêtes', 'Forever hotfixes, November 5–14: dungeon XP, classes, items and quests')
nv['article']['keyPoints'].insert(0, item('14 novembre : l’XP en donjon n’est plus annulée que si un membre dépasse les ennemis de plus de 12 niveaux.', 'November 14: dungeon XP is nullified only when a member is more than 12 levels above the enemies.', ['bz-kaivax-1114-us']))
REV.append(nv); LOG['revisions'].append((nv['title']['fr'], '/fr/actualites/' + eslug(nv,'fr') + '/', '+ correctif officiel du 14 novembre (forums Blizzard)'))

(OUT / 'import-batches/t388u-nouvelles-fiches.entries.json').write_text(json.dumps(NEW, ensure_ascii=False, separators=(',', ':')))
for f in (OUT / 'revisions').glob('*.json'): f.unlink()
for r in REV: (OUT / 'revisions' / f"{r['id']}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
(OUT / 'log.json').write_text(json.dumps(LOG, ensure_ascii=False, indent=1))
print('new', len(NEW), 'revisions', len(REV), 'zone/dungeon quest revisions', zone_rev, 'bytes', len(json.dumps(NEW)))
