#!/usr/bin/env python3
"""v42 (t407u) : met à jour tests/wiki-baseline.json et les compteurs de tests/test_community.py dans v42-test/tree."""
import hashlib, json, sys
from pathlib import Path
T = Path('/workspace/wowkipedia-v21-elite/v42-test/tree'); W = T / 'wiki'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
b['source'] = ('v42 (t407u, 2026-11-17, Europe/Paris) : matériaux de métier « où les trouver » (10 nouvelles fiches FR/EN), annuaire « PNJ : où les trouver » sur 50 fiches de zone, matériaux liés sur 12 pages de recettes, 4 montures vendues par un PNJ ; inclut la v41 (Collections, non publiée) : icônes du jeu '
               '(fichiers du client 1.60.1.70862, CDN officiel Blizzard), sur la base v40b (en ligne). 473 pages, 220 fiches. '
               'Empreinte = SHA-256 du manifeste trié des fichiers wiki/. Build de TEST, non publié. ' + 'Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
hdr = H(T / 'community/templates/_v2_header.html')
t = (T / 'tests/test_community.py').read_text()
rep = [
 ("self.assertEqual(baseline['tarball_sha256'],'e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce')  # v40b",
  f"self.assertEqual(baseline['tarball_sha256'],'{fp}')  # v42 (t407u, matériaux + PNJ, inclut v41, sur v40b) ; v40b = e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce ; v40b"),
 ("self.assertEqual(sum(1 for f in files if f.endswith('.html')),451)  # v39", "self.assertEqual(sum(1 for f in files if f.endswith('.html')),473)  # v42 (t407u): +22 pages (Collections FR+EN, 10 fiches Matériaux FR+EN)  # v39"),
 ("self.assertEqual(len(set(current)-set(reference['pages'])),310)  # v39", "self.assertEqual(len(set(current)-set(reference['pages'])),332)  # v42 (t407u): +22 (Collections et Matériaux FR+EN) ; v39"),
 ("self.assertEqual(len(pages),451)  # v39", "self.assertEqual(len(pages),473)  # v42 (t407u): +2 Collections FR+EN +20 Matériaux FR+EN ; v39"),
 ("self.assertEqual(len(ids),209)  # v39", "self.assertEqual(len(ids),220)  # v42 (t407u): +1 fiche Collections +10 fiches Matériaux ; v39"),
 ("self.assertEqual(hashlib.sha256(header.encode()).hexdigest(),'f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019','forum header = v38 + compteurs v39')",
  f"self.assertEqual(hashlib.sha256(header.encode()).hexdigest(),'{hdr}','forum header = v38 + compteurs v39 + Objets 9 (v41) + Métiers 28 (v42, t407u)')  # v39 = f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019"),
]
for a, c in rep:
    n = t.count(a); assert n >= 1, a[:80]; t = t.replace(a, c)
(T / 'tests/test_community.py').write_text(t)
print('fingerprint', fp, 'files', len(files), 'html', sum(1 for k in files if k.endswith('.html')), 'header', hdr)
