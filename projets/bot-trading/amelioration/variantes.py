"""Construction d'une exposition à partir d'une spécification de version (stratégie + paramètres + modifications)."""
import importlib

import numpy as np
import pandas as pd

from labo import regimes
from labo.donnees import BARRES_PAR_JOUR

from .garde_fous import verifier_spec


def _stop_suiveur(df, cible, k, bpj):
    sigma = np.log(df.close).diff().rolling(30 * bpj).std() * np.sqrt(bpj)
    out, en_pos, haut, bloque = np.zeros(len(df)), False, 0.0, False
    for i, (c, s, x) in enumerate(zip(df.close.values, sigma.values, cible.values)):
        if x <= 0:
            en_pos, bloque = False, False
            continue
        if bloque:
            continue                         # stop touché : on attend que le signal retombe avant de reprendre
        if not en_pos:
            en_pos, haut = True, c
        haut = max(haut, c)
        if np.isfinite(s) and c < haut * (1 - k * s):
            bloque, en_pos = True, False
            continue
        out[i] = x
    return pd.Series(out, index=df.index)


def exposition(df, spec):
    verifier_spec(spec)
    tf = spec.get("intervalle", "1d")
    bpj = BARRES_PAR_JOUR[tf]
    s = importlib.import_module(f"labo.strategies.{spec['strategie']}")
    c = s.cible(df, bpj, **spec["params"])
    for m in spec.get("modifications", []):
        if m["type"] == "regimes_exclus":
            reg = regimes.etiqueter(df, tf, m.get("seuil_efficacite", 0.25))        # données ≤ t : décision à la clôture t
            c = c * (~reg.isin(m["regimes"])).astype(float)
        elif m["type"] == "stop_suiveur":
            c = _stop_suiveur(df, c, m["k_sigma"], bpj)
        else:
            raise ValueError(f"modification inconnue : {m['type']}")
    return c
