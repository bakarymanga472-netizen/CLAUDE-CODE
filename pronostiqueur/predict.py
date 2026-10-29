"""Prédiction d'un match à venir et rapport au format du cahier des charges (section 13)."""

from __future__ import annotations

import difflib
import json
import math
from dataclasses import dataclass

import pandas as pd

from . import config
from .data import storage
from .features import FeatureBuilder
from .models.ensemble import BASE_MODELS, HalfTimePredictor
from .models.players import player_markets_status
from .risk import Assessment, assess

MODEL_NAMES = {"poisson": "Poisson mi-temps", "marche": "Marché (cotes)", "bayes": "Bayésien (fréquences)",
               "logistique": "Régression logistique", "gbm": "Gradient boosting"}


@dataclass
class FixturePrediction:
    league: str
    date: str
    home: str
    away: str
    features: dict
    components: dict[str, dict[str, float]]
    assessments: dict[str, Assessment]
    model_version: str
    notes: list[str]


def resolve_team(builder: FeatureBuilder, league: str, name: str) -> tuple[str | None, list[str]]:
    """Retrouve le nom exact de l'équipe dans les données (aucune invention)."""
    known = builder.known_teams(league)
    if name in known:
        return name, []
    lowered = {k.lower(): k for k in known}
    if name.lower() in lowered:
        return lowered[name.lower()], []
    close = difflib.get_close_matches(name, known, n=3, cutoff=0.6)
    if len(close) == 1:
        return close[0], [f"« {name} » interprété comme « {close[0]} »"]
    return None, [f"Équipe « {name} » introuvable en {league}. Proches : {close or 'aucune'}"]


def predict_fixture(predictor: HalfTimePredictor, builder: FeatureBuilder, model_version: str,
                    league: str, home: str, away: str, date: str, odds: dict | None = None,
                    offered: dict | None = None) -> FixturePrediction:
    notes: list[str] = []
    home_r, n1 = resolve_team(builder, league, home)
    away_r, n2 = resolve_team(builder, league, away)
    notes += n1 + n2
    ts = pd.Timestamp(date)
    offered = offered or {}
    if home_r is None or away_r is None:
        assessments = {m: assess(math.nan, 0, 1, math.nan, 0, 0, offered.get(m)) for m in predictor.models}
        for a in assessments.values():
            a.status = "donnees_insuffisantes"
            a.reasons = ["équipe absente des données"]
        return FixturePrediction(league, date, home, away, {}, {}, assessments, model_version, notes)

    feats = builder.snapshot(league, home_r, away_r, ts, odds or {})
    frame = pd.DataFrame([feats])
    comps, assessments = {}, {}
    for market, out in predictor.predict(frame).items():
        row = out.iloc[0]
        comps[market] = {m: (None if pd.isna(row[m]) else float(row[m])) for m in BASE_MODELS}
        comps[market]["ensemble"] = float(row["probabilite"])
        assessments[market] = assess(float(row["probabilite"]), float(row["prob_basse"]),
                                     float(row["prob_haute"]), float(row["ecart_modeles"]),
                                     int(feats["home_n_matches"]), int(feats["away_n_matches"]),
                                     offered.get(market))
    if math.isnan(feats["market_lambda_total"]):
        notes.append("Cotes +/-2,5 non fournies : le modèle de marché n'a pas pu être utilisé.")
    return FixturePrediction(league, date, home_r, away_r, feats, comps, assessments, model_version, notes)


def _pct(x) -> str:
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.0%}"


def to_markdown(fp: FixturePrediction) -> str:
    title = f"## {fp.home} – {fp.away} ({config.LEAGUES.get(fp.league, fp.league)}, {fp.date})"
    lines = [title, "", f"Modèle : `{fp.model_version}`", "",
             "| Marché | Probabilité calibrée | Fourchette d'incertitude | Cote juste | Cote disponible | Statut |",
             "|---|---|---|---|---|---|"]
    for market, label in config.MARKETS.items():
        a = fp.assessments.get(market)
        if a is None:
            continue
        offered = f"{a.offered_odds:.2f}" if a.offered_odds else "à récupérer"
        if math.isnan(a.probability):
            lines.append(f"| {label} | — | — | — | {offered} | {a.status_label} |")
        else:
            lines.append(f"| {label} | {a.probability:.1%} | {a.low:.0%} – {a.high:.0%} | {a.fair_odds:.2f} "
                         f"| {offered} | {a.status_label} |")
    for label, status in player_markets_status():
        lines.append(f"| {label} | — | — | — | — | {status} |")

    f = fp.features
    lines += ["", "**1. Raisons statistiques principales**"]
    if f:
        for h, name in (("h1", "1re"), ("h2", "2e")):
            lines.append(f"- {name} mi-temps : buts attendus (Poisson) {f[f'poisson_lambda_{h}']:.2f} ; "
                         f"fréquence « but dans la mi-temps » {fp.home} {_pct(f[f'home_{h}_any'])}, "
                         f"{fp.away} {_pct(f[f'away_{h}_any'])}, ligue {_pct(f[f'league_any_{h}'])}.")
        if not math.isnan(f["market_lambda_total"]):
            lines.append(f"- Marché : P(+2,5 buts) corrigée de la marge {f['market_p_over25']:.0%}, "
                         f"soit {f['market_lambda_total']:.2f} buts attendus dans le match.")
    lines += ["", "**2. Facteurs défavorables / 8. Décision**"]
    for market, a in fp.assessments.items():
        why = "; ".join(a.reasons) if a.reasons else "aucun signal bloquant"
        lines.append(f"- {config.MARKETS[market]} → **{a.status_label}** (indice de risque {a.risk_index}/100) : {why}.")
    lines += ["", "**3. Compositions** : non connectées dans cette version (à vérifier manuellement "
              "avant le match ; une rotation ou une absence majeure invalide la prédiction).",
              "", "**4. Différences entre modèles**"]
    for market, comp in fp.components.items():
        parts = ", ".join(f"{MODEL_NAMES[m]} {_pct(comp[m])}" for m in BASE_MODELS)
        lines.append(f"- {config.MARKETS[market]} : {parts} → ensemble {_pct(comp['ensemble'])}.")
    if f:
        lines += ["", f"**5. Scénario le plus probable** : environ {f['poisson_lambda_h1']:.1f} but(s) "
                  f"en 1re mi-temps et {f['poisson_lambda_h2']:.1f} en 2e (moyennes, pas une certitude)."]
        worst = max(fp.assessments.items(), key=lambda kv: kv[1].risk_index)
        lines.append(f"\n**6. Principal risque d'échec** : mi-temps sans but sur « {config.MARKETS[worst[0]]} » "
                     f"(environ {1 - worst[1].probability:.0%} de chances).")
    missing = ["compositions officielles", "blessures/suspensions", "xG", "cotes par mi-temps (à saisir)",
               "minutes des buts (buts précoces/tardifs)"] + fp.notes
    lines += ["", "**7. Données manquantes** : " + " ; ".join(missing) + "."]
    return "\n".join(lines)


def log_prediction(conn, fp: FixturePrediction) -> list[int]:
    ids = []
    for market, a in fp.assessments.items():
        if math.isnan(a.probability):
            continue
        ids.append(storage.insert_prediction(conn, {
            "model_version": fp.model_version, "league": fp.league, "match_date": fp.date,
            "home": fp.home, "away": fp.away, "market": market, "probability": a.probability,
            "prob_low": a.low, "prob_high": a.high, "fair_odds": a.fair_odds,
            "offered_odds": a.offered_odds, "expected_value": a.expected_value, "status": a.status,
            "risk_index": a.risk_index, "model_probs": fp.components.get(market, {}),
            "features": {k: (None if isinstance(v, float) and math.isnan(v) else v)
                         for k, v in fp.features.items()},
            "data_sources": {"football-data.co.uk": "historique jusqu'au dernier fichier téléchargé"},
            "notes": json.dumps({"raisons": a.reasons, "notes": fp.notes}, ensure_ascii=False),
        }))
    return ids
