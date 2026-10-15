"""Aladdin — moteur : rendement du portefeuille, frais, statistiques, taux de réussite par trade."""
import numpy as np
import pandas as pd

from .donnees import FRAIS, type_actif


def portefeuille(px, poids):
    """Poids décidés à la clôture de t → appliqués au rendement de t+1, frais sur la rotation."""
    rend = px.pct_change().fillna(0.0)
    p = poids.shift(1).fillna(0.0)
    frais = pd.Series({c: FRAIS[type_actif(c)] for c in px.columns})
    rotation = p.diff().abs().fillna(p.abs())
    r = (p * rend).sum(axis=1) - (rotation * frais).sum(axis=1)
    return r


def stats(r, debut=None, fin=None):
    r = r.loc[debut:fin]
    r = r[r.index >= r.ne(0).idxmax()] if r.ne(0).any() else r
    courbe = (1 + r).cumprod()
    annees = max((r.index[-1] - r.index[0]).days / 365.25, 1e-9)
    total = courbe.iloc[-1] - 1
    vol = r.std() * np.sqrt(365)
    return {"rendement": total, "par_an": (1 + total) ** (1 / annees) - 1,
            "pire_baisse": (courbe / courbe.cummax() - 1).min(),
            "sharpe": r.mean() * 365 / vol if vol > 0 else np.nan,
            "jours_gagnants": (r[r != 0] > 0).mean()}


def trades(px, signal, debut=None, fin=None):
    """Un trade = une période continue où le signal est à 1 sur un actif. Rendement net des frais aller-retour."""
    out = []
    for c in px.columns:
        s = signal[c].fillna(0).values
        p = px[c].values
        idx = px.index
        i = 0
        while i < len(s):
            if s[i] > 0:
                j = i
                while j + 1 < len(s) and s[j + 1] > 0:
                    j += 1
                sortie = min(j + 1, len(s) - 1)
                if not np.isnan(p[i]) and not np.isnan(p[sortie]):
                    r = p[sortie] / p[i] * (1 - 2 * FRAIS[type_actif(c)]) - 1
                    out.append((c, idx[i], idx[sortie], r))
                i = j + 1
            else:
                i += 1
    t = pd.DataFrame(out, columns=["actif", "entree", "sortie", "rendement"])
    if debut or fin:
        t = t[(t.entree >= pd.Timestamp(debut or "1900")) & (t.entree <= pd.Timestamp(fin or "2100"))]
    return t


def piege_99(px, actif="BTC", gain=0.01, perte=0.50):
    """Démonstration : prendre +1 % dès qu'il vient, ne couper qu'à -50 %.
    Taux de réussite énorme… mais regarde le rendement."""
    p = px[actif].dropna()
    res, i = [], 0
    v = p.values
    while i < len(v) - 1:
        e = v[i]
        j = i + 1
        while j < len(v) and e * (1 - perte) < v[j] < e * (1 + gain):
            j += 1
        if j >= len(v):
            break
        res.append(v[j] / e * (1 - 2 * FRAIS["crypto"]) - 1)
        i = j + 1
    res = np.array(res)
    capital = np.prod(1 + res)
    return {"trades": len(res), "reussite": (res > 0).mean(), "capital_final": capital - 1,
            "garder": v[-1] / v[0] - 1}
