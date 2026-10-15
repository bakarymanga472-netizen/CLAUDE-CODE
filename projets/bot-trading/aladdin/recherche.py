"""Aladdin — recherche de la meilleure structure, sans tricher.

1. On génère toutes les structures candidates (desks × réglages × univers × gestion du risque).
2. Walk-forward : chaque année de 2017 à 2024, on choisit la structure qui avait le meilleur Sharpe
   AVANT cette année, et on la fait tourner sur l'année (résultat « hors échantillon »).
3. Coffre-fort : 2025-01-01 → aujourd'hui n'est JAMAIS regardé pendant la sélection.
   On choisit la structure finale avec les données jusqu'à fin 2024, puis on l'ouvre une seule fois.

Usage : python3 -m aladdin.recherche [--rafraichir]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import desks, donnees, moteur

ICI = Path(__file__).resolve().parent.parent
COFFRE = "2025-01-01"
ANNEES_WF = range(2017, 2025)
UNIVERS = {"crypto": [c.replace("USDT", "") for c in donnees.CRYPTOS],
           "multi-actifs": [c.replace("USDT", "") for c in donnees.CRYPTOS] + list(donnees.TRADITIONNELS)}


def catalogue(px):
    """Signaux de chaque desk pour chaque réglage (calculés une fois sur tout l'univers)."""
    s = {}
    for lb in (20, 60, 120, 250):
        s[f"momentum {lb} j"] = desks.desk_momentum(px, lb)
    for a, b in ((20, 100), (50, 200)):
        s[f"moyennes {a}/{b}"] = desks.desk_moyennes(px, a, b)
    for seuil in (5, 10):
        s[f"rebond RSI2<{seuil}"] = desks.desk_rebond(px, seuil)
    s["momentum 60+rebond"] = (s["momentum 60 j"] + s["rebond RSI2<10"]).clip(upper=1)
    s["momentum 120+rebond"] = (s["momentum 120 j"] + s["rebond RSI2<10"]).clip(upper=1)
    s["momentum 120 + moyennes 50/200"] = (s["momentum 120 j"] + s["moyennes 50/200"]) / 2
    s["ensemble momentum 60/120/250"] = (s["momentum 60 j"] + s["momentum 120 j"] + s["momentum 250 j"]) / 3
    return s


def candidats(px):
    out = {}
    for nom_sig, sig in catalogue(px).items():
        for u, cols in UNIVERS.items():
            p, sg = px[cols], sig[cols]
            for gestion in ("vol cible", "parts égales"):
                if gestion == "vol cible":
                    w = desks.desk_risque(p, sg)
                else:
                    n = p.notna().sum(axis=1).clip(lower=1)
                    w = sg.where(p.notna(), 0).div(n, axis=0)
                cle = f"{nom_sig} | {u} | {gestion}"
                out[cle] = {"rend": moteur.portefeuille(p, w), "signal": sg, "px": p}
    return out


def sharpe(r):
    r = r[r.index >= r.ne(0).idxmax()] if r.ne(0).any() else r
    if len(r) < 365 * 2 or r.std() == 0:
        return -np.inf
    return r.mean() / r.std() * np.sqrt(365)


def pct(x):
    return f"{x * 100:+.1f} %" if pd.notna(x) else "—"


def main():
    px = donnees.prix("--rafraichir" in sys.argv)
    cands = candidats(px)
    out = ["# Aladdin — rapport de recherche\n",
           f"Données jusqu'au {px.index[-1].date()}. {len(cands)} structures candidates. "
           f"Coffre-fort fermé pendant la sélection : {COFFRE} → aujourd'hui.\n"]

    # --- Le piège des 99 % ---
    p99 = moteur.piege_99(px.loc[:COFFRE])
    out += ["## Le piège du taux de réussite\n",
            f"Règle « vendre à +1 %, ne couper qu'à -50 % » sur BTC 2020-2024 : **{p99['reussite'] * 100:.1f} % de trades gagnants** "
            f"({p99['trades']} trades), capital final {pct(p99['capital_final'])}, contre {pct(p99['garder'])} en gardant simplement le BTC.\n"]

    # --- Walk-forward ---
    choix, morceaux = [], []
    for y in ANNEES_WF:
        passe = f"{y - 1}-12-31"
        meilleur = max(cands, key=lambda k: sharpe(cands[k]["rend"].loc[:passe]))
        choix.append((y, meilleur, sharpe(cands[meilleur]["rend"].loc[:passe])))
        morceaux.append(cands[meilleur]["rend"].loc[f"{y}-01-01":f"{y}-12-31"])
    wf = pd.concat(morceaux)
    out += ["## Walk-forward 2017-2024 (choix fait chaque année avec le passé seulement)\n",
            "| Année | Structure choisie | Sharpe passé | Résultat de l'année |", "|---|---|---|---|"]
    for (y, k, s), m in zip(choix, morceaux):
        out.append(f"| {y} | {k} | {s:.2f} | {pct((1 + m).prod() - 1)} |")
    st = moteur.stats(wf)
    out.append(f"\nTotal hors échantillon 2017-2024 : {pct(st['rendement'])} ({pct(st['par_an'])}/an), "
               f"pire baisse {pct(st['pire_baisse'])}, Sharpe {st['sharpe']:.2f}.\n")

    # --- Classement des candidats avant le coffre ---
    lignes = []
    for k, c in cands.items():
        r = c["rend"].loc[:"2024-12-31"]
        s = moteur.stats(r)
        t = moteur.trades(c["px"].loc[:"2024-12-31"], c["signal"].loc[:"2024-12-31"])
        lignes.append((sharpe(r), k, s, (t.rendement > 0).mean() if len(t) else np.nan, len(t)))
    lignes.sort(key=lambda x: -x[0] if np.isfinite(x[0]) else np.inf)
    out += ["## Top 12 des structures avant 2025 (et taux de trades gagnants)\n",
            "| Structure | Sharpe | Par an | Pire baisse | Trades gagnants | Trades |", "|---|---|---|---|---|---|"]
    for sh, k, s, wr, n in lignes[:12]:
        out.append(f"| {k} | {sh:.2f} | {pct(s['par_an'])} | {pct(s['pire_baisse'])} | {wr * 100:.0f} % | {n} |")
    meilleur_wr = max(lignes, key=lambda x: (x[3] if pd.notna(x[3]) else -1))
    out.append(f"\nMeilleur taux de réussite parmi les {len(lignes)} : **{meilleur_wr[3] * 100:.0f} %** ({meilleur_wr[1]}), "
               f"Sharpe {meilleur_wr[0]:.2f}, {pct(meilleur_wr[2]['par_an'])}/an.\n")

    # --- Ouverture du coffre-fort ---
    final = lignes[0][1]
    r = cands[final]["rend"]
    t = moteur.trades(cands[final]["px"], cands[final]["signal"], debut=COFFRE)
    s_coffre = moteur.stats(r, debut=COFFRE)
    out += [f"## Coffre-fort {COFFRE} → aujourd'hui (ouvert une seule fois)\n",
            f"Structure finale choisie avec les données ≤ 2024 : **{final}**\n",
            "| | Rendement | Par an | Pire baisse | Sharpe |", "|---|---|---|---|---|",
            f"| **Aladdin** | {pct(s_coffre['rendement'])} | {pct(s_coffre['par_an'])} | {pct(s_coffre['pire_baisse'])} | {s_coffre['sharpe']:.2f} |"]
    for nom in ("BTC", "OR", "ACTIONS", "OBLIGATIONS"):
        b = px[nom].loc[COFFRE:].pct_change().fillna(0)
        sb = moteur.stats(b)
        out.append(f"| Garder {nom} | {pct(sb['rendement'])} | {pct(sb['par_an'])} | {pct(sb['pire_baisse'])} | {sb['sharpe']:.2f} |")
    cols = UNIVERS["multi-actifs"]
    panier = px[cols].loc[COFFRE:].pct_change().fillna(0).mean(axis=1)
    sp = moteur.stats(panier)
    out.append(f"| Panier égal des 8 actifs (rééquilibré chaque jour) | {pct(sp['rendement'])} | {pct(sp['par_an'])} | {pct(sp['pire_baisse'])} | {sp['sharpe']:.2f} |")
    out.append(f"\nTrades d'Aladdin dans le coffre : {len(t)}, gagnants {((t.rendement > 0).mean() * 100 if len(t) else 0):.0f} %.")

    (ICI / "resultats").mkdir(exist_ok=True)
    (ICI / "resultats" / "aladdin_rapport.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (ICI / "resultats" / "aladdin_structure.txt").write_text(final + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
