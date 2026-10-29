-- Schéma de la base historique et du journal de pronostics (SQLite).
-- Chaque table porte des horodatages pour permettre l'audit a posteriori.

CREATE TABLE IF NOT EXISTS matches (
    league        TEXT NOT NULL,
    season        TEXT NOT NULL,
    date          TEXT NOT NULL,          -- AAAA-MM-JJ
    home          TEXT NOT NULL,
    away          TEXT NOT NULL,
    ft_home       INTEGER NOT NULL,
    ft_away       INTEGER NOT NULL,
    ht_home       INTEGER NOT NULL,
    ht_away       INTEGER NOT NULL,
    h1_goals      INTEGER NOT NULL,
    h2_goals      INTEGER NOT NULL,
    shots_home    REAL,
    shots_away    REAL,
    sot_home      REAL,
    sot_away      REAL,
    odds_home     REAL,
    odds_draw     REAL,
    odds_away     REAL,
    odds_over25   REAL,
    odds_under25  REAL,
    odds_over25_close  REAL,
    odds_under25_close REAL,
    source        TEXT NOT NULL,
    fetched_at    TEXT NOT NULL,
    PRIMARY KEY (league, date, home, away)
);

CREATE TABLE IF NOT EXISTS data_sources (
    name         TEXT PRIMARY KEY,
    url          TEXT,
    licence      TEXT,
    coverage     TEXT,
    reliability  TEXT,
    last_fetch   TEXT
);

-- Journal : une ligne par marché pronostiqué, écrite AVANT le match.
CREATE TABLE IF NOT EXISTS predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    league          TEXT NOT NULL,
    match_date      TEXT NOT NULL,
    home            TEXT NOT NULL,
    away            TEXT NOT NULL,
    market          TEXT NOT NULL,         -- H1_O05, H2_O05, ...
    probability     REAL NOT NULL,         -- probabilité calibrée finale
    prob_low        REAL NOT NULL,
    prob_high       REAL NOT NULL,
    fair_odds       REAL NOT NULL,
    offered_odds    REAL,                  -- cote disponible (saisie ou API), NULL si inconnue
    taken_odds      REAL,                  -- cote réellement prise, si pari placé
    expected_value  REAL,
    status          TEXT NOT NULL,         -- admissible / a_surveiller / donnees_insuffisantes / a_eviter
    risk_index      REAL NOT NULL,
    model_probs     TEXT NOT NULL,         -- JSON {modèle: probabilité}
    features        TEXT NOT NULL,         -- JSON des variables utilisées à cet instant
    data_sources    TEXT NOT NULL,         -- JSON des sources et horodatages
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS outcomes (
    prediction_id   INTEGER PRIMARY KEY REFERENCES predictions(id),
    settled_at      TEXT NOT NULL,
    result          INTEGER NOT NULL,      -- 1 = marché gagné, 0 = perdu
    h1_goals        INTEGER,
    h2_goals        INTEGER,
    error_category  TEXT,                  -- modele / aleatoire / contexte / donnees (analyse humaine)
    comment         TEXT
);

CREATE TABLE IF NOT EXISTS model_versions (
    version        TEXT PRIMARY KEY,
    created_at     TEXT NOT NULL,
    trained_until  TEXT NOT NULL,
    status         TEXT NOT NULL,          -- production / candidat / archive
    metrics        TEXT NOT NULL           -- JSON (log-loss, Brier, calibration)
);
