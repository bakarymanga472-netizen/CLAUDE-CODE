"""Filtre « actualité » pour D1F1 (demande du 2026-10-21) — tour 5, déclaré après les tours 1-4.

Autopsie des 38 trades perdants des 5 dernières années (U40-K10-T ×2) : ils ne se distinguent PAS à l'entrée
(VIX/VIX3M > 1 à l'entrée : 8 % des perdants, 6 % des gagnants) mais un choc d'actualité survient PENDANT le trade
(VIX/VIX3M > 1 pendant : 74 % des perdants, 14 % des gagnants). Grappes vérifiées dans la presse : Fed 18/12/2024,
droits de douane avril 2025, guerre Iran mars 2026, 2022 (Ukraine, hausses de taux).
Mesure du choc, sans archive de presse : la courbe du VIX s'inverse (VIX 1 mois > VIX 3 mois) — les opérateurs
paient plus cher la protection immédiate que celle à 3 mois, signature d'une mauvaise nouvelle en cours.

Variantes FIXÉES AVANT EXÉCUTION :
- REF : U40-K10-T ×2 sans filtre (jambe D1F1 du bot actuel) ;
- E1 : choc (VIX/VIX3M > 1 à la clôture) → aucune entrée ET vente de toutes les positions à la clôture suivante ;
- E2 : choc → aucune entrée seulement ;
- E3 : choc = VIX/VIX3M > 1 OU VIX +25 % en une séance → aucune entrée ET vente de tout.
Règle de choix : meilleur Sharpe 2008-2015 parmi E1-E3 ayant ≥ 85 % de trades gagnants sur 2008-2015 ;
retenu seulement s'il bat REF en Sharpe sur 2008-2015. Autres périodes et 5 ans : contrôle.
Usage : python3 -m labo.actualite → rapports/actualite.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import combine, donnees
from .combine import indicateurs, mesures
from .haute_reussite import PERIODES, U40, charger, exposition, taux_tresor

ICI = Path(__file__).resolve().parent.parent
D1F1 = {"sortie": "C", "seuil": 5, "tp": 0.01, "stop": 0.10, "duree": 20, "limite": True}


def chocs(index):
    vix = donnees.charger_yahoo("^VIX")[0].close.reindex(index).ffill()
    v3 = donnees.charger_yahoo("^VIX3M")[0].close.reindex(index).ffill()
    inv = (vix / v3 > 1).fillna(False)
    saut = (vix.pct_change(fill_method=None) > 0.25).fillna(False)
    return {"E1": (inv.values, True), "E2": (inv.values, False), "E3": ((inv | saut).values, True)}


def lancer(c, ind, levier=2.0, panique=None, sortie=True):
    combine.K = 10
    try:
        r, t = combine.backtest(c, ind, levier=levier, panique=panique, panique_sortie=sortie, **D1F1)
    finally:
        combine.K = 5
    libre = (1.0 - exposition(t, c.index, levier / 10)).clip(lower=0.0)
    return r + libre * taux_tresor(c.index), t


def main():
    c, o, h = charger(U40)
    ind = indicateurs(c, o, h)
    ch = chocs(c.index)
    fin = c.index[-1]
    per = {**PERIODES, "5 ans": (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")}
    res = {"REF": lancer(c, ind)}
    for n, (p, s) in ch.items():
        res[n] = lancer(c, ind, panique=p, sortie=s)
    m = {n: {p: mesures(r, t, a, b) for p, (a, b) in per.items()} for n, (r, t) in res.items()}
    ok = [n for n in ch if (m[n]["2008-2015 (choix)"]["reussite"] or 0) >= 0.85]
    best = max(ok, key=lambda n: m[n]["2008-2015 (choix)"]["sharpe"]) if ok else None
    retenu = best if best and m[best]["2008-2015 (choix)"]["sharpe"] > m["REF"]["2008-2015 (choix)"]["sharpe"] else "REF"
    L = [f"# Filtre actualité (courbe du VIX) — données jusqu'au {fin.date()}\n",
         "Commande : `python3 -m labo.actualite` · règles fixées avant exécution : en-tête du fichier.\n",
         "| Variante | Période | Trades | Réussite | Gain moyen | Perte moyenne | Rendement/an | Pire baisse | Sharpe | Pire mois |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for n, d in m.items():
        for p, x in d.items():
            L.append(f"| {n}{' ← retenue' if n == retenu else ''} | {p} | {x['trades']} | {x['reussite']:.0%} | {x['gain_moyen']:+.2%} | "
                     f"{x['perte_moyenne']:+.2%} | {x['rendement_annuel']:+.1%} | {x['pire_baisse']:.0%} | {x['sharpe']:.2f} | {x['pire_mois']:+.1%} |")
    t5 = {n: t[t.entree > pd.Timestamp(per['5 ans'][0])] for n, (_, t) in res.items()}
    L.append("\n**Perdants sur 5 ans par cause** : " + " ; ".join(
        f"{n} : {len(t[t.rendement <= 0])} ({t[t.rendement <= 0].motif.value_counts().to_dict()})" for n, t in t5.items()))
    L.append(f"\nVariante retenue par la règle : **{retenu}**.")
    (ICI / "rapports" / "actualite.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return retenu, res


if __name__ == "__main__":
    main()
