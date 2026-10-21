"""Enquête sur les trades perdants de D1 et correctifs (demande du 2026-10-21).

Autopsie faite sur 2000-2015 SEULEMENT (période de choix), avec les informations connues à la clôture de décision.
Constats (voir rapport) :
  1. 67 % des perdants étaient GAGNANTS à la clôture de décision, puis vendus perdants au cours de clôture du lendemain ;
  2. à l'entrée, gagnants et perdants sont indiscernables (RSI-2, écart à la MM200, baisse 5 jours, largeur du marché) ;
  3. les stops surviennent en volatilité élevée ; les sorties « par la durée » sont déjà à -2,6 % au 10e jour.
Correctifs FIXÉS AVANT de regarder 2016-2021 et 2022+ :
  F1 : objectif et « rebond au-dessus de la MM5 en gain » transformés en ORDRE LIMITE posé la veille (seuil connu à la
       clôture : moyenne des 4 dernières clôtures, au moins +0,1 % au-dessus du prix d'entrée), exécuté dans la séance si le
       plus haut dépasse la limite de 0,05 % ; stop -10 % et durée inchangés ;
  F2 : durée maximale 10 séances au lieu de 20 ;
  F3 : pas de nouvelle entrée quand la volatilité 20 jours du SPY est dans les 20 % les plus hautes de son historique ;
  et les combinaisons F1+F2, F1+F3, F1+F2+F3.
Règle d'acceptation : sur 2000-2015 PUIS sur 2016-2021, la réussite monte ET le rendement annuel ne baisse pas.
Lecture ajoutée après exécution (tracée) : F1 est rejeté par la règle (rendement à levier 1 plus faible) alors qu'il transforme
la plupart des perdants en gagnants. On mesure donc aussi F1 contre le hasard et À RISQUE ÉGAL (curseur de levier), sans
changer la règle : F1 reste « non accepté » par la règle et est présenté comme candidate au suivi papier.
Usage : python3 -m labo.enquete_d1 → rapports/enquete_d1.md / .json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import validation as V
from .combine import PERIODES, backtest, charger_ohlc, indicateurs, mesures, ruine
from .combine80 import VARIANTES80

ICI = Path(__file__).resolve().parent.parent
BASE = VARIANTES80["D1"]
CORRECTIFS = {"D1": {}, "F1": {"limite": True}, "F2": {"duree": 10}, "F3": {"filtre_vol": True},
              "F1+F2": {"limite": True, "duree": 10}, "F1+F3": {"limite": True, "filtre_vol": True},
              "F1+F2+F3": {"limite": True, "duree": 10, "filtre_vol": True}}


def autopsie(c, ind, t):
    dev = t[t.entree <= pd.Timestamp("2015-12-31")]
    p = dev[dev.rendement <= 0]
    return {"trades": int(len(dev)), "perdants": int(len(p)), "par_motif": p.motif.value_counts().to_dict(),
            "part_perte_par_motif": (p.groupby("motif").rendement.sum() / p.rendement.sum()).round(3).to_dict(),
            "perte_moyenne_par_motif": p.groupby("motif").rendement.mean().round(4).to_dict()}


def main():
    c, o_, h_ = charger_ohlc()
    ind = indicateurs(c, o_, h_)
    out = {"variantes": {}}
    res = {}
    for nom, x in CORRECTIFS.items():
        r, t = backtest(c, ind, **{**BASE, **x})
        res[nom] = (r, t)
        out["variantes"][nom] = {p: mesures(r, t, a, b) for p, (a, b) in PERIODES.items()}
        dev = t[t.entree <= pd.Timestamp("2015-12-31")]
        out["variantes"][nom]["perdants_dev_par_motif"] = dev[dev.rendement <= 0].motif.value_counts().to_dict()
        if nom != "D1":
            V.enregistrer_experience("combine:etf16", f"D1+{nom}|K5|L1", "-", {})
    out["autopsie_D1"] = autopsie(c, ind, res["D1"][1])
    b = out["variantes"]["D1"]
    acc = {}
    for nom in CORRECTIFS:
        if nom == "D1":
            continue
        v = out["variantes"][nom]
        acc[nom] = all(v[p]["reussite"] > b[p]["reussite"] and v[p]["rendement_annuel"] >= b[p]["rendement_annuel"]
                       for p in ("2000-2015 (choix)", "2016-2021 (contrôle)"))
    out["acceptes"] = acc
    gardes = [n for n, ok in acc.items() if ok]
    final = max(gardes, key=lambda n: out["variantes"][n]["2000-2015 (choix)"]["sharpe"]) if gardes else "D1"
    out["final"] = final
    out["hasard"], out["levier"] = {}, {}
    cv, m200 = c.values, ind["mm200"].values
    zone = cv > m200
    for nom in dict.fromkeys([final, "D1", "F1"]):
        x = {**BASE, **CORRECTIFS[nom]}
        vrai = (ind["rsi"].values < x["seuil"]) & zone
        freq = vrai.sum() / max(zone.sum(), 1)
        tout = mesures(*res[nom], "2000-01-01", "2100-01-01")
        hz = []
        for g in range(50):
            sgn = (np.random.default_rng(g).random(cv.shape) < freq) & zone
            rh, th = backtest(c, ind, signal=sgn, **{k: v for k, v in x.items() if k != "filtre_vol"})
            hz.append(mesures(rh, th, "2000-01-01", "2100-01-01"))
        out["hasard"][nom] = {"reussite_mediane": float(np.median([h["reussite"] for h in hz])),
                              "sharpe_median": float(np.median([h["sharpe"] for h in hz])),
                              "percentile_sharpe": float(np.mean([h["sharpe"] < tout["sharpe"] for h in hz])),
                              "percentile_reussite": float(np.mean([h["reussite"] < tout["reussite"] for h in hz])),
                              "reussite": tout["reussite"], "sharpe": tout["sharpe"]}
        out["levier"][nom] = {}
        for Lv in (1, 2, 3, 4):
            r, t = backtest(c, ind, levier=float(Lv), **x)
            out["levier"][nom][Lv] = {"tout": mesures(r, t, "2000-01-01", "2100-01-01"),
                                      "test": mesures(r, t, *PERIODES["2022 → aujourd'hui (test)"]), "ruine_5ans": ruine(r)}
    (ICI / "rapports" / "enquete_d1.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    rapport(out)


def pc(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f} %"


def rapport(o):
    a = o["autopsie_D1"]
    L = ["# Enquête sur les trades perdants de D1 et correctifs\n",
         "Commande : `python3 -m labo.enquete_d1` · autopsie sur 2000-2015 seulement · correctifs fixés avant de regarder 2016-2021 et 2022+ "
         "(en-tête de `labo/enquete_d1.py`).\n", "## Autopsie (2000-2015)\n",
         f"- {a['trades']} trades, {a['perdants']} perdants.",
         f"- Perdants par cause : {a['par_motif']} — part de la perte totale : {a['part_perte_par_motif']} — perte moyenne : {a['perte_moyenne_par_motif']}.",
         "- « objectif/rebond » = le trade était GAGNANT à la clôture de décision, mais la vente au cours de clôture du LENDEMAIN l'a rendu perdant.",
         "- À l'entrée, gagnants et perdants ont les mêmes caractéristiques (RSI-2, écart à la MM200, baisse sur 5 jours, largeur du marché) : "
         "aucun filtre d'entrée ne les sépare. Les stops arrivent plutôt en volatilité élevée ; les sorties par la durée sont déjà à -2,6 % au 10e jour.\n",
         "## Correctifs testés\n",
         "| Version | Période | Trades | Réussite | Gain moyen | Perte moyenne | Profit factor | Rendement/an | Pire baisse | Sharpe | Mois positifs |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, d in o["variantes"].items():
        for p, m in d.items():
            if not isinstance(m, dict) or "trades" not in m:
                continue
            tag = " ← retenue" if n == o["final"] else (" (accepté)" if o["acceptes"].get(n) else "")
            L.append(f"| {n}{tag} | {p} | {m['trades']} | {pc(m['reussite'], 0)} | {pc(m['gain_moyen'])} | {pc(m['perte_moyenne'])} | "
                     f"{'—' if m['profit_factor'] is None else format(m['profit_factor'], '.2f')} | {pc(m['rendement_annuel'])} | {pc(m['pire_baisse'], 0)} | "
                     f"{m['sharpe']:.2f} | {m['mois_positifs'] * 100:.0f} % |")
    L += ["\n**Perdants restants en 2000-2015, par cause** :\n"] + [f"- {n} : {d['perdants_dev_par_motif']}" for n, d in o["variantes"].items()]
    L += [f"\n## Version retenue par la règle : {o['final']}\n",
          "## Comparaison au hasard (mêmes sorties, 50 tirages, 2000 → aujourd'hui)\n",
          "| Version | Réussite | Réussite du hasard | Sharpe | Sharpe du hasard | Bat le hasard (réussite) | Bat le hasard (Sharpe) |", "|---|---|---|---|---|---|---|"]
    for n, h in o["hasard"].items():
        L.append(f"| {n} | {h['reussite'] * 100:.0f} % | {h['reussite_mediane'] * 100:.0f} % | {h['sharpe']:.2f} | {h['sharpe_median']:.2f} | "
                 f"{h['percentile_reussite'] * 100:.0f} % | {h['percentile_sharpe'] * 100:.0f} % |")
    L += ["\n## À risque égal : curseur de levier\n",
          "| Version | Levier | Réussite | Rendement/an | Mois moyen | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for n, lv in o["levier"].items():
        for Lv, d in lv.items():
            m, t = d["tout"], d["test"]
            L.append(f"| {n} | ×{Lv} | {pc(m['reussite'], 0)} | {pc(m['rendement_annuel'])} | {pc(m['mois_moyen'], 2)} | {m['mois_positifs'] * 100:.0f} % | "
                     f"{pc(m['pire_mois'])} | {pc(m['pire_baisse'], 0)} | {pc(t['rendement_annuel'])}, {pc(t['pire_baisse'], 0)} | {d['ruine_5ans'] * 100:.0f} % |")
    L += ["\n**Lecture.** F1 vend dès que le cours touche un seuil fixé la veille (objectif +1 % ou retour au-dessus de la moyenne des "
          "4 dernières clôtures, au moins +0,1 %) : les trades « gagnants à la décision, perdants le lendemain » deviennent gagnants. "
          "La réussite passe à ~95 % — mais des entrées au hasard avec la même sortie font aussi ~95 % : ce taux vient de la "
          "sortie. Ce qui vient de l'entrée, c'est le Sharpe (comparaison au hasard ci-dessus). Prix à payer : gain moyen ~+0,6 % "
          "contre une perte moyenne ~-4,8 % (une perte ≈ 8 gains). À levier 1, F1 rapporte moins que D1 ; à pire baisse égale "
          "(F1 ×3 contre D1 ×2), il rapporte autant ou plus. La règle fixée à l'avance le rejette (rendement à levier 1) : il reste "
          "candidat au suivi papier, pas validé.\n"]
    L.append("\nLimite : les ventes à cours limité sont simulées avec le plus haut du jour (marge de 0,05 %) ; en réel, un ordre posé "
             "exactement au plus haut peut ne pas être exécuté. Les correctifs ont été choisis après une autopsie sur 2000-2015 : "
             "2016-2021 et 2022+ sont les seuls juges.")
    (ICI / "rapports" / "enquete_d1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
