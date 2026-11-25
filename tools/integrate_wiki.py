#!/usr/bin/env python3
"""Integrate the CURRENT live static wiki build into the community app, reproducibly.

Input : the static wiki tarball (v6 = live build of 28/10/2026 + 6 news published 30/10/2026), verified by SHA-256.
Output: wiki/ (served by the app or by Caddy) + tests/wiki-baseline.json.

L1 (refonte, 30/10/2026): the pipeline now renders the shared WoWki4ever header itself (links to /community/
and /account/ included), so for such builds no navigation edit is needed; only the theme <link> is added.
The build also ships wk-header.js and search-index.json (allow-listed below).

Only navigation markup is changed (links to /community/ and /account/) and, since v7, one
<link> to the night-blue/gold theme layer (wiki-theme.css, from tools/wiki-theme.css) is added
right after site.css in every page. Article text, statuses, illustrations, site.css and JS are
copied byte for byte. Every edit is recorded (original -> new snippet) so tests can reverse it
and prove the content is unchanged; the two added files (wiki-theme.css and the self-hosted
Cinzel font, assets/cinzel-latin.woff2) are recorded with their SHA-256 under "added".

Usage: python3 tools/integrate_wiki.py TARBALL [--expected-sha SHA] [--no-community-links] [--no-theme]
"""
import argparse, hashlib, io, json, re, shutil, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# L1 (refonte) build, reproducible with SOURCE_DATE_EPOCH=1793376000 (ops/l1/build.sh). v7 was 2ed60db2…
EXPECTED = '771326700019ddecc57e5ea14f6380b6f7451f0447b5c5fcf0d7574a359d915f'
ALLOWED = re.compile(r'(index\.html|site\.css|app\.js|ui-core\.mjs|wk-header\.js|search-index\.json|assets/[a-z0-9-]+\.(webp|jpg|svg)|(fr|en)/([a-z0-9-]+/)*index\.html)')
HOME = {'index.html': 'fr', 'fr/index.html': 'fr', 'en/index.html': 'en'}
THEME_CSS = ROOT / 'tools/wiki-theme.css'
THEME_FONT = ROOT / 'community/static/fonts/cinzel-latin.woff2'
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


def theme_edits(text):
    # v7: load the theme layer after site.css, with the same relative prefix (pages work from any depth).
    m = re.search(r'<link rel="stylesheet" href="((?:\.\./)*|\./)site\.css">', text)
    if not m:
        raise SystemExit('lien site.css introuvable')
    return [(m.group(0), m.group(0) + f'<link rel="stylesheet" href="{m.group(1)}wiki-theme.css">')]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tarball', type=Path)
    ap.add_argument('--expected-sha', default=EXPECTED)
    ap.add_argument('--no-community-links', action='store_true', help='no links to /community/ or /account/ (e.g. while the community is private)')
    ap.add_argument('--no-theme', action='store_true', help='do not add the night-blue/gold theme layer (wiki-theme.css)')
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
                changes = []
                if 'data-wk-header' in text:
                    # L1 build: the shared WoWki4ever header (pipeline lib/site-chrome.mjs) already links /community/ and /account/.
                    if args.no_community_links:
                        raise SystemExit('--no-community-links : non pris en charge avec l’en-tête partagé (L1) ; reconstruire le pipeline.')
                elif not args.no_community_links:
                    changes += home_edits(text, HOME[name]) if name in HOME else page_edits(text)
                if not args.no_theme:
                    changes += theme_edits(text)
                if changes:
                    for old, new in changes:
                        if text.count(old) != 1 or new in text:
                            raise SystemExit(f'Point d’insertion ambigu ou absent dans {name}')
                        text = text.replace(old, new, 1)
                    edits[name] = changes
                data = text.encode('utf-8')
            target = out / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    added = {}
    if not args.no_theme:
        for name, src in (('wiki-theme.css', THEME_CSS), ('assets/cinzel-latin.woff2', THEME_FONT)):
            data = src.read_bytes()
            if name in files:
                raise SystemExit(f'{name} existe déjà dans l’archive')
            if name.endswith('.css') and re.search(rb'@import|https?:|//[a-z]', data.split(b'*/', 1)[-1], re.I):
                raise SystemExit('wiki-theme.css ne doit charger aucune ressource externe')
            (out / name).write_bytes(data)
            added[name] = sha(data)
    baseline = {'source': 'wow4ever-web.tar.gz (static build L1 refonte: v7 content + shared WoWki4ever header, branch refonte)', 'tarball_sha256': args.expected_sha,
                'algorithm': 'sha256', 'files': dict(sorted(files.items())), 'edits': edits, 'added': added}
    (ROOT / 'tests/wiki-baseline.json').write_text(json.dumps(baseline, ensure_ascii=False, indent=1) + '\n')
    pages = sum(1 for n in files if n.endswith('.html'))
    print(f'Wiki intégré : {len(files)} fichiers, {pages} pages HTML, {len(edits)} pages modifiées, {len(added)} fichiers de thème ajoutés.')


if __name__ == '__main__':
    main()
