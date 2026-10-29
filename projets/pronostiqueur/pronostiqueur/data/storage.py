"""Stockage SQLite : base historique, journal de pronostics, versions de modèles."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from .. import config

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

MATCH_COLUMNS = [
    "league", "season", "date", "home", "away", "ft_home", "ft_away", "ht_home", "ht_away",
    "h1_goals", "h2_goals", "shots_home", "shots_away", "sot_home", "sot_away",
    "odds_home", "odds_draw", "odds_away", "odds_over25", "odds_under25",
    "odds_over25_close", "odds_under25_close", "source", "fetched_at",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or config.DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


def upsert_matches(conn: sqlite3.Connection, df: pd.DataFrame) -> int:
    rows = df[MATCH_COLUMNS].copy()
    rows["date"] = rows["date"].dt.strftime("%Y-%m-%d")
    rows = rows.astype(object).where(rows.notna(), None)
    placeholders = ",".join("?" for _ in MATCH_COLUMNS)
    conn.executemany(
        f"INSERT OR REPLACE INTO matches ({','.join(MATCH_COLUMNS)}) VALUES ({placeholders})",
        rows.itertuples(index=False, name=None),
    )
    conn.commit()
    return len(rows)


def read_matches(conn: sqlite3.Connection) -> pd.DataFrame:
    df = pd.read_sql_query("SELECT * FROM matches ORDER BY date, league, home", conn)
    df["date"] = pd.to_datetime(df["date"])
    return df


def record_source(conn: sqlite3.Connection, name: str, url: str, licence: str, coverage: str,
                  reliability: str) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO data_sources VALUES (?,?,?,?,?,?)",
        (name, url, licence, coverage, reliability, now_iso()),
    )
    conn.commit()


def insert_prediction(conn: sqlite3.Connection, record: dict) -> int:
    payload = dict(record)
    for key in ("model_probs", "features", "data_sources"):
        payload[key] = json.dumps(payload.get(key, {}), ensure_ascii=False, default=float)
    payload.setdefault("created_at", now_iso())
    cols = list(payload)
    cur = conn.execute(
        f"INSERT INTO predictions ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",
        [payload[c] for c in cols],
    )
    conn.commit()
    return int(cur.lastrowid)


def unsettled_predictions(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT p.* FROM predictions p LEFT JOIN outcomes o ON o.prediction_id = p.id "
        "WHERE o.prediction_id IS NULL ORDER BY p.match_date"
    ).fetchall()


def settle(conn: sqlite3.Connection, prediction_id: int, result: int, h1_goals: int | None,
           h2_goals: int | None, comment: str | None = None) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO outcomes (prediction_id, settled_at, result, h1_goals, h2_goals, comment) "
        "VALUES (?,?,?,?,?,?)",
        (prediction_id, now_iso(), int(result), h1_goals, h2_goals, comment),
    )
    conn.commit()


def settled_predictions(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT p.*, o.result, o.settled_at, o.error_category FROM predictions p "
        "JOIN outcomes o ON o.prediction_id = p.id ORDER BY p.match_date",
        conn,
    )


def register_model(conn: sqlite3.Connection, version: str, trained_until: str, status: str,
                   metrics: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO model_versions VALUES (?,?,?,?,?)",
        (version, now_iso(), trained_until, status, json.dumps(metrics, default=float)),
    )
    conn.commit()
