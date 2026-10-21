# Audit 03 — Aladdin momentum crypto

## 1. Reproduction et décomposition

- Walk-forward reproduit : +401.8 % (+22.3 %/an), pire baisse -33.2 %, Sharpe 1.37 (rapport : +401,8 %, +22,3 %/an, -33,2 %, 1,37).
- Coffre-fort reproduit (données au 2026-10-16, 2 jours de plus que le rapport) : +5.2 % (rapport : +5,5 % au 2026-10-14).
- Moteur d'audit identique à recherche.candidats : True
- Données crypto Binance : début 2020-01-01 (bot/data.py:31 `debut="2020-01-01"`) ; SOL dès 2020-08-11.

| Année WF | Structure choisie | Candidats évaluables (Sharpe fini) | dont crypto | Résultat |
|---|---|---|---|---|
| 2017 | moyennes 50/200 | multi-actifs | vol cible | 24/48 | 0/24 | +13.5 % |
| 2018 | moyennes 50/200 | multi-actifs | vol cible | 24/48 | 0/24 | -5.9 % |
| 2019 | moyennes 20/100 | multi-actifs | vol cible | 24/48 | 0/24 | +19.8 % |
| 2020 | moyennes 20/100 | multi-actifs | vol cible | 24/48 | 0/24 | +56.9 % |
| 2021 | moyennes 20/100 | multi-actifs | vol cible | 24/48 | 0/24 | +74.0 % |
| 2022 | moyennes 20/100 | multi-actifs | vol cible | 24/48 | 0/24 | -20.8 % |
| 2023 | momentum 250 j | crypto | vol cible | 48/48 | 24/24 | +28.2 % |
| 2024 | momentum 120 j | crypto | vol cible | 48/48 | 24/24 | +41.5 % |

→ Le walk-forward +22 %/an n'est PAS celui de la structure présentée : 6 années sur 8 viennent de moyennes mobiles multi-actifs. Années où une structure crypto a été choisie (2023-2024) : +81.5 % cumulé. La structure finale « momentum 120 j | crypto | vol cible » n'a été hors échantillon qu'en 2024 (WF) et 2025+ (coffre).

Résultat annuel de la structure finale : 2006 +0.0 %, 2007 +0.0 %, 2008 +0.0 %, 2009 +0.0 %, 2010 +0.0 %, 2011 +0.0 %, 2012 +0.0 %, 2013 +0.0 %, 2014 +0.0 %, 2015 +0.0 %, 2016 +0.0 %, 2017 +0.0 %, 2018 +0.0 %, 2019 +0.0 %, 2020 +67.6 %, 2021 +64.6 %, 2022 -8.6 %, 2023 +65.4 %, 2024 +41.5 %, 2025 +4.0 %, 2026 +1.1 %

BTC gardé : 2006 +0.0 %, 2007 +0.0 %, 2008 +0.0 %, 2009 +0.0 %, 2010 +0.0 %, 2011 +0.0 %, 2012 +0.0 %, 2013 +0.0 %, 2014 +0.0 %, 2015 +0.0 %, 2016 +0.0 %, 2017 +0.0 %, 2018 +0.0 %, 2019 +0.0 %, 2020 +301.7 %, 2021 +59.8 %, 2022 -64.2 %, 2023 +155.6 %, 2024 +121.3 %, 2025 -6.3 %, 2026 -6.9 %

## 2. Coûts et exécution

| Variante | ≤2024 /an | ≤2024 pire baisse | ≤2024 Sharpe | 2025+ total | 2025+ pire baisse | 2025+ Sharpe |
|---|---|---|---|---|---|---|
| Référence (frais 0,15 %/rotation, clôture 00:00 UTC) | +46.3 % | -22.6 % | 1.84 | +5.2 % | -17.1 % | 0.24 |
| Frais ×2 | +44.5 % | -23.1 % | 1.79 | +2.8 % | -17.7 % | 0.18 |
| Frais ×3 | +42.7 % | -23.7 % | 1.73 | +0.5 % | -18.4 % | 0.11 |
| Exécution 1 jour plus tard | +47.8 % | -23.1 % | 1.86 | +3.9 % | -16.7 % | 0.21 |
| Exécution 2 jours plus tard | +47.0 % | -24.1 % | 1.83 | +2.7 % | -17.5 % | 0.17 |

Rotation moyenne 2.6× le capital par an → frais annuels ≈ 0.39 % au tarif de base.

## 3. Paramètres voisins

| Variante | ≤2024 /an | ≤2024 pire baisse | ≤2024 Sharpe | 2025+ total | 2025+ pire baisse | 2025+ Sharpe |
|---|---|---|---|---|---|---|
| lookback 60 j | +37.7 % | -31.6 % | 1.52 | +18.1 % | -22.8 % | 0.57 |
| lookback 90 j | +33.2 % | -32.0 % | 1.45 | +2.9 % | -20.4 % | 0.18 |
| lookback 100 j | +33.3 % | -26.3 % | 1.50 | +0.5 % | -21.6 % | 0.11 |
| lookback 110 j | +43.1 % | -20.2 % | 1.76 | +0.7 % | -20.0 % | 0.12 |
| lookback 120 j | +46.3 % | -22.6 % | 1.84 | +5.2 % | -17.1 % | 0.24 |
| lookback 130 j | +48.0 % | -23.1 % | 1.90 | +3.3 % | -18.0 % | 0.19 |
| lookback 140 j | +44.6 % | -26.2 % | 1.76 | +2.4 % | -18.4 % | 0.17 |
| lookback 150 j | +40.0 % | -29.0 % | 1.61 | -3.5 % | -22.0 % | 0.00 |
| lookback 180 j | +39.8 % | -33.2 % | 1.56 | -1.4 % | -19.2 % | 0.06 |
| lookback 250 j | +43.1 % | -24.3 % | 1.71 | -14.0 % | -30.3 % | -0.37 |
| lookback 120, vol cible 10% | +29.5 % | -15.5 % | 1.84 | +4.2 % | -11.6 % | 0.24 |
| lookback 120, vol cible 20% | +64.1 % | -29.2 % | 1.84 | +4.6 % | -22.3 % | 0.23 |
| lookback 120, vol cible 30% | +93.5 % | -41.1 % | 1.79 | -4.4 % | -31.6 % | 0.09 |
| lookback 120, fenêtre vol 45 j | +46.4 % | -24.2 % | 1.85 | +4.9 % | -17.6 % | 0.23 |
| lookback 120, fenêtre vol 90 j | +43.5 % | -21.4 % | 1.79 | +3.5 % | -17.6 % | 0.20 |
| lookback 120, parts égales | +115.6 % | -54.1 % | 1.66 | -10.4 % | -34.2 % | 0.00 |

## 4. Univers (biais de survivance)

| Variante | ≤2024 /an | ≤2024 pire baisse | ≤2024 Sharpe | 2025+ total | 2025+ pire baisse | 2025+ Sharpe |
|---|---|---|---|---|---|---|
| sans BTC | +40.0 % | -20.2 % | 1.78 | +9.4 % | -15.4 % | 0.37 |
| sans ETH | +40.1 % | -21.5 % | 1.82 | +7.2 % | -15.5 % | 0.31 |
| sans BNB | +42.2 % | -20.4 % | 1.85 | -2.9 % | -17.4 % | -0.01 |
| sans SOL | +38.3 % | -24.3 % | 1.63 | +3.0 % | -16.3 % | 0.18 |
| sans XRP | +42.7 % | -18.5 % | 1.89 | +8.1 % | -17.4 % | 0.33 |
| BTC seul | +20.2 % | -13.8 % | 1.54 | -5.6 % | -10.0 % | -0.26 |
| ETH seul | +19.9 % | -8.7 % | 1.46 | -1.5 % | -11.7 % | -0.04 |
| BNB seul | +16.1 % | -16.4 % | 1.14 | +19.8 % | -9.5 % | 0.90 |
| SOL seul | +25.6 % | -10.8 % | 1.98 | +6.6 % | -10.8 % | 0.40 |
| XRP seul | +14.9 % | -23.3 % | 0.87 | -3.3 % | -16.7 % | -0.13 |
| 10 cryptos de bot/data.py (+ADA DOGE AVAX LINK DOT) | +58.0 % | -24.8 % | 1.84 | -4.3 % | -22.1 % | 0.02 |
| Point-dans-le-temps janv. 2020 (BTC, ETH, XRP, BCH, LTC, EOS, BNB, XTZ) | +33.1 % | -34.1 % | 1.22 | -13.0 % | -22.5 % | -0.26 |

(Univers point-dans-le-temps : capitalisations de janvier 2020 de mémoire d'auditeur — BSV exclu car retiré de Binance en 2019 ; LUNA/FTT non inclus faute de série propre : le symbole LUNAUSDT a été réattribué en 2022.)

## 5. Crises

| Fenêtre | Stratégie | Pire baisse stratégie | BTC gardé |
|---|---|---|---|
| Krach mars 2020 | +0.0 % | +0.0 % | -16.7 % |
| Mai-juil. 2021 | -5.8 % | -15.4 % | -28.1 % |
| LUNA mai 2022 | +0.0 % | +0.0 % | -47.0 % |
| Année 2022 | -8.6 % | -10.4 % | -64.2 % |
| FTX nov. 2022 | -5.2 % | -9.8 % | -16.2 % |

Pire jour de la stratégie : -7.7 % (2021-05-19) ; pire semaine glissante -11.3 %

## 6. Corrélation des positions et volatilité réalisée

- Corrélation moyenne des rendements quotidiens entre les 5 cryptos (2021+) : **0.61**
- desk_risque divise par √n (desks.py:55) comme si les actifs étaient indépendants ; vol réalisée de la stratégie 2021+ : 20.6 %/an (cible 15 %), 23.6 %/an les jours investis ; exposition brute moyenne 27 %, max 88 %

## 7. 5 % des jours retirés au hasard (50 tirages)

- Sharpe ≤2024 : médiane 1.92 [1.77 – 2.06] ; par an ≤2024 médiane +45.3 %
- Coffre 2025+ : médiane +1.4 % [-7.1 % – +7.2 %]

## 8. Bootstrap par blocs de 30 jours (rendements quotidiens 2020-03 → 2026-10 ; 5 000 tirages)

Hypothèse : le futur ressemble à 2020-2026 (un seul cycle crypto, haussier) ; blocs de 30 j pour garder l'autocorrélation.

- Horizon 1 an(s) : P(perte) = 11% ; pire baisse médiane -12.8 %, 5e centile -23.8 % ; P(baisse ≥ 30 %) = 0.9% ; P(baisse ≥ 50 %) = 0.00%
- Horizon 3 an(s) : P(perte) = 2% ; pire baisse médiane -18.6 %, 5e centile -30.9 % ; P(baisse ≥ 30 %) = 6.1% ; P(baisse ≥ 50 %) = 0.00%
- Mois perdants : 39% (31/80) ; pire mois -12.0 %

## 9. Deflated Sharpe Ratio (rendements quotidiens de la structure finale, période de sélection ≤ 2024)

Essais : 48 candidats de recherche.py (+ sélection walk-forward annuelle) ; variance des Sharpe quotidiens des 48 = 4.97e-04. Le projet a aussi testé auparavant bot/ (5-7 agents crypto) et l'or : N=100 est une borne plus honnête.

| Essais N | Sharpe annuel observé | Sharpe max attendu sous H0 | PSR(0) | DSR |
|---|---|---|---|---|
| 1 | 1.84 | 0.00 | 1.000 | **1.000** |
| 48 | 1.84 | 0.96 | 1.000 | **0.974** |
| 100 | 1.84 | 1.08 | 1.000 | **0.955** |

Coffre 2025+ seul : Sharpe annuel 0.24, PSR(Sharpe>0) = 0.63 (T = 654 jours).
