"""Aladdin — les desks (stratégies) et le desk risque.

Chaque desk renvoie un signal 0/1 par actif et par jour, calculé avec les cours jusqu'à t inclus.
Le moteur l'applique au rendement de t+1 (aucun regard vers le futur).
"""
import numpy as np
import pandas as pd


def desk_momentum(px, lookback):
    """Momentum de série temporelle : long si l'actif a monté sur `lookback` jours."""
    return (px / px.shift(lookback) - 1 > 0).astype(float).where(px.notna(), 0.0)


def desk_moyennes(px, rapide, lente):
    """Croisement de moyennes mobiles : long si MM rapide > MM lente."""
    return (px.rolling(rapide).mean() > px.rolling(lente).mean()).astype(float).where(px.notna(), 0.0)


def rsi(px, n):
    d = px.diff()
    h = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    b = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + h / b.replace(0, np.nan))


def desk_rebond(px, seuil, n=2, filtre=200):
    """Retour à la moyenne (type Connors RSI-2) : achète une forte baisse court terme dans une tendance haussière,
    revend dès que le cours repasse au-dessus de sa moyenne 5 jours."""
    r = rsi(px, n)
    tendance = px > px.rolling(filtre).mean()
    au_dessus = px > px.rolling(5).mean()
    sig = pd.DataFrame(0.0, index=px.index, columns=px.columns)
    for c in px.columns:
        en_pos, out = False, np.zeros(len(px))
        rv, tv, av = r[c].values, tendance[c].values, au_dessus[c].values
        for i in range(len(px)):
            if not en_pos and tv[i] and rv[i] < seuil:
                en_pos = True
            elif en_pos and av[i]:
                en_pos = False
            out[i] = 1.0 if en_pos else 0.0
        sig[c] = out
    return sig.where(px.notna(), 0.0)


def desk_risque(px, signal, vol_cible=0.15, fenetre=60):
    """Volatilité cible : chaque position est dimensionnée pour viser `vol_cible` annualisée sur le portefeuille,
    à risque égal entre actifs, sans levier (somme des poids ≤ 100 %)."""
    rend = px.pct_change()
    vol = rend.rolling(fenetre, min_periods=40).std() * np.sqrt(365)
    actifs = signal.notna() & px.notna() & vol.notna()
    n = actifs.sum(axis=1).clip(lower=1)
    poids = signal * (vol_cible / vol).clip(upper=3.0)
    poids = poids.div(np.sqrt(n), axis=0).fillna(0.0)
    total = poids.sum(axis=1)
    poids = poids.div(total.clip(lower=1.0), axis=0)        # pas de levier
    return poids


def poids_egaux(signal):
    """Sans desk risque : chaque actif en position reçoit la même part."""
    n = signal.notna().sum(axis=1).clip(lower=1)
    return signal.fillna(0).div(n, axis=0)
