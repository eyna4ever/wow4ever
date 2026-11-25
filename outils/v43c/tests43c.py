#!/usr/bin/env python3
"""v43c : tests et empreinte de l'arbre v43c-test/tree (477 pages : +2 article Blackmaw ; titre correctifs « du 5 au 20 novembre »)."""
import hashlib, json, re
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); T = R / 'v43c-test/tree'; W = T / 'wiki'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
import shutil
for f in ('tests/test_community.py', 'tests/wiki-baseline.json'): shutil.copy2(R / 'v43b-test/tree' / f, T / f)  # idempotent : repart des tests v43b
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
assert b['tarball_sha256'] == 'c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517'
b['source'] = ('v43c (2026-11-24) : article « Correctifs Forever » FR/EN mis à jour avec les lots officiels des 17, 19 et 20 novembre (titre « du 5 au 20 novembre » '
               'repris dans les liens, accueils et index de recherche), nouvel article Blackmaw Hold (« Repaire des Noiregueules ») FR/EN, épisode 8 du podcast officiel. '
               '477 pages, 221 fiches. Base v43b en ligne. Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
t = (T / 'tests/test_community.py').read_text()
def sub(pat, rep, n_exp):
    global t; t, n = re.subn(pat, rep, t); assert n == n_exp, (pat, n)
sub(r"self\.assertEqual\(baseline\['tarball_sha256'\],'[0-9a-f]{64}'\)", f"self.assertEqual(baseline['tarball_sha256'],'{fp}')  # v43c (2026-11-24) ; v43b = c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517", 1)
sub(r"(self\.assertEqual\(sum\(1 for f in files if f\.endswith\('\.html'\)\),)475\)", r"\g<1>477)  # v43c: +2 article Blackmaw FR+EN", 1)
sub(r"self\.assertEqual\(len\(pages\),475\)", "self.assertEqual(len(pages),477)  # v43c: +2 article Blackmaw FR+EN", 2)
sub(r"self\.assertEqual\(len\(ids\),220\)", "self.assertEqual(len(ids),221)  # v43c: +1 article Blackmaw ;", 1)
sub(r"self\.assertEqual\(len\(set\(current\)-set\(reference\['pages'\]\)\),334\)", "self.assertEqual(len(set(current)-set(reference['pages'])),336)  # v43c: +2 article Blackmaw FR+EN ;", 1)
# v40b : le titre suit désormais les lots jusqu'au 20 novembre ; les sources 17 à 23 sont ajoutées par la v43c
sub(r"self\.assertIn\('Correctifs Forever du 5 au 16 novembre', hot\)", "self.assertIn('Correctifs Forever du 5 au 20 novembre', hot)  # v43c: titre étendu (lots des 17, 19, 20 novembre)", 1)
sub(r"self\.assertIn\('Forever hotfixes, November 5–16', en_hot\)", "self.assertIn('Forever hotfixes, November 5–20', en_hot)", 1)
sub(r"self\.assertNotIn\('id=\"source-17\"', page\)", "self.assertNotIn('id=\"source-24\"', page)  # v43c: sources 17 à 23", 1)
sub(r"\(\('fr', 'Correctifs Forever du 5 au 16 novembre'\), \('en', 'Forever hotfixes, November 5–16'\)\)", "(('fr', 'Correctifs Forever du 5 au 20 novembre'), ('en', 'Forever hotfixes, November 5–20'))", 1)
a = "    def test_shared_header(self):\n"; assert t.count(a) == 1
t = t.replace(a, '''    def test_v43c_hotfixes_blackmaw_podcast(self):
        # v43c (2026-11-24): « Correctifs Forever » gains the official hotfix batches of November 17, 19 and 20 (news.blizzard 24315281,
        # Kaivax US 2403040 #12-#14 / EU 639885 #11-#13); new Blackmaw Hold article FR/EN; official podcast episode 8 (24317086).
        text=lambda page:(WIKI_ROOT/page).read_text()
        hot=text('fr/actualites/correctifs-forever-5-et-6-novembre/index.html')
        en_hot=text('en/news/forever-hotfixes-november-5-6/index.html')
        for page in (hot, en_hot):
            for d in ('nov17','nov19','nov20'):
                self.assertIn(f'id="details-{d}"', page); self.assertIn(f'href="#details-{d}"', page)
            for u in ('us.forums.blizzard.com/en/wow/t/2403040/12','us.forums.blizzard.com/en/wow/t/2403040/13','us.forums.blizzard.com/en/wow/t/2403040/14',
                      'eu.forums.blizzard.com/en/wow/t/639885/11','eu.forums.blizzard.com/en/wow/t/639885/12','eu.forums.blizzard.com/en/wow/t/639885/13'):
                self.assertIn('https://'+u+'"', page)
            self.assertIn('id="source-23"', page); self.assertNotIn('id="source-24"', page)
            self.assertNotRegex(page, r'(?i)streamer')
        stale=[str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*.html') if 'du 5 au 16 novembre' in p.read_text() or 'November 5–16' in p.read_text()]
        self.assertEqual(stale, [])
        bm=text('fr/actualites/sanctions-abus-blackmaw-hold/index.html'); en_bm=text('en/news/blackmaw-hold-abuse-actions/index.html')
        self.assertIn('Repaire des Noiregueules', bm); self.assertIn('Blackmaw Hold', en_bm)
        for page in (bm, en_bm):
            self.assertIn('<meta name="robots" content="noindex,nofollow">', page)
            self.assertIn('https://us.forums.blizzard.com/en/wow/t/2419757"', page); self.assertIn('https://eu.forums.blizzard.com/en/wow/t/643759"', page)
            self.assertNotIn('[src:', page)
        for page in (text('fr/actualites/le-podcast-officiel-wow-forever/index.html'), text('en/news/the-official-wow-forever-podcast/index.html')):
            self.assertIn('https://news.blizzard.com/en-us/article/24317086"', page); self.assertIn('id="source-8"', page)
        self.assertIn('fr/actualites/sanctions-abus-blackmaw-hold/', text('fr/index.html'))
        self.assertIn('en/news/blackmaw-hold-abuse-actions/', text('en/index.html'))
        for lang, page in (('fr','fr/actualites/sanctions-abus-blackmaw-hold/'),('en','en/news/blackmaw-hold-abuse-actions/')):
            d=json.loads((WIKI_ROOT/f'search-detail-{lang}.json').read_text())
            self.assertEqual(len(d['pages']),221); self.assertIn(page,[p[0] for p in d['pages']])
            self.assertIn(page,(WIKI_ROOT/'search-index.json').read_text())

''' + a)
(T / 'tests/test_community.py').write_text(t)
print(json.dumps({'fingerprint': fp, 'wiki_files': len(files), 'html': sum(1 for k in files if k.endswith('.html'))}))
