# Fiche instrument — BTCUSDT

Générée par `python3 -m labo.pilote BTCUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T02:41:36+00:00, DÉJÀ OUVERT avant cette exécution : ne prouve plus rien de neuf).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2017-08-17 → 2026-10-19 (9.2 ans) | 3351 | 0 | aucun | 0 | 0 | 1 | `b8ab886f48468540` | oui |
| 4h | 2017-08-17 → 2026-10-19 (9.2 ans) | 20089 | 16 | 1 days 08:00:00 | 0 | 0 | 8 | `25746113f8f021b1` | oui |
| 1h | 2017-08-17 → 2026-10-20 (9.2 ans) | 80294 | 128 | 1 days 10:00:00 | 0 | 0 | 63 | `9598ea31702fc234` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +82.0 % | -1.10 | 14.1 | -0.061 | 1.00 | 1.17 | -83.2 % |
| 4h | +83.7 % | -0.21 | 17.5 | -0.061 | 0.95 | 1.11 | -83.9 % |
| 1h | +89.2 % | -0.48 | 29.7 | -0.052 | 0.84 | 0.98 | -83.9 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur BTCUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.17**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 60 | +39.1 % | -60.1 % | 3.22 | +5.7 % | 2.59 | 1.13 | 0.82 | 0.99 | 4/5 | 0.00 | 0.00 | 0.64 | 0.37 | 91 % | 0.403 | stratégie non validée |
| tendance|4h | 100 | +52.9 % | -43.7 % | 4.17 | +3.8 % | 1.49 | 1.44 | 1.14 | 1.33 | 4/5 | 0.01 | 0.00 | 0.86 | 0.23 | 100 % | 0.091 | stratégie non validée |
| tendance|1h | 197 | +43.6 % | -48.5 % | 3.21 | +1.8 % | 0.64 | 1.25 | 0.77 | 1.28 | 4/5 | 0.00 | 0.00 | 0.74 | 0.37 | 100 % | 0.258 | stratégie non validée |
| cassure|1d | 23 | +45.0 % | -43.2 % | 4.51 | +12.6 % | 4.64 | 1.34 | 1.20 | 1.23 | 4/5 | 0.00 | 0.00 | 0.81 | 0.37 | 90 % | 0.237 | stratégie non validée |
| cassure|4h | 26 | +52.6 % | -27.4 % | 4.97 | +10.3 % | 3.50 | 1.56 | 1.47 | 1.52 | 4/5 | 0.01 | 0.00 | 0.92 | 0.87 | 98 % | 0.100 | stratégie non validée |
| cassure|1h | 20 | +23.9 % | -50.9 % | 3.51 | +10.7 % | 2.91 | 0.87 | 0.80 | 0.85 | 4/5 | 0.00 | 0.00 | 0.42 | 0.90 | 70 % | 0.713 | stratégie non validée |
| croisement_mm|1d | 20 | +49.4 % | -45.5 % | 5.90 | +16.2 % | 6.00 | 1.38 | 1.26 | 1.26 | 4/5 | 0.00 | 0.00 | 0.83 | 0.45 | 98 % | 0.172 | stratégie non validée |
| croisement_mm|4h | 18 | +39.8 % | -48.6 % | 4.43 | +17.2 % | 5.38 | 1.13 | 1.07 | 1.09 | 4/5 | 0.00 | 0.00 | 0.64 | 0.40 | 85 % | 0.376 | stratégie non validée |
| croisement_mm|1h | 18 | +41.5 % | -50.0 % | 4.54 | +17.6 % | 5.15 | 1.17 | 1.12 | 1.20 | 4/5 | 0.00 | 0.00 | 0.67 | 0.33 | 85 % | 0.320 | stratégie non validée |
| rebond_rsi|1d | 66 | +5.2 % | -23.2 % | 1.56 | +0.5 % | 0.10 | 0.44 | -0.32 | -0.02 | 2/5 | 0.00 | 0.00 | 0.12 | 0.62 | 75 % | 0.876 | stratégie non validée |
| rebond_rsi|4h | 284 | -20.3 % | -71.5 % | 0.49 | -0.4 % | -0.11 | -1.52 | -3.39 | -1.06 | 0/5 | 0.00 | 0.00 | 0.00 | 0.34 | 0 % | 1.000 | stratégie non validée |
| rebond_rsi|1h | 657 | -13.9 % | -54.5 % | 0.68 | -0.1 % | -0.04 | -1.25 | -5.13 | -1.82 | 0/5 | 0.00 | 0.00 | 0.00 | 0.00 | 76 % | 1.000 | stratégie non validée |
| selecteur_global | 23 | +49.6 % | -43.2 % | 4.67 | +13.4 % | 4.94 | 1.43 | 1.30 | 1.31 | 4/5 | 0.00 | 0.00 | 0.86 | 0.17 | 96 % | 0.164 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +62.8 % | -76.6 % | 1.06 |
| achat_conservation_vol_ciblee | +44.9 % | -64.1 % | 1.06 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 2.51 (284 j) | 0.17 (785 j) | 3.10 (79 j) | 1.27 (678 j) |
| tendance|4h | 2.49 (284 j) | 0.82 (785 j) | 2.66 (79 j) | 1.46 (678 j) |
| tendance|1h | 2.55 (284 j) | 0.69 (785 j) | 2.32 (79 j) | 1.01 (678 j) |
| cassure|1d | 2.57 (284 j) | 0.44 (785 j) | 3.94 (79 j) | 1.19 (678 j) |
| cassure|4h | 2.45 (284 j) | 1.04 (785 j) | 0.81 (79 j) | 1.73 (678 j) |
| cassure|1h | 2.62 (284 j) | 0.47 (785 j) | 0.90 (79 j) | -0.02 (678 j) |
| croisement_mm|1d | 2.60 (284 j) | 0.52 (785 j) | 3.66 (79 j) | 1.29 (678 j) |
| croisement_mm|4h | 2.62 (284 j) | 0.23 (785 j) | 3.51 (79 j) | 1.06 (678 j) |
| croisement_mm|1h | 2.64 (284 j) | 0.22 (785 j) | 3.85 (79 j) | 1.15 (678 j) |
| rebond_rsi|1d | 2.25 (284 j) | 0.03 (785 j) | 1.90 (79 j) | -0.02 (678 j) |
| rebond_rsi|4h | -1.87 (284 j) | -2.20 (785 j) | -0.02 (79 j) | 0.49 (678 j) |
| rebond_rsi|1h | -1.58 (284 j) | -1.68 (785 j) | 1.88 (79 j) | -0.79 (678 j) |
| selecteur_global | 2.61 (284 j) | 0.71 (785 j) | 3.94 (79 j) | 1.13 (678 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 30}|1d` | +8.7 % | -35.2 % | 0.43 |
| tendance|4h | `tendance|{"jours": 30}|4h` | +4.8 % | -37.1 % | 0.31 |
| tendance|1h | `tendance|{"jours": 30}|1h` | +1.9 % | -45.6 % | 0.21 |
| cassure|1d | `cassure|{"jours": 20}|1d` | +14.2 % | -35.1 % | 0.63 |
| cassure|4h | `cassure|{"jours": 20}|4h` | +21.1 % | -25.3 % | 0.85 |
| cassure|1h | `cassure|{"jours": 20}|1h` | +18.9 % | -30.8 % | 0.79 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +18.1 % | -33.5 % | 0.73 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +21.4 % | -35.0 % | 0.80 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +21.9 % | -34.7 % | 0.83 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 20}|1d` | -7.1 % | -29.0 % | -0.40 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -3.4 % | -18.3 % | -0.29 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -22.4 % | -51.9 % | -2.49 |
| selecteur_global | `tendance|{"jours": 30}|4h` | +4.8 % | -37.1 % | 0.31 |
| *achat_conservation* | — | +26.8 % | -53.0 % | 0.74 |
| *achat_conservation_vol_ciblee* | — | +25.5 % | -50.6 % | 0.77 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 90} 1d`, 2021 → `{"jours": 30} 1d`, 2022 → `{"jours": 30} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : DSR 0.00 < 0.95; ne bat que 91 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 90} 4h`, 2020 → `{"jours": 90} 4h`, 2021 → `{"jours": 30} 4h`, 2022 → `{"jours": 30} 4h`, 2023 → `{"jours": 30} 4h`
- Raisons de rejet : DSR 0.01 < 0.95
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1h` ; choix walk-forward par année : 2019 → `{"jours": 90} 1h`, 2020 → `{"jours": 90} 1h`, 2021 → `{"jours": 30} 1h`, 2022 → `{"jours": 30} 1h`, 2023 → `{"jours": 30} 1h`
- Raisons de rejet : DSR 0.00 < 0.95
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : DSR 0.00 < 0.95; 23 trades hors échantillon < 30; ne bat que 90 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|4h` ; choix walk-forward par année : 2019 → `{"jours": 20} 4h`, 2020 → `{"jours": 20} 4h`, 2021 → `{"jours": 20} 4h`, 2022 → `{"jours": 20} 4h`, 2023 → `{"jours": 20} 4h`
- Raisons de rejet : DSR 0.01 < 0.95; PBO 0.87 > 0.5; 26 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 100} 1h`, 2020 → `{"jours": 100} 1h`, 2021 → `{"jours": 20} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 100} 1h`
- Raisons de rejet : DSR 0.00 < 0.95; PBO 0.90 > 0.5; 20 trades hors échantillon < 30; ne bat que 70 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : DSR 0.00 < 0.95; 20 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 4h`, 2020 → `{"court": 20, "long": 100} 4h`, 2021 → `{"court": 10, "long": 50} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : DSR 0.00 < 0.95; 18 trades hors échantillon < 30; ne bat que 85 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1h`, 2020 → `{"court": 20, "long": 100} 1h`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.00 < 0.95; 18 trades hors échantillon < 30; ne bat que 85 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 20}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 20} 1d`, 2021 → `{"seuil": 20} 1d`, 2022 → `{"seuil": 20} 1d`, 2023 → `{"seuil": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.44 < 0.5; DSR 0.00 < 0.95; PBO 0.62 > 0.5; ne résiste pas aux coûts ×3; ne bat que 75 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 10} 4h`, 2020 → `{"seuil": 20} 4h`, 2021 → `{"seuil": 10} 4h`, 2022 → `{"seuil": 5} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon -1.52 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 0 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1h`, 2020 → `{"seuil": 5} 1h`, 2021 → `{"seuil": 5} 1h`, 2022 → `{"seuil": 5} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon -1.25 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 76 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 4h`
- Raisons de rejet : DSR 0.00 < 0.95; 23 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
