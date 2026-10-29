# Aladdin — structures à 60 % de réussite ou plus

1350 combinaisons testées (entrées sur repli, sorties rapides, objectifs, stops, 5 univers). Une structure est éligible si, sur la période de sélection : réussite ≥ 60 %, ≥ 60 trades, profit factor ≥ 1,3, rendement positif.

## Étape 1 — tester la MÉTHODE de choix sur le passé (choix ≤ 2019, vérification 2020-2024)

| Méthode | Structure choisie avec ≤ 2019 | Réussite 2020-2024 | Rendement/an 2020-2024 | Pire baisse 2020-2024 |
|---|---|---|---|---|
| meilleur Sharpe | multi-actifs — RSI2<15 · objectif +4 %, stop -8 %, max 20 j | 60 % | +7.5 % | -29.3 % |
| le plus régulier (pire année la moins mauvaise, ≥ 6 ans d'historique) | actions+or — RSI2<5 · objectif +2 %, sans stop, max 20 j | 69 % | +3.5 % | -12.9 % |

Méthode retenue (meilleure sur 2020-2024) : **meilleur Sharpe**.

## Étape 2 — la méthode retenue choisit avec ≤ 2024 (top 8)

| # | Univers | Règle | Réussite ≤2024 | Par an ≤2024 | Pire baisse ≤2024 | Pire année ≤2024 |
|---|---|---|---|---|---|---|
| 1 | crypto | plus bas 3 j · objectif +2 %, stop -8 %, max 10 j | 61 % | +28.5 % | -44.1 % | -23.1 % |
| 2 | crypto | plus bas 3 j · objectif +4 %, sans stop, max 20 j | 66 % | +36.0 % | -50.3 % | -22.0 % |
| 3 | crypto | plus bas 3 j · objectif +2 %, stop -15 %, max 10 j | 64 % | +27.7 % | -41.7 % | -23.3 % |
| 4 | crypto | plus bas 3 j · objectif +4 %, stop -15 %, max 20 j | 65 % | +27.7 % | -47.4 % | -24.5 % |
| 5 | crypto | plus bas 5 j · objectif +4 %, sans stop, max 20 j | 70 % | +28.8 % | -46.8 % | -13.3 % |
| 6 | actions+or | RSI2<15 · objectif +4 %, stop -8 %, max 20 j | 64 % | +6.1 % | -16.4 % | -8.9 % |
| 7 | actions+or | plus bas 5 j · objectif +4 %, stop -8 %, max 20 j | 61 % | +6.4 % | -21.0 % | -11.8 % |
| 8 | actions+or | RSI2<15 · objectif +4 %, stop -15 %, max 20 j | 64 % | +5.9 % | -16.4 % | -8.9 % |

## Étape 3 — vérification 2025 → aujourd'hui : crypto — plus bas 3 j · objectif +2 %, stop -8 %, max 10 j

| | ≤ 2024 | 2025 → aujourd'hui |
|---|---|---|
| **Trades gagnants** | **61 %** | **57 %** |
| Nombre de trades | 576 | 144 |
| Gain moyen / perte moyenne par trade | +7.1 % / -7.8 % | +4.2 % / -7.8 % |
| Rendement | +28.5 %/an | -23.3 % au total (-13.8 %/an) |
| Pire baisse | -44.1 % | -30.9 % |

Référence 2025 → aujourd'hui, Garder actions (SPY) : +32.8 %

Référence 2025 → aujourd'hui, Garder or : +58.3 %

Référence 2025 → aujourd'hui, Garder BTC : -13.7 %
