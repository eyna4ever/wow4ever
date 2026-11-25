#!/usr/bin/env python3
"""v41 : met à jour tests/wiki-baseline.json et les compteurs de tests/test_community.py dans v41-test/tree."""
import hashlib, json, sys
from pathlib import Path
T = Path('/workspace/wowkipedia-v21-elite/v41-test/tree'); W = T / 'wiki'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
b['source'] = ('v41 (t403u, 2026-11-17, Europe/Paris) : catégorie Collections (montures, mascottes, jouets, héritage) illustrée par les icônes du jeu '
               '(fichiers du client 1.60.1.70862, CDN officiel Blizzard), 1 nouvelle fiche FR/EN + 4 fiches révisées, sur la base v40b (en ligne). 453 pages, 210 fiches. '
               'Empreinte = SHA-256 du manifeste trié des fichiers wiki/. Build de TEST, non publié. ' + 'Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
hdr = H(T / 'community/templates/_v2_header.html')
t = (T / 'tests/test_community.py').read_text()
rep = [
 ("self.assertEqual(baseline['tarball_sha256'],'e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce')  # v40b",
  f"self.assertEqual(baseline['tarball_sha256'],'{fp}')  # v41 (t403u, collections, sur v40b) ; v40b = e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce ; v40b"),
 ("self.assertEqual(sum(1 for f in files if f.endswith('.html')),451)  # v39", "self.assertEqual(sum(1 for f in files if f.endswith('.html')),453)  # v41 (t403u): +2 pages (Collections FR+EN)  # v39"),
 ("self.assertEqual(len(set(current)-set(reference['pages'])),310)  # v39", "self.assertEqual(len(set(current)-set(reference['pages'])),312)  # v41 (t403u): +2 Collections FR+EN ; v39"),
 ("self.assertEqual(len(pages),451)  # v39", "self.assertEqual(len(pages),453)  # v41 (t403u): +2 Collections FR+EN ; v39"),
 ("self.assertEqual(len(ids),209)  # v39", "self.assertEqual(len(ids),210)  # v41 (t403u): +1 fiche Collections ; v39"),
 ("self.assertEqual(hashlib.sha256(header.encode()).hexdigest(),'f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019','forum header = v38 + compteurs v39')",
  f"self.assertEqual(hashlib.sha256(header.encode()).hexdigest(),'{hdr}','forum header = v38 + compteurs v39 + Objets 9 (v41, t403u)')  # v39 = f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019"),
]
for a, c in rep:
    n = t.count(a); assert n >= 1, a[:80]; t = t.replace(a, c)
(T / 'tests/test_community.py').write_text(t)
print('fingerprint', fp, 'files', len(files), 'html', sum(1 for k in files if k.endswith('.html')), 'header', hdr)
