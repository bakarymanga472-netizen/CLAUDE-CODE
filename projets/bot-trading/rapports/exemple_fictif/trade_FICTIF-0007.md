> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0007 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-01-22 00:00:00 · sortie 2026-01-24 00:00:00 · régime forte_volatilite · net +1.30 % · **0.22 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | anomalie | cause confirmée | [confirmée] dernière barre trop ancienne (> 2 barres) |
| execution | aucune anomalie détectée | — | — |
| processus | aucune anomalie détectée | — | — |
| statistique | non conforme | — | gain malgré une décision NON conforme : ne pas le compter comme une preuve de la règle |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 32163.93 | 32180.02 |
| Taille | 0.1000 | 0.1000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00050 |
| Sortie | — | signal |

## Lecture

- Nature : **gain malgré une décision non conforme — ne valide rien**
- Position du résultat dans la distribution attendue : centile 54
- Cas comparables : 7 (confiance faible), part de perdants 0.43, R moyen 0.07 — ex. FICTIF-0004, FICTIF-0003, FICTIF-0001, FICTIF-0006, FICTIF-0005
- Récurrence : {'n': 7, 'statut': 'échantillon insuffisant'}
- R moyen des comparables par régime (R, n) : {'forte_volatilite': (0.37, 4), 'tendance': (-0.22, 1), 'range': (-0.37, 2)}

## Ce qui est connu

- donnees : [confirmée] dernière barre trop ancienne (> 2 barres)

## Ce qui reste incertain

- un gain isolé n'est pas une preuve que la décision était bonne

## Ce qui nécessite plus de données

- au moins 20 trades comparables (actuellement 7)

## Décision

- aucune modification
- Erreur confirmée (donnees) → règle de prévention testée `PREV-DONNEES`
