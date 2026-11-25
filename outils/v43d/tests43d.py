#!/usr/bin/env python3
"""v43d : met à jour tests et empreinte de l'arbre v43d-test/tree (déjà copié de la v43c)."""
import hashlib, json, re
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); T = R / 'v43d-test/tree'; W = T / 'wiki'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
import shutil
for f in ('tests/test_community.py', 'tests/wiki-baseline.json'): shutil.copy2(R / 'v43c-test/tree' / f, T / f)  # idempotent : repart des tests v43c
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
assert b['tarball_sha256'] == 'b2f35655cad35ec602dfa214b9a67a2219ae4f29ec77ec9921494e9c0bf50bc8'
b['source'] = ('v43d (2026-11-25) : article « Correctifs Forever » FR/EN mis à jour avec le lot officiel du 23 novembre et un encadré « problèmes en cours » '
               '(lockboxes, compétence de monte épique) ; titre « du 5 au 23 novembre » ; description couvrant toute la série ; lien de l’article Blackmaw vers la fiche du donjon. '
               'Inclut la v43c (non déployée) : lots des 17, 19 et 20 novembre, article Blackmaw Hold FR/EN, podcast épisode 8. 477 pages, 221 fiches. Base v43b en ligne. Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
t = (T / 'tests/test_community.py').read_text()
def sub(pat, rep, n_exp):
    global t; t, n = re.subn(pat, rep, t); assert n == n_exp, (pat, n)
sub(r"self\.assertEqual\(baseline\['tarball_sha256'\],'[0-9a-f]{64}'\)", f"self.assertEqual(baseline['tarball_sha256'],'{fp}')  # v43d (2026-11-25) ; v43b = c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517", 1)
# titres 20 → 23 (tests v40b et v43c)
sub(r"Correctifs Forever du 5 au 20 novembre", "Correctifs Forever du 5 au 23 novembre", 2)
sub(r"Forever hotfixes, November 5–20", "Forever hotfixes, November 5–23", 2)
sub(r"self\.assertNotIn\('id=\"source-24\"', page\)  # v43c: sources 17 à 23", "self.assertNotIn('id=\"source-31\"', page)  # v43d: sources 17 à 30", 1)
sub(r"self\.assertNotRegex\(page, r'\(\?i\)exploit\|streamer'\)",
    "self.assertNotRegex(re.sub(r'<ol class=\"source-list\">.*?</ol>', '', page, flags=re.S), r'(?i)exploit|streamer')  # v43d: titre officiel du fil Kaivax « Lockbox exploit… » cité en source", 1)
# le test v43c refuse encore source-24 et l'ancien titre 5–16 ; on l'étend
old = """        for page in (hot, en_hot):
            for d in ('nov17','nov19','nov20'):
                self.assertIn(f'id="details-{d}"', page); self.assertIn(f'href="#details-{d}"', page)
            for u in ('us.forums.blizzard.com/en/wow/t/2403040/12','us.forums.blizzard.com/en/wow/t/2403040/13','us.forums.blizzard.com/en/wow/t/2403040/14',
                      'eu.forums.blizzard.com/en/wow/t/639885/11','eu.forums.blizzard.com/en/wow/t/639885/12','eu.forums.blizzard.com/en/wow/t/639885/13'):
                self.assertIn('https://'+u+'"', page)
            self.assertIn('id="source-23"', page); self.assertNotIn('id="source-24"', page)
            self.assertNotRegex(page, r'(?i)streamer')
        stale=[str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*.html') if 'du 5 au 16 novembre' in p.read_text() or 'November 5–16' in p.read_text()]
        self.assertEqual(stale, [])
"""
new = """        for page in (hot, en_hot):
            for d in ('nov17','nov19','nov20','nov23'):
                self.assertIn(f'id="details-{d}"', page); self.assertIn(f'href="#details-{d}"', page)
            self.assertIn('id="problemes-en-cours"', page); self.assertIn('href="#problemes-en-cours"', page)
            for u in ('us.forums.blizzard.com/en/wow/t/2403040/12','us.forums.blizzard.com/en/wow/t/2403040/13','us.forums.blizzard.com/en/wow/t/2403040/14','us.forums.blizzard.com/en/wow/t/2403040/15',
                      'eu.forums.blizzard.com/en/wow/t/639885/11','eu.forums.blizzard.com/en/wow/t/639885/12','eu.forums.blizzard.com/en/wow/t/639885/13','eu.forums.blizzard.com/en/wow/t/639885/14',
                      'us.forums.blizzard.com/en/wow/t/2426335/4','eu.forums.blizzard.com/en/wow/t/645296/2','us.forums.blizzard.com/en/wow/t/2424420/2','eu.forums.blizzard.com/en/wow/t/642667/11'):
                self.assertIn('https://'+u+'"', page)
            self.assertIn('id="source-30"', page); self.assertNotIn('id="source-31"', page)
            self.assertIn('Feralheart', page); self.assertIn('Mortal Strike', page)
            self.assertNotRegex(page, r'(?i)streamer')
            self.assertNotIn('Lots des 5, 6, 8, 9, 10 et 11 novembre', page)
            self.assertNotIn('Batches of November 5, 6, 8, 9, 10 and 11', page)
        stale=[str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*.html') if 'du 5 au 16 novembre' in p.read_text() or 'November 5–16' in p.read_text() or 'du 5 au 20 novembre' in p.read_text() or 'November 5–20' in p.read_text()]
        self.assertEqual(stale, [])
"""
assert t.count(old)==1; t=t.replace(old,new)
# Blackmaw : lien vers la fiche donjon
old = """        self.assertIn('Repaire des Noiregueules', bm); self.assertIn('Blackmaw Hold', en_bm)
        for page in (bm, en_bm):
            self.assertIn('<meta name="robots" content="noindex,nofollow">', page)
"""
new = """        self.assertIn('Repaire des Noiregueules', bm); self.assertIn('Blackmaw Hold', en_bm)
        self.assertIn('href="../../../fr/donjons-raids/repaire-des-noiregueules/"', bm)
        self.assertIn('href="../../../en/dungeons-raids/blackmaw-hold/"', en_bm)
        for page in (bm, en_bm):
            self.assertIn('<meta name="robots" content="noindex,nofollow">', page)
"""
assert t.count(old)==1; t=t.replace(old,new)
(T / 'tests/test_community.py').write_text(t)
print(json.dumps({'fingerprint': fp, 'wiki_files': len(files), 'html': sum(1 for k in files if k.endswith('.html'))}))
