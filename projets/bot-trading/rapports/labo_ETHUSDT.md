# Fiche instrument — ETHUSDT

Générée par `python3 -m labo.pilote ETHUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:34:25+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2017-08-17 → 2026-10-19 (9.2 ans) | 3351 | 0 | aucun | 0 | 0 | 1 | `3250264d4c9cb191` | oui |
| 4h | 2017-08-17 → 2026-10-20 (9.2 ans) | 20093 | 16 | 1 days 08:00:00 | 0 | 0 | 5 | `b6f9216d3d10dfaf` | oui |
| 1h | 2017-08-17 → 2026-10-20 (9.2 ans) | 80309 | 128 | 1 days 10:00:00 | 0 | 0 | 61 | `5b8dbe334bb01e30` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +103.8 % | -1.11 | 11.4 | -0.078 | 1.00 | 1.14 | -94.0 % |
| 4h | +102.8 % | -0.35 | 11.9 | -0.052 | 1.01 | 1.17 | -94.1 % |
| 1h | +108.1 % | -0.58 | 23.9 | -0.037 | 0.92 | 1.06 | -94.3 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur ETHUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.23**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 52 | +37.6 % | -41.2 % | 3.69 | +4.7 % | 1.38 | 1.06 | 0.81 | 1.26 | 4/5 | 0.01 | 0.00 | 0.59 | 0.77 | 81 % | 0.707 | stratégie non validée |
| tendance|4h | 137 | +47.3 % | -40.3 % | 3.79 | +2.5 % | 0.73 | 1.26 | 0.91 | 1.21 | 4/5 | 0.04 | 0.00 | 0.75 | 0.39 | 98 % | 0.411 | stratégie non validée |
| tendance|1h | 248 | +41.2 % | -39.1 % | 2.92 | +1.2 % | 0.34 | 1.15 | 0.63 | 1.17 | 4/5 | 0.02 | 0.00 | 0.66 | 0.65 | 98 % | 0.565 | stratégie non validée |
| cassure|1d | 13 | +29.0 % | -42.1 % | 5.83 | +16.1 % | 3.58 | 0.97 | 0.89 | 0.94 | 4/5 | 0.01 | 0.00 | 0.51 | 0.92 | 70 % | 0.767 | stratégie non validée |
| cassure|4h | 20 | +37.5 % | -34.2 % | 5.20 | +12.4 % | 3.09 | 1.13 | 1.06 | 1.10 | 4/5 | 0.02 | 0.00 | 0.65 | 0.64 | 91 % | 0.557 | stratégie non validée |
| cassure|1h | 26 | +39.0 % | -25.8 % | 5.15 | +9.6 % | 2.43 | 1.20 | 1.13 | 1.22 | 4/5 | 0.03 | 0.00 | 0.71 | 0.11 | 89 % | 0.484 | stratégie non validée |
| croisement_mm|1d | 20 | +37.7 % | -44.0 % | 6.36 | +18.6 % | 6.68 | 1.07 | 0.96 | 1.07 | 4/5 | 0.01 | 0.00 | 0.59 | 0.70 | 77 % | 0.694 | stratégie non validée |
| croisement_mm|4h | 20 | +40.5 % | -45.9 % | 6.99 | +22.0 % | 5.70 | 1.10 | 1.03 | 1.08 | 4/5 | 0.02 | 0.00 | 0.62 | 0.63 | 75 % | 0.644 | stratégie non validée |
| croisement_mm|1h | 20 | +37.9 % | -43.9 % | 6.56 | +19.2 % | 4.83 | 1.07 | 1.02 | 1.06 | 4/5 | 0.02 | 0.00 | 0.59 | 0.58 | 77 % | 0.688 | stratégie non validée |
| rebond_rsi|1d | 31 | +1.1 % | -16.9 % | 1.21 | +0.2 % | -0.11 | 0.15 | -0.22 | -0.19 | 3/5 | 0.00 | 0.00 | 0.04 | 1.00 | 50 % | 0.985 | stratégie non validée |
| rebond_rsi|4h | 307 | -5.3 % | -36.7 % | 0.87 | -0.1 % | -0.02 | -0.33 | -2.24 | -0.29 | 1/5 | 0.00 | 0.00 | 0.00 | 0.17 | 43 % | 1.000 | stratégie non validée |
| rebond_rsi|1h | 710 | -11.7 % | -50.4 % | 0.74 | -0.1 % | -0.03 | -1.11 | -5.16 | -1.20 | 1/5 | 0.00 | 0.00 | 0.00 | 0.02 | 67 % | 1.000 | stratégie non validée |
| selecteur_global | 67 | +36.8 % | -37.6 % | 3.84 | +4.0 % | 1.02 | 1.10 | 0.97 | 1.17 | 4/5 | 0.02 | 0.00 | 0.62 | 0.23 | 84 % | 0.594 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +77.0 % | -79.3 % | 1.10 |
| achat_conservation_vol_ciblee | +54.2 % | -56.2 % | 1.21 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 0.90 (180 j) | 1.77 (696 j) | -0.04 (56 j) | 0.65 (894 j) |
| tendance|4h | 0.87 (180 j) | 1.83 (696 j) | 0.57 (56 j) | 1.01 (894 j) |
| tendance|1h | 0.67 (180 j) | 1.73 (696 j) | 0.17 (56 j) | 0.93 (894 j) |
| cassure|1d | 0.80 (180 j) | 1.65 (696 j) | -0.31 (56 j) | 0.58 (894 j) |
| cassure|4h | 0.79 (180 j) | 1.44 (696 j) | 0.35 (56 j) | 1.15 (894 j) |
| cassure|1h | 0.74 (180 j) | 1.69 (696 j) | 3.06 (56 j) | 0.90 (894 j) |
| croisement_mm|1d | 0.73 (180 j) | 1.76 (696 j) | 0.09 (56 j) | 0.70 (894 j) |
| croisement_mm|4h | 0.84 (180 j) | 1.76 (696 j) | 1.07 (56 j) | 0.66 (894 j) |
| croisement_mm|1h | 0.70 (180 j) | 1.73 (696 j) | 0.64 (56 j) | 0.68 (894 j) |
| rebond_rsi|1d | 1.92 (180 j) | -0.07 (696 j) | -1.75 (56 j) | 0.63 (894 j) |
| rebond_rsi|4h | -3.45 (180 j) | 0.95 (696 j) | -0.21 (56 j) | -0.39 (894 j) |
| rebond_rsi|1h | 0.34 (180 j) | -2.25 (696 j) | -0.20 (56 j) | -0.40 (894 j) |
| selecteur_global | 0.63 (180 j) | 1.92 (696 j) | 3.06 (56 j) | 0.46 (894 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 30}|1d` | +19.6 % | -35.2 % | 0.71 |
| tendance|4h | `tendance|{"jours": 30}|4h` | +23.7 % | -38.6 % | 0.81 |
| tendance|1h | `tendance|{"jours": 30}|1h` | +20.0 % | -37.0 % | 0.72 |
| cassure|1d | `cassure|{"jours": 20}|1d` | -12.6 % | -55.2 % | -0.40 |
| cassure|4h | `cassure|{"jours": 20}|4h` | +4.7 % | -40.1 % | 0.31 |
| cassure|1h | `cassure|{"jours": 20}|1h` | +14.8 % | -35.4 % | 0.65 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +14.5 % | -36.0 % | 0.59 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +16.9 % | -36.8 % | 0.65 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +23.0 % | -34.4 % | 0.82 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 10}|1d` | -2.2 % | -17.7 % | -0.10 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -13.0 % | -35.2 % | -1.19 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -16.7 % | -40.2 % | -1.68 |
| selecteur_global | `cassure|{"jours": 20}|1h` | +14.8 % | -35.4 % | 0.65 |
| *achat_conservation* | — | +2.0 % | -67.6 % | 0.36 |
| *achat_conservation_vol_ciblee* | — | +8.4 % | -54.8 % | 0.40 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1d` ; choix walk-forward par année : 2019 → `{"jours": 90} 1d`, 2020 → `{"jours": 90} 1d`, 2021 → `{"jours": 90} 1d`, 2022 → `{"jours": 30} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : DSR 0.01 < 0.95; PBO 0.77 > 0.5; ne bat que 81 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 90} 4h`, 2020 → `{"jours": 90} 4h`, 2021 → `{"jours": 30} 4h`, 2022 → `{"jours": 30} 4h`, 2023 → `{"jours": 30} 4h`
- Raisons de rejet : DSR 0.04 < 0.95
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1h` ; choix walk-forward par année : 2019 → `{"jours": 90} 1h`, 2020 → `{"jours": 90} 1h`, 2021 → `{"jours": 30} 1h`, 2022 → `{"jours": 30} 1h`, 2023 → `{"jours": 30} 1h`
- Raisons de rejet : DSR 0.02 < 0.95; PBO 0.65 > 0.5
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 55} 1d`, 2020 → `{"jours": 55} 1d`, 2021 → `{"jours": 55} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 100} 1d`
- Raisons de rejet : DSR 0.01 < 0.95; PBO 0.92 > 0.5; 13 trades hors échantillon < 30; ne bat que 70 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|4h` ; choix walk-forward par année : 2019 → `{"jours": 55} 4h`, 2020 → `{"jours": 55} 4h`, 2021 → `{"jours": 55} 4h`, 2022 → `{"jours": 20} 4h`, 2023 → `{"jours": 20} 4h`
- Raisons de rejet : DSR 0.02 < 0.95; PBO 0.64 > 0.5; 20 trades hors échantillon < 30; ne bat que 91 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"jours": 55} 1h`, 2021 → `{"jours": 20} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 20} 1h`
- Raisons de rejet : DSR 0.03 < 0.95; 26 trades hors échantillon < 30; ne bat que 89 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 20, "long": 100} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : DSR 0.01 < 0.95; PBO 0.70 > 0.5; 20 trades hors échantillon < 30; ne bat que 77 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 4h`, 2020 → `{"court": 20, "long": 100} 4h`, 2021 → `{"court": 10, "long": 50} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : DSR 0.02 < 0.95; PBO 0.63 > 0.5; 20 trades hors échantillon < 30; ne bat que 75 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1h`, 2020 → `{"court": 20, "long": 100} 1h`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.02 < 0.95; PBO 0.58 > 0.5; 20 trades hors échantillon < 30; ne bat que 77 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 10}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 10} 1d`, 2022 → `{"seuil": 10} 1d`, 2023 → `{"seuil": 10} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.15 < 0.5; DSR 0.00 < 0.95; PBO 1.00 > 0.5; ne résiste pas aux coûts ×3; ne bat que 50 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 4h`, 2020 → `{"seuil": 20} 4h`, 2021 → `{"seuil": 10} 4h`, 2022 → `{"seuil": 5} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon -0.33 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 43 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1h`, 2020 → `{"seuil": 5} 1h`, 2021 → `{"seuil": 5} 1h`, 2022 → `{"seuil": 5} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon -1.11 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 67 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : range, forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"jours": 90} 1h`, 2021 → `{"jours": 20} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 20} 1h`
- Raisons de rejet : DSR 0.02 < 0.95; ne bat que 84 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
