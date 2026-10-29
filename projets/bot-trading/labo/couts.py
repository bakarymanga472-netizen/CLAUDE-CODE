"""Labo — modèle de coûts d'exécution.

Coût par unité de rotation = commission + demi-spread variable + glissement variable.
- commission : 0,10 % (Binance spot, taker, sans remise BNB).
- demi-spread : base × (vol récente / vol médiane passée), plancher = base. La vol est mesurée avec des données passées seulement.
- glissement : fraction de l'écart-type d'une barre (plus fort en marché agité).
- financement : appliqué aux positions courtes (perpétuel) ou empruntées ; 0 pour du spot long-only.
Les paramètres de base sont des hypothèses, pas des mesures du carnet d'ordres : ils sont stressés ×2 et ×3 dans chaque rapport.
"""
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Couts:
    commission: float = 0.0010
    demi_spread_base: float = 0.0001
    glissement_sigma: float = 0.05        # fraction de l'écart-type d'une barre
    financement_8h: float = 0.0001        # perpétuel, payé par les positions courtes nettes si > 0 (convention simplifiée)
    retard_barres: int = 1                # exécution à l'ouverture de la barre suivante (1) ou plus tard

    def stresse(self, facteur=1.0, retard=None):
        return replace(self, commission=self.commission * facteur, demi_spread_base=self.demi_spread_base * facteur,
                       glissement_sigma=self.glissement_sigma * facteur,
                       retard_barres=self.retard_barres if retard is None else retard)


def cout_unitaire(df, c: Couts):
    """Coût (fraction) d'une unité de rotation à l'ouverture de chaque barre, avec des infos connues à la clôture précédente."""
    r = np.log(df.close).diff()
    sigma = r.rolling(100, min_periods=20).std()
    med = sigma.expanding(min_periods=20).median()
    spread = c.demi_spread_base * (sigma / med).clip(lower=1.0)
    cout = c.commission + spread.fillna(c.demi_spread_base) + c.glissement_sigma * sigma.fillna(sigma.mean())
    return cout.shift(1).bfill()          # connu à la clôture précédente


def financement_par_barre(df, c: Couts, intervalle_h):
    return pd.Series(c.financement_8h * intervalle_h / 8.0, index=df.index)
