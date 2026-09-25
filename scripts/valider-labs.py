#!/usr/bin/env python3
"""Joue chaque lab dans les deux sens et vérifie qu'il ne laisse aucune trace.

Repris de kubernetes-dsoxlab-training/scripts/valider-labs.py, adapté au
runtime shell : pas de cluster à photographier, mais un répertoire de travail
que `dsoxlab clean` doit retirer, et un moteur Docker qu'act ne doit pas
laisser encombré. Un test qui passe ne prouve rien tant qu'on n'a pas vu
échouer ce qui doit échouer. Pour chaque lab, dans l'ordre :

    0. photographie : conteneurs Docker présents, répertoire de travail absent
    1. dsoxlab run            l'état initial est posé (fixtures)
    2. dsoxlab check          DOIT rendre 0 : le travail n'est pas fait
    3. la solution du formateur, challenge/solution.sh, jouée dans le
       répertoire de travail par `bash -s`
    4. dsoxlab check          DOIT rendre 100
    5. dsoxlab clean, run, check   DOIT rendre 0 : le point de départ se rejoue
    6. dsoxlab clean
    7. photographie à nouveau, comparée à la première : aucun écart admis

Le validateur exige 0 puis 100, pas « moins » puis « plus » : un lab à cinq
tests dont deux passent avant le travail mesure 40 points de rien.

    uv run scripts/valider-labs.py                              # tous les labs
    uv run scripts/valider-labs.py --lab fondations-premier-workflow
    uv run scripts/valider-labs.py --sans-rejeu                 # saute l'étape 5

Le résultat de chaque lab est écrit dans validation-labs.json, à la racine :
c'est l'attestation que le lab a été joué, avec la date, la version d'act, le
digest de l'image du runner et les mesures. Le journal complet de chaque lab
va dans ~/.cache/dsoxlab/<catalogue>/validation-<lab>.log.

Ce script ne remplace aucune commande de dsoxlab : il les enchaîne. Il refuse
de jouer avec une autre version d'act que celle de mise.toml, parce que le
verdict ne vaudrait pas ce qu'il annonce.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from datetime import UTC, datetime
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
LABS = RACINE / "labs"
RESULTATS = RACINE / "validation-labs.json"
CACHE = Path.home() / ".cache" / "dsoxlab" / RACINE.name

sys.path.insert(0, str(RACINE))
from conftest import IMAGE_RUNNER  # noqa: E402


class Echec(Exception):
    pass


def commande(args: list[str], journal, timeout: int, entree: str | None = None,
             cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Lance une commande, journalise tout, rend le résultat sans lever."""
    journal.write(f"\n$ {' '.join(args)}\n")
    journal.flush()
    env = dict(os.environ, LAB_HOME=str(RACINE))
    try:
        # check=False : c'est l'appelant qui juge le code de retour, et une
        # exception ici perdrait la sortie déjà journalisée.
        res = subprocess.run(args, capture_output=True, text=True, timeout=timeout, env=env,
                             stdin=subprocess.DEVNULL if entree is None else None, input=entree,
                             cwd=cwd or RACINE, check=False)
    except subprocess.TimeoutExpired as e:
        journal.write(f"DÉLAI DÉPASSÉ après {timeout}s\n")
        raise Echec(f"délai de {timeout}s dépassé : {' '.join(args[:3])}") from e
    except FileNotFoundError as e:
        # Une trace Python de quinze lignes pour dire qu'un binaire manque
        # n'apprend rien. Mesuré le 2026-09-25 : la CI a rendu
        # `FileNotFoundError: 'dsoxlab'` sans dire comment l'installer.
        journal.write(f"OUTIL ABSENT : {args[0]}\n")
        raise Echec(
            f"`{args[0]}` n'est pas sur le PATH. dsoxlab est un OUTIL, pas une "
            "dépendance de ce dépôt : `uv tool install dsoxlab`, ou "
            "`uvx dsoxlab` pour un essai."
        ) from e
    journal.write(res.stdout)
    journal.write(res.stderr)
    return res


def dsoxlab(sous_commande: list[str], journal, timeout: int) -> subprocess.CompletedProcess:
    return commande(["dsoxlab", *sous_commande], journal, timeout)


# `FAILED chemin/test_functional.py::test_nom - message` : la ligne de résumé
# que pytest écrit pour chaque échec, la seule qui nomme le test.
_RE_ECHEC = re.compile(r"^FAILED\s+\S+::(\S+)", re.MULTILINE)


def tests_en_echec(sortie: str) -> list[str]:
    """Les noms des tests qu'un `check` a laissés rouges.

    POURQUOI LES EXTRAIRE

    « la solution ne fait pas passer tous les tests » dit qu'il y a un
    problème ; il ne dit pas lequel, et c'est pourtant la seule information
    utile pour le corriger. La sortie de pytest est dans le JSON de dsoxlab :
    la lire coûte une expression régulière et épargne d'ouvrir le journal.

    La sortie du terminal est repliée sur la largeur de la console, ce qui
    coupe les noms longs en plein milieu. On recolle donc les lignes de
    continuation avant de lire.
    """
    recollee = re.sub(r"\n(?=[A-Za-z_])", "", sortie) if "\nFAILED" not in sortie else sortie
    noms = _RE_ECHEC.findall(recollee)
    if not noms:
        # Le repli a pu couper juste après « FAILED ». On retente en
        # supprimant tous les retours à la ligne, au prix de la lisibilité.
        noms = _RE_ECHEC.findall("FAILED " + sortie.replace("\n", ""))
    return sorted(set(noms))


def check(lab: str, journal) -> dict:
    """Rend {"passed", "total", "score", "echecs"} de dsoxlab check --json."""
    res = dsoxlab(["check", lab, "--json"], journal, 900)
    try:
        d = json.loads(res.stdout)["check"]
    except (json.JSONDecodeError, KeyError) as e:
        raise Echec(f"dsoxlab check n'a pas rendu de JSON lisible : {e}") from e
    return {
        "passed": d.get("passed", 0),
        "total": d.get("total", 0),
        "score": d.get("score", 0),
        "echecs": tests_en_echec(d.get("output", "")),
    }


def workdir(lab: Path) -> Path:
    d = yaml.safe_load((lab / "lab.yaml").read_text(encoding="utf-8"))
    rel = ((d.get("runtime") or {}).get("workdir")) or "challenge/work"
    return lab / rel


def version_act() -> str:
    res = subprocess.run(["act", "--version"], capture_output=True, text=True, check=False)
    m = re.search(r"act version (\S+)", res.stdout + res.stderr)
    return m.group(1) if m else "inconnue"


def version_act_attendue() -> str:
    return str(tomllib.loads((RACINE / "mise.toml").read_text(encoding="utf-8"))["tools"]["act"])


def photographier(lab: Path, journal) -> dict:
    """Ce qu'un lab shell pourrait laisser : des conteneurs, et son répertoire de travail."""
    res = commande(["docker", "ps", "-a", "--format", "{{.ID}} {{.Names}} {{.Image}}"], journal, 60)
    if res.returncode != 0:
        raise Echec(f"docker ne répond pas : {res.stderr.strip()[-200:]}")
    return {
        "conteneurs": sorted(ligne for ligne in res.stdout.splitlines() if ligne.strip()),
        "workdir_present": workdir(lab).exists(),
    }


def ecarts(avant: dict, apres: dict) -> list[str]:
    out = [f"conteneur laissé : {c}" for c in sorted(set(apres["conteneurs"]) - set(avant["conteneurs"]))]
    if apres["workdir_present"]:
        out.append("le répertoire de travail existe encore après clean")
    return out


def valider(lab: Path, rejeu: bool) -> dict:
    ident = lab.name
    CACHE.mkdir(parents=True, exist_ok=True)
    journal_path = CACHE / f"validation-{ident}.log"
    debut = time.time()
    resultat: dict = {
        "date": datetime.now(tz=UTC).date().isoformat(),
        "act": version_act(),
        "image": IMAGE_RUNNER,
        # Le chemin du journal est enregistré RELATIF au cache de l'utilisateur :
        # `validation-labs.json` est versionné et lu par d'autres, et
        # `/home/<qui-que-ce-soit>/...` n'a de sens pour personne d'autre que
        # celui qui a joué la campagne.
        "journal": str(journal_path.relative_to(Path.home())),
    }
    etapes: list[str] = []

    def dire(msg: str) -> None:
        etapes.append(msg)
        print(f"    {msg}", flush=True)

    with journal_path.open("w", encoding="utf-8") as journal:
        try:
            avant_photo = photographier(lab, journal)
            if avant_photo["workdir_present"]:
                raise Echec("le répertoire de travail existe déjà : lancez `dsoxlab clean` avant de valider")
            dire(f"état photographié, {len(avant_photo['conteneurs'])} conteneur(s) Docker présents")

            res = dsoxlab(["run", ident], journal, 300)
            if res.returncode != 0:
                raise Echec(f"dsoxlab run a échoué (rc={res.returncode}) : {(res.stdout + res.stderr).strip()[-400:]}")
            resultat["avant"] = check(ident, journal)
            dire(f"avant le travail : {resultat['avant']['passed']}/{resultat['avant']['total']}")

            poser_solution(lab, journal)
            resultat["apres"] = check(ident, journal)
            dire(f"après la solution : {resultat['apres']['passed']}/{resultat['apres']['total']}")

            if rejeu:
                dsoxlab(["clean", ident, "--yes"], journal, 300)
                res = dsoxlab(["run", ident], journal, 300)
                if res.returncode != 0:
                    raise Echec(f"le second dsoxlab run a échoué (rc={res.returncode}) : le point de départ "
                                f"ne se rejoue pas. {(res.stdout + res.stderr).strip()[-300:]}")
                resultat["rejeu"] = check(ident, journal)
                dire(f"après clean et run : {resultat['rejeu']['passed']}/{resultat['rejeu']['total']}")

            res = dsoxlab(["clean", ident, "--yes"], journal, 300)
            if res.returncode != 0:
                raise Echec(f"dsoxlab clean a échoué (rc={res.returncode})")
            apres_photo = photographier(lab, journal)
            resultat["ecarts"] = ecarts(avant_photo, apres_photo)
            dire("poste rendu intact" if not resultat["ecarts"] else f"{len(resultat['ecarts'])} écart(s) après clean")
        except Echec as e:
            resultat["erreur"] = str(e)
            dire(f"ÉCHEC : {e}")
            # On tente quand même de rendre le poste.
            with contextlib.suppress(Echec):
                dsoxlab(["clean", ident, "--yes"], journal, 300)

    resultat["duree_s"] = round(time.time() - debut)
    resultat["verdict"] = verdict(resultat, rejeu)
    resultat["etapes"] = etapes
    return resultat


def poser_solution(lab: Path, journal) -> None:
    """Pose `solution/` par-dessus le répertoire de travail, fichier par fichier.

    POURQUOI UNE COPIE ET PAS UN SCRIPT

    Ce que le formateur livre ici est un ARBORESCENCE de fichiers, pas une suite
    de gestes : un workflow est un fichier à sa place. Un `solution.sh` qui
    écrirait ces fichiers en heredoc ferait le même travail en moins lisible, et
    c'est `solution/` que documentent l'anatomie d'un lab et la CI, qui passe
    zizmor sur `labs/**/solution/`.

    La copie descend dans les SOUS-RÉPERTOIRES, et c'est le piège : `.github/
    workflows/ci.yml` est à trois niveaux, et une pose à plat ne créerait rien
    d'utile. Le catalogue Terraform a perdu une campagne entière sur exactement
    ce défaut, quinze labs rendant 0 puis 0.
    """
    source = lab / "solution"
    if not source.is_dir():
        raise Echec(
            "le lab n'a pas de répertoire `solution/` : rien à poser, et le "
            "cycle ne peut pas prouver que les tests passent une fois le "
            "travail fait"
        )

    cible = workdir(lab)
    fichiers = [f for f in sorted(source.rglob("*")) if f.is_file()]
    if not fichiers:
        raise Echec("le répertoire `solution/` est vide")

    for fichier in fichiers:
        destination = cible / fichier.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fichier, destination)

    journal.write(f"solution posée : {len(fichiers)} fichier(s)\n")
    for fichier in fichiers:
        journal.write(f"  {fichier.relative_to(source)}\n")
    journal.flush()


def verdict(r: dict, rejeu: bool) -> str:
    if "erreur" in r:
        return "ROUGE"
    raisons = []
    if r["avant"]["passed"] != 0:
        raisons.append(f"{r['avant']['passed']} test(s) passent avant le travail")
    if r["apres"]["total"] == 0:
        raisons.append("aucun test n'a été collecté : le lab ne mesure rien")
    elif r["apres"]["passed"] != r["apres"]["total"]:
        restes = r["apres"]["echecs"]
        detail = f" : {', '.join(restes)}" if restes else ""
        raisons.append(
            f"la solution laisse {r['apres']['total'] - r['apres']['passed']} test(s) "
            f"en échec{detail}"
        )
    if rejeu and r["rejeu"]["passed"] != 0:
        raisons.append(f"{r['rejeu']['passed']} test(s) passent après clean et run")
    if r["ecarts"]:
        raisons.append("le poste n'est pas rendu intact")
    r["raisons"] = raisons
    return "VALIDE" if not raisons else "ROUGE"


def relire() -> int:
    """Le verdict versionné couvre-t-il le catalogue, et est-il vert ?

    POURQUOI CE MODE EXISTE

    Rejouer les labs prend des minutes et demande Docker ; relire le verdict
    prend une milliseconde. Un hook local et la moitié des jobs de CI n'ont
    besoin que de la seconde question : « ce qui est versionné dit-il que le
    catalogue tient ? »

    Il vérifie DEUX choses, et la première est la moins évidente : qu'aucun lab
    n'a été ajouté sans être validé. Un fichier de verdicts tous verts qui
    ignore la moitié du catalogue passerait sans elle.
    """
    if not RESULTATS.is_file():
        print(f"{RESULTATS.name} est absent : aucun lab n'a jamais été validé.", file=sys.stderr)
        return 1

    verdicts = json.loads(RESULTATS.read_text(encoding="utf-8"))
    labs = sorted(p.name for p in LABS.iterdir() if (p / "lab.yaml").is_file())

    manquants = [nom for nom in labs if nom not in verdicts]
    if manquants:
        print(
            f"{len(manquants)} lab(s) sans verdict : {', '.join(manquants)}.\n"
            "Un lab livré sans validation ne prouve rien. Jouez "
            "`mise exec -- uv run scripts/valider-labs.py --lab <id>`.",
            file=sys.stderr,
        )
        return 1

    rouges = [nom for nom in labs if verdicts[nom].get("verdict") != "VALIDE"]
    if rouges:
        for nom in rouges:
            raisons = verdicts[nom].get("raisons") or [verdicts[nom].get("erreur", "raison non enregistrée")]
            print(f"{nom} : {'; '.join(raisons)}", file=sys.stderr)
        return 1

    fantomes = sorted(set(verdicts) - set(labs))
    if fantomes:
        print(
            f"{RESULTATS.name} porte le verdict de lab(s) qui n'existent plus : "
            f"{', '.join(fantomes)}. Retirez ces entrées.",
            file=sys.stderr,
        )
        return 1

    print(f"{len(labs)} lab(s), aucun ROUGE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lab", action="append", help="ne jouer que ce lab (répétable)")
    ap.add_argument("--sans-rejeu", action="store_true", help="sauter l'étape clean, run, check")
    ap.add_argument(
        "--check",
        action="store_true",
        help="relire validation-labs.json sans rien rejouer : exit 0 si chaque lab y est VALIDE",
    )
    args = ap.parse_args()

    if args.check:
        return relire()

    attendue, installee = version_act_attendue(), version_act()
    if attendue != installee:
        print(f"act {installee} est sur le PATH, mise.toml épingle {attendue} : le verdict ne vaudrait pas "
              "ce qu'il annonce. Lancez `mise install`, puis `mise exec -- uv run scripts/valider-labs.py`.",
              file=sys.stderr)
        return 2

    labs = sorted(p for p in LABS.iterdir() if (p / "lab.yaml").is_file())
    if args.lab:
        inconnus = set(args.lab) - {p.name for p in labs}
        if inconnus:
            print(f"lab(s) inconnu(s) : {', '.join(sorted(inconnus))}", file=sys.stderr)
            return 2
        labs = [p for p in labs if p.name in args.lab]

    anciens = json.loads(RESULTATS.read_text(encoding="utf-8")) if RESULTATS.is_file() else {}
    rouges = 0
    for lab in labs:
        print(f"\n{lab.name}", flush=True)
        r = valider(lab, rejeu=not args.sans_rejeu)
        anciens[lab.name] = r
        RESULTATS.write_text(json.dumps(anciens, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
        if r["verdict"] != "VALIDE":
            rouges += 1
            for raison in r.get("raisons", []):
                print(f"    - {raison}")
            for e in r.get("ecarts", [])[:15]:
                print(f"      {e}")
        print(f"    {r['verdict']} en {r['duree_s']} s")

    print(f"\n{len(labs) - rouges} valide(s), {rouges} rouge(s) sur {len(labs)} lab(s). Détail : {RESULTATS}")
    return 1 if rouges else 0


if __name__ == "__main__":
    sys.exit(main())
