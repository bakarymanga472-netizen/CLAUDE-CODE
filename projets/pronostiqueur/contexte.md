# Projet : pronostiqueur

_Créé le 2026-10-29 — Dernière mise à jour : 2026-10-29_

## Objectif (une phrase, mesurable)
Estimer des probabilités calibrées de but en 1re et 2e mi-temps (football), validées hors échantillon, et ne retenir que les sélections fiables ; viser 95 % de réussite sur un sous-ensemble à très haute confiance **seulement si les données le démontrent** (borne basse de l'IC95 > 95 %).

## Où on en est
- v0.1 livrée : collecte football-data.co.uk (30 655 matchs, 12 championnats, 2019/20 → 2026/27), base SQLite, variables par mi-temps sans fuite, 6 modèles (Poisson, Dixon-Coles, marché, bayésien, logistique, gradient boosting) combinés hors échantillon, validation walk-forward sur 22 315 matchs, fiche par match, journal + bilan réel, évolution contrôlée (bootstrap) + retour arrière, agent `.claude/agents/pronostiqueur.md`, 14 tests.
- Résultats (simulation) : 2e MT +0,5 annoncée ≥ 90 % → 89,9 % observé (IC95 86,2–92,7 %, 328 matchs). **Objectif 95 % non atteint.** Les cotes du marché portent presque toute l'information (poids ≈ 1 en 2e MT). Dixon-Coles : aucun gain mesurable.
- 2026-10-30 : marchés **+1,5 but par mi-temps** ajoutés (modèles, cible et calibration propres ; la déduction directe depuis le +0,5 surestimait : 73 % annoncé → 66 % observé). Backtest 22 315 matchs : 2e MT +1,5 annoncé 54/62/67/73 % → observé 53/59/65/76 % ; Brier meilleur que la ligue. Commande `tableau matchs.csv` = tableau de synthèse demandé (Match · Buts attendus · Part 2e MT · 2e MT +0,5 · 2e MT +1,5 · 1re MT +0,5 · Alertes).
- Rapport : `reports/backtest_report.md`. Limites : `docs/LIMITES_ET_FEUILLE_DE_ROUTE.md`.

## Décisions prises (et pourquoi)
- Source gratuite football-data.co.uk : seule source vérifiée avec scores mi-temps + cotes ; Betclic n'a pas d'API (site bloqué depuis l'étranger) → cotes saisies à la main.
- Module buteurs/passeurs non construit : aucune donnée joueurs fiable (règle : ne rien inventer).
- Combinaison par poids positifs + Platt appris hors échantillon : le stacking libre surestimait les hautes probabilités (annoncé 96 % → observé 86 %).
- Aucun pari automatique ; évolution uniquement via `evolve` (jamais après un pari perdu isolé).
- footballsoccerapi.com testé le 2026-10-30 (clé gratuite) : 50 appels/jour, **uniquement les résultats de la veille** (score final + mi-temps, arbitre, météo). Événements, compositions, absences, matchs à venir et cotes → offres payantes Archive/Live (403 `plan_required`). Inutile pour prédire ; au mieux pour accélérer les bilans. Prix non vérifiés (site bloqué par Cloudflare depuis le cloud). Variable prévue : `FSA_API_KEY`.

- API-Football (offre gratuite, 2026-10-30) : saisons 2022-2024 seulement, 100 appels/jour, **10/min** ; pas de paramètre `ids`. Compte **suspendu** après une rafale d'appels non espacés lors du premier lancement (erreur corrigée : espacement 6,5 s). Connecteur `pronostiqueur/data/api_football.py`, variable `API_FOOTBALL_KEY`.
- **Absences : aucune valeur ajoutée mesurée** (`experiments/valeur_absences.py`, E0/E1/D1 2022-2024, 3 713 matchs, test hors échantillon 2023/24 + 2024/25 = 2 475 matchs) : log-loss 1re MT 0,5701 → 0,5746, 2e MT 0,4877 → 0,4899 avec les absences (pire) ; variantes à une variable : gain nul (IC95 contient 0, P(mieux) ≤ 27 %). Les cotes intègrent déjà les absences. Limite : absents comptés, non pondérés par l'importance du joueur.

## Prochaine étape
1. Ne pas payer API-Football pour les absences (aucun gain mesuré). Ne le reconsidérer que pour un module joueurs (buteurs/passeurs), à tester d'abord sur 2022-2024 si le compte est réactivé.
2. Enregistrer les cotes Betclic par mi-temps à chaque pronostic (`--cote-h1/--cote-h2 --log`) pour mesurer le rendement réel.

## Tâches Notion
Base/page Notion : _non créée_
