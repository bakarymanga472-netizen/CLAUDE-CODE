"""Labo — caractéristiques statistiques d'un marché (descriptives, calculées sur la période de développement)."""
import numpy as np
import pandas as pd

from .donnees import BARRES_PAR_JOUR


def ratio_variance(r, q):
    """Lo-MacKinlay : > 1 = persistance (tendance), < 1 = retour à la moyenne, à l'horizon q barres."""
    rq = r.rolling(q).sum().dropna()
    return float(rq.var() / (q * r.var()))


def decrire(df, intervalle):
    bpj = BARRES_PAR_JOUR[intervalle]
    r = np.log(df.close).diff().dropna()
    courbe = df.close / df.close.cummax() - 1
    return {
        "vol_annuelle": float(r.std() * np.sqrt(365 * bpj)),
        "asymetrie": float(r.skew()),
        "aplatissement_exces": float(r.kurt()),
        "autocorr_1_barre": float(r.autocorr(1)),
        "ratio_variance_1j": ratio_variance(r, max(2, bpj)) if bpj > 1 else ratio_variance(r, 2),
        "ratio_variance_1sem": ratio_variance(r, 7 * bpj),
        "ratio_variance_1mois": ratio_variance(r, 30 * bpj),
        "pire_baisse_achat_conservation": float(courbe.min()),
        "part_jours_sous_moins_50pct": float((courbe < -0.5).mean()),
    }
