# Réattester les labs de ce catalogue

> Page écrite le 2026-10-19, avec des valeurs **mesurées sur le disque** et non
> recopiées. Les chiffres vieillissent : le `validation-labs.json` reste la
> source de vérité pour les verdicts.

## Pourquoi cette page existe

Le 2026-10-19, une campagne de réattestation a inscrit **douze faux ROUGE** dans
un catalogue avant d'être arrêtée, et s'est bloquée vingt-trois minutes dans un
autre. Aucune des deux causes ne tenait aux labs : un `.venv` dont les shebangs
désignaient l'ancien nom du dépôt après son renommage, et un outil en ligne de
commande qui attendait un réseau que le bac à sable ne lui donnait pas.

Dans les deux cas, le validateur **avait l'air de mesurer les labs alors qu'il
mesurait sa propre panne**, et il l'écrivait dans le relevé. Un faux ROUGE coûte
plus cher qu'une absence de verdict : il envoie chercher un défaut dans un lab
qui n'en a pas.

## Ce que ce catalogue exige

- **dsoxlab 0.5.4 ou plus** dans le `PATH`. C'est la version du moteur qui sera inscrite dans le relevé, et le relevé la déclare pour TOUS les labs : voir la section sur le rejeu partiel.
- Les outils épinglés par `mise.toml`, donc la commande se lance par `mise exec --`. Sans lui, un outil absent ou d'une autre version fait échouer des labs sans rapport avec leur sujet.
- **`.vault-pass` à la racine** : 1 fichier(s) de solution de ce catalogue sont chiffrés par ansible-vault, et le cycle les pose déchiffrés. Le secret n'est jamais commité. Ici : présent.
- Aucun secret : ce catalogue déclare `solutions: plaintext` dans son `meta.yml`, avec sa raison. Ses solutions servent de fixtures au lab suivant, donc elles doivent rester lisibles.

## La commande

```bash
mise exec -- uv run scripts/valider-labs.py
```

Un seul lab, pour éprouver le harnais avant d'engager les 1 :

```bash
mise exec -- uv run scripts/valider-labs.py --lab <id-du-lab>
```

**Commencer par un seul lab n'est pas une précaution de principe.** C'est ce qui
distingue un défaut d'environnement d'un défaut de lab : si le lab unitaire
passe, le harnais est sain ; s'il échoue comme les autres, c'est le harnais
qu'il faut réparer.

## L'état actuel

Relevé actuel : 1 VALIDE. Moteur déclaré : **aucune version de moteur enregistrée**. Dates des verdicts : 2026-10-19. Durée cumulée du dernier cycle mesuré : **0 minutes** pour 1 labs, hors provisionnement et destruction d'infrastructure.

## Les quatre pièges qui produisent un faux verdict

**1. Un `.venv` au shebang mort.** Si le dépôt a été renommé, les scripts de
`.venv/bin/` pointent encore l'ancien chemin et ne s'exécutent plus. Le
symptôme est un échec identique sur chaque lab, souvent sur le déchiffrement de
la solution. Vérification et correctif :

```bash
head -1 .venv/bin/ansible-vault      # le chemin doit exister
uv venv --clear && uv sync           # le recréer
```

**2. `uv run --no-sync` sur un venv vide.** Le drapeau suppose un environnement
déjà peuplé. Sur un clone neuf, il rend un `ModuleNotFoundError` avant d'avoir
regardé un seul lab. Lancer sans `--no-sync` la première fois.

**3. Un outil qui attend un réseau que le bac à sable ne donne pas.** Mesuré
sur un `octl --version` resté bloqué vingt-trois minutes : seule la commande de
premier niveau est exemptée, un sous-processus ne l'est pas. Si une campagne
n'avance plus, regarder ses processus enfants avant de soupçonner un lab :

```bash
ps -eo pid,etimes,cmd | grep -E 'python.*valider[-]labs'
ps --ppid <pid-du-validateur> -o pid,etimes,cmd
```

**4. Un rejeu partiel rend l'en-tête du relevé faux.** La version du moteur est
enregistrée **une fois pour tout le fichier**, alors que les verdicts sont
individuels. Rejouer un seul lab réécrit donc cet en-tête, et le relevé affirme
que tous ses labs ont été attestés avec la version courante. Soit on rejoue tout,
soit on restaure le relevé :

```bash
git checkout -- validation-labs.json
```

## Ce que le relevé ne dit pas

Il ne dit pas **avec quelle version du moteur chaque lab** a été attesté, mais
seulement celle de la dernière campagne. C'est un manque connu, et il se voit
dès qu'une campagne est partielle.

**Ici, le relevé ne porte même pas de version de moteur** : il n'a aucune clé racine, là où six catalogues de la collection enregistrent `genere_le`, `dsoxlab` et la version de chaque outil employé. Tant que c'est le cas, rien ne permet de dire si ses verdicts valent pour le moteur courant.

## Pourquoi les verdicts de ce catalogue sont périmés

Aucun commit de la campagne du 2026-10-17 n'a touché les tests de ce catalogue. Ses verdicts ne sont périmés que par ce qui l'a modifié depuis, et un changement de descripteur ou de documentation ne justifie pas à lui seul un rejeu.

## Le format du relevé décide de ce que le site peut en dire

Le relevé de ce catalogue est au format **plat**, et le site **n'y lit aucune version de moteur**, et affiche donc une attestation sans dire avec quoi elle a été obtenue.

Le générateur du site ne lit `genere_le` et `dsoxlab` **que si la clé `labs`
est un dictionnaire** : un relevé dont les clés de premier niveau sont
directement les identifiants de labs part dans une autre branche, qui rend une
date et un outil vides. Corriger le champ sans corriger le format ne servirait
donc à rien, et c'est pour ça que les deux sont dits ensemble ici.
