"""Teste le bot multi-agents sur l'historique réel et écrit resultats/rapport.md.

Usage : python3 tester.py [--rafraichir]
"""
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from bot import agents, data
from bot.backtest import achat_conserve, executer, metriques

ICI = Path(__file__).resolve().parent
PERIODES = {
    "complète (2020-08 → aujourd'hui)": ("2020-08-01", None),
    "2020-08 → 2023-12": ("2020-08-01", "2023-12-31"),
    "2024-01 → aujourd'hui": ("2024-01-01", None),
}
N_ALEATOIRES = 300


def pct(x):
    return f"{x * 100:+.1f} %" if pd.notna(x) else "—"


def ligne(nom, m):
    return (f"| {nom} | {pct(m['rendement_total'])} | {pct(m['cagr'])} | {pct(m['drawdown_max'])} | "
            f"{m['sharpe']:.2f} | {m.get('trades', '—')} | "
            f"{(f'{m['taux_reussite'] * 100:.0f} %' if 'taux_reussite' in m else '—')} | "
            f"{(f'{m['profit_factor']:.2f}' if 'profit_factor' in m else '—')} |")


def main():
    rafraichir = "--rafraichir" in sys.argv
    marches, fng = data.tout_charger(rafraichir)
    marches = {s: agents.indicateurs(d) for s, d in marches.items()}
    fin_donnees = marches["BTCUSDT"].index[-1].date()

    base = agents.Config()
    variantes = [base,
                 replace(base, nom="sans agent sentiment", agent_sentiment=False),
                 replace(base, nom="sans agent flux", agent_flux=False),
                 replace(base, nom="sans agent setups", agent_setups=False),
                 replace(base, nom="sans agent risque", agent_risque=False)]

    out = [f"# Résultats du bot multi-agents\n",
           f"Données Binance journalières jusqu'au {fin_donnees}. Capital fictif 10 000 USDT. "
           f"Frais 0,1 % + glissement 0,05 % par ordre. Décision à la clôture, exécution à l'ouverture du lendemain.\n",
           "Paramètres fixés à l'avance, **aucune optimisation** sur ces données.\n"]
    tete = "| Stratégie | Rendement | Par an | Pire baisse | Sharpe | Trades | Gagnants | Profit factor |\n|---|---|---|---|---|---|---|---|"
    resume = {}

    for titre, (debut, fin) in PERIODES.items():
        out += [f"\n## Période {titre}\n", tete]
        courbe, trades = executer(marches, fng, base, debut, fin)
        m = metriques(courbe, trades)
        resume[titre] = {"bot": m}
        out.append(ligne("**Bot complet (5 agents)**", m))
        for v in variantes[1:]:
            c, tr = executer(marches, fng, v, debut, fin)
            out.append(ligne(v.nom, metriques(c, tr)))
        btc = metriques(achat_conserve(marches, ["BTCUSDT"], debut, fin))
        panier = metriques(achat_conserve(marches, data.UNIVERS, debut, fin))
        resume[titre].update({"btc": btc, "panier": panier})
        out.append(ligne("Acheter et garder BTC", btc))
        out.append(ligne("Acheter et garder le panier", panier))

        # Référence hasard : mêmes règles de taille et de stop, entrées au hasard, durées tirées des vrais trades
        jours_actifs = max(len(courbe), 1)
        cfg_h = replace(base, nom="hasard", aleatoire=True,
                        proba_aleatoire=min(1.0, 3 * max(len(trades), 1) / (jours_actifs * base.top_scanner)),
                        durees_aleatoires=list(trades.jours.clip(lower=1)) or [20])
        rends, dds = [], []
        for g in range(N_ALEATOIRES):
            c, _ = executer(marches, fng, cfg_h, debut, fin, graine=g)
            mh = metriques(c)
            rends.append(mh["rendement_total"])
            dds.append(mh["drawdown_max"])
        rends = np.array(rends)
        rang = (rends < m["rendement_total"]).mean()
        resume[titre]["rang_hasard"] = rang
        out.append(f"| {N_ALEATOIRES} bots au hasard (médiane) | {pct(np.median(rends))} | — | {pct(np.median(dds))} | — | — | — | — |")
        out.append(f"\nLe bot fait mieux que **{rang * 100:.0f} %** des {N_ALEATOIRES} bots qui achètent au hasard "
                   f"(même gestion du risque, même nombre de trades environ).")
        if titre.startswith("complète"):
            courbe.to_csv(ICI / "resultats" / "courbe_bot.csv")
            trades.to_csv(ICI / "resultats" / "trades.csv", index=False)

    (ICI / "resultats").mkdir(exist_ok=True)
    (ICI / "resultats" / "rapport.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
