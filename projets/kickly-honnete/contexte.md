# kickly-honnete

## Objectif
Outil d'analyse de match de football, version honnête d'un site concurrent (kickly.io) : données réelles, méthode visible, performances mesurées, suivi des résultats de l'utilisateur. Pas de promesse de gain, pas de faux témoignages ni de fausses statistiques.

## Où on en est
- `index.html` (sans dépendance) : 5 ligues (openfootball, sans clé, saison en cours + précédente), choix d'un match à venir, forme, classement, domicile/extérieur, confrontations, probabilités du marché (cotes sans marge) et du modèle Poisson, suivi localStorage (ROI, Brier), export CSV.
- `backtest/` : `telecharger.py` (football-data.co.uk, cotes de clôture Pinnacle) + `backtest.py` (walk-forward, paramètres choisis sur 2020-23, test unique 2023-26). Sortie dans `backtest/resultats.txt`.
- Résultat mesuré sur 5 256 matchs : log-loss modèle 0,998 / marché 0,964 / mélange 60-40 0,972. Aucun mélange ne bat le marché seul. Paris à avantage > 5 % : 2 476 paris, 21 % gagnés, ROI -18 %.
- Conséquence : le site affiche le marché comme référence, ne propose plus de mise Kelly ni d'« avantage ».
- Testé en navigateur headless (5 ligues, tous les flux, panne réseau, mobile) : 0 erreur.
- Déploiement : `.github/workflows/pages-verdict.yml` (après fusion dans main + Settings > Pages > Source : GitHub Actions).

## Limites connues
- openfootball a quelques semaines de retard (dernier match connu affiché dans la page).
- Pas de blessures, compositions ni calendrier. Pas de cotes automatiques (saisie manuelle).

## Prochaine étape
Si on veut un modèle utile : ajouter xG, blessures, ratings Elo par club, puis refaire le backtest contre le marché. Sans battre le marché en backtest, ne rien annoncer.

## Décisions
- Refus de copier les éléments trompeurs de kickly.io (94 % de réussite, gains « en direct », faux témoignages).
- Paramètres du modèle figés après le backtest d'entraînement ; le test 2023-26 n'a servi qu'une fois.
