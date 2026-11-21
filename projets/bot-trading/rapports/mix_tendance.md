# Bot retenu : 50 % tendance + 50 % D1F1 élargi

Commande : `python3 -m labo.mix_tendance` · données jusqu'au 2026-10-20 · règles et historique : en-tête du fichier.

| Version | Période | Trades D1F1 | Réussite | Rendement/an | Pire baisse (quotidienne) | Sharpe | Mois positifs | Pire mois | Bat le SPY | Objectif |
|---|---|---|---|---|---|---|---|---|---|---|
| D1F1 ×1 | 2008-2015 (choix) | 922 | 94% | +6.3% | -10% | 0.95 | 62% | -4.3% | **non** | non |
| D1F1 ×1 | 2016-2021 (contrôle) | 766 | 94% | +9.7% | -11% | 1.22 | 60% | -5.9% | **non** | non |
| D1F1 ×1 | 2022-2024 (test) | 362 | 93% | +9.5% | -12% | 0.89 | 58% | -4.9% | oui | **ATTEINT** |
| D1F1 ×1 | 2025 → auj. (récent) | 286 | 96% | +13.3% | -7% | 1.80 | 82% | -4.7% | **non** | non |
| D1F1 ×2 | 2008-2015 (choix) | 922 | 94% | +7.8% | -10% | 1.05 | 64% | -4.6% | oui | **ATTEINT** |
| D1F1 ×2 | 2016-2021 (contrôle) | 766 | 94% | +11.2% | -12% | 1.29 | 64% | -7.8% | **non** | non |
| D1F1 ×2 | 2022-2024 (test) | 362 | 93% | +10.0% | -14% | 0.87 | 58% | -5.2% | oui | **ATTEINT** |
| D1F1 ×2 | 2025 → auj. (récent) | 286 | 96% | +16.3% | -9% | 1.90 | 82% | -5.9% | **non** | non |
| D1F1 ×3 | 2008-2015 (choix) | 922 | 94% | +9.1% | -14% | 1.04 | 66% | -5.3% | oui | **ATTEINT** |
| D1F1 ×3 | 2016-2021 (contrôle) | 766 | 94% | +12.6% | -13% | 1.31 | 65% | -9.8% | **non** | non |
| D1F1 ×3 | 2022-2024 (test) | 362 | 93% | +10.4% | -16% | 0.84 | 58% | -7.6% | oui | non |
| D1F1 ×3 | 2025 → auj. (récent) | 286 | 96% | +19.2% | -12% | 1.92 | 82% | -7.1% | oui | **ATTEINT** |
| SPY gardé | 2008-2015 (choix) | — | — | +6.5% | -52% | 0.47 | 60% | -16.5% | — | — |
| SPY gardé | 2016-2021 (contrôle) | — | — | +17.3% | -34% | 1.17 | 76% | -12.5% | — | — |
| SPY gardé | 2022-2024 (test) | — | — | +8.9% | -24% | 0.57 | 61% | -9.2% | — | — |
| SPY gardé | 2025 → auj. (récent) | — | — | +17.6% | -19% | 1.35 | 68% | -5.6% | — | — |

Jambe tendance : 9 instruments dont 6 cryptos (entrées après 400 jours d'historique), long seul, vol cible 20 %. Jambe D1F1 : 40 ETF, 10 positions, cash au taux du Trésor. Rééquilibrage 50/50 mensuel, sans frais de rééquilibrage.
