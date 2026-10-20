# Stratégie combinée à haut taux de réussite

Commande : `python3 -m labo.combine` · règles fixées avant exécution : en-tête de `labo/combine.py`.

## Les 4 variantes (levier 1, 5 positions max de 20 %)

| Variante | Période | Trades | Réussite | Gain moyen | Perte moyenne | Pire trade | Profit factor | Rendement/an | Pire baisse | Sharpe | Mois positifs | Mois moyen | Pire mois |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A5 ← choix ≥ 70 % | 2000-2015 (choix) | 573 | +79 % | +1.7 % | -3.7 % | -18.5 % | 1.67 | +3.8 % | -13 % | 0.60 | 58 % | +0.32 % | -9.1 % |
| A5 ← choix ≥ 70 % | 2016-2021 (contrôle) | 269 | +71 % | +1.7 % | -2.3 % | -10.2 % | 1.82 | +5.0 % | -9 % | 0.57 | 61 % | +0.42 % | -6.8 % |
| A5 ← choix ≥ 70 % | 2022 → aujourd'hui (test) | 227 | +75 % | +1.8 % | -3.1 % | -10.6 % | 1.78 | +5.6 % | -10 % | 0.84 | 62 % | +0.47 % | -4.8 % |
| A10 | 2000-2015 (choix) | 884 | +75 % | +1.7 % | -3.6 % | -18.5 % | 1.43 | +4.1 % | -13 % | 0.51 | 59 % | +0.35 % | -9.0 % |
| A10 | 2016-2021 (contrôle) | 396 | +71 % | +1.7 % | -2.6 % | -17.5 % | 1.60 | +6.1 % | -13 % | 0.64 | 64 % | +0.52 % | -6.3 % |
| A10 | 2022 → aujourd'hui (test) | 337 | +73 % | +1.9 % | -3.7 % | -11.5 % | 1.33 | +4.0 % | -11 % | 0.47 | 60 % | +0.35 % | -5.4 % |
| B5 | 2000-2015 (choix) | 642 | +67 % | +1.4 % | -1.5 % | -18.5 % | 1.82 | +3.4 % | -14 % | 0.67 | 54 % | +0.29 % | -9.5 % |
| B5 | 2016-2021 (contrôle) | 323 | +63 % | +1.2 % | -1.5 % | -6.9 % | 1.38 | +2.3 % | -10 % | 0.38 | 57 % | +0.20 % | -3.7 % |
| B5 | 2022 → aujourd'hui (test) | 270 | +68 % | +1.4 % | -1.6 % | -9.2 % | 1.87 | +4.9 % | -6 % | 0.96 | 67 % | +0.41 % | -3.7 % |
| B10 ← choix Sharpe | 2000-2015 (choix) | 1180 | +63 % | +1.4 % | -1.4 % | -18.5 % | 1.63 | +4.9 % | -14 % | 0.73 | 63 % | +0.42 % | -9.9 % |
| B10 ← choix Sharpe | 2016-2021 (contrôle) | 540 | +62 % | +1.2 % | -1.6 % | -11.4 % | 1.23 | +2.5 % | -14 % | 0.36 | 64 % | +0.22 % | -5.7 % |
| B10 ← choix Sharpe | 2022 → aujourd'hui (test) | 477 | +68 % | +1.4 % | -1.7 % | -12.0 % | 1.83 | +8.3 % | -6 % | 1.19 | 71 % | +0.68 % | -5.0 % |

**Achat-conservation équipondéré des 16 ETF (référence)** :

| Période | Rendement/an | Pire baisse | Sharpe | Mois positifs | Mois moyen | Pire mois |
|---|---|---|---|---|---|---|
| 2000-2015 (choix) | +6.2 % | -47 % | 0.42 | 59 % | +0.58 % | -15.6 % |
| 2016-2021 (contrôle) | +14.5 % | -31 % | 0.95 | 76 % | +1.20 % | -11.8 % |
| 2022 → aujourd'hui (test) | +10.3 % | -19 % | 0.78 | 64 % | +0.88 % | -8.7 % |

## Curseur de levier — ce que coûtent des gains plus gros


### B10 — choix initial (Sharpe)

**Entrées au hasard, mêmes sorties (50 tirages)** : réussite médiane 57 %, Sharpe médian 0.52 ; la stratégie bat 100 % des tirages en réussite et 98 % en Sharpe.

| Levier | Réussite | Rendement/an (2000 → auj.) | Mois moyen | Mois médian | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |
|---|---|---|---|---|---|---|---|---|---|
| ×1 | +64 % | +5.0 % | +0.42 % | +0.37 % | 65 % | -9.9 % | -14 % | +8.3 %, -6 % | 0 % |
| ×2 | +64 % | +8.9 % | +0.78 % | +0.68 % | 63 % | -19.6 % | -29 % | +15.8 %, -13 % | 0 % |
| ×3 | +64 % | +12.1 % | +1.10 % | +0.92 % | 62 % | -28.9 % | -43 % | +22.9 %, -18 % | 4 % |
| ×4 | +64 % | +14.7 % | +1.42 % | +1.20 % | 61 % | -37.7 % | -55 % | +29.6 %, -24 % | 18 % |
| ×6 | +64 % | +18.0 % | +2.01 % | +1.62 % | 60 % | -53.9 % | -73 % | +41.8 %, -35 % | 50 % |
| ×10 | +64 % | +16.2 % | +3.07 % | +2.13 % | 58 % | -79.4 % | -94 % | +59.3 %, -54 % | 94 % |

### A5 — choix sous contrainte ≥ 70 % de réussite

**Entrées au hasard, mêmes sorties (50 tirages)** : réussite médiane 75 %, Sharpe médian 0.62 ; la stratégie bat 78 % des tirages en réussite et 54 % en Sharpe.

| Levier | Réussite | Rendement/an (2000 → auj.) | Mois moyen | Mois médian | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |
|---|---|---|---|---|---|---|---|---|---|
| ×1 | +76 % | +4.4 % | +0.37 % | +0.34 % | 59 % | -9.1 % | -13 % | +5.6 %, -10 % | 0 % |
| ×2 | +76 % | +7.6 % | +0.67 % | +0.56 % | 59 % | -18.2 % | -24 % | +10.2 %, -21 % | 0 % |
| ×3 | +76 % | +10.0 % | +0.92 % | +0.82 % | 59 % | -27.0 % | -35 % | +13.9 %, -30 % | 6 % |
| ×4 | +76 % | +11.6 % | +1.15 % | +0.97 % | 59 % | -35.4 % | -45 % | +17.1 %, -38 % | 20 % |
| ×6 | +76 % | +12.9 % | +1.55 % | +1.36 % | 57 % | -51.1 % | -62 % | +21.7 %, -53 % | 57 % |
| ×10 | +76 % | +7.0 % | +2.18 % | +1.63 % | 56 % | -76.9 % | -86 % | +23.7 %, -74 % | 95 % |

Levier ×L = chaque position pèse L × 20 % ; au-delà de 100 % investi, emprunt à 5 %/an. Risque de ruine estimé par rééchantillonnage de l'historique (blocs d'un mois) : il ne contient pas de krach pire que ceux déjà vus.

