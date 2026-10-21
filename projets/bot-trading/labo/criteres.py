"""Critères de décision FIXÉS AVANT le premier test (2026-10-20). Ne pas les modifier après avoir vu des résultats :
toute modification doit passer par un nouvel identifiant de version et être notée dans registre/modifications."""
VERSION = "criteres-v1-2026-10-20"

DEVELOPPEMENT = ("2017-08-17", "2021-12-31")
VALIDATION = ("2022-01-01", "2023-12-31")
COFFRE = ("2024-01-01", "2100-01-01")          # ouvert une seule fois, ne sert qu'à rejeter
WALK_FORWARD_ANNEES = list(range(2019, 2024))  # sélection sur [début, Y-1], application sur Y ; 2019-2023

SHARPE_MIN_OOS = 0.5
DSR_MIN = 0.95
PBO_MAX = 0.5
TRADES_MIN_OOS = 30
STRESS_COUTS = 3.0          # Sharpe OOS doit rester > 0 avec coûts ×3
PERCENTILE_HASARD = 0.95    # doit battre 95 % des expositions aléatoires de même profil
SHARPE_MIN_COFFRE = 0.0
P_SUPERIORITE = 0.05        # « supérieure à la référence » seulement si bootstrap p < 0,05
