"""Données synthétiques pour les tests (aucun accès réseau)."""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import pytest

from pronostiqueur.odds import poisson_cdf


def make_matches(n_teams: int = 8, seasons=("2223", "2324", "2425"), seed: int = 0,
                 league: str = "XX") -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    teams = [f"Equipe{i}" for i in range(n_teams)]
    attack = dict(zip(teams, rng.uniform(0.7, 1.4, n_teams)))
    defence = dict(zip(teams, rng.uniform(0.7, 1.4, n_teams)))
    rows = []
    date = pd.Timestamp("2022-08-06")
    for season in seasons:
        fixtures = list(itertools.permutations(teams, 2))
        rng.shuffle(fixtures)
        for i in range(0, len(fixtures), n_teams // 2):
            for home, away in fixtures[i:i + n_teams // 2]:
                lam = {}
                for h, base in (("h1", (0.6, 0.45)), ("h2", (0.8, 0.65))):
                    lam[f"{h}_home"] = base[0] * attack[home] * defence[away]
                    lam[f"{h}_away"] = base[1] * attack[away] * defence[home]
                g = {k: rng.poisson(v) for k, v in lam.items()}
                total = sum(lam.values())
                p_over = 1 - poisson_cdf(2, total)
                rows.append({
                    "league": league, "season": season, "date": date, "home": home, "away": away,
                    "ht_home": g["h1_home"], "ht_away": g["h1_away"],
                    "ft_home": g["h1_home"] + g["h2_home"], "ft_away": g["h1_away"] + g["h2_away"],
                    "shots_home": rng.poisson(12), "shots_away": rng.poisson(10),
                    "sot_home": rng.poisson(4), "sot_away": rng.poisson(3),
                    "odds_home": 2.4, "odds_draw": 3.3, "odds_away": 3.0,
                    "odds_over25": round(0.95 / p_over, 2), "odds_under25": round(0.95 / (1 - p_over), 2),
                    "odds_over25_close": np.nan, "odds_under25_close": np.nan,
                    "source": "synthetique", "fetched_at": "2026-01-01T00:00:00+00:00",
                })
            date += pd.Timedelta(days=7)
        date += pd.Timedelta(days=60)
    df = pd.DataFrame(rows)
    df["h1_goals"] = df["ht_home"] + df["ht_away"]
    df["h2_goals"] = df["ft_home"] + df["ft_away"] - df["h1_goals"]
    return df


@pytest.fixture(scope="session")
def synthetic_matches() -> pd.DataFrame:
    return make_matches()
