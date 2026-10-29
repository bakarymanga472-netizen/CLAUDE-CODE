# Audit 02 — Aladdin Rebond

## 1. Reproduction

- `enquete.executer` (moteur de sorties.py) : 143 trades ; moteur d'audit : 143 trades ; identiques : **True**
- Réussite reproduite : 2006-19 84.3 % (89), 2020-24 77.5 % (40), 2025+ 78.6 % (14) — rapport : 84 / 78 / 79 %, 89 / 40 / 14 trades.
- Premier trade : 2006-11-02 (le libellé « 2008-2019 » de sorties.py couvre en fait 2006-2019).
- Trades encore ouverts comptés comme clos (valorisés à la dernière clôture) : 0
- ACTIONS : 83 trades, réussite 80 %
- OR : 60 trades, réussite 85 %
- Intervalle de confiance 95 % (Wilson) de la réussite 2025+ : 52–92 % ; 2020-24 : 62–88 %
- « Rendement cumulé des trades » 2020-24 (somme des log, enquete.py:111, affiché par sorties.py) : +38 % vs portefeuille 50/50 réel : +20.6 %
- « Rendement cumulé des trades » 2025+ (somme des log, enquete.py:111, affiché par sorties.py) : +13 % vs portefeuille 50/50 réel : +8.2 %
- Portefeuille Rebond 2006-10→fin : +3.3 %/an, pire baisse -7.3 %, Sharpe 0.74, exposition 22 % des séances ; 50/50 SPY+or gardé : +11.6 %/an, pire baisse -32.6 %, Sharpe 0.88
- Gain moyen +1.76 %, perte moyenne -2.85 %, pire trade -11.65 % → réussite d'équilibre = 62 %

## 2. Coûts, exécution, instrument

| Variante | Réussite 2006-19 (n) | 2020-24 (n) | 2025+ (n) | PF app/val/2025+ | Portefeuille /an | Pire baisse | Sharpe (252) |
|---|---|---|---|---|---|---|---|
| Référence (clôture suivante, frais 0,05 %) | 84 % (89) | 78 % (40) | 79 % (14) | 2.72 / 3.15 / 2.37 | +3.3 % | -7.3 % | 0.74 |
| Frais ×2 (0.10 % par côté) | 82 % (89) | 78 % (40) | 79 % (14) | 2.47 / 2.84 / 2.19 | +3.0 % | -7.4 % | 0.66 |
| Frais ×3 (0.15 % par côté) | 82 % (89) | 78 % (40) | 79 % (14) | 2.24 / 2.56 / 2.03 | +2.6 % | -7.5 % | 0.58 |
| Même clôture que le signal (optimiste, ≈ alpaca.py idéal) | 90 % (91) | 83 % (41) | 80 % (15) | 2.92 / 1.55 / 1.12 | +2.3 % | -11.3 % | 0.56 |
| Un jour de retard (clôture t+2) | 75 % (88) | 70 % (37) | 69 % (13) | 1.93 / 1.22 / 2.62 | +1.9 % | -9.8 % | 0.43 |
| GLD au lieu de GC=F (instrument réellement traité) | 82 % (92) | 79 % (39) | 82 % (17) | 2.92 / 2.92 / 1.81 | +3.3 % | -7.1 % | 0.72 |
| SPY+GLD, clôture suivante (base de comparaison) | 82 % (92) | 79 % (39) | 82 % (17) | 2.77 / 2.92 / 1.81 | +3.2 % | -7.1 % | 0.71 |
| SPY+GLD, ouverture suivante | 86 % (92) | 79 % (39) | 89 % (18) | 2.69 / 1.88 / 1.71 | +2.8 % | -9.7 % | 0.64 |
| SPY+GLD, ouverture suivante + frais ×3 | 85 % (92) | 79 % (39) | 89 % (18) | 2.22 / 1.56 / 1.45 | +2.0 % | -9.9 % | 0.47 |
| Moteur 7j/7 de reussite.py = celui de live_rebond.py (Sharpe sur 252 non comparable) | 76 % (178) | 71 % (75) | 75 % (32) | 1.84 / 1.78 / 1.62 | +3.6 % | -10.7 % | 0.55 |
| ACTIONS seul | 83 % (52) | 73 % (22) | 78 % (9) | 3.12 / 2.05 / 2.11 | +3.4 % | -14.1 % | 0.52 |
| OR seul | 86 % (37) | 83 % (18) | 80 % (5) | 2.34 / 6.92 / 2.77 | +3.1 % | -12.4 % | 0.54 |

## 3. Périodes de crise (trades entrés dans la fenêtre, portefeuille sur la fenêtre)

| Fenêtre | Trades | Réussite | Pire trade | Rendement portefeuille | Pire baisse portefeuille | SPY+or gardé |
|---|---|---|---|---|---|---|
| 2008 (crise financière) | 6 | 83 % | -11.7 % | -0.8 % | -6.0 % | -15.3 % |
| Krach 2020 | 2 | 50 % | -7.8 % | +0.7 % | -6.3 % | -3.0 % |
| 2022 (inflation) | 4 | 25 % | -1.7 % | -0.6 % | -3.0 % | -8.8 % |
| Or : avril 2013 | 0 | nan % | — | +0.0 % | +0.0 % | -10.9 % |

Les 8 pires trades : OR 2008-07-31 -11.7 % (8 s.); ACTIONS 2011-07-28 -9.9 % (8 s.); ACTIONS 2020-02-25 -7.8 % (10 s.); OR 2014-03-21 -4.2 % (21 s.); ACTIONS 2025-02-25 -4.1 % (21 s.); OR 2026-05-18 -4.0 % (21 s.); ACTIONS 2012-05-07 -3.8 % (21 s.); OR 2007-05-11 -3.4 % (21 s.)

Trades sortis au-delà du stop -10 % (écart de cours / exécution le lendemain) : 1

## 4. 5 % des séances retirées au hasard (50 tirages)

- Réussite 2006-19 : médiane 83 % [min 77 – max 89]
- Réussite 2020-24 : médiane 78 % [min 64 – max 84]
- Réussite 2025+ : médiane 77 % [min 67 – max 87], trades 11–16
- Sharpe portefeuille : médiane 0.64 [min 0.41 – max 0.87]

## 5. Paramètres voisins (durée max 20 séances)

| RSI2 < | Objectif | Stop | Réussite 06-19 | 20-24 | 2025+ | PF 06-19 / 20-24 / 25+ | Portefeuille /an | Pire baisse | Sharpe |
|---|---|---|---|---|---|---|---|---|---|
| 3 | +0.5 % | -5 % | 80 % | 71 % | 57 % | 3.14 / 1.33 / 1.20 | +1.2 % | -6.6 % | 0.44 |
| 3 | +0.5 % | -10 % | 80 % | 71 % | 57 % | 3.21 / 1.15 / 1.69 | +1.2 % | -7.3 % | 0.39 |
| 3 | +0.5 % | -15 % | 80 % | 71 % | 57 % | 3.87 / 0.87 / 1.69 | +1.2 % | -10.7 % | 0.32 |
| 3 | +1.0 % | -5 % | 85 % | 62 % | 71 % | 4.37 / 1.28 / 1.82 | +1.9 % | -6.1 % | 0.62 |
| 3 | +1.0 % | -10 % | 85 % | 62 % | 71 % | 4.47 / 1.14 / 2.58 | +1.9 % | -7.0 % | 0.56 |
| 3 | +1.0 % | -15 % | 85 % | 62 % | 71 % | 5.43 / 0.91 / 2.58 | +1.8 % | -10.7 % | 0.48 |
| 3 | +1.5 % | -5 % | 89 % | 58 % | 71 % | 3.97 / 1.30 / 0.86 | +1.8 % | -5.7 % | 0.57 |
| 3 | +1.5 % | -10 % | 89 % | 58 % | 71 % | 3.63 / 1.17 / 1.12 | +1.8 % | -7.0 % | 0.50 |
| 3 | +1.5 % | -15 % | 89 % | 58 % | 71 % | 4.15 / 0.93 / 1.12 | +1.8 % | -10.7 % | 0.43 |
| 3 | +2.0 % | -5 % | 83 % | 54 % | 71 % | 2.56 / 1.30 / 0.75 | +1.7 % | -6.3 % | 0.46 |
| 3 | +2.0 % | -10 % | 83 % | 54 % | 71 % | 2.49 / 1.17 / 0.99 | +1.7 % | -6.6 % | 0.42 |
| 3 | +2.0 % | -15 % | 83 % | 54 % | 71 % | 2.70 / 0.94 / 0.99 | +1.6 % | -10.9 % | 0.37 |
| 5 | +0.5 % | -5 % | 81 % | 74 % | 64 % | 2.29 / 2.40 / 1.55 | +2.2 % | -6.2 % | 0.62 |
| 5 | +0.5 % | -10 % | 81 % | 74 % | 71 % | 2.21 / 1.95 / 2.82 | +2.2 % | -7.5 % | 0.56 |
| 5 | +0.5 % | -15 % | 81 % | 74 % | 71 % | 2.34 / 1.51 / 2.82 | +2.2 % | -10.7 % | 0.49 |
| 5 | +1.0 % | -5 % | 84 % | 78 % | 71 % | 2.82 / 4.03 / 1.08 | +3.1 % | -5.6 % | 0.77 |
| 5 | +1.0 % | -10 % | 84 % | 78 % | 79 % | 2.72 / 3.15 / 2.37 | +3.3 % | -7.3 % | 0.74 |
| 5 | +1.0 % | -15 % | 84 % | 78 % | 79 % | 2.89 / 2.36 / 2.37 | +3.3 % | -10.7 % | 0.67 |
| 5 | +1.5 % | -5 % | 82 % | 74 % | 77 % | 2.26 / 2.83 / 1.21 | +3.0 % | -7.5 % | 0.68 |
| 5 | +1.5 % | -10 % | 82 % | 74 % | 85 % | 2.29 / 2.80 / 2.99 | +3.3 % | -8.5 % | 0.69 |
| 5 | +1.5 % | -15 % | 82 % | 74 % | 85 % | 2.40 / 2.18 / 2.99 | +3.2 % | -10.7 % | 0.63 |
| 5 | +2.0 % | -5 % | 82 % | 71 % | 77 % | 2.27 / 3.08 / 1.34 | +3.5 % | -7.3 % | 0.75 |
| 5 | +2.0 % | -10 % | 82 % | 71 % | 85 % | 2.23 / 3.05 / 3.58 | +3.9 % | -7.8 % | 0.76 |
| 5 | +2.0 % | -15 % | 82 % | 71 % | 85 % | 2.32 / 2.39 / 3.58 | +3.8 % | -10.9 % | 0.70 |
| 7 | +0.5 % | -5 % | 79 % | 72 % | 81 % | 2.28 / 2.87 / 3.13 | +3.3 % | -8.8 % | 0.78 |
| 7 | +0.5 % | -10 % | 79 % | 72 % | 81 % | 2.24 / 2.37 / 4.64 | +3.3 % | -9.5 % | 0.71 |
| 7 | +0.5 % | -15 % | 79 % | 72 % | 81 % | 2.36 / 1.87 / 4.64 | +3.2 % | -10.7 % | 0.64 |
| 7 | +1.0 % | -5 % | 81 % | 76 % | 86 % | 2.79 / 3.62 / 2.13 | +4.3 % | -5.9 % | 0.92 |
| 7 | +1.0 % | -10 % | 81 % | 76 % | 86 % | 2.51 / 2.97 / 4.16 | +4.3 % | -9.3 % | 0.84 |
| 7 | +1.0 % | -15 % | 81 % | 76 % | 86 % | 2.61 / 2.32 / 4.16 | +4.2 % | -10.7 % | 0.77 |
| 7 | +1.5 % | -5 % | 79 % | 71 % | 85 % | 2.58 / 2.48 / 2.52 | +4.6 % | -7.4 % | 0.89 |
| 7 | +1.5 % | -10 % | 79 % | 71 % | 85 % | 2.38 / 2.46 / 5.30 | +4.7 % | -9.3 % | 0.84 |
| 7 | +1.5 % | -15 % | 79 % | 71 % | 85 % | 2.46 / 2.03 / 5.30 | +4.6 % | -10.7 % | 0.78 |
| 7 | +2.0 % | -5 % | 80 % | 69 % | 85 % | 2.88 / 2.94 / 2.59 | +5.5 % | -7.4 % | 0.99 |
| 7 | +2.0 % | -10 % | 79 % | 69 % | 85 % | 2.53 / 2.93 / 5.06 | +5.5 % | -9.3 % | 0.92 |
| 7 | +2.0 % | -15 % | 79 % | 69 % | 85 % | 2.61 / 2.42 / 5.06 | +5.4 % | -10.7 % | 0.87 |
| 10 | +0.5 % | -5 % | 77 % | 73 % | 76 % | 1.54 / 1.98 / 1.70 | +2.6 % | -11.8 % | 0.53 |
| 10 | +0.5 % | -10 % | 77 % | 76 % | 79 % | 1.72 / 2.63 / 2.05 | +3.2 % | -11.1 % | 0.60 |
| 10 | +0.5 % | -15 % | 77 % | 76 % | 79 % | 1.80 / 2.11 / 3.33 | +3.3 % | -10.8 % | 0.58 |
| 10 | +1.0 % | -5 % | 78 % | 77 % | 76 % | 1.94 / 2.10 / 1.53 | +3.7 % | -12.1 % | 0.68 |
| 10 | +1.0 % | -10 % | 78 % | 78 % | 79 % | 2.06 / 2.85 / 2.20 | +4.4 % | -11.1 % | 0.75 |
| 10 | +1.0 % | -15 % | 78 % | 78 % | 79 % | 2.16 / 2.30 / 3.33 | +4.4 % | -10.7 % | 0.72 |
| 10 | +1.5 % | -5 % | 76 % | 71 % | 70 % | 1.80 / 1.91 / 1.16 | +3.6 % | -13.7 % | 0.63 |
| 10 | +1.5 % | -10 % | 76 % | 73 % | 74 % | 1.90 / 2.55 / 1.57 | +4.4 % | -12.1 % | 0.70 |
| 10 | +1.5 % | -15 % | 76 % | 73 % | 73 % | 1.97 / 2.15 / 1.97 | +4.5 % | -11.1 % | 0.68 |
| 10 | +2.0 % | -5 % | 73 % | 69 % | 74 % | 1.69 / 2.15 / 1.55 | +4.1 % | -15.3 % | 0.66 |
| 10 | +2.0 % | -10 % | 73 % | 70 % | 78 % | 1.71 / 2.86 / 2.08 | +4.7 % | -13.7 % | 0.72 |
| 10 | +2.0 % | -15 % | 73 % | 70 % | 77 % | 1.76 / 2.41 / 2.80 | +4.8 % | -12.7 % | 0.70 |

Sharpe sur la grille de 48 voisins : min 0.32, médiane 0.68, max 0.99 ; référence 0.74. Réussite 2025+ ≥ 70 % pour 44/48 voisins.
- Durée max 5 séances : réussite 73 / 57 / 60 %, Sharpe 0.54
- Durée max 10 séances : réussite 76 / 70 / 71 %, Sharpe 0.51
- Durée max 30 séances : réussite 85 / 82 / 77 %, Sharpe 0.61

## 6. Entrées au hasard (cours > MM200, même nombre de trades, mêmes sorties +1 % / -10 % / 20 s.) — 200 tirages

- Hasard : réussite médiane 76 % (5e–95e centile 73–80 %), PF médian 1.51
- Règle RSI2<5 : réussite 82 %, PF 2.78 → centile de la règle parmi le hasard : réussite 99e, log-rendement moyen par trade 100e

## 7. Bootstrap des trades (hypothèses explicites)

Hypothèses : 143 trades clos 2006-2026 tirés avec remise ; 7.3 trades/an (Poisson) ; chaque trade engage 50 % du capital (une poche) ; trades indépendants (pas de chevauchement modélisé) ; horizon 10 ans ; 20000 simulations.

- Fréquence des trades perdants : 18 % ; probabilité d'au moins 2 pertes sur 10 trades : 57%
- Pire baisse sur 10 ans : médiane -5.8 %, 5e centile -10.8 %, 1er centile -14.5 %
- P(pire baisse ≥ 10 %) = 7.4% ; P(≥ 20 %) = 0.07% ; P(≥ 50 %, « ruine ») = 0.000%
- P(perte sur 10 ans) = 0.20% ; rendement 10 ans médian +39.5 % (≈ +3.4 %/an)
- Variante 100 % du capital par trade (un seul actif) : P(pire baisse ≥ 20 %) = 3.2%, P(≥ 30 %) = 0.2%
- Bootstrap par blocs de 21 séances du portefeuille quotidien (10 ans) : pire baisse médiane -7.5 %, 5e centile -13.0 %, P(≥ 20 %) = 0.4%

## 8. Deflated Sharpe Ratio (portefeuille quotidien 2006-10 → 2024, période de sélection + validation)

Essais comptés dans la lignée Rebond : reussite.py 1 350 combinaisons (+2 méthodes de choix), enquete.py 42 filtres × 2 structures (+1 validation), sorties.py 180 réglages → **1 572 essais** (1 662 pour tout Aladdin). Variance des Sharpe entre essais estimée sur la grille de 48 voisins (par séance) = 7.53e-05 (borne basse : des voisins sont très corrélés).

| Essais N | Sharpe annuel observé | Sharpe annuel attendu du meilleur sous H0 | PSR(0) | DSR |
|---|---|---|---|---|
| 1 | 0.74 | 0.00 | 0.999 | **0.999** |
| 180 | 0.74 | 0.38 | 0.999 | **0.937** |
| 1572 | 0.74 | 0.47 | 0.999 | **0.876** |
| 1572 (var ×4) | 0.74 | 0.93 | 0.999 | **0.217** |

Asymétrie -0.65, kurtosis 38.0, T = 4594 séances. DSR > 0,95 requis pour conclure à un Sharpe > 0 après correction.
