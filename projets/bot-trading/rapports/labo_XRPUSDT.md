# Fiche instrument — XRPUSDT

Générée par `python3 -m labo.pilote XRPUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:45:22+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2018-05-04 → 2026-10-19 (8.5 ans) | 3091 | 0 | aucun | 0 | 0 | 3 | `7f30dd5921f9874e` | oui |
| 4h | 2018-05-04 → 2026-10-20 (8.5 ans) | 18539 | 9 | 0 days 12:00:00 | 0 | 0 | 12 | `2945a12e0a5589fc` | oui |
| 1h | 2018-05-04 → 2026-10-20 (8.5 ans) | 74105 | 88 | 0 days 11:00:00 | 0 | 0 | 82 | `12efd1074cc87ffb` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +116.7 % | 0.06 | 14.3 | -0.036 | 1.00 | 1.04 | -85.0 % |
| 4h | +110.3 % | -0.23 | 20.3 | -0.005 | 1.11 | 1.15 | -85.8 % |
| 1h | +119.1 % | -0.13 | 35.6 | -0.046 | 0.95 | 0.99 | -87.2 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur XRPUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.38**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 59 | -2.1 % | -65.6 % | 1.16 | +0.5 % | -0.08 | 0.10 | -0.22 | 0.44 | 2/5 | 0.00 | 0.00 | 0.03 | 0.78 | 25 % | 0.962 | stratégie non validée |
| tendance|4h | 167 | +11.1 % | -43.7 % | 1.51 | +0.5 % | 0.11 | 0.48 | 0.02 | 0.28 | 2/5 | 0.03 | 0.00 | 0.13 | 0.64 | 69 % | 0.791 | stratégie non validée |
| tendance|1h | 322 | +7.9 % | -39.2 % | 1.36 | +0.2 % | 0.05 | 0.40 | -0.30 | 0.49 | 2/5 | 0.02 | 0.00 | 0.10 | 0.74 | 82 % | 0.836 | stratégie non validée |
| cassure|1d | 18 | -0.2 % | -42.3 % | 1.93 | +4.8 % | 0.71 | 0.14 | 0.04 | -0.04 | 1/5 | 0.00 | 0.00 | 0.03 | 0.94 | 28 % | 0.957 | stratégie non validée |
| cassure|4h | 30 | +12.0 % | -46.6 % | 1.82 | +3.1 % | 0.70 | 0.50 | 0.41 | 0.37 | 2/5 | 0.03 | 0.00 | 0.14 | 0.48 | 60 % | 0.784 | stratégie non validée |
| cassure|1h | 31 | +6.9 % | -40.9 % | 1.56 | +2.1 % | 0.33 | 0.36 | 0.29 | 0.39 | 3/5 | 0.02 | 0.00 | 0.09 | 0.65 | 45 % | 0.890 | stratégie non validée |
| croisement_mm|1d | 18 | +3.0 % | -54.1 % | 1.63 | +3.6 % | 0.73 | 0.25 | 0.14 | 0.19 | 2/5 | 0.01 | 0.00 | 0.05 | 0.81 | 28 % | 0.937 | stratégie non validée |
| croisement_mm|4h | 18 | +1.2 % | -51.5 % | 1.52 | +2.6 % | 0.63 | 0.20 | 0.14 | 0.11 | 2/5 | 0.01 | 0.00 | 0.04 | 0.64 | 28 % | 0.953 | stratégie non validée |
| croisement_mm|1h | 18 | +2.7 % | -47.9 % | 1.57 | +3.0 % | 0.76 | 0.24 | 0.19 | 0.21 | 2/5 | 0.01 | 0.00 | 0.05 | 0.56 | 30 % | 0.933 | stratégie non validée |
| rebond_rsi|1d | 14 | +1.4 % | -12.4 % | 1.70 | +0.5 % | 0.18 | 0.23 | -0.02 | 0.16 | 4/5 | 0.01 | 0.00 | 0.06 | 0.26 | 67 % | 0.845 | stratégie non validée |
| rebond_rsi|4h | 152 | -12.0 % | -49.1 % | 0.49 | -0.4 % | -0.12 | -1.04 | -2.04 | -0.82 | 0/5 | 0.00 | 0.00 | 0.00 | 0.14 | 5 % | 1.000 | stratégie non validée |
| rebond_rsi|1h | 502 | -5.4 % | -34.8 % | 0.83 | -0.1 % | -0.02 | -0.51 | -3.21 | -1.16 | 1/5 | 0.00 | 0.00 | 0.00 | 0.06 | 92 % | 0.994 | stratégie non validée |
| selecteur_global | 71 | -10.9 % | -50.9 % | 0.71 | -0.6 % | -0.20 | -0.27 | -0.48 | -0.26 | 2/5 | 0.00 | 0.00 | 0.00 | 0.38 | 6 % | 1.000 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +12.0 % | -83.2 % | 0.62 |
| achat_conservation_vol_ciblee | +34.2 % | -52.6 % | 0.76 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 0.06 (74 j) | 1.21 (379 j) | -0.71 (156 j) | -0.26 (1217 j) |
| tendance|4h | 0.06 (74 j) | 0.77 (379 j) | -0.02 (156 j) | 0.60 (1217 j) |
| tendance|1h | 0.12 (74 j) | 0.45 (379 j) | 0.22 (156 j) | 0.51 (1217 j) |
| cassure|1d | -0.10 (74 j) | 0.01 (379 j) | -0.24 (156 j) | 0.38 (1217 j) |
| cassure|4h | -0.34 (74 j) | 1.04 (379 j) | 0.67 (156 j) | 0.41 (1217 j) |
| cassure|1h | -0.35 (74 j) | 1.19 (379 j) | -0.27 (156 j) | 0.32 (1217 j) |
| croisement_mm|1d | 0.96 (74 j) | 0.19 (379 j) | -0.64 (156 j) | 0.38 (1217 j) |
| croisement_mm|4h | 0.75 (74 j) | 0.30 (379 j) | -0.47 (156 j) | 0.27 (1217 j) |
| croisement_mm|1h | 0.82 (74 j) | 0.32 (379 j) | -0.32 (156 j) | 0.30 (1217 j) |
| rebond_rsi|1d | 0.00 (74 j) | 0.74 (379 j) | -1.16 (156 j) | 0.73 (1217 j) |
| rebond_rsi|4h | -2.80 (74 j) | -1.52 (379 j) | -1.99 (156 j) | -0.35 (1217 j) |
| rebond_rsi|1h | 1.20 (74 j) | -1.01 (379 j) | 0.66 (156 j) | -0.78 (1217 j) |
| selecteur_global | -2.88 (74 j) | 0.05 (379 j) | -1.90 (156 j) | 0.20 (1217 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 180}|1d` | +6.5 % | -41.6 % | 0.35 |
| tendance|4h | `tendance|{"jours": 30}|4h` | +2.8 % | -49.5 % | 0.24 |
| tendance|1h | `tendance|{"jours": 30}|1h` | -5.5 % | -59.4 % | -0.02 |
| cassure|1d | `cassure|{"jours": 20}|1d` | +23.5 % | -32.8 % | 0.83 |
| cassure|4h | `cassure|{"jours": 20}|4h` | +27.4 % | -31.4 % | 0.95 |
| cassure|1h | `cassure|{"jours": 20}|1h` | +35.9 % | -27.5 % | 1.22 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +8.8 % | -47.3 % | 0.42 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +4.1 % | -44.5 % | 0.28 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +6.1 % | -43.0 % | 0.35 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | +9.5 % | -7.2 % | 0.82 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -10.9 % | -34.5 % | -0.98 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -4.4 % | -22.6 % | -0.38 |
| selecteur_global | `cassure|{"jours": 20}|1h` | +35.9 % | -27.5 % | 1.22 |
| *achat_conservation* | — | +30.9 % | -72.0 % | 0.72 |
| *achat_conservation_vol_ciblee* | — | +26.7 % | -58.3 % | 0.73 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 180}|1d` ; choix walk-forward par année : 2019 → `{"jours": 180} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 180} 1d`, 2022 → `{"jours": 180} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.10 < 0.5; DSR 0.00 < 0.95; PBO 0.78 > 0.5; ne résiste pas aux coûts ×3; ne bat que 25 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 180} 4h`, 2020 → `{"jours": 30} 4h`, 2021 → `{"jours": 30} 4h`, 2022 → `{"jours": 30} 4h`, 2023 → `{"jours": 30} 4h`
- Raisons de rejet : Sharpe hors échantillon 0.48 < 0.5; DSR 0.03 < 0.95; PBO 0.64 > 0.5; ne bat que 69 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1h` ; choix walk-forward par année : 2019 → `{"jours": 180} 1h`, 2020 → `{"jours": 30} 1h`, 2021 → `{"jours": 30} 1h`, 2022 → `{"jours": 30} 1h`, 2023 → `{"jours": 30} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.40 < 0.5; DSR 0.02 < 0.95; PBO 0.74 > 0.5; ne résiste pas aux coûts ×3; ne bat que 82 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 100} 1d`, 2020 → `{"jours": 100} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.14 < 0.5; DSR 0.00 < 0.95; PBO 0.94 > 0.5; 18 trades hors échantillon < 30; ne bat que 28 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|4h` ; choix walk-forward par année : 2019 → `{"jours": 20} 4h`, 2020 → `{"jours": 20} 4h`, 2021 → `{"jours": 20} 4h`, 2022 → `{"jours": 20} 4h`, 2023 → `{"jours": 20} 4h`
- Raisons de rejet : DSR 0.03 < 0.95; ne bat que 60 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"jours": 20} 1h`, 2021 → `{"jours": 55} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 20} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.36 < 0.5; DSR 0.02 < 0.95; PBO 0.65 > 0.5; ne bat que 45 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 50, "long": 200} 1d`, 2020 → `{"court": 50, "long": 200} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.25 < 0.5; DSR 0.01 < 0.95; PBO 0.81 > 0.5; 18 trades hors échantillon < 30; ne bat que 28 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 50, "long": 200} 4h`, 2020 → `{"court": 50, "long": 200} 4h`, 2021 → `{"court": 10, "long": 50} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : Sharpe hors échantillon 0.20 < 0.5; DSR 0.01 < 0.95; PBO 0.64 > 0.5; 18 trades hors échantillon < 30; ne bat que 28 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 50, "long": 200} 1h`, 2020 → `{"court": 50, "long": 200} 1h`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.24 < 0.5; DSR 0.01 < 0.95; PBO 0.56 > 0.5; 18 trades hors échantillon < 30; ne bat que 30 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 5} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.23 < 0.5; DSR 0.01 < 0.95; 14 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 67 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 4h`, 2020 → `{"seuil": 10} 4h`, 2021 → `{"seuil": 5} 4h`, 2022 → `{"seuil": 5} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon -1.04 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 5 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, range, forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1h`, 2020 → `{"seuil": 5} 1h`, 2021 → `{"seuil": 5} 1h`, 2022 → `{"seuil": 5} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon -0.51 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 92 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"seuil": 10} 4h`, 2021 → `{"jours": 55} 1h`, 2022 → `{"jours": 20} 1h`, 2023 → `{"jours": 20} 1h`
- Raisons de rejet : Sharpe hors échantillon -0.27 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 6 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
