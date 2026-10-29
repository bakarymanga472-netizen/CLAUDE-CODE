# S3 — Carry funding crypto (long spot + short perpétuel) — BTCUSDT, ETHUSDT

Généré le 2026-10-20 par `python3 -m carry.pilote`. Recherche historique uniquement : aucun ordre, aucune clé. Critères : `carry-criteres-v1-2026-10-20`. Aucun résultat n'est « validé » : au mieux « candidate démo ».

## 1. Données et qualité

- Funding : archives Binance USDT-M `data/futures/um/monthly/fundingRate` (CSV : `calc_time` ms UTC, `funding_interval_hours`, `last_funding_rate` = fraction par période de 8 h ; >0 : les longs paient les shorts). Premier mois disponible : 2020-01.
- Perp : klines 1d `data/futures/um/monthly/klines/<SYM>/1d` ; mark price 1d `markPriceKlines` (sensibilité liquidation). Spot : `labo.donnees.charger(sym, '1d')` (Binance spot).
- Les archives mensuelles s'arrêtent au dernier mois complet : le backtest finit avant le mois en cours.

| | BTCUSDT | ETHUSDT |
|---|---|---|
| Funding : début → fin | 2020-01-01 → 2026-09-30 16:00 | 2020-01-01 → 2026-09-30 16:00 |
| Paiements / attendus (8 h) | 7395 / 7395 | 7395 / 7395 |
| Trous / doublons / hors grille | 0 / 0 / 0 | 0 / 0 / 0 |
| Jours sans 3 paiements | 0 | 0 |
| Intervalles (h) | [8.0] | [8.0] |
| Taux min / max par 8 h | -0.300 % / 0.300 % | -0.356 % / 0.375 % |
| Paiements à |taux| ≥ 0,3 % (plafond) ; > 0,3 % | 2 ; 0 | 5 ; 5 |
| Aberrants (z > 10) | 0 | 0 |
| Part de paiements négatifs | 14.0 % | 13.8 % |
| Funding moyen annualisé (notionnel) | 11.7 % | 13.8 % |
| Perp 1d : barres manquantes | 0 | 0 |
| Mark price 1d : barres manquantes | 9 | 3 |
| Spot 1d : barres manquantes / doublons | 0 / 0 | 0 / 0 |
| Cadre du backtest | 2020-01-01 → 2026-09-29 (2464 j) | 2020-01-01 → 2026-09-29 (2464 j) |
| Empreintes funding / perp / spot | `6056d3342cdcf6ff` / `b40c82a4ec5389e1` / `b8ab886f48468540` / `814cf0543021ae48` | `b3ea37d0bee75236` / `5a294416971436ec` / `3250264d4c9cb191` / `3b49ff4ab020d9d8` |

**Contrôle croisé OKX** (API publique, historique court ≈ 3 mois) :

- BTCUSDT : 217 paiements communs (2026-07-20 → 2026-09-30), corrélation 0.52, même signe 90.8 %, annualisé Binance 6.4 % vs OKX 5.7 %.
- ETHUSDT : 217 paiements communs (2026-07-20 → 2026-09-30), corrélation 0.50, même signe 84.3 %, annualisé Binance 4.9 % vs OKX 4.7 %.

Les taux bornés à ±0,3 % sont les bornes réglementaires du funding Binance (pas des erreurs) : conservés.

**Base perp/spot à l'ouverture** (perp/spot − 1) :

- BTCUSDT : developpement moy. 0.000 % [min -0.79 %, max 0.29 %] ; validation moy. -0.027 % [min -0.07 %, max 0.09 %] ; controle moy. -0.031 % [min -0.10 %, max 0.12 %]
- ETHUSDT : developpement moy. 0.012 % [min -0.65 %, max 0.52 %] ; validation moy. -0.023 % [min -0.09 %, max 0.09 %] ; controle moy. -0.030 % [min -0.25 %, max 0.14 %]

**Funding brut moyen annualisé par année (notionnel, donnée de marché)** :

| Année | BTCUSDT | ETHUSDT |
|---|---|---|
| 2020 | 17.2 % | 27.4 % |
| 2021 | 30.6 % | 37.5 % |
| 2022 | 4.2 % | 0.8 % |
| 2023 | 7.9 % | 8.3 % |
| 2024 | 11.9 % | 13.0 % |
| 2025 | 5.1 % | 4.9 % |
| 2026 | 2.9 % | 1.9 % |

## 2. Méthode

- Position : 50 % du capital en spot long, 50 % en marge USDT sur un short perp de même notionnel (levier 1 sur la jambe short). Les rendements sont exprimés **sur le capital total** : un funding de 10 %/an sur le notionnel ≈ 5 %/an sur le capital.
- Funding du jour t = paiements de t 08:00, t 16:00, t+1 00:00 ; position ouverte/fermée à l'ouverture (00:00 UTC) du jour t aux prix d'ouverture spot ET perp (la base à l'entrée/sortie est dans le PnL).
- Décision du jour t : indicateur = moyenne des N derniers paiements STRICTEMENT antérieurs à t 00:00, ×3×365. Pas de look-ahead (testé).
- Coûts par jambe : spot 0.10 % + glissement 0.02 % ; perp 0.05 % + glissement 0.02 %. 4 jambes par aller-retour. Stress : commissions et glissement ×3.
- Rééquilibrage vérifié chaque jour, exécuté si une jambe s'écarte de plus de 5 % de sa cible (frais payés).
- Liquidation : chaque jour, si au plus haut perp du jour la marge tombe sous la marge de maintenance (0.4 %, hypothèse), la marge est perdue et le spot vendu.
- Position passive tenue jusqu'au bout : ses frais de sortie sont imputés au dernier jour de l'échantillon. Les trades d'une période = ceux qui la chevauchent.
- Approximation : funding calculé sur le notionnel au prix perp d'ouverture du jour (pas au mark exact de chaque paiement). La marge USDT ne rapporte rien.
- Référence sans risque : 0 %/an (HYPOTHÈSE, aucune série de taux chargée). Achat-conservation spot sur les mêmes jours.
- Périodes : développement 2020-01 → 2022-12, validation 2023, contrôle 2024-01 → fin des archives (ouvert une seule fois).

## 3. Grille déclarée avant tout test et critères annoncés

Grille (par symbole) : `passive`, `cond_N3_in10_out0`, `cond_N3_in20_out0`, `cond_N21_in10_out0`, `cond_N21_in20_out0` → **10 variantes au total** (N ∈ {3, 21} paiements, entrée ∈ {10 %, 20 %}/an annualisé sur le notionnel, sortie < 0 %).

Critères « candidate démo » (TOUS requis, fixés avant le lancement) :

1. Sélection : variante au meilleur Sharpe en DÉVELOPPEMENT, par symbole (5 variantes chacune).
2. Validation 2023 : rendement annualisé net > 0 % (sans risque supposé 0 %) et Sharpe ≥ 0,5.
3. Validation 2023 avec coûts ×3 : rendement annualisé net > 0 %.
4. Aucune liquidation de la jambe short (levier 1) sur toute la période simulée.
5. DSR (dev + validation, 10 variantes) ≥ 0,95.
6. Pire baisse dev + validation ≥ −20 %.
7. Contrôle 2024+ : rendement annualisé net > 0 % (sert uniquement à rejeter).

PBO (CSCV, 10 variantes, dev+val) : 0.06.

## 4. Résultats par période

### BTCUSDT

| Variante | Période | Rend. annuel | Vol | Sharpe | Pire baisse | Trades | Réussite | PF | Temps exposé | Funding encaissé* | Coûts* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| passive ★ | dév | 8.3 % | 0.9 % | 8.59 | -1.3 % | 1 | 100 % | n/d | 100 % | 29.5 % | 1.92 % |
| passive ★ | val | 3.7 % | 0.3 % | 13.94 | -0.0 % | 1 | 100 % | n/d | 100 % | 5.1 % | 0.29 % |
| passive ★ | contrôle | 3.3 % | 0.3 % | 11.20 | -0.3 % | 1 | 100 % | n/d | 100 % | 13.3 % | 1.25 % |
| cond_N3_in10_out0 | dév | 6.2 % | 1.0 % | 5.85 | -2.5 % | 35 | 34 % | 6.03 | 71 % | 28.7 % | 8.83 % |
| cond_N3_in10_out0 | val | 1.9 % | 0.4 % | 4.26 | -0.2 % | 8 | 75 % | 104.63 | 67 % | 4.0 % | 1.75 % |
| cond_N3_in10_out0 | contrôle | 2.4 % | 0.4 % | 6.51 | -0.4 % | 9 | 44 % | 19.30 | 58 % | 10.6 % | 2.64 % |
| cond_N3_in20_out0 | dév | 7.1 % | 0.9 % | 7.49 | -0.8 % | 7 | 86 % | 586.81 | 43 % | 24.9 % | 2.28 % |
| cond_N3_in20_out0 | val | 1.5 % | 0.3 % | 5.09 | -0.2 % | 3 | 100 % | n/d | 34 % | 2.5 % | 0.67 % |
| cond_N3_in20_out0 | contrôle | 1.9 % | 0.3 % | 6.89 | -0.1 % | 2 | 100 % | n/d | 29 % | 7.2 % | 0.70 % |
| cond_N21_in10_out0 | dév | 7.6 % | 0.9 % | 7.80 | -0.8 % | 7 | 57 % | 68.22 | 60 % | 27.2 % | 2.74 % |
| cond_N21_in10_out0 | val | 3.1 % | 0.3 % | 9.99 | -0.2 % | 2 | 100 % | n/d | 78 % | 4.5 % | 0.57 % |
| cond_N21_in10_out0 | contrôle | 2.4 % | 0.3 % | 7.78 | -0.2 % | 3 | 100 % | n/d | 51 % | 9.7 % | 1.25 % |
| cond_N21_in20_out0 | dév | 7.3 % | 0.9 % | 7.69 | -0.8 % | 4 | 100 % | n/d | 51 % | 25.3 % | 1.88 % |
| cond_N21_in20_out0 | val | 0.2 % | 0.1 % | 1.70 | -0.0 % | 1 | 100 % | n/d | 2 % | 0.4 % | 0.12 % |
| cond_N21_in20_out0 | contrôle | 1.8 % | 0.3 % | 6.62 | -0.2 % | 2 | 100 % | n/d | 37 % | 6.9 % | 0.86 % |

\* cumul sur la période, en fraction du capital initial de la période (somme simple). ★ = variante retenue (meilleur Sharpe en dév).

Achat-conservation BTCUSDT (spot) : dév 32.0 %/an, Sharpe 0.76, pire baisse -76.6 % ; val 156.4 %/an, Sharpe 2.35, pire baisse -20.0 % ; contrôle 28.2 %/an, Sharpe 0.76, pire baisse -53.0 %.

Retenue : `passive` — DSR dev+val 0.994 (Sharpe journalier max attendu par hasard 0.3111), pire baisse dev+val -1.3 %.

### ETHUSDT

| Variante | Période | Rend. annuel | Vol | Sharpe | Pire baisse | Trades | Réussite | PF | Temps exposé | Funding encaissé* | Coûts* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| passive ★ | dév | -5.6 % | 21.9 % | -0.11 | -37.9 % | 1 | 0 % | 0.00 | 100 % | 25.9 % | 2.14 % |
| passive ★ | val | 3.9 % | 0.3 % | 12.84 | -0.0 % | 1 | 0 % | 0.00 | 100 % | 3.5 % | 0.24 % |
| passive ★ | contrôle | 3.0 % | 0.3 % | 9.60 | -0.4 % | 1 | 0 % | 0.00 | 100 % | 8.8 % | 1.30 % |
| cond_N3_in10_out0 | dév | -6.7 % | 21.9 % | -0.17 | -38.0 % | 27 | 26 % | 0.73 | 74 % | 25.9 % | 5.32 % |
| cond_N3_in10_out0 | val | 2.4 % | 0.4 % | 5.27 | -0.5 % | 7 | 57 % | 22.26 | 74 % | 3.0 % | 1.10 % |
| cond_N3_in10_out0 | contrôle | 2.1 % | 0.4 % | 5.63 | -0.8 % | 10 | 40 % | 12.95 | 52 % | 6.9 % | 2.14 % |
| cond_N3_in20_out0 | dév | -6.0 % | 21.9 % | -0.14 | -37.9 % | 5 | 80 % | 0.75 | 51 % | 23.9 % | 1.61 % |
| cond_N3_in20_out0 | val | 1.7 % | 0.3 % | 5.42 | -0.2 % | 3 | 67 % | 395.67 | 36 % | 1.9 % | 0.48 % |
| cond_N3_in20_out0 | contrôle | 2.0 % | 0.3 % | 7.17 | -0.1 % | 2 | 100 % | n/d | 30 % | 5.2 % | 0.56 % |
| cond_N21_in10_out0 | dév | -5.7 % | 21.9 % | -0.12 | -38.0 % | 5 | 60 % | 0.81 | 66 % | 25.3 % | 2.14 % |
| cond_N21_in10_out0 | val | 3.1 % | 0.3 % | 9.18 | -0.2 % | 2 | 100 % | n/d | 78 % | 3.0 % | 0.42 % |
| cond_N21_in10_out0 | contrôle | 2.2 % | 0.3 % | 6.97 | -0.2 % | 4 | 100 % | n/d | 43 % | 6.3 % | 1.08 % |
| cond_N21_in20_out0 | dév | -6.0 % | 21.9 % | -0.14 | -38.0 % | 3 | 67 % | 0.78 | 55 % | 23.9 % | 1.61 % |
| cond_N21_in20_out0 | val | 1.0 % | 0.2 % | 5.05 | -0.1 % | 1 | 100 % | n/d | 13 % | 1.0 % | 0.11 % |
| cond_N21_in20_out0 | contrôle | 2.0 % | 0.3 % | 6.83 | -0.2 % | 2 | 100 % | n/d | 31 % | 5.1 % | 0.58 % |

\* cumul sur la période, en fraction du capital initial de la période (somme simple). ★ = variante retenue (meilleur Sharpe en dév).

Achat-conservation ETHUSDT (spot) : dév 110.1 %/an, Sharpe 1.26, pire baisse -79.3 % ; val 91.2 %/an, Sharpe 1.61, pire baisse -27.3 % ; contrôle 6.0 %/an, Sharpe 0.42, pire baisse -67.6 %.

Retenue : `passive` — DSR dev+val 0.000 (Sharpe journalier max attendu par hasard 0.3111), pire baisse dev+val -37.9 %.

## 5. Rendement net par année (coûts de base, toute la période)

Montre l'évolution du carry dans le temps. Les années de bord sont partielles (2026 jusqu'à la fin des archives).

**BTCUSDT**

| Variante | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| passive | 8.0 % | 15.8 % | 1.7 % | 3.7 % | 5.8 % | 2.3 % | 0.8 % |
| cond_N3_in10_out0 | 6.9 % | 14.6 % | -2.2 % | 1.9 % | 5.4 % | 0.7 % | 0.4 % |
| cond_N3_in20_out0 | 6.8 % | 14.8 % | 0.1 % | 1.5 % | 5.0 % | 0.3 % | 0.0 % |
| cond_N21_in10_out0 | 7.7 % | 15.7 % | -0.1 % | 3.1 % | 5.4 % | 1.2 % | 0.0 % |
| cond_N21_in20_out0 | 7.1 % | 15.1 % | 0.1 % | 0.2 % | 4.4 % | 0.5 % | 0.0 % |
| achat-conservation spot | 302.0 % | 59.8 % | -64.2 % | 155.6 % | 121.3 % | -6.3 % | -4.5 % |

**ETHUSDT**

| Variante | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| passive | -29.2 % | 19.5 % | -0.4 % | 3.8 % | 6.2 % | 1.9 % | 0.3 % |
| cond_N3_in10_out0 | -29.8 % | 18.2 % | -2.1 % | 2.3 % | 6.0 % | 0.1 % | -0.2 % |
| cond_N3_in20_out0 | -29.8 % | 18.1 % | 0.0 % | 1.7 % | 5.4 % | 0.3 % | 0.0 % |
| cond_N21_in10_out0 | -29.4 % | 18.7 % | -0.0 % | 3.1 % | 5.6 % | 0.5 % | 0.0 % |
| cond_N21_in20_out0 | -29.9 % | 18.4 % | 0.0 % | 1.0 % | 5.2 % | 0.3 % | 0.0 % |
| achat-conservation spot | 470.2 % | 399.2 % | -67.5 % | 90.8 % | 46.3 % | -11.0 % | -9.9 % |

## 6. Stress des coûts (×3)

| Symbole | Variante | Dév rend. / Sharpe | Val rend. / Sharpe | Contrôle rend. (retenue) |
|---|---|---|---|---|
| BTCUSDT | passive | 7.1 % / 7.08 | 3.3 % / 11.20 | 2.6 % |
| BTCUSDT | cond_N3_in10_out0 | 0.9 % / 0.57 | -1.0 % / -0.96 |  |
| BTCUSDT | cond_N3_in20_out0 | 5.6 % / 5.02 | 0.4 % / 0.66 |  |
| BTCUSDT | cond_N21_in10_out0 | 5.8 % / 5.05 | 2.2 % / 3.85 |  |
| BTCUSDT | cond_N21_in20_out0 | 6.1 % / 5.76 | 0.0 % / 0.14 |  |
| ETHUSDT | passive | -7.3 % / -0.19 | 3.3 % / 10.29 | 2.0 % |
| ETHUSDT | cond_N3_in10_out0 | -10.9 % / -0.37 | -0.4 % / -0.36 |  |
| ETHUSDT | cond_N3_in20_out0 | -7.4 % / -0.20 | 0.5 % / 0.82 |  |
| ETHUSDT | cond_N21_in10_out0 | -7.5 % / -0.20 | 2.1 % / 3.55 |  |
| ETHUSDT | cond_N21_in20_out0 | -7.4 % / -0.20 | 0.8 % / 2.44 |  |

## 7. Liquidation de la jambe short

Rééquilibrage quotidien à l'ouverture ; pire cas = plus haut perp du jour vs ouverture. Seuil = hausse qui épuise la marge (marge initiale 1/levier, maintenance 0,4 %, hypothèse).

| Symbole | Hausse intrajour max (date) | Levier 1 | Levier 2 | Levier 3 | Levier 5 | Liquidations dans la simulation retenue |
|---|---|---|---|---|---|---|
| BTCUSDT | 36.2 % (2021-07-26) | 0 j (seuil 99 %) | 0 j (seuil 49 %) | 1 j (seuil 33 %) | 4 j (seuil 20 %) | 0 |
| ETHUSDT | 202.0 % (2020-03-13) | 1 j (seuil 99 %) | 1 j (seuil 49 %) | 1 j (seuil 33 %) | 11 j (seuil 20 %) | 1 |

**Même calcul avec le plus haut du MARK PRICE** (archives `markPriceKlines`, prix qui déclenche réellement les liquidations) :

| Symbole | Hausse intrajour max (date) | Levier 1 | Levier 2 | Levier 3 | Levier 5 |
|---|---|---|---|---|---|
| BTCUSDT | 36.2 % (2021-07-26) | 0 j | 0 j | 1 j | 3 j |
| ETHUSDT | 30.9 % (2021-01-03) | 0 j | 0 j | 0 j | 10 j |

Jours sans barre mark dans les archives (repli conservateur sur le dernier prix perp) : BTCUSDT 9, ETHUSDT 3. Le 36,2 % BTC du 2021-07-26 est un tel repli (mèche du dernier prix perp à 48 168 ; plus haut spot 40 550, soit +14,6 %).

**Sensibilité POST-HOC** (ajoutée après avoir constaté la mèche du dernier prix ETH perp le 2020-03-13 : plus haut 323 contre ≈ 140 au spot et au mark) — variante retenue, liquidation contrôlée sur le mark price. Elle **ne modifie pas le statut**, fondé sur la règle déclarée :

- BTCUSDT : liquidations 0 ; dév 8.3 %/an (Sharpe 8.59), val 3.7 %/an, contrôle 3.3 %/an ; pire baisse dev+val -1.3 % ; DSR dev+val 0.994 ; par année : 2020 8.0 %, 2021 15.8 %, 2022 1.7 %, 2023 3.7 %, 2024 5.8 %, 2025 2.3 %, 2026 0.8 %.
- ETHUSDT : liquidations 0 ; dév 10.5 %/an (Sharpe 8.46), val 3.9 %/an, contrôle 3.0 %/an ; pire baisse dev+val -1.1 % ; DSR dev+val 0.999 ; par année : 2020 13.3 %, 2021 19.5 %, 2022 -0.4 %, 2023 3.8 %, 2024 6.2 %, 2025 1.9 %, 2026 0.3 %.

Limite : le mark price Binance (qui déclenche la liquidation) diffère du dernier prix des klines ; les mèches de dernier prix peuvent exagérer ou sous-estimer le risque. Le rééquilibrage suppose aussi un transfert spot → marge instantané.

## 8. Statut (critères annoncés avant le lancement)

- **BTCUSDT — candidate démo** (retenue `passive`) : rendement_val ✔, sharpe_val ✔, stress_val ✔, liquidations ✔, dsr ✔, pire_baisse_dev_val ✔, controle ✔. Contrôle ouvert le 2026-10-20T17:30:01+00:00 (DÉJÀ ouvert auparavant : résultat moins vierge).
- **ETHUSDT — non validée** (retenue `passive`) : rendement_val ✔, sharpe_val ✔, stress_val ✔, liquidations ✘, dsr ✘, pire_baisse_dev_val ✘, controle ✔. Contrôle ouvert le 2026-10-20T17:30:01+00:00 (DÉJÀ ouvert auparavant : résultat moins vierge).

« Candidate démo » signifie seulement : mérite un essai en démo/papier avec suivi ; ce n'est pas une validation.

## 9. Limites et risques non modélisés

- **Faillite / gel de plateforme** (FTX 2022) : spot et marge chez le même tiers ; perte possible de tout le capital. Non modélisé.
- **ADL (auto-deleveraging)** : la jambe short peut être réduite de force lors de liquidations en chaîne, laissant le spot non couvert. Non modélisé.
- **Changement de règles de funding** : formule, plafonds (±0,3 % observés), intervalle (8 h → 4 h/1 h sur certains contrats). Supposé stable.
- **Emprunt** : aucun emprunt modélisé (stratégie entièrement financée) ; une version à levier ajouterait coût d'emprunt et risque de rappel.
- Taux sans risque supposé à 0 % : en 2023-2025 un placement monétaire USD rapportait nettement plus ; la comparaison réelle est donc moins favorable.
- Funding payé au prix d'ouverture (approximation), marge non rémunérée, glissement fixe supposé, pas de carnet d'ordres, exécution simultanée parfaite des 2 jambes.
- Mark price ≠ dernier prix pour la liquidation ; frais de transfert et délais entre comptes spot/futures ignorés ; fiscalité ignorée.
- Survivant : BTC et ETH sont les deux contrats les plus liquides ; résultat non transposable aux altcoins.
- Le registre global `registre/` du labo n'a pas été modifié (consigne) : le registre de ces expériences est `carry/registre/`.
