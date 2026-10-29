"""Labo — moteur de backtest barre par barre.

Chronologie (pas de look-ahead) :
  clôture de la barre t  → la stratégie décide une exposition avec les données ≤ t ;
  ouverture de t+retard  → l'ordre est exécuté, avec coûts connus à la clôture précédente ;
  le rendement porté est celui d'ouverture à ouverture.
Taille : exposition × min(1, vol_cible / vol réalisée 30 jours), sans levier, rééquilibrage seulement si l'écart > 10 points.
"""
import numpy as np
import pandas as pd

from .couts import Couts, cout_unitaire, financement_par_barre
from .donnees import BARRES_PAR_JOUR, par_an

VOL_CIBLE = 0.40
SEUIL_REEQUILIBRAGE = 0.10
HEURES = {"1d": 24, "4h": 4, "1h": 1}


def taille(df, cible, intervalle, vol_cible=VOL_CIBLE):
    bpj = BARRES_PAR_JOUR[intervalle]
    vol = np.log(df.close).diff().rolling(30 * bpj, min_periods=10 * bpj).std() * np.sqrt(par_an(df.index))
    return (cible.clip(-1, 1) * (vol_cible / vol).clip(upper=1.0)).fillna(0.0)


def _hysteresis(w):
    out, cur = np.zeros(len(w)), 0.0
    for i, x in enumerate(w):
        if (x == 0) != (cur == 0) or abs(x - cur) > SEUIL_REEQUILIBRAGE:
            cur = x
        out[i] = cur
    return out


def simuler(df, cible, intervalle, couts=Couts(), vol_cible=VOL_CIBLE, dimensionner=True, execution="ouverture"):
    """execution = "ouverture" : exécuté à l'ouverture de la barre t+retard, rendement ouverture → ouverture.
    execution = "cloture" : exécuté à la CLÔTURE de la barre t+retard (ordre au cours de clôture), rendement clôture → clôture."""
    voulu = taille(df, cible, intervalle, vol_cible) if dimensionner else cible.clip(-1, 1).fillna(0.0)
    decale = couts.retard_barres + (1 if execution == "cloture" else 0)
    w = pd.Series(_hysteresis(voulu.values), index=df.index).shift(decale).fillna(0.0)
    if execution == "cloture":
        r_oo = df.close.pct_change().fillna(0.0)          # la position exécutée à la clôture t-1 porte t-1 → t
    else:
        r_oo = (df.open.shift(-1) / df.open - 1).fillna(0.0)
    cu = cout_unitaire(df, couts)
    rotation = w.diff().abs().fillna(w.abs())
    cout = rotation * cu
    fin = (-w).clip(lower=0) * financement_par_barre(df, couts, HEURES[intervalle])
    brut = w * r_oo
    net = brut - cout - fin
    return {"net": net, "brut": brut, "w": w, "cout": cout + fin, "trades": trades(df, w, net, brut, cout + fin, intervalle)}


def atr(df, n):
    pc = df.close.shift(1)
    tr = pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def trades(df, w, net, brut, cout, intervalle):
    """Un trade = une période continue d'exposition non nulle (la barre de sortie, qui porte le coût, est incluse).
    R = risque initial = 2 × écart-type JOURNALIER (14 jours) × exposition d'entrée (stop théorique, non exécuté).
    Même unité de risque quelle que soit l'unité de temps, pour que les R soient comparables."""
    bpj = BARRES_PAR_JOUR[intervalle]
    a = (2 * np.log(df.close).diff().rolling(14 * bpj).std() * np.sqrt(bpj)).shift(1)   # connu avant l'exécution
    actif = (w != 0).values
    lignes, i, n = [], 0, len(w)
    while i < n:
        if not actif[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and actif[j + 1]:
            j += 1
        fin = min(j + 1, n - 1)
        seg = slice(i, fin + 1)
        rn = float(np.prod(1 + net.values[seg]) - 1)
        rb = float(np.prod(1 + brut.values[seg]) - 1)
        risque = float(a.iloc[i] * abs(w.iloc[i])) if pd.notna(a.iloc[i]) else np.nan
        lignes.append({"entree": df.index[i], "sortie": df.index[fin], "barres": fin - i + 1,
                       "expo_entree": float(w.iloc[i]), "brut": rb, "net": rn,
                       "couts": float(cout.values[seg].sum()), "R": rn / risque if risque else np.nan})
        i = fin + 1
    return pd.DataFrame(lignes)


def mesures(net, trades_df, intervalle, w=None):
    bpj = BARRES_PAR_JOUR[intervalle]
    if len(net) < 10:
        return None
    courbe = (1 + net).cumprod()
    annees = max((net.index[-1] - net.index[0]).days / 365.25, 1e-9)
    k = par_an(net.index)
    vol = net.std() * np.sqrt(k)
    t = trades_df
    gains, pertes = (t.net[t.net > 0].sum(), -t.net[t.net <= 0].sum()) if len(t) else (0, 0)
    an = (1 + net).groupby(net.index.year).prod() - 1
    return {
        "rendement_total": float(courbe.iloc[-1] - 1),
        "rendement_annuel": float(courbe.iloc[-1] ** (1 / annees) - 1),
        "volatilite": float(vol),
        "sharpe": float(net.mean() * k / vol) if vol > 0 else 0.0,
        "pire_baisse": float((courbe / courbe.cummax() - 1).min()),
        "trades": int(len(t)),
        "reussite": float((t.net > 0).mean()) if len(t) else np.nan,
        "profit_factor": float(gains / pertes) if pertes > 0 else (np.inf if gains > 0 else np.nan),
        "esperance_trade": float(t.net.mean()) if len(t) else np.nan,
        "esperance_R": float(t.R.mean()) if len(t) and t.R.notna().any() else np.nan,
        "exposition_moyenne": float(w.abs().mean()) if w is not None else np.nan,
        "annees_positives": f"{int((an > 0).sum())}/{len(an)}",
    }


def periode(res, debut, fin, intervalle):
    net, w = res["net"].loc[debut:fin], res["w"].loc[debut:fin]
    t = res["trades"]
    t = t[(t.entree >= pd.Timestamp(debut)) & (t.entree <= pd.Timestamp(fin))] if len(t) else t
    return mesures(net, t, intervalle, w)
