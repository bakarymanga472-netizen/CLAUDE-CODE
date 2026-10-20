"""Audit 01 — qualité des données et artefacts du calendrier 7j/7.

Contrôles : bornes, doublons, trous, jours à variation nulle, plus forts mouvements (sauts de contrat GC=F),
part des jours « reportés », trades de reussite.simuler dont l'entrée/sortie tombe sur un jour reporté
(prix d'exécution = clôture du signal → regard vers le futur), comparaison GC=F vs GLD.

Usage : cd projets/bot-trading && python3 audit/a01_donnees.py
"""
import numpy as np
import pandas as pd

import commun
from aladdin import desks, reussite

out = ["# Audit 01 — données\n"]
px = commun.prix()
out.append(f"Index prix() : {px.index[0].date()} → {px.index[-1].date()}, {len(px)} jours calendaires.\n")
out.append("| Actif | 1re date valide | Dernière | NaN internes | Jours à variation nulle | Plus forte hausse | Plus forte baisse |")
out.append("|---|---|---|---|---|---|---|")
for c in px.columns:
    s = px[c]
    v = s.dropna()
    interne = s.loc[v.index[0]:v.index[-1]].isna().sum()
    r = v.pct_change()
    out.append(f"| {c} | {v.index[0].date()} | {v.index[-1].date()} | {interne} | {(r == 0).sum()} "
               f"({(r == 0).mean() * 100:.0f} %) | {r.max() * 100:+.1f} % ({r.idxmax().date()}) | {r.min() * 100:+.1f} % ({r.idxmin().date()}) |")

# Fichiers bruts : doublons et trous
out.append("\n## Fichiers bruts de data/\n")
for f in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]:
    d = pd.read_csv(commun.RACINE / "data" / f"{f}.csv", index_col=0, parse_dates=True)
    attendu = pd.date_range(d.index.min(), d.index.max(), freq="D")
    out.append(f"- {f} : {len(d)} lignes, doublons {d.index.duplicated().sum()}, jours manquants {len(attendu.difference(d.index))}, "
               f"bougies à volume nul {(d.volume == 0).sum()}")
for f in ["yahoo_SPY", "yahoo_GC_F", "yahoo_TLT"]:
    d = pd.read_csv(commun.RACINE / "data" / f"{f}.csv", index_col=0, parse_dates=True)["close"]
    bd = pd.bdate_range(d.index.min(), d.index.max())
    out.append(f"- {f} : {len(d)} séances, doublons {d.index.duplicated().sum()}, jours ouvrés absents {len(bd.difference(d.index))} "
               f"(fériés US ≈ 9-10/an attendus), séances à variation exactement nulle {(d.pct_change() == 0).sum()}")

# Jours à variation nulle supprimés par enquete.executer (vraies séances perdues)
out.append("\n## enquete.py:78 — `c.diff().ne(0)` retire aussi de VRAIES séances sans variation\n")
for c in ["ACTIONS", "OR"]:
    brut = pd.read_csv(commun.RACINE / "data" / f"yahoo_{'SPY' if c == 'ACTIONS' else 'GC_F'}.csv", index_col=0, parse_dates=True)["close"]
    garde = commun.seances(px[c])
    perdues = brut.index.difference(garde.index)
    out.append(f"- {c} : {len(brut)} séances Yahoo, {len(garde)} gardées, **{len(perdues)} vraies séances supprimées** "
               f"(ex. {', '.join(str(x.date()) for x in perdues[:5])})")

# GC=F : sauts au changement de contrat (future continu non ajusté)
out.append("\n## GC=F (future continu) vs GLD (ETF réellement traité par alpaca.py)\n")
try:
    gld = commun.yahoo_ohlc("GLD")["adjclose"]
    gc = pd.read_csv(commun.RACINE / "data" / "yahoo_GC_F.csv", index_col=0, parse_dates=True)["close"]
    j = pd.concat([gc.pct_change(), gld.pct_change()], axis=1, keys=["gc", "gld"]).dropna()
    diff = (j.gc - j.gld)
    out.append(f"- Corrélation quotidienne GC=F/GLD : {j.corr().iloc[0, 1]:.3f} ; écart-type de l'écart quotidien {diff.std() * 100:.2f} % ; "
               f"{(diff.abs() > 0.01).sum()} jours avec écart > 1 % (sur {len(j)})")
    an = pd.concat([(1 + j.gc).groupby(j.index.year).prod() - 1, (1 + j.gld).groupby(j.index.year).prod() - 1], axis=1, keys=["GC=F", "GLD"])
    out.append(f"- Rendement cumulé {j.index[0].date()}→{j.index[-1].date()} : GC=F {commun.pct((1 + j.gc).prod() - 1)}, GLD {commun.pct((1 + j.gld).prod() - 1)}")
    out.append(f"- Les 5 plus gros écarts GC=F − GLD : " + ", ".join(f"{d.date()} {x * 100:+.1f} %" for d, x in diff.abs().nlargest(5).items()))
except Exception as e:  # noqa: BLE001
    out.append(f"- GLD non téléchargé : {e}")

# reussite.simuler sur calendrier 7j/7 : entrées et sorties sur jours reportés
out.append("\n## reussite.py:46/61 — exécution « clôture suivante » qui tombe un jour reporté (= clôture du signal)\n")
regle = {"entree": "rsi2", "seuil": 5, "mm5": False, "tp": 0.01, "sl": 0.10, "duree": 20}
port, tr = reussite.portefeuille(px, ["ACTIONS", "OR"], regle)
tot = len(tr)
for a in ["ACTIONS", "OR"]:
    c = px[a].dropna()
    reporte = c.diff().eq(0)
    t = tr[tr.actif == a]
    e_rep = t.date.map(lambda d: bool(reporte.get(d, False))).sum()
    s_rep = t.sortie.map(lambda d: bool(reporte.get(d, False))).sum()
    out.append(f"- {a} : {len(t)} trades ; entrée sur un jour reporté (achat au cours du signal) : **{e_rep}** ; "
               f"sortie sur un jour reporté (vente au cours du déclenchement) : **{s_rep}**")
out.append(f"- Ce moteur est celui de `live_rebond.py:29` (via reussite.portefeuille), PAS celui qui a produit 84/78/79 % (enquete.executer).")
# durée et MM200 en jours calendaires
out.append("- Dans reussite.py, `rolling(200)` = 200 jours calendaires (≈ 138 séances) et `duree` = jours calendaires, "
           "alors que sorties.py/enquete.py comptent en séances : deux règles différentes portent le même nom.")

(commun.SORTIES / "a01_donnees.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
