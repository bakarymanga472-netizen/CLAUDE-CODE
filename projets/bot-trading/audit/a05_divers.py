"""Audit 05 — comptage des essais, walk-forward avec retard d'exécution, annualisation 365 vs 252.

Usage : cd projets/bot-trading && python3 audit/a05_divers.py
"""
import math

import numpy as np
import pandas as pd

import commun
from aladdin import enquete, moteur, recherche, reussite

out = ["# Audit 05 — essais, walk-forward retardé, annualisation\n"]
px = commun.prix()

# 1. comptage des essais à partir du code
n_rech = len(recherche.candidats(px))
n_reg = len(list(reussite.regles()))
n_reu = n_reg * len(reussite.PORTEFEUILLES)
n_enq = len(enquete.NOMS) * 6
n_sor = 3 * 5 * 4 * 3
out += ["## 1. Variantes testées avant les choix finaux (comptées dans le code)\n",
        f"- recherche.py : {n_rech} structures (12 signaux × 2 univers × 2 gestions) + sélection annuelle walk-forward (8 choix)",
        f"- reussite.py : {n_reg} règles × {len(reussite.PORTEFEUILLES)} univers = {n_reu} combinaisons + 2 méthodes de choix",
        f"- enquete.py : {n_enq} filtres candidats par tour (7 indicateurs × 6 quantiles) × 2 structures = {2 * n_enq} (+1 test de validation)",
        f"- sorties.py : {n_sor} réglages (3 seuils × 5 objectifs × 4 stops × 3 durées)",
        f"- **Total Aladdin : {n_rech + n_reu + 2 * n_enq + n_sor} variantes** ; lignée Rebond (reussite → enquête → sorties) : {n_reu + n_enq + n_sor} ; "
        f"lignée momentum : {n_rech} (+{n_enq} filtres d'enquête). Sans compter bot/ (tester.py, tester_or.py, or_systeme.py) testés avant."]

# 2. walk-forward avec 1 jour de retard sur TOUS les candidats
cands = recherche.candidats(px)
for retard in (0, 1):
    rends = {}
    for k, c in cands.items():
        if retard == 0:
            rends[k] = c["rend"]
        else:
            nom_sig, u, g = [x.strip() for x in k.split("|")]
            p = c["px"]
            sg = c["signal"]
            from aladdin import desks
            if g == "vol cible":
                w = desks.desk_risque(p, sg)
            else:
                n = p.notna().sum(axis=1).clip(lower=1)
                w = sg.where(p.notna(), 0).div(n, axis=0)
            rends[k] = moteur.portefeuille(p, w.shift(retard).fillna(0.0))
    morceaux = []
    for y in recherche.ANNEES_WF:
        meilleur = max(rends, key=lambda k: recherche.sharpe(rends[k].loc[:f"{y - 1}-12-31"]))
        morceaux.append(rends[meilleur].loc[f"{y}-01-01":f"{y}-12-31"])
    st = moteur.stats(pd.concat(morceaux))
    if retard == 0:
        out.append("\n## 2. Walk-forward recalculé avec exécution retardée\n")
    out.append(f"- Retard {retard} j : {commun.pct(st['rendement'])} ({commun.pct(st['par_an'])}/an), pire baisse {commun.pct(st['pire_baisse'])}, Sharpe {st['sharpe']:.2f}")
out.append("(Poids décidés à la clôture crypto de 00:00 UTC appliqués au rendement SPY/TLT/or depuis la clôture de New York de la veille au soir : "
           "≈ 4 h d'avance pour les actifs traditionnels du panier multi-actifs.)")

# 3. annualisation
out.append("\n## 3. Annualisation : calendrier 7j/7 × 365 (moteur.py:24-27) vs séances × 252\n")
for a in ["ACTIONS", "OR", "OBLIGATIONS"]:
    r7 = px[a].pct_change().dropna()
    rs = commun.seances(px[a]).pct_change().dropna()
    s7 = r7.mean() * 365 / (r7.std() * math.sqrt(365))
    s5 = rs.mean() * 252 / (rs.std() * math.sqrt(252))
    out.append(f"- {a} : Sharpe 7j/7×365 = {s7:.3f} ; séances×252 = {s5:.3f} ; vol 7j/7 {r7.std() * math.sqrt(365) * 100:.1f} % vs {rs.std() * math.sqrt(252) * 100:.1f} %")
out.append("→ Écart faible : l'annualisation 365 sur un calendrier à week-ends nuls n'est pas une source d'erreur significative.")

(commun.SORTIES / "a05_divers.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
