"""Connecteur football-data.co.uk.

Source gratuite (usage personnel, voir docs/AUDIT_SOURCES.md) qui fournit pour
chaque match : scores à la mi-temps et finaux, tirs, tirs cadrés, et cotes
1N2 / plus-moins 2,5 buts (ouverture et clôture, plusieurs bookmakers).

Ce module :
- télécharge les fichiers CSV avec cache local, délai d'attente et nouvelles
  tentatives espacées (sans jamais contourner de protection) ;
- normalise les colonnes, qui varient selon les saisons ;
- horodate et identifie la source de chaque ligne.
"""

from __future__ import annotations

import io
import os
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .. import config

BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"
SOURCE_NAME = "football-data.co.uk"

# Colonnes candidates par ordre de préférence (les noms changent selon les saisons).
_ODDS_COLUMNS = {
    "odds_home": ["AvgH", "BbAvH", "B365H"],
    "odds_draw": ["AvgD", "BbAvD", "B365D"],
    "odds_away": ["AvgA", "BbAvA", "B365A"],
    "odds_over25": ["Avg>2.5", "BbAv>2.5", "B365>2.5"],
    "odds_under25": ["Avg<2.5", "BbAv<2.5", "B365<2.5"],
    "odds_over25_close": ["AvgC>2.5", "B365C>2.5"],
    "odds_under25_close": ["AvgC<2.5", "B365C<2.5"],
}
_STAT_COLUMNS = {"HS": "shots_home", "AS": "shots_away", "HST": "sot_home", "AST": "sot_away"}


class DataSourceError(RuntimeError):
    """Erreur de collecte : la donnée est absente, on ne l'invente pas."""


def _ssl_context() -> ssl.SSLContext:
    bundle = os.environ.get("PRONO_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if not bundle and Path("/root/.ccr/ca-bundle.crt").exists():
        bundle = "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=bundle) if bundle else ssl.create_default_context()


def fetch_csv(league: str, season: str, *, cache_dir: Path | None = None, refresh: bool = False,
              retries: int = 3, timeout: float = 30.0) -> bytes:
    """Télécharge (ou lit dans le cache) le CSV d'une ligue et d'une saison."""
    cache_dir = cache_dir or config.RAW_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{league}_{season}.csv"
    if path.exists() and not refresh:
        return path.read_bytes()

    url = BASE_URL.format(season=season, league=league)
    request = urllib.request.Request(url, headers={"User-Agent": config.USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=_ssl_context()) as resp:
                content = resp.read()
            if not content.strip():
                raise DataSourceError(f"Fichier vide : {url}")
            path.write_bytes(content)
            return content
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise DataSourceError(f"Saison ou ligue indisponible : {url}") from exc
            last_error = exc
        except (urllib.error.URLError, TimeoutError, DataSourceError) as exc:
            last_error = exc
        time.sleep(2 ** attempt)
    raise DataSourceError(f"Échec du téléchargement après {retries} tentatives : {url} ({last_error})")


def _first_column(df: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for name in candidates:
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce")
    return pd.Series([float("nan")] * len(df), index=df.index)


def parse_csv(content: bytes, league: str, season: str, fetched_at: str | None = None) -> pd.DataFrame:
    """Transforme un CSV brut en tableau normalisé (une ligne par match joué)."""
    text = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise DataSourceError(f"Encodage illisible pour {league} {season}")

    raw = pd.read_csv(io.StringIO(text), on_bad_lines="skip")
    raw = raw.dropna(how="all")
    required = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "HTHG", "HTAG"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise DataSourceError(f"Colonnes manquantes {missing} pour {league} {season}")

    df = pd.DataFrame({
        "league": league,
        "season": season,
        "date": pd.to_datetime(raw["Date"], dayfirst=True, errors="coerce", format="mixed"),
        "home": raw["HomeTeam"].astype(str).str.strip(),
        "away": raw["AwayTeam"].astype(str).str.strip(),
        "ft_home": pd.to_numeric(raw["FTHG"], errors="coerce"),
        "ft_away": pd.to_numeric(raw["FTAG"], errors="coerce"),
        "ht_home": pd.to_numeric(raw["HTHG"], errors="coerce"),
        "ht_away": pd.to_numeric(raw["HTAG"], errors="coerce"),
    })
    for raw_name, name in _STAT_COLUMNS.items():
        df[name] = pd.to_numeric(raw[raw_name], errors="coerce") if raw_name in raw.columns else float("nan")
    for name, candidates in _ODDS_COLUMNS.items():
        df[name] = _first_column(raw, candidates)

    df["h1_goals"] = df["ht_home"] + df["ht_away"]
    df["h2_goals"] = (df["ft_home"] - df["ht_home"]) + (df["ft_away"] - df["ht_away"])
    df["source"] = SOURCE_NAME
    df["fetched_at"] = fetched_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
    return df


def load_matches(leagues: list[str] | None = None, seasons: list[str] | None = None, *,
                 refresh_current: bool = False, cache_dir: Path | None = None) -> tuple[pd.DataFrame, list[str]]:
    """Charge toutes les ligues/saisons demandées.

    Retourne le tableau des matchs et la liste des problèmes rencontrés
    (fichiers manquants, erreurs réseau) : rien n'est masqué.
    """
    leagues = leagues or list(config.LEAGUES)
    seasons = seasons or config.DEFAULT_SEASONS
    frames, issues = [], []
    current = seasons[-1]
    for league in leagues:
        for season in seasons:
            try:
                content = fetch_csv(league, season, cache_dir=cache_dir,
                                    refresh=refresh_current and season == current)
                frames.append(parse_csv(content, league, season))
            except DataSourceError as exc:
                issues.append(str(exc))
    if not frames:
        raise DataSourceError("Aucune donnée chargée. " + " | ".join(issues))
    return pd.concat(frames, ignore_index=True), issues
