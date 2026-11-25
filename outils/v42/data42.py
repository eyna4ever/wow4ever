"""v42 (t407u) — chargement des données : fichiers du client Forever 1.60.1.70862 (CDN officiel Blizzard)
+ base de données Forever non officielle (PNJ, vendeurs, formateurs, cartes, quêtes) — toujours « à confirmer »."""
import sys, os, re, json, glob, html, collections as C
sys.path.insert(0, '/workspace/wowkipedia-v21-elite/collections-v41/outils'); _cwd = os.getcwd(); os.chdir('/workspace/wowkipedia-v21-elite/collections-v41/outils')
from load import T
import db2
R = '/workspace/wowkipedia-v21-elite'; RS = f'{R}/v42-research'
it = T('Item'); sp = T('ItemSparse'); spf = T('ItemSparse', 'frFR'); sla = T('SkillLineAbility')
sn = T('SpellName'); snf = T('SpellName', 'frFR')
srg = db2.read(f'{RS}/db2/SpellReagents.enUS.db2', 'SpellReagents')
area = db2.read(f'{RS}/db2/AreaTable.enUS.db2', 'AreaTable'); areaf = db2.read(f'{RS}/db2/AreaTable.frFR.db2', 'AreaTable')
QE, QF = {}, {}
for f in glob.glob('../cache/quests/en-*.json'): QE.update({int(k): v for k, v in json.load(open(f)).items()})
for f in glob.glob('../cache/quests/fr-*.json'): QF.update({int(k): v for k, v in json.load(open(f)).items()})
os.chdir(_cwd)
M = {int(k): v for k, v in json.load(open(f'{RS}/materials.json')).items()}
ND = json.load(open(f'{RS}/npc-data.json')); NP = ND['npcs']; MAPS = ND['maps']
RAW = json.load(open(f'{RS}/raw/npc-liste-en.json'))  # [slug, name, ?, zone, level, roles, nquests]
APOS = lambda s: (s or '').replace('’', "'")
ZFR = {}
for k, v in area.items():
    if v['ParentAreaID'] == 0 and k in areaf: ZFR.setdefault(v['AreaName_lang'], areaf[k]['AreaName_lang'])
ZFR.update({'Zephras Isle': 'Île de Zéphras', "Shen'dralas": "Shen'dralas", 'Riverglades': 'Rives Claires'})
# noms français des PNJ : seulement quand les données de quêtes françaises donnent un nom distinct
NFR = {}
for k, q in QE.items():
    for key in ('start', 'ende'):
        a, b = (q.get(key) or {}).get('npc'), (QF.get(k, {}).get(key) or {}).get('npc')
        if a and b and a != b: NFR.setdefault(a, b)
# noms étranges (décision d) : exclus ou signalés
EXCLUDE = re.compile(r'^Materialbot$')
GT = ('Gastwirt|Gastwirtin|Schmied|Schmiedin|Kriegerheld|Steinwache|Auktionator|Auktionatorin|Kampfmeister|Stallmeister|Flugmeister|Flugmeisterin|Bankier|Bauer|Bandit|Händler|Händlerin|'
      'Lehrer|Lehrerin|Wache|Späher|Krieger|Jäger|Jägerin|Magier|Magierin|Priester|Priesterin|Schamane|Schamanin|Hexenmeister|Hexenmeisterin|Schurke|Schurkin|Druide|Druidin|Lehrling|'
      'Meister|Meisterin|Großknecht|Bürger|Arbeiter|Hauptmann|Leutnant|Soldat|Kultist|Seher|Seherin|Wächter|Wächterin|Hüter|Hüterin|Kommandant|Oberst|Kundschafter|Rekrut|Diener|Dienerin|Bote|Botin|Fürst|Gräfin|Graf')
GERMAN = re.compile(r'[äöüßÄÖÜ]|\b(der|die|das|von|des|vom|und|zum|zur|dem|den)\b|^(' + GT + r')\b')
def odd(name):
    if not name or EXCLUDE.search(name): return 'exclude'
    if GERMAN.search(name): return 'german'
    return None
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
L = lambda l, fr, en: en if l == 'en' else fr
def zname(z, l):
    if not z: return L(l, 'zone non indiquée', 'zone not given')
    return ZFR.get(z, z) if l == 'fr' else z
def iname(i, l):
    r = (spf.get(i) if l == 'fr' else sp.get(i)) or {}
    return r.get('Display_lang') or ((sp.get(i) or {}).get('Display_lang') if l == 'fr' else None)
def qname(q, l):
    if l == 'fr' and q in QF and QF[q].get('n'): return QF[q]['n']
    return QE[q]['n'] if q in QE else str(q)
COORD = {}
for z, rows in MAPS.items():
    for r in rows:
        if r['xy']: COORD.setdefault((r['name'], z), tuple(r['xy']))
QPLACE = C.defaultdict(dict)  # zone -> npc -> {xy, start:set, end:set}
for qid, q in QE.items():
    for key in ('start', 'ende'):
        s = q.get(key) or {}; m = re.match(r'(.+?) ([\d.]+), ([\d.]+)$', s.get('ort') or '')
        if s.get('npc') and m:
            z = m.group(1); COORD.setdefault((s['npc'], z), (float(m.group(2)), float(m.group(3))))
            d = QPLACE[z].setdefault(s['npc'], {'start': set(), 'end': set(), 'xy': (float(m.group(2)), float(m.group(3)))})
            d['start' if key == 'start' else 'end'].add(qid)
for d in NP.values():
    if d.get('coord'): COORD.setdefault((d['name'], d['coord_zone']), tuple(d['coord']))
def xy(name, z):
    c = COORD.get((name, z)); return f'{c[0]:g}, {c[1]:g}' if c else None
def money(c, l):
    if c is None: return L(l, 'prix non indiqué', 'price not given')
    if c == 0: return L(l, 'gratuit', 'free')
    g, s, k = c // 10000, c // 100 % 100, c % 100; p = []
    if g: p.append(f"{g} {L(l, 'po', 'g')}")
    if s: p.append(f"{s} {L(l, 'pa', 's')}")
    if k: p.append(f"{k} {L(l, 'pc', 'c')}")
    return ' '.join(p)
PROF = {129: ('Secourisme', 'First Aid', 'recettes-secourisme', 'first-aid-recipes'), 164: ('Forge', 'Blacksmithing', 'recettes-forge', 'blacksmithing-recipes'),
        165: ('Travail du cuir', 'Leatherworking', 'recettes-travail-du-cuir', 'leatherworking-recipes'), 171: ('Alchimie', 'Alchemy', 'recettes-alchimie', 'alchemy-recipes'),
        182: ('Herboristerie', 'Herbalism', 'recettes-herboristerie', 'herbalism-recipes'), 185: ('Cuisine', 'Cooking', 'recettes-cuisine', 'cooking-recipes'),
        186: ('Minage', 'Mining', 'recettes-minage', 'mining-recipes'), 197: ('Couture', 'Tailoring', 'recettes-couture', 'tailoring-recipes'),
        202: ('Ingénierie', 'Engineering', 'recettes-ingenierie', 'engineering-recipes'), 333: ('Enchantement', 'Enchanting', 'recettes-enchantement', 'enchanting-recipes'),
        356: ('Pêche', 'Fishing', 'recettes-peche', 'fishing-recipes'), 393: ('Dépeçage', 'Skinning', 'recettes-depecage', 'skinning-recipes')}
PROF_BY_FR = {v[0]: k for k, v in PROF.items()}
PROF_KEY = {129: 'first-aid', 164: 'blacksmithing', 165: 'leatherworking', 171: 'alchemy', 182: 'herbalism', 185: 'cooking', 186: 'mining', 197: 'tailoring', 202: 'engineering', 333: 'enchanting', 356: 'fishing', 393: 'skinning'}
TLOW = {r['Spell']: r['TrivialSkillLineRankLow'] for r in sla.values() if r['SkillLine'] in PROF}
REAG = {r['SpellID']: [(i, n) for i, n in zip(r['Reagent'], r['ReagentCount']) if i] for r in srg.values()}
