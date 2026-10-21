# Rebond corrigé — SPY + GLD, séances réelles, exécution clôture suivante

Commande : `python3 -m labo.rebond` · règle figée {'seuil': 5, 'tp': 0.01, 'sl': 0.1, 'duree': 20} · données {'SPY': 'f9c84d7757bbfc4e', 'GLD': 'f7b66bafce3ae12a'} · critères `rebond-demo-v1-2026-10-21` (fixés avant exécution).

Corrige les anomalies d'audit 3 (trades ouverts), 4 (calendrier), 5 (exécution le jour du signal), 6 (séances supprimées), 7 (rendement de portefeuille réel) et 8 (GLD au lieu de GC=F).

| Période | Version | Trades | Réussite | Gain moy. | Perte moy. | Pire trade | PF | Rendement/an | Pire baisse | Sharpe | Exposition |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2008-2019 | base | 81 | +82.7 % | +1.7 % | -2.7 % | -9.8 % | 3.01 | +3.2 % | -7.1 % | 0.78 | 11% |
| 2008-2019 | couts_x3 | 81 | +82.7 % | +1.6 % | -2.8 % | -10.0 % | 2.68 | +2.8 % | -7.1 % | 0.68 | 11% |
| 2008-2019 | retard_1_seance | 81 | +75.3 % | +2.0 % | -2.4 % | -13.2 % | 2.48 | +3.0 % | -8.0 % | 0.74 | 11% |
| 2008-2019 | *SPY+GLD gardés 50/50* | — | — | — | — | — | — | +7.8 % | -32.5 % | 0.63 | 100 % |
| 2020-2024 | base | 39 | +79.5 % | +1.8 % | -2.3 % | -7.8 % | 3.04 | +3.9 % | -6.3 % | 0.80 | 12% |
| 2020-2024 | couts_x3 | 39 | +79.5 % | +1.7 % | -2.4 % | -8.0 % | 2.71 | +3.4 % | -6.3 % | 0.71 | 12% |
| 2020-2024 | retard_1_seance | 39 | +66.7 % | +2.1 % | -2.1 % | -12.0 % | 2.01 | +2.7 % | -7.4 % | 0.57 | 12% |
| 2020-2024 | *SPY+GLD gardés 50/50* | — | — | — | — | — | — | +13.6 % | -20.3 % | 0.98 | 100 % |
| 2025+ (déjà vu pendant la sélection) | base | 17 | +82.4 % | +1.8 % | -4.6 % | -7.8 % | 1.85 | +3.3 % | -5.9 % | 0.53 | 16% |
| 2025+ (déjà vu pendant la sélection) | couts_x3 | 17 | +82.4 % | +1.7 % | -4.8 % | -8.1 % | 1.64 | +2.5 % | -6.0 % | 0.42 | 16% |
| 2025+ (déjà vu pendant la sélection) | retard_1_seance | 17 | +58.8 % | +2.6 % | -2.0 % | -6.2 % | 1.81 | +3.2 % | -5.2 % | 0.56 | 16% |
| 2025+ (déjà vu pendant la sélection) | *SPY+GLD gardés 50/50* | — | — | — | — | — | — | +24.0 % | -12.9 % | 1.41 | 100 % |

**Entrées au hasard, mêmes sorties (2020+, 200 tirages)** : réussite médiane 77% (5e-95e : 68%-85%) ; la règle bat 72% des tirages en réussite et 79% en Sharpe.

**DSR 2020+** (1 662 variantes dans la lignée, variance nulle) : 0.06.

Positions encore ouvertes à la dernière clôture : {'SPY': False, 'GLD': False}.

## Statut : **non validée**

- Raisons : ne bat que 79% des entrées au hasard (Sharpe)
- Même « candidate démo », la règle ne doit pas aller en argent réel : 2025+ a été vu pendant la sélection, le rendement est faible face à SPY+GLD gardés, et le DSR de la lignée reste sous 0,95.
- Ne pas utiliser : si une donnée du jour manque, si le marché est fermé, si l'ordre MOC ne peut plus être passé (après 15 h 50 New York).
