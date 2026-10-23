# Journal des changements

**Langue :** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Ce journal est **daté et versionné**, suivant
[Keep a Changelog](https://keepachangelog.com/) et le versionnement sémantique,
comme les catalogues frères. Du 2026-09-25 au 2026-10-17 il n'était que daté, au
motif qu'un catalogue de labs ne promet aucune compatibilité entre deux de ses
états ; les douze catalogues publient désormais une release chacun, et celui-ci
n'en est plus l'exception.

Ce que la date apporte, et que la version ne remplace pas : savoir **quand** un
lab a été éprouvé, avec quelle version d'act et sur quelle image de runner.
C'est ce que `validation-labs.json` enregistre lab par lab, et ce journal le
résume.

Les releases `v1.0.0` à `v1.2.0`, publiées en décembre 2025, ont été
**supprimées**. Elles cumulaient 39 téléchargements, mesurés avant la
suppression, et leur numérotation rendait toute reprise illisible : une version
ne recule pas, et 0.2.0 sous v1.2.0 aurait menti sur l'ordre des choses.

---

## [0.2.3] - 2026-10-23

### Ajouté

- Un verdict ne peut plus être commité avec ce qu'il mesure. Le hook
  `verdicts-et-commun-separes` refuse un commit portant `validation-labs.json`
  à côté de ce que le cycle joue : `challenge/tests/`, `setup.yaml`,
  `cleanup.yaml`, `lab.yaml` d'un lab, et l'outillage partagé. Il est lui-même
  éprouvé, dans les deux sens, par un hook à lui.

  Cela ferme un cas **qu'aucune mesure ne rattrape après coup**. La péremption
  d'un verdict se jugeait en comparant des DATES, et cette comparaison s'est
  trompée dans les deux sens le 2026-10-22 : une correction commitée avec les
  verdicts qu'elle périmait est passée pour saine, et des labs réattestés sur
  une branche sont ressortis « à réattester » après leur fusion en squash,
  contenu inchangé. Quand une pull request squashée retouche un test *après* sa
  campagne, le commit unique porte les deux et le squash a détruit ce qui les
  distinguait. Cela ne se constate pas, donc cela s'empêche.

  L'énoncé reste autorisé à côté d'un relevé : il n'est pas joué par le cycle,
  et l'interdire obligerait à une campagne pour une coquille.

### Corrigé

- `pipelineMustNotLeakSecretsInConfig` est retiré du `.plumber.yaml`, où il
  était déclaré deux fois. Plumber a supprimé ce contrôle et répond « was
  removed and is now ignored: secret detection is no longer part of Plumber;
  remove this block ». Le garder laissait croire que la détection de secrets
  était couverte ici. Elle ne l'est pas, et c'est `detect-private-key` qui s'en
  approche, en hook.

## [0.2.2] - 2026-10-19

### Sécurité

- **La solution de référence est chiffrée par ansible-vault, et `meta.yml` ne
  déclare plus ses solutions en clair.** Le workflow de
  `fondations-premier-workflow` était commité en clair dans un dépôt public :
  l'apprenant qui clone avait la réponse sous la main.

  La déclaration `solutions: plaintext` motivait ce choix par le fait qu'un
  workflow chiffré « ne se relirait pas ». C'était vrai des OUTILS du dépôt,
  pas une fatalité : deux lecteurs lisaient le fichier en clair, et il
  suffisait de leur apprendre à déchiffrer.

  `scripts/valider-labs.py` pose la solution par-dessus le répertoire de
  travail : il la déchiffre à la pose. `tests/test_solutions_exemplaires.py`
  contrôle que la solution épingle ses actions sur un SHA et déclare ses
  `permissions` : ses trois lectures déchiffrent. Sans cette seconde
  adaptation, le contrôle aurait gardé ses quinze verts en n'ayant plus aucun
  `uses:` à examiner, ce qui est précisément le défaut que ce dépôt traque
  chez les autres.

  Vérifié sur le comportement : le contrôle voit les 62 lignes du workflow et
  ses 2 `uses:` épinglés ; sans le secret, la lecture lève et les tests se
  déclarent non joués.

- **Le rejeu « 0 avant, 100 après » ne se joue plus en CI.** C'est le coût
  assumé du chiffrement : le cycle a besoin du clair, et `.vault-pass` n'est
  pas sur la forge, comme dans aucun catalogue de la collection. Les deux
  étapes concernées se déclarent non jouées par un avertissement visible, au
  lieu de passer pour un succès ou de rendre un rouge permanent.

  L'opposabilité de `validation-labs.json` ne tient donc plus à cette CI mais
  à la campagne locale qui l'a produit. L'autre voie, confier le secret à un
  secret de dépôt, a été écartée en connaissance.

## [0.2.1] - 2026-10-19

### Modifié

- **Chaque `doc_url` pointe désormais `www.stephane-robert.info`.** Le site est
  passé de `blog.` à `www.`, et l'ancien hôte redirige en 301 vers le même
  chemin. Rien n'était cassé : `validate-structure --check-urls` suit les
  redirections, et ce catalogue était vert avant qu'une ligne change. La
  migration est une mise au propre et non une réparation : un `doc_url` doit
  pointer la page, pas dépendre d'une redirection qu'il faudra bien retirer un
  jour.

  Les chemins sont identiques entre les deux hôtes : seul l'hôte a changé. Les
  359 `doc_url` que les catalogues déclarent ont été cherchés dans le dépôt du
  site, hors réseau : ils y existent tous, y compris vingt-trois pages que
  l'ancien hôte rendait en 404.

## [0.2.0] - 2026-10-17

### Modifié

- **Le versionnement reprend à 0.2.0, et les cinq anciennes releases
  disparaissent.** Ce catalogue était le seul des douze sans release, et son
  `pyproject.toml` déclarait pourtant `0.2.0` sous des tags publiés jusqu'en
  `v1.2.0` : la version reculait, ce qu'aucun ordre ne peut rattraper. Les
  releases `v1.0.0` à `v1.2.0` et leurs tags ont été supprimés, et celle-ci est
  la première du nouveau compte.

- **La branche par défaut est `main`.** Elle était la seule des treize dépôts
  encore sur `master`. Trois workflows se déclenchaient sur
  `branches: [master]` : `ci.yml`, `codeql.yml` et `scorecard.yml`. Renommer une
  branche ne met **pas** à jour les fichiers qui la nomment : CodeQL et
  Scorecard auraient simplement cessé de tourner, sans erreur et sans que rien
  ne le dise. Ils se déclenchent sur `main`, et un contrôle lit le workflow
  chargé plutôt que son texte pour le prouver.

- **La chaîne de publication est en place** : `release.yml`, `attester.yml` et
  les deux `RELEASING`, dont le bundle distingue les chemins requis des chemins
  facultatifs. Depuis dsoxlab 0.5.1, ils viennent de `new catalog`, et un
  cliquet du moteur compare la liste des requis à ce qu'un catalogue neuf porte
  réellement.

- **Le validateur lit le contrat, plus l'encadré du terminal.**
  `scripts/valider-labs.py` lisait le score dans ce que `dsoxlab check`
  *affiche*. Cet encadré est de l'interface : il a changé en dsoxlab 0.4.0 et
  la regex a cessé de trouver quoi que ce soit. Il lit désormais
  `check --json`, qui porte un `schema`, et cette lecture vit dans
  `scripts/verdict_check.py`, **identique dans les douze catalogues**.

- **Trois verdicts, pas deux.** Une exécution dont tous les tests collectés ont
  skippé n'a rien mesuré : elle est **SKIP**, ni verte ni rouge, et reste à
  mesurer. La peindre en rouge accuserait le lab de ce qui manque au poste.
  `--check` sort donc en `10` dans ce cas, contre `1` pour un ROUGE, à l'image
  de `dsoxlab doctor --strict` où 9 se répare et 10 se remesure.

- **Le README prend la structure de référence** commune aux douze catalogues :
  quatorze sections, dans les deux langues. Sept d'entre elles décrivent
  dsoxlab et non le sujet, et sont donc identiques partout.

### Exige

- **dsoxlab 0.4.1 ou plus récent**, qui a introduit le champ `status` de
  `check --json`. Sans lui, le validateur refuse de conclure plutôt que de
  deviner.

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
