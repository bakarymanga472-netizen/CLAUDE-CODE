"""Labo — étiquetage des régimes de marché avec des données PASSÉES uniquement (utilisable pour décider).

Priorité : crise > forte volatilité > tendance > range.
- crise : baisse de plus de 40 % depuis le plus haut d'un an, ou -25 % en 30 jours ;
- forte volatilité : vol 30 j dans les 20 % les plus hautes de tout l'historique disponible à cette date ;
- tendance / range : ratio d'efficacité de Kaufman sur 60 jours ≥ 0,25 / < 0,25.
Seuils fixés avant les tests (2026-10-20), non optimisés.
"""
import numpy as np
import pandas as pd

from .donnees import BARRES_PAR_JOUR

REGIMES = ["tendance", "range", "forte_volatilite", "crise"]


def etiqueter(df, intervalle, seuil_efficacite=0.25):
    b = BARRES_PAR_JOUR[intervalle]
    c = df.close
    vol = np.log(c).diff().rolling(30 * b, min_periods=10 * b).std()
    rang_vol = vol.expanding(min_periods=180 * b).rank(pct=True)
    n = 60 * b
    efficacite = (c - c.shift(n)).abs() / c.diff().abs().rolling(n).sum()
    dd = c / c.rolling(365 * b, min_periods=30 * b).max() - 1
    r30 = c / c.shift(30 * b) - 1
    e = pd.Series("range", index=df.index)
    e[efficacite >= seuil_efficacite] = "tendance"
    e[rang_vol >= 0.8] = "forte_volatilite"
    e[(dd <= -0.40) | (r30 <= -0.25)] = "crise"
    e[efficacite.isna()] = "inconnu"
    return e


def par_regime(res, regimes, intervalle):
    """Rendement annualisé et Sharpe de la stratégie dans chaque régime (régime connu à la clôture précédente)."""
    b = BARRES_PAR_JOUR[intervalle]
    reg = regimes.shift(1)
    out = {}
    for nom in REGIMES:
        r = res["net"][reg == nom]
        if len(r) < 30 * b:
            out[nom] = {"part_du_temps": float((reg == nom).mean()), "rendement_annualise": None, "sharpe": None}
            continue
        vol = r.std() * np.sqrt(365 * b)
        out[nom] = {"part_du_temps": float((reg == nom).mean()),
                    "rendement_annualise": float(r.mean() * 365 * b),
                    "sharpe": float(r.mean() * 365 * b / vol) if vol else 0.0}
    return out
