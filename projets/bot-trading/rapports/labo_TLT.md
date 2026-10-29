# Fiche instrument — TLT

Générée par `python3 -m labo.pilote TLT` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:28:17+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2002-07-30 → 2026-10-19 (24.2 ans) | 6095 | 0 | aucun | 0 | 0 | 0 | `36165dc23f7d879e` | oui |

Source : Yahoo (séances réelles, OHLC ajustés). Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +16.7 % | -0.01 | 4.5 | -0.023 | 0.85 | 0.86 | -26.6 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur TLT (registre `registre/experiences.jsonl`) : **12**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.15**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 24 | +3.5 % | -21.5 % | 0.88 | -0.2 % | -0.05 | 0.34 | 0.29 | 0.36 | 3/5 | 0.45 | 0.19 | 0.18 | 0.60 | 93 % | 0.113 | stratégie non validée |
| cassure|1d | 18 | -2.7 % | -38.0 % | 0.70 | -0.6 % | -0.22 | -0.19 | -0.23 | -0.14 | 2/5 | 0.10 | 0.02 | 0.02 | 0.40 | 35 % | 0.637 | stratégie non validée |
| croisement_mm|1d | 13 | +6.3 % | -18.0 % | 3.06 | +2.3 % | 1.70 | 0.57 | 0.53 | 0.54 | 4/5 | 0.65 | 0.36 | 0.34 | 0.54 | 99 % | 0.021 | stratégie non validée |
| rebond_rsi|1d | 11 | +2.0 % | -2.1 % | 5.96 | +0.9 % | 0.57 | 0.92 | 0.78 | 1.36 | 3/5 | 0.93 | 0.70 | 0.69 | 0.00 | 97 % | 0.041 | stratégie non validée |
| selecteur_global | 11 | +2.0 % | -2.1 % | 5.96 | +0.9 % | 0.57 | 0.92 | 0.78 | 1.36 | 3/5 | 0.93 | 0.70 | 0.69 | 0.15 | 97 % | 0.041 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | -2.0 % | -50.2 % | -0.04 |
| achat_conservation_vol_ciblee | -2.3 % | -50.9 % | -0.06 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | 0.76 (97 j) | 0.82 (624 j) | -0.69 (537 j) | — (0 j) |
| cassure|1d | 0.69 (97 j) | -0.12 (624 j) | -0.65 (537 j) | — (0 j) |
| croisement_mm|1d | 0.76 (97 j) | 0.74 (624 j) | -0.14 (537 j) | — (0 j) |
| rebond_rsi|1d | -0.46 (97 j) | 1.06 (624 j) | -0.14 (537 j) | — (0 j) |
| selecteur_global | -0.46 (97 j) | 1.06 (624 j) | -0.14 (537 j) | — (0 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 90}|1d` | -9.3 % | -24.8 % | -1.07 |
| cassure|1d | `cassure|{"jours": 20}|1d` | -8.7 % | -22.4 % | -1.08 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | -2.5 % | -13.5 % | -0.26 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 5}|1d` | +1.1 % | -1.7 % | 0.60 |
| selecteur_global | `rebond_rsi|{"seuil": 5}|1d` | +1.1 % | -1.7 % | 0.60 |
| *achat_conservation* | — | -3.1 % | -17.4 % | -0.19 |
| *achat_conservation_vol_ciblee* | — | -3.1 % | -17.4 % | -0.19 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 90}|1d` ; choix walk-forward par année : 2019 → `{"jours": 90} 1d`, 2020 → `{"jours": 90} 1d`, 2021 → `{"jours": 90} 1d`, 2022 → `{"jours": 90} 1d`, 2023 → `{"jours": 90} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.34 < 0.5; DSR 0.45 < 0.95; PBO 0.60 > 0.5; 24 trades hors échantillon < 30; ne bat que 93 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 100} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 55} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon -0.19 < 0.5; DSR 0.10 < 0.95; 18 trades hors échantillon < 30; ne résiste pas aux coûts ×3; ne bat que 35 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : range, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 10, "long": 50} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : DSR 0.65 < 0.95; PBO 0.54 > 0.5; 13 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 5} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : DSR 0.93 < 0.95; 11 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 5}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 5} 1d`, 2022 → `{"seuil": 5} 1d`, 2023 → `{"seuil": 5} 1d`
- Raisons de rejet : DSR 0.93 < 0.95; 11 trades hors échantillon < 30
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance, forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
