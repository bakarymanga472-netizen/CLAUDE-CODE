# Plan d'investissement « Équilibrée » — version finale (2026-10-21)

Synthèse de 15 tours de recherche (plus de 1 000 variantes testées). Backtests frais inclus ; aucun argent réel engagé.
Détails : `rapports/` (combo3, fusion, strategie_finale, optim_pertes, x5_recherche, macro) et `contexte.md`.

## 0. Objectif et réalité

| | Valeur |
|---|---|
| Capital de départ | 5 000 € |
| Objectif | **500 € de gains par mois** |
| Rendement réaliste de la stratégie | ≈ +1,1 %/mois en moyenne (+14,8 %/an sur 5 ans), avec des mois négatifs |
| Capital nécessaire pour 500 €/mois en moyenne | **≈ 46 000 €** |
| Chemin | la stratégie fait travailler le capital, **l'épargne mensuelle le fait grossir** |

500 €/mois avec 5 000 € = +10 %/mois : aucun test ne l'a approché durablement (le meilleur fonds de l'histoire : ≈ +5 %/mois au mieux, avant frais).

## 1. Architecture (inchangée, validée)

```
Capital
├── 75 % — Bloc RENDEMENT (C3), à parts égales :
│   ├── Bot haute réussite : 50 % portefeuille de tendance + 50 % achat des replis D1F1 ×2 (40 ETF)
│   ├── Rotation : les 3 ETF les plus forts sur 12 mois (hors dernier mois), au-dessus de leur MM200
│   └── QQQ ×2 quand QQQ > sa MM200, sinon bons du Trésor
└── 25 % — Bloc STABILITÉ (poids ∝ 1/volatilité) :
    bot haute réussite · jour de décision Fed · saisonnalité Halloween · SPY MM50/MM200 · D1F1 ×2
```
Rééquilibrage chaque fin de mois (75 / 25 et poids internes). Levier global : **×1**.

## 2. Résultats attendus (backtest, rendement/an / pire baisse)

| Période | Équilibrée | SPY gardé |
|---|---|---|
| 2008-2015 | +9,4 % / -16 % | +6,5 % / -52 % |
| 2016-2021 | +16,6 % / -22 % | +17,3 % / -34 % |
| 2022-2024 | +11,7 % / -15 % | +8,9 % / -24 % |
| 2025 → 10/2026 | +20,8 % / -13 % | +17,6 % / -19 % |
| **5 ans** | **+14,8 % / -17 %** (Sharpe 1,14) | +12,8 % / -24 % (Sharpe 0,85) |

Réussite : 94 % des trades D1F1 gagnants ; ≈ 62 % de mois positifs. Durée des positions : D1F1 1 séance (médiane), QQQ ×2 ≈ 9 mois sur les gagnants, rotation ≥ 1 mois.

## 3. Plan d'épargne vers 500 €/mois

Simulation : 4 000 tirages des rendements mensuels réels de la stratégie (2008-2026), départ 5 000 €.

| Versement mensuel | 500 €/mois atteint en (médiane) | Cas lent (1 sur 10) | Cas rapide (1 sur 10) | Capital à 5 ans (médiane) |
|---|---|---|---|---|
| 0 € | 17,7 ans | 24 ans | 13 ans | 9 218 € |
| 200 € | 7,9 ans | 9,8 ans | 6,3 ans | 25 746 € |
| **300 € (recommandé)** | **6,3 ans** | 7,8 ans | 5,2 ans | 34 034 € |
| 500 € | 4,6 ans | 5,6 ans | 3,8 ans | 50 713 € |
| 750 € | 3,4 ans | 4,1 ans | 2,9 ans | 71 684 € |

Rejeu de l'historique réel (janvier 2016, 300 €/mois) : objectif atteint en juin 2021. Impôts (≈ 30 % en France, ou PEA/assurance-vie selon les supports) non modélisés.

## 4. Phases

| Phase | Durée | Ce qu'on fait | Critère pour passer à la suivante |
|---|---|---|---|
| 1. Démo (paper, Alpaca) | 3 mois minimum | Ordres simulés, journal quotidien, rapport mensuel | Écart avec le backtest raisonnable ; aucune erreur d'exécution ; tu tiens les règles |
| 2. Réel prudent | 6 mois | 50 % du capital investi, ×1 | Pire baisse réelle ≤ 20 % ; règles respectées |
| 3. Réel complet | ensuite | 100 % du capital, ×1, versement mensuel | Revue trimestrielle |
| (Option) levier | après 12 mois réels | ×1,25 maximum, via compte sur marge | Pire baisse réelle ≤ 17 % sur 12 mois ; jamais ×5 (ruine démontrée, tour 14) |

## 5. Règles de risque (non négociables)

1. **Levier** : ×1 ; ×1,25 au maximum après 12 mois ; **jamais de CFD** (financement destructeur, tour 4) ; jamais ×5.
2. **Disjoncteur de revue** : si le compte baisse de plus de 25 % depuis son plus haut (pire baisse backtest : -17 %), on **arrête les nouveaux achats et on analyse** avant de continuer — pas de vente de panique (tour 5 : vendre au creux coûte plus cher).
3. **Pas d'intervention manuelle** sur les signaux, même sur actualité choquante : les filtres « actualité » et « avant la Fed » ont été testés et rejetés (tours 5-6).
4. **Pas de nouveau moteur** ajouté sans test hors échantillon (le plafond observé, Sharpe ≈ 1,1-1,2, ne se dépasse pas en empilant des moteurs, tour 9).
5. **Aucun ordre réel sans « oui » explicite** (configuration `ask` sur les outils d'ordre Alpaca).

## 6. Routine

- **Chaque jour (après la clôture de New York)** : signaux D1F1 (achats, ventes limites), QQQ vs MM200, portefeuille de tendance ; ordres pour la clôture suivante.
- **Chaque fin de mois** : rotation, pondération 1/volatilité, retour à 75 / 25, versement mensuel investi.
- **Chaque mois** : rapport (gains, baisse, écart au backtest) ; tableau des régimes macro (`python3 -m labo.macro`) **pour comprendre le contexte, pas pour trader**.
- **Chaque trimestre** : revue des critères de phase.

## 7. Ce qui a été écarté (et pourquoi)

| Idée | Raison |
|---|---|
| 98 % de réussite comme objectif | Un perdant efface ~9 gagnants ; Medallion gagnait 50,75 % de ses trades |
| Levier ×4-×5 | 5 ans : 81-96 % de chances de perdre 50 % ; sélection réelle ×5 2011-2026 : +10,2 %/an, -60 % |
| CFD | Financement sur toute la position : moins bon que sans levier |
| Trading court terme (5 min à 1 h) | 288 essais, aucun validé ; frais et bruit |
| Filtres actualité / Fed / ventes de panique | Gains concentrés sur une année, pertes ailleurs |
| Corrections des pertes QQQ / rotation | Déplacent les pertes dans le temps sans les supprimer |
| Stratégie « macro » par régimes | 5 ans +8,4 %/an : utile pour comprendre, pas pour battre le marché |

## 8. Limites honnêtes

- Le bloc C3 a été conçu en ayant vu 2016-2026 ; la règle la plus stricte (tout choisir sur 2008-2015) n'a donné que +7,2 %/an. D'où le 75/25 et la phase démo.
- Non modélisés : impôts, appels de marge, frais réels du courtier, change EUR/USD.
- Un backtest n'est pas une garantie : seule la phase démo puis réel prudent le confirmera.
