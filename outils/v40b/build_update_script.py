#!/usr/bin/env python3
"""Fabrique v40b-deploy/update-v40b.sh à partir de update-v40.sh (même structure, même sécurité)."""
import sys
from pathlib import Path
B=Path(__file__).resolve().parent.parent
changed=(B/'changed-files.txt').read_text().split()
s=(B/'../v40-test/v40-deploy/update-v40.sh').read_text()
def rep(old,new,count=1):
    global s
    c=s.count(old); assert c==count,(old[:90],c); s=s.replace(old,new)
head_old=s[:s.index('set -eEuo pipefail')]
s=(B/'outils/header-v40b.txt').read_text()+s[len(head_old):]
rep('R="${W40_ROOT:-}"','R="${W40B_ROOT:-}"')
rep('NAME=wow4ever-wiki-v40.tar.gz','NAME=wow4ever-wiki-v40b.tar.gz')
rep('SUM=ac0202014e7dd0e0fb2e62c3e1cc6790c310134455029b127c499b8e20eae9b7','SUM='+sys.argv[1])
rep('URL="${W40_URL:-}"','URL="${W40B_URL:-}"')
rep('CF="${W40_CADDYFILE:-$R/etc/caddy/Caddyfile}"','CF="${W40B_CADDYFILE:-$R/etc/caddy/Caddyfile}"')
rep('[ -n "$URL" ] || die "archive absente de $TMP et W40_URL non défini."','[ -n "$URL" ] || die "archive absente de $TMP et W40B_URL non défini."')
rep('BK=$R/root/wow4ever-v40-backup-$TS','BK=$R/root/wow4ever-v40b-backup-$TS')
rep('LOG=$R/root/wow4ever-v40-$TS.log','LOG=$R/root/wow4ever-v40b-$TS.log')
rep('RBS=$R/root/wow4ever-rollback-v40.sh','RBS=$R/root/wow4ever-rollback-v40b.sh')
rep('RBLIST="39 38 37 36 35 34 33 32 31 30"','RBLIST="40 39 38 37 36 35 34 33 32 31 30"')
rep('''V39REL=releases/20261116T225702
V39TAR=e1ec85bf95e7b62009bc2616b66d9743b32f19c49ffce19937549922e66b2b5d
V40TAR=f208c6cf2fdffe66e5d79203f57ebf845c310dfada3f36f73059d29b49510ab5
V39CSS=411b05b487e795aa97c2b96fbb2b36112ed723644bda887af41755fec017f967
''','''V40REL=releases/20261117T013451
V40TAR=f208c6cf2fdffe66e5d79203f57ebf845c310dfada3f36f73059d29b49510ab5
V40BTAR=e5ecbb6c60bd503a30831ccc22a27afa7e6b2318a73ea50674fe456581a291ce
V40CSS=0758ffb0d1488471d4f24e73f9448f5e25420f6672ad9496bbd9983662a99d25
''')
rep('CHANGED="wiki/v2.css wiki/fr/index.html wiki/en/index.html tests/test_community.py tests/wiki-baseline.json"',
    'CHANGED="'+' '.join(changed)+'"\nNCHANGED='+str(len(changed)))
for v in ['W40_SCHEME','W40_PORT','W40_RPORT','W40_TEST_FAIL','W40_EXPECT_OLD','W40_TEST']:
    s=s.replace(v,v.replace('W40_','W40B_'))
assert 'W40_' not in s, [l for l in s.splitlines() if 'W40_' in l]
rep('say "Retour arrière vers la v39 ($OLD)…"','say "Retour arrière vers la v40 ($OLD)…"')
rep('say "Retour arrière OK : v39 ($OLD) restaurée','say "Retour arrière OK : v40 ($OLD) restaurée')
rep('(v40 déjà tentée ?)','(v40b déjà tentée ?)')
rep('''[ "$BASE" != "$V40TAR" ] || die "la v40 est déjà en ligne ($OLD) : rien modifié."''','''[ "$BASE" != "$V40BTAR" ] || die "la v40b est déjà en ligne ($OLD) : rien modifié."''')
rep('''[ "$BASE" = "$V39TAR" ] || die "la release actuelle n'est pas la v39 (wiki $BASE, attendu $V39TAR) : rien modifié."''','''[ "$BASE" = "$V40TAR" ] || die "la release actuelle n'est pas la v40 (wiki $BASE, attendu $V40TAR) : rien modifié."''')
rep('application différente de la v39','application différente de la v40')
rep('''[ "$(sha < "$OLDREL/wiki/v2.css")" = "$V39CSS" ] || die "wiki/v2.css n'est pas celle de la v39 : rien modifié."''','''[ "$(sha < "$OLDREL/wiki/v2.css")" = "$V40CSS" ] || die "wiki/v2.css n'est pas celle de la v40 : rien modifié."''')
rep("wiki/wk-header.js n'est pas celui de la v39","wiki/wk-header.js n'est pas celui de la v40")
rep("_v2_header.html n'est pas celui de la v39","_v2_header.html n'est pas celui de la v40")
rep('''say "   v39 reconnue (wiki $V39TAR, application, CSS, JS, schéma, en-tête, pied de page) : $OLD$([ "$OLD" = "$V39REL" ] && echo ' (release connue)' || echo " (release connue : $V39REL ; empreintes conformes)")"''',
    '''say "   v40 reconnue (wiki $V40TAR, application, CSS, JS, schéma, en-tête, pied de page) : $OLD$([ "$OLD" = "$V40REL" ] && echo ' (release connue)' || echo " (release connue : $V40REL ; empreintes conformes)")"''')
rep("la release v39 n'a pas 451 pages","la release v40 n'a pas 451 pages")
rep('''grep -vqE '^(wiki/(v2\\.css|fr/index\\.html|en/index\\.html)|tests/(test_community\\.py|wiki-baseline\\.json))$' <<<"$LIST" && die "archive : fichier inattendu."''',
    '''[ "$(LC_ALL=C sort <<<"$LIST")" = "$(tr ' ' '\\n' <<<"$CHANGED" | LC_ALL=C sort)" ] || die "archive : liste de fichiers inattendue."''')
rep('''[ "$(wc -l <<<"$LIST")" = 5 ] || die "archive : 5 fichiers attendus."''','''[ "$(wc -l <<<"$LIST")" = "$NCHANGED" ] || die "archive : $NCHANGED fichiers attendus."''')
rep('release-v39.tar.gz','release-v40.tar.gz',2)
rep('say "4/7 Nouvelle release (copie de $OLD + wiki v40)"','say "4/7 Nouvelle release (copie de $OLD + wiki v40b)"')
# python verification block replaced entirely
i=s.index('python3 - "$NEWREL" "$OLDREL" "$V40TAR"'); j=s.index('\nPY\n',i)+4
s=s[:i]+(B/'outils/verify-block-v40b.txt').read_text()+s[j:]
rep('say "   v40 : style journal de quêtes + accueil restructuré ; 451 pages, 209 fiches ; contenu des fiches identique à la v39 ; forum inchangé"',
    'say "   v40b : article Correctifs Forever FR/EN + lot du 16 novembre ; titre repris dans $((NCHANGED-5)) autres pages et l\'index ; 451 pages, 209 fiches ; v2.css et forum inchangés"')
rep('wow4ever-v40-tests-$TS.txt','wow4ever-v40b-tests-$TS.txt',3)
# rollback file
rep('''# Retour arrière v40 -> v39 : release $OLD (v39, $V39REL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v40.
# N'écrase aucun rollback-v39.sh … rollback-v30.sh. Sauvegarde : $BK''','''# Retour arrière v40b -> v40 : release $OLD (v40, $V40REL) et redémarrage du forum. Caddyfile et schéma non modifiés par la v40b.
# N'écrase aucun rollback-v40.sh … rollback-v30.sh. Sauvegarde : $BK''')
rep('echo WOW4EVER_ROLLBACK_V40_DONE','echo WOW4EVER_ROLLBACK_V40B_DONE')
# post checks: add article checks after Mulgore check
rep('''HM=$(get /fr/zones/mulgore/); echo "$HM" | grep -q 'Image du jeu © Blizzard Entertainment' || die "crédit image du jeu manquant sur Mulgore."''',
'''HM=$(get /fr/zones/mulgore/); echo "$HM" | grep -q 'Image du jeu © Blizzard Entertainment' || die "crédit image du jeu manquant sur Mulgore."
HA=$(get /fr/actualites/correctifs-forever-5-et-6-novembre/); echo "$HA" | grep -q 'id="details-nov16"' && echo "$HA" | grep -qF 'Correctifs Forever du 5 au 16 novembre' || die "article FR sans le lot du 16 novembre."
HB=$(get /en/news/forever-hotfixes-november-5-6/); echo "$HB" | grep -q 'id="details-nov16"' && echo "$HB" | grep -qF 'Forever hotfixes, November 5–16' || die "article EN sans le lot du 16 novembre."
echo "$HF" | grep -qF 'Correctifs Forever du 5 au 16 novembre' || die "accueil FR sans le nouveau titre."
say "   article Correctifs Forever FR/EN : lot du 16 novembre en ligne"''')
rep('say "7/7 Terminé (paquet appliqué localement${W40B_TEST:+ — mode test, pas de bascule production})"','say "7/7 Terminé (paquet appliqué localement${W40B_TEST:+ — mode test, pas de bascule production})"')
rep('say "Sauvegardes : $BK · Retour arrière : bash $RBS (-> $OLD / $V39REL)"','say "Sauvegardes : $BK · Retour arrière : bash $RBS (-> $OLD / $V40REL)"')
rep('say WOW4EVER_UPDATE_V40_DONE','say WOW4EVER_UPDATE_V40B_DONE')
assert 'V39REL' not in s and 'V39TAR' not in s and 'V39CSS' not in s, [l for l in s.splitlines() if 'V39' in l]
out=B/'v40b-deploy/update-v40b.sh'; out.write_text(s); out.chmod(0o755)
print('écrit', out)
