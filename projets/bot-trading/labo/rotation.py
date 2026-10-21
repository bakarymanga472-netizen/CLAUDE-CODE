"""Nouvelle approche « gros gains, pertes contrôlées » (demande du 2026-10-21) — tour 7 : suivre la force (momentum)
au lieu d'acheter les baisses. Famille documentée : Antonacci (« Dual Momentum », GEM), Faber (rotation d'ETF,
filtre MM200/10 mois), timing à levier d'un indice au-dessus de sa MM200.

Variantes FIXÉES AVANT EXÉCUTION :
- R1 GEM : chaque fin de mois, si SPY a fait mieux que les bons du Trésor sur 12 mois → le meilleur de SPY/EFA sur
  12 mois, sinon IEF (obligations 7-10 ans).
- R2 Rotation : chaque fin de mois, les 3 ETF (univers U40) au plus fort rendement 12 mois hors dernier mois, parmi
  ceux au-dessus de leur MM200 ; parts égales ; places vides → IEF s'il est au-dessus de sa MM200, sinon Trésor.
- R3-L : QQQ à levier L ∈ {2, 3} quand QQQ clôture au-dessus de sa MM200 (décision à la clôture, exécution à la
  suivante), sinon Trésor. Rendement quotidien = L × QQQ − (L−1) × Trésor − 0,95 %/an de frais (type TQQQ/QLD).
Exécution à la clôture suivant la décision ; coûts 0,02 % par côté sur le volume échangé ; cash au taux ^IRX.
Choix : meilleur rapport rendement / pire baisse (Calmar) sur 2008-2015. 2001-2007 (bulle internet) = test de choc.
Usage : python3 -m labo.rotation → rapports/rotation.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import donnees
from .haute_reussite import U40, taux_tresor

ICI = Path(__file__).resolve().parent.parent
COUT = 0.0002
PERIODES = {"2001-2007 (choc bulle)": ("2001-01-01", "2007-12-31"), "2008-2015 (choix)": ("2008-01-01", "2015-12-31"),
            "2016-2021": ("2016-01-01", "2021-12-31"), "2022-2024": ("2022-01-01", "2024-12-31"),
            "2025 → auj.": ("2025-01-01", "2100-01-01")}


def prix(symboles):
    c = pd.DataFrame({s: donnees.charger_yahoo(s)[0].close for s in symboles}).sort_index()
    return c.loc["1999-06-01":]


def portefeuille(poids, c, tb):
    """poids : DataFrame (index = jours de décision) ; exécution à la clôture suivante, détenu ensuite."""
    w = poids.reindex(c.index).ffill().shift(1).fillna(0.0)          # décidé à t, en place après la clôture t+1
    w = w.shift(1).fillna(0.0)
    r = c.pct_change(fill_method=None).fillna(0.0)
    brut = (w * r[w.columns]).sum(axis=1)
    cash = (1 - w.sum(axis=1)).clip(lower=0.0) * tb
    rot = w.diff().abs().sum(axis=1).fillna(0.0) * COUT
    return brut + cash - rot


def fins_de_mois(index):
    s = pd.Series(index, index=index)
    return s.groupby([index.year, index.month]).max().values


def r1(c, tb):
    fm = fins_de_mois(c.index)
    tr12 = (1 + tb).cumprod()
    w = pd.DataFrame(0.0, index=fm, columns=["SPY", "EFA", "IEF"])
    for d in fm:
        i = c.index.get_loc(d)
        if i < 252:
            continue
        ret = c.iloc[i] / c.iloc[i - 252] - 1
        t12 = tr12.iloc[i] / tr12.iloc[i - 252] - 1
        if ret.SPY > t12:
            w.loc[d, "SPY" if ret.SPY >= ret.EFA else "EFA"] = 1.0
        else:
            w.loc[d, "IEF"] = 1.0
    return portefeuille(w, c[["SPY", "EFA", "IEF"]], tb)


def r2(c, tb, n=3):
    fm = fins_de_mois(c.index)
    mm = c.rolling(200).mean()
    w = pd.DataFrame(0.0, index=fm, columns=c.columns)
    for d in fm:
        i = c.index.get_loc(d)
        if i < 252:
            continue
        mom = c.iloc[i - 21] / c.iloc[i - 252] - 1
        ok = mom[(c.iloc[i] > mm.iloc[i]) & mom.notna()].sort_values(ascending=False)
        choix = list(ok.index[:n])
        for s in choix:
            w.loc[d, s] = 1.0 / n
        if len(choix) < n and c.IEF.iloc[i] > mm.IEF.iloc[i]:
            w.loc[d, "IEF"] += (n - len(choix)) / n
    return portefeuille(w, c, tb)


def r3(c, tb, L):
    q = c.QQQ
    dedans = (q > q.rolling(200).mean()).astype(float).shift(2).fillna(0.0)   # décision t, exécution t+1, détenu t+2
    r = q.pct_change(fill_method=None).fillna(0.0)
    lev = L * r - (L - 1) * tb - 0.0095 / 252
    rot = dedans.diff().abs().fillna(0.0) * COUT * L
    return dedans * lev + (1 - dedans) * tb - rot


def stats(x, a, b):
    x = x.loc[a:b]
    v = (1 + x).cumprod()
    an = max((x.index[-1] - x.index[0]).days / 365.25, 0.1)
    m = (1 + x).resample("ME").prod() - 1
    cagr, dd = v.iloc[-1] ** (1 / an) - 1, (v / v.cummax() - 1).min()
    return {"rend": cagr, "baisse": dd, "calmar": cagr / abs(dd) if dd < 0 else 0, "sharpe": m.mean() / m.std() * np.sqrt(12),
            "mois_pos": (m > 0).mean(), "pire_mois": m.min(), "final": v.iloc[-1]}


def main():
    c = prix(sorted(set(U40 + ["QQQ", "IEF", "EFA", "SPY"])))
    tb = taux_tresor(c.index)
    v = {"R1 GEM": r1(c, tb), "R2 Rotation top 3": r2(c, tb), "R3 QQQ ×2 > MM200": r3(c, tb, 2), "R3 QQQ ×3 > MM200": r3(c, tb, 3),
         "SPY gardé": c.SPY.pct_change(fill_method=None).fillna(0.0), "QQQ gardé": c.QQQ.pct_change(fill_method=None).fillna(0.0)}
    fin = c.index[-1]
    per = {**PERIODES, "5 ans": (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")}
    m = {n: {p: stats(x, a, b) for p, (a, b) in per.items()} for n, x in v.items()}
    choix = max([n for n in v if n.startswith("R")], key=lambda n: m[n]["2008-2015 (choix)"]["calmar"])
    L = [f"# Tour 7 — momentum et levier (données jusqu'au {fin.date()})\n",
         "Commande : `python3 -m labo.rotation` · règles fixées avant exécution : en-tête du fichier.\n",
         "| Stratégie | Période | Rendement/an | Pire baisse | Calmar | Sharpe | Mois positifs | Pire mois |", "|---|---|---|---|---|---|---|---|"]
    for n, d in m.items():
        for p, x in d.items():
            L.append(f"| {n}{' ← choisie' if n == choix else ''} | {p} | {x['rend']:+.1%} | {x['baisse']:.0%} | {x['calmar']:.2f} | "
                     f"{x['sharpe']:.2f} | {x['mois_pos']:.0%} | {x['pire_mois']:+.1%} |")
    L.append("\n| Stratégie | 20 000 € sur 5 ans → |\n|---|---|")
    for n in v:
        L.append(f"| {n} | {20000 * m[n]['5 ans']['final']:,.0f} € |")
    L.append(f"\nChoisie par la règle (Calmar 2008-2015) : **{choix}**.")
    (ICI / "rapports" / "rotation.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
