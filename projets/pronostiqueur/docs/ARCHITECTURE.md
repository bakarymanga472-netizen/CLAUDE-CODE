# Architecture

```
football-data.co.uk ──► data/football_data_uk.py ──► data/quality.py ──► data/storage.py (SQLite)
                         (téléchargement, cache,       (rejets motivés,      matches · predictions
                          normalisation, horodatage)    doublons, cohérence)  outcomes · model_versions
                                                                                     │
                                         features.py ◄───────────────────────────────┘
                     (parcours chronologique, état AVANT chaque journée,
                      moyennes pondérées, rétrécissement bayésien, 1re et 2e MT séparées)
                                               │
                     models/ensemble.py ◄──────┘
        poisson · dixon-coles · marché (cotes sans marge) · bayésien · logistique · gradient boosting
        → poids positifs + calibration de Platt appris hors échantillon
                                               │
          ┌────────────────────────────────────┼─────────────────────────────┐
     backtest.py                          predict.py + risk.py           registry.py
  (walk-forward, Brier, log-loss,     (tableau par match, fourchette,   (versions, comparaison
   calibration, haute confiance,       cote juste, valeur, statut,       bootstrap, promotion,
   biais par segment)                  journalisation)                   retour arrière)
          │                                    │                             │
     report.py ── reports/backtest_report.md · backtest_dashboard.html · journal_report.md
```

## Modules

| Module | Rôle |
|---|---|
| `config.py` | Ligues, saisons, chemins, règles de sélection, réglages des variables |
| `data/football_data_uk.py` | Connecteur (cache, délais, nouvelles tentatives, erreurs explicites) |
| `data/quality.py` | Contrôle qualité : dates, scores manquants, mi-temps > final, doublons, cotes aberrantes |
| `data/schema.sql`, `data/storage.py` | Base SQLite : historique, journal, résultats, versions |
| `features.py` | Variables d'avant-match sans fuite (vérifié par test) |
| `odds.py` | Probabilités implicites, retrait de marge (méthode « power »), λ implicite, cote juste, espérance |
| `models/ensemble.py` | Modèles par mi-temps et combinaison calibrée |
| `models/players.py` | Buteurs / passeurs : **non implémenté** (données manquantes) |
| `backtest.py`, `metrics.py` | Validation chronologique et mesures (Brier, log-loss, ECE, Wilson) |
| `risk.py` | Indice de risque et statut (admissible / à surveiller / données insuffisantes / à éviter) |
| `registry.py` | Évolution contrôlée des modèles et retour arrière |
| `report.py` | Rapports Markdown et tableau de bord HTML statique |
| `cli.py` | Commandes `fetch`, `backtest`, `train`, `predict`, `settle`, `report`, `evolve`, `rollback` |

## Garanties de non-fuite

1. Les variables d'un match sont calculées avec l'état des équipes **avant**
   la journée (les matchs du même jour ne se voient pas). Testé dans
   `tests/test_features_models.py`.
2. Les cotes utilisées sont les cotes **d'avant-match** (colonnes `Avg`), pas
   les cotes de clôture.
3. Validation « walk-forward » : chaque saison est prédite par des modèles
   entraînés uniquement sur les saisons précédentes.
4. Les poids de l'ensemble sont appris sur des prédictions hors échantillon
   (validation croisée temporelle à l'intérieur de la période d'entraînement).

## Évolution

- `settle` + `report` : performance réelle (séparée de la simulation).
- `evolve` : teste des réglages candidats contre la production sur les
  120 derniers jours (jamais vus à l'entraînement). Promotion seulement si
  le candidat est meilleur dans au moins 95 % des rééchantillonnages
  (bootstrap apparié sur la log-loss). Ancienne version conservée → `rollback`.
- Le workflow GitHub `pronostiqueur-evaluation.yml` (racine du dépôt) relance chaque semaine la collecte, la
  validation et l'évolution, et publie les rapports en artefacts.
