# Décisions de la Fed (programmées) et trades perdants — données jusqu'au 2026-10-20

Commande : `python3 -m labo.evenements` · règles fixées avant exécution : en-tête du fichier.

## Autopsie (REF, 2008 → aujourd'hui)

- décision FOMC pendant le trade : perdants 49%, gagnants 6% ; réussite avec 68.4%, sans 96.8%.
- décision FOMC dans les 10 séances suivant l'entrée : perdants 31%, gagnants 29% ; réussite avec 93.8%, sans 94.5%.

## Filtres testés

| Variante | Période | Trades | Réussite | Perte moyenne | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|---|---|---|
| REF | 2008-2015 (choix) | 922 | 93.9% | -5.56% | +5.7% | -23% | 0.56 |
| REF | 2016-2021 (contrôle) | 766 | 94.1% | -3.94% | +6.9% | -10% | 0.73 |
| REF | 2022-2024 (test) | 362 | 93.1% | -5.74% | +5.6% | -11% | 0.81 |
| REF | 2025 → auj. (récent) | 286 | 95.8% | -4.27% | +15.6% | -10% | 1.38 |
| REF | 5 ans | 673 | 94.4% | -5.25% | +9.0% | -11% | 1.01 |
| F3 | 2008-2015 (choix) | 828 | 93.7% | -5.70% | +4.7% | -23% | 0.50 |
| F3 | 2016-2021 (contrôle) | 682 | 94.7% | -4.33% | +6.7% | -10% | 0.76 |
| F3 | 2022-2024 (test) | 354 | 93.2% | -5.64% | +6.0% | -11% | 0.88 |
| F3 | 2025 → auj. (récent) | 255 | 95.3% | -4.27% | +12.7% | -9% | 1.28 |
| F3 | 5 ans | 634 | 94.2% | -5.17% | +8.2% | -11% | 1.00 |
| F5 | 2008-2015 (choix) | 759 | 93.4% | -5.62% | +4.2% | -21% | 0.48 |
| F5 | 2016-2021 (contrôle) | 638 | 94.7% | -4.20% | +6.7% | -10% | 0.78 |
| F5 | 2022-2024 (test) | 320 | 94.1% | -5.45% | +7.8% | -9% | 1.26 |
| F5 | 2025 → auj. (récent) | 242 | 95.9% | -4.46% | +12.7% | -9% | 1.32 |
| F5 | 5 ans | 587 | 94.9% | -5.10% | +9.3% | -9% | 1.19 |
| F10 ← retenue | 2008-2015 (choix) | 603 | 93.5% | -5.34% | +4.0% | -15% | 0.60 |
| F10 ← retenue | 2016-2021 (contrôle) | 513 | 94.0% | -4.34% | +4.9% | -11% | 0.62 |
| F10 ← retenue | 2022-2024 (test) | 244 | 96.3% | -5.14% | +9.1% | -3% | 2.05 |
| F10 ← retenue | 2025 → auj. (récent) | 216 | 95.8% | -4.08% | +12.2% | -7% | 1.45 |
| F10 ← retenue | 5 ans | 483 | 96.1% | -4.62% | +9.9% | -7% | 1.51 |

Variante retenue par la règle : **F10**.
