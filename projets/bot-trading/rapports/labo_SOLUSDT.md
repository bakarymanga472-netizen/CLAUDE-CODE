# Fiche instrument — SOLUSDT

Générée par `python3 -m labo.pilote SOLUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:54:02+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2020-08-11 → 2026-10-19 (6.2 ans) | 2261 | 0 | aucun | 0 | 0 | 1 | `9fe8f29010fc8d7b` | oui |
| 4h | 2020-08-11 → 2026-10-20 (6.2 ans) | 13569 | 0 | aucun | 0 | 0 | 2 | `d28d94fb2b4b7160` | oui |
| 1h | 2020-08-11 → 2026-10-20 (6.2 ans) | 54255 | 20 | 0 days 05:00:00 | 0 | 0 | 30 | `cb084b828a754568` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +163.8 % | -0.02 | 3.4 | -0.095 | 0.88 | 1.22 | -74.7 % |
| 4h | +172.9 % | 0.28 | 6.0 | -0.072 | 0.81 | 1.09 | -75.0 % |
| 1h | +177.3 % | 0.35 | 11.3 | -0.030 | 0.78 | 1.04 | -75.6 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur SOLUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.25**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 25 | +56.2 % | -39.1 % | 6.91 | +9.9 % | 2.17 | 1.57 | 1.41 | 1.79 | 2/4 | 0.24 | 0.01 | 0.78 | 0.43 | 97 % | 0.324 | stratégie non validée |
| tendance|4h | 60 | +51.5 % | -39.3 % | 4.83 | +4.0 % | 0.95 | 1.55 | 1.34 | 1.66 | 2/4 | 0.23 | 0.01 | 0.77 | 0.79 | 96 % | 0.348 | stratégie non validée |
| tendance|1h | 93 | +44.9 % | -48.3 % | 5.29 | +2.9 % | 0.66 | 1.43 | 1.20 | 1.52 | 2/4 | 0.18 | 0.01 | 0.69 | 0.76 | 86 % | 0.417 | stratégie non validée |
| cassure|1d | 5 | +45.8 % | -32.8 % | 10.30 | +57.5 % | 12.74 | 1.58 | 1.53 | 1.75 | 2/4 | 0.25 | 0.01 | 0.79 | 0.61 | 88 % | 0.341 | stratégie non validée |
| cassure|4h | 6 | +46.3 % | -30.2 % | 7.19 | +34.8 % | 7.81 | 1.66 | 1.63 | 1.69 | 2/4 | 0.30 | 0.02 | 0.83 | 0.65 | 88 % | 0.291 | stratégie non validée |
| cassure|1h | 8 | +42.1 % | -44.1 % | 5.03 | +26.2 % | 5.83 | 1.52 | 1.49 | 1.48 | 2/4 | 0.22 | 0.01 | 0.75 | 0.86 | 80 % | 0.367 | stratégie non validée |
| croisement_mm|1d | 11 | +38.1 % | -59.5 % | 4.73 | +24.9 % | 6.11 | 1.15 | 1.07 | 1.13 | 2/4 | 0.08 | 0.00 | 0.49 | 0.58 | 71 % | 0.643 | stratégie non validée |
| croisement_mm|4h | 11 | +55.4 % | -40.0 % | 5.92 | +20.0 % | 4.18 | 1.55 | 1.51 | 1.43 | 2/4 | 0.24 | 0.01 | 0.76 | 0.54 | 98 % | 0.318 | stratégie non validée |
| croisement_mm|1h | 11 | +63.7 % | -33.3 % | 7.52 | +21.9 % | 4.75 | 1.82 | 1.79 | 1.81 | 2/4 | 0.42 | 0.04 | 0.89 | 0.45 | 100 % | 0.124 | stratégie non validée |
| rebond_rsi|1d | 18 | -3.2 % | -23.1 % | 0.67 | -0.5 % | -0.15 | -0.31 | -0.69 | -0.79 | 1/4 | 0.00 | 0.00 | 0.00 | 0.85 | 12 % | 0.991 | stratégie non validée |
| rebond_rsi|4h | 85 | +2.1 % | -13.2 % | 1.20 | +0.1 % | 0.01 | 0.28 | -0.67 | -0.21 | 1/4 | 0.00 | 0.00 | 0.05 | 0.56 | 75 % | 0.920 | stratégie non validée |
| rebond_rsi|1h | 347 | +3.1 % | -17.3 % | 1.14 | +0.0 % | 0.00 | 0.45 | -2.72 | -0.14 | 2/4 | 0.00 | 0.00 | 0.10 | 0.02 | 100 % | 0.885 | stratégie non validée |
| selecteur_global | 20 | +32.9 % | -49.0 % | 3.50 | +8.7 % | 1.92 | 1.11 | 1.00 | 1.28 | 2/4 | 0.06 | 0.00 | 0.46 | 0.25 | 65 % | 0.673 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +174.9 % | -96.3 % | 1.41 |
| achat_conservation_vol_ciblee | +68.2 % | -67.4 % | 1.35 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 4.75 (233 j) | 1.11 (142 j) | — (19 j) | 0.36 (783 j) |
| tendance|4h | 5.34 (233 j) | 1.46 (142 j) | — (19 j) | -0.01 (783 j) |
| tendance|1h | 5.36 (233 j) | 1.86 (142 j) | — (19 j) | -0.49 (783 j) |
| cassure|1d | 4.78 (233 j) | 2.33 (142 j) | — (19 j) | -1.15 (783 j) |
| cassure|4h | 5.31 (233 j) | 2.58 (142 j) | — (19 j) | -1.04 (783 j) |
| cassure|1h | 5.38 (233 j) | 3.22 (142 j) | — (19 j) | -1.44 (783 j) |
| croisement_mm|1d | 4.77 (233 j) | 2.55 (142 j) | — (19 j) | -0.96 (783 j) |
| croisement_mm|4h | 5.02 (233 j) | 2.34 (142 j) | — (19 j) | -0.07 (783 j) |
| croisement_mm|1h | 5.23 (233 j) | 3.14 (142 j) | — (19 j) | 0.03 (783 j) |
| rebond_rsi|1d | 1.30 (233 j) | -1.08 (142 j) | — (19 j) | -0.54 (783 j) |
| rebond_rsi|4h | 1.41 (233 j) | 0.54 (142 j) | — (19 j) | -0.65 (783 j) |
| rebond_rsi|1h | 3.61 (233 j) | -0.94 (142 j) | — (19 j) | -0.71 (783 j) |
| selecteur_global | 4.82 (233 j) | 0.87 (142 j) | — (19 j) | -0.88 (783 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 30}|1d` | +4.4 % | -48.0 % | 0.29 |
| tendance|4h | `tendance|{"jours": 30}|4h` | -4.1 % | -51.9 % | 0.01 |
| tendance|1h | `tendance|{"jours": 30}|1h` | -1.9 % | -49.1 % | 0.07 |
| cassure|1d | `cassure|{"jours": 100}|1d` | +14.0 % | -35.8 % | 0.56 |
| cassure|4h | `cassure|{"jours": 100}|4h` | +7.9 % | -35.1 % | 0.40 |
| cassure|1h | `cassure|{"jours": 55}|1h` | -8.7 % | -46.3 % | -0.24 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +7.9 % | -40.1 % | 0.40 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +5.4 % | -37.9 % | 0.32 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +5.8 % | -34.2 % | 0.34 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | -0.3 % | -12.7 % | 0.01 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -4.5 % | -20.5 % | -0.45 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -7.7 % | -29.2 % | -0.71 |
| selecteur_global | `tendance|{"jours": 30}|1d` | +4.4 % | -48.0 % | 0.29 |
| *achat_conservation* | — | +0.8 % | -76.3 % | 0.40 |
| *achat_conservation_vol_ciblee* | — | +14.9 % | -58.3 % | 0.54 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 90} 1d`, 2022 → `{"jours": 180} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : DSR 0.24 < 0.95; 25 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|4h` ; choix walk-forward par année : 2019 → `{"jours": 30} 4h`, 2020 → `{"jours": 30} 4h`, 2021 → `{"jours": 90} 4h`, 2022 → `{"jours": 180} 4h`, 2023 → `{"jours": 30} 4h`
- Raisons de rejet : DSR 0.23 < 0.95; PBO 0.79 > 0.5
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1h` ; choix walk-forward par année : 2019 → `{"jours": 30} 1h`, 2020 → `{"jours": 30} 1h`, 2021 → `{"jours": 90} 1h`, 2022 → `{"jours": 180} 1h`, 2023 → `{"jours": 180} 1h`
- Raisons de rejet : DSR 0.18 < 0.95; PBO 0.76 > 0.5; ne bat que 86 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 55} 1d`, 2022 → `{"jours": 100} 1d`, 2023 → `{"jours": 100} 1d`
- Raisons de rejet : DSR 0.25 < 0.95; PBO 0.61 > 0.5; 5 trades hors échantillon < 30; ne bat que 88 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.6 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|4h` ; choix walk-forward par année : 2019 → `{"jours": 20} 4h`, 2020 → `{"jours": 20} 4h`, 2021 → `{"jours": 55} 4h`, 2022 → `{"jours": 100} 4h`, 2023 → `{"jours": 100} 4h`
- Raisons de rejet : DSR 0.30 < 0.95; PBO 0.65 > 0.5; 6 trades hors échantillon < 30; ne bat que 88 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 55}|1h` ; choix walk-forward par année : 2019 → `{"jours": 20} 1h`, 2020 → `{"jours": 20} 1h`, 2021 → `{"jours": 55} 1h`, 2022 → `{"jours": 55} 1h`, 2023 → `{"jours": 100} 1h`
- Raisons de rejet : DSR 0.22 < 0.95; PBO 0.86 > 0.5; 8 trades hors échantillon < 30; ne bat que 80 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 20, "long": 100} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 20, "long": 100} 1d`
- Raisons de rejet : DSR 0.08 < 0.95; PBO 0.58 > 0.5; 11 trades hors échantillon < 30; ne bat que 71 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 4h`, 2020 → `{"court": 10, "long": 50} 4h`, 2021 → `{"court": 20, "long": 100} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : DSR 0.24 < 0.95; PBO 0.54 > 0.5; 11 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1h`, 2020 → `{"court": 10, "long": 50} 1h`, 2021 → `{"court": 20, "long": 100} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.42 < 0.95; 11 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 5} 1d`, 2022 → `{"seuil": 20} 1d`, 2023 → `{"seuil": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.31 < 0.5; DSR 0.00 < 0.95; PBO 0.85 > 0.5; 18 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 12 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 4h`, 2020 → `{"seuil": 5} 4h`, 2021 → `{"seuil": 5} 4h`, 2022 → `{"seuil": 5} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon 0.28 < 0.5; DSR 0.00 < 0.95; PBO 0.56 > 0.5; ne résiste pas aux coûts ×3; ne bat que 75 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1h`, 2020 → `{"seuil": 5} 1h`, 2021 → `{"seuil": 5} 1h`, 2022 → `{"seuil": 5} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.45 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 30}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 90} 1d`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"jours": 100} 4h`
- Raisons de rejet : DSR 0.06 < 0.95; 20 trades hors échantillon < 30; ne bat que 65 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
