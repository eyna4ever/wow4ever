#!/bin/sh
# Installe le wiki wow4ever.raveforge.eu sans toucher aux autres sites.
set -e
D=/var/www/wow4ever
if [ -d $D/.git ]; then git -C $D pull -q; else rm -rf $D; git clone -q https://github.com/eyna4ever/wow4ever.git $D; fi
C=/etc/caddy/Caddyfile
[ -f $C ] || { echo "ERREUR: $C introuvable. Envoie une capture a Wow4ever."; ls /etc/caddy; exit 1; }
if ! grep -q 'wow4ever.raveforge.eu' $C; then
  cp $C $C.avant-wow4ever
  printf '\nwow4ever.raveforge.eu {\n\troot * %s\n\tencode gzip\n\tfile_server\n}\n' $D >> $C
  if ! caddy validate --config $C --adapter caddyfile >/dev/null 2>&1; then
    cp $C.avant-wow4ever $C; echo "ERREUR: config refusee, rien n'a ete change."; exit 1
  fi
fi
systemctl reload caddy && echo "OK WOW4EVER EN LIGNE"
