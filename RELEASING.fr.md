# Publier une version de github-actions-training

**Langue :** [English](./RELEASING.md) · [Français](./RELEASING.fr.md)

Ce dépôt livre du **contenu de labs**, pas un paquet Python. Une version publie
un **bundle `tar.gz`** du catalogue comme asset d'une Release GitHub : pas de
PyPI, pas de wheel, aucun registre d'artefacts externe.

## Ce que contient une version

Le workflow `release.yml` construit
`github-actions-training-<version>.tar.gz` avec :

- `labs/`, `meta.yml`, `meta.fr.yml`, `curriculums.yml`, `conftest.py`,
  `pyproject.toml`, `uv.lock` et `mise.toml`,
- `scripts/` et `tests/`, parce qu'un catalogue qui prétend se valider doit
  livrer de quoi le faire,
- `validation-labs.json`, la preuve que chaque lab a été joué dans les deux
  sens par les vraies commandes dsoxlab, avec sa date et les versions de dsoxlab et des outils employés par les labs,
- les documents de gouvernance (`README`, `LICENSE`, `CONTRIBUTING`,
  `CODE_OF_CONDUCT`, `SECURITY`, `CHANGELOG`, `RELEASING`), **dans les deux
  langues** :
  l'archive est ce que reçoit quelqu'un qui n'a pas le dépôt.

Le verrou voyage avec `pyproject.toml` délibérément. Une contrainte `>=` laisse
chaque installation résoudre ce qu'elle veut ; une archive qui prétend livrer
de quoi se valider ne dirait pas **avec quoi**.

Il **exclut** les solutions de référence (`solution/`, chiffrées, ce sont les
réponses), le pilotage local non versionné et les fichiers générés (caches,
état runtime de dsoxlab). Une exclusion qui ne correspond à rien ne fait pas
échouer `tar`, contrairement à un chemin listé mais absent, ce qui a déjà
cassé une release dans le dépôt Linux jumeau.

Quatre artefacts accompagnent l'archive :

| Artefact | Rôle |
| --- | --- |
| `<pkg>.tar.gz.sha256` | empreinte d'intégrité |
| `provenance.intoto.jsonl` | provenance SLSA, ce que lit Scorecard Signed-Releases |
| `<pkg>.tar.gz.cosign.bundle` | bundle de signature Cosign keyless |
| (côté registre) | attestation de build native GitHub |

## Pourquoi trois jobs, et pas un seul

Le workflow est découpé en **construire**, **attester**, **publier**, et ce
découpage est la seule chose qui sépare SLSA Build Level 2 de Level 3.

La documentation GitHub le dit en deux phrases : « Artifact attestations by
itself provides SLSA v1.0 Build Level 2 », et « Reusable workflows can provide
isolation between the build process and the calling workflow, to meet SLSA
v1.0 Build Level 3 ». Tant que le job qui construit l'archive est aussi celui
qui signe sa provenance, rien n'empêche techniquement le processus de build de
produire une provenance qui ment. Le niveau 3 exige que la signature se fasse
hors de sa portée.

D'où `.github/workflows/attester.yml`, appelé comme workflow réutilisable :

- il est le **seul du dépôt** à recevoir la permission `attestations: write` ;
- il ne reçoit qu'un **nom et une empreinte**, jamais l'archive ni le dépôt : il
  ne fait aucun `checkout` ;
- le job de publication, lui, peut écrire la release mais **ne peut pas
  attester**, faute de cette permission ;
- l'archive est recomparée à son empreinte **avant** publication, pour qu'un
  artefact altéré entre deux jobs ne soit pas publié avec une provenance qui ne
  le décrit pas.

L'appel s'écrit `uses: ./.github/workflows/attester.yml`, et non la forme
« self-repository » `$/`, plus récente, que zizmor recommande pourtant. La
raison mérite d'être consignée : l'outillage de sécurité ne sait pas encore
lire `$/`, et un analyseur qui ne comprend pas une construction ne peut pas la
juger sûre. Mesuré le 2026-09-15, sur cette ligne exactement : actionlint la
rejette comme un format invalide, zizmor 1.26.1 refuse de charger le fichier et
n'audite plus rien, et Plumber la prend pour une action tierce non épinglée
venant d'une source non autorisée, deux constats HIGH et un score de 70/100 au
lieu de 100/100. Le workflow appelé est celui qui SIGNE : c'est la dernière
ligne du dépôt sur laquelle se priver du regard des analyseurs.

## Produire une version

1. Vérifier que le catalogue est vert, et pas seulement livrable :

   ```bash
   dsoxlab validate-structure --check-urls
   pre-commit run --all-files --hook-stage pre-push
   python3 scripts/verify-solutions.py --deux-sens --check
   python3 scripts/valider-labs.py      # écrit validation-labs.json
   ```

2. **Réattester les labs qui ont changé depuis leur verdict.** Un lab dont les
   tests, les fichiers, un `conftest.py` commun ou les descripteurs ont été
   modifiés après le commit qui a inscrit son verdict n'est plus attesté par
   `validation-labs.json`. Depuis le dépôt du site (`test-astro-5`, cloné à
   côté de ce dépôt), lancer :

   ```bash
   python3 scripts/reattester-labs.py --depot github-actions-training           # plan et garde-fous
   python3 scripts/reattester-labs.py --depot github-actions-training --apply   # rejoue et commite
   ```

   Le script rejoue chaque lab « à réattester » par `scripts/valider-labs.py`,
   un par un (tests et lab modifiés d'abord, puis `conftest.py` commun, puis
   descripteurs), vérifie que le diff de `validation-labs.json` ne touche que
   ces labs, relance `--check` et `pytest tests/`, puis fait un commit **local**
   du seul relevé. Il refuse un dépôt non propre et un lab actif. Un verdict
   ROUGE n'est pas commité : corriger le lab, puis relancer.

   Avant de taguer, relancer le dry-run : il doit afficher
   **« 0 lab(s) à réattester »**. Pousser ensuite le commit du relevé avec le
   reste de la version.

3. Basculer les entrées de `CHANGELOG.md` sous une nouvelle version.
4. Taguer et pousser le tag, ce qui déclenche `release.yml` :

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. Le workflow construit le `tar.gz`, atteste sa provenance, le signe en
   keyless et crée la Release GitHub avec des notes générées automatiquement.

## Vérifier une version

Intégrité et contenu :

```bash
sha256sum -c github-actions-training-<version>.tar.gz.sha256
tar tzf github-actions-training-<version>.tar.gz | head
```

Provenance du build. Prouve que l'archive a bien été produite par le workflow de
ce dépôt, et non reconstruite par quelqu'un d'autre :

```bash
gh attestation verify github-actions-training-<version>.tar.gz \
  --repo stephrobert/github-actions-training
```

**La vérification qui atteste le niveau 3** nomme le workflow signataire. Elle
échoue si la provenance a été produite ailleurs que par le workflow
d'attestation isolé, et c'est elle qu'il faut lancer à la première release pour
confirmer que la chaîne tient :

```bash
gh attestation verify github-actions-training-<version>.tar.gz \
  --repo stephrobert/github-actions-training \
  --signer-workflow stephrobert/github-actions-training/.github/workflows/attester.yml
```

Signature Cosign keyless. Les **deux** options de certificat sont obligatoires :
sans elles, `cosign verify-blob` accepte n'importe quelle identité, ce qui vide
la vérification de son sens.

```bash
cosign verify-blob \
  --bundle github-actions-training-<version>.tar.gz.cosign.bundle \
  --certificate-identity-regexp "https://github.com/stephrobert/github-actions-training/.github/workflows/release.yml@.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  github-actions-training-<version>.tar.gz
```

> **Piège de version Cosign.** La CI installe **Cosign 3.x**, qui écrit un
> nouveau format de bundle. Un **Cosign 2.x** local répond `no signatures found`
> sur une archive pourtant parfaitement signée : la release n'est pas cassée,
> c'est l'outil local qui ne sait pas lire le format. Vérifiez `cosign version`
> et alignez-le avant de conclure quoi que ce soit.

## Réglages GitHub à faire une fois

Deux workflows ont besoin d'une configuration qui ne vit pas dans le dépôt :

- **`plumber.yml`** attend un environnement `security`, restreint à la branche
  `main`, portant le secret `PLUMBER_ADMIN_TOKEN` : un PAT à portée fine avec
  Administration, Contents et Metadata en lecture. Sans lui, le workflow tourne
  quand même, sur le jeton du job, mais le contrôle `branchMustBeProtected`
  s'abstient et le score reste incomplet.
- **La protection de la branche `main`**, par le ruleset « Protection de main » :
  c'est elle que Scorecard et Plumber mesurent. Historique linéaire, suppression
  et poussée en force interdites, passage par pull request avec résolution des
  fils de discussion, et les jobs de la CI en contrôles obligatoires.

### Le ruleset « Protection de main », prêt à appliquer

Un ruleset est un réglage GitHub, pas un fichier du dépôt : il ne voyage pas
avec un `git push`. Il se pose **une fois**, après la création du dépôt et le
premier passage de la CI (un contrôle obligatoire doit avoir tourné au moins
une fois pour que GitHub le propose). La charge ci-dessous reprend les règles
des catalogues voisins ; les contextes sont les noms des jobs de `ci.yml`, la
matrice CodeQL en donnant deux.

Aucune approbation n'est exigée (`required_approving_review_count: 0`) : le
dépôt n'a qu'un mainteneur, qui ne peut pas approuver sa propre pull request.
Le passage par pull request, la résolution des fils et la CI verte restent
obligatoires.

```bash
gh api --method POST repos/stephrobert/github-actions-training/rulesets \
  --input - <<'JSON'
{
  "name": "Protection de main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "required_linear_history"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": true,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": true}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "required_status_checks": [
        {"context": "Zizmor (workflow static analysis)"},
        {"context": "Actionlint (workflow syntax)"},
        {"context": "Poutine (CI/CD exploit chains)"},
        {"context": "Pre-commit parity (all hooks)"},
        {"context": "Contrat du catalogue (leçons jumelées comprises)"},
        {"context": "CodeQL (python)"},
        {"context": "CodeQL (actions)"}]}}
  ]
}
JSON
```

Ce bloc n'a **jamais été appliqué** : le dépôt n'existe pas encore sur GitHub.
À la première application, relire le ruleset créé dans *Settings > Rules* et
vérifier qu'une poussée directe sur `main` est refusée.
