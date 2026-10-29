"""Validation chronologique « walk-forward » (sans fuite de données futures).

Pour chaque saison testée S :
  - les modèles sont entraînés uniquement sur les saisons antérieures à S ;
  - leurs poids (stacking) sont fixés sur la fin de cette période d'entraînement ;
  - ils prédisent ensuite tous les matchs de S, dont les variables n'utilisent
    que des matchs déjà joués à la date du match.
La première saison sert de « rodage » aux variables et n'est jamais évaluée.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config, metrics
from .models.ensemble import BASE_MODELS, HalfTimePredictor


def walk_forward(features: pd.DataFrame, min_train_seasons: int = 1,
                 random_state: int = 0) -> pd.DataFrame:
    seasons = sorted(features["season"].unique())
    if len(seasons) < min_train_seasons + 2:
        raise ValueError("Pas assez de saisons pour une validation chronologique")
    burn_in = seasons[0]
    usable = features[features["season"] != burn_in]
    results = []
    for test_season in seasons[1 + min_train_seasons:]:
        train = usable[usable["season"] < test_season]
        test = usable[usable["season"] == test_season]
        if test.empty:
            continue
        predictor = HalfTimePredictor(random_state).fit(train)
        preds = predictor.predict(test)
        for market, out in preds.items():
            h = "h1" if market == "H1_O05" else "h2"
            frame = test[["date", "league", "season", "home", "away", "home_n_matches",
                          "away_n_matches", "market_lambda_total"]].copy()
            frame["market"] = market
            frame["y"] = test[f"y_{h}"].to_numpy()
            frame["baseline_ligue"] = test[f"league_any_{h}"].to_numpy()
            for col in BASE_MODELS + ["probabilite", "ecart_modeles", "prob_basse", "prob_haute"]:
                frame[col] = out[col].to_numpy()
            results.append(frame)
    return pd.concat(results, ignore_index=True)


def evaluate(bt: pd.DataFrame, rules: config.SelectionRules | None = None) -> dict:
    """Mesures globales, par modèle, par saison, par ligue, calibration et haute confiance."""
    rules = rules or config.SELECTION
    report: dict = {}
    for market, g in bt.groupby("market"):
        y = g["y"].to_numpy()
        models = {"ensemble": g["probabilite"], "baseline_ligue": g["baseline_ligue"]}
        for m in BASE_MODELS:
            models[m] = g[m].fillna(g["poisson"])
        per_model = {name: metrics.summary(p.to_numpy(), y) for name, p in models.items()}
        eligible = g[(g["home_n_matches"] >= rules.min_team_matches) &
                     (g["away_n_matches"] >= rules.min_team_matches)]
        report[market] = {
            "global": per_model,
            "par_saison": {s: metrics.summary(x["probabilite"].to_numpy(), x["y"].to_numpy())
                           for s, x in g.groupby("season")},
            "par_ligue": {lg: metrics.summary(x["probabilite"].to_numpy(), x["y"].to_numpy())
                          for lg, x in g.groupby("league")},
            "calibration": metrics.calibration_table(g["probabilite"].to_numpy(), y),
            "haute_confiance": metrics.high_confidence_table(g["probabilite"].to_numpy(), y),
            "haute_confiance_equipes_rodees": metrics.high_confidence_table(
                eligible["probabilite"].to_numpy(), eligible["y"].to_numpy()),
            "selection_regles": selection_backtest(g, rules),
        }
    return report


def selection_backtest(g: pd.DataFrame, rules: config.SelectionRules) -> dict:
    """Applique les règles de sélection (hors cotes, indisponibles dans l'historique)."""
    mask = ((g["probabilite"] >= rules.min_probability) &
            (g["prob_basse"] >= rules.min_lower_bound) &
            (g["ecart_modeles"] <= rules.max_model_spread) &
            (g["home_n_matches"] >= rules.min_team_matches) &
            (g["away_n_matches"] >= rules.min_team_matches))
    sel = g[mask]
    n, k = len(sel), int(sel["y"].sum())
    lo, hi = metrics.wilson_interval(k, n) if n else (float("nan"), float("nan"))
    return {"n_matchs": int(len(g)), "n_selections": n, "taux_selection": n / len(g) if len(g) else 0.0,
            "prob_moyenne_annoncee": float(sel["probabilite"].mean()) if n else float("nan"),
            "taux_reussite": k / n if n else float("nan"), "ic95": [lo, hi],
            "cote_juste_moyenne": float((1 / sel["probabilite"]).mean()) if n else float("nan")}


def bias_by_segment(bt: pd.DataFrame) -> pd.DataFrame:
    """Écart moyen (annoncé - observé) par marché, ligue et tranche : détecte les biais récurrents."""
    df = bt.copy()
    df["tranche"] = pd.cut(df["probabilite"], [0, 0.6, 0.7, 0.8, 0.85, 0.9, 1.0])
    out = (df.groupby(["market", "league", "tranche"], observed=True)
             .agg(n=("y", "size"), annonce=("probabilite", "mean"), observe=("y", "mean"))
             .reset_index())
    out["ecart"] = out["annonce"] - out["observe"]
    return out[out["n"] >= 30].sort_values("ecart", key=np.abs, ascending=False)
