# APERÇU du retour arrière v43d -> v43b (le vrai /root/wow4ever-rollback-v43d.sh est écrit par update-v43d.sh).
set -euo pipefail
APP=/srv/wow4ever-app
OLD=releases/20261118T005337
SVC=wow4ever-community.service
[ -d $APP/$OLD/wiki ] && [ -f $APP/$OLD/community/selfcheck.py ] || { echo "ERREUR: $APP/$OLD absent ou incomplet"; exit 1; }
ln -sfn $OLD $APP/current.rb && mv -Tf $APP/current.rb $APP/current
systemctl restart $SVC
echo WOW4EVER_ROLLBACK_V43D_DONE
