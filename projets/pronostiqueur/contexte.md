# Projet : pronostiqueur

_Créé le 2026-10-29 — Dernière mise à jour : 2026-10-29_

## Objectif (une phrase, mesurable)
Estimer des probabilités calibrées de but en 1re et 2e mi-temps (football), validées hors échantillon, et ne retenir que les sélections fiables ; viser 95 % de réussite sur un sous-ensemble à très haute confiance **seulement si les données le démontrent** (borne basse de l'IC95 > 95 %).

## Où on en est
- v0.1 livrée : collecte football-data.co.uk (30 655 matchs, 12 championnats, 2019/20 → 2026/27), base SQLite, variables par mi-temps sans fuite, 6 modèles (Poisson, Dixon-Coles, marché, bayésien, logistique, gradient boosting) combinés hors échantillon, validation walk-forward sur 22 315 matchs, fiche par match, journal + bilan réel, évolution contrôlée (bootstrap) + retour arrière, agent `.claude/agents/pronostiqueur.md`, 14 tests.
- Résultats (simulation) : 2e MT +0,5 annoncée ≥ 90 % → 89,9 % observé (IC95 86,2–92,7 %, 328 matchs). **Objectif 95 % non atteint.** Les cotes du marché portent presque toute l'information (poids ≈ 1 en 2e MT). Dixon-Coles : aucun gain mesurable.
- Rapport : `reports/backtest_report.md`. Limites : `docs/LIMITES_ET_FEUILLE_DE_ROUTE.md`.

## Décisions prises (et pourquoi)
- Source gratuite football-data.co.uk : seule source vérifiée avec scores mi-temps + cotes ; Betclic n'a pas d'API (site bloqué depuis l'étranger) → cotes saisies à la main.
- Module buteurs/passeurs non construit : aucune donnée joueurs fiable (règle : ne rien inventer).
- Combinaison par poids positifs + Platt appris hors échantillon : le stacking libre surestimait les hautes probabilités (annoncé 96 % → observé 86 %).
- Aucun pari automatique ; évolution uniquement via `evolve` (jamais après un pari perdu isolé).

## Prochaine étape
1. Clé API-Football (≈ 20 $/mois) dans `.env` / secret GitHub → compositions, blessures, minutes des buts, puis module joueurs.
2. Enregistrer les cotes Betclic par mi-temps à chaque pronostic (`--cote-h1/--cote-h2 --log`) pour mesurer le rendement réel.

## Tâches Notion
Base/page Notion : _non créée_
