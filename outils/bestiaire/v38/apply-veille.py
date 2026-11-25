#!/usr/bin/env python3
"""Revise the four official news sheets from the 13–14 Nov veille drafts."""
import copy
import json
from pathlib import Path

ROOT = Path('/workspace/wowkipedia-v21-elite')
ENTRIES = ROOT / 'bestiaire/test-tree-v38/pipeline/runtime/entries.json'
OUT = ROOT / 'bestiaire/v38-t359u/veille-revisions'
LICENSE = (
    'Droits réservés Blizzard ; référence et synthèse originale, '
    'réutilisation à vérifier lors de la revue humaine.'
)
GV_TUNING = 'World of Warcraft: Forever — annonces officielles, état documentaire 2026-11-14'
GV_NEWS = 'World of Warcraft: Forever — annonces, état documentaire 2026-11-14'


def load(eid, records):
    return copy.deepcopy(next(e for e in records if e['id'] == eid))


def align_gv(entry, gv):
    entry['gameVersion'] = gv
    for s in entry.get('sources') or []:
        s['gameVersion'] = gv
    return entry


def src(key, language, url, title, published, accessed, gv):
    return {
        'key': key,
        'language': language,
        'url': url,
        'title': title,
        'publishedAt': published,
        'accessedAt': accessed,
        'license': LICENSE,
        'gameVersion': gv,
    }


def dump(entry):
    entry = copy.deepcopy(entry)
    entry['status'] = 'draft'
    entry['identityConfirmed'] = False
    entry.pop('review', None)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{entry['id']}.json"
    path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
    print('wrote', path.name, 'nsrc', len(entry['sources']))


def patch_tuning(e):
    e = align_gv(e, GV_TUNING)
    # keep values source; point at the current official page title as of 14 Nov
    for s in e['sources']:
        if s.get('key') == 'bz-hotfixes-en':
            s['url'] = 'https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-13-2026'
            s['title'] = 'WoW: Forever Hotfixes - November 13, 2026'
            s['accessedAt'] = '2026-11-14'
            s['publishedAt'] = '2026-11-14'
        s['accessedAt'] = s.get('accessedAt') or '2026-11-14'
    keys = {s['key'] for s in e['sources']}
    if 'bz-forum-kaivax-us' not in keys:
        e['sources'].append(src(
            'bz-forum-kaivax-us', 'en',
            'https://us.forums.blizzard.com/en/wow/t/2403040/9',
            'WoW: Forever Hotfixes - November 11, 2026 (Kaivax, message 9 — Shaman deployment delay)',
            '2026-11-12', '2026-11-14', GV_TUNING,
        ))
    if 'bz-forum-kaivax-eu' not in keys:
        e['sources'].append(src(
            'bz-forum-kaivax-eu', 'en',
            'https://eu.forums.blizzard.com/en/wow/t/639885/8',
            'WoW: Forever Hotfixes (Kaivax, message 8 — Shaman deployment delay, 19:45 CET)',
            '2026-11-12', '2026-11-14', GV_TUNING,
        ))
    art = e['article']
    # lead: mention shaman delay, keep under 1200
    art['lead'] = {
        'fr': (
            "Blizzard avait annoncé le 6 novembre, sur les forums officiels, une série d’ajustements de classes "
            "pour le mardi 10 novembre, visant les familiers tanks, le démoniste Affliction et le chaman Amélioration. "
            "Ces mesures figurent, avec des valeurs chiffrées, dans la liste officielle des correctifs datée du 10 novembre. "
            "À cause d’un retard de déploiement, les changements du chaman ne sont entrés en jeu dans toutes les régions "
            "que le 12 novembre à 19 h 45, heure de Paris. La page française de l’article 24315281 renvoie une erreur 404 : "
            "les noms de sorts sont repris en anglais. Un lot distinct du 11 novembre ajoute d’autres correctifs de classes."
        ),
        'en': (
            "On November 6, on the official forums, Blizzard announced a set of class adjustments for Tuesday, November 10, "
            "aimed at tank pets, Affliction Warlock and Enhancement Shaman. The numbers now appear in the official "
            "November 10 hotfix list. Because of a deployment delay, the Shaman changes only went live in all regions on "
            "November 12 at 10:45 a.m. PST (19:45 CET). The French page of article 24315281 returns 404, so spell names "
            "are kept in English. A separate November 11 batch adds further class hotfixes."
        ),
        'src': ['bz-hotfixes-en', 'bz-tuning-us', 'bz-forum-kaivax-us', 'bz-forum-kaivax-eu'],
    }
    # key point 0: add delay sentence
    kp0 = art['keyPoints'][0]
    if 'retard de déploiement' not in kp0['fr']:
        kp0['fr'] = (
            "Les changements annoncés pour le 10 novembre sont appliqués et chiffrés dans la liste officielle des "
            "correctifs du 10 novembre. À cause d’un retard de déploiement, les changements du chaman (cumul des "
            "imprégnations et des totems d’arme, Stormstrike, Mental Dexterity, Maelstrom Weapon et son infobulle) "
            "ne sont entrés en jeu dans toutes les régions que le 12 novembre à 19 h 45, heure de Paris."
        )
        kp0['en'] = (
            "The changes announced for November 10 are applied and listed in the official November 10 hotfix notes. "
            "Because of a deployment delay, the Shaman changes (weapon imbues stacking with weapon totems, Stormstrike, "
            "Mental Dexterity, Maelstrom Weapon and its tooltip) only went live in all regions on November 12 at "
            "10:45 a.m. PST (19:45 CET)."
        )
        kp0['src'] = ['bz-hotfixes-en', 'bz-tuning-us', 'bz-forum-kaivax-us', 'bz-forum-kaivax-eu']
    # key point 1 shaman: add tooltip example
    kp1 = art['keyPoints'][1]
    if '3,6' not in kp1['fr'] and '3.6' not in kp1['fr']:
        kp1['fr'] = kp1['fr'].rstrip('.') + (
            " ; l’infobulle de Maelstrom Weapon affiche désormais la chance de déclenchement selon la vitesse de "
            "l’arme en main droite (exemple officiel : 5 points et une arme à 3,6 de vitesse donnent 60 % par coup, "
            "contre 33 % avec une arme à 2,0)."
        )
        kp1['en'] = kp1['en'].rstrip('.') + (
            "; the Maelstrom Weapon tooltip now shows the proc chance based on main-hand weapon speed "
            "(official example: 5 points with a 3.6-speed weapon shows 60% per swing, versus 33% with a 2.0-speed weapon)."
        )
        srcs = list(kp1.get('src') or [])
        if 'bz-forum-kaivax-us' not in srcs:
            srcs.append('bz-forum-kaivax-us')
        kp1['src'] = srcs
    # section applique-10-nov: first paragraph + tooltip already mentioned; add delay paragraph after first p
    sec = next(s for s in art['sections'] if s['id'] == 'applique-10-nov')
    if not any('19 h 45' in (b.get('fr') or '') for b in sec['blocks']):
        sec['blocks'].insert(1, {
            'type': 'p',
            'fr': (
                "À cause d’un retard de déploiement, les changements du chaman (cumul des imprégnations et des totems "
                "d’arme, Stormstrike, Mental Dexterity, Maelstrom Weapon et son infobulle) ne sont entrés en jeu dans "
                "toutes les régions que le 12 novembre à 19 h 45, heure de Paris, et non avec le reste du lot du 10 novembre. "
                "Les autres parties de cet équilibrage (démoniste, familiers, et les classes non visées par ce message) "
                "restent datées du 10 novembre. La page officielle des correctifs classe toujours ces lignes sous le 10 novembre ; "
                "ce message de forum fixe la date réelle d’entrée en jeu pour le chaman."
            ),
            'en': (
                "Because of a deployment delay, the Shaman changes (weapon imbues stacking with weapon totems, Stormstrike, "
                "Mental Dexterity, Maelstrom Weapon and its tooltip) only went live in all regions on November 12 at "
                "10:45 a.m. PST (19:45 CET), not with the rest of the November 10 batch. The other parts of this tuning "
                "(Warlock, pets, and the classes not covered by this post) stay dated November 10. The official hotfix page "
                "still lists these lines under November 10; the forum post fixes the actual go-live date for the Shaman changes."
            ),
            'src': ['bz-forum-kaivax-us', 'bz-forum-kaivax-eu', 'bz-hotfixes-en'],
        })
    # add official tooltip example to the first paragraph if missing — the first p already says tooltip shows chance by speed; add example
    p0 = sec['blocks'][0]
    if '60 %' not in p0['fr'] and '60%' not in p0['fr']:
        p0['fr'] = p0['fr'].rstrip('.') + (
            " (exemple officiel : 5 points et une arme à 3,6 de vitesse donnent 60 % par coup, contre 33 % avec une arme à 2,0)."
        )
        p0['en'] = p0['en'].rstrip('.') + (
            " (official example: 5 points with a 3.6-speed weapon shows 60% per swing, versus 33% with a 2.0-speed weapon)."
        )
        srcs = list(p0.get('src') or [])
        if 'bz-forum-kaivax-us' not in srcs:
            srcs.append('bz-forum-kaivax-us')
        p0['src'] = srcs
    # analysis sentence
    an = next(s for s in art['sections'] if s['id'] == 'analyse')
    block = an['blocks'][0]
    if 'décalage' not in block['fr']:
        block['fr'] = block['fr'].rstrip('.') + (
            " Ce décalage explique que des joueurs aient pu ne rien remarquer en jeu pendant deux jours ; "
            "les impressions sur l’Amélioration publiées avant le 12 au soir portent donc sur l’ancienne version."
        )
        block['en'] = block['en'].rstrip('.') + (
            " The delay explains why some players may have seen no change in game for two days; Enhancement impressions "
            "posted before the evening of November 12 describe the old version."
        )
    # date line
    dates = art.setdefault('dates', [])
    if not any(d.get('date') == '2026-11-12' and '19 h 45' in d.get('fr', '') for d in dates):
        dates.insert(0, {
            'date': '2026-11-12',
            'fr': 'Changements du chaman entrés en jeu à 19 h 45, heure de Paris, après un retard de déploiement (message Kaivax, 19:10 UTC).',
            'en': 'Shaman changes went live at 10:45 a.m. PST (19:45 CET) after a deployment delay (Kaivax post, 19:10 UTC).',
            'src': ['bz-forum-kaivax-us', 'bz-forum-kaivax-eu'],
        })
    for part, limit in ((art['lead'], 1200), (kp0, 2400), (kp1, 2400), (p0, 2400)):
        for lang in ('fr', 'en'):
            if len(part[lang]) > limit:
                raise SystemExit(f'tuning {lang} too long {len(part[lang])}: {part[lang][:80]}')
    return e


def patch_hotfixes(e):
    e = align_gv(e, GV_TUNING)
    e['title'] = {
        'fr': 'Correctifs Forever du 5 au 13 novembre : XP en donjon, classes, objets et quêtes',
        'en': 'Forever hotfixes, November 5–13: dungeon XP, classes, items and quests',
    }
    # slug must stay
    assert e['article']['slug'] == {
        'fr': 'correctifs-forever-5-et-6-novembre',
        'en': 'forever-hotfixes-november-5-6',
    }
    for s in e['sources']:
        if s.get('key') == 'bz-hotfixes-en':
            s['url'] = 'https://news.blizzard.com/en-us/article/24315281/wow-forever-hotfixes-november-13-2026'
            s['title'] = 'WoW: Forever Hotfixes - November 13, 2026'
            s['publishedAt'] = '2026-11-14'
            s['accessedAt'] = '2026-11-14'
    keys = {s['key'] for s in e['sources']}
    if 'bz-kaivax-1113' not in keys:
        e['sources'].append(src(
            'bz-kaivax-1113', 'en',
            'https://us.forums.blizzard.com/en/wow/t/2403040/10',
            'WoW: Forever Hotfixes - November 13, 2026 (Kaivax, message 10)',
            '2026-11-14', '2026-11-14', GV_TUNING,
        ))
    if 'bz-refund-eu' not in keys:
        e['sources'].append(src(
            'bz-refund-eu', 'en',
            'https://eu.forums.blizzard.com/en/wow/t/642655',
            'Lost Training Purchase Refunds - 13 November (Kaivax)',
            '2026-11-14', '2026-11-14', GV_TUNING,
        ))
    art = e['article']
    art['lead'] = {
        'fr': (
            "Blizzard tient une page cumulative de correctifs Forever, désormais titrée "
            "« WoW: Forever Hotfixes - November 13, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11 et 13 novembre. "
            "La page française de l’article 24315281 reste titrée 9 novembre et les noms de sorts, PNJ, objets et quêtes "
            "sont repris tels quels en anglais. Le 12 novembre à 00:48 UTC, Kaivax a reporté au 17 novembre les changements "
            "de l’hôtel des ventes du 10 novembre. Le 13 novembre, l’XP en donjon s’arrête pour tout le groupe dès qu’un "
            "ennemi est « gris » pour au moins un membre ; les formations perdues le 9 novembre sont remboursées en or. "
            "L’équilibrage de classes du 10 novembre reste détaillé dans l’article dédié."
        ),
        'en': (
            "Blizzard keeps a cumulative Forever hotfix page, now titled “WoW: Forever Hotfixes - November 13, 2026”. "
            "It covers the November 5, 6, 8, 9, 10, 11 and 13 batches. The French page of article 24315281 is still titled "
            "November 9, so spell, NPC, item and quest names are kept in English. On November 12 at 00:48 UTC, Kaivax "
            "postponed the November 10 Auction House changes to November 17. On November 13, dungeon enemies grant no XP "
            "to the whole party once they are “grey” to at least one member; training lost on November 9 is refunded in gold. "
            "November 10 class tuning remains in the dedicated article."
        ),
        'src': ['bz-hotfixes-en', 'bz-hotfixes-forum-us', 'bz-kaivax-1113', 'bz-refund-eu'],
    }
    # new key point at head
    art['keyPoints'].insert(0, {
        'fr': (
            "Le 13 novembre, les ennemis de donjon ne rapportent plus aucune XP à tout le groupe dès qu’ils sont "
            "insignifiants (« gris ») pour au moins un membre ; correctifs de classes, d’objets et de quêtes. "
            "Les formations achetées puis perdues lors de l’incident serveur du 9 novembre (22 h 17–23 h 17 CET) "
            "sont remboursées en or par courrier en jeu."
        ),
        'en': (
            "On November 13, dungeon enemies stop giving any XP to the whole party as soon as they are trivial "
            "(“grey”) to at least one member; class, item and quest fixes also landed. Training bought and lost "
            "during the November 9 server incident (22:17–23:17 CET) is refunded in gold by in-game mail."
        ),
        'src': ['bz-hotfixes-en', 'bz-kaivax-1113', 'bz-refund-eu'],
    })
    nov13 = {
        'id': 'details-nov13',
        'title': {'fr': '13 novembre 2026', 'en': 'November 13, 2026'},
        'blocks': [
            {
                'type': 'p',
                'fr': (
                    "Tuer un ennemi en donjon ne donne plus aucune expérience à aucun membre du groupe si son niveau "
                    "est insignifiant pour au moins un des membres. Les ennemis non-boss de The Drowned City réapparaissent "
                    "après 2 heures (au lieu d’1 heure) ; Sneed (The Deadmines) est correctement éjecté ; Balnazzar "
                    "(Stratholme) compte pour le défi d’héritage Master Spelunker."
                ),
                'en': (
                    "Killing dungeon enemies now awards zero experience to all party members if the enemy is trivial to "
                    "one or more of them. Non-boss enemies in The Drowned City respawn after 2 hours (was 1); Sneed "
                    "(The Deadmines) ejects properly; Balnazzar (Stratholme) counts toward the Master Spelunker legacy challenge."
                ),
                'src': ['bz-hotfixes-en', 'bz-kaivax-1113'],
            },
            {
                'type': 'p',
                'fr': (
                    "Classes : rendements décroissants rétablis pour les étourdissements entre joueurs et créatures. "
                    "Druide Restauration : Wild Growth ne peut plus être lancé en mouvement, coefficient de soin porté "
                    "à 6,6 % (au lieu de 3,3 %). Paladin : Judgement of Command déclenche les effets « au toucher » et "
                    "compte comme une attaque de mêlée (les autres jugements restent des attaques à distance). Chaman : "
                    "Windfury Totem se déclenche avec toutes les techniques de mêlée, sauf les frappes de main gauche. "
                    "Corrections aussi pour mage (Frost Nova), prêtre (perk The Quick and the Dead), démoniste "
                    "(Siphon Life rang 1) et guerrier (Berserker Rage contre Sap)."
                ),
                'en': (
                    "Classes: diminishing returns restored for stuns between players and creatures. Restoration Druid: "
                    "Wild Growth can no longer be cast while moving, healing coefficient raised to 6.6% (was 3.3%). "
                    "Paladin: Judgement of Command triggers on-hit effects and counts as a melee attack (other judgements "
                    "stay ranged). Shaman: Windfury Totem procs from all melee abilities except off-hand strikes. Fixes also "
                    "for Mage (Frost Nova), Priest (The Quick and the Dead perk), Warlock (Siphon Life Rank 1) and Warrior "
                    "(Berserker Rage vs Sap)."
                ),
                'src': ['bz-hotfixes-en'],
            },
            {
                'type': 'p',
                'fr': (
                    "Objets : statistiques corrigées sur une dizaine d’objets ; Channeler's Ring donne de la puissance "
                    "des sorts (au lieu d’Esprit) et Blessed Band of Light perd son toucher. Les porteurs de Blessed "
                    "Band of Light peuvent l’échanger, sans retour possible, contre un Channeler's Ring chez Pix Xizzix "
                    "jusqu’à l’ouverture des raids."
                ),
                'en': (
                    "Items: stats corrected on about ten items; Channeler's Ring now has spell power (was Spirit) and "
                    "Blessed Band of Light loses its hit. Blessed Band of Light owners may swap it, irreversibly, for a "
                    "Channeler's Ring at Pix Xizzix until raids open."
                ),
                'src': ['bz-hotfixes-en'],
            },
            {
                'type': 'p',
                'fr': (
                    "Quêtes et monde : une quinzaine de quêtes corrigées (objets de quête partagés en groupe, rives Claires / "
                    "Riverglades, Feralas, mont Hyjal) ; apparitions ajustées (Mulgore moins dense au départ, Strangleronce "
                    "et Terres ingrates plus fournies) ; plus de gagnants par ensemble de règles au concours de pêche "
                    "hebdomadaire de Strangleronce. Interface : les barres d’action ne se réinitialisent plus à la "
                    "déconnexion pour les personnages ayant des talents secondaires."
                ),
                'en': (
                    "Quests and world: around fifteen quest fixes (party-shared quest items, Riverglades, Feralas, Mount Hyjal); "
                    "spawn tweaks (quieter Mulgore start, busier Stranglethorn and Badlands); many more winners per ruleset "
                    "in the weekly Stranglethorn fishing tournament. User interface: action bars no longer reset on logout "
                    "for characters with Secondary Talents."
                ),
                'src': ['bz-hotfixes-en'],
            },
            {
                'type': 'p',
                'fr': (
                    "Remboursement : les formations achetées puis perdues lors de l’incident serveur du 9 novembre entre "
                    "22 h 17 et 23 h 17 CET sont remboursées en or par courrier en jeu (annonce du 14 novembre, 01:36 UTC)."
                ),
                'en': (
                    "Refund: training bought and lost during the November 9 server incident (22:17–23:17 CET) is refunded "
                    "in gold by in-game mail (announced November 14, 01:36 UTC)."
                ),
                'src': ['bz-refund-eu'],
            },
            {
                'type': 'p',
                'fr': (
                    "Conséquence pour les joueurs : grouper avec un personnage nettement plus haut niveau en donjon peut "
                    "désormais priver tout le groupe d’XP sur les ennemis devenus gris pour lui. Blizzard indique continuer "
                    "à travailler sur les performances du concours de pêche, avec d’autres correctifs dans les semaines à venir."
                ),
                'en': (
                    "Player impact: grouping in a dungeon with a much higher-level character can now cost the whole party XP "
                    "on enemies grey to that character. Blizzard says it keeps working on fishing tournament performance, "
                    "with more fixes in the coming weeks."
                ),
                'src': ['bz-hotfixes-en'],
            },
        ],
    }
    if not any(s['id'] == 'details-nov13' for s in art['sections']):
        art['sections'].insert(0, nov13)
    # analysis addition
    an = next(s for s in art['sections'] if s['id'] == 'analyse')
    block = an['blocks'][0]
    if 'portages' not in block['fr']:
        block['fr'] = block['fr'].rstrip('.') + (
            " La règle d’XP en donjon du 13 novembre vise clairement les « portages » par un personnage de haut niveau ; "
            "elle pèse aussi sur les groupes d’amis aux niveaux écartés, ce qui explique les réactions vives sur les forums. "
            "Reste à voir si Blizzard nuancera ce seuil."
        )
        block['en'] = block['en'].rstrip('.') + (
            " The November 13 dungeon XP rule clearly targets high-level “boosting”; it also affects friends with wide level "
            "gaps, which explains the strong forum reactions. Whether Blizzard softens the threshold remains to be seen."
        )
    dates = art.setdefault('dates', [])
    if not any(d.get('date') == '2026-11-13' for d in dates):
        dates.insert(0, {
            'date': '2026-11-13',
            'fr': 'Lot officiel (XP en donjon, classes, objets, quêtes, interface) ; remboursement des formations annoncé le 14 novembre à 01:36 UTC.',
            'en': 'Official batch (dungeon XP, classes, items, quests, UI); training refund announced on November 14 at 01:36 UTC.',
            'src': ['bz-hotfixes-en', 'bz-kaivax-1113', 'bz-refund-eu'],
        })
    # pending: bump FR page note date; add fishing follow-up
    for p in art['pending']:
        if '24315281' in p['fr']:
            p['fr'] = (
                "Page française de l’article 24315281 et traductions officielles des noms Forever : "
                "toujours titrée 9 novembre, consultée le 14 novembre 2026."
            )
            p['en'] = (
                "French article 24315281 and official translations of Forever names: still titled November 9, "
                "checked on November 14, 2026."
            )
    if not any('concours de pêche' in p['fr'] for p in art['pending']):
        art['pending'].append({
            'fr': 'Autres correctifs annoncés sur les performances du concours de pêche hebdomadaire, dans les semaines à venir.',
            'en': 'Further fixes announced for weekly fishing-tournament performance, in the coming weeks.',
        })
    for lang in ('fr', 'en'):
        if len(art['lead'][lang]) > 1200:
            raise SystemExit(f'hotfix lead {lang} {len(art["lead"][lang])}')
        if len(art['keyPoints'][0][lang]) > 2400:
            raise SystemExit('kp0 too long')
        if len(an['blocks'][0][lang]) > 2400:
            raise SystemExit(f'analysis {lang} {len(an["blocks"][0][lang])}')
    if len(e['sources']) > 20:
        raise SystemExit(f'too many sources {len(e["sources"])}')
    return e


def patch_podcast(e):
    e = align_gv(e, GV_NEWS)
    fr_add = (
        " Épisode 7 (12 nov.) : l’histoire de l’univers de Forever, avec les invités PlatinumWoW et Nobbel et, "
        "pour Blizzard, Josh « Aggrend » Greenfield (concepteur de jeu senior) et Sean Copeland (historien en chef "
        "de l’univers), animé par Countdown To Classic."
    )
    en_add = (
        " Episode 7 (Nov 12): the lore and story of Forever, with guests PlatinumWoW and Nobbel and, from Blizzard, "
        "Josh “Aggrend” Greenfield (Senior Game Designer) and Sean Copeland (Lore Historian Lead), hosted by "
        "Countdown To Classic."
    )
    if 'Épisode 7' not in e['description']['fr']:
        e['description']['fr'] = e['description']['fr'].rstrip('.') + fr_add
        e['description']['en'] = e['description']['en'].rstrip('.') + en_add
    keys = {s.get('key') for s in e['sources']}
    if 'bz-podcast-ep7-fr' not in keys:
        e['sources'].append(src(
            'bz-podcast-ep7-fr', 'fr',
            'https://news.blizzard.com/fr-fr/article/24316981',
            'Découvrez le podcast WoW: Forever – L\'histoire de l\'univers',
            '2026-11-12', '2026-11-14', GV_NEWS,
        ))
        e['sources'].append(src(
            'bz-podcast-ep7-en', 'en',
            'https://news.blizzard.com/en-us/article/24316981',
            'Watch the WoW: Forever Podcast – The Lore Episode',
            '2026-11-12', '2026-11-14', GV_NEWS,
        ))
    # no rumor, no player-thread 2412878
    return e


def patch_unbowed(e):
    e = align_gv(e, GV_NEWS)
    # Pin existing URLs while broadening the title.
    e['title'] = {
        'fr': 'Les nouvelles officielles de WoW: Forever',
        'en': 'Official WoW: Forever short stories',
    }
    e['description'] = {
        'fr': (
            "Blizzard publie des nouvelles narrées officielles de WoW: Forever. "
            "« Unbowed » (26 octobre) suit Cormack, ancien Croisé écarlate devenu Réprouvé, qui se demande si un mort-vivant "
            "peut encore servir la Lumière. « Le prix de l’honneur » (13 novembre), lue au coin du feu par Demar Brant, "
            "défend l’idée que la force d’un peuple tient aussi au courage de se protéger les uns les autres."
        ),
        'en': (
            "Blizzard publishes official narrated short stories for WoW: Forever. "
            "“Unbowed” (October 26) follows Cormack, a former Scarlet Crusader raised as Forsaken, who wonders whether "
            "an undead can still serve the Light. “Cost of Honor” (November 13), told by the fireside by Demar Brant, "
            "argues that a people’s strength also lies in the courage to protect one another."
        ),
    }
    # existing unbowed source: give it a key, keep URL
    first = e['sources'][0]
    first['key'] = first.get('key') or 'bz-story-unbowed-en'
    first['language'] = first.get('language') or 'en'
    first['license'] = LICENSE
    keys = {s.get('key') for s in e['sources']}
    if 'bz-story-coh-fr' not in keys:
        e['sources'].append(src(
            'bz-story-coh-fr', 'fr',
            'https://news.blizzard.com/fr-fr/article/24316096',
            'Découvrez la nouvelle « Le prix de l\'honneur » de WoW: Forever',
            '2026-11-13', '2026-11-14', GV_NEWS,
        ))
        e['sources'].append(src(
            'bz-story-coh-en', 'en',
            'https://news.blizzard.com/en-us/article/24316096',
            'Watch the WoW: Forever Short Story, “Cost of Honor”',
            '2026-11-13', '2026-11-14', GV_NEWS,
        ))
    e['article'] = {
        'format': 2,
        'slug': {'fr': 'nouvelle-unbowed', 'en': 'short-story-unbowed'},
        'lead': {
            'fr': (
                "Blizzard rassemble désormais au moins deux nouvelles officielles narrées pour WoW: Forever. "
                "« Unbowed », publiée le 26 octobre, suit Cormack, ancien Croisé écarlate devenu Réprouvé. "
                "Le 13 novembre, « Le prix de l’honneur », lue au coin du feu par Demar Brant, évoque la guerre, "
                "le sacrifice et des choix difficiles."
            ),
            'en': (
                "Blizzard now has at least two official narrated short stories for WoW: Forever. "
                "“Unbowed”, published on October 26, follows Cormack, a former Scarlet Crusader raised as Forsaken. "
                "On November 13, “Cost of Honor”, told by the fireside by Demar Brant, turns to war, sacrifice and hard choices."
            ),
            'src': ['bz-story-unbowed-en', 'bz-story-coh-fr', 'bz-story-coh-en'],
        },
        'keyPoints': [
            {
                'fr': '26 octobre : nouvelle officielle « Unbowed », narrée et illustrée, sur Cormack, qui se demande si un mort-vivant peut encore servir la Lumière.',
                'en': 'October 26: official short story “Unbowed”, narrated and illustrated, about Cormack, who wonders whether an undead can still serve the Light.',
                'src': ['bz-story-unbowed-en'],
            },
            {
                'fr': '13 novembre : deuxième nouvelle officielle, « Le prix de l’honneur », lue au coin du feu par Demar Brant ; elle défend l’idée que la force d’un peuple tient aussi au courage de se protéger les uns les autres.',
                'en': 'November 13: second official short story, “Cost of Honor”, told by the fireside by Demar Brant; it argues that a people’s strength also lies in the courage to protect one another.',
                'src': ['bz-story-coh-fr', 'bz-story-coh-en'],
            },
        ],
        'sections': [
            {
                'id': 'unbowed',
                'title': {'fr': '« Unbowed » (26 octobre)', 'en': '“Unbowed” (October 26)'},
                'blocks': [{
                    'type': 'p',
                    'fr': (
                        "Blizzard publie une nouvelle narrée et illustrée sur Cormack, ancien Croisé écarlate devenu "
                        "Réprouvé, qui se demande si un mort-vivant peut encore servir la Lumière."
                    ),
                    'en': (
                        "Blizzard releases a narrated, illustrated short story about Cormack, a former Scarlet Crusader "
                        "raised as Forsaken, who wonders whether an undead can still serve the Light."
                    ),
                    'src': ['bz-story-unbowed-en'],
                }],
            },
            {
                'id': 'prix-de-lhonneur',
                'title': {'fr': '« Le prix de l’honneur » (13 novembre)', 'en': '“Cost of Honor” (November 13)'},
                'blocks': [{
                    'type': 'p',
                    'fr': (
                        "Le 13 novembre, Blizzard publie une deuxième nouvelle, « Le prix de l’honneur », lue au coin du feu "
                        "par Demar Brant ; à travers des récits de guerre, de sacrifice et de choix difficiles, elle défend "
                        "l’idée que la force d’un peuple tient aussi au courage de se protéger les uns les autres."
                    ),
                    'en': (
                        "On November 13, Blizzard releases a second short story, “Cost of Honor”, told by the fireside by "
                        "Demar Brant; through tales of war, sacrifice and hard choices, it argues that a people’s strength "
                        "also lies in the courage to protect one another."
                    ),
                    'src': ['bz-story-coh-fr', 'bz-story-coh-en'],
                }],
            },
        ],
        'confirmed': [
            {
                'fr': 'Deux nouvelles officielles publiées sur le site de Blizzard : « Unbowed » (26 octobre) et « Le prix de l’honneur » (13 novembre).',
                'en': 'Two official short stories published on the Blizzard site: “Unbowed” (October 26) and “Cost of Honor” (November 13).',
                'src': ['bz-story-unbowed-en', 'bz-story-coh-fr', 'bz-story-coh-en'],
            },
        ],
        'pending': [
            {
                'fr': 'Page française officielle de « Unbowed » : seule la source en-us est citée ici (consultée le 14 novembre 2026).',
                'en': 'Official French page for “Unbowed”: only the en-us source is cited here (checked 14 November 2026).',
            },
            {
                'fr': 'D’éventuelles nouvelles officielles suivantes, non encore publiées.',
                'en': 'Any later official short stories not yet published.',
            },
        ],
        'dates': [
            {'date': '2026-10-26', 'fr': 'Publication officielle de « Unbowed ».', 'en': 'Official publication of “Unbowed”.', 'src': ['bz-story-unbowed-en']},
            {'date': '2026-11-13', 'fr': 'Publication officielle de « Le prix de l’honneur ».', 'en': 'Official publication of “Cost of Honor”.', 'src': ['bz-story-coh-fr', 'bz-story-coh-en']},
        ],
    }
    for lang in ('fr', 'en'):
        if len(e['article']['lead'][lang]) > 1200:
            raise SystemExit('unbowed lead too long')
    return e


def main():
    records = json.loads(ENTRIES.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    dump(patch_tuning(load('forever-news-class-tuning-nov10', records)))
    dump(patch_hotfixes(load('forever-news-hotfixes-nov5-6', records)))
    dump(patch_podcast(load('forever-news-podcast-series', records)))
    dump(patch_unbowed(load('forever-news-story-unbowed', records)))
    # length report
    for f in sorted(OUT.glob('*.json')):
        e = json.loads(f.read_text())
        art = e.get('article') or {}
        lead = (art.get('lead') or {})
        print(f.name, 'lead', {k: len(lead[k]) for k in lead if k in ('fr','en')}, 'nsrc', len(e['sources']))


if __name__ == '__main__':
    main()
