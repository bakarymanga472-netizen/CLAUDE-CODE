> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0023 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-03-11 00:00:00 · sortie 2026-03-13 00:00:00 · régime range · net +0.39 % · **0.06 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | aucune anomalie détectée | — | — |
| execution | aucune anomalie détectée | — | — |
| processus | anomalie | cause confirmée | [confirmée] mauvaise taille : taille 0.2 ≠ taille prévue 0.1 (> 5%) |
| statistique | non conforme | — | gain malgré une décision NON conforme : ne pas le compter comme une preuve de la règle |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 71905.74 | 71941.69 |
| Taille | 0.1000 | 0.2000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00050 |
| Sortie | — | signal |

## Lecture

- Nature : **gain malgré une décision non conforme — ne valide rien**
- Position du résultat dans la distribution attendue : centile 46
- Cas comparables : 20 (confiance moyenne), part de perdants 0.45, R moyen 0.04 — ex. FICTIF-0009, FICTIF-0008, FICTIF-0013, FICTIF-0015, FICTIF-0017
- Récurrence : {'n': 20, 'statut': 'sans objet (gain)'}
- R moyen des comparables par régime (R, n) : {'range': (-0.53, 9), 'tendance': (0.66, 7), 'forte_volatilite': (0.22, 4)}

## Ce qui est connu

- processus : [confirmée] mauvaise taille : taille 0.2 ≠ taille prévue 0.1 (> 5%)

## Ce qui reste incertain

- un gain isolé n'est pas une preuve que la décision était bonne

## Ce qui nécessite plus de données

- —

## Décision

- aucune modification
- Erreur confirmée (processus) → règle de prévention testée `PREV-TAILLE`
