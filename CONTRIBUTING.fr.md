# Contribuer à github-actions-training

**Langue :** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

Ce dépôt est un **catalogue de labs** consommé par la CLI
[`dsoxlab`](https://github.com/stephrobert/dsoxlab). Les contributions sont de
nouveaux labs et des correctifs. La CLI vit dans son propre dépôt : n'ajoutez
ici ni runner, ni calcul de score, ni gestion des indices. Si vous butez sur
une limite du moteur, ouvrez une issue
[dans son dépôt](https://github.com/stephrobert/dsoxlab/issues) plutôt que de
la contourner localement.

## Mise en place

```bash
uv tool install dsoxlab        # la CLI, outil externe
git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training
git switch develop             # on ne travaille jamais sur master
mise install                   # act, actionlint, zizmor, pinact, poutine, uv
dsoxlab doctor                 # vérifier l'environnement
```

## Les branches

`master` reste dans son état publié tant que le catalogue refondu n'est pas
complet et validé. Le travail se fait sur une **branche dédiée**, ouverte
depuis `develop`, et revient dans `develop` par une pull request. Aucune
fusion automatique.

## La règle non négociable : un lab s'éprouve dans les deux sens

Un test qui passe ne prouve rien tant qu'on n'a pas vu **échouer** ce qui doit
échouer. Un lab dont les tests passent **avant** le travail ne mesure rien, et
c'est le défaut le plus coûteux du domaine parce qu'il ne se voit qu'ainsi.

```bash
python3 scripts/valider-labs.py --lab <id>
```

Le validateur enchaîne les commandes de dsoxlab : il pose le point de départ
(`dsoxlab run`), vérifie que le score est **0**, pose la solution de
référence, vérifie que le score est **100**, remet à zéro, rejoue, puis
nettoie. Il refuse de jouer avec une autre version d'act que celle de
`mise.toml`, et note la date, la version d'act et le digest de l'image du
runner dans `validation-labs.json`. Un lab absent de ce fichier est
**livrable**, pas **validé**.

Le contrôle mécanique ne dit **rien** de la justesse d'un lab, mais il refuse
un lab non conforme avant qu'un humain ne le lise :

```bash
dsoxlab validate-structure
```

## Les tests jouent le workflow, ils ne relisent pas le YAML

L'apprenant arrive au résultat par le chemin qu'il veut. La preuve est donc
l'**exécution** : act joue le workflow, et le test lit ce qu'il a produit.

```python
# NON : on relit ce que l'apprenant a écrit
assert "pytest" in Path(".github/workflows/ci.yml").read_text()

# OUI : on joue le workflow et on lit ce qu'il a fait
run = jouer_act(depot, "push")
assert run.job("test").result == "success"
```

Relire le YAML (actionlint, zizmor) complète la preuve, sans jamais la
remplacer. Le dernier test d'un lab exerce **les deux côtés** : ce qui doit
être refusé l'est, ce qui doit passer passe. Pour un premier workflow : un test
cassé fait échouer le pipeline, et la suite saine le fait passer.

Avant d'écrire un test, posez-vous une question : **serait-il vert si
l'apprenant ne faisait rien ?** « L'application a des tests » ou « act
s'exécute sans erreur » le sont : ce ne sont pas des tests, ce sont des
hypothèses du point de départ.

## Ce qu'act ne joue pas

Filtres `branches:` et `paths:`, `services:`, environnements et approbations,
OIDC, attestations, rulesets, Scorecard, `concurrency` : ces fonctions
n'existent que sur GitHub. Le lab qui en parle se vérifie sur le dépôt de
l'apprenant, désigné par `LAB_REPO=compte/depot`, par l'API de GitHub. Le
tableau mesuré est dans [`docs/conception.md`](docs/conception.md).

## Anatomie d'un lab

```text
labs/<module>-<sujet>/
├── lab.yaml, lab.fr.yaml       # le contrat : section et level = module du parcours,
│                               # doc_url = la leçon jumelée, runtime.fixtures = le point de départ
├── scenario.md, .fr.md         # la situation et l'objectif, jamais un mode d'emploi
├── README.md, .fr.md           # le tutoriel, sur des exemples étrangers au challenge
├── fixtures/                   # le point de départ, copié dans challenge/work par dsoxlab run
├── solution/                   # la solution de référence, posée pour la validation
└── challenge/
    ├── README.md, .fr.md       # l'énoncé : les exigences à satisfaire
    ├── hints.yaml              # quatre indices en base64, bilingues, de coût croissant
    └── tests/test_functional.py  # la preuve, lue par pytest (nom imposé)
```

`dsoxlab new lab <id> --runtime shell` crée le squelette. L'identifiant suit
`<module>-<sujet>`, en minuscules et en français :
`fondations-premier-workflow`. `section` et `level` reprennent l'identifiant
du module **dans le parcours du blog**, mot pour mot : c'est ce qui permet de
répondre à la question qui pilote ce dépôt, « combien de compétences du
parcours puis-je démontrer ? ».

`doc_url` pointe la leçon que le lab éprouve. Un lab sans leçon jumelée est un
lab qui enseigne au lieu d'éprouver, et enseigner est le rôle du site.

Une fixture déclarée dans `lab.yaml` doit exister dans `fixtures/` :
`dsoxlab validate-structure` refuse le lab sinon.

## Le tutoriel ne donne jamais la solution

Le `README.md` d'un lab enseigne le mécanisme sur un **exemple neutre**, aux
noms étrangers au challenge : un workflow `demo.yml`, pas le `ci.yml` que
l'énoncé demande. Aucun bloc du tutoriel ne doit se copier-coller dans
`challenge/work`. Toute sortie affichée provient d'une exécution réelle.

## Style de rédaction

Le français du blog : clair, pragmatique, sans jargon inutile.

- **Pas d'emoji, pas de tiret cadratin** dans ce que l'apprenant lit :
  scénarios, README, énoncés, indices, messages d'assertion.
- **Les messages d'assertion enseignent.** Un test qui échoue dit ce qui ne va
  pas et pourquoi, pas seulement ce qui était attendu. C'est souvent le seul
  texte que l'apprenant lira attentivement.
- Le `scenario.md` décrit une **situation**, jamais une liste de commandes.
- On rédige en français d'abord, puis on traduit vers les fichiers anglais,
  qui font foi pour dsoxlab.

## Les workflows donnent l'exemple

Ce dépôt enseigne la sécurité des workflows : les siens, et ceux des labs, la
respectent. Permissions minimales, actions épinglées par SHA avec le bon
commentaire de version, aucun `pull_request_target` dangereux.

```bash
actionlint
GH_TOKEN="$(gh auth token)" zizmor .github/workflows/ labs/
trufflehog filesystem . --no-update
```

## Ce qu'un lab contredit dans le blog

Écrire un lab oblige à jouer ce que la leçon affirme. Un écart se consigne
dans [`docs/corrections-guides.md`](docs/corrections-guides.md), avec le
fichier, la section, ce que dit le guide, ce qui est vrai et la preuve. Le
blog se corrige dans son propre dépôt, jamais depuis celui-ci.

## Conventions

- **Commits** : messages en français, sujet factuel qui dit ce qui a changé et
  pourquoi, sans préfixe conventionnel. Le corps raconte ce qui a été
  **mesuré**, y compris les mesures jetées en route.
- **Une issue par lab** : cochez sa définition de terminé au fur et à mesure,
  avec la preuve en commentaire.

## Sécurité

Les vulnérabilités se signalent en privé, jamais par une issue publique : voir
[`SECURITY.fr.md`](SECURITY.fr.md).
