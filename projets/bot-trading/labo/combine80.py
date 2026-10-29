"""Combinaison de A5 et B10, objectif ≥ 80 % de réussite (demande du 2026-10-21).

Ce qui est combiné :
- l'ENTRÉE de B10 (RSI-2 < 10 au-dessus de la MM200), la seule qui bat le hasard ;
- une SORTIE hybride A+B : vendre dès que l'objectif est atteint (variante A) OU dès que le cours repasse au-dessus de
  la MM5 (variante B) mais SEULEMENT si le trade est en gain ; stop -10 % ; 20 séances maximum.
Variantes FIXÉES AVANT EXÉCUTION (2026-10-21) — 4 seulement, pour limiter le surapprentissage :
  objectif ∈ {+1 %, +0,5 %} × filtre de tendance forte (MM50 > MM200) ∈ {non, oui}.
Règle de choix fixée avant : parmi les variantes à ≥ 80 % de réussite sur 2000-2015, la meilleure en Sharpe 2000-2015 ;
si aucune n'atteint 80 %, on le dit et on montre la plus proche. Contrôle 2016-2021, test 2022 → aujourd'hui.
Références : A5, B10, entrées au hasard avec les MÊMES sorties (50 tirages), curseur de levier ×1 à ×3.
2e TOUR (déclaré après avoir vu le 1er, qui plafonne à 72-75 %) — plus exposé au surapprentissage, signalé comme tel :
  D1 : entrée de A5 (RSI-2 < 5) + sortie hybride (objectif +1 %), stop -10 %, 20 séances ;
  D2 : RSI-2 < 5, objectif +1 %, stop -15 %, 30 séances ;
  D3 : RSI-2 < 10, objectif +1 %, stop -15 %, 30 séances ;
  D4 : RSI-2 < 5, objectif +0,5 %, stop -15 %, 30 séances.
  Même règle de choix (≥ 80 % sur 2000-2015, puis meilleur Sharpe 2000-2015), mêmes contrôles.
Usage : python3 -m labo.combine80 → rapports/combine80.md / .json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import validation as V
from .combine import PERIODES, VARIANTES, backtest, charger, indicateurs, mesures, ruine

ICI = Path(__file__).resolve().parent.parent
VARIANTES80 = {
    "C1": {"sortie": "C", "seuil": 10, "tp": 0.01, "tendance_forte": False},
    "C1T": {"sortie": "C", "seuil": 10, "tp": 0.01, "tendance_forte": True},
    "C05": {"sortie": "C", "seuil": 10, "tp": 0.005, "tendance_forte": False},
    "C05T": {"sortie": "C", "seuil": 10, "tp": 0.005, "tendance_forte": True},
    "D1": {"sortie": "C", "seuil": 5, "tp": 0.01, "stop": 0.10, "duree": 20},
    "D2": {"sortie": "C", "seuil": 5, "tp": 0.01, "stop": 0.15, "duree": 30},
    "D3": {"sortie": "C", "seuil": 10, "tp": 0.01, "stop": 0.15, "duree": 30},
    "D4": {"sortie": "C", "seuil": 5, "tp": 0.005, "stop": 0.15, "duree": 30},
}


def hasard(c, ind, v, n=50):
    cv, m200, m50 = c.values, ind["mm200"].values, ind["mm50"].values
    zone = cv > m200
    if v.get("tendance_forte"):
        zone = zone & (m50 > m200)
    vrai = (ind["rsi"].values < v["seuil"]) & zone
    freq = vrai.sum() / max(zone.sum(), 1)
    out = []
    for g in range(n):
        s = (np.random.default_rng(g).random(cv.shape) < freq) & zone
        r, t = backtest(c, ind, signal=s, **{k: x for k, x in v.items() if k != "tendance_forte"})
        out.append(mesures(r, t, "2000-01-01", "2100-01-01"))
    return out


def main():
    c = charger()
    ind = indicateurs(c)
    o = {"variantes": {}, "references": {}}
    res = {}
    for nom, v in {**VARIANTES80, "A5": VARIANTES["A5"], "B10": VARIANTES["B10"]}.items():
        r, t = backtest(c, ind, **v)
        res[nom] = (r, t)
        cible = o["variantes"] if nom in VARIANTES80 else o["references"]
        cible[nom] = {p: mesures(r, t, a, b) for p, (a, b) in PERIODES.items()}
        cible[nom]["tout"] = mesures(r, t, "2000-01-01", "2100-01-01")
        if nom in VARIANTES80:
            V.enregistrer_experience("combine:etf16", f"{nom}|K5|L1", "-", {"sharpe_choix": cible[nom]["2000-2015 (choix)"]["sharpe"]})
    dev = {n: o["variantes"][n]["2000-2015 (choix)"] for n in VARIANTES80}
    ok = [n for n in VARIANTES80 if dev[n]["reussite"] >= 0.80]
    o["choisie"] = max(ok, key=lambda n: dev[n]["sharpe"]) if ok else max(VARIANTES80, key=lambda n: dev[n]["reussite"])
    o["atteint_80"] = bool(ok)
    o["hasard"] = {}
    for n in VARIANTES80:
        hz = hasard(c, ind, VARIANTES80[n])
        tout = o["variantes"][n]["tout"]
        o["hasard"][n] = {"reussite_mediane": float(np.median([h["reussite"] for h in hz])),
                          "sharpe_median": float(np.median([h["sharpe"] for h in hz])),
                          "percentile_sharpe": float(np.mean([h["sharpe"] < tout["sharpe"] for h in hz])),
                          "percentile_reussite": float(np.mean([h["reussite"] < tout["reussite"] for h in hz]))}
    v = VARIANTES80[o["choisie"]]
    o["levier"] = {}
    for Lv in (1, 2, 3):
        r, t = backtest(c, ind, levier=float(Lv), **v)
        o["levier"][Lv] = {"tout": mesures(r, t, "2000-01-01", "2100-01-01"),
                           "test": mesures(r, t, *PERIODES["2022 → aujourd'hui (test)"]), "ruine_5ans": ruine(r)}
    (ICI / "rapports" / "combine80.json").write_text(json.dumps(o, indent=1, ensure_ascii=False, default=str))
    rapport(o)


def pc(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f} %"


def rapport(o):
    L = ["# Combinaison A5 + B10 — objectif 80 % de réussite\n",
         "Commande : `python3 -m labo.combine80` · variantes et règle de choix fixées avant exécution (en-tête de `labo/combine80.py`).\n",
         "| Variante | Période | Trades | Réussite | Gain moyen | Perte moyenne | Pire trade | Profit factor | Rendement/an | Pire baisse | Sharpe | Mois positifs |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for groupe in ("variantes", "references"):
        for n, d in o[groupe].items():
            for p_, m in d.items():
                if p_ == "tout":
                    continue
                tag = " ← choisie" if n == o["choisie"] else (" (référence)" if groupe == "references" else "")
                L.append(f"| {n}{tag} | {p_} | {m['trades']} | {pc(m['reussite'], 0)} | {pc(m['gain_moyen'])} | {pc(m['perte_moyenne'])} | {pc(m['pire_trade'])} | "
                         f"{'—' if m['profit_factor'] is None else format(m['profit_factor'], '.2f')} | {pc(m['rendement_annuel'])} | {pc(m['pire_baisse'], 0)} | "
                         f"{m['sharpe']:.2f} | {m['mois_positifs'] * 100:.0f} % |")
    L += ["\n## Comparaison au hasard (mêmes sorties, 50 tirages, 2000 → aujourd'hui)\n",
          "| Variante | Réussite | Réussite du hasard | Sharpe | Sharpe du hasard | Bat le hasard (réussite) | Bat le hasard (Sharpe) |", "|---|---|---|---|---|---|---|"]
    for n, h in o["hasard"].items():
        t = o["variantes"][n]["tout"]
        L.append(f"| {n} | {pc(t['reussite'], 0)} | {h['reussite_mediane'] * 100:.0f} % | {t['sharpe']:.2f} | {h['sharpe_median']:.2f} | "
                 f"{h['percentile_reussite'] * 100:.0f} % | {h['percentile_sharpe'] * 100:.0f} % |")
    L += [f"\n## Curseur de levier — variante {o['choisie']}\n",
          "| Levier | Réussite | Rendement/an | Mois moyen | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |",
          "|---|---|---|---|---|---|---|---|---|"]
    for Lv, d in o["levier"].items():
        m, t = d["tout"], d["test"]
        L.append(f"| ×{Lv} | {pc(m['reussite'], 0)} | {pc(m['rendement_annuel'])} | {pc(m['mois_moyen'], 2)} | {m['mois_positifs'] * 100:.0f} % | {pc(m['pire_mois'])} | "
                 f"{pc(m['pire_baisse'], 0)} | {pc(t['rendement_annuel'])}, {pc(t['pire_baisse'], 0)} | {d['ruine_5ans'] * 100:.0f} % |")
    L.append(f"\nObjectif 80 % atteint sur 2000-2015 : **{'oui' if o['atteint_80'] else 'non'}**.")
    (ICI / "rapports" / "combine80.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
