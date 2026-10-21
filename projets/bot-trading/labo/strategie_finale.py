"""Stratégie finale (demande du 2026-10-21) : « meilleurs rendements tout en minimisant les pertes » — tour 10.

Règles FIXÉES AVANT EXÉCUTION, toutes les décisions sur 2008-2015 uniquement (2016 → aujourd'hui = vérification) :
1. Sélection : moteurs de labo/fusion.py au Sharpe ≥ 0,5 sur 2008-2015 ; si deux moteurs ont une corrélation
   mensuelle > 0,6 sur 2008-2015, on garde celui au meilleur Sharpe (pas de double emploi).
2. Pondération, deux variantes : parts égales (EG) ou 1/volatilité des 252 séances précédentes (IV) ; rééquilibrage mensuel.
   Référence : C3 (tour 8).
3. Choix : meilleur rapport rendement / pire baisse (Calmar) sur 2008-2015 parmi EG, IV, C3.
4. Taille : levier constant L tel que la pire baisse 2008-2015 = -20 % (plafond ×2), financement 5 %/an sur la part
   empruntée. Ce levier est figé et appliqué tel quel ensuite.
Usage : python3 -m labo.strategie_finale → rapports/strategie_finale.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .combine import ruine
from .combo3 import melange
from .fusion import fusion_iv, moteurs
from .rotation import PERIODES, stats

ICI = Path(__file__).resolve().parent.parent
A, B = "2008-01-01", "2015-12-31"


def selection(M):
    df = pd.DataFrame(M).loc[A:B]
    sh = {k: stats(df[k], A, B)["sharpe"] for k in df}
    cand = sorted([k for k in sh if sh[k] >= 0.5], key=lambda k: -sh[k])
    corr = df.resample("ME").apply(lambda g: (1 + g).prod() - 1).corr()
    garde = []
    for k in cand:
        if all(corr.loc[k, g] <= 0.6 for g in garde):
            garde.append(k)
    return garde, sh


def levier_pour(x, cible=-0.20, plafond=2.0):
    for L in np.arange(1.0, plafond + 0.001, 0.05):
        if stats(x * L - (L - 1) * 0.05 / 252, A, B)["baisse"] < cible:
            return max(round(L - 0.05, 2), 1.0)
    return plafond


def main():
    M, spy = moteurs()
    garde, sh = selection(M)
    V = {"EG": melange([M[k] for k in garde], [1 / len(garde)] * len(garde)),
         "IV": fusion_iv({k: M[k] for k in garde}),
         "C3": melange([M["M1 bot haute réussite"], M["M2 rotation top 3"], M["M3 QQQ ×2 > MM200"]], [1 / 3] * 3)}
    choix = max(V, key=lambda n: stats(V[n], A, B)["calmar"])
    L = levier_pour(V[choix])
    finale = V[choix] * L - (L - 1) * 0.05 / 252
    fin = spy.index[-1]
    P = {k: v for k, v in PERIODES.items() if not k.startswith("2001")}
    P["5 ans"] = (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")
    lignes = {f"FINALE = {choix} ×{L:g}": finale, **{f"{n} ×1": x for n, x in V.items()}, "SPY gardé": spy}
    T = [f"# Stratégie finale (données jusqu'au {fin.date()})\n", "Commande : `python3 -m labo.strategie_finale` · règles : en-tête du fichier.\n",
         "Moteurs retenus (Sharpe 2008-2015) : " + ", ".join(f"{k} ({sh[k]:.2f})" for k in garde) + ".\n",
         f"Pondération choisie (Calmar 2008-2015) : **{choix}** ; levier figé pour -20 % de pire baisse en 2008-2015 : **×{L:g}**.\n",
         "Chaque case : rendement/an / pire baisse.\n",
         "| Stratégie | " + " | ".join(P) + " | Sharpe 5 ans | Pire mois 5 ans | 20 000 € (5 ans) | Ruine 5 ans |", "|---|" + "---|" * (len(P) + 4)]
    for n, x in lignes.items():
        x = x.loc[A:]
        s5 = stats(x, *P["5 ans"])
        T.append(f"| {n} | " + " | ".join(f"{stats(x, *P[k])['rend']:+.1%} / {stats(x, *P[k])['baisse']:.0%}" for k in P)
                 + f" | {s5['sharpe']:.2f} | {s5['pire_mois']:+.1%} | {20000 * s5['final']:,.0f} € | {ruine(x):.0%} |")
    x = finale.loc[A:]
    an = (1 + x).resample("YE").prod() - 1
    T += ["\n## Année par année (stratégie finale vs SPY)\n", "| Année | Finale | SPY |", "|---|---|---|"]
    sa = (1 + spy.loc[A:]).resample("YE").prod() - 1
    for d in an.index:
        T.append(f"| {d.year} | {an[d]:+.1%} | {sa[d]:+.1%} |")
    (ICI / "rapports" / "strategie_finale.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T))


if __name__ == "__main__":
    main()
