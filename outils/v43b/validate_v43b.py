"""v43b : compare v43b-test/tree avec la v43 en ligne (polestar-test/tree). Changements permis : tuiles de carte (mêmes noms),
100 fiches de zone (adresses des tuiles ?v=43b + phrase de crédit), 2 pages « Sources et licences » (crédit), 2 fichiers de test."""
import filecmp, hashlib, json, re, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'polestar-test/tree'; B = R / 'v43b-test/tree'
walk = lambda p: {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file() and '__pycache__' not in x.parts}
fa, fb = walk(A), walk(B); bad = []
if fa != fb: bad.append(('fichiers ajoutés/retirés', sorted(fa ^ fb)[:5]))
ch = sorted(f for f in fa & fb if not filecmp.cmp(A / f, B / f, shallow=False))
tiles = [f for f in ch if re.fullmatch(r'wiki/assets/carte/\d+/r\d+-c\d+\.webp', f)]
pages = [f for f in ch if re.fullmatch(r'wiki/(fr|en)/zones/[^/]+/index\.html', f)]
cred = [f for f in ch if re.fullmatch(r'wiki/(fr/sources-et-licences|en/sources-and-licences)/index\.html', f)]
other = sorted(set(ch) - set(tiles) - set(pages) - set(cred))
if other != ['tests/test_community.py', 'tests/wiki-baseline.json']: bad.append(('autres changements', other))
OLD_FR = 'Carte : image du jeu World of Warcraft: Forever © Blizzard Entertainment, tirée des fichiers du client 1.60.1.70862, non retouchée (seuls le format et la compression ont changé).'
OLD_EN = 'Map: World of Warcraft: Forever in-game image © Blizzard Entertainment, from the client 1.60.1.70862 files, not retouched (only format and compression changed).'
sys.path.insert(0, '/workspace/wow4ever-polestar/tools/polestar'); import render_zone as rz
for f in pages:
    o, n = (A / f).read_text(), (B / f).read_text(); fr = '/fr/' in f
    o2 = re.sub(r'(assets/carte/\d+/r\d+-c\d+\.webp)"', r'\1?v=43b"', o).replace(OLD_FR if fr else OLD_EN, rz.TXT['fr' if fr else 'en']['credit'])
    if o2 != n: bad.append((f, 'autre contenu modifié'))
    if re.search(r'\.webp"', n) and re.search(r'assets/carte/\d+/r\d+-c\d+\.webp"', n): bad.append((f, 'tuile sans ?v=43b'))
for f in cred:
    if 'WorldMapOverlay' not in (B / f).read_text(): bad.append((f, 'crédit non mis à jour'))
exp = json.load(open('/workspace/polestar-work/explored/report.json'))
withov = {str(z['uiMap']) for z in exp if z['used']}
tz = {f.split('/')[3] for f in tiles}
if not tz <= withov: bad.append(('tuiles changées sans calque', sorted(tz - withov)))
print(json.dumps({'tiles_changed': len(tiles), 'zones_tiles_changed': len(tz), 'zones_with_layers': len(withov), 'pages': len(pages), 'credits_pages': len(cred),
                  'other': other, 'bytes_tiles_new': sum((B / f).stat().st_size for f in tiles), 'bytes_tiles_old': sum((A / f).stat().st_size for f in tiles), 'problems': bad[:20]}, ensure_ascii=False, indent=1))
sys.exit(1 if bad or len(pages) != 100 or len(cred) != 2 else 0)
