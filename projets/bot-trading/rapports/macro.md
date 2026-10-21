# Stratégie « trader macro » par régimes (données jusqu'au 2026-10-20)

Commande : `python3 -m labo.macro` · règles fixées avant exécution : en-tête du fichier. Tout est hors échantillon (apprentissage sur le passé seulement).

**Réussite des positions** : 57% de 550 positions mensuelles gagnantes (gain moyen +6.3%, perte moyenne -4.6%).

| Version | 2011-2015 | 2016-2021 | 2022-2024 | 2025 → auj. | 5 ans | 2011 → auj. | Mois positifs | Pire mois | 5 000 € sur 5 ans |
|---|---|---|---|---|---|---|---|---|---|
| Macro ×1 | +1.7% / -19% | +43.4% / -20% | +13.9% / -30% | +4.5% / -22% | +8.4% / -37% | +18.7% / -37% | 55% | -14.4% | 7,491 € |
| Macro ×2 | -3.9% / -38% | +85.1% / -41% | +19.2% / -55% | -0.0% / -44% | +7.8% / -64% | +29.0% / -64% | 51% | -28.0% | 7,263 € |
| Macro ×5 | -30.0% / -87% | +186.0% / -81% | +11.0% / -90% | -31.2% / -84% | -15.5% / -95% | +30.1% / -95% | 48% | -61.8% | 2,152 € |
| SPY gardé | +12.5% / -19% | +17.3% / -34% | +8.9% / -24% | +17.6% / -19% | +12.8% / -24% | +14.1% / -34% | 69% | -12.5% | 9,123 € |

## Ce que chaque marché fait selon le régime (rendement mensuel moyen, 2003 → auj.)

| Régime | Mois | SPY | QQQ | IWM | EFA | EEM | TLT | IEF | GLD | DBC | UUP | BTC-USD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| taux ↓ dollar ↓ actions ↓ | 11 | +0.1% | +1.4% | -0.7% | -0.6% | -0.9% | +1.1% | +0.5% | +1.0% | -0.1% | -0.2% | +6.4% |
| taux ↓ dollar ↓ actions ↑ | 59 | +1.0% | +1.3% | +1.3% | +0.5% | +1.7% | +0.2% | +0.1% | +1.4% | +1.7% | +0.5% | +6.2% |
| taux ↓ dollar ↑ actions ↓ | 18 | +2.7% | +3.6% | +3.5% | +2.6% | +4.5% | +0.5% | +0.7% | +2.2% | +1.6% | -1.0% | +8.0% |
| taux ↓ dollar ↑ actions ↑ | 46 | +1.0% | +1.5% | +0.6% | +0.6% | +0.7% | +0.1% | +0.1% | +1.1% | -0.0% | +0.5% | +3.2% |
| taux ↑ dollar ↓ actions ↓ | 4 | +2.0% | +3.5% | +2.9% | +0.6% | -0.0% | +3.2% | +1.4% | +0.8% | +1.3% | +1.0% | +39.2% |
| taux ↑ dollar ↓ actions ↑ | 66 | +1.6% | +2.1% | +1.6% | +1.3% | +0.9% | +0.4% | +0.3% | -0.3% | +0.7% | -0.1% | +7.9% |
| taux ↑ dollar ↑ actions ↓ | 17 | -0.9% | -1.3% | -1.6% | -1.5% | -2.2% | +0.8% | +0.6% | +0.2% | -3.8% | +0.5% | -4.5% |
| taux ↑ dollar ↑ actions ↑ | 55 | +0.3% | +0.0% | -0.1% | +0.4% | +0.1% | +0.0% | +0.2% | +1.6% | +0.1% | +0.2% | +7.5% |

**Régime actuel (2026-10-20)** : taux ↑ dollar ↑ actions ↑ → positions : BTC-USD, GLD, EFA.
