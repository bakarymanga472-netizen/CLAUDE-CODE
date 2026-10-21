# Stratégie finale « Équilibrée » — synthèse de 10 tours de recherche (2026-10-21)

**But** : meilleurs rendements que le marché (SPY) tout en perdant moins que lui. Backtests frais inclus, aucun argent réel.
Résultats détaillés : `rapports/combo3.md`, `rapports/fusion.md`, `rapports/strategie_finale.md`. Historique : `contexte.md`.

## 1. Architecture

```
Capital
├── 75 % — Bloc RENDEMENT (C3, labo/combo3.py), à parts égales :
│   ├── Bot haute réussite : 50 % portefeuille de tendance + 50 % achat des replis D1F1 ×2 sur 40 ETF
│   ├── Rotation : les 3 ETF les plus forts sur 12 mois (hors dernier mois), au-dessus de leur MM200
│   └── QQQ ×2 quand QQQ > sa MM200, sinon bons du Trésor
└── 25 % — Bloc STABILITÉ (labo/strategie_finale.py, moteurs choisis sur 2008-2015, poids ∝ 1/volatilité) :
    ├── Bot haute réussite        ├── Jour de décision de la Fed (SPY)
    ├── Saisonnalité Halloween     ├── SPY si MM50 > MM200, sinon obligations IEF
    └── D1F1 ×2
```
Rééquilibrage : chaque fin de mois, retour à 75 / 25 et aux poids internes.

## 2. Ce qu'on a gardé, et pourquoi (les bons côtés)

| Élément | Apport mesuré |
|---|---|
| Achat des replis D1F1 (RSI-2 < 5, vente limite +1 %) | 93-97 % de trades gagnants, pertes faibles hors chocs |
| Portefeuille de tendance | Rendement régulier, peu corrélé aux actions |
| Rotation momentum | Capte les secteurs/pays qui s'envolent (2025+ : +34 %/an seul) |
| QQQ ×2 au-dessus de la MM200 | Moteur de gros gains, sort du marché dans les grandes baisses |
| Combinaison de moteurs qui ne perdent pas en même temps | Pire baisse divisée par ~2 à rendement égal |
| Levier via courtier sur marge, modéré | Transforme la régularité en rendement |

## 3. Ce qu'on a écarté, et pourquoi (les mauvais côtés)

| Élément | Raison (preuve) |
|---|---|
| Chercher 98 % de réussite | Mauvais indicateur : un perdant efface ~9 gagnants (tours 1-2) |
| Levier via CFD | Financement sur toute la position : moins bon que sans levier (tour 4) |
| Vendre au premier choc d'actualité | Vend au creux, rate le rebond : plus de perdants (tour 5) |
| Filtre « pas d'achat avant la Fed » | Gain concentré sur 2022, moins bon 3 périodes sur 4 (tour 6) |
| QQQ ×2 ou ×3 seul | Pire baisse -43 % à -59 % (tour 7) |
| Fusionner 15 moteurs sans tri | Dilue le rendement (+7 à +10 %/an) (tour 9) |
| Tendance obligations, rotation pays | Perdants ou faibles depuis 2022 (tour 9) |
| Volatilité cible automatique | Coûts d'emprunt + retard : Sharpe 0,65 (tour 9) |

## 4. Résultats (rendement/an / pire baisse)

| Profil | 2008-2015 | 2016-2021 | 2022-2024 | 2025 → auj. | **5 ans** | 20 000 € (5 ans) |
|---|---|---|---|---|---|---|
| Dynamique (100 % C3) | +10,2 % / -21 % | +20,2 % / -26 % | +13,2 % / -19 % | +26,2 % / -16 % | +17,6 % / -22 % | 44 922 € |
| **Équilibrée (75 / 25) ← retenue** | **+9,4 % / -16 %** | **+16,6 % / -22 %** | **+11,7 % / -15 %** | **+20,8 % / -13 %** | **+14,8 % / -17 %** | **39 913 €** |
| Prudente (50 / 50) | +8,6 % / -11 % | +12,9 % / -17 % | +10,0 % / -11 % | +15,6 % / -10 % | +12,0 % / -12 % | 35 288 € |
| SPY gardé | +6,5 % / -52 % | +17,3 % / -34 % | +8,9 % / -24 % | +17,6 % / -19 % | +12,8 % / -24 % | 36 492 € |

Équilibrée : plus de rendement ET moins de baisse que le SPY sur 3 périodes sur 4 et sur 5 ans ; en 2016-2021 rendement légèrement inférieur (+16,6 % vs +17,3 %) mais baisse bien plus faible (-22 % vs -34 %). Sharpe 5 ans 1,14 (SPY 0,85). Gain moyen ≈ 1,15 %/mois (20 000 € → ≈ 230 €/mois la 1re année, avant impôts).

## 5. Règles d'exploitation

1. Décisions à la clôture, ordres exécutés à la clôture suivante (aucune information future).
2. Fin de mois : recalcul de la rotation, de la pondération 1/volatilité, retour à 75 / 25.
3. Chaque jour : signaux D1F1 (entrées, ventes limites), QQQ vs MM200, portefeuille de tendance.
4. Levier : uniquement via compte sur marge (jamais CFD) ; QQQ ×2 via marge ou ETF ×2 (QLD).
5. Pas de vente de panique : les règles de sortie sont celles du système, rien d'autre.
6. Paper trading 3 mois minimum avant tout argent réel ; aucun ordre réel sans « oui » explicite.

## 6. Limites honnêtes

- Le bloc C3 a été conçu en ayant déjà vu 2016-2026 : une partie de son avance peut venir de ce regard en arrière.
- La règle la plus stricte (tout choisir sur 2008-2015) a donné +7,2 %/an seulement : les moteurs qui brillaient avant 2015 se sont essoufflés. C'est la raison du mélange 75/25 plutôt qu'un pari unique.
- Non modélisés : impôts (≈ 30 % en France), appels de marge, frais réels du courtier, change EUR/USD.
- Le plafond observé (Sharpe ≈ 1,1-1,2) ne sera pas dépassé en ajoutant des moteurs publics ; il faut plus de capital pour plus d'euros.
