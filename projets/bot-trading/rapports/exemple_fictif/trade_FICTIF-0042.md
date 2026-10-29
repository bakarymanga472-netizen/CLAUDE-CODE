> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0042 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-05-07 00:00:00 · sortie 2026-05-09 00:00:00 · régime tendance · net -2.32 % · **-0.39 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | aucune anomalie détectée | — | — |
| execution | aucune anomalie détectée | — | — |
| processus | anomalie | cause confirmée | [confirmée] signal non conforme : règles non satisfaites : ['rendement_30j>0'] |
| statistique | non conforme | — | perte avec décision non conforme : la non-conformité est une cause possible, pas certaine |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 50390.70 | 50415.90 |
| Taille | 0.1000 | 0.1000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00050 |
| Sortie | — | signal |

## Lecture

- Nature : **perte liée (au moins en partie) à un défaut de processus, d'exécution ou de données**
- Position du résultat dans la distribution attendue : centile 29
- Cas comparables : 20 (confiance moyenne), part de perdants 0.60, R moyen -0.12 — ex. FICTIF-0020, FICTIF-0006, FICTIF-0024, FICTIF-0032, FICTIF-0031
- Récurrence : {'pertes_comparables': 12, 'n': 20, 'taux_attendu': 0.4355, 'p_valeur': 0.10463926112984474}

## Ce qui est connu

- processus : [confirmée] signal non conforme : règles non satisfaites : ['rendement_30j>0']

## Ce qui reste incertain

- —

## Ce qui nécessite plus de données

- —

## Décision

- aucune modification de stratégie : une perte isolée ne justifie pas de changement
- Erreur confirmée (processus) → règle de prévention testée `PREV-REGLES`
