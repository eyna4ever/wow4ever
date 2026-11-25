#!/usr/bin/env bash
# Après le « Oui » de Mathieu uniquement : republier les 28 fiches révisées (t359u),
# reconstruire le wiki, puis préparer le paquet update-v38 (empreinte wiki + tarball).
# Ne déploie pas. Ne pas lancer avant le Oui.
set -euo pipefail
TREE="$(cd "$(dirname "$0")/../test-tree-v38/pipeline" && pwd)"
IDS_FILE="$(cd "$(dirname "$0")" && pwd)/IDS.txt"
NOTE_SUBMIT='t359u : relire la révision (retrait de « à confirmer » sur les données du client 1.60.1.70862).'
NOTE_APPROVE='t359u Oui : validation humaine, identité, droits et traductions.'
NOTE_PUBLISH='t359u Oui : republication des fiches révisées, d’un seul tenant.'
cd "$TREE"
mapfile -t IDS < "$IDS_FILE"
for id in "${IDS[@]}"; do
  node scripts/review.mjs submit "$id" --actor Mathieu --note "$NOTE_SUBMIT"
  node scripts/review.mjs approve "$id" --actor Mathieu --note "$NOTE_APPROVE" \
    --confirm-human-review --confirm-identity --confirm-rights --confirm-translations
  node scripts/review.mjs publish "$id" --actor Mathieu --note "$NOTE_PUBLISH" --confirm-publish
  echo "published $id"
done
node scripts/check-data.mjs runtime/entries.json
npm test
# build-v2 n’écrit que les fiches publiées (les 2 brouillons news historiques restent hors wiki)
node scripts/build-v2.mjs
echo "Wiki reconstruit. Reste à : caler test_wiki_preservation sur le sha des fichiers wiki/,"
echo "fabriquer wow4ever-wiki-v38.tar.gz, écrire update-v38.sh (exige la release v37 20261112T150552,"
echo "rollback vers cette release, WOW4EVER_UPDATE_V38_DONE), uploader sur litterbox et vérifier les sha."
