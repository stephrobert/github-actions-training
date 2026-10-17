# Corrections à apporter aux guides GitHub Actions du blog

Relevé fait en construisant les labs, le 2026-09-25, en lisant les leçons du
parcours `github-actions` et en confrontant chaque affirmation à sa source :
l'API GitHub, la documentation officielle, ou une exécution sous act 0.2.89.
Les chemins sont relatifs à `src/content/docs/docs/`. La version anglaise de
chaque page, sous `src/content/docs-en/`, porte les mêmes passages.

Rien n'a été modifié dans le blog : ce fichier est une liste à traiter, pas un
correctif. Chaque entrée dit ce que le guide affirme, ce qui est vrai, et la
commande ou la page qui le prouve. Une entrée sans preuve reproductible
n'aurait pas sa place ici.

Trois gravités :

- **faux** : l'affirmation est contredite par la source, ou la commande ne fait
  pas ce que le guide dit ;
- **périmé** : l'affirmation était vraie et ne l'est plus, version ou date ;
- **imprécis** : l'affirmation est vraie ou presque, mais elle contredit une
  autre leçon, ou elle laisse l'apprenant conclure une chose fausse ;
- **manque** : rien de faux, mais une information sans laquelle l'apprenant
  échoue ou fait moins bien.

Ce que les mesures ont confirmé et qui n'est donc PAS dans la liste : les six
SHA cités par les leçons du module fondations correspondent tous au tag
annoncé (`checkout` v7.0.1, v4.2.2 et v4.1.1, `setup-node` v7.0.0,
`setup-python` v7.0.0 et v5.3.0), de même que `setup-node` v4.4.0 et
`upload-artifact` v4.6.2 de `pinner-sha.mdx`. Vérifié par
`gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.

## Vue d'ensemble

| Fichier | Entrées | Faux | Périmé | Imprécis | Manque |
| --- | --- | --- | --- | --- | --- |
| `pipeline-cicd/github/act.mdx` | 1 à 6 | 2 | 1 | 2 | 1 |
| `pipeline-cicd/github/fondations/index.mdx` | 7 à 9 | 0 | 1 | 2 | 0 |
| `pipeline-cicd/github/fondations/workflow.mdx` | 10 à 12 | 1 | 1 | 1 | 0 |
| `pipeline-cicd/github/fondations/securite-bases.mdx` | 13, 14 | 1 | 0 | 1 | 0 |
| `pipeline-cicd/github/fondations/secrets.mdx` | 15, 16 | 1 | 1 | 0 | 0 |
| `pipeline-cicd/github/fondations/marketplace.mdx` | 17, 18 | 0 | 0 | 1 | 1 |
| `pipeline-cicd/github/securite/pinner-sha.mdx` | 19, 20 | 1 | 1 | 0 | 0 |
| `pipeline-cicd/github/workflows/variables-secrets.mdx` | 21, 22 | 2 | 0 | 0 | 0 |
| `pipeline-cicd/github/workflows/index.mdx` | 23 | 1 | 0 | 0 | 0 |

## `pipeline-cicd/github/act.mdx`

### 1. La version recommandée est vulnérable à deux CVE de gravité haute

- **Section** : frontmatter (`badge: v0.2.84`, `toolVersion: "0.2.84"`),
  « Installation », encadré « Version actuelle », onglet Linux
  (`VERSION=0.2.84`), « Vérification de l'installation ».
- **Le guide dit** : « Ce guide utilise la version v0.2.84 (décembre 2025)
  d'act. »
- **Ce qui est vrai** : la version courante est 0.2.89 (publiée le
  2026-06-01). Toute version antérieure à 0.2.86 (2026-03-25) est vulnérable
  à CVE-2026-34041 (GHSA-xmgr-9pqc-h5vw, high : injection d'environnement par
  `set-env` et `add-path` non restreints) et CVE-2026-34042
  (GHSA-x34h-54cw-9825, high : injection dans le serveur `actions/cache`
  d'act). Le guide fait donc télécharger et épingler une version vulnérable.
- **Preuve** : `gh api repos/nektos/act/releases/latest --jq .tag_name` rend
  `v0.2.89` ; `gh api 'advisories?cve_id=CVE-2026-34041'` et `…34042` rendent
  les deux GHSA ci-dessus, publiés le 2026-03-27 ; act 0.2.84 lui-même
  affiche au lancement : « This version of 'act' is vulnerable to
  CVE-2026-34041 and CVE-2026-34042 - please upgrade to 0.2.86 or later ».
- **Gravité** : faux (la recommandation), périmé (la version).
- **Lab jumelé** : tous, `mise.toml` épingle act 0.2.89.

### 2. L'événement `schedule` est annoncé non supporté, act le joue

- **Section** : « Limitations de act » (tableau, ligne « Événements
  limités ») et « Dépannage » (ligne « Événement non supporté »).
- **Le guide dit** : « `schedule`, `deployment`, `page_build` ne sont pas
  supportés ».
- **Ce qui est vrai** : `act schedule` joue un workflow déclenché par
  `on: schedule` et le job voit `github.event_name == 'schedule'`.
  `deployment` et `page_build` n'ont pas été mesurés.
- **Preuve** : act 0.2.89, workflow `on: schedule: [{cron: "0 6 * * 1"}]`,
  `act schedule -W .github/workflows/cron.yml` rend
  `je tourne sur schedule, event=schedule` puis `Job succeeded`, rc 0.
- **Gravité** : faux.
- **Lab jumelé** : `act-rejouer-en-local` (#47).

### 3. Les artefacts : act a bien une API, mais pas pour les versions courantes des actions

- **Section** : « Limitations de act », lignes « Artifacts » et « Cache ».
- **Le guide dit** : « `actions/upload-artifact` crée des fichiers locaux,
  pas d'API ».
- **Ce qui est vrai** : act embarque un serveur d'artefacts qui implémente
  l'API (`--artifact-server-path`), et un serveur de cache
  (`--cache-server-path`) qui rend `cache-hit=true` au second passage. Ce qui
  ne marche pas, c'est `upload-artifact` v6 et v7 et `download-artifact` v7 et
  v8, que ce serveur refuse ; v5.0.0 et v6.0.0 fonctionnent. Un apprenant qui
  suit la formation, qui épingle les versions courantes, tombe sur cet échec
  sans que le guide l'en prévienne.
- **Preuve** : act 0.2.89, `upload-artifact@043fb46d…` (v7.0.1) :
  `Error decode request body: proto: (line 1:92): unknown field "mime_type"`,
  cinq tentatives puis `Job failed`. Même workflow avec v5.0.0 et v6.0.0 :
  `Job succeeded`. PR amont ouverte : nektos/act#6174.
- **Gravité** : imprécis.
- **Lab jumelé** : `artefacts-entre-jobs` (#38), `cache-des-dependances` (#39).

### 4. Les filtres `branches:` et `paths:` sont ignorés, et le guide ne le dit pas

- **Section** : « Limitations de act ».
- **Le guide dit** : rien sur les filtres de déclencheur.
- **Ce qui est vrai** : act joue le job quel que soit le nom de la branche du
  dépôt local, et quel que soit le fichier modifié. Un apprenant qui teste un
  `on: push: branches: [main]` depuis une branche `feature` conclut à tort que
  son filtre est bon.
- **Preuve** : act 0.2.89, workflow `on: push: branches: [main]`, dépôt sur
  `refs/heads/feature` : le job tourne. Mesuré le 2026-09-25, voir
  `docs/conception.md`.
- **Gravité** : manque.
- **Lab jumelé** : `declencheurs` (#22), qui prouve les filtres sur la
  plateforme avec `gh run list`.

### 5. L'image du runner est un tag flottant, alors que la formation épingle tout

- **Section** : « Fichier .actrc », « Images Docker personnalisées »,
  « Dépannage », « Aide-mémoire ».
- **Le guide dit** : `-P ubuntu-24.04=catthehacker/ubuntu:act-latest`.
- **Ce qui est vrai** : `act-latest` est un tag mobile ; `act-24.04` existe et
  correspond au label demandé, et `-P` accepte un digest, ce qui rend une
  exécution reproductible : `-P ubuntu-24.04=catthehacker/ubuntu:act-24.04@sha256:c58e2b36…`.
  C'est la règle que la formation applique aux actions ; elle vaut pour
  l'image qui les exécute.
- **Preuve** : act 0.2.89 avec ce `.actrc` : `Start
  image=catthehacker/ubuntu:act-24.04@sha256:c58e2b36…`, `Job succeeded`.
  `docker image inspect catthehacker/ubuntu:act-24.04` : digest
  `c58e2b364da03b0c804c7d660f2ecbedf2f221a382b9baa0b344b0144780ff43`, image
  construite le 2026-08-15.
- **Gravité** : imprécis.
- **Lab jumelé** : tous, le `.actrc` de chaque lab épingle l'image par digest.

### 6. L'installation télécharge une archive, la formation installe par mise

- **Section** : « Installation », onglet Linux.
- **Le guide dit** : `curl -sSL -O ".../act_Linux_x86_64.tar.gz"` puis
  `sha256sum --check`.
- **Ce qui est vrai** : la vérification d'empreinte est juste. Mais les labs
  installent tous leurs outils par mise, à une version nommée
  (`mise use act@0.2.89`), et le guide `actionlint.mdx` de la même formation
  fait pareil. Un apprenant qui suit les deux guides installe act de deux
  façons.
- **Preuve** : `mise ls-remote act | tail -1` rend `0.2.89`.
- **Gravité** : manque (une préférence de cohérence, pas une erreur).
- **Lab jumelé** : tous.

## `pipeline-cicd/github/fondations/index.mdx`

### 7. Les SHA cités datent de 2023, la leçon suivante en cite d'autres

- **Section** : « La solution : épingler par SHA », « Les trois réflexes de
  sécurité », « Votre premier workflow », tableau « Les concepts clés ».
- **Le guide dit** : `actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11 # v4.1.1`
  et `actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b # v5.3.0`.
- **Ce qui est vrai** : les deux SHA sont justes pour ces tags, mais
  `checkout` en est à v7.0.1 (2026-07-20) et `setup-python` à v7.0.0
  (2026-07-20), et ce sont ces versions que `workflow.mdx` et
  `marketplace.mdx`, dans le même module, citent. L'apprenant lit v4.1.1 sur
  une page et v7.0.1 sur la suivante sans explication.
- **Preuve** : `gh api repos/actions/checkout/releases/latest --jq .tag_name`
  rend `v7.0.1` ; `gh api repos/actions/setup-python/releases/latest` rend
  `v7.0.0`.
- **Gravité** : périmé.
- **Lab jumelé** : `premier-workflow` (#16), dont la solution épingle
  v7.0.1 et v7.0.0.

### 8. Le secret interpolé dans `run:` est marqué correct ici, dangereux deux leçons plus loin

- **Section** : « Les trois réflexes de sécurité », point 3. Même passage dans
  `fondations/securite-bases.mdx`, section « 1. Les secrets exposés ».
- **Le guide dit** : `- run: curl -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" …`
  précédé de « Les secrets sont masqués automatiquement si utilisés
  correctement » (coche verte).
- **Ce qui est vrai** : `fondations/secrets.mdx` (« Comment utiliser un
  secret ») enseigne de passer le secret par `env:` pour qu'il ne figure pas
  dans la ligne de commande, et `workflows/variables-secrets.mdx` (« Ne jamais
  exposer un secret ») montre exactement cette ligne `curl -H "Authorization:
  Bearer ${{ secrets.NPM_TOKEN }}"` avec une croix rouge, « DANGEREUX ». Les
  deux formes sont masquées dans les logs ; la différence est que
  l'interpolation place le secret dans l'argument de la commande, visible dans
  la liste des processus. Une même ligne ne peut pas être verte sur une page et
  rouge sur l'autre.
- **Preuve** : lecture croisée des trois pages ; masquage mesuré à l'entrée 14.
- **Gravité** : imprécis (contradiction entre leçons).
- **Lab jumelé** : `secrets-et-variables` (#17).

### 9. Le tableau des concepts cite `windows-latest`, que la leçon suivante interdit

- **Section** : tableau « Les concepts clés », ligne « Runner ».
- **Le guide dit** : « `ubuntu-24.04`, `windows-latest` ».
- **Ce qui est vrai** : `workflow.mdx`, encadré « Évitez les tags 'latest' »,
  demande de ne jamais employer `-latest`. L'exemple contredit la consigne.
- **Preuve** : lecture croisée.
- **Gravité** : imprécis.
- **Lab jumelé** : aucun.

## `pipeline-cicd/github/fondations/workflow.mdx`

### 10. `macos-14` est en cours de retrait

- **Section** : « Les runners : où s'exécute le code », tableau et exemple.
- **Le guide dit** : « `macos-14` | macOS 14 (Sonoma) | Applications
  iOS/macOS ».
- **Ce qui est vrai** : GitHub a annoncé la dépréciation de macOS 14 à partir
  du 2026-07-06, avec des coupures programmées en octobre 2026 et un retrait
  complet le 2026-11-02. Les labels courants sont `macos-15` et `macos-26`.
  `windows-2022` reste disponible, mais `windows-latest` désigne désormais
  `windows-2025`.
- **Preuve** : `gh api repos/actions/runner-images/issues/13518` : « macOS 14
  Sonoma based runner images will begin deprecation on July 6th and will be
  fully unsupported by November 2nd » ; README de `actions/runner-images`,
  ligne macOS 14 marquée `deprecated`.
- **Gravité** : périmé.
- **Lab jumelé** : aucun.

### 11. Le premier workflow de la formation contient l'injection que la leçon suivante interdit

- **Section** : « Votre premier workflow », fichier `hello.yml`.
- **Le guide dit** :
  `run: | echo "Branche: ${{ github.ref_name }}" … echo "Auteur du commit: ${{ github.actor }}"`,
  sans bloc `permissions:`.
- **Ce qui est vrai** : `securite-bases.mdx`, réflexe 6, interdit d'insérer
  une donnée contrôlée par l'extérieur avec `${{ }}` dans un `run:` ; un nom
  de branche l'est. `index.mdx` demande `permissions: contents: read` « dès
  votre premier workflow ». Le premier workflow que l'apprenant copie viole les
  deux règles, et zizmor, enseigné plus loin, le rejette.
- **Preuve** : `zizmor --offline hello.yml` (1.30.0, persona regular) :
  `error[template-injection]` sur `github.ref_name` et sur `github.actor`
  (confiance High), `warning[excessive-permissions]` : « default permissions
  used due to no permissions: block ».
- **Gravité** : faux (au regard des règles de la formation).
- **Lab jumelé** : `premier-workflow` (#16), dont les tests refusent un
  workflow sans `permissions:`.

### 12. « Chaque ligne est exécutée comme une commande séparée »

- **Section** : « Commandes sur plusieurs lignes ».
- **Le guide dit** : « Chaque ligne après le `|` est exécutée comme une
  commande séparée. »
- **Ce qui est vrai** : le bloc entier est un seul script, passé à
  `bash -e {0}` ; une ligne qui échoue arrête le step, et une variable définie
  sur une ligne vaut sur la suivante. Un apprenant qui croit à des commandes
  séparées ne comprend ni pourquoi `npm test` n'est pas lancé quand `npm ci`
  échoue, ni pourquoi `VERSION=1.2` puis `echo $VERSION` marche.
- **Preuve** : documentation « Workflow syntax », `jobs.<job_id>.steps[*].shell` :
  shell par défaut sur Linux « `bash -e {0}` », et « `bash --noprofile --norc
  -eo pipefail {0}` » quand `shell: bash` est explicite.
- **Gravité** : imprécis.
- **Lab jumelé** : `premier-workflow` (#16).

## `pipeline-cicd/github/fondations/securite-bases.mdx`

### 13. ua-parser-js a été compromis en 2021, pas en 2022

- **Section** : « Exemples réels d'attaques supply chain », tableau.
- **Le guide dit** : « 2022 | ua-parser-js | Package npm populaire infecté,
  minait de la crypto ».
- **Ce qui est vrai** : la compromission date du 22 octobre 2021.
- **Preuve** : `gh api advisories/GHSA-pjwm-rvh2-c87w --jq .published_at`
  rend `2021-10-22T20:38:14Z`, « Embedded malware in ua-parser-js ».
- **Gravité** : faux.
- **Lab jumelé** : aucun.

### 14. Un secret affiché « apparaît dans les logs » : non, sauf s'il est transformé

- **Section** : « 1. Les secrets exposés », erreur 2 : « Afficher un secret
  pour "débuguer" : Il apparaît dans les logs, visibles par tous les
  collaborateurs ». Même sujet dans `fondations/secrets.mdx` : « Même si votre
  script fait un `echo` du secret par erreur, GitHub le masque » (section
  « Exemple concret »), puis « DANGEREUX - le secret pourrait apparaître dans
  les logs » (encadré « Ne jamais faire echo d'un secret ») ; et dans
  `workflows/variables-secrets.mdx`, « Ne jamais exposer un secret » : « Un
  secret interpolé directement dans une commande apparaît dans les logs, même
  masqué ».
- **Ce qui est vrai** : la valeur brute est masquée, qu'elle soit interpolée
  ou lue depuis `env:`. Ce qui fuit, c'est toute valeur dérivée : encodage
  base64, sous-chaîne, découpage. C'est la raison de ne jamais afficher un
  secret, et l'encadré « Le masquage n'est pas parfait » de `secrets.mdx` le
  dit bien ; les trois autres passages disent le contraire ou l'inverse.
- **Preuve** : act 0.2.89, `-s JETON=ghp_ValeurTresSecrete123456` :
  `echo "${{ secrets.JETON }}"` rend `***` ; `echo "$JETON"` (par `env:`)
  rend `***` ; `printf '%s' "$JETON" | base64` rend
  `Z2hwX1ZhbGV1clRyZXNTZWNyZXRlMTIzNDU2` en clair ; `${JETON:0:8}` rend
  `ghp_Vale` en clair ; `${JETON}!` rend `***!`. Le masquage d'act suit la
  règle du runner GitHub : valeur exacte, jamais ses dérivés.
- **Gravité** : imprécis.
- **Lab jumelé** : `secrets-et-variables` (#17), dont le point de départ fuit
  par base64.

## `pipeline-cicd/github/fondations/secrets.mdx`

### 15. GitHub ne journalise pas l'accès aux secrets

- **Section** : « Comment ça protège vos données ? », tableau, ligne
  « Audit ».
- **Le guide dit** : « GitHub journalise qui accède aux secrets et quand ».
- **Ce qui est vrai** : le journal d'audit enregistre la création, la mise à
  jour et la suppression d'un secret (`org.create_actions_secret`,
  `org.update_actions_secret`, `org.remove_actions_secret`, et leurs
  équivalents `repo.*`). Aucun événement ne trace la lecture d'un secret par un
  workflow. Un apprenant qui compte sur ce journal pour savoir si un secret a
  été consommé ne trouvera rien.
- **Preuve** : documentation « Audit log events for your organization »,
  catégorie `org` : seuls `create`, `update` et `remove` existent pour
  `actions_secret`.
- **Gravité** : faux.
- **Lab jumelé** : aucun.

### 16. Le PAT classique à portée `repo` n'est plus la recommandation

- **Section** : « 3. Appliquez le principe de moindre privilège », tableau,
  ligne « GitHub PAT ».
- **Le guide dit** : « GitHub PAT | `repo` scope uniquement ».
- **Ce qui est vrai** : `repo` est la portée la plus large d'un PAT classique
  (tous les dépôts du compte, lecture et écriture). GitHub recommande les
  fine-grained PAT, limités à des dépôts nommés et à des permissions
  unitaires.
- **Preuve** : documentation « Managing your personal access tokens » :
  « GitHub recommends that you use fine-grained personal access tokens instead
  of personal access tokens (classic) whenever possible ».
- **Gravité** : périmé.
- **Lab jumelé** : aucun.

## `pipeline-cicd/github/fondations/marketplace.mdx`

### 17. Résoudre `commits/v4` ne dit pas quelle version écrire en commentaire, et rien ne le vérifie

- **Section** : « 1. Épingler par SHA », « Comment trouver le SHA ? ».
- **Le guide dit** : `gh api repos/actions/checkout/commits/v4 --jq .sha`,
  puis « Le commentaire `# v4.2.2` conserve la lisibilité ».
- **Ce qui est vrai** : `v4` est un tag majeur mobile ; le SHA obtenu est
  celui de la dernière v4.x au moment de la commande, et la commande ne dit
  pas laquelle. Un commentaire faux à côté d'un SHA juste est le défaut le
  plus sournois : le SHA est sûr, mais Dependabot, les relecteurs et l'audit
  raisonnent sur la version affichée. `pinact run --check` ne le voit pas ;
  `pinact run --verify` et zizmor en mode en ligne le voient.
- **Preuve** : workflow avec
  `actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v5.3.0`
  (le SHA est celui de v7.0.0). `pinact run --check` : rc 0.
  `pinact run --verify --check` (5.0.0) : « action_version must be equal to
  commit_hash_of_version_annotation », rc 3. `GH_TOKEN=… zizmor` (1.30.0) :
  `warning[ref-version-mismatch]: … is pointed to by tag v7.0.0 … tag points
  to commit 0b93645e9fea`, Medium, confiance High. `zizmor --offline` : rien.
- **Gravité** : imprécis.
- **Lab jumelé** : `evaluer-et-epingler-une-action` (#18), dont le point de
  départ porte exactement ce défaut.

### 18. Le `dependabot.yml` proposé n'a pas de `cooldown`

- **Section** : « 5. Activer Dependabot pour les actions ». Même exemple dans
  `securite/pinner-sha.mdx`, « Solution 1 : Dependabot ».
- **Le guide dit** : un `dependabot.yml` réduit à `package-ecosystem`,
  `directory` et `schedule`.
- **Ce qui est vrai** : sans `cooldown`, Dependabot propose une version le
  jour de sa publication, ce qui est la fenêtre où une version compromise fait
  le plus de dégâts ; `securite/maintenance-sha.mdx` enseigne cette
  quarantaine, et zizmor, enseigné aussi, signale son absence.
- **Preuve** : `zizmor --offline .github/dependabot.yml` sur l'exemple du
  guide : `warning[dependabot-cooldown]: insufficient cooldown in Dependabot
  updates`, Medium. Mesuré aussi sur le `dependabot.yml` de ce dépôt (issue
  #14).
- **Gravité** : manque.
- **Lab jumelé** : `evaluer-et-epingler-une-action` (#18).

## `pipeline-cicd/github/securite/pinner-sha.mdx`

### 19. `pin-github-action` n'écrit pas `# v4.2.2`, et ne change jamais de version majeure

- **Section** : « Option 1 : pin-github-action », exemple « Avant / Après »,
  encadré « Le commentaire est important » ; « À retenir ».
- **Le guide dit** : avant
  `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4`, après
  `actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0` ;
  « L'outil ajoute automatiquement le commentaire `# v4.2.2`. Gardez-le ! ».
- **Ce qui est vrai** : l'outil remplace la référence par le SHA qu'elle
  pointe au moment de l'exécution et conserve la référence d'origine en
  commentaire, sous la forme `# pin@v4` ; il ne passe jamais de v4 à v7, et
  n'écrit pas de version exacte. L'exemple « avant » est d'ailleurs déjà
  épinglé (le SHA de v4.4.0), donc il n'illustre pas une conversion.
- **Preuve** : README de `mheap/pin-github-action` (v3.5.2, 2026-08-13) :
  « converting your workflow to use a specific commit hash, whilst adding the
  original value as a comment on that line », exemple
  `uses: actions/checkout@db41740e… # pin@main`, et « Each time you run the
  tool the exact SHA will be updated to the latest available SHA for your
  pinned ref ». `gh api repos/actions/setup-node/commits/v4.4.0 --jq .sha`
  rend `49933ea5…`.
- **Gravité** : faux.
- **Lab jumelé** : `evaluer-et-epingler-une-action` (#18), qui emploie pinact.

### 20. L'exemple complet épingle des versions de deux générations en arrière

- **Section** : « Exemple complet : workflow sécurisé ».
- **Le guide dit** : `checkout` v4.2.2, `setup-node` v4.4.0,
  `upload-artifact` v4.6.2, alors que la section « Après » de la même page
  montre `checkout` v7.0.1 et `setup-node` v7.0.0.
- **Ce qui est vrai** : les SHA sont justes pour ces tags, mais les versions
  courantes sont `checkout` v7.0.1, `setup-node` v7.0.0 et `upload-artifact`
  v7.0.1 (2026-04-10). Un apprenant qui copie l'exemple part avec deux
  majeures de retard, et Dependabot lui ouvrira trois PR le jour même.
- **Preuve** : `gh api repos/actions/upload-artifact/releases/latest --jq
  .tag_name` rend `v7.0.1`.
- **Gravité** : périmé.
- **Lab jumelé** : `evaluer-et-epingler-une-action` (#18).

## `pipeline-cicd/github/workflows/variables-secrets.mdx`

### 21. `if: secrets.MY_SECRET != ''` est refusé : le contexte `secrets` n'existe pas dans un `if` de step

- **Section** : « Erreurs courantes », « Secret non disponible », exemple
  marqué correct.
- **Le guide dit** :
  `- name: Vérifier la présence du secret` / `if: secrets.MY_SECRET != ''`.
- **Ce qui est vrai** : dans `jobs.<job_id>.steps[*].if`, les contextes
  disponibles sont `github`, `needs`, `strategy`, `matrix`, `job`, `runner`,
  `env`, `vars`, `steps` et `inputs`. `secrets` n'en fait pas partie ; il
  n'est pas non plus disponible dans `jobs.<job_id>.if`. La forme juste passe
  le secret dans `env:` au niveau du job, puis teste `if: env.MY_SECRET != ''`.
- **Preuve** : documentation « Contexts », tableau « Context availability »,
  ligne `jobs.<job_id>.steps.if`. actionlint 1.7.12 : « context "secrets" is
  not allowed here. available contexts are "env", "github", "inputs", "job",
  "matrix", "needs", "runner", "steps", "strategy", "vars" ». act 0.2.89
  refuse le fichier entier : « workflow is not valid … Unknown Variable Access
  secrets ».
- **Gravité** : faux.
- **Lab jumelé** : `secrets-et-variables` (#17), dont la solution montre la
  forme `env:` puis `if: env.X != ''`.

### 22. `ACTIONS_RUNNER_DEBUG` et `ACTIONS_STEP_DEBUG` ne se règlent pas dans `env:`

- **Section** : « Débogage », « Activer les logs détaillés ».
- **Le guide dit** : `env: ACTIONS_RUNNER_DEBUG: true` /
  `ACTIONS_STEP_DEBUG: true`, « Deux variables font passer GitHub Actions en
  mode verbeux ».
- **Ce qui est vrai** : ces deux réglages sont lus par le runner avant que le
  workflow ne s'exécute. Ils se posent comme secret ou comme variable du
  dépôt, ou par le bouton « Re-run with debug logging ». Un `env:` dans le
  YAML n'a aucun effet sur le runner ; l'apprenant qui le pose ne verra jamais
  les lignes `::debug::`.
- **Preuve** : documentation « Enabling debug logging » : « set the following
  secret or variable in the repository that contains the workflow:
  ACTIONS_RUNNER_DEBUG to true », idem pour `ACTIONS_STEP_DEBUG`, « If both
  the secret and variable are set, the value of the secret takes precedence ».
- **Gravité** : faux.
- **Lab jumelé** : `debug-d-un-workflow` (#40).

## `pipeline-cicd/github/workflows/index.mdx`

### 23. Le lien vers le TP est mort, et le TP décrit n'est pas celui du dépôt

- **Section** : encadré « TP 01 : Votre premier workflow ».
- **Le guide dit** : « Automatisez l'exécution des tests d'une application
  Node.js », lien
  `https://github.com/stephane-robert/github-actions-training/blob/main/tp-01-premier-workflow/README.md`.
- **Ce qui est vrai** : le propriétaire est `stephrobert` et la branche
  `master` ; le TP est en Python (calculatrice et pytest). Après fusion de
  la branche `labs-socle-et-premiers-labs`, la cible devient
  `https://github.com/stephrobert/github-actions-training/blob/master/labs/fondations/premier-workflow/scenario.md`.
- **Preuve** : `curl -s -o /dev/null -w '%{http_code}' <lien du guide>` rend
  `404` ; la même URL avec `stephrobert` et `master` rend `200`.
- **Gravité** : faux.
- **Lab jumelé** : `premier-workflow` (#16).

## Ce que les labs mesurent et que les guides pourraient reprendre

Ces points ne sont pas des erreurs, mais des mesures faites pour les labs qui
manquent aux guides et rendraient l'apprenant plus autonome :

- l'image `catthehacker/ubuntu:act-24.04` embarque Python 3.12.3 et pip 24.0,
  mais pas `uv` ; `actions/setup-python` v7.0.0 y installe une autre version
  en 36 s au premier passage (mesuré le 2026-09-25) ;
- act rend un JSON par ligne avec `--json` : `jobResult` (`success`,
  `failure`), `stepResult`, et `raw_output: true` pour chaque ligne écrite par
  un step. C'est ce qui permet de vérifier un workflow par son résultat plutôt
  qu'en relisant son YAML ; `act.mdx` mentionne `--json` sans dire ce qu'il
  contient ;
- `check-jsonschema --builtin-schema vendor.dependabot` valide un
  `dependabot.yml` hors ligne, `cooldown` compris (0.37.4 et 0.38.2).
