# Comparaison avec TradingView

Colle chaque script `.pine` de ce dossier dans TradingView (Pine Editor → Add to chart → onglet Strategy Tester) et compare avec les chiffres ci-dessous, calculés par le moteur Python avec exactement les mêmes réglages. Capital 10 000 $, 100 % du capital par trade, pas de glissement.

Écarts NORMAUX à attendre : quelques trades en plus/moins au tout début (historique de chauffe), petites différences de prix entre le flux TradingView et l'API Binance, RSI légèrement différent sur les premières barres. Un écart important (signe du profit différent, nombre de trades très différent) = bug à investiguer d'un côté ou de l'autre.

| Script | Graphique | Réglage | Trades clôturés | Gagnants | Profit factor | Profit net (clôturés) | Pire baisse | Trade ouvert | Premier trade | Données jusqu'au |
|---|---|---|---|---|---|---|---|---|---|---|
| tendance.pine | BINANCE:BTCUSDT 1D | {'jours': 30} | 136 | 34.6% | 1.46 | +2567% | -74.2% | oui | 2017-10-05 | 2026-10-19 |
| tendance.pine | BINANCE:BTCUSDT 1D | {'jours': 90} | 59 | 32.2% | 2.03 | +941% | -66.7% | oui | 2017-11-16 | 2026-10-19 |
| tendance.pine | BINANCE:BTCUSDT 1D | {'jours': 180} | 28 | 42.9% | 2.65 | +654% | -64.9% | oui | 2018-02-14 | 2026-10-19 |
| cassure.pine | BINANCE:BTCUSDT 1D | {'jours': 20} | 44 | 47.7% | 1.71 | +2928% | -54.3% | non | 2017-10-09 | 2026-10-19 |
| cassure.pine | BINANCE:BTCUSDT 1D | {'jours': 55} | 18 | 55.6% | 3.27 | +1489% | -64.0% | oui | 2017-10-13 | 2026-10-19 |
| cassure.pine | BINANCE:BTCUSDT 1D | {'jours': 100} | 10 | 50.0% | 6.06 | +734% | -63.8% | oui | 2017-11-26 | 2026-10-19 |
| croisement_mm.pine | BINANCE:BTCUSDT 1D | {'court': 10, 'long': 50} | 40 | 40.0% | 1.87 | +2484% | -73.9% | oui | 2017-10-06 | 2026-10-19 |
| croisement_mm.pine | BINANCE:BTCUSDT 1D | {'court': 20, 'long': 100} | 17 | 47.1% | 1.91 | +847% | -69.9% | oui | 2017-11-25 | 2026-10-19 |
| croisement_mm.pine | BINANCE:BTCUSDT 1D | {'court': 50, 'long': 200} | 9 | 55.6% | 2.79 | +330% | -66.8% | oui | 2018-03-05 | 2026-10-19 |
| rebond.pine | AMEX:SPY 1D (ADJ) | {'seuil': 5, 'tp': 0.01, 'sl': 0.1, 'duree': 20} | 95 | 80.0% | 2.48 | +111% | -13.8% | non | 2003-06-25 | 2026-10-19 |
| rebond.pine | AMEX:GLD 1D (ADJ) | {'seuil': 5, 'tp': 0.01, 'sl': 0.1, 'duree': 20} | 68 | 82.4% | 2.20 | +68% | -15.4% | non | 2006-03-10 | 2026-10-19 |

## Ce que TradingView ne vérifie PAS

- Le surapprentissage : TradingView affiche un backtest, pas un DSR ni un test hors échantillon. Un bon résultat dans TradingView ne valide rien.
- Les coûts réels : ici commission fixe, sans spread ni glissement variable (le labo, lui, les inclut).
- Le ciblage de volatilité du labo : les scripts Pine investissent 100 % du capital, donc les rendements et les baisses sont plus forts que dans les fiches.

À me renvoyer : une capture de l'onglet « Performance Summary » et « List of Trades » pour chaque script, je compare ligne à ligne.
