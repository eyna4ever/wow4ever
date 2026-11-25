#!/usr/bin/env python3
"""v43c (Oui de Mathieu t422u, 23/11/2026) : relecture technique du brouillon converti « sanctions-abus-blackmaw-hold »
avant publication. Aucune information ajoutée ni retirée :
  1. les marqueurs bruts « [src: …] » restés dans le paragraphe « Les détails » (ils s'affichaient tels quels) deviennent
     3 paragraphes sourcés (mêmes sources bz-blackmaw-us / bz-blackmaw-eu) ;
  2. nom officiel français du donjon (news.blizzard.com fr-fr 24303862, déjà employé sur la fiche du wiki) : « Repaire des
     Noiregueules », avec « Blackmaw Hold » entre parenthèses à la première mention (texte FR seulement) ;
  3. apostrophes typographiques (’) comme sur les autres articles.
Usage : fix_blackmaw43c.py IN.json OUT.json"""
import json, re, sys
src, dst = sys.argv[1:3]
entries = json.load(open(src, encoding='utf-8')); assert len(entries) == 1
e = entries[0]; a = e['article']
SRC = ['bz-blackmaw-us', 'bz-blackmaw-eu']
# 1) paragraphe « Les détails »
sec = next(s for s in a['sections'] if s['id'] == 'les-details'); assert len(sec['blocks']) == 1
b = sec['blocks'][0]; assert b['type'] == 'p'
parts = {L: [x.strip() for x in re.split(r'\s*\[src: bz-blackmaw-us, bz-blackmaw-eu\]\s*', b[L])] for L in ('fr', 'en')}
assert len(parts['fr']) == len(parts['en']) == 3 and all(parts['fr']) and all(parts['en']), parts
assert b.get('src', SRC) == SRC
sec['blocks'] = [{'type': 'p', 'fr': parts['fr'][i], 'en': parts['en'][i], 'src': list(SRC)} for i in range(3)]
# 2) nom officiel FR
FR = [('title', 'l\'abus de butin à Blackmaw Hold', 'l\'abus de butin au Repaire des Noiregueules'),
      ('description', 'dans le donjon Blackmaw Hold', 'dans le donjon Repaire des Noiregueules (Blackmaw Hold)'),
      ('lead', 'dans le donjon Blackmaw Hold', 'dans le donjon Repaire des Noiregueules (Blackmaw Hold)'),
      ('kp0', 'non élites de Blackmaw Hold', 'non élites du Repaire des Noiregueules'),
      ('cons', 'a fait Blackmaw Hold normalement', 'a fait le Repaire des Noiregueules normalement')]
tgt = {'title': e['title'], 'description': e['description'], 'lead': a['lead'], 'kp0': a['keyPoints'][0],
       'cons': next(s for s in a['sections'] if s['blocks'][0]['fr'].startswith('Un joueur qui a fait'))['blocks'][0]}
for k, old, new in FR:
    assert tgt[k]['fr'].count(old) == 1, k; tgt[k]['fr'] = tgt[k]['fr'].replace(old, new)
# 3) apostrophes typographiques dans les textes affichés (fr/en), jamais dans les sources
def typo(x, path=()):
    if isinstance(x, dict):
        return {k: (v if k in ('sources', 'slug', 'id', 'key', 'url', 'src') else typo(v, path + (k,))) for k, v in x.items()}
    if isinstance(x, list): return [typo(v, path) for v in x]
    if isinstance(x, str) and path and path[-1] in ('fr', 'en'): return x.replace("'", '’')
    return x
e = typo(e)
txt = json.dumps(e, ensure_ascii=False)
assert '[src:' not in txt
assert all('Blackmaw Hold' not in s or '(Blackmaw Hold)' in s for s in re.findall(r'"fr": "([^"]*)"', txt))
json.dump([e], open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1); open(dst, 'a').write('\n')
print('ok', dst)
