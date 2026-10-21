> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0015 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-02-15 00:00:00 · sortie 2026-02-17 00:00:00 · régime range · net -4.64 % · **-0.77 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | aucune anomalie détectée | — | — |
| execution | anomalie | cause confirmée | [confirmée] ordre(s) rejeté(s) : ['O15-0'] |
| processus | aucune anomalie détectée | — | — |
| statistique | non conforme | — | perte avec décision non conforme : la non-conformité est une cause possible, pas certaine |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 29126.60 | 29141.16 |
| Taille | 0.1000 | 0.1000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00050 |
| Sortie | — | signal |

## Lecture

- Nature : **perte liée (au moins en partie) à un défaut de processus, d'exécution ou de données**
- Position du résultat dans la distribution attendue : centile 17
- Cas comparables : 15 (confiance faible), part de perdants 0.40, R moyen 0.15 — ex. FICTIF-0000, FICTIF-0011, FICTIF-0013, FICTIF-0002, FICTIF-0008
- Récurrence : {'n': 15, 'statut': 'échantillon insuffisant'}

## Ce qui est connu

- execution : [confirmée] ordre(s) rejeté(s) : ['O15-0']

## Ce qui reste incertain

- —

## Ce qui nécessite plus de données

- au moins 20 trades comparables (actuellement 15)

## Décision

- aucune modification de stratégie : une perte isolée ne justifie pas de changement
- Erreur confirmée (execution) → règle de prévention testée `PREV-ORDRE`
