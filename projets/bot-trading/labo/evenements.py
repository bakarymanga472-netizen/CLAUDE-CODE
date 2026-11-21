"""Événements PROGRAMMÉS et trades perdants (demande du 2026-10-21) — tour 6, déclaré après les tours 1-5.

Idée : une nouvelle trouvée après coup n'aide pas à trader ; un rendez-vous publié à l'avance, si. Les décisions de la
Fed (FOMC) sont fixées des mois avant (calendrier officiel federalreserve.gov, réunions non programmées exclues ;
labo/fomc_dates.json, 150 décisions 2008-2026).
Variantes FIXÉES AVANT EXÉCUTION (jambe D1F1 : U40-K10-T ×2) :
- REF : sans filtre ;
- Fk : aucune entrée si une décision FOMC tombe dans les k prochaines séances, k ∈ {3, 5, 10}.
Règle de choix : meilleur Sharpe 2008-2015 parmi Fk à ≥ 85 % de trades gagnants ; retenu seulement s'il bat REF en
Sharpe sur 2008-2015. Autres périodes et 5 ans : contrôle.
Usage : python3 -m labo.evenements → rapports/evenements.md
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .actualite import lancer
from .combine import indicateurs, mesures
from .haute_reussite import PERIODES, U40, charger

ICI = Path(__file__).resolve().parent.parent
FOMC = pd.to_datetime(json.loads((Path(__file__).parent / "fomc_dates.json").read_text()))


def seances_avant_fomc(index):
    """Pour chaque séance : nombre de séances jusqu'à la prochaine décision FOMC (0 = le jour même)."""
    pos = np.searchsorted(index.values, FOMC.values)          # indice de la séance de chaque décision
    pos = pos[pos < len(index)]
    prochain = np.full(len(index), 10 ** 6)
    j = 0
    for i in range(len(index)):
        while j < len(pos) and pos[j] < i:
            j += 1
        if j < len(pos):
            prochain[i] = pos[j] - i
    return prochain


def main():
    c, o, h = charger(U40)
    ind = indicateurs(c, o, h)
    fin = c.index[-1]
    per = {**PERIODES, "5 ans": (str((fin - pd.DateOffset(years=5)).date()), "2100-01-01")}
    dist = seances_avant_fomc(c.index)
    base = (ind["rsi"].values < 5) & (c.values > ind["mm200"].values)
    res = {"REF": lancer(c, ind)}
    for k in (3, 5, 10):
        res[f"F{k}"] = lancer(c, ind, panique=None) if False else None
        sig = base & ~(dist <= k)[:, None]
        from . import combine
        combine.K = 10
        try:
            r, t = combine.backtest(c, ind, levier=2.0, signal=sig, sortie="C", seuil=5, tp=0.01, stop=0.10, duree=20, limite=True)
        finally:
            combine.K = 5
        from .haute_reussite import exposition, taux_tresor
        r = r + (1.0 - exposition(t, c.index, 0.2)).clip(lower=0.0) * taux_tresor(c.index)
        res[f"F{k}"] = (r, t)
    # autopsie : une décision FOMC tombe-t-elle PENDANT le trade ?
    idx = {d: i for i, d in enumerate(c.index)}
    t0 = res["REF"][1].copy()
    t0["fomc_pendant"] = [bool(((FOMC > a) & (FOMC <= b)).any()) for a, b in zip(t0.entree, t0.sortie)]
    t0["fomc_proche"] = [dist[idx[a]] <= 10 for a in t0.entree]
    m = {n: {p: mesures(r, t, a, b) for p, (a, b) in per.items()} for n, (r, t) in res.items()}
    ok = [n for n in res if n != "REF" and (m[n]["2008-2015 (choix)"]["reussite"] or 0) >= 0.85]
    best = max(ok, key=lambda n: m[n]["2008-2015 (choix)"]["sharpe"]) if ok else None
    retenu = best if best and m[best]["2008-2015 (choix)"]["sharpe"] > m["REF"]["2008-2015 (choix)"]["sharpe"] else "REF"
    L = [f"# Décisions de la Fed (programmées) et trades perdants — données jusqu'au {fin.date()}\n",
         "Commande : `python3 -m labo.evenements` · règles fixées avant exécution : en-tête du fichier.\n", "## Autopsie (REF, 2008 → aujourd'hui)\n"]
    for nom, col in (("décision FOMC pendant le trade", "fomc_pendant"), ("décision FOMC dans les 10 séances suivant l'entrée", "fomc_proche")):
        L.append(f"- {nom} : perdants {t0[t0.rendement <= 0][col].mean():.0%}, gagnants {t0[t0.rendement > 0][col].mean():.0%} ; "
                 f"réussite avec {t0[t0[col]].rendement.gt(0).mean():.1%}, sans {t0[~t0[col]].rendement.gt(0).mean():.1%}.")
    L += ["\n## Filtres testés\n", "| Variante | Période | Trades | Réussite | Perte moyenne | Rendement/an | Pire baisse | Sharpe |", "|---|---|---|---|---|---|---|---|"]
    for n, d in m.items():
        for p, x in d.items():
            L.append(f"| {n}{' ← retenue' if n == retenu else ''} | {p} | {x['trades']} | {x['reussite']:.1%} | {x['perte_moyenne']:+.2%} | "
                     f"{x['rendement_annuel']:+.1%} | {x['pire_baisse']:.0%} | {x['sharpe']:.2f} |")
    L.append(f"\nVariante retenue par la règle : **{retenu}**.")
    (ICI / "rapports" / "evenements.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
