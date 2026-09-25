# Premier workflow : les tests tournent à chaque push

Lab du module **fondations** de la formation GitHub Actions, leçons
« Qu'est-ce qu'un workflow ? » et « Sécurité : les bases ». Il éprouve la
première compétence du parcours : écrire un workflow qui fait tourner les
tests d'un projet à chaque push et à chaque pull request, avec les réflexes
de sécurité posés dès le premier fichier.

Ce que le lab prouve, et que l'ancien TP ne prouvait pas : **le workflow est
joué**, avec act, et un test cassé le fait passer au rouge. Un workflow qui
écrit `run: echo pytest` passait l'ancienne vérification, qui relisait le
YAML ; il ne passe pas celle-ci.

| | |
|---|---|
| Cible | votre poste : act 0.2.89 et Docker, image `ubuntu-24.04` du runner épinglée par digest |
| Durée | environ 30 minutes |
| Leçons jumelées | [Qu'est-ce qu'un workflow ?](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/workflow/), [Sécurité : les bases](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/securite-bases/) |
| Jouable avec act | oui, entièrement |

```bash
mise install                               # act, actionlint, zizmor, pinact
dsoxlab run   fondations-premier-workflow   # pose le projet dans challenge/work
dsoxlab check fondations-premier-workflow   # joue le workflow et note
```

Les tests lisent ce qu'act produit : le résultat des jobs sur `push` et sur
`pull_request`, les lignes écrites par pytest, et le verdict d'une copie du
projet dans laquelle une fonction a été cassée. Deux compléments statiques
relisent le YAML : le bloc `permissions:` et l'épinglage des actions par SHA,
que zizmor confirme hors ligne.

Validé par `scripts/valider-labs.py` : 0 avant le travail, 100 après la
solution du formateur, rejouable, poste rendu intact. Le verdict, avec la
version d'act et le digest de l'image, est dans `validation-labs.json`.
