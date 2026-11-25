#!/usr/bin/env python3
"""v41 (t403u) — 1 nouvelle fiche (hub Collections) + 4 révisions (montures, mascottes, jouets, récompenses d'héritage).
Écrit ../out/entries/new-*.json et ../out/entries/rev-*.json (statut brouillon ; le build de test les publie dans /tmp uniquement)."""
import json, copy, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
PIPE = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/v41-pipeline')
OUT = HERE / 'out/entries'; OUT.mkdir(parents=True, exist_ok=True)
ENT = {e['id']: e for e in json.load(open(PIPE / 'runtime/entries.json'))}
FR = json.load(open(PIPE / 'data/collections-v41.json'))
C = json.load(open(HERE / 'out/counts.json'))
NOW = '2026-11-17T17:00:00.000Z'; ACC = '2026-11-17'
GV = 'World of Warcraft: Forever — annonces officielles et fichiers du jeu (client 1.60.1.70862), état documentaire 2026-11-17'
BZL = 'Droits réservés Blizzard ; référence et synthèse originale (courtes citations), mention © Blizzard Entertainment conservée ; site non commercial.'
def bz(key, lang, url, title, pub):
    return dict(key=key, language=lang, url=url, title=title, publishedAt=pub, accessedAt=ACC, license=BZL, gameVersion=GV)
S = {
 'bz-legacy': [bz('bz-legacy-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24307383/decouvrez-le-systeme-dheritage-de-world-of-warcraft-forever', 'Découvrez le système d’héritage de World of Warcraft: Forever', '2026-09-23'),
               bz('bz-legacy-en', 'en', 'https://news.blizzard.com/en-us/article/24307383/get-to-know-the-world-of-warcraft-forever-legacy-system', 'Get to Know the World of Warcraft: Forever Legacy System', '2026-09-23')],
 'bz-pack': [bz('bz-pack-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24301508/achetez-les-avantages-de-world-of-warcraft-forever-et-lancez-vous-dans-vos-prochaines-aventures-sur-azeroth', 'Achetez les avantages de World of Warcraft: Forever et lancez-vous dans vos prochaines aventures sur Azeroth', '2026-09-12'),
             bz('bz-pack-en', 'en', 'https://news.blizzard.com/en-us/article/24301508/purchase-world-of-warcraft-forever-upgrades-and-begin-your-next-journey-in-azeroth', 'Purchase World of Warcraft: Forever Upgrades and Begin Your Next Journey in Azeroth', '2026-09-12')],
 'bz-sub-year': [bz('bz-sub-year-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24310658/debloquez-un-an-de-world-of-warcraft-et-recevez-des-tresors-bonus', 'Débloquez un an de World of Warcraft® et recevez des trésors bonus', '2026-10-15'),
                 bz('bz-sub-year-en', 'en', 'https://news.blizzard.com/en-us/article/24310658/unlock-a-year-of-world-of-warcraft-and-get-bonus-treasures', 'Unlock a Year of World of Warcraft® and Get Bonus Treasures', '2026-10-15')],
 'bz-hotfixes': [bz('bz-hotfixes-en', 'en', 'https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-11-2026', 'WoW: Forever Hotfixes - November 11, 2026', '2026-11-11')],
 'client-fichiers': [dict(key='client-fichiers-en', language='en', url='https://us.cdn.blizzard.com/tpr/wow/config/5a/da/5ada954223f7c409ea172361f5c9e565',
     title='WoW Forever client files, build 1.60.1.70862 — data tables and icons read from Blizzard’s official CDN', accessedAt=ACC, undated=True,
     license='Fichiers du jeu World of Warcraft: Forever (build 1.60.1.70862) lus sur le CDN officiel Blizzard : noms, prix, niveaux et icônes ; icônes converties en WebP sans retouche. Contenus et images du jeu © Blizzard Entertainment ; site non commercial.',
     gameVersion=GV, clientBuild='1.60.1.70862', verification='données du jeu')],
 'client-quetes': [dict(key='client-quetes-en', language='en', url='https://eternadex.com/en/daten/quests/0.json',
     title='Quest data JSON (Forever game data 1.60.1, partly completed by player-addon contributions; 64 files consulted)', accessedAt=ACC, undated=True,
     license='Base de fans sans licence de réutilisation : faits courts repris avec lien, à confirmer ; site non commercial. Contenus de jeu © Blizzard Entertainment.', gameVersion=GV)],
}
def srcs(*keys): return [s for k in keys for s in S[k]]
def t(fr, en, *src): return {'fr': fr, 'en': en, 'src': list(src)}
def coll(ref, fr, en, *src): return {'type': 'collection', 'ref': ref, 'fr': fr, 'en': en, 'src': list(src)}
def sec(id_, fr, en, blocks): return {'id': id_, 'title': {'fr': fr, 'en': en}, 'blocks': [b if 'type' in b else {'type': 'p', **b} for b in blocks]}
def n(ref): return FR[ref]['count'] if ref in FR else 0
ICON_NOTE = t('Chaque fiche montre l’icône officielle de l’objet, lue dans les fichiers du jeu WoW Forever (client 1.60.1.70862) et seulement convertie au format WebP, sans retouche (images du jeu © Blizzard Entertainment). Quand aucune image du jeu n’existe pour un élément, aucune image n’est affichée.',
              'Each card shows the item’s official icon, read from the WoW Forever game files (client 1.60.1.70862) and only converted to WebP, unretouched (game images © Blizzard Entertainment). When no game image exists for an entry, no image is shown.', 'client-fichiers')
READ_FR = ('Les noms français et anglais, la qualité, la faction, le niveau requis, le prix et l’effet viennent des fichiers du jeu (client 1.60.1.70862). '
           'L’obtention « officielle » vient des articles Blizzard cités. Les quêtes, PNJ et zones viennent de données de quêtes du jeu complétées par des joueurs : elles restent à confirmer. '
           'Quand les fichiers du jeu ne disent pas comment obtenir un élément, la fiche l’écrit (« non indiquée ») : rien n’est ajouté de mémoire ni d’après une autre version du jeu. '
           'Le prix inscrit dans les fichiers du jeu ne prouve pas qu’un vendeur le vende dans Forever, et la présence d’un élément dans ces fichiers ne prouve pas qu’il soit obtenable dans Forever.')
READ_EN = ('French and English names, quality, faction, required level, price and effect come from the game files (client 1.60.1.70862). '
           '“Official” acquisition comes from the cited Blizzard articles. Quests, NPCs and zones come from game quest data completed by players: they remain to be confirmed. '
           'When the game files do not say how to get an entry, the card says so (“not given”): nothing is added from memory or from another version of the game. '
           'A price recorded in the game files does not prove that a vendor sells it in Forever, and the presence of an entry in those files does not prove it can be obtained in Forever.')
TOC_NOTE = lambda fr, en: t(fr, en, 'client-fichiers')

def revise(eid, title=None, description=None, article=None, sources=None, relations=None):
    e = copy.deepcopy(ENT[eid])
    if title: e['title'] = title
    if description: e['description'] = description
    if article: e['article'] = article
    if sources is not None: e['sources'] = sources
    if relations is not None: e['relations'] = relations
    e['gameVersion'] = GV; e['updatedAt'] = NOW
    for x in e['sources']: x['gameVersion'] = GV
    e.pop('verification', None)
    return e

def base_article(old, lead, kps, sections, confirmed, pending, dates, extra=None):
    a = {'format': 1, 'slug': old['article']['slug'], 'illustration': old['article']['illustration'], 'noAmbiance': True,
         'lead': lead, 'keyPoints': kps, 'sections': sections, 'confirmed': confirmed, 'pending': pending}
    if dates: a['dates'] = dates
    return a

HIST = lambda prev: prev + [sec('historique-des-corrections', 'Historique des corrections', 'Correction history', [
    t('17 novembre 2026 (v41, test) : fiches illustrées par les icônes du jeu, regroupées par moyen d’obtention ; noms français officiels et prix repris des fichiers du jeu (client 1.60.1.70862) ; quêtes et PNJ des données de quêtes, à confirmer. Remplace l’ancien tableau. Pas une mise en ligne.',
      '17 November 2026 (v41, test): cards illustrated with game icons, grouped by acquisition; official French names and prices taken from the game files (client 1.60.1.70862); quests and NPCs from quest data, to be confirmed. Replaces the former table. Not a publication.', 'client-fichiers')])]

DATES = [{'date': '2026-09-12', 'fr': 'Packs des Éolides annoncés (Fièregriffe céruléenne, Puits de vent shen’dorei).', 'en': 'Skyborne packs announced (Cerulean Prideclaw, Shen’dorei Windwell).', 'src': ['bz-pack']},
         {'date': '2026-09-23', 'fr': 'Système d’héritage : quatre récompenses au lancement.', 'en': 'Legacy system: four launch rewards.', 'src': ['bz-legacy']},
         {'date': '2026-10-15', 'fr': 'Bonus d’abonnement 6 ou 12 mois : mascotte Azurbie.', 'en': '6- or 12-month subscription bonus: Azurky pet.', 'src': ['bz-sub-year']},
         {'date': '2026-11-10', 'fr': 'Correctif : montures de vendeur racial liées quand ramassées.', 'en': 'Hotfix: racial vendor mounts bind on pickup.', 'src': ['bz-hotfixes']}]

out = []
# ---------- mounts ----------
mm = ENT['forever-items-mounts']
nk = C['mounts_known']; N = C['mounts']
groups = [('montures-heritage', 'heritage', 'Héritage', 'Legacy', 'Récompense d’héritage du lancement (officiel).', 'Launch Legacy reward (official).', ['bz-legacy', 'client-fichiers']),
          ('montures-pack', 'pack-boutique', 'Pack boutique', 'Shop pack', 'Monture incluse dans les packs des Éolides (officiel).', 'Mount included in the Skyborne packs (official).', ['bz-pack', 'client-fichiers']),
          ('montures-classe', 'montures-de-classe', 'Montures de classe', 'Class mounts', 'Sorts de monture de démoniste et de paladin (pas d’objet). Les quêtes indiquées viennent des données de quêtes (à confirmer).', 'Warlock and paladin mount spells (no item). Listed quests come from quest data (to be confirmed).', ['client-fichiers', 'client-quetes']),
          ('montures-echange', 'echanges-montures-rapides', 'Montures rapides par quête d’échange', 'Swift mounts from exchange quests', 'Montures rapides proposées au choix par des quêtes d’échange (niveau 60), avec le PNJ qui les donne. Données de quêtes, à confirmer.', 'Swift mounts offered as a choice by exchange quests (level 60), with the NPC who gives them. Quest data, to be confirmed.', ['client-fichiers', 'client-quetes'])]
for fac, ffr, fen in (('alliance', 'Alliance', 'Alliance'), ('horde', 'Horde', 'Horde'), ('both', 'deux factions', 'both factions')):
    for lv in (40, 60, 'autre'):
        ref = f'montures-ni-{fac}-{lv}'
        if ref in FR and n(ref):
            lfr = f'niveau {lv}' if lv != 'autre' else 'autre niveau requis'; len_ = f'level {lv}' if lv != 'autre' else 'other required level'
            groups.append((ref, f'{fac}-niveau-{lv}', f'{ffr[0].upper()+ffr[1:]} — {lfr}', f'{fen[0].upper()+fen[1:]} — {len_}',
                           f'Montures {("de l’" + ffr) if fac == "alliance" else ("de la " + ffr) if fac == "horde" else "utilisables par les deux factions"}, {lfr} : présentes dans les fichiers du jeu, obtention non indiquée.',
                           f'{fen[0].upper()+fen[1:]} mounts, {len_}: present in the game files, acquisition not given.', ['client-fichiers']))
secs = [sec('lire-cette-liste', 'Comment lire cette liste', 'How to read this list', [t(READ_FR, READ_EN, 'client-fichiers', 'client-quetes'), ICON_NOTE])]
secs.append(sec('par-obtention', 'Par moyen d’obtention', 'By acquisition', [{'type': 'table', 'caption': {'fr': 'Nombre de montures par groupe', 'en': 'Number of mounts per group'},
    'head': [{'fr': 'Groupe', 'en': 'Group'}, {'fr': 'Montures', 'en': 'Mounts'}],
    'rows': [[{'fr': g[2], 'en': g[3]}, {'fr': str(n(g[0])), 'en': str(n(g[0]))}] for g in groups], 'src': ['client-fichiers']}]))
for ref, sid, fr, en, dfr, den, src in groups:
    secs.append(sec(sid, f'{fr} — {n(ref)}', f'{en} — {n(ref)}', [coll(ref, dfr, den, *src)]))
secs.append(sec('montures-raciales-officiel', 'Montures de vendeur racial (règle officielle)', 'Racial vendor mounts (official rule)', [
    t('Correctif officiel du 10 novembre 2026 : toutes les montures de vendeur racial sont désormais liées quand ramassées. L’article ne nomme ni les montures, ni les vendeurs, ni les prix.', 'Official hotfix of 10 November 2026: all racial vendor mounts now bind on pickup. The article names neither the mounts, nor the vendors, nor the prices.', 'bz-hotfixes')]))
art = base_article(mm, t(f'{N} montures de WoW Forever, chacune avec son icône du jeu : nom officiel français et anglais, faction, niveau, prix inscrit dans les fichiers du jeu et effet. L’obtention est indiquée pour {nk} d’entre elles (héritage, pack boutique, sort de classe, quête d’échange) ; pour les autres, les fichiers du jeu ne la donnent pas.',
                         f'{N} WoW Forever mounts, each with its game icon: official French and English name, faction, level, price recorded in the game files and effect. Acquisition is given for {nk} of them (Legacy, shop pack, class spell, exchange quest); for the others, the game files do not give it.', 'client-fichiers', 'bz-legacy', 'bz-pack'),
    [t(f'{N} montures, toutes illustrées par l’icône du jeu.', f'{N} mounts, all illustrated with the game icon.', 'client-fichiers'),
     t('2 obtentions officielles : Rênes d’ours spectral (héritage) et Fièregriffe céruléenne (pack des Éolides).', '2 official acquisitions: Reins of the Spectral Bear (Legacy) and Cerulean Prideclaw (Skyborne pack).', 'bz-legacy', 'bz-pack'),
     t(f'{n("montures-echange")} montures rapides données au choix par des quêtes d’échange, et {n("montures-classe")} montures de classe (sorts) : quêtes et PNJ à confirmer.', f'{n("montures-echange")} swift mounts offered by exchange quests, and {n("montures-classe")} class mounts (spells): quests and NPCs to be confirmed.', 'client-quetes'),
     t('Les montures sans obtention connue sont rangées par faction et par niveau requis, avec le prix inscrit dans les fichiers du jeu.', 'Mounts without known acquisition are sorted by faction and required level, with the price recorded in the game files.', 'client-fichiers')],
    HIST(secs),
    [t('Rênes d’ours spectral : récompense d’héritage du lancement. Fièregriffe céruléenne : pack héroïque des Éolides.', 'Reins of the Spectral Bear: launch Legacy reward. Cerulean Prideclaw: Skyborne Heroic Pack.', 'bz-legacy', 'bz-pack'),
     t('Correctif du 10 novembre 2026 : montures de vendeur racial liées quand ramassées.', 'Hotfix of 10 November 2026: racial vendor mounts bind on pickup.', 'bz-hotfixes')],
    [{'fr': 'Vendeurs, zones et prix réels en jeu des montures sans obtention indiquée : non publiés par Blizzard, absents des fichiers du jeu.', 'en': 'Vendors, zones and real in-game prices of mounts without stated acquisition: not published by Blizzard, absent from the game files.'},
     {'fr': 'Quêtes d’échange et quêtes de classe : données de quêtes complétées par des joueurs, à confirmer en jeu.', 'en': 'Exchange and class quests: quest data completed by players, to be confirmed in game.'},
     {'fr': 'Palier de points d’héritage pour les Rênes d’ours spectral : non publié.', 'en': 'Legacy point threshold for the Reins of the Spectral Bear: not published.'}],
    [d for d in DATES if d['src'][0] in ('bz-legacy', 'bz-pack', 'bz-hotfixes')])
out.append(('rev', revise('forever-items-mounts', description={'fr': f'Les {N} montures de WoW Forever, illustrées par l’icône du jeu, avec nom officiel FR/EN, faction, niveau, prix et moyen d’obtention quand il est connu ({nk}).', 'en': f'The {N} WoW Forever mounts, illustrated with the game icon, with official FR/EN name, faction, level, price and acquisition when known ({nk}).'},
    article=art, sources=srcs('bz-legacy', 'bz-pack', 'bz-hotfixes', 'client-fichiers', 'client-quetes'), relations=['forever-items-collections', 'forever-legacy-rewards', 'forever-items-pets', 'forever-items-toys'])))

# ---------- pets ----------
pm = ENT['forever-items-pets']; NP = C['pets']; pk = C['pets_known']
pg = [('mascottes-heritage', 'heritage', 'Héritage', 'Legacy', 'Récompense d’héritage du lancement (officiel).', 'Launch Legacy reward (official).', ['bz-legacy', 'client-fichiers']),
      ('mascottes-abonnement', 'abonnement', 'Abonnement', 'Subscription', 'Bonus officiel de l’offre d’abonnement 6 ou 12 mois. L’objet n’apparaît pas dans les fichiers du jeu lisibles : pas d’image.', 'Official bonus of the 6- or 12-month subscription offer. The item does not appear in the readable game files: no image.', ['bz-sub-year']),
      ('mascottes-artisanat', 'artisanat', 'Artisanat', 'Crafting', 'Mascottes fabriquées par un métier : recette lue dans les fichiers du jeu (niveau de compétence requis non indiqué).', 'Pets made by a profession: recipe read from the game files (required skill level not given).', ['client-fichiers']),
      ('mascottes-quete', 'quetes', 'Récompenses de quête', 'Quest rewards', 'Mascottes données par une quête. Données de quêtes, à confirmer.', 'Pets given by a quest. Quest data, to be confirmed.', ['client-fichiers', 'client-quetes']),
      ('mascottes-reputation', 'reputation', 'Réputation', 'Reputation', 'Mascotte qui exige un niveau de réputation (fichiers du jeu).', 'Pet that requires a reputation standing (game files).', ['client-fichiers']),
      ('mascottes-non-indique', 'obtention-non-indiquee', 'Obtention non indiquée', 'Acquisition not given', 'Mascottes présentes dans les fichiers du jeu ; leur obtention n’y figure pas.', 'Pets present in the game files; their acquisition is not given there.', ['client-fichiers'])]
secs = [sec('lire-cette-liste', 'Comment lire cette liste', 'How to read this list', [t(READ_FR, READ_EN, 'client-fichiers', 'client-quetes'), ICON_NOTE]),
        sec('par-obtention', 'Par moyen d’obtention', 'By acquisition', [{'type': 'table', 'caption': {'fr': 'Nombre de mascottes par groupe', 'en': 'Number of pets per group'},
            'head': [{'fr': 'Groupe', 'en': 'Group'}, {'fr': 'Mascottes', 'en': 'Pets'}], 'rows': [[{'fr': g[2], 'en': g[3]}, {'fr': str(n(g[0])), 'en': str(n(g[0]))}] for g in pg], 'src': ['client-fichiers']}])]
for ref, sid, fr, en, dfr, den, src in pg: secs.append(sec(sid, f'{fr} — {n(ref)}', f'{en} — {n(ref)}', [coll(ref, dfr, den, *src)]))
art = base_article(pm, t(f'{NP} mascottes de WoW Forever avec l’icône du jeu, le nom officiel français et anglais, le prix inscrit dans les fichiers du jeu et l’obtention quand elle est connue ({pk}). Deux obtentions sont officielles : Ourson spectral (héritage) et Azurbie (abonnement).',
                         f'{NP} WoW Forever companion pets with the game icon, official French and English name, price recorded in the game files and acquisition when known ({pk}). Two acquisitions are official: Spectral Bear Cub (Legacy) and Azurky (subscription).', 'client-fichiers', 'bz-legacy', 'bz-sub-year'),
    [t(f'{NP} mascottes, dont {NP - 1} illustrées par l’icône du jeu (Azurbie : pas d’image disponible).', f'{NP} pets, {NP - 1} of them illustrated with the game icon (Azurky: no image available).', 'client-fichiers', 'bz-sub-year'),
     t(f'{n("mascottes-artisanat")} mascottes fabriquées par l’ingénierie et {n("mascottes-quete")} récompenses de quête (à confirmer).', f'{n("mascottes-artisanat")} pets crafted with Engineering and {n("mascottes-quete")} quest rewards (to be confirmed).', 'client-fichiers', 'client-quetes'),
     t('Écureuil trombenoire : réputation Révéré auprès des Druides de la Griffe nocturne (fichiers du jeu).', 'Shadowgale Squirrel: Revered with the Nightclaw Druids (game files).', 'client-fichiers')],
    HIST(secs),
    [t('Ourson spectral : récompense d’héritage du lancement.', 'Spectral Bear Cub: launch Legacy reward.', 'bz-legacy'), t('Azurbie : bonus de l’offre d’abonnement 6 ou 12 mois.', 'Azurky: bonus of the 6- or 12-month subscription offer.', 'bz-sub-year')],
    [{'fr': 'Obtention de la plupart des mascottes (vendeur, butin, événement) : non indiquée dans les fichiers du jeu ni par Blizzard.', 'en': 'Acquisition of most pets (vendor, loot, event): not given in the game files nor by Blizzard.'},
     {'fr': 'Mascottes du pack épique des Éolides : non nommées par Blizzard.', 'en': 'Skyborne Epic Pack pets: not named by Blizzard.'}],
    [d for d in DATES if d['src'][0] in ('bz-legacy', 'bz-sub-year')])
out.append(('rev', revise('forever-items-pets', description={'fr': f'Les {NP} mascottes de WoW Forever, illustrées par l’icône du jeu, avec nom officiel FR/EN, prix et moyen d’obtention quand il est connu ({pk}).', 'en': f'The {NP} WoW Forever companion pets, illustrated with the game icon, with official FR/EN name, price and acquisition when known ({pk}).'},
    article=art, sources=srcs('bz-legacy', 'bz-sub-year', 'client-fichiers', 'client-quetes'), relations=['forever-items-collections', 'forever-legacy-rewards', 'forever-items-mounts', 'forever-items-toys'])))

# ---------- toys ----------
tm = ENT['forever-items-toys']; NT = C['toys']; tk = C['toys_known']
tg = [('jouets-heritage', 'heritage', 'Héritage', 'Legacy', 'Récompense d’héritage du lancement (officiel) ; dans les fichiers du jeu, le jouet s’appelle « Réplique de carabine à air comprimé de Forgefer dans son étui ».', 'Launch Legacy reward (official); in the game files the toy is named “Holstered Replica Ironforge Air Rifle”.', ['bz-legacy', 'client-fichiers']),
      ('jouets-pack', 'pack-boutique', 'Pack boutique', 'Shop pack', 'Jouet inclus dans les packs des Éolides (officiel).', 'Toy included in the Skyborne packs (official).', ['bz-pack', 'client-fichiers']),
      ('jouets-artisanat', 'artisanat', 'Artisanat', 'Crafting', 'Jouets fabriqués par l’ingénierie : recette lue dans les fichiers du jeu (niveau de compétence requis non indiqué).', 'Toys made with Engineering: recipe read from the game files (required skill level not given).', ['client-fichiers']),
      ('jouets-quete', 'quetes', 'Récompenses de quête', 'Quest rewards', 'Jouets donnés par une quête (fêtes saisonnières, Orneval). Données de quêtes, à confirmer.', 'Toys given by a quest (seasonal festivals, Ashenvale). Quest data, to be confirmed.', ['client-fichiers', 'client-quetes']),
      ('jouets-non-indique', 'obtention-non-indiquee', 'Obtention non indiquée', 'Acquisition not given', 'Jouets présents dans les fichiers du jeu ; leur obtention n’y figure pas.', 'Toys present in the game files; their acquisition is not given there.', ['client-fichiers'])]
secs = [sec('lire-cette-liste', 'Comment lire cette liste', 'How to read this list', [t(READ_FR, READ_EN, 'client-fichiers', 'client-quetes'), ICON_NOTE]),
        sec('par-obtention', 'Par moyen d’obtention', 'By acquisition', [{'type': 'table', 'caption': {'fr': 'Nombre de jouets par groupe', 'en': 'Number of toys per group'},
            'head': [{'fr': 'Groupe', 'en': 'Group'}, {'fr': 'Jouets', 'en': 'Toys'}], 'rows': [[{'fr': g[2], 'en': g[3]}, {'fr': str(n(g[0])), 'en': str(n(g[0]))}] for g in tg], 'src': ['client-fichiers']}])]
for ref, sid, fr, en, dfr, den, src in tg: secs.append(sec(sid, f'{fr} — {n(ref)}', f'{en} — {n(ref)}', [coll(ref, dfr, den, *src)]))
art = base_article(tm, t(f'{NT} jouets de WoW Forever (table des jouets des fichiers du jeu) avec l’icône du jeu, le nom officiel français et anglais et l’obtention quand elle est connue ({tk}).',
                         f'{NT} WoW Forever toys (toy table of the game files) with the game icon, official French and English name and acquisition when known ({tk}).', 'client-fichiers'),
    [t(f'{NT} jouets, tous illustrés par l’icône du jeu.', f'{NT} toys, all illustrated with the game icon.', 'client-fichiers'),
     t('Officiels : la réplique de carabine de Forgefer (héritage) et le Puits de vent shen’dorei (pack des Éolides).', 'Official: the Ironforge air rifle replica (Legacy) and the Shen’dorei Windwell (Skyborne pack).', 'bz-legacy', 'bz-pack'),
     t(f'{n("jouets-artisanat")} jouets fabriqués par l’ingénierie, avec la recette (fichiers du jeu).', f'{n("jouets-artisanat")} toys made with Engineering, with the recipe (game files).', 'client-fichiers')],
    HIST(secs),
    [t('Réplique de carabine à air comprimé de Forgefer : récompense d’héritage du lancement.', 'Replica Ironforge Air Rifle: launch Legacy reward.', 'bz-legacy'), t('Puits de vent shen’dorei : pack héroïque des Éolides.', 'Shen’dorei Windwell: Skyborne Heroic Pack.', 'bz-pack')],
    [{'fr': 'Obtention des jouets sans indication (vendeur, butin) : non publiée.', 'en': 'Acquisition of toys without indication (vendor, loot): not published.'},
     {'fr': 'Quêtes de fête et d’Orneval : données de quêtes, à confirmer.', 'en': 'Festival and Ashenvale quests: quest data, to be confirmed.'}],
    [d for d in DATES if d['src'][0] in ('bz-legacy', 'bz-pack')])
out.append(('rev', revise('forever-items-toys', description={'fr': f'Les {NT} jouets de WoW Forever, illustrés par l’icône du jeu, avec nom officiel FR/EN et moyen d’obtention quand il est connu ({tk}).', 'en': f'The {NT} WoW Forever toys, illustrated with the game icon, with official FR/EN name and acquisition when known ({tk}).'},
    article=art, sources=srcs('bz-legacy', 'bz-pack', 'client-fichiers', 'client-quetes'), relations=['forever-items-collections', 'forever-legacy-rewards', 'forever-items-mounts', 'forever-items-pets'])))

# ---------- heritage ----------
hm = ENT['forever-legacy-rewards']
old_secs = [s for s in hm['article']['sections'] if s['id'] == 'liste']
secs = [sec('illustrees', 'Les quatre récompenses, illustrées', 'The four rewards, illustrated', [coll('heritage-lancement',
            'Les quatre récompenses du lancement avec leur icône du jeu et leurs données des fichiers du jeu (client 1.60.1.70862). Chaque récompense a aussi une quête « Legacy Reward » dans les données de quêtes (à confirmer).',
            'The four launch rewards with their game icon and game-file data (client 1.60.1.70862). Each reward also has a “Legacy Reward” quest in the quest data (to be confirmed).', 'bz-legacy', 'client-fichiers', 'client-quetes')])] + old_secs + [
        sec('collections', 'Toutes les collections', 'All collections', [t('Toutes les montures, mascottes et jouets, avec image du jeu et obtention : /fr/objets/collections/ (montures : /fr/objets/montures/, mascottes : /fr/objets/mascottes/, jouets : /fr/objets/jouets/).',
            'All mounts, pets and toys, with game image and acquisition: /en/items/collections/ (mounts: /en/items/mounts/, pets: /en/items/companion-pets/, toys: /en/items/toys/).', 'client-fichiers')])]
art = copy.deepcopy(hm['article']); art['sections'] = HIST(secs); art['noAmbiance'] = True
art['keyPoints'] = hm['article']['keyPoints'] + [t('Icônes du jeu affichées pour les quatre récompenses (fichiers du jeu, client 1.60.1.70862).', 'Game icons shown for all four rewards (game files, client 1.60.1.70862).', 'client-fichiers')]
art['pending'] = hm['article'].get('pending', []) + [{'fr': 'Quête « Legacy Reward » de chaque récompense : vue dans les données de quêtes, sans PNJ ni lieu ; à confirmer en jeu.', 'en': '“Legacy Reward” quest of each reward: seen in the quest data, without NPC or location; to be confirmed in game.'}]
hs = [s for s in hm['sources']] + srcs('client-fichiers', 'client-quetes')
out.append(('rev', revise('forever-legacy-rewards', article=art, sources=hs, relations=list(dict.fromkeys(['forever-items-collections'] + hm.get('relations', []))))))

# ---------- hub (new) ----------
hub = {'id': 'forever-items-collections', 'title': {'fr': 'Collections : montures, mascottes, jouets et héritage', 'en': 'Collections: mounts, pets, toys and Legacy'},
       'category': 'items', 'subcategory': 'collections',
       'description': {'fr': f'La rubrique des collections de WoW Forever : {C["mounts"]} montures, {C["pets"]} mascottes et {C["toys"]} jouets illustrés par l’image du jeu, avec leur moyen d’obtention, plus les récompenses d’héritage.',
                       'en': f'The WoW Forever collections section: {C["mounts"]} mounts, {C["pets"]} pets and {C["toys"]} toys illustrated with the game image, with how to get them, plus the Legacy rewards.'},
       'sources': srcs('bz-legacy', 'bz-pack', 'bz-sub-year', 'bz-hotfixes', 'client-fichiers', 'client-quetes'), 'status': 'draft', 'identityConfirmed': False,
       'updatedAt': NOW, 'version': 1, 'gameVersion': GV, 'relations': ['forever-items-mounts', 'forever-items-pets', 'forever-items-toys', 'forever-legacy-rewards'],
       'history': [{'at': NOW, 'actor': 'GrokBot', 'note': 'v41 (t403u) : brouillon de la rubrique Collections (test, non publié).', 'version': 1}],
       'article': {'format': 1, 'slug': {'fr': 'collections', 'en': 'collections'}, 'illustration': 'items', 'noAmbiance': True,
         'lead': t(f'Tout ce qui se collectionne dans WoW Forever, au même endroit : {C["mounts"]} montures, {C["pets"]} mascottes, {C["toys"]} jouets et les récompenses d’héritage. Chaque élément a sa fiche avec l’image du jeu, son nom officiel en français et en anglais, et son moyen d’obtention quand il est connu.',
                   f'Everything collectible in WoW Forever in one place: {C["mounts"]} mounts, {C["pets"]} pets, {C["toys"]} toys and the Legacy rewards. Each entry has its card with the game image, its official French and English name, and how to get it when known.', 'client-fichiers', 'bz-legacy'),
         'keyPoints': [t(f'{C["img"]} fiches sur {C["mounts"] + C["pets"] + C["toys"]} ont l’icône officielle du jeu ; Azurbie n’a pas d’image (absente des fichiers du jeu lisibles).', f'{C["img"]} of {C["mounts"] + C["pets"] + C["toys"]} cards have the official game icon; Azurky has no image (absent from the readable game files).', 'client-fichiers', 'bz-sub-year'),
                       t(f'Obtention indiquée pour {C["mounts_known"]} montures, {C["pets_known"]} mascottes et {C["toys_known"]} jouets ; les autres sont rangés par faction et niveau, sans rien inventer.', f'Acquisition given for {C["mounts_known"]} mounts, {C["pets_known"]} pets and {C["toys_known"]} toys; the others are sorted by faction and level, without inventing anything.', 'client-fichiers', 'client-quetes'),
                       t('Quatre récompenses d’héritage au lancement : jouet, mascotte, tabard et monture.', 'Four Legacy rewards at launch: toy, pet, tabard and mount.', 'bz-legacy')],
         'sections': [sec('rubriques', 'Les quatre collections', 'The four collections', [coll('hub', 'Choisissez une collection : chaque page regroupe les fiches par moyen d’obtention.', 'Pick a collection: each page groups the cards by acquisition.', 'client-fichiers', 'bz-legacy')]),
                      sec('obtention', 'Moyens d’obtention', 'Ways to get them', [{'type': 'table', 'caption': {'fr': 'Nombre de fiches par moyen d’obtention', 'en': 'Number of cards per acquisition'},
                          'head': [{'fr': 'Obtention', 'en': 'Acquisition'}, {'fr': 'Montures', 'en': 'Mounts'}, {'fr': 'Mascottes', 'en': 'Pets'}, {'fr': 'Jouets', 'en': 'Toys'}],
                          'rows': [[{'fr': a, 'en': b}] + [{'fr': str(v), 'en': str(v)} for v in vals] for a, b, vals in [
                              ('Héritage (officiel)', 'Legacy (official)', (n('montures-heritage'), n('mascottes-heritage'), n('jouets-heritage'))),
                              ('Pack boutique (officiel)', 'Shop pack (official)', (n('montures-pack'), 0, n('jouets-pack'))),
                              ('Abonnement (officiel)', 'Subscription (official)', (0, n('mascottes-abonnement'), 0)),
                              ('Sort de classe (quête à confirmer)', 'Class spell (quest to be confirmed)', (n('montures-classe'), 0, 0)),
                              ('Quête (à confirmer)', 'Quest (to be confirmed)', (n('montures-echange'), n('mascottes-quete'), n('jouets-quete'))),
                              ('Artisanat (fichiers du jeu)', 'Crafting (game files)', (0, n('mascottes-artisanat'), n('jouets-artisanat'))),
                              ('Réputation (fichiers du jeu)', 'Reputation (game files)', (0, n('mascottes-reputation'), 0)),
                              ('Non indiquée', 'Not given', (C['mounts'] - C['mounts_known'], n('mascottes-non-indique'), n('jouets-non-indique')))]],
                          'src': ['client-fichiers', 'client-quetes', 'bz-legacy', 'bz-pack', 'bz-sub-year']}]),
                      sec('images', 'Images et données', 'Images and data', [ICON_NOTE, t(READ_FR, READ_EN, 'client-fichiers', 'client-quetes')])],
         'confirmed': [t('Quatre récompenses d’héritage au lancement (jouet, mascotte, tabard, monture).', 'Four Legacy rewards at launch (toy, pet, tabard, mount).', 'bz-legacy'),
                       t('Fièregriffe céruléenne et Puits de vent shen’dorei : packs des Éolides. Azurbie : bonus d’abonnement.', 'Cerulean Prideclaw and Shen’dorei Windwell: Skyborne packs. Azurky: subscription bonus.', 'bz-pack', 'bz-sub-year')],
         'pending': [{'fr': 'Obtention de la plupart des montures, mascottes et jouets : non publiée par Blizzard et absente des fichiers du jeu.', 'en': 'Acquisition of most mounts, pets and toys: not published by Blizzard and absent from the game files.'},
                     {'fr': 'Quêtes, PNJ et zones : données de quêtes complétées par des joueurs, à confirmer en jeu.', 'en': 'Quests, NPCs and zones: quest data completed by players, to be confirmed in game.'}],
         'dates': DATES}}
out.append(('new', hub))
for kind, e in out:
    (OUT / f'{kind}-{e["id"]}.json').write_text(json.dumps(e, ensure_ascii=False, indent=1))
print([f'{k}:{e["id"]}' for k, e in out])
