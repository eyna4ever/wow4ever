# Commandes serveur v43d (25/11/2026) — base v43b en ligne : releases/20261118T005337, wiki c82421613a35….
# NE PAS LANCER sans le « Oui » explicite de Mathieu.
cd /root
curl -fsSLo u43d.sh https://github.com/eyna4ever/wow4ever/releases/download/deploy-v5-20261030/update-v43d.sh
sha256sum u43d.sh   # attendu : 8ee4c1fc97a40f4b0cd62972d7944d473e0ae9ca7c015391d187ef6b8195a295
W43D_URL=https://github.com/eyna4ever/wow4ever/releases/download/deploy-v5-20261030/wow4ever-wiki-v43d.tar.gz bash u43d.sh </dev/null >u43d.log 2>&1; echo CODE $?
tail -n 15 u43d.log
# attendu : update-v43d.sh 8ee4c1fc97a40f4b0cd62972d7944d473e0ae9ca7c015391d187ef6b8195a295 ; archive 454a7aa35509e3fd09ff14a4a87a73088946c529af39b8b54e0aaab18c50a9db (vérifiée par le script)
# Succès : WOW4EVER_UPDATE_V43D_DONE · Retour arrière manuel vers la v43b : bash /root/wow4ever-rollback-v43d.sh
