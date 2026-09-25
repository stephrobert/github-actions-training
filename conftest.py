"""
Configuration pytest globale pour le catalogue github-actions-training.

Repris du catalogue terraform-training, dont les labs sont aussi en
`runtime: shell` : l'apprenant travaille dans `challenge/work` sur sa propre
machine, `dsoxlab run` y pose les fixtures, `dsoxlab check` joue
`challenge/tests/test_functional.py`. Il n'y a NI VM NI control node, donc pas
de testinfra ici.

Ce que ce fichier ajoute pour GitHub Actions : la façon de JOUER un workflow.
Les tests d'un lab lisent l'état, jamais les commandes tapées, et l'état d'un
workflow, c'est ce qu'il produit quand act le joue : le résultat de chaque
job, les lignes écrites par chaque step, les erreurs du moteur. Un test qui
relit le YAML est un complément, nommé `test_complement_*`, jamais la preuve.

Helpers exposés aux tests :

- `workdir_lab(fichier_test)` et `exiger_workdir(workdir, lab_id)`, comme dans
  terraform-training ;
- `jouer_act(depot, evenement, ...)` joue un workflow dans une COPIE du
  répertoire de travail et rend un `ResultatAct` : `jobs`, `lignes`,
  `erreurs`, `rc` ;
- `copie_temporaire(depot)` donne une copie à modifier (planter un test,
  altérer un commentaire de version) avant de la jouer ;
- `lire_workflows`, `references_uses`, `declencheurs` pour les compléments
  statiques ; `executer`, `exiger_outil`, `exiger_jeton_github` pour zizmor,
  pinact, actionlint et l'API GitHub.

Deux décisions mesurées le 2026-09-25 (act 0.2.89) :

- l'image du runner est épinglée PAR DIGEST et passée explicitement à act :
  une validation vaut pour une image donnée, et le `~/.actrc` de l'apprenant
  ne doit pas la remplacer. Le `.actrc` livré en fixture porte la même ligne ;
- le serveur d'artefacts et le serveur de cache sont créés par run, dans le
  répertoire temporaire : un lab ne profite jamais d'un artefact ou d'un cache
  laissé par un run précédent.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent
LABS_ROOT = REPO_ROOT / "labs"

# L'image qui joue `runs-on: ubuntu-24.04`. Digest mesuré le 2026-09-25 par
# `docker image inspect catthehacker/ubuntu:act-24.04` (image construite le
# 2026-08-15). Le `.actrc` livré à l'apprenant porte la même ligne.
LABEL_RUNNER = "ubuntu-24.04"
IMAGE_RUNNER = (
    "catthehacker/ubuntu:act-24.04"
    "@sha256:c58e2b364da03b0c804c7d660f2ecbedf2f221a382b9baa0b344b0144780ff43"
)

# Ce qu'on ne copie jamais d'un répertoire de travail : le dépôt git de
# l'apprenant (act en reçoit un neuf), les caches Python et pytest.
EXCLUS_COPIE = (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache")

_image_verifiee = False


# ── Où travaille l'apprenant (repris de terraform-training) ─────────────────


def workdir_lab(fichier_test: str | Path) -> Path:
    """Workdir du lab auquel appartient un fichier de test.

    Par défaut `<lab>/challenge/work`. La variable d'environnement
    `LAB_WORKDIR` la surcharge, pour rejouer les mêmes tests contre une autre
    copie.
    """
    surcharge = os.environ.get("LAB_WORKDIR")
    if surcharge:
        return Path(surcharge)
    return Path(fichier_test).resolve().parents[2] / "challenge" / "work"


def exiger_workdir(workdir: Path, lab_id: str) -> None:
    """Arrête proprement le test quand le workdir n'existe pas.

    - lab simplement pas joué : on SKIPPE, un `pytest` lancé à la racine ne
      doit pas afficher des erreurs rouges pour des labs que personne n'a
      ouverts ;
    - workdir surchargé par `LAB_WORKDIR` : on ÉCHOUE, son absence est un vrai
      défaut de l'appelant.
    """
    if workdir.is_dir():
        return
    if os.environ.get("LAB_WORKDIR"):
        pytest.fail(
            f"LAB_WORKDIR pointe sur {workdir}, qui n'existe pas. "
            "L'appelant devait matérialiser ce répertoire avant de lancer les tests."
        )
    pytest.skip(
        f"Lab non joué : {workdir} est absent. "
        f"Lancez `dsoxlab run {lab_id}` pour poser l'état de départ."
    )


# ── Outils ───────────────────────────────────────────────────────────────────


def exiger_outil(nom: str) -> str:
    """Le chemin de l'outil, ou un échec qui dit comment l'installer."""
    chemin = shutil.which(nom)
    if not chemin:
        pytest.fail(
            f"L'outil `{nom}` n'est pas sur le PATH. Il est épinglé dans "
            "mise.toml à la racine du catalogue : lancez `mise install`, puis "
            "rejouez `dsoxlab check`."
        )
    return chemin


def executer(
    cmd: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
    entree: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Lance une commande et rend le résultat sans lever : c'est le test qui juge."""
    environnement = dict(os.environ)
    if env:
        environnement.update(env)
    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            env=environnement,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=entree,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        sortie = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        return subprocess.CompletedProcess(cmd, 124, stdout=sortie, stderr=f"délai de {timeout} s dépassé")


def jeton_github() -> str | None:
    """Un jeton pour l'API GitHub : `GH_TOKEN`, `GITHUB_TOKEN`, ou `gh auth token`."""
    for nom in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(nom):
            return os.environ[nom]
    if shutil.which("gh"):
        res = executer(["gh", "auth", "token"], timeout=30)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip()
    return None


def exiger_jeton_github() -> str:
    """Certaines vérifications interrogent l'API GitHub. Sans jeton, on échoue en le disant."""
    jeton = jeton_github()
    if not jeton:
        pytest.fail(
            "Cette vérification interroge l'API GitHub et n'a trouvé aucun jeton : "
            "ni GH_TOKEN, ni GITHUB_TOKEN, ni `gh auth token`. Lancez `gh auth login`, "
            "ou exportez GH_TOKEN. Sans réseau ce test ne peut pas conclure, et il "
            "refuse de passer au vert par défaut."
        )
    return jeton


# ── Copie du répertoire de travail, dépôt git, image ────────────────────────


@contextlib.contextmanager
def copie_temporaire(depot: Path) -> Iterator[Path]:
    """Une copie du répertoire de travail, à modifier ou à jouer, détruite à la sortie."""
    with tempfile.TemporaryDirectory(prefix="lab-gha-") as tmp:
        cible = Path(tmp) / "depot"
        shutil.copytree(depot, cible, ignore=shutil.ignore_patterns(*EXCLUS_COPIE), symlinks=True)
        yield cible


def _git(*args: str, cwd: Path) -> None:
    cmd = [
        "git",
        "-c", "user.name=lab",
        "-c", "user.email=lab@example.invalid",
        "-c", "commit.gpgsign=false",
        "-c", "init.defaultBranch=main",
        *args,
    ]
    res = executer(cmd, cwd=cwd, timeout=60)
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} a échoué : {res.stderr.strip()}")


def initialiser_git(depot: Path) -> None:
    """act déduit le contexte (ref, sha, dépôt) d'un dépôt git : on lui en donne un neuf."""
    _git("init", "-q", "-b", "main", cwd=depot)
    _git("add", "-A", cwd=depot)
    _git("commit", "-q", "--allow-empty", "-m", "point de depart", cwd=depot)


def image_prete() -> None:
    """L'image du runner est présente, sinon on la tire une fois, par digest."""
    global _image_verifiee
    if _image_verifiee:
        return
    if executer(["docker", "image", "inspect", IMAGE_RUNNER], timeout=60).returncode != 0:
        res = executer(["docker", "pull", IMAGE_RUNNER], timeout=900)
        if res.returncode != 0:
            pytest.fail(
                f"Impossible de tirer l'image du runner {IMAGE_RUNNER} : "
                f"{res.stderr.strip()[-400:]}. Docker doit répondre (`docker info`) ; "
                "act ne joue rien sans lui."
            )
    _image_verifiee = True


# ── act ──────────────────────────────────────────────────────────────────────


@dataclass
class ResultatAct:
    """Ce qu'act a produit, lu depuis sa sortie `--json`."""

    commande: list[str]
    rc: int
    jobs: dict[str, list[str]] = field(default_factory=dict)  # jobID -> résultats
    lignes: list[str] = field(default_factory=list)  # tout ce que les steps ont écrit
    lignes_par_job: dict[str, list[str]] = field(default_factory=dict)
    steps: list[dict[str, str | None]] = field(default_factory=list)
    erreurs: list[str] = field(default_factory=list)
    brut: str = ""

    def job(self, identifiant: str) -> str | None:
        """Le résultat d'un job : `success`, `failure`, ou `None` s'il n'a pas été joué."""
        resultats = self.jobs.get(identifiant) or []
        if not resultats:
            return None
        if len(resultats) == 1:
            return resultats[0]
        # Une matrice produit plusieurs jobs sous le même identifiant : on rend
        # `failure` dès qu'un seul a échoué, c'est ce que GitHub affiche.
        return "failure" if "failure" in resultats else resultats[0]

    @property
    def sortie(self) -> str:
        return "\n".join(self.lignes)

    def contient(self, texte: str) -> bool:
        return texte in self.brut

    def resume(self, n: int = 12) -> str:
        """Un extrait pour les messages d'assertion : jobs, erreurs, dernières lignes."""
        parts = [f"commande : {' '.join(self.commande)}", f"code de retour : {self.rc}"]
        if self.jobs:
            etats = ", ".join(f"{j}={'/'.join(r)}" for j, r in sorted(self.jobs.items()))
            parts.append(f"jobs : {etats}")
        else:
            parts.append("jobs : aucun job n'a été joué")
        if self.erreurs:
            parts.append("erreurs d'act :\n    " + "\n    ".join(e.strip() for e in self.erreurs[-4:]))
        if self.lignes:
            parts.append("dernières lignes écrites :\n    " + "\n    ".join(self.lignes[-n:]))
        return "\n  ".join(parts)


def _ecrire_dotenv(chemin: Path, valeurs: dict[str, str]) -> None:
    chemin.write_text("".join(f"{k}={v}\n" for k, v in valeurs.items()), encoding="utf-8")
    chemin.chmod(0o600)


def jouer_act(
    depot: Path,
    evenement: str = "push",
    *,
    workflow: str | None = None,
    job: str | None = None,
    secrets_: dict[str, str] | None = None,
    variables: dict[str, str] | None = None,
    payload: dict | None = None,
    timeout: int = 600,
) -> ResultatAct:
    """Joue un workflow avec act dans une copie neuve du répertoire de travail.

    `workflow` est un chemin relatif au dépôt (`.github/workflows/ci.yml`),
    `job` un identifiant de job, `secrets_` et `variables` ce que GitHub
    fournirait par `secrets.*` et `vars.*`, `payload` le corps de l'événement
    (`-e`). Les secrets passent par un fichier hors du dépôt joué, jamais par
    la ligne de commande.
    """
    exiger_outil("act")
    image_prete()
    with copie_temporaire(depot) as d:
        initialiser_git(d)
        aux = d.parent
        cmd = [
            "act", evenement, "--json", "--pull=false",
            "-P", f"{LABEL_RUNNER}={IMAGE_RUNNER}",
            "--artifact-server-path", str(aux / "artefacts"),
            "--cache-server-path", str(aux / "cache"),
        ]
        if workflow:
            cmd += ["-W", workflow]
        if job:
            cmd += ["-j", job]
        if secrets_:
            _ecrire_dotenv(aux / "secrets.env", secrets_)
            cmd += ["--secret-file", str(aux / "secrets.env")]
        if variables:
            _ecrire_dotenv(aux / "vars.env", variables)
            cmd += ["--var-file", str(aux / "vars.env")]
        if payload is not None:
            (aux / "event.json").write_text(json.dumps(payload), encoding="utf-8")
            cmd += ["-e", str(aux / "event.json")]
        res = executer(cmd, cwd=d, env={"ACT_DISABLE_VERSION_CHECK": "1"}, timeout=timeout)
        brut = res.stdout + res.stderr
    return _lire_json_act(cmd, res.returncode, brut)


def _lire_json_act(cmd: list[str], rc: int, brut: str) -> ResultatAct:
    res = ResultatAct(commande=cmd, rc=rc, brut=brut)
    for ligne in brut.splitlines():
        try:
            obj = json.loads(ligne)
        except ValueError:
            continue
        if not isinstance(obj, dict):
            continue
        msg = str(obj.get("msg", ""))
        job_id = obj.get("jobID") or obj.get("job") or "?"
        if obj.get("raw_output"):
            for ecrite in msg.split("\n"):
                if ecrite == "" and msg.endswith("\n"):
                    continue
                res.lignes.append(ecrite)
                res.lignes_par_job.setdefault(job_id, []).append(ecrite)
        if obj.get("jobResult"):
            res.jobs.setdefault(job_id, []).append(str(obj["jobResult"]))
        if obj.get("stepResult"):
            res.steps.append({"job": job_id, "step": obj.get("step"), "resultat": str(obj["stepResult"])})
        if obj.get("level") == "error":
            res.erreurs.append(msg)
    if rc != 0 and not res.erreurs and not res.jobs:
        # act a refusé avant de jouer (workflow invalide, aucun job) : la
        # raison est dans la sortie brute.
        res.erreurs.append(brut.strip()[-600:])
    return res


# ── Lecture statique des workflows (compléments) ────────────────────────────


def fichiers_workflows(depot: Path) -> list[Path]:
    dossier = depot / ".github" / "workflows"
    if not dossier.is_dir():
        return []
    return sorted(p for p in dossier.iterdir() if p.suffix in (".yml", ".yaml"))


def exiger_workflows(depot: Path) -> list[Path]:
    fichiers = fichiers_workflows(depot)
    if not fichiers:
        pytest.fail(
            "Aucun fichier `.github/workflows/*.yml` dans le répertoire de travail : "
            "GitHub ne cherche les workflows que dans ce dossier, avec le point devant "
            "`.github` et l'extension .yml ou .yaml. Rien ne peut tourner tant qu'il "
            "n'existe pas."
        )
    return fichiers


def lire_workflows(depot: Path) -> dict[str, dict]:
    """Chaque workflow, analysé. Un YAML invalide est un échec qui nomme le fichier."""
    resultat: dict[str, dict] = {}
    for fichier in exiger_workflows(depot):
        try:
            donnees = yaml.safe_load(fichier.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            pytest.fail(
                f"{fichier.relative_to(depot)} n'est pas un YAML valide : {exc}. "
                "GitHub l'ignorerait, avec une erreur dans l'onglet Actions."
            )
        if not isinstance(donnees, dict):
            pytest.fail(f"{fichier.relative_to(depot)} ne contient pas un workflow (dictionnaire attendu).")
        resultat[str(fichier.relative_to(depot))] = donnees
    return resultat


def declencheurs(workflow: dict) -> set[str]:
    """Les événements d'un workflow. PyYAML lit la clé `on` comme le booléen True."""
    valeur = workflow.get("on", workflow.get(True))
    if valeur is None:
        return set()
    if isinstance(valeur, str):
        return {valeur}
    if isinstance(valeur, list):
        return {str(v) for v in valeur}
    if isinstance(valeur, dict):
        return {str(k) for k in valeur}
    return set()


@dataclass(frozen=True)
class ReferenceUses:
    fichier: str
    ligne: int
    action: str  # owner/repo ou owner/repo/chemin
    ref: str | None  # ce qui suit le @
    commentaire: str | None  # ce qui suit le #

    @property
    def locale(self) -> bool:
        return self.action.startswith("./") or self.action.startswith("docker://")

    @property
    def epinglee_par_sha(self) -> bool:
        return bool(self.ref) and re.fullmatch(r"[0-9a-f]{40}", self.ref or "") is not None


_RE_USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^\s'\"#]+)['\"]?\s*(?:#\s*(.*?)\s*)?$")


def references_uses(depot: Path) -> list[ReferenceUses]:
    """Chaque `uses:` des workflows, lu dans le texte pour garder le commentaire."""
    refs: list[ReferenceUses] = []
    for fichier in fichiers_workflows(depot):
        for numero, texte in enumerate(fichier.read_text(encoding="utf-8").splitlines(), 1):
            m = _RE_USES.match(texte)
            if not m:
                continue
            cible, commentaire = m.group(1), m.group(2)
            action, _, ref = cible.partition("@")
            refs.append(
                ReferenceUses(
                    fichier=str(fichier.relative_to(depot)),
                    ligne=numero,
                    action=action,
                    ref=ref or None,
                    commentaire=commentaire or None,
                )
            )
    return refs


def chaine_aleatoire(prefixe: str = "") -> str:
    """Une valeur que le point de départ ne peut pas connaître d'avance."""
    return f"{prefixe}{secrets.token_hex(12)}"
