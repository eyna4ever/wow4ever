#!/usr/bin/env python3
"""v42c (t412u/t413u) : met à jour tests/wiki-baseline.json et l'empreinte de tests/test_community.py dans v42c-test/tree (base v42b)."""
import hashlib, json, re
from pathlib import Path
T = Path('/workspace/wowkipedia-v21-elite/v42c-test/tree'); W = T / 'wiki'
V42B = '002361bf959a5df5b118146dd861265357d50361a1ba576de5ed70609ed27067'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
if b['tarball_sha256'] == V42B:
    b['source'] = ('v42c (t412u/t413u, 2026-11-17) : recherche affichée dans la page « Tout le wiki » (/fr/wiki/, /en/wiki/, ?q= compris) '
                   'et adresses versionnées ?v=42c de wk-header.js, ui-core.mjs, v2.css. Base v42b en ligne. Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
t = (T / 'tests/test_community.py').read_text()
t, n = re.subn(r"self\.assertEqual\(baseline\['tarball_sha256'\],'[0-9a-f]{64}'\)", f"self.assertEqual(baseline['tarball_sha256'],'{fp}')", t, count=1); assert n == 1
a = "        self.assertEqual(self.get('/search-detail-de.json').status_code,404)\n"
if 'v42c (t412u' not in t:
    assert t.count(a) == 1
    t = t.replace(a, a + "        for name in ('wk-header.js','ui-core.mjs','v2.css'):  # v42c (t412u/t413u): versioned asset URLs are served\n"
                         "            self.assertEqual(self.get(f'/{name}?v=42c').status_code,200)\n")
for a, c in [(r"""self.assertRegex(links[0],r'^(\./|(\.\./)+)v2\.css$')""", r"""self.assertRegex(links[0],r'^(\./|(\.\./)+)v2\.css\?v=42c$')  # v42c (t412u/t413u): versioned URL"""),
             (r"""self.assertRegex(text,r'<script type="module" src="(\./|(\.\./)+)wk-header\.js"></script>')""", r"""self.assertRegex(text,r'<script type="module" src="(\./|(\.\./)+)wk-header\.js\?v=42c"></script>')  # v42c (t412u/t413u): versioned URL""")]:
    if c not in t: assert t.count(a) == 1, a; t = t.replace(a, c)
(T / 'tests/test_community.py').write_text(t)
print('fingerprint', fp, 'files', len(files), 'html', sum(1 for k in files if k.endswith('.html')))
