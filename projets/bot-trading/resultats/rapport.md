# Résultats du bot multi-agents

Données Binance journalières jusqu'au 2026-10-14. Capital fictif 10 000 USDT. Frais 0,1 % + glissement 0,05 % par ordre. Décision à la clôture, exécution à l'ouverture du lendemain.

Paramètres fixés à l'avance, **aucune optimisation** sur ces données.


## Période complète (2020-08 → aujourd'hui)

| Stratégie | Rendement | Par an | Pire baisse | Sharpe | Trades | Gagnants | Profit factor |
|---|---|---|---|---|---|---|---|
| **Bot 5 agents** | +168.7 % | +17.3 % | -21.7 % | 0.89 | 288 | 32 % | 1.89 |
| sans agent sentiment | +205.7 % | +19.7 % | -21.7 % | 0.97 | 297 | 32 % | 1.93 |
| sans agent flux | +166.4 % | +17.1 % | -21.7 % | 0.89 | 290 | 31 % | 1.86 |
| sans agent setups | +58.3 % | +7.7 % | -27.9 % | 0.49 | 407 | 36 % | 1.29 |
| sans agent risque | +929.8 % | +45.7 % | -50.1 % | 1.01 | 205 | 29 % | 1.55 |
| + agent macro (MacroMicro) | +27.3 % | +4.0 % | -25.4 % | 0.34 | 233 | 29 % | 1.31 |
| + agent géopolitique (World Monitor) | +176.4 % | +17.8 % | -20.8 % | 0.92 | 266 | 31 % | 2.00 |
| **7 agents (5 + macro + géopolitique)** | +22.0 % | +3.3 % | -25.9 % | 0.30 | 216 | 30 % | 1.28 |
| Acheter et garder BTC | +592.2 % | +36.6 % | -76.6 % | 0.83 | — | — | — |
| Acheter et garder le panier | +995.5 % | +47.1 % | -87.1 % | 0.87 | — | — | — |
| 300 bots au hasard (médiane) | +55.9 % | — | -25.1 % | — | — | — | — |

Mieux que les 300 bots qui achètent au hasard (même gestion du risque) : bot 5 agents **99 %**, bot 7 agents **17 %**.

## Période 2020-08 → 2023-12

| Stratégie | Rendement | Par an | Pire baisse | Sharpe | Trades | Gagnants | Profit factor |
|---|---|---|---|---|---|---|---|
| **Bot 5 agents** | +142.0 % | +29.5 % | -18.4 % | 1.29 | 160 | 34 % | 2.79 |
| sans agent sentiment | +178.2 % | +34.9 % | -18.4 % | 1.41 | 168 | 35 % | 2.97 |
| sans agent flux | +145.2 % | +30.0 % | -19.5 % | 1.30 | 160 | 34 % | 2.85 |
| sans agent setups | +60.9 % | +15.0 % | -27.9 % | 0.85 | 218 | 36 % | 1.66 |
| sans agent risque | +946.7 % | +98.9 % | -50.1 % | 1.50 | 109 | 36 % | 2.84 |
| + agent macro (MacroMicro) | +50.6 % | +12.8 % | -19.2 % | 0.76 | 133 | 32 % | 1.85 |
| + agent géopolitique (World Monitor) | +129.2 % | +27.5 % | -17.9 % | 1.25 | 149 | 34 % | 2.71 |
| **7 agents (5 + macro + géopolitique)** | +41.2 % | +10.6 % | -17.8 % | 0.67 | 123 | 33 % | 1.77 |
| Acheter et garder BTC | +258.3 % | +45.3 % | -76.6 % | 0.90 | — | — | — |
| Acheter et garder le panier | +700.6 % | +83.9 % | -87.1 % | 1.10 | — | — | — |
| 300 bots au hasard (médiane) | +40.8 % | — | -24.7 % | — | — | — | — |

Mieux que les 300 bots qui achètent au hasard (même gestion du risque) : bot 5 agents **100 %**, bot 7 agents **51 %**.

## Période 2024-01 → aujourd'hui

| Stratégie | Rendement | Par an | Pire baisse | Sharpe | Trades | Gagnants | Profit factor |
|---|---|---|---|---|---|---|---|
| **Bot 5 agents** | +10.2 % | +3.6 % | -21.7 % | 0.29 | 134 | 27 % | 1.24 |
| sans agent sentiment | +9.1 % | +3.2 % | -21.7 % | 0.27 | 135 | 27 % | 1.22 |
| sans agent flux | +8.5 % | +3.0 % | -21.7 % | 0.26 | 137 | 26 % | 1.21 |
| sans agent setups | -3.2 % | -1.2 % | -27.9 % | 0.03 | 195 | 34 % | 1.00 |
| sans agent risque | +7.5 % | +2.6 % | -47.9 % | 0.26 | 100 | 22 % | 1.09 |
| + agent macro (MacroMicro) | -19.6 % | -7.5 % | -24.8 % | -0.74 | 106 | 24 % | 0.46 |
| + agent géopolitique (World Monitor) | +19.3 % | +6.6 % | -20.8 % | 0.45 | 124 | 27 % | 1.43 |
| **7 agents (5 + macro + géopolitique)** | -20.0 % | -7.7 % | -25.2 % | -0.80 | 100 | 24 % | 0.43 |
| Acheter et garder BTC | +84.9 % | +24.7 % | -53.0 % | 0.70 | — | — | — |
| Acheter et garder le panier | +7.0 % | +2.5 % | -67.3 % | 0.35 | — | — | — |
| 300 bots au hasard (médiane) | +11.2 % | — | -22.5 % | — | — | — | — |

Mieux que les 300 bots qui achètent au hasard (même gestion du risque) : bot 5 agents **48 %**, bot 7 agents **0 %**.
