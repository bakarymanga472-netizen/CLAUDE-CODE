# Pronostiqueur — IA de prédiction des buts par mi-temps

Système **d'analyse et de simulation** qui estime la probabilité qu'au moins
un but soit marqué en **1re mi-temps** et en **2e mi-temps** d'un match de
football, la compare aux cotes, et ne retient que les sélections dont les
données sont fiables. **Aucun pari n'est placé automatiquement.**

> ⚠️ Les paris sportifs comportent un risque de perte. Ce projet ne garantit
> aucun gain. Aide : Joueurs Info Service, 09 74 75 13 13 (appel non surtaxé).

## État du projet (version 0.1, 29/10/2026)

| Fonctionnalité | État |
|---|---|
| Collecte de 30 655 matchs (12 championnats, 2019/20 → 2026/27) avec scores mi-temps et cotes | ✅ Fait et testé |
| Contrôle qualité, base SQLite horodatée | ✅ |
| Variables par mi-temps sans fuite de données futures | ✅ (test automatique) |
| 5 modèles par mi-temps (Poisson, marché, bayésien, logistique, gradient boosting) combinés selon leur performance hors échantillon | ✅ |
| Validation chronologique (walk-forward), Brier, log-loss, calibration, IC95 | ✅ |
| Fiche par match au format demandé (probabilité, fourchette, cote juste, statut) | ✅ |
| Journal des pronostics, règlement après match, bilan réel | ✅ |
| Évolution contrôlée des modèles + retour arrière | ✅ |
| Agent Claude Code `pronostiqueur` | ✅ `.claude/agents/pronostiqueur.md` |
| Buteurs / passeurs décisifs | ❌ **Non implémenté** : données joueurs non connectées |
| Compositions, blessures, xG, minutes des buts, cotes par mi-temps | ❌ Non disponibles dans la source actuelle |

Détails : [docs/AUDIT_SOURCES.md](docs/AUDIT_SOURCES.md) ·
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) ·
[docs/LIMITES_ET_FEUILLE_DE_ROUTE.md](docs/LIMITES_ET_FEUILLE_DE_ROUTE.md)

## Résultats de la validation (simulation, pas des paris réels)

22 315 matchs prédits saison par saison, chacun par un modèle qui n'avait vu
que le passé. Rapport complet : [reports/backtest_report.md](reports/backtest_report.md).

| Marché | Taux de base | Sélections annoncées ≥ 90 % | Réussite observée (IC95) |
|---|---|---|---|
| +0,5 but 2e mi-temps | 79,4 % | 328 (1,5 % des matchs) | **89,9 %** (86,2 – 92,7 %) |
| +0,5 but 1re mi-temps | 71,2 % | 19 | 100 % (83,2 – 100 %), échantillon trop petit |

Ce que ces chiffres montrent :
- Les probabilités sont **bien calibrées** : annoncé 91,5 %, observé 89,9 % sur
  la 2e mi-temps ; écart moyen de calibration 0,6 %.
- **Les cotes du marché contiennent déjà presque toute l'information.** Pour la
  2e mi-temps, l'ensemble donne 99,8 % du poids au modèle de marché.
- **L'objectif de 95 % n'est pas atteint.** Au seuil 95 %, il n'y a que 9
  sélections en 6 saisons (8 réussies) : rien n'est démontré. Ne jamais
  présenter ce système comme fiable à 95 %.
- Le rendement financier ne peut pas être calculé : l'historique ne contient
  pas les cotes par mi-temps.

## Installation

```bash
pip install -r requirements.txt
python -m pronostiqueur fetch          # télécharge et contrôle l'historique (~2 min)
python -m pronostiqueur backtest       # validation chronologique + rapports
python -m pronostiqueur train          # met un modèle en production
```

## Utilisation

```bash
# Fiche d'un match (cotes Betclic saisies à la main)
python -m pronostiqueur predict --league F1 --home "Le Havre" --away "Paris SG" \
  --date 2026-10-30 --over25 1.33 --under25 3.32 --cote-1 9.25 --cote-n 6.40 --cote-2 1.20 \
  --cote-h2 1.12 --log

python -m pronostiqueur settle --refresh   # après les matchs : règle le journal
python -m pronostiqueur report             # bilan réel (séparé de la simulation)
python -m pronostiqueur evolve             # teste de nouveaux réglages, promotion si gain prouvé
python -m pronostiqueur rollback           # revient à la version précédente
```

Codes ligues : `E0` Premier League, `E1` Championship, `D1`/`D2` Bundesliga 1/2,
`I1` Serie A, `SP1` LaLiga, `F1`/`F2` Ligue 1/2, `N1` Eredivisie,
`P1` Liga Portugal, `T1` Süper Lig, `B1` Pro League.

Statuts : **Sélection admissible** (probabilité ≥ 80 %, borne basse ≥ 75 %,
modèles d'accord, historique suffisant, cote ≥ cote juste) · **À surveiller** ·
**Données insuffisantes** · **À éviter**. Sans cote saisie, aucun match ne peut
être « admissible » : la valeur ne peut pas être vérifiée.

## Comment le système évolue

1. Chaque pronostic journalisé est réglé après le match (`settle`) et comparé
   à la probabilité annoncée (`report`).
2. Chaque semaine, le workflow GitHub `evaluation-hebdomadaire` met les données
   à jour, relance la validation, teste des réglages candidats et réentraîne le
   modèle ; les rapports sont publiés en artefacts.
3. Un réglage n'est promu que s'il bat la production sur des matchs récents
   jamais vus, dans au moins 95 % des rééchantillonnages. Un pari perdu isolé
   ne modifie jamais rien.

## Tests

```bash
python -m pytest -q
```
