#!/bin/bash
# Essais à blanc du paquet v43 dans une fausse racine (/tmp/w43b-root), serveur local = vraie application Flask de la release pointée par current.
set -uo pipefail
P=/workspace/wowkipedia-v21-elite; D=$P/v43b-test/v43b-deploy; E=$P/v43b-test/essais; FR=/tmp/w43b-root
mkdir -p "$E"; rm -f "$E"/*.txt
STUB=/tmp/w43b-stub; mkdir -p $STUB; printf '#!/bin/sh\necho "stub systemctl $*"\n' > $STUB/systemctl; chmod +x $STUB/systemctl
setup(){ # $1 = arbre de base
  rm -rf $FR; mkdir -p $FR/etc/caddy $FR/root $FR/srv/wow4ever-app/releases
  printf 'wowkipedia.com {\n  reverse_proxy 127.0.0.1:8014\n}\n' > $FR/etc/caddy/Caddyfile; : > $FR/etc/wow4ever-community.env
  cp -a "$1" $FR/srv/wow4ever-app/releases/20261118T002429; mkdir -p $FR/srv/wow4ever-app/releases/20261118T002429/.venv/bin
  printf '#!/bin/sh\n' > $FR/srv/wow4ever-app/releases/20261118T002429/.venv/bin/gunicorn; chmod +x $FR/srv/wow4ever-app/releases/20261118T002429/.venv/bin/gunicorn
  ln -sfn releases/20261118T002429 $FR/srv/wow4ever-app/current
}
ENV=(PATH=$STUB:$PATH W43B_TEST=1 W43B_ROOT=$FR W43B_SCHEME=http W43B_PORT=:8784 W43B_RPORT=8784 W43B_EXPECT_OLD=releases/20261118T002429 W43B_URL=http://127.0.0.1:8786/wow4ever-wiki-v43b.tar.gz)
( cd $D && exec python3 -m http.server 8786 --bind 127.0.0.1 >/tmp/w43-http.log 2>&1 ) & HTTP=$!
sim_start(){ ( cd $P/v42c-test/tests-recherche && exec /workspace/venv-v10/bin/python sim_server42c.py $FR/srv/wow4ever-app 8784 >>$E/sim.log 2>&1 ) & SIM=$!; sleep 3; }
sim_stop(){ kill $SIM 2>/dev/null; wait $SIM 2>/dev/null; }
cur(){ echo "   [current -> $(readlink $FR/srv/wow4ever-app/current)]"; }
sleep 1
# 0) simulateur absent : contrôles après bascule en échec -> retour arrière automatique
setup $P/polestar-test/tree
env "${ENV[@]}" W43B_TEST_POST=1 bash $D/update-v43b.sh > $E/essai0-simulateur-absent-retour-arriere.txt 2>&1; echo "code $? $(cur)" >> $E/essai0-simulateur-absent-retour-arriere.txt
# 1) succès (contrôles après bascule contre la vraie application)
setup $P/polestar-test/tree; sim_start
env "${ENV[@]}" W43B_TEST_POST=1 bash $D/update-v43b.sh > $E/essai1-succes.txt 2>&1; echo "code $? $(cur)" >> $E/essai1-succes.txt
# 2) relance : refus (déjà tentée)
env "${ENV[@]}" W43B_TEST_POST=1 bash $D/update-v43b.sh > $E/essai2-refus-deja-tentee.txt 2>&1; echo "code $? $(cur)" >> $E/essai2-refus-deja-tentee.txt
# 3) retour arrière manuel
( PATH=$STUB:$PATH bash $FR/root/wow4ever-rollback-v43b.sh ) > $E/essai3-rollback.txt 2>&1; echo "code $? $(cur)" >> $E/essai3-rollback.txt
# 4) échec simulé après bascule -> retour arrière automatique
rm -f $FR/root/wow4ever-rollback-v43b.sh
env "${ENV[@]}" W43B_TEST_POST=1 W43B_TEST_FAIL=1 bash $D/update-v43b.sh > $E/essai4-echec-simule.txt 2>&1; echo "code $? $(cur)" >> $E/essai4-echec-simule.txt
sim_stop
# 5) SHA-256 faux
setup $P/polestar-test/tree; head -c 1000 /dev/urandom > $FR/root/wow4ever-wiki-v43b.tar.gz
env "${ENV[@]}" W43B_URL=http://127.0.0.1:8786/LIRE-MOI.txt bash $D/update-v43b.sh > $E/essai5-sha-faux.txt 2>&1; echo "code $? $(cur)" >> $E/essai5-sha-faux.txt
# 6) base v42b (pas la v42c) : refus
setup $P/v42c-test/tree
env "${ENV[@]}" bash $D/update-v43b.sh > $E/essai6-refus-base-v42c.txt 2>&1; echo "code $? $(cur)" >> $E/essai6-refus-base-v42c.txt
# 6b) release en ligne différente de releases/20261118T002429 : refus
setup $P/polestar-test/tree
env "${ENV[@]}" W43B_EXPECT_OLD=releases/20261118T999999 bash $D/update-v43b.sh > $E/essai6b-refus-release-inattendue.txt 2>&1; echo "code $? $(cur)" >> $E/essai6b-refus-release-inattendue.txt
# 7) sans W43B_TEST et pas root : refus
setup $P/polestar-test/tree
env PATH=$STUB:$PATH W43B_ROOT=$FR bash $D/update-v43b.sh > $E/essai7-refus-non-root.txt 2>&1; echo "code $? $(cur)" >> $E/essai7-refus-non-root.txt
kill $HTTP 2>/dev/null
for f in $E/essai*.txt; do echo "== $(basename $f)"; cat $f; done
