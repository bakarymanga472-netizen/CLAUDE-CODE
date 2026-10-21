"""Analyste post-trade : diagnostic en 4 catégories, analyse des pertes et des gains, bilan périodique.

Niveaux de preuve : « cause confirmée » (constat direct dans les enregistrements), « cause probable » (indice chiffré
mais pas de preuve directe), « cause inconnue » (rien de mesurable). L'analyste ne modifie JAMAIS une stratégie :
il propose au plus une hypothèse testable, qui part dans le registre des hypothèses.
"""
from math import comb

import numpy as np

from . import prevention

SEUIL_GLISSEMENT_CONFIRME = 3.0   # × le glissement attendu
SEUIL_GLISSEMENT_PROBABLE = 1.5
K_COMPARABLES = 20
N_MIN_RECURRENCE = 20


def confiance(n):
    return "faible" if n < 20 else ("moyenne" if n < 100 else "élevée")


def binom_sup(k, n, p):
    """P(X ≥ k) pour X ~ Binomiale(n, p)."""
    return float(sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1)))


def _cat(constats):
    if not constats:
        return {"statut": "aucune anomalie détectée", "niveau": None, "constats": []}
    niveau = "cause confirmée" if any(c[0] == "confirmée" for c in constats) else "cause probable"
    return {"statut": "anomalie", "niveau": niveau, "constats": [f"[{c[0]}] {c[1]}" for c in constats]}


def diagnostiquer(t):
    d, p, x, res = t["donnees_entree"], t["plan"], t["execution"], t["resultat"]
    # 1. Données
    c1 = []
    motif = prevention.donnees_fraiches(d)
    if motif:
        c1.append(("confirmée", motif))
    ref = d.get("valeurs", {}).get("cloture")
    if ref and x.get("prix_entree") and abs(x["prix_entree"] / ref - 1) > 0.05:
        c1.append(("probable", f"prix d'entrée à {abs(x['prix_entree'] / ref - 1):.1%} de la dernière clôture connue"))
    # 2. Exécution
    c2 = []
    rejets = [o["id"] for o in x.get("ordres", []) if o.get("statut") == "rejete"]
    if rejets:
        c2.append(("confirmée", f"ordre(s) rejeté(s) : {rejets}"))
    ids = [o["id"] for o in x.get("ordres", [])]
    if len(ids) != len(set(ids)):
        c2.append(("confirmée", "ordre en double"))
    attendu = p.get("cout_prevu", {}).get("glissement")
    if attendu and res.get("glissement") is not None:
        ratio = res["glissement"] / attendu
        if ratio > SEUIL_GLISSEMENT_CONFIRME:
            c2.append(("confirmée", f"glissement {ratio:.1f}× l'attendu"))
        elif ratio > SEUIL_GLISSEMENT_PROBABLE:
            c2.append(("probable", f"glissement {ratio:.1f}× l'attendu"))
    if p.get("stop") and x.get("prix_sortie") and p.get("sens", "long") == "long" \
            and x["prix_sortie"] < p["stop"] * 0.99 and x.get("motif_sortie") != "stop":
        c2.append(("probable", "sortie sous le stop sans motif « stop » : stop peut-être non respecté"))
    # 3. Processus
    c3 = []
    motif = prevention.regles_respectees(p.get("regles", []))
    if motif:
        c3.append(("confirmée", f"signal non conforme : {motif}"))
    motif = prevention.taille_conforme(x.get("taille", 0), p.get("taille_prevue"))
    if motif:
        c3.append(("confirmée", f"mauvaise taille : {motif}"))
    ignores = [f["nom"] for f in p.get("filtres", []) if not f.get("respecte", True)]
    if ignores:
        c3.append(("confirmée", f"filtre(s) ignoré(s) : {ignores}"))
    cats = {"donnees": _cat(c1), "execution": _cat(c2), "processus": _cat(c3)}
    # 4. Statistique
    conforme = all(cats[k]["statut"] != "anomalie" for k in cats)
    gagne = res["net"] > 0
    if conforme and not gagne:
        stat = "perte malgré une décision conforme : résultat statistique (cause inconnue au-delà du hasard)"
    elif conforme and gagne:
        stat = "gain avec une décision conforme"
    elif gagne:
        stat = "gain malgré une décision NON conforme : ne pas le compter comme une preuve de la règle"
    else:
        stat = "perte avec décision non conforme : la non-conformité est une cause possible, pas certaine"
    cats["statistique"] = {"conforme": conforme, "lecture": stat}
    return cats


def _vecteur(t, cles):
    return np.array([float(t["signaux"].get(k, np.nan)) for k in cles])


def comparables(t, historique, k=K_COMPARABLES):
    meme = [h for h in historique if h["strategie"] == t["strategie"] and h["instrument"] == t["instrument"]
            and h["id"] != t["id"]]
    cles = [c for c, v in t["signaux"].items() if isinstance(v, (int, float))]
    if not meme or not cles:
        return meme[:k]
    m = np.array([_vecteur(h, cles) for h in meme])
    sd = np.nanstd(m, axis=0)
    sd[sd == 0] = 1
    dist = np.sqrt(np.nansum(((m - _vecteur(t, cles)) / sd) ** 2, axis=1)) + np.array(
        [0 if h["regime"] == t["regime"] else 1.0 for h in meme])
    return [meme[i] for i in np.argsort(dist)[:k]]


def _position(r, reference_R):
    ref = np.asarray(reference_R)
    return float((ref <= r).mean()) if len(ref) else None


def analyser(t, diag, historique, reference_R):
    """Analyse commune perte/gain. reference_R : distribution des R attendue (backtest) pour cette version."""
    r, gagne = t["resultat"]["R"], t["resultat"]["net"] > 0
    comp = comparables(t, historique)
    n = len(comp)
    part_perdants = float(np.mean([h["resultat"]["net"] <= 0 for h in comp])) if n else None
    p0 = float(np.mean(np.asarray(reference_R) <= 0)) if len(reference_R) else None
    rang = _position(r, reference_R)
    out = {
        "plan_vs_execution": {
            "prix_prevu": t["plan"].get("prix_prevu"), "prix_entree": t["execution"].get("prix_entree"),
            "taille_prevue": t["plan"].get("taille_prevue"), "taille": t["execution"].get("taille"),
            "motif_sortie": t["execution"].get("motif_sortie"),
            "cout_prevu": t["plan"].get("cout_prevu"), "frais": t["resultat"].get("frais"),
            "glissement": t["resultat"].get("glissement")},
        "regles_respectees": diag["statistique"]["conforme"],
        "R": r, "rang_dans_distribution_attendue": rang,
        "comparables": {"n": n, "confiance": confiance(n), "part_perdants": part_perdants,
                        "R_moyen": float(np.mean([h["resultat"]["R"] for h in comp])) if n else None,
                        "ids": [h["id"] for h in comp[:5]]},
        "connu": [], "incertain": [], "a_collecter": [], "hypothese": None, "erreurs_prevention": [],
    }
    # Erreurs confirmées → règle de prévention testée
    for cat, regle in (("donnees", "PREV-DONNEES"), ("processus", "PREV-REGLES"), ("execution", "PREV-DOUBLON")):
        if diag[cat]["niveau"] == "cause confirmée":
            out["connu"].append(f"{cat} : {'; '.join(diag[cat]['constats'])}")
            texte = " ".join(diag[cat]["constats"])
            if cat == "processus" and "taille" in texte:
                regle = "PREV-TAILLE"
            elif cat == "execution":
                regle = "PREV-ORDRE" if "rejet" in texte else ("PREV-GLISSEMENT" if "glissement" in texte else "PREV-DOUBLON")
            out["erreurs_prevention"].append({"categorie": cat, "regle_prevention": regle,
                                              "constats": diag[cat]["constats"]})
        elif diag[cat]["niveau"] == "cause probable":
            out["incertain"].append(f"{cat} : {'; '.join(diag[cat]['constats'])}")
    if not gagne:
        if not diag["statistique"]["conforme"]:
            out["nature"] = "perte liée (au moins en partie) à un défaut de processus, d'exécution ou de données"
        elif rang is not None and rang < 0.01:
            out["nature"] = "perte extrême (sous le 1er centile attendu) : à examiner, pas forcément un défaut"
        else:
            out["nature"] = "perte normale : dans la distribution attendue de la stratégie"
    else:
        out["nature"] = ("gain conforme au modèle" if diag["statistique"]["conforme"]
                         else "gain malgré une décision non conforme — ne valide rien")
        meilleurs = {}
        for h in comp:
            meilleurs.setdefault(h["regime"], []).append(h["resultat"]["R"])
        out["R_moyen_par_regime_comparables"] = {k: (round(float(np.mean(v)), 2), len(v)) for k, v in meilleurs.items()}
        out["incertain"].append("un gain isolé n'est pas une preuve que la décision était bonne")
    # Récurrence
    if n >= N_MIN_RECURRENCE and p0 is not None and not gagne:
        k = int(round(part_perdants * n))
        pval = binom_sup(k, n, p0)
        out["recurrence"] = {"pertes_comparables": k, "n": n, "taux_attendu": p0, "p_valeur": pval}
        if pval < 0.05:
            out["hypothese"] = {
                "enonce": f"Les trades {t['strategie']} proches de ce contexte (régime {t['regime']}) perdent plus souvent "
                          f"qu'attendu ({k}/{n} contre {p0:.0%}).",
                "protocole": "Définir le filtre à partir des seuls trades antérieurs à la date du jour ; le tester sur des "
                             "données historiques distinctes (walk-forward) avec coûts ×1 et ×3 ; accepter seulement si "
                             "l'espérance par trade augmente et la pire baisse ne se dégrade pas de plus de 10 %.",
                "p_valeur": pval}
            out["incertain"].append("la récurrence est statistique ; elle doit être confirmée sur des données distinctes")
    else:
        out["recurrence"] = {"n": n, "statut": "échantillon insuffisant" if n < N_MIN_RECURRENCE else "sans objet (gain)"}
        if n < N_MIN_RECURRENCE:
            out["a_collecter"].append(f"au moins {N_MIN_RECURRENCE} trades comparables (actuellement {n})")
    if out["hypothese"] is None and not gagne:
        out["decision"] = "aucune modification de stratégie : une perte isolée ne justifie pas de changement"
    elif out["hypothese"]:
        out["decision"] = "hypothèse ajoutée au registre ; la stratégie n'est PAS modifiée avant validation"
    else:
        out["decision"] = "aucune modification"
    return out


def bilan(trades, reference_R, version):
    """Bilan périodique : résultats par régime avec correction de Holm sur les tests multiples."""
    if not trades:
        return {"n": 0}
    R = np.array([t["resultat"]["R"] for t in trades])
    net = np.array([t["resultat"]["net"] for t in trades])
    p0 = float(np.mean(np.asarray(reference_R) <= 0))
    tests = []
    for rg in sorted({t["regime"] for t in trades}):
        sel = [t for t in trades if t["regime"] == rg]
        k = sum(t["resultat"]["net"] <= 0 for t in sel)
        tests.append({"regime": rg, "n": len(sel), "pertes": k, "R_moyen": float(np.mean([t["resultat"]["R"] for t in sel])),
                      "p_brute": binom_sup(k, len(sel), p0), "confiance": confiance(len(sel))})
    m = len(tests)
    for i, tt in enumerate(sorted(tests, key=lambda z: z["p_brute"])):          # Holm
        tt["p_holm"] = min(1.0, tt["p_brute"] * (m - i))
        tt["significatif"] = tt["p_holm"] < 0.05 and tt["n"] >= N_MIN_RECURRENCE
    gains, pertes = net[net > 0].sum(), -net[net <= 0].sum()
    return {"n": len(trades), "version": version, "reussite": float((net > 0).mean()), "R_moyen": float(R.mean()),
            "R_total": float(R.sum()), "profit_factor": float(gains / pertes) if pertes else None,
            "taux_perte_attendu": p0, "par_regime": tests,
            "conformes": int(sum(t.get("_conforme", True) for t in trades))}
