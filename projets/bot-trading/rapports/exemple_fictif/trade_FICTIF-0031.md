> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0031 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-04-04 00:00:00 · sortie 2026-04-06 00:00:00 · régime tendance · net -4.61 % · **-0.77 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | aucune anomalie détectée | — | — |
| execution | anomalie | cause confirmée | [confirmée] glissement 8.0× l'attendu |
| processus | aucune anomalie détectée | — | — |
| statistique | non conforme | — | perte avec décision non conforme : la non-conformité est une cause possible, pas certaine |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 20777.21 | 20787.60 |
| Taille | 0.1000 | 0.1000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00400 |
| Sortie | — | signal |

## Lecture

- Nature : **perte liée (au moins en partie) à un défaut de processus, d'exécution ou de données**
- Position du résultat dans la distribution attendue : centile 17
- Cas comparables : 20 (confiance moyenne), part de perdants 0.45, R moyen 0.05 — ex. FICTIF-0024, FICTIF-0020, FICTIF-0019, FICTIF-0006, FICTIF-0003
- Récurrence : {'pertes_comparables': 9, 'n': 20, 'taux_attendu': 0.4355, 'p_valeur': 0.533651473850856}

## Ce qui est connu

- execution : [confirmée] glissement 8.0× l'attendu

## Ce qui reste incertain

- —

## Ce qui nécessite plus de données

- —

## Décision

- aucune modification de stratégie : une perte isolée ne justifie pas de changement
- Erreur confirmée (execution) → règle de prévention testée `PREV-GLISSEMENT`
