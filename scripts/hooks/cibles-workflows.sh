#!/usr/bin/env bash
# Les répertoires de workflows sur lesquels l'exemplarité est due.
#
# POURQUOI PAS TOUT LE DÉPÔT
#
# Les points de départ des labs sont FAUTIFS PAR CONSTRUCTION : un
# `challenge/` peut porter une action non épinglée, `permissions: write-all` ou
# une injection de template, puisque c'est ce que l'apprenant doit corriger.
# Passer actionlint ou zizmor dessus rendrait un échec permanent, et la seule
# façon de le faire taire serait de retirer du lab ce qui fait le lab.
#
# L'exemplarité est due là où le dépôt parle en son nom : ses propres workflows,
# et les solutions de référence qu'il publie.
#
# `challenge/work` est le répertoire de travail de l'apprenant, jamais versionné
# et toujours en chantier : il n'est jamais contrôlé.
set -euo pipefail

cibles=()
[ -d .github/workflows ] && cibles+=(.github/workflows)

while IFS= read -r -d '' dossier; do
    cibles+=("$dossier")
done < <(find labs -type d -path '*/solution/.github/workflows' -print0 2>/dev/null | sort -z)

printf '%s\n' "${cibles[@]+"${cibles[@]}"}"
