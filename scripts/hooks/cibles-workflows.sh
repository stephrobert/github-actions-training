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
#
# UN WORKFLOW DE SOLUTION CHIFFRÉ N'EST PAS ANALYSABLE
#
# Les solutions sont chiffrées par ansible-vault. actionlint et zizmor
# liraient « $ANSIBLE_VAULT;1.1;AES256 » et rendraient « "on" section is
# missing » : un échec qui ne parle pas de chiffrement et qu'on ne peut pas
# corriger côté workflow. Ces répertoires sont donc écartés, et le dire sur
# STDERR est important : stdout est la liste des cibles, un avertissement y
# deviendrait un chemin à analyser.
#
# Ce qui reste couvert, et par quoi : l'exemplarité des solutions (actions
# épinglées sur un SHA, bloc `permissions` déclaré) est contrôlée par
# `tests/test_solutions_exemplaires.py`, qui DÉCHIFFRE. C'est là que vit la
# valeur pédagogique du contrôle. Et la syntaxe du workflow de solution est
# éprouvée autrement, et mieux : le cycle local le fait jouer par `act`.
set -euo pipefail

cibles=()
[ -d .github/workflows ] && cibles+=(.github/workflows)

ecartes=0
while IFS= read -r -d '' dossier; do
    chiffres=0
    lisibles=0
    for workflow in "$dossier"/*.y*ml; do
        [ -e "$workflow" ] || continue
        if head -c 14 "$workflow" | grep -q 'ANSIBLE_VAULT'; then
            chiffres=$((chiffres + 1))
        else
            lisibles=$((lisibles + 1))
        fi
    done
    if [ "$lisibles" -eq 0 ] && [ "$chiffres" -gt 0 ]; then
        ecartes=$((ecartes + 1))
        continue
    fi
    cibles+=("$dossier")
done < <(find labs -type d -path '*/solution/.github/workflows' -print0 2>/dev/null | sort -z)

if [ "$ecartes" -gt 0 ]; then
    printf '%s répertoire(s) de solution écarté(s) : workflows chiffrés, donc non analysables. Leur exemplarité est contrôlée par tests/test_solutions_exemplaires.py, qui déchiffre.\n' "$ecartes" >&2
fi

printf '%s\n' "${cibles[@]+"${cibles[@]}"}"
