import base64
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import subprocess
import tempfile
import time
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from community.app import ROOT, create_app, digest

BASE = 'http://localhost:8000'


class CommunityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.database = str(Path(self.tmp.name)/'db.sqlite3')
        self.app = create_app({'TESTING': True, 'DATABASE': self.database,
                               'SECRET_KEY': 'test-secret-with-at-least-thirty-two-characters',
                               'PUBLIC_URL': BASE, 'DISCORD_CLIENT_ID': '12345',
                               'DISCORD_CLIENT_SECRET': 'test-client-secret'})
        self.runner = self.app.test_cli_runner()
        result = self.runner.invoke(args=['init-db'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.conn = sqlite3.connect(self.database)
        self.conn.row_factory = sqlite3.Row
        stamp = int(time.time())
        for uid, role in [(1,'member'),(2,'member'),(3,'moderator'),(4,'admin')]:
            self.conn.execute('INSERT INTO users(id,discord_id,name,handle,role,created,last_login) VALUES(?,?,?,?,?,?,?)',
                              (uid,str(10000+uid),f'Membre {uid}',f'u-{10000+uid}',role,stamp,stamp))
        self.conn.commit()
        self.client = self.app.test_client()
        self.sign_in(1)

    def tearDown(self):
        self.conn.close()
        self.tmp.cleanup()

    def sign_in(self, uid, age=0):
        self.token, self.csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        stamp = int(time.time())
        self.conn.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?)',
                          (digest(self.token),uid,self.csrf,stamp,stamp,stamp-age))
        self.conn.commit()
        self.client.set_cookie('forever-local',self.token)

    def get(self,path,**kwargs):
        return self.client.get(path,base_url=BASE,buffered=True,**kwargs)

    def post(self,path,data=None,**kwargs):
        return self.client.post(path,base_url=BASE,data={'csrf':self.csrf,**(data or {})},**kwargs)

    def new_topic(self,title='Question sur Forever',body='Comment explorer ce nouveau monde ?'):
        response=self.post('/community/new',{'title':title,'body':body,'category':'1'})
        self.assertEqual(response.status_code,302,response.data)
        return int(response.location.rsplit('/',1)[1])

    def test_wiki_preservation(self):
        baseline=json.loads((ROOT/'tests/wiki-baseline.json').read_text())
        htmls=list((ROOT/'fr').rglob('*.html'))+list((ROOT/'en').rglob('*.html'))
        self.assertEqual(len(htmls),100)
        self.assertEqual({str(p.relative_to(ROOT)) for p in htmls},set(baseline['pages']))
        has_history=(ROOT/'.git').exists()
        for file in htmls:
            with self.subTest(path=file):
                key=str(file.relative_to(ROOT))
                if has_history:
                    original=subprocess.check_output(['git','show',f"{baseline['base_commit']}:{key}"],cwd=ROOT)
                    self.assertEqual(hashlib.sha256(original).hexdigest(),baseline['pages'][key])
                current=file.read_text().replace('\n<link rel="stylesheet" href="/assets/community.css">','')
                current=re.sub(r'<nav aria-label="(?:Communauté|Community \(FR\))"><div class="wrap actions">.*?</div></nav>\n','',current)
                self.assertEqual(hashlib.sha256(current.encode()).hexdigest(),baseline['pages'][key])

    def test_source_allowlist_and_pages(self):
        for file in [*ROOT.joinpath('fr').rglob('*.html'),*ROOT.joinpath('en').rglob('*.html')]:
            with self.subTest(path=file):
                self.assertEqual(self.get('/'+str(file.relative_to(ROOT))).status_code,200)
        for path in ['/community/app.py','/community/schema.sql','/instance/community.sqlite3','/.git/config','/.env',
                     '/requirements.txt','/install.sh','/assets/../community/app.py','/fr/../../community/app.py',
                     '/tests/wiki-baseline.json','/docs/REPORT.md','/deploy/wow4ever-staging.service','/qa/package.json']:
            self.assertEqual(self.get(path).status_code,404,path)
        self.assertEqual(self.get('/assets/community.css').status_code,200)

    def test_csrf_origin_and_host(self):
        self.assertEqual(self.client.post('/community/new',base_url=BASE,data={}).status_code,403)
        self.assertEqual(self.post('/community/new',{'csrf':'é'}).status_code,403)
        self.assertEqual(self.post('/community/new',headers={'Origin':'https://evil.test'}).status_code,403)
        self.assertEqual(self.client.get('/community/',base_url='http://evil.test').status_code,400)
        self.assertEqual(self.get('/auth/discord').status_code,404)
        self.assertEqual(self.get('/auth/logout').status_code,404)

    def test_oauth_pkce_one_use_and_rotation(self):
        old_token=self.token
        start=self.post('/auth/discord')
        self.assertEqual(start.status_code,302)
        args=parse_qs(urlsplit(start.location).query)
        self.assertEqual(args['scope'],['identify'])
        self.assertEqual(args['code_challenge_method'],['S256'])
        self.assertNotIn('client_secret',args)
        flow=self.conn.execute('SELECT * FROM oauth').fetchone()
        challenge=base64.urlsafe_b64encode(hashlib.sha256(flow['verifier'].encode()).digest()).rstrip(b'=').decode()
        self.assertEqual(args['code_challenge'],[challenge])
        token=Mock(); token.json.return_value={'access_token':'test-access','token_type':'Bearer','scope':'identify'}
        person=Mock(); person.json.return_value={'id':'999999','username':'New user','avatar':None,'email':'must-not-be-saved'}
        with patch('community.app.requests.post',side_effect=[token,Mock()]) as http_post, patch('community.app.requests.get',return_value=person):
            response=self.get('/auth/discord/callback?'+urlsplit(start.location).query+'&code=test-code&iss=https%3A%2F%2Fdiscord.com')
        self.assertEqual(response.status_code,302)
        self.assertEqual(http_post.call_args_list[0].kwargs['data']['code_verifier'],flow['verifier'])
        self.assertIn('/revoke',http_post.call_args_list[1].args[0])
        self.assertIsNone(self.conn.execute('SELECT * FROM sessions WHERE token=?',(digest(old_token),)).fetchone())
        new_cookie=self.client.get_cookie('forever-local').value
        self.assertNotEqual(new_cookie,old_token)
        self.assertEqual(self.get('/auth/discord/callback?state='+args['state'][0]+'&code=test-code').status_code,400)
        columns={r[1] for r in self.conn.execute('PRAGMA table_info(users)')}
        self.assertNotIn('email',columns)
        self.assertNotIn('access_token',columns)

    def test_oauth_wrong_browser_expiry_issuer_and_provider_error(self):
        for failure in ('wrong-state','wrong-session','expired','issuer','denied'):
            with self.subTest(failure=failure):
                start=self.post('/auth/discord')
                state=parse_qs(urlsplit(start.location).query)['state'][0]
                if failure=='wrong-state': state='bad'
                if failure=='wrong-session': self.sign_in(2)
                if failure=='expired':
                    self.conn.execute('UPDATE oauth SET expires=0'); self.conn.commit()
                suffix='&iss=https://evil.test' if failure=='issuer' else '&error=access_denied' if failure=='denied' else ''
                with patch('community.app.requests.post') as network:
                    r=self.get('/auth/discord/callback?state='+state+'&code=abc'+suffix)
                self.assertEqual(r.status_code,400)
                network.assert_not_called()

    def test_oauth_disabled_is_honest(self):
        self.app.config.update(DISCORD_CLIENT_ID='',DISCORD_CLIENT_SECRET='')
        self.client.delete_cookie('forever-local')
        response=self.get('/account/')
        self.assertIn('n’est pas configurée'.encode(),response.data)
        self.assertNotIn(b'Continuer avec Discord</button>',response.data)

    def test_full_discussion_interactions_and_notifications(self):
        tid=self.new_topic()
        self.sign_in(2)
        response=self.post(f'/community/topics/{tid}/reply',{'body':'Bienvenue @u-10001, explorons Forever !','quote':'1'})
        self.assertEqual(response.status_code,302)
        self.assertEqual(self.conn.execute('SELECT kind FROM notifications WHERE user_id=1').fetchone()[0],'mention')
        self.assertEqual(self.get(f'/community/topics/{tid}').status_code,200)
        self.assertEqual(self.post('/community/posts/1/react',{'kind':'helpful'}).status_code,302)
        self.assertIn(b'1 votes',self.get('/community/profiles/1').data)
        self.assertEqual(self.post('/community/posts/1/react',{'kind':'helpful'}).status_code,302)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM reactions').fetchone()[0],0)
        for action,table in [('follow','follows'),('favorite','favorites')]:
            self.assertEqual(self.post(f'/community/topics/{tid}/{action}').status_code,302)
            self.assertEqual(self.conn.execute(f'SELECT count(*) FROM {table} WHERE user_id=2').fetchone()[0],1)
        self.assertIn(b'Question sur Forever',self.get('/community/?filter=favorites').data)
        self.sign_in(1)
        self.assertEqual(self.post('/notifications/').status_code,302)
        self.assertEqual(self.conn.execute('SELECT seen FROM notifications WHERE user_id=1').fetchone()[0],1)

    def test_permission_boundaries_and_moderation(self):
        tid=self.new_topic()
        self.sign_in(2)
        self.assertEqual(self.post('/community/posts/1/edit',{'body':'Texte piraté'}).status_code,403)
        self.assertEqual(self.get('/moderation/').status_code,403)
        self.assertEqual(self.post('/moderation/topics/1',{'action':'hide'}).status_code,403)
        self.assertEqual(self.post('/community/posts/1/report',{'reason':'Ce contenu doit être examiné.'}).status_code,200)
        self.sign_in(3)
        self.assertEqual(self.get('/moderation/').status_code,200)
        self.assertEqual(self.post('/moderation/users/2',{'action':'admin'}).status_code,403)
        self.assertEqual(self.post('/moderation/categories',{'name':'Xx','description':''}).status_code,403)
        self.assertEqual(self.post('/moderation/topics/1',{'action':'lock'}).status_code,302)
        self.sign_in(1)
        self.assertEqual(self.post(f'/community/topics/{tid}/reply',{'body':'Impossible'}).status_code,403)
        self.assertEqual(self.post('/community/posts/1/edit',{'title':'Nouveau titre','body':'Modification bloquée'}).status_code,403)
        self.sign_in(3)
        self.post('/moderation/topics/1',{'action':'hide'})
        self.sign_in(2)
        for path in ['/community/topics/1','/community/posts/1','/community/posts/1/report']:
            self.assertEqual(self.get(path).status_code,404)
        self.assertNotIn(b'Question sur Forever',self.get('/community/?q=Forever').data)
        self.assertNotIn(b'Question sur Forever',self.get('/community/profiles/1').data)
        self.sign_in(3)
        self.assertEqual(self.post('/moderation/reports/1/resolve').status_code,302)
        self.assertEqual(self.post('/moderation/topics/1',{'action':'restore'}).status_code,302)
        self.assertGreater(self.conn.execute('SELECT count(*) FROM audit').fetchone()[0],0)

    def test_suspension_keeps_privacy_rights(self):
        self.sign_in(3)
        self.assertEqual(self.post('/moderation/users/1',{'action':'suspend'}).status_code,302)
        self.sign_in(1)
        self.assertEqual(self.get('/community/new').status_code,403)
        self.assertEqual(self.get('/account/').status_code,200)
        self.assertEqual(self.post('/account/export').status_code,200)
        self.assertEqual(self.post('/account/delete',{'confirm':'SUPPRIMER'}).status_code,200)

    def test_xss_sql_and_quote_boundaries(self):
        tid=self.new_topic(title='<script>alert(1)</script>',body='<img src=x onerror=alert(1)> @u-10002')
        response=self.get(f'/community/topics/{tid}')
        self.assertNotIn(b'<script>alert(1)</script>',response.data)
        self.assertIn(b'&lt;script&gt;',response.data)
        self.assertNotIn(b'<img src=x onerror=',response.data)
        self.assertEqual(self.get('/community/?q=%27%20OR%201%3D1--').status_code,200)
        self.assertEqual(self.get('/community/?category=1%20OR%201=1').status_code,400)
        second=self.new_topic(title='Un autre sujet Forever')
        self.assertEqual(self.post(f'/community/topics/{second}/reply',{'body':'citation impossible','quote':'1'}).status_code,400)
        self.assertEqual(self.post('/community/posts/1/react',{'kind':'helpful'}).status_code,400)
        self.assertEqual(self.get('/community/?q=%25').status_code,200)

    def test_export_deletion_and_private_history(self):
        self.new_topic(body='Message personnel à effacer intégralement.')
        self.post('/account/',{})
        self.sign_in(2)
        public=self.get('/community/profiles/1')
        self.assertNotIn(b'Question sur Forever',public.data)
        self.assertIn('masquer son historique'.encode(),public.data)
        self.post('/community/topics/1/reply',{'body':'Une citation','quote':'1'})
        self.post('/community/posts/1/react',{'kind':'helpful'})
        self.sign_in(1)
        response=self.post('/account/export')
        self.assertEqual(response.status_code,200)
        data=json.loads(response.data)
        self.assertEqual(data['profile']['discord_id'],'10001')
        self.assertEqual(len(data['posts']),1)
        self.assertNotIn('csrf',response.text)
        self.assertNotIn(self.token,response.text)
        self.assertEqual(self.post('/account/delete',{'confirm':'no'}).status_code,400)
        self.assertEqual(self.post('/account/delete',{'confirm':'SUPPRIMER'}).status_code,200)
        self.assertIsNone(self.conn.execute('SELECT id FROM users WHERE id=1').fetchone())
        self.assertEqual(self.conn.execute('SELECT body FROM posts WHERE id=1').fetchone()[0],'[Contribution supprimée]')
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions WHERE user_id=1').fetchone()[0],0)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM reactions').fetchone()[0],0)
        self.sign_in(3)
        self.assertNotIn('Message personnel à effacer'.encode(),self.get('/community/topics/1').data)

    def test_secure_cookies_headers_expiration_logout(self):
        self.app.config['PUBLIC_URL']='https://localhost:8000' # create separate app so closure uses HTTPS
        secure_app=create_app(dict(self.app.config))
        response=secure_app.test_client().get('/account/',base_url='https://localhost:8000')
        cookie=response.headers['Set-Cookie']
        for flag in ['__Host-forever','Secure','HttpOnly','SameSite=Lax','Path=/']:
            self.assertIn(flag,cookie)
        self.assertIn('max-age=',response.headers['Strict-Transport-Security'])
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])
        self.sign_in(1)
        self.conn.execute('UPDATE sessions SET seen=0 WHERE token=?',(digest(self.token),));self.conn.commit()
        self.assertEqual(self.get('/community/new').status_code,401)
        self.sign_in(1)
        self.assertEqual(self.post('/auth/logout').status_code,302)
        self.assertEqual(self.get('/community/new').status_code,401)

    def test_recent_auth_and_last_admin(self):
        self.sign_in(4)
        self.assertEqual(self.post('/account/delete',{'confirm':'SUPPRIMER'}).status_code,409)
        self.sign_in(4,age=601)
        self.assertEqual(self.post('/moderation/users/2',{'action':'admin'}).status_code,403)
        self.sign_in(4)
        self.assertEqual(self.post('/moderation/users/2',{'action':'admin'}).status_code,302)
        self.assertEqual(self.post('/account/delete',{'confirm':'SUPPRIMER'}).status_code,200)

    def test_category_hierarchy_and_cycle(self):
        self.sign_in(4)
        self.assertEqual(self.post('/moderation/categories',{'name':'Sous-salon','description':'Forever','parent':'1'}).status_code,302)
        self.assertEqual(self.post('/moderation/categories',{'id':'1','name':'Parent','parent':'1'}).status_code,400)
        self.assertEqual(self.post('/moderation/categories',{'id':'1','name':'Parent','parent':'2'}).status_code,400)
        self.assertEqual(self.post('/moderation/categories',{'name':'Troisième niveau','parent':'5'}).status_code,400)

    def test_rate_limit_shared_across_clients_and_purge(self):
        for i in range(5): self.new_topic(title=f'Question Forever {i}')
        self.assertEqual(self.post('/community/new',{'title':'Encore une question','body':'Message assez long','category':'1'}).status_code,429)
        self.conn.execute("UPDATE sessions SET seen=0")
        self.conn.execute('UPDATE rate_limits SET expires=0')
        self.conn.commit()
        result=self.runner.invoke(args=['purge'])
        self.assertEqual(result.exit_code,0,result.output)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0],0)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM rate_limits').fetchone()[0],0)

    def test_pagination_permalinks_and_no_content_loss(self):
        self.new_topic()
        stamp=int(time.time())
        self.conn.executemany('INSERT INTO posts(topic_id,author_id,body,created) VALUES(1,2,?,?)',
                              [(f'Réponse {i}',stamp) for i in range(25)])
        self.conn.commit()
        first=self.get('/community/topics/1')
        self.assertIn('Page suivante'.encode(),first.data)
        self.assertNotIn('Réponse 24'.encode(),first.data)
        self.assertIn('Réponse 24'.encode(),self.get('/community/topics/1?page=2').data)
        self.assertIn('page=2',self.get('/community/posts/26').location)
        self.assertEqual(self.get('/community/profiles/2').status_code,200)

    def test_backup_restore_and_idempotent_schema(self):
        self.new_topic()
        target=Path(self.tmp.name)/'backup.sqlite3'
        result=self.runner.invoke(args=['backup',str(target)])
        self.assertEqual(result.exit_code,0,result.output)
        self.assertEqual(target.stat().st_mode & 0o777,0o600)
        with sqlite3.connect(target) as restored:
            self.assertEqual(restored.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(restored.execute('PRAGMA foreign_key_check').fetchall(),[])
            self.assertEqual(restored.execute('SELECT title FROM topics').fetchone()[0],'Question sur Forever')
        self.assertNotEqual(self.runner.invoke(args=['backup',str(target)]).exit_code,0)
        self.assertEqual(self.runner.invoke(args=['init-db']).exit_code,0)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM categories').fetchone()[0],4)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM topics').fetchone()[0],1)

    def test_atomic_edit_and_hidden_quotes(self):
        self.new_topic(body='Texte initial qui doit rester intact.')
        r=self.post('/community/posts/1/edit',{'title':'x','body':'Cette modification doit être annulée.'})
        self.assertEqual(r.status_code,400)
        self.assertEqual(self.conn.execute('SELECT body FROM posts WHERE id=1').fetchone()[0],'Texte initial qui doit rester intact.')
        self.sign_in(2)
        self.post('/community/topics/1/reply',{'body':'Réponse citée @u-10001','quote':'1'})
        self.sign_in(3)
        self.post('/moderation/posts/1',{'action':'hide'})
        self.sign_in(2)
        self.assertNotIn('Texte initial'.encode(),self.get('/community/topics/1').data)
        self.assertEqual(self.get('/community/posts/1').status_code,404)

    def test_provider_failure_does_not_authenticate(self):
        start=self.post('/auth/discord')
        state=parse_qs(urlsplit(start.location).query)['state'][0]
        response=Mock();response.json.return_value={'access_token':'test-access','token_type':'Bearer','scope':'identify email'}
        with patch('community.app.requests.post',side_effect=[response,Mock()]),patch('community.app.requests.get') as identity:
            result=self.get('/auth/discord/callback?state='+state+'&code=test')
        self.assertEqual(result.status_code,502)
        identity.assert_not_called()
        self.assertEqual(self.conn.execute('SELECT count(*) FROM users').fetchone()[0],4)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM oauth').fetchone()[0],0)

    def test_retention_actual_cutoffs(self):
        self.new_topic()
        stamp=int(time.time())
        day=86400
        self.conn.execute('INSERT INTO notifications(user_id,actor_id,topic_id,post_id,kind,created) VALUES(2,1,1,1,?,?)',('reply',stamp-91*day))
        self.conn.execute('INSERT INTO notifications(user_id,actor_id,topic_id,post_id,kind,created) VALUES(2,1,1,1,?,?)',('reply',stamp))
        self.conn.execute("INSERT INTO reports(reporter_id,post_id,reason,status,created,resolved) VALUES(2,1,'ancien','resolved',?,?)",(stamp-200*day,stamp-181*day))
        self.conn.execute("INSERT INTO reports(reporter_id,post_id,reason,created) VALUES(2,1,'ouvert',?)",(stamp-200*day,))
        self.conn.execute("INSERT INTO audit(action,target,created) VALUES('test','1',?)",(stamp-181*day,))
        self.conn.execute('INSERT INTO oauth VALUES(?,?,?,?)',(digest('state'),digest(self.token),'verifier',stamp-1))
        self.conn.commit()
        self.assertEqual(self.runner.invoke(args=['purge']).exit_code,0)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM notifications').fetchone()[0],1)
        self.assertEqual(self.conn.execute('SELECT status FROM reports').fetchone()[0],'open')
        self.assertEqual(self.conn.execute('SELECT count(*) FROM audit').fetchone()[0],0)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM oauth').fetchone()[0],0)

    def test_anonymous_reads_allocate_no_database_sessions(self):
        count=self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0]
        for _ in range(70):
            client=self.app.test_client()
            for path in ['/community/','/privacy/','/account/']:
                response=client.get(path,base_url=BASE)
                self.assertEqual(response.status_code,200)
                self.assertFalse(any(header.startswith('forever-local=') for header in response.headers.getlist('Set-Cookie')))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0],count)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM rate_limits').fetchone()[0],0)

    def test_anonymous_login_csrf_and_lazy_session(self):
        client=self.app.test_client()
        form=client.get('/account/',base_url=BASE)
        self.assertIn("form-action 'self' https://discord.com/oauth2/authorize",form.headers['Content-Security-Policy'])
        self.assertNotIn('https://discord.com',client.get('/community/',base_url=BASE).headers['Content-Security-Policy'])
        csrf=re.search(r'name="csrf" value="([^"]+)"',form.text).group(1)
        before=self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0]
        bad=client.post('/auth/discord',base_url=BASE,data={'csrf':csrf+'tampered'})
        self.assertEqual(bad.status_code,403)
        other=self.app.test_client()
        self.assertEqual(other.post('/auth/discord',base_url=BASE,data={'csrf':csrf}).status_code,403)
        with patch('itsdangerous.timed.time.time',return_value=time.time()+601):
            self.assertEqual(client.post('/auth/discord',base_url=BASE,data={'csrf':csrf}).status_code,403)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0],before)
        result=client.post('/auth/discord',base_url=BASE,data={'csrf':csrf},headers={'Origin':BASE})
        self.assertEqual(result.status_code,302)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0],before+1)
        self.assertIsNotNone(client.get_cookie('forever-local'))
        self.assertIsNone(client.get_cookie('forever-csrf-local'))
        self.assertEqual(other.get('/auth/discord/callback?state=missing&code=x',base_url=BASE).status_code,400)

    def test_trusted_proxy_uses_distinct_clients_only(self):
        app=create_app({**self.app.config,'TRUSTED_PROXY_IPS':'127.0.0.1,::1'})
        for i in range(12):
            client=app.test_client()
            headers={'X-Forwarded-For':f'203.0.113.250, 198.51.100.{i+1}',
                     'X-Forwarded-Host':'evil.test','X-Forwarded-Proto':'https'}
            response=client.get('/account/',base_url=BASE,headers=headers)
            self.assertEqual(response.status_code,200)
            self.assertNotIn('Secure',response.headers['Set-Cookie'])
            csrf=re.search(r'name="csrf" value="([^"]+)"',response.text).group(1)
            result=client.post('/auth/discord',base_url=BASE,data={'csrf':csrf},headers=headers)
            self.assertEqual(result.status_code,302)
        invalid=app.test_client().get('/account/',base_url=BASE,headers={'X-Forwarded-For':'invalid'})
        self.assertEqual(invalid.status_code,400)
        with self.assertRaises(RuntimeError):
            create_app({**self.app.config,'TRUSTED_PROXY_IPS':'0.0.0.0/0'})

    def test_untrusted_forwarded_header_cannot_reset_budgets(self):
        for i in range(12):
            client=self.app.test_client()
            headers={'X-Forwarded-For':f'198.51.100.{i+1}'}
            peer={'REMOTE_ADDR':'203.0.113.50'}
            response=client.get('/account/',base_url=BASE,headers=headers,environ_overrides=peer)
            csrf=re.search(r'name="csrf" value="([^"]+)"',response.text).group(1)
            result=client.post('/auth/discord',base_url=BASE,data={'csrf':csrf},headers=headers,environ_overrides=peer)
            self.assertEqual(result.status_code,302 if i<10 else 429)

    def test_session_activity_writes_are_coalesced(self):
        seen=int(time.time())-30
        self.conn.execute('UPDATE sessions SET seen=? WHERE token=?',(seen,digest(self.token)))
        self.conn.commit()
        self.get('/community/')
        self.assertEqual(self.conn.execute('SELECT seen FROM sessions WHERE token=?',(digest(self.token),)).fetchone()[0],seen)
        self.conn.execute('UPDATE sessions SET seen=? WHERE token=?',(seen-90,digest(self.token)))
        self.conn.commit()
        self.get('/community/')
        self.assertGreater(self.conn.execute('SELECT seen FROM sessions WHERE token=?',(digest(self.token),)).fetchone()[0],seen)

    def test_typed_audit_targets_survive_account_erasure(self):
        self.new_topic()
        stamp=int(time.time())
        for actor,action,target in [(3,'post.hide','post:1'),(3,'topic.lock','topic:1'),(3,'category.save','category:1'),
                                    (3,'report.resolve','report:1'),(3,'user.suspend','user:1'),(1,'post.edit','post:2')]:
            self.conn.execute('INSERT INTO audit(actor_id,action,target,created) VALUES(?,?,?,?)',(actor,action,target,stamp))
        self.conn.commit()
        self.assertEqual(self.post('/account/delete',{'confirm':'SUPPRIMER'}).status_code,200)
        rows={r['action']:r for r in self.conn.execute('SELECT * FROM audit')}
        for action in ['post.hide','topic.lock','category.save','report.resolve']:
            self.assertTrue(rows[action]['target'].endswith(':1'))
            self.assertEqual(rows[action]['actor_id'],3)
        self.assertEqual(rows['user.suspend']['target'],'user:[effacé]')
        self.assertEqual(rows['user.suspend']['actor_id'],3)
        self.assertEqual(rows['post.edit']['target'],'post:2')
        self.assertIsNone(rows['post.edit']['actor_id'])

    def test_audit_migration_preserves_legacy_entity_meanings(self):
        self.conn.execute('DELETE FROM migrations WHERE version=2')
        for action in ['post.edit','topic.lock','category.save','report.create','report.resolve','user.suspend','operator.role.admin']:
            self.conn.execute('INSERT INTO audit(action,target,created) VALUES(?,?,?)',(action,'2',int(time.time())))
        self.conn.commit()
        self.assertEqual(self.runner.invoke(args=['init-db']).exit_code,0)
        targets={r['action']:r['target'] for r in self.conn.execute('SELECT * FROM audit')}
        self.assertEqual(targets,{'post.edit':'post:2','topic.lock':'topic:2','category.save':'category:2',
                                  'report.create':'post:2','report.resolve':'report:2','user.suspend':'user:2','operator.role.admin':'user:2'})
        self.assertEqual(self.runner.invoke(args=['init-db']).exit_code,0)
        self.assertEqual(targets,{r['action']:r['target'] for r in self.conn.execute('SELECT * FROM audit')})

    def test_local_backup_rotation_and_private_permissions(self):
        directory=Path(self.tmp.name)/'snapshots'
        directory.mkdir(mode=0o700)
        stale=directory/'community-20200101T000000Z-12345678.sqlite3'
        stale.write_text('stale')
        os.utime(stale,(0,0))
        unrelated=directory/'personal-notes.txt'
        unrelated.write_text('keep')
        link=directory/'community-20200102T000000Z-12345678.sqlite3'
        link.symlink_to(unrelated)
        result=self.runner.invoke(args=['backup-daily',str(directory)])
        self.assertEqual(result.exit_code,0,result.output)
        self.assertFalse(stale.exists())
        self.assertTrue(link.is_symlink())
        self.assertEqual(unrelated.read_text(),'keep')
        snapshots=[p for p in directory.glob('*.sqlite3') if not p.is_symlink()]
        self.assertEqual(len(snapshots),1)
        self.assertEqual(snapshots[0].stat().st_mode & 0o777,0o600)
        with sqlite3.connect(snapshots[0]) as restored:
            self.assertEqual(restored.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(restored.execute('PRAGMA foreign_key_check').fetchall(),[])
        directory.chmod(0o755)
        self.assertNotEqual(self.runner.invoke(args=['backup-daily',str(directory)]).exit_code,0)

    def test_historical_installer_is_inert_and_disclaimer_exact(self):
        result=subprocess.run(['sh',str(ROOT/'install.sh')],cwd=self.tmp.name,capture_output=True,text=True)
        self.assertEqual(result.returncode,1)
        self.assertIn('désactivé',result.stderr)
        for forbidden in ['rm -rf','systemctl','/etc/caddy','git clone','git pull']:
            self.assertNotIn(forbidden,(ROOT/'install.sh').read_text())
        self.assertIn('Site indépendant et non officiel de Blizzard Entertainment.',self.get('/community/').text)


if __name__=='__main__':
    unittest.main()
