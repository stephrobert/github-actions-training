# Challenge : le premier workflow de la calculatrice

5 tâches, 100 points, 30 minutes.

Le projet est dans `challenge/work`. Tout se passe dans `.github/workflows/`,
que vous créez. Les tests notent ce qu'act produit ; ils ne lisent pas vos
commandes.

### Tâche 1 : les tests tournent à chaque push (20 pts)

`act push` joue un job qui réussit, et pytest y annonce ses neuf tests.

### Tâche 2 : les tests tournent à chaque pull request (20 pts)

`act pull_request` joue le même job, avec le même résultat.

### Tâche 3 : le workflow ne réclame que le droit de lire le code (20 pts)

Un bloc `permissions:` est déclaré, et aucun job n'obtient plus que
`contents: read`. Ni `write-all`, ni un bloc absent qui laisserait les
permissions par défaut.

### Tâche 4 : chaque action est épinglée sur le SHA de son commit (20 pts)

Chaque `uses:` désigne un SHA complet de quarante caractères, suivi de la
version en commentaire, et `zizmor --offline` ne rend aucun finding sur le
répertoire `.github/workflows`.

### Tâche 5 : un test cassé fait échouer le pipeline (20 pts)

Sur une copie du projet où `add` rend une somme fausse, `act push` rend un job
en échec ; sur le projet intact, le même job réussit. C'est le contrôle qui
distingue un workflow qui teste d'un workflow qui affiche « tests OK ».
