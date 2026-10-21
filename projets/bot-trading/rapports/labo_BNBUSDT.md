# Fiche instrument — BNBUSDT

Générée par `python3 -m labo.pilote BNBUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:40:09+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2017-11-06 → 2026-10-19 (9.0 ans) | 3270 | 0 | aucun | 0 | 0 | 2 | `a4a615036271e3d8` | oui |
| 4h | 2017-11-06 → 2026-10-20 (9.0 ans) | 19608 | 16 | 1 days 08:00:00 | 0 | 0 | 12 | `73c5ebf8901a4ad9` | oui |
| 1h | 2017-11-06 → 2026-10-20 (9.0 ans) | 78372 | 122 | 1 days 10:00:00 | 0 | 0 | 52 | `e1d12619f8985a7f` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +123.0 % | 0.28 | 14.3 | -0.012 | 1.03 | 1.41 | -80.0 % |
| 4h | +119.4 % | 0.17 | 11.7 | -0.034 | 1.10 | 1.49 | -82.7 % |
| 1h | +128.0 % | 0.02 | 26.9 | -0.062 | 0.95 | 1.30 | -83.4 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur BNBUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.23**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 67 | +47.5 % | -40.8 % | 3.34 | +4.4 % | 1.04 | 1.27 | 0.96 | 1.34 | 4/5 | 0.08 | 0.00 | 0.76 | 0.52 | 100 % | 0.220 | stratégie non validée |
| tendance|4h | 163 | +45.5 % | -35.0 % | 2.89 | +1.8 % | 0.42 | 1.27 | 0.84 | 1.24 | 4/5 | 0.07 | 0.00 | 0.76 | 0.49 | 98 % | 0.209 | stratégie non validée |
| tendance|1h | 311 | +38.1 % | -38.8 % | 2.34 | +0.7 % | 0.18 | 1.16 | 0.47 | 1.11 | 4/5 | 0.04 | 0.00 | 0.68 | 0.47 | 100 % | 0.353 | stratégie non validée |
| cassure|1d | 23 | +32.8 % | -40.6 % | 5.49 | +14.3 % | 3.95 | 1.04 | 0.92 | 1.26 | 3/5 | 0.03 | 0.00 | 0.57 | 0.68 | 92 % | 0.481 | stratégie non validée |
| cassure|4h | 22 | +28.0 % | -34.5 % | 4.38 | +9.9 % | 2.66 | 0.94 | 0.87 | 0.91 | 4/5 | 0.01 | 0.00 | 0.48 | 0.86 | 74 % | 0.589 | stratégie non validée |
| cassure|1h | 26 | +38.5 % | -34.3 % | 8.13 | +16.3 % | 3.82 | 1.25 | 1.18 | 1.24 | 5/5 | 0.07 | 0.00 | 0.75 | 0.63 | 91 % | 0.255 | stratégie non validée |
| croisement_mm|1d | 20 | +48.6 % | -36.8 % | 7.48 | +20.2 % | 7.20 | 1.30 | 1.19 | 1.31 | 4/5 | 0.09 | 0.00 | 0.78 | 0.27 | 98 % | 0.190 | stratégie non validée |
| croisement_mm|4h | 19 | +56.1 % | -27.2 % | 9.27 | +22.5 % | 6.66 | 1.49 | 1.43 | 1.46 | 4/5 | 0.17 | 0.00 | 0.89 | 0.13 | 99 % | 0.064 | stratégie non validée |
| croisement_mm|1h | 19 | +61.0 % | -20.9 % | 11.66 | +23.7 % | 7.41 | 1.61 | 1.56 | 1.57 | 4/5 | 0.25 | 0.01 | 0.93 | 0.11 | 100 % | 0.029 | stratégie non validée |
| rebond_rsi|1d | 21 | +2.2 % | -9.2 % | 1.77 | +0.6 % | 0.16 | 0.32 | -0.05 | -0.18 | 3/5 | 0.00 | 0.00 | 0.07 | 0.67 | 75 % | 0.865 | stratégie non validée |
| rebond_rsi|4h | 293 | -9.0 % | -44.6 % | 0.76 | -0.1 % | -0.05 | -0.61 | -2.21 | -0.40 | 0/5 | 0.00 | 0.00 | 0.00 | 0.92 | 22 % | 1.000 | stratégie non validée |
| rebond_rsi|1h | 782 | -4.8 % | -34.1 % | 0.91 | -0.0 % | -0.01 | -0.41 | -4.68 | -1.05 | 2/5 | 0.00 | 0.00 | 0.00 | 0.00 | 100 % | 0.985 | stratégie non validée |
| selecteur_global | 37 | +40.2 % | -22.5 % | 4.74 | +8.0 % | 2.01 | 1.19 | 1.04 | 1.03 | 4/5 | 0.05 | 0.00 | 0.70 | 0.23 | 90 % | 0.287 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +119.7 % | -76.1 % | 1.29 |
| achat_conservation_vol_ciblee | +40.8 % | -56.9 % | 1.00 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 1.09 (218 j) | 1.02 (708 j) | 4.24 (73 j) | 1.17 (827 j) |
| tendance|4h | 1.15 (218 j) | 0.96 (708 j) | 4.28 (73 j) | 1.11 (827 j) |
| tendance|1h | 1.47 (218 j) | 0.86 (708 j) | 4.05 (73 j) | 0.84 (827 j) |
| cassure|1d | 1.24 (218 j) | 0.86 (708 j) | 4.06 (73 j) | 0.60 (827 j) |
| cassure|4h | 0.84 (218 j) | 0.98 (708 j) | 4.03 (73 j) | 0.30 (827 j) |
| cassure|1h | 0.66 (218 j) | 1.44 (708 j) | 4.08 (73 j) | 0.83 (827 j) |
| croisement_mm|1d | 0.98 (218 j) | 1.40 (708 j) | 4.08 (73 j) | 0.90 (827 j) |
| croisement_mm|4h | 1.21 (218 j) | 1.62 (708 j) | 3.81 (73 j) | 1.13 (827 j) |
| croisement_mm|1h | 1.29 (218 j) | 1.55 (708 j) | 4.15 (73 j) | 1.42 (827 j) |
| rebond_rsi|1d | 1.09 (218 j) | 0.33 (708 j) | 1.34 (73 j) | 0.18 (827 j) |
| rebond_rsi|4h | -0.20 (218 j) | -0.46 (708 j) | 3.66 (73 j) | -1.73 (827 j) |
| rebond_rsi|1h | 3.64 (218 j) | -1.53 (708 j) | 0.18 (73 j) | -0.55 (827 j) |
| selecteur_global | 0.60 (218 j) | 1.15 (708 j) | 4.15 (73 j) | 0.96 (827 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 30}|1d` | +34.4 % | -33.0 % | 1.05 |
| tendance|4h | `tendance|{"jours": 30}|4h` | +17.9 % | -45.5 % | 0.66 |
| tendance|1h | `tendance|{"jours": 30}|1h` | +2.7 % | -55.2 % | 0.25 |
| cassure|1d | `cassure|{"jours": 20}|1d` | +28.1 % | -30.7 % | 0.94 |
| cassure|4h | `cassure|{"jours": 20}|4h` | +6.4 % | -41.0 % | 0.36 |
| cassure|1h | `cassure|{"jours": 20}|1h` | +12.5 % | -36.2 % | 0.54 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +38.7 % | -33.4 % | 1.15 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +36.4 % | -34.7 % | 1.09 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +34.2 % | -35.3 % | 1.05 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | -2.3 % | -16.3 % | -0.20 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -13.2 % | -44.3 % | -1.02 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -20.9 % | -51.1 % | -2.26 |
| selecteur_global | `croisement_mm|{"court": 10, "long": 50}|1h` | +34.2 % | -35.3 % | 1.05 |
| *achat_conservation* | — | +35.1 % | -58.2 % | 0.83 |
| *achat_conservation_vol_ciblee* | — | +42.9 % | -44.8 % | 1.08 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 30} 1d`, 2022 → `{"jours": 30} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : DSR 0.08 < 0.95; PBO 0.52 > 0.5
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 30} 4h`, 2020 → `{"jours": 30} 4h`, 2021 → `{"jours": 30} 4h`, 2022 → `{"jours": 30} 4h`, 2023 → `{"jours": 30} 4h`
- Raisons de rejet : DSR 0.07 < 0.95
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1h` ; choix walk-forward par année : 2019 → `{"jours": 90} 1h`, 2020 → `{"jours": 30} 1h`, 2021 → `{"jours": 30} 1h`, 2022 → `{"jours": 30} 1h`, 2023 → `{"jours": 30} 1h`
- Raisons de rejet : DSR 0.04 < 0.95
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 55} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : DSR 0.03 < 0.95; PBO 0.68 > 0.5; 23 trades hors échantillon < 30; ne bat que 92 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|4h` ; choix walk-forward par année : 2019 → `{"jours": 20} 4h`, 2020 → `{"jours": 55} 4h`, 2021 → `{"jours": 55} 4h`, 2022 → `{"jours": 55} 4h`, 2023 → `{"jours": 20} 4h`
- Raisons de rejet : DSR 0.01 < 0.95; PBO 0.86 > 0.5; 22 trades hors échantillon < 30; ne bat que 74 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"jours": 100} 1h`, 2021 → `{"jours": 20} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 20} 1h`
- Raisons de rejet : DSR 0.07 < 0.95; PBO 0.63 > 0.5; 26 trades hors échantillon < 30; ne bat que 91 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : DSR 0.09 < 0.95; 20 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 4h`, 2020 → `{"court": 10, "long": 50} 4h`, 2021 → `{"court": 10, "long": 50} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : DSR 0.17 < 0.95; 19 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1h`, 2020 → `{"court": 10, "long": 50} 1h`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.25 < 0.95; 19 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 5} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.32 < 0.5; DSR 0.00 < 0.95; PBO 0.67 > 0.5; 21 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 75 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 20} 4h`, 2020 → `{"seuil": 10} 4h`, 2021 → `{"seuil": 10} 4h`, 2022 → `{"seuil": 10} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon -0.61 < 0.5; DSR 0.00 < 0.95; PBO 0.92 > 0.5; ne résiste pas aux coûts ×3; ne bat que 22 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 10} 1h`, 2020 → `{"seuil": 5} 1h`, 2021 → `{"seuil": 5} 1h`, 2022 → `{"seuil": 5} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon -0.41 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 4h`, 2020 → `{"jours": 30} 1d`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.05 < 0.95; ne bat que 90 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
