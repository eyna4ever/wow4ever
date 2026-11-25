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

from community.app import ROOT, WIKI_ROOT, create_app, digest

BASE = 'http://localhost:8000'


def article_blocks_of(html):
    import sys
    sys.path.insert(0,str(ROOT/'tools'))
    from content_blocks import article_blocks
    return article_blocks(html)


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

    # v12 (wowki4ever-source typo-v12 29c241c, phone margins/typography in v2.css only; content identical to v10/v11).
    # v11 (wowki4ever-source mobile-v11 c822937, mobile-first CSS + AVIF images; content identical to v10).
    # v10 (wowki4ever-source contenu-v10 91c9048): the wiki is the v2c static build, integrated by tools/integrate_v2.py
    # from a reproducible archive (ops/v2/package.sh). Nothing is edited or added after the build: every file of wiki/
    # must match tests/wiki-baseline.json byte for byte (193 pages = v9's 141 + 26 new published entries in FR and EN),
    # and no v8-only file (site.css, app.js, wiki-theme.css, Cinzel font) may linger.
    def test_wiki_preservation(self):
        baseline=json.loads((ROOT/'tests/wiki-baseline.json').read_text())
        # v17 (ameliorations-v17, « Oui » de Mathieu t255u, 01/11/2026 17:16): home « Quoi de neuf », faster search, 9 beginner
        # guides published via review.mjs (18 new pages FR/EN). v16 format styles kept, v17 styles appended.
        self.assertEqual(baseline['tarball_sha256'],'5875d6be00b3d058195bd8000f0ea194b323ab5dfb78e8bb7eb91858421e8dd4')  # v43d (2026-11-25) ; v43b = c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517  # v43c (2026-11-24) ; v43b = c82421613a35ec1c3306c82b908c545f353347ea22c324589db355337f649517  # v42 (t407u, matériaux + PNJ, inclut v41, sur v40b) ; v40b = e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce ; v40b (t404u, correctifs du 16 novembre) ; v40 = f208c6cf2fdffe66e5d79203f57ebf845c310dfada3f36f73059d29b49510ab5 (t402u, césure tuiles) empreinte wiki (manifeste trié) ; v39 = e1ec85bf95e7b62009bc2616b66d9743b32f19c49ffce19937549922e66b2b5d
        css=(ROOT/'wiki/v2.css').read_text()
        self.assertIn('.v16-analysis{',css); self.assertIn('.v16-tags{',css); self.assertIn('.v16-discussion{',css)
        self.assertIn('.v17-whatsnew',css); self.assertIn('.wk-result mark{',css)
        self.assertIn('.v18-path{',css)  # v18: beginner path block on the 9 beginner guide pages
        self.assertIn('.v19-path-more{',css)  # v19: race-history annexes unnumbered under step 3
        # v40 (t401u): accueil restructuré, plus de bandeau « Quoi de neuf » ; recherche + rubriques + mises à jour.
        for lang, title, hid in (('fr', 'Dernières mises à jour', 'v40-upd-title'),
                                 ('en', 'Latest updates', 'v40-upd-title')):
            html = (WIKI_ROOT/lang/'index.html').read_text()
            self.assertIn('class="v40-home"', html)
            self.assertNotIn('v2-hero', html)
            self.assertIn(f'<h2 id="{hid}">{title}</h2>', html)
        self.assertIn('.v40-home', (ROOT/'wiki/v2.css').read_text())
        css = (ROOT/'wiki/v2.css').read_text()
        self.assertIn('body.v39', css)
        self.assertNotIn('@import', css)
        files={str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*') if p.is_file()}
        self.assertEqual(files,set(baseline['files']))
        self.assertEqual(sum(1 for f in files if f.endswith('.html')),477)  # v43c: +2 article Blackmaw FR+EN  # v43 (t418u): +2 Sources et licences FR+EN  # v42 (t407u): +22 pages (Collections FR+EN, 10 fiches Matériaux FR+EN)  # v39 (t391u): +52 pages (26 fiches de complétion, FR+EN)  # v38 (t361u): +96 pages (48 fiches de zones, FR+EN)  # v37 (t355u): +22 pages (10 bestiaire + 1 poissons, FR+EN)  # v36 (t351u): +30 pages  # v35 (t347u): +2 factions  # v33: +8 lot 2  # v32: +14 lot 1
        self.assertFalse(files&{'site.css','app.js','wiki-theme.css','assets/cinzel-latin.woff2','PROPOSITION-V2-LOCALE.txt'})
        for key in sorted(files):
            with self.subTest(path=key):
                self.assertEqual(hashlib.sha256((WIKI_ROOT/key).read_bytes()).hexdigest(),baseline['files'][key])

    # v10 corrections approved by Mathieu (30/10/2026 22:30, review.mjs revise -> publish): the only v8 entry pages whose
    # documentary content may differ (official FR names in AR05 / AR07 / zones article, expanded raid/dungeon notices).
    V10_CORRECTED={'fr/donjons-raids/raids-et-donjons/index.html','fr/races/les-eolides/index.html','fr/zones/zones-forever/index.html',
                   'fr/donjons-raids/salle-des-thanes/index.html','en/dungeons-raids/hall-of-thanes/index.html',
                   'fr/donjons-raids/profondeurs-des-saisons/index.html','en/dungeons-raids/barrow-deeps/index.html',
                   'fr/donjons-raids/sommet-d-hyjal/index.html','en/dungeons-raids/hyjal-summit/index.html'}

    # v15 (fusion approved by Mathieu, 01/11/2026 04:39 Europe/Paris, review.mjs revise -> publish / reject): two duplicates
    # merged. The kept launch page carries the merged facts and sources; the two merged addresses now serve a static
    # redirect page (no documentary block) to the kept page. The kept podcast page is a v10 page (not in the v8 reference).
    V15_KEPT={'fr/actualites/lancement-mondial-annonce/index.html','en/news/announced-worldwide-launch/index.html'}
    # v22: the golive-nov4 entry was rewritten and republished at its own address (Mathieu's « Oui », 04/11/2026),
    # so its two v15 redirect pages became the launch article again.
    V22_GOLIVE={'fr/actualites/lancement-mondial-le-4-novembre-ce-qu-il-faut-savoir/index.html','en/news/global-launch-on-november-4-what-to-know/index.html'}
    # v22: existing pages updated with a dated correction line (veille du 04/11/2026, approved by Mathieu).
    V22_UPDATED={'en/guides/prepare-launch-names/index.html','fr/guides/preparer-lancement-noms/index.html','en/guides/rulesets/index.html',
                 'fr/guides/ensembles-de-regles/index.html','en/news/forever-schedule/index.html','fr/actualites/calendrier-forever/index.html',
                 'en/pvp/darkspear-islands/index.html','fr/jcj/iles-des-sombrelances/index.html'}
    # v23: pages updated through review.mjs (veille du 04/11 : classes, races, campement, noms FR des notes de lancement ; « Oui » t302u).
    # v28: the 9 short entries completed from the November 4 audit (official Blizzard sources, approved by Mathieu, t316u), FR + EN.
    V38_UPDATED={'fr/actualites/nouvelle-unbowed/index.html','en/news/short-story-unbowed/index.html'}
    V30_UPDATED={'fr/actualites/lancement-mondial-le-4-novembre-ce-qu-il-faut-savoir/index.html','en/news/global-launch-on-november-4-what-to-know/index.html','fr/index.html','en/index.html','fr/actualites/index.html','en/news/index.html','index.html','fr/wiki/index.html','en/wiki/index.html'}
    V28_UPDATED={'en/creatures/foxes/index.html','en/creatures/onyxia/index.html','en/professions/recipes-and-advanced-blueprints/index.html','en/pvp/honor/index.html','en/pvp/rank-points/index.html','en/zones/mount-hyjal/index.html','en/zones/riverglades/index.html','en/zones/shen-dralas/index.html','en/zones/zephras-isle/index.html','fr/creatures/onyxia/index.html','fr/creatures/renards/index.html','fr/jcj/honneur/index.html','fr/jcj/points-de-rang/index.html','fr/metiers/recettes-et-plans-avances/index.html','fr/zones/ile-de-zephras/index.html','fr/zones/mont-hyjal/index.html','fr/zones/rives-claires/index.html','fr/zones/shen-dralas/index.html'}
    V23_UPDATED={'en/classes/druid/index.html',
                 'en/classes/forever-classes/index.html',
                 'en/classes/hunter/index.html',
                 'en/classes/mage/index.html',
                 'en/classes/paladin/index.html',
                 'en/classes/priest/index.html',
                 'en/classes/rogue/index.html',
                 'en/classes/shaman/index.html',
                 'en/classes/warlock/index.html',
                 'en/classes/warrior/index.html',
                 'en/news/launch-notes-class-damage/index.html',
                 'en/professions/camping-and-crafting/index.html',
                 'en/professions/campsite-crafting/index.html',
                 'en/races/dwarf/index.html',
                 'en/races/gnome/index.html',
                 'en/races/human/index.html',
                 'en/races/night-elf/index.html',
                 'en/races/orc/index.html',
                 'en/races/skyborne/index.html',
                 'en/races/tauren/index.html',
                 'en/races/troll/index.html',
                 'en/races/undead/index.html',
                 'fr/actualites/notes-de-lancement-degats-des-classes/index.html',
                 'fr/classes/chaman/index.html',
                 'fr/classes/chasseur-chasseresse/index.html',
                 'fr/classes/classes-forever/index.html',
                 'fr/classes/demoniste/index.html',
                 'fr/classes/druide-druidesse/index.html',
                 'fr/classes/guerrier-guerriere/index.html',
                 'fr/classes/mage/index.html',
                 'fr/classes/paladin/index.html',
                 'fr/classes/pretre-pretresse/index.html',
                 'fr/classes/voleur-voleuse/index.html',
                 'fr/metiers/artisanat-du-campement/index.html',
                 'fr/metiers/campement-et-artisanat/index.html',
                 'fr/races/elfe-de-la-nuit/index.html',
                 'fr/races/eolides/index.html',
                 'fr/races/gnome/index.html',
                 'fr/races/humain-humaine/index.html',
                 'fr/races/mort-vivant-morte-vivante/index.html',
                 'fr/races/nain-naine/index.html',
                 'fr/races/orc-orque/index.html',
                 'fr/races/tauren-taurene/index.html',
                 'fr/races/troll-trollesse/index.html'}
    V15_REDIRECTS={'fr/actualites/podcast-wow-forever-la-technique/index.html':'../../../fr/actualites/le-podcast-officiel-wow-forever/',
                   'en/news/wow-forever-podcast-all-about-tech/index.html':'../../../en/news/the-official-wow-forever-podcast/'}

    @staticmethod
    def v14_sources_form(block):
        # v15 display fix: a source without a language no longer shows an empty « () » nor hreflang="". Re-insert them to
        # compare with the v8 fingerprint: proves that this is the only change in the unchanged pages.
        return re.sub(r'(<a href="[^"]+" rel="noopener noreferrer")>([^<]*)</a>(?! <span class="source-lang">)',r'\1 hreflang="">\2</a> <span class="source-lang">()</span>',block) if 'sources-block' in block else block

    def test_v15_redirect_pages(self):
        for page,target in self.V15_REDIRECTS.items():
            with self.subTest(page=page):
                text=(WIKI_ROOT/page).read_text()
                self.assertIn(f'<meta http-equiv="refresh" content="0; url={target}">',text)
                self.assertIn(f'<link rel="canonical" href="{target}">',text)
                self.assertIn(f'href="{target}"',text)
                self.assertIn('noindex',text)
                self.assertEqual(article_blocks_of(text),[])
                self.assertTrue((WIKI_ROOT/target.replace('../../../','')/'index.html').is_file())
                url='/'+page.removesuffix('index.html')
                self.assertEqual(self.get(url).status_code,200,url)
                self.assertEqual(self.get(url.rstrip('/')).status_code,308,url)
        for file in WIKI_ROOT.rglob('index.html'):
            self.assertNotIn('source-lang">()',file.read_text(),str(file))

    def test_wiki_content_unchanged_since_v8(self):
        # The v2c redesign changes the page layout only. For each of the 110 v8 entry pages (55 entries, FR + EN), the
        # article sections and the sources block must be byte-identical to the v8 build deployed on 30/10/2026
        # (reference: tests/v8-content-fingerprint.json, taken from the v8 wiki before integration), except the 9 pages
        # corrected in v10 (V10_CORRECTED). This includes the official Discord (WoW Portal Room) page, checked by name
        # below. v10 adds exactly 52 new entry pages (26 entries, FR + EN). See tools/content_blocks.py.
        import sys
        sys.path.insert(0,str(ROOT/'tools'))
        from content_blocks import article_blocks
        reference=json.loads((ROOT/'tests/v8-content-fingerprint.json').read_text())
        self.assertIn('771326700019ddecc57e5ea14f6380b6f7451f0447b5c5fcf0d7574a359d915f',reference['source'])
        self.assertEqual(len(reference['pages']),110)
        current={}
        for file in WIKI_ROOT.rglob('index.html'):
            blocks=article_blocks(file.read_text())
            if blocks:
                current[str(file.relative_to(WIKI_ROOT))]=hashlib.sha256('\n'.join(blocks).encode()).hexdigest()
        redirects=set(self.V15_REDIRECTS)
        self.assertTrue(redirects<=set(reference['pages']) and not redirects&set(current))
        self.assertTrue(self.V22_GOLIVE<=set(reference['pages']) and self.V22_GOLIVE<=set(current))
        self.assertEqual(set(reference['pages'])-set(current),redirects)
        self.assertEqual(len(set(current)-set(reference['pages'])),336)  # v43c: +2 article Blackmaw FR+EN ;  # v43 (t418u): +2 Sources et licences FR+EN ;  # v42 (t407u): +22 (Collections et Matériaux FR+EN) ; v39 (t391u): +52 fiches de complétion FR+EN ; v38 (t361u): +96 zones FR+EN ; v37 (t355u): +22 bestiaire/poissons FR+EN ; v36 (t351u): +30 listes FR+EN ; v35 (t347u): +2 factions ; v33: +8 lot 2 ; v32: +14 lot 1 ; v31: +4 ; v30: +4 ; v23: + article 03 ; v10's 52 + v17's 18 + v22 Priest, launch notes, gamepad FR/EN
        self.assertTrue(self.V10_CORRECTED<=set(reference['pages']) and self.V15_KEPT<=set(reference['pages']))
        normalized={}
        for file in WIKI_ROOT.rglob('index.html'):
            blocks=article_blocks(file.read_text())
            if blocks:
                normalized[str(file.relative_to(WIKI_ROOT))]=hashlib.sha256('\n'.join(self.v14_sources_form(b) for b in blocks).encode()).hexdigest()
        for page,digest in reference['pages'].items():
            if page in redirects:
                continue
            with self.subTest(page=page):
                # v20: the beta recap (FR + EN) gains the November 2 development-notes section, approved by Mathieu.
                if page in self.V10_CORRECTED|self.V15_KEPT|self.V22_GOLIVE|self.V22_UPDATED|(self.V23_UPDATED&set(reference['pages'])-self.V22_UPDATED-self.V10_CORRECTED-self.V15_KEPT)|self.V28_UPDATED|self.V30_UPDATED|self.V38_UPDATED|{'fr/actualites/beta-forever-bilan/index.html','en/news/forever-beta-recap/index.html'}:
                    self.assertNotEqual(normalized[page],digest)
                else:
                    self.assertEqual(normalized[page],digest)
        for page in ('fr/actualites/le-discord-officiel-wow-portal-room-accueille-les-joueurs-forever/index.html',
                     'en/news/official-wow-portal-room-discord-welcomes-forever-players/index.html'):
            self.assertIn(page,reference['pages'])
            self.assertNotIn(page,self.V10_CORRECTED)
            self.assertEqual(normalized[page],reference['pages'][page])
        # Official French names (news.blizzard.com fr-fr) on the corrected pages; the old wrong ones are gone everywhere.
        text=lambda page:(WIKI_ROOT/page).read_text()
        for name in ('Excavations','La cité Submergée','Bastion Krol’dok','Repaire des Noiregueules'):
            self.assertIn(name,text('fr/donjons-raids/raids-et-donjons/index.html'))
        for name in ('Sculpte-vents','Ordre suprême','Mur-Céleste'):
            self.assertIn(name,text('fr/races/les-eolides/index.html'))
        for file in (WIKI_ROOT/'fr').rglob('index.html'):
            body=file.read_text()
            for old in ('Site de fouilles','Cité engloutie','Bastion des Blackmaw','Façonneur de vents','Planélion'):
                self.assertNotIn(old,body,str(file))

    def test_v31_official_entries(self):
        # v31 (Mathieu pt330u/pt331u/pt334u): two new articles and the Taldramir French name. Facts stay sourced;
        # the November 10 tuning is announced only; the November 8 dungeon XP hotfix is already deployed and is not
        # on news.blizzard 24315281 yet. No fourth article.
        text=lambda page:(WIKI_ROOT/page).read_text()
        tuning=text('fr/actualites/equilibrage-classes-10-novembre/index.html')
        hot=text('fr/actualites/correctifs-forever-5-et-6-novembre/index.html')
        tal=text('fr/actualites/forging-forever-taldramir-premiere-legendaire/index.html')
        en_hot=text('en/news/forever-hotfixes-november-5-6/index.html')
        # v35 (t347u): the 10 Nov tuning is now on the official hotfix list (applied); additional class hotfixes on 11 Nov.
        self.assertIn('figure dans la liste officielle des correctifs', tuning)
        self.assertIn('11 novembre', tuning)
        en_tuning=text('en/news/class-tuning-november-10/index.html')
        self.assertIn('official November 10 hotfix list', en_tuning)
        self.assertIn('November 11', en_tuning)
        self.assertIn('hreflang="fr" href="../../../fr/actualites/equilibrage-classes-10-novembre/"', en_tuning)
        for page in (hot, en_hot):
            self.assertIn('24315281', page)
            self.assertIn('2406595', page)
            self.assertIn('640598', page)
            self.assertNotIn('[src:', page)
            self.assertIn('name="robots" content="noindex', page)
        self.assertIn('6 novembre', hot)
        self.assertIn('November 6', en_hot)
        self.assertIn('17 novembre', hot)
        self.assertIn('November 17', en_hot)
        self.assertIn('hôtel des ventes', hot)
        self.assertIn('Auction House', en_hot)
        self.assertIn('50 %', hot)
        self.assertIn('20:05', hot)
        self.assertIn('1 cuivre', hot)
        self.assertIn('réapparition', hot)
        self.assertIn('+50%', en_hot)
        self.assertIn('11:05 PST', en_hot)
        self.assertIn('not a reduction in its purchase price', en_hot)
        self.assertIn('respawn timing', en_hot)
        self.assertIn('le bois des murmures', tal)
        self.assertIn('the Whispering Wood', text('en/news/forging-forever-taldramir-first-legendary/index.html'))
        self.assertIn('quelles classes', tal)
        self.assertFalse(any('sitemap' in path.name.lower() for path in WIKI_ROOT.rglob('*')))

    def test_v40b_hotfixes_nov16(self):
        # v40b (Oui de Mathieu t404u, 17/11/2026): the « Correctifs Forever » article (same URL, no new page) gains the
        # official November 16 hotfix batch (news.blizzard 24315281, Kaivax US 2403040 #11 / EU 639885 #10).
        # Nothing about player-reported exploits; the Auction House changes stay « à confirmer ».
        text=lambda page:(WIKI_ROOT/page).read_text()
        hot=text('fr/actualites/correctifs-forever-5-et-6-novembre/index.html')
        en_hot=text('en/news/forever-hotfixes-november-5-6/index.html')
        self.assertIn('Correctifs Forever du 5 au 23 novembre', hot)  # v43c: titre étendu (lots des 17, 19, 20 novembre)
        self.assertIn('Forever hotfixes, November 5–23', en_hot)
        for page in (hot, en_hot):
            self.assertIn('id="details-nov16"', page)
            self.assertIn('href="#details-nov16"', page)
            self.assertIn('https://news.blizzard.com/en-us/article/24315281"', page)
            self.assertIn('https://us.forums.blizzard.com/en/wow/t/2403040/11', page)
            self.assertIn('https://eu.forums.blizzard.com/en/wow/t/639885/10', page)
            self.assertIn('id="source-16"', page)
            self.assertNotIn('id="source-31"', page)  # v43d: sources 17 à 30
            self.assertIn('Vampiric Embrace', page)
            self.assertIn('Windfury Totem', page)
            self.assertNotRegex(re.sub(r'<ol class="source-list">.*?</ol>', '', page, flags=re.S), r'(?i)exploit|streamer')  # v43d: titre officiel du fil Kaivax « Lockbox exploit… » cité en source
        self.assertIn('de 20 % à 10 %', hot); self.assertIn('from 20% to 10%', en_hot)
        self.assertIn('Entrée en vigueur effective des changements de l’hôtel des ventes', hot)
        for lang, label in (('fr', 'Correctifs Forever du 5 au 23 novembre'), ('en', 'Forever hotfixes, November 5–23')):
            home=text(f'{lang}/index.html')
            self.assertIn(label, home)
            self.assertIn('datetime="2026-11-17"', home)
        stale=[str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*.html') if 'du 5 au 14 novembre' in p.read_text() or 'November 5–14' in p.read_text()]
        self.assertEqual(stale, [])

    def test_v43c_hotfixes_blackmaw_podcast(self):
        # v43c (2026-11-24): « Correctifs Forever » gains the official hotfix batches of November 17, 19 and 20 (news.blizzard 24315281,
        # Kaivax US 2403040 #12-#14 / EU 639885 #11-#13); new Blackmaw Hold article FR/EN; official podcast episode 8 (24317086).
        text=lambda page:(WIKI_ROOT/page).read_text()
        hot=text('fr/actualites/correctifs-forever-5-et-6-novembre/index.html')
        en_hot=text('en/news/forever-hotfixes-november-5-6/index.html')
        for page in (hot, en_hot):
            for d in ('nov17','nov19','nov20','nov23'):
                self.assertIn(f'id="details-{d}"', page); self.assertIn(f'href="#details-{d}"', page)
            self.assertIn('id="problemes-en-cours"', page); self.assertIn('href="#problemes-en-cours"', page)
            for u in ('us.forums.blizzard.com/en/wow/t/2403040/12','us.forums.blizzard.com/en/wow/t/2403040/13','us.forums.blizzard.com/en/wow/t/2403040/14','us.forums.blizzard.com/en/wow/t/2403040/15',
                      'eu.forums.blizzard.com/en/wow/t/639885/11','eu.forums.blizzard.com/en/wow/t/639885/12','eu.forums.blizzard.com/en/wow/t/639885/13','eu.forums.blizzard.com/en/wow/t/639885/14',
                      'us.forums.blizzard.com/en/wow/t/2426335/4','eu.forums.blizzard.com/en/wow/t/645296/2','us.forums.blizzard.com/en/wow/t/2424420/2','eu.forums.blizzard.com/en/wow/t/642667/11'):
                self.assertIn('https://'+u+'"', page)
            self.assertIn('id="source-30"', page); self.assertNotIn('id="source-31"', page)
            self.assertIn('Feralheart', page); self.assertIn('Mortal Strike', page)
            self.assertNotRegex(page, r'(?i)streamer')
            self.assertNotIn('Lots des 5, 6, 8, 9, 10 et 11 novembre', page)
            self.assertNotIn('Batches of November 5, 6, 8, 9, 10 and 11', page)
        stale=[str(p.relative_to(WIKI_ROOT)) for p in WIKI_ROOT.rglob('*.html') if 'du 5 au 16 novembre' in p.read_text() or 'November 5–16' in p.read_text() or 'du 5 au 20 novembre' in p.read_text() or 'November 5–20' in p.read_text()]
        self.assertEqual(stale, [])
        bm=text('fr/actualites/sanctions-abus-blackmaw-hold/index.html'); en_bm=text('en/news/blackmaw-hold-abuse-actions/index.html')
        self.assertIn('Repaire des Noiregueules', bm); self.assertIn('Blackmaw Hold', en_bm)
        self.assertIn('href="../../../fr/donjons-raids/repaire-des-noiregueules/"', bm)
        self.assertIn('href="../../../en/dungeons-raids/blackmaw-hold/"', en_bm)
        for page in (bm, en_bm):
            self.assertIn('<meta name="robots" content="noindex,nofollow">', page)
            self.assertIn('https://us.forums.blizzard.com/en/wow/t/2419757"', page); self.assertIn('https://eu.forums.blizzard.com/en/wow/t/643759"', page)
            self.assertNotIn('[src:', page)
        for page in (text('fr/actualites/le-podcast-officiel-wow-forever/index.html'), text('en/news/the-official-wow-forever-podcast/index.html')):
            self.assertIn('https://news.blizzard.com/en-us/article/24317086"', page); self.assertIn('id="source-8"', page)
        self.assertIn('fr/actualites/sanctions-abus-blackmaw-hold/', text('fr/index.html'))
        self.assertIn('en/news/blackmaw-hold-abuse-actions/', text('en/index.html'))
        for lang, page in (('fr','fr/actualites/sanctions-abus-blackmaw-hold/'),('en','en/news/blackmaw-hold-abuse-actions/')):
            d=json.loads((WIKI_ROOT/f'search-detail-{lang}.json').read_text())
            self.assertEqual(len(d['pages']),221); self.assertIn(page,[p[0] for p in d['pages']])
            self.assertIn(page,(WIKI_ROOT/'search-index.json').read_text())

    def test_shared_header(self):
        css=(WIKI_ROOT/'theme-wow.css').read_text()
        self.assertIn('url(assets/v25-map-azeroth-1280.webp)',css); self.assertNotIn('url(assets/v24-banner',css)   # v25: bandeau + cadre = même carte
        self.assertNotRegex(css,r'https?:|@import')   # v24: image auto-hébergée, aucun hôte externe
        self.assertLess((WIKI_ROOT/'assets/v25-map-azeroth-1280.webp').stat().st_size,150_000)
        fh=(ROOT/'community/templates/_v2_header.html').read_text(); self.assertIn('<span class="wk-wordmark">Wowkipedia</span>',fh); self.assertNotIn('v2-tagline',fh)
        # One shared header on every page: brand, menu, search overlay, FR/EN switch, Discord sign-in, no inline script/style.
        pages=list(WIKI_ROOT.rglob('index.html'))
        self.assertEqual(len(pages),477)  # v43c: +2 article Blackmaw FR+EN  # v43 (t418u): +2 Sources et licences FR+EN  # v42 (t407u): +2 Collections FR+EN +20 Matériaux FR+EN ; v39 (t391u): +52 pages (26 fiches de complétion FR+EN) ; v38 (t361u): +96 zones FR+EN ; v37 (t355u): +22 bestiaire/poissons FR+EN ; v36 (t351u): +30 listes FR+EN ; v35 (t347u): +2 factions ; v33: +8 lot 2 ; v32: +14 lot 1
        for file in pages:
            text=file.read_text()
            with self.subTest(path=str(file.relative_to(WIKI_ROOT))):
                self.assertEqual(text.count('data-wk-header'),1); self.assertEqual(text.count('id="wk-search"'),1)
                # v21: project renamed « Wowkipedia » (text/CSS wordmark, no image)
                # v24: bandeau carte du monde + « WOWKIPEDIA » seul (majuscules en CSS), plus de slogan ni d'emblème dans le bandeau
                self.assertIn('<a class="wk-brand v24-brand" href="',text); self.assertIn('<span class="wk-wordmark">Wowkipedia</span>',text)
                self.assertNotIn('v2-tagline',text.split('</header>',1)[0])
                main=text[text.find('<main'):]
                if 'class="v2-banner' in main or 'class="v2-hero"' in main:
                    # v25: cadre sous le bandeau = suite de la carte, sans image de démonstration ni légende
                    self.assertIn('<div class="v2-banner-art v25-map" aria-hidden="true"></div>' if 'class="v2-banner' in main else '<div class="v2-hero-art v25-map" aria-hidden="true"></div>',main)
                    self.assertNotIn('v2-hero-cap',main); self.assertNotIn('<figure class="v2-banner-art">',main)
                self.assertNotIn('WoW Forever Wiki',text.split('<main',1)[0])
                self.assertIn('id="wk-search" role="dialog" aria-modal="true"',text)
                self.assertRegex(text,r'<a class="wk-lang" href="[^"]+" hreflang="(fr|en)"')
                self.assertEqual(len(re.findall(r'<a class="wk-discord" href="/account/" data-community-link>',text)),2)
                self.assertRegex(text,r'<script type="module" src="(\./|(\.\./)+)wk-header\.js\?v=42c"></script>')  # v42c (t412u/t413u): versioned URL
                self.assertIsNone(re.search(r'<script(?![^>]*(\bsrc="|type="application/json"))[^>]*>',text))
                self.assertNotIn(' style="',text)
                self.assertNotIn('<style',text)
        index=json.loads((WIKI_ROOT/'search-index.json').read_text())
        ids={entry['id'] for entry in index['entries']}
        self.assertEqual(len(ids),221)  # v43c: +1 article Blackmaw ;  # v42 (t407u): +1 fiche Collections +10 fiches Matériaux ; v39 (t391u): +26 fiches de complétion ; v38 (t361u): +48 fiches de zones ; v37 (t355u): +10 bestiaire +1 poissons ; v36 (t351u): +12 recettes +3 collections ; v35 (t347u): + factions JcJ ; v33: +4 lot 2 ; v32: +7 lot 1
        self.assertTrue({'forever-reputations-confirmed','forever-exploration-named-places','forever-creatures-official-notes','forever-items-loot-appearances'}<=ids)  # v33 lot 2
        self.assertTrue({'forever-legacy-challenges','forever-legacy-perks','forever-legacy-rewards','forever-camp-features','forever-professions-overview','forever-quest-rewards-expanded','forever-questline-gelkis-magram'}<=ids)  # v31: +2 ; v30: +2 ; v23: + article 03 ; v22: + CL3 Priest, launch article, launch notes, gamepad ; v17 guides
        self.assertTrue({'guide-debutant-avant-de-jouer','guide-debutant-histoire-eolides','guide-debutant-jouer-a-plusieurs','forever-news-class-tuning-nov10','forever-news-hotfixes-nov5-6','forever-news-forging-forever-taldramir','forever-news-pvp-faction-balance'}<=ids)
        self.assertFalse({'forever-news-beta','forever-news-podcast-tech'}&ids); self.assertIn('forever-news-golive-nov4',ids)  # v22: golive republished
        self.assertTrue(all(entry['status']=='published' and entry['publicationValidated'] is True for entry in index['entries']))
        self.assertEqual(self.get('/search-index.json').status_code,200)
        for lang in ('fr','en'):  # v42b (t409u/t410u): detailed search index, allowlisted and well formed
            response=self.get(f'/search-detail-{lang}.json'); self.assertEqual(response.status_code,200)
            detail=json.loads(response.data); self.assertEqual(detail['lang'],lang); self.assertGreater(len(detail['r']),15000)
            self.assertTrue(all(page[0].startswith(lang+'/') for page in detail['pages']))
        self.assertEqual(self.get('/search-detail-de.json').status_code,404)
        # v43 (t418u): interactive map files and credits data are served; nothing else in those folders
        self.assertEqual(self.get('/assets/carte/1411/donnees.json').status_code,200)
        self.assertEqual(self.get('/wk-map.js?v=43').mimetype,'text/javascript')
        g=self.get('/fr/sources-et-licences/donnees-polestar.json.gz')
        self.assertEqual((g.status_code,g.mimetype),(200,'application/gzip')); self.assertIn('attachment',g.headers['Content-Disposition'])
        for p in ('/assets/carte/1411/manifest.json','/assets/carte/1411/../../v2.css','/assets/carte/x/r0-c0.webp','/fr/sources-et-licences/autre.json.gz','/fr/zones/durotar/donnees.json'):
            self.assertEqual(self.get(p).status_code,404,p)
        for name in ('wk-header.js','ui-core.mjs','v2.css'):  # v42c (t412u/t413u): versioned asset URLs are served
            self.assertEqual(self.get(f'/{name}?v=42c').status_code,200)
        self.assertEqual(self.get('/wk-header.js').mimetype,'text/javascript')

    def test_v2_stylesheet_and_notice(self):
        # Every page loads exactly one self-hosted stylesheet (v2.css, same relative prefix as the header script),
        # never an external resource, and carries the mandatory Blizzard notice.
        for name in ('v2.css','theme-wow.css'):
            self.assertNotRegex((WIKI_ROOT/name).read_text(),r'(?i)@import|https?:|url\(\s*["\']?//|expression\(')
        theme=(WIKI_ROOT/'theme-wow.css').read_text()
        for rule in re.findall(r'(?m)^([^@/\s][^{]*)\{',theme):
            if not rule.startswith('.wk-theme'):
                self.assertTrue(all(sel.strip().startswith(('[data-theme=wow]','html[data-theme=wow]')) for sel in rule.split(',')),rule)
        js=(WIKI_ROOT/'theme.js').read_text()
        self.assertNotIn('wk-theme-txt',js); self.assertIn("localStorage.removeItem('wk-theme')",js)  # v22: single WoW Forever theme, no switcher
        self.assertIn('localStorage',js); self.assertNotRegex(js,r'document\.cookie|fetch\(|XMLHttpRequest|https?://(?!www\.w3\.org/2000/svg)')
        pages=list(WIKI_ROOT.rglob('index.html'))
        self.assertEqual(len(pages),477)  # v43c: +2 article Blackmaw FR+EN  # v43 (t418u): +2 Sources et licences FR+EN  # v42 (t407u): +2 Collections FR+EN +20 Matériaux FR+EN ; v39 (t391u): +52 pages (26 fiches de complétion FR+EN) ; v38 (t361u): +96 zones FR+EN ; v37 (t355u): +22 bestiaire/poissons FR+EN ; v36 (t351u): +30 listes FR+EN ; v35 (t347u): +2 factions ; v33: +8 lot 2 ; v32: +14 lot 1
        for file in pages:
            text=file.read_text()
            with self.subTest(path=str(file.relative_to(WIKI_ROOT))):
                links=re.findall(r'<link rel="stylesheet" href="([^"]+)">',text)
                # v20: v2.css, then the opt-in theme-wow.css (every rule scoped to html[data-theme=wow]) and the
                # self-hosted theme.js (classic script, CSP script-src 'self'; localStorage only).
                zone_map='wk-map.css?v=43' in text and '/zones/' in '/'+str(file.relative_to(WIKI_ROOT))  # v43 (t418u): zone pages load the map stylesheet
                self.assertEqual(len(links),3 if zone_map else 2)
                if zone_map: self.assertRegex(links[2],r'^(\.\./)+wk-map\.css\?v=43$')
                self.assertRegex(links[0],r'^(\./|(\.\./)+)v2\.css\?v=42c$')  # v42c (t412u/t413u): versioned URL
                self.assertRegex(links[1],r'^(\./|(\.\./)+)theme-wow\.css$')
                self.assertRegex(text,r'<script src="(\./|(\.\./)+)theme\.js"></script>')
                self.assertNotRegex(text,r'(?i)\b(src|srcset)="(https?:)?//|<link[^>]+href="(https?:)?//')  # no external resource (source links stay)
                self.assertIn('Site indépendant et non officiel de Blizzard Entertainment.',text)
        for path in ('/fr/le-jeu/','/en/the-game/','/fr/wiki/','/en/wiki/','/fr/classes/'):
            self.assertEqual(self.get(path).status_code,200,path)
        response=self.get('/v2.css')
        self.assertEqual((response.status_code,response.mimetype),(200,'text/css'))
        response=self.get('/assets/v2-hero-accueil-1280.webp')
        self.assertEqual((response.status_code,response.mimetype),(200,'image/webp'))
        # v11: AVIF variants of every illustration, each referenced by a page, served as image/avif
        avif={str(p.relative_to(WIKI_ROOT)) for p in (WIKI_ROOT/'assets').glob('*.avif')}
        # t390u : +28 AVIF (14 images du jeu © Blizzard × 640/1024 ; les 102 photos Wikimedia de t389u sont retirées), toutes référencées par une page de zone
        self.assertEqual(len(avif),115)
        referenced=set()
        for file in pages:
            referenced|=set(re.findall(r'assets/([a-z0-9-]+\.avif)',file.read_text()))
        self.assertTrue({'assets/'+name for name in referenced}<=avif)
        response=self.get('/assets/v2-hero-accueil-960.avif')
        self.assertEqual((response.status_code,response.mimetype),(200,'image/avif'))
        self.assertEqual(self.get('/assets/x.avif').status_code,404)
        self.assertEqual(self.get('/assets/x.woff').status_code,404)
        self.assertEqual(self.get('/site.css').status_code,404)

    def test_drafts_not_published(self):
        # AC2 (forever-news-beta) must remain an unpublished draft (v22: CL3 Priest published with Mathieu's « Oui »).
        for file in WIKI_ROOT.rglob('*.html'):
            text=file.read_text()
            self.assertNotIn('forever-news-beta"',text)
        self.assertTrue((WIKI_ROOT/'fr/classes/pretre-pretresse/index.html').is_file() and (WIKI_ROOT/'en/classes/priest/index.html').is_file())
        for file in WIKI_ROOT.rglob('*.html'):
            self.assertNotIn('BROUILLON',file.read_text())  # no local preview banner ever ships

    def test_source_allowlist_and_pages(self):
        for file in WIKI_ROOT.rglob('*'):
            if file.is_file():
                with self.subTest(path=file):
                    key=str(file.relative_to(WIKI_ROOT))
                    response=self.get('/'+key)
                    self.assertEqual(response.status_code,200)
                    if key.endswith('.jpg'):
                        self.assertEqual(response.mimetype,'image/jpeg')
                    if key.endswith('.mjs') or key.endswith('.js'):
                        self.assertEqual(response.mimetype,'text/javascript')
        self.assertEqual(self.get('/fr/zones/').status_code,200)
        redirect=self.get('/fr/zones')
        self.assertEqual((redirect.status_code,redirect.location),(308,'/fr/zones/'))
        self.assertIn('data-community-link',self.get('/fr/').text)
        for path in ['/community/app.py','/community/schema.sql','/instance/community.sqlite3','/.git/config','/.env',
                     '/requirements.txt','/install.sh','/assets/../community/app.py','/fr/../../community/app.py',
                     '/tests/wiki-baseline.json','/docs/REPORT.md','/deploy/wow4ever-staging.service','/qa/package.json',
                     '/wiki/index.html','/tools/integrate_wiki.py','/community/static/../app.py','/community/static/img/CREDITS.md',
                     '/fr/../community/app.py','/assets/style.css','/robots.txt','/fr/zones/index.json','/en/x/../../wiki/app.js']:
            self.assertEqual(self.get(path).status_code,404,path)
        self.assertEqual(self.get('/community/static/community.css').status_code,200)
        self.assertEqual(self.get('/community/static/img/default.svg').status_code,200)

    def test_csrf_origin_and_host(self):
        self.assertEqual(self.client.post('/community/new',base_url=BASE,data={}).status_code,403)
        self.assertEqual(self.post('/community/new',{'csrf':'é'}).status_code,403)
        self.assertEqual(self.post('/community/new',headers={'Origin':'https://evil.test'}).status_code,403)
        self.assertEqual(self.client.get('/community/',base_url='http://evil.test').status_code,400)
        self.assertEqual(self.get('/auth/discord').status_code,302)  # v14: one-click login start (GET), flow bound to this browser
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
        token=Mock(status_code=200); token.json.return_value={'access_token':'test-access','token_type':'Bearer','scope':'identify'}
        person=Mock(status_code=200); person.json.return_value={'id':'999999','username':'New user','avatar':None,'email':'must-not-be-saved'}
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
        response=Mock(status_code=200);response.json.return_value={'access_token':'test-access','token_type':'Bearer','scope':'guilds'}
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
            for path in ['/community/','/privacy/','/account/?manual','/account/']:
                response=client.get(path,base_url=BASE)
                self.assertEqual(response.status_code,302 if path=='/account/' else 200)
                self.assertFalse(any(header.startswith('forever-local=') for header in response.headers.getlist('Set-Cookie')))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM sessions').fetchone()[0],count)
        self.assertEqual(self.conn.execute('SELECT count(*) FROM rate_limits').fetchone()[0],0)

    def test_anonymous_login_csrf_and_lazy_session(self):
        client=self.app.test_client()
        form=client.get('/account/?manual',base_url=BASE)
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
            response=client.get('/account/?manual',base_url=BASE,headers=headers)
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
        for i in range(22):
            client=self.app.test_client()
            headers={'X-Forwarded-For':f'198.51.100.{i+1}'}
            peer={'REMOTE_ADDR':'203.0.113.50'}
            response=client.get('/account/?manual',base_url=BASE,headers=headers,environ_overrides=peer)
            csrf=re.search(r'name="csrf" value="([^"]+)"',response.text).group(1)
            result=client.post('/auth/discord',base_url=BASE,data={'csrf':csrf},headers=headers,environ_overrides=peer)
            self.assertEqual(result.status_code,302 if i<20 else 429)

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

    # v13: the forums use the wiki's v2 header/menu, typography, phone margins and footer (same files as the wiki).
    def test_forum_uses_wiki_v2_design(self):
        tid=self.new_topic()
        header=(ROOT/'community/templates/_v2_header.html').read_text(); footer=(ROOT/'community/templates/_v2_footer.html').read_text()
        page=(WIKI_ROOT/'fr/actualites/index.html').read_text()
        wiki_header=page[page.index('<header class="wk-header'):page.index('<main')].rstrip().replace('"../../','"/')
        # v17: the forum is deliberately left unchanged; the only allowed header difference is the « Bien débuter » count
        # (8 in the forum template, 17 in the wiki since the v17 beginner guides).
        # v39 BUILD DE TEST (UI t387u): the wiki gets the new header (search bar, fixed menu, side tree) but the forum must stay
        # unchanged (standing rule), so the byte-for-byte parity is replaced by: forum header = v38 template, unchanged; the
        # wiki header keeps every hook the shared wk-header.js drives (same script for both).
        # v39 (Oui de Mathieu t391u) : seuls les compteurs du menu changent (Classes 11, Donjons et raids 26, Objets 8, Quêtes et progression 23) ; v38 = 7a6042470a70c7122550713c9957a7f063040bdc60fa14ebe22c29bb3b2b6ed7
        self.assertEqual(hashlib.sha256(header.encode()).hexdigest(),'392336a1ff7a793f6a4600e2c73680921f4fe7c0f10dac9205be619572471756','forum header = v38 + compteurs v39 + Objets 9 (v41) + Métiers 28 (v42, t407u)')  # v39 = f3b4e04831147bfb0a3fb5460b8360b8ed97a418d08174540a2d4ea1410cc019
        for hook in ('data-wk-header','id="wk-nav"','id="wk-menu-toggle"','data-wk-search-open','class="wk-lang"','class="wk-discord"','class="wk-drawer-extra"','<span class="wk-wordmark">Wowkipedia</span>'):
            self.assertIn(hook,wiki_header,hook); self.assertIn(hook,header,hook)
        self.assertIn('Site indépendant et non officiel de Blizzard Entertainment.',footer)
        for path in ('/community/',f'/community/topics/{tid}','/privacy/','/notifications/',f'/community/profiles/1','/account/'):
            response=self.get(path); text=response.text
            with self.subTest(path=path):
                self.assertEqual(response.status_code,200)
                self.assertEqual(text.count('data-wk-header'),1); self.assertEqual(text.count('id="wk-search"'),1)
                self.assertIn('<link rel="stylesheet" href="/v2.css">',text)
                self.assertIn('<link rel="stylesheet" href="/community/static/forum-v2.css">',text)
                self.assertIn('<script type="module" src="/wk-header.js"></script>',text)
                self.assertIn('<body class="v2 community">',text)
                self.assertIn('<footer class="v2-footer">',text)
                self.assertIn('Site indépendant et non officiel de Blizzard Entertainment.',text)
                self.assertNotRegex(text,r'<script(?![^>]*\bsrc=")[^>]*>|<style|\sstyle="')
                self.assertNotIn('../',re.sub(r'<main.*</main>','',text,flags=re.S))
                self.assertIn("script-src 'self'",response.headers['Content-Security-Policy'])
        css=(ROOT/'community/static/forum-v2.css').read_text()
        self.assertNotRegex(css,r'@font-face|@import|https?:|Cinzel')
        self.assertEqual(self.get('/community/static/forum-v2.css').mimetype,'text/css')

    # ---- v14: one-click Discord login, remembered session, no avatar, clear diagnostics ----
    def discord_mocks(self,person=None,token_status=200,token_body=None):
        token=Mock(status_code=token_status); token.json.return_value=token_body or {'access_token':'test-access','token_type':'Bearer','scope':'identify'}
        who=Mock(status_code=200); who.json.return_value=person or {'id':'777777777','username':'mathieu','global_name':'Mathieu','avatar':'a_'+'b'*32}
        return token,who

    def test_v14_one_click_login_creates_account_and_returns_to_page(self):
        client=self.app.test_client()
        step=client.get('/account/',base_url=BASE,headers={'Referer':BASE+'/fr/actualites/'})
        self.assertEqual(step.status_code,302)
        self.assertEqual(step.location,'/auth/discord?next=%2Ffr%2Factualites%2F')
        start=client.get(step.location,base_url=BASE)
        self.assertEqual(start.status_code,302)
        url=urlsplit(start.location); args=parse_qs(url.query)
        self.assertEqual((url.scheme,url.netloc,url.path),('https','discord.com','/oauth2/authorize'))
        self.assertEqual(args['scope'],['identify']); self.assertEqual(args['redirect_uri'],[BASE+'/auth/discord/callback'])
        self.assertEqual(args['client_id'],['12345']); self.assertNotIn('client_secret',args)
        token,who=self.discord_mocks()
        with patch('community.app.requests.post',side_effect=[token,Mock()]),patch('community.app.requests.get',return_value=who) as get:
            done=client.get('/auth/discord/callback?state='+args['state'][0]+'&code=c',base_url=BASE)
        self.assertEqual((done.status_code,done.location),(302,'/fr/actualites/'))
        get.assert_called_once()  # users/@me only: the avatar CDN is never contacted
        user=self.conn.execute("SELECT * FROM users WHERE discord_id='777777777'").fetchone()
        self.assertEqual((user['name'],user['role'],user['avatar'],user['show_avatar']),('Mathieu','member',None,0))
        cookie=[h for h in done.headers.getlist('Set-Cookie') if h.startswith('forever-local=')][0]
        self.assertIn('Max-Age=2592000',cookie); self.assertIn('HttpOnly',cookie)
        page=client.get('/community/',base_url=BASE).text
        self.assertIn('<span>Mathieu<span class="visually-hidden"> · mon compte</span></span>',page)
        self.assertNotIn('Se connecter<span',page)
        account=client.get('/account/',base_url=BASE)
        self.assertEqual(account.status_code,200); self.assertIn('Vous restez connecté 30 jours',account.text)
        profile=client.get(f"/community/profiles/{user['id']}",base_url=BASE).text
        self.assertNotIn('<img',profile.split('<main',1)[1].split('</main>',1)[0])
        self.assertIn('class="avatar-initial"',profile)
        # second login: same account, nothing re-created, still no avatar
        start=client.get('/auth/discord',base_url=BASE); state=parse_qs(urlsplit(start.location).query)['state'][0]
        token,who=self.discord_mocks()
        with patch('community.app.requests.post',side_effect=[token,Mock()]),patch('community.app.requests.get',return_value=who):
            self.assertEqual(client.get('/auth/discord/callback?state='+state+'&code=c',base_url=BASE).location,'/community/')
        self.assertEqual(self.conn.execute("SELECT count(*) FROM users WHERE discord_id='777777777'").fetchone()[0],1)

    def test_v14_login_finishes_in_another_browser_but_not_in_a_foreign_session(self):
        start=self.app.test_client().get('/auth/discord',base_url=BASE)
        state=parse_qs(urlsplit(start.location).query)['state'][0]
        other=self.app.test_client()   # e.g. the phone comes back from the Discord app into another browser
        token,who=self.discord_mocks()
        with patch('community.app.requests.post',side_effect=[token,Mock()]),patch('community.app.requests.get',return_value=who):
            self.assertEqual(other.get('/auth/discord/callback?state='+state+'&code=c',base_url=BASE).status_code,302)
        self.assertIsNotNone(other.get_cookie('forever-local'))
        start=self.app.test_client().get('/auth/discord',base_url=BASE)
        state=parse_qs(urlsplit(start.location).query)['state'][0]
        with patch('community.app.requests.post') as network:   # self.client has its own (signed-in) session
            self.assertEqual(self.get('/auth/discord/callback?state='+state+'&code=c').status_code,400)
        network.assert_not_called()

    def test_v14_failures_are_explained_and_logged_without_secrets(self):
        cases=[('invalid_client',401,{'error':'invalid_client'},'Client Secret','HTTP 401 error=invalid_client'),
               ('invalid_grant',400,{'error':'invalid_grant'},'adresse de retour','HTTP 400 error=invalid_grant'),
               ('ratelimit',429,{'message':'x'},'limite temporairement','HTTP 429'),
               ('network',None,None,'joindre Discord','network error ConnectionError')]
        for name,status,body,message,log in cases:
            with self.subTest(case=name):
                client=self.app.test_client()
                start=client.get('/auth/discord',base_url=BASE); state=parse_qs(urlsplit(start.location).query)['state'][0]
                effect=[__import__('requests').ConnectionError('boom')] if status is None else [self.discord_mocks(token_status=status,token_body=body)[0]]
                with self.assertLogs(self.app.logger,'WARNING') as logs, patch('community.app.requests.post',side_effect=effect), patch('community.app.requests.get') as get:
                    r=client.get('/auth/discord/callback?state='+state+'&code=SECRET-CODE-123',base_url=BASE)
                self.assertEqual(r.status_code,502); get.assert_not_called()
                self.assertIn(message,r.text); self.assertIn('Réessayer la connexion',r.text)
                text='\n'.join(logs.output); self.assertIn(log,text)
                for leak in ('test-client-secret','SECRET-CODE-123',state):
                    self.assertNotIn(leak,text); self.assertNotIn(leak,r.text)
                if name=='invalid_client': self.assertIn('secret de l’application Discord doit être recollé',r.text)
        client=self.app.test_client()
        start=client.get('/auth/discord',base_url=BASE); state=parse_qs(urlsplit(start.location).query)['state'][0]
        with self.assertLogs(self.app.logger,'WARNING') as logs:
            r=client.get('/auth/discord/callback?state='+state+'&error=access_denied',base_url=BASE)
        self.assertEqual(r.status_code,400); self.assertIn('Connexion annulée',r.text); self.assertIn('access_denied',logs.output[0])
        with self.assertLogs(self.app.logger,'WARNING') as logs:
            r=self.app.test_client().get('/auth/discord/callback?state=old&code=x',base_url=BASE)
        self.assertEqual(r.status_code,400); self.assertIn('expiré',r.text); self.assertIn('no session cookie',logs.output[0])

    def test_v14_next_is_local_only(self):
        from community.app import safe_next
        for bad in ('//evil.test/','https://evil.test/','/auth/discord','/\\evil','/a/../b','x',''):
            self.assertIsNone(safe_next(bad),bad)
        self.assertEqual(safe_next('/fr/actualites/?page=2'),'/fr/actualites/?page=2')
        client=self.app.test_client()
        self.assertEqual(client.get('/account/',base_url=BASE,headers={'Referer':'https://evil.test/x'}).location,'/auth/discord?next=%2Fcommunity%2F')
        start=client.get('/auth/discord?next=//evil.test',base_url=BASE)
        self.assertEqual(self.conn.execute('SELECT next FROM oauth_next').fetchone()[0],'/community/')

    def test_v14_remembered_sessions(self):
        day=86400; stamp=int(time.time())
        for seen,created,user,valid in [(10*day,20*day,1,True),(31*day,40*day,1,False),(day,91*day,1,False),(2*3600,2*3600,None,False)]:
            with self.subTest(seen=seen,created=created,user=user):
                token=secrets.token_urlsafe(32)
                self.conn.execute('INSERT INTO sessions VALUES(?,?,?,?,?,?)',(digest(token),user,'c',stamp-created,stamp-seen,stamp-created)); self.conn.commit()
                client=self.app.test_client(); client.set_cookie('forever-local',token)
                r=client.get('/notifications/',base_url=BASE)
                self.assertEqual(r.status_code,200 if valid else 401)
                if valid:
                    self.assertIn('Max-Age=2592000',[h for h in r.headers.getlist('Set-Cookie') if h.startswith('forever-local=')][0])

    def test_v14_private_pages_need_a_session_not_a_password(self):
        client=self.app.test_client()
        for path in ('/notifications/','/moderation/'):
            self.assertEqual(client.get(path,base_url=BASE).status_code,401,path)
        self.assertEqual(client.get('/account/',base_url=BASE).status_code,302)
        self.sign_in(1)
        self.assertEqual(self.get('/moderation/').status_code,403)   # members never moderate
        self.sign_in(4)
        self.assertEqual(self.get('/moderation/').status_code,200)

    def test_v14_avatar_purged_and_never_fetched(self):
        self.conn.execute("UPDATE users SET avatar=?,show_avatar=1 WHERE id=1",('c'*32,))
        self.conn.execute('DELETE FROM migrations WHERE version=3'); self.conn.commit()
        create_app(dict(self.app.config))   # startup migration
        self.assertEqual(tuple(self.conn.execute('SELECT avatar,show_avatar FROM users WHERE id=1').fetchone()),(None,0))
        self.assertEqual(self.conn.execute('SELECT count(*) FROM migrations WHERE version=3').fetchone()[0],1)
        create_app(dict(self.app.config))   # idempotent
        with patch('community.app.requests.get') as network:
            r=self.get('/community/profiles/1/avatar')
        network.assert_not_called()
        self.assertEqual((r.status_code,r.location),(302,'/community/static/img/default.svg'))
        for path in ('/community/profiles/1','/account/','/privacy/'):
            self.assertNotIn('avatar Discord',self.get(path).text)
        self.assertNotIn('show_avatar',self.get('/account/').text)

    def test_v14_claim_owner(self):
        self.assertNotEqual(self.runner.invoke(args=['claim-owner']).exit_code,0)   # an admin exists: refused
        self.conn.execute("UPDATE users SET role='member'"); self.conn.execute('UPDATE users SET last_login=last_login+100 WHERE id=2'); self.conn.commit()
        result=self.runner.invoke(args=['claim-owner'])
        self.assertEqual(result.exit_code,0,result.output); self.assertIn('Membre 2',result.output)
        self.assertEqual([r[0] for r in self.conn.execute("SELECT id FROM users WHERE role='admin'")],[2])

    def test_v14_selfcheck_never_prints_the_secret(self):
        import io, contextlib
        from community import selfcheck
        cases={'a'*64:'Public Key','Ab3_'*8:'format d’un Client Secret','x'*15+' '+'y'*16:'espaces','':'vide'}
        for value,expected in cases.items():
            with self.subTest(expected=expected):
                env=Path(self.tmp.name)/'env'
                env.write_text(f'PUBLIC_URL=https://wow4ever.raveforge.eu\nDISCORD_CLIENT_ID=1565699718397296672\nDISCORD_CLIENT_SECRET={value}\nTRUSTED_PROXY_IPS=127.0.0.1\n')
                out=io.StringIO()
                with contextlib.redirect_stdout(out):
                    code=selfcheck.main([str(env),'--offline'])
                text=out.getvalue()
                self.assertIn(expected,text); self.assertIn('https://wow4ever.raveforge.eu/auth/discord/callback',text)
                if value.strip(): self.assertNotIn(value.strip(),text)
                self.assertEqual(code,0 if expected.startswith('format') else 1)
        env.write_text('PUBLIC_URL=https://wow4ever.raveforge.eu\nDISCORD_CLIENT_ID=1565699718397296672\nDISCORD_CLIENT_SECRET='+'Ab3_'*8+'\n')
        answers={'/gateway':(200,b'{}'),'/oauth2/token':(401,b'{"error": "invalid_client"}')}
        with patch.object(selfcheck,'request',side_effect=lambda url,data=None,timeout=10: answers[url.split('/v10',1)[1]]):
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(selfcheck.main([str(env)]),1)
        self.assertIn('invalid_client',out.getvalue()); self.assertIn('WOW4EVER_DISCORD_CHECK_PROBLEME',out.getvalue())
        self.assertNotIn('Ab3_Ab3_',out.getvalue())


if __name__=='__main__':
    unittest.main()


class RpV20Test(CommunityTest):
    """v20: RP charter, category intro, character-sheet template, derived ranks/badges and role cockpits."""
    def rp_salon(self,name):
        self.sign_in(4)
        self.assertEqual(self.post('/moderation/categories',{'name':name,'description':'Salon RP','position':'1'}).status_code,302)
        return self.conn.execute('SELECT id FROM categories WHERE name=?',(name,)).fetchone()[0]

    def test_charter_template_and_intro(self):
        text=self.get('/community/').get_data(as_text=True)
        self.assertIn('CHARTE DU JEU DE RÔLE',text); self.assertIn('((je serai absent ce soir))',text)
        self.assertIn('Modèle de fiche de personnage',self.get('/community/new').get_data(as_text=True))
        cid=self.rp_salon('Présentation de personnages')
        self.assertEqual(self.conn.execute('SELECT position FROM categories WHERE id=?',(cid,)).fetchone()[0],1)
        self.assertIn('Salon RP',self.get(f'/community/?category={cid}').get_data(as_text=True))

    def test_ranks_badges_and_cockpit_permissions(self):
        cid=self.rp_salon('Présentation de personnages')
        self.sign_in(1)
        self.assertEqual(self.post('/community/new',{'title':'Fiche : exemple','body':'Nom : exemple de test','category':str(cid)}).status_code,302)
        page=self.get('/community/profiles/1').get_data(as_text=True)
        self.assertIn('Recrue',page); self.assertIn('3 points RP',page); self.assertIn('is-earned',page)
        c=self.get('/community/cockpit/').get_data(as_text=True)
        self.assertIn('Mes personnages',c); self.assertNotIn('File de modération',c); self.assertNotIn('Dernières actions sensibles',c)
        self.sign_in(3); c=self.get('/community/cockpit/').get_data(as_text=True)
        self.assertIn('File de modération',c); self.assertNotIn('Dernières actions sensibles',c)
        self.sign_in(4); self.assertIn('Dernières actions sensibles',self.get('/community/cockpit/').get_data(as_text=True))
        self.client.delete_cookie('forever-local')
        self.assertEqual(self.get('/community/cockpit/').status_code,401)


# RpV20Test reuses CommunityTest's fixtures only: do not run the inherited tests a second time.
for _name in [n for n in dir(CommunityTest) if n.startswith('test_') and n not in RpV20Test.__dict__]:
    setattr(RpV20Test, _name, None)
