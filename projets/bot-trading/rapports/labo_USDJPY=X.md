# Fiche instrument — USDJPY=X

Générée par `python3 -m labo.pilote USDJPY=X` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:28:52+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2000-01-03 → 2026-10-18 (26.8 ans) | 6957 | 24 | 18 days 00:00:00 | 0 | 263 | 6 | `73733c7d70726530` | NON |

Source : Yahoo (séances réelles, OHLC ajustés) — ATTENTION : swap de financement FX non modélisé. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +13.7 % | -0.53 | 112.5 | -0.181 | 0.69 | 0.63 | -43.8 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur USDJPY=X (registre `registre/experiences.jsonl`) : **12**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.39**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 37 | +2.1 % | -15.7 % | 1.64 | +0.3 % | 0.87 | 0.39 | 0.29 | 0.41 | 3/5 | 0.17 | 0.01 | 0.18 | 0.66 | 46 % | 0.925 | stratégie non validée |
| cassure|1d | 2 | +6.1 % | -10.4 % | — | +16.5 % | 19.22 | 1.23 | 1.22 | 1.20 | 3/5 | 0.73 | 0.21 | 0.74 | 0.72 | 96 % | 0.121 | stratégie non validée |
| croisement_mm|1d | 12 | +4.0 % | -11.5 % | 3.05 | +1.8 % | 2.48 | 0.72 | 0.69 | 0.80 | 3/5 | 0.37 | 0.04 | 0.38 | 0.86 | 65 % | 0.556 | stratégie non validée |
| rebond_rsi|1d | 25 | -0.5 % | -6.0 % | 0.77 | -0.1 % | -0.07 | -0.21 | -0.39 | -0.11 | 1/5 | 0.02 | 0.00 | 0.02 | 0.44 | 21 % | 0.948 | stratégie non validée |
| selecteur_global | 10 | +4.3 % | -10.4 % | 3.49 | +2.4 % | 2.56 | 0.81 | 0.78 | 0.79 | 3/5 | 0.43 | 0.06 | 0.45 | 0.39 | 79 % | 0.505 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +5.2 % | -14.7 % | 0.74 |
| achat_conservation_vol_ciblee | +5.2 % | -14.7 % | 0.74 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 0.57 (161 j) | 0.58 (990 j) | -0.46 (152 j) | — (0 j) |
| cassure|1d | 0.57 (161 j) | 1.53 (990 j) | 1.10 (152 j) | — (0 j) |
| croisement_mm|1d | 0.57 (161 j) | 0.67 (990 j) | 1.29 (152 j) | — (0 j) |
| rebond_rsi|1d | -1.82 (161 j) | -0.26 (990 j) | 1.57 (152 j) | — (0 j) |
| selecteur_global | 0.57 (161 j) | 0.77 (990 j) | 1.44 (152 j) | — (0 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 90}|1d` | -0.7 % | -10.8 % | -0.10 |
| cassure|1d | `cassure|{"jours": 100}|1d` | -1.8 % | -11.3 % | -0.38 |
| croisement_mm|1d | `croisement_mm|{"court": 20, "long": 100}|1d` | -0.1 % | -12.9 % | 0.02 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | -0.3 % | -3.9 % | -0.17 |
| selecteur_global | `cassure|{"jours": 100}|1d` | -1.8 % | -11.3 % | -0.38 |
| *achat_conservation* | — | +4.1 % | -12.9 % | 0.56 |
| *achat_conservation_vol_ciblee* | — | +4.1 % | -12.9 % | 0.56 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|1d` ; choix walk-forward par année : 2019 → `{"jours": 30} 1d`, 2020 → `{"jours": 30} 1d`, 2021 → `{"jours": 90} 1d`, 2022 → `{"jours": 90} 1d`, 2023 → `{"jours": 90} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon 0.39 < 0.5; DSR 0.17 < 0.95; PBO 0.66 > 0.5; ne bat que 46 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|1d` ; choix walk-forward par année : 2019 → `{"jours": 100} 1d`, 2020 → `{"jours": 100} 1d`, 2021 → `{"jours": 100} 1d`, 2022 → `{"jours": 100} 1d`, 2023 → `{"jours": 100} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; DSR 0.73 < 0.95; PBO 0.72 > 0.5; 2 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 20, "long": 100}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 20, "long": 100} 1d`, 2022 → `{"court": 20, "long": 100} 1d`, 2023 → `{"court": 20, "long": 100} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; DSR 0.37 < 0.95; PBO 0.86 > 0.5; 12 trades hors échantillon < 30; ne bat que 65 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 20} 1d`, 2020 → `{"seuil": 10} 1d`, 2021 → `{"seuil": 10} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; Sharpe hors échantillon -0.21 < 0.5; DSR 0.02 < 0.95; 25 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 21 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : tendance, range ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 100}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"jours": 100} 1d`, 2022 → `{"jours": 100} 1d`, 2023 → `{"jours": 100} 1d`
- Raisons de rejet : données insuffisantes; données insuffisantes : coût de financement (swap) non modélisé; DSR 0.43 < 0.95; 10 trades hors échantillon < 30; ne bat que 79 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.0 %
- Ne pas utiliser en régime : aucun régime négatif identifié (échantillon limité) ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
