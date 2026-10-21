"""Surveillance des performances et détection de changements, avec les seuils fixés dans seuils.json."""
import json
from math import erf, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

SEUILS = json.loads((Path(__file__).parent / "seuils.json").read_text())


def _p_moyenne_negative(x):
    """p-valeur (approx. normale) que la moyenne soit ≥ 0 contre < 0."""
    x = np.asarray(x, dtype=float)
    if len(x) < 5 or x.std(ddof=1) == 0:
        return 1.0
    z = x.mean() / (x.std(ddof=1) / sqrt(len(x)))
    return 0.5 * (1 + erf(z / sqrt(2)))


def psi(reference, recent, bins=10):
    """Population Stability Index : dérive de distribution d'une caractéristique."""
    q = np.unique(np.quantile(reference, np.linspace(0, 1, bins + 1)))
    a = np.histogram(reference, q)[0] / len(reference) + 1e-6
    b = np.histogram(np.clip(recent, q[0], q[-1]), q)[0] / len(recent) + 1e-6
    return float(((b - a) * np.log(b / a)).sum())


def indicateurs(df, net_jour, trades, ref):
    """ref : {pire_baisse, cout_moyen_trade, reussite_c5} issus du backtest de la version."""
    S = SEUILS
    n = S["fenetre_trades"]
    alertes = []
    if len(trades) >= n:
        dern = trades.tail(n)
        p = _p_moyenne_negative(dern.net)
        if dern.net.mean() < 0 and p < S["esperance_glissante_p_max"]:
            alertes.append(f"espérance glissante {n} trades négative (p = {p:.3f})")
        if dern.net.gt(0).mean() < ref["reussite_c5"]:
            alertes.append("taux de réussite sous le 5e centile attendu")
        if "couts" in dern and dern.couts.mean() > S["cout_multiple_modele"] * ref["cout_moyen_trade"]:
            alertes.append("coûts réels > 2× le modèle")
    courbe = (1 + net_jour).cumprod()
    dd = float((courbe / courbe.cummax() - 1).iloc[-1])
    if dd < S["drawdown_multiple_backtest"] * ref["pire_baisse"]:
        alertes.append(f"baisse en cours {dd:.0%} au-delà de 1,5× la pire baisse du backtest")
    an = net_jour.tail(S["fenetre_jours"])
    sh = an.mean() / an.std() * np.sqrt(365) if an.std() > 0 else 0
    if sh < S["sharpe_glissant_min"]:
        alertes.append(f"Sharpe glissant 1 an {sh:.2f} < {S['sharpe_glissant_min']}")
    r = np.log(df.close).diff()
    vol30, volmed = r.tail(30).std(), r.rolling(30).std().tail(365).median()
    if vol30 > S["vol_multiple_mediane"] * volmed:
        alertes.append("volatilité 30 j > 2× sa médiane d'un an")
    v30, vmed = df.volume.tail(30).mean(), df.volume.rolling(30).mean().tail(365).median()
    if v30 < S["volume_multiple_min"] * vmed:
        alertes.append("liquidité : volume 30 j < 0,5× sa médiane d'un an")
    caracs = pd.DataFrame({"r": r, "amplitude": (df.high - df.low) / df.close}).dropna()
    for col in caracs:
        x = psi(caracs[col].iloc[-395:-30].values, caracs[col].tail(30).values)
        if x > S["psi_max"]:
            alertes.append(f"dérive des données « {col} » (PSI {x:.2f})")
    return {"sharpe_glissant_1an": float(sh), "baisse_en_cours": dd, "alertes": alertes}


# ---------- Détecteurs de changement, évalués sur l'historique ----------
def detecteurs(df):
    """Événements datés (connus à la clôture) pour chaque détecteur."""
    c = df.close
    r = np.log(c).diff()
    vol = r.rolling(30).std()
    eff = (c - c.shift(60)).abs() / c.diff().abs().rolling(60).sum()
    amp = ((df.high - df.low) / c).rolling(30).mean()
    volu = df.volume.rolling(30).mean()
    return {
        "hausse_volatilite": (vol > 2 * vol.rolling(365).median()) & ~(vol.shift(1) > 2 * vol.shift(1).rolling(365).median()),
        "tendance_vers_range": (eff < 0.25) & (eff.shift(1) >= 0.25),
        "hausse_couts_proxy": (amp > 2 * amp.rolling(365).median()) & ~(amp.shift(1) > 2 * amp.shift(1).rolling(365).median()),
        "baisse_liquidite": (volu < 0.5 * volu.rolling(365).median()) & ~(volu.shift(1) < 0.5 * volu.shift(1).rolling(365).median()),
    }


def evaluer_detecteurs(df, strategie_jour=None, horizon=30):
    """Pour chaque détecteur : l'état annoncé persiste-t-il sur les `horizon` jours suivants plus souvent qu'au hasard ?"""
    c = df.close
    r = np.log(c).diff()
    fut_vol = r[::-1].rolling(horizon).std()[::-1].shift(-1)
    fut_eff = ((c.shift(-horizon) - c).abs() / c.diff().abs()[::-1].rolling(horizon).sum()[::-1].shift(-1))
    fut_amp = ((df.high - df.low) / c)[::-1].rolling(horizon).mean()[::-1].shift(-1)
    fut_volu = df.volume[::-1].rolling(horizon).mean()[::-1].shift(-1)
    criteres = {
        "hausse_volatilite": fut_vol > r.rolling(365).std(),
        "tendance_vers_range": fut_eff < 0.25,
        "hausse_couts_proxy": fut_amp > ((df.high - df.low) / c).rolling(365).median(),
        "baisse_liquidite": fut_volu < df.volume.rolling(365).median(),
    }
    out = {}
    for nom, ev in detecteurs(df).items():
        ok = criteres[nom].dropna()
        ev = ev.reindex(ok.index).fillna(False).astype(bool)
        base = float(ok.mean())
        n = int(ev.sum())
        succes = float(ok[ev].mean()) if n else None
        from memoire.analyste import binom_sup
        p = binom_sup(int(round(succes * n)), n, base) if n else None
        out[nom] = {"evenements": n, "taux_succes": succes, "taux_de_base": base, "p_valeur": p}
    if strategie_jour is not None:
        cum = strategie_jour.cumsum()
        cusum = (strategie_jour - strategie_jour.expanding(365).mean()).rolling(90).sum()
        ev = cusum < -2 * strategie_jour.rolling(365).std() * np.sqrt(90)
        ev = ev & ~ev.shift(1, fill_value=False)
        fut = strategie_jour[::-1].rolling(90).sum()[::-1].shift(-1)
        ok = (fut < 0).dropna()
        ev = ev.reindex(ok.index).fillna(False).astype(bool)
        n = int(ev.sum())
        from memoire.analyste import binom_sup
        succes = float(ok[ev].mean()) if n else None
        out["deterioration_esperance"] = {"evenements": n, "taux_succes": succes, "taux_de_base": float(ok.mean()),
                                          "p_valeur": binom_sup(int(round(succes * n)), n, float(ok.mean())) if n else None}
    return out
