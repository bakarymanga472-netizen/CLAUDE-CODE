"""Aladdin — viser 70 % : optimiser la SORTIE de la structure Rebond (actions + or).

L'enquête a montré que les perdants sont indiscernables à l'entrée : la marge de progrès est dans la sortie.
Choix sur 2008-2019, validation 2020-2024 (doit tenir ≥ 70 % et rester rentable), vérification 2025+.
Usage : python3 -m aladdin.sorties
"""
import itertools
from pathlib import Path

import numpy as np

from . import donnees
from .enquete import executer, note, periode, APPRENTISSAGE, VALIDATION, VERIF

ICI = Path(__file__).resolve().parent.parent


def main():
    px = donnees.prix()
    res = []
    for seuil, tp, sl, duree in itertools.product((5, 10, 15), (0.01, 0.015, 0.02, 0.03, 0.04),
                                                  (0.04, 0.06, 0.08, 0.10), (5, 10, 20)):
        st = {"actifs": ["ACTIONS", "OR"],
              "regle": {"entree": "rsi2", "seuil": seuil, "mm5": False, "tp": tp, "sl": sl, "duree": duree}}
        t = executer(px, st)
        res.append((seuil, tp, sl, duree, note(periode(t, APPRENTISSAGE)), note(periode(t, VALIDATION)), note(periode(t, VERIF))))
    # Choix sur l'apprentissage seulement : réussite max, avec profit factor ≥ 1,3 et ≥ 80 trades
    ok = [r for r in res if r[4]["pf"] >= 1.3 and r[4]["n"] >= 80 and r[4]["somme"] > 0]
    ok.sort(key=lambda r: (-round(r[4]["reussite"], 2), -r[4]["somme"]))
    out = ["# Aladdin — règles de sortie pour viser 70 %\n",
           f"{len(res)} réglages testés. Choix sur 2008-2019 : réussite maximale avec profit factor ≥ 1,3 et ≥ 80 trades.\n",
           "| # | Entrée | Objectif | Stop | Durée max | Réussite 2008-19 | PF 2008-19 | **Réussite 2020-24** | PF 2020-24 | **Réussite 2025+** | PF 2025+ | Rendement cumulé 2025+ | Trades 2025+ |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (s, tp, sl, d, a, v, w) in enumerate(ok[:12], 1):
        out.append(f"| {i} | RSI2<{s} | +{tp * 100:.1f} % | -{sl * 100:.0f} % | {d} j | {a['reussite'] * 100:.0f} % | {a['pf']:.2f} | "
                   f"**{v['reussite'] * 100:.0f} %** | {v['pf']:.2f} | **{w['reussite'] * 100:.0f} %** | {w['pf']:.2f} | {w['somme'] * 100:+.0f} % | {w['n']} |")
    choix = next((r for r in ok if r[5]["reussite"] >= 0.70 and r[5]["pf"] >= 1.2), None)
    if choix:
        s, tp, sl, d, a, v, w = choix
        out += [f"\n## Retenu : premier réglage du classement qui tient ≥ 70 % ET reste rentable en validation 2020-2024\n",
                f"**RSI2<{s}, objectif +{tp * 100:.1f} %, stop -{sl * 100:.0f} %, {d} jours max**\n",
                "| Période | Trades | Réussite | Profit factor | Rendement cumulé des trades |", "|---|---|---|---|---|"]
        for nom, n in (("2008-2019 (choix)", a), ("2020-2024 (validation)", v), ("2025 → aujourd'hui (vérification)", w)):
            out.append(f"| {nom} | {n['n']} | {n['reussite'] * 100:.0f} % | {n['pf']:.2f} | {n['somme'] * 100:+.0f} % |")
        (ICI / "resultats" / "aladdin_sortie_retenue.txt").write_text(f"{s},{tp},{sl},{d}\n")
    else:
        out.append("\nAucun réglage ne tient 70 % en validation tout en restant rentable.")
    (ICI / "resultats" / "aladdin_sorties.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
