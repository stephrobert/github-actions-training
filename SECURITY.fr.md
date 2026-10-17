# Politique de sécurité

**Langue :** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Versions supportées

`github-actions-training` n'est pas versionné : il n'y a pas de version
publiée à maintenir. Les correctifs de sécurité sont appliqués à la branche
d'intégration `develop`, le seul état supporté du catalogue.

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique pour une vulnérabilité de sécurité.**

Si vous pensez avoir trouvé une vulnérabilité, signalez-la en privé :

- De préférence : ouvrez un
  [avis de sécurité privé](https://github.com/stephrobert/github-actions-training/security/advisories/new)
  sur GitHub.
- Sinon, utilisez les coordonnées publiées sur
  <https://blog.stephane-robert.info>.

Merci d'inclure :

- une description de la vulnérabilité et de son impact,
- les étapes pour la reproduire (commande, environnement, `dsoxlab --version`,
  `act --version`),
- tout journal ou preuve de concept pertinent.

Nous vous tiendrons informé de l'avancement du correctif et vous créditerons
dans l'avis si vous le souhaitez.

## Politique de divulgation

Nous pratiquons la divulgation coordonnée et nous engageons sur les délais
suivants, décomptés à partir de la réception de votre signalement :

| Étape | Délai visé |
| --- | --- |
| Accusé de réception de votre signalement | sous **48 heures** |
| Évaluation initiale et qualification de la sévérité | sous **5 jours** |
| Correctif publié, ou plan de remédiation écrit | sous **30 jours** |
| Divulgation publique de la vulnérabilité | sous **90 jours** |

Nous publions l'avis dès qu'un correctif est disponible, ou au plus tard à
l'échéance des **90 jours**, selon ce qui arrive en premier. Si une
vulnérabilité est activement exploitée, nous pouvons la divulguer plus tôt pour
protéger les utilisateurs. Si un correctif complexe demande plus de temps, nous
vous prévenons avant l'échéance et convenons d'une nouvelle date avec vous.

## Périmètre

Ce dépôt livre du **contenu de labs** exécuté par la CLI externe `dsoxlab` :
scénarios, points de départ, solutions de référence, tests, et les workflows
que act joue sur le poste de l'apprenant.

Sont **dans** le périmètre :

- du matériel de lab dangereux ou malveillant : une fixture, une solution ou
  un test qui ferait autre chose que ce qu'il annonce ;
- un workflow du dépôt ou d'un lab qui exposerait un secret, élargirait les
  permissions du jeton sans raison, ou exécuterait du code non fiable ;
- une action épinglée sur un SHA qui ne correspond pas à la version annoncée ;
- une fuite de secret commitée par erreur.

Une remarque particulière sur ce catalogue : **plusieurs labs livrent
délibérément un workflow vulnérable**, parce que c'est leur sujet. Le lab sur
l'injection de template part d'un workflow injectable, celui sur
`pull_request_target` part du motif dangereux, celui sur l'épinglage part de
tags mobiles. Ce n'est pas une vulnérabilité du dépôt : c'est la matière de
l'exercice. Ces workflows se jouent **en local, avec act**, dans le répertoire
de travail du lab, et non sur un dépôt qui sert à autre chose.

Sont **hors** périmètre : les vulnérabilités du moteur `dsoxlab`, qui relèvent
de [son propre dépôt](https://github.com/stephrobert/dsoxlab), celles d'act et
des actions tierces, à signaler à leurs projets respectifs.
