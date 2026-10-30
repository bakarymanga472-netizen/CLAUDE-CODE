"""Connecteur API-Football (api-sports.io, v3).

Fournit les matchs, les absences (blessures, suspensions), les compositions et
les événements (minute des buts). La clé est lue dans la variable
d'environnement API_FOOTBALL_KEY et n'est jamais écrite ni affichée.

L'offre gratuite (100 appels par jour) ne couvre que les saisons 2022 à 2024 :
toute erreur renvoyée par l'API (offre, quota, paramètre) lève DataSourceError
au lieu de produire des données partielles ou inventées.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

from .. import config
from .football_data_uk import DataSourceError, _ssl_context

BASE_URL = "https://v3.football.api-sports.io"
SOURCE_NAME = "api-football"
KEY_ENV = "API_FOOTBALL_KEY"

# Correspondance codes football-data.co.uk -> identifiants de ligue API-Football.
LEAGUE_IDS: dict[str, int] = {
    "E0": 39, "E1": 40, "D1": 78, "D2": 79, "I1": 135, "SP1": 140,
    "F1": 61, "F2": 62, "N1": 88, "P1": 94, "T1": 203, "B1": 144,
}


def season_year(season: str) -> int:
    """« 2324 » (football-data.co.uk) -> 2023 (année de début, API-Football)."""
    return 2000 + int(season[:2])


def _cache_dir() -> Path:
    return config.RAW_DIR / "api_football"


# L'offre gratuite limite à 10 appels par minute : on espace les appels réels.
MIN_INTERVAL_S = 6.5
_last_call = 0.0


def _throttle() -> None:
    global _last_call
    wait = MIN_INTERVAL_S - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def _cache_path(endpoint: str, params: dict) -> Path:
    query = urllib.parse.urlencode(sorted(params.items()))
    return _cache_dir() / f"{endpoint.replace('/', '_')}__{query.replace('&', '_').replace('=', '-')}.json"


def get(endpoint: str, params: dict, *, refresh: bool = False, retries: int = 3,
        timeout: float = 30.0) -> dict:
    """Appelle l'API (ou lit le cache local) et renvoie la réponse JSON complète."""
    query = urllib.parse.urlencode(sorted(params.items()))
    cache = _cache_path(endpoint, params)
    if cache.exists() and not refresh:
        return json.loads(cache.read_text())

    key = os.environ.get(KEY_ENV)
    if not key:
        raise DataSourceError(f"Variable d'environnement {KEY_ENV} absente : aucune donnée API-Football.")
    url = f"{BASE_URL}/{endpoint}?{query}"
    request = urllib.request.Request(url, headers={"x-apisports-key": key, "User-Agent": config.USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            _throttle()
            with urllib.request.urlopen(request, timeout=timeout, context=_ssl_context()) as resp:
                payload = json.loads(resp.read())
            errors = payload.get("errors")
            if isinstance(errors, dict) and "rateLimit" in errors:
                last_error = DataSourceError(str(errors))
                time.sleep(61)
                continue
            if errors:
                # Erreur métier (offre, quota, paramètre) : inutile de réessayer.
                raise DataSourceError(f"API-Football {endpoint} {params} : {errors}")
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(payload))
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise DataSourceError(f"Clé API-Football refusée ({exc.code}).") from exc
            last_error = exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
        time.sleep(2 ** attempt)
    raise DataSourceError(f"Échec API-Football après {retries} tentatives : {endpoint} ({last_error})")


def fixtures(league: str, season: str, **kw) -> pd.DataFrame:
    """Matchs terminés d'une ligue et d'une saison (un seul appel)."""
    payload = get("fixtures", {"league": LEAGUE_IDS[league], "season": season_year(season)}, **kw)
    rows = []
    for item in payload["response"]:
        fx, teams, score = item["fixture"], item["teams"], item["score"]
        if fx["status"]["short"] not in ("FT", "AET", "PEN"):
            continue
        rows.append({
            "fixture_id": fx["id"],
            "kickoff_utc": pd.Timestamp(fx["date"]).tz_convert("UTC"),
            "league": league,
            "season": season,
            "api_home": teams["home"]["name"],
            "api_away": teams["away"]["name"],
            "api_home_id": teams["home"]["id"],
            "api_away_id": teams["away"]["id"],
            "ht_home": score["halftime"]["home"],
            "ht_away": score["halftime"]["away"],
            "ft_home": score["fulltime"]["home"],
            "ft_away": score["fulltime"]["away"],
        })
    return pd.DataFrame(rows)


def injuries(league: str, season: str, **kw) -> pd.DataFrame:
    """Absences déclarées par match pour une ligue et une saison (un seul appel)."""
    payload = get("injuries", {"league": LEAGUE_IDS[league], "season": season_year(season)}, **kw)
    rows = [{
        "fixture_id": item["fixture"]["id"],
        "team_id": item["team"]["id"],
        "player_id": item["player"]["id"],
        "type": item["player"]["type"],
        "reason": item["player"]["reason"],
    } for item in payload["response"]]
    return pd.DataFrame(rows, columns=["fixture_id", "team_id", "player_id", "type", "reason"])
