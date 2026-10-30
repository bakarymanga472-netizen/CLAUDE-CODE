import numpy as np
import pandas as pd

from pronostiqueur import backtest, config
from pronostiqueur.features import FeatureBuilder
from pronostiqueur.models.ensemble import HalfTimePredictor
from pronostiqueur.predict import predict_fixture, to_markdown, to_table


def test_no_future_leakage(synthetic_matches):
    """Modifier un résultat futur ne doit pas changer les variables d'un match passé."""
    base = FeatureBuilder().build(synthetic_matches)
    altered = synthetic_matches.copy()
    last_date = altered["date"].max()
    altered.loc[altered["date"] == last_date, ["ht_home", "ft_home", "h1_goals"]] += 5
    feats = FeatureBuilder().build(altered)
    cols = ["home_h1_for", "away_h2_against", "poisson_lambda_h1", "poisson_lambda_h2"]
    pd.testing.assert_frame_equal(base[cols], feats[cols])


def test_same_day_matches_do_not_see_each_other(synthetic_matches):
    feats = FeatureBuilder().build(synthetic_matches)
    first_day = feats[feats["date"] == feats["date"].min()]
    # Avant tout match, toutes les équipes ont un historique nul.
    assert (first_day["home_n_matches"] == 0).all()
    assert (first_day["away_n_matches"] == 0).all()


def test_ensemble_and_walk_forward(synthetic_matches):
    feats = FeatureBuilder().build(synthetic_matches)
    bt = backtest.walk_forward(feats)
    assert set(bt["market"]) == set(config.MARKETS)
    assert bt["probabilite"].between(0, 1).all()
    assert (bt["prob_basse"] <= bt["probabilite"] + 1e-9).all()
    assert (bt["prob_haute"] >= bt["probabilite"] - 1e-9).all()
    evaluation = backtest.evaluate(bt)
    assert "haute_confiance" in evaluation["H2_O05"]


def test_predict_fixture_and_report(synthetic_matches):
    builder = FeatureBuilder()
    feats = builder.build(synthetic_matches)
    predictor = HalfTimePredictor().fit(feats[feats["season"] != "2223"])
    weights = predictor.models["H2_O05"].weights
    assert np.isclose(weights.sum(), 1.0) and (weights >= 0).all()
    fp = predict_fixture(predictor, builder, "test", "XX", "Equipe0", "Equipe1", "2026-01-01",
                         {"odds_over25": 1.8, "odds_under25": 2.0}, {"H2_O05": 1.15})
    md = to_markdown(fp)
    assert "+0,5 but deuxième mi-temps" in md
    assert "module joueurs non implémenté" in md
    unknown = predict_fixture(predictor, builder, "test", "XX", "Inconnue FC", "Equipe1", "2026-01-01")
    assert all(a.status == "donnees_insuffisantes" for a in unknown.assessments.values())
    # Le +1,5 d'une mi-temps est toujours moins probable que le +0,5 de la même mi-temps.
    assert fp.assessments["H2_O15"].probability < fp.assessments["H2_O05"].probability
    table = to_table([(fp, "rotation probable"), (unknown, None)])
    lines = table.splitlines()
    assert lines[0].startswith("| Match | Buts attendus | Part des buts en 2e MT | 2e MT +0,5 | 2e MT +1,5")
    assert "Equipe0 – Equipe1" in lines[2] and "rotation probable" in lines[2]
    assert "Inconnue FC" in lines[3] and "—" in lines[3]  # match inconnu en dernier, sans chiffres
