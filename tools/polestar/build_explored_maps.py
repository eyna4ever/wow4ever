"""v43b : cartes « entièrement explorées » comme en jeu. Pour chaque zone : tuiles de base (UiMapArtTile, couche 0) +
calques des zones explorées (WorldMapOverlay / WorldMapOverlayTile, client 1.60.1.70862, CDN officiel Blizzard) collés à
leurs décalages officiels (OffsetX/OffsetY, tuiles de 256 px), sans autre retouche ; puis redécoupe en tuiles identiques.
Seuls les calques sans condition (PlayerConditionID = 0) sont posés (ceux à condition dépendent de la phase du joueur)."""
import json, io, hashlib, os, sys, pathlib
sys.path.insert(0, '/workspace/wowkipedia-v21-elite/collections-v41/outils'); os.chdir('/workspace/wowkipedia-v21-elite/collections-v41/outils')
import tact, db2
from PIL import Image
C = pathlib.Path('/workspace/polestar-work/client'); IN = pathlib.Path('/workspace/polestar-work/maps'); OUT = pathlib.Path('/workspace/polestar-work/explored')
rd = lambda n: db2.read((C / f'{n}.enUS.db2').read_bytes(), n)
O, OT, AT, L, A = rd('WorldMapOverlay'), rd('WorldMapOverlayTile'), rd('UiMapArtTile'), rd('UiMapArtStyleLayer'), rd('UiMapArt')
zones = json.load(open('/workspace/polestar-work/zones.json'))
t = tact.open_70862(); t.load_encoding(); t.load_root()
def blp(fd):
    raw = t.file(fd)
    if not raw or raw.count(0) == len(raw): return None, raw
    im = Image.open(io.BytesIO(raw)); im.load(); return im.convert('RGBA'), raw
tiles_by_ov = {}
for r in OT.values():
    tiles_by_ov.setdefault(r['WorldMapOverlayID'], []).append(r)
report = []
for z in zones:
    mdir = IN / str(z['uiMap'])
    if not (mdir / 'manifest.json').exists(): continue
    man = json.load(open(mdir / 'manifest.json')); art = man['uiMapArtID']; lay = man['layer']
    tw, th = lay['tw'], lay['th']
    rows = max(x['row'] for x in man['tiles']) + 1; cols = max(x['col'] for x in man['tiles']) + 1
    canvas = Image.new('RGBA', (cols * tw, rows * th))
    before = Image.new('RGBA', (cols * tw, rows * th))
    for x in man['tiles']:
        im, raw = blp(x['fdid']); assert im is not None and hashlib.sha256(raw).hexdigest() == x['blp_sha256']
        canvas.paste(im, (x['col'] * tw, x['row'] * th)); before.paste(im, (x['col'] * tw, x['row'] * th))
    ovs = sorted((o for o in O.values() if o['UiMapArtID'] == art), key=lambda o: o['ID'])
    used, cond, enc, src = 0, 0, 0, []
    for o in ovs:
        if o['PlayerConditionID']: cond += 1; continue
        pieces = sorted(tiles_by_ov.get(o['ID'], []), key=lambda r: (r['LayerIndex'], r['RowIndex'], r['ColIndex']))
        pieces = [p for p in pieces if p['LayerIndex'] == 0]
        ok = True; imgs = []
        for p in pieces:
            im, raw = blp(p['FileDataID'])
            if im is None: ok = False; break
            imgs.append((p, im, hashlib.sha256(raw).hexdigest()))
        if not ok or not imgs: enc += 1; continue
        for p, im, h in imgs:
            x0, y0 = p['ColIndex'] * 256, p['RowIndex'] * 256
            w = min(im.size[0], o['TextureWidth'] - x0); hh = min(im.size[1], o['TextureHeight'] - y0)
            if w <= 0 or hh <= 0: continue
            piece = im.crop((0, 0, w, hh))
            canvas.alpha_composite(piece, (o['OffsetX'] + x0, o['OffsetY'] + y0))
            src.append({'overlay': o['ID'], 'area': o['AreaID'][0], 'fdid': p['FileDataID'], 'row': p['RowIndex'], 'col': p['ColIndex'], 'blp_sha256': h})
        used += 1
    d = OUT / str(z['uiMap']); d.mkdir(parents=True, exist_ok=True); out = []
    for x in man['tiles']:
        tile = canvas.crop((x['col'] * tw, x['row'] * th, x['col'] * tw + x['w'], x['row'] * th + x['h'])).convert('RGB')
        tile.save(d / x['file'], 'WEBP', quality=85, method=6); out.append({**x, 'webp_sha256': hashlib.sha256((d / x['file']).read_bytes()).hexdigest()})
    W, H = lay['w'], lay['h']
    canvas.crop((0, 0, W, H)).convert('RGB').save(d / '_after.png'); before.crop((0, 0, W, H)).convert('RGB').save(d / '_before.png')
    json.dump({'build': '1.60.1.70862', 'uiMapID': z['uiMap'], 'uiMapArtID': art, 'layer': lay, 'tiles': out, 'overlays_used': used,
               'overlays_conditional_skipped': cond, 'overlays_unreadable': enc, 'overlay_pieces': src,
               'method': 'base tiles + WorldMapOverlay layers at official offsets (as rendered in game, fully explored); BLP -> WebP q85'},
              open(d / 'manifest.json', 'w'), indent=1)
    report.append({'fr': z['fr'], 'uiMap': z['uiMap'], 'overlays': len(ovs), 'used': used, 'conditional': cond, 'unreadable': enc})
    print(z['fr'], z['uiMap'], len(ovs), used, cond, enc, flush=True)
json.dump(report, open(OUT / 'report.json', 'w'), indent=1, ensure_ascii=False)
