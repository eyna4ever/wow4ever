#!/bin/bash
# v42 (t407u) : chaîne complète, TEST uniquement (rien n'est publié ni déployé). Base : pipeline v41 (Collections) sous /tmp.
set -euo pipefail
O=/workspace/wowkipedia-v21-elite/v42-test/outils; P=/tmp/v42-pipeline; B=/tmp/v41-pipeline
cd $O
rm -rf $P/runtime && cp -a $B/runtime $P/runtime
cp $B/data/collections-v41.json $P/data/collections-v41.json; rm -f $O/../out/collections-v41.orig.json
python3 frag42.py $P; python3 gen_entries42.py $P
cd $P
node $O/apply-v42.mjs $P $O/../out/entries
node scripts/build-v2.mjs
