"""Optimisation par les pertes (demande du 2026-10-21) — tour 11.

Autopsie du moteur QQQ ×2 > MM200 (2008 → auj.) : 58 passages, 41 perdants ; 34 perdants durent < 20 séances
(médiane 3 séances) et font -140 % des -180 % de pertes cumulées : ce sont des FAUX SIGNAUX autour de la MM200
(« whipsaw »). Les gagnants durent ~190 séances.
Variantes FIXÉES AVANT EXÉCUTION (remèdes classiques au faux signal) :
- Bb : bande de tolérance — entrée si QQQ > MM200 × (1 + b), sortie si QQQ < MM200 × (1 − b), b ∈ {1 %, 2 %, 3 %} ;
- Nn : confirmation — entrée après n clôtures consécutives > MM200, sortie au 1er passage dessous, n ∈ {3, 5}.
Choix : meilleur Calmar 2008-2015 du moteur QQQ ×2 (référence incluse : sans correctif) ; puis on remplace le moteur
dans la stratégie Équilibrée (75 % C3 + 25 % stable) et on vérifie toutes les périodes.
Usage : python3 -m labo.optim_pertes → rapports/optim_pertes.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .combine import ruine
from .combo3 import melange
from .fusion import fusion_iv, moteurs
from .haute_reussite import taux_tresor
from .rotation import PERIODES, prix, stats
from .strategie_finale import selection

ICI = Path(__file__).resolve().parent.parent


def etat_bande(q, b):
    mm = q.rolling(200).mean()
    out, dedans = np.zeros(len(q)), False
    for i, (p, m) in enumerate(zip(q.values, mm.values)):
        if np.isfinite(m):
            if not dedans and p > m * (1 + b):
                dedans = True
            elif dedans and p < m * (1 - b):
                dedans = False
        out[i] = dedans
    return pd.Series(out, index=q.index)


def etat_confirm(q, n):
    au_dessus = q > q.rolling(200).mean()
    suite = au_dessus.astype(int).groupby((~au_dessus).cumsum()).cumsum()
    out, dedans = np.zeros(len(q)), False
    for i, (a, s) in enumerate(zip(au_dessus.values, suite.values)):
        if not dedans and s >= n:
            dedans = True
        elif dedans and not a:
            dedans = False
        out[i] = dedans
    return pd.Series(out, index=q.index)


def moteur_qqq(etat, q, tb, L=2):
    d = etat.astype(float).shift(2).fillna(0.0)
    r = q.pct_change(fill_method=None).fillna(0.0)
    return d * (L * r - (L - 1) * tb - 0.0095 / 252) + (1 - d) * tb - d.diff().abs().fillna(0.0) * 0.0002 * L


def main():
    c = prix(["QQQ"])
    q, tb = c.QQQ, taux_tresor(c.index)
    V = {"Sans correctif": moteur_qqq(q > q.rolling(200).mean(), q, tb)}
    for b in (0.01, 0.02, 0.03):
        V[f"B{int(b * 100)} bande ±{b:.0%}"] = moteur_qqq(etat_bande(q, b), q, tb)
    for n in (3, 5):
        V[f"N{n} confirmation {n} jours"] = moteur_qqq(etat_confirm(q, n), q, tb)
    A, B = "2008-01-01", "2015-12-31"
    choix = max(V, key=lambda k: stats(V[k], A, B)["calmar"])
    M, spy = moteurs()
    fin = spy.index[-1]
    P = {k: v for k, v in PERIODES.items() if not k.startswith("2001")}
    P["5 ans"] = (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")
    garde, _ = selection(M)
    stable = fusion_iv({k: M[k] for k in garde})

    def equilibree(m3):
        c3 = melange([M["M1 bot haute réussite"], M["M2 rotation top 3"], m3.reindex(spy.index).fillna(0.0)], [1 / 3] * 3)
        return melange([c3, stable], [0.75, 0.25])

    T = [f"# Optimisation par les pertes — moteur QQQ ×2 (données jusqu'au {fin.date()})\n",
         "Commande : `python3 -m labo.optim_pertes` · règles : en-tête du fichier.\n", "## Moteur QQQ ×2 seul (rendement/an / pire baisse)\n",
         "| Variante | " + " | ".join(P) + " | Passages perdants (2008+) |", "|---|" + "---|" * (len(P) + 1)]
    for k, x in V.items():
        d = (x != 0)
        T.append(f"| {k}{' ← choisie' if k == choix else ''} | " + " | ".join(f"{stats(x, *P[p])['rend']:+.1%} / {stats(x, *P[p])['baisse']:.0%}" for p in P) + " | — |")
    T += [f"\n## Stratégie Équilibrée : avant / après (moteur {choix})\n",
          "| Version | " + " | ".join(P) + " | Sharpe 5 ans | 20 000 € (5 ans) | Ruine 5 ans |", "|---|" + "---|" * (len(P) + 3)]
    for nom, m3 in (("Équilibrée actuelle", V["Sans correctif"]), (f"Équilibrée + {choix}", V[choix])):
        x = equilibree(m3).loc["2008":]
        s5 = stats(x, *P["5 ans"])
        T.append(f"| {nom} | " + " | ".join(f"{stats(x, *P[p])['rend']:+.1%} / {stats(x, *P[p])['baisse']:.0%}" for p in P)
                 + f" | {s5['sharpe']:.2f} | {20000 * s5['final']:,.0f} € | {ruine(x):.0%} |")
    s = spy.loc["2008":]
    T.append("| SPY gardé | " + " | ".join(f"{stats(s, *P[p])['rend']:+.1%} / {stats(s, *P[p])['baisse']:.0%}" for p in P)
             + f" | {stats(s, *P['5 ans'])['sharpe']:.2f} | {20000 * stats(s, *P['5 ans'])['final']:,.0f} € | {ruine(s):.0%} |")
    (ICI / "rapports" / "optim_pertes.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T))


if __name__ == "__main__":
    main()
