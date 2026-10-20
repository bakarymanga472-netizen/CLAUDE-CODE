"""Labo — évaluation complète d'un instrument : données, caractéristiques, stratégies concurrentes sur plusieurs
unités de temps, coûts, régimes, walk-forward, références, DSR/PBO, coffre, fiche.

Usage : python3 -m labo.pilote BTCUSDT
Sorties : rapports/labo_<SYM>.md (fiche), rapports/labo_<SYM>.json (chiffres), registre/experiences.jsonl.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import caracteristiques, criteres as K, donnees, regimes, validation as V
from .couts import Couts
from .moteur import mesures, simuler
from .strategies import CANDIDATES, achat_conservation

ICI = Path(__file__).resolve().parent.parent
INTERVALLES = ["1d", "4h", "1h"]
N_HASARD = 100


def cle(strat, p, tf):
    return f"{strat.NOM}|{json.dumps(p, sort_keys=True)}|{tf}"


def trades_oos(resultats, choix):
    morceaux = []
    for y, k in choix.items():
        t = resultats[k]["trades"]
        if len(t):
            morceaux.append(t[(t.entree >= f"{y}-01-01") & (t.entree <= f"{y}-12-31 23:59")])
    return pd.concat(morceaux) if morceaux else pd.DataFrame(columns=["net", "R"])


def resume_jour(r, trades_df):
    m = mesures(r, trades_df, "1d")
    return {k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in m.items()} if m else None


def evaluer(symbole):
    out = {"instrument": symbole, "criteres": K.VERSION, "donnees": {}, "caracteristiques": {}}
    resultats, stress, retard, jour, donnees_tf, reg_tf = {}, {}, {}, {}, {}, {}
    for tf in INTERVALLES:
        df, h = donnees.charger(symbole, tf)
        q = donnees.qualite(df, tf)
        q["empreinte"], q["suffisant"] = h, donnees.suffisant(q)
        out["donnees"][tf] = q
        out["caracteristiques"][tf] = caracteristiques.decrire(df.loc[:K.DEVELOPPEMENT[1]], tf)
        donnees_tf[tf], reg_tf[tf] = df, regimes.etiqueter(df, tf)
        bpj = donnees.BARRES_PAR_JOUR[tf]
        for s in CANDIDATES:
            for p in s.GRILLE:
                k = cle(s, p, tf)
                c = s.cible(df, bpj, **p)
                resultats[k] = simuler(df, c, tf)
                stress[k] = simuler(df, c, tf, Couts().stresse(K.STRESS_COUTS))
                retard[k] = simuler(df, c, tf, Couts().stresse(1.0, retard=2))
                jour[k] = V.journalier(resultats[k]["net"])
                m = V.sharpe_annuel(jour[k].loc[:K.VALIDATION[1]])
                V.enregistrer_experience(symbole, k, h, {"sharpe_dev_val": round(m, 3), "criteres": K.VERSION})

    # Références sur données journalières
    d1 = donnees_tf["1d"]
    ref_brut = simuler(d1, achat_conservation.cible(d1, 1), "1d", dimensionner=False)
    ref_vol = simuler(d1, achat_conservation.cible(d1, 1), "1d")
    refs = {"achat_conservation": V.journalier(ref_brut["net"]), "achat_conservation_vol_ciblee": V.journalier(ref_vol["net"])}

    debut, fin_val = K.DEVELOPPEMENT[0], K.VALIDATION[1]
    oos_debut, oos_fin = f"{K.WALK_FORWARD_ANNEES[0]}-01-01", fin_val
    n_essais = V.nombre_experiences(symbole)
    toutes = pd.DataFrame({k: v.loc[oos_debut:oos_fin] for k, v in jour.items()})
    var_sr = float((toutes.mean() / toutes.std()).var())
    pbo_global = V.pbo(pd.DataFrame({k: v.loc[debut:fin_val] for k, v in jour.items()}))
    out["essais"] = {"configurations_distinctes": n_essais, "variance_sharpe_journalier": var_sr, "pbo_global": pbo_global}

    # Candidats : (stratégie, unité de temps) avec walk-forward sur sa propre grille ; + sélecteur global
    candidats = {f"{s.NOM}|{tf}": [cle(s, p, tf) for p in s.GRILLE] for s in CANDIDATES for tf in INTERVALLES}
    candidats["selecteur_global"] = list(jour)
    fiches = {}
    for nom, cles in candidats.items():
        wf, choix = V.walk_forward({k: jour[k] for k in cles}, K.WALK_FORWARD_ANNEES, debut)
        wf_stress, _ = V.walk_forward({k: jour[k] for k in cles}, K.WALK_FORWARD_ANNEES, debut)
        wf_stress = pd.concat([V.journalier(stress[choix[y]]["net"]).loc[f"{y}-01-01":f"{y}-12-31"] for y in choix])
        wf_retard = pd.concat([V.journalier(retard[choix[y]]["net"]).loc[f"{y}-01-01":f"{y}-12-31"] for y in choix])
        t = trades_oos(resultats, choix)
        m = resume_jour(wf, t)
        proba, sr0 = V.dsr(wf.values, max(n_essais, len(cles)), var_sr)
        proba_500, _ = V.dsr(wf.values, 500, var_sr)
        proba_nulle, _ = V.dsr(wf.values, max(n_essais, len(cles)), 1 / len(wf))
        p_fam = V.pbo(pd.DataFrame({k: jour[k].loc[debut:fin_val] for k in cles})) if len(cles) > 2 else None
        # Hasard de même profil, sur la variante choisie la plus récente
        k_ref = choix[K.WALK_FORWARD_ANNEES[-1]]
        tf_ref = k_ref.split("|")[-1]
        dfr = donnees_tf[tf_ref]
        w = resultats[k_ref]["w"]
        tr = resultats[k_ref]["trades"]
        expo = float((w != 0).mean())
        duree = float(tr.barres.mean()) if len(tr) else 1.0
        sh_h = []
        for g in range(N_HASARD):
            c = pd.Series(V.hasard(len(dfr), expo, duree, g), index=dfr.index)
            r = V.journalier(simuler(dfr, c, tf_ref)["net"]).loc[oos_debut:oos_fin]
            sh_h.append(V.sharpe_annuel(r))
        pct_hasard = float((np.array(sh_h) < V.sharpe_annuel(wf)).mean())
        p_sup = V.bootstrap_difference(wf, refs["achat_conservation_vol_ciblee"].loc[oos_debut:oos_fin])
        # Régimes : toujours étiquetés sur les bougies journalières (seuils définis en jours), connus la veille
        reg = reg_tf["1d"].shift(1)
        par_reg = {}
        for rg in regimes.REGIMES:
            r = wf[reg.reindex(wf.index) == rg]
            par_reg[rg] = {"jours": int(len(r)), "sharpe": V.sharpe_annuel(r) if len(r) >= 30 else None,
                           "rendement_annualise": float(r.mean() * 365) if len(r) >= 30 else None}
        # Coffre : configuration figée = meilleure sur tout ≤ 2023, appliquée 2024+
        scores = {k: V.sharpe_annuel(jour[k].loc[debut:fin_val]) for k in cles}
        finale = max(scores, key=scores.get)
        fiches[nom] = {
            "walk_forward": m, "choix_par_annee": {str(y): k for y, k in choix.items()},
            "sharpe_oos": V.sharpe_annuel(wf), "sharpe_oos_couts_x3": V.sharpe_annuel(wf_stress),
            "sharpe_oos_retard_2_barres": V.sharpe_annuel(wf_retard),
            "dsr": proba, "sharpe_max_hasard_journalier": sr0, "dsr_si_500_essais": proba_500, "dsr_variance_nulle": proba_nulle,
            "pbo_famille": p_fam, "percentile_hasard": pct_hasard, "p_superiorite_vs_vol_ciblee": p_sup,
            "regimes": par_reg, "configuration_finale": finale,
            "sharpe_annees_par_variante": {k: round(v, 2) for k, v in scores.items()},
            "couts_moyens_par_trade": float(t.couts.mean()) if len(t) and "couts" in t else None,
            "_finale_jour": jour[finale], "_wf": wf,
        }
    # Références sur la même fenêtre
    out["references"] = {n: resume_jour(r.loc[oos_debut:oos_fin], pd.DataFrame(columns=["net", "R"]))
                         for n, r in refs.items()}
    # Décision
    for nom, f in fiches.items():
        raisons = []
        tf = nom.split("|")[-1] if "|" in nom else "1d"
        if not out["donnees"][tf]["suffisant"]:
            raisons.append("données insuffisantes")
        if f["sharpe_oos"] < K.SHARPE_MIN_OOS:
            raisons.append(f"Sharpe hors échantillon {f['sharpe_oos']:.2f} < {K.SHARPE_MIN_OOS}")
        if f["dsr"] < K.DSR_MIN:
            raisons.append(f"DSR {f['dsr']:.2f} < {K.DSR_MIN}")
        if f["pbo_famille"] is not None and f["pbo_famille"] > K.PBO_MAX:
            raisons.append(f"PBO {f['pbo_famille']:.2f} > {K.PBO_MAX}")
        if (f["walk_forward"] or {}).get("trades", 0) < K.TRADES_MIN_OOS:
            raisons.append(f"{(f['walk_forward'] or {}).get('trades', 0)} trades hors échantillon < {K.TRADES_MIN_OOS}")
        if f["sharpe_oos_couts_x3"] <= 0:
            raisons.append("ne résiste pas aux coûts ×3")
        if f["percentile_hasard"] < K.PERCENTILE_HASARD:
            raisons.append(f"ne bat que {f['percentile_hasard'] * 100:.0f} % des expositions aléatoires (seuil 95 %)")
        f["raisons_rejet"] = raisons
        f["statut_developpement"] = "passe les critères de développement" if not raisons else "stratégie non validée"
    passants = [n for n, f in fiches.items() if not f["raisons_rejet"]]
    date_coffre, vierge = V.ouvrir_coffre(symbole)
    out["coffre"] = {"premiere_ouverture": date_coffre, "vierge_a_cette_execution": vierge}
    for n, f in fiches.items():
        r = f["_finale_jour"].loc[K.COFFRE[0]:]
        f["coffre"] = resume_jour(r, pd.DataFrame(columns=["net", "R"]))
        if n in passants:
            ok = V.sharpe_annuel(r) > K.SHARPE_MIN_COFFRE
            f["statut"] = "candidate — démo seulement" if ok else "rejetée par le coffre"
        else:
            f["statut"] = f["statut_developpement"]
    out["references_coffre"] = {n: resume_jour(r.loc[K.COFFRE[0]:], pd.DataFrame(columns=["net", "R"])) for n, r in refs.items()}
    out["fiches"] = {n: {k: v for k, v in f.items() if not k.startswith("_")} for n, f in fiches.items()}
    return out


def pct(x):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x * 100:+.1f} %"


def nb(x, d=2):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{d}f}"


def rapport(o):
    L = [f"# Fiche instrument — {o['instrument']}\n",
         f"Générée par `python3 -m labo.pilote {o['instrument']}` · critères `{o['criteres']}` (fixés avant les tests, `labo/criteres.py`).",
         f"Développement {K.DEVELOPPEMENT[0]} → {K.DEVELOPPEMENT[1]} · validation {K.VALIDATION[0]} → {K.VALIDATION[1]} · "
         f"walk-forward hors échantillon {K.WALK_FORWARD_ANNEES[0]}-{K.WALK_FORWARD_ANNEES[-1]} · coffre {K.COFFRE[0]} → aujourd'hui "
         f"(première ouverture : {o['coffre']['premiere_ouverture']}, {'vierge' if o['coffre']['vierge_a_cette_execution'] else 'DÉJÀ OUVERT avant cette exécution : ne prouve plus rien de neuf'}).\n",
         "## 1. Données\n", "| Unité | Période | Barres | Manquantes | Plus long trou | Doublons | OHLC incohérents | Rendements > 8σ | Empreinte | Suffisant |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for tf, q in o["donnees"].items():
        L.append(f"| {tf} | {q['debut'][:10]} → {q['fin'][:10]} ({q['annees']} ans) | {q['barres']} | {q['barres_manquantes']} | {q['plus_long_trou']} | "
                 f"{q['doublons']} | {q['ohlc_incoherents']} | {q['rendements_sup_8_sigma']} | `{q['empreinte']}` | {'oui' if q['suffisant'] else 'NON'} |")
    L += ["\nSource : Binance spot. Limites : un seul marché (pas de prix consolidé), pas de carnet d'ordres historique → spread et glissement modélisés, pas mesurés.\n",
          "## 2. Caractéristiques du marché (période de développement)\n",
          "| Unité | Vol annuelle | Asymétrie | Excès d'aplatissement | Autocorr. 1 barre | Ratio de variance 1 sem. | 1 mois | Pire baisse |", "|---|---|---|---|---|---|---|---|"]
    for tf, c in o["caracteristiques"].items():
        L.append(f"| {tf} | {pct(c['vol_annuelle'])} | {nb(c['asymetrie'])} | {nb(c['aplatissement_exces'], 1)} | {nb(c['autocorr_1_barre'], 3)} | "
                 f"{nb(c['ratio_variance_1sem'])} | {nb(c['ratio_variance_1mois'])} | {pct(c['pire_baisse_achat_conservation'])} |")
    L.append("\nRatio de variance > 1 : persistance (favorable au suivi de tendance) ; < 1 : retour à la moyenne. Aplatissement élevé : queues épaisses, stops glissants.\n")
    e = o["essais"]
    L += ["## 3. Contrôle du surapprentissage\n",
          f"- Configurations distinctes testées sur {o['instrument']} (registre `registre/experiences.jsonl`) : **{e['configurations_distinctes']}**.",
          f"- Probabilité de surapprentissage globale (PBO, CSCV 10 blocs, toutes variantes, ≤ 2023) : **{e['pbo_global']:.2f}**.",
          "- Le DSR (critère) utilise ce nombre d'essais et la variance OBSERVÉE des Sharpe des essais (formule de Bailey & López de Prado). "
          "Cette variance est gonflée par les variantes très mauvaises (rebond RSI intrajournalier) : le seuil devient très exigeant. "
          "La colonne « DSR var. nulle » (variance attendue si aucun essai n'avait d'avantage, 1/T) est donnée à titre d'information ; "
          "elle n'est PAS le critère fixé à l'avance et ne change aucun statut.",
          "- « DSR (500) » montre l'effet des recherches antérieures (Aladdin) non comptées ici.\n",
          "## 4. Résultats hors échantillon (walk-forward 2019-2023, coûts réalistes)\n",
          "| Candidat | Trades | Rendement/an | Pire baisse | PF | Espérance/trade | Espérance R | Sharpe | Coûts ×3 | Retard 2 barres | Années + | DSR | DSR (500) | DSR var. nulle | PBO | % hasard battu | p sup. vs vol ciblée | Statut |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, f in o["fiches"].items():
        m = f["walk_forward"] or {}
        L.append(f"| {n} | {m.get('trades')} | {pct(m.get('rendement_annuel'))} | {pct(m.get('pire_baisse'))} | {nb(m.get('profit_factor'))} | "
                 f"{pct(m.get('esperance_trade'))} | {nb(m.get('esperance_R'))} | {nb(f['sharpe_oos'])} | {nb(f['sharpe_oos_couts_x3'])} | "
                 f"{nb(f['sharpe_oos_retard_2_barres'])} | {m.get('annees_positives')} | {nb(f['dsr'])} | {nb(f['dsr_si_500_essais'])} | {nb(f['dsr_variance_nulle'])} | "
                 f"{nb(f['pbo_famille'])} | {f['percentile_hasard'] * 100:.0f} % | {nb(f['p_superiorite_vs_vol_ciblee'], 3)} | {f['statut']} |")
    L.append("\n**Références sur la même fenêtre** (aucune stratégie n'est dite supérieure sans p < 0,05 au bootstrap apparié) :\n")
    L += ["| Référence | Rendement/an | Pire baisse | Sharpe |", "|---|---|---|---|"]
    for n, m in o["references"].items():
        L.append(f"| {n} | {pct(m['rendement_annuel'])} | {pct(m['pire_baisse'])} | {nb(m['sharpe'])} |")
    L += ["\n## 5. Performance par régime (walk-forward, régimes connus la veille)\n",
          "| Candidat | Tendance | Range | Forte volatilité | Crise |", "|---|---|---|---|---|"]
    for n, f in o["fiches"].items():
        c = [f"{nb(f['regimes'][r]['sharpe'])} ({f['regimes'][r]['jours']} j)" for r in regimes.REGIMES]
        L.append(f"| {n} | " + " | ".join(c) + " |")
    L.append("\nValeur = Sharpe annualisé dans le régime ; « — » = moins de 30 jours, pas de conclusion.\n")
    L += ["## 6. Coffre 2024 → aujourd'hui (configuration figée avec ≤ 2023)\n",
          "| Candidat | Configuration figée | Rendement/an | Pire baisse | Sharpe |", "|---|---|---|---|---|"]
    for n, f in o["fiches"].items():
        m = f["coffre"] or {}
        L.append(f"| {n} | `{f['configuration_finale']}` | {pct(m.get('rendement_annuel'))} | {pct(m.get('pire_baisse'))} | {nb(m.get('sharpe'))} |")
    for n, m in o["references_coffre"].items():
        L.append(f"| *{n}* | — | {pct(m['rendement_annuel'])} | {pct(m['pire_baisse'])} | {nb(m['sharpe'])} |")
    L += ["\n## 7. Fiches de décision\n"]
    for n, f in o["fiches"].items():
        mauvais = [r for r in regimes.REGIMES if f["regimes"][r]["sharpe"] is not None and f["regimes"][r]["sharpe"] < 0]
        L += [f"### {n} — **{f['statut']}**\n",
              f"- Version/paramètres : configuration figée `{f['configuration_finale']}` ; choix walk-forward par année : "
              + ", ".join(f"{y} → `{k.split('|')[1]} {k.split('|')[2]}`" for y, k in f["choix_par_annee"].items()),
              f"- Raisons de rejet : {'; '.join(f['raisons_rejet']) if f['raisons_rejet'] else 'aucune en développement'}",
              f"- Coût moyen par trade (hors échantillon) : {pct(f['couts_moyens_par_trade'])}",
              f"- Ne pas utiliser en régime : {', '.join(mauvais) if mauvais else 'aucun régime négatif identifié (échantillon limité)'} ; "
              "désactiver aussi si les données du jour échouent au contrôle qualité, ou si le Sharpe glissant 1 an passe sous 0 (seuil fixé à l'avance).\n"]
    L += ["## 8. Ce qui reste incertain\n",
          "- Spread et glissement sont modélisés (pas de carnet d'ordres historique). Les colonnes coûts ×3 et retard 2 barres bornent l'erreur.",
          "- Un seul instrument : aucun effet de diversification n'est mesuré ici.",
          "- 5 années hors échantillon = peu de cycles crypto complets ; toute conclusion est provisoire.",
          "- Les chiffres « par régime » reposent sur peu de jours en crise.\n"]
    return "\n".join(L)


def main(symbole="BTCUSDT"):
    o = evaluer(symbole)
    (ICI / "rapports").mkdir(exist_ok=True)
    (ICI / "rapports" / f"labo_{symbole}.json").write_text(json.dumps(o, indent=1, default=str, ensure_ascii=False))
    texte = rapport(o)
    (ICI / "rapports" / f"labo_{symbole}.md").write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main(*sys.argv[1:])
