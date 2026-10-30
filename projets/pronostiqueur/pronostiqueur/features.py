"""Calcul des variables d'avant-match, sans fuite d'information future.

Principe : on parcourt les matchs dans l'ordre chronologique. Pour chaque
date, on photographie l'état des équipes AVANT de le mettre à jour avec les
résultats du jour. Une variable d'un match n'utilise donc jamais ce match ni
un match postérieur.

Les moyennes sont pondérées exponentiellement (la forme récente compte plus),
réduites à chaque changement de saison, puis « rétrécies » vers la moyenne de
la ligue (estimation bayésienne empirique) pour ne pas surestimer une équipe
après quelques matchs exceptionnels.

Première et deuxième mi-temps sont suivies séparément.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import config
from .odds import implied_total_goals, remove_margin

TEAM_KEYS = ["h1_for", "h1_against", "h2_for", "h2_against", "h1_any", "h2_any"]
SHOT_KEYS = ["shots_for", "shots_against", "sot_for", "sot_against"]
LEAGUE_KEYS = ["home_h1", "away_h1", "home_h2", "away_h2", "any_h1", "any_h2",
               "shots_home", "shots_away", "sot_home", "sot_away"]
# Valeurs initiales de ligue (écrasées très vite par les vraies données).
LEAGUE_PRIOR = {"home_h1": 0.62, "away_h1": 0.50, "home_h2": 0.85, "away_h2": 0.70,
                "any_h1": 0.70, "any_h2": 0.78, "shots_home": 13.0, "shots_away": 10.5,
                "sot_home": 4.6, "sot_away": 3.8}


@dataclass
class _EWState:
    """Sommes pondérées exponentiellement avec poids total."""

    decay: float
    sums: dict = field(default_factory=lambda: defaultdict(float))
    weights: dict = field(default_factory=lambda: defaultdict(float))
    count: int = 0
    last_season: str | None = None
    last_date: pd.Timestamp | None = None

    def update(self, values: dict, season: str, date: pd.Timestamp, carry_over: float) -> None:
        factor = self.decay
        if self.last_season is not None and season != self.last_season:
            factor *= carry_over
        for key in set(self.sums) | set(values):
            self.sums[key] *= factor
            self.weights[key] *= factor
        for key, value in values.items():
            if value is None or (isinstance(value, float) and math.isnan(value)):
                continue
            self.sums[key] += float(value)
            self.weights[key] += 1.0
        self.count += 1
        self.last_season = season
        self.last_date = date

    def mean(self, key: str, prior: float, strength: float) -> float:
        return (self.sums[key] + strength * prior) / (self.weights[key] + strength)

    def weight(self, key: str) -> float:
        return self.weights[key]


class FeatureBuilder:
    def __init__(self, settings: config.FeatureSettings | None = None):
        self.settings = settings or config.FEATURES
        self.team_decay = 0.5 ** (1.0 / self.settings.half_life_matches)
        self.teams: dict[tuple[str, str], _EWState] = {}
        self.venues: dict[tuple[str, str, str], _EWState] = {}
        self.leagues: dict[str, _EWState] = {}

    # ------------------------------------------------------------------ états
    def _team(self, league: str, team: str) -> _EWState:
        return self.teams.setdefault((league, team), _EWState(self.team_decay))

    def _venue(self, league: str, team: str, venue: str) -> _EWState:
        return self.venues.setdefault((league, team, venue), _EWState(self.team_decay))

    def _league(self, league: str) -> _EWState:
        return self.leagues.setdefault(league, _EWState(0.5 ** (1.0 / 300.0)))

    def league_means(self, league: str) -> dict[str, float]:
        state = self._league(league)
        return {k: state.mean(k, LEAGUE_PRIOR[k], 20.0) for k in LEAGUE_KEYS}

    # ------------------------------------------------------------ variables
    def snapshot(self, league: str, home: str, away: str, date: pd.Timestamp,
                 odds: dict | None = None) -> dict:
        """Variables d'avant-match pour (league, home, away) avec l'état actuel."""
        k = self.settings.shrinkage_matches
        lg = self.league_means(league)
        per_team = {h: (lg[f"home_{h}"] + lg[f"away_{h}"]) / 2 for h in ("h1", "h2")}
        shots_mean = (lg["shots_home"] + lg["shots_away"]) / 2
        sot_mean = (lg["sot_home"] + lg["sot_away"]) / 2
        feats: dict[str, float] = {}

        for side, team, venue in (("home", home, "home"), ("away", away, "away")):
            st = self._team(league, team)
            vs = self._venue(league, team, venue)
            for h in ("h1", "h2"):
                for kind in ("for", "against"):
                    overall = st.mean(f"{h}_{kind}", per_team[h], k)
                    feats[f"{side}_{h}_{kind}"] = overall
                    # Variante lieu (domicile/extérieur) rétrécie vers la valeur globale.
                    feats[f"{side}_{venue}_{h}_{kind}"] = vs.mean(f"{h}_{kind}", overall, k)
                feats[f"{side}_{h}_any"] = st.mean(f"{h}_any", lg[f"any_{h}"], k)
            feats[f"{side}_shots_for"] = st.mean("shots_for", shots_mean, k)
            feats[f"{side}_shots_against"] = st.mean("shots_against", shots_mean, k)
            feats[f"{side}_sot_for"] = st.mean("sot_for", sot_mean, k)
            feats[f"{side}_sot_against"] = st.mean("sot_against", sot_mean, k)
            feats[f"{side}_n_matches"] = float(st.count)
            rest = (date - st.last_date).days if st.last_date is not None else np.nan
            feats[f"{side}_rest_days"] = float(min(rest, 30)) if rest == rest else np.nan

        # Modèle de Poisson par mi-temps (attaque x défense, base ligue).
        for h in ("h1", "h2"):
            base = per_team[h]
            lam_home = lg[f"home_{h}"] * (feats[f"home_{h}_for"] / base) * (feats[f"away_{h}_against"] / base)
            lam_away = lg[f"away_{h}"] * (feats[f"away_{h}_for"] / base) * (feats[f"home_{h}_against"] / base)
            feats[f"poisson_lambda_{h}"] = lam_home + lam_away
            feats[f"poisson_lambda_home_{h}"] = lam_home
            feats[f"poisson_lambda_away_{h}"] = lam_away
            feats[f"league_any_{h}"] = lg[f"any_{h}"]
        total_h1 = lg["home_h1"] + lg["away_h1"]
        total_h2 = lg["home_h2"] + lg["away_h2"]
        feats["league_h1_share"] = total_h1 / (total_h1 + total_h2)

        # Variables de marché (cotes corrigées de la marge), si disponibles.
        odds = odds or {}
        over, under = odds.get("odds_over25"), odds.get("odds_under25")
        if _valid(over) and _valid(under):
            p_over = remove_margin([over, under])[0]
            lam = implied_total_goals(p_over)
            feats["market_p_over25"] = p_over
            feats["market_lambda_total"] = lam
        else:
            feats["market_p_over25"] = np.nan
            feats["market_lambda_total"] = np.nan
        h, d, a = odds.get("odds_home"), odds.get("odds_draw"), odds.get("odds_away")
        if _valid(h) and _valid(d) and _valid(a):
            ph, _, pa = remove_margin([h, d, a])
            feats["market_fav_strength"] = abs(ph - pa)
            feats["market_home_fav"] = float(ph > pa)
        else:
            feats["market_fav_strength"] = np.nan
            feats["market_home_fav"] = np.nan
        return feats

    def update(self, row) -> None:
        """Met à jour les états avec le résultat d'un match terminé."""
        co = self.settings.season_carry_over
        league, season, date = row.league, row.season, row.date
        h1_home, h1_away = row.ht_home, row.ht_away
        h2_home, h2_away = row.ft_home - row.ht_home, row.ft_away - row.ht_away
        any_h1 = float(row.h1_goals > 0)
        any_h2 = float(row.h2_goals > 0)
        home_vals = {"h1_for": h1_home, "h1_against": h1_away, "h2_for": h2_home, "h2_against": h2_away,
                     "h1_any": any_h1, "h2_any": any_h2, "shots_for": row.shots_home,
                     "shots_against": row.shots_away, "sot_for": row.sot_home, "sot_against": row.sot_away}
        away_vals = {"h1_for": h1_away, "h1_against": h1_home, "h2_for": h2_away, "h2_against": h2_home,
                     "h1_any": any_h1, "h2_any": any_h2, "shots_for": row.shots_away,
                     "shots_against": row.shots_home, "sot_for": row.sot_away, "sot_against": row.sot_home}
        self._team(league, row.home).update(home_vals, season, date, co)
        self._team(league, row.away).update(away_vals, season, date, co)
        self._venue(league, row.home, "home").update(home_vals, season, date, co)
        self._venue(league, row.away, "away").update(away_vals, season, date, co)
        self._league(league).update({
            "home_h1": h1_home, "away_h1": h1_away, "home_h2": h2_home, "away_h2": h2_away,
            "any_h1": any_h1, "any_h2": any_h2, "shots_home": row.shots_home,
            "shots_away": row.shots_away, "sot_home": row.sot_home, "sot_away": row.sot_away,
        }, season, date, 1.0)

    def build(self, matches: pd.DataFrame) -> pd.DataFrame:
        """Variables de tous les matchs historiques (ordre chronologique, sans fuite)."""
        matches = matches.sort_values(["date", "league", "home"]).reset_index(drop=True)
        records = []
        for _, day in matches.groupby("date", sort=True):
            snaps = []
            for row in day.itertuples(index=False):
                odds = {c: getattr(row, c) for c in ("odds_over25", "odds_under25", "odds_home",
                                                       "odds_draw", "odds_away")}
                feats = self.snapshot(row.league, row.home, row.away, row.date, odds)
                feats.update({"league": row.league, "season": row.season, "date": row.date,
                              "home": row.home, "away": row.away,
                              "y_h1": int(row.h1_goals > 0), "y_h2": int(row.h2_goals > 0),
                              "y_h1_o15": int(row.h1_goals >= 2), "y_h2_o15": int(row.h2_goals >= 2),
                              "h1_goals": row.h1_goals, "h2_goals": row.h2_goals})
                snaps.append(feats)
            records.extend(snaps)
            for row in day.itertuples(index=False):
                self.update(row)
        return pd.DataFrame.from_records(records)

    def known_teams(self, league: str) -> list[str]:
        return sorted(team for (lg, team) in self.teams if lg == league)


def _valid(x) -> bool:
    return x is not None and not (isinstance(x, float) and math.isnan(x)) and float(x) > 1.0
