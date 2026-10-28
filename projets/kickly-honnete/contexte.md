# kickly-honnete

## Objectif
Outil d'analyse de match de football, version honnête d'un site concurrent (kickly.io) : données réelles, méthode visible, suivi des résultats de l'utilisateur. Pas de promesse de gain, pas de faux témoignages ni de fausses statistiques.

## Où on en est
- `index.html` unique (sans dépendance) : Poisson, cotes sans marge, mélange 60 % marché / 40 % modèle, Kelly/4 plafonné 3 %, suivi localStorage avec Brier.
- Testé en navigateur headless : 0 erreur JS, chargement TheSportsDB OK.
- Limite : la clé gratuite `123` ne renvoie qu'1 match par équipe.
- Déploiement : `.github/workflows/pages-verdict.yml` (après fusion dans main + Settings > Pages > Source : GitHub Actions).

## Prochaine étape
Brancher une source avec historique (football-data.org, clé gratuite dans `.env`), puis backtest sur plusieurs saisons contre les cotes de clôture avant d'afficher la moindre « précision ».

## Décisions
- Refus de copier les éléments trompeurs de kickly.io (94 % de réussite, gains « en direct », faux témoignages).
