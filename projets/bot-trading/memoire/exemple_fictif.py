"""EXEMPLE AVEC DONNÉES FICTIVES — aucun de ces trades n'a eu lieu.

Génère 80 trades inventés (graine fixe) avec quelques anomalies volontaires (données périmées, ordre rejeté, taille
doublée, glissement anormal, règle violée), les enregistre dans memoire/exemple_fictif/, les analyse et écrit les
rapports dans rapports/exemple_fictif/. Usage : python3 -m memoire.exemple_fictif
"""
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from . import analyste, rapports
from .base import Memoire

ICI = Path(__file__).resolve().parent.parent
DOSSIER = ICI / "memoire" / "exemple_fictif"
SORTIE = ICI / "rapports" / "exemple_fictif"
ENTETE = "> ⚠️ **DONNÉES FICTIVES** — exemple de démonstration généré par `memoire/exemple_fictif.py`. Aucun trade réel.\n"
VERSION = "tendance-1d-v0-FICTIF"


def fabriquer(i, rng):
    regime = rng.choice(["tendance", "range", "forte_volatilite", "crise"], p=[0.35, 0.4, 0.15, 0.1])
    prix = float(30000 * np.exp(rng.normal(0, 0.3)))
    risque = 0.06
    taille = 0.10
    # Espérance fictive : positive en tendance, négative en range (pour que le bilan ait quelque chose à détecter)
    r = rng.normal({"tendance": 0.6, "range": -0.35, "forte_volatilite": 0.1, "crise": -0.1}[regime], 1.0)
    net = r * risque
    slip_prevu = 0.0005
    t = {
        "id": f"FICTIF-{i:04d}", "instrument": "BTCUSDT-FICTIF", "marche": "binance-spot (fictif)",
        "strategie": "tendance", "version": VERSION,
        "horodatage_entree": str(pd.Timestamp("2026-01-01") + pd.Timedelta(days=3 * i)),
        "horodatage_sortie": str(pd.Timestamp("2026-01-01") + pd.Timedelta(days=3 * i + 2)),
        "donnees_entree": {"derniere_barre": str(pd.Timestamp("2026-01-01") + pd.Timedelta(days=3 * i - 1)),
                           "age_secondes": 3600, "duree_barre_secondes": 86400, "qualite_ok": True,
                           "valeurs": {"cloture": prix, "rendement_30j": float(rng.normal(0.05, 0.1))}},
        "signaux": {"rendement_30j": float(rng.normal(0.08, 0.05)), "vol_30j": float(abs(rng.normal(0.6, 0.15)))},
        "plan": {"sens": "long", "prix_prevu": prix, "stop": prix * (1 - risque), "objectif": None,
                 "taille_prevue": taille, "risque_unitaire": risque,
                 "regles": [{"nom": "rendement_30j>0", "valeur": 0.05, "op": ">", "seuil": 0}],
                 "filtres": [{"nom": "qualite_donnees", "respecte": True}],
                 "cout_prevu": {"frais": 0.001, "glissement": slip_prevu}},
        "execution": {"ordres": [{"id": f"O{i}-a", "statut": "rempli", "prix": prix, "quantite": taille}],
                      "prix_entree": prix * (1 + slip_prevu), "prix_sortie": prix * (1 + net),
                      "taille": taille, "motif_sortie": "signal"},
        "resultat": {"brut": net + 0.002, "net": net, "frais": 0.002, "glissement": slip_prevu, "R": r},
        "regime": str(regime), "decision_agent": "entrée conforme au signal tendance 30 j (FICTIF)",
        "etat_systeme": {"version_code": "fictif", "anomalies": []},
    }
    # Anomalies volontaires
    if i == 7:
        t["donnees_entree"].update(age_secondes=3 * 86400)
    if i == 15:
        t["execution"]["ordres"].insert(0, {"id": f"O{i}-0", "statut": "rejete", "prix": prix, "quantite": taille})
    if i == 23:
        t["execution"]["taille"] = 0.2
    if i == 31:
        t["resultat"]["glissement"] = 0.004
    if i == 42:
        t["plan"]["regles"][0]["valeur"] = -0.02
    return t


def main():
    if DOSSIER.exists():
        shutil.rmtree(DOSSIER)          # exemple jetable : régénéré à l'identique (graine fixe)
    SORTIE.mkdir(parents=True, exist_ok=True)
    m = Memoire(DOSSIER)
    rng = np.random.default_rng(42)
    reference_R = np.random.default_rng(7).normal(0.2, 1.0, 2000)   # distribution « backtest » FICTIVE
    for i in range(80):
        t = fabriquer(i, rng)
        m.enregistrer_trade(t)
        historique = m.trades_effectifs()[:-1]
        d = analyste.diagnostiquer(t)
        a = analyste.analyser(t, d, historique, reference_R)
        m.r["diagnostics"].ajouter({"trade_id": t["id"], "diagnostic": d, "nature": a["nature"]}, "DIAG")
        for e in a["erreurs_prevention"]:
            m.ajouter("erreurs_processus", {"date": t["horodatage_sortie"][:10], "trade_id": t["id"], "echantillon": 1,
                                            "confiance": "cause confirmée", "version_modele": VERSION, **e}, "ERR")
        deja = any(h["statut"] == "proposée" and h.get("regime") == t["regime"] for h in m.r["hypotheses"].lire())
        if a["hypothese"] and not deja:
            m.ajouter("hypotheses", {"date": t["horodatage_sortie"][:10], "echantillon": a["recurrence"]["n"],
                                     "confiance": analyste.confiance(a["recurrence"]["n"]), "version_modele": VERSION,
                                     "statut": "proposée", "regime": t["regime"], **a["hypothese"]}, "HYP")
        if i in (7, 15, 23, 31, 42, 60, 79):
            (SORTIE / f"trade_{t['id']}.md").write_text(rapports.rapport_trade(t, d, a, ENTETE), encoding="utf-8")
    # Une correction (exemple) : jamais d'écrasement, une entrée séparée justifiée
    m.corriger("FICTIF-0031", "resultat.glissement", 0.0038, "relevé de la plateforme reçu après coup (FICTIF)", "analyste")
    tr = m.trades_effectifs()
    b = analyste.bilan(tr, reference_R, VERSION)
    for t_ in b["par_regime"]:
        m.ajouter("conditions_marche", {"date": "2026-08-31", "regime": t_["regime"], "echantillon": t_["n"],
                                        "confiance": t_["confiance"], "version_modele": VERSION,
                                        "R_moyen": t_["R_moyen"], "p_holm": t_["p_holm"]}, "COND")
    (SORTIE / "bilan.md").write_text(rapports.rapport_bilan(b, "2026-01-01 → 2026-08-31 (FICTIF)", ENTETE), encoding="utf-8")
    m.ajouter("modifications", {"date": "2026-09-01", "objet": "exemple : filtre « pas d'entrée en range »",
                                "resultat": "non testé dans l'exemple — voir amelioration/ pour la boucle réelle",
                                "echantillon": b["n"], "confiance": "faible", "version_modele": VERSION}, "MOD")
    (SORTIE / "modifications.md").write_text(rapports.historique_modifications(m.r["modifications"].lire(), ENTETE), encoding="utf-8")
    print(ENTETE)
    print(f"{len(tr)} trades fictifs, intégrité : {m.verifier()}")
    print(f"Erreurs confirmées : {len(m.r['erreurs_processus'].lire())} · hypothèses proposées : {len(m.r['hypotheses'].lire())}")
    print(rapports.rapport_bilan(b, "FICTIF"))


if __name__ == "__main__":
    main()
