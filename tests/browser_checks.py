"""Browser and accessibility checks against a disposable DB, never production."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import sys
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from community.app import ROOT, create_app


def main():
    results=[]
    output=ROOT/'test-results'
    output.mkdir(exist_ok=True)
    axe=Path(os.environ.get('AXE_PATH',str(ROOT/'qa/node_modules/axe-core/axe.min.js')))
    if not axe.is_file():
        raise RuntimeError('Installer axe-core dans qa/ ou renseigner AXE_PATH.')
    with tempfile.TemporaryDirectory() as directory:
        database=str(Path(directory)/'browser.sqlite3')
        app=create_app({'DATABASE':database,'SECRET_KEY':secrets.token_urlsafe(48),'PUBLIC_URL':'http://localhost:8015',
                        'DISCORD_CLIENT_ID':'12345','DISCORD_CLIENT_SECRET':'qa-only-not-a-real-discord-secret','TESTING':True})
        assert app.test_cli_runner().invoke(args=['init-db']).exit_code==0
        connection=sqlite3.connect(database)
        stamp=int(time.time())
        for uid,role in [(1,'member'),(2,'member'),(3,'admin')]:
            connection.execute('INSERT INTO users(id,discord_id,name,handle,role,created,last_login) VALUES(?,?,?,?,?,?,?)',
                               (uid,str(99000+uid),f'Test QA {uid}',f'qa-{uid}',role,stamp,stamp))
        connection.commit()
        server=make_server('127.0.0.1',8015,app)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                options={'headless':True}
                if os.environ.get('BROWSER_EXECUTABLE'):
                    options['executable_path']=os.environ['BROWSER_EXECUTABLE']
                browser=playwright.chromium.launch(**options)
                context=browser.new_context(viewport={'width':1440,'height':1000})
                page=context.new_page()
                errors=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                csp_errors=[]
                page.on('console',lambda msg: csp_errors.append(msg.text) if 'Content Security Policy' in msg.text else None)

                def visit(path):
                    response=page.goto('http://localhost:8015'+path,wait_until='networkidle')
                    assert response.status==200,(path,response.status)
                    assert not errors,errors

                def sign_in(uid):
                    token=secrets.token_urlsafe(32)
                    connection.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?)',
                        (hashlib.sha256(token.encode()).hexdigest(),uid,secrets.token_urlsafe(32),stamp,stamp,stamp))
                    connection.commit()
                    context.add_cookies([{'name':'forever-local','value':token,'domain':'localhost','path':'/','httpOnly':True,'sameSite':'Lax'}])

                for width in (320,390,768,1440):
                    page.set_viewport_size({'width':width,'height':900})
                    for path in ('/community/','/account/','/privacy/','/fr/','/fr/actualites/calendrier-forever/','/en/zones/mount-hyjal/'):
                        visit(path)
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path,'overflow')
                        results.append({'check':'responsive','width':width,'path':path,'pass':True})
                page.set_viewport_size({'width':1440,'height':1000})
                visit('/community/')
                page.keyboard.press('Tab')
                assert page.locator('.skip').evaluate('(el)=>el===document.activeElement')
                results.append({'check':'keyboard-skip-link','pass':True})
                # Intercept the provider navigation: no real Discord account or network call.
                context.route('https://discord.com/**',lambda route: route.fulfill(status=200,content_type='text/html',body='<p>Discord QA</p>'))
                visit('/account/')
                page.get_by_role('button',name='Continuer avec Discord',exact=True).click()
                page.wait_for_url('https://discord.com/**',timeout=5000)
                assert connection.execute('SELECT count(*) FROM oauth').fetchone()[0]==1
                context.unroute('https://discord.com/**')
                errors.clear()  # errors raised by the intercepted fake Discord page are not site errors
                results.append({'check':'anonymous-login-browser-redirect','pass':True})
                sign_in(1)
                visit('/community/new')
                page.get_by_label('Titre',exact=True).fill('Question Forever pour la recette QA')
                page.get_by_label('Votre message').fill('Explorons Forever ensemble. Message de test temporaire.')
                page.get_by_role('button',name='Publier la discussion',exact=True).click()
                assert page.url.endswith('/community/topics/1'),page.inner_text('main')
                page.wait_for_url('**/community/topics/1')
                page.locator('#post-1').get_by_role('link',name='Modifier',exact=True).click()
                page.get_by_label('Titre',exact=True).fill('Question Forever modifiée par QA')
                page.get_by_role('button',name='Enregistrer les modifications',exact=True).click()
                assert 'Question Forever modifiée' in page.title()
                sign_in(2)
                visit('/community/topics/1')
                page.get_by_role('link',name='Citer',exact=True).click()
                page.get_by_label('Votre réponse').fill('Merci @qa-1, voici une réponse de test.')
                page.get_by_role('button',name='Publier la réponse',exact=True).click()
                page.wait_for_url('**#post-2')
                assert page.locator('#post-2 blockquote').count()==1
                page.locator('#post-1').get_by_role('button',name='Utile').click()
                page.get_by_role('button',name='Suivre',exact=True).click()
                page.get_by_role('button',name='Favori',exact=True).click()
                assert page.get_by_role('button',name='Favori ✓',exact=True).get_attribute('aria-pressed')=='true'
                page.locator('#post-1').get_by_role('link',name='Signaler',exact=True).click()
                page.get_by_label('Motif du signalement').fill('Signalement de test pour la recette uniquement.')
                page.get_by_role('button',name='Transmettre à la modération').click()
                assert page.get_by_role('heading',name='Signalement transmis').count()==1
                sign_in(3)
                visit('/moderation/')
                assert 'Signalement de test' in page.inner_text('main')
                page.get_by_role('button',name='Clore le signalement').click()
                assert 'Aucun signalement ouvert.' in page.inner_text('main')
                visit('/community/profiles/2')
                page.get_by_label('Rôle',exact=True).select_option('moderator')
                page.get_by_role('button',name='Attribuer le rôle sélectionné').click()
                assert connection.execute('SELECT role FROM users WHERE id=2').fetchone()[0]=='moderator'
                page.get_by_role('button',name='Suspendre',exact=True).click()
                assert connection.execute('SELECT suspended FROM users WHERE id=2').fetchone()[0]==1
                results.append({'check':'authenticated-browser-workflows','pass':True})
                assert not csp_errors,csp_errors
                browser.close()

                # Separate context allows only the local audit script to bypass CSP.
                # Functional flows above run with the real, enforced policy.
                browser=playwright.chromium.launch(**options)
                context=browser.new_context(viewport={'width':390,'height':844},bypass_csp=True)
                page=context.new_page()
                for authenticated in (False,True):
                    if authenticated:
                        sign_in(3)
                    paths=('/community/','/account/','/privacy/','/fr/','/fr/actualites/calendrier-forever/','/en/zones/mount-hyjal/') if not authenticated else (
                        '/community/topics/1','/community/new','/community/posts/1/edit','/community/posts/1/report','/community/profiles/2','/account/','/notifications/','/moderation/')
                    for path in paths:
                        visit(path)
                        page.add_script_tag(path=str(axe))
                        report=page.evaluate("async()=>await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})")
                        violations=[{'id':v['id'],'nodes':[n['html'] for n in v['nodes']]} for v in report['violations']]
                        wiki_page=path.startswith(('/fr/','/en/'))
                        # Live wiki pages come from the separate static build (not editable here): their axe findings are
                        # reported as informational ('axe-wiki'); community pages stay strictly blocking.
                        results.append({'check':'axe-wiki' if wiki_page else 'axe','path':path,'authenticated':authenticated,'violations':violations,'pass':not violations})
                        assert wiki_page or not violations,(path,violations)
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),path
                browser.close()
        finally:
            server.shutdown()
            thread.join(timeout=5)
            connection.close()
            (output/'browser-checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    blocking=[r for r in results if r['check']!='axe-wiki']
    info=[r for r in results if r['check']=='axe-wiki']
    print(f"{sum(r['pass'] for r in blocking)}/{len(blocking)} contrôles bloquants réussis ; audits axe du wiki (informatifs) : {sum(r['pass'] for r in info)}/{len(info)} sans violation. Base temporaire supprimée.")


if __name__=='__main__':
    main()
