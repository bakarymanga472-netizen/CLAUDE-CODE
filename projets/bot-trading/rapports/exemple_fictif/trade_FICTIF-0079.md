> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.

# Rapport post-trade FICTIF-0079 — BTCUSDT-FICTIF — tendance tendance-1d-v0-FICTIF

Entrée 2026-08-26 00:00:00 · sortie 2026-08-28 00:00:00 · régime range · net -0.99 % · **-0.16 R**

## Diagnostic

| Catégorie | Statut | Niveau de preuve | Constats |
|---|---|---|---|
| donnees | aucune anomalie détectée | — | — |
| execution | aucune anomalie détectée | — | — |
| processus | aucune anomalie détectée | — | — |
| statistique | conforme | — | perte malgré une décision conforme : résultat statistique (cause inconnue au-delà du hasard) |

## Plan contre exécution

| | Prévu | Réalisé |
|---|---|---|
| Prix d'entrée | 27546.85 | 27560.62 |
| Taille | 0.1000 | 0.1000 |
| Coûts | {'frais': 0.001, 'glissement': 0.0005} | frais 0.00200, glissement 0.00050 |
| Sortie | — | signal |

## Lecture

- Nature : **perte normale : dans la distribution attendue de la stratégie**
- Position du résultat dans la distribution attendue : centile 37
- Cas comparables : 20 (confiance moyenne), part de perdants 0.65, R moyen -0.32 — ex. FICTIF-0035, FICTIF-0009, FICTIF-0033, FICTIF-0048, FICTIF-0022
- Récurrence : {'pertes_comparables': 13, 'n': 20, 'taux_attendu': 0.4355, 'p_valeur': 0.044183650574308155}

## Ce qui est connu

- aucune anomalie confirmée

## Ce qui reste incertain

- la récurrence est statistique ; elle doit être confirmée sur des données distinctes

## Ce qui nécessite plus de données

- —

## Décision

- hypothèse ajoutée au registre ; la stratégie n'est PAS modifiée avant validation
- Hypothèse : Les trades tendance proches de ce contexte (régime range) perdent plus souvent qu'attendu (13/20 contre 44%). (p = 0.044)
- Protocole : Définir le filtre à partir des seuls trades antérieurs à la date du jour ; le tester sur des données historiques distinctes (walk-forward) avec coûts ×1 et ×3 ; accepter seulement si l'espérance par trade augmente et la pire baisse ne se dégrade pas de plus de 10 %.
