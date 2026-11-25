#!/usr/bin/env python3
"""v42b (t409u/t410u) — recherche détaillée : ajoute des ancres stables (id) aux lignes, PNJ, vendeurs, cartes et sections
des pages construites, et écrit un index léger par langue (search-detail-fr.json / search-detail-en.json), chargé à la demande
par wk-header.js. Chaque entrée : nom, type, page (zone, métier…), ancre exacte, précision courte.
Usage : search42b.py WIKI_DIR   (modifie les pages en place, écrit les deux index, imprime un résumé JSON)."""
import sys, re, json, html, unicodedata
from pathlib import Path
W = Path(sys.argv[1])
TYPES = [('npc', 'PNJ', 'NPC'), ('creature', 'Créature', 'Creature'), ('boss', 'Boss', 'Boss'), ('quest', 'Quête', 'Quest'),
         ('quest_item', 'Objet de quête', 'Quest item'), ('vendor_item', 'Objet vendu', 'Vendor item'), ('material', 'Matériau', 'Material'),
         ('recipe', 'Recette', 'Recipe'), ('mount', 'Monture', 'Mount'), ('pet', 'Mascotte', 'Pet'), ('toy', 'Jouet', 'Toy'),
         ('heritage', 'Héritage', 'Legacy'), ('item', 'Objet', 'Item'), ('object', 'Objet du décor', 'World object'),
         ('class', 'Classe, sort ou maître', 'Class, spell or trainer'), ('passage', 'Article, guide ou actualité', 'Article, guide or news'), ('place', 'Lieu', 'Place'), ('section', 'Section de page', 'Page section'),
         ('entry', 'Élément de page', 'Page entry')]
TI = {t[0]: i for i, t in enumerate(TYPES)}
SKIP_SEC = {'historique-des-corrections', 'sources', 'confirme-a-confirmer', 'dates', 'dates-cles', 'points-cles', 'en-bref', 'informations-non-indiquees', 'lire-cette-liste'}
TXT = lambda s: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
def NAME(s):
    s = re.sub(r'<span class="(v42-pill|v41-loc|v41-na)[^"]*">.*?</span>', ' ', s, flags=re.S)
    s = re.sub(r'<sup.*?</sup>', ' ', s, flags=re.S)
    return re.sub(r'\s+×\d+$', '', TXT(s)).strip(' ·—-')
def slug(s):
    s = unicodedata.normalize('NFD', s); s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40] or 'x'
CARD_TYPE = [(r'montures|mounts', 'mount'), (r'mascottes|companion-pets', 'pet'), (r'jouets|toys', 'toy'), (r'heritage|legacy', 'heritage'), (r'materiaux|materials', 'material')]
def card_type(slug_):
    for rx, t in CARD_TYPE:
        if re.search(rx, slug_): return t
    return 'item'
def row_type(cat, pslug, sec_title, sub, ctx, head):
    st = (sec_title + ' ' + sub).lower()
    if cat in ('zones',):
        if ctx == 'vendor': return 'vendor_item'
        if ctx == 'others': return 'npc'
        if re.search(r'donneurs|quest givers', st): return 'npc'
        if re.search(r'objets de quête|quest items', st): return 'quest_item'
        if re.search(r'quête|quest', st): return 'quest'
        if re.search(r'lieux|places|sous-zones|subzones|points d’intérêt|points of interest', st): return 'place'
        return 'entry'
    if cat in ('metiers', 'professions'):
        if re.search(r'^recettes|-recipes$', pslug): return 'recipe'
        return 'entry'
    if cat in ('objets', 'items'): return 'item'
    if cat in ('quetes', 'quests'):
        if re.search(r'heritage|legacy', pslug): return 'heritage'
        return 'quest'
    if cat in ('creatures', 'donjons-raids', 'dungeons-raids'):
        if re.search(r'boss', st + ' ' + pslug): return 'boss'
        if re.search(r'recette|recipe', st): return 'recipe'
        if re.search(r'quête|quest', st) and cat != 'creatures': return 'quest'
        return 'creature'
    if cat == 'classes': return 'class'
    return 'entry'
COLS = {'role': r'^(rôle|role|type de pnj)$', 'zone': r'^(zone|lieu|location)$', 'quest': r'^(quête|quest)$', 'from': r'^(obtenu sur ou dans|obtained from)$',
        'level': r'^(niveau|level|compétence|skill)$', 'class': r'^(classes?|classe)$', 'price': r'^(prix|price)$'}
def detail_from(cells, head, typ, lang):
    hl = [TXT(h).lower() for h in head]
    get = lambda k: next((TXT(cells[i - 1]) for i, h in enumerate(hl) if i >= 1 and i - 1 < len(cells) and re.match(COLS[k], h)), '')
    parts = []
    if typ in ('npc', 'creature', 'boss'):
        r = get('role'); z = get('zone'); lv = get('level')
        parts = [x for x in (r, z, (('niveau ' if lang == 'fr' else 'level ') + lv) if lv and lv not in ('—', 'non indiqué', 'not given') else '') if x and x not in ('—', 'non indiqué', 'not given')]
    elif typ == 'quest_item':
        q = get('quest'); f = get('from'); parts = [x for x in ((('quête : ' if lang == 'fr' else 'quest: ') + q) if q else '', f) if x and x not in ('non indiqué', 'not given')]
    elif typ == 'recipe':
        lv = get('level'); parts = [(('compétence ' if lang == 'fr' else 'skill ') + lv)] if lv and re.match(r'^\d+$', lv) else []
    elif typ == 'vendor_item':
        p = get('price'); parts = [p] if p else []
    return ' · '.join(parts)[:70]
TOK = re.compile(r'<h3(?![^>]*v41-name)[^>]*>(?P<h3>.*?)</h3>|<thead><tr>(?P<head>.*?)</tr></thead>|<details class="v42-vendor"><summary>(?P<sum>.*?)</summary>|(?P<dclose></details>)'
                 r'|(?P<tr><tr>)(?=<th scope="row">)|(?P<li><li>)(?=<strong>)|(?P<pp><p>|<li>)(?!<strong>)|<article class="v41-card[^"]*" id="(?P<card>[^"]+)">', re.S)
PROSE = {'classes', 'races', 'jcj', 'pvp', 'actualites', 'news', 'guides', 'le-jeu', 'the-game', 'glossaire', 'glossary'}
NAMECOL = re.compile(r'^(nom|name|maître|maitre|trainer|pnj|npc|quête|quest|recette|recipe|objet|item|boss|créature|creature|sort|spell|arme|weapon|monture|mount)', re.I)
# pages Discord / correctifs : règle « Discord inchangé sauf compteurs » → aucune ancre ajoutée, seules les sections existantes sont indexées
FROZEN = {'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en/news/forever-hotfixes-november-5-6/',
          'fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/', 'en/news/official-wow-portal-room-discord-welcomes-forever-players/',
          # pages verrouillées depuis v8 (empreinte d’article inchangée exigée par test_wiki_content_unchanged_since_v8)
          'en/dungeons-raids/raids-and-dungeons/', 'en/glossary/legacy-and-ruleset-glossary/', 'en/news/irvine-improv-poster-signing/',
          'en/pvp/pvp-honor-and-ranks/', 'en/races/the-skyborne/', 'fr/actualites/dedicaces-irvine-improv/',
          'fr/glossaire/lexique-heritage-et-ensembles/', 'fr/jcj/jcj-honneur-et-rangs/'}
def process(f, lang, cat, pslug, ptitle, ppath, recs, pages, stats):
    t = f.read_text('utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', t)); orig_ids = set(ids); first = len(recs)
    def newid(name):
        b = 'r-' + slug(name); i = b; n = 2
        while i in ids: i = f'{b}-{n}'; n += 1
        ids.add(i); return i
    pi = len(pages); pages.append([ppath, ptitle])
    out = []; pos = 0; seen = set()
    def add(name, typ, anchor, detail='', text=''):
        if not name or len(name) > 120: return
        if (name.lower(), typ) in seen and typ not in ('section', 'passage') and not text: return
        seen.add((name.lower(), typ))
        recs.append([name, TI[typ], pi, anchor] + ([detail] if detail or text else []) + ([text] if text else [])); stats[typ] = stats.get(typ, 0) + 1
    for sm in re.finditer(r'<section class="article-section" id="([^"]+)"[^>]*>(.*?)</section>', t, re.S):
        sid, body = sm.group(1), sm.group(2)
        if sid in SKIP_SEC: continue
        stitle = NAME(re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S).group(1)) if re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S) else ''
        if stitle: add(stitle, 'section', sid)
        start = sm.start(2); sub = ''; head = []; ctx = ''; vendor = ('', '')
        for m in TOK.finditer(body):
            a = start + m.start()
            if m.group('h3') is not None: sub = NAME(m.group('h3')); ctx = ''; head = []
            elif m.group('head') is not None: head = re.findall(r'<th scope="col">(.*?)</th>', m.group('head'), re.S)
            elif m.group('sum') is not None:
                s_ = m.group('sum'); nm = NAME((re.search(r'<strong>(.*?)</strong>', s_, re.S) or [None, ''])[1])
                if re.match(r'(Autres PNJ|Other NPCs|Composants de chaque recette|Reagents of each recipe)', nm): ctx = 'others' if nm.startswith(('Autres', 'Other')) else 'reagents'; head = []; continue
                if cat == 'zones':
                    vid = newid(nm); out.append(t[pos:a] + f'<details class="v42-vendor" id="{vid}">'); pos = a + len('<details class="v42-vendor">')
                    add(nm, 'npc', vid, 'vendeur' if lang == 'fr' else 'vendor'); ctx = 'vendor'; vendor = (nm, vid); head = []
            elif m.group('dclose') is not None: ctx = ''; head = []
            elif m.group('tr') is not None:
                rm = re.match(r'<tr><th scope="row">(.*?)</th>(.*?)</tr>', body[m.start():], re.S)
                if not rm: continue
                nm = NAME(rm.group(1)); cells = re.findall(r'<td[^>]*>(.*?)</td>', rm.group(2), re.S)
                if ctx == 'reagents': continue
                hl = [TXT(h) for h in head]
                if hl and not NAMECOL.match(hl[0]):
                    j = next((i for i, h in enumerate(hl) if i and NAMECOL.match(h) and i - 1 < len(cells)), None)
                    if j is not None:
                        extra = ' · '.join(x for x in [nm] + [NAME(c) for i, c in enumerate(cells) if i != j - 1][:3] if x and len(x) < 40)
                        nm = NAME(cells[j - 1])
                        rid = newid(nm); out.append(t[pos:a] + f'<tr id="{rid}">'); pos = a + 4
                        add(nm, 'class' if cat == 'classes' else row_type(cat, pslug, stitle, sub, ctx, head), rid, ((hl[j] + ' · ') if cat == 'classes' else '') + extra[:60]); continue
                typ = row_type(cat, pslug, stitle, sub, ctx, head)
                if ctx == 'vendor':
                    add(nm, 'vendor_item', vendor[1], (('vendu par ' if lang == 'fr' else 'sold by ') + vendor[0] + (' · ' + TXT(cells[0]) if cells else ''))[:70]); continue
                if typ == 'npc' and ctx == 'others':
                    hl = [TXT(h).lower() for h in head]; role = next((TXT(cells[i - 1]) for i, h in enumerate(hl) if i and re.match(COLS['role'], h) and i - 1 < len(cells)), '')
                    if re.search(r'boss', role, re.I): typ = 'boss'
                    elif re.search(r'objectif|objective|mob|créature|creature', role, re.I): typ = 'creature'
                rid = newid(nm); out.append(t[pos:a] + f'<tr id="{rid}">'); pos = a + 4
                det = detail_from(cells, head, typ, lang)
                if typ == 'npc' and cat == 'zones' and not ctx: det = ('donneur ou receveur de quêtes' if lang == 'fr' else 'quest giver or turn-in') + (' · ' + TXT(cells[0]) if cells else '')
                add(nm, typ, rid, det)
                if cat == 'zones' and re.search(r'donneurs|quest givers', (stitle + ' ' + sub).lower()):
                    for c in cells[1:3]:
                        for q in re.split(r',\s+', re.sub(r'\s*\(\+\d+\)$', '', TXT(c))):
                            if q and q != '—': add(q, 'quest', rid, (('donnée ou rendue à ' if lang == 'fr' else 'given or taken by ') + nm)[:70])
            elif m.group('li') is not None:
                lm = re.match(r'<li><strong>(.*?)</strong>(.*?)</li>', body[m.start():], re.S)
                if not lm: continue
                nm = NAME(lm.group(1)); rest = TXT(re.sub(r'<span class="v42-pill[^"]*">.*?</span>', '', lm.group(2)))
                st_ = (stitle + ' ' + sub).lower()
                if cat == 'zones' and re.search(r'formateurs|trainers', st_): typ = 'npc'
                elif cat == 'zones' and re.search(r'décor|world objects', st_): typ = 'object'
                elif cat == 'classes': typ = 'class'
                else: typ = row_type(cat, pslug, stitle, sub, '', [])
                rid = newid(nm); out.append(t[pos:a] + f'<li id="{rid}">'); pos = a + 4
                det = rest.lstrip('—·( ').split(' · ')[0]
                if cat == 'zones' and typ == 'npc': det = ('formateur · ' if lang == 'fr' else 'trainer · ') + det
                add(nm, typ, rid, det[:70] if typ in ('npc', 'class') else '')
            elif m.group('pp') is not None:
                if cat not in PROSE: continue
                op = m.group('pp'); close = '</p>' if op == '<p>' else '</li>'
                e_ = body.find(close, m.end())
                if e_ < 0: continue
                txt = TXT(re.sub(r'<sup.*?</sup>', ' ', body[m.end():e_], flags=re.S))
                if len(txt) < 20: continue
                typ = 'class' if cat == 'classes' else 'passage'
                rid = newid((stitle or ptitle) + ' passage'); out.append(t[pos:a] + op[:-1] + f' id="{rid}">'); pos = a + len(op)
                add(stitle or ptitle, typ, rid, '', txt[:600])
            elif m.group('card') is not None:
                cm = re.search(r'<h3 class="v41-name">(.*?)</h3>', body[m.start():m.start() + 4000], re.S)
                if cm:
                    ct = card_type(pslug)
                    add(NAME(cm.group(1)), ct, m.group('card'), ptitle.split(' : ')[0] if ct == 'material' else '')
    out.append(t[pos:]); nt = ''.join(out)
    assert len(re.findall(r'\sid="([^"]+)"', nt)) == len(set(re.findall(r'\sid="([^"]+)"', nt))), f'ids en double {f}'
    if ppath in FROZEN:
        keep = [r for r in recs[first:] if r[3] in orig_ids]
        for r in recs[first:]:
            if r[3] not in orig_ids: stats[TYPES[r[1]][0]] -= 1
        recs[first:] = keep; return
    if nt != t: f.write_text(nt, 'utf-8')
# t411u (Mathieu : « rajoute sanglier comme ça sa fonctionnera ») : mots-clés de recherche FR cachés (index FR seulement,
# aucun texte de page modifié, aucun nom de créature inventé). Mot anglais (ou expression) du nom -> mots-clés français.
# Familles et types : noms français officiels des fichiers du client 70862 (CreatureFamily / CreatureType, frFR) ;
# termes demandés par Mathieu hors fichiers du client (kodo, murloc, gnoll, kobold, harpie, centaure, huran, vautour, busard, squelette).
CLIENT = {'wolf': 'loup', 'wolves': 'loup', 'worg': 'loup', 'cat': 'félin', 'panther': 'félin', 'tiger': 'félin', 'lynx': 'félin', 'cougar': 'félin',
  'leopard': 'félin', 'lion': 'félin', 'jaguar': 'félin', 'nightsaber': 'félin', 'spider': 'araignée', 'bear': 'ours', 'boar': 'sanglier',
  'crocolisk': 'crocilisque', 'carrion bird': 'charognard', 'crab': 'crabe', 'gorilla': 'gorille', 'raptor': 'raptor', 'tallstrider': 'haut-trotteur',
  'plainstrider': 'haut-trotteur', 'strider': 'haut-trotteur', 'scorpid': 'scorpide', 'turtle': 'tortue', 'imp': 'diablotin', 'bat': 'chauve-souris',
  'hyena': 'hyène', 'owl': 'oiseau de proie', 'hawk': 'oiseau de proie', 'eagle': 'oiseau de proie', 'wind serpent': 'serpent des vents',
  'fox': 'renard', 'felhunter': 'chasseur corrompu', 'voidwalker': 'marcheur du vide', 'succubus': 'succube', 'doomguard': 'garde funeste',
  'core hound': 'chien du magma', 'felguard': 'gangregarde', 'elemental': 'élémentaire', 'undead': 'mort-vivant', 'demon': 'démon',
  'dragonkin': 'draconien', 'giant': 'géant', 'mechanical': 'mécanique', 'critter': 'bestiole'}
ASKED = {'kodo': 'kodo', 'murloc': 'murloc', 'gnoll': 'gnoll', 'kobold': 'kobold', 'harpy': 'harpie', 'centaur': 'centaure', 'quilboar': 'huran',
  'vulture': 'vautour charognard', 'buzzard': 'busard charognard', 'skeleton': 'squelette mort-vivant', 'skeletal': 'squelette mort-vivant'}
SYN = sorted([k, v] for k, v in {**CLIENT, **ASKED}.items())
summary = {}
for lang in ('fr', 'en'):
    recs, pages, stats = [], [], {}
    for f in sorted((W / lang).glob('*/*/index.html')):
        t = f.read_text('utf-8')
        if 'http-equiv="refresh"' in t: continue
        rel = f.relative_to(W).parent.as_posix() + '/'
        cat, pslug = rel.split('/')[1], rel.split('/')[2]
        ptitle = TXT(re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S).group(1))
        process(f, lang, cat, pslug, ptitle, rel, recs, pages, stats)
    # compactage : ancre omise ("") quand elle vaut r-<slug(nom)> (recalculée par wk-header.js) ; précisions répétées en table
    dcount = {}
    for r in recs:
        if len(r) > 4: dcount[r[4]] = dcount.get(r[4], 0) + 1
    dl = sorted([d for d, n in dcount.items() if n > 1], key=lambda d: -dcount[d]); di = {d: i for i, d in enumerate(dl)}
    comp = []
    for r in recs:
        a = '' if r[3] == 'r-' + slug(r[0]) else r[3]
        x = [r[0], r[1], r[2], a]
        if len(r) > 4: x.append(di[r[4]] if r[4] in di else r[4])
        if len(r) > 5: x.append(r[5])
        comp.append(x)
    data = {'v': 1, 'lang': lang, 'types': [[k, fr, en] for k, fr, en in TYPES], 'pages': pages, 'd': dl, 'r': comp}
    if lang == 'fr': data['syn'] = SYN  # t411u : mots-clés FR cachés pour les créatures aux noms seulement anglais
    p = W / f'search-detail-{lang}.json'; p.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    summary[lang] = dict(records=len(recs), pages=len(pages), bytes=p.stat().st_size, types=stats)
print(json.dumps(summary, ensure_ascii=False, indent=1))
