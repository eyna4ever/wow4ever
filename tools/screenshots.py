"""Local visual check: serves the merged app on 127.0.0.1:8016 with an empty temporary DB and takes screenshots."""
import os, secrets, sys, tempfile, threading
from pathlib import Path
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from community.app import create_app

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    app = create_app({'DATABASE': str(Path(tmp)/'db.sqlite3'), 'SECRET_KEY': secrets.token_urlsafe(48),
                      'PUBLIC_URL': 'http://localhost:8016', 'TESTING': True})
    app.test_cli_runner().invoke(args=['init-db'])
    server = make_server('127.0.0.1', 8016, app); threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            opts = {'headless': True}
            if os.environ.get('BROWSER_EXECUTABLE'): opts['executable_path'] = os.environ['BROWSER_EXECUTABLE']
            browser = p.chromium.launch(**opts)
            shots = [('desktop-1440-fr-accueil.png', '/fr/', 1440, 900, False),
                     ('desktop-1440-fr-accueil-full.png', '/fr/', 1440, 900, True),
                     ('desktop-1440-article-calendrier-forever.png', '/fr/actualites/calendrier-forever/', 1440, 900, False),
                     ('desktop-1440-forums.png', '/community/', 1440, 900, True),
                     ('desktop-1440-compte.png', '/account/', 1440, 900, False),
                     ('mobile-390-fr-accueil.png', '/fr/', 390, 844, False),
                     ('mobile-390-article-calendrier-forever.png', '/fr/actualites/calendrier-forever/', 390, 844, False),
                     ('mobile-390-forums.png', '/community/', 390, 844, True)]
            problems = []
            for name, path, w, h, full in shots:
                page = browser.new_page(viewport={'width': w, 'height': h})
                page.on('console', lambda m: problems.append((path, m.text)) if m.type == 'error' else None)
                page.on('pageerror', lambda e: problems.append((path, str(e))))
                r = page.goto('http://localhost:8016' + path, wait_until='networkidle')
                assert r.status == 200, (path, r.status)
                broken = page.evaluate("[...document.images].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.currentSrc||i.src)")
                if broken: problems.append((path, 'broken images', broken))
                page.screenshot(path=str(out/name), full_page=full)
                page.close()
            page = browser.new_page()
            jpg = page.request.get('http://localhost:8016/assets/art-ar01-calendar-1280.jpg')
            print('jpg', jpg.status, jpg.headers.get('content-type'), len(jpg.body()))
            browser.close()
            print('problems:', problems or 'none')
    finally:
        server.shutdown()
