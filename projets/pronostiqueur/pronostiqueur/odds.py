"""Outils de cotes : probabilités implicites, marge, cote juste, espérance."""

from __future__ import annotations

import math
from typing import Sequence


def implied_probability(odds: float) -> float:
    """Probabilité implicite brute d'une cote décimale (1/d), marge incluse."""
    if odds <= 1.0:
        raise ValueError("Une cote décimale doit être > 1")
    return 1.0 / odds


def bookmaker_margin(odds: Sequence[float]) -> float:
    """Marge (overround) d'un marché complet : somme des 1/d moins 1."""
    return sum(1.0 / o for o in odds) - 1.0


def remove_margin(odds: Sequence[float], method: str = "power") -> list[float]:
    """Probabilités corrigées de la marge pour un marché à issues exclusives.

    - « proportional » : normalisation simple.
    - « power » (défaut) : p_i = (1/d_i)^k avec k tel que la somme vaille 1 ;
      corrige mieux le biais favori/outsider que la normalisation simple.
    """
    raw = [1.0 / o for o in odds]
    if method == "proportional":
        total = sum(raw)
        return [r / total for r in raw]
    lo, hi = 0.5, 3.0
    for _ in range(100):
        k = (lo + hi) / 2
        total = sum(r ** k for r in raw)
        if total > 1.0:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2
    probs = [r ** k for r in raw]
    total = sum(probs)
    return [p / total for p in probs]


def poisson_cdf(k: int, lam: float) -> float:
    return sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k + 1))


def implied_total_goals(p_over25: float) -> float:
    """λ total tel que P(Poisson(λ) ≥ 3) = p_over25 (recherche dichotomique)."""
    p_over25 = min(max(p_over25, 1e-4), 1 - 1e-4)
    lo, hi = 0.05, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if 1 - poisson_cdf(2, mid) < p_over25:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def prob_at_least_one(lam: float) -> float:
    """P(au moins un but) = 1 - exp(-λ) dans un modèle de Poisson."""
    return 1.0 - math.exp(-max(lam, 0.0))


def fair_odds(probability: float) -> float:
    return float("inf") if probability <= 0 else 1.0 / probability


def expected_value(probability: float, odds: float) -> float:
    """Espérance de gain par unité misée : p * d - 1."""
    return probability * odds - 1.0
