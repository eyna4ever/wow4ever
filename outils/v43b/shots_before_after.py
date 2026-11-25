"""Captures avant (site en ligne, v43) / après (v43b sur le simulateur = vraie application) de la carte, bureau 1280 px."""
import sys
from playwright.sync_api import sync_playwright
BEFORE, AFTER, OUT = sys.argv[1], sys.argv[2], '/workspace/wowkipedia-v21-elite/v43b-test/captures'
PAGES = [('fr', 'durotar'), ('fr', 'orgrimmar'), ('fr', 'foret-d-elwynn'), ('en', 'elwynn-forest'), ('fr', 'vallee-de-strangleronce')]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for tag, base in (('avant-v43-en-ligne', BEFORE), ('apres-v43b', AFTER)):
        pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
        pg.on('console', lambda m: m.type == 'error' and errs.append(m.text)); pg.on('pageerror', lambda e: errs.append(str(e)))
        for lang, sl in PAGES:
            pg.goto(f'{base}/{lang}/zones/{sl}/', wait_until='load'); pg.locator('#carte-interactive').scroll_into_view_if_needed()
            pg.wait_for_function("()=>[...document.querySelectorAll('.wk-map-tiles img')].every(i=>i.complete&&i.naturalWidth>0)", timeout=20000)
            srcs = pg.evaluate("()=>[...document.querySelectorAll('.wk-map-tiles img')].map(i=>i.getAttribute('src')).slice(0,1)")
            pg.locator('.wk-map-frame').screenshot(path=f'{OUT}/{tag}-{lang}-{sl}.png'); print(tag, lang, sl, srcs, errs)
        pg.close()
    b.close()
