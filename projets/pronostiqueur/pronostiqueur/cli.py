"""Interface en ligne de commande : python -m pronostiqueur <commande> [options]."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

import pandas as pd

from . import backtest, config, registry, report
from .data import football_data_uk as fdu
from .data import quality, storage
from .features import FeatureBuilder
from .models.ensemble import HalfTimePredictor
from .predict import log_prediction, predict_fixture, to_markdown, to_table


def _load_db_matches(args, conn) -> pd.DataFrame:
    df = storage.read_matches(conn)
    if df.empty:
        print("Base vide : téléchargement des données…", file=sys.stderr)
        cmd_fetch(args, conn)
        df = storage.read_matches(conn)
    if getattr(args, "leagues", None):
        df = df[df["league"].isin(args.leagues)]
    if getattr(args, "seasons", None):
        df = df[df["season"].isin(args.seasons)]
    return df


def cmd_fetch(args, conn) -> None:
    raw, issues = fdu.load_matches(args.leagues, args.seasons, refresh_current=args.refresh)
    clean, qrep = quality.clean_matches(raw)
    n = storage.upsert_matches(conn, clean)
    storage.record_source(conn, fdu.SOURCE_NAME, "https://www.football-data.co.uk",
                          "Gratuit, usage personnel (voir conditions du site)",
                          "Scores mi-temps/fin, tirs, cotes 1N2 et +/-2,5", "élevée (données officielles de résultats)")
    print(qrep.summary())
    print(f"{n} matchs enregistrés dans {config.DB_PATH}")
    for issue in issues:
        print(f"  ! {issue}")


def cmd_backtest(args, conn) -> None:
    matches = _load_db_matches(args, conn)
    feats = FeatureBuilder(registry.production_settings()).build(matches)
    bt = backtest.walk_forward(feats)
    evaluation = backtest.evaluate(bt)
    bias = backtest.bias_by_segment(bt)
    summary = (f"{len(matches)} matchs · ligues {sorted(matches['league'].unique())} · "
               f"saisons {sorted(matches['season'].unique())} · source football-data.co.uk")
    md = report.backtest_markdown(evaluation, bias, summary)
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (config.REPORTS_DIR / "backtest_report.md").write_text(md, encoding="utf-8")
    (config.REPORTS_DIR / "backtest_dashboard.html").write_text(report.to_html(md, "Validation"), encoding="utf-8")
    bt.to_csv(config.REPORTS_DIR / "backtest_predictions.csv", index=False)
    for market, ev in evaluation.items():
        print(f"\n=== {config.MARKETS[market]} ===")
        print(pd.DataFrame(ev["global"]).T[["n", "taux_base", "brier", "log_loss", "ece"]].round(4).to_string())
        print(ev["haute_confiance"].round(3).to_string(index=False))
        print("Règles de sélection :", json.dumps(ev["selection_regles"], default=float, ensure_ascii=False))
    print(f"\nRapport : {config.REPORTS_DIR / 'backtest_report.md'}")


def cmd_train(args, conn) -> None:
    matches = _load_db_matches(args, conn)
    settings = registry.production_settings()
    feats = FeatureBuilder(settings).build(matches)
    burn_in = sorted(feats["season"].unique())[0]
    predictor = HalfTimePredictor().fit(feats[feats["season"] != burn_in])
    metrics = {m: mdl.validation_report for m, mdl in predictor.models.items()}
    version = registry.save_model(predictor, settings, metrics, args.note or "entraînement complet")
    storage.register_model(conn, version, predictor.trained_until, "production", metrics)
    print(f"Modèle {version} en production (données jusqu'au {predictor.trained_until}).")
    print(json.dumps(metrics, indent=2, ensure_ascii=False, default=float))


def _production_builder(conn):
    predictor, meta = registry.load_production()
    builder = FeatureBuilder(config.FeatureSettings(**meta["feature_settings"]))
    builder.build(storage.read_matches(conn))
    return predictor, meta, builder


def cmd_predict(args, conn) -> None:
    predictor, meta, builder = _production_builder(conn)
    odds = {"odds_over25": args.over25, "odds_under25": args.under25,
            "odds_home": args.cote_1, "odds_draw": args.cote_n, "odds_away": args.cote_2}
    offered = {"H1_O05": args.cote_h1, "H2_O05": args.cote_h2,
               "H1_O15": args.cote_h1_15, "H2_O15": args.cote_h2_15}
    fp = predict_fixture(predictor, builder, meta["version"], args.league, args.home, args.away,
                         args.date, odds, offered)
    print(to_markdown(fp))
    if args.log:
        ids = log_prediction(conn, fp)
        print(f"\nJournalisé (ids {ids}). Réglez après le match avec `settle`.")


TABLE_ODDS = {"over25": "odds_over25", "under25": "odds_under25", "cote_1": "odds_home",
              "cote_n": "odds_draw", "cote_2": "odds_away"}


def cmd_tableau(args, conn) -> None:
    """Tableau de synthèse pour une liste de matchs (fichier CSV)."""
    fixtures = pd.read_csv(args.fichier, dtype=str).fillna("")
    missing = {"league", "home", "away", "date"} - set(fixtures.columns)
    if missing:
        sys.exit(f"Colonnes obligatoires absentes du CSV : {sorted(missing)}")
    predictor, meta, builder = _production_builder(conn)
    rows = []
    for fx in fixtures.to_dict("records"):
        odds = {key: float(fx[col]) for col, key in TABLE_ODDS.items() if fx.get(col)}
        fp = predict_fixture(predictor, builder, meta["version"], fx["league"], fx["home"], fx["away"],
                             fx["date"], odds)
        rows.append((fp, fx.get("alertes") or None))
        if args.log:
            log_prediction(conn, fp)
    print(f"Modèle : `{meta['version']}`\n")
    print(to_table(rows))


def cmd_settle(args, conn) -> None:
    if args.refresh:
        cmd_fetch(argparse.Namespace(leagues=None, seasons=None, refresh=True), conn)
    matches = storage.read_matches(conn)
    settled = 0
    for p in storage.unsettled_predictions(conn):
        m = matches[(matches["league"] == p["league"]) & (matches["home"] == p["home"]) &
                    (matches["away"] == p["away"]) &
                    (matches["date"].dt.strftime("%Y-%m-%d") == p["match_date"])]
        if m.empty:
            continue
        row = m.iloc[0]
        half, min_goals = config.MARKET_SPECS[p["market"]]
        hit = int(row[f"{half}_goals"] >= min_goals)
        storage.settle(conn, p["id"], hit, int(row["h1_goals"]), int(row["h2_goals"]))
        settled += 1
    print(f"{settled} pronostic(s) réglé(s).")


def cmd_report(args, conn) -> None:
    md = report.journal_markdown(storage.settled_predictions(conn))
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (config.REPORTS_DIR / "journal_report.md").write_text(md, encoding="utf-8")
    (config.REPORTS_DIR / "journal_dashboard.html").write_text(report.to_html(md, "Journal"), encoding="utf-8")
    print(md)


def cmd_evolve(args, conn) -> None:
    matches = _load_db_matches(args, conn)
    result = registry.evolve(matches, args.holdout_days, args.candidates)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=float))
    if result["promu"]:
        settings = config.FeatureSettings(**result["promu"]["settings"])
        feats = FeatureBuilder(settings).build(matches)
        burn_in = sorted(feats["season"].unique())[0]
        predictor = HalfTimePredictor().fit(feats[feats["season"] != burn_in])
        version = registry.save_model(predictor, settings, {"evolution": result}, "promotion après comparaison")
        storage.register_model(conn, version, predictor.trained_until, "production", {"evolution": result})
        print(f"Nouvelle configuration promue : {version} ({asdict(settings)})")
    else:
        print("Aucune configuration candidate n'apporte d'amélioration crédible : production inchangée.")


def cmd_rollback(args, conn) -> None:
    print(f"Retour à la version {registry.rollback()}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pronostiqueur", description="IA de prédiction des buts par mi-temps")
    sub = p.add_subparsers(dest="cmd", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--leagues", nargs="*", default=None, help="Codes ligues (ex. F1 E0 D1)")
    common.add_argument("--seasons", nargs="*", default=None, help="Saisons (ex. 2425 2526 2627)")

    f = sub.add_parser("fetch", parents=[common], help="Télécharger et stocker l'historique")
    f.add_argument("--refresh", action="store_true", help="Re-télécharger la saison en cours")
    sub.add_parser("backtest", parents=[common], help="Validation chronologique complète")
    t = sub.add_parser("train", parents=[common], help="Entraîner et mettre en production")
    t.add_argument("--note", default=None)

    pr = sub.add_parser("predict", help="Prédire un match à venir")
    pr.add_argument("--league", required=True)
    pr.add_argument("--home", required=True)
    pr.add_argument("--away", required=True)
    pr.add_argument("--date", required=True, help="AAAA-MM-JJ")
    for name in ("over25", "under25", "cote-1", "cote-n", "cote-2", "cote-h1", "cote-h2",
                 "cote-h1-15", "cote-h2-15"):
        pr.add_argument(f"--{name}", type=float, default=None)
    pr.add_argument("--log", action="store_true", help="Enregistrer dans le journal")

    tb = sub.add_parser("tableau", help="Tableau de synthèse pour plusieurs matchs (CSV)")
    tb.add_argument("fichier", help="CSV : league,home,away,date[,over25,under25,cote_1,cote_n,cote_2,alertes]")
    tb.add_argument("--log", action="store_true", help="Enregistrer dans le journal")

    s = sub.add_parser("settle", help="Régler les pronostics journalisés")
    s.add_argument("--refresh", action="store_true")
    sub.add_parser("report", help="Performance réelle du journal")
    e = sub.add_parser("evolve", parents=[common], help="Tester et promouvoir une meilleure configuration")
    e.add_argument("--holdout-days", type=int, default=120)
    e.add_argument("--candidates", type=int, default=4)
    sub.add_parser("rollback", help="Revenir à la version précédente")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    conn = storage.connect()
    handlers = {"fetch": cmd_fetch, "backtest": cmd_backtest, "train": cmd_train, "predict": cmd_predict, "tableau": cmd_tableau,
                "settle": cmd_settle, "report": cmd_report, "evolve": cmd_evolve, "rollback": cmd_rollback}
    try:
        handlers[args.cmd](args, conn)
    finally:
        conn.close()
