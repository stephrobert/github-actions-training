"""Ce que l'apprenant lit ne porte ni emoji décoratif ni tiret cadratin.

La règle est écrite dans `CONTRIBUTING.md`, et elle ne tient que si quelque
chose la vérifie : une règle de rédaction sans contrôle dérive au premier lab
écrit vite.

Le tiret cadratin mérite une explication, parce qu'il a l'air inoffensif. Il
arrive tout seul : un assistant en produit par habitude, un copier-coller depuis
une page anglaise en amène, et il se distingue mal d'un tiret ordinaire à la
relecture. Il n'appartient pas à la typographie de ce dépôt, et l'issue #20 le
rappelle à propos d'une simple cellule vide de tableau.

DEUX ADAPTATIONS À CE DÉPÔT, ET ELLES SONT MESURÉES

1. **Les emoji sont tolérés dans `challenge/README*`.** Mesuré le 2026-09-25 :
   174 briefs en portent, comme repères de section (objectif, validation,
   piège). Ce n'est pas une dérive, c'est la convention du gabarit, et la
   changer demanderait de réécrire 174 fichiers pour un gain nul. Partout
   ailleurs, ils sont refusés.

2. **Les flèches `←` et `→` ne sont pas surveillées.** Six README les emploient
   dans des tableaux, avec un sens (une direction, une correspondance), là où un
   pictogramme n'en a pas.

LA DETTE, ET POURQUOI ELLE EST NOMMÉE

33 fichiers portaient un tiret cadratin le jour où ce contrôle a été écrit. Les
corriger à l'aveugle serait risqué : un cadratin se remplace par une virgule,
un deux-points ou rien selon la phrase, et une substitution en masse abîmerait
le texte. Ils sont donc recensés ci-dessous, et la liste ne peut que décroître :
le test refuse aussi qu'un fichier y reste alors qu'il a été corrigé.

    pytest tests/test_style_apprenant.py -v
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
LABS = RACINE / "labs"

#: Plages Unicode des pictogrammes décoratifs. Les flèches (0x2190-0x21FF) en
#: sont volontairement absentes : voir l'adaptation 2 ci-dessus.
PLAGES_EMOJI = [
    (0x1F300, 0x1FAFF),
    (0x2600, 0x27BF),
    (0xFE0F, 0xFE0F),
    (0x2B00, 0x2BFF),
]
EMOJI = re.compile("[" + "".join(f"{chr(a)}-{chr(b)}" for a, b in PLAGES_EMOJI) + "]")

CADRATIN = chr(0x2014)

#: Les briefs, où l'emoji est la convention du dépôt.
TOLERE_LES_EMOJI = ("challenge/README.md", "challenge/README.fr.md")

#: Fichiers portant encore un tiret cadratin, mesurés le 2026-09-25. La liste
#: ne peut que décroître.
DETTE_CADRATIN: set[str] = set()


def _fichiers_lus() -> list[Path]:
    """Tout ce que l'apprenant lit : scénarios, README, briefs, fixtures textuelles."""
    return sorted(LABS.rglob("*.md"))


# Six par lab au minimum : les deux README, les deux scénarios et les deux
# énoncés du challenge. Le seuil suit donc le nombre de labs, et il vaut mieux
# qu'un nombre en dur : celui de `terraform-dsoxlab-training`, 200, ne voulait
# rien dire ici, où le catalogue commence.
MINIMUM_PAR_LAB = 6


def test_il_y_a_des_textes_a_lire() -> None:
    """Garde-fou : un glob cassé rendrait la suite verte sans rien mesurer."""
    trouves = _fichiers_lus()
    labs = [d for d in LABS.iterdir() if (d / "lab.yaml").is_file()] if LABS.is_dir() else []
    attendu = MINIMUM_PAR_LAB * len(labs)
    assert labs, "Aucun lab sous `labs/` : le catalogue est vide ou mal placé."
    assert len(trouves) >= attendu, (
        f"{len(trouves)} fichier(s) .md pour {len(labs)} lab(s), {attendu} "
        "attendus au minimum.\n\nChaque lab porte au moins ses deux README, "
        "ses deux scénarios et ses deux énoncés de challenge. En dessous, il "
        "en manque, ou le glob ne regarde plus au bon endroit."
    )


@pytest.mark.parametrize(
    "fichier", _fichiers_lus(), ids=lambda p: str(p.relative_to(LABS))
)
def test_pas_d_emoji_hors_des_briefs(fichier: Path) -> None:
    rel = str(fichier.relative_to(LABS))
    if rel.endswith(TOLERE_LES_EMOJI):
        pytest.skip("brief : l'emoji y est la convention du dépôt")

    trouves = sorted(set(EMOJI.findall(fichier.read_text(encoding="utf-8", errors="ignore"))))
    assert not trouves, (
        f"{rel} porte {len(trouves)} pictogramme(s) : {trouves}\n\n"
        "Ce que l'apprenant lit s'en passe, hors des briefs `challenge/README`, "
        "où ils servent de repères de section."
    )


@pytest.mark.parametrize(
    "fichier", _fichiers_lus(), ids=lambda p: str(p.relative_to(LABS))
)
def test_pas_de_tiret_cadratin(fichier: Path) -> None:
    rel = str(fichier.relative_to(LABS))
    contenu = fichier.read_text(encoding="utf-8", errors="ignore")
    occurrences = contenu.count(CADRATIN)

    if rel in DETTE_CADRATIN:
        assert occurrences, (
            f"{rel} ne porte plus de tiret cadratin, mais figure encore dans "
            "DETTE_CADRATIN. Retirez-le de la liste, sinon elle ne décroît "
            "jamais et plus personne ne la regarde."
        )
        pytest.skip(f"dette connue : {occurrences} cadratin(s) à reprendre")

    assert not occurrences, (
        f"{rel} porte {occurrences} tiret(s) cadratin.\n\n"
        "Il se distingue mal d'un tiret ordinaire à la relecture et n'appartient "
        "pas à la typographie de ce dépôt. Selon la phrase, il se remplace par "
        "une virgule, un deux-points, ou rien."
    )
