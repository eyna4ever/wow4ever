"""Extract each zone's world-map tiles from the WoW Forever client 1.60.1.70862 (official Blizzard CDN).
BLP -> WebP (quality 85: format/compression change only, no retouching). Writes maps/<uimap>/ + manifest."""
import json, io, hashlib, re, os, sys, pathlib
sys.path.insert(0, '/workspace/wowkipedia-v21-elite/collections-v41/outils'); os.chdir('/workspace/wowkipedia-v21-elite/collections-v41/outils')
import tact, db2
from PIL import Image
C = pathlib.Path('/workspace/polestar-work/client'); OUT = pathlib.Path('/workspace/polestar-work/maps')
rd = lambda n: db2.read((C / f'{n}.enUS.db2').read_bytes(), n)
U, X, T, A, L = rd('UiMap'), rd('UiMapXMapArt'), rd('UiMapArtTile'), rd('UiMapArt'), rd('UiMapArtStyleLayer')
ASG = json.load(open('/workspace/polestar-work/uimap-assignment-70862.json'))['rows']
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
byname = {norm(v['Name_lang']): k for k, v in U.items() if v['Type'] >= 3}
tree = pathlib.Path('/workspace/wowkipedia-v21-elite/v42c-test/tree/wiki')
zones = []
for slug in sorted(os.listdir(tree / 'fr/zones')):
    p = tree / 'fr/zones' / slug / 'index.html'
    if not p.exists(): continue
    s = p.read_text(); m = re.search(r'href="\.\./\.\./\.\./en/zones/([^/"]+)/"[^>]*hreflang="en"|hreflang="en"[^>]*href="\.\./\.\./\.\./en/zones/([^/"]+)/"', s)
    en = (m.group(1) or m.group(2)) if m else None
    um = byname.get(norm(en or ''))
    if not um: continue
    asg = [r for r in ASG if r['UiMapID'] == um and r.get('OrderIndex', 0) == 0]
    zones.append({'fr': slug, 'en': en, 'uiMap': um, 'name_en': U[um]['Name_lang'], 'areaID': asg[0]['AreaID'] if asg else None, 'mapID': asg[0]['MapID'] if asg else None})
t = tact.open_70862(); t.load_encoding(); t.load_root()
layer = {r['UiMapArtStyleID']: r for r in L.values() if r['LayerIndex'] == 0}
for z in zones:
    arts = [r['UiMapArtID'] for r in X.values() if r['UiMapID'] == z['uiMap'] and r['PhaseID'] == 0]
    if not arts: z['tiles'] = []; continue
    art = arts[0]; st = layer[A[art]['UiMapArtStyleID']]
    tiles = sorted([r for r in T.values() if r['UiMapArtID'] == art and r['LayerIndex'] == 0], key=lambda r: (r['RowIndex'], r['ColIndex']))
    d = OUT / str(z['uiMap']); d.mkdir(parents=True, exist_ok=True); man = []
    for r in tiles:
        raw = t.file(r['FileDataID'])
        if raw.count(0) == len(raw): man = None; break
        im = Image.open(io.BytesIO(raw)); im.load()
        f = f"r{r['RowIndex']}-c{r['ColIndex']}.webp"
        im.convert('RGB').save(d / f, 'WEBP', quality=85, method=6)
        man.append({'row': r['RowIndex'], 'col': r['ColIndex'], 'fdid': r['FileDataID'], 'w': im.size[0], 'h': im.size[1], 'blp_sha256': hashlib.sha256(raw).hexdigest(), 'file': f})
    z.update(tiles=man or [], art=art, layer={'w': st['LayerWidth'], 'h': st['LayerHeight'], 'tw': st['TileWidth'], 'th': st['TileHeight']})
    if man: json.dump({'build': '1.60.1.70862', 'uiMapID': z['uiMap'], 'uiMapArtID': art, 'layer': z['layer'], 'tiles': man, 'conversion': 'BLP -> WebP q85, no retouching'}, open(d / 'manifest.json', 'w'), indent=1)
    print(z['fr'], z['uiMap'], len(man or []), flush=True)
json.dump(zones, open('/workspace/polestar-work/zones.json', 'w'), indent=1, ensure_ascii=False)
