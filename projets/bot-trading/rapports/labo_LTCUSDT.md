# Fiche instrument — LTCUSDT

Générée par `python3 -m labo.pilote LTCUSDT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:50:35+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2017-12-13 → 2026-10-19 (8.8 ans) | 3233 | 0 | aucun | 0 | 0 | 1 | `4b6572931287fa51` | oui |
| 4h | 2017-12-13 → 2026-10-20 (8.9 ans) | 19386 | 16 | 1 days 08:00:00 | 0 | 0 | 10 | `d74172b93c9c1491` | oui |
| 1h | 2017-12-13 → 2026-10-20 (8.9 ans) | 77484 | 122 | 1 days 10:00:00 | 0 | 0 | 60 | `962c98b3521e4805` | oui |

Source : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +108.2 % | -0.70 | 8.5 | -0.077 | 0.92 | 0.92 | -93.4 % |
| 4h | +109.3 % | -0.31 | 8.1 | -0.029 | 0.90 | 0.90 | -93.6 % |
| 1h | +117.9 % | -0.53 | 29.4 | -0.059 | 0.78 | 0.78 | -93.7 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur LTCUSDT (registre `registre/experiences.jsonl`) : **36**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.18**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 70 | -8.1 % | -60.3 % | 1.01 | +0.0 % | 0.04 | -0.07 | -0.38 | 0.34 | 1/5 | 0.00 | 0.00 | 0.01 | 0.94 | 6 % | 0.995 | stratégie non validée |
| tendance|4h | 142 | -1.6 % | -53.7 % | 1.21 | +0.2 % | 0.06 | 0.11 | -0.23 | 0.15 | 2/5 | 0.01 | 0.00 | 0.03 | 0.96 | 26 % | 0.984 | stratégie non validée |
| tendance|1h | 163 | -0.4 % | -51.8 % | 1.09 | +0.1 % | 0.03 | 0.14 | -0.16 | 0.26 | 3/5 | 0.01 | 0.00 | 0.03 | 0.79 | 30 % | 0.975 | stratégie non validée |
| cassure|1d | 14 | +7.7 % | -56.2 % | 1.52 | +3.1 % | 0.41 | 0.40 | 0.31 | 0.40 | 3/5 | 0.05 | 0.00 | 0.10 | 0.55 | 48 % | 0.846 | stratégie non validée |
| cassure|4h | 11 | +16.5 % | -42.8 % | 3.01 | +9.9 % | 2.12 | 0.66 | 0.62 | 0.60 | 3/5 | 0.14 | 0.02 | 0.25 | 0.93 | 82 % | 0.607 | stratégie non validée |
| cassure|1h | 11 | +23.6 % | -39.4 % | 4.86 | +12.6 % | 2.62 | 0.87 | 0.84 | 0.87 | 4/5 | 0.27 | 0.04 | 0.42 | 0.07 | 91 % | 0.347 | stratégie non validée |
| croisement_mm|1d | 21 | +11.7 % | -40.2 % | 2.27 | +5.3 % | 0.88 | 0.49 | 0.38 | 0.44 | 3/5 | 0.07 | 0.01 | 0.15 | 0.26 | 58 % | 0.765 | stratégie non validée |
| croisement_mm|4h | 21 | +18.1 % | -39.5 % | 2.76 | +6.8 % | 1.46 | 0.66 | 0.60 | 0.58 | 4/5 | 0.14 | 0.02 | 0.25 | 0.10 | 76 % | 0.559 | stratégie non validée |
| croisement_mm|1h | 21 | +21.3 % | -35.9 % | 3.02 | +7.4 % | 1.64 | 0.76 | 0.71 | 0.75 | 3/5 | 0.19 | 0.03 | 0.32 | 0.05 | 80 % | 0.449 | stratégie non validée |
| rebond_rsi|1d | 31 | -3.1 % | -32.8 % | 0.78 | -0.4 % | -0.12 | -0.21 | -0.52 | 0.09 | 2/5 | 0.00 | 0.00 | 0.00 | 0.94 | 29 % | 0.958 | stratégie non validée |
| rebond_rsi|4h | 113 | -4.9 % | -34.1 % | 0.74 | -0.2 % | -0.05 | -0.40 | -1.16 | -0.86 | 1/5 | 0.00 | 0.00 | 0.00 | 0.43 | 36 % | 0.986 | stratégie non validée |
| rebond_rsi|1h | 729 | -4.6 % | -27.7 % | 0.90 | -0.0 % | -0.01 | -0.37 | -3.83 | -1.19 | 1/5 | 0.00 | 0.00 | 0.00 | 0.42 | 93 % | 0.987 | stratégie non validée |
| selecteur_global | 22 | +9.6 % | -37.7 % | 2.01 | +2.9 % | 0.50 | 0.45 | 0.38 | 0.50 | 2/5 | 0.06 | 0.00 | 0.12 | 0.18 | 46 % | 0.800 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +19.5 % | -88.8 % | 0.67 |
| achat_conservation_vol_ciblee | +26.4 % | -54.8 % | 0.75 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | -5.33 (44 j) | 0.23 (450 j) | -0.01 (106 j) | 0.04 (1226 j) |
| tendance|4h | -4.61 (44 j) | 0.09 (450 j) | 1.38 (106 j) | 0.24 (1226 j) |
| tendance|1h | -4.61 (44 j) | 0.19 (450 j) | 1.37 (106 j) | 0.23 (1226 j) |
| cassure|1d | -5.30 (44 j) | 0.85 (450 j) | 0.98 (106 j) | 0.43 (1226 j) |
| cassure|4h | -5.02 (44 j) | 0.85 (450 j) | 1.91 (106 j) | 0.79 (1226 j) |
| cassure|1h | -4.32 (44 j) | 1.16 (450 j) | 1.53 (106 j) | 0.98 (1226 j) |
| croisement_mm|1d | -5.25 (44 j) | 0.75 (450 j) | 0.65 (106 j) | 0.66 (1226 j) |
| croisement_mm|4h | -4.64 (44 j) | 0.87 (450 j) | 1.62 (106 j) | 0.74 (1226 j) |
| croisement_mm|1h | -4.49 (44 j) | 1.01 (450 j) | 1.51 (106 j) | 0.84 (1226 j) |
| rebond_rsi|1d | 0.00 (44 j) | 0.19 (450 j) | -0.01 (106 j) | -0.52 (1226 j) |
| rebond_rsi|4h | -2.15 (44 j) | -0.30 (450 j) | -1.70 (106 j) | -0.17 (1226 j) |
| rebond_rsi|1h | 0.57 (44 j) | -0.44 (450 j) | 2.19 (106 j) | -1.00 (1226 j) |
| selecteur_global | -4.66 (44 j) | 0.94 (450 j) | 1.61 (106 j) | 0.34 (1226 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 90}|1d` | +25.5 % | -25.4 % | 0.86 |
| tendance|4h | `tendance|{"jours": 90}|4h` | +13.1 % | -32.7 % | 0.55 |
| tendance|1h | `tendance|{"jours": 90}|1h` | +1.8 % | -39.0 % | 0.21 |
| cassure|1d | `cassure|{"jours": 55}|1d` | -8.3 % | -54.5 % | -0.10 |
| cassure|4h | `cassure|{"jours": 55}|4h` | -8.7 % | -48.4 % | -0.14 |
| cassure|1h | `cassure|{"jours": 55}|1h` | -2.7 % | -42.9 % | 0.05 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +4.0 % | -46.5 % | 0.28 |
| croisement_mm|4h | `croisement_mm|{"court": 10, "long": 50}|4h` | +5.6 % | -38.3 % | 0.33 |
| croisement_mm|1h | `croisement_mm|{"court": 10, "long": 50}|1h` | +4.4 % | -37.4 % | 0.29 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | +1.7 % | -3.3 % | 0.40 |
| rebond_rsi|4h | `rebond_rsi|{"seuil": 5}|4h` | -1.6 % | -16.8 % | -0.15 |
| rebond_rsi|1h | `rebond_rsi|{"seuil": 5}|1h` | -3.2 % | -16.9 % | -0.30 |
| selecteur_global | `croisement_mm|{"court": 10, "long": 50}|1h` | +4.4 % | -37.4 % | 0.29 |
| *achat_conservation* | — | -7.2 % | -70.1 % | 0.25 |
| *achat_conservation_vol_ciblee* | — | +8.1 % | -55.9 % | 0.40 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|1d` ; choix walk-forward par année : 2019 → `{"jours": 180} 1d`, 2020 → `{"jours": 90} 1d`, 2021 → `{"jours": 30} 1d`, 2022 → `{"jours": 30} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.07 < 0.5; DSR 0.00 < 0.95; PBO 0.94 > 0.5; ne résiste pas aux coûts ×3; ne bat que 6 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|4h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|4h` ; choix walk-forward par année : 2019 → `{"jours": 180} 4h`, 2020 → `{"jours": 90} 4h`, 2021 → `{"jours": 30} 4h`, 2022 → `{"jours": 30} 4h`, 2023 → `{"jours": 90} 4h`
- Raisons de rejet : Sharpe hors échantillon 0.11 < 0.5; DSR 0.01 < 0.95; PBO 0.96 > 0.5; ne résiste pas aux coûts ×3; ne bat que 26 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### tendance|1h — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|1h` ; choix walk-forward par année : 2019 → `{"jours": 180} 1h`, 2020 → `{"jours": 90} 1h`, 2021 → `{"jours": 90} 1h`, 2022 → `{"jours": 90} 1h`, 2023 → `{"jours": 90} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.14 < 0.5; DSR 0.01 < 0.95; PBO 0.79 > 0.5; ne résiste pas aux coûts ×3; ne bat que 30 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 55}|1d` ; choix walk-forward par année : 2019 → `{"jours": 55} 1d`, 2020 → `{"jours": 55} 1d`, 2021 → `{"jours": 55} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 55} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.40 < 0.5; DSR 0.05 < 0.95; PBO 0.55 > 0.5; 14 trades hors échantillon < 30; ne bat que 48 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.4 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|4h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 55}|4h` ; choix walk-forward par année : 2019 → `{"jours": 55} 4h`, 2020 → `{"jours": 55} 4h`, 2021 → `{"jours": 55} 4h`, 2022 → `{"jours": 55} 4h`, 2023 → `{"jours": 55} 4h`
- Raisons de rejet : DSR 0.14 < 0.95; PBO 0.93 > 0.5; 11 trades hors échantillon < 30; ne bat que 82 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1h — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 55}|1h` ; choix walk-forward par année : 2019 → `{"jours": 55} 1h`, 2020 → `{"jours": 55} 1h`, 2021 → `{"jours": 55} 1h`, 2022 → `{"jours": 55} 1h`, 2023 → `{"jours": 55} 1h`
- Raisons de rejet : DSR 0.27 < 0.95; 11 trades hors échantillon < 30; ne bat que 91 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 20, "long": 100} 1d`, 2020 → `{"court": 20, "long": 100} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.49 < 0.5; DSR 0.07 < 0.95; 21 trades hors échantillon < 30; ne bat que 58 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.5 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|4h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|4h` ; choix walk-forward par année : 2019 → `{"court": 20, "long": 100} 4h`, 2020 → `{"court": 20, "long": 100} 4h`, 2021 → `{"court": 10, "long": 50} 4h`, 2022 → `{"court": 10, "long": 50} 4h`, 2023 → `{"court": 10, "long": 50} 4h`
- Raisons de rejet : DSR 0.14 < 0.95; 21 trades hors échantillon < 30; ne bat que 76 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1h — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"court": 20, "long": 100} 1h`, 2020 → `{"court": 20, "long": 100} 1h`, 2021 → `{"court": 10, "long": 50} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : DSR 0.19 < 0.95; 21 trades hors échantillon < 30; ne bat que 80 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 20} 1d`, 2021 → `{"seuil": 20} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.21 < 0.5; DSR 0.00 < 0.95; PBO 0.94 > 0.5; ne résiste pas aux coûts ×3; ne bat que 29 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|4h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|4h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 4h`, 2020 → `{"seuil": 5} 4h`, 2021 → `{"seuil": 5} 4h`, 2022 → `{"seuil": 5} 4h`, 2023 → `{"seuil": 5} 4h`
- Raisons de rejet : Sharpe hors échantillon -0.40 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 36 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.2 %
- Ne pas utiliser en régime : tendance, range, forte_volatilite, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1h — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1h` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1h`, 2020 → `{"seuil": 10} 1h`, 2021 → `{"seuil": 10} 1h`, 2022 → `{"seuil": 10} 1h`, 2023 → `{"seuil": 5} 1h`
- Raisons de rejet : Sharpe hors échantillon -0.37 < 0.5; DSR 0.00 < 0.95; ne résiste pas aux coûts ×3; ne bat que 93 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : range, crise ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1h` ; choix walk-forward par année : 2019 → `{"jours": 180} 1d`, 2020 → `{"jours": 55} 1h`, 2021 → `{"jours": 55} 1h`, 2022 → `{"court": 10, "long": 50} 1h`, 2023 → `{"court": 10, "long": 50} 1h`
- Raisons de rejet : Sharpe hors échantillon 0.45 < 0.5; DSR 0.06 < 0.95; 22 trades hors échantillon < 30; ne bat que 46 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.3 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
