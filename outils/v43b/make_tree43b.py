#!/usr/bin/env python3
"""v43b (t420u) : comme make_tree43.py (même chaîne depuis la v42c), avec les cartes entièrement explorées ; construit v43b-test/tree = v42c-test/tree + données Polestar/carte sur toutes les zones Forever (FR/EN),
pages « Sources et licences », liste blanche de l'application étendue aux seuls nouveaux fichiers, tests et empreinte mis à jour.
Build de TEST : aucun envoi, aucun déploiement."""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path
R = Path('/workspace/wowkipedia-v21-elite'); A = R / 'v42c-test/tree'; T = R / 'v43b-test/tree'; W = T / 'wiki'
REPO = Path('/workspace/wow4ever-polestar'); PW = Path('/workspace/polestar-work')
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
V42C = 'c59626b1c32b73aadaa4971a1b5b36b5a2999aaa24e2aaf48a4b997ec32ac9aa'
assert json.loads((A / 'tests/wiki-baseline.json').read_text())['tarball_sha256'] == V42C
if T.exists(): shutil.rmtree(T)
shutil.copytree(A, T, symlinks=True, ignore=shutil.ignore_patterns('__pycache__'))
subprocess.run([sys.executable, str(REPO / 'tools/polestar/render_all.py'), '--src', '/workspace/polestar/forever-db', '--tree', str(T),
                '--zones', str(PW / 'zones.json'), '--maps', str(PW / 'explored'), '--frame', str(PW / 'uimap-assignment-70862.json'),
                '--area-table', str(PW / 'areatable-parent-70862.json'),
                '--ours-quests', str(R / 'completion-v39b/sources/quests-index.json'), '--ours-npcs', str(R / 'v42-research/npc-data.json'),
                '--items-fr', str(PW / 'items-fr-70862.json'), '--items-en', str(PW / 'items-en-70862.json'),
                '--classic-items', str(PW / 'items/staging-classic-items.json'), '--report', str(R / 'v43b-test/render-report.json')], check=True)
# 1) application : liste blanche étendue (et seulement) aux fichiers v43
ap = T / 'community/app.py'; s = ap.read_text()
old = "        if re.fullmatch(r'assets/[a-z0-9-]+\\.(?:avif|webp|jpg|svg|woff2)',path) or path in ('index.html','v2.css','site.css','wiki-theme.css','app.js','ui-core.mjs','wk-header.js','search-index.json','search-detail-fr.json','search-detail-en.json','theme.js','theme-wow.css'):\n            pass\n"
new = ("        if re.fullmatch(r'assets/[a-z0-9-]+\\.(?:avif|webp|jpg|svg|woff2)',path) or path in ('index.html','v2.css','site.css','wiki-theme.css','app.js','ui-core.mjs','wk-header.js','search-index.json','search-detail-fr.json','search-detail-en.json','theme.js','theme-wow.css','wk-map.css','wk-map.js'):\n            pass\n"
       "        elif re.fullmatch(r'assets/carte/[0-9]{1,5}/(?:r[0-9]{1,2}-c[0-9]{1,2}\\.webp|donnees\\.json)',path):\n"
       "            pass  # v43: carte interactive (images officielles du jeu + repères à confirmer)\n"
       "        elif re.fullmatch(r'(?:fr/sources-et-licences|en/sources-and-licences)/(?:donnees-polestar|objets-classic)\\.json\\.gz',path):\n"
       "            response=send_from_directory(WIKI_ROOT,path,mimetype='application/gzip',as_attachment=True)  # v43: données sous forme modifiable (GPL)\n"
       "            response.headers['Cache-Control']='no-cache'\n"
       "            return response\n")
assert s.count(old) == 1; s = s.replace(old, new); ap.write_text(s)
# 2) tests : 475 pages (+2 « Sources et licences »), nouvelles adresses servies, empreinte
files = {str(p.relative_to(W)): H(p) for p in sorted(W.rglob('*')) if p.is_file()}
fp = hashlib.sha256(('\n'.join(f'{k}\t{files[k]}' for k in sorted(files)) + '\n').encode()).hexdigest()
b = json.loads((T / 'tests/wiki-baseline.json').read_text())
b['source'] = ('v43b (t420u, 2026-11-18) : cartes entièrement explorées (calques WorldMapOverlay du client assemblés comme en jeu), tuiles ?v=43b. Base v43 en ligne. Précédent : v43 (t418u, 2026-11-18) : quêtes fusionnées et carte interactive sur les 50 fiches de zone FR/EN (images officielles du jeu, '
               'repères à confirmer), pages noindex « Sources et licences ». Base v42c en ligne. Précédent : ' + b['source'])
b['tarball_sha256'] = fp; b['files'] = files
(T / 'tests/wiki-baseline.json').write_text(json.dumps(b, ensure_ascii=False, indent=1) + '\n')
t = (T / 'tests/test_community.py').read_text()
t, n = re.subn(r"self\.assertEqual\(baseline\['tarball_sha256'\],'[0-9a-f]{64}'\)", f"self.assertEqual(baseline['tarball_sha256'],'{fp}')", t, count=1); assert n == 1
t, n = re.subn(r"(self\.assertEqual\(sum\(1 for f in files if f\.endswith\('\.html'\)\),)473\)", r"\g<1>475)  # v43 (t418u): +2 Sources et licences FR+EN", t); assert n == 1
t, n = re.subn(r"self\.assertEqual\(len\(pages\),473\)", "self.assertEqual(len(pages),475)  # v43 (t418u): +2 Sources et licences FR+EN", t); assert n == 2, n
a = "        self.assertEqual(self.get('/search-detail-de.json').status_code,404)\n"
assert t.count(a) == 1
t = t.replace(a, a + "        # v43 (t418u): interactive map files and credits data are served; nothing else in those folders\n"
              "        self.assertEqual(self.get('/assets/carte/1411/donnees.json').status_code,200)\n"
              "        self.assertEqual(self.get('/wk-map.js?v=43').mimetype,'text/javascript')\n"
              "        g=self.get('/fr/sources-et-licences/donnees-polestar.json.gz')\n"
              "        self.assertEqual((g.status_code,g.mimetype),(200,'application/gzip')); self.assertIn('attachment',g.headers['Content-Disposition'])\n"
              "        for p in ('/assets/carte/1411/manifest.json','/assets/carte/1411/../../v2.css','/assets/carte/x/r0-c0.webp','/fr/sources-et-licences/autre.json.gz','/fr/zones/durotar/donnees.json'):\n"
              "            self.assertEqual(self.get(p).status_code,404,p)\n")
t, n = re.subn(r"self\.assertEqual\(len\(set\(current\)-set\(reference\['pages'\]\)\),332\)", "self.assertEqual(len(set(current)-set(reference['pages'])),334)  # v43 (t418u): +2 Sources et licences FR+EN ;", t); assert n == 1
a = "                self.assertEqual(len(links),2)\n"; assert t.count(a) == 1
t = t.replace(a, "                zone_map='wk-map.css?v=43' in text and '/zones/' in '/'+str(file.relative_to(WIKI_ROOT))  # v43 (t418u): zone pages load the map stylesheet\n"
                 "                self.assertEqual(len(links),3 if zone_map else 2)\n"
                 "                if zone_map: self.assertRegex(links[2],r'^(\\.\\./)+wk-map\\.css\\?v=43$')\n")
(T / 'tests/test_community.py').write_text(t)
ch = sorted(k for k in files if not (A / 'wiki' / k).is_file() or H(A / 'wiki' / k) != files[k])
print(json.dumps({'fingerprint': fp, 'wiki_files': len(files), 'html': sum(1 for k in files if k.endswith('.html')), 'wiki_changed_or_added': len(ch), 'app': H(ap)}))
