"""Stratégie « trader macro » (demande du 2026-10-21) — tour 15 : partir de ce qui fait monter/baisser les marchés.

Régime de marché (observable à chaque fin de mois, sans information future) = 3 interrupteurs, 8 régimes :
- TAUX : rendement US 10 ans (^TNX) en hausse sur 6 mois ? (inflation / Fed qui resserre)
- DOLLAR : indice dollar (DX-Y.NYB) en hausse sur 6 mois ?
- RISQUE : SPY au-dessus de sa MM200 ? (appétit pour le risque)
Univers : SPY, QQQ, IWM, EFA, EEM, TLT, IEF, GLD, DBC, UUP (dollar), + BTC dès 36 mois d'historique.
Règles FIXÉES AVANT EXÉCUTION :
- chaque fin de mois, pour le régime du moment, rendement mensuel moyen de chaque actif dans ce même régime,
  calculé sur TOUT le passé disponible (fenêtre croissante, ≥ 60 mois d'historique de régimes) ;
- on achète à parts égales les 3 actifs au meilleur rendement moyen, seulement s'il dépasse celui du Trésor ;
  sinon Trésor. Exécution à la clôture suivante, frais 0,02 % par côté (crypto 0,10 %).
- résultats 2011 → aujourd'hui (tout est hors échantillon par construction), + levier ×1, ×2, ×5 (financement 5 %/an).
- « réussite » = part des positions mensuelles gagnantes ; aussi : part des mois positifs.
Usage : python3 -m labo.macro → rapports/macro.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import donnees
from .haute_reussite import taux_tresor
from .rotation import stats

ICI = Path(__file__).resolve().parent.parent
ACTIFS = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "IEF", "GLD", "DBC", "UUP", "BTC-USD"]


def charger():
    px = {s: donnees.charger_yahoo(s)[0].close for s in ACTIFS + ["^TNX", "DX-Y.NYB"]}
    spy_idx = px["SPY"].index
    c = pd.DataFrame({s: v.reindex(spy_idx, method="ffill") for s, v in px.items()}).loc["2003-01-01":]
    return c


def regimes(c):
    fm = c.groupby([c.index.year, c.index.month]).tail(1).index
    m = c.loc[fm]
    taux = (m["^TNX"] > m["^TNX"].shift(6)).astype(int)
    dollar = (m["DX-Y.NYB"] > m["DX-Y.NYB"].shift(6)).astype(int)
    mm200 = c.SPY.rolling(200).mean().loc[fm]
    risque = (m.SPY > mm200).astype(int)
    reg = (taux * 4 + dollar * 2 + risque).where(m["^TNX"].shift(6).notna() & mm200.notna())
    return fm, reg


NOMS = {0: "taux ↓ dollar ↓ actions ↓", 1: "taux ↓ dollar ↓ actions ↑", 2: "taux ↓ dollar ↑ actions ↓", 3: "taux ↓ dollar ↑ actions ↑",
        4: "taux ↑ dollar ↓ actions ↓", 5: "taux ↑ dollar ↓ actions ↑", 6: "taux ↑ dollar ↑ actions ↓", 7: "taux ↑ dollar ↑ actions ↑"}


def main():
    c = charger()
    tb = taux_tresor(c.index)
    fm, reg = regimes(c)
    ret_m = c[ACTIFS].loc[fm].pct_change(fill_method=None)            # rendement du mois qui se termine à fm[i]
    suiv = ret_m.shift(-1)                                              # rendement du mois suivant (à prédire)
    tb_m = (1 + tb).groupby([tb.index.year, tb.index.month]).prod().values - 1
    tb_m = pd.Series(tb_m, index=fm)
    poids = pd.DataFrame(0.0, index=fm, columns=ACTIFS)
    choix = {}
    for i, d in enumerate(fm):
        if d < pd.Timestamp("2010-12-01") or pd.isna(reg.iloc[i]):
            continue
        passe = [j for j in range(i) if not pd.isna(reg.iloc[j]) and not pd.isna(suiv.iloc[j]).all()]
        if len(passe) < 60:
            continue
        meme = [j for j in passe if reg.iloc[j] == reg.iloc[i]]
        if len(meme) < 6:
            continue
        hist = suiv.iloc[meme]
        moy = hist.mean()
        moy = moy[hist.count() >= 6]                                    # au moins 6 mois observés dans ce régime (BTC)
        seuil = tb_m.iloc[[j for j in meme]].mean()
        top = moy[moy > seuil].sort_values(ascending=False).index[:3]
        for s in top:
            poids.loc[d, s] = 1 / 3
        choix[d] = (int(reg.iloc[i]), list(top))
    W = poids.reindex(c.index).ffill().shift(2).fillna(0.0)
    r = c[ACTIFS].pct_change(fill_method=None).fillna(0.0)
    cout = W.diff().abs().fillna(0.0)
    cout = cout.drop(columns="BTC-USD").sum(axis=1) * 0.0002 + cout["BTC-USD"] * 0.001
    base = (W * r).sum(axis=1) + (1 - W.sum(axis=1)).clip(lower=0) * tb - cout
    base = base.loc["2011-01-01":]
    spy = r.SPY.loc["2011-01-01":]
    # réussite : positions mensuelles gagnantes
    pos = []
    for d, (rg, top) in choix.items():
        i = list(fm).index(d)
        if i + 1 < len(fm):
            for s in top:
                pos.append(suiv.loc[d, s])
    pos = pd.Series(pos).dropna()
    fin = c.index[-1]
    P = {"2011-2015": ("2011-01-01", "2015-12-31"), "2016-2021": ("2016-01-01", "2021-12-31"), "2022-2024": ("2022-01-01", "2024-12-31"),
         "2025 → auj.": ("2025-01-01", "2100-01-01"), "5 ans": (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01"),
         "2011 → auj.": ("2011-01-01", "2100-01-01")}
    T = [f"# Stratégie « trader macro » par régimes (données jusqu'au {fin.date()})\n",
         "Commande : `python3 -m labo.macro` · règles fixées avant exécution : en-tête du fichier. Tout est hors échantillon (apprentissage sur le passé seulement).\n",
         f"**Réussite des positions** : {(pos > 0).mean():.0%} de {len(pos)} positions mensuelles gagnantes (gain moyen {pos[pos > 0].mean():+.1%}, perte moyenne {pos[pos <= 0].mean():+.1%}).\n",
         "| Version | " + " | ".join(P) + " | Mois positifs | Pire mois | 5 000 € sur 5 ans |", "|---|" + "---|" * (len(P) + 3)]
    for nom, L in (("Macro ×1", 1), ("Macro ×2", 2), ("Macro ×5", 5)):
        x = (base * L - (L - 1) * 0.05 / 252).clip(lower=-1)
        s5 = stats(x, *P["5 ans"])
        sa = stats(x, *P["2011 → auj."])
        T.append(f"| {nom} | " + " | ".join(f"{stats(x, *P[p])['rend']:+.1%} / {stats(x, *P[p])['baisse']:.0%}" for p in P)
                 + f" | {sa['mois_pos']:.0%} | {sa['pire_mois']:+.1%} | {5000 * s5['final']:,.0f} € |")
    s5 = stats(spy, *P["5 ans"])
    T.append("| SPY gardé | " + " | ".join(f"{stats(spy, *P[p])['rend']:+.1%} / {stats(spy, *P[p])['baisse']:.0%}" for p in P)
             + f" | {stats(spy, *P['2011 → auj.'])['mois_pos']:.0%} | {stats(spy, *P['2011 → auj.'])['pire_mois']:+.1%} | {5000 * s5['final']:,.0f} € |")
    # ce que le marché a fait dans chaque régime (tout l'historique, pour comprendre)
    T += ["\n## Ce que chaque marché fait selon le régime (rendement mensuel moyen, 2003 → auj.)\n",
          "| Régime | Mois | " + " | ".join(ACTIFS) + " |", "|---|---|" + "---|" * len(ACTIFS)]
    for k in range(8):
        idx = [j for j in range(len(fm)) if reg.iloc[j] == k and not pd.isna(suiv.iloc[j]).all()]
        mo = suiv.iloc[idx].mean()
        T.append(f"| {NOMS[k]} | {len(idx)} | " + " | ".join("—" if pd.isna(mo[s]) else f"{mo[s]:+.1%}" for s in ACTIFS) + " |")
    dern = reg.dropna().iloc[-1]
    T.append(f"\n**Régime actuel ({fm[-1].date()})** : {NOMS[int(dern)]} → positions : {', '.join(choix.get(fm[-1], (0, ['—']))[1]) or 'Trésor'}.")
    (ICI / "rapports" / "macro.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T))


if __name__ == "__main__":
    main()
