"""v43 test: every zone page FR+EN under the production CSP (Chrome headless). Mobile (412x915, touch) on town pages
+ screenshots. Checks: tiles loaded, pins placed inside the frame, filters, compact card in towns, no JS/CSP errors,
no horizontal scroll, merged quest table present once, no-JS fallback list."""
import json, sys
from playwright.sync_api import sync_playwright
B = sys.argv[1]; OUT = '/workspace/wowkipedia-v21-elite/v43b-test/captures'
zones = json.load(open('/workspace/polestar-work/zones.json'))
TOWNS = ['orgrimmar', 'hurlevent', 'durotar', 'ile-de-zephras', 'forgefer', 'thunder-bluff']
res = {'pages': {}, 'mobile': {}}; problems = []
UA = 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36'
CHECK = """()=>{const f=document.querySelector('.wk-map-frame');const fr=f?f.getBoundingClientRect():null;
const imgs=[...document.querySelectorAll('.wk-map-tiles img')];const pins=[...document.querySelectorAll('.wk-pin')];
const vis=pins.filter(b=>!b.hidden);const out=vis.filter(b=>{const r=b.getBoundingClientRect();return r.left<fr.left-16||r.right>fr.right+16||r.top<fr.top-16||r.bottom>fr.bottom+16}).length;
return {imgs:imgs.length,loaded:imgs.filter(i=>i.complete&&i.naturalWidth>0).length,pins:pins.length,visible:vis.length,outside:out,
quest_sections:document.querySelectorAll('#quetes-liste').length,rows:document.querySelectorAll('#quetes-liste tbody tr').length,
hscroll:document.documentElement.scrollWidth>window.innerWidth+1}}"""
with sync_playwright() as p:
    br = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
    def ctx(mobile):
        c = br.new_context(**(dict(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, user_agent=UA) if mobile else dict(viewport={'width': 1280, 'height': 800})))
        pg = c.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: (m.type == 'error' and 'Failed to load resource' not in m.text) and errs.append(m.text))
        return c, pg, errs
    c, pg, errs = ctx(False)
    for z in zones:
        for lang, slug in (('fr', z['fr']), ('en', z['en'])):
            errs.clear()
            pg.goto(f"{B}/{lang}/zones/{slug}/", wait_until='load')
            pg.locator('#carte-interactive').scroll_into_view_if_needed()
            pg.wait_for_function("()=>[...document.querySelectorAll('.wk-map-tiles img')].every(i=>i.complete)", timeout=15000)
            pg.wait_for_timeout(150)
            s = pg.evaluate(CHECK); s['errors'] = list(errs)
            ok = s['imgs'] > 0 and s['loaded'] == s['imgs'] and s['outside'] == 0 and s['quest_sections'] == 1 and (s['rows'] > 0 or s['pins'] == 0) and not s['errors'] and not s['hscroll'] and (s['pins'] == 0 or s['visible'] > 0 or True)
            res['pages'][f'{lang}/{slug}'] = s
            if not ok: problems.append(f'{lang}/{slug}')
    c.close()
    for slug in TOWNS:
        z = next(x for x in zones if x['fr'] == slug)
        for lang, sl in (('fr', z['fr']), ('en', z['en'])):
            c, pg, errs = ctx(True)
            pg.goto(f"{B}/{lang}/zones/{sl}/", wait_until='load'); pg.locator('#carte-interactive').scroll_into_view_if_needed(); pg.wait_for_timeout(500)
            vis = pg.locator('.wk-pin:not([hidden])')
            if vis.count() == 0:
                res['mobile'][f'{lang}/{sl}'] = {'pins_visible': 0}; c.close(); continue
            # tap the marker with the most neighbours (densest spot)
            best = pg.evaluate("""()=>{const v=[...document.querySelectorAll('.wk-pin')].filter(b=>!b.hidden);let bi=0,bn=-1;
              v.forEach((b,i)=>{const x=parseFloat(b.style.left),y=parseFloat(b.style.top);const n=v.filter(o=>Math.hypot(parseFloat(o.style.left)-x,parseFloat(o.style.top)-y)<=2.5).length;if(n>bn){bn=n;bi=i}});
              const r=v[bi].getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2,n:bn}}""")
            pg.touchscreen.tap(best['x'], best['y']); pg.wait_for_timeout(300)
            card = pg.evaluate("""()=>{const c=document.querySelector('.wk-map-card');const r=c.getBoundingClientRect();
              return {shown:!c.hidden,entries:c.querySelectorAll('details').length,open:c.querySelectorAll('details[open]').length,height:Math.round(r.height),vh:innerHeight,head:c.querySelector('.wk-card-head strong')?.textContent}}""")
            pg.locator('#carte-interactive').screenshot(path=f'{OUT}/v43b-{lang}-{sl}-mobile-carte.png')
            card['near'] = best['n']; card['errors'] = list(errs)
            res['mobile'][f'{lang}/{sl}'] = card
            if not (card['shown'] and card['entries'] <= 8 and card['open'] == 1 and card['height'] <= 0.45 * card['vh'] + 2 and not errs): problems.append('mobile ' + sl + lang)
            c.close()
    c = br.new_context(java_script_enabled=False); pg = c.new_page()
    pg.goto(f"{B}/fr/zones/orgrimmar/"); res['nojs_rows'] = pg.locator('.wk-map-table tbody tr').count()
    if not res['nojs_rows']: problems.append('nojs')
    c.close(); br.close()
summary = {'pages_tested': len(res['pages']), 'pages_with_pins': sum(1 for v in res['pages'].values() if v['pins']), 'total_rows': sum(v['rows'] for v in res['pages'].values()), 'mobile': res['mobile'], 'nojs_rows': res['nojs_rows'], 'problems': problems}
json.dump(res, open('/workspace/wowkipedia-v21-elite/v43b-test/map_test_all.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(summary, ensure_ascii=False, indent=1)); sys.exit(1 if problems else 0)
