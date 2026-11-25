#!/usr/bin/env python3
"""Content fingerprint of a static wiki build (lot L1, 30/10/2026).

The L1 redesign only changes the site chrome (shared header, brand name, scripts). This tool extracts, for every
HTML page, the parts that carry documentary content and must stay identical to the v7 build:
  - main      : the whole <main id="main-content">…</main> element (articles, notices, home sections);
  - notice    : the footer « independence » paragraph (mandatory Blizzard notice);
  - tail      : home pages only, everything between </footer> and the first module script (dialogs + embedded catalogue);
  - title     : the page <title> without the site-name suffix.
The only normalisation is the approved brand rename (« WoWki4ever » -> « WoW Forever Wiki »), applied to compare.

Usage: python3 tools/content_fingerprint.py BUILD_TARBALL_OR_DIR > tests/v7-content-fingerprint.json
"""
import hashlib, io, json, re, sys, tarfile
from pathlib import Path

RENAME = [('WoWki4ever', 'WoW Forever Wiki')]


def normalise(text):
    for new, old in RENAME:
        text = text.replace(new, old)
    return text


def parts(html):
    out = {}
    m = re.search(r'<main id="main-content"[\s\S]*?</main>', html)
    out['main'] = m.group(0) if m else ''
    m = re.search(r'<p class="independence"[^>]*>[\s\S]*?</p>', html)
    out['notice'] = m.group(0) if m else ''
    end = html.find('</footer>')
    script = html.find('<script type="module"', end)
    out['tail'] = html[end + 9:script] if end != -1 and script != -1 and 'id="wiki-data"' in html[end:script] else ''
    m = re.search(r'<title>([\s\S]*?)</title>', html)
    out['title'] = re.sub(r' — (WoW Forever Wiki|WoWki4ever)( — .*)?$', '', normalise(m.group(1))) if m else ''
    return {k: hashlib.sha256(normalise(v).encode()).hexdigest() for k, v in out.items()}


def pages(source):
    source = Path(source)
    if source.is_dir():
        for p in sorted(source.rglob('*.html')):
            yield str(p.relative_to(source)), p.read_text('utf-8')
        return
    with tarfile.open(source, 'r:gz') as tar:
        for member in sorted(tar.getmembers(), key=lambda m: m.name):
            if member.isfile() and member.name.endswith('.html'):
                yield member.name.lstrip('./'), tar.extractfile(member).read().decode('utf-8')


def fingerprint(source):
    return {name: parts(html) for name, html in pages(source)}


if __name__ == '__main__':
    print(json.dumps({'source': 'wow4ever-web.tar.gz v7 (sha256 2ed60db2b192585b7963d1561afe49246a41df672f044a4b6aedba8c7bcca885)',
                      'rename': RENAME, 'pages': fingerprint(sys.argv[1])}, ensure_ascii=False, indent=1))
