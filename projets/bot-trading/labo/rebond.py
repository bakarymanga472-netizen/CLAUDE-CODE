"""Rebond corrigé (après audit) : même règle figée, mais en séances réelles, sur SPY + GLD (l'instrument réellement
traité), exécution au cours de clôture de la séance SUIVANTE, trades ouverts marqués comme ouverts.

Usage : python3 -m labo.rebond → rapports/rebond_corrige.md / .json
Critères « candidate démo » fixés AVANT exécution (2026-10-21, voir CRITERES) ; aucun critère n'autorise l'argent réel.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import donnees, validation as V
from .couts import Couts
from .moteur import simuler
from .strategies import rebond_tp_sl as R
from .strategies.outils import rsi

ICI = Path(__file__).resolve().parent.parent
ACTIFS = ["SPY", "GLD"]
P = R.GRILLE[0]
COUTS = Couts(commission=0.0, demi_spread_base=0.0001, glissement_sigma=0.02)   # ETF très liquides, ordre MOC, sans commission
PERIODES = {"2008-2019": ("2008-01-01", "2019-12-31"), "2020-2024": ("2020-01-01", "2024-12-31"),
            "2025+ (déjà vu pendant la sélection)": ("2025-01-01", "2100-01-01")}
ESSAIS_LIGNEE = 1662          # variantes comptées par l'audit (audit/a05_divers.py)
N_HASARD = 200
CRITERES = {"version": "rebond-demo-v1-2026-10-21",
            "sharpe_2020plus_couts_x3_min": 0.0, "percentile_hasard_min": 0.95, "trades_2020plus_min": 30}


def executer(df, cible, couts=COUTS):
    return simuler(df, cible, "1d", couts, dimensionner=False, execution="cloture")


def tableau(res_par_actif, debut, fin):
    t = pd.concat([r["trades"].assign(actif=a) for a, r in res_par_actif.items()])
    t = t[(t.entree >= debut) & (t.entree <= fin)]
    port = pd.concat({a: r["net"] for a, r in res_par_actif.items()}, axis=1).loc[debut:fin].fillna(0).mean(axis=1)
    c = (1 + port).cumprod()
    ans = max((port.index[-1] - port.index[0]).days / 365.25, 0.1)
    g, p = t.net[t.net > 0].sum(), -t.net[t.net <= 0].sum()
    return {"trades": len(t), "reussite": float((t.net > 0).mean()) if len(t) else None,
            "gain_moyen": float(t.net[t.net > 0].mean()) if (t.net > 0).any() else None,
            "perte_moyenne": float(t.net[t.net <= 0].mean()) if (t.net <= 0).any() else None,
            "pire_trade": float(t.net.min()) if len(t) else None, "profit_factor": float(g / p) if p else None,
            "rendement_annuel": float(c.iloc[-1] ** (1 / ans) - 1), "pire_baisse": float((c / c.cummax() - 1).min()),
            "sharpe": float(port.mean() / port.std() * np.sqrt(252)) if port.std() > 0 else 0.0,
            "exposition": float(pd.concat({a: r["w"] for a, r in res_par_actif.items()}, axis=1).loc[debut:fin].mean().mean())}


def hasard(df, graine, freq):
    """Mêmes sorties, entrées tirées au hasard parmi les séances au-dessus de la MM200, à la même fréquence que le signal."""
    rng = np.random.default_rng(graine)
    au_dessus = (df.close > df.close.rolling(200).mean()).values
    faux = df.copy()
    tirage = (rng.random(len(df)) < freq) & au_dessus
    # On remplace le RSI par un indicateur qui vaut 0 les jours tirés : même machine à états, mêmes sorties
    c = faux.close.values
    out = np.zeros(len(c))
    etat, e = 0, None
    for i in range(len(c)):
        if etat == 0 and tirage[i]:
            etat, e = 1, i + 1
        elif etat == 1:
            etat = 2
        if etat == 2:
            g = c[i] / c[e] - 1
            if g >= P["tp"] or g <= -P["sl"] or (i - e) >= P["duree"]:
                etat = 0
        out[i] = 1.0 if etat else 0.0
    return pd.Series(out, index=df.index)


def evaluer():
    data, emp, res, x3, ret, cibles = {}, {}, {}, {}, {}, {}
    for a in ACTIFS:
        data[a], emp[a] = donnees.charger_yahoo(a)
        cibles[a] = R.cible(data[a], 1, **P)
        res[a] = executer(data[a], cibles[a])
        x3[a] = executer(data[a], cibles[a], COUTS.stresse(3.0))
        ret[a] = executer(data[a], cibles[a], COUTS.stresse(1.0, retard=2))
    o = {"regle": P, "donnees": emp, "criteres": CRITERES, "periodes": {}}
    for nom, (d, f) in PERIODES.items():
        o["periodes"][nom] = {"base": tableau(res, d, f), "couts_x3": tableau(x3, d, f), "retard_1_seance": tableau(ret, d, f)}
        bh = pd.concat({a: data[a].close.pct_change() for a in ACTIFS}, axis=1).loc[d:f].fillna(0).mean(axis=1)
        cb = (1 + bh).cumprod()
        o["periodes"][nom]["achat_conservation_50_50"] = {
            "rendement_annuel": float(cb.iloc[-1] ** (365.25 / max((bh.index[-1] - bh.index[0]).days, 1)) - 1),
            "pire_baisse": float((cb / cb.cummax() - 1).min()), "sharpe": float(bh.mean() / bh.std() * np.sqrt(252))}
    # Trades ouverts (la dernière barre ne clôt pas un trade)
    o["positions_ouvertes"] = {a: bool(res[a]["w"].iloc[-1] != 0 or cibles[a].iloc[-1] != 0) for a in ACTIFS}
    # Hasard de même profil, 2020+
    debut = "2020-01-01"
    base = tableau(res, debut, "2100-01-01")
    freq = {a: float(((rsi(data[a].close, 2) < P["seuil"]) & (data[a].close > data[a].close.rolling(200).mean())).mean()) for a in ACTIFS}
    sh, wr = [], []
    for g in range(N_HASARD):
        rh = {a: executer(data[a], hasard(data[a], g * 10 + i, freq[a])) for i, a in enumerate(ACTIFS)}
        th = tableau(rh, debut, "2100-01-01")
        sh.append(th["sharpe"])
        wr.append(th["reussite"] or 0)
    o["hasard_2020plus"] = {"reussite_mediane": float(np.median(wr)), "reussite_c5_c95": [float(np.quantile(wr, .05)), float(np.quantile(wr, .95))],
                            "sharpe_median": float(np.median(sh)), "percentile_sharpe_regle": float((np.array(sh) < base["sharpe"]).mean()),
                            "percentile_reussite_regle": float((np.array(wr) < base["reussite"]).mean())}
    port = pd.concat({a: res[a]["net"] for a in ACTIFS}, axis=1).loc[debut:].fillna(0).mean(axis=1)
    o["dsr_2020plus"] = {"lignee_1662_var_nulle": V.dsr(port.values, ESSAIS_LIGNEE, 1 / len(port))[0]}
    x = o["periodes"]
    p20 = [x["2020-2024"], x["2025+ (déjà vu pendant la sélection)"]]
    n20 = sum(p["base"]["trades"] for p in p20)
    sx3 = tableau(x3, debut, "2100-01-01")["sharpe"]
    raisons = []
    if sx3 <= CRITERES["sharpe_2020plus_couts_x3_min"]:
        raisons.append(f"Sharpe 2020+ avec coûts ×3 = {sx3:.2f}")
    if o["hasard_2020plus"]["percentile_sharpe_regle"] < CRITERES["percentile_hasard_min"]:
        raisons.append(f"ne bat que {o['hasard_2020plus']['percentile_sharpe_regle']:.0%} des entrées au hasard (Sharpe)")
    if n20 < CRITERES["trades_2020plus_min"]:
        raisons.append(f"{n20} trades depuis 2020 < {CRITERES['trades_2020plus_min']}")
    o["statut"] = "candidate démo (paper uniquement)" if not raisons else "non validée"
    o["raisons"] = raisons
    return o


def pct(x):
    return "—" if x is None else f"{x * 100:+.1f} %"


def rapport(o):
    L = ["# Rebond corrigé — SPY + GLD, séances réelles, exécution clôture suivante\n",
         f"Commande : `python3 -m labo.rebond` · règle figée {o['regle']} · données {o['donnees']} · critères `{o['criteres']['version']}` (fixés avant exécution).\n",
         "Corrige les anomalies d'audit 3 (trades ouverts), 4 (calendrier), 5 (exécution le jour du signal), 6 (séances supprimées), 7 (rendement de portefeuille réel) et 8 (GLD au lieu de GC=F).\n",
         "| Période | Version | Trades | Réussite | Gain moy. | Perte moy. | Pire trade | PF | Rendement/an | Pire baisse | Sharpe | Exposition |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, p in o["periodes"].items():
        for v in ("base", "couts_x3", "retard_1_seance"):
            m = p[v]
            L.append(f"| {nom} | {v} | {m['trades']} | {pct(m['reussite'])} | {pct(m['gain_moyen'])} | {pct(m['perte_moyenne'])} | {pct(m['pire_trade'])} | "
                     f"{'—' if m['profit_factor'] is None else format(m['profit_factor'], '.2f')} | {pct(m['rendement_annuel'])} | {pct(m['pire_baisse'])} | {m['sharpe']:.2f} | {m['exposition']:.0%} |")
        b = p["achat_conservation_50_50"]
        L.append(f"| {nom} | *SPY+GLD gardés 50/50* | — | — | — | — | — | — | {pct(b['rendement_annuel'])} | {pct(b['pire_baisse'])} | {b['sharpe']:.2f} | 100 % |")
    h = o["hasard_2020plus"]
    L += [f"\n**Entrées au hasard, mêmes sorties (2020+, {N_HASARD} tirages)** : réussite médiane {h['reussite_mediane']:.0%} "
          f"(5e-95e : {h['reussite_c5_c95'][0]:.0%}-{h['reussite_c5_c95'][1]:.0%}) ; la règle bat {h['percentile_reussite_regle']:.0%} des tirages en réussite "
          f"et {h['percentile_sharpe_regle']:.0%} en Sharpe.",
          f"\n**DSR 2020+** (1 662 variantes dans la lignée, variance nulle) : {o['dsr_2020plus']['lignee_1662_var_nulle']:.2f}.",
          f"\nPositions encore ouvertes à la dernière clôture : {o['positions_ouvertes']}.",
          f"\n## Statut : **{o['statut']}**\n", f"- Raisons : {'; '.join(o['raisons']) or 'tous les critères démo passés'}",
          "- Même « candidate démo », la règle ne doit pas aller en argent réel : 2025+ a été vu pendant la sélection, le rendement est faible face "
          "à SPY+GLD gardés, et le DSR de la lignée reste sous 0,95.",
          "- Ne pas utiliser : si une donnée du jour manque, si le marché est fermé, si l'ordre MOC ne peut plus être passé (après 15 h 50 New York)."]
    return "\n".join(L) + "\n"


def main():
    o = evaluer()
    (ICI / "rapports" / "rebond_corrige.json").write_text(json.dumps(o, indent=1, default=str, ensure_ascii=False))
    t = rapport(o)
    (ICI / "rapports" / "rebond_corrige.md").write_text(t, encoding="utf-8")
    print(t)


if __name__ == "__main__":
    main()
