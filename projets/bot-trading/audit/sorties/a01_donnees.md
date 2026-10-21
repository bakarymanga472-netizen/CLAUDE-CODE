# Audit 01 — données

Index prix() : 2006-01-03 → 2026-10-16, 7592 jours calendaires.

| Actif | 1re date valide | Dernière | NaN internes | Jours à variation nulle | Plus forte hausse | Plus forte baisse |
|---|---|---|---|---|---|---|
| BTC | 2020-01-01 | 2026-10-16 | 0 | 0 (0 %) | +19.5 % (2021-02-08) | -39.5 % (2020-03-12) |
| ETH | 2020-01-01 | 2026-10-16 | 0 | 0 (0 %) | +26.3 % (2021-05-24) | -44.6 % (2020-03-12) |
| BNB | 2020-01-01 | 2026-10-16 | 0 | 7 (0 %) | +70.3 % (2021-02-19) | -44.1 % (2020-03-12) |
| SOL | 2020-08-11 | 2026-10-16 | 0 | 4 (0 %) | +45.9 % (2020-09-09) | -42.2 % (2022-11-09) |
| XRP | 2020-01-01 | 2026-10-16 | 0 | 7 (0 %) | +73.1 % (2023-07-13) | -41.6 % (2020-12-23) |
| OR | 2006-01-03 | 2026-10-16 | 0 | 2387 (31 %) | +9.0 % (2008-09-17) | -10.8 % (2026-01-30) |
| ACTIONS | 2006-01-03 | 2026-10-16 | 0 | 2375 (31 %) | +14.5 % (2008-10-13) | -10.9 % (2020-03-16) |
| OBLIGATIONS | 2006-01-03 | 2026-10-16 | 0 | 2385 (31 %) | +7.5 % (2020-03-20) | -6.7 % (2020-03-17) |

## Fichiers bruts de data/

- BTCUSDT : 2481 lignes, doublons 0, jours manquants 0, bougies à volume nul 0
- ETHUSDT : 2481 lignes, doublons 0, jours manquants 0, bougies à volume nul 0
- BNBUSDT : 2481 lignes, doublons 0, jours manquants 0, bougies à volume nul 0
- SOLUSDT : 2258 lignes, doublons 0, jours manquants 0, bougies à volume nul 0
- XRPUSDT : 2481 lignes, doublons 0, jours manquants 0, bougies à volume nul 0
- yahoo_SPY : 5230 séances, doublons 0, jours ouvrés absents 194 (fériés US ≈ 9-10/an attendus), séances à variation exactement nulle 13
- yahoo_GC_F : 5230 séances, doublons 0, jours ouvrés absents 194 (fériés US ≈ 9-10/an attendus), séances à variation exactement nulle 25
- yahoo_TLT : 5230 séances, doublons 0, jours ouvrés absents 194 (fériés US ≈ 9-10/an attendus), séances à variation exactement nulle 23

## enquete.py:78 — `c.diff().ne(0)` retire aussi de VRAIES séances sans variation

- ACTIONS : 5230 séances Yahoo, 5217 gardées, **13 vraies séances supprimées** (ex. 2007-12-19, 2010-08-31, 2012-07-30, 2012-10-31, 2013-03-27)
- OR : 5230 séances Yahoo, 5205 gardées, **25 vraies séances supprimées** (ex. 2006-02-22, 2006-06-26, 2006-09-04, 2006-11-24, 2007-01-02)

## GC=F (future continu) vs GLD (ETF réellement traité par alpaca.py)

- Corrélation quotidienne GC=F/GLD : 0.886 ; écart-type de l'écart quotidien 0.56 % ; 313 jours avec écart > 1 % (sur 5224)
- Rendement cumulé 2006-01-04→2026-10-16 : GC=F +681.4 %, GLD +623.5 %
- Les 5 plus gros écarts GC=F − GLD : 2008-09-18 +8.6 %, 2008-09-19 +7.4 %, 2009-03-19 +6.5 %, 2009-03-18 +6.4 %, 2013-09-19 +4.9 %

## reussite.py:46/61 — exécution « clôture suivante » qui tombe un jour reporté (= clôture du signal)

- ACTIONS : 161 trades ; entrée sur un jour reporté (achat au cours du signal) : **13** ; sortie sur un jour reporté (vente au cours du déclenchement) : **30**
- OR : 124 trades ; entrée sur un jour reporté (achat au cours du signal) : **8** ; sortie sur un jour reporté (vente au cours du déclenchement) : **27**
- Ce moteur est celui de `live_rebond.py:29` (via reussite.portefeuille), PAS celui qui a produit 84/78/79 % (enquete.executer).
- Dans reussite.py, `rolling(200)` = 200 jours calendaires (≈ 138 séances) et `duree` = jours calendaires, alors que sorties.py/enquete.py comptent en séances : deux règles différentes portent le même nom.
