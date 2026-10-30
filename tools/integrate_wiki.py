#!/usr/bin/env python3
"""Integrate the CURRENT live static wiki build into the community app, reproducibly.

Input : the static wiki tarball (v6 = live build of 28/10/2026 + 6 news published 30/10/2026), verified by SHA-256.
Output: wiki/ (served by the app or by Caddy) + tests/wiki-baseline.json.

Only navigation markup is changed (links to /community/ and /account/). Article text,
statuses, illustrations, CSS and JS are copied byte for byte. Every edit is recorded
(original -> new snippet) so tests can reverse it and prove the content is unchanged.

Usage: python3 tools/integrate_wiki.py TARBALL [--expected-sha SHA] [--no-community-links]
"""
import argparse, hashlib, io, json, re, shutil, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = '2ed60db2b192585b7963d1561afe49246a41df672f044a4b6aedba8c7bcca885'
ALLOWED = re.compile(r'(index\.html|site\.css|app\.js|ui-core\.mjs|assets/[a-z0-9-]+\.(webp|jpg|svg)|(fr|en)/([a-z0-9-]+/)*index\.html)')
HOME = {'index.html': 'fr', 'fr/index.html': 'fr', 'en/index.html': 'en'}
LABEL = {'fr': ('Communauté', 'Connexion'), 'en': ('Community', 'Sign in')}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def home_edits(text, lang):
    community, signin = LABEL[lang]
    edits = [
        # In-page placeholder "community" panel -> the real community app.
        (f'<a href="#feature-panel" data-view="community" data-fr="Communauté" data-en="Community">{community}</a>',
         f'<a href="/community/" data-community-link data-fr="Communauté" data-en="Community">{community}</a>'),
        # Local-only account dialog button -> real Discord sign-in page (id changed so app.js no longer binds it).
        (f'<button id="account-open" class="gold-outline" type="button" data-fr="Connexion" data-en="Sign in">{signin}</button>',
         f'<a id="community-account" class="gold-outline" href="/account/" data-community-link data-fr="Connexion" data-en="Sign in">{signin}</a>'),
    ]
    return edits


def page_edits(text):
    m = re.search(r'<nav class="page-nav" aria-label="(Navigation principale|Main navigation)">(.*?)</nav>', text)
    if not m:
        raise SystemExit('page-nav introuvable')
    label = 'Communauté' if m.group(1) == 'Navigation principale' else 'Community'
    old = m.group(0)
    new = old[:-len('</nav>')] + f'<a href="/community/" data-community-link>{label}</a></nav>'
    return [(old, new)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tarball', type=Path)
    ap.add_argument('--expected-sha', default=EXPECTED)
    ap.add_argument('--no-community-links', action='store_true', help='copy the wiki unchanged (e.g. while the community is private)')
    args = ap.parse_args()
    raw = args.tarball.read_bytes()
    if sha(raw) != args.expected_sha:
        raise SystemExit(f'SHA-256 inattendu pour {args.tarball}')
    out = ROOT / 'wiki'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    files, edits = {}, {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for member in tar.getmembers():
            if member.isdir():
                continue
            name = member.name.lstrip('./')
            if not member.isfile() or not ALLOWED.fullmatch(name) or '..' in name.split('/'):
                raise SystemExit(f'Fichier hors liste blanche dans l’archive : {member.name}')
            data = tar.extractfile(member).read()
            files[name] = sha(data)
            if name.endswith('.html'):
                text = data.decode('utf-8')
                if 'Site indépendant et non officiel de Blizzard Entertainment.' not in text:
                    raise SystemExit(f'Mention Blizzard absente : {name}')
                if not args.no_community_links:
                    changes = home_edits(text, HOME[name]) if name in HOME else page_edits(text)
                    for old, new in changes:
                        if text.count(old) != 1 or new in text:
                            raise SystemExit(f'Point d’insertion ambigu ou absent dans {name}')
                        text = text.replace(old, new, 1)
                    edits[name] = changes
                data = text.encode('utf-8')
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    baseline = {'source': 'wow4ever-web.tar.gz (static build v6: live 2026-10-28 + 6 news published 2026-10-30)', 'tarball_sha256': args.expected_sha,
                'algorithm': 'sha256', 'files': dict(sorted(files.items())), 'edits': edits}
    (ROOT / 'tests/wiki-baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=1) + '\n')
    pages = sum(1 for n in files if n.endswith('.html'))
    print(f'Wiki intégré : {len(files)} fichiers, {pages} pages HTML, {len(edits)} pages avec liens communauté.')


if __name__ == '__main__':
    main()
