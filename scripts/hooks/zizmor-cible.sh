#!/usr/bin/env bash
# zizmor sur les workflows du dépôt et sur les solutions, jamais sur les points
# de départ. Voir cibles-workflows.sh pour le pourquoi.
#
# `--offline` : le hook tourne sans réseau ni jeton. Les règles qui interrogent
# l'API (résolution d'un tag en SHA) s'abstiennent alors, et c'est la CI qui les
# joue, avec un jeton.
set -euo pipefail
cd "$(dirname "$0")/../.."

mapfile -t cibles < <(bash scripts/hooks/cibles-workflows.sh)
if [ ${#cibles[@]} -eq 0 ]; then
    echo "aucun répertoire de workflows à contrôler"
    exit 0
fi

echo "zizmor --offline sur ${#cibles[@]} répertoire(s)"
zizmor --offline --no-progress "${cibles[@]}"
