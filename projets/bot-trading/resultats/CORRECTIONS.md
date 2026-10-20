# Corrections après audit (2026-10-21)

Les rapports d'origine de ce dossier ne sont PAS réécrits (règle : ne jamais réécrire l'historique). Ce fichier indique
lesquels sont affectés par les anomalies de `audit/rapport_audit_aladdin.md` et où trouver les chiffres corrigés.

| Rapport d'origine | Anomalies qui l'affectent | Statut | Chiffres corrigés |
|---|---|---|---|
| aladdin_rapport.md (walk-forward « +22 %/an ») | 1 (ce n'est pas la structure crypto), survivance | **Ne plus citer** | Momentum crypto rejeté : audit §7 |
| aladdin_reussite.md | 2, 3, 5, 7 | Résultats biaisés (exécution le jour du signal, coffre vu) | rapports/rebond_corrige.md |
| aladdin_enquete.md | 2, 3, 6, 7 | Idem | rapports/rebond_corrige.md |
| aladdin_sorties.md (84/78/79 %) | 2, 4, 7, 8 | Mesurés sur GC=F, rendement additionné | rapports/rebond_corrige.md (SPY+GLD, séances réelles) : 83/80/82 % de réussite, mais statut **non validée** (ne bat que 79 % des entrées au hasard en Sharpe) |
| aladdin_rebond_journal.csv (trade SPY « ouvert » du 2026-10-15) | 4 | Artefact du calendrier 7j/7 : avec les vraies séances, RSI-2 du 14/10 = 7,5 → pas de signal | resultats/aladdin_rebond_journal_v2.csv |

Code corrigé : `aladdin/live_rebond.py` (utilise le code du backtest corrigé), `aladdin/alpaca.py` (garde-fous, idempotence,
pas d'ordre si la stratégie n'est pas « candidate démo »), `aladdin/desks.py` (covariance, fenêtre libre).
Non corrigés volontairement : `aladdin/reussite.py`, `enquete.py`, `sorties.py`, `recherche.py` (scripts de recherche historiques, remplacés par `labo/`).
