"""v41 : captures 412x915 (Chrome du box, serveur local avec la CSP de production) + erreurs console/CSP + images chargées."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
base, out = sys.argv[1], Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
S = [('v41-fr-accueil-rubriques', '/fr/', '.v40-home-grid'),
     ('v41-fr-accueil-mises-a-jour', '/fr/', '.v40-home-updates'),
     ('v41-fr-correctifs-16-novembre', '/fr/actualites/correctifs-forever-5-et-6-novembre/', '#details-nov16'),
     ('v41-fr-collections-hub', '/fr/objets/collections/', None),
     ('v41-fr-collections-hub-cartes', '/fr/objets/collections/', '#rubriques'),
     ('v41-fr-montures-haut', '/fr/objets/montures/', None),
     ('v41-fr-montures-fiches', '/fr/objets/montures/', '#echanges-montures-rapides'),
     ('v41-fr-mascottes-fiches', '/fr/objets/mascottes/', '#quetes'),
     ('v41-fr-jouets-fiches', '/fr/objets/jouets/', '#artisanat'),
     ('v41-fr-heritage-fiches', '/fr/quetes/recompenses-heritage/', '.v41-grid'),
     ('v41-fr-mascottes-sans-image', '/fr/objets/mascottes/', '#p-sazurbie'),
     ('v41-en-collections-hub-cards', '/en/items/collections/', '#rubriques'),
     ('v41-en-mounts-cards', '/en/items/mounts/', '#echanges-montures-rapides')]
problems, report = [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
    for name, path, sel in S:
        ctx = b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=1, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.on('console', lambda m, n=name: problems.append((n, m.type, m.text)) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e, n=name: problems.append((n, 'pageerror', str(e))))
        page.goto(base + path, wait_until='networkidle')
        if sel:
            el = page.query_selector(sel)
            if not el: problems.append((name, 'selector', sel))
            else: page.evaluate("(e)=>{const y=e.getBoundingClientRect().top+scrollY-150; window.scrollTo({top:y,behavior:'instant'})}", el)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(out / f'{name}-412x915.png'))
        if name in ('v41-fr-montures-haut', 'v41-fr-mascottes-fiches', 'v41-fr-jouets-fiches', 'v41-fr-collections-hub', 'v41-fr-heritage-fiches', 'v41-en-mounts-cards'):
            h = page.evaluate('document.body.scrollHeight')
            for y in range(0, h + 915, 700):
                page.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); page.wait_for_timeout(60)
            page.wait_for_timeout(500)
            report[path] = page.evaluate("""()=>{const i=[...document.querySelectorAll('img.v41-ic')];return {imgs:i.length,loaded:i.filter(x=>x.complete&&x.naturalWidth>0).length,
              overflowX: document.documentElement.scrollWidth>window.innerWidth}}""")
        ctx.close()
    b.close()
print(json.dumps({'problems': problems, 'images': report}, ensure_ascii=False, indent=1))
