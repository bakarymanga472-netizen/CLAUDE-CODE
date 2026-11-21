"""Fusion multi-approches (demande du 2026-10-21) — tour 9, déclaré après les tours 1-8.

15 moteurs (chacun une série de rendements quotidiens, frais 0,02 % par côté, cash au taux ^IRX) :
 M1  bot haute réussite (50 % tendance + 50 % D1F1 ×2)        M2  rotation top 3 (R2)       M3  QQQ ×2 > MM200 (R3)
 M4  GEM (R1)                                                  M5  portefeuille de tendance seul (crypto, SPY, GLD, TLT)
 M6  D1F1 élargi ×2 seul                                       M7  début de mois : SPY du dernier jour du mois aux 3 premiers
 M8  veille Fed : SPY le jour des décisions FOMC programmées (Lucca-Moench 2015 ; calendrier connu à l'avance)
 M9  saisonnalité « Halloween » : SPY de novembre à avril, IEF de mai à octobre
 M10 parité de risque : SPY, TLT, GLD, DBC pondérés par 1/volatilité 60 j, chaque mois
 M11 tendance or : GLD > MM200, sinon Trésor          M12 tendance obligations : TLT > MM200, sinon Trésor
 M13 croisement SPY MM50 > MM200, sinon IEF            M14 rotation sectorielle : 3 secteurs XL* les plus forts (12-1 mois) > MM200
 M15 tendance pays : 3 ETF pays/régions les plus forts (12-1 mois) > MM200, sinon IEF
Fusions FIXÉES AVANT EXÉCUTION (rééquilibrage mensuel) :
 F-EG  : poids égaux sur les 15 ;
 F-IV  : poids ∝ 1 / volatilité des 252 séances précédentes (aucune information future) ;
 F-SEL : poids égaux sur les moteurs au Sharpe ≥ 0,5 sur 2008-2015 (sélection sur la période de choix uniquement).
Choix : meilleur Sharpe 2008-2015. Puis curseur « volatilité cible » 15 %/an (levier = 15 % / vol 60 j, plafonné à ×2,
financement 5 %/an sur la part empruntée) pour transformer la régularité en rendement.
Usage : python3 -m labo.fusion → rapports/fusion.md
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .combine import ruine
from .combo3 import melange
from .haute_reussite import U40, charger, lancer, taux_tresor
from .portefeuille import UNIVERS as UT, executer
from .rotation import PERIODES, fins_de_mois, portefeuille, prix, r1, r2, r3, stats

ICI = Path(__file__).resolve().parent.parent
SECTEURS = ["XLE", "XLF", "XLK", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB"]
PAYS = ["SPY", "EFA", "EEM", "VGK", "EWJ", "EWZ", "FXI", "EWG", "EWU", "EWC", "EWA", "EWT"]
FOMC = pd.to_datetime(json.loads((Path(__file__).parent / "fomc_dates.json").read_text()))


def tenir(sig, ret, tb, lag=2):
    """sig quotidien 0/1 décidé à la clôture ; détenu à partir de lag séances après (2 = exécution à la clôture suivante)."""
    w = sig.astype(float).shift(lag).fillna(0.0)
    return w * ret + (1 - w) * tb - w.diff().abs().fillna(0.0) * 0.0002


def calendrier(mask, ret, tb):
    """Fenêtre connue à l'avance : position prise la veille, aucun retard supplémentaire."""
    return tenir(mask, ret, tb, lag=0)


def top_n(c, univ, tb, n=3, repli="IEF"):
    cc = c[univ + ([repli] if repli and repli not in univ else [])]
    mm = cc.rolling(200).mean()
    fm = fins_de_mois(cc.index)
    w = pd.DataFrame(0.0, index=fm, columns=cc.columns)
    for d in fm:
        i = cc.index.get_loc(d)
        if i < 252:
            continue
        mom = (cc[univ].iloc[i - 21] / cc[univ].iloc[i - 252] - 1)
        ok = mom[(cc[univ].iloc[i] > mm[univ].iloc[i]) & mom.notna()].sort_values(ascending=False).index[:n]
        for s in ok:
            w.loc[d, s] = 1 / n
        if repli and len(ok) < n:
            w.loc[d, repli] += (n - len(ok)) / n
    return portefeuille(w, cc, tb)


def moteurs():
    c40, _, _ = charger(U40)
    s = c40.index
    tend, _ = executer(UT)
    tend = (1 + tend).groupby(tend.index.to_series().apply(lambda d: s[s.searchsorted(d)] if d <= s[-1] else pd.NaT)).prod() - 1
    tend = tend.reindex(s).fillna(0.0)
    _, d1, _ = lancer(U40, 10, True, levier=2.0)
    c = prix(sorted(set(U40 + ["QQQ", "IEF", "EFA", "SPY", "TLT", "GLD", "DBC"] + SECTEURS + PAYS))).reindex(s)
    tb = taux_tresor(s)
    ret = c.pct_change(fill_method=None).fillna(0.0)
    M = {}
    M["M1 bot haute réussite"] = melange([tend, d1], [0.5, 0.5])
    M["M2 rotation top 3"] = r2(c[U40], tb)
    M["M3 QQQ ×2 > MM200"] = r3(c, tb, 2)
    M["M4 GEM"] = r1(c, tb)
    M["M5 tendance (crypto/SPY/GLD/TLT)"] = tend
    M["M6 D1F1 ×2"] = d1
    # M7 : dernier jour du mois + 3 premiers jours du mois suivant
    rang = pd.Series(range(len(s)), index=s)
    mois = s.to_period("M")
    debut = rang.groupby(mois).transform("min")
    fin = rang.groupby(mois).transform("max")
    tom = ((rang - debut) < 3) | (rang == fin)
    M["M7 début de mois"] = calendrier(tom, ret.SPY, tb)
    fomc_j = pd.Series(s.isin(FOMC), index=s)
    M["M8 jour de décision Fed"] = calendrier(fomc_j, ret.SPY, tb)
    hiver = pd.Series(s.month.isin([11, 12, 1, 2, 3, 4]), index=s)
    M["M9 Halloween"] = hiver.astype(float) * ret.SPY + (1 - hiver.astype(float)) * ret.IEF - hiver.astype(float).diff().abs().fillna(0) * 0.0002
    fm = fins_de_mois(s)
    rp = c[["SPY", "TLT", "GLD", "DBC"]]
    vol = rp.pct_change(fill_method=None).rolling(60).std()
    w = (1 / vol).div((1 / vol).sum(axis=1), axis=0).loc[fm].fillna(0.0)
    M["M10 parité de risque"] = portefeuille(w, rp, tb)
    M["M11 tendance or"] = tenir(c.GLD > c.GLD.rolling(200).mean(), ret.GLD, tb)
    M["M12 tendance obligations"] = tenir(c.TLT > c.TLT.rolling(200).mean(), ret.TLT, tb)
    x = (c.SPY.rolling(50).mean() > c.SPY.rolling(200).mean()).astype(float).shift(2).fillna(0.0)
    M["M13 SPY MM50 > MM200"] = x * ret.SPY + (1 - x) * ret.IEF - x.diff().abs().fillna(0) * 0.0002
    M["M14 rotation sectorielle"] = top_n(c, SECTEURS, tb)
    M["M15 rotation pays"] = top_n(c, PAYS, tb)
    spy = ret.SPY
    debut_commun = "2007-01-01"                                  # tous les moteurs existent (DBC, VGK… cotés en 2005-2006)
    return {k: v.loc[debut_commun:] for k, v in M.items()}, spy.loc[debut_commun:]


def fusion_iv(M):
    df = pd.DataFrame(M).fillna(0.0)
    vol = df.rolling(252, min_periods=126).std().shift(1)
    out = []
    for _, g in df.groupby(df.index.to_period("M")):
        v0 = vol.loc[g.index[0]]
        w = (1 / v0).replace([np.inf], np.nan)
        w = (w / w.sum()).fillna(1 / len(df.columns)) if w.notna().any() else pd.Series(1 / len(df.columns), index=df.columns)
        v = (1 + g).cumprod() * w.values
        tot = v.sum(axis=1)
        out.append(tot / tot.shift(1).fillna(1.0) - 1)
    return pd.concat(out)


def vol_cible(x, cible=0.15, plafond=2.0):
    L = (cible / (x.rolling(60).std() * np.sqrt(252))).shift(1).clip(upper=plafond).fillna(1.0)
    return L * x - (L - 1).clip(lower=0) * 0.05 / 252


def main():
    M, spy = moteurs()
    fin = spy.index[-1]
    P = {k: v for k, v in PERIODES.items() if not k.startswith("2001")}
    P["5 ans"] = (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")
    sel = [k for k, v in M.items() if stats(v, *P["2008-2015 (choix)"])["sharpe"] >= 0.5]
    F = {"F-EG (15 à parts égales)": melange(list(M.values()), [1 / len(M)] * len(M)),
         "F-IV (1/volatilité)": fusion_iv(M),
         f"F-SEL ({len(sel)} moteurs Sharpe ≥ 0,5 en 2008-15)": melange([M[k] for k in sel], [1 / len(sel)] * len(sel))}
    choix = max(F, key=lambda n: stats(F[n], *P["2008-2015 (choix)"])["sharpe"])
    F[f"{choix.split(' ')[0]} + vol cible 15 %"] = vol_cible(F[choix])
    c3 = melange([M["M1 bot haute réussite"], M["M2 rotation top 3"], M["M3 QQQ ×2 > MM200"]], [1 / 3] * 3)
    lignes = {**{k: v for k, v in M.items()}, "C3 (réf., tour 8)": c3, **F, "SPY gardé": spy}
    L = [f"# Fusion de 15 approches (données jusqu'au {fin.date()})\n", "Commande : `python3 -m labo.fusion` · règles fixées avant exécution : en-tête du fichier.\n",
         f"Moteurs retenus par F-SEL : {', '.join(sel)}.\n", f"Fusion choisie (Sharpe 2008-2015) : **{choix}**.\n",
         "Chaque case : rendement/an / pire baisse.\n",
         "| Stratégie | " + " | ".join(P) + " | Sharpe 5 ans | 20 000 € (5 ans) | Ruine 5 ans |", "|---|" + "---|" * (len(P) + 3)]
    for n, x in lignes.items():
        x = x.loc["2008-01-01":]
        L.append(f"| {n} | " + " | ".join(f"{stats(x, *P[k])['rend']:+.1%} / {stats(x, *P[k])['baisse']:.0%}" for k in P)
                 + f" | {stats(x, *P['5 ans'])['sharpe']:.2f} | {20000 * stats(x, *P['5 ans'])['final']:,.0f} € | {ruine(x):.0%} |")
    corr = pd.DataFrame(M).loc["2008":].resample("ME").apply(lambda g: (1 + g).prod() - 1).corr()
    L.append(f"\nCorrélation mensuelle moyenne entre moteurs : {corr.values[np.triu_indices(len(corr), 1)].mean():.2f}.")
    (ICI / "rapports" / "fusion.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
