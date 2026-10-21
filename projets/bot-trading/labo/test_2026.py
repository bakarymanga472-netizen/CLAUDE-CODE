"""Stratégie D1+F1 (repli RSI-2 < 5 sur 16 ETF, ventes à cours limité) sur l'année 2026 (1er janvier → dernière clôture).

Attention : 2026 fait partie de la période de test 2022+ déjà regardée en bloc ; aucun paramètre n'a été réglé sur 2026.
Usage : python3 -m labo.test_2026 → rapports/test_2026.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .combine import backtest, charger_ohlc, indicateurs
from .combine80 import VARIANTES80

ICI = Path(__file__).resolve().parent.parent
DEBUT = "2026-01-01"


def main():
    c, o_, h_ = charger_ohlc()
    ind = indicateurs(c, o_, h_)
    x = {**VARIANTES80["D1"], "limite": True}
    L = [f"# D1+F1 en 2026 ({DEBUT} → {c.index[-1].date()})\n",
         "Commande : `python3 -m labo.test_2026`. 2026 appartient à la période de test 2022+ déjà regardée en bloc ; "
         "aucun réglage n'a été fait sur 2026.\n"]
    r1, t1 = backtest(c, ind, **x)
    t = t1[t1.entree >= pd.Timestamp(DEBUT)]
    rd1, td1 = backtest(c, ind, **VARIANTES80["D1"])
    td = td1[td1.entree >= pd.Timestamp(DEBUT)]
    L += ["## Trades\n",
          f"- D1+F1 : **{len(t)} trades, {(t.rendement > 0).mean():.0%} gagnants** ({(t.rendement > 0).sum()} gagnants, {(t.rendement <= 0).sum()} perdants), "
          f"gain moyen {t.rendement[t.rendement > 0].mean():+.2%}, perte moyenne {t.rendement[t.rendement <= 0].mean() if (t.rendement <= 0).any() else 0:+.2%}, "
          f"durée médiane {int(t.seances.median())} séance(s).",
          f"- D1 sans F1 (pour comparer) : {len(td)} trades, {(td.rendement > 0).mean():.0%} gagnants.\n",
          "| Levier | Rendement 2026 | Pire baisse 2026 | Mois positifs | Meilleur mois | Pire mois | 10 000 € au 1er janvier → aujourd'hui |", "|---|---|---|---|---|---|---|"]
    for Lv in (1, 3, 5, 7):
        r, _ = backtest(c, ind, levier=float(Lv), **x)
        y = r.loc[DEBUT:]
        cour = (1 + y).cumprod()
        mois = (1 + y).resample("ME").prod() - 1
        L.append(f"| ×{Lv} | {cour.iloc[-1] - 1:+.1%} | {(cour / cour.cummax() - 1).min():.1%} | {(mois > 0).sum()}/{len(mois)} | "
                 f"{mois.max():+.1%} | {mois.min():+.1%} | {10000 * cour.iloc[-1]:,.0f} € |")
    bh = c.loc[DEBUT:].pct_change(fill_method=None).mean(axis=1).fillna(0)
    spy = c.SPY.loc[DEBUT:]
    L += [f"\nRéférences 2026 : les 16 ETF achetés et gardés à parts égales **{(1 + bh).prod() - 1:+.1%}** ; SPY seul **{spy.iloc[-1] / spy.iloc[0] - 1:+.1%}**.\n",
          "## Mois par mois (×1 et ×5)\n", "| Mois | Trades | Gagnants | ×1 | ×5 |", "|---|---|---|---|---|"]
    r5, _ = backtest(c, ind, levier=5.0, **x)
    m1 = (1 + r1.loc[DEBUT:]).resample("ME").prod() - 1
    m5 = (1 + r5.loc[DEBUT:]).resample("ME").prod() - 1
    for d in m1.index:
        tm = t[(t.entree.dt.year == d.year) & (t.entree.dt.month == d.month)]
        L.append(f"| {d.strftime('%Y-%m')} | {len(tm)} | {(tm.rendement > 0).sum()} | {m1[d]:+.2%} | {m5[d]:+.2%} |")
    perd = t[t.rendement <= 0]
    L += ["\n## Trades perdants de 2026\n", "| Actif | Entrée | Sortie | Résultat | Séances | Cause |", "|---|---|---|---|---|---|"]
    for _, x_ in perd.iterrows():
        L.append(f"| {x_.actif} | {x_.entree.date()} | {x_.sortie.date()} | {x_.rendement:+.2%} | {x_.seances} | {x_.motif} |")
    if perd.empty:
        L.append("| — | — | — | aucun | — | — |")
    L += ["\nRappel : rendement à levier ×L = chaque position pèse L × 20 % du capital ; intérêts 5 %/an sur la part empruntée ; "
          "ventes à cours limité simulées avec le plus haut du jour."]
    (ICI / "rapports" / "test_2026.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
