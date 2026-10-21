# Fiche instrument — GLD

Générée par `python3 -m labo.pilote GLD` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:26:57+00:00, DÉJÀ OUVERT avant cette exécution : ne prouve plus rien de neuf).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2004-11-18 → 2026-10-19 (21.9 ans) | 5513 | 0 | aucun | 0 | 0 | 1 | `f7b66bafce3ae12a` | oui |

Source : Yahoo (séances réelles, OHLC ajustés). Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +21.7 % | -0.33 | 6.3 | -0.010 | 0.97 | 0.85 | -45.6 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur GLD (registre `registre/experiences.jsonl`) : **12**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.67**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 37 | -0.5 % | -31.3 % | 1.15 | +0.2 % | 0.18 | 0.00 | -0.08 | -0.21 | 2/5 | 0.19 | 0.05 | 0.05 | 0.94 | 2 % | 0.984 | stratégie non validée |
| cassure|1d | 20 | +2.3 % | -21.8 % | 1.40 | +0.6 % | 0.39 | 0.26 | 0.22 | 0.27 | 3/5 | 0.38 | 0.15 | 0.14 | 1.00 | 33 % | 0.863 | stratégie non validée |
| croisement_mm|1d | 5 | +4.5 % | -23.4 % | 15.32 | +27.9 % | 13.68 | 0.41 | 0.40 | 0.39 | 3/5 | 0.51 | 0.24 | 0.23 | 0.83 | 28 % | 0.884 | stratégie non validée |
| rebond_rsi|1d | 42 | -1.3 % | -15.7 % | 0.82 | -0.1 % | -0.08 | -0.19 | -0.34 | 0.00 | 2/5 | 0.09 | 0.02 | 0.02 | 0.63 | 20 % | 0.961 | stratégie non validée |
| selecteur_global | 18 | -2.2 % | -34.5 % | 0.99 | -0.0 % | 0.12 | -0.15 | -0.19 | -0.13 | 1/5 | 0.11 | 0.02 | 0.02 | 0.67 | 0 % | 0.995 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +9.6 % | -22.2 % | 0.69 |
| achat_conservation_vol_ciblee | +9.0 % | -20.9 % | 0.69 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | -0.15 (161 j) | 0.12 (1031 j) | -0.11 (66 j) | — (0 j) |
| cassure|1d | -0.27 (161 j) | 0.70 (1031 j) | -1.17 (66 j) | — (0 j) |
| croisement_mm|1d | -0.15 (161 j) | 0.57 (1031 j) | 0.24 (66 j) | — (0 j) |
| rebond_rsi|1d | 0.65 (161 j) | -0.08 (1031 j) | -0.81 (66 j) | — (0 j) |
| selecteur_global | -0.15 (161 j) | 0.09 (1031 j) | -1.17 (66 j) | — (0 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 90}|1d` | +31.0 % | -21.4 % | 1.53 |
| cassure|1d | `cassure|{"jours": 100}|1d` | +30.2 % | -21.4 % | 1.58 |
| croisement_mm|1d | `croisement_mm|{"court": 20, "long": 100}|1d` | +29.7 % | -22.5 % | 1.46 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 20}|1d` | +4.7 % | -16.8 % | 0.48 |
| selecteur_global | `croisement_mm|{"court": 20, "long": 100}|1d` | +29.7 % | -22.5 % | 1.46 |
| *achat_conservation* | — | +28.0 % | -28.5 % | 1.28 |
| *achat_conservation_vol_ciblee* | — | +25.6 % | -28.0 % | 1.23 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 180} 1d`, 2022 → `{"jours": 180} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.00 < 0.5; DSR 0.19 < 0.95; PBO 0.94 > 0.5; ne résiste pas aux coûts ×3; ne bat que 2 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.26 < 0.5; DSR 0.38 < 0.95; PBO 1.00 > 0.5; 20 trades hors échantillon < 30; ne bat que 33 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 20, "long": 100}|1d` ; choix walk-forward par année : 2019 → `{"court": 20, "long": 100} 1d`, 2020 → `{"court": 50, "long": 200} 1d`, 2021 → `{"court": 50, "long": 200} 1d`, 2022 → `{"court": 50, "long": 200} 1d`, 2023 → `{"court": 20, "long": 100} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.41 < 0.5; DSR 0.51 < 0.95; PBO 0.83 > 0.5; 5 trades hors échantillon < 30; ne bat que 28 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 20}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 10} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 20} 1d`, 2022 → `{"seuil": 20} 1d`, 2023 → `{"seuil": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.19 < 0.5; DSR 0.09 < 0.95; PBO 0.63 > 0.5; ne résiste pas aux coûts ×3; ne bat que 20 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 20, "long": 100}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"court": 50, "long": 200} 1d`, 2022 → `{"court": 50, "long": 200} 1d`, 2023 → `{"jours": 30} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.15 < 0.5; DSR 0.11 < 0.95; PBO 0.67 > 0.5; 18 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 0 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
