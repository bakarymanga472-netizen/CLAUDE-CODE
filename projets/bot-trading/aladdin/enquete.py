"""Aladdin — comité d'enquête : autopsie de chaque trade perdant, puis recherche de corrections validées.

1. Pour chaque trade perdant, on mesure le contexte à l'entrée et ce qui s'est passé pendant le trade,
   et on lui attribue une cause probable (ou « bruit » si aucune cause mesurable).
2. Boucle de correction : on cherche le filtre d'entrée qui aurait évité le plus de pertes sur 2008-2019.
   Il n'est GARDÉ que s'il améliore aussi 2020-2024 (années qu'il n'a pas vues). On recommence avec le
   filtre suivant, jusqu'à ce qu'aucun filtre ne passe ce test.
3. Résultat final vérifié sur 2025 → aujourd'hui.

Usage : python3 -m aladdin.enquete
"""
from pathlib import Path

import numpy as np
import pandas as pd

from . import desks, donnees
from .donnees import FRAIS, type_actif
from .reussite import simuler

ICI = Path(__file__).resolve().parent.parent
STRUCTURES = {
    "Rebond (actions + or)": {"actifs": ["ACTIONS", "OR"],
                              "regle": {"entree": "rsi2", "seuil": 15, "mm5": False, "tp": 0.04, "sl": 0.08, "duree": 20}},
    "Momentum crypto (Aladdin v1)": {"actifs": ["BTC", "ETH", "BNB", "SOL", "XRP"], "regle": "momentum"},
}
APPRENTISSAGE, VALIDATION, VERIF = ("2006-01-01", "2019-12-31"), ("2020-01-01", "2024-12-31"), ("2025-01-01", None)
NOMS = {"vol_rang": "volatilité (rang sur 3 ans)", "dist200": "écart à la MM200", "ret20": "rendement 20 j",
        "dd52": "écart au plus haut 1 an", "pente50": "pente de la MM50", "rsi2": "RSI-2", "ret5": "rendement 5 j"}


def contexte(c):
    """Indicateurs connus à la clôture de chaque jour."""
    r = c.pct_change()
    vol = r.rolling(20).std() * np.sqrt(252)
    m50, m200 = c.rolling(50).mean(), c.rolling(200).mean()
    return pd.DataFrame({
        "vol_rang": vol.rolling(756, min_periods=250).rank(pct=True),
        "dist200": c / m200 - 1,
        "ret20": c.pct_change(20),
        "ret5": c.pct_change(5),
        "dd52": c / c.rolling(252).max() - 1,
        "pente50": m50 / m50.shift(20) - 1,
        "rsi2": desks.rsi(c.to_frame(), 2).iloc[:, 0],
        "vol_j": r.rolling(20).std(),
        "m200": m200,
    })


def signal(c, ctx, regle):
    if regle == "momentum":
        return (c / c.shift(120) - 1 > 0).values
    return ((ctx["rsi2"] < regle["seuil"]) & (c > ctx["m200"])).values


def simuler_momentum(c, sig, frais):
    """Momentum : en position tant que le signal est vrai (entrée/sortie à la clôture suivante)."""
    trades, n, i = [], len(c), 0
    while i < n - 2:
        if not sig[i]:
            i += 1
            continue
        e = i + 1
        j = e
        while j < n - 1 and sig[j]:
            j += 1
        s = min(j + 1, n - 1)
        trades.append((e, s, c[s] / c[e] * (1 - 2 * frais) - 1))
        i = s
    return trades


def executer(px, structure, filtres=()):
    lignes = []
    for a in structure["actifs"]:
        c = px[a].dropna()
        if type_actif(a) == "autre":                          # retire les week-ends reportés
            c = c[c.diff().ne(0) | (c.index == c.index[0])]
        ctx = contexte(c)
        sig = signal(c, ctx, structure["regle"])
        for f, op, seuil in filtres:
            v = ctx[f].values
            sig = sig & ~np.isnan(v) & ((v >= seuil) if op == ">=" else (v <= seuil))
        frais = FRAIS[type_actif(a)]
        if structure["regle"] == "momentum":
            tr = simuler_momentum(c.values, sig, frais)
        else:
            r = structure["regle"]
            _, tr = simuler(c.values, sig, r["mm5"], r["tp"], r["sl"], r["duree"], frais)
        for e, s, x in tr:
            k = max(e - 1, 0)                                   # jour du signal
            seg = c.iloc[e:s + 1]
            choc = (seg.pct_change() / ctx["vol_j"].iloc[k]).min() if s > e else 0
            lignes.append({"actif": a, "entree": c.index[e], "sortie": c.index[s], "rendement": x,
                           **{f: ctx[f].iloc[k] for f in NOMS},
                           "sous_mm200": bool((seg < ctx["m200"].iloc[e:s + 1]).any()),
                           "choc_sigma": choc, "pire_pendant": seg.min() / seg.iloc[0] - 1})
    return pd.DataFrame(lignes)


def periode(t, p):
    d, f = p
    return t[(t.entree >= pd.Timestamp(d)) & (t.entree <= pd.Timestamp(f or "2100"))]


def note(t):
    if len(t) == 0:
        return {"n": 0, "reussite": np.nan, "pf": np.nan, "somme": 0.0}
    g, p = t.rendement[t.rendement > 0].sum(), -t.rendement[t.rendement <= 0].sum()
    return {"n": len(t), "reussite": (t.rendement > 0).mean(), "pf": g / p if p else np.inf,
            "somme": np.log1p(t.rendement).sum()}


def cause(row, seuils):
    if row["choc_sigma"] <= -3:
        return "choc soudain (une journée à plus de 3 écarts-types)"
    if row["sous_mm200"]:
        return "la tendance de fond s'est cassée pendant le trade"
    if row["vol_rang"] >= 0.8:
        return "entrée en période de volatilité extrême"
    if row["dd52"] <= seuils["dd52"]:
        return "acheté un marché déjà en forte chute (couteau qui tombe)"
    if row["pente50"] <= seuils["pente50"]:
        return "tendance moyen terme en train de s'essouffler"
    return "bruit : aucune cause mesurable"


def boucle(px, structure, out):
    filtres, base = [], executer(px, structure)
    tour = 0
    while True:
        tour += 1
        app = periode(base, APPRENTISSAGE)
        if structure["regle"] == "momentum":
            app = periode(base, ("2020-01-01", "2022-12-31"))
        n0, v0 = note(app), note(periode(base, VALIDATION if structure["regle"] != "momentum" else ("2023-01-01", "2024-12-31")))
        meilleur = None
        for f in NOMS:
            vals = app[f].dropna()
            if len(vals) < 30:
                continue
            for q in (0.1, 0.2, 0.3, 0.7, 0.8, 0.9):
                seuil = vals.quantile(q)
                op = ">=" if q < 0.5 else "<="
                garde = app[(app[f] >= seuil) if op == ">=" else (app[f] <= seuil)]
                n1 = note(garde)
                if n1["n"] < 0.6 * n0["n"] or n1["somme"] < 0.9 * n0["somme"]:
                    continue                                    # ne pas sacrifier le rendement
                gain = n1["reussite"] - n0["reussite"]
                if gain > 0.02 and (meilleur is None or gain > meilleur[0]):
                    meilleur = (gain, f, op, seuil)
        if meilleur is None:
            out.append(f"- Tour {tour} : aucun nouveau filtre n'améliore l'apprentissage sans sacrifier le rendement → **arrêt**.")
            break
        _, f, op, seuil = meilleur
        essai = executer(px, structure, filtres + [(f, op, seuil)])
        per_v = VALIDATION if structure["regle"] != "momentum" else ("2023-01-01", "2024-12-31")
        v1 = note(periode(essai, per_v))
        accepte = v1["reussite"] > v0["reussite"] and v1["somme"] >= 0.9 * v0["somme"]
        out.append(f"- Tour {tour} : filtre « {NOMS[f]} {op} {seuil:.3f} » → validation : réussite "
                   f"{v0['reussite'] * 100:.0f} % → {v1['reussite'] * 100:.0f} %, rendement cumulé "
                   f"{v0['somme'] * 100:+.0f} % → {v1['somme'] * 100:+.0f} % → **{'GARDÉ' if accepte else 'REJETÉ (ne tient pas sur des années non vues)'}**")
        if not accepte:
            break
        filtres.append((f, op, seuil))
        base = essai
    return filtres, base


def main():
    px = donnees.prix()
    out = ["# Aladdin — comité d'enquête sur les trades perdants\n"]
    for nom_s, structure in STRUCTURES.items():
        t = executer(px, structure)
        pertes = t[t.rendement <= 0].copy()
        seuils = {"dd52": t.dd52.quantile(0.2), "pente50": t.pente50.quantile(0.2)}
        pertes["cause"] = pertes.apply(lambda r: cause(r, seuils), axis=1)
        out += [f"\n## {nom_s}\n",
                f"{len(t)} trades, {len(pertes)} perdants ({len(pertes) / len(t) * 100:.0f} %). Causes trouvées :\n",
                "| Cause probable | Trades perdants | Part | Perte moyenne |", "|---|---|---|---|"]
        for c_, g in pertes.groupby("cause"):
            out.append(f"| {c_} | {len(g)} | {len(g) / len(pertes) * 100:.0f} % | {g.rendement.mean() * 100:+.1f} % |")
        out.append("\n**Comparaison gagnants / perdants au moment de l'entrée** (médianes) :\n")
        out += ["| Indicateur | Gagnants | Perdants |", "|---|---|---|"]
        for f in NOMS:
            out.append(f"| {NOMS[f]} | {t[t.rendement > 0][f].median():.3f} | {pertes[f].median():.3f} |")
        out.append("\n**Boucle de correction** (gardé seulement si ça marche aussi sur des années non vues) :\n")
        filtres, finale = boucle(px, structure, out)
        avant = note(periode(t, VERIF))
        apres = note(periode(finale, VERIF))
        out += [f"\nFiltres retenus : {', '.join(f'{NOMS[f]} {op} {s:.3f}' for f, op, s in filtres) or 'aucun'}\n",
                "| 2025 → aujourd'hui | Trades | Réussite | Profit factor | Rendement cumulé des trades |", "|---|---|---|---|---|",
                f"| Avant enquête | {avant['n']} | {avant['reussite'] * 100:.0f} % | {avant['pf']:.2f} | {avant['somme'] * 100:+.0f} % |",
                f"| Après enquête | {apres['n']} | {apres['reussite'] * 100:.0f} % | {apres['pf']:.2f} | {apres['somme'] * 100:+.0f} % |"]
        pertes.to_csv(ICI / "resultats" / f"enquete_{nom_s.split()[0].lower()}_pertes.csv", index=False)
    (ICI / "resultats" / "aladdin_enquete.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
