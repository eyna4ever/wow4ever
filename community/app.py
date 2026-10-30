import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
from urllib.parse import urlencode, urlsplit

import click
import requests
from itsdangerous import BadSignature, URLSafeTimedSerializer
from flask import (Flask, abort, g, make_response, redirect, render_template,
                   request, send_from_directory, url_for)
from werkzeug.exceptions import HTTPException

from community.proxy import trusted_client_ip

ROOT = Path(__file__).resolve().parent.parent
DAY = 86400


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def create_app(test_config=None):
    app = Flask(__name__, static_folder=None)
    app.config.from_mapping(
        DATABASE=os.getenv('DATABASE', str(ROOT / 'instance/community.sqlite3')),
        SECRET_KEY=os.getenv('SECRET_KEY'),
        PUBLIC_URL=os.getenv('PUBLIC_URL', 'http://localhost:8000').rstrip('/'),
        DISCORD_CLIENT_ID=os.getenv('DISCORD_CLIENT_ID', ''),
        DISCORD_CLIENT_SECRET=os.getenv('DISCORD_CLIENT_SECRET', ''),
        PRIVACY_CONTACT=os.getenv('PRIVACY_CONTACT', ''),
        CONTROLLER_NAME=os.getenv('CONTROLLER_NAME', ''),
        TRUSTED_PROXY_IPS=os.getenv('TRUSTED_PROXY_IPS', ''),
        MAX_CONTENT_LENGTH=32768,
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY'] or len(app.config['SECRET_KEY']) < 32:
        raise RuntimeError('SECRET_KEY requis (au moins 32 caractères aléatoires).')
    origin = urlsplit(app.config['PUBLIC_URL'])
    if origin.scheme not in ('http', 'https') or not origin.hostname or origin.path or origin.query or origin.fragment or origin.username:
        raise RuntimeError('PUBLIC_URL doit être une origine sans chemin.')
    if origin.scheme != 'https' and origin.hostname not in ('localhost', '127.0.0.1'):
        raise RuntimeError('HTTPS requis hors localhost.')
    secure = origin.scheme == 'https'
    cookie_name = '__Host-forever' if secure else 'forever-local'
    csrf_cookie_name = '__Host-forever-csrf' if secure else 'forever-csrf-local'
    anonymous_csrf = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='forever-login-csrf-v1')
    app.wsgi_app = trusted_client_ip(app.wsgi_app, app.config['TRUSTED_PROXY_IPS'])

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
            g.db.row_factory = sqlite3.Row
            g.db.execute('PRAGMA foreign_keys=ON')
            g.db.execute('PRAGMA secure_delete=ON')
            g.db.execute('PRAGMA busy_timeout=10000')
        return g.db

    def query(sql, args=(), one=False):
        rows = db().execute(sql, args)
        return rows.fetchone() if one else rows.fetchall()

    def audit(action, target):
        if not re.fullmatch(r'(user|post|topic|report|category):\d+', target):
            raise ValueError('Audit targets must include their entity type.')
        db().execute('INSERT INTO audit(actor_id,action,target,created) VALUES(?,?,?,?)',
                     (g.user['id'] if g.user else None, action, str(target), now()))

    def now():
        return int(time.time())

    def staff():
        return bool(g.user and g.user['role'] in ('moderator', 'admin'))

    def require_user(role=None, recent=False):
        if not g.user:
            abort(401, 'Connectez-vous avec Discord pour continuer.')
        if g.user['suspended']:
            abort(403, 'Votre compte est suspendu. Les paramètres et droits RGPD restent accessibles.')
        if role == 'staff' and not staff() or role == 'admin' and g.user['role'] != 'admin':
            abort(403, 'Permission insuffisante.')
        if recent and now() - (g.session['authenticated'] or 0) > 600:
            abort(403, 'Reconnectez-vous avec Discord avant cette action sensible (10 minutes).')

    def limit(action, maximum, period, user=False):
        identity = str(g.user['id']) if user and g.user else request.remote_addr or 'unknown'
        key = hmac.new(app.config['SECRET_KEY'].encode(), f'{action}:{identity}:{now()//period}'.encode(), hashlib.sha256).hexdigest()
        row = db().execute('INSERT INTO rate_limits VALUES(?,1,?) ON CONFLICT(bucket) DO UPDATE SET count=count+1 RETURNING count',
                           (key, now()+period)).fetchone()
        # Commit before refusing so rejected attempts remain counted across workers.
        db().commit()
        if row['count'] > maximum:
            abort(429, 'Trop de demandes. Réessayez dans quelques instants.')

    def field(name, minimum=1, maximum=10000):
        value = request.form.get(name, '').strip()
        if not minimum <= len(value) <= maximum or '\x00' in value:
            abort(400, f'Champ {name} : entre {minimum} et {maximum} caractères.')
        return value

    def integer(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            abort(400, 'Identifiant invalide.')

    def page():
        return max(1, min(integer(request.args.get('page', 1)), 10000))

    def topic_row(topic_id):
        row = query('SELECT t.*,c.name category FROM topics t JOIN categories c ON c.id=t.category_id WHERE t.id=?', (topic_id,), True)
        if not row or row['hidden'] and not staff():
            abort(404)
        return row

    def post_row(post_id):
        row = query('SELECT * FROM posts WHERE id=?', (post_id,), True)
        if not row:
            abort(404)
        topic = topic_row(row['topic_id'])
        if row['hidden'] and not staff():
            abort(404)
        return row, topic

    def notify(topic_id, post_id, body):
        recipients = {r['user_id']: 'reply' for r in query('SELECT user_id FROM follows WHERE topic_id=?', (topic_id,))}
        for handle in set(re.findall(r'(?<![\w@])@([a-z0-9-]{2,64})', body.lower())):
            person = query('SELECT id FROM users WHERE handle=?', (handle,), True)
            if person:
                recipients[person['id']] = 'mention'
        for uid, kind in recipients.items():
            if uid != g.user['id'] and query('SELECT id FROM users WHERE id=? AND notify=1 AND suspended=0', (uid,), True):
                db().execute('INSERT INTO notifications(user_id,actor_id,topic_id,post_id,kind,created) VALUES(?,?,?,?,?,?)',
                             (uid, g.user['id'], topic_id, post_id, kind, now()))

    @app.teardown_appcontext
    def close_db(error=None):
        conn = g.pop('db', None)
        if conn:
            conn.close()  # Uncommitted failed requests roll back.

    def create_login_session():
        """Allocate server state only after a valid, rate-limited login POST."""
        if g.session:
            return
        limit('session-new', 60, 600)
        token = secrets.token_urlsafe(32)
        db().execute('INSERT INTO sessions VALUES(?,NULL,?,?,?,NULL)',
                     (digest(token), secrets.token_urlsafe(32), now(), now()))
        g.session = query('SELECT * FROM sessions WHERE token=?', (digest(token),), True)
        g.new_cookie = token
        g.clear_anonymous_csrf = True
        db().commit()

    @app.before_request
    def security():
        g.user = None
        g.session = None
        g.new_cookie = None
        g.anonymous_csrf = ''
        g.clear_anonymous_csrf = False
        if request.host != origin.netloc:
            abort(400, 'Hôte non autorisé.')
        if request.endpoint == 'wiki' or request.endpoint == 'health':
            return
        if request.endpoint is None:
            return
        token = request.cookies.get(cookie_name, '')
        if len(token) <= 128 and token:
            g.session = query('SELECT * FROM sessions WHERE token=? AND seen>? AND created>?',
                              (digest(token), now()-3600, now()-DAY), True)
        if g.session:
            if now()-g.session['seen'] >= 60:
                db().execute('UPDATE sessions SET seen=? WHERE token=?', (now(), g.session['token']))
                db().commit()
            if g.session['user_id']:
                g.user = query('SELECT * FROM users WHERE id=?', (g.session['user_id'],), True)
        if request.endpoint == 'callback' and not g.session:
            abort(400, 'La session de connexion Discord est absente ou expirée.')
        if request.endpoint == 'account' and request.method == 'GET' and not g.session and app.config['DISCORD_CLIENT_ID'] and app.config['DISCORD_CLIENT_SECRET']:
            existing = request.cookies.get(csrf_cookie_name, '')
            try:
                if len(existing) > 256 or not existing:
                    raise BadSignature('Missing CSRF token')
                anonymous_csrf.loads(existing, max_age=600)
                g.anonymous_csrf = existing
            except BadSignature:
                # Signed, expiring double-submit token; no SQLite session for a GET.
                g.anonymous_csrf = anonymous_csrf.dumps(secrets.token_urlsafe(32))
        if request.method == 'POST':
            if request.headers.get('Origin') not in (None, app.config['PUBLIC_URL']):
                abort(403, 'Origine de la demande refusée.')
            csrf = request.form.get('csrf', '')
            if g.session:
                if not hmac.compare_digest(csrf.encode(), g.session['csrf'].encode()):
                    abort(403, 'Formulaire expiré ou protection CSRF invalide.')
            else:
                cookie = request.cookies.get(csrf_cookie_name, '')
                if request.endpoint != 'login' or not cookie or len(cookie)>256 or not hmac.compare_digest(csrf.encode(),cookie.encode()):
                    abort(403, 'Formulaire expiré ou protection CSRF invalide.')
                try:
                    anonymous_csrf.loads(cookie, max_age=600)
                except BadSignature:
                    abort(403, 'Formulaire de connexion expiré ou invalide.')
            limit('write-ip', 120, 600)

    @app.after_request
    def headers(response):
        form_action = "'self' https://discord.com/oauth2/authorize" if request.endpoint in ('account','login') else "'self'"
        response.headers.update({
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'no-referrer' if request.endpoint == 'callback' else 'same-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action " + form_action,
        })
        if secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        if request.endpoint != 'wiki':
            response.headers['Cache-Control'] = 'no-store'
            response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        if getattr(g, 'new_cookie', None):
            response.set_cookie(cookie_name, g.new_cookie, secure=secure, httponly=True, samesite='Lax', path='/')
        if getattr(g, 'anonymous_csrf', ''):
            response.set_cookie(csrf_cookie_name, g.anonymous_csrf, max_age=600, secure=secure, httponly=True, samesite='Lax', path='/')
        if getattr(g, 'clear_anonymous_csrf', False):
            response.delete_cookie(csrf_cookie_name, path='/', secure=secure, httponly=True, samesite='Lax')
        return response

    @app.context_processor
    def context():
        unread = query('SELECT count(*) n FROM notifications n JOIN topics t ON t.id=n.topic_id JOIN posts p ON p.id=n.post_id WHERE n.user_id=? AND n.seen=0 AND t.hidden=0 AND p.hidden=0', (g.user['id'],), True)['n'] if g.user else 0
        return dict(user=g.user, csrf=g.session['csrf'] if g.session else getattr(g,'anonymous_csrf',''), staff=staff(),
                    oauth_enabled=bool(app.config['DISCORD_CLIENT_ID'] and app.config['DISCORD_CLIENT_SECRET']),
                    unread=unread, contact=app.config['PRIVACY_CONTACT'], controller=app.config['CONTROLLER_NAME'])

    @app.template_filter('date')
    def date(value):
        return time.strftime('%d/%m/%Y %H:%M UTC', time.gmtime(value)) if value else '—'

    @app.errorhandler(HTTPException)
    def error(exc):
        response = make_response(render_template('error.html', error=exc), exc.code)
        if exc.code == 429:
            response.headers['Retry-After'] = '600'
        return response

    @app.get('/healthz')
    def health():
        return {'status': 'ok', 'schema': query('SELECT max(version) v FROM migrations', one=True)['v']}

    @app.post('/auth/discord')
    def login():
        if not app.config['DISCORD_CLIENT_ID'] or not app.config['DISCORD_CLIENT_SECRET']:
            abort(503, 'Connexion Discord non configurée sur cet environnement.')
        limit('oauth', 10, 600)
        create_login_session()
        state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
        db().execute('DELETE FROM oauth WHERE session_token=? OR expires<?', (g.session['token'], now()))
        db().execute('INSERT INTO oauth VALUES(?,?,?,?)', (digest(state), g.session['token'], verifier, now()+600))
        db().commit()
        return redirect('https://discord.com/oauth2/authorize?' + urlencode(dict(
            client_id=app.config['DISCORD_CLIENT_ID'], response_type='code',
            redirect_uri=app.config['PUBLIC_URL']+'/auth/discord/callback', scope='identify',
            state=state, code_challenge=challenge, code_challenge_method='S256')))

    @app.get('/auth/discord/callback')
    def callback():
        limit('oauth-callback', 20, 600)
        state = request.args.get('state', '')
        if len(state) > 128:
            abort(400)
        flow = db().execute('DELETE FROM oauth WHERE state=? AND session_token=? AND expires>? RETURNING verifier',
                            (digest(state), g.session['token'], now())).fetchone()
        db().commit()
        if not flow or request.args.get('error') or not request.args.get('code'):
            abort(400, 'Autorisation Discord expirée, refusée ou déjà utilisée.')
        if request.args.get('iss', 'https://discord.com') != 'https://discord.com':
            abort(400, 'Émetteur OAuth invalide.')
        access_token = None
        try:
            response = requests.post('https://discord.com/api/oauth2/token', data={
                'grant_type': 'authorization_code', 'code': request.args['code'],
                'redirect_uri': app.config['PUBLIC_URL']+'/auth/discord/callback',
                'client_id': app.config['DISCORD_CLIENT_ID'], 'client_secret': app.config['DISCORD_CLIENT_SECRET'],
                'code_verifier': flow['verifier'],
            }, timeout=10, allow_redirects=False)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data['access_token']
            if token_data.get('token_type', '').lower() != 'bearer' or set(token_data.get('scope', '').split()) != {'identify'}:
                raise ValueError('Invalid token scope/type')
            response = requests.get('https://discord.com/api/v10/users/@me',
                                    headers={'Authorization': 'Bearer '+access_token}, timeout=10, allow_redirects=False)
            response.raise_for_status()
            person = response.json()
            if not re.fullmatch(r'\d{5,25}', str(person['id'])):
                raise ValueError('Invalid Discord ID')
            name = str(person.get('global_name') or person['username'])[:80]
            avatar = person.get('avatar')
            if avatar and not re.fullmatch(r'(a_)?[a-f0-9]{32}', avatar):
                avatar = None
        except (requests.RequestException, KeyError, ValueError, TypeError):
            abort(502, 'Discord est indisponible ou a retourné une réponse invalide. Réessayez la connexion.')
        finally:
            # No Discord access/refresh token is retained. Revoke immediately after identification.
            if access_token:
                try:
                    revoked = requests.post('https://discord.com/api/oauth2/token/revoke', data={
                        'token': access_token, 'client_id': app.config['DISCORD_CLIENT_ID'],
                        'client_secret': app.config['DISCORD_CLIENT_SECRET'],
                    }, timeout=10, allow_redirects=False)
                    revoked.raise_for_status()
                except requests.RequestException:
                    app.logger.warning('Discord token revocation failed; no token stored locally')
        existing = query('SELECT * FROM users WHERE discord_id=?', (person['id'],), True)
        if existing:
            uid = existing['id']
            db().execute('UPDATE users SET name=?,avatar=?,last_login=? WHERE id=?', (name, avatar, now(), uid))
        else:
            uid = db().execute('INSERT INTO users(discord_id,name,handle,avatar,created,last_login) VALUES(?,?,?,?,?,?)',
                (str(person['id']), name, 'u-'+secrets.token_hex(8), avatar, now(), now())).lastrowid
        db().execute('DELETE FROM sessions WHERE token=?', (g.session['token'],))
        token = secrets.token_urlsafe(32)
        db().execute('INSERT INTO sessions VALUES(?,?,?,?,?,?)',
                     (digest(token), uid, secrets.token_urlsafe(32), now(), now(), now()))
        db().commit()
        g.new_cookie = token
        return redirect(url_for('account'))

    @app.post('/auth/logout')
    def logout():
        db().execute('DELETE FROM sessions WHERE token=?', (g.session['token'],))
        db().commit()
        g.new_cookie = None
        response = redirect(url_for('forum'))
        response.delete_cookie(cookie_name, path='/', secure=secure, httponly=True, samesite='Lax')
        return response

    @app.get('/community/')
    def forum():
        p, q = page(), request.args.get('q', '').strip()[:100]
        selected = request.args.get('category', '')
        mode = request.args.get('filter', '')
        conditions, args = ['t.hidden=0'], []
        if selected:
            conditions.append('(t.category_id=? OR c.parent_id=?)')
            args.extend([integer(selected), integer(selected)])
        if q:
            conditions.append("(t.title LIKE ? ESCAPE '\\' OR EXISTS(SELECT 1 FROM posts p WHERE p.topic_id=t.id AND p.hidden=0 AND p.body LIKE ? ESCAPE '\\'))")
            term = '%'+q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')+'%'
            args.extend([term, term])
        if mode in ('followed', 'favorites'):
            require_user()
            table = 'follows' if mode == 'followed' else 'favorites'
            conditions.append(f'EXISTS(SELECT 1 FROM {table} x WHERE x.topic_id=t.id AND x.user_id=?)')
            args.append(g.user['id'])
        where = ' AND '.join(conditions)
        topics = query(f'''SELECT t.*,c.name category,u.name author,
            (SELECT count(*) FROM posts p WHERE p.topic_id=t.id AND p.hidden=0) posts
            FROM topics t JOIN categories c ON c.id=t.category_id LEFT JOIN users u ON u.id=t.author_id
            WHERE {where} ORDER BY t.updated DESC,t.id DESC LIMIT 21 OFFSET ?''', (*args, (p-1)*20))
        categories = query('SELECT c.*,p.name parent FROM categories c LEFT JOIN categories p ON p.id=c.parent_id ORDER BY coalesce(c.parent_id,c.id),c.parent_id IS NOT NULL,c.position,c.id')
        return render_template('forum.html', topics=topics[:20], more=len(topics)>20, categories=categories,
                               q=q, selected=selected, mode=mode, page=p)

    @app.route('/community/new', methods=['GET', 'POST'])
    def new_topic():
        require_user()
        if request.method == 'POST':
            title, body = field('title', 5, 150), field('body', 10, 10000)
            category_id = integer(request.form.get('category'))
            if not query('SELECT id FROM categories WHERE id=?', (category_id,), True):
                abort(400, 'Catégorie inconnue.')
            limit('topic-user', 5, 600, True)
            tid = db().execute('INSERT INTO topics(category_id,author_id,title,created,updated) VALUES(?,?,?,?,?)',
                               (category_id, g.user['id'], title, now(), now())).lastrowid
            pid = db().execute('INSERT INTO posts(topic_id,author_id,body,created) VALUES(?,?,?,?)', (tid,g.user['id'],body,now())).lastrowid
            db().execute('INSERT INTO follows VALUES(?,?)', (g.user['id'],tid))
            notify(tid, pid, body)
            db().commit()
            return redirect(url_for('topic', topic_id=tid))
        return render_template('compose.html', categories=query('SELECT * FROM categories ORDER BY position,id'), topic=None, post=None)

    @app.get('/community/topics/<int:topic_id>')
    def topic(topic_id):
        row, p = topic_row(topic_id), page()
        posts = query('''SELECT p.*,u.name,u.handle,u.id uid,
            CASE WHEN q.hidden=0 THEN q.body ELSE NULL END quote_body,
            CASE WHEN q.hidden=0 THEN qu.name ELSE NULL END quote_author,
            (SELECT count(*) FROM reactions r WHERE r.post_id=p.id AND r.kind='helpful') helpful,
            (SELECT count(*) FROM reactions r WHERE r.post_id=p.id AND r.kind='thanks') thanks
            FROM posts p LEFT JOIN users u ON u.id=p.author_id
            LEFT JOIN posts q ON q.id=p.quote_id LEFT JOIN users qu ON qu.id=q.author_id
            WHERE p.topic_id=? AND (p.hidden=0 OR ?=1) ORDER BY p.id LIMIT 21 OFFSET ?''', (topic_id, int(staff()), (p-1)*20))
        follows = bool(g.user and query('SELECT 1 FROM follows WHERE user_id=? AND topic_id=?', (g.user['id'],topic_id), True))
        favorite = bool(g.user and query('SELECT 1 FROM favorites WHERE user_id=? AND topic_id=?', (g.user['id'],topic_id), True))
        quote = None
        if request.args.get('quote'):
            quote, _ = post_row(integer(request.args['quote']))
            if quote['topic_id'] != topic_id or quote['hidden']:
                abort(400)
        return render_template('topic.html', topic=row, posts=posts[:20], more=len(posts)>20, page=p,
                               follows=follows, favorite=favorite, quote=quote)

    @app.post('/community/topics/<int:topic_id>/reply')
    def reply(topic_id):
        require_user()
        row = topic_row(topic_id)
        if row['locked'] or row['hidden']:
            abort(403, 'Cette discussion est fermée.')
        body = field('body', 2, 10000)
        quote_id = integer(request.form['quote']) if request.form.get('quote') else None
        if quote_id:
            quoted, _ = post_row(quote_id)
            if quoted['topic_id'] != topic_id or quoted['hidden']:
                abort(400, 'Citation invalide.')
        limit('post-user', 10, 60, True)
        pid = db().execute('INSERT INTO posts(topic_id,author_id,body,quote_id,created) VALUES(?,?,?,?,?)',
                           (topic_id,g.user['id'],body,quote_id,now())).lastrowid
        db().execute('UPDATE topics SET updated=? WHERE id=?', (now(),topic_id))
        notify(topic_id,pid,body)
        db().commit()
        count = query('SELECT count(*) n FROM posts WHERE topic_id=? AND id<=? AND hidden=0', (topic_id,pid), True)['n']
        return redirect(url_for('topic',topic_id=topic_id,page=(count-1)//20+1)+f'#post-{pid}')

    @app.route('/community/posts/<int:post_id>/edit', methods=['GET','POST'])
    def edit(post_id):
        require_user()
        post, row = post_row(post_id)
        if post['author_id'] != g.user['id'] and not staff():
            abort(403)
        if (row['locked'] or row['hidden'] or post['hidden']) and not staff():
            abort(403, 'Discussion verrouillée ou contenu masqué.')
        first = query('SELECT min(id) id FROM posts WHERE topic_id=?', (row['id'],), True)['id'] == post_id
        if request.method == 'POST':
            body = field('body', 2, 10000)
            limit('edit-user', 20, 600, True)
            db().execute('UPDATE posts SET body=?,edited=? WHERE id=?', (body,now(),post_id))
            if first:
                db().execute('UPDATE topics SET title=? WHERE id=?', (field('title',5,150),row['id']))
            audit('post.edit', f'post:{post_id}')
            db().commit()
            return redirect(url_for('topic',topic_id=row['id']))
        return render_template('compose.html',post=post,topic=row,first=first)

    @app.post('/community/topics/<int:topic_id>/<action>')
    def toggle_topic(topic_id, action):
        require_user()
        row = topic_row(topic_id)
        if row['hidden']:
            abort(403)
        if action not in ('follow','favorite'):
            abort(404)
        table = 'follows' if action == 'follow' else 'favorites'
        args = (g.user['id'],topic_id)
        if query(f'SELECT 1 FROM {table} WHERE user_id=? AND topic_id=?',args,True):
            db().execute(f'DELETE FROM {table} WHERE user_id=? AND topic_id=?',args)
        else:
            db().execute(f'INSERT INTO {table} VALUES(?,?)',args)
        db().commit()
        return redirect(url_for('topic',topic_id=topic_id))

    @app.post('/community/posts/<int:post_id>/react')
    def react(post_id):
        require_user()
        post, row = post_row(post_id)
        kind = request.form.get('kind')
        if kind not in ('helpful','thanks') or post['author_id'] == g.user['id'] or post['hidden'] or row['hidden']:
            abort(400, 'Réaction invalide.')
        limit('reaction-user', 30, 60, True)
        args = (g.user['id'],post_id,kind)
        if query('SELECT 1 FROM reactions WHERE user_id=? AND post_id=? AND kind=?',args,True):
            db().execute('DELETE FROM reactions WHERE user_id=? AND post_id=? AND kind=?',args)
        else:
            db().execute('INSERT INTO reactions VALUES(?,?,?)',args)
        db().commit()
        return redirect(url_for('topic',topic_id=row['id']))

    @app.get('/community/posts/<int:post_id>')
    def permalink(post_id):
        post, row = post_row(post_id)
        count = query('SELECT count(*) n FROM posts WHERE topic_id=? AND id<=? AND (hidden=0 OR ?=1)',
                      (row['id'], post_id, int(staff())), True)['n']
        return redirect(url_for('topic', topic_id=row['id'], page=(count-1)//20+1)+f'#post-{post_id}')

    @app.route('/community/posts/<int:post_id>/report', methods=['GET','POST'])
    def report(post_id):
        require_user()
        post, row = post_row(post_id)
        if request.method == 'POST':
            reason = field('reason',10,1000)
            limit('report-user', 5, 600, True)
            db().execute('INSERT OR IGNORE INTO reports(reporter_id,post_id,reason,created) VALUES(?,?,?,?)',
                         (g.user['id'],post_id,reason,now()))
            report_id = query("SELECT id FROM reports WHERE reporter_id=? AND post_id=? AND status='open'", (g.user['id'],post_id), True)['id']
            audit('report.create',f'report:{report_id}')
            db().commit()
            return render_template('message.html',title='Signalement transmis',message='Les modérateurs pourront examiner votre signalement.')
        return render_template('report.html', post=post)

    @app.get('/community/profiles/<int:user_id>')
    def profile(user_id):
        person = query('SELECT id,name,handle,role,public_history,show_avatar,avatar,created FROM users WHERE id=?',(user_id,),True)
        if not person:
            abort(404)
        public = person['public_history'] or g.user and g.user['id'] == user_id
        p = page()
        history = query('''SELECT p.id,p.created,p.topic_id,t.title FROM posts p JOIN topics t ON t.id=p.topic_id
            WHERE p.author_id=? AND p.hidden=0 AND t.hidden=0 ORDER BY p.id DESC LIMIT 21 OFFSET ?''',(user_id,(p-1)*20)) if public else []
        reputation = query('''SELECT count(*) n FROM reactions r JOIN posts p ON p.id=r.post_id JOIN topics t ON t.id=p.topic_id
            WHERE p.author_id=? AND p.hidden=0 AND t.hidden=0 AND r.kind='helpful' ''',(user_id,),True)['n'] if public else None
        contributions = query('SELECT count(*) n FROM posts p JOIN topics t ON t.id=p.topic_id WHERE p.author_id=? AND p.hidden=0 AND t.hidden=0',(user_id,),True)['n'] if public else None
        return render_template('profile.html',person=person,history=history[:20],more=len(history)>20,page=p,
                               reputation=reputation,contributions=contributions,public=public)

    @app.get('/community/profiles/<int:user_id>/avatar')
    def avatar(user_id):
        person = query('SELECT discord_id,avatar,show_avatar FROM users WHERE id=?',(user_id,),True)
        if not person or not person['avatar'] or not person['show_avatar']:
            return redirect('/assets/img/default.svg')
        limit('avatar-ip',60,60)
        try:
            result = requests.get(f"https://cdn.discordapp.com/avatars/{person['discord_id']}/{person['avatar']}.png?size=128",
                                  timeout=5, allow_redirects=False)
            result.raise_for_status()
            if not result.content.startswith(b'\x89PNG\r\n\x1a\n') or len(result.content)>256000:
                raise ValueError('Invalid avatar')
        except (requests.RequestException,ValueError):
            return redirect('/assets/img/default.svg')
        return app.response_class(result.content, mimetype='image/png')

    @app.route('/account/', methods=['GET','POST'])
    def account():
        if not g.user:
            return render_template('account.html')
        # Suspended users retain export, erasure and privacy settings.
        if request.method == 'POST':
            db().execute('UPDATE users SET public_history=?,show_avatar=?,notify=? WHERE id=?',
                         tuple(int(request.form.get(k)=='on') for k in ('public_history','show_avatar','notify'))+(g.user['id'],))
            audit('privacy.update',f"user:{g.user['id']}")
            db().commit()
            return redirect(url_for('account'))
        return render_template('account.html',sessions=query('SELECT created,seen,token FROM sessions WHERE user_id=? AND seen>? AND created>?',(g.user['id'],now()-3600,now()-DAY)),current=g.session['token'])

    @app.post('/account/sessions/revoke')
    def revoke_sessions():
        if not g.user:
            abort(401)
        db().execute('DELETE FROM sessions WHERE user_id=? AND token<>?',(g.user['id'],g.session['token']))
        audit('sessions.revoke',f"user:{g.user['id']}")
        db().commit()
        return redirect(url_for('account'))

    @app.post('/account/export')
    def export():
        if not g.user:
            abort(401)
        limit('export-user',3,600,True)
        uid = g.user['id']
        data = {'profile':dict(g.user)}
        for table, column in [('topics','author_id'),('posts','author_id'),('follows','user_id'),('favorites','user_id'),
                              ('reactions','user_id'),('notifications','user_id'),('reports','reporter_id'),('audit','actor_id')]:
            data[table]=[dict(r) for r in query(f'SELECT * FROM {table} WHERE {column}=?',(uid,))]
        data['sessions']=[dict(r) for r in query('SELECT created,seen,authenticated FROM sessions WHERE user_id=?',(uid,))]
        audit('data.export',f'user:{uid}')
        db().commit()
        response=make_response(json.dumps(data,ensure_ascii=False,indent=2))
        response.headers['Content-Type']='application/json; charset=utf-8'
        response.headers['Content-Disposition']='attachment; filename="wow-forever-donnees.json"'
        return response

    @app.post('/account/delete')
    def delete_account():
        if not g.user:
            abort(401)
        if now()-(g.session['authenticated'] or 0)>600:
            abort(403,'Reconnectez-vous avant la suppression (10 minutes).')
        if request.form.get('confirm') != 'SUPPRIMER':
            abort(400,'Saisissez SUPPRIMER pour confirmer.')
        uid=g.user['id']
        if g.user['role']=='admin' and query("SELECT count(*) n FROM users WHERE role='admin' AND suspended=0",one=True)['n']<=1:
            abort(409,'Transférez le rôle administrateur avant de supprimer le dernier compte administrateur.')
        # Remove authored text, including personal data embedded in it; preserve discussion structure.
        db().execute("UPDATE posts SET body='[Contribution supprimée]',quote_id=NULL,hidden=1 WHERE author_id=?",(uid,))
        db().execute("UPDATE topics SET title='[Sujet supprimé]',hidden=1 WHERE author_id=?",(uid,))
        db().execute('DELETE FROM reports WHERE reporter_id=? OR post_id IN(SELECT id FROM posts WHERE author_id=?)',(uid,uid))
        db().execute('DELETE FROM reactions WHERE post_id IN(SELECT id FROM posts WHERE author_id=?)',(uid,))
        db().execute('DELETE FROM notifications WHERE actor_id=? OR post_id IN(SELECT id FROM posts WHERE author_id=?)',(uid,uid))
        # Entity IDs may overlap. Only erase this user's target; FK erases their actor identity.
        db().execute('UPDATE audit SET target=? WHERE target=?',('user:[effacé]',f'user:{uid}'))
        db().execute('DELETE FROM users WHERE id=?',(uid,))
        db().commit()
        g.user=None
        g.new_cookie=None
        response=make_response(render_template('message.html',title='Compte supprimé',message='Votre profil et vos données de compte ont été supprimés. Vos contributions ont été effacées. Les sauvegardes expirent sous 30 jours selon la procédure opérateur.'))
        response.delete_cookie(cookie_name,path='/',secure=secure,httponly=True,samesite='Lax')
        return response

    @app.route('/notifications/',methods=['GET','POST'])
    def notifications():
        require_user()
        if request.method=='POST':
            db().execute('UPDATE notifications SET seen=1 WHERE user_id=?',(g.user['id'],))
            db().commit()
            return redirect(url_for('notifications'))
        p=page()
        rows=query('''SELECT n.*,t.title,u.name actor FROM notifications n JOIN topics t ON t.id=n.topic_id
            JOIN posts p ON p.id=n.post_id LEFT JOIN users u ON u.id=n.actor_id
            WHERE n.user_id=? AND t.hidden=0 AND p.hidden=0 ORDER BY n.id DESC LIMIT 21 OFFSET ?''',(g.user['id'],(p-1)*20))
        return render_template('notifications.html',rows=rows[:20],more=len(rows)>20,page=p)

    @app.get('/moderation/')
    def moderation():
        require_user('staff')
        p=page()
        reports=query('''SELECT r.*,p.body,p.topic_id,u.name reporter FROM reports r JOIN posts p ON p.id=r.post_id
            LEFT JOIN users u ON u.id=r.reporter_id WHERE r.status='open' ORDER BY r.id LIMIT 21 OFFSET ?''',((p-1)*20,))
        return render_template('moderation.html',reports=reports[:20],more=len(reports)>20,page=p,
            categories=query('SELECT * FROM categories ORDER BY position,id'),
            logs=query('SELECT a.*,u.name actor FROM audit a LEFT JOIN users u ON u.id=a.actor_id ORDER BY a.id DESC LIMIT 50'),
            hidden=query('SELECT * FROM topics WHERE hidden=1 ORDER BY id DESC LIMIT 50'))

    @app.post('/moderation/posts/<int:post_id>')
    def moderate_post(post_id):
        require_user('staff')
        post,row=post_row(post_id)
        action=request.form.get('action')
        if action not in ('hide','restore'):
            abort(400)
        db().execute('UPDATE posts SET hidden=? WHERE id=?',(int(action=='hide'),post_id))
        if action=='hide':
            db().execute('DELETE FROM notifications WHERE post_id=?',(post_id,))
        audit('post.'+action,f'post:{post_id}')
        db().commit()
        return redirect(url_for('topic',topic_id=row['id']))

    @app.post('/moderation/topics/<int:topic_id>')
    def moderate_topic(topic_id):
        require_user('staff')
        topic_row(topic_id)
        action=request.form.get('action')
        actions={'lock':('locked',1),'unlock':('locked',0),'hide':('hidden',1),'restore':('hidden',0)}
        if action not in actions:
            abort(400)
        col,val=actions[action]
        db().execute(f'UPDATE topics SET {col}=? WHERE id=?',(val,topic_id))
        audit('topic.'+action,f'topic:{topic_id}')
        db().commit()
        return redirect(url_for('topic',topic_id=topic_id))

    @app.post('/moderation/reports/<int:report_id>/resolve')
    def resolve_report(report_id):
        require_user('staff')
        if not query('SELECT id FROM reports WHERE id=?',(report_id,),True):
            abort(404)
        db().execute("UPDATE reports SET status='resolved',resolved=? WHERE id=?",(now(),report_id))
        audit('report.resolve',f'report:{report_id}')
        db().commit()
        return redirect(url_for('moderation'))

    @app.post('/moderation/categories')
    def category():
        require_user('admin')
        name,description=field('name',2,80),field('description',0,500)
        cid=integer(request.form['id']) if request.form.get('id') else None
        parent=integer(request.form['parent']) if request.form.get('parent') else None
        if parent and not query('SELECT id FROM categories WHERE id=? AND parent_id IS NULL',(parent,),True):
            abort(400,'Parent invalide : deux niveaux maximum.')
        if cid:
            if not query('SELECT id FROM categories WHERE id=?',(cid,),True):
                abort(404)
            if cid==parent or parent and query('SELECT id FROM categories WHERE parent_id=?',(cid,),True):
                abort(400,'Hiérarchie cyclique ou trop profonde.')
            db().execute('UPDATE categories SET name=?,description=?,parent_id=? WHERE id=?',(name,description,parent,cid))
        else:
            cid=db().execute('INSERT INTO categories(name,description,parent_id) VALUES(?,?,?)',(name,description,parent)).lastrowid
        audit('category.save',f'category:{cid}')
        db().commit()
        return redirect(url_for('moderation'))

    @app.post('/moderation/users/<int:user_id>')
    def moderate_user(user_id):
        require_user('staff',recent=True)
        person=query('SELECT * FROM users WHERE id=?',(user_id,),True)
        if not person:
            abort(404)
        action=request.form.get('action')
        if user_id==g.user['id'] or person['role']=='admin':
            abort(403,'Ce compte protégé ne peut pas être modifié ici.')
        if action in ('suspend','unsuspend'):
            if person['role']!='member' and g.user['role']!='admin':
                abort(403)
            db().execute('UPDATE users SET suspended=? WHERE id=?',(int(action=='suspend'),user_id))
        elif action in ('member','moderator','admin'):
            require_user('admin',recent=True)
            if person['suspended']:
                abort(409,'Le compte doit être réactivé avant un changement de rôle.')
            db().execute('UPDATE users SET role=? WHERE id=?',(action,user_id))
        else:
            abort(400)
        audit('user.'+action,f'user:{user_id}')
        db().commit()
        return redirect(url_for('profile',user_id=user_id))

    @app.get('/privacy/')
    def privacy():
        return render_template('privacy.html')

    @app.get('/')
    @app.get('/<path:path>')
    def wiki(path='index.html'):
        # Explicit allowlist: never expose source, SQLite, .env or deployment files.
        if '..' in Path(path).parts or '\\' in path:
            abort(404)
        if path.startswith('assets/'):
            suffix=Path(path).suffix.lower()
            if suffix not in ('.css','.js','.svg','.woff2','.png','.webp','.jpg'):
                abort(404)
        elif path in ('index.html','robots.txt','sitemap.xml'):
            pass
        elif re.fullmatch(r'(fr|en)/(?:[a-z0-9-]+/)*(?:index\.(?:html|json))?',path):
            if path.endswith('/'):
                path+='index.html'
        else:
            abort(404)
        return send_from_directory(ROOT,path)

    @app.cli.command('init-db')
    def init_db_command():
        """Apply additive schema and seed genuine, empty Forever categories."""
        Path(app.config['DATABASE']).parent.mkdir(parents=True,exist_ok=True)
        conn=db()
        conn.execute('PRAGMA journal_mode=WAL')
        conn.executescript((ROOT/'community/schema.sql').read_text())
        if not query('SELECT 1 FROM migrations WHERE version=1',one=True):
            for name,description in [
                ('L’auberge','Échanges et entraide autour de WoW Forever.'),
                ('Classes et progression','Stratégies, expériences et questions sur Forever.'),
                ('Le wiki','Corrections sourcées et propositions pour enrichir le wiki.'),
            ]:
                conn.execute('INSERT INTO categories(name,description) VALUES(?,?)',(name,description))
            parent=query("SELECT id FROM categories WHERE name='Classes et progression'",one=True)['id']
            conn.execute('INSERT INTO categories(name,description,parent_id) VALUES(?,?,?)',('Donjons et raids','Discussions consacrées aux rencontres de Forever.',parent))
            conn.execute('INSERT INTO migrations VALUES(1,?)',(now(),))
        if not query('SELECT 1 FROM migrations WHERE version=2',one=True):
            # Legacy report.create used a post ID; preserve its historical meaning.
            conn.execute('''UPDATE audit SET target=(CASE
                WHEN action LIKE 'post.%' OR action='report.create' THEN 'post:'
                WHEN action LIKE 'topic.%' THEN 'topic:'
                WHEN action LIKE 'category.%' THEN 'category:'
                WHEN action LIKE 'report.%' THEN 'report:'
                WHEN action LIKE 'user.%' OR action LIKE 'privacy.%' OR action LIKE 'sessions.%'
                  OR action LIKE 'data.%' OR action LIKE 'operator.role.%' THEN 'user:'
                ELSE 'legacy:' END)||target
                WHERE target<>'' AND target NOT GLOB '*[^0-9]*' ''')
            conn.execute('INSERT INTO migrations VALUES(2,?)',(now(),))
        conn.commit()
        click.echo('Schéma 2 prêt. Aucun faux membre ni sujet créé.')

    @app.cli.command('set-role')
    @click.argument('discord_id')
    @click.argument('role',type=click.Choice(['member','moderator','admin']))
    def set_role(discord_id,role):
        """Operator-only bootstrap/recovery; requires an existing Discord account."""
        person=query('SELECT * FROM users WHERE discord_id=?',(discord_id,),True)
        if not person:
            raise click.ClickException('Ce compte doit d’abord se connecter avec Discord.')
        if person['role']=='admin' and role!='admin' and query("SELECT count(*) n FROM users WHERE role='admin' AND suspended=0",one=True)['n']<=1:
            raise click.ClickException('Impossible de retirer le dernier administrateur.')
        db().execute('UPDATE users SET role=?,suspended=0 WHERE id=?',(role,person['id']))
        db().execute('INSERT INTO audit(actor_id,action,target,created) VALUES(NULL,?,?,?)',('operator.role.'+role,f"user:{person['id']}",now()))
        db().commit()
        click.echo('Rôle mis à jour et action journalisée.')

    @app.cli.command('purge')
    def purge():
        """Run daily. Retention values are project policy, subject to controller review."""
        conn=db()
        conn.execute('DELETE FROM sessions WHERE seen<? OR created<?',(now()-3600,now()-DAY))
        conn.execute('DELETE FROM oauth WHERE expires<?',(now(),))
        conn.execute('DELETE FROM rate_limits WHERE expires<?',(now(),))
        conn.execute('DELETE FROM notifications WHERE created<?',(now()-90*DAY,))
        conn.execute("DELETE FROM reports WHERE status='resolved' AND resolved<?",(now()-180*DAY,))
        conn.execute('DELETE FROM audit WHERE created<?',(now()-180*DAY,))
        conn.commit()
        click.echo('Données arrivées à expiration purgées.')

    def write_backup(destination):
        try:
            descriptor=os.open(destination,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except OSError as exc:
            raise click.ClickException('Destination indisponible ou déjà existante.') from exc
        os.close(descriptor)
        try:
            with sqlite3.connect(destination) as target:
                db().backup(target)
                if target.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                    raise click.ClickException('La vérification de la sauvegarde a échoué.')
        except Exception:
            destination.unlink(missing_ok=True)
            raise

    @app.cli.command('backup')
    @click.argument('destination',type=click.Path(path_type=Path))
    def backup(destination):
        """Consistent SQLite snapshot, mode 0600; refuses to overwrite a backup."""
        write_backup(destination)
        click.echo('Sauvegarde cohérente créée (0600). Chiffrez-la avant transfert hors serveur.')

    @app.cli.command('backup-daily')
    @click.argument('directory',type=click.Path(path_type=Path))
    @click.option('--keep-days',default=30,type=click.IntRange(1,365),show_default=True)
    def backup_daily(directory,keep_days):
        """Local staging snapshots only; encryption/off-site storage is not configured."""
        if directory.is_symlink():
            raise click.ClickException('Le répertoire de sauvegarde ne doit pas être un lien symbolique.')
        directory.mkdir(parents=True,exist_ok=True,mode=0o700)
        if directory.stat().st_mode & 0o077:
            raise click.ClickException('Le répertoire de sauvegarde doit être privé (0700).')
        stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
        destination=directory/f'community-{stamp}-{secrets.token_hex(4)}.sqlite3'
        write_backup(destination)
        # Only rotate our own regular snapshots, after a successful verified backup.
        for path in directory.iterdir():
            if (re.fullmatch(r'community-\d{8}T\d{6}Z-[a-f0-9]{8}\.sqlite3',path.name)
                    and not path.is_symlink() and path.is_file()
                    and path.stat().st_mtime < now()-keep_days*DAY):
                path.unlink()
        click.echo('Sauvegarde locale vérifiée ; rotation appliquée. Aucun chiffrement ni transfert distant effectué.')

    return app
