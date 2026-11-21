"""Configuration centrale du pronostiqueur.

Toutes les valeurs réglables (ligues, saisons, seuils de sélection, chemins)
sont regroupées ici pour que chaque décision soit traçable et modifiable
sans toucher au code des modèles.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PRONO_DATA_DIR", ROOT / "data"))
RAW_DIR = DATA_DIR / "raw"
DB_PATH = Path(os.environ.get("PRONO_DB_PATH", DATA_DIR / "pronostiqueur.db"))
MODELS_DIR = Path(os.environ.get("PRONO_MODELS_DIR", ROOT / "models_store"))
REPORTS_DIR = Path(os.environ.get("PRONO_REPORTS_DIR", ROOT / "reports"))

# Codes de championnats de football-data.co.uk.
LEAGUES: dict[str, str] = {
    "E0": "Angleterre - Premier League",
    "E1": "Angleterre - Championship",
    "D1": "Allemagne - Bundesliga",
    "D2": "Allemagne - 2. Bundesliga",
    "I1": "Italie - Serie A",
    "SP1": "Espagne - LaLiga",
    "F1": "France - Ligue 1",
    "F2": "France - Ligue 2",
    "N1": "Pays-Bas - Eredivisie",
    "P1": "Portugal - Liga Portugal",
    "T1": "Turquie - Süper Lig",
    "B1": "Belgique - Pro League",
}

# Saisons au format football-data.co.uk ("2526" = 2025/26).
DEFAULT_SEASONS: list[str] = ["1920", "2021", "2122", "2223", "2324", "2425", "2526", "2627"]

MARKETS = {
    "H1_O05": "+0,5 but première mi-temps",
    "H2_O05": "+0,5 but deuxième mi-temps",
    "H1_O15": "+1,5 but première mi-temps",
    "H2_O15": "+1,5 but deuxième mi-temps",
}

# Mi-temps concernée et nombre minimal de buts pour gagner chaque marché.
MARKET_SPECS: dict[str, tuple[str, int]] = {
    "H1_O05": ("h1", 1), "H2_O05": ("h2", 1), "H1_O15": ("h1", 2), "H2_O15": ("h2", 2),
}


def target_column(market: str) -> str:
    """Colonne cible (0/1) d'un marché dans le tableau de variables."""
    half, min_goals = MARKET_SPECS[market]
    return f"y_{half}" if min_goals == 1 else f"y_{half}_o15"


@dataclass(frozen=True)
class SelectionRules:
    """Règles de sélection (section 12 du cahier des charges).

    Les seuils sont volontairement explicites : aucune sélection n'est forcée.
    """

    # Probabilité calibrée minimale pour envisager une sélection.
    min_probability: float = 0.80
    # Borne basse minimale de la fourchette d'incertitude.
    min_lower_bound: float = 0.75
    # Écart maximal toléré entre modèles (écart-type des probabilités).
    max_model_spread: float = 0.06
    # Nombre minimal de matchs dans l'historique de chaque équipe.
    min_team_matches: int = 8
    # Espérance de gain minimale (EV = p * cote - 1) pour une sélection admissible.
    min_expected_value: float = 0.0


@dataclass
class FeatureSettings:
    """Paramètres du calcul des variables d'équipe."""

    # Demi-vie (en matchs) de la pondération exponentielle de la forme.
    half_life_matches: float = 10.0
    # Force du rétrécissement bayésien vers la moyenne de la ligue
    # (équivalent en nombre de matchs « fictifs » à la moyenne).
    shrinkage_matches: float = 6.0
    # Facteur de réduction des poids lors d'un changement de saison
    # (les effectifs changent : on oublie partiellement le passé).
    season_carry_over: float = 0.5
    extra: dict = field(default_factory=dict)


SELECTION = SelectionRules()
FEATURES = FeatureSettings()

USER_AGENT = "pronostiqueur-research/0.1 (+analyse personnelle; respecte les conditions d'utilisation)"
