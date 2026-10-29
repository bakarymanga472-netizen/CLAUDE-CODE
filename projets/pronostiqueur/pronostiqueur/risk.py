"""Indice de risque et statut de chaque marché (section 9 du cahier des charges)."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from . import config
from .odds import expected_value, fair_odds

STATUS_LABELS = {
    "admissible": "Sélection admissible",
    "a_surveiller": "À surveiller",
    "donnees_insuffisantes": "Données insuffisantes",
    "a_eviter": "À éviter",
}


@dataclass
class Assessment:
    probability: float
    low: float
    high: float
    model_spread: float
    fair_odds: float
    offered_odds: float | None
    expected_value: float | None
    risk_index: float
    status: str
    reasons: list[str] = field(default_factory=list)

    @property
    def status_label(self) -> str:
        return STATUS_LABELS[self.status]


def assess(probability: float, low: float, high: float, model_spread: float,
           home_matches: int, away_matches: int, offered_odds: float | None = None,
           rules: config.SelectionRules | None = None) -> Assessment:
    rules = rules or config.SELECTION
    reasons: list[str] = []
    ev = expected_value(probability, offered_odds) if offered_odds else None
    spread = 0.0 if math.isnan(model_spread) else model_spread

    # Indice de risque 0-100 : probabilité d'échec, incertitude, désaccord, échantillon.
    sample_penalty = max(0, rules.min_team_matches - min(home_matches, away_matches)) / rules.min_team_matches
    risk = 100 * min(1.0, 0.5 * (1 - probability) / 0.3 + 0.2 * (high - low) / 0.3
                     + 0.2 * spread / 0.1 + 0.1 * sample_penalty)

    if min(home_matches, away_matches) < rules.min_team_matches:
        reasons.append(f"historique trop court (moins de {rules.min_team_matches} matchs pour une équipe)")
        status = "donnees_insuffisantes"
    elif probability < 0.70 or (ev is not None and ev < -0.02):
        if probability < 0.70:
            reasons.append("probabilité trop faible")
        if ev is not None and ev < -0.02:
            reasons.append(f"cote {offered_odds:.2f} inférieure à la cote juste {fair_odds(probability):.2f}")
        status = "a_eviter"
    else:
        if probability < rules.min_probability:
            reasons.append(f"probabilité < {rules.min_probability:.0%}")
        if low < rules.min_lower_bound:
            reasons.append(f"borne basse {low:.0%} < {rules.min_lower_bound:.0%}")
        if spread > rules.max_model_spread:
            reasons.append(f"modèles en désaccord (écart {spread:.0%})")
        if offered_odds is None:
            reasons.append("cote disponible inconnue : impossible de vérifier la valeur")
        elif ev is not None and ev < rules.min_expected_value:
            reasons.append(f"espérance négative ({ev:+.1%})")
        status = "a_surveiller" if reasons else "admissible"
    return Assessment(probability, low, high, spread, fair_odds(probability), offered_odds, ev,
                      round(risk, 1), status, reasons)
