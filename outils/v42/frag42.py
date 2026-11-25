#!/usr/bin/env python3
"""v42 (t407u) — fragments HTML (FR/EN) pour les blocs « collection » du pipeline :
  matériaux par famille (cartes « où le trouver »), page d’accueil des matériaux, matériaux de chaque page de recettes,
  annuaire « PNJ : où les trouver » de chaque zone. Écrit PIPE/data/collections-v42.json + out/counts42.json, copie les icônes."""
import sys, re, json, shutil, collections as C
from pathlib import Path
import data42 as D
from data42 import E, L, M, NP, MAPS, RAW, QE, QF, zname, iname, qname, xy, money, odd, PROF, PROF_BY_FR, TLOW, REAG
PIPE = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/v42-pipeline')
OUT = Path('/workspace/wowkipedia-v21-elite/v42-test/out'); OUT.mkdir(parents=True, exist_ok=True)
ICONS = Path(D.RS) / 'icons'
CONF = lambda l: f'<span class="v42-pill is-draft">{L(l, "à confirmer", "to be confirmed")}</span>'
GAME = lambda l: f'<span class="v42-pill is-game">{L(l, "fichiers du jeu", "game files")}</span>'
NA = lambda l, fr='non indiqué', en='not given': f'<span class="v41-na">{L(l, fr, en)}</span>'
GER = lambda l: f' <span class="v41-loc">({L(l, "nom allemand dans la source, à confirmer", "German name in the source, to be confirmed")})</span>'
def npcname(n, l):
    o = odd(n)
    if o == 'exclude': return None
    return E(D.NFR.get(n, n) if l == 'fr' else n) + (GER(l) if o == 'german' else '')
CAT = lambda l: L(l, 'metiers', 'professions')
FRAG = {}; STATS = {}
used_icons = set()
# ---------------- familles ----------------
FAMS = [('minerais', 'materiaux-minerais-barres-pierres', 'materials-ore-bars-stone', 'Minerais, barres et pierres', 'Ore, bars and stone', {'Métal et pierre'}),
        ('herbes', 'materiaux-herbes', 'materials-herbs', 'Herbes', 'Herbs', {'Herbe'}),
        ('cuirs', 'materiaux-cuirs-peaux', 'materials-leather-hides', 'Cuirs, peaux et écailles', 'Leather, hides and scales', {'Cuir'}),
        ('tissus', 'materiaux-tissus', 'materials-cloth', 'Tissus', 'Cloth', {'Tissu'}),
        ('viandes', 'materiaux-viandes-ingredients', 'materials-meat-ingredients', 'Viandes et ingrédients de cuisine', 'Meat and cooking ingredients', {'Viande'}),
        ('elements', 'materiaux-elements-enchantement', 'materials-elemental-enchanting', 'Éléments et matériaux d’enchantement', 'Elemental and enchanting materials', {'Élémentaire', 'Enchantement'}),
        ('pieces', 'materiaux-pieces-ingenierie', 'materials-engineering-parts', 'Pièces d’ingénierie', 'Engineering parts', {'Pièces'}),
        ('divers', 'materiaux-composants-divers', 'materials-other-reagents', 'Fils, fioles, teintures et autres composants', 'Thread, vials, dyes and other reagents', {'Autre', 'Composant'}),
        ('objets', 'materiaux-objets-utilises', 'materials-items-used', 'Objets utilisés comme composants', 'Items used as reagents', None)]
FAM_OF = {}
for i, m in M.items():
    FAM_OF[i] = next((f for f in FAMS if f[5] and m['fam'] in f[5]), FAMS[-1])
def mat_href(i, l):
    f = FAM_OF[i]; return f'{{P}}{l}/{CAT(l)}/{f[1] if l == "fr" else f[2]}/#mat-{i}'
def mname(i, l):
    n = iname(i, l)
    return n if n else L(l, f'objet n° {i} (nom non lisible)', f'item #{i} (unreadable name)')
def mat_link(i, l):
    return f'<a href="{mat_href(i, l)}">{E(mname(i, l))}</a>' if i in M else E(iname(i, l) or (L(l, 'objet n° ', 'item #') + str(i)))
def prof_link(p, l):
    fr, en, sfr, sen = PROF[p]; return f'<a href="{{P}}{l}/{CAT(l)}/{sfr if l == "fr" else sen}/">{E(L(l, fr, en))}</a>'
CLASS_GROUP = {0: ('Consommables (potions, élixirs, nourriture…)', 'Consumables (potions, elixirs, food…)'), 2: ('Armes', 'Weapons'), 4: ('Armures et bijoux', 'Armour and jewellery'),
               6: ('Projectiles', 'Projectiles'), 9: ('Recettes', 'Recipes'), 12: ('Objets de quête', 'Quest items'), 15: ('Divers', 'Miscellaneous')}
def subgroup(m, fam):
    if not m['en']: return ('sans-nom', 'Nom non lisible dans les fichiers du jeu', 'Name unreadable in the game files')
    en = m['en']
    if fam[0] == 'minerais':
        if m['id'] in (249391, 249425, 249426): return ('rares', 'Matériaux rares de Forever', 'Forever scarce materials')
        if en.endswith(' Ore') or en == 'Coal': return ('minerais', 'Minerais et charbon', 'Ores and coal')
        if en.endswith(' Bar') or 'Ingot' in en or 'Plates' in en: return ('barres', 'Barres et lingots', 'Bars and ingots')
        if 'Stone' in en or 'Shard' in en: return ('pierres', 'Pierres, éclats et silex', 'Stones, shards and grinding stones')
        return ('autres', 'Autres', 'Other')
    if fam[0] == 'objets':
        c = D.it[m['id']]['ClassID'] if m['id'] in D.it else None
        fr, en_ = CLASS_GROUP.get(c, ('Autres objets', 'Other items')); return (f'classe-{c}', fr, en_)
    lv = m['ilvl'] or 0
    for lo, hi in ((0, 15), (16, 30), (31, 45), (46, 999)):
        if lo <= lv <= hi:
            return (f'niveau-{lo if lo else 1}-{hi if hi < 999 else "plus"}', f'Niveau d’objet {lo if lo else 1}–{hi}' if hi < 999 else f'Niveau d’objet {lo} et plus', f'Item level {lo if lo else 1}–{hi}' if hi < 999 else f'Item level {lo} and up')
GATHER = {'minerais': ('Gisements (minerai, pierre) : non indiqué — aucune source Forever autorisée ne donne leur position', 'Nodes (ore, stone): not given — no allowed Forever source gives their location'),
          'herbes': ('Lieux de cueillette : non indiqué — aucune source Forever autorisée ne donne leur position', 'Where it grows: not given — no allowed Forever source gives the locations'),
          'cuirs': ('Créatures à dépecer : non indiqué — aucune source Forever autorisée ne les donne', 'Creatures to skin: not given — no allowed Forever source gives them')}
QUAL = {0: ('Médiocre', 'Poor'), 1: ('Classique', 'Common'), 2: ('Inhabituel', 'Uncommon'), 3: ('Rare', 'Rare'), 4: ('Épique', 'Epic'), 5: ('Légendaire', 'Legendary')}
def vprice(item, price, per, l):
    if price is not None: return money(price, l) + ((' / ' + str(per)) if per and per > 1 else '')
    s = D.sp.get(item) or {}; b = s.get('BuyPrice')
    if b is None: return NA(l, 'prix non indiqué', 'price not given')
    vs = s.get('VendorStackCount') or 1
    return money(b, l) + ((' / ' + str(vs)) if vs > 1 else '') + f' <span class="v41-loc">({L(l, "prix de base, fichiers du jeu", "base price, game files")})</span>'
def mat_sources(m):
    sold = [s for s in m['sold'] if odd(s['npc']) != 'exclude']; drop = [d for d in m['dropped'] if odd(d['npc']) != 'exclude']
    return sold, drop
def card(m, fam, l):
    i = m['id']; name = mname(i, l); sold, drop = mat_sources(m)
    where = []
    gathered = not m['made_by'] and fam[0] in GATHER and m['en'] and (fam[0] != 'minerais' or subgroup(m, fam)[0] in ('minerais', 'pierres', 'rares'))
    if gathered: where.append(f'<li>{NA(l, *GATHER[fam[0]])}</li>')
    for mb in m['made_by']:
        reag = ', '.join(f'{n}× {mat_link(r, l)}' for r, n in mb['reag'])
        sk = TLOW.get(mb['spell']); sk = f', {L(l, "compétence", "skill")} {sk}' if sk else ''
        rn = (mb['fr'] if l == 'fr' else mb['en']) or mb['en']
        where.append(f'<li>{L(l, "Fabrication", "Crafted")} : <strong>{E(rn)}</strong> ({prof_link(mb["prof"], l)}{sk}) — {reag} {GAME(l)}</li>')
    for s in sold[:6]:
        c = xy(s['npc'], s['zone'])
        where.append(f'<li>{L(l, "Vendu par", "Sold by")} <strong>{npcname(s["npc"], l)}</strong> ({E(zname(s["zone"], l))}{", " + c if c else ""}) — {vprice(i, s["price"], s["per"], l)} {CONF(l)}</li>')
    if len(sold) > 6: where.append(f'<li>{L(l, "et", "and")} {len(sold) - 6} {L(l, "autres vendeurs", "more vendors")} {CONF(l)}</li>')
    for d in sorted(drop, key=lambda d: -int(re.sub(r'\D', '', d['share']) or 0))[:4]:
        nobs = re.sub(r'\D', '', d['share'])
        where.append(f'<li>{L(l, "Butin observé sur", "Loot observed on")} <strong>{npcname(d["npc"], l)}</strong> ({E(zname(d["zone"], l))}) — {L(l, "vu", "seen")} {nobs} {L(l, "fois", "time" if nobs == "1" else "times")} {CONF(l)}</li>')
    if len(drop) > 4: where.append(f'<li>{L(l, "et", "and")} {len(drop) - 4} {L(l, "autres créatures", "more creatures")} {CONF(l)}</li>')
    for q in m['qrew'][:2]:
        z = QE.get(q, {}).get('zone')
        where.append(f'<li>{L(l, "Récompense de la quête", "Reward of the quest")} « {E(qname(q, l))} » ({E(zname(z, l)) if z else NA(l)}) {CONF(l)}</li>' if l == 'fr' else
                     f'<li>Reward of the quest “{E(qname(q, l))}” ({E(zname(z, l)) if z else NA(l)}) {CONF(l)}</li>')
    vons = m['qvon']
    if vons: where.append(f'<li>{L(l, "Pour une quête, obtenu sur ou dans", "For a quest, obtained from")} : {E("; ".join(vons[:2]))}{" (+" + str(len(vons) - 2) + ")" if len(vons) > 2 else ""} {CONF(l)}</li>')
    has = bool(m['made_by'] or sold or drop or vons or m['qrew'])
    if not has and not gathered: where.append(f'<li>{NA(l, "non indiqué dans les données consultées", "not given in the data consulted")}</li>')
    uses = ' · '.join(f'{prof_link(PROF_BY_FR[p], l)} : {n} {L(l, "recette" if n == 1 else "recettes", "recipe" if n == 1 else "recipes")}' for p, n in m['uses'].items())
    qs = m['quests']; qtxt = NA(l, 'aucune quête trouvée', 'no quest found')
    if qs:
        names = []
        for q in qs[:3]:
            z = QE[q].get('zone'); names.append(f'{E(qname(q, l))} <span class="v41-loc">({E(zname(z, l)) if z else "—"})</span>')
        qtxt = f'{len(qs)} {CONF(l)}<ul class="v42-list">' + ''.join(f'<li>{x}</li>' for x in names) + (f'<li>{L(l, "et", "and")} {len(qs) - 3} {L(l, "autres", "more")}</li>' if len(qs) > 3 else '') + '</ul>'
    q = m['q'] if m['q'] is not None else 1
    tags = f'<li class="v41-tag is-q{q}">{QUAL.get(q, ("", ""))[0 if l == "fr" else 1]}</li>' + (f'<li class="v41-tag">{L(l, "Niveau d’objet", "Item level")} {m["ilvl"]}</li>' if m['ilvl'] else '')
    ic = ''
    if m['icon'] and (ICONS / f'icone-jeu-{m["icon"]}.webp').exists():
        used_icons.add(m['icon'])
        ic = f'<img class="v41-ic" src="{{P}}assets/icone-jeu-{m["icon"]}.webp" width="56" height="56" alt="{L(l, "Icône du jeu", "Game icon")} : {E(name)}" loading="lazy" decoding="async">'
    alt = (m['en'] if l == 'fr' else m['fr']) or ''
    altp = f'<p class="v41-alt" lang="{L(l, "en", "fr")}">{E(alt)}</p>' if alt and alt != name else ''
    html_ = (f'<article class="v41-card v42-card is-q{q}" id="mat-{i}">{ic}<div class="v41-body"><h3 class="v41-name">{E(name)}</h3>{altp}<ul class="v41-tags">{tags}</ul><dl class="v41-facts">'
             f'<div class="v42-where"><dt>{L(l, "Où le trouver", "Where to find it")}</dt><dd><ul class="v42-list">{"".join(where)}</ul></dd></div>'
             f'<div><dt>{L(l, "Utilisé par", "Used by")}</dt><dd>{uses} {GAME(l)}</dd></div>'
             f'<div class="v42-where"><dt>{L(l, "Quêtes qui le demandent", "Quests that ask for it")}</dt><dd>{qtxt}</dd></div>'
             f'<div><dt>{L(l, "Revente au marchand", "Sells to vendors for")}</dt><dd>{money(m["sell"], l) if m["sell"] else NA(l, "non vendable ou non indiqué", "cannot be sold or not given")}</dd></div>'
             f'<div><dt>{L(l, "Référence", "Reference")}</dt><dd>{L(l, "objet n°", "item #")} {i}</dd></div></dl></div></article>')
    return html_, dict(has=has, made=bool(m['made_by']), sold=bool(sold), drop=bool(drop), quest=bool(vons or m['qrew']), asked=bool(qs), named=bool(m['en']))
FAMSTATS = {}
for fam in FAMS:
    mats = sorted([m for m in M.values() if FAM_OF[m['id']] is fam], key=lambda m: (m['en'] is None, m['ilvl'] or 0, m['en'] or '', m['id']))
    groups = C.OrderedDict()
    order = {'minerais': 0, 'rares': 1, 'barres': 2, 'pierres': 3, 'autres': 4}
    for m in sorted(mats, key=lambda m: (order.get(subgroup(m, fam)[0], 5), subgroup(m, fam)[0] == 'sans-nom', subgroup(m, fam)[0])):
        groups.setdefault(subgroup(m, fam), []).append(m)
    st = C.Counter(); gl = []
    for (gid, gfr, gen), ms in groups.items():
        ref = f'mat-{fam[0]}-{gid}'
        fr = []; en = []
        for m in ms:
            h, s = card(m, fam, 'fr'); fr.append(h); en.append(card(m, fam, 'en')[0])
            for k, v in s.items(): st[k] += v
        FRAG[ref] = {'count': len(ms), 'fr': f'<div class="v41-grid">{"".join(fr)}</div>', 'en': f'<div class="v41-grid">{"".join(en)}</div>',
                     'names': {'fr': ' '.join(mname(m['id'], 'fr') for m in ms if m['en']), 'en': ' '.join(m['en'] for m in ms if m['en'])}}
        gl.append(dict(ref=ref, id=gid, fr=gfr, en=gen, n=len(ms)))
    st['n'] = len(mats)
    FAMSTATS[fam[0]] = dict(stats=dict(st), groups=gl, slug_fr=fam[1], slug_en=fam[2], fr=fam[3], en=fam[4],
                           icon=next((m['icon'] for m in mats if m['icon'] and (ICONS / f'icone-jeu-{m["icon"]}.webp').exists()), None))
# hub
def hub(l):
    li = ''
    for fam in FAMS:
        s = FAMSTATS[fam[0]]; ic = f'<img class="v41-ic" src="{{P}}assets/icone-jeu-{s["icon"]}.webp" width="56" height="56" alt="" loading="lazy" decoding="async">' if s['icon'] else ''
        li += (f'<li><a class="v41-hub-card" href="{{P}}{l}/{CAT(l)}/{fam[1] if l == "fr" else fam[2]}/">{ic}<span class="v41-hub-txt"><strong>{E(L(l, fam[3], fam[4]))}</strong>'
               f'<span>{s["stats"]["n"]} {L(l, "matériaux", "materials")} · {L(l, "au moins une source", "at least one source")} : {s["stats"]["has"]}</span></span></a></li>')
    return f'<ul class="v41-hub">{li}</ul>'
FRAG['mat-hub'] = {'count': len(FAMS), 'fr': hub('fr'), 'en': hub('en'), 'names': {'fr': ' '.join(f[3] for f in FAMS), 'en': ' '.join(f[4] for f in FAMS)}}
# ---------------- pages de recettes : matériaux + composants ----------------
RSTATS = {}
def strip_md(s): return re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)
def recipe_frag(prof, page_names, l):
    byname = C.defaultdict(list)
    for r in D.sla.values():
        if r['SkillLine'] == prof: byname[(D.sn.get(r['Spell']) or {}).get('Name_lang')].append(r['Spell'])
    rows = ''; used = C.Counter(); nrec = 0
    for nfr, nen in page_names:
        if re.search(r'campfire|feu de camp', nen + ' ' + nfr, re.I): continue  # campement non publié : aucune occurrence nouvelle
        sets = []
        for s in byname.get(strip_md(nen), []):
            rg = REAG.get(s)
            if rg and rg not in sets: sets.append(rg)
        if not sets: continue
        nrec += 1
        for i, n in sets[0]: used[i] += 1
        comp = f' <em>{L(l, "ou", "or")}</em> '.join(', '.join(f'{n}× {mat_link(i, l)}' for i, n in rg) for rg in sets)
        rows += f'<tr><th scope="row">{E(strip_md(nfr if l == "fr" else nen))}</th><td>{comp}</td></tr>'
    byfam = C.OrderedDict((f[0], []) for f in FAMS)
    for i, n in used.most_common():
        if i in M: byfam[FAM_OF[i][0]].append((i, n))
    chips = ''
    for fam in FAMS:
        xs = byfam[fam[0]]
        if not xs: continue
        lis = ''
        for i, n in sorted(xs, key=lambda x: (-x[1], mname(x[0], l))):
            ic = M[i]['icon']; img = f'<img class="v42-chip-ic" src="{{P}}assets/icone-jeu-{ic}.webp" width="28" height="28" alt="" loading="lazy" decoding="async">' if ic and (ICONS / f'icone-jeu-{ic}.webp').exists() else ''
            if img: used_icons.add(ic)
            lis += f'<li><a class="v42-chip" href="{mat_href(i, l)}">{img}<span>{E(mname(i, l))}</span><span class="v42-chip-n">{n}</span></a></li>'
        chips += f'<h3 class="v42-h3">{E(L(l, fam[3], fam[4]))} — {len(xs)}</h3><ul class="v42-chips">{lis}</ul>'
    tbl = (f'<details class="v42-vendor"><summary><strong>{L(l, "Composants de chaque recette", "Reagents of each recipe")}</strong> · {nrec} {L(l, "recettes", "recipes")}</summary>'
           f'<div class="table-wrap" tabindex="0"><table><thead><tr><th scope="col">{L(l, "Recette", "Recipe")}</th><th scope="col">{L(l, "Composants", "Reagents")}</th></tr></thead><tbody>{rows}</tbody></table></div></details>')
    return chips + tbl, nrec, len([i for i in used if i in M])
ENT = {e['id']: e for e in json.load(open(PIPE / 'runtime/entries.json'))}
for prof, key in D.PROF_KEY.items():
    e = ENT[f'forever-professions-recipes-{key}']
    names = [(r[0]['fr'], r[0]['en']) for s in e['article']['sections'] for b in s['blocks'] if b.get('type') == 'table' for r in b['rows']]
    fr, nrec, nmat = recipe_frag(prof, names, 'fr'); en, _, _ = recipe_frag(prof, names, 'en')
    FRAG[f'mat-recettes-{key}'] = {'count': nmat, 'fr': fr, 'en': en, 'names': {'fr': '', 'en': ''}}
    RSTATS[key] = dict(recipes=nrec, materials=nmat, page_recipes=len(names))
# ---------------- annuaire PNJ par zone ----------------
CLS = {'druide': ('Druide', 'Druid'), 'hexenmeister': ('Démoniste', 'Warlock'), 'jaeger': ('Chasseur', 'Hunter'), 'krieger': ('Guerrier', 'Warrior'), 'magier': ('Mage', 'Mage'),
       'paladin': ('Paladin', 'Paladin'), 'priester': ('Prêtre', 'Priest'), 'schamane': ('Chaman', 'Shaman'), 'schurke': ('Voleur', 'Rogue')}
import html as _h
CT = C.defaultdict(list); CQ = C.defaultdict(list)
for slug, (cfr, cen) in CLS.items():
    t = open(f'{D.RS}/classes/{slug}.html', errors='ignore').read(); tx = _h.unescape(re.sub(r'<[^>]+>', ' ', t)); tx = re.sub(r'\s+', ' ', tx)
    for fac, z, n, x, y in re.findall(r'(Horde|Alliance|Both factions) ([A-Z][\w\' ]+?) : ([^·]+?) ([\d.]+), ([\d.]+)', tx):
        CT[z.strip()].append(dict(cls=(cfr, cen), name=n.strip(), xy=(float(x), float(y)), fac=fac))
    i = tx.find('In the capital cities'); cap = tx[i:]
    ZN = sorted(set(MAPS) | {'Thunder Bluff', 'Orgrimmar', 'Undercity', 'Darnassus', 'Stormwind City', 'Ironforge', 'Moonglade', 'Zephras Isle'}, key=len, reverse=True)
    pieces = re.split(r'((?:' + '|'.join(map(re.escape, ZN)) + r') Quest level [\d–-]+)', cap)
    for hdr, blk in zip(pieces[1::2], pieces[2::2]):
        z = re.sub(r' Quest level.*', '', hdr)
        for n, x, y, lv, c in re.findall(r'([^·]+?) · ([\d.]+), ([\d.]+) · Quest level ([\d–-]+) · (\d+) class quests?', blk):
            n = re.sub(r'^.*\b(?:Horde|Alliance|Both factions) ', '', n.strip())
            CQ[z].append(dict(cls=(cfr, cen), name=n.strip(), xy=(float(x), float(y)), lv=lv, n=int(c)))
FACN = {'Horde': ('Horde', 'Horde'), 'Alliance': ('Alliance', 'Alliance'), 'Both factions': ('Les deux', 'Both')}
ROLE = {'q': ('donneur de quête', 'quest giver'), 'z': ('objectif de quête', 'quest objective'), 'b': ('butin indiqué', 'loot listed'), 'x': ('boss', 'boss'), 'h': ('vendeur', 'vendor'), 'l': ('formateur', 'trainer')}
XY = lambda c: f'<span class="v42-xy">{c}</span>'
def table(head, rows):
    return ('<div class="table-wrap" tabindex="0"><table><thead><tr>' + ''.join(f'<th scope="col">{h}</th>' for h in head) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
def qlist(qs, l, k=3):
    qs = sorted(qs, key=lambda q: (QE[q].get('lv') or 0, qname(q, l)))
    return ', '.join(E(qname(q, l)) for q in qs[:k]) + (f' (+{len(qs) - k})' if len(qs) > k else '')
RETAIL = re.compile(r"\bMidnight\b|Nerub-ar|Nerub’ar|Nerub'ar|Chevalier de la mort|Death Knight|[Bb]uilder de talents|[Tt]alent builder|[Cc]onstructeur de talents")
ZSTATS = {}
def zone_frag(z, l):
    st = C.Counter(); parts = []; shown = set()
    rows_raw = [r for r in RAW if D.APOS(r[3]) == z]
    npcz = [d for d in NP.values() if D.APOS(d['zone']) == z]
    places = MAPS.get(z, [])
    # 1. formateurs
    li = ''
    for t in CT.get(z, []):
        nm = npcname(t['name'], l)
        if not nm: continue
        li += f'<li><strong>{nm}</strong> — {L(l, "maître", "trainer")} {E(L(l, t["cls"][0].lower(), t["cls"][1]))} ({E(L(l, *FACN.get(t["fac"], ("", ""))))}) · {XY(f"{t[chr(120)+chr(121)][0]:g}, {t[chr(120)+chr(121)][1]:g}")}</li>'; shown.add(t['name']); st['trainers'] += 1; st['trainers_xy'] += 1
    for t in CQ.get(z, []):
        nm = npcname(t['name'], l)
        if not nm: continue
        li += f'<li><strong>{nm}</strong> — {L(l, "quêtes de classe", "class quests")} {E(L(l, t["cls"][0].lower(), t["cls"][1]))} : {t["n"]}, {L(l, "niveau", "level")} {E(t["lv"])} · {XY(f"{t[chr(120)+chr(121)][0]:g}, {t[chr(120)+chr(121)][1]:g}")}</li>'; shown.add(t['name']); st['trainers'] += 1; st['trainers_xy'] += 1
    for d in npcz:
        if not d.get('teaches') or d['name'] in shown: continue
        nm = npcname(d['name'], l)
        if not nm: continue
        tea = ', '.join(E(x['n']) for x in d['teaches'][:6]) + (f' (+{len(d["teaches"]) - 6})' if len(d['teaches']) > 6 else '')
        c = xy(d['name'], d['zone'])
        li += f'<li><strong>{nm}</strong>{" (" + L(l, "niveau", "level") + " " + E(d.get("level")) + ")" if d.get("level") else ""} — {L(l, "enseigne", "teaches")} : {tea} · {XY(c) if c else NA(l, "position non indiquée", "position not given")}</li>'
        shown.add(d['name']); st['trainers'] += 1; st['trainers_xy'] += bool(c)
    parts.append(f'<h3 class="v42-h3">{L(l, "Formateurs et maîtres de classe", "Trainers and class trainers")} — {st["trainers"]} {CONF(l)}</h3>' + (f'<ul class="v42-npcs">{li}</ul>' if li else f'<p>{NA(l, "aucun formateur relevé pour cette zone dans les données consultées", "no trainer recorded for this zone in the data consulted")}</p>'))
    # 2. vendeurs
    vh = ''
    for d in sorted(npcz, key=lambda d: d['name']):
        if not d.get('sells'): continue
        nm = npcname(d['name'], l)
        if not nm: st['excluded'] += 1; continue
        c = xy(d['name'], d['zone'])
        items = ''.join(f'<tr><th scope="row">{mat_link(s["id"], l) if s["id"] in M else E(iname(s["id"], l) or s["n"])}</th><td>{vprice(s["id"], s["price"], s["per"], l)}</td></tr>' for s in d['sells'])
        n = len(d['sells'])
        vh += (f'<details class="v42-vendor"><summary><strong>{nm}</strong>{" · " + L(l, "niveau", "level") + " " + E(d.get("level")) if d.get("level") else ""} · {n} {L(l, "objet" if n == 1 else "objets", "item" if n == 1 else "items")} · {XY(c) if c else NA(l, "position non indiquée", "position not given")}</summary>'
               + table([L(l, 'Objet', 'Item'), L(l, 'Prix', 'Price')], [items]) + '</details>')
        shown.add(d['name']); st['vendors'] += 1; st['vendor_items'] += n; st['vendors_xy'] += bool(c)
    parts.append(f'<h3 class="v42-h3">{L(l, "Vendeurs et leur stock", "Vendors and their stock")} — {st["vendors"]} {CONF(l)}</h3>' + (vh or f'<p>{NA(l, "aucun vendeur relevé pour cette zone dans les données consultées (la base consultée liste surtout des vendeurs de la Horde)", "no vendor recorded for this zone in the data consulted (the database consulted lists mostly Horde vendors)")}</p>'))
    # 3. donneurs et receveurs de quêtes
    qp = {}
    for n, d in D.QPLACE.get(z, {}).items(): qp[n] = dict(xy=d['xy'], start=set(d['start']), end=set(d['end']), fac=set())
    for p in places:
        if p['type'] in ('Quest givers', 'Quest turn-in') and p['xy']:
            d = qp.setdefault(p['name'], dict(xy=tuple(p['xy']), start=set(), end=set(), fac=set()))
            if p.get('faction'): d['fac'].add(p['faction'])
    trs = []
    for n in sorted(qp, key=lambda n: (D.NFR.get(n, n) if l == 'fr' else n)):
        d = qp[n]; nm = npcname(n, l)
        if not nm: continue
        facs = {QE[q].get('f') for q in d['start'] | d['end'] if q in QE}
        fac = ('Alliance' if facs == {'A'} else 'Horde' if facs == {'H'} else (L(l, 'les deux', 'both') if facs else (next(iter(d['fac'])) if len(d['fac']) == 1 and next(iter(d['fac'])) in ('Horde', 'Alliance') else NA(l))))
        trs.append(f'<tr><th scope="row">{nm}</th><td class="v42-xy">{d["xy"][0]:g}, {d["xy"][1]:g}</td><td>{qlist(d["start"], l) if d["start"] else "—"}</td><td>{qlist(d["end"], l) if d["end"] else "—"}</td><td>{fac}</td></tr>')
        shown.add(n); st['questnpcs'] += 1
    parts.append(f'<h3 class="v42-h3">{L(l, "Donneurs et receveurs de quêtes", "Quest givers and turn-ins")} — {st["questnpcs"]} {CONF(l)}</h3>' +
                 (table([L(l, 'PNJ', 'NPC'), L(l, 'Position (x, y)', 'Position (x, y)'), L(l, 'Donne', 'Gives'), L(l, 'Reçoit', 'Takes'), L(l, 'Faction', 'Faction')], trs) if trs else f'<p>{NA(l, "aucune position de donneur de quête dans les données consultées", "no quest giver position in the data consulted")}</p>'))
    # 4. objets de quête
    qi = {}
    for k, q in QE.items():
        if D.APOS(q.get('zone')) != z: continue
        qf = QF.get(k, {})
        for j, b in enumerate(q.get('brauche', [])):
            if 'id' not in b: continue
            von = b.get('von'); vfr = None
            fb = (qf.get('brauche') or [])
            if l == 'fr' and j < len(fb) and fb[j].get('id') == b['id']: vfr = fb[j].get('von')
            v = (vfr or von) if l == 'fr' else von
            key = (b['id'], k)
            qi[key] = (iname(b['id'], l) or (fb[j].get('n') if l == 'fr' and j < len(fb) else None) or b['n'], b.get('q') or 1, k, v)
    rows = []
    for (iid, k), (nm, n, q, v) in sorted(qi.items(), key=lambda x: (x[1][0], qname(x[1][2], l))):
        if RETAIL.search(' '.join(str(x) for x in (nm, iname(iid, 'en'), qname(q, 'en'), QE[q].get('n'), v))): st['retail_skipped'] += 1; continue  # garde « hors périmètre retail » du pipeline
        st['qitems'] += 1; st['qitems_src'] += bool(v)
        nm_h = mat_link(iid, l) if iid in M else (E(nm) + (GER(l) if not iname(iid, l) and odd(nm) == 'german' else ''))
        v_h = (E(v) + (GER(l) if odd(v) == 'german' else '')) if v else NA(l)
        rows.append(f'<tr><th scope="row">{nm_h}{" ×" + str(n) if n > 1 else ""}</th><td>{E(qname(q, l))}</td><td>{v_h}</td></tr>')
    parts.append(f'<h3 class="v42-h3">{L(l, "Objets de quête : où les obtenir", "Quest items: where to get them")} — {st["qitems"]} {CONF(l)}</h3>' +
                 (table([L(l, 'Objet', 'Item'), L(l, 'Quête', 'Quest'), L(l, 'Obtenu sur ou dans', 'Obtained from')], rows) if rows else f'<p>{NA(l, "aucun objet de quête rattaché à cette zone dans les données consultées", "no quest item attached to this zone in the data consulted")}</p>'))
    objs = [p for p in places if p['type'] == 'Quest object' and p['xy']]
    if objs:
        li = ''.join(f'<li><strong>{E(p["name"])}</strong> · {XY(f"{p[chr(120)+chr(121)][0]:g}, {p[chr(120)+chr(121)][1]:g}")}</li>' for p in sorted(objs, key=lambda p: p['name']))
        st['qobjects'] = len(objs)
        parts.append(f'<h3 class="v42-h3">{L(l, "Objets du décor liés à une quête", "World objects tied to a quest")} — {len(objs)} {CONF(l)}</h3><ul class="v42-npcs">{li}</ul>')
    # 5. autres PNJ de la liste (objectifs, boss, butin) — rien n’est perdu de l’ancien tableau
    rows = []
    for r in sorted(rows_raw, key=lambda r: r[1]):
        if r[1] in shown: continue
        nm = npcname(r[1], l)
        if not nm: st['excluded'] += 1; continue
        d = next((d for d in npcz if d['name'] == r[1]), None)
        loot = []
        if d:
            for x in sorted(d.get('loot', []), key=lambda x: -int(re.sub(r'\D', '', x['share']) or 0)):
                if x.get('id') and (iname(x['id'], l)):
                    loot.append(mat_link(x['id'], l) if x['id'] in M else E(iname(x['id'], l)))
                if len(loot) == 3: break
        c = xy(r[1], z)
        roles = ', '.join(L(l, *ROLE[ch]) for ch in r[5] if ch in ROLE) or NA(l)
        rows.append(f'<tr><th scope="row">{nm}</th><td>{E(r[4]) if r[4] else "—"}</td><td>{roles}</td><td>{XY(c) if c else NA(l)}</td><td>{", ".join(loot) if loot else "—"}</td></tr>')
        st['others'] += 1
    if rows:
        parts.append(f'<details class="v42-vendor"><summary><strong>{L(l, "Autres PNJ de la liste", "Other NPCs in the list")}</strong> · {st["others"]} ({L(l, "objectifs de quête, boss, butin", "quest objectives, bosses, loot")}) {CONF(l)}</summary>'
                     + table([L(l, 'Nom', 'Name'), L(l, 'Niveau', 'Level'), L(l, 'Rôle', 'Role'), L(l, 'Position', 'Position'), L(l, 'Butin observé', 'Observed loot')], rows) + '</details>')
    st['npcs_list'] = len(rows_raw)
    st['german'] = sum(1 for r in rows_raw if odd(r[1]) == 'german')
    return ''.join(parts), st, sorted({n for n in shown} | {r[1] for r in rows_raw if odd(r[1]) != 'exclude'})
ZONES = [e for e in ENT.values() if e['category'] == 'zones' and any((s.get('key') or '').startswith('client-npc-liste') for s in e['sources'])]
for e in ZONES:
    z = D.APOS(e['title']['en'])
    if e['id'] == 'forever-zones-directory': continue
    fr, st, names = zone_frag(z, 'fr'); en, _, _ = zone_frag(z, 'en')
    if st['npcs_list'] == 0 and st['questnpcs'] == 0 and st['trainers'] == 0: ZSTATS[e['id']] = dict(st, empty=True); continue
    ref = 'pnj-' + e['id'].replace('forever-zone-', '')
    FRAG[ref] = {'count': st['npcs_list'], 'fr': fr, 'en': en, 'names': {'fr': ' '.join(D.NFR.get(n, n) for n in names), 'en': ' '.join(names)}}
    ZSTATS[e['id']] = dict(st, ref=ref, zone=z)

# ---------------- Collections (v41) : 4 cors de loup vendus par un PNJ (à confirmer) ----------------
V41_ORIG = OUT / 'collections-v41.orig.json'
if not V41_ORIG.exists(): shutil.copy(PIPE / 'data/collections-v41.json', V41_ORIG)
F41 = json.load(open(V41_ORIG))
WOLF = [1041, 5668, 5665, 1132]
og = next(d for d in NP.values() if d['name'] == 'Ogunaro Wolfrunner'); ogxy = xy(og['name'], og['zone'])
assert all(any(s['id'] == w for s in og['sells']) for w in WOLF)
src = F41['montures-ni-horde-40']; cards = {'fr': [], 'en': []}
for l in ('fr', 'en'):
    h = src[l]
    for w in WOLF:
        m_ = re.search(r'<article class="v41-card[^"]*" id="m-' + str(w) + r'">.*?</article>', h, re.S); assert m_, w
        c = m_.group(0); h = h.replace(c, '', 1)
        old = re.search(r'<div><dt>(Obtention|How to get it)</dt>.*?<div><dt>(PNJ|NPC)</dt><dd>.*?</dd></div>', c, re.S); assert old, w
        new = (f'<div><dt>{L(l, "Obtention", "How to get it")}</dt><dd>{L(l, "Vendue par un PNJ", "Sold by an NPC")} {CONF(l)}</dd></div>'
               f'<div><dt>Zone</dt><dd>{E(zname("Orgrimmar", l))}</dd></div>'
               f'<div><dt>{L(l, "PNJ", "NPC")}</dt><dd>{npcname(og["name"], l)} <span class="v41-loc">({ogxy})</span></dd></div>')
        c = c.replace(old.group(0), new)
        c = c.replace('</dl>', '</dl>', 1).replace('<span class="v41-st is-game">', f'<span class="v41-st is-pending">{L(l, "Vendeur d’après une base non officielle — à confirmer", "Vendor from an unofficial database — to be confirmed")}</span><span class="v41-st is-game">', 1)
        cards[l].append(c)
    src[l] = h
assert src['count'] == 21; src['count'] = 17
wolf_names = {l: [re.search(r'<h3 class="v41-name">([^<]*)</h3>', c).group(1) for c in cards[l]] for l in ('fr', 'en')}
for l in ('fr', 'en'):
    for n_ in wolf_names[l]:
        assert _h.unescape(n_) in src['names'][l], n_
        src['names'][l] = re.sub(r'\s+', ' ', src['names'][l].replace(_h.unescape(n_), '', 1)).strip()
FRAG['montures-vendeur'] = {'count': 4, 'fr': '<div class="v41-grid">' + ''.join(cards['fr']) + '</div>', 'en': '<div class="v41-grid">' + ''.join(cards['en']) + '</div>',
                            'names': {l: ' '.join(_h.unescape(n_) for n_ in wolf_names[l]) for l in ('fr', 'en')}}
for l, a_, b_ in (('fr', 'obtention connue : 28', 'obtention connue : 32'), ('en', 'known acquisition : 28', 'known acquisition : 32')):
    if a_ in F41['hub'][l]: F41['hub'][l] = F41['hub'][l].replace(a_, b_, 1)
    else: raise SystemExit(f'hub text not found: {l} {a_!r} in {F41["hub"][l][:400]}')
(PIPE / 'data/collections-v41.json').write_text(json.dumps(F41, ensure_ascii=False))
for k, v in FRAG.items():
    assert re.fullmatch(r'[a-z0-9-]+', k), k
    for l in ('fr', 'en'):
        assert '<script' not in v[l] and 'style=' not in v[l], k
(PIPE / 'data/collections-v42.json').write_text(json.dumps(FRAG, ensure_ascii=False))
dst = PIPE / 'public/v2/assets'; n = 0
for ic in sorted(used_icons):
    p = dst / f'icone-jeu-{ic}.webp'
    if not p.exists(): shutil.copy(ICONS / f'icone-jeu-{ic}.webp', p); n += 1
(OUT / 'counts42.json').write_text(json.dumps(dict(fam=FAMSTATS, recipes=RSTATS, zones=ZSTATS, icons=len(used_icons), icons_new=n), ensure_ascii=False, indent=1, default=list))
print('fragments', len(FRAG), 'icons used', len(used_icons), 'new', n)
for f, s in FAMSTATS.items(): print(f, s['stats'])
print({k: v for k, v in RSTATS.items()})
