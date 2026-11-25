#!/usr/bin/env python3
"""Lot 2 « monde » (étape 04) — environnement de test isolé uniquement.
Sources : pages officielles Blizzard (news.blizzard.com FR/EN, forums officiels US/EU) consultées le 2026-11-09
(copies brutes dans etape-04/sources-brutes/). Aucune donnée Eternadex, Wowhead, *.wiki.gg ou extraite du client.
Produit :
  lot2.entries.json            4 nouvelles fiches (brouillons) à importer avec scripts/import.mjs
  revisions/<id>.json          9 fiches donjon existantes enrichies, à appliquer avec scripts/review.mjs revise
Usage : python3 build_lot2.py <runtime/entries.json de départ (v32)>"""
import json, pathlib, sys, unicodedata, re, copy
HERE = pathlib.Path(__file__).resolve().parent
GV = 'World of Warcraft: Forever — annonces et notes officielles, état documentaire 2026-11-09'
LIC = 'Droits réservés Blizzard ; référence et synthèse originale (courtes citations), mention © Blizzard Entertainment conservée ; site non commercial.'
ACC = '2026-11-09'
ACTOR = 'GrokBot — lot 2 étape 04 (environnement de test isolé)'
def src(key, lang, url, title, pub):
    return {'key': key, 'language': lang, 'url': url, 'title': title, 'publishedAt': pub, 'accessedAt': ACC, 'license': LIC, 'gameVersion': GV}
DUNG = [src('bz-dungeons-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24301455/decouvrez-les-nouveaux-donjons-de-world-of-warcraft-forever', 'Découvrez les nouveaux donjons de World of Warcraft: Forever', '2026-10-20'),
        src('bz-dungeons-en', 'en', 'https://news.blizzard.com/en-us/article/24301455/explore-the-new-dungeons-of-world-of-warcraft-forever', 'Explore the New Dungeons of World of Warcraft: Forever', '2026-10-20')]
RAIDS = [src('bz-raids-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24303009/apercu-des-raids-de-world-of-warcraft-forever-emplacements-taille-des-raids-et-harmonisation', 'Aperçu des raids de World of Warcraft: Forever – Emplacements, taille des raids et harmonisation', '2026-10-20'),
         src('bz-raids-en', 'en', 'https://news.blizzard.com/en-us/article/24303009/world-of-warcraft-forever-raid-overviewlocations-raid-sizes-and-attunement', 'World of Warcraft: Forever Raid Overview—Locations, Raid Sizes, and Attunement', '2026-10-20')]
DIVE = [src('bz-dive-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24303313/recapitulatif-de-la-presentation-au-cur-de-world-of-warcraft-forever', 'Récapitulatif de la présentation « Au cœur de World of Warcraft: Forever »', '2026-09-13'),
        src('bz-dive-en', 'en', 'https://news.blizzard.com/en-us/article/24303313/world-of-warcraft-forever-deep-dive-panel-recap', 'World of Warcraft: Forever Deep Dive Panel Recap', '2026-09-13')]
CAMP = [src('bz-camp-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24301516/retrouvez-vous-autour-dun-feu-de-camp-dans-world-of-warcraft-forever', 'Retrouvez-vous autour d’un feu de camp dans World of Warcraft: Forever', '2026-10-21'),
        src('bz-camp-en', 'en', 'https://news.blizzard.com/en-us/article/24301516/gather-around-the-campfire-in-world-of-warcraft-forever', 'Gather Around the Campfire in World of Warcraft: Forever', '2026-10-21')]
LEG = [src('bz-legacy-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24307383/decouvrez-le-systeme-dheritage-de-world-of-warcraft-forever', 'Découvrez le système d’héritage de World of Warcraft: Forever', '2026-09-23'),
       src('bz-legacy-en', 'en', 'https://news.blizzard.com/en-us/article/24307383/get-to-know-the-world-of-warcraft-forever-legacy-system', 'Get to Know the World of Warcraft: Forever Legacy System', '2026-09-23')]
LIVE = [src('bz-golive-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24315820/world-of-warcraft-forever-sort-partout-dans-le-monde-le-5-novembre', 'World of Warcraft: Forever est disponible !', '2026-11-04'),
        src('bz-golive-en', 'en', 'https://news.blizzard.com/en-us/article/24315820', 'World of Warcraft: Forever Now Live!', '2026-11-04')]
PHOTOS = [src('bz-photos-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24304071/recapitulatif-de-la-conference-photos-retrouvees-de-world-of-warcraft-forever', 'Récapitulatif de la conférence « Photos retrouvées de World of Warcraft: Forever »', '2026-09-13'),
          src('bz-photos-en', 'en', 'https://news.blizzard.com/en-us/article/24304071/world-of-warcraft-forever-found-photos-panel-recap', 'World of Warcraft: Forever Found Photos Panel Recap', '2026-09-13')]
HOT = [src('bz-hotfixes-en', 'en', 'https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-6-2026', 'WoW: Forever Hotfixes - November 6, 2026 (correctifs des 5 et 6 novembre)', '2026-11-06'),
       src('bz-hotfixes-eu', 'en', 'https://eu.forums.blizzard.com/en/wow/t/639885', 'WoW: Forever Hotfixes - November 6, 2026 — forum officiel EU (Kaivax)', '2026-11-06')]
def dev(n, date):
    return [src(f'bz-devnotes{n}', 'en', f'https://us.forums.blizzard.com/en/wow/t/2360696/{n}', f'WoW Forever Beta Development Notes — message n° {n} du {date} (forum officiel US, Kaivax)', date)]
DEV1, DEV4, DEV5, DEV6, DEV9 = dev(1, '2026-09-24'), dev(4, '2026-10-01'), dev(5, '2026-10-08'), dev(6, '2026-10-16'), dev(9, '2026-11-03')

def C(fr, en): return {'fr': fr, 'en': en}
def P(fr, en, s): return {'type': 'p', 'fr': fr, 'en': en, 'src': s}
def L(items, s): return {'type': 'list', 'items': [{'fr': a, 'en': b, 'src': s} for a, b in items], 'src': s}
def LS(items): return {'type': 'list', 'items': [{'fr': a, 'en': b, 'src': s} for a, b, s in items], 'src': sorted({k for _, _, s in items for k in s})}
def T(cap, head, rows, s): return {'type': 'table', 'caption': C(*cap), 'head': [C(*h) for h in head], 'rows': [[C(*c) for c in r] for r in rows], 'src': s}
def K(fr, en, s): return {'fr': fr, 'en': en, 'src': s}
S = lambda id, t, blocks: {'id': id, 'title': C(*t), 'blocks': blocks}
def art(slug, ill, lead, kps, sections, confirmed, pending, dates=None):
    a = {'format': 1, 'slug': C(*slug), 'illustration': ill, 'lead': lead, 'keyPoints': kps, 'sections': sections, 'confirmed': confirmed, 'pending': pending}
    if dates: a['dates'] = dates
    return a
HIST_NOTE = ('Fiche rédigée uniquement à partir des sources officielles Blizzard citées (synthèse originale, noms repris tels quels ; '
             'noms anglais conservés quand aucune traduction française officielle n’a été publiée). Relecture humaine de Mathieu requise avant toute mise en production.')
def entry(id, cat, sub, title, desc, sources, relations, article):
    return {'id': id, 'title': C(*title), 'description': C(*desc), 'category': cat, 'subcategory': sub, 'sources': sources, 'status': 'draft',
            'updatedAt': ACC, 'gameVersion': GV, 'version': 1, 'relations': relations, 'verification': 'officiel confirmé',
            'history': [{'at': ACC, 'actor': ACTOR, 'note': HIST_NOTE, 'version': 1}], 'article': article}
dg, rd, dv, cp, lg, lv, ph, hf = ['bz-dungeons'], ['bz-raids'], ['bz-dive'], ['bz-camp'], ['bz-legacy'], ['bz-golive'], ['bz-photos'], ['bz-hotfixes']
d1, d4, d5, d6, d9 = ['bz-devnotes1'], ['bz-devnotes4'], ['bz-devnotes5'], ['bz-devnotes6'], ['bz-devnotes9']
BETA_FR = 'Note de bêta (avant le lancement du 4 novembre) : peut avoir évolué depuis.'
BETA_EN = 'Beta note (before the 4 November launch): may have changed since.'

# Bloc commun aux 9 donjons : ce que Blizzard dit du butin de donjon en général.
LOOT_BLOCKS = [
  P('Blizzard indique que tout le butin des donjons a été réexaminé et que des centaines de nouveaux objets ont été ajoutés ; les objets uniques des boss de donjon sont désormais de qualité bleue (rare) et les bonus d’ensemble ont été améliorés. Quand un objet inhabituel ou rare lié quand ramassé tombe en donjon, son apparence est accordée à tous les membres éligibles du groupe.',
    'Blizzard says every dungeon drop has been re-examined and hundreds of new drops added; unique dungeon boss items are now blue (Rare) quality and set bonuses have been improved. When a bind-on-pickup Uncommon or Rare item drops in a dungeon, its appearance is granted to every eligible looter.', dv),
  P('Les plans avancés d’objets de campement proviennent de certains boss de donjon, sans que Blizzard précise lesquels.', 'Advanced camp feature blueprints drop from specific dungeon bosses; Blizzard does not say which ones.', cp)]
LOOT_PENDING = [C('Liste des boss, table de butin et taux d’obtention : non publiés par Blizzard ; ce wiki ne reprend pas de bases tierces ni de données extraites du client.',
                  'Boss list, loot table and drop rates: not published by Blizzard; this wiki does not reuse third-party databases or client-extracted data.')]

def slugify(v):
    v = unicodedata.normalize('NFD', v); v = ''.join(c for c in v if not unicodedata.combining(c)).lower()
    v = re.sub(r"[’'`]", '-', v); v = re.sub(r'[^a-z0-9]+', '-', v).strip('-'); v = re.sub(r'-{2,}', '-', v)
    return v[:80].rstrip('-')

# ---------- B. Donjons : 9 fiches existantes enrichies (révision, pas de doublon) ----------
# (id, levels_fr, levels_en, place_fr, place_en, access_fr, access_en, story_fr, story_en, extra_sections, extra_sources, extra_conf, extra_pending, extra_rel, dates)
D = {}
D['forever-dungeon-hall-of-thanes'] = dict(
  lv=('13 à 18', '13–18'), place=('Sous Forgefer, en Dun Morogh', 'Beneath Ironforge, Dun Morogh'),
  acc=('Entrée facile pour l’Alliance depuis sa capitale ; la Horde doit traverser le territoire ennemi.', 'Easy for the Alliance from its capital; the Horde must cross enemy territory.'),
  story=('Dernière demeure des monarques nains, la salle des Thanes a été envahie par des intrus que l’on soupçonne d’appartenir aux Nains sombrefer. Le groupe doit les chasser et découvrir ce qui s’est réveillé dans ces salles, où résonnent encore des murmures fantomatiques.',
         'The resting place of the dwarven monarchs has been broken into by intruders suspected to be Dark Iron dwarves. Your group must drive them out and find out what has stirred in these halls, where ghostly whispers still echo.'),
  kp3=('Plus bas donjon des neuf nouveautés : niveaux 13 à 18.', 'Lowest-level of the nine new dungeons: levels 13–18.'))
D['forever-dungeon-ruins-of-lordaeron'] = dict(
  lv=('15 à 20', '15–20'), place=('Cité en ruine au-dessus de Fossoyeuse, clairières de Tirisfal', 'Ruined city above the Undercity, Tirisfal Glades'),
  acc=('Entrée facile pour la Horde depuis Fossoyeuse ; l’Alliance doit traverser le territoire ennemi.', 'Easy for the Horde from the Undercity; the Alliance must cross enemy territory.'),
  story=('Les Réprouvés tentent de reprendre les ruines de Lordaeron, hantées par le Fléau, où reposent encore souvenirs et objets de valeur. Un nécromancien y gagnerait en puissance : le groupe doit sécuriser la cité et affronter cette menace.',
         'The Forsaken are trying to reclaim the Scourge-haunted ruins of Lordaeron, where keepsakes and memories still lie. A necromancer is reportedly gathering power there, and your group must secure the city and face that threat.'),
  kp3=('Une rencontre est nommée par Blizzard : The Baron (nom anglais), dont la Tête abominable lance une quête pour la Horde.', 'One encounter is named by Blizzard: The Baron, whose Abominable Head starts a quest for the Horde.'),
  extra=[S('quetes', ('Quêtes et rencontre nommées par Blizzard', 'Quests and encounter named by Blizzard'), [
     LS([('The Baron (nom anglais ; traduction officielle non publiée) laisse tomber l’objet « Abomimable Head » (graphie des notes), qui propose la quête « Unending Torment » aux joueurs de la Horde dès le niveau 15 (16 auparavant) — correctif du 6 novembre 2026.', 'The Baron drops the “Abomimable Head” (as spelled in the notes), which offers the quest “Unending Torment” to Horde players from level 15 (was 16) — 6 November 2026 hotfix.', hf),
         ('Toutes les quêtes du donjon demandent désormais au minimum le niveau 15 (auparavant 15 ou 16) et certains prérequis ont été ajustés — notes du 3 novembre 2026.', 'All of the dungeon’s quests now require at least level 15 (was a mix of 15 and 16) and some prerequisites were adjusted — 3 November 2026 notes.', d9),
         ('Quête « A Frightened Request » rangée sous le donjon dans le journal de quêtes ; correction d’un problème qui donnait plusieurs exemplaires de l’objet de quête « Bloodied Insignia ». ' + BETA_FR, '“A Frightened Request” quest sorted under the dungeon in the quest log; fixed players receiving multiple copies of the “Bloodied Insignia” quest item. ' + BETA_EN, d4)])])],
  srcs=HOT + DEV4 + DEV9, rel=['forever-news-hotfixes-nov5-6'],
  conf=[K('The Baron et la quête « Unending Torment » (Horde, niveau 15).', 'The Baron and the “Unending Torment” quest (Horde, level 15).', hf), K('Quêtes du donjon : niveau 15 minimum.', 'Dungeon quests: level 15 minimum.', d9)],
  pend=[C('Nom et rôle du nécromancien, autres rencontres : non publiés.', 'The necromancer’s name and role, other encounters: not published.')],
  dates=[{'date': '2026-11-03', 'fr': 'Quêtes du donjon harmonisées au niveau 15.', 'en': 'Dungeon quests aligned at level 15.', 'src': d9},
         {'date': '2026-11-06', 'fr': 'Correctif : « Unending Torment » dès le niveau 15 pour la Horde.', 'en': 'Hotfix: “Unending Torment” from level 15 for the Horde.', 'src': hf}])
D['forever-dungeon-excavation-site'] = dict(
  lv=('24 à 29', '24–29'), place=('Près du rocher de Thelgen et de Dun Algaz, dans les Paluns', 'Near Thelgen Rock and Dun Algaz, Wetlands'),
  acc=('Blizzard ne publie pas de note d’accès propre à une faction.', 'Blizzard publishes no faction-specific access note.'),
  story=('Une brume étrange descend des montagnes au-dessus des excavations de Whelgar, avec des éclairs à l’horizon. Au-delà du chantier s’étend un lieu figé dans le temps, gardé par des assemblages titans errants et une faune dangereuse, de quoi attirer la Ligue des explorateurs.',
         'A strange mist drifts down from the mountains above Whelgar’s Excavation, with flashes of light on the horizon. Beyond the dig lies a place frozen in time, guarded by errant titan constructs and dangerous wildlife — enough to draw the Explorers’ League.'),
  kp3=('Écart de niveaux entre la bêta (26 à 31 le 1er octobre) et l’article du 20 octobre (24 à 29) : ce wiki retient l’article le plus récent.', 'Level gap between the beta (26–31 on 1 October) and the 20 October article (24–29): this wiki keeps the most recent article.', d4 + dg),
  extra=[S('quetes', ('Quêtes citées par les notes officielles', 'Quests cited in the official notes'), [
     LS([('Rubrique « Excavation Site: Wetlands » des notes du 8 octobre : l’objet « Titan Relic » obtenu avec « Elder Knowledge » ou « Lost Relic Carry » est rendu pour les suites « Earthen Echo » ou « Prehistoric Prism » ; inutile d’obtenir une seconde relique. ' + BETA_FR,
          '“Excavation Site: Wetlands” section of the 8 October notes: the Titan Relic from “Elder Knowledge” or “Lost Relic Carry” is given back for the follow-ups “Earthen Echo” or “Prehistoric Prism”, so you do not need another relic. ' + BETA_EN, d5),
         ('Le donjon est apparu en bêta le 1er octobre sous le nom « Excavation Site: Wetlands », annoncé alors pour les niveaux 26 à 31.', 'The dungeon arrived in the beta on 1 October as “Excavation Site: Wetlands”, then listed for levels 26–31.', d4)])])],
  srcs=DEV4 + DEV5, conf=[K('Quêtes « Elder Knowledge », « Lost Relic Carry », « Earthen Echo », « Prehistoric Prism » (titres anglais des notes).', 'Quests “Elder Knowledge”, “Lost Relic Carry”, “Earthen Echo”, “Prehistoric Prism” (English titles from the notes).', d5)],
  pend=[C('Titres français officiels de ces quêtes : non publiés.', 'Official French titles for these quests: not published.')],
  dates=[{'date': '2026-10-01', 'fr': 'Arrivée du donjon en bêta (niveaux 26 à 31).', 'en': 'Dungeon added to the beta (levels 26–31).', 'src': d4}])
D['forever-dungeon-city-of-dalaran'] = dict(
  lv=('28 à 33', '28–33'), place=('Montagnes d’Alterac', 'Alterac Mountains'),
  acc=('Harmonisation obligatoire. Alliance : « Une requête alarmante » (émissaire Jacques, Austrivage). Horde : « Clé de la ville » et « L’invasion de la prison » (magus Wordeen Toisevide, Moulin-de-Tarren).', 'Attunement required. Alliance: “An Alarming Request” (Emissary Jacques, Southshore). Horde: “Key to the City” and “Prison Break-In” (Magus Wordeen Voidglare, Tarren Mill).'),
  story=('La barrière qui cachait la reconstruction de Dalaran est tombée : enchantements qui se retournent, assemblages hors de contrôle, énergies magiques dans les rues. Après avoir gagné la confiance du Kirin Tor, le groupe entre par les égouts et choisit entre plusieurs chemins et rencontres jusqu’à la source des perturbations.',
         'The barrier hiding Dalaran’s restoration has fallen: backfiring enchantments, runaway constructs, magic spilling into the streets. After earning the Kirin Tor’s trust, your group enters through the sewers and picks among several paths and encounters on the way to the source of the trouble.'),
  kp3=('Entrée par les égouts, plusieurs chemins possibles dans la cité.', 'Entry through the sewers, several possible paths through the city.'),
  extra=[S('horde-kirin-tor', ('Horde, Kirin Tor et accès à la ville', 'Horde, Kirin Tor and city access'), [
     LS([('Depuis les notes du 3 novembre, la Horde n’est plus la bienvenue à Dalaran : ses membres y sont attaqués à vue. Cela ne change pas l’accès au donjon, mais la suite de quêtes de la Horde qui donne la clé des égouts de Dalaran (« Dalaran Sewer Key ») n’ouvre plus librement la ville dans le monde extérieur.',
          'Since the 3 November notes, the Horde is no longer welcome in Dalaran and is attacked on sight. Dungeon access is unaffected, but the Horde questline that grants the Dalaran Sewer Key no longer gives unrestricted access to the open-world city.', d9),
         ('Le 16 octobre, Blizzard a corrigé un problème qui permettait aux joueurs de la Horde de gagner de la réputation auprès du Kirin Tor. ' + BETA_FR, 'On 16 October, Blizzard fixed an issue that let Horde players gain Kirin Tor reputation. ' + BETA_EN, d6),
         ('Le donjon est ouvert aux tests de la bêta le 8 octobre ; les invocateurs de Dalaran des montagnes d’Alterac, qui invoquaient sans fin, sont corrigés le 3 novembre.', 'The dungeon opened for beta testing on 8 October; the Dalaran Summoners in the Alterac Mountains, who kept summoning endlessly, were fixed on 3 November.', d5 + d9)])])],
  srcs=DEV5 + DEV6 + DEV9, rel=['forever-questline-dalaran-attunement', 'forever-reputations-confirmed'],
  conf=[K('Accès : harmonisation propre à chaque faction, entrée par les égouts.', 'Access: faction-specific attunement, entry through the sewers.', dg), K('Horde attaquée à vue dans Dalaran (hors donjon) depuis le 3 novembre.', 'Horde attacked on sight in Dalaran (outside the dungeon) since 3 November.', d9)],
  pend=[C('Paliers de réputation Kirin Tor exigés et récompenses : non publiés.', 'Required Kirin Tor standing and rewards: not published.')],
  dates=[{'date': '2026-10-08', 'fr': 'Donjon ouvert aux tests en bêta.', 'en': 'Dungeon opened for beta testing.', 'src': d5}, {'date': '2026-11-03', 'fr': 'La Horde est attaquée à vue dans Dalaran.', 'en': 'The Horde is attacked on sight in Dalaran.', 'src': d9}])
D['forever-dungeon-drowned-city'] = dict(
  lv=('35 à 40', '35–40'), place=('Au large de la vallée de Strangleronce, à l’ouest de Grom’gol', 'Off the coast of Stranglethorn Vale, west of Grom’gol'),
  acc=('Entrée sous l’eau : il faut plonger pour la trouver.', 'Underwater entrance: dive to find it.'),
  story=('D’anciennes ruines trolles englouties sont remontées à la surface. Trolls et nagas y circulent, près d’un navire pirate qui a mal fini. Donjon à ciel ouvert : brume et pluie montent jusqu’à une tempête avant l’affrontement final.',
         'Ancient sunken troll ruins have risen from the sea. Trolls and naga roam them, next to a pirate ship that met a bad end. An open-air dungeon: mist and rain build into a full storm before the final fight.'),
  kp3=('Météo évolutive : brume, pluie puis tempête avant le dernier combat.', 'Evolving weather: mist, rain, then a storm before the last fight.'),
  extra=[S('correctifs', ('Correctifs officiels', 'Official hotfixes'), [
     L([('6 novembre 2026 : le portail d’instance téléporte correctement à l’intérieur de la cité Submergée.', '6 November 2026: the instance portal now correctly teleports you inside The Drowned City.'),
        ('6 novembre 2026 : certaines créatures du donjon ne se désengagent plus à tort du combat.', '6 November 2026: some creatures inside no longer erroneously disengage.')], hf)])],
  srcs=HOT, rel=['forever-news-hotfixes-nov5-6'],
  conf=[K('Portail d’instance et désengagements corrigés le 6 novembre.', 'Instance portal and disengage issues fixed on 6 November.', hf)], pend=[],
  dates=[{'date': '2026-11-06', 'fr': 'Correctifs : portail et désengagement des créatures.', 'en': 'Hotfixes: portal and creature disengage.', 'src': hf}])
D['forever-dungeon-kroldok-stronghold'] = dict(
  lv=('40 à 45', '40–45'), place=('Rives Claires', 'Riverglades'),
  acc=('Blizzard ne publie pas de note d’accès propre à une faction.', 'Blizzard publishes no faction-specific access note.'),
  story=('Des estafettes ogres enlèvent des voyageurs et pillent les communautés des rives Claires. Leur piste mène au bastion Krol’dok, vaste place forte faite d’ateliers, de campements et de passages intérieurs gardés ; d’étranges incantations s’y font entendre la nuit.',
         'Ogre outrunners are kidnapping travelers and raiding communities across the Riverglades. Their trail leads to Krol’dok Stronghold, a sprawling fortress of workshops, encampments and guarded inner passages, where strange chanting is heard after nightfall.'),
  kp3=('Seul des neuf donjons situé dans une nouvelle zone : les rives Claires.', 'The only one of the nine dungeons set in a new zone: the Riverglades.'), rel=['forever-zone-riverglades'])
D['forever-dungeon-alcaz-prison'] = dict(
  lv=('48 à 53', '48–53'), place=('Île d’Alcaz, marécage d’Âprefange', 'Alcaz Island, Dustwallow Marsh'),
  acc=('Blizzard ne publie pas de note d’accès propre à une faction.', 'Blizzard publishes no faction-specific access note.'),
  story=('L’île d’Alcaz est entourée de rumeurs sur des prisonniers de haut rang, dont le roi Varian Wrynn, mais sa prison était inaccessible. Ses portes s’ouvrent enfin : la Confrérie défias et des nagas s’y affrontent, et l’exploration lève un peu plus le voile sur un mystère familier.',
         'Alcaz Island has long been the subject of rumors about high-ranking prisoners, King Varian Wrynn among them, but its prison stayed out of reach. Its doors finally open: the Defias Brotherhood and naga are fighting inside, and exploring it uncovers more of a familiar mystery.'),
  kp3=('Affrontement entre Confrérie défias et nagas à l’intérieur.', 'Defias Brotherhood and naga fighting inside.'))
D['forever-dungeon-blackmaw-hold'] = dict(
  lv=('55 à 60', '55–60'), place=('Azshara, derrière une porte longtemps scellée', 'Azshara, behind a long-sealed gate'),
  acc=('Blizzard ne publie pas de note d’accès propre à une faction.', 'Blizzard publishes no faction-specific access note.'),
  story=('Une grande cité furbolg se cache derrière une porte scellée en Azshara. Le clan des Noiregueules y lutte contre une corruption qui gagne ses bosquets et ses tunnels : une aventure de niveau maximum à plusieurs itinéraires et plusieurs boss, dont les profondeurs mèneraient encore plus bas sous Azeroth.',
         'A great furbolg city lies behind a sealed gate in Azshara. The Blackmaw clan is fighting a corruption spreading through its groves and tunnels: a max-level adventure with several routes and bosses, whose depths may lead even farther below Azeroth.'),
  kp3=('Une des entrées du raid des profondeurs des Saisons est reliée au repaire des Noiregueules.', 'One of the Barrow Deeps raid entrances connects through Blackmaw Hold.', rd),
  extra=[S('profondeurs', ('Lien avec les profondeurs des Saisons', 'Link to the Barrow Deeps'), [
     P('L’aperçu des raids indique que le raid des profondeurs des Saisons (10 joueurs, niveau 60, à partir du 9 décembre 2026) a plusieurs entrées, reliées au mont Hyjal, au Berceau-de-l’Hiver et au repaire des Noiregueules.', 'The raid overview says the Barrow Deeps raid (10 players, level 60, from 9 December 2026) has several entrances, connected through Mount Hyjal, Winterspring and Blackmaw Hold.', rd)]),
    S('correctifs', ('Correctifs officiels', 'Official hotfixes'), [
     L([('6 novembre 2026 : certaines créatures du repaire ne se désengagent plus à tort du combat.', '6 November 2026: some creatures inside no longer erroneously disengage.')], hf)])],
  srcs=RAIDS + HOT, rel=['forever-raid-barrow-deeps', 'forever-news-hotfixes-nov5-6'],
  conf=[K('Entrée du raid des profondeurs des Saisons reliée au repaire.', 'Barrow Deeps raid entrance connected through the hold.', rd)], pend=[C('Emplacement exact du passage vers le raid : non publié.', 'Exact location of the passage to the raid: not published.')],
  dates=[{'date': '2026-11-06', 'fr': 'Correctif : désengagement des créatures.', 'en': 'Hotfix: creature disengage.', 'src': hf}])
D['forever-dungeon-shapers-terrace'] = dict(
  lv=('58 à 60', '58–60'), place=('Collines du nord du cratère d’Un’Goro', 'Northern hills of Un’Goro Crater'),
  acc=('Apporter des cristaux de puissance récoltés dans Un’Goro, utilisés sur des consoles à l’intérieur.', 'Bring power crystals gathered in Un’Goro, used at consoles inside.'),
  story=('Une ancienne installation titan domine le cratère d’Un’Goro : dinosaures, structures titanesques, fosses de goudron et cristaux. Les cristaux de puissance récoltés dehors servent sur les consoles de la terrasse, qui relient l’exploration du monde aux défis de l’intérieur.',
         'An ancient titan facility overlooks Un’Goro Crater: dinosaurs, titan structures, tar pits and crystals. Power crystals gathered outside are used at the terrace’s consoles, tying outdoor exploration to the challenges inside.'),
  kp3=('Mécanique annoncée : cristaux de puissance d’Un’Goro utilisés sur des consoles.', 'Announced mechanic: Un’Goro power crystals used at consoles.'))

REV_NOTE = ('Lot 2 étape 04 (TEST ISOLÉ) : fiche existante enrichie en article (accès, histoire, quêtes/rencontres, correctifs et butin selon les sources officielles Blizzard citées) ; '
            'slug inchangé ; aucune donnée tierce. Relecture humaine de Mathieu requise.')
def revise_dungeon(existing, d):
    e = copy.deepcopy(existing)
    for k in ('importMeta', 'review'): e.pop(k, None)
    slug = (slugify(existing['title']['fr']), slugify(existing['title']['en']))
    WN = [src('bz-whatsnext-fr', 'fr', 'https://news.blizzard.com/fr-fr/article/24303862/recapitulatif-de-la-conference-lavenir-de-world-of-warcraft-forever', 'Récapitulatif de la conférence L’avenir de World of Warcraft: Forever', '2026-09-13'),
          src('bz-whatsnext-en', 'en', 'https://news.blizzard.com/en-us/article/24303862/world-of-warcraft-forever-whats-next-panel-recap', 'World of Warcraft: Forever What’s Next Panel Recap', '2026-09-13')]
    e['sources'] = DUNG + WN + d.get('srcs', []) + DIVE + CAMP
    lost = {x['url'] for x in existing['sources']} - {x['url'] for x in e['sources']}
    assert not lost, (existing['id'], lost)  # toute source d'origine est conservée (revérifiée le 2026-11-09)
    e['gameVersion'] = GV
    e['verification'] = 'officiel confirmé'
    e['relations'] = list(dict.fromkeys(existing['relations'] + d.get('rel', []) + ['forever-items-loot-appearances', 'forever-exploration-named-places']))
    kp3s = d['kp3'][2] if len(d['kp3']) > 2 else dg
    sections = [S('acces', ('Accès, niveaux et emplacement', 'Access, levels and location'), [
                  T(('Fiche d’accès (source : Blizzard, 20/10/2026)', 'Access sheet (source: Blizzard, 2026-10-20)'), [('Niveaux', 'Levels'), ('Emplacement', 'Location'), ('Accès', 'Access')],
                    [[d['lv'], d['place'], d['acc']]], dg),
                  P('Donjon à cinq joueurs, l’un des neuf nouveaux donjons de WoW: Forever (niveaux 13 à 60, royaumes de l’Est et Kalimdor).', 'Five-player dungeon, one of the nine new WoW: Forever dungeons (levels 13–60, Eastern Kingdoms and Kalimdor).', dg)]),
                S('histoire', ('Ce que Blizzard en dit', 'What Blizzard says'), [P(*d['story'], dg)])]
    sections += d.get('extra', [])
    sections.append(S('butin', ('Butin : ce qui est confirmé', 'Loot: what is confirmed'), LOOT_BLOCKS))
    e['article'] = art(slug, 'instances', K(existing['description']['fr'], existing['description']['en'], dg),
      [K(f"Niveaux {d['lv'][0]} — {d['place'][0]}.", f"Levels {d['lv'][1]} — {d['place'][1]}.", dg), K(d['acc'][0], d['acc'][1], dg), K(d['kp3'][0], d['kp3'][1], kp3s)],
      sections,
      [K(f"Niveaux {d['lv'][0]}, emplacement et accès d’après l’article officiel du 20 octobre 2026.", f"Levels {d['lv'][1]}, location and access per the official 20 October 2026 article.", dg)] + d.get('conf', []) +
      [K('Objets uniques des boss de donjon de qualité bleue ; apparence partagée pour les objets liés quand ramassés inhabituels ou rares.', 'Unique dungeon boss items are blue quality; shared appearance for bind-on-pickup Uncommon or Rare drops.', dv)],
      LOOT_PENDING + d.get('pend', []),
      [{'date': '2026-10-20', 'fr': 'Article officiel de présentation des neuf donjons.', 'en': 'Official article presenting the nine dungeons.', 'src': dg}] + d.get('dates', []))
    e['history'] = existing['history']
    return e

# ---------- A. Réputations ----------
E = []
E.append(entry('forever-reputations-confirmed', 'quests', 'reputations',
  ('Réputations : ce que Blizzard a confirmé (Kirin Tor, champs de bataille, Diplomatie)', 'Reputations: what Blizzard has confirmed (Kirin Tor, battlegrounds, Diplomat)'),
  ('Les seules informations officielles sur les réputations de WoW: Forever au 9 novembre 2026 : le Kirin Tor (confiance requise pour Dalaran, réputation fermée à la Horde), les réputations de champ de bataille comptées par l’héritage et l’avantage Diplomatie. Ni liste complète des factions, ni vendeurs, ni récompenses publiés.',
   'The only official information about WoW: Forever reputations as of 9 November 2026: the Kirin Tor (trust required for Dalaran, reputation closed to the Horde), battleground reputations counted by the Legacy System and the Diplomat perk. No full faction list, vendors or rewards published.'),
  DUNG + DEV6 + DEV9 + LEG + LIVE,
  ['forever-dungeon-city-of-dalaran', 'forever-questline-dalaran-attunement', 'forever-legacy-challenges', 'forever-legacy-perks', 'forever-pvp-darkspear-islands'],
  art(('reputations-confirmees', 'confirmed-reputations'), 'quests',
    K('Blizzard n’a publié aucun article consacré aux réputations de Forever. Cette fiche rassemble les mentions éparses des sources officielles : le Kirin Tor de Dalaran, les réputations de champ de bataille dans le système d’héritage et l’avantage Diplomatie. Le reste (factions, gains, vendeurs, récompenses) n’est pas confirmé.',
      'Blizzard has published no article dedicated to Forever reputations. This entry gathers the scattered mentions in official sources: Dalaran’s Kirin Tor, battleground reputations in the Legacy System and the Diplomat perk. Everything else (factions, gains, vendors, rewards) is unconfirmed.', dg + d6 + lg),
    [K('Kirin Tor : il faut gagner sa confiance pour entrer dans le donjon de la cité de Dalaran.', 'Kirin Tor: you must earn its trust to enter the City of Dalaran dungeon.', dg),
     K('La Horde ne doit pas gagner de réputation Kirin Tor (correction du 16 octobre) et est attaquée à vue dans Dalaran depuis le 3 novembre.', 'The Horde is not meant to gain Kirin Tor reputation (16 October fix) and is attacked on sight in Dalaran since 3 November.', d6 + d9),
     K('Héritage : être exalté auprès de chaque réputation de champ de bataille rapporte 4 points.', 'Legacy: Exalted with each battleground reputation is worth 4 points.', lg)],
    [S('tableau', ('Réputations citées par Blizzard', 'Reputations mentioned by Blizzard'), [
       T(('Mentions officielles de réputation (sources Blizzard, septembre–novembre 2026)', 'Official reputation mentions (Blizzard sources, September–November 2026)'), [('Réputation', 'Reputation'), ('Ce que Blizzard confirme', 'What Blizzard confirms'), ('Date', 'Date')],
         [[('Kirin Tor', 'Kirin Tor'), ('Confiance requise pour entrer dans le donjon de la cité de Dalaran, après la suite d’harmonisation de sa faction', 'Trust required to enter the City of Dalaran dungeon, after your faction’s attunement questline'), ('20/10/2026', '2026-10-20')],
          [('Kirin Tor', 'Kirin Tor'), ('Problème corrigé : des joueurs de la Horde pouvaient gagner cette réputation (bêta)', 'Fixed: Horde players could gain this reputation (beta)'), ('16/10/2026', '2026-10-16')],
          [('Réputations de champ de bataille', 'Battleground reputations'), ('Exalté auprès de chacune : 4 points d’héritage au total (catégorie JcJ)', 'Exalted with each: 4 Legacy Points in total (PvP category)'), ('23/09/2026', '2026-09-23')],
          [('Avantage Diplomatie', 'Diplomat perk'), ('Augmente les gains de réputation (arbre d’avantages d’héritage)', 'Increases reputation gains (Legacy perk tree)'), ('23/09/2026', '2026-09-23')]], dg + d6 + lg)]),
     S('dalaran', ('Kirin Tor et Horde à Dalaran', 'Kirin Tor and the Horde in Dalaran'), [
       P('Le 3 novembre, Blizzard précise que la Horde n’est plus la bienvenue à Dalaran et y est attaquée à vue. L’accès au donjon n’est pas touché, mais la suite de quêtes de la Horde qui donne la clé des égouts n’ouvre plus librement la ville.', 'On 3 November, Blizzard stated the Horde is no longer welcome in Dalaran and is attacked on sight. Dungeon access is unaffected, but the Horde questline that grants the sewer key no longer opens the city freely.', d9)]),
     S('champs-de-bataille', ('Réputations de champ de bataille', 'Battleground reputations'), [
       P('Le système d’héritage compte « chaque réputation de champ de bataille » dans ses défis JcJ (4 points), sans en publier la liste dans l’article. Pour les îles des Sombrelances, Blizzard nomme les deux camps, les chevaucheurs sombrelances et la troupe d’intervention de Theramore, sans dire dans les sources consultées s’il s’agit de réputations. Le détail du JcJ relève des fiches JcJ.', 'The Legacy System counts “each Battleground reputation” in its PvP challenges (4 points) without listing them in the article. For the Darkspear Islands, Blizzard names both sides, the Darkspear Raiders and the Theramore Expeditionary Force, without saying in the sources consulted whether these are reputations. PvP details belong to the PvP entries.', lg + lv)])],
    [K('Kirin Tor : confiance requise pour le donjon de Dalaran ; réputation fermée à la Horde.', 'Kirin Tor: trust required for the Dalaran dungeon; reputation closed to the Horde.', dg + d6),
     K('4 points d’héritage pour l’exalté auprès de chaque réputation de champ de bataille.', '4 Legacy Points for Exalted with each battleground reputation.', lg),
     K('Diplomatie augmente les gains de réputation.', 'Diplomat increases reputation gains.', lg)],
    [C('Liste officielle des factions de Forever : non publiée. Les chiffres de factions qui circulent viennent de bases extraites du client (par ex. Eternadex) et ne sont pas repris ici.', 'Official list of Forever factions: not published. Faction counts going around come from client-extracted databases (e.g. Eternadex) and are not used here.'),
     C('Gains par action, paliers, intendants, vendeurs et récompenses de chaque réputation : non publiés par Blizzard.', 'Gains per action, standings, quartermasters, vendors and rewards of each reputation: not published by Blizzard.'),
     C('Pourcentage exact de l’avantage Diplomatie : non indiqué dans l’article officiel.', 'Exact Diplomat percentage: not given in the official article.')],
    dates=[{'date': '2026-10-16', 'fr': 'Correction : la Horde ne gagne plus de réputation Kirin Tor (bêta).', 'en': 'Fix: the Horde no longer gains Kirin Tor reputation (beta).', 'src': d6},
           {'date': '2026-11-03', 'fr': 'La Horde est attaquée à vue dans Dalaran.', 'en': 'The Horde is attacked on sight in Dalaran.', 'src': d9}])))

# ---------- D. Exploration ----------
PL = [  # (id lieu, lieu fr/en, zone fr/en, type fr/en, repère fr/en, src)
 ('salle-des-thanes', ('Salle des Thanes', 'Hall of Thanes'), ('Dun Morogh', 'Dun Morogh'), ('Donjon', 'Dungeon'), ('Sous Forgefer', 'Beneath Ironforge'), dg),
 ('ruines-de-lordaeron', ('Ruines de Lordaeron', 'Ruins of Lordaeron'), ('Clairières de Tirisfal', 'Tirisfal Glades'), ('Donjon', 'Dungeon'), ('Cité en ruine au-dessus de Fossoyeuse', 'Ruined city above the Undercity'), dg),
 ('excavations', ('Excavations', 'Excavation Site'), ('Paluns', 'Wetlands'), ('Donjon', 'Dungeon'), ('Près du rocher de Thelgen et de Dun Algaz, au-dessus des excavations de Whelgar', 'Near Thelgen Rock and Dun Algaz, above Whelgar’s Excavation'), dg),
 ('cite-de-dalaran', ('Cité de Dalaran', 'City of Dalaran'), ('Montagnes d’Alterac', 'Alterac Mountains'), ('Donjon', 'Dungeon'), ('Entrée par les égouts, après harmonisation', 'Sewer entrance, after attunement'), dg),
 ('cite-submergee', ('La cité Submergée', 'The Drowned City'), ('Vallée de Strangleronce (large)', 'Stranglethorn Vale (offshore)'), ('Donjon', 'Dungeon'), ('À l’ouest de Grom’gol ; entrée sous l’eau', 'West of Grom’gol; underwater entrance'), dg),
 ('bastion-kroldok', ('Bastion Krol’dok', 'Krol’dok Stronghold'), ('Rives Claires', 'Riverglades'), ('Donjon', 'Dungeon'), ('Dans les rives Claires (pas de repère plus précis publié)', 'In the Riverglades (no finer landmark published)'), dg),
 ('prison-dalcaz', ('Prison d’Alcaz', 'Alcaz Prison'), ('Marécage d’Âprefange', 'Dustwallow Marsh'), ('Donjon', 'Dungeon'), ('Île d’Alcaz', 'Alcaz Island'), dg),
 ('repaire-des-noiregueules', ('Repaire des Noiregueules', 'Blackmaw Hold'), ('Azshara', 'Azshara'), ('Donjon', 'Dungeon'), ('Derrière une porte longtemps scellée', 'Behind a long-sealed gate'), dg),
 ('terrasse-du-faconneur', ('La terrasse du Façonneur', 'Shaper’s Terrace'), ('Cratère d’Un’Goro', 'Un’Goro Crater'), ('Donjon', 'Dungeon'), ('Collines du nord du cratère', 'Northern hills of the crater'), dg),
 ('profondeurs-des-saisons', ('Profondeurs des Saisons', 'Barrow Deeps'), ('Mont Hyjal', 'Mount Hyjal'), ('Raid', 'Raid'), ('Entrées reliées au mont Hyjal, au Berceau-de-l’Hiver et au repaire des Noiregueules', 'Entrances connected through Mount Hyjal, Winterspring and Blackmaw Hold'), rd),
 ('sommet-dhyjal', ('Sommet d’Hyjal', 'Hyjal Summit'), ('Mont Hyjal', 'Mount Hyjal'), ('Raid', 'Raid'), ('Au sommet, près de Nordrassil, l’Arbre-Monde', 'At the peak, near the World Tree Nordrassil'), rd),
 ('repaire-donyxia', ('Repaire d’Onyxia', 'Onyxia’s Lair'), ('Marécage d’Âprefange', 'Dustwallow Marsh'), ('Raid', 'Raid'), ('Au fond du marécage (pas de repère plus précis publié)', 'Deep in the marsh (no finer landmark published)'), rd),
 ('iles-des-sombrelances', ('Îles des Sombrelances', 'Darkspear Islands'), ('Marécage d’Âprefange (large)', 'Dustwallow Marsh (offshore)'), ('Champ de bataille', 'Battleground'), ('Au large du marécage d’Âprefange', 'Off the coast of Dustwallow Marsh'), lv),
 ('port-de-poudremeche', ('Port de Poudremèche', 'Powderfuse Port'), ('Rives Claires', 'Riverglades'), ('Port', 'Port'), ('Arrivée de la nouvelle liaison de Gentepression partie de Tanaris', 'Arrival of the new Steamwheedle route from Tanaris'), ph),
 ('shendar-highlands', ('Shen’dar Highlands (nom anglais)', 'Shen’dar Highlands'), ('Île de Zéphras', 'Zephras Isle'), ('Sous-zone', 'Subzone'), ('Pierres levées « Overlook Standing Stones » (quête « Catching Wind » de l’Ordre suprême)', 'Overlook Standing Stones (High Order quest “Catching Wind”)'), d1),
 ('nightclaw-cavern', ('Nightclaw Cavern (nom anglais)', 'Nightclaw Cavern'), ('Île de Zéphras', 'Zephras Isle'), ('Grotte', 'Cave'), ('Druides de la grotte, quête « Wounds of Betrayal »', 'The cavern’s druids, quest “Wounds of Betrayal”'), d1),
]
E.append(entry('forever-exploration-named-places', 'zones', 'lieux-et-acces',
  ('Exploration : lieux nommés par Blizzard et repères d’accès', 'Exploration: places named by Blizzard and access landmarks'),
  ('Index des lieux nouveaux ou réinventés de WoW: Forever que Blizzard situe lui-même (donjons, raids, champ de bataille, port, sous-zones de Zéphras), avec le repère officiel de chacun. Aucune coordonnée : Blizzard n’en publie pas.',
   'Index of the new or reimagined WoW: Forever places that Blizzard locates itself (dungeons, raids, battleground, port, Zephras subzones), with each one’s official landmark. No coordinates: Blizzard publishes none.'),
  DUNG + RAIDS + LIVE + PHOTOS + DEV1,
  ['article-forever-zones', 'forever-zone-zephras-isle', 'forever-zone-riverglades', 'forever-zone-mount-hyjal', 'forever-raid-barrow-deeps', 'forever-raid-hyjal-summit', 'forever-raid-onyxias-lair', 'forever-pvp-darkspear-islands'],
  art(('lieux-nommes-acces', 'named-places-access'), 'zones',
    K('Blizzard situe ses nouveaux lieux par des repères en toutes lettres (« sous Forgefer », « à l’ouest de Grom’gol »), jamais par des coordonnées. Cette fiche les rassemble en un seul tableau, avec un identifiant stable par lieu, pour pouvoir y rattacher plus tard d’autres données officielles.',
      'Blizzard locates its new places with written landmarks (“beneath Ironforge”, “west of Grom’gol”), never with coordinates. This entry gathers them in one table, with a stable identifier per place, so that more official data can be attached later.', dg + rd),
    [K('9 donjons, 3 raids, 1 champ de bataille, 1 port et 2 lieux de Zéphras situés par Blizzard.', '9 dungeons, 3 raids, 1 battleground, 1 port and 2 Zephras places located by Blizzard.', dg + rd + lv + ph + d1),
     K('Entrées sous l’eau (cité Submergée) ou par les égouts (Dalaran) : seuls repères d’accès détaillés.', 'Underwater (Drowned City) or sewer (Dalaran) entrances: the only detailed access landmarks.', dg),
     K('Coordonnées : aucune publiée par Blizzard ; aucune reprise de bases tierces.', 'Coordinates: none published by Blizzard; none taken from third-party databases.', dg)],
    [S('index', ('Index des lieux', 'Place index'), [
       T(('Lieux nommés et repères officiels (Blizzard, sept.–nov. 2026)', 'Named places and official landmarks (Blizzard, Sept.–Nov. 2026)'), [('Identifiant', 'Identifier'), ('Lieu', 'Place'), ('Zone', 'Zone'), ('Type', 'Type'), ('Repère officiel', 'Official landmark'), ('Coordonnées', 'Coordinates')],
         [[(pid, pid), n, z, t, r, ('Non publiées', 'Not published')] for pid, n, z, t, r, _ in PL], sorted({k for *_, s in PL for k in s}))]),
     S('zephras', ('Lieux de l’île de Zéphras', 'Zephras Isle places'), [
       P('Les notes de bêta du 24 septembre citent, sur l’île de Zéphras, les pierres levées « Overlook Standing Stones » dans les Shen’dar Highlands (quête « Catching Wind » de l’Ordre suprême) et les druides de la grotte Nightclaw (quête « Wounds of Betrayal »). Aucune traduction française officielle de ces noms n’est publiée. ' + BETA_FR, 'The 24 September beta notes name, on Zephras Isle, the Overlook Standing Stones in the Shen’dar Highlands (High Order quest “Catching Wind”) and the druids of Nightclaw Cavern (quest “Wounds of Betrayal”). No official French translation of these names is published. ' + BETA_EN, d1)]),
     S('rives-claires', ('Rives Claires : la route maritime', 'Riverglades: the sea route'), [
       P('La dernière nouvelle liaison part de Tanaris avec le cartel Gentepression et arrive au port de Poudremèche, dans les rives Claires, une zone de niveau intermédiaire à peu près aussi vaste que la vallée de Strangleronce.', 'The last new route leaves Tanaris with the Steamwheedle Cartel and arrives at Powderfuse Port in the Riverglades, a mid-level zone roughly the size of Stranglethorn Vale.', ph)])],
    [K('Les repères du tableau sont repris des articles officiels donjons et raids du 20 octobre 2026.', 'The table’s landmarks come from the official 20 October 2026 dungeon and raid articles.', dg + rd),
     K('Îles des Sombrelances au large du marécage d’Âprefange.', 'Darkspear Islands off the coast of Dustwallow Marsh.', lv)],
    [C('Coordonnées (x, y) des entrées et des lieux : non publiées par Blizzard. Ce wiki n’en reprend pas d’Eternadex, de Wowhead ou d’autres bases extraites du client.', 'Coordinates (x, y) of entrances and places: not published by Blizzard. This wiki does not take any from Eternadex, Wowhead or other client-extracted databases.'),
     C('Liste officielle des sous-zones de Zéphras, des rives Claires, du mont Hyjal et de Shen’dralas : non publiée.', 'Official subzone list for Zephras, the Riverglades, Mount Hyjal and Shen’dralas: not published.'),
     C('Aucune carte interactive n’est proposée : un futur outil cartographique ne pourra utiliser que des positions officielles ou constatées en jeu et documentées.', 'No interactive map is offered: a future mapping tool could only use official or documented in-game positions.')])))

# ---------- E. Bestiaire ----------
CR_LIVE = [  # depuis le lancement (correctifs officiels des 5 et 6 novembre)
 (('Krek the Noxious', 'Krek the Noxious'), ('Rives Claires', 'Riverglades'), ('Butin corrigé : la créature a désormais le bon butin', 'Loot fixed: now has the correct loot'), ('06/11/2026', '2026-11-06')),
 (('Ridgeshade Lurkers', 'Ridgeshade Lurkers'), ('Durotar', 'Durotar'), ('Ont désormais du butin', 'Now correctly have loot'), ('06/11/2026', '2026-11-06')),
 (('Pelluk', 'Pelluk'), ('Marais des Chagrins', 'Swamp of Sorrows'), ('N’apparaissait parfois pas : corrigé', 'Would sometimes not spawn: fixed'), ('05–06/11/2026', '2026-11-05/06')),
 (('Yarrog Baneshadow', 'Yarrog Baneshadow'), ('Durotar', 'Durotar'), ('Réapparition plus lente que prévu : corrigée', 'Respawned more slowly than intended: fixed'), ('05/11/2026', '2026-11-05')),
 (('Troggs de la carrière Grol’bolar', 'Troggs in Grol’bolar Quarry'), ('Dun Morogh', 'Dun Morogh'), ('Réapparaissaient trop vite : corrigé', 'Respawned too quickly: fixed'), ('06/11/2026', '2026-11-06')),
 (('Lasher Sproutlings, Blooming Lashers, Wrathvine', 'Lasher Sproutlings, Blooming Lashers, Wrathvine'), ('Teldrassil', 'Teldrassil'), ('Étaient à tort insensibles aux dégâts de nature : corrigé', 'Were wrongly immune to Nature damage: fixed'), ('06/11/2026', '2026-11-06')),
 (('Murlocs', 'Murlocs'), ('Marécage d’Âprefange', 'Dustwallow Marsh'), ('Certains réapparaissaient trop vite : corrigé', 'Some respawned too quickly: fixed'), ('05/11/2026', '2026-11-05')),
 (('The Baron', 'The Baron'), ('Ruines de Lordaeron (donjon)', 'Ruins of Lordaeron (dungeon)'), ('Laisse tomber la tête qui propose « Unending Torment » à la Horde dès le niveau 15', 'Drops the head that offers “Unending Torment” to the Horde from level 15'), ('06/11/2026', '2026-11-06'))]
CR_BETA = [
 (('Mother Fang', 'Mother Fang'), ('Forêt d’Elwynn', 'Elwynn Forest'), ('Réapparaît un peu plus lentement et ne laisse plus systématiquement un objet vert', 'Respawns a bit more slowly and no longer always drops a green item'), ('24/09/2026', '2026-09-24'), d1),
 (('Snow Leopard Prowler', 'Snow Leopard Prowler'), ('Dun Morogh', 'Dun Morogh'), ('Réapparition beaucoup plus rapide', 'Much faster respawn'), ('24/09/2026', '2026-09-24'), d1),
 (('Stitches', 'Stitches'), ('Bois de la Pénombre', 'Duskwood'), ('De nouveau hostile en entrant à Sombre-Comté', 'Hostile again as he enters Darkshire'), ('08/10/2026', '2026-10-08'), d5),
 (('Alliance Outrunners', 'Alliance Outrunners'), ('Barrens (nom anglais)', 'The Barrens'), ('Apparaissent désormais à des emplacements aléatoires', 'Now spawn in random locations'), ('03/11/2026', '2026-11-03'), d9),
 (('Dalaran Summoners', 'Dalaran Summoners'), ('Montagnes d’Alterac', 'Alterac Mountains'), ('N’invoquent plus sans fin', 'No longer summon endlessly'), ('03/11/2026', '2026-11-03'), d9),
 (('Certains satyres', 'Some satyrs'), ('Plusieurs zones', 'Several zones'), ('Classés démons (et non plus humanoïdes)', 'Classified as demons (no longer humanoids)'), ('03/11/2026', '2026-11-03'), d9)]
E.append(entry('forever-creatures-official-notes', 'creatures', 'notes-officielles',
  ('Bestiaire : créatures nommées par les notes officielles (apparitions et butins corrigés)', 'Bestiary: creatures named in the official notes (spawns and loot fixes)'),
  ('Les créatures du monde que Blizzard cite dans ses correctifs et notes de développement de Forever, avec la zone et ce qui a changé. Blizzard ne publie aucun taux de butin ni minuteur : ce wiki n’en invente pas.',
   'The world creatures Blizzard names in its Forever hotfixes and development notes, with the zone and what changed. Blizzard publishes no drop rates or timers, and this wiki invents none.'),
  HOT + DEV1 + DEV5 + DEV9 + DIVE,
  ['article-forever-creatures', 'forever-creature-onyxia', 'forever-dungeon-ruins-of-lordaeron', 'forever-zone-riverglades', 'forever-news-hotfixes-nov5-6', 'forever-items-loot-appearances'],
  art(('creatures-notes-officielles', 'creatures-official-notes'), 'creatures',
    K('Blizzard ne publie pas de bestiaire de Forever. Ses correctifs et notes de développement nomment pourtant des créatures précises quand leur apparition ou leur butin change. Cette fiche les recense, sans statut « rare » ni taux d’obtention que Blizzard n’indique pas.',
      'Blizzard publishes no Forever bestiary. Its hotfixes and development notes still name specific creatures when their spawn or loot changes. This entry lists them, without any “rare” status or drop rate Blizzard does not state.', hf + d9),
    [K('8 corrections de créatures depuis le lancement (5 et 6 novembre 2026).', '8 creature fixes since launch (5 and 6 November 2026).', hf),
     K('Des centaines de nouveaux butins de créatures rares ont été ajoutés, sans liste publiée.', 'Hundreds of new rare-creature drops have been added, with no published list.', dv),
     K('Noms anglais conservés : Blizzard n’a pas publié ces correctifs en français.', 'English names kept: Blizzard did not publish these hotfixes in French.', hf)],
    [S('depuis-le-lancement', ('Depuis le lancement (correctifs officiels)', 'Since launch (official hotfixes)'), [
       T(('Créatures citées par les correctifs des 5 et 6 novembre 2026', 'Creatures named in the 5 and 6 November 2026 hotfixes'), [('Créature (nom anglais)', 'Creature'), ('Zone', 'Zone'), ('Ce que dit Blizzard', 'What Blizzard says'), ('Date', 'Date')],
         [[a, b, c, d] for a, b, c, d in CR_LIVE], hf)]),
     S('beta', ('Pendant la bêta (notes de développement)', 'During the beta (development notes)'), [
       T(('Créatures citées par les notes de bêta (septembre–novembre 2026)', 'Creatures named in the beta notes (September–November 2026)'), [('Créature (nom anglais)', 'Creature'), ('Zone', 'Zone'), ('Ce que dit Blizzard', 'What Blizzard says'), ('Date', 'Date')],
         [[a, b, c, d] for a, b, c, d, _ in CR_BETA], d1 + d5 + d9),
       P(BETA_FR + ' Ces lignes décrivent l’état de la bêta à la date indiquée.', BETA_EN + ' These rows describe the beta at the date shown.', d1 + d5 + d9)]),
     S('rares-et-butins', ('Créatures rares et butins', 'Rare creatures and loot'), [
       P('Selon Blizzard, des centaines de nouveaux butins provenant de créatures rares ont été ajoutés et les objets épiques hors instance ont été améliorés. Aucune liste de créatures rares, aucune position et aucun taux ne sont publiés ; le correctif du 6 novembre augmente par exemple le taux d’obtention de la « Damp Note » sans donner de chiffre.', 'According to Blizzard, hundreds of new rare-creature drops have been added and world-drop epics improved. No list of rare creatures, positions or rates is published; the 6 November hotfix, for example, raises the “Damp Note” drop rate without giving a figure.', dv + hf)])],
    [K('8 corrections de créatures listées par les correctifs officiels des 5 et 6 novembre.', '8 creature fixes listed in the official 5 and 6 November hotfixes.', hf),
     K('Centaines de nouveaux butins de créatures rares (annonce, sans liste).', 'Hundreds of new rare-creature drops (announced, no list).', dv)],
    [C('Statut « rare » ou « élite » de ces créatures, niveaux, positions, minuteurs de réapparition et tables de butin : non publiés par Blizzard.', 'Rare or elite status of these creatures, levels, positions, respawn timers and loot tables: not published by Blizzard.'),
     C('Taux d’obtention : jamais publiés. Les « taux » diffusés par des bases tierces sont des échantillons ou des extractions du client et ne sont pas repris.', 'Drop rates: never published. “Rates” shown by third-party databases are samples or client extractions and are not used.'),
     C('Noms français officiels de ces créatures : non publiés dans les correctifs.', 'Official French names of these creatures: not published in the hotfixes.')],
    dates=[{'date': '2026-11-05', 'fr': 'Premier lot de correctifs après le lancement.', 'en': 'First post-launch hotfix list.', 'src': hf}, {'date': '2026-11-06', 'fr': 'Second lot de correctifs (créatures, donjons, quêtes).', 'en': 'Second hotfix list (creatures, dungeons, quests).', 'src': hf}])))

# ---------- F. Objets ----------
E.append(entry('forever-items-loot-appearances', 'items', 'itemisation',
  ('Objets : butin de donjon, apparences et itemisation de Forever', 'Items: dungeon loot, appearances and itemization in Forever'),
  ('Ce que Blizzard a confirmé sur les objets de WoW: Forever : statistiques remaniées, butin de donjon réexaminé (objets uniques des boss en bleu), règles de collection des apparences en donjon et en raid, et ajustements de bêta. Aucune table de butin.',
   'What Blizzard has confirmed about WoW: Forever items: reworked stats, re-examined dungeon loot (unique boss items in blue), appearance collection rules in dungeons and raids, and beta adjustments. No loot tables.'),
  DIVE + CAMP + DEV1 + DEV4 + DEV5,
  ['article-forever-items', 'forever-item-worgenbane-talisman', 'forever-item-ladimore-heirloom-ring', 'forever-quest-rewards-expanded', 'forever-camp-features', 'forever-guide-experience-preset'],
  art(('butin-apparences-itemisation', 'loot-appearances-itemization'), 'items',
    K('Forever garde les statistiques de Classic mais en remanie plusieurs pour que l’équipement varie selon le rôle et l’activité. Tout le butin des donjons a été réexaminé, les objets uniques des boss passent en qualité bleue et la collection d’apparences suit des règles pensées pour le jeu en groupe.',
      'Forever keeps Classic’s stats but reworks several so gear varies by role and activity. Every dungeon drop has been re-examined, unique boss items move to blue quality and appearance collection follows rules designed for group play.', dv),
    [K('Objets uniques des boss de donjon : qualité bleue ; bonus d’ensemble améliorés.', 'Unique dungeon boss items: blue quality; improved set bonuses.', dv),
     K('Objet inhabituel ou rare lié quand ramassé en donjon : apparence pour tous les membres éligibles.', 'Bind-on-pickup Uncommon or Rare dungeon drop: appearance for every eligible looter.', dv),
     K('Butin épique de raid : apparence pour le seul joueur à qui l’objet se lie.', 'Epic raid drop: appearance only for the player it binds to.', dv)],
    [S('statistiques', ('Statistiques remaniées', 'Reworked stats'), [
       L([('Chances de toucher des sorts, de la mêlée et à distance combinées ; idem pour les chances de coup critique.', 'Spell, melee and ranged hit chance are combined, as are critical strike chances.'),
          ('La compétence d’arme fonctionne comme avant, mais chaque objet en donne moins.', 'Weapon skill works as before, but each item grants less of it.'),
          ('Le bonus aux soins inclut aussi un tiers de bonus aux dégâts.', 'Bonus healing also includes one third as much bonus damage.'),
          ('Nouveaux effets liés à des environnements (bois, montagnes, déserts) ou à des types de créatures, comme X’calibhure.', 'New effects tied to environments (woodlands, mountains, deserts) or creature types, such as X’caliboar.'),
          ('Bijoux plus situationnels, par exemple le talisman de fléau des Worgens.', 'More situational trinkets, such as the Worgenbane Talisman.')], dv)]),
     S('butin', ('Butin des donjons et du monde', 'Dungeon and world loot'), [
       P('Chaque butin de donjon a été réexaminé : les objets marquants le restent, les moins intéressants sont ajustés et des centaines de nouveaux objets sont ajoutés. Les objets épiques hors instance sont améliorés et des centaines de nouveaux butins de créatures rares font leur apparition.', 'Every dungeon drop has been re-examined: memorable items stay memorable, less exciting ones are adjusted and hundreds of new drops are added. World-drop epics are improved and hundreds of new rare-creature drops appear.', dv),
       P('Les plans d’objets de campement avancés tombent sur certains boss de donjon.', 'Advanced camp feature blueprints drop from specific dungeon bosses.', cp)]),
     S('apparences', ('Collection d’apparences', 'Appearance collection'), [
       T(('Règles de collection d’apparences (Blizzard, 13/09/2026)', 'Appearance collection rules (Blizzard, 2026-09-13)'), [('Cas', 'Case'), ('Règle', 'Rule')],
         [[('Objet inhabituel ou rare lié quand ramassé, en donjon', 'Bind-on-pickup Uncommon or Rare item, in a dungeon'), ('Apparence accordée à tous les membres éligibles quand l’objet est ramassé', 'Appearance granted to all eligible looters when the item is looted')],
          [('Butin épique de raid', 'Epic raid drop'), ('Apparence accordée au seul joueur à qui l’objet se lie', 'Appearance granted only to the player the item binds to')],
          [('Objet de qualité médiocre ou commune', 'Poor or Common quality item'), ('Apparence obtenue dès le ramassage, sans liaison', 'Appearance granted as soon as it is looted, without binding')],
          [('Type d’objet', 'Item type'), ('Plaque sur plaque, tissu sur tissu', 'Plate to plate, cloth to cloth')],
          [('Niveau', 'Level'), ('Apparences de haut niveau utilisables à partir du niveau 60', 'High-level appearances usable from level 60')]], dv),
       P('Le système de transmogrification peut être désactivé chez un transmogrifieur ; il l’est automatiquement en mode Classique, et la collection continue en arrière-plan. Les objets purement cosmétiques seront rares.', 'Transmog can be disabled at a transmogrifier; it is off automatically in Classic Mode, and collecting continues in the background. Cosmetic-only items will be rare.', dv)]),
     S('beta', ('Ajustements pendant la bêta', 'Beta adjustments'), [
       L([('Vendre à un marchand un objet lié quand équipé dont l’apparence n’est pas collectée le rend lié à l’âme (et non plus lié au compte) — 1er octobre.', 'Selling a bind-on-equip item with an uncollected appearance to a vendor now makes it soulbound (was bound to account) — 1 October.'),
          ('Plusieurs récompenses de quêtes de donjon passent de rare à inhabituel, avec des statistiques adaptées — 8 octobre.', 'Various dungeon quest rewards lowered from Rare to Uncommon, with adjusted stats — 8 October.'),
          ('Les baguettes ne profitent plus des dégâts des sorts de l’utilisateur — 24 septembre.', 'Wands no longer gain damage from the user’s spell damage — 24 September.')], d4 + d5 + d1),
       P(BETA_FR, BETA_EN, d1 + d4 + d5)])],
    [K('Objets uniques des boss de donjon en qualité bleue ; bonus d’ensemble améliorés.', 'Unique dungeon boss items in blue quality; improved set bonuses.', dv),
     K('Règles d’apparence : donjon partagé, raid épique réservé, médiocre/commun dès le ramassage.', 'Appearance rules: shared in dungeons, reserved for epic raid drops, Poor/Common on loot.', dv),
     K('Plans de campement avancés sur certains boss de donjon.', 'Advanced camp blueprints from specific dungeon bosses.', cp)],
    [C('Tables de butin par boss, statistiques détaillées des objets et taux d’obtention : non publiés par Blizzard ; aucune base tierce reprise.', 'Per-boss loot tables, detailed item stats and drop rates: not published by Blizzard; no third-party database reused.'),
     C('Liste des nouveaux objets de créatures rares et des objets épiques hors instance : non publiée.', 'List of new rare-creature drops and world-drop epics: not published.'),
     C('Numéro de build : non indiqué dans les sources officielles consultées.', 'Build number: not given in the official sources consulted.')])))

def main():
    runtime = json.load(open(sys.argv[1], encoding='utf-8'))
    byid = {e['id']: e for e in runtime}
    for e in E: assert e['id'] not in byid, e['id']
    (HERE / 'lot2.entries.json').write_text(json.dumps(E, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    rd_dir = HERE / 'revisions'; rd_dir.mkdir(exist_ok=True)
    for id, d in D.items():
        r = revise_dungeon(byid[id], d)
        (rd_dir / f'{id}.json').write_text(json.dumps(r, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(len(E), 'new;', len(D), 'revisions')
main()
