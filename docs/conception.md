# Conception des labs

Ce document dit **pourquoi** le catalogue est organisé ainsi. Il a été écrit le
2026-09-25 à partir d'une lecture complète des 69 leçons du parcours et d'une
série de mesures sur act 0.2.89. Quand une décision repose sur une mesure, la
mesure est donnée : une conception qui ne se vérifie pas ne vaut rien.

## Ce que le catalogue doit prouver

Le parcours LMS `github-actions` compte 12 modules et 69 leçons, dont 6 de type
`lab`. Ces six labs s'appuient sur le dépôt `stephrobert/secure-python-pipeline`
et se vérifient à la main : aucune page ne fournit de point de départ, de
vérification automatique ni de solution rejouable. Six modules sur douze n'ont
**aucun** lab : `fondations`, `workflows`, `optimiser`, `runners`,
`gouvernance`, `outils`, soit 45 leçons sans pratique.

La question qui pilote ce dépôt est donc la même que celle des catalogues
frères : **combien de compétences du parcours l'apprenant peut-il démontrer
réellement, et se vérifier lui-même ?**

## La règle non négociable : un lab s'éprouve dans les deux sens

Une vérification qui passe **avant** le travail ne mesure rien. Chaque lab de ce
dépôt est joué par `scripts/valider-labs.py` dans cet ordre :

1. le point de départ (`challenge/`) est copié dans un répertoire temporaire ;
2. la vérification DOIT rendre **0/100** ;
3. la solution de référence (`solution/`) est posée par-dessus ;
4. la vérification DOIT rendre **100/100** ;
5. le cycle est rejoué une seconde fois, pour prouver qu'il est rejouable.

Le verdict est écrit dans `validation-labs.json`, avec la date, la version d'act
et l'empreinte de l'image du runner. Un lab absent de ce fichier est un lab
**livrable**, pas un lab **validé**.

Les tests d'un lab lisent **l'état**, jamais les commandes tapées : ils jouent
le workflow avec act et regardent ce qu'il produit (résultat des jobs, lignes
écrites, jobs sautés, artefacts, findings d'un scanner). Un test qui ne fait que
relire le YAML est un complément, jamais la preuve ; il est nommé comme tel.
Le dernier test de chaque lab exerce **les deux côtés** : ce qui doit être
refusé l'est, et ce qui doit passer passe.

## Ce qu'act sait faire, mesuré

Mesuré le 2026-09-25, act 0.2.89 (mise), Docker 29.1.3, image
`catthehacker/ubuntu:act-24.04` au digest
`sha256:c58e2b364da03b0c804c7d660f2ecbedf2f221a382b9baa0b344b0144780ff43`
(construite le 2026-08-15).

| Ce que le lab a besoin de jouer | act | Mesure |
| --- | --- | --- |
| jobs, steps, `needs`, `if`, `github.event_name` | oui | `outputs.yml` : `use` tourne sur `push`, `only-pr` sur `pull_request` |
| `$GITHUB_OUTPUT`, outputs de job, `needs.X.outputs` | oui | `got v1.2.3` relu dans le job dépendant |
| `strategy.matrix`, `include` | oui | 3 jobs générés, `experimental=true` sur la seule combinaison ajoutée |
| `uses: ./.github/workflows/x.yml` (`workflow_call`) avec inputs et outputs | oui | `resultat=deploye-sur-staging` remonté à l'appelant |
| action composite locale avec inputs et outputs | oui | `msg=bonjour monde` |
| `actions/cache` (`--cache-server-path`) | oui | `cache-hit=true` au second passage |
| masquage d'un secret (`-s`), `vars` (`--var`) | oui | `le secret est ***` |
| `actions/setup-python` puis `pip`, `pytest` | oui | 36 s au premier passage |
| commandes `::warning::`, `::notice::` | oui | affichées |
| `-e event.json` (payload d'une issue, d'une PR, `inputs`) | oui | une injection par `github.event.issue.title` s'exécute, la forme `env:` l'affiche telle quelle |
| filtres `branches:` et `paths:` de `on:` | **non** | le job tourne pour `refs/heads/feature` comme pour `main` |
| `actions/upload-artifact` v6 et v7, `download-artifact` v7 et v8 | **non** | `unknown field "mime_type"` ; PR amont nektos/act#6174 ouverte ; v5.0.0 + v6.0.0 fonctionnent |
| `services:` | **non** | le job tourne en `network=host`, le service sur un réseau dédié : `redis:6379` et `127.0.0.1:6379` injoignables |
| `concurrency`, `timeout-minutes` réels, `environment` et approbations, OIDC, attestations, GHCR, rulesets, Scorecard, harden-runner | **non** | ce sont des services de la plateforme, act ne les émule pas |

Trois conséquences :

- un lab dont le sujet est un filtre de déclencheur ne se prouve pas avec act,
  il se prouve avec `gh run list` sur un dépôt de l'apprenant ;
- un lab sur les artefacts épingle `upload-artifact` v5.0.0 et
  `download-artifact` v6.0.0 **tant que** la PR amont n'est pas fusionnée, et
  le dit ;
- tout ce qui exige la plateforme reçoit un chemin « plateforme » : le test lit
  le dépôt de l'apprenant par `gh api` quand `LAB_REPO=owner/nom` est fourni,
  et s'arrête avec un message clair sinon.

## Anatomie d'un lab

```text
labs/<module>/<id>/
  lab.yaml              le contrat : module, leçons éprouvées, jouabilité act
  scenario.md           la situation et l'objectif, jamais un mode d'emploi
  challenge/            le point de départ, que l'apprenant modifie
    .actrc              l'image du runner, épinglée par digest
    .github/workflows/  ce qu'il y a à écrire ou à corriger
    hints.yaml          quatre indices, encodés en base64, de coût croissant
    tests/test_functional.py   la preuve, lue par pytest
  solution/             la solution de référence, posée par-dessus challenge/
```

`<module>` est l'identifiant du module dans le parcours (`fondations`,
`workflows`, `securite`, ...). `meta.yml` donne l'ordre de jeu, calqué sur le
parcours ; `tests/test_meta_declare_les_labs.py` refuse un lab présent sur le
disque et absent de `meta.yml`, ou l'inverse.

L'apprenant joue ainsi :

```bash
mise install                                   # act, actionlint, zizmor, pinact, uv
cd labs/fondations/premier-workflow/challenge  # lire scenario.md d'abord
# ... le travail ...
python3 ../../../../scripts/verifier-lab.py fondations-premier-workflow
python3 ../../../../scripts/indice.py fondations-premier-workflow 1
```

## Le sort de `tp-01-premier-workflow`

Refondu en `labs/fondations/premier-workflow`. Trois raisons, mesurées :

- sa vérification (`validate.py`) était une **analyse statique** du YAML : un
  workflow qui écrit `run: echo pytest` la passait sans jamais exécuter un
  test. Le nouveau lab joue le workflow avec act, et vérifie qu'un test cassé
  fait échouer le pipeline ;
- son README était un mode d'emploi de 500 lignes, en Node.js, alors que son
  challenge était en Python, et la page `workflows/index.mdx` du blog le
  décrivait dans les deux langages à la fois ;
- le blog y renvoie par `github.com/stephane-robert/github-actions-training/blob/main/...` :
  mauvais propriétaire (`stephrobert`) et mauvaise branche (`master`). Le lien
  est mort. C'est au blog de le corriger, vers
  `labs/fondations/premier-workflow/scenario.md`.

L'application calculatrice et ses neuf tests sont conservés.

## Articulation avec `secure-python-pipeline`

Le dépôt `secure-python-pipeline` reste **le résultat de référence** des cinq
labs du module `securite-lab` et du lab de promotion du module `deployer` :
c'est lui que les pages du blog décrivent, et c'est lui qui porte un Scorecard,
un score Plumber et des attestations publiques qu'un tiers peut vérifier.

Ce qu'il ne peut pas être, et que ce dépôt apporte :

- **un point de départ** : chaque lab `securite-lab/*` part de l'état laissé
  par le lab précédent (l'application minimale, puis les fichiers de
  gouvernance, puis la CI) ;
- **une vérification** : locale quand elle existe (`ruff`, `pytest`, `bandit`,
  `pip-audit`, `trivy`, `actionlint`, `zizmor --offline`,
  `poutine analyze_local`), par `gh api` sur le fork de l'apprenant pour les
  rulesets, les environnements, les attestations et Scorecard ;
- **une solution rejouable**, paramétrée par `${{ github.repository }}` et
  `${{ github.repository_owner }}` là où le dépôt de référence écrit
  `stephrobert` en dur.

Trois écarts mesurés entre les pages et le dépôt de référence, à remonter à
Stéphane et non à corriger ici : les SHA de `checkout`, `setup-python`,
`login-action`, `plumber`, `scorecard-action` et `upload-sarif` des pages ne
sont pas ceux du dépôt ; `deploy.yml`, promis par `lab-promotion.mdx`, n'existe
pas dans le dépôt ; le digest de l'image de base cité dans `bootstrap.mdx` a
été remplacé le 2026-09-11.

## Les labs, module par module

Le tableau dit ce que chaque lab prouve et comment. La colonne act vaut
« oui » quand la preuve entière se joue en local, « partiel » quand une partie
seulement, « non » quand la preuve exige la plateforme.

### fondations

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `premier-workflow` | les tests d'une application tournent à chaque `push` et `pull_request`, et un test cassé fait échouer le pipeline | oui |
| `secrets-et-variables` | un secret passe par `env:`, reste masqué, et une valeur dérivée (base64) ne l'est plus ; une `vars` s'affiche en clair | oui |
| `evaluer-et-epingler-une-action` | chaque action est épinglée sur le SHA du tag annoncé (vérifié par `pinact --verify`), et Dependabot est déclaré pour les maintenir | partiel |

### workflows

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `pipeline-en-graphe` | `needs`, outputs de job, `if` sur l'événement, propagation des sauts, rapport final en `!cancelled()` | oui |
| `matrice-de-tests` | produit cartésien, `include` qui enrichit ou ajoute, `exclude`, matrice dynamique par `fromJSON` | oui |
| `reutiliser` | un `workflow_call` local avec inputs et outputs, une action composite locale avec `shell:` obligatoire | oui |
| `declencheurs` | `workflow_dispatch` avec inputs typés, `github.event_name` ; les filtres se prouvent sur la plateforme | partiel |
| `services-conteneurs` | un job qui attend la santé de son service ; act ne le joue pas | non |

### securite

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `neutraliser-une-injection` | une charge dans le titre d'une issue s'exécute avant, s'affiche telle quelle après ; zizmor rend 0 finding | oui |
| `epingler-et-maintenir` | un dépôt à tags mobiles passe en SHA, `pinact --verify` confirme, `dependabot.yml` porte un `cooldown` | partiel |
| `auditer-avec-les-scanners` | un dépôt piégé sur chaque règle citée par les leçons zizmor, poutine et plumber rend 0 finding, et ses workflows tournent toujours | oui |
| `harden-runner-et-threat-model` | harden-runner en premier step, en `block` avec une allowlist, et un modèle de menace versionné et validé par schéma | partiel |

### securite-permissions

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `permissions-minimales` | `permissions: {}` en tête, `write` seulement dans le job qui publie ; Scorecard Token-Permissions en local | oui |
| `desamorcer-pull-request-target` | le motif en deux workflows (`pull_request` puis `workflow_run`), la garde `head.repo.fork` jouée sous act avec un payload de fork | partiel |
| `oidc-sans-cle-longue-duree` | aucune clé cloud dans les secrets, `id-token: write` au niveau job, une trust policy qui refuse `repo:owner/*` | partiel |
| `attester-et-verifier` | `gh attestation verify` et `cosign verify` sur une image publique, puis sur l'image du fork de l'apprenant | non |

### securite-lab (résultat de référence : `secure-python-pipeline`)

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `1-bootstrap-securise` | gouvernance, dépendances par hash, image non-root, zéro vulnérabilité HIGH/CRITICAL | oui |
| `2-pipeline-ci-durci` | actionlint, zizmor, poutine et plumber à zéro, et la CI qui teste vraiment | oui |
| `3-build-verifiable` | provenance SLSA, SBOM attesté, signature Cosign, vérifiés par un tiers | non |
| `4-protection-et-gouvernance` | un ruleset relu par `gh api`, CODEOWNERS sans erreur, plumber à 21/21 | non |
| `5-scoring-et-durcissement` | Scorecard décortiqué contrôle par contrôle, fuzzing | non |

### deployer

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `promouvoir-un-deploiement-approuve` | deux environnements, une approbation, la promotion par digest, le rollback sans rebuild | non |

### optimiser

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `artefacts-entre-jobs` | un build partagé par `needs` et artefact, `if-no-files-found: error`, `if: always()` pour les rapports | oui (v5/v6, voir plus haut) |
| `cache-des-dependances` | `cache-hit` au second passage, invalidation quand le lockfile change, version de Python dans la clé | oui |
| `debug-d-un-workflow` | un workflow qui échoue pour trois raisons distinctes, à diagnostiquer et corriger | oui |
| `concurrency` | l'annulation des runs obsolètes, lue sur les runs du dépôt de l'apprenant | non |

### runners

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `runner-ephemere-en-conteneur` | une image de runner non-root construite, enregistrée en `--ephemeral`, qui disparaît après un job | non |
| `securiser-un-runner` | nettoyage entre les jobs par les hooks du runner, compte dédié, sortie réseau filtrée | partiel |

### gouvernance

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `rulesets-et-codeowners` | un ruleset actif relu par `gh api`, `codeowners/errors` vide, une PR bloquée sans revue | non |
| `actions-autorisees` | la politique d'actions posée au niveau du dépôt par API, et un workflow hors liste refusé | non |

### outils

| Lab | Ce qu'il prouve | act |
| --- | --- | --- |
| `actionlint-corriger-des-workflows` | trois workflows fautifs rendus propres, `actionlint.yaml` pour les labels maison | oui |
| `act-rejouer-en-local` | un workflow rejoué avec événement, inputs, secrets et matrice filtrée | oui |
| `gh-piloter-les-runs` | déclencher, suivre avec `--exit-status`, relancer les seuls jobs en échec | non |

## Ce qui reste à Stéphane

Les décisions qui ne se prennent pas ici :

- corriger dans le blog le lien vers ce dépôt (`workflows/index.mdx`), et les
  erreurs de leçons relevées dans les issues de chaque lab ;
- publier `deploy.yml` dans `secure-python-pipeline` et y remplacer
  `stephrobert` en dur par le contexte du dépôt, pour qu'un fork produise une
  image sans retouche ;
- décider si les labs « plateforme » exigent un fork public par apprenant, ce
  qui est le cas aujourd'hui pour les rulesets et les environnements protégés.
