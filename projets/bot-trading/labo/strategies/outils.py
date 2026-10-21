import numpy as np
import pandas as pd


def rsi(close, n):
    d = close.diff()
    h = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    b = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + h / b.replace(0, np.nan))


def etat(entree, sortie):
    """Machine à états : 1 dès qu'entree est vrai, retombe à 0 dès que sortie est vrai."""
    pos, out = 0.0, np.zeros(len(entree))
    for i, (e, s) in enumerate(zip(entree.values, sortie.values)):
        if pos == 0 and e:
            pos = 1.0
        elif pos == 1 and s:
            pos = 0.0
        out[i] = pos
    return pd.Series(out, index=entree.index)
