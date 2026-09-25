# GitHub Actions DevSecOps Training : les labs de la formation

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/github-actions-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/github-actions-training)
[![Licence : CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Formation pratique **GitHub Actions et sécurité de la chaîne
d'approvisionnement**, pilotée par la CLI
[`dsoxlab`](https://github.com/stephrobert/dsoxlab). Ce dépôt est le **catalogue
de labs** de la formation GitHub Actions du site
[blog.stephane-robert.info](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/),
du premier workflow aux runners auto-hébergés, avec un angle de durcissement
systématique.

## Ce que c'est

`github-actions-training` est un **dépôt de contenu**, pas une application. Il
propose :

- des **labs** jumelés chacun à une leçon du parcours, du premier workflow à la
  gouvernance de la CI,
- des **challenges** sans pas-à-pas, pour vérifier l'autonomie,
- une **validation automatique** qui **joue réellement tes workflows** et
  prouve ce qu'ils ont produit (et non que tu as écrit tel mot-clé),
- un **scoring** avec des indices à coût variable.

La CLI `dsoxlab` est le seul point d'entrée : elle démarre un lab, affiche les
instructions, valide, note et fait le bilan. Elle vit dans **son propre dépôt**
et s'installe **séparément** : elle ne fait pas partie de ce dépôt.

> **État : en reconstruction (2026-09-25).** Le catalogue est refondu pour
> suivre les 12 modules du parcours. Le plan complet, un lab par compétence, se
> suit dans les [jalons](https://github.com/stephrobert/github-actions-training/milestones)
> et les [issues](https://github.com/stephrobert/github-actions-training/issues).

## Prérequis

- Python 3.11+ et [`uv`](https://docs.astral.sh/uv/)
- `git`
- **Docker** qui répond (`docker info`) : act exécute chaque job dans un
  conteneur qui imite le runner `ubuntu-24.04` de GitHub.
- [`mise`](https://mise.jdx.dev/), qui pose act, actionlint, zizmor, pinact,
  poutine et uv aux versions épinglées dans `mise.toml`.
- Pour les labs **plateforme** seulement : un compte GitHub, un dépôt à toi et
  `gh` authentifié.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/) : on
l'installe comme un outil autonome.

```bash
# 1. Installer la CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab        # ou : pipx install dsoxlab

# 2. Cloner ce catalogue de labs
git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training

# 3. Installer l'outillage épinglé (act, actionlint, zizmor, pinact, poutine, uv)
mise install

# 4. Vérifier que tout est en place
dsoxlab doctor
```

### Ton premier lab, en cinq minutes

**Commence par la section `fondations`.** Ses labs se jouent entièrement sur
ton poste : act exécute tes workflows dans Docker, sans pousser quoi que ce
soit sur GitHub.

```bash
dsoxlab use fondations                # section de départ
dsoxlab next                          # → fondations-premier-workflow
```

Puis, pour ce lab comme pour tous les autres, le même cycle en quatre temps :

```bash
dsoxlab course fondations-premier-workflow      # 1. le contexte, puis le cours
dsoxlab challenge fondations-premier-workflow   # 2. ce qui t'est demandé
dsoxlab run fondations-premier-workflow         # 3. prépare ton espace de travail
                                                #    (challenge/work/) et t'y place
dsoxlab check fondations-premier-workflow       # 4. joue tes workflows, valide et note
```

`run` est l'étape que l'on oublie : c'est elle qui copie le point de départ
(une petite application, parfois un workflow à corriger) dans
`challenge/work/`. Un `check` lancé sans `run` échoue en annonçant que rien
n'est fait, ce qui est vrai mais trompeur.

Bloqué ? `dsoxlab hint <id>` révèle un indice, au prix de quelques points.

### Passer aux labs « plateforme »

Certaines fonctions n'existent que sur GitHub : environnements protégés et
approbations, OIDC, attestations, rulesets, Scorecard, filtres de
déclencheur. Les labs qui en parlent se vérifient sur **ton dépôt**, par l'API
de GitHub.

```bash
gh auth status                              # gh doit être authentifié
export LAB_REPO=ton-compte/ton-depot        # le dépôt que le lab va lire
dsoxlab check <id>
```

Vérifie ton environnement avec `dsoxlab doctor` (Python, pytest, runtimes, labs
détectés).

### Garder à jour

De nouveaux labs arrivent dans ce dépôt, et la CLI évolue de son côté. Mets à
jour chacun séparément :

```bash
git pull                       # récupère les labs nouveaux/mis à jour dans ton clone
mise install                   # aligne l'outillage sur les versions épinglées
uv tool upgrade dsoxlab        # met à jour la CLI (ou : pipx upgrade dsoxlab)
```

Tes réponses en cours vivent dans le `challenge/work/` de chaque lab, qui est
gitignoré : `git pull` apporte donc les nouveaux labs sans jamais toucher à ton
travail.

## Comment ça marche

### Le contrat déclaratif (deux niveaux)

Le catalogue est décrit par des données, pas par du code : le moteur `dsoxlab`
reste agnostique du domaine et lit deux niveaux de fichiers.

- **`meta.yml`** à la racine déclare l'identité du dépôt et l'**ordre** des
  sections affiché par `list-labs`. Chaque section est un module du parcours du
  blog. Il n'y a pas de bloc `infra` : aucune machine à provisionner.
- **`lab.yaml`** par lab (sous `labs/<module>-<sujet>/`) déclare ses `skills`,
  son `level` (le module du parcours), son `runtime` et ses `fixtures`, son
  `doc_url` (la leçon jumelée) et un bloc `validation`. Un `lab.fr.yaml`
  optionnel surcharge le `title` et la `description` en français.

`dsoxlab validate-structure` vérifie tout le contrat : le `meta.yml` est
conforme, chaque lab référencé existe avec un `lab.yaml` valide, et chaque
fixture ou fichier de test référencé est présent.

### Le cycle de vie d'un lab

L'apprenant pilote tout via la CLI ; un parcours type :

```bash
dsoxlab doctor                        # vérifier l'environnement (Python, pytest, runtimes, labs)
dsoxlab list-labs                     # parcourir le catalogue
dsoxlab show <id>                     # métadonnées et statut d'un lab
dsoxlab run <id>                      # préparer l'espace de travail
dsoxlab course <id>                   # lire le cours guidé (optionnel)
dsoxlab challenge <id>                # lire la mission (sans pas-à-pas)
dsoxlab hint <id>                     # révéler un indice (déduit du score)
dsoxlab check <id>                    # jouer les workflows, calculer et noter
dsoxlab submit <id>                   # soumission finale, ferme la session
dsoxlab progress                      # progression par bloc, score moyen
```

C'est `run` qui monte l'environnement : il crée le `workdir` du lab et copie
les fixtures déclarées. Tout se passe ensuite sur ton poste, dans ce
répertoire, comme dans un vrai dépôt.

### Les runtimes

| Runtime | Backend | Ce qu'il apporte |
|---|---|---|
| `shell` | shell local, act et Docker | Tous les labs. act rejoue tes workflows dans des conteneurs qui imitent le runner `ubuntu-24.04`, sur ta machine, sans rien pousser. |

Ce qu'act ne sait pas jouer se vérifie sur ton dépôt GitHub. Mesuré le
2026-09-25 avec act 0.2.89 et Docker 29.1.3 :

| Ce que le lab doit jouer | En local avec act |
|---|---|
| jobs, `needs`, `if`, outputs, matrices, workflows réutilisables, actions composites | oui |
| cache, secrets masqués, `vars`, payload d'un événement | oui |
| filtres `branches:` et `paths:` de `on:` | non, sur ton dépôt |
| `services:` | non, sur ton dépôt |
| `upload-artifact` v6 et plus | non : les labs épinglent v5.0.0 tant que [nektos/act#6174](https://github.com/nektos/act/pull/6174) n'est pas fusionnée |
| environnements, approbations, OIDC, attestations, rulesets, Scorecard, `concurrency` | non, sur ton dépôt |

act doit être au moins en 0.2.86 : les versions antérieures sont vulnérables à
CVE-2026-34041 et CVE-2026-34042. Le détail des mesures est dans
[`docs/conception.md`](./docs/conception.md).

### Le modèle de validation

La validation **prouve ce que tes workflows font, elle ne fait pas confiance à
l'apprenant**. Chaque lab embarque des tests `pytest` sous `challenge/tests/`
qui **jouent tes workflows avec act** et vérifient ce qu'ils ont produit : le
job de test a réussi **et** échoue quand un test casse, le secret est passé
**et** reste masqué, l'action est épinglée **et** sur le SHA du tag annoncé.
Un test qui vérifie seulement qu'un mot-clé figure dans le YAML est rejeté.

- Côté formateur, `scripts/valider-labs.py` enchaîne `dsoxlab run`, `check` et
  `clean` pour prouver chaque lab **dans les deux sens** : 0 avant le travail,
  100 après la solution de référence (`solution/`), et de nouveau 0 après remise
  à zéro.
- Dans `dsoxlab check` (le parcours apprenant), les tests valident **ton**
  travail, dans ton `challenge/work/`.
- Le dernier test d'un lab exerce **les deux côtés** : ce qui doit être refusé
  l'est, ce qui doit passer passe.

### Scoring, indices, progression

`check` enregistre un score (tests réussis/total, moins le coût des indices
utilisés). Les indices sont **à coût variable** : en révéler un déduit des
points, d'où leur caractère opt-in. L'historique vit dans une base SQLite **propre à ce dépôt**
(`.dsoxlab.db`, à la racine, gitignorée) ; `dsoxlab scores` et
`dsoxlab progress` la lisent. La session active est stockée par dépôt dans
`.dsoxlab-context.json`.

## Catalogue

Les labs vivent sous `labs/` et sont ordonnés par `meta.yml`, un module du
parcours par section. La table ci-dessous est générée à partir des vrais
`lab.yaml` : lance `python3 scripts/gen_catalog.py` pour la rafraîchir. Les
labs à venir se suivent dans les
[jalons](https://github.com/stephrobert/github-actions-training/milestones).

<!-- LABS:START -->
### Écrire son premier workflow

| Lab (id) | Titre | Niveau | Certif | Runtime | Guide compagnon |
|---|---|---|---|---|---|
| `fondations-premier-workflow` | Premier workflow : les tests tournent à chaque push, et un test cassé fait échouer le pipeline | fondations | - | shell | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/workflow/) |

_1 lab, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contribuer et licence

- Contribuer : voir [CONTRIBUTING](./CONTRIBUTING.fr.md).
- Conduite : [Code de conduite](./CODE_OF_CONDUCT.fr.md) · Sécurité : [SECURITY](./SECURITY.fr.md).
- Corrections des leçons du blog relevées par les labs : [corrections-guides](./docs/corrections-guides.md).
- Licence : [CC BY 4.0](./LICENSE).

### Licence

Copyright (c) 2026 Stéphane Robert, https://blog.stephane-robert.info

Ce catalogue est publié sous licence
[Creative Commons Attribution 4.0 International (CC BY 4.0)](./LICENSE). Vous
pouvez le partager et l'adapter, y compris commercialement, à une condition :
créditer Stéphane Robert, lier le blog, et indiquer si vous avez modifié le
contenu, sans laisser entendre que l'auteur approuve votre usage.

Le fichier `LICENSE` ne contient que le texte officiel de la licence, sans
en-tête ajouté : c'est ce qui permet à GitHub de la reconnaître.
