#!/bin/bash
# v41 (t403u) : chaîne complète, test uniquement (rien n'est publié ni déployé).
set -euo pipefail
O=/workspace/wowkipedia-v21-elite/collections-v41/outils; P=/tmp/v41-pipeline; V=/workspace/wowkipedia-v21-elite/ui-v39-test/tree/pipeline
cd $O
python3 build_data.py; python3 icons.py; python3 gen_v41.py $P; python3 gen_entries.py
rm -rf $P/runtime && cp -a $V/runtime $P/runtime && rm -rf $P/runtime/backups && mkdir $P/runtime/backups
rm -f $P/public/v2/assets/icone-jeu-*.webp; python3 gen_v41.py $P >/dev/null
( cd $P && node $O/apply-test-v41.mjs $P $O/../out/entries && node scripts/build-v2.mjs )
python3 make_tree.py; python3 update_tests.py
