# Les tests d'une calculatrice que personne ne lance

## Situation

Votre équipe vient de récupérer une petite bibliothèque Python, `src/calculator.py`,
qui sert de brique à d'autres projets de l'entreprise. Elle est livrée avec neuf
tests pytest, dans `tests/`, qui passent tous quand on pense à les lancer. La
semaine dernière, personne n'y a pensé : une modification de `divide` est partie
en production avec une division par zéro non gérée, et un test la détectait.

Le dépôt n'a aucun workflow. Le répertoire `challenge/work` contient le projet tel
qu'il a été livré : le code, les tests, `requirements.txt`, `pytest.ini`, et un
`.actrc` qui désigne l'image du runner pour act. Ce n'est pas encore un dépôt git ;
act en a besoin pour lire le contexte (branche, commit), et un projet qui n'en a
pas ne peut pas avoir de pull request.

## Objectif

Faire tourner les neuf tests **à chaque push et à chaque pull request**, de sorte
qu'une modification qui casse un test ne puisse plus arriver sur `main` sans que
quelqu'un le voie. Le workflow doit respecter, dès ce premier fichier, les
réflexes de la leçon « Sécurité : les bases » : il ne réclame que le droit de
lire le code, et chaque action qu'il emploie est épinglée sur le SHA complet de
son commit, avec sa version en commentaire, sans que zizmor n'ait rien à redire.

Le workflow est bon quand act le joue sur les deux événements avec un job vert
où pytest annonce ses neuf tests, et quand la même commande, sur une copie du
projet où une fonction a été cassée, rend le job rouge.

## Repères

- La leçon dit où GitHub cherche les workflows, et de quoi l'un d'eux est fait :
  un nom, des déclencheurs, des jobs. `act -l` liste ce qu'act a compris de vos
  fichiers ; un job qui n'y figure pas ne tournera jamais.
- `act push` et `act pull_request` jouent le workflow pour chacun des deux
  événements. act ignore les filtres `branches:`, ce qui n'est pas une raison de
  les omettre : sur GitHub, ils comptent.
- Le runner ne connaît rien de votre projet : chaque job commence sur une machine
  neuve, et c'est à vous d'y récupérer le code et d'y installer Python.
- Une action se désigne par `owner/repo@ref`. La version courante de chaque
  action de l'organisation `actions` se lit sur sa page Releases, et
  `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha` donne le SHA d'un tag.
- `zizmor --offline .github/workflows` relit vos fichiers comme le fera la
  vérification.

## Vérifier

```bash
dsoxlab check fondations-premier-workflow
```

Cinq contrôles, vingt points chacun. Les trois premiers jouent le workflow avec
act et lisent ce qu'il produit ; les deux autres relisent le YAML. Le dernier
contrôle est celui qui compte : il casse une fonction dans une copie du projet
et exige que le pipeline le dise.
