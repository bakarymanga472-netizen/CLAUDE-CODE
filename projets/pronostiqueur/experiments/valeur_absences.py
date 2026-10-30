"""Expérience : les absences (API-Football) améliorent-elles les prédictions ?

Question : à probabilité du modèle en production fixée (prédictions hors
échantillon du backtest walk-forward), le nombre d'absents déclarés avant le
match réduit-il la log-loss sur des saisons jamais vues ?

Protocole (sans fuite) :
- matchs API-Football reliés aux matchs football-data.co.uk par ligue, date
  (±1 jour) et scores mi-temps + final, puis correspondance des noms d'équipes
  par vote majoritaire ;
- variables : absents « Missing Fixture » et « Questionable » par équipe, et
  écart à la moyenne de l'équipe sur ses matchs précédents de la saison ;
- validation chronologique : apprentissage sur les saisons antérieures, test
  sur la saison suivante (2023/24 puis 2024/25) ;
- comparaison A = recalibrage de la probabilité seule, B = A + absences ;
  bootstrap apparié sur l'écart de log-loss.

Usage : python experiments/valeur_absences.py  (cache API déjà rempli)

Résultat du 2026-10-30 (E0, E1, D1, 2022-2024 ; 2 475 matchs de test) : les
absences dégradent la log-loss (1re MT 0,5701 → 0,5746 ; 2e MT 0,4877 →
0,4899) et les variantes à une seule variable n'apportent aucun gain
significatif. Conclusion : les cotes intègrent déjà l'information.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pronostiqueur import config  # noqa: E402
from pronostiqueur.data import api_football as af, storage  # noqa: E402
from pronostiqueur.data.football_data_uk import DataSourceError  # noqa: E402

SEASONS = ["2223", "2324", "2425"]


def link_fixtures(fx: pd.DataFrame, fd: pd.DataFrame) -> pd.DataFrame:
    """Associe chaque match API-Football à un match football-data.co.uk."""
    fx = fx.copy()
    fx["date"] = fx["kickoff_utc"].dt.tz_localize(None).dt.normalize()
    votes: dict[tuple[str, str], Counter] = {}
    for lg, g in fx.groupby("league"):
        cand = fd[fd["league"] == lg]
        by_key = cand.groupby(["ht_home", "ht_away", "ft_home", "ft_away"])
        groups = {k: v for k, v in by_key}
        for row in g.itertuples():
            pool = groups.get((row.ht_home, row.ht_away, row.ft_home, row.ft_away))
            if pool is None:
                continue
            near = pool[(pool["date"] - row.date).abs() <= pd.Timedelta(days=1)]
            if len(near) == 1:
                hit = near.iloc[0]
                votes.setdefault((lg, row.api_home), Counter())[hit["home"]] += 1
                votes.setdefault((lg, row.api_away), Counter())[hit["away"]] += 1
    names = {k: c.most_common(1)[0][0] for k, c in votes.items()}
    fx["home"] = [names.get((lg, t)) for lg, t in zip(fx["league"], fx["api_home"])]
    fx["away"] = [names.get((lg, t)) for lg, t in zip(fx["league"], fx["api_away"])]
    fx = fx.dropna(subset=["home", "away"])
    merged = fx.merge(fd[["league", "date", "home", "away", "ft_home", "ft_away"]],
                      on=["league", "home", "away"], suffixes=("", "_fd"))
    merged = merged[((merged["date_fd"] - merged["date"]).abs() <= pd.Timedelta(days=1))
                    & (merged["ft_home"] == merged["ft_home_fd"]) & (merged["ft_away"] == merged["ft_away_fd"])]
    return merged.drop_duplicates("fixture_id")


def absence_features(linked: pd.DataFrame, inj: pd.DataFrame) -> pd.DataFrame:
    """Absents par équipe et écart à la moyenne passée de l'équipe (causal)."""
    counts = (inj.assign(missing=inj["type"].eq("Missing Fixture"), doubt=inj["type"].eq("Questionable"))
              .groupby(["fixture_id", "team_id"])[["missing", "doubt"]].sum().reset_index())
    out = linked.copy()
    for side in ("home", "away"):
        c = counts.rename(columns={"team_id": f"api_{side}_id", "missing": f"{side}_missing", "doubt": f"{side}_doubt"})
        out = out.merge(c, on=["fixture_id", f"api_{side}_id"], how="left")
        out[[f"{side}_missing", f"{side}_doubt"]] = out[[f"{side}_missing", f"{side}_doubt"]].fillna(0)
    # Écart à la moyenne des matchs précédents de la même équipe dans la saison.
    long = pd.concat([
        out[["fixture_id", "kickoff_utc", "season", "api_home_id", "home_missing"]]
        .rename(columns={"api_home_id": "team_id", "home_missing": "missing"}),
        out[["fixture_id", "kickoff_utc", "season", "api_away_id", "away_missing"]]
        .rename(columns={"api_away_id": "team_id", "away_missing": "missing"}),
    ]).sort_values("kickoff_utc")
    long["prior_mean"] = (long.groupby(["season", "team_id"])["missing"]
                          .transform(lambda s: s.shift().expanding().mean()))
    for side in ("home", "away"):
        pm = long.rename(columns={"team_id": f"api_{side}_id", "prior_mean": f"{side}_prior"})[
            ["fixture_id", f"api_{side}_id", f"{side}_prior"]]
        out = out.merge(pm, on=["fixture_id", f"api_{side}_id"], how="left")
        out[f"{side}_excess"] = out[f"{side}_missing"] - out[f"{side}_prior"].fillna(out[f"{side}_missing"])
    return out


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _logloss(y, p):
    p = np.clip(p, 1e-12, 1 - 1e-12)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


FEATURES = ["home_missing", "away_missing", "home_doubt", "away_doubt", "home_excess", "away_excess"]


def evaluate(data: pd.DataFrame, market: str, n_boot: int = 2000, seed: int = 0) -> dict:
    d = data[data["market"] == market].copy()
    d["z"] = _logit(d["probabilite"].to_numpy())
    losses_a, losses_b = [], []
    for test_season in SEASONS[1:]:
        train = d[d["season"] < test_season]
        test = d[d["season"] == test_season]
        if len(train) < 500 or len(test) < 200:
            continue
        a = LogisticRegression(C=1e6, max_iter=1000).fit(train[["z"]], train["y"])
        b = LogisticRegression(C=1.0, max_iter=1000).fit(train[["z"] + FEATURES], train["y"])
        losses_a.append(_logloss(test["y"].to_numpy(), a.predict_proba(test[["z"]])[:, 1]))
        losses_b.append(_logloss(test["y"].to_numpy(), b.predict_proba(test[["z"] + FEATURES])[:, 1]))
        coefs = dict(zip(["z"] + FEATURES, np.round(b.coef_[0], 4)))
    la, lb = np.concatenate(losses_a), np.concatenate(losses_b)
    diff = la - lb  # > 0 : les absences améliorent
    rng = np.random.default_rng(seed)
    boots = np.array([diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(n_boot)])
    return {
        "marche": market, "n_test": len(diff),
        "logloss_sans": round(la.mean(), 5), "logloss_avec": round(lb.mean(), 5),
        "gain_moyen": round(diff.mean(), 6),
        "ic95_gain": (round(np.quantile(boots, 0.025), 6), round(np.quantile(boots, 0.975), 6)),
        "p_amelioration": round((boots > 0).mean(), 3),
        "coefficients_derniere_saison": coefs,
    }


def main() -> None:
    # Relit le cache JSON du connecteur ; les ligues-saisons absentes du cache sont ignorées.
    fx_parts, inj_parts = [], []
    for lg in config.LEAGUES:
        for s in SEASONS:
            try:
                fx_parts.append(af.fixtures(lg, s))
                inj_parts.append(af.injuries(lg, s).assign(league=lg, season=s))
            except DataSourceError:
                continue
    fx, inj = pd.concat(fx_parts), pd.concat(inj_parts)
    covered = inj.groupby(["league", "season"]).size()
    covered = covered[covered > 200].index  # ligue-saison sans absences déclarées = non couverte
    fd = storage.read_matches(storage.connect())
    fd = fd[fd["season"].isin(SEASONS)]
    linked = link_fixtures(fx, fd)
    print(f"Matchs API reliés : {len(linked)}/{len(fx)}")
    feats = absence_features(linked, inj)
    feats = feats[[(lg, s) in set(covered) for lg, s in zip(feats["league"], feats["season"])]]
    bt = pd.read_csv(config.REPORTS_DIR / "backtest_predictions.csv", dtype={"season": str},
                     parse_dates=["date"])
    data = bt.merge(feats[["league", "home", "away", "date_fd"] + FEATURES].rename(columns={"date_fd": "date"}),
                    on=["league", "home", "away", "date"])
    print(f"Prédictions hors échantillon avec absences : {len(data)} lignes, "
          f"ligues-saisons couvertes : {len(covered)}")
    print(data.groupby("season")[["home_missing", "away_missing"]].mean().round(2))
    for market in config.MARKETS:
        print(evaluate(data, market))


if __name__ == "__main__":
    main()
