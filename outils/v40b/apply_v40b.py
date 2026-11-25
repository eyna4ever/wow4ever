#!/usr/bin/env python3
"""v40b (Oui de Mathieu t404u, 17/11/2026) : mise à jour de l'article « Correctifs Forever » (FR + EN)
avec le lot officiel de correctifs du 16 novembre 2026 (page Blizzard 24315281, relais Kaivax US/EU).
Usage : python3 apply_v40b.py <racine contenant wiki/>   (idempotence : refuse un arbre déjà traité)
Applicable tel quel sur l'arbre v41 (mêmes chaînes d'origine) : aucune autre page n'est réécrite
que par remplacement exact du titre de l'article et de la date de mise à jour attenante."""
import json, re, sys
from pathlib import Path

W = Path(sys.argv[1]) / 'wiki'
FR = W / 'fr/actualites/correctifs-forever-5-et-6-novembre/index.html'
EN = W / 'en/news/forever-hotfixes-november-5-6/index.html'
OLD_T = {'fr': 'Correctifs Forever du 5 au 14 novembre : XP en donjon, classes, objets et quêtes',
         'en': 'Forever hotfixes, November 5–14: dungeon XP, classes, items and quests'}
NEW_T = {'fr': 'Correctifs Forever du 5 au 16 novembre : XP en donjon, classes, objets et quêtes',
         'en': 'Forever hotfixes, November 5–16: dungeon XP, classes, items and quests'}
URLS = {'fr': 'fr/actualites/correctifs-forever-5-et-6-novembre/', 'en': 'en/news/forever-hotfixes-november-5-6/'}

def cite(*n): return ''.join(f'<sup class="cite"><a href="#source-{i}" aria-label="Source {i}">[{i}]</a></sup>' for i in n)
def once(t, old, new, what):
    c = t.count(old); assert c == 1, (what, c); return t.replace(old, new)

SEC = {
 'fr': ('16 novembre 2026', [
   'Lot publié sur la page officielle, désormais titrée « WoW: Forever Hotfixes - November 16, 2026 », et relayé par Kaivax sur les forums officiels US et EU le 17 novembre à 03:17 heure de Paris. Les noms de sorts, PNJ, objets et quêtes sont repris en anglais.' + cite(14, 15, 16)], [
   'Camping : le Fishing Rack fournit désormais des appâts à tout le monde ; les Bloated Fish pêchés grâce à lui tombent plus souvent et leur butin est ajusté.',
   'Druide : les rangs de Wild Growth repartent bien en temps de recharge ; Équilibre : le talent Genesis augmente bien les dégâts du saignement de Pounce.',
   'Prêtre : Dark Inspiration ne se cumule plus avec plusieurs prêtres Ombre dans le groupe. Avec la maintenance hebdomadaire, les soins de Vampiric Embrace passent de 20 % à 10 % des dégâts d’Ombre du prêtre, qui reçoit en échange 100 % de soins en plus de cet effet ; Blizzard précise que rien ne change en solo.',
   'Voleur : les rangs de poison ne dépassent plus le rang maximum ; Shank ne retire plus à tort les points de combo posés sur d’autres cibles.',
   'Chaman : plusieurs corrections de Windfury Totem (armure ignorée et absence de temps de recharge interne, rage non générée, déclenchements en trop) ; Amélioration : Maelstrom Weapon ne profite plus à deux sorts, Thundering Strikes n’exige plus d’arme équipée.',
   'Guerrier : le Revered Champion propose de nouveau Legacy of Valor aux guerriers éligibles ; Fureur : Cleave et Heroic Strike déclenchent bien Unbridled Wrath et Reckless Swings et ne consomment plus Flurry.',
   'Donjons : dans The Drowned City, Captain Dreadrise n’est plus insensible aux étourdissements, son Abyssal Bubble ne bloque/esquive/pare plus et le rare « Pyromancer » Braxton réagit au combat ; Temple englouti : correction des statues de serpent d’Atal’alarion activées dans le mauvais ordre.',
   'Objets : Formula: Enchant Boots - Speed (réputation) devient liée quand ramassée ; Outrider’s Gloves fonctionnent ; la Violet Tragan ne brise plus les contrôles.',
   'JcJ : mourir dans la mine d’or du Bassin Arathi ne renvoie plus vers un cimetière des Riverglades.',
   'Quêtes : « Blood Red Bandanas » tombent plus souvent ; corrections pour « The Talisman of Kazdor », « No Soldier Left Behind » (crédit pour tout le groupe), « Screecher Spirits » (Vale Screamers déplacés sur la côte de l’Île de Dread) et « The Return of the King? » (Theramore) ; « Water Pouch Bounty » ne donne plus d’XP.',
   'Conséquences pour les joueurs : les prêtres Ombre en groupe soignent moins leurs alliés via Vampiric Embrace mais se soignent davantage eux-mêmes ; les groupes chaman/guerrier perdent les attaques Windfury qui ignoraient l’armure.']),
 'en': ('November 16, 2026', [
   'Batch published on the official page, now titled “WoW: Forever Hotfixes - November 16, 2026”, and relayed by Kaivax on the official US and EU forums on November 17 at 03:17 Paris time.' + cite(14, 15, 16)], [
   'Camping: the Fishing Rack now gives lures to everyone; Bloated Fish caught through it drop more often and have adjusted loot.',
   'Druid: Wild Growth ranks now correctly go on cooldown; Balance: Genesis now increases Pounce’s bleed damage.',
   'Priest: Dark Inspiration no longer stacks with several Shadow priests in the party. With weekly maintenance, Vampiric Embrace healing drops from 20% to 10% of the priest’s Shadow damage, and the priest receives 100% more healing from the effect; Blizzard says solo play is unchanged.',
   'Rogue: poison ranks can no longer exceed the maximum rank; Shank no longer wrongly removes combo points held on other targets.',
   'Shaman: several Windfury Totem fixes (ignored armor and no internal cooldown, no Rage generated, extra procs); Enhancement: Maelstrom Weapon no longer benefits two casts, Thundering Strikes no longer needs a weapon equipped.',
   'Warrior: the Revered Champion offers Legacy of Valor to eligible warriors again; Fury: Cleave and Heroic Strike now trigger Unbridled Wrath and Reckless Swings and no longer consume Flurry.',
   'Dungeons: in The Drowned City, Captain Dreadrise is no longer stun-immune, his Abyssal Bubble can no longer block/dodge/parry and the rare “Pyromancer” Braxton now reacts to combat; Sunken Temple: fix for Atal’alarion serpent statues activated in the wrong order.',
   'Items: Formula: Enchant Boots - Speed (reputation) is now bind-on-pickup; Outrider’s Gloves work; the Violet Tragan no longer breaks crowd control.',
   'PvP: dying in the Arathi Basin Gold Mine no longer sends you to a Riverglades graveyard.',
   'Quests: “Blood Red Bandanas” drop more often; fixes for “The Talisman of Kazdor”, “No Soldier Left Behind” (credit for the whole party), “Screecher Spirits” (Vale Screamers moved to the Isle of Dread coast) and “The Return of the King?” (Theramore); “Water Pouch Bounty” no longer grants XP.',
   'Consequences for players: Shadow priests in groups heal allies less through Vampiric Embrace but heal themselves more; shaman/warrior groups lose the Windfury attacks that ignored armor.']),
}
KEY = {'fr': '16 novembre : correctifs de classes (dont Windfury Totem), de donjons, d’objets, de JcJ et de quêtes ; avec la maintenance hebdomadaire, les soins de Vampiric Embrace passent de 20 % à 10 % des dégâts d’Ombre du prêtre, sans changement en solo selon Blizzard.',
       'en': 'November 16: class (including Windfury Totem), dungeon, item, PvP and quest fixes; with weekly maintenance, Vampiric Embrace healing drops from 20% to 10% of the priest’s Shadow damage, with no change to solo play according to Blizzard.'}
INTRO = {'fr': ('désormais titrée « WoW: Forever Hotfixes - November 13, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11 et 13 novembre.',
                'désormais titrée « WoW: Forever Hotfixes - November 16, 2026 ». Elle couvre les lots des 5, 6, 8, 9, 10, 11, 13 et 16 novembre.'),
         'en': ('now titled “WoW: Forever Hotfixes - November 13, 2026”. It covers the November 5, 6, 8, 9, 10, 11 and 13 batches.',
                'now titled “WoW: Forever Hotfixes - November 16, 2026”. It covers the November 5, 6, 8, 9, 10, 11, 13 and 16 batches.')}
ANAL = {'fr': ' Ce lot ressemble surtout à un nettoyage de bugs de talents et de quêtes ; le seul vrai réglage d’équilibre vise le prêtre Ombre en groupe, sans toucher au jeu en solo.',
        'en': ' This batch mostly cleans up talent and quest bugs; the only real balance change targets the Shadow priest in groups, leaving solo play untouched.'}
TL = {'fr': '<li><time datetime="2026-11-16">16 novembre 2026</time><span>Lot du 16 novembre (camping, classes, donjons, objets, JcJ, quêtes), publié le 17 novembre à 03:17 heure de Paris ; le changement de Vampiric Embrace accompagne la maintenance hebdomadaire.' + cite(14, 15, 16) + '</span></li>',
      'en': '<li><time datetime="2026-11-16">16 November 2026</time><span>November 16 batch (camping, classes, dungeons, items, PvP, quests), published on November 17 at 03:17 Paris time; the Vampiric Embrace change comes with weekly maintenance.' + cite(14, 15, 16) + '</span></li>'}
SRC = [('https://news.blizzard.com/en-us/article/24315281', {'fr': 'WoW: Forever Hotfixes - November 16, 2026', 'en': 'WoW: Forever Hotfixes - November 16, 2026'}),
       ('https://us.forums.blizzard.com/en/wow/t/2403040/11', {'fr': 'WoW: Forever Hotfixes - November 16, 2026 (Kaivax, forum officiel US, message 11)', 'en': 'WoW: Forever Hotfixes - November 16, 2026 (Kaivax, official US forum, post 11)'}),
       ('https://eu.forums.blizzard.com/en/wow/t/639885/10', {'fr': 'WoW: Forever Hotfixes - November 16, 2026 (Kaivax, forum officiel EU, message 10)', 'en': 'WoW: Forever Hotfixes - November 16, 2026 (Kaivax, official EU forum, post 10)'})]
D17 = {'fr': '<time datetime="2026-11-17">17 novembre 2026</time>', 'en': '<time datetime="2026-11-17">17 November 2026</time>'}
D15 = {'fr': '<time datetime="2026-11-15">15 novembre 2026</time>', 'en': '<time datetime="2026-11-15">15 November 2026</time>'}

def words(t):
    a = t[t.find('<article'):t.find('</article>')]
    return len(re.sub(r'<[^>]+>', ' ', a).split())

def article(path, L):
    t = path.read_text('utf-8')
    assert 'id="details-nov16"' not in t, 'déjà appliqué'
    w0 = words(t)
    title, paras, items = SEC[L]
    sec = (f'<section class="article-section" id="details-nov16" aria-labelledby="details-nov16-title"><h2 id="details-nov16-title">{title}</h2>'
           + ''.join(f'<p>{p}</p>' for p in paras) + '<ul>' + ''.join(f'<li>{i}{cite(14)}</li>' for i in items) + '</ul></section>')
    t = once(t, '<section class="article-section" id="details-nov14"', sec + '<section class="article-section" id="details-nov14"', 'section')
    t = once(t, '<li><a href="#details-nov14"><span>', f'<li><a href="#details-nov16"><span>{title}</span></a></li><li><a href="#details-nov14"><span>', 'toc')
    assert len(re.findall(r'<li><a href="#details-nov14">(?!<span>)', t)) == 1, 'tabs'
    t = re.sub(r'<li><a href="#details-nov14">(?!<span>)', f'<li><a href="#details-nov16">{title}</a></li><li><a href="#details-nov14">', t)
    t = once(t, '<ul class="key-points"><li>', f'<ul class="key-points"><li>{KEY[L]}{cite(14)}</li><li>', 'keypoint')
    o, n = INTRO[L]; t = once(t, o, n, 'intro')
    i = t.find('id="introduction-title"'); j = t.find('</p></section>', i); assert 0 < i < j
    t = t[:j] + cite(14) + t[j:]
    k = t.find('<p class="v16-analysis-note">'); assert k > 0 and t[k-4:k] == '</p>'
    t = t[:k-4] + ANAL[L] + t[k-4:]
    t = once(t, '</ol><div class="status-columns">', TL[L] + '</ol><div class="status-columns">', 'timeline')
    pub, acc = ('publié le', 'consulté le') if L == 'fr' else ('published', 'accessed')
    lis = ''.join(f'<li id="source-{14+i}"><span class="source-number">[{14+i}]</span> <span class="source-lines"><a href="{u}" rel="noopener noreferrer" hreflang="en">{tt[L]}</a> <span class="source-lang">(EN)</span> · {pub} {D17[L]} · {acc} {D17[L]}</span></li>' for i, (u, tt) in enumerate(SRC))
    assert 'id="source-14"' not in t and 'id="source-13"' in t
    t = once(t, '</li></ol><p class="rights-note">', '</li>' + lis + '</ol><p class="rights-note">', 'sources')
    if L == 'fr':
        t = once(t, '<dt>Mis à jour</dt><dd>' + D15[L], '<dt>Mis à jour</dt><dd>' + D17[L], 'maj')
        t = once(t, '<dt>Date de l’événement</dt><dd><time datetime="2026-11-11">11 novembre 2026</time>', '<dt>Date de l’événement</dt><dd><time datetime="2026-11-16">16 novembre 2026</time>', 'event')
        t = once(t, '13 sources officielles', '16 sources officielles', 'nsrc')
        t = once(t, ' · révision 20</p>', ' · révision 21</p>', 'rev')
    else:
        t = once(t, '<dt>Updated</dt><dd>' + D15[L], '<dt>Updated</dt><dd>' + D17[L], 'maj')
        t = once(t, '<dt>Event date</dt><dd><time datetime="2026-11-11">11 November 2026</time>', '<dt>Event date</dt><dd><time datetime="2026-11-16">16 November 2026</time>', 'event')
        t = once(t, '13 official sources', '16 official sources', 'nsrc')
        t = once(t, ' · revision 20</p>', ' · revision 21</p>', 'rev')
    t = t.replace('état documentaire 2026-11-14', 'état documentaire 2026-11-17')
    lab = '<dt>Lecture</dt><dd>' if L == 'fr' else '<dt>Reading time</dt><dd>'
    m = re.search(re.escape(lab) + r'(\d+) min</dd>', t); assert m
    newmin = round(int(m.group(1)) * words(t) / w0)
    t = t.replace(m.group(0), f'{lab}{newmin} min</dd>')
    path.write_text(t, 'utf-8')
    return newmin

changed = set()
mins = {L: article(p, L) for p, L in ((FR, 'fr'), (EN, 'en'))}
changed |= {FR, EN}
# titre : remplacement exact partout (pages HTML)
for f in sorted(W.rglob('*.html')):
    t = f.read_text('utf-8'); n = t
    for L in ('fr', 'en'):
        n = n.replace(OLD_T[L], NEW_T[L])
    # date « mis à jour » attenante au lien de l'article (accueils, listes)
    for L in ('fr', 'en'):
        n = re.sub(r'(<a [^>]*href="[^"]*' + re.escape(URLS[L]) + r'"[^>]*>(?:(?!</a>).)*?' + re.escape(NEW_T[L]) + r'(?:(?!</a>).)*?)' + re.escape(D15[L]), lambda m: m.group(1) + D17[L], n, flags=re.S)
    if n != t:
        f.write_text(n, 'utf-8'); changed.add(f)
# vignettes « lecture / sources » attenantes (page d'accueil racine, en-têtes des rubriques Actualités / News)
def lead_fix(f, pairs):
    t = f.read_text('utf-8'); n = t
    for o, nw in pairs: n = once(n, o, nw, f.name)
    f.write_text(n, 'utf-8'); changed.add(f)
for L, f, unit in (('fr', W / 'fr/actualites/index.html', 'sources'), ('en', W / 'en/news/index.html', 'sources')):
    t = f.read_text('utf-8'); i = t.find('v2-lead-title">' + NEW_T[L]); assert i > 0
    j = t.find('</ul>', i); blk = t[i:j]
    old_min = {'fr': 14, 'en': 11}[L]
    assert f'<span>{old_min} min</span>' in blk and '<span>13 sources</span>' in blk, L
    blk2 = blk.replace(f'<span>{old_min} min</span>', f'<span>{mins[L]} min</span>').replace('<span>13 sources</span>', '<span>16 sources</span>')
    f.write_text(t[:i] + blk2 + t[j:], 'utf-8'); changed.add(f)
lead_fix(W / 'index.html', [('Article · 14 min · ' + D17['fr'], f'Article · {mins["fr"]} min · ' + D17['fr'])])
# index de recherche
si = W / 'search-index.json'; raw = si.read_text('utf-8'); d = json.loads(raw)
e = next(x for x in d['entries'] if x['id'] == 'forever-news-hotfixes-nov5-6')
assert e['title'] == OLD_T
e['title'] = dict(NEW_T)
for L in ('fr', 'en'):
    if isinstance(e.get('searchText'), dict):
        e['searchText'][L] = e['searchText'][L].replace(OLD_T[L].lower(), NEW_T[L].lower())
e['searchText']['fr'] += ' 16 novembre fishing rack vampiric embrace windfury totem dark inspiration drowned city temple englouti bassin arathi'
e['searchText']['en'] += ' november 16 fishing rack vampiric embrace windfury totem dark inspiration drowned city sunken temple arathi basin'
lic = e['sources'][-1]['license']
for u, _ in SRC: e['sources'].append({'url': u, 'license': lic, 'accessedAt': '2026-11-17'})
compact = not raw.lstrip().startswith('{\n')
si.write_text(json.dumps(d, ensure_ascii=False, separators=(',', ':')) if compact else json.dumps(d, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''), 'utf-8')
changed.add(si)
print('lecture', mins)
for f in sorted(changed): print(f.relative_to(W.parent))
print(len(changed), 'fichiers')
