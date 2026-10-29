# Pronostiqueur — consignes pour Claude

- Projet Python : IA de prédiction des buts par mi-temps (analyse et simulation uniquement, aucun pari automatique).
- Agent dédié : `.claude/agents/pronostiqueur.md` (pronostics, bilans).
- Avant tout commit : `python -m pytest -q` doit passer.
- Ne jamais committer `data/`, `models_store/` ni de clé API (variables d'environnement uniquement).
- Toute nouvelle variable ou réglage doit prouver un gain hors échantillon (`backtest`, `evolve`) avant d'être conservé.
- Les limites et ce qui n'est pas implémenté sont listés dans `docs/LIMITES_ET_FEUILLE_DE_ROUTE.md` : ne pas les présenter comme disponibles.
