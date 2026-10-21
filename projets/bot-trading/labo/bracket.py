"""Moteur « ordre avec stop et objectif » (bracket), pour les stratégies à prise de profit fixe (vidéos YouTube).

Chronologie, sans regard vers le futur :
- le signal est décidé à la CLÔTURE de la barre t (données ≤ t) ;
- entrée à l'OUVERTURE de t+1 ; risque = |entrée − stop| ; objectif = entrée ± k × risque ;
- à partir de la barre d'entrée, on regarde plus haut/plus bas : si le stop ET l'objectif sont touchés dans la même barre,
  on suppose le STOP d'abord (prudent) ; si une barre ouvre au-delà du stop, sortie à l'ouverture (glissement réel) ;
- seuil de break-even optionnel (le stop passe au prix d'entrée à partir de la barre SUIVANTE) ;
- une seule position à la fois par instrument ;
- coût aller-retour (spread + commission + glissement) en unités de prix, retiré du résultat.
Résultats en R (multiples du risque initial) : indépendants de la taille de position.
"""
import numpy as np
import pandas as pd


def executer(df, signaux, cout_prix, be_R=None, barres_max=None):
    """signaux : DataFrame indexé comme df (barres de décision) avec colonnes sens (+1/−1), stop, tp_R."""
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    pos = {t: i for i, t in enumerate(df.index)}
    cout = cout_prix if np.ndim(cout_prix) else np.full(len(df), cout_prix)
    lignes, libre_a = [], 0
    for t, s in signaux.sort_index().iterrows():
        i = pos[t] + 1                                    # barre d'entrée
        if i >= len(df) or i < libre_a:
            continue
        sens, entree = int(s.sens), o[i]
        risque = (entree - s.stop) * sens
        if not np.isfinite(risque) or risque <= 0:        # le prix a déjà dépassé le stop à l'ouverture
            continue
        stop, tp = s.stop, entree + sens * s.tp_R * risque
        be_actif, sortie, motif, j = False, None, None, i
        while j < len(df):
            if sens * (o[j] - stop) <= 0 and j > i:       # ouverture au-delà du stop (trou)
                sortie, motif = o[j], "stop (trou)"
                break
            if sens * (l[j] - stop) <= 0 if sens > 0 else sens * (h[j] - stop) <= 0:
                sortie, motif = stop, "stop" if not be_actif else "break-even"
                break
            if (h[j] >= tp) if sens > 0 else (l[j] <= tp):
                sortie, motif = (max(tp, o[j]) if sens > 0 else min(tp, o[j])) if j > i else tp, "objectif"
                break
            if barres_max and j - i + 1 >= barres_max:
                sortie, motif = c[j], "durée"
                break
            if be_R and not be_actif and ((h[j] - entree) * sens >= be_R * risque if sens > 0 else (entree - l[j]) >= be_R * risque):
                be_actif, stop = True, entree
            j += 1
        if sortie is None:
            break                                          # trade ouvert à la fin des données : non compté
        brut = (sortie - entree) * sens
        lignes.append({"decision": t, "entree_t": df.index[i], "sortie_t": df.index[j], "sens": sens, "entree": entree,
                       "stop": s.stop, "objectif": tp, "risque": risque, "sortie": sortie, "motif": motif,
                       "R_brut": brut / risque, "R": (brut - cout[i]) / risque, "risque_pct": risque / entree})
        libre_a = j + 1
    return pd.DataFrame(lignes)


def mesures(t, risque_par_trade=0.01):
    """Mesures en R ; courbe de capital avec un risque fixe de 1 % du capital par trade."""
    if len(t) == 0:
        return {"trades": 0}
    r = t.R.values
    eq = np.cumprod(1 + risque_par_trade * r)
    g, p = r[r > 0].sum(), -r[r <= 0].sum()
    return {"trades": int(len(r)), "reussite": float((r > 0).mean()), "R_moyen": float(r.mean()),
            "R_moyen_brut": float(t.R_brut.mean()), "profit_factor": float(g / p) if p > 0 else float("inf"),
            "gain_moyen_R": float(r[r > 0].mean()) if (r > 0).any() else 0.0,
            "perte_moyenne_R": float(r[r <= 0].mean()) if (r <= 0).any() else 0.0,
            "rendement_1pct": float(eq[-1] - 1), "pire_baisse_1pct": float((eq / np.maximum.accumulate(eq) - 1).min()),
            "pertes_consecutives_max": int(max((len(x) for x in "".join("P" if v <= 0 else "G" for v in r).split("G")), default=0)),
            "cout_moyen_R": float((t.R_brut - t.R).mean())}


def hasard(df, signaux, cout_prix, graine, **k):
    """Mêmes barres de décision, même sens et même distance de stop, mais décalées au hasard dans le temps :
    mesure ce que donnerait la même gestion (stop/objectif) avec des entrées sans information."""
    rng = np.random.default_rng(graine)
    if len(signaux) == 0:
        return pd.DataFrame()
    dist = (df.close.reindex(signaux.index) - signaux.stop).abs().values / df.close.reindex(signaux.index).values
    idx = np.sort(rng.choice(np.arange(200, len(df) - 2), size=len(signaux), replace=False))
    sens = rng.choice([-1, 1], size=len(signaux)) if (signaux.sens < 0).any() else np.ones(len(signaux))
    rng.shuffle(dist)
    t = df.index[idx]
    c = df.close.values[idx]
    faux = pd.DataFrame({"sens": sens, "stop": c * (1 - sens * dist), "tp_R": signaux.tp_R.values[:len(idx)]}, index=t)
    return executer(df, faux, cout_prix, **k)
