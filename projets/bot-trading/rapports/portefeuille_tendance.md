# Portefeuille de tendance multi-instruments

Commande : `python3 -m labo.portefeuille` · règle `portefeuille-tendance-v1-2026-10-21` fixée avant exécution (voir l'en-tête de `labo/portefeuille.py`).
Univers : BTCUSDT, ETHUSDT, BNBUSDT, XRPUSDT, LTCUSDT, SOLUSDT, GLD, SPY, TLT (entrée après 400 jours d'historique). Vol cible 20%, sans levier.

## developpement (≤2021)

| Variante | Rendement/an | Vol | Sharpe | Pire baisse | Années + |
|---|---|---|---|---|---|
| tendance (règle) | +16.7% | 13% | 1.27 | -20% | 4/5 |
| tendance coûts ×3 | +13.0% | 13% | 1.02 | -22% | 4/5 |
| tendance retard 1 jour | +18.1% | 13% | 1.36 | -18% | 4/5 |
| référence : toujours investi, même risque | +20.8% | 12% | 1.69 | -14% | 4/5 |
| sensibilité : crypto seulement | +14.6% | 17% | 0.90 | -35% | 3/5 |
| sensibilité : + FX long/short (swap NON modélisé) | -5.1% | 5% | -0.97 | -27% | 1/5 |
| référence : parts égales achetées-gardées | +79.5% | 54% | 1.36 | -66% | 4/5 |

## validation 2022-2023

| Variante | Rendement/an | Vol | Sharpe | Pire baisse | Années + |
|---|---|---|---|---|---|
| tendance (règle) | +4.6% | 18% | 0.34 | -22% | 1/2 |
| tendance coûts ×3 | -5.0% | 18% | -0.19 | -35% | 1/2 |
| tendance retard 1 jour | +8.2% | 18% | 0.52 | -19% | 1/2 |
| référence : toujours investi, même risque | +4.0% | 14% | 0.35 | -23% | 1/2 |
| sensibilité : crypto seulement | +4.3% | 17% | 0.33 | -20% | 1/2 |
| sensibilité : + FX long/short (swap NON modélisé) | +2.7% | 8% | 0.38 | -13% | 2/2 |
| référence : parts égales achetées-gardées | -4.6% | 45% | 0.12 | -56% | 1/2 |

## hors échantillon WF 2019-2023

| Variante | Rendement/an | Vol | Sharpe | Pire baisse | Années + |
|---|---|---|---|---|---|
| tendance (règle) | +19.2% | 16% | 1.16 | -29% | 4/5 |
| tendance coûts ×3 | +12.1% | 16% | 0.79 | -41% | 4/5 |
| tendance retard 1 jour | +21.5% | 16% | 1.27 | -24% | 4/5 |
| référence : toujours investi, même risque | +19.6% | 14% | 1.35 | -27% | 4/5 |
| sensibilité : crypto seulement | +16.1% | 19% | 0.88 | -35% | 4/5 |
| sensibilité : + FX long/short (swap NON modélisé) | -3.9% | 6% | -0.58 | -26% | 2/5 |
| référence : parts égales achetées-gardées | +68.9% | 53% | 1.25 | -64% | 4/5 |

## 2024 → aujourd'hui (déjà vu instrument par instrument)

| Variante | Rendement/an | Vol | Sharpe | Pire baisse | Années + |
|---|---|---|---|---|---|
| tendance (règle) | +22.0% | 15% | 1.40 | -10% | 3/3 |
| tendance coûts ×3 | +16.0% | 15% | 1.06 | -11% | 3/3 |
| tendance retard 1 jour | +24.7% | 16% | 1.49 | -13% | 3/3 |
| référence : toujours investi, même risque | +20.4% | 22% | 0.96 | -26% | 2/3 |
| sensibilité : crypto seulement | +10.1% | 18% | 0.63 | -20% | 3/3 |
| sensibilité : + FX long/short (swap NON modélisé) | +1.1% | 8% | 0.19 | -10% | 2/3 |
| référence : parts égales achetées-gardées | +23.3% | 38% | 0.74 | -45% | 2/3 |

- DSR (variance nulle, 253 essais cumulés sur l'univers) : 0.41
- p (tendance meilleure que « toujours investi, même risque ») : 2019-2023 0.684 · 2024+ 0.087

## Statut : **non validée**

- Raisons : DSR 0.41 < 0,95 avec 253 essais
- Données 2024+ déjà vues instrument par instrument dans les fiches : ce n'est pas un test vierge. Seul le suivi papier futur le sera.
- Biais de survivance : les cryptos de l'univers sont celles qui existent encore aujourd'hui (LUNA, FTT absentes).
