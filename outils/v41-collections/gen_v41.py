#!/usr/bin/env python3
"""v41 (t403u) — génère, pour le pipeline de TEST (/tmp/v41-pipeline) :
  - data/collections-v41.json : fragments HTML des fiches-objets (FR/EN), regroupés par moyen d'obtention ;
  - public/v2/assets/icone-jeu-<fdid>.webp : icônes du jeu (fichiers du client WoW Forever 1.60.1.70862) ;
  - ../out/entries/*.json : 1 nouvelle fiche (hub Collections) + 4 fiches révisées (montures, mascottes, jouets, héritage).
Aucune donnée inventée : chaque champ vient des fichiers du client, d'un article Blizzard cité ou des données de quêtes (à confirmer)."""
import json, html, re, shutil, copy, collections, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
PIPE = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/v41-pipeline')
D = json.load(open(HERE / 'out/collections.json'))
MAN = json.load(open(HERE / 'out/icons-manifest.json'))['icons']
BUILD = '1.60.1.70862'
ACC = '2026-11-17'
NOW = '2026-11-17T17:00:00.000Z'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
QUAL = {0: ('Médiocre', 'Poor'), 1: ('Classique', 'Common'), 2: ('Inhabituel', 'Uncommon'), 3: ('Rare', 'Rare'), 4: ('Épique', 'Epic'), 5: ('Légendaire', 'Legendary')}
FAC = {'alliance': ('Alliance', 'Alliance'), 'horde': ('Horde', 'Horde'), 'both': ('Les deux factions', 'Both factions')}
QFAC = {'A': 'alliance', 'H': 'horde'}

def L(lang, fr, en): return en if lang == 'en' else fr

def money(m, lang):
    if not m: return ''
    p = []
    if m['g']: p.append(f"{m['g']} {L(lang, 'po', 'g')}")
    if m['s']: p.append(f"{m['s']} {L(lang, 'pa', 's')}")
    if m['c']: p.append(f"{m['c']} {L(lang, 'pc', 'c')}")
    return ' '.join(p)

# ---------- normalisation ----------
def fix_faction(x):
    r = x.get('rep')
    if r and r['en'] in ('Alliance', 'Horde') and r['st_en'] == 'Neutral':
        x['faction'] = r['en'].lower(); x.pop('rep')
    return x

def group_of(x):
    t = [h['type'] for h in x['how']]
    if 'heritage' in t or any(h['type'] == 'quest' and (h.get('q_en') or '').startswith('Legacy Reward') for h in x['how']): return 'heritage'
    if 'pack' in t: return 'pack'
    if 'subscription' in t: return 'abonnement'
    if x.get('spell_mount'): return 'classe'
    if 'craft' in t: return 'artisanat'
    if 'quest' in t: return 'quete'
    if x.get('rep'): return 'reputation'
    return 'non-indique'

def is_exchange(x):
    return any(h['type'] == 'quest' and h.get('choice') and h.get('lv') == 60 and h.get('minlv') == 60 for h in x['how'])

def how_lines(x, lang):
    """Return list of (label, html) facts + status ('official'|'game'|'quest')."""
    facts, status = [], 'game'
    obt = []
    zone = npc = ''
    for h in x['how']:
        t = h['type']
        if t in ('heritage', 'pack', 'subscription'):
            obt.append(E(h['fr'] if lang == 'fr' else h['en'])); status = 'official'
        elif t == 'craft':
            rk_fr = f" (compétence {h['rank']})" if (h.get('rank') or 0) > 1 else ''; rk_en = f" (skill {h['rank']})" if (h.get('rank') or 0) > 1 else ''
            obt.append(E(L(lang, f"Artisanat : {h['prof_fr']}{rk_fr} — recette « {h['spell_fr']} »", f"Crafted: {h['prof_en']}{rk_en} — recipe “{h['spell_en']}”")))
        elif t == 'quest':
            qn = h.get('q_fr') if lang == 'fr' and h.get('q_fr') and h.get('q_fr') != h.get('q_en') else h.get('q_en')
            kind = L(lang, 'Sort appris par la quête', 'Spell learned from the quest') if h.get('learns') else (L(lang, 'Récompense au choix de la quête', 'Choice reward of the quest') if h.get('choice') else L(lang, 'Récompense de la quête', 'Reward of the quest'))
            lv = f" ({L(lang, 'niveau', 'level')} {h['lv']})" if h.get('lv') and h['lv'] > 1 else ''
            fq = QFAC.get(h.get('fac') or '')
            ftxt = f" — {FAC[fq][0 if lang=='fr' else 1]}" if fq else ''
            obt.append(f"{kind} « {E(qn)} »{lv}{ftxt}" if lang == 'fr' else f"{kind} “{E(qn)}”{lv}{ftxt}")
            n = h.get('npc_fr') if lang == 'fr' else h.get('npc_en')
            loc = h.get('loc_fr') if lang == 'fr' else h.get('loc_en')
            z = (h.get('zone_fr') if lang == 'fr' else h.get('zone_en')) if h.get('zone_en') not in ('Special',) else None
            if n:
                npc_s = E(n) + (f" <span class=\"v41-loc\">({E(loc)})</span>" if loc else '')
                if npc_s not in npc: npc = (npc + '<br>' if npc else '') + npc_s
                zz = (loc.rsplit(' ', 2)[0] if loc and loc[-1].isdigit() else z) or z
                if zz and E(zz) not in zone: zone = (zone + ', ' if zone else '') + E(zz)
            if status != 'official': status = 'quest'
    if x.get('rep'):
        r = x['rep']
        obt.append(E(L(lang, f"Réputation requise : {r['st_fr']} auprès de {r['fr']}", f"Requires {r['st_en']} with {r['en']}")))
    if not obt:
        obt.append(L(lang, '<span class="v41-na">Non indiquée dans les fichiers du jeu</span>', '<span class="v41-na">Not given in the game files</span>'))
    facts.append((L(lang, 'Obtention', 'How to get it'), '<br>'.join(dict.fromkeys(obt))))
    facts.append((L(lang, 'Zone', 'Zone'), zone or L(lang, '<span class="v41-na">non indiquée</span>', '<span class="v41-na">not given</span>')))
    facts.append((L(lang, 'PNJ', 'NPC'), npc or L(lang, '<span class="v41-na">non indiqué</span>', '<span class="v41-na">not given</span>')))
    if x.get('buy') and x['buy'] != {'g': 0, 's': 0, 'c': 1}:  # 1 pc = valeur de remplissage du client, non affichée
        facts.append((L(lang, 'Prix', 'Price'), E(money(x['buy'], lang)) + f" <span class=\"v41-loc\">({L(lang, 'prix inscrit dans les fichiers du jeu', 'price recorded in the game files')})</span>"))
    if x.get('skill'):
        s = x['skill']; facts.append((L(lang, 'Prérequis', 'Requires'), E(L(lang, f"{s['fr']} ({s['rank']})", f"{s['en']} ({s['rank']})"))))
    use = x.get('use_fr') if lang == 'fr' else x.get('use_en')
    use = re.sub(r'\s+', ' ', re.sub(r'\|c[0-9A-Fa-f]{8}|\|r', '', use or '')).strip()
    if use and '$' not in use:
        facts.append((L(lang, 'Effet', 'Effect'), E(use)))
    pd = x.get('pdesc_fr') if lang == 'fr' else x.get('pdesc_en')
    if pd: facts.append((L(lang, 'Description', 'Description'), E(pd)))
    ref = []
    if x.get('id'): ref.append(L(lang, f"objet n° {x['id']}", f"item #{x['id']}"))
    if x.get('spell_mount') and x.get('spells'): ref.append(L(lang, f"sort n° {x['spells'][0]}", f"spell #{x['spells'][0]}"))
    if x.get('species'): ref.append(L(lang, f"espèce n° {x['species']}", f"species #{x['species']}"))
    if ref: facts.append((L(lang, 'Référence', 'Reference'), E(' · '.join(ref))))
    return facts, status

STATUS = {
    'official': ('<span class="v41-st is-official">Officiel Blizzard</span>', '<span class="v41-st is-official">Official Blizzard</span>'),
    'game': ('<span class="v41-st is-game">Fichiers du jeu (client 1.60.1.70862)</span>', '<span class="v41-st is-game">Game files (client 1.60.1.70862)</span>'),
    'quest': ('<span class="v41-st is-pending">Obtention d’après les données de quêtes — à confirmer</span>', '<span class="v41-st is-pending">Acquisition from quest data — to be confirmed</span>'),
}

def card(x, lang, prefix_key):
    name = x['name_fr'] if lang == 'fr' else x['name_en']
    other = x['name_en'] if lang == 'fr' else x['name_fr']
    anchor = f"{prefix_key}-{x['id'] or ('s' + str(x.get('mount_id') or 'azurbie'))}"
    q = x.get('quality')
    tags = []
    if q is not None and q in QUAL: tags.append(f'<li class="v41-tag is-q{q}">{QUAL[q][0 if lang=="fr" else 1]}</li>')
    tags.append(f'<li class="v41-tag is-{x["faction"]}">{FAC[x["faction"]][0 if lang=="fr" else 1]}</li>')
    if x.get('level'): tags.append(f'<li class="v41-tag">{L(lang, "Niveau", "Level")} {x["level"]}</li>')
    if x.get('spell_mount'): tags.append(f'<li class="v41-tag">{L(lang, "Sort de classe", "Class spell")}</li>')
    facts, status = how_lines(x, lang)
    if x.get('official_only'): status = 'official'
    ic = x.get('icon')
    img = (f'<img class="v41-ic" src="{{P}}assets/icone-jeu-{ic}.webp" width="56" height="56" alt="{E(L(lang, "Icône du jeu : ", "Game icon: ") + name)}" loading="lazy" decoding="async">'
           if ic and str(ic) in MAN else f'<span class="v41-ic is-none" role="img" aria-label="{E(L(lang, "Pas d’image du jeu disponible", "No game image available"))}"></span>')
    qcls = f' is-q{q}' if q is not None else ''
    sub = f'<p class="v41-alt" lang="{"en" if lang=="fr" else "fr"}">{E(other)}</p>' if other and other != name else ''
    return (f'<article class="v41-card{qcls}" id="{anchor}">{img}<div class="v41-body"><h3 class="v41-name">{E(name)}</h3>{sub}'
            f'<ul class="v41-tags">{"".join(tags)}</ul><dl class="v41-facts">{"".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts)}</dl>'
            f'{STATUS[status][0 if lang=="fr" else 1]}</div></article>')

def grid(items, lang, key):
    return '<div class="v41-grid">' + ''.join(card(x, lang, key) for x in items) + '</div>'

def sort_key(x):
    return ((x.get('level') or 0), x['name_fr'].lower())

# ---------- groups ----------
for k in ('mounts', 'pets', 'toys'):
    for x in D[k]: fix_faction(x)
G = collections.OrderedDict()
def put(ref, items):
    G[ref] = items
mounts = D['mounts']; pets = D['pets']; toys = D['toys']
def by(items, g): return sorted([x for x in items if group_of(x) == g], key=sort_key)
M = {g: by(mounts, g) for g in ('heritage', 'pack', 'classe', 'quete', 'non-indique')}
M['echange'] = [x for x in M['quete'] if is_exchange(x)]; M['quete'] = [x for x in M['quete'] if not is_exchange(x)]
for fac in ('alliance', 'horde', 'both'):
    for lv in (40, 60):
        M[f'ni-{fac}-{lv}'] = [x for x in M['non-indique'] if x['faction'] == fac and (x.get('level') or 0) == lv]
    M[f'ni-{fac}-autre'] = [x for x in M['non-indique'] if x['faction'] == fac and (x.get('level') or 0) not in (40, 60)]
P = {g: by(pets, g) for g in ('heritage', 'abonnement', 'artisanat', 'quete', 'reputation', 'non-indique')}
Tt = {g: by(toys, g) for g in ('heritage', 'pack', 'artisanat', 'quete', 'reputation', 'non-indique')}
# toys with faction rule only -> keep in non-indique
frag = {}
def add(ref, items, key):
    if not items: return
    frag[ref] = {'count': len(items), 'fr': grid(items, 'fr', key), 'en': grid(items, 'en', key),
                 'names': {'fr': ' '.join(x['name_fr'] for x in items), 'en': ' '.join(x['name_en'] for x in items)}}
for g, items in M.items():
    if g != 'non-indique': add(f'montures-{g}', items, 'm')
for g, items in P.items(): add(f'mascottes-{g}', items, 'p')
for g, items in Tt.items(): add(f'jouets-{g}', items, 't')
# heritage page: 4 launch rewards (toy, pet, tabard, mount)
hid = {276236: 'toy', 277714: 'pet', 277718: 'mount'}
her = [x for x in toys + pets + mounts if x.get('id') in hid]
tab = D['tabard']; tab['faction'] = 'both'
her_sorted = [next(x for x in her if x['id'] == 276236), next(x for x in her if x['id'] == 277714), tab, next(x for x in her if x['id'] == 277718)]
add('heritage-lancement', her_sorted, 'h')

def pick_icon(items):
    for x in items:
        if x.get('icon') and str(x['icon']) in MAN: return x['icon']
counts = {
    'mounts': len(mounts), 'pets': len(pets), 'toys': len(toys),
    'mounts_known': sum(1 for x in mounts if group_of(x) != 'non-indique'),
    'pets_known': sum(1 for x in pets if group_of(x) != 'non-indique'),
    'toys_known': sum(1 for x in toys if group_of(x) != 'non-indique'),
    'img': sum(1 for x in mounts + pets + toys if x.get('icon') and str(x['icon']) in MAN),
    'noimg': [x['name_fr'] for x in mounts + pets + toys if not (x.get('icon') and str(x['icon']) in MAN)],
}
HUB = [
    ('montures', 'mounts', 'Montures', 'Mounts', counts['mounts'], counts['mounts_known'], pick_icon(M['heritage']) or pick_icon(mounts)),
    ('mascottes', 'companion-pets', 'Mascottes', 'Companion pets', counts['pets'], counts['pets_known'], pick_icon(P['heritage'])),
    ('jouets', 'toys', 'Jouets', 'Toys', counts['toys'], counts['toys_known'], pick_icon(Tt['heritage'])),
]
def hub_html(lang):
    out = ['<ul class="v41-hub">']
    for fr_slug, en_slug, fr, en, n, known, ic in HUB:
        href = f'{{P}}{lang}/{"objets" if lang=="fr" else "items"}/{fr_slug if lang=="fr" else en_slug}/'
        out.append(f'<li><a class="v41-hub-card" href="{href}"><img class="v41-ic" src="{{P}}assets/icone-jeu-{ic}.webp" width="56" height="56" alt="" loading="lazy" decoding="async">'
                   f'<span class="v41-hub-txt"><strong>{fr if lang=="fr" else en}</strong><span>{n} {L(lang, "fiches", "entries")} · {L(lang, "obtention connue", "known acquisition")} : {known}</span></span></a></li>')
    href = f'{{P}}{lang}/{"quetes/recompenses-heritage" if lang=="fr" else "quests/legacy-rewards"}/'
    out.append(f'<li><a class="v41-hub-card" href="{href}"><img class="v41-ic" src="{{P}}assets/icone-jeu-{tab["icon"]}.webp" width="56" height="56" alt="" loading="lazy" decoding="async">'
               f'<span class="v41-hub-txt"><strong>{L(lang, "Héritage", "Legacy")}</strong><span>{L(lang, "4 récompenses du lancement (jouet, mascotte, tabard, monture)", "4 launch rewards (toy, pet, tabard, mount)")}</span></span></a></li>')
    out.append('</ul>')
    return ''.join(out)
frag['hub'] = {'count': 4, 'fr': hub_html('fr'), 'en': hub_html('en'), 'names': {'fr': 'montures mascottes jouets héritage', 'en': 'mounts pets toys legacy'}}

data_out = PIPE / 'data/collections-v41.json'
data_out.write_text(json.dumps(frag, ensure_ascii=False))
assets = PIPE / 'public/v2/assets'
for f in MAN: shutil.copyfile(HERE / f'out/icons/{f}.webp', assets / f'icone-jeu-{f}.webp')
json.dump(counts, open(HERE / 'out/counts.json', 'w'), ensure_ascii=False, indent=1)
print({k: v['count'] for k, v in frag.items()})
print({k: v for k, v in counts.items() if k != 'noimg'}, 'noimg', counts['noimg'])
