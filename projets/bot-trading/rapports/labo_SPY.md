# Fiche instrument — SPY

Générée par `python3 -m labo.pilote SPY` · critères `criteres-v1-2026-10-20` (fixés avant les tests, `labo/criteres.py`).
Développement 2017-08-17 → 2021-12-31 · validation 2022-01-01 → 2023-12-31 · walk-forward hors échantillon 2019-2023 · coffre 2024-01-01 → aujourd'hui (première ouverture : 2026-10-20T17:28:00+00:00, vierge).

## 1. Données

| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |
|---|---|---|---|---|---|---|---|---|---|
| 1d | 2000-01-03 → 2026-10-19 (26.8 ans) | 6739 | 6 | 7 days 00:00:00 | 0 | 0 | 4 | `53022d7b748d9bf2` | oui |

Source : Yahoo (séances réelles, OHLC ajustés). Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.

## 2. Caractéristiques du marché (période de développement)

| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |
|---|---|---|---|---|---|---|---|
| 1d | +23.6 % | -0.26 | 11.9 | -0.095 | 0.78 | 0.72 | -55.2 % |

Ratio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.

## 3. Contrôle du surapprentissage

- Configurations distinctes testées sur SPY (registre `registre/experiences.jsonl`) : **12**.
- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **0.23**.
- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; elle n'est PAS le critère fixé à l'avance et ne change aucun statut.
- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.

## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)

| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| tendance|1d | 23 | +6.7 % | -20.7 % | 6.28 | +3.6 % | 1.80 | 0.52 | 0.48 | 0.48 | 4/5 | 0.50 | 0.17 | 0.31 | 0.82 | 26 % | 0.830 | stratégie non validée |
| cassure|1d | 23 | +10.7 % | -8.6 % | 4.39 | +2.3 % | 0.98 | 0.98 | 0.92 | 0.76 | 4/5 | 0.84 | 0.52 | 0.70 | 0.68 | 85 % | 0.345 | stratégie non validée |
| croisement_mm|1d | 12 | +9.2 % | -15.2 % | 2.64 | +3.2 % | 1.04 | 0.74 | 0.71 | 0.65 | 4/5 | 0.69 | 0.32 | 0.49 | 0.81 | 69 % | 0.567 | stratégie non validée |
| rebond_rsi|1d | 46 | +0.4 % | -13.3 % | 1.10 | +0.1 % | 0.12 | 0.09 | -0.08 | 0.31 | 2/5 | 0.17 | 0.03 | 0.07 | 0.91 | 36 % | 0.915 | stratégie non validée |
| selecteur_global | 23 | +10.7 % | -8.6 % | 4.39 | +2.3 % | 0.98 | 0.98 | 0.92 | 0.76 | 4/5 | 0.84 | 0.52 | 0.70 | 0.23 | 85 % | 0.345 | stratégie non validée |

**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :

| Référence | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|
| achat_conservation | +15.8 % | -32.0 % | 0.85 |
| achat_conservation_vol_ciblee | +14.1 % | -28.6 % | 0.81 |

## 5. Performance par régime (walk-forward, régimes connus la veille)

| Candidat | Tendance | Range | Forte volatilité | Crise |
|---|---|---|---|---|
| tendance|1d | -0.27 (175 j) | 0.55 (788 j) | 0.36 (286 j) | — (9 j) |
| cassure|1d | -0.40 (175 j) | 1.08 (788 j) | 0.72 (286 j) | — (9 j) |
| croisement_mm|1d | -0.24 (175 j) | 0.71 (788 j) | 0.56 (286 j) | — (9 j) |
| rebond_rsi|1d | 0.06 (175 j) | 0.10 (788 j) | -0.22 (286 j) | — (9 j) |
| selecteur_global | -0.40 (175 j) | 1.08 (788 j) | 0.72 (286 j) | — (9 j) |

Valeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.

## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)

| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |
|---|---|---|---|---|
| tendance|1d | `tendance|{"jours": 180}|1d` | +16.5 % | -16.6 % | 1.30 |
| cassure|1d | `cassure|{"jours": 20}|1d` | +7.8 % | -7.8 % | 0.95 |
| croisement_mm|1d | `croisement_mm|{"court": 10, "long": 50}|1d` | +9.1 % | -10.7 % | 0.88 |
| rebond_rsi|1d | `rebond_rsi|{"seuil": 20}|1d` | +9.3 % | -5.2 % | 1.38 |
| selecteur_global | `cassure|{"jours": 20}|1d` | +7.8 % | -7.8 % | 0.95 |
| *achat_conservation* | — | +20.3 % | -19.8 % | 1.26 |
| *achat_conservation_vol_ciblee* | — | +20.0 % | -19.5 % | 1.26 |

## 7. Fiches de décision

### tendance|1d — **stratégie non validée**

- Version/paramètres : configuration figée `tendance|{"jours": 180}|1d` ; choix walk-forward par année : 2019 → `{"jours": 90} 1d`, 2020 → `{"jours": 180} 1d`, 2021 → `{"jours": 30} 1d`, 2022 → `{"jours": 180} 1d`, 2023 → `{"jours": 180} 1d`
- Raisons de rejet : DSR 0.50 < 0.95; PBO 0.82 > 0.5; 23 trades hors échantillon < 30; ne bat que 26 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### cassure|1d — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : DSR 0.84 < 0.95; PBO 0.68 > 0.5; 23 trades hors échantillon < 30; ne bat que 85 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### croisement_mm|1d — **stratégie non validée**

- Version/paramètres : configuration figée `croisement_mm|{"court": 10, "long": 50}|1d` ; choix walk-forward par année : 2019 → `{"court": 50, "long": 200} 1d`, 2020 → `{"court": 10, "long": 50} 1d`, 2021 → `{"court": 10, "long": 50} 1d`, 2022 → `{"court": 10, "long": 50} 1d`, 2023 → `{"court": 10, "long": 50} 1d`
- Raisons de rejet : DSR 0.69 < 0.95; PBO 0.81 > 0.5; 12 trades hors échantillon < 30; ne bat que 69 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### rebond_rsi|1d — **stratégie non validée**

- Version/paramètres : configuration figée `rebond_rsi|{"seuil": 20}|1d` ; choix walk-forward par année : 2019 → `{"seuil": 5} 1d`, 2020 → `{"seuil": 5} 1d`, 2021 → `{"seuil": 20} 1d`, 2022 → `{"seuil": 20} 1d`, 2023 → `{"seuil": 20} 1d`
- Raisons de rejet : Sharpe hors échantillon 0.09 < 0.5; DSR 0.17 < 0.95; PBO 0.91 > 0.5; ne résiste pas aux coûts ×3; ne bat que 36 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : forte_volatilite ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

### selecteur_global — **stratégie non validée**

- Version/paramètres : configuration figée `cassure|{"jours": 20}|1d` ; choix walk-forward par année : 2019 → `{"jours": 20} 1d`, 2020 → `{"jours": 20} 1d`, 2021 → `{"jours": 20} 1d`, 2022 → `{"jours": 20} 1d`, 2023 → `{"jours": 20} 1d`
- Raisons de rejet : DSR 0.84 < 0.95; 23 trades hors échantillon < 30; ne bat que 85 % des expositions aléatoires (seuil 95 %)
- Coût moyen par trade (hors échantillon) : +0.1 %
- Ne pas utiliser en régime : tendance ; désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).

## 8. Ce qui reste incertain

- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.
- Un seul instrument : aucun effet de diversification n'est mesuré ici.
- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.
- Les chiffres « par régime » reposent sur peu de jours en crise.
