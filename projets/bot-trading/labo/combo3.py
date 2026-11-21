"""Bot C3 (2026-10-21, tour 8, déclaré après le tour 7) : trois moteurs qui ne perdent pas en même temps, à parts égales.
- ⅓ bot « haute réussite » : 50 % portefeuille de tendance + 50 % D1F1 élargi ×2 (achat des replis) ;
- ⅓ R2 rotation : 3 ETF les plus forts sur 12 mois au-dessus de leur MM200 (labo/rotation.py) ;
- ⅓ R3 : QQQ ×2 quand QQQ > MM200, sinon Trésor (labo/rotation.py).
Rééquilibrage mensuel, poids égaux NON optimisés. Curseur de levier global sur marge (5 %/an sur la part empruntée).
Usage : python3 -m labo.combo3 → rapports/combo3.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .combine import ruine
from .haute_reussite import U40, charger, lancer, taux_tresor
from .portefeuille import UNIVERS as UT, executer
from .rotation import PERIODES, prix, r2, r3, stats

ICI = Path(__file__).resolve().parent.parent


def melange(cols, w):
    m = pd.concat(cols, axis=1).fillna(0.0)
    out = []
    for _, g in m.groupby(m.index.to_period("M")):
        v = (1 + g).cumprod() * w
        tot = v.sum(axis=1)
        out.append(tot / tot.shift(1).fillna(1.0) - 1)
    return pd.concat(out)


def series():
    c40, _, _ = charger(U40)
    s = c40.index
    tend, _ = executer(UT)
    tend = (1 + tend).groupby(tend.index.to_series().apply(lambda d: s[s.searchsorted(d)] if d <= s[-1] else pd.NaT)).prod() - 1
    _, rd, _ = lancer(U40, 10, True, levier=2.0)
    bot = melange([tend.reindex(rd.index).fillna(0.0), rd], [0.5, 0.5])
    c = prix(sorted(set(U40 + ["QQQ", "IEF", "EFA", "SPY"])))
    tb = taux_tresor(c.index)
    R2, R3 = r2(c, tb).reindex(bot.index).fillna(0.0), r3(c, tb, 2).reindex(bot.index).fillna(0.0)
    spy = c.SPY.pct_change(fill_method=None).reindex(bot.index).fillna(0.0)
    return bot, R2, R3, spy


def main():
    bot, R2, R3, spy = series()
    c3 = melange([bot, R2, R3], [1 / 3] * 3)
    V = {"Bot actuel ×1,5 (réf.)": bot * 1.5 - 0.5 * 0.05 / 252}
    for L in (1.0, 1.25, 1.5):
        V[f"C3 ×{L:g}"] = c3 * L - (L - 1) * 0.05 / 252
    V["SPY gardé"] = spy
    fin = bot.index[-1]
    P = {k: v for k, v in PERIODES.items() if not k.startswith("2001")}
    P["5 ans"] = (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")
    L_ = [f"# Bot C3 — trois moteurs (données jusqu'au {fin.date()})\n", "Commande : `python3 -m labo.combo3` · règles : en-tête du fichier.\n",
          "Chaque case : rendement/an / pire baisse.\n", "| Stratégie | " + " | ".join(P) + " | Sharpe 5 ans | 20 000 € (5 ans) | Ruine 5 ans |",
          "|---|" + "---|" * (len(P) + 3)]
    for n, x in V.items():
        L_.append(f"| {n} | " + " | ".join(f"{stats(x, *P[k])['rend']:+.1%} / {stats(x, *P[k])['baisse']:.0%}" for k in P)
                  + f" | {stats(x, *P['5 ans'])['sharpe']:.2f} | {20000 * stats(x, *P['5 ans'])['final']:,.0f} € | {ruine(x.loc['2008':]):.0%} |")
    (ICI / "rapports" / "combo3.md").write_text("\n".join(L_) + "\n", encoding="utf-8")
    print("\n".join(L_))


if __name__ == "__main__":
    main()
