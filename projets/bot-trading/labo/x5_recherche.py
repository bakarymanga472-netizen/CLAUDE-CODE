"""Recherche massive à levier ×5 imposé (demande du 2026-10-21) — tour 14.

Règles FIXÉES AVANT EXÉCUTION :
- Bases (≈ 140) : les 15 moteurs de labo/fusion.py ; C3, Équilibrée (75/25), Prudente (50/50), fusions F-EG/F-IV ;
  toutes les paires et tous les triplets à parts égales (rééquilibrage mensuel) parmi 9 moteurs « actions/tendance » :
  M1 bot, M2 rotation, M3 QQQ×2, M5 tendance, M6 D1F1, M10 parité de risque, M11 or, M13 MM50/200, M14 secteurs.
- Levier ×5 (financement 5 %/an sur la part empruntée, perte journalière plafonnée à -100 %), 3 modes :
  NU (×5 permanent), D20 et D30 (disjoncteur : ×1 si baisse > 20 % / 30 % depuis le plus haut, retour à ×5 au plus haut).
- Deux lectures :
  A. « Meilleure sur tout l'historique » (2008-2026) — RÉSULTAT REGARDÉ APRÈS COUP, montré pour information seulement ;
  B. « Sélection en marche » : chaque 1er janvier (2011 → 2026), on choisit la combinaison au meilleur Calmar sur les
     3 années précédentes (simulée à ×5, départ à neuf), puis on la garde toute l'année (départ à neuf). C'est le
     résultat qu'un utilisateur aurait réellement obtenu, sans connaître le futur.
Usage : python3 -m labo.x5_recherche → rapports/x5_recherche.md
"""
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .combo3 import melange
from .fusion import fusion_iv, moteurs
from .strategie_finale import selection

ICI = Path(__file__).resolve().parent.parent
POOL = ["M1 bot haute réussite", "M2 rotation top 3", "M3 QQQ ×2 > MM200", "M5 tendance (crypto/SPY/GLD/TLT)", "M6 D1F1 ×2",
        "M10 parité de risque", "M11 tendance or", "M13 SPY MM50 > MM200", "M14 rotation sectorielle"]
FIN = 0.05 / 252


def x5(b, mode):
    b = np.asarray(b)
    out = np.empty(len(b))
    v = pic = 1.0
    L = 5.0
    seuil = {"NU": None, "D20": -0.20, "D30": -0.30}[mode]
    for i, r in enumerate(b):
        x = max(L * r - (L - 1) * FIN, -1.0)
        out[i] = x
        v *= 1 + x
        pic = max(pic, v)
        if seuil is not None:
            if v / pic - 1 < seuil:
                L = 1.0
            elif v >= pic * 0.9999:
                L = 5.0
        if v <= 1e-6:
            out[i + 1:] = 0.0
            break
    return out


def st(x):
    v = np.cumprod(1 + x)
    an = max(len(x) / 252, 0.1)
    cagr = v[-1] ** (1 / an) - 1 if v[-1] > 0 else -1.0
    dd = (v / np.maximum.accumulate(v) - 1).min()
    return cagr, dd, (cagr / abs(dd) if dd < 0 else cagr * 100), v[-1]


def bases():
    M, spy = moteurs()
    garde, _ = selection(M)
    stable = fusion_iv({k: M[k] for k in garde})
    c3 = melange([M[POOL[0]], M[POOL[1]], M[POOL[2]]], [1 / 3] * 3)
    B = {k: v for k, v in M.items()}
    B.update({"C3": c3, "Équilibrée": melange([c3, stable], [0.75, 0.25]), "Prudente": melange([c3, stable], [0.5, 0.5]),
              "F-EG 15": melange(list(M.values()), [1 / len(M)] * len(M)), "F-IV sélection": stable})
    for n in (2, 3):
        for combo in combinations(POOL, n):
            B[" + ".join(k.split(" ")[0] for k in combo)] = melange([M[k] for k in combo], [1 / n] * n)
    idx = spy.loc["2008-01-01":].index
    return {k: v.reindex(idx).fillna(0.0) for k, v in B.items()}, spy.reindex(idx).fillna(0.0)


def main():
    B, spy = bases()
    idx = spy.index
    cand = [(b, m) for b in B for m in ("NU", "D20", "D30")]
    # A. après coup
    full = {(b, m): st(x5(B[b].values, m)) for b, m in cand}
    top = sorted(full, key=lambda k: -full[k][3])[:10]
    # B. sélection en marche
    ans = sorted(set(idx.year))
    lignes, realise = [], []
    for Y in [a for a in ans if a >= 2011]:
        fen = (idx.year >= Y - 3) & (idx.year <= Y - 1)
        sc = {k: st(x5(B[k[0]].values[fen], k[1])) for k in cand}
        choix = max(sc, key=lambda k: sc[k][2])
        dans = idx.year == Y
        r = x5(B[choix[0]].values[dans], choix[1])
        realise.append(pd.Series(r, index=idx[dans]))
        c, d, _, f = st(r)
        lignes.append((Y, choix, f - 1, d, (1 + spy[dans]).prod() - 1))
    wf = pd.concat(realise)
    c, d, cal, f = st(wf.values)
    s5 = wf.loc[str(idx[-1] - pd.DateOffset(years=5))[:10]:]
    c5, d5, _, f5 = st(s5.values)
    spyc, spyd, _, spyf = st(spy.loc["2011":].values)
    T = [f"# Recherche ×5 : {len(B)} bases × 3 modes = {len(cand)} stratégies (données jusqu'au {idx[-1].date()})\n",
         "Commande : `python3 -m labo.x5_recherche` · règles : en-tête du fichier.\n",
         "## A. Les 10 meilleures sur 2008-2026, choisies APRÈS COUP (information seulement, non reproductible)\n",
         "| Stratégie | Mode | Rendement/an | Pire baisse | 20 000 € en 2008 → 2026 |", "|---|---|---|---|---|"]
    for k in top:
        cg, dg, _, fg = full[k]
        T.append(f"| {k[0]} | {k[1]} | {cg:+.1%} | {dg:.0%} | {20000 * fg:,.0f} € |")
    T += ["\n## B. Sélection en marche (ce que tu aurais vraiment obtenu)\n",
          "| Année | Stratégie choisie au 1er janvier (3 ans précédents) | Mode | Résultat ×5 | Pire baisse | SPY |", "|---|---|---|---|---|---|"]
    for Y, ch, rr, dd, sp in lignes:
        T.append(f"| {Y} | {ch[0]} | {ch[1]} | {rr:+.1%} | {dd:.0%} | {sp:+.1%} |")
    T += [f"\n**2011 → {idx[-1].date()}** : {c:+.1%}/an, pire baisse {d:.0%}, 20 000 € → {20000 * f:,.0f} € "
          f"(SPY gardé : {spyc:+.1%}/an, {spyd:.0%}, {20000 * spyf:,.0f} €).",
          f"**5 dernières années** : {c5:+.1%}/an, pire baisse {d5:.0%}, 20 000 € → {20000 * f5:,.0f} €."]
    (ICI / "rapports" / "x5_recherche.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T))


if __name__ == "__main__":
    main()
