"""Teste le système 7 agents sur l'or (COMEX) et écrit resultats/rapport_or.md.

Usage : python3 tester_or.py [--rafraichir]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from bot import or_systeme as osy
from bot.backtest import metriques

ICI = Path(__file__).resolve().parent
AGENTS = ["sentinelle", "bouclier", "vortex", "phantom", "atlas"]
PERIODES = {
    "2008 → 2015 (or en hausse puis krach 2013)": ("2008-01-01", "2015-12-31"),
    "2016 → 2023": ("2016-01-01", "2023-12-31"),
    "2024 → aujourd'hui": ("2024-01-01", None),
    "complète 2008 → aujourd'hui": ("2008-01-01", None),
}
N_HASARD = 300


def pct(x):
    return f"{x * 100:+.1f} %" if pd.notna(x) else "—"


def morceau(courbe, trades, debut, fin):
    c = courbe.loc[debut:fin]
    c = c / c.iloc[0]
    t = trades[(trades.entree >= pd.Timestamp(debut)) & ((fin is None) | (trades.entree <= pd.Timestamp(fin or "2100")))] if len(trades) else trades
    return c, t


def ligne(nom, c, t):
    m = metriques(c)
    n = len(t)
    reussite = f"{(t.rendement > 0).mean() * 100:.0f} %" if n else "—"
    expo = "—"
    return (f"| {nom} | {pct(m['rendement_total'])} | {pct(m['cagr'])} | {pct(m['drawdown_max'])} | "
            f"{m['sharpe']:.2f} | {n} | {reussite} |"), m


def hasard(px, trades, graine):
    """Entrées au hasard, même nombre de trades et mêmes durées que le vrai système."""
    rng = np.random.default_rng(graine)
    n = len(px)
    p = len(trades) / max(n, 1) * 1.6
    durees = list(trades.jours.clip(lower=1)) if len(trades) else [20]
    entree = pd.Series(rng.random(n) < p, index=px.index)
    sortie = pd.Series(False, index=px.index)
    # sortie forcée après une durée tirée au hasard : on la simule via une file de dates
    fin_prevue = None
    for i, t in enumerate(px.index):
        if fin_prevue is not None and t >= fin_prevue:
            sortie.iloc[i] = True
            fin_prevue = None
        if entree.iloc[i] and fin_prevue is None:
            fin_prevue = t + pd.Timedelta(days=int(rng.choice(durees)))
    return osy.kronos(px, entree, sortie, stop_atr=3.0)[0]


def main():
    r = "--rafraichir" in sys.argv
    px = osy.prix_or(r)
    avis = osy.avis_agents(px, r)
    out = ["# Système 7 agents sur l'or — résultats\n",
           f"Or : future COMEX continu (Yahoo GC=F) jusqu'au {px.index[-1].date()}. Frais 0,05 % par ordre. "
           "Long ou cash, sans levier. Décision à la clôture, exécution à l'ouverture suivante. "
           "Paramètres fixés à l'avance, aucune optimisation.\n",
           "Agents : Sentinelle (taux réels), Bouclier (risque géopolitique), Vortex (tendance), "
           "Phantom (positions des fonds COMEX, CFTC), Atlas (dollar), Oracle (probabilité apprise sur le passé), "
           "Kronos (exécution, stop 3 ATR, journal).\n"]

    variantes = {"**Oracle, 5 agents**": (AGENTS, "oracle"),
                 "Consensus fort (« quand ils sont d'accord »)": (AGENTS, "consensus")}
    for a in AGENTS:
        variantes[f"Oracle sans {a}"] = ([x for x in AGENTS if x != a], "oracle")
    resultats = {nom: osy.strategie(px, avis, ag, regle) for nom, (ag, regle) in variantes.items()}
    principal_c, principal_t = resultats["**Oracle, 5 agents**"]
    hasards = [hasard(px, principal_t, g) for g in range(N_HASARD)]

    for titre, (debut, fin) in PERIODES.items():
        out += [f"\n## {titre}\n",
                "| Stratégie | Rendement | Par an | Pire baisse | Sharpe | Trades | Gagnants |",
                "|---|---|---|---|---|---|---|"]
        for nom, (c, t) in resultats.items():
            cc, tt = morceau(c, t, debut, fin)
            l, m = ligne(nom, cc, tt)
            out.append(l)
            if nom.startswith("**Oracle"):
                m_principal = m
        bh = px["close"].loc[debut:fin]
        l, m_bh = ligne("Acheter et garder l'or", bh / bh.iloc[0], pd.DataFrame())
        out.append(l)
        rends = np.array([metriques((h.loc[debut:fin] / h.loc[debut:fin].iloc[0]))["rendement_total"] for h in hasards])
        out.append(f"| {N_HASARD} bots au hasard (médiane) | {pct(np.median(rends))} | — | — | — | — | — |")
        rang = (rends < m_principal["rendement_total"]).mean()
        out.append(f"\nOracle 5 agents fait mieux que **{rang * 100:.0f} %** des bots au hasard.")

    # Avis du jour
    score, proba, base = osy.oracle(avis, px, AGENTS)
    t = px.index[-1]
    out += ["\n## Avis des agents à la dernière clôture\n",
            f"Date {t.date()} — or {px['close'].iloc[-1]:.1f} USD",
            "| " + " | ".join(AGENTS) + " | Score | Proba hausse 20 j | Base |",
            "|" + "---|" * (len(AGENTS) + 3),
            "| " + " | ".join(f"{int(avis.loc[t, a]):+d}" for a in AGENTS)
            + f" | {int(score.iloc[-1]):+d} | {proba.iloc[-1] * 100:.0f} % | {base.iloc[-1] * 100:.0f} % |"]

    (ICI / "resultats").mkdir(exist_ok=True)
    principal_t.to_csv(ICI / "resultats" / "journal_or_kronos.csv", index=False)
    (ICI / "resultats" / "rapport_or.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
