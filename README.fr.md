# Formation GitHub Actions : les labs vérifiables

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/github-actions-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/github-actions-training)
[![Licence : MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

Catalogue de **labs vérifiables** pour la
[formation GitHub Actions](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/)
du blog de Stéphane Robert. Joué par la CLI
[dsoxlab](https://github.com/stephrobert/dsoxlab).

Lire un workflow ne prouve pas qu'on sait en écrire un. Chaque lab de ce dépôt
éprouve **une compétence du parcours**, jumelée à la leçon qui l'enseigne : il
pose un point de départ, énonce un objectif, et vérifie le travail en **jouant
réellement le workflow**, puis en lisant ce qu'il a produit. Jamais en relisant
le YAML que vous avez écrit.

> **État : en reconstruction (2026-09-25).** Le catalogue est refondu de A à Z
> pour suivre les 12 modules du parcours. Aucun lab n'est encore validé ; le
> plan complet est ci-dessous, et chaque lab a son issue. L'ancien TP
> `tp-01-premier-workflow` reste consultable sur la branche `master` en
> attendant son remplaçant, `fondations-premier-workflow`.

## Démarrer

```bash
uv tool install dsoxlab        # la CLI, outil externe

git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training
mise install                   # act, actionlint, zizmor, pinact, poutine, uv

dsoxlab list-labs
dsoxlab run       fondations-premier-workflow
dsoxlab challenge fondations-premier-workflow
dsoxlab check     fondations-premier-workflow
```

`dsoxlab hint <id>` donne un indice, déduit du score. `dsoxlab clean <id>`
remet le lab à zéro.

## Prérequis

- **Docker qui répond** (`docker info`). act exécute chaque job dans un
  conteneur qui imite le runner `ubuntu-24.04` de GitHub.
- **Les outils de [`mise.toml`](mise.toml)**, posés par `mise install` à la
  version mesurée : act 0.2.89, actionlint, zizmor, pinact, poutine, uv. act
  doit être au moins en 0.2.86 : les versions antérieures sont vulnérables à
  CVE-2026-34041 et CVE-2026-34042.
- **Pour les labs « plateforme » seulement** : un compte GitHub, un dépôt à
  vous, et `gh` authentifié. Ces labs lisent votre dépôt, désigné par
  `LAB_REPO=votre-compte/votre-depot`.

## Comment un lab se joue

`dsoxlab run` copie le point de départ dans `labs/<id>/challenge/work` : une
petite application, parfois un workflow à corriger. Vous y travaillez comme
dans un vrai dépôt. `dsoxlab check` joue alors vos workflows avec **act**, sur
votre poste, et vérifie ce qu'ils ont fait : jobs réussis ou sautés, sorties,
artefacts, findings d'un scanner.

Certaines choses n'existent que sur GitHub : les environnements protégés et
leurs approbations, OIDC, les attestations, les rulesets, Scorecard, les
filtres de déclencheur. Les labs qui en parlent se vérifient sur **votre
dépôt**, par l'API de GitHub. La colonne « act » du catalogue dit, pour chaque
lab, ce qui se joue en local.

| Ce que le lab doit jouer | En local avec act |
| --- | --- |
| jobs, `needs`, `if`, outputs, matrices, workflows réutilisables, actions composites | oui |
| cache, secrets masqués, `vars`, payload d'un événement | oui |
| filtres `branches:` et `paths:` de `on:` | non, sur votre dépôt |
| `services:` | non, sur votre dépôt |
| `upload-artifact` v6 et plus | non : les labs épinglent v5.0.0, le temps que [nektos/act#6174](https://github.com/nektos/act/pull/6174) soit fusionnée |
| environnements, approbations, OIDC, attestations, rulesets, Scorecard, `concurrency` | non, sur votre dépôt |

Mesuré le 2026-09-25 avec act 0.2.89 et Docker 29.1.3. Le détail, commande par
commande, est dans [`docs/conception.md`](docs/conception.md).

## Le catalogue

<!-- LABS:START -->

C'est l'ordre du [parcours du blog](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/),
tel que [`meta.yml`](meta.yml) le déclare. Chaque module du parcours est une
section, et chaque lab a une issue qui porte sa définition de terminé.

**act** : « oui » quand toute la preuve se joue en local, « partiel » quand une
partie seulement, « non » quand elle exige votre dépôt GitHub.

### Écrire son premier workflow

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `fondations-premier-workflow` | les tests tournent à chaque `push` et `pull_request`, et un test cassé fait échouer le pipeline | oui | [#16](https://github.com/stephrobert/github-actions-training/issues/16) |
| `secrets-et-variables` | un secret passe par `env:` et reste masqué, une valeur dérivée ne l'est plus | oui | [#17](https://github.com/stephrobert/github-actions-training/issues/17) |
| `evaluer-et-epingler-une-action` | chaque action sur le SHA du tag annoncé, et Dependabot pour les maintenir | partiel | [#18](https://github.com/stephrobert/github-actions-training/issues/18) |

### Concevoir des workflows dynamiques

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `pipeline-en-graphe` | `needs`, outputs de job, `if` sur l'événement, un rapport qui survit à l'échec | oui | [#19](https://github.com/stephrobert/github-actions-training/issues/19) |
| `matrice-de-tests` | produit cartésien, `include`, `exclude`, matrice dynamique par `fromJSON` | oui | [#20](https://github.com/stephrobert/github-actions-training/issues/20) |
| `reutiliser` | un workflow réutilisable avec inputs et outputs, une action composite | oui | [#21](https://github.com/stephrobert/github-actions-training/issues/21) |
| `declencheurs` | `workflow_dispatch` à inputs typés, `github.event_name`, les filtres prouvés sur la plateforme | partiel | [#22](https://github.com/stephrobert/github-actions-training/issues/22) |
| `services-conteneurs` | un job qui attend la santé de son service | non | [#23](https://github.com/stephrobert/github-actions-training/issues/23) |

### Défendre la chaîne d'approvisionnement

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `neutraliser-une-injection` | la charge d'un titre d'issue s'exécute avant, s'affiche telle quelle après | oui | [#24](https://github.com/stephrobert/github-actions-training/issues/24) |
| `epingler-et-maintenir` | un dépôt à tags mobiles passe en SHA, Dependabot le maintient avec un délai | partiel | [#25](https://github.com/stephrobert/github-actions-training/issues/25) |
| `auditer-avec-les-scanners` | un dépôt piégé rend 0 finding à zizmor, poutine et plumber, et ses workflows tournent toujours | oui | [#26](https://github.com/stephrobert/github-actions-training/issues/26) |
| `harden-runner-et-threat-model` | harden-runner en blocage avec une liste d'autorisation, et un modèle de menace versionné | partiel | [#27](https://github.com/stephrobert/github-actions-training/issues/27) |

### Droits minimaux, OIDC et provenance

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `permissions-minimales` | `permissions: {}` en tête, `write` dans le seul job qui publie | oui | [#28](https://github.com/stephrobert/github-actions-training/issues/28) |
| `desamorcer-pull-request-target` | le motif en deux workflows, et la garde contre un fork jouée avec un payload de fork | partiel | [#29](https://github.com/stephrobert/github-actions-training/issues/29) |
| `oidc-sans-cle-longue-duree` | aucune clé cloud dans les secrets, et une trust policy qui refuse le joker | partiel | [#30](https://github.com/stephrobert/github-actions-training/issues/30) |
| `attester-et-verifier` | `gh attestation verify` et `cosign verify`, sur une image publique puis sur la vôtre | non | [#31](https://github.com/stephrobert/github-actions-training/issues/31) |

### Un pipeline GitHub durci de bout en bout

Cinq ateliers dont le résultat de référence est
[`stephrobert/secure-python-pipeline`](https://github.com/stephrobert/secure-python-pipeline).
Ce dépôt apporte le point de départ, la vérification et la solution.

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `1-bootstrap-securise` | gouvernance, dépendances épinglées par hash, image non-root, zéro vulnérabilité HIGH ou CRITICAL | oui | [#32](https://github.com/stephrobert/github-actions-training/issues/32) |
| `2-pipeline-ci-durci` | actionlint, zizmor, poutine et plumber à zéro, et une CI qui teste vraiment | oui | [#33](https://github.com/stephrobert/github-actions-training/issues/33) |
| `3-build-verifiable` | provenance SLSA, SBOM attesté, signature Cosign, vérifiés par un tiers | non | [#34](https://github.com/stephrobert/github-actions-training/issues/34) |
| `4-protection-et-gouvernance` | un ruleset relu par l'API, CODEOWNERS sans erreur | non | [#35](https://github.com/stephrobert/github-actions-training/issues/35) |
| `5-scoring-et-durcissement` | Scorecard décortiqué contrôle par contrôle | non | [#36](https://github.com/stephrobert/github-actions-training/issues/36) |

### Livrer : environnements et déploiements

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `promouvoir-un-deploiement-approuve` | deux environnements, une approbation, la promotion par digest, le rollback sans rebuild | non | [#37](https://github.com/stephrobert/github-actions-training/issues/37) |

### Accélérer et déboguer les pipelines

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `artefacts-entre-jobs` | un build partagé par artefact, un rapport produit même en cas d'échec | oui | [#38](https://github.com/stephrobert/github-actions-training/issues/38) |
| `cache-des-dependances` | le cache touché au second passage, invalidé quand le fichier de verrouillage change | oui | [#39](https://github.com/stephrobert/github-actions-training/issues/39) |
| `debug-d-un-workflow` | un workflow qui échoue pour trois raisons distinctes, diagnostiqué puis corrigé | oui | [#40](https://github.com/stephrobert/github-actions-training/issues/40) |
| `concurrency` | l'annulation des runs obsolètes, et un déploiement qu'on n'annule jamais | non | [#41](https://github.com/stephrobert/github-actions-training/issues/41) |

### Choisir et sécuriser les runners

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `runner-ephemere-en-conteneur` | une image de runner non-root, enregistrée en éphémère, qui disparaît après un job | non | [#42](https://github.com/stephrobert/github-actions-training/issues/42) |
| `securiser-un-runner` | nettoyage entre les jobs, compte dédié, sortie réseau filtrée | partiel | [#43](https://github.com/stephrobert/github-actions-training/issues/43) |

### Gouverner la CI au-delà du YAML

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `rulesets-et-codeowners` | un ruleset actif, CODEOWNERS sans erreur, une PR bloquée sans revue | non | [#44](https://github.com/stephrobert/github-actions-training/issues/44) |
| `actions-autorisees` | la politique d'actions posée par l'API, et un workflow hors liste refusé | non | [#45](https://github.com/stephrobert/github-actions-training/issues/45) |

### L'outillage en ligne de commande

| Lab | Ce qu'il prouve | act | Suivi |
| --- | --- | --- | --- |
| `actionlint-corriger-des-workflows` | trois workflows fautifs rendus propres, une configuration pour les labels maison | oui | [#46](https://github.com/stephrobert/github-actions-training/issues/46) |
| `act-rejouer-en-local` | un workflow rejoué avec événement, inputs, secrets et matrice filtrée | oui | [#47](https://github.com/stephrobert/github-actions-training/issues/47) |
| `gh-piloter-les-runs` | déclencher, suivre jusqu'au verdict, relancer les seuls jobs en échec | non | [#48](https://github.com/stephrobert/github-actions-training/issues/48) |

Total : **33 labs planifiés, 0 validé.** Un lab n'est validé qu'après avoir
été joué dans les deux sens : 0 avant le travail, 100 après la solution de
référence, et de nouveau 0 après remise à zéro.

<!-- LABS:END -->

## Contribuer

Les règles d'écriture d'un lab, la doctrine de test et les conventions vivent
dans [`CONTRIBUTING.fr.md`](CONTRIBUTING.fr.md). Le socle du catalogue se suit
dans les issues [#11 à #15](https://github.com/stephrobert/github-actions-training/milestones).

## Ce que les labs corrigent dans les leçons

Chaque lab est jumelé à une leçon du blog, et l'écrire oblige à jouer ce que la
leçon affirme. La lecture complète du parcours a déjà relevé **23 constats sur
9 leçons**, dont 7 affirmations fausses, consignés avec leur preuve dans
[`docs/corrections-guides.md`](docs/corrections-guides.md). Par exemple, la
leçon sur act faisait installer une version vulnérable, et le premier workflow
de la formation contenait l'injection de template que la leçon suivante
interdit.

La formation enseigne, ce catalogue éprouve : ce qu'il contredit remonte au
blog.

## Licence

Copyright (c) 2024 Stéphane Robert, https://blog.stephane-robert.info

Ce dépôt est publié sous [licence MIT](LICENSE).
