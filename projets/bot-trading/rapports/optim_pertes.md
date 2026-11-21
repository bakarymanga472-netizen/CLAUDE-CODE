# Optimisation par les pertes — moteur QQQ ×2 (données jusqu'au 2026-10-20)

Commande : `python3 -m labo.optim_pertes` · règles : en-tête du fichier.

## Moteur QQQ ×2 seul (rendement/an / pire baisse)

| Variante | 2008-2015 (choix) | 2016-2021 | 2022-2024 | 2025 → auj. | 5 ans | Passages perdants (2008+) |
|---|---|---|---|---|---|---|
| Sans correctif ← choisie | +12.6% / -38% | +33.9% / -41% | +15.3% / -43% | +24.5% / -23% | +20.4% / -43% | — |
| B1 bande ±1% | +7.9% / -44% | +31.5% / -45% | +29.0% / -26% | +19.5% / -26% | +26.9% / -26% | — |
| B2 bande ±2% | +12.0% / -43% | +32.2% / -41% | +23.2% / -33% | +13.4% / -26% | +21.1% / -34% | — |
| B3 bande ±3% | +12.1% / -39% | +36.1% / -46% | +23.2% / -33% | +10.0% / -26% | +19.8% / -34% | — |
| N3 confirmation 3 jours | +12.1% / -42% | +34.6% / -35% | +20.0% / -31% | +22.9% / -23% | +22.7% / -32% | — |
| N5 confirmation 5 jours | +11.2% / -42% | +37.0% / -35% | +19.2% / -33% | +18.0% / -23% | +20.5% / -34% | — |

## Stratégie Équilibrée : avant / après (moteur Sans correctif)

| Version | 2008-2015 (choix) | 2016-2021 | 2022-2024 | 2025 → auj. | 5 ans | Sharpe 5 ans | 20 000 € (5 ans) | Ruine 5 ans |
|---|---|---|---|---|---|---|---|---|
| Équilibrée actuelle | +9.4% / -16% | +16.6% / -22% | +11.7% / -15% | +20.8% / -13% | +14.8% / -17% | 1.14 | 39,913 € | 0% |
| Équilibrée + Sans correctif | +9.4% / -16% | +16.6% / -22% | +11.7% / -15% | +20.8% / -13% | +14.8% / -17% | 1.14 | 39,913 € | 0% |
| SPY gardé | +6.5% / -52% | +17.3% / -34% | +8.9% / -24% | +17.6% / -19% | +12.8% / -24% | 0.85 | 36,492 € | 3% |

## Rotation (R2) — autopsie et correctifs (fixés avant ; choix Calmar 2008-2015)

78 mois perdants sur 226 ; pires mois : 2011-09 -18,8 %, 2026-03 -12,1 %, 2010-05/06 -10,7 %, 2026-06 -10,4 %, 2022-06 -10,2 %, 2008-07/09 -10,1 %, 2018-10 -10,0 % — des retournements brutaux du marché en cours de mois.

| Variante | 2008-2015 | 2016-2021 | 2022-2024 | 2025 → auj. | 5 ans |
|---|---|---|---|---|---|
| R2 actuel | +7,2 % / -34 % | +13,2 % / -31 % | +10,8 % / -34 % | +34,3 % / -23 % | +17,1 % / -34 % |
| S stop MM200 en cours de mois ← choisie | +8,6 % / -26 % | +14,7 % / -20 % | +6,3 % / -35 % | +30,4 % / -23 % | +13,2 % / -35 % |
| X momentum 3/6/12 mois | +5,1 % / -32 % | +5,6 % / -37 % | +8,5 % / -33 % | +45,2 % / -22 % | +18,6 % / -33 % |
| SX les deux | +4,4 % / -29 % | +6,4 % / -30 % | +4,6 % / -33 % | +38,9 % / -22 % | +14,2 % / -33 % |

Équilibrée avec S : 5 ans +13,9 %/an, -17 %, Sharpe 1,09 (actuelle : +14,8 %, -17 %, 1,14) — mieux avant 2022, moins bien depuis. Non adopté.
