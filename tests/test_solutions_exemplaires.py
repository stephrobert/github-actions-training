"""Les solutions de référence donnent l'exemple, et le dépôt le vérifie.

## Pourquoi ce contrôle existe

Ce catalogue enseigne l'épinglage par SHA et les permissions minimales. Une
solution de référence qui emploie `@v4` ou qui laisse le bloc `permissions`
absent enseigne le contraire de ce que son propre challenge exige, et personne
ne s'en apercevrait : les tests d'un lab notent le travail de l'apprenant, pas
la solution qu'on lui montre ensuite.

Mesuré le 2026-09-25 en écrivant `fondations-premier-workflow` : la solution de
référence rendait 80/100 à son propre challenge, recalée par zizmor sur
`artipacked`. Elle laissait le jeton du job dans `.git/config`, ce que la
tâche 4 interdit.

## Ce qu'il ne contrôle PAS, et c'est délibéré

Les points de départ, sous `labs/*/challenge/`. Ils sont fautifs par
construction : un challenge peut porter une action non épinglée, `write-all` ou
une injection, puisque c'est ce que l'apprenant doit corriger. Le seul endroit
où l'exemplarité est due est `solution/`, et `.github/` du dépôt.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
LABS = REPO / "labs"

# `uses: owner/repo@ref  # commentaire`, lu dans le TEXTE et non dans le YAML
# analysé : le commentaire de version disparaît à l'analyse, et c'est lui qu'on
# veut voir.
RE_USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^\s'\"#]+)['\"]?\s*(?:#\s*(.*?)\s*)?$")
RE_SHA = re.compile(r"^[0-9a-f]{40}$")

# Ce qu'un job de ce catalogue peut légitimement demander. Tout le reste est
# soit une erreur, soit un lab qui enseigne autre chose et qui le dira dans son
# propre test.
LECTURES = {"none", "read"}


def workflows_exemplaires() -> list[Path]:
    """Les workflows du dépôt et ceux des solutions, jamais les challenges."""
    fichiers = sorted((REPO / ".github" / "workflows").glob("*.y*ml"))
    for lab in sorted(LABS.iterdir()) if LABS.is_dir() else []:
        dossier = lab / "solution" / ".github" / "workflows"
        if dossier.is_dir():
            fichiers += sorted(dossier.glob("*.y*ml"))
    return fichiers


def identifiant(chemin: Path) -> str:
    return str(chemin.relative_to(REPO))


CIBLES = workflows_exemplaires()


def test_le_depot_a_des_workflows_a_controler() -> None:
    """Sans cette garde, tous les tests ci-dessous passeraient à vide.

    Un `glob` qui ne trouve rien produit une liste vide, donc zéro cas
    paramétré, donc zéro échec possible : le contrôle aurait l'air vert en ne
    mesurant rien. C'est le défaut que ce dépôt traque chez les autres.
    """
    assert CIBLES, (
        "Aucun workflow trouvé sous `.github/workflows/` ni sous "
        "`labs/*/solution/.github/workflows/`. Soit le dépôt a été déplacé, "
        "soit ce contrôle ne regarde plus au bon endroit."
    )


@pytest.mark.parametrize("chemin", CIBLES, ids=identifiant)
def test_chaque_action_est_epinglee_avec_sa_version_en_commentaire(chemin: Path) -> None:
    for numero, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        correspondance = RE_USES.match(ligne)
        if not correspondance:
            continue
        cible, commentaire = correspondance.group(1), correspondance.group(2)
        if cible.startswith("./") or cible.startswith("docker://"):
            continue

        action, _, reference = cible.partition("@")
        assert RE_SHA.match(reference or ""), (
            f"{identifiant(chemin)}:{numero} — `{action}@{reference}` n'est pas "
            "épinglée sur un SHA de quarante caractères.\n\nCe catalogue "
            "enseigne l'épinglage : ses propres workflows et ses solutions de "
            "référence ne peuvent pas employer un tag mobile."
        )
        assert commentaire, (
            f"{identifiant(chemin)}:{numero} — `{action}` est épinglée, mais le "
            "SHA n'est suivi d'aucun commentaire de version.\n\nC'est ce "
            "commentaire que Dependabot lit pour proposer la montée, et c'est "
            "lui qui rend la ligne relisible."
        )


@pytest.mark.parametrize("chemin", CIBLES, ids=identifiant)
def test_aucun_job_ne_demande_plus_que_la_lecture(chemin: Path) -> None:
    workflow = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    assert isinstance(workflow, dict), f"{identifiant(chemin)} n'est pas un workflow."

    racine = workflow.get("permissions")
    jobs = workflow.get("jobs") or {}

    sans_bloc = [nom for nom, corps in jobs.items() if (corps or {}).get("permissions") is None]
    assert racine is not None or not sans_bloc, (
        f"{identifiant(chemin)} ne déclare aucun bloc `permissions`, ni au "
        f"niveau du workflow ni dans {sans_bloc}.\n\nLe jeton prend alors les "
        "permissions par défaut du dépôt, et Scorecard le relève sous "
        "« Token-Permissions »."
    )

    portees = [("workflow", racine)] + [
        (f"job `{nom}`", (corps or {}).get("permissions")) for nom, corps in jobs.items()
    ]
    for portee, valeur in portees:
        if valeur is None or valeur == "read-all" or valeur == {}:
            continue
        assert valeur != "write-all", (
            f"{identifiant(chemin)}, {portee} : `write-all` donne l'écriture sur "
            "tout, dans un dépôt qui enseigne le contraire."
        )
        assert isinstance(valeur, dict), (
            f"{identifiant(chemin)}, {portee} : `permissions` vaut {valeur!r}."
        )
        # Une écriture peut être légitime (publier un SARIF, attester), mais
        # elle se justifie en commentaire, sur la ligne ou juste au-dessus.
        ecritures = {p: d for p, d in valeur.items() if d not in LECTURES}
        if not ecritures:
            continue
        texte = chemin.read_text(encoding="utf-8")
        for portee_nom in ecritures:
            motif = re.compile(rf"(#[^\n]*\n\s*)?{re.escape(portee_nom)}:\s*write[^\n]*(#[^\n]*)?")
            trouve = motif.search(texte)
            justifie = bool(trouve and ("#" in trouve.group(0)))
            assert justifie, (
                f"{identifiant(chemin)}, {portee} : `{portee_nom}: "
                f"{ecritures[portee_nom]}` dépasse la lecture sans qu'un "
                "commentaire dise pourquoi.\n\nUne écriture peut être "
                "légitime, publier un SARIF par exemple. Ce qui ne l'est pas, "
                "c'est de ne pas dire laquelle."
            )
