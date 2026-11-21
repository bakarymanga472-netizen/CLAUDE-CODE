import math

import numpy as np
import pytest

from pronostiqueur import metrics, odds
from pronostiqueur.risk import assess


def test_remove_margin_sums_to_one():
    for method in ("power", "proportional"):
        probs = odds.remove_margin([1.90, 1.90, 8.0], method=method)
        assert math.isclose(sum(probs), 1.0, rel_tol=1e-9)
        assert all(0 < p < 1 for p in probs)


def test_margin_and_fair_odds():
    assert odds.bookmaker_margin([1.90, 1.90]) == pytest.approx(0.0526, abs=1e-3)
    assert odds.fair_odds(0.8) == pytest.approx(1.25)
    assert odds.expected_value(0.8, 1.30) == pytest.approx(0.04)


def test_implied_total_goals_round_trip():
    for lam in (1.5, 2.6, 3.4):
        p = 1 - odds.poisson_cdf(2, lam)
        assert odds.implied_total_goals(p) == pytest.approx(lam, abs=1e-3)


def test_prob_at_least_one():
    assert odds.prob_at_least_one(1.6) == pytest.approx(1 - math.exp(-1.6))


def test_wilson_interval_contains_proportion():
    lo, hi = metrics.wilson_interval(95, 100)
    assert lo < 0.95 < hi
    assert lo == pytest.approx(0.888, abs=0.005)


def test_high_confidence_table_counts():
    p = np.array([0.96, 0.96, 0.80, 0.60])
    y = np.array([1, 0, 1, 1])
    tab = metrics.high_confidence_table(p, y, thresholds=(0.95,))
    assert tab.loc[0, "n_selections"] == 2
    assert tab.loc[0, "echecs"] == 1


def test_risk_statuses():
    ok = assess(0.88, 0.84, 0.92, 0.02, 20, 20, offered_odds=1.18)
    assert ok.status == "admissible"
    no_odds = assess(0.88, 0.84, 0.92, 0.02, 20, 20, offered_odds=None)
    assert no_odds.status == "a_surveiller"
    bad_value = assess(0.88, 0.84, 0.92, 0.02, 20, 20, offered_odds=1.05)
    assert bad_value.status == "a_eviter"
    short = assess(0.9, 0.85, 0.95, 0.02, 3, 20, offered_odds=1.2)
    assert short.status == "donnees_insuffisantes"


def test_dixon_coles_reduces_to_poisson_and_fits_rho():
    from pronostiqueur.models.ensemble import dixon_coles_prob_goal, fit_dixon_coles_rho
    lh, la = np.array([0.7, 0.4]), np.array([0.5, 0.3])
    assert np.allclose(dixon_coles_prob_goal(lh, la, 0.0), 1 - np.exp(-(lh + la)))
    # ρ négatif = plus de 0-0 que le Poisson indépendant
    assert (dixon_coles_prob_goal(lh, la, -0.3) < dixon_coles_prob_goal(lh, la, 0.0)).all()
    rng = np.random.default_rng(1)
    lam_h, lam_a = rng.uniform(0.3, 1.0, 20000), rng.uniform(0.2, 0.8, 20000)
    p_true = dixon_coles_prob_goal(lam_h, lam_a, -0.4)
    y = rng.random(20000) < p_true
    assert fit_dixon_coles_rho(lam_h, lam_a, y) == pytest.approx(-0.4, abs=0.15)


def test_at_least_two_goals_formulas():
    from pronostiqueur.models.ensemble import dixon_coles_prob_goal, prob_at_least
    lam = np.array([0.5, 1.2])
    assert np.allclose(prob_at_least(lam, 2), 1 - np.exp(-lam) * (1 + lam))
    lh, la = np.array([0.7, 0.4]), np.array([0.5, 0.3])
    # Sans correction (ρ = 0), Dixon-Coles revient au Poisson de la somme des λ.
    assert np.allclose(dixon_coles_prob_goal(lh, la, 0.0, 2), prob_at_least(lh + la, 2))
    assert (prob_at_least(lam, 2) < prob_at_least(lam, 1)).all()
