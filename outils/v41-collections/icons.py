#!/usr/bin/env python3
"""Fetch item icons (BLP) by FileDataID from the WoW Forever client on the official Blizzard CDN,
convert to WebP (format conversion only, no retouching). Writes ../out/icons/<fdid>.webp + manifest."""
import json, io, hashlib, pathlib
from PIL import Image
import tact
d = json.load(open('../out/collections.json'))
t = tact.open_70862(); t.load_encoding(); t.load_root()
out = pathlib.Path('../out/icons'); out.mkdir(parents=True, exist_ok=True)
blp = pathlib.Path('../cache/blp'); blp.mkdir(exist_ok=True)
fids = set()
for k in ('mounts', 'pets', 'toys'):
    for x in d[k]:
        if x.get('icon'): fids.add(x['icon'])
if d.get('tabard', {}).get('icon'): fids.add(d['tabard']['icon'])
man = {}; fail = []
for f in sorted(fids):
    try:
        raw = t.file(f)
        if raw.count(0) == len(raw): raise ValueError('encrypted/empty')
        (blp / f'{f}.blp').write_bytes(raw)
        im = Image.open(io.BytesIO(raw)); im.load()
        w, h = im.size
        im = im.convert('RGBA')
        p = out / f'{f}.webp'
        im.save(p, 'WEBP', quality=88, method=6)
        man[f] = dict(w=w, h=h, blp_sha256=hashlib.sha256(raw).hexdigest(), webp_bytes=p.stat().st_size)
    except Exception as e:
        fail.append((f, repr(e)))
json.dump(dict(build='1.60.1.70862', icons=man, failed=fail), open('../out/icons-manifest.json', 'w'), indent=1)
print(len(fids), 'ok', len(man), 'fail', fail[:10], 'bytes', sum(v['webp_bytes'] for v in man.values()))
