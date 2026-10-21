"""Bot « haute réussite + gros gains », version retenue (2026-10-21) : 50 % portefeuille de tendance + 50 % D1F1 élargi.

Historique de la recherche (tout est tracé, pour mesurer le risque de surapprentissage) :
- 1er tour (labo/haute_reussite.py, règles fixées avant) : D1F1 sur 40 ETF → 93-97 % de trades gagnants sur toutes
  les périodes, mais ne bat pas le SPY gardé en 2016-2021 ni en 2022-2024, même avec levier.
- 2e tour (déclaré après le 1er) : U40-K10-T ×2 à ×4 → même constat ; le levier n'ajoute pas d'avantage.
- 3e tour (déclaré après le 2e, CE FICHIER) : mélange mensuel 50/50 avec le portefeuille de tendance (règles inchangées
  de labo/portefeuille.py). Poids 50/50 non optimisé. Levier de la jambe D1F1 ∈ {1, 2, 3}, aucun autre réglage.
Critères (frais inclus) : ≥ 85 % de trades gagnants (jambe D1F1, seule à avoir des trades au sens strict),
rendement > SPY gardé, pire baisse > -15 % (quotidienne), ≥ 30 trades — vérifiés sur CHAQUE période, pas seulement 2025+.
Usage : python3 -m labo.mix_tendance → rapports/mix_tendance.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from .haute_reussite import PERIODES, U40, charger, lancer
from .portefeuille import UNIVERS as UT, executer

ICI = Path(__file__).resolve().parent.parent


def stats(jour, a, b):
    x = jour.loc[a:b].dropna()
    v = (1 + x).cumprod()
    ans = max((x.index[-1] - x.index[0]).days / 365.25, 0.1)
    mois = (1 + x).resample("ME").prod() - 1
    return {"rend": v.iloc[-1] ** (1 / ans) - 1, "baisse": (v / v.cummax() - 1).min(),
            "sharpe": mois.mean() / mois.std() * np.sqrt(12), "mois_pos": (mois > 0).mean(), "pire_mois": mois.min()}


def main():
    tend, _ = executer(UT)
    c = charger(["SPY"])[0]
    seances = c.index
    tend = (1 + tend).groupby(tend.index.to_series().apply(lambda d: seances[seances.searchsorted(d)]
                                                            if d <= seances[-1] else pd.NaT)).prod() - 1   # week-ends → séance suivante
    spy = c.SPY.pct_change(fill_method=None).fillna(0.0)
    L = ["# Bot retenu : 50 % tendance + 50 % D1F1 élargi\n",
         f"Commande : `python3 -m labo.mix_tendance` · données jusqu'au {seances[-1].date()} · règles et historique : en-tête du fichier.\n",
         "| Version | Période | Trades D1F1 | Réussite | Rendement/an | Pire baisse (quotidienne) | Sharpe | Mois positifs | Pire mois | Bat le SPY | Objectif |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for Lv in (1, 2, 3):
        _, r, t = lancer(U40, 10, True, levier=float(Lv))
        mix = pd.DataFrame({"t": tend.reindex(r.index).fillna(0.0), "d": r})
        # rééquilibrage 50/50 chaque début de mois : poids qui dérivent dans le mois
        out = []
        for _, g in mix.groupby(mix.index.to_period("M")):
            v = 0.5 * (1 + g).cumprod()
            tot = v.sum(axis=1)
            out.append(tot / tot.shift(1).fillna(1.0) - 1)
        jour = pd.concat(out)
        for p, (a, b) in PERIODES.items():
            m, s = stats(jour, a, b), stats(spy, a, b)
            tt = t[(t.entree >= pd.Timestamp(a)) & (t.entree <= pd.Timestamp(b))]
            ok = [(tt.rendement > 0).mean() >= 0.85, m["rend"] > s["rend"], m["baisse"] > -0.15, len(tt) >= 30]
            L.append(f"| D1F1 ×{Lv} | {p} | {len(tt)} | {(tt.rendement > 0).mean():.0%} | {m['rend']:+.1%} | {m['baisse']:.0%} | {m['sharpe']:.2f} | "
                     f"{m['mois_pos']:.0%} | {m['pire_mois']:+.1%} | {'oui' if ok[1] else '**non**'} | {'**ATTEINT**' if all(ok) else 'non'} |")
    for p, (a, b) in PERIODES.items():
        s = stats(spy, a, b)
        L.append(f"| SPY gardé | {p} | — | — | {s['rend']:+.1%} | {s['baisse']:.0%} | {s['sharpe']:.2f} | {s['mois_pos']:.0%} | {s['pire_mois']:+.1%} | — | — |")
    L.append("\nJambe tendance : 9 instruments dont 6 cryptos (entrées après 400 jours d'historique), long seul, vol cible 20 %. "
             "Jambe D1F1 : 40 ETF, 10 positions, cash au taux du Trésor. Rééquilibrage 50/50 mensuel, sans frais de rééquilibrage.")
    (ICI / "rapports" / "mix_tendance.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
