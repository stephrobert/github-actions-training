"""Le premier workflow : cinq contrôles, vingt points chacun.

## Ce que ces tests lisent

Ce qu'act PRODUIT, et le YAML écrit. Jamais les commandes tapées : l'apprenant
arrive au résultat par le chemin qu'il veut, et un workflow se juge sur ce
qu'il fait tourner.

Les trois premiers contrôles jouent le workflow pour de bon, dans l'image du
runner épinglée par digest. Les deux derniers relisent le fichier, parce que
« ne demander que le droit de lire » et « épingler par SHA » sont des
propriétés du texte : elles ne se voient pas dans la sortie d'un job vert.

## Le dernier contrôle est celui qui compte

Un workflow qui affiche « tests OK » sans lancer pytest rend un job vert et
passe les quatre premiers. Le cinquième casse une fonction dans une COPIE du
projet et exige que le pipeline le dise, puis vérifie sur le projet intact que
ce n'est pas le workflow qui est cassé. Les deux moitiés sont dans le même
test, et la seconde n'a de sens que par la première.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from conftest import (
    declencheurs,
    executer,
    exiger_outil,
    exiger_workdir,
    jouer_act,
    lire_workflows,
    references_uses,
    workdir_lab,
)

WORKDIR = workdir_lab(__file__)
LAB_ID = "fondations-premier-workflow"

# Les neuf tests de la bibliothèque. Le compte est dans l'énoncé, et un
# workflow qui n'en lance que trois n'a pas fait le travail.
TESTS_ATTENDUS = 9


@pytest.fixture(scope="module")
def depot() -> Path:
    exiger_workdir(WORKDIR, LAB_ID)
    return WORKDIR


def _exiger_job_vert(resultat, evenement: str) -> str:
    """Un seul job, vert, et son identifiant. Sinon un message qui enseigne."""
    assert resultat.jobs, (
        f"`act {evenement}` n'a joué aucun job.\n  {resultat.resume()}\n\n"
        f"Soit aucun workflow ne déclare `{evenement}` dans son `on:`, soit le "
        "fichier n'est pas là où GitHub le cherche. `act -l` liste ce qu'act a "
        "compris de vos fichiers : un job qui n'y figure pas ne tournera jamais."
    )

    echoues = [nom for nom, etats in resultat.jobs.items() if "failure" in etats]
    assert not echoues, (
        f"`act {evenement}` a joué {sorted(resultat.jobs)}, et {echoues} a échoué.\n"
        f"  {resultat.resume()}"
    )
    return sorted(resultat.jobs)[0]


def _exiger_neuf_tests(resultat, evenement: str) -> None:
    """pytest a nommé ses neuf tests, et un `echo` ne peut pas l'imiter."""
    assert f"{TESTS_ATTENDUS} passed" in resultat.brut, (
        f"`act {evenement}` a rendu un job vert, mais sa sortie ne contient pas "
        f"« {TESTS_ATTENDUS} passed ».\n  {resultat.resume()}\n\n"
        "C'est pytest qui écrit cette ligne, et lui seul. Un job qui réussit "
        "sans elle n'a pas lancé les tests : il a installé Python, ou affiché "
        "un message, et il est reparti."
    )


def test_les_tests_tournent_a_chaque_push(depot: Path) -> None:
    """Tâche 1 : `act push` joue un job vert où pytest annonce ses neuf tests."""
    resultat = jouer_act(depot, "push")
    _exiger_job_vert(resultat, "push")
    _exiger_neuf_tests(resultat, "push")


def test_les_tests_tournent_a_chaque_pull_request(depot: Path) -> None:
    """Tâche 2 : le même job, sur l'autre événement.

    Un `on: push` seul laisse passer exactement ce que le scénario raconte :
    une modification relue en pull request, fusionnée sans que rien ne l'ait
    jouée.
    """
    resultat = jouer_act(depot, "pull_request")
    _exiger_job_vert(resultat, "pull_request")
    _exiger_neuf_tests(resultat, "pull_request")

    declares = set()
    for workflow in lire_workflows(depot).values():
        declares |= declencheurs(workflow)
    assert "pull_request" in declares, (
        f"Aucun workflow ne déclare `pull_request` dans son `on:` (trouvé : "
        f"{sorted(declares)}).\n\nact a joué quelque chose parce qu'on lui a "
        "nommé l'événement, mais GitHub, lui, ne déclenche que ce qui est "
        "déclaré."
    )


def test_le_workflow_ne_reclame_que_la_lecture_du_code(depot: Path) -> None:
    """Tâche 3 : `permissions` est déclaré, et personne n'obtient plus que la lecture.

    Un bloc absent n'est pas neutre : le jeton prend alors les permissions par
    défaut du dépôt, qui peuvent être en écriture sur tout. C'est ce que
    Scorecard relève sous « Token-Permissions ».
    """
    for nom, workflow in lire_workflows(depot).items():
        racine = workflow.get("permissions")
        jobs = workflow.get("jobs") or {}

        sans_bloc = [j for j, corps in jobs.items() if (corps or {}).get("permissions") is None]
        assert racine is not None or not sans_bloc, (
            f"{nom} ne déclare aucun bloc `permissions`, ni au niveau du "
            f"workflow ni dans {sans_bloc}.\n\nLe jeton prend alors les "
            "permissions par défaut du dépôt. Un bloc au niveau du workflow "
            "couvre tous ses jobs d'un coup."
        )

        for portee, valeur in [("workflow", racine)] + [
            (f"job `{j}`", (corps or {}).get("permissions")) for j, corps in jobs.items()
        ]:
            if valeur is None:
                continue
            assert valeur != "write-all", (
                f"{nom}, {portee} : `permissions: write-all` donne l'écriture "
                "sur tout, au moment précis où l'on cherche à la restreindre."
            )
            if valeur == "read-all" or valeur == {}:
                continue
            assert isinstance(valeur, dict), (
                f"{nom}, {portee} : `permissions` vaut {valeur!r}, un "
                "dictionnaire de portées était attendu."
            )
            trop = {p: d for p, d in valeur.items() if d not in ("none", "read")}
            assert not trop, (
                f"{nom}, {portee} : {trop} dépasse la lecture.\n\nCe job "
                "récupère du code et lance des tests : `contents: read` suffit, "
                "et tout ce qui va au-delà est du droit qu'une action "
                "compromise pourrait employer."
            )
            hors_sujet = {p for p in valeur if p != "contents" and valeur[p] != "none"}
            assert not hors_sujet, (
                f"{nom}, {portee} : {sorted(hors_sujet)} n'a rien à faire ici. "
                "Le seul droit dont ce job a besoin est `contents: read`."
            )


def test_chaque_action_est_epinglee_sur_le_sha_de_son_commit(depot: Path) -> None:
    """Tâche 4 : un SHA de quarante caractères, la version en commentaire, zizmor muet.

    Un tag est un pointeur mobile. `@v7` peut désigner un autre code demain, y
    compris du code hostile si le dépôt de l'action est compromis : c'est
    exactement ce qui est arrivé à `tj-actions/changed-files` en mars 2025.
    """
    references = [r for r in references_uses(depot) if not r.locale]
    assert references, (
        "Aucun `uses:` dans vos workflows.\n\nLe runner démarre sur une machine "
        "neuve : sans action pour récupérer le code, il n'y a rien à tester."
    )

    for reference in references:
        assert reference.epinglee_par_sha, (
            f"{reference.fichier}:{reference.ligne} — `{reference.action}@"
            f"{reference.ref}` n'est pas épinglée sur un SHA.\n\nUn SHA fait "
            "quarante caractères hexadécimaux. `gh api repos/"
            f"{reference.action}/commits/{reference.ref} --jq .sha` donne celui "
            "du tag que vous employez."
        )
        assert reference.commentaire, (
            f"{reference.fichier}:{reference.ligne} — le SHA n'est suivi "
            "d'aucun commentaire de version.\n\nSans lui, la ligne devient "
            "illisible et Dependabot ne sait plus quelle version elle "
            "représente : c'est ce commentaire qu'il lit pour proposer la "
            "montée. La forme attendue est `# v7.0.1`."
        )

    zizmor = exiger_outil("zizmor")
    res = executer([zizmor, "--offline", "--no-progress", ".github/workflows"], cwd=depot, timeout=180)
    assert res.returncode == 0, (
        "`zizmor --offline .github/workflows` relève quelque chose :\n\n"
        f"{(res.stdout + res.stderr).strip()[-1500:]}\n\n"
        "C'est la même lecture que fera la revue. Un workflow juste passe sans "
        "rien à ignorer."
    )


def test_un_test_casse_fait_echouer_le_pipeline(depot: Path, tmp_path: Path) -> None:
    """Tâche 5 : le contrôle qui distingue un workflow qui teste d'un qui affiche.

    ## Pourquoi les deux moitiés sont dans le même test

    « Le projet intact rend un job vert » est VRAI dès que la tâche 1 l'est :
    isolé, ce serait une hypothèse du setup, pas un contrôle. Réuni au sabotage,
    il reprend son sens : il distingue un pipeline qui détecte la régression
    d'un pipeline cassé, qui échoue sur tout et n'apprend rien.

    ## Pourquoi une copie

    Le répertoire de travail de l'apprenant n'est pas touché : la fonction est
    cassée dans une copie jetable, et l'original reste celui qu'il a écrit.
    """
    sabote = tmp_path / "projet-sabote"
    shutil.copytree(depot, sabote, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))

    calculatrice = sabote / "src" / "calculator.py"
    assert calculatrice.is_file(), (
        "`src/calculator.py` est introuvable dans le répertoire de travail : "
        "le point de départ a été déplacé ou supprimé."
    )
    source = calculatrice.read_text(encoding="utf-8")
    ancien = "    return a + b"
    assert ancien in source, (
        "La fonction `add` de `src/calculator.py` n'est plus celle du point de "
        "départ : la vérification ne peut plus la casser pour éprouver votre "
        "pipeline. Rétablissez `return a + b`."
    )
    calculatrice.write_text(source.replace(ancien, "    return a + b + 1", 1), encoding="utf-8")

    rouge = jouer_act(sabote, "push")
    echoue = [nom for nom, etats in rouge.jobs.items() if "failure" in etats]
    assert echoue, (
        "Une somme fausse a été introduite dans `add`, et votre pipeline est "
        f"resté vert.\n  {rouge.resume()}\n\n"
        "Trois tests de `TestAdd` auraient dû tomber. Un workflow qui ne lance "
        "pas vraiment pytest, ou qui avale son code de retour, rend un job vert "
        "sur du code faux : c'est exactement la panne que le scénario raconte."
    )

    vert = jouer_act(depot, "push")
    assert not [nom for nom, etats in vert.jobs.items() if "failure" in etats], (
        "Votre pipeline échoue AUSSI sur le projet intact.\n"
        f"  {vert.resume()}\n\n"
        "Il ne détecte donc pas la régression : il est cassé. Un pipeline qui "
        "échoue toujours n'apprend rien de plus qu'un pipeline qui réussit "
        "toujours."
    )
    _exiger_neuf_tests(vert, "push")
