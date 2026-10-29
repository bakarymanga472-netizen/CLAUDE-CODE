"""Aladdin — recherche de structures à ≥ 60 % de trades gagnants ET rentables.

Entrées testées (toujours dans une tendance haussière, cours > MM200) :
  - rebond RSI-2 sous un seuil (achat d'une baisse courte)
  - plus bas de N jours (achat d'un repli)
Sorties testées :
  - dès que le cours repasse au-dessus de sa MM5 (sortie rapide)
  - objectif de gain fixe, avec durée max et stop éventuel
Exécution prudente : signal à la clôture de t → entrée à la clôture de t+1 ; sortie à la clôture qui suit le déclenchement.
Frais aller-retour inclus. Sélection sur ≤ 2024, vérification sur 2025 → aujourd'hui.

Usage : python3 -m aladdin.reussite
"""
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from . import desks, donnees
from .donnees import FRAIS, type_actif

ICI = Path(__file__).resolve().parent.parent
FIN_SELECTION = "2024-12-31"
VERIF = "2025-01-01"
PORTEFEUILLES = {
    "actions+or": ["ACTIONS", "OR"],
    "actions": ["ACTIONS"],
    "or": ["OR"],
    "crypto": ["BTC", "ETH", "BNB", "SOL", "XRP"],
    "multi-actifs": ["BTC", "ETH", "BNB", "SOL", "XRP", "ACTIONS", "OR", "OBLIGATIONS"],
}


def simuler(c, entree, sortie_mm5, tp, sl, duree, frais):
    """Simule un actif. Renvoie (rendements quotidiens de la position, liste des rendements par trade)."""
    n = len(c)
    pos = np.zeros(n)
    trades = []
    i = 0
    mm5 = pd.Series(c).rolling(5).mean().values
    while i < n - 2:
        if not entree[i]:
            i += 1
            continue
        e = i + 1                               # entrée à la clôture suivante
        px_e = c[e]
        j = e
        while j < n - 1:
            j += 1
            g = c[j] / px_e - 1
            fin = (j - e) >= duree
            if sortie_mm5 and c[j] > mm5[j]:
                fin = True
            if tp and g >= tp:
                fin = True
            if sl and g <= -sl:
                fin = True
            if fin:
                break
        s = min(j + 1, n - 1)                   # sortie à la clôture suivante
        pos[e + 1:s + 1] = 1.0                  # porte le rendement de e+1 à s
        trades.append((e, s, c[s] / px_e * (1 - 2 * frais) - 1))
        i = s
    return pos, trades


def portefeuille(px, cols, regle):
    """Capital réparti à parts égales entre les actifs disponibles ; chaque actif trade sa part."""
    rends, tous = [], []
    for a in cols:
        c = px[a].dropna()
        if len(c) < 400:
            continue
        frais = FRAIS[type_actif(a)]
        r = c.pct_change().fillna(0).values
        sma200 = c.rolling(200).mean().values
        if regle["entree"] == "rsi2":
            sig = (desks.rsi(c.to_frame(), 2).iloc[:, 0].values < regle["seuil"]) & (c.values > sma200)
        else:
            sig = (c.values <= c.rolling(regle["seuil"]).min().values) & (c.values > sma200)
        pos, tr = simuler(c.values, sig, regle["mm5"], regle["tp"], regle["sl"], regle["duree"], frais)
        couts = np.zeros(len(c))
        for e, _s, _ in tr:
            couts[min(e + 1, len(c) - 1)] += 2 * frais   # frais comptés au premier jour porté
        rends.append(pd.Series(pos * r - couts, index=c.index, name=a))
        tous += [(c.index[e], x, a, c.index[s]) for e, s, x in tr]
    if not rends:
        return None, None
    df = pd.concat(rends, axis=1).reindex(px.index)
    dispo = df.notna().sum(axis=1).replace(0, np.nan)
    port = (df.fillna(0).sum(axis=1) / dispo).fillna(0)
    return port, pd.DataFrame(tous, columns=["date", "rendement", "actif", "sortie"])


def bilan(port, trades, debut, fin):
    r = port.loc[debut:fin]
    r = r[r.index >= r.ne(0).idxmax()] if r.ne(0).any() else r
    t = trades[(trades.date >= pd.Timestamp(debut or "1900")) & (trades.date <= pd.Timestamp(fin or "2100"))]
    if len(t) == 0 or len(r) < 30:
        return None
    courbe = (1 + r).cumprod()
    ans = max((r.index[-1] - r.index[0]).days / 365.25, 0.1)
    gains, pertes = t.rendement[t.rendement > 0].sum(), -t.rendement[t.rendement <= 0].sum()
    vol = r.std() * np.sqrt(365)
    return {"reussite": (t.rendement > 0).mean(), "trades": len(t), "gain_moyen": t.rendement[t.rendement > 0].mean(),
            "perte_moyenne": t.rendement[t.rendement <= 0].mean(), "profit_factor": gains / pertes if pertes else np.inf,
            "total": courbe.iloc[-1] - 1, "par_an": courbe.iloc[-1] ** (1 / ans) - 1,
            "pire_baisse": (courbe / courbe.cummax() - 1).min(), "sharpe": r.mean() * 365 / vol if vol else 0}


def regles():
    for seuil in (5, 10, 15):
        for mm5, tp, sl, duree in itertools.product((True, False), (None, 0.02, 0.04), (None, 0.08, 0.15), (5, 10, 20)):
            if not mm5 and tp is None:
                continue
            yield {"entree": "rsi2", "seuil": seuil, "mm5": mm5, "tp": tp, "sl": sl, "duree": duree}
    for n in (3, 5, 10):
        for mm5, tp, sl, duree in itertools.product((True, False), (None, 0.02, 0.04), (None, 0.08, 0.15), (5, 10, 20)):
            if not mm5 and tp is None:
                continue
            yield {"entree": "plus_bas", "seuil": n, "mm5": mm5, "tp": tp, "sl": sl, "duree": duree}


def nom(r):
    e = f"RSI2<{r['seuil']}" if r["entree"] == "rsi2" else f"plus bas {r['seuil']} j"
    s = []
    if r["mm5"]:
        s.append("sortie > MM5")
    if r["tp"]:
        s.append(f"objectif +{r['tp'] * 100:.0f} %")
    s.append(f"stop -{r['sl'] * 100:.0f} %" if r["sl"] else "sans stop")
    s.append(f"max {r['duree']} j")
    return f"{e} · " + ", ".join(s)


def annees_positives(port, fin):
    """Rendement de chaque année civile ≤ fin, en ignorant les années sans activité."""
    r = port.loc[:fin]
    r = r[r.index >= r.ne(0).idxmax()] if r.ne(0).any() else r
    an = (1 + r).groupby(r.index.year).prod() - 1
    return an[an != 0]


CRITERES = {
    "meilleur Sharpe": lambda l, fin: l["bilans"][fin]["sharpe"],
    "le plus régulier (pire année la moins mauvaise, ≥ 6 ans d'historique)":
        lambda l, fin: annees_positives(l["port"], fin).min() if len(annees_positives(l["port"], fin)) >= 6 else -np.inf,
}


def eligibles(lignes, fin):
    return [l for l in lignes if l["bilans"][fin] and l["bilans"][fin]["reussite"] >= 0.60
            and l["bilans"][fin]["trades"] >= 60 and l["bilans"][fin]["profit_factor"] >= 1.3
            and l["bilans"][fin]["par_an"] > 0]


def pct(x):
    return f"{x * 100:+.1f} %" if pd.notna(x) else "—"


def main():
    px = donnees.prix()
    lignes = []
    for u, cols in PORTEFEUILLES.items():
        for r in regles():
            port, tr = portefeuille(px, cols, r)
            if port is None:
                continue
            lignes.append({"univers": u, "regle": nom(r), "port": port, "trades": tr,
                           "bilans": {"2019-12-31": bilan(port, tr, None, "2019-12-31"),
                                      FIN_SELECTION: bilan(port, tr, None, FIN_SELECTION)},
                           "val": bilan(port, tr, "2020-01-01", FIN_SELECTION),
                           "apres": bilan(port, tr, VERIF, None)})
    out = ["# Aladdin — structures à 60 % de réussite ou plus\n",
           f"{len(lignes)} combinaisons testées (entrées sur repli, sorties rapides, objectifs, stops, 5 univers). "
           "Une structure est éligible si, sur la période de sélection : réussite ≥ 60 %, ≥ 60 trades, "
           "profit factor ≥ 1,3, rendement positif.\n",
           "## Étape 1 — tester la MÉTHODE de choix sur le passé (choix ≤ 2019, vérification 2020-2024)\n",
           "| Méthode | Structure choisie avec ≤ 2019 | Réussite 2020-2024 | Rendement/an 2020-2024 | Pire baisse 2020-2024 |",
           "|---|---|---|---|---|"]
    score_methode = {}
    for nom_c, f in CRITERES.items():
        el = eligibles(lignes, "2019-12-31")
        best = max(el, key=lambda l: f(l, "2019-12-31"))
        v = best["val"]
        score_methode[nom_c] = v["sharpe"] if v else -np.inf
        out.append(f"| {nom_c} | {best['univers']} — {best['regle']} | {v['reussite'] * 100:.0f} % | {pct(v['par_an'])} | {pct(v['pire_baisse'])} |")
    methode = max(score_methode, key=score_methode.get)
    out.append(f"\nMéthode retenue (meilleure sur 2020-2024) : **{methode}**.\n")

    el = eligibles(lignes, FIN_SELECTION)
    el.sort(key=lambda l: -CRITERES[methode](l, FIN_SELECTION))
    out += ["## Étape 2 — la méthode retenue choisit avec ≤ 2024 (top 8)\n",
            "| # | Univers | Règle | Réussite ≤2024 | Par an ≤2024 | Pire baisse ≤2024 | Pire année ≤2024 |",
            "|---|---|---|---|---|---|---|"]
    for i, l in enumerate(el[:8], 1):
        a = l["bilans"][FIN_SELECTION]
        out.append(f"| {i} | {l['univers']} | {l['regle']} | {a['reussite'] * 100:.0f} % | {pct(a['par_an'])} | "
                   f"{pct(a['pire_baisse'])} | {pct(annees_positives(l['port'], FIN_SELECTION).min())} |")
    best = el[0]
    a, b = best["bilans"][FIN_SELECTION], best["apres"]
    out += [f"\n## Étape 3 — vérification 2025 → aujourd'hui : {best['univers']} — {best['regle']}\n",
            "| | ≤ 2024 | 2025 → aujourd'hui |", "|---|---|---|",
            f"| **Trades gagnants** | **{a['reussite'] * 100:.0f} %** | **{b['reussite'] * 100:.0f} %** |",
            f"| Nombre de trades | {a['trades']} | {b['trades']} |",
            f"| Gain moyen / perte moyenne par trade | {pct(a['gain_moyen'])} / {pct(a['perte_moyenne'])} | {pct(b['gain_moyen'])} / {pct(b['perte_moyenne'])} |",
            f"| Rendement | {pct(a['par_an'])}/an | {pct(b['total'])} au total ({pct(b['par_an'])}/an) |",
            f"| Pire baisse | {pct(a['pire_baisse'])} | {pct(b['pire_baisse'])} |"]
    for nom_b, cols in (("Garder actions (SPY)", ["ACTIONS"]), ("Garder or", ["OR"]), ("Garder BTC", ["BTC"])):
        c = px[cols[0]].loc[VERIF:].dropna()
        out.append(f"\nRéférence 2025 → aujourd'hui, {nom_b} : {pct(c.iloc[-1] / c.iloc[0] - 1)}")
    best["trades"].to_csv(ICI / "resultats" / "aladdin_reussite_trades.csv", index=False)
    (ICI / "resultats" / "aladdin_reussite_structure.txt").write_text(f"{best['univers']} | {best['regle']}\n")
    (ICI / "resultats").mkdir(exist_ok=True)
    (ICI / "resultats" / "aladdin_reussite.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
