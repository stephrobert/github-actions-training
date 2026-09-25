#!/usr/bin/env bash
# actionlint sur les workflows du dépôt et sur les solutions, jamais sur les
# points de départ. Voir cibles-workflows.sh pour le pourquoi.
set -euo pipefail
cd "$(dirname "$0")/../.."

mapfile -t cibles < <(bash scripts/hooks/cibles-workflows.sh)
if [ ${#cibles[@]} -eq 0 ]; then
    echo "aucun répertoire de workflows à contrôler"
    exit 0
fi

fichiers=()
for dossier in "${cibles[@]}"; do
    while IFS= read -r -d '' f; do
        fichiers+=("$f")
    done < <(find "$dossier" -maxdepth 1 -type f \( -name '*.yml' -o -name '*.yaml' \) -print0)
done

if [ ${#fichiers[@]} -eq 0 ]; then
    echo "aucun workflow à contrôler"
    exit 0
fi

echo "actionlint sur ${#fichiers[@]} workflow(s)"
actionlint "${fichiers[@]}"
