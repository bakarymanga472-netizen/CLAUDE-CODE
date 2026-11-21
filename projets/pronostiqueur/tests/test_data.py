import pandas as pd

from pronostiqueur.data import football_data_uk as fdu
from pronostiqueur.data import quality, storage

CSV = (
    "﻿Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,HS,AS,HST,AST,"
    "AvgH,AvgD,AvgA,Avg>2.5,Avg<2.5\n"
    "F1,25/10/2026,17:00,Rennes,Strasbourg,3,0,H,2,0,H,15,8,7,2,1.8,3.8,4.2,1.70,2.15\n"
    "F1,26/10/2026,20:45,Paris SG,Lyon,2,0,H,0,0,D,18,9,8,3,1.3,5.5,9.0,1.40,2.90\n"
    "F1,26/10/2026,20:45,Paris SG,Lyon,2,0,H,0,0,D,18,9,8,3,1.3,5.5,9.0,1.40,2.90\n"
    "F1,27/10/2026,20:45,Nice,Lens,1,1,D,2,0,H,10,10,4,4,2.5,3.3,2.8,1.90,1.90\n"
    "F1,28/10/2026,20:45,Brest,Lille,,,,,,,,,,,2.5,3.3,2.8,1.90,1.90\n"
).encode("utf-8")


def test_parse_and_clean():
    df = fdu.parse_csv(CSV, "F1", "2627")
    assert list(df["h1_goals"][:2]) == [2, 0]
    assert list(df["h2_goals"][:2]) == [1, 2]
    assert df.loc[0, "odds_over25"] == 1.70
    clean, rep = quality.clean_matches(df)
    # doublon retiré, HT > FT rejeté, score manquant rejeté
    assert len(clean) == 2
    assert rep.rejected["doublon"] == 1
    assert rep.rejected["score mi-temps > score final"] == 1
    assert rep.rejected["score manquant"] == 1


def test_storage_roundtrip(tmp_path):
    df, _ = quality.clean_matches(fdu.parse_csv(CSV, "F1", "2627"))
    conn = storage.connect(tmp_path / "t.db")
    assert storage.upsert_matches(conn, df) == 2
    back = storage.read_matches(conn)
    assert len(back) == 2 and isinstance(back["date"].iloc[0], pd.Timestamp)
    pid = storage.insert_prediction(conn, {
        "model_version": "test", "league": "F1", "match_date": "2026-10-30", "home": "A", "away": "B",
        "market": "H2_O05", "probability": 0.9, "prob_low": 0.85, "prob_high": 0.94, "fair_odds": 1.11,
        "offered_odds": 1.12, "expected_value": 0.008, "status": "admissible", "risk_index": 30.0,
        "model_probs": {"marche": 0.9}, "features": {}, "data_sources": {}})
    assert len(storage.unsettled_predictions(conn)) == 1
    storage.settle(conn, pid, 1, 0, 2)
    assert storage.unsettled_predictions(conn) == []
    assert storage.settled_predictions(conn)["result"].tolist() == [1]


def test_ssl_context_sans_variable_d_environnement(monkeypatch):
    # Sur GitHub Actions aucun certificat spécifique n'est défini : le contexte par défaut doit suffire.
    monkeypatch.delenv("PRONO_CA_BUNDLE", raising=False)
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    assert fdu._ssl_context().verify_mode.name == "CERT_REQUIRED"
