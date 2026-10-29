# Boucle d'amélioration — BTCUSDT (pilote)

Commandes : `python3 -m amelioration.boucle declarer`, `tester`, `rapport`. Règle de décision : `decision-v1-2026-10-20` (fixée avant les tests, `amelioration/boucle.py`). Données distinctes : ETHUSDT, LTCUSDT, XRPUSDT, BNBUSDT.

**Version stable** : `BTC-tendance-1d-v1` — non validée (voir rapports/labo_BTCUSDT.md) — référence de simulation seulement.

## Hypothèses et verdicts

| Id | Problème documenté | Énoncé | Verdict | Raisons | Δ Sharpe portefeuille distinct | p corrigée | Δ Sharpe coûts ×3 | Voisins (Δ Sharpe) | Pire baisse combinée stable → candidate | Empreinte |
|---|---|---|---|---|---|---|---|---|---|---|
| H-001 | Sharpe de la tendance 1d faible en régime « range » (0,17 sur 785 j, rapports/labo_BTCUSDT.md §5) | Ne pas être exposé quand le régime connu est « range » améliore le rapport rendement/risque. | **rejetée** | amélioration non significative (p corrigée 0.935); améliore seulement 1/4 instruments distincts; ne résiste pas aux coûts ×3; au moins un paramètre voisin n'améliore pas (résultat fragile) | -0.34 | 0.935 | -0.49 | -0.30, -0.43 | -45% → -37% | `238fe354e320ac8c` |
| H-002 | Pire baisse hors échantillon de -60 % pour la tendance 1d (rapports/labo_BTCUSDT.md §4) | Un stop suiveur à 3 écarts-types journaliers sous le plus haut depuis l'entrée réduit la pire baisse sans détruire le rendement. | **rejetée** | amélioration non significative (p corrigée 1.000); améliore seulement 1/4 instruments distincts; ne résiste pas aux coûts ×3; au moins un paramètre voisin n'améliore pas (résultat fragile) | -0.24 | 1.000 | -0.42 | -0.33, +0.01 | -45% → -39% | `0a498033c430cde1` |
| H-003 | Le walk-forward choisit souvent 30 jours plutôt que 90 (choix par année, rapports/labo_BTCUSDT.md §7) | Un lookback de 30 jours fait mieux que 90 jours. | **rejetée** | amélioration non significative (p corrigée 1.000); ne résiste pas aux coûts ×3 | +0.09 | 1.000 | -0.18 | +0.06, +0.14 | -45% → -34% | `637ebe9ed537aaf5` |

## Détail par instrument distinct (Sharpe stable → candidate)

| Hypothèse | ETHUSDT | LTCUSDT | XRPUSDT | BNBUSDT | BTC dév. | BTC valid. | BTC récent |
|---|---|---|---|---|---|---|---|
| H-001 | 0.82 → 0.34 | 0.47 → 0.16 | -0.08 → -0.03 | 0.92 → 0.60 | 0.96 → 1.08 | 0.14 → 0.90 | 0.86 → 0.61 |
| H-002 | 0.82 → 0.39 | 0.47 → 0.22 | -0.08 → 0.36 | 0.92 → 0.04 | 0.96 → 0.66 | 0.14 → 0.31 | 0.86 → -0.28 |
| H-003 | 0.82 → 1.00 | 0.47 → 0.04 | -0.08 → 0.30 | 0.92 → 1.13 | 0.96 → 1.49 | 0.14 → 0.83 | 0.86 → 0.43 |

## Versions

- Stable : `BTC-tendance-1d-v1`
- `BTC-tendance-1d-v1+H-001` : rejetée
- `BTC-tendance-1d-v1+H-002` : rejetée
- `BTC-tendance-1d-v1+H-003` : rejetée

## Surveillance de la version stable (seuils `amelioration/seuils.json`, fixés avant les tests)

- Sharpe glissant 1 an : -0.90 · baisse en cours : -22%
- Alertes : Sharpe glissant 1 an -0.90 < 0.0; dérive des données « r » (PSI 0.37); dérive des données « amplitude » (PSI 1.59)

## Détecteurs de changement — évaluation historique (BTC 1d)

Un détecteur n'est utile que si l'état annoncé se confirme sur les 30 jours suivants plus souvent que le taux de base.

| Détecteur | Événements | Taux de confirmation | Taux de base | p-valeur | Lecture |
|---|---|---|---|---|---|
| hausse_volatilite | 3 | 100% | 28% | 0.022 | indéterminé : moins de 20 événements |
| tendance_vers_range | 87 | 70% | 62% | 0.084 | pas mieux que le hasard |
| hausse_couts_proxy | 4 | 100% | 53% | 0.081 | indéterminé : moins de 20 événements |
| baisse_liquidite | 4 | 100% | 36% | 0.016 | indéterminé : moins de 20 événements |
| deterioration_esperance | 8 | 50% | 47% | 0.569 | indéterminé : moins de 20 événements |

## Limites

- Les instruments « distincts » sont des cryptos encore cotées aujourd'hui (biais de survivance) et très corrélées à BTC : ce n'est pas une indépendance parfaite.
- Correction des tests multiples : borne de Bonferroni sur le nombre cumulé d'hypothèses testées (conservatrice).
- Toutes les données BTC jusqu'à aujourd'hui ont déjà été vues : seules les données FUTURES (suivi papier) seront réellement vierges.
