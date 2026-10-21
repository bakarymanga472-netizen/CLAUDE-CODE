"""Boucle d'amélioration continue — pilote sur un instrument.

  python3 -m amelioration.boucle declarer   → enregistre la version de référence et les hypothèses AVEC leur protocole
  python3 -m amelioration.boucle tester     → exécute le protocole en 8 étapes pour chaque hypothèse déclarée non testée
  python3 -m amelioration.boucle surveiller → indicateurs, alertes et évaluation historique des détecteurs
  python3 -m amelioration.boucle promouvoir <version> --autorisation-humaine "<texte>"  (humain uniquement)

Règle de décision commune (fixée le 2026-10-20, avant tout test) : voir DECISION.
Aucune version ne remplace automatiquement la version stable.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from labo import donnees, validation as V
from labo.couts import Couts
from labo.moteur import simuler
from memoire.registre import Registre

from . import garde_fous, surveillance
from .variantes import exposition

ICI = Path(__file__).resolve().parent.parent
DOSSIER = Path(__file__).resolve().parent / "registre"
INSTRUMENT = "BTCUSDT"
DISTINCTS = ["ETHUSDT", "LTCUSDT", "XRPUSDT", "BNBUSDT"]   # données NON utilisées pour formuler les hypothèses
PERIODES = {"developpement": ("2017-08-17", "2021-12-31"), "validation": ("2022-01-01", "2023-12-31"),
            "recent": ("2024-01-01", "2100-01-01")}
DECISION = {
    "version": "decision-v1-2026-10-20",
    "p_holm_max": 0.05,                 # test apparié sur le portefeuille des instruments distincts, corrigé de Holm
    "instruments_ameliores_min": 3,     # sur 4 instruments distincts
    "baisse_max_degradation": 0.10,     # pire baisse du portefeuille combiné pas plus de 10 % plus profonde
    "couts_stress": 3.0,                # l'amélioration doit rester > 0 avec coûts ×3
    "voisins_tous_positifs": True,      # chaque paramètre voisin déclaré doit aussi améliorer
}
STABLE = {"id": "BTC-tendance-1d-v1", "strategie": "tendance", "params": {"jours": 90}, "intervalle": "1d",
          "modifications": [], "statut_labo": "non validée (voir rapports/labo_BTCUSDT.md) — référence de simulation seulement"}
HYPOTHESES = [
    {"id": "H-001", "probleme": "Sharpe de la tendance 1d faible en régime « range » (0,17 sur 785 j, rapports/labo_BTCUSDT.md §5)",
     "enonce": "Ne pas être exposé quand le régime connu est « range » améliore le rapport rendement/risque.",
     "modification": {"type": "regimes_exclus", "regimes": ["range"]},
     "voisins": [{"type": "regimes_exclus", "regimes": ["range"], "seuil_efficacite": 0.20},
                 {"type": "regimes_exclus", "regimes": ["range"], "seuil_efficacite": 0.30}]},
    {"id": "H-002", "probleme": "Pire baisse hors échantillon de -60 % pour la tendance 1d (rapports/labo_BTCUSDT.md §4)",
     "enonce": "Un stop suiveur à 3 écarts-types journaliers sous le plus haut depuis l'entrée réduit la pire baisse sans détruire le rendement.",
     "modification": {"type": "stop_suiveur", "k_sigma": 3.0},
     "voisins": [{"type": "stop_suiveur", "k_sigma": 2.5}, {"type": "stop_suiveur", "k_sigma": 3.5}]},
    {"id": "H-003", "probleme": "Le walk-forward choisit souvent 30 jours plutôt que 90 (choix par année, rapports/labo_BTCUSDT.md §7)",
     "enonce": "Un lookback de 30 jours fait mieux que 90 jours.",
     "params": {"jours": 30}, "voisins_params": [{"jours": 20}, {"jours": 45}]},
]


def reg(nom):
    return Registre(DOSSIER / f"{nom}.jsonl")


def spec_de(h, voisin=None, params=None):
    s = {k: v for k, v in STABLE.items() if k in ("strategie", "params", "intervalle")}
    s["params"] = params or h.get("params") or STABLE["params"]
    s["modifications"] = [voisin or h["modification"]] if (voisin or h.get("modification")) else []
    return s


def jour_de(sym, spec, couts=Couts()):
    df, h = donnees.charger(sym, spec["intervalle"])
    return V.journalier(simuler(df, exposition(df, spec), spec["intervalle"], couts)["net"]), h


def metriques(r):
    c = (1 + r).cumprod()
    return {"sharpe": V.sharpe_annuel(r), "rendement_annuel": float(c.iloc[-1] ** (365 / max(len(r), 1)) - 1),
            "pire_baisse": float((c / c.cummax() - 1).min())}


def empreinte(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ---------------- Déclaration ----------------
def declarer():
    versions = reg(f"versions_{INSTRUMENT}")
    if not any(e["evenement"] == "stable_definie" for e in versions.lire()):
        r, h = jour_de(INSTRUMENT, STABLE)
        versions.ajouter({"evenement": "stable_definie", "version": STABLE["id"], "spec": STABLE, "donnees": h,
                          "metriques_reference": metriques(r)}, "VER")
    hyp = reg("hypotheses")
    deja = {e["hypothese"] for e in hyp.lire()}
    for h in HYPOTHESES:
        if h["id"] not in deja:
            hyp.ajouter({"evenement": "declaree", "hypothese": h["id"], "definition": h, "decision": DECISION,
                         "protocole": ["tests unitaires", "reproduction de la version stable", "backtest coûts réalistes",
                                       "validation chronologique + instruments distincts " + ", ".join(DISTINCTS),
                                       "comparaison appariée à la stable (bootstrap, Holm)", "robustesse coûts ×3 et voisins",
                                       "effet sur le portefeuille combiné", "enregistrement du résultat"]}, "HYP")
    print(f"Version stable : {STABLE['id']} · hypothèses déclarées : {[e['hypothese'] for e in hyp.lire() if e['evenement'] == 'declaree']}")


# ---------------- Protocole en 8 étapes ----------------
def tester_hypothese(h, n_deja_testees):
    etapes = {}
    # 1. Tests unitaires
    import os
    t = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=ICI,
                       capture_output=True, text=True, env={**os.environ, "BOUCLE_EN_COURS": "1"})
    etapes["1_tests_unitaires"] = "OK" if t.returncode == 0 else "ÉCHEC"
    if t.returncode:
        return etapes, "rejetée", ["tests unitaires en échec"]
    # 2. Reproduction de la stable
    ref = next(e for e in reg(f"versions_{INSTRUMENT}").lire() if e["evenement"] == "stable_definie")
    r_stable, hdon = jour_de(INSTRUMENT, STABLE)
    m = metriques(r_stable)
    repro = hdon == ref["donnees"] and all(abs(m[k] - ref["metriques_reference"][k]) < 1e-9 for k in m)
    etapes["2_reproduction_stable"] = {"reproduit": repro, "donnees": hdon, "attendu": ref["metriques_reference"], "obtenu": m}
    if not repro:
        return etapes, "non concluante", ["la version stable ne se reproduit pas (données ou code changés)"]
    spec = spec_de(h)
    # 3 + 4. Backtest coûts réalistes, chronologique et instruments distincts
    r_cand, _ = jour_de(INSTRUMENT, spec)
    etapes["3_backtest_btc"] = {"stable": metriques(r_stable), "candidate": metriques(r_cand)}
    etapes["4_chronologique_btc"] = {p: {"stable": metriques(r_stable.loc[a:b]), "candidate": metriques(r_cand.loc[a:b])}
                                     for p, (a, b) in PERIODES.items()}
    dist_s, dist_c, ameliores = {}, {}, 0
    etapes["4_instruments_distincts"] = {}
    for sym in DISTINCTS:
        dist_s[sym], _ = jour_de(sym, STABLE)
        dist_c[sym], _ = jour_de(sym, spec)
        ms, mc = metriques(dist_s[sym]), metriques(dist_c[sym])
        ameliores += mc["sharpe"] > ms["sharpe"]
        etapes["4_instruments_distincts"][sym] = {"stable": ms, "candidate": mc}
    # 5. Comparaison appariée sur le portefeuille équipondéré des instruments distincts, Holm
    ps = pd.concat(dist_s, axis=1).mean(axis=1)
    pc = pd.concat(dist_c, axis=1).mean(axis=1)
    p_brut = V.bootstrap_difference(pc, ps, n=1000, graine=0)
    m_tests = n_deja_testees + 1
    p_holm = min(1.0, p_brut * m_tests)   # borne conservatrice (Bonferroni) tant que les tests passés ne sont pas reclassés
    etapes["5_comparaison"] = {"p_brute": p_brut, "tests_cumules": m_tests, "p_corrigee": p_holm,
                               "sharpe_portefeuille_distinct": {"stable": V.sharpe_annuel(ps), "candidate": V.sharpe_annuel(pc)}}
    # 6. Robustesse coûts ×3 et voisins
    cs = pd.concat({s: jour_de(s, STABLE, Couts().stresse(DECISION["couts_stress"]))[0] for s in DISTINCTS}, axis=1).mean(axis=1)
    cc = pd.concat({s: jour_de(s, spec, Couts().stresse(DECISION["couts_stress"]))[0] for s in DISTINCTS}, axis=1).mean(axis=1)
    voisins = []
    for v in h.get("voisins", []):
        sv = spec_de(h, voisin=v)
        pv = pd.concat({s: jour_de(s, sv)[0] for s in DISTINCTS}, axis=1).mean(axis=1)
        voisins.append({"voisin": v, "delta_sharpe": V.sharpe_annuel(pv) - V.sharpe_annuel(ps)})
    for pa in h.get("voisins_params", []):
        sv = spec_de(h, params=pa)
        pv = pd.concat({s: jour_de(s, sv)[0] for s in DISTINCTS}, axis=1).mean(axis=1)
        voisins.append({"voisin": pa, "delta_sharpe": V.sharpe_annuel(pv) - V.sharpe_annuel(ps)})
    etapes["6_robustesse"] = {"delta_sharpe_couts_x3": V.sharpe_annuel(cc) - V.sharpe_annuel(cs), "voisins": voisins}
    # 7. Portefeuille combiné (BTC + distincts)
    tout_s = pd.concat({**dist_s, INSTRUMENT: r_stable}, axis=1).mean(axis=1)
    tout_c = pd.concat({**dist_c, INSTRUMENT: r_cand}, axis=1).mean(axis=1)
    etapes["7_portefeuille_combine"] = {"stable": metriques(tout_s), "candidate": metriques(tout_c)}
    return etapes, *decider(p_holm, ameliores, etapes["7_portefeuille_combine"], etapes["6_robustesse"])


def decider(p_corrigee, ameliores, combine, robustesse):
    """Applique la règle DECISION (fixée avant les tests). Fonction pure, testée dans tests/test_amelioration.py."""
    raisons = []
    if p_corrigee >= DECISION["p_holm_max"]:
        raisons.append(f"amélioration non significative (p corrigée {p_corrigee:.3f})")
    if ameliores < DECISION["instruments_ameliores_min"]:
        raisons.append(f"améliore seulement {ameliores}/4 instruments distincts")
    pb_s, pb_c = combine["stable"]["pire_baisse"], combine["candidate"]["pire_baisse"]
    if pb_c < pb_s * (1 + DECISION["baisse_max_degradation"]):
        raisons.append(f"pire baisse du portefeuille dégradée ({pb_s:.0%} → {pb_c:.0%})")
    if robustesse["delta_sharpe_couts_x3"] <= 0:
        raisons.append("ne résiste pas aux coûts ×3")
    if DECISION["voisins_tous_positifs"] and any(v["delta_sharpe"] <= 0 for v in robustesse["voisins"]):
        raisons.append("au moins un paramètre voisin n'améliore pas (résultat fragile)")
    return ("acceptée comme candidate" if not raisons else "rejetée"), raisons


def tester():
    hyp = reg("hypotheses")
    evts = hyp.lire()
    testees = {e["hypothese"] for e in evts if e["evenement"] == "resultat"}
    n_deja = len(testees)
    for e in [e for e in evts if e["evenement"] == "declaree" and e["hypothese"] not in testees]:
        h = e["definition"]
        etapes, verdict, raisons = tester_hypothese(h, n_deja)
        n_deja += 1
        res = {"evenement": "resultat", "hypothese": h["id"], "verdict": verdict, "raisons": raisons,
               "etapes": etapes, "decision": DECISION["version"]}
        res["empreinte_resultat"] = empreinte({"etapes": etapes, "verdict": verdict})
        hyp.ajouter(res, "HYP")
        evt = "candidate_acceptee" if verdict.startswith("acceptée") else "candidate_rejetee"
        reg(f"versions_{INSTRUMENT}").ajouter({"evenement": evt, "version": f"{STABLE['id']}+{h['id']}",
                                              "spec": spec_de(h), "raisons": raisons,
                                              "note": "n'est PAS promue stable : promotion réservée à l'humain"}, "VER")
        print(f"{h['id']} : {verdict} — {'; '.join(raisons) or 'tous les critères passés'}")


def etat_versions():
    stable, candidates = None, {}
    for e in reg(f"versions_{INSTRUMENT}").lire():
        if e["evenement"] in ("stable_definie", "promotion_humaine", "retour_stable"):
            stable = e["version"]
        elif e["evenement"] == "candidate_acceptee":
            candidates[e["version"]] = "acceptée (en attente d'autorisation humaine)"
        elif e["evenement"] == "candidate_rejetee":
            candidates[e["version"]] = "rejetée"
    return stable, candidates


def retour_stable(version_candidate, motif):
    """En cas de dégradation en simulation, on revient à la version stable validée (enregistré, jamais effacé)."""
    stable, _ = etat_versions()
    return reg(f"versions_{INSTRUMENT}").ajouter({"evenement": "retour_stable", "version": stable,
                                                 "abandonnee": version_candidate, "motif": motif}, "VER")


def promouvoir(version, autorisation):
    garde_fous.exiger_humain("promouvoir_stable", autorisation)
    return reg(f"versions_{INSTRUMENT}").ajouter({"evenement": "promotion_humaine", "version": version,
                                                 "autorisation": autorisation}, "VER")


def surveiller():
    df, _ = donnees.charger(INSTRUMENT, "1d")
    res = simuler(df, exposition(df, STABLE), "1d")
    j = V.journalier(res["net"])
    t = res["trades"]
    ref = {"pire_baisse": metriques(j.loc[:"2023-12-31"])["pire_baisse"],
           "cout_moyen_trade": float(t[t.entree <= "2023-12-31"].couts.mean()),
           "reussite_c5": float(np.quantile([t.net.sample(50, replace=True, random_state=i).gt(0).mean() for i in range(500)], 0.05))}
    ind = surveillance.indicateurs(df, j, t, ref)
    det = surveillance.evaluer_detecteurs(df, j)
    return ind, det


def rapport():
    hyp = reg("hypotheses").lire()
    stable, cand = etat_versions()
    ind, det = surveiller()
    L = [f"# Boucle d'amélioration — {INSTRUMENT} (pilote)\n",
         "Commandes : `python3 -m amelioration.boucle declarer`, `tester`, `rapport`. Règle de décision : "
         f"`{DECISION['version']}` (fixée avant les tests, `amelioration/boucle.py`). Données distinctes : {', '.join(DISTINCTS)}.\n",
         f"**Version stable** : `{stable}` — {STABLE['statut_labo']}.\n", "## Hypothèses et verdicts\n",
         "| Id | Problème documenté | Énoncé | Verdict | Raisons | Δ Sharpe portefeuille distinct | p corrigée | Δ Sharpe coûts ×3 | Voisins (Δ Sharpe) | Pire baisse combinée stable → candidate | Empreinte |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    defs = {e["hypothese"]: e["definition"] for e in hyp if e["evenement"] == "declaree"}
    for e in [e for e in hyp if e["evenement"] == "resultat"]:
        et = e["etapes"]
        if "5_comparaison" not in et:
            L.append(f"| {e['hypothese']} | | | {e['verdict']} | {'; '.join(e['raisons'])} | | | | | | |")
            continue
        c = et["5_comparaison"]
        d = c["sharpe_portefeuille_distinct"]["candidate"] - c["sharpe_portefeuille_distinct"]["stable"]
        p7 = et["7_portefeuille_combine"]
        L.append(f"| {e['hypothese']} | {defs[e['hypothese']]['probleme']} | {defs[e['hypothese']]['enonce']} | **{e['verdict']}** | "
                 f"{'; '.join(e['raisons']) or '—'} | {d:+.2f} | {c['p_corrigee']:.3f} | {et['6_robustesse']['delta_sharpe_couts_x3']:+.2f} | "
                 + ", ".join(f"{v['delta_sharpe']:+.2f}" for v in et["6_robustesse"]["voisins"])
                 + f" | {p7['stable']['pire_baisse']:.0%} → {p7['candidate']['pire_baisse']:.0%} | `{e['empreinte_resultat']}` |")
    L += ["\n## Détail par instrument distinct (Sharpe stable → candidate)\n", "| Hypothèse | " + " | ".join(DISTINCTS) + " | BTC dév. | BTC valid. | BTC récent |",
          "|---|" + "---|" * (len(DISTINCTS) + 3)]
    for e in [e for e in hyp if e["evenement"] == "resultat" and "4_instruments_distincts" in e["etapes"]]:
        d, ch = e["etapes"]["4_instruments_distincts"], e["etapes"]["4_chronologique_btc"]
        L.append(f"| {e['hypothese']} | " + " | ".join(f"{d[s]['stable']['sharpe']:.2f} → {d[s]['candidate']['sharpe']:.2f}" for s in DISTINCTS)
                 + " | " + " | ".join(f"{ch[p]['stable']['sharpe']:.2f} → {ch[p]['candidate']['sharpe']:.2f}" for p in PERIODES) + " |")
    L += ["\n## Versions\n", f"- Stable : `{stable}`"] + [f"- `{k}` : {v}" for k, v in cand.items()]
    L += ["\n## Surveillance de la version stable (seuils `amelioration/seuils.json`, fixés avant les tests)\n",
          f"- Sharpe glissant 1 an : {ind['sharpe_glissant_1an']:.2f} · baisse en cours : {ind['baisse_en_cours']:.0%}",
          f"- Alertes : {'; '.join(ind['alertes']) if ind['alertes'] else 'aucune'}\n",
          "## Détecteurs de changement — évaluation historique (BTC 1d)\n",
          "Un détecteur n'est utile que si l'état annoncé se confirme sur les 30 jours suivants plus souvent que le taux de base.\n",
          "| Détecteur | Événements | Taux de confirmation | Taux de base | p-valeur | Lecture |", "|---|---|---|---|---|---|"]
    for k, v in det.items():
        if not v["evenements"]:
            lect = "aucun événement"
        elif v["evenements"] < 20:
            lect = "indéterminé : moins de 20 événements"
        else:
            lect = "mieux que le hasard" if v["p_valeur"] < 0.05 else "pas mieux que le hasard"
        L.append(f"| {k} | {v['evenements']} | {('—' if v['taux_succes'] is None else format(v['taux_succes'], '.0%'))} | "
                 f"{v['taux_de_base']:.0%} | {('—' if v['p_valeur'] is None else format(v['p_valeur'], '.3f'))} | {lect} |")
    L += ["\n## Limites\n",
          "- Les instruments « distincts » sont des cryptos encore cotées aujourd'hui (biais de survivance) et très corrélées à BTC : ce n'est pas une indépendance parfaite.",
          "- Correction des tests multiples : borne de Bonferroni sur le nombre cumulé d'hypothèses testées (conservatrice).",
          "- Toutes les données BTC jusqu'à aujourd'hui ont déjà été vues : seules les données FUTURES (suivi papier) seront réellement vierges."]
    (ICI / "rapports" / f"amelioration_{INSTRUMENT}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "rapport"
    if cmd == "declarer":
        declarer()
    elif cmd == "tester":
        tester()
    elif cmd == "promouvoir":
        promouvoir(sys.argv[2], sys.argv[sys.argv.index("--autorisation-humaine") + 1] if "--autorisation-humaine" in sys.argv else None)
    else:
        rapport()
