# Fiche instrument — EURUSD=X

Générée par `python3 -m labo.pilote EURUSD=X` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:28:33+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2003-12-01 → 2026-10-18 (22.9 ans) | 5937 | 24 | 18 days 00:00:00 | 0 | 128 | 8 | `3ddf2ff7290d1173` | NON |

Source : Yahoo (séances réelles, OHLC ajustés) — ATTENTION : swap de financement FX non modélisé. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +14.0 % | 0.56 | 98.3 | -0.196 | 0.63 | 0.62 | -35.0 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur EURUSD=X (registre `registre/experiences.jsonl`) : **12**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.68**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 23 | -1.0 % | -11.5 % | 0.60 | -0.2 % | -0.24 | -0.23 | -0.31 | -0.08 | 1/5 | 0.04 | 0.00 | 0.02 | 0.79 | 29 % | 0.601 | stratégie non validée |
| cassure|1d | 6 | -1.6 % | -10.7 % | 0.23 | -1.8 % | -2.17 | -0.42 | -0.44 | -0.24 | 2/5 | 0.02 | 0.00 | 0.01 | 0.94 | 23 % | 0.674 | stratégie non validée |
| croisement_mm|1d | 9 | -0.1 % | -7.9 % | 0.85 | -0.2 % | -0.48 | -0.00 | -0.04 | 0.05 | 1/5 | 0.09 | 0.01 | 0.05 | 0.93 | 52 % | 0.356 | stratégie non validée |
| rebond_rsi|1d | 25 | -0.8 % | -4.3 % | 0.60 | -0.2 % | -0.20 | -0.48 | -0.72 | -0.57 | 0/5 | 0.01 | 0.00 | 0.00 | 0.79 | 14 % | 0.747 | stratégie non validée |
| selecteur_global | 22 | -1.6 % | -8.1 % | 0.26 | -0.4 % | -0.57 | -0.47 | -0.56 | -0.52 | 0/5 | 0.01 | 0.00 | 0.01 | 0.68 | 16 % | 0.746 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | -0.8 % | -22.2 % | -0.08 |
| achat_conservation_vol_ciblee | -0.8 % | -22.2 % | -0.08 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 0.20 (134 j) | -0.20 (1090 j) | -3.10 (79 j) | — (0 j) |
| cassure|1d | -0.69 (134 j) | -0.39 (1090 j) | -2.15 (79 j) | — (0 j) |
| croisement_mm|1d | -0.28 (134 j) | 0.05 (1090 j) | 0.00 (79 j) | — (0 j) |
| rebond_rsi|1d | 2.03 (134 j) | -0.62 (1090 j) | 0.00 (79 j) | — (0 j) |
| selecteur_global | -0.52 (134 j) | -0.47 (1090 j) | 0.00 (79 j) | — (0 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 180}|1d` | +0.2 % | -4.8 % | 0.08 |
| cassure|1d | `cassure|{"jours": 100}|1d` | -0.1 % | -5.4 % | -0.02 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +0.6 % | -5.8 % | 0.16 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | +0.4 % | -2.7 % | 0.36 |
| selecteur_global | `croisement_mm|{"court": 10, "long": 50}|1d` | +0.6 % | -5.8 % | 0.16 |
| *achat_conservation* | — | +0.6 % | -8.5 % | 0.14 |
| *achat_conservation_vol_ciblee* | — | +0.6 % | -8.5 % | 0.14 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 180}|1d` ; choix walk-forward par année : 2019 → `{"jours": 90} 1d`, 2020 → `{"jours": 90} 1d`, 2021 → `{"jours": 180} 1d`, 2022 → `{"jours": 180} 1d`, 2023 → `{"jours": 180} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.23 < 0.5; DSR 0.04 < 0.95; PBO 0.79 > 0.5; 23 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 29 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|1d` ; choix walk-forward par année : 2019 → `{"jours": 55} 1d`, 2020 → `{"jours": 100} 1d`, 2021 → `{"jours": 100} 1d`, 2022 → `{"jours": 100} 1d`, 2023 → `{"jours": 100} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.42 < 0.5; DSR 0.02 < 0.95; PBO 0.94 > 0.5; 6 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 23 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : tendance, range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 50, "long": 200} 1d`, 2021 → `{"court": 50, "long": 200} 1d`, 2022 → `{"court": 50, "long": 200} 1d`, 2023 → `{"court": 50, "long": 200} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.00 < 0.5; DSR 0.09 < 0.95; PBO 0.93 > 0.5; 9 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 52 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 20} 1d`, 2020 → `{"seuil": 20} 1d`, 2021 → `{"seuil": 20} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.48 < 0.5; DSR 0.01 < 0.95; PBO 0.79 > 0.5; 25 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 14 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : range ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"jours": 90} 1d`, 2020 → `{"seuil": 20} 1d`, 2021 → `{"court": 50, "long": 200} 1d`, 2022 → `{"court": 50, "long": 200} 1d`, 2023 → `{"court": 50, "long": 200} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.47 < 0.5; DSR 0.01 < 0.95; PBO 0.68 > 0.5; 22 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 16 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : tendance, range ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
