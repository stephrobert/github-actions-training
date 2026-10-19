"""Lire une solution de formateur, qu'elle soit chiffrée ou non.

Les solutions sont chiffrées par ansible-vault : l'apprenant ne doit pas
pouvoir les lire dans le dépôt qu'il clone. Tout ce qui les CONSOMME passe
donc par ici, plutôt que par un ``read_text`` qui rendrait le blob chiffré.

Le piège qu'évite ce module est silencieux, et c'est pour ça qu'il mérite un
module plutôt qu'une ligne recopiée deux fois. Un lecteur qui ne déchiffre pas
ne lève pas : il lit ``$ANSIBLE_VAULT;1.1;AES256`` suivi d'un pavé
hexadécimal, et conclut sur ce pavé. Le contrôle des ``ssh`` sans ``-n``
passerait ainsi au vert sur les soixante-quatre solutions, faute d'y voir une
seule ligne de code, et le piège qu'il garde a déjà coûté un cycle de cluster.

D'où le choix de lever plutôt que de rendre une chaîne vide quand le
déchiffrement est impossible : un appelant qui reçoit "" en tire une
conclusion, un appelant qui reçoit une exception doit décider quoi en dire.
C'est la règle du dépôt : un contrôle qui n'a pas pu regarder ne conclut
jamais au vert.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

#: Jamais commité, par construction : c'est tout l'objet du chiffrement.
VAULT_PASS = RACINE / ".vault-pass"

#: L'en-tête qu'ansible-vault écrit en première ligne d'un fichier chiffré.
MARQUEUR = "$ANSIBLE_VAULT"


class SolutionIllisible(RuntimeError):
    """La solution est chiffrée et rien ici ne permet de la déchiffrer."""


def est_chiffree(chemin: Path) -> bool:
    """Le fichier porte-t-il l'en-tête d'ansible-vault ?"""
    return chemin.read_text(encoding="utf-8", errors="replace").lstrip().startswith(
        MARQUEUR
    )


def lire_solution(chemin: Path) -> str:
    """Le texte de la solution, déchiffré si besoin.

    Lève :class:`SolutionIllisible` si le fichier est chiffré et que le secret
    manque ou ne convient pas. L'appelant choisit alors ce qu'il en dit : un
    script de validation s'arrête, un test se déclare non joué.
    """
    brut = chemin.read_text(encoding="utf-8", errors="replace")
    if not brut.lstrip().startswith(MARQUEUR):
        return brut

    if not VAULT_PASS.is_file():
        raise SolutionIllisible(
            f"{chemin.name} est chiffrée et .vault-pass est absent de la "
            "racine du dépôt. Le secret n'est jamais commité : récupère-le "
            "avant de rejouer ou d'analyser une solution."
        )

    vu = subprocess.run(
        [
            "ansible-vault",
            "view",
            "--vault-password-file",
            str(VAULT_PASS),
            str(chemin),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if vu.returncode != 0:
        raise SolutionIllisible(
            f"ansible-vault n'a pas pu lire {chemin.name} "
            f"(code {vu.returncode}) : {(vu.stderr or vu.stdout).strip()[-300:]}"
        )
    return vu.stdout
