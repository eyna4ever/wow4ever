"""v42 (t407u) : captures 412x915, serveur local avec la CSP de production, erreurs console/CSP, images, débordement horizontal."""
import json, sys, threading, functools, http.server
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = '/workspace/wowkipedia-v21-elite/v42-test/tree/wiki'; out = Path('/workspace/wowkipedia-v21-elite/v42-test/captures'); out.mkdir(parents=True, exist_ok=True)
CSP = "default-src 'self'; script-src 'self'; img-src 'self'; connect-src 'self'; style-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self): self.send_header('Content-Security-Policy', CSP); super().end_headers()
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8742), functools.partial(H, directory=ROOT)); threading.Thread(target=srv.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:8742'
S = [('01-fr-accueil-metiers', '/fr/', '.v40-home a[href="../fr/metiers/"]'),
     ('02-fr-accueil-acces-rapide', '/fr/', 'a[href="../fr/metiers/materiaux/"]'),
     ('03-fr-index-metiers-materiaux', '/fr/metiers/', '#fiches-materials'),
     ('04-fr-materiaux-accueil', '/fr/metiers/materiaux/', None),
     ('05-fr-materiaux-familles', '/fr/metiers/materiaux/', '#familles'),
     ('06-fr-materiaux-couverture', '/fr/metiers/materiaux/', '#couverture'),
     ('07-fr-minerais-haut', '/fr/metiers/materiaux-minerais-barres-pierres/', None),
     ('08-fr-minerais-cuivre', '/fr/metiers/materiaux-minerais-barres-pierres/', '#mat-2770'),
     ('09-fr-barre-de-cuivre', '/fr/metiers/materiaux-minerais-barres-pierres/', '#mat-2840'),
     ('10-fr-herbes', '/fr/metiers/materiaux-herbes/', '#mat-765'),
     ('11-fr-cuirs', '/fr/metiers/materiaux-cuirs-peaux/', '#mat-2318'),
     ('12-fr-tissus-fil', '/fr/metiers/materiaux-tissus/', '#mat-2320'),
     ('13-fr-recettes-alchimie-materiaux', '/fr/metiers/recettes-alchimie/', '#materiaux'),
     ('14-fr-recettes-alchimie-composants', '/fr/metiers/recettes-alchimie/', '#materiaux details.v42-vendor'),
     ('15-fr-mulgore-pnj', '/fr/zones/mulgore/', '#pnj-ou-les-trouver'),
     ('16-fr-mulgore-objets-quete', '/fr/zones/mulgore/', '#pnj-ou-les-trouver h3:nth-of-type(4)'),
     ('17-fr-orgrimmar-vendeurs', '/fr/zones/orgrimmar/', '#pnj-ou-les-trouver h3:nth-of-type(2)'),
     ('18-fr-orgrimmar-vendeur-ouvert', '/fr/zones/orgrimmar/', '#pnj-ou-les-trouver details.v42-vendor'),
     ('19-fr-hurlevent-donneurs', '/fr/zones/hurlevent/', '#pnj-ou-les-trouver h3:nth-of-type(3)'),
     ('20-fr-durotar-autres-pnj', '/fr/zones/durotar/', '#pnj-ou-les-trouver details.v42-vendor:last-of-type'),
     ('21-fr-mulgore-sources', '/fr/zones/mulgore/', '#sources'),
     ('22-fr-montures-vendeur', '/fr/objets/montures/', '#vendues-par-un-pnj'),
     ('23-en-materials-hub', '/en/professions/materials/', '#familles'),
     ('24-en-thunder-bluff-npcs', '/en/zones/thunder-bluff/', '#pnj-ou-les-trouver')]
problems, report = [], {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
    for name, path, sel in S:
        ctx = b.new_context(viewport={'width': 412, 'height': 915}, device_scale_factor=1, is_mobile=True, has_touch=True)
        page = ctx.new_page()
        page.on('console', lambda m, n=name: problems.append((n, m.type, m.text)) if m.type in ('error', 'warning') else None)
        page.on('response', lambda r, n=name: problems.append((n, 'http', r.status, r.url)) if r.status >= 400 else None)
        page.on('pageerror', lambda e, n=name: problems.append((n, 'pageerror', str(e))))
        r = page.goto(base + path, wait_until='networkidle')
        if r.status != 200: problems.append((name, 'status', r.status))
        if sel:
            el = page.query_selector(sel)
            if not el: problems.append((name, 'selector', sel))
            else:
                if sel and 'details' in sel: page.evaluate("(e)=>e.open=true", el)
                page.evaluate("(e)=>{const y=e.getBoundingClientRect().top+scrollY-90; window.scrollTo({top:y,behavior:'instant'})}", el)
        page.wait_for_timeout(900)
        page.screenshot(path=str(out / f'{name}-412x915.png'))
        if path not in report:
            h = page.evaluate('document.body.scrollHeight')
            for y in range(0, h + 915, 800):
                page.evaluate(f"window.scrollTo({{top:{y},behavior:'instant'}})"); page.wait_for_timeout(40)
            page.wait_for_timeout(400)
            report[path] = page.evaluate("""()=>{const i=[...document.querySelectorAll('img.v41-ic, img.v42-chip-ic')];return {imgs:i.length,loaded:i.filter(x=>x.complete&&x.naturalWidth>0).length,
              overflowX: document.documentElement.scrollWidth>window.innerWidth, height: document.body.scrollHeight}}""")
        ctx.close()
    b.close()
srv.shutdown()
print(json.dumps({'problems': problems, 'pages': report}, ensure_ascii=False, indent=1))
