#!/usr/bin/env python3
"""Étape 04 — non-régression du wiki lot 2 (dist-v2, arbre de test) contre le wiki v32 en production (site/wiki).
Usage : python3 non_regression.py <site/wiki v32> <dist-v2 lot 2>"""
import os, re, sys, json, hashlib
old, new = sys.argv[1], sys.argv[2]
def pages(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f); out[os.path.relpath(p, root)] = p
    return out
O, N = pages(old), pages(new)
cnt = lambda h: re.sub(r'<span class="wk-count">\d+<', '<span class="wk-count">N<', h)
def main_wo_rail(h):
    m = re.search(r'<main id="main-content"[\s\S]*?</main>', h)
    return re.sub(r'<aside class="v2-rail">[\s\S]*?</aside>', '', m.group(0)) if m else None
def article(h):
    m = re.search(r'<article class="v2-article"[\s\S]*?</article>', h); return m.group(0) if m else None
res = {'identique': [], 'compteurs_menu_seulement': [], 'rail_navigation_seulement': [], 'contenu_modifie': [], 'supprimee': [], 'nouvelle': [], 'fichier_non_html_modifie': []}
for rel, p in sorted(O.items()):
    if rel not in N: res['supprimee'].append(rel); continue
    a, b = open(p, 'rb').read(), open(N[rel], 'rb').read()
    if a == b: res['identique'].append(rel); continue
    if not rel.endswith('.html'): res['fichier_non_html_modifie'].append(rel); continue
    a, b = a.decode(), b.decode()
    if cnt(a) == cnt(b): res['compteurs_menu_seulement'].append(rel)
    elif main_wo_rail(a) is not None and main_wo_rail(cnt(a)) == main_wo_rail(cnt(b)) and cnt(a).split('<main')[0] == cnt(b).split('<main')[0]: res['rail_navigation_seulement'].append(rel)
    else: res['contenu_modifie'].append(rel)
res['nouvelle'] = sorted(set(N) - set(O))
# a11y / Android de base sur toutes les pages HTML du wiki lot 2
a11y = []
for rel, p in sorted(N.items()):
    if not rel.endswith('.html'): continue
    h = open(p, encoding='utf-8').read()
    if '<meta http-equiv="refresh"' in h and '<main' not in h: continue  # redirections de fusion
    errs = []
    if not re.search(r'<html lang="(fr|en)"', h): errs.append('lang')
    if 'name="viewport" content="width=device-width,initial-scale=1"' not in h: errs.append('viewport')
    if 'name="robots" content="noindex,nofollow"' not in h: errs.append('noindex')
    if len(re.findall(r'<h1[\s>]', h)) != 1: errs.append('h1=%d' % len(re.findall(r'<h1[\s>]', h)))
    lv = [int(x) for x in re.findall(r'<h([1-6])[\s>]', re.sub(r'<div class="wk-search"[\s\S]*?</form>', '', h))]
    if any(lv[i] > lv[i-1] + 1 for i in range(1, len(lv))): errs.append('saut de titre %s' % lv)
    if len(re.findall(r'<table[\s>]', h)) != len(re.findall(r'<caption[\s>]', h)): errs.append('tableau sans légende')
    if re.search(r'<script(?![^>]*\bsrc=)[^>]*>', h): errs.append('script inline')
    if re.search(r'<style[\s>]|\sstyle="', h): errs.append('style inline')
    if errs: a11y.append((rel, errs))
sitemaps = [r for r in N if 'sitemap' in r.lower()]
robots = open(N['robots.txt']).read() if 'robots.txt' in N else None
print(json.dumps({k: len(v) for k, v in res.items()}, ensure_ascii=False))
for k in ('compteurs_menu_seulement', 'rail_navigation_seulement', 'contenu_modifie', 'supprimee', 'nouvelle', 'fichier_non_html_modifie'):
    print('\n## %s (%d)' % (k, len(res[k])))
    for r in res[k]: print('  ' + r)
print('\n## a11y/Android : %d page(s) HTML en défaut' % len(a11y))
for r, e in a11y: print('  %s : %s' % (r, ', '.join(e)))
print('\n## sitemap : %s' % (sitemaps or 'aucun'))
print('## robots.txt : %s' % (repr(robots) if robots is not None else 'absent du dist (servi par le site)'))
