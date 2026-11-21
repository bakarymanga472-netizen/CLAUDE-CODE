"""Bot « haute réussite + gros gains » (demande du 2026-10-21) — D1+F1 élargi.

Diagnostic de départ (rapports/test_2026.md, combine80.md) : D1+F1 fait 95-97 % de trades gagnants mais seulement
+3,7 à +6,6 %/an, car avec 16 ETF le capital reste investi une petite partie du temps. Piste : PLUS de signaux
(univers élargi) et un capital qui travaille, SANS toucher aux règles d'entrée/sortie (aucun réglage nouveau).

Règles FIXÉES AVANT EXÉCUTION (2026-10-21) :
- stratégie D1+F1 inchangée : RSI-2 < 5 au-dessus de la MM200, vente à cours limité (+1 % ou rebond MM5 en gain),
  stop -10 %, 20 séances ; coûts 0,02 % par côté ; emprunt 5 %/an au-delà de 100 % investi.
- 4 variantes : U16-K5 (référence actuelle), U40-K5, U40-K10, U40-K10-T (argent non investi placé au taux des
  bons du Trésor à 13 semaines, ^IRX).
- univers U40 : 40 ETF liquides cotés avant 2008 (actions US, secteurs, pays, obligations, matières premières).
- règle de choix : parmi les variantes à ≥ 85 % de trades gagnants sur 2008-2015, meilleur Sharpe 2008-2015.
  Contrôle 2016-2021, test 2022-2024, récent 2025 → aujourd'hui (rapporté à part, jamais utilisé pour choisir).
- critères de réussite de l'objectif (sur 2025 → aujourd'hui, frais inclus) : ≥ 85 % de trades gagnants,
  rendement > SPY gardé, pire baisse > -15 %, ≥ 30 trades.
- levier ×1, ×2, ×3 montré comme curseur de risque (risque de perdre 50 % en 5 ans).
Usage : python3 -m labo.haute_reussite → rapports/haute_reussite.md / .json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import combine, donnees
from .combine import indicateurs, mesures, ruine

ICI = Path(__file__).resolve().parent.parent
U16 = combine.UNIVERS
U40 = U16 + ["MDY", "VGK", "EWJ", "EWZ", "FXI", "EWG", "EWU", "EWC", "EWA", "SLV", "IEF", "LQD", "TIP",
             "XLB", "IYR", "SMH", "XBI", "KRE", "XHB", "XRT", "IBB", "DBC", "USO", "EWT"]
VARIANTES = {"U16-K5": (U16, 5, False), "U40-K5": (U40, 5, False), "U40-K10": (U40, 10, False),
             "U40-K10-T": (U40, 10, True)}
D1F1 = {"sortie": "C", "seuil": 5, "tp": 0.01, "stop": 0.10, "duree": 20, "limite": True}
PERIODES = {"2008-2015 (choix)": ("2008-01-01", "2015-12-31"), "2016-2021 (contrôle)": ("2016-01-01", "2021-12-31"),
            "2022-2024 (test)": ("2022-01-01", "2024-12-31"), "2025 → auj. (récent)": ("2025-01-01", "2100-01-01")}


def charger(univers):
    d = {s: donnees.charger_yahoo(s)[0] for s in univers}
    c = pd.DataFrame({s: x.close for s, x in d.items()}).sort_index()
    c = c.loc[c.index >= c.SPY.first_valid_index()]
    o = pd.DataFrame({s: x.open for s, x in d.items()}).reindex(c.index)
    h = pd.DataFrame({s: x.high for s, x in d.items()}).reindex(c.index)
    return c, o, h


def taux_tresor(index):
    """Rendement quotidien des bons du Trésor à 13 semaines (^IRX, en % annuel), aligné sur les séances."""
    irx = donnees.charger_yahoo("^IRX")[0].close.reindex(index).ffill().fillna(0.0)
    return irx / 100 / 252


def exposition(t, index, poids):
    """Part du capital investie chaque séance, reconstituée à partir des trades (entrée → sortie)."""
    e = pd.Series(0.0, index=index)
    if len(t):
        pos = {d: i for i, d in enumerate(index)}
        v = np.zeros(len(index))
        for _, x in t.iterrows():
            a, b = pos[x.entree], pos[x.sortie]
            v[a + 1:b + 1] += poids
        e[:] = v
    return e


def lancer(univers, k, tresor, levier=1.0):
    c, o, h = charger(univers)
    ind = indicateurs(c, o, h)
    combine.K = k                                     # backtest() lit K au niveau du module
    try:
        r, t = combine.backtest(c, ind, levier=levier, **D1F1)
    finally:
        combine.K = 5
    if tresor:
        libre = (1.0 - exposition(t, c.index, levier / k)).clip(lower=0.0)
        r = r + libre * taux_tresor(c.index)
    return c, r, t


def main():
    out = {"variantes": {}, "references": {}, "criteres": {}}
    res = {}
    for nom, (u, k, tr) in VARIANTES.items():
        c, r, t = lancer(u, k, tr)
        res[nom] = (c, r, t)
        out["variantes"][nom] = {p: mesures(r, t, a, b) for p, (a, b) in PERIODES.items()}
    ok = [n for n in VARIANTES if (out["variantes"][n]["2008-2015 (choix)"]["reussite"] or 0) >= 0.85]
    choix = max(ok or VARIANTES, key=lambda n: out["variantes"][n]["2008-2015 (choix)"]["sharpe"])
    out["choisie"], out["seuil_85_atteint_au_choix"] = choix, bool(ok)

    c40 = res["U40-K10"][0]
    vide = pd.DataFrame(columns=["entree", "rendement"])
    spy = c40.SPY.pct_change(fill_method=None).fillna(0.0)
    ew = c40.pct_change(fill_method=None).mean(axis=1).fillna(0.0)
    out["references"]["SPY gardé"] = {p: mesures(spy, vide, a, b) for p, (a, b) in PERIODES.items()}
    out["references"]["40 ETF gardés"] = {p: mesures(ew, vide, a, b) for p, (a, b) in PERIODES.items()}

    u, k, tr = VARIANTES[choix]
    out["levier"] = {}
    for Lv in (1, 2, 3):
        _, r, t = lancer(u, k, tr, levier=float(Lv))
        out["levier"][Lv] = {p: mesures(r, t, a, b) for p, (a, b) in PERIODES.items()}
        out["levier"][Lv]["ruine_5ans"] = ruine(r.loc["2008-01-01":])
    rec = "2025 → auj. (récent)"
    for Lv, d in out["levier"].items():
        m, s = d[rec], out["references"]["SPY gardé"][rec]
        out["criteres"][Lv] = {"reussite_85": (m["reussite"] or 0) >= 0.85, "bat_spy": m["rendement_annuel"] > s["rendement_annuel"],
                               "baisse_15": m["pire_baisse"] > -0.15, "trades_30": m["trades"] >= 30}
    (ICI / "rapports" / "haute_reussite.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    rapport(out, res[choix][0].index[-1])


def pc(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f} %"


def ligne(nom, p, m):
    return (f"| {nom} | {p} | {m['trades']} | {pc(m['reussite'], 0) if m['reussite'] is not None else '—'} | {pc(m['gain_moyen'], 2)} | "
            f"{pc(m['perte_moyenne'], 2)} | {pc(m['rendement_annuel'])} | {pc(m['pire_baisse'], 0)} | {m['sharpe']:.2f} | "
            f"{m['mois_positifs'] * 100:.0f} % | {pc(m['pire_mois'])} |")


def rapport(o, fin):
    L = [f"# Bot haute réussite — D1+F1 élargi (données jusqu'au {fin.date()})\n",
         "Commande : `python3 -m labo.haute_reussite` · règles fixées avant exécution : en-tête de `labo/haute_reussite.py`.\n",
         "| Variante | Période | Trades | Réussite | Gain moyen | Perte moyenne | Rendement/an | Pire baisse | Sharpe | Mois positifs | Pire mois |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, d in o["variantes"].items():
        for p, m in d.items():
            L.append(ligne(n + (" ← choisie" if n == o["choisie"] else ""), p, m))
    for n, d in o["references"].items():
        for p, m in d.items():
            L.append(ligne(n + " (référence)", p, m))
    L += [f"\n## Curseur de levier — {o['choisie']}\n",
          "| Levier | Période | Trades | Réussite | Gain moyen | Perte moyenne | Rendement/an | Pire baisse | Sharpe | Mois positifs | Pire mois |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for Lv, d in o["levier"].items():
        for p, m in d.items():
            if p != "ruine_5ans":
                L.append(ligne(f"×{Lv}", p, m))
    L += ["\n| Levier | Risque de perdre 50 % en 5 ans | ≥ 85 % réussite (récent) | Bat SPY (récent) | Pire baisse > -15 % | ≥ 30 trades | **Objectif** |",
          "|---|---|---|---|---|---|---|"]
    for Lv, cr in o["criteres"].items():
        f = lambda b: "oui" if b else "**non**"
        L.append(f"| ×{Lv} | {o['levier'][Lv]['ruine_5ans'] * 100:.0f} % | {f(cr['reussite_85'])} | {f(cr['bat_spy'])} | {f(cr['baisse_15'])} | "
                 f"{f(cr['trades_30'])} | {'**ATTEINT**' if all(cr.values()) else 'non atteint'} |")
    L.append("\nVentes à cours limité simulées avec le plus haut du jour ; levier ×L = chaque position pèse L/K du capital.")
    (ICI / "rapports" / "haute_reussite.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
