"""Tout lab livré est déclaré dans `meta.yml`, et réciproquement.

Repris du catalogue Kubernetes. Le catalogue a deux descriptions :
`labs/*/lab.yaml` dit ce qui existe, `meta.yml` dit dans quel ordre le jouer.
Chaque outil lit la sienne et a raison de son côté ; le trou est entre les
deux. Le catalogue Kubernetes a perdu deux labs validés ainsi, le 2026-09-16,
après une manipulation de branches : présents dans la table de couverture,
absents du parcours. Et `dsoxlab validate-structure` ne peut pas le voir :
il itère sur les labs découverts, il ne lit pas `meta.yml`.

Ce module énumère les RÉPERTOIRES, pas les `lab.yaml` : on ne peut pas
constater l'absence d'un fichier en partant de ce fichier.

    uv run pytest tests/test_meta_declare_les_labs.py -v
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
META = RACINE / "meta.yml"
LABS = RACINE / "labs"


def _declares() -> list[str]:
    donnees = yaml.safe_load(META.read_text(encoding="utf-8"))
    declares: list[str] = []
    for section in donnees.get("sections") or []:
        declares += [str(lab) for lab in (section.get("labs") or [])]
    return declares


def _sur_disque() -> set[str]:
    """Tout répertoire `labs/<id>/`, qu'il soit complet ou amputé."""
    return {d.name for d in LABS.iterdir() if d.is_dir() and not d.name.startswith((".", "_"))}


def test_chaque_lab_livre_est_declare_dans_le_parcours() -> None:
    oublies = sorted(_sur_disque() - set(_declares()))
    assert not oublies, (
        "Lab(s) présent(s) sur le disque mais absent(s) de meta.yml :\n  "
        + "\n  ".join(oublies)
        + "\n\nUn apprenant qui suit le parcours ne les jouera jamais. Ajoutez chaque "
        "lab dans la liste `labs:` de sa section."
    )


def test_chaque_lab_declare_existe_sur_le_disque() -> None:
    fantomes = sorted(set(_declares()) - _sur_disque())
    assert not fantomes, (
        "Lab(s) déclaré(s) dans meta.yml sans répertoire sous labs/ :\n  "
        + "\n  ".join(fantomes)
        + "\n\nLe parcours pointe dans le vide. Retirez la ligne, ou restaurez le lab."
    )


def test_chaque_lab_sur_disque_porte_son_contrat() -> None:
    """Un répertoire sans lab.yaml est invisible de dsoxlab : c'est un lab amputé."""
    amputes = sorted(d for d in _sur_disque() if not (LABS / d / "lab.yaml").is_file())
    assert not amputes, (
        "Répertoire(s) de lab sans lab.yaml :\n  " + "\n  ".join(amputes)
        + "\n\ndsoxlab ne les découvre pas, validate-structure ne les voit pas, et "
        "le parcours les annonce quand même."
    )


def test_aucun_lab_n_est_declare_deux_fois() -> None:
    doublons = sorted(lab for lab, n in Counter(_declares()).items() if n > 1)
    assert not doublons, f"Lab(s) déclaré(s) plus d'une fois dans meta.yml : {doublons}"


def test_l_id_du_contrat_est_le_nom_du_repertoire() -> None:
    """`dsoxlab run <id>` : l'id est la clé de la CLI, le répertoire celle de la découverte.

    Les faire coïncider épargne à l'apprenant d'avoir à ouvrir lab.yaml pour
    savoir quoi taper.
    """
    ecarts = []
    for nom in sorted(_sur_disque()):
        contrat_chemin = LABS / nom / "lab.yaml"
        if not contrat_chemin.is_file():
            continue
        contrat = yaml.safe_load(contrat_chemin.read_text(encoding="utf-8")) or {}
        if contrat.get("id") != nom:
            ecarts.append(f"{nom} : lab.yaml dit id={contrat.get('id')!r}")
    assert not ecarts, "\n".join(ecarts)
