"""Export article illustrations: webp 640 + 1280 and jpg 1280 fallback, update provenance.json.
Sources: design/illustrations-src/articles/<file>.jpg (1280x720, GenerateImage output, unmodified)."""
import hashlib, json, subprocess, pathlib
from PIL import Image
root = pathlib.Path(__file__).resolve().parent.parent
meta = json.loads(subprocess.check_output(['node', '-e', "import('./lib/visuals.mjs').then(m=>console.log(JSON.stringify({date:m.VISUAL_DATE,v:Object.values(m.ARTICLE_VISUALS)})))"], cwd=root))
src_dir = root / 'design/illustrations-src/articles'
assets = root / 'public/wiki/assets'
prov_path = root / 'design/illustrations-src/provenance.json'
prov = json.loads(prov_path.read_text())
total = 0
for v in meta['v']:
    src = src_dir / f"{v['file']}.jpg"
    data = src.read_bytes()
    img = Image.open(src).convert('RGB')
    assert img.size == (1280, 720), (src, img.size)
    files = {}
    for w, q in ((640, 74), (1280, 72)):
        out = assets / f"art-{v['file']}-{w}.webp"
        im = img if w == 1280 else img.resize((w, w * 9 // 16), Image.LANCZOS)
        im.save(out, 'WEBP', quality=q, method=6)
        files[str(out.relative_to(root))] = out.stat().st_size
    jpg = assets / f"art-{v['file']}-1280.jpg"
    img.save(jpg, 'JPEG', quality=74, optimize=True, progressive=True)
    files[str(jpg.relative_to(root))] = jpg.stat().st_size
    total += sum(files.values())
    prov[f"article:{v['code']}"] = {
        'entryId': v['id'], 'method': 'GenerateImage (outil de génération d’images de Grok Bot), image originale, aucune référence ni capture',
        'date': meta['date'], 'prompt': v['prompt'], 'source': f"design/illustrations-src/articles/{v['file']}.jpg",
        'sourceSha256': hashlib.sha256(data).hexdigest(), 'size': [1280, 720], 'alt': v['alt'],
        'caption': {'fr': 'Illustration d’ambiance — ne constitue pas une source', 'en': 'Ambiance illustration — not a source'},
        'ip': 'Aucun logo, personnage reconnaissable, capture, interface ou texte ; création d’ambiance sans valeur documentaire.',
        'files': files}
prov_path.write_text(json.dumps(prov, ensure_ascii=False, indent=1) + '\n')
print(f"{len(meta['v'])} illustrations, {total/1024/1024:.2f} MiB of exports")
