# Journal des changements

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Ce journal est daté, et non versionné. C'est un écart assumé avec les
catalogues frères, qui suivent [Keep a Changelog](https://keepachangelog.com/)
et le versionnement sémantique : **ce projet n'a ni tag, ni release, ni
CHANGELOG versionné** depuis la décision du 2026-09-25. Un numéro de version
promet une compatibilité entre deux états d'un logiciel ; un catalogue de labs
n'a rien de tel à promettre, et un apprenant ne joue jamais « la version 1.2 »
d'un lab, il joue celui qui est en ligne.

Ce que la date apporte, elle : savoir **quand** un lab a été éprouvé, avec
quelle version d'act et sur quelle image de runner. C'est ce que
`validation-labs.json` enregistre lab par lab, et ce journal le résume.

Les releases `v1.0.1` à `v1.2.0`, publiées en décembre 2025, restent en place et
ne sont pas reconduites.

---

## 2026-09-25

### Le premier lab se joue, et le cycle le prouve

`fondations-premier-workflow` était un squelette : trois fixtures déclarées mais
absentes, aucun test, aucune solution, aucun indice.
`dsoxlab validate-structure` le refusait. Il porte désormais cinq contrôles de
vingt points, joués par act dans l'image du runner épinglée par digest.

```
avant le travail : 0/5
après la solution : 5/5
après clean et run : 0/5
poste rendu intact
VALIDE
```

Le cinquième contrôle porte ses deux moitiés ensemble : il casse une fonction
dans une copie du projet et exige que le pipeline le dise, puis vérifie sur le
projet intact qu'il ne rougit pas toujours. Séparées, la seconde moitié serait
vraie dès le premier contrôle, donc sans valeur.

### La validation laisse une trace opposable

`scripts/valider-labs.py` enchaîne les commandes dsoxlab, sans en réimplémenter
aucune, et écrit son verdict dans `validation-labs.json` avec la date, la
version d'act et le digest de l'image du runner : une validation vaut pour une
image donnée.

Il a été éprouvé dans les deux sens. Sur une solution amputée de son déclencheur
`pull_request` :

```
après la solution : 4/5
- la solution laisse 1 test(s) en échec : test_les_tests_tournent_a_chaque_pull_request
ROUGE
```

Il ne nommait d'abord que « la solution ne fait pas passer tous les tests », ce
qui signale un problème sans dire lequel.

`--check` relit le verdict sans rien rejouer, et vérifie d'abord la chose la
moins évidente : qu'aucun lab n'a été **ajouté sans être validé**. Un fichier de
verdicts tous verts qui ignorerait la moitié du catalogue passerait sans cela.

### Dix-neuf hooks, quatre vérificateurs

Le dépôt n'avait aucun `.pre-commit-config.yaml` et un seul vérificateur.

`tests/test_solutions_exemplaires.py` contrôle ce qu'aucun test de lab ne
regarde : les tests d'un lab notent le travail de l'apprenant, jamais la
solution qu'on lui montre ensuite. Il a trouvé un vrai cas dès sa première
exécution.

actionlint et zizmor ne passent **jamais** sur les points de départ : un
`challenge/` peut porter une action non épinglée ou une injection, puisque c'est
ce que l'apprenant doit corriger. Ils ne regardent que `.github/` et
`labs/**/solution/`, et `scripts/hooks/cibles-workflows.sh` calcule cette liste
une seule fois, pour le hook local comme pour la CI.

### Une CI qui joue les labs

Cinq jobs : zizmor, actionlint, poutine, la parité pre-commit aux deux étapes,
et un job qui rejoue le cycle complet avec act sur le runner GitHub. C'est ce
dernier qui rend `validation-labs.json` opposable : un verdict local qui ne se
reproduit pas en CI est ROUGE.

`dependabot.yml` est aligné sur le modèle commun aux six dépôts, avec un
écosystème que les frères n'ont pas : les `requirements.txt` des points de
départ, qui vivent hors du verrou du catalogue et doivent rester d'actualité.

### Trois défauts corrigés, qui ne se voyaient qu'à l'exécution

**La solution de référence n'était pas exemplaire.** Elle rendait 80/100 à son
propre challenge : `actions/checkout` y laissait le jeton du job dans
`.git/config`, ce que la tâche 4 interdit et que zizmor relève sous
`artipacked`. Le même défaut existait dans `codeql.yml`.

**ruff réécrivait le sujet des labs.** Il a trié les imports d'une fixture,
c'est-à-dire du point de départ livré à l'apprenant. L'exclusion posée dans
`pyproject.toml` est **ignorée** pour tout fichier passé en argument, et
pre-commit passe justement les fichiers en argument : il faut
`--force-exclude`, sans quoi l'exclusion ne protège que les exécutions à la
main, celles qui n'en ont pas besoin.

**Un SHA d'action avait été écrit de mémoire.** `jdx/mise-action` portait un SHA
inexistant avec une version dépassée en commentaire. Confronté à l'API action
par action, il était le seul faux sur cinq. Un dépôt qui enseigne l'épinglage ne
peut pas en inventer un.

### Le catalogue prend la forme dsoxlab

`meta.yml`, `conftest.py` avec `jouer_act()`, le README suivant la trame des
autres formations avec son catalogue généré, la documentation alignée, et
`mise.toml` qui épingle act, actionlint, zizmor, pinact, poutine et uv aux
versions mesurées ce jour.

Toute version d'act antérieure à 0.2.86 est vulnérable à CVE-2026-34041 et
CVE-2026-34042 : `mise.toml` épingle la 0.2.89, et le validateur refuse de jouer
avec une autre.

### La licence passe de MIT à CC BY 4.0

Comme les catalogues Linux et Kubernetes, et pour la même raison : ce dépôt est
du **contenu pédagogique**, pas du logiciel. Le texte officiel est repris nu,
sans en-tête personnalisé, faute de quoi GitHub ne détecte pas la licence.

### Le versionnement est retiré

Ni tag, ni release, ni `RELEASING`. Le workflow `release.yml` a été retiré, et
avec lui le badge SLSA qui en dépendait.

---

## 2026-01-26

La section OpenSSF Scorecard du README est retirée, et les actions montent de
version.

---

## 2025-12-29 et avant

Naissance du dépôt sous licence MIT, avec un TP unique vérifié par `validate.py`,
une analyse statique qui cherchait `pytest` dans un `run:` sans jamais rien
exécuter. Provenance SLSA, CodeQL, Scorecard, et les releases `v1.0.1` à
`v1.2.0`.

C'est cette approche que la refonte du 2026-09-25 remplace : un test qui lit le
code ne prouve pas qu'un workflow tourne, et encore moins qu'un test cassé
ferait échouer le pipeline.
