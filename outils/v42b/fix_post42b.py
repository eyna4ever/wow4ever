# t412u : correctif des contrôles après bascule (échec réel du 17/11/2026 23:42 Europe/Paris : « index détaillé FR illisible »).
# Cause : « get … | head -c 300 | grep » sous « set -o pipefail » : head ferme le tube après 300 octets, curl (1,2 Mo) sort en 23
# (« Failure writing output »), le tube échoue alors que le fichier servi est bon. Les contrôles lisent désormais un fichier ou une variable.
# Exécuté par make_deploy42b.py (variable s = texte de update-v42b.sh).
import re
a0 = s.index('[ "$(code /fr/ $HOST)" = 200 ] || die "/fr/ ne répond pas 200."')
a1 = s.index('\n', s.index('for p in $KEPT_FR $POD_FR $POD_EN', a0))
body = s[a0:a1]
OLD = """get /search-detail-fr.json | head -c 300 | grep -q '"lang":"fr"' || die "index détaillé FR illisible."
get /fr/zones/mulgore/ | grep -q 'id="r-baine-bloodhoof"' || die "ancre r-baine-bloodhoof absente de Mulgore."
HM=$(get /fr/zones/mulgore/); echo "$HM" | grep -q 'Image du jeu © Blizzard Entertainment' || die "crédit image du jeu manquant sur Mulgore."
"""
NEW = """for l in fr en; do json_ok /search-detail-$l.json $l || die "index détaillé $l illisible (JSON, langue ou taille)."; done
HM=$(get /fr/zones/mulgore/); grep -qF 'id="r-baine-bloodhoof"' <<<"$HM" || die "ancre r-baine-bloodhoof absente de Mulgore."
grep -qF 'Image du jeu © Blizzard Entertainment' <<<"$HM" || die "crédit image du jeu manquant sur Mulgore."
"""
assert body.count(OLD) == 1; body = body.replace(OLD, NEW)
body = re.sub(r'echo "\$(H[FEM])" \| grep (-qF?) (\'[^\']*\')', r'grep \2 \3 <<<"$\1"', body)
assert '| head' not in body and 'echo "$H' not in body, body
FUNCS = """# Contrôles du wiki après bascule (aussi lancés en mode test avec W42B_TEST_POST=1 contre un serveur local).
# Aucun « curl | head/grep » : sous pipefail, un lecteur qui s'arrête tôt fait échouer curl (code 23).
json_ok(){
  local f="$R/root/wow4ever-v42b-check-$2.json" n
  for n in $(seq 1 10); do
    if curl -fsS --compressed -m 60 "${RES[@]}" -o "$f" "$(U "$1")" && python3 - "$f" "$2" <<'PY'
import json,sys
d=json.load(open(sys.argv[1],encoding='utf-8'))
assert d.get('v')==1 and d.get('lang')==sys.argv[2] and len(d.get('r',[]))>15000 and len(d.get('pages',[]))==220
PY
    then rm -f "$f"; return 0; fi
    sleep 2
  done
  rm -f "$f"; return 1
}
wiki_checks(){
""" + body + "\n}\n\n"
s = s[:a0] + 'wiki_checks' + s[a1:]
k = s.index('say "5/7 Bascule'); s = s[:k] + FUNCS + s[k:]
TP = """if [ -n "${W42B_TEST:-}" ] && [ -n "${W42B_TEST_POST:-}" ]; then
  say "6/7 (test) Contrôles du wiki après bascule (serveur local $(U /))"
  wiki_checks
  [ -z "${W42B_TEST_FAIL:-}" ] || die "échec simulé (test)."
  say "   contrôles du wiki après bascule OK (test)"
fi
"""
k = s.index('STAGE="done"; trap - ERR'); s = s[:k] + TP + s[k:]
