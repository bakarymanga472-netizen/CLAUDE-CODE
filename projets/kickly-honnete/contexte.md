# kickly-honnete (site "Verdict")

## Objectif
Site d'analyse de matchs façon kickly.io (multi-sports, verdict en %, cotes, analyse pas à pas), mais honnête : données réelles, pas de faux témoignages ni de faux taux de réussite, bilan de l'utilisateur vérifié automatiquement.

## Architecture
- `index.html`, `style.css`, `app.js` (interface, routeur `#/`), `models.js` (modèles purs : football Poisson, NBA, MMA, cotes américaines -> décimales, retrait de marge), `tests/models.test.js`.
- `scripts/build-data.js` : récupère ESPN côté serveur (GitHub Actions, toutes les 3 h) et écrit `data/` (jours, détails foot/NBA, résultats des 14 derniers jours, meta). Le navigateur n'appelle AUCUN service externe.
  - Pourquoi : appel direct navigateur -> ESPN refusé en test (403 Akamai) ; API non officielle, donc fragile.
- `.github/workflows/pages-verdict.yml` : tests, assemblage, build des données, déploiement GitHub Pages.
- `backtest/` : football contre cotes de clôture (football-data.co.uk), 5 ligues, test 2023-26. Résultat : log-loss modèle 0,998 / marché 0,964 / mélange 60-40 0,972 ; paris à avantage > 5 % : ROI -18 %.

## Couverture
- Football (Serie A, PL, Liga, Bundesliga, Ligue 1, Ligue des champions) : verdict = cotes DraftKings sans marge si publiées, sinon modèle. Forme, classement, domicile/extérieur, confrontations, scores probables.
- NBA : cotes si publiées, sinon modèle simple (non backtesté) ; prévision ESPN, blessures.
- MMA : fiche + estimation très grossière (non backtestée) ; cotes si publiées.
- Tennis, F1 : planning/résultats, AUCUN pronostic (pas de classement ni de cotes gratuits).

## Limites connues
- Cotes ESPN publiées seulement quelques jours avant le match.
- Aucun modèle ne bat le marché en backtest. Le site ne promet aucun gain.
- Données au plus vieilles de 3 h (sauf panne du workflow : l'ancienne version reste en ligne).
- Vérification des verdicts : fenêtre de 14 jours de résultats.

## Prochaine étape
xG / blessures football, backtest NBA, Elo tennis, puis seulement alors parler de précision.

## Décisions
- Pas de copie des éléments trompeurs de kickly.io (94 %, gains en direct, avis fictifs).
- Barre de progression = étapes réellement exécutées (chargement, cotes, forme, classement, modèle, verdict).
