"""Carry — pilote : données + qualité, grille déclarée, backtests, stress, liquidation, DSR, contrôle, rapport.

Usage : python3 -m carry.pilote
Sorties : rapports/carry_crypto.md, rapports/carry_crypto.json, carry/registre/ (expériences + coffre).
Le registre global registre/ du labo n'est PAS modifié (consigne : n'écrire que dans carry/ et rapports/carry_crypto.*).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from labo import donnees as labo_donnees, validation as V
from labo.moteur import mesures
from . import donnees as D, strategie as S

ICI = Path(__file__).resolve().parent
RAPPORTS = ICI.parent / "rapports"
REGISTRE = ICI / "registre"

# ---------- Périodes et critères FIXÉS AVANT le premier lancement (2026-10-20) ----------
VERSION = "carry-criteres-v1-2026-10-20"
DEVELOPPEMENT = ("2020-01-01", "2022-12-31")
VALIDATION = ("2023-01-01", "2023-12-31")
CONTROLE = ("2024-01-01", "2100-01-01")          # ouvert une seule fois, à la fin ; ne sert qu'à rejeter
STRESS = 3.0
CRITERES = {
    "selection": "variante au meilleur Sharpe en DÉVELOPPEMENT, par symbole (5 variantes chacune)",
    "rendement_annuel_validation_min": 0.0,       # > taux sans risque supposé 0 % (HYPOTHÈSE)
    "sharpe_validation_min": 0.5,
    "rendement_annuel_validation_stress_x3_min": 0.0,
    "liquidations_levier1_max": 0,                 # sur toute la période, dans la simulation retenue
    "dsr_min": 0.95,                               # dev+val, n_essais = 10 variantes
    "pire_baisse_dev_val_min": -0.20,
    "controle_rendement_annuel_min": 0.0,          # 2024+ : rejet seulement
}
STATUTS = ("candidate démo", "non validée")         # jamais « validée »


def _propre(x):
    if isinstance(x, dict):
        return {k: _propre(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_propre(v) for v in x]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else round(float(x), 6)
    if isinstance(x, np.integer):
        return int(x)
    return x


def enregistrer(instrument, cle, empreinte, resume):
    REGISTRE.mkdir(exist_ok=True)
    with open(REGISTRE / "experiences.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "instrument": instrument,
                            "experience": cle, "donnees": empreinte, **_propre(resume)}, ensure_ascii=False) + "\n")


def ouvrir_coffre(cle):
    REGISTRE.mkdir(exist_ok=True)
    f = REGISTRE / "coffre.json"
    etat = json.loads(f.read_text()) if f.exists() else {}
    if cle in etat:
        return etat[cle], False
    etat[cle] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    f.write_text(json.dumps(etat, indent=2))
    return etat[cle], True


def mes(res, debut, fin):
    net, w = res["net"].loc[debut:fin], res["w"].loc[debut:fin]
    t = res["trades"]
    if len(t):   # trades qui chevauchent la période
        t = t[(t.sortie >= pd.Timestamp(debut)) & (t.entree <= pd.Timestamp(fin))]
    m = mesures(net, t, "1d", w)
    if m is None:
        return None
    m.pop("esperance_R", None)
    m["part_temps_expose"] = m.pop("exposition_moyenne")
    m["liquidations"] = int(res["liquidations"].loc[debut:fin].sum())
    m["funding_encaisse_sur_capital"] = float(res["funding"].loc[debut:fin].sum())
    m["couts_sur_capital"] = float(res["couts"].loc[debut:fin].sum())
    m["debut"], m["fin"] = str(net.index[0].date()), str(net.index[-1].date())
    return m


def par_annee(r):
    return {int(y): float(v) for y, v in ((1 + r).groupby(r.index.year).prod() - 1).items()}


def evaluer():
    out = {"criteres_version": VERSION, "criteres": CRITERES, "grille": [S.nom(p) for p in S.GRILLE],
           "n_variantes_total": S.N_VARIANTES_TOTAL,
           "periodes": {"developpement": DEVELOPPEMENT, "validation": VALIDATION, "controle": CONTROLE},
           "hypotheses_couts": S.CoutsCarry().__dict__, "symboles": {}}
    res_tous, jour_tous, cadres = {}, {}, {}
    for sym in S.SYMBOLES:
        f_brut, mois_abs, h_f = D.funding(sym)
        perp, mois_abs_k, h_k = D.klines_perp(sym)
        spot, h_s = labo_donnees.charger(sym, "1d")
        mark, mois_abs_m, h_m = D.mark_perp(sym)
        q = {"funding": D.qualite_funding(f_brut), "funding_mois_absents": mois_abs,
             "perp_1d": D.qualite_klines(perp), "perp_mois_absents": mois_abs_k,
             "spot_1d": labo_donnees.qualite(spot, "1d"),
             "mark_1d": D.qualite_klines(mark), "mark_mois_absents": mois_abs_m,
             "empreintes": {"funding": h_f, "perp": h_k, "spot": h_s, "mark": h_m}}
        try:
            q["controle_croise_okx"] = D.controle_croise(f_brut, D.funding_okx(sym))
        except Exception as e:                                      # noqa: BLE001
            q["controle_croise_okx"] = {"erreur": str(e)[:200]}
        fund = D.nettoyer_funding(f_brut).taux
        df = S.aligner(spot, perp, fund, mark)
        base = df.f_open / df.s_open - 1
        q["base_perp_spot_ouverture"] = {
            nomp: {"moyenne": float(base.loc[a:b].mean()), "min": float(base.loc[a:b].min()),
                   "max": float(base.loc[a:b].max())}
            for nomp, (a, b) in {"developpement": DEVELOPPEMENT, "validation": VALIDATION, "controle": CONTROLE}.items()}
        q["funding_annualise_par_annee"] = {int(y): float(v) for y, v in
                                           (fund.groupby(fund.index.year).mean() * 3 * 365).items()}
        q["cadre_backtest"] = {"debut": str(df.index[0].date()), "fin": str(df.index[-1].date()), "jours": len(df)}
        cadres[sym] = (df, fund, perp, mark)
        out["symboles"][sym] = {"donnees": q}
        for p in S.GRILLE:
            k = f"{sym}|{S.nom(p)}"
            pos = S.positions(fund, df.index, p)
            res_tous[k] = {"base": S.simuler(df, pos), "stress": S.simuler(df, pos, S.CoutsCarry().stresse(STRESS))}
            jour_tous[k] = res_tous[k]["base"]["net"]
            enregistrer(f"carry_{sym}", S.nom(p), h_f,
                        {"criteres": VERSION, "sharpe_dev": V.sharpe_annuel(jour_tous[k].loc[DEVELOPPEMENT[0]:DEVELOPPEMENT[1]])})

    dv = (DEVELOPPEMENT[0], VALIDATION[1])
    mat = pd.DataFrame({k: v.loc[dv[0]:dv[1]] for k, v in jour_tous.items()})
    sr_jour = mat.mean() / mat.std()
    var_sr = float(sr_jour.var())
    out["essais"] = {"n": S.N_VARIANTES_TOTAL, "variance_sharpe_journalier_dev_val": var_sr,
                     "pbo_dev_val_10_variantes": V.pbo(mat)}

    for sym in S.SYMBOLES:
        df, fund, perp, mark = cadres[sym]
        bloc = out["symboles"][sym]
        bloc["variantes"] = {}
        for p in S.GRILLE:
            k = f"{sym}|{S.nom(p)}"
            rb, rs = res_tous[k]["base"], res_tous[k]["stress"]
            bloc["variantes"][S.nom(p)] = {
                "developpement": mes(rb, *DEVELOPPEMENT), "validation": mes(rb, *VALIDATION),
                "stress_x3": {"developpement": mes(rs, *DEVELOPPEMENT), "validation": mes(rs, *VALIDATION)},
                "par_annee_dev_val": {a: v for a, v in par_annee(rb["net"].loc[dv[0]:dv[1]]).items()},
                "dsr_dev_val": V.dsr(rb["net"].loc[dv[0]:dv[1]].values, S.N_VARIANTES_TOTAL, var_sr)[0],
            }
        # sélection sur le développement seulement
        retenue = max(bloc["variantes"], key=lambda n: bloc["variantes"][n]["developpement"]["sharpe"])
        v = bloc["variantes"][retenue]
        k = f"{sym}|{retenue}"
        rb = res_tous[k]["base"]
        dsr_val, sr0 = V.dsr(rb["net"].loc[dv[0]:dv[1]].values, S.N_VARIANTES_TOTAL, var_sr)
        dd_dv = mesures(rb["net"].loc[dv[0]:dv[1]], rb["trades"], "1d")["pire_baisse"]
        p_vs_passive = None
        if retenue != "passive":
            p_vs_passive = V.bootstrap_difference(rb["net"].loc[dv[0]:dv[1]],
                                                  res_tous[f"{sym}|passive"]["base"]["net"].loc[dv[0]:dv[1]])
        tests = {
            "rendement_val": v["validation"]["rendement_annuel"] > CRITERES["rendement_annuel_validation_min"],
            "sharpe_val": v["validation"]["sharpe"] >= CRITERES["sharpe_validation_min"],
            "stress_val": v["stress_x3"]["validation"]["rendement_annuel"] > CRITERES["rendement_annuel_validation_stress_x3_min"],
            "liquidations": int(rb["liquidations"].sum()) <= CRITERES["liquidations_levier1_max"],
            "dsr": dsr_val >= CRITERES["dsr_min"],
            "pire_baisse_dev_val": dd_dv >= CRITERES["pire_baisse_dev_val_min"],
        }
        bloc["retenue"] = {"variante": retenue, "dsr_dev_val": dsr_val, "sharpe_max_attendu_hasard_journalier": sr0,
                           "pire_baisse_dev_val": dd_dv, "p_bootstrap_retenue_pas_mieux_que_passive": p_vs_passive,
                           "tests_avant_controle": tests}
        # Liquidation contrefactuelle (rééquilibrage quotidien)
        bloc["liquidation_quotidienne"] = {
            "toute_periode": S.liquidations_quotidiennes(perp, df.index[0], df.index[-1]),
            "toute_periode_mark_price": S.liquidations_quotidiennes(perp, df.index[0], df.index[-1], haut=mark.high),
            "simulation_retenue_liquidations": int(rb["liquidations"].sum())}
        # Sensibilité POST-HOC (ajoutée après avoir vu la mèche ETH du 2020-03-13) : liquidation contrôlée sur le mark
        # price. NE CHANGE PAS le statut, qui reste fondé sur la règle déclarée (dernier prix).
        pos_r = S.positions(fund, df.index, next(p for p in S.GRILLE if S.nom(p) == retenue))
        rm = S.simuler(df, pos_r, liquidation_sur="m_high")
        bloc["sensibilite_mark_price_post_hoc"] = {
            "liquidations": int(rm["liquidations"].sum()),
            "developpement": mes(rm, *DEVELOPPEMENT), "validation": mes(rm, *VALIDATION), "controle": mes(rm, *CONTROLE),
            "pire_baisse_dev_val": mesures(rm["net"].loc[dv[0]:dv[1]], rm["trades"], "1d")["pire_baisse"],
            "dsr_dev_val": V.dsr(rm["net"].loc[dv[0]:dv[1]].values, S.N_VARIANTES_TOTAL, var_sr)[0],
            "par_annee": par_annee(rm["net"])}
        # Contrôle : ouvert une seule fois, à la fin
        date_ouv, vierge = ouvrir_coffre(f"carry_{sym}")
        rs = res_tous[k]["stress"]
        bloc["controle"] = {"ouvert_le": date_ouv, "premiere_ouverture": vierge,
                            "retenue": mes(rb, *CONTROLE), "retenue_stress_x3": mes(rs, *CONTROLE),
                            "par_annee": par_annee(rb["net"].loc[CONTROLE[0]:]),
                            "toutes_variantes": {S.nom(p): mes(res_tous[f"{sym}|{S.nom(p)}"]["base"], *CONTROLE)
                                                 for p in S.GRILLE}}
        tests["controle"] = bloc["controle"]["retenue"]["rendement_annuel"] > CRITERES["controle_rendement_annuel_min"]
        bloc["statut"] = STATUTS[0] if all(tests.values()) else STATUTS[1]
        bloc["par_annee_toute_periode"] = {S.nom(p): par_annee(res_tous[f"{sym}|{S.nom(p)}"]["base"]["net"])
                                           for p in S.GRILLE}
        # Références : achat-conservation spot sur les mêmes jours (ouverture → ouverture)
        r_bh = (df.s_next / df.s_open - 1)
        vide = pd.DataFrame(columns=["net", "R"])
        bloc["achat_conservation"] = {nomp: mesures(r_bh.loc[a:b], vide, "1d") for nomp, (a, b) in
                                      {"developpement": DEVELOPPEMENT, "validation": VALIDATION, "controle": CONTROLE}.items()}
        bloc["achat_conservation"]["par_annee"] = par_annee(r_bh)
    out["sans_risque"] = "0 %/an par HYPOTHÈSE (aucune série de taux chargée) ; un placement monétaire réel a rapporté davantage en 2023-2025."
    return _propre(out)


def pct(x, d=1):
    return "n/d" if x is None else f"{x * 100:.{d}f} %"


def num(x, d=2):
    return "n/d" if x is None else f"{x:.{d}f}"


def rapport(o):
    L = ["# S3 — Carry funding crypto (long spot + short perpétuel) — BTCUSDT, ETHUSDT", "",
         f"Généré le {datetime.now(timezone.utc).date()} par `python3 -m carry.pilote`. Recherche historique uniquement : aucun ordre, aucune clé. "
         f"Critères : `{o['criteres_version']}`. Aucun résultat n'est « validé » : au mieux « candidate démo ».", ""]
    L += ["## 1. Données et qualité", "",
          "- Funding : archives Binance USDT-M `data/futures/um/monthly/fundingRate` (CSV : `calc_time` ms UTC, `funding_interval_hours`, "
          "`last_funding_rate` = fraction par période de 8 h ; >0 : les longs paient les shorts). Premier mois disponible : 2020-01.",
          "- Perp : klines 1d `data/futures/um/monthly/klines/<SYM>/1d` ; mark price 1d `markPriceKlines` (sensibilité liquidation). Spot : `labo.donnees.charger(sym, '1d')` (Binance spot).",
          "- Les archives mensuelles s'arrêtent au dernier mois complet : le backtest finit avant le mois en cours.", "",
          "| | BTCUSDT | ETHUSDT |", "|---|---|---|"]
    q = {s: o["symboles"][s]["donnees"] for s in S.SYMBOLES}
    lignes = [("Funding : début → fin", lambda d: f"{d['funding']['debut'][:10]} → {d['funding']['fin'][:16]}"),
              ("Paiements / attendus (8 h)", lambda d: f"{d['funding']['paiements']} / {d['funding']['paiements_attendus_8h']}"),
              ("Trous / doublons / hors grille", lambda d: f"{d['funding']['nb_trous']} / {d['funding']['doublons']} / {d['funding']['heures_hors_grille_00_08_16']}"),
              ("Jours sans 3 paiements", lambda d: str(d['funding']['jours_pas_3_paiements'])),
              ("Intervalles (h)", lambda d: str(d['funding']['intervalles_h'])),
              ("Taux min / max par 8 h", lambda d: f"{pct(d['funding']['taux_min'], 3)} / {pct(d['funding']['taux_max'], 3)}"),
              ("Paiements à |taux| ≥ 0,3 % (plafond) ; > 0,3 %", lambda d: f"{d['funding']['au_plafond_abs_0_3pct']} ; {d['funding']['aberrants_abs_sup_0_3pct']}"),
              ("Aberrants (z > 10)", lambda d: str(d['funding']['aberrants_z_sup_10'])),
              ("Part de paiements négatifs", lambda d: pct(d['funding']['part_negatifs'])),
              ("Funding moyen annualisé (notionnel)", lambda d: pct(d['funding']['taux_moyen_annualise'])),
              ("Perp 1d : barres manquantes", lambda d: str(d['perp_1d']['manquantes'])),
              ("Mark price 1d : barres manquantes", lambda d: str(d['mark_1d']['manquantes'])),
              ("Spot 1d : barres manquantes / doublons", lambda d: f"{d['spot_1d']['barres_manquantes']} / {d['spot_1d']['doublons']}"),
              ("Cadre du backtest", lambda d: f"{d['cadre_backtest']['debut']} → {d['cadre_backtest']['fin']} ({d['cadre_backtest']['jours']} j)"),
              ("Empreintes funding / perp / spot", lambda d: " / ".join(f"`{v}`" for v in d['empreintes'].values()))]
    for t, f in lignes:
        L.append(f"| {t} | {f(q['BTCUSDT'])} | {f(q['ETHUSDT'])} |")
    L += ["", "**Contrôle croisé OKX** (API publique, historique court ≈ 3 mois) :", ""]
    for s in S.SYMBOLES:
        c = q[s]["controle_croise_okx"]
        if "correlation" in c:
            L.append(f"- {s} : {c['paiements_communs']} paiements communs ({c['debut'][:10]} → {c['fin'][:10]}), corrélation {num(c['correlation'])}, "
                     f"même signe {pct(c['meme_signe'])}, annualisé Binance {pct(c['binance_annualise'])} vs OKX {pct(c['okx_annualise'])}.")
        else:
            L.append(f"- {s} : contrôle impossible ({c}).")
    L += ["", "Les taux bornés à ±0,3 % sont les bornes réglementaires du funding Binance (pas des erreurs) : conservés.",
          "", "**Base perp/spot à l'ouverture** (perp/spot − 1) :", ""]
    for s in S.SYMBOLES:
        b = q[s]["base_perp_spot_ouverture"]
        L.append(f"- {s} : " + " ; ".join(f"{k} moy. {pct(v['moyenne'], 3)} [min {pct(v['min'], 2)}, max {pct(v['max'], 2)}]" for k, v in b.items()))
    L += ["", "**Funding brut moyen annualisé par année (notionnel, donnée de marché)** :", "",
          "| Année | " + " | ".join(S.SYMBOLES) + " |", "|---|---|---|"]
    annees = sorted(q["BTCUSDT"]["funding_annualise_par_annee"])
    for a in annees:
        L.append(f"| {a} | " + " | ".join(pct(q[s]["funding_annualise_par_annee"].get(a)) for s in S.SYMBOLES) + " |")

    c0 = o["hypotheses_couts"]
    L += ["", "## 2. Méthode", "",
          "- Position : 50 % du capital en spot long, 50 % en marge USDT sur un short perp de même notionnel (levier 1 sur la jambe short). "
          "Les rendements sont exprimés **sur le capital total** : un funding de 10 %/an sur le notionnel ≈ 5 %/an sur le capital.",
          "- Funding du jour t = paiements de t 08:00, t 16:00, t+1 00:00 ; position ouverte/fermée à l'ouverture (00:00 UTC) du jour t aux prix "
          "d'ouverture spot ET perp (la base à l'entrée/sortie est dans le PnL).",
          "- Décision du jour t : indicateur = moyenne des N derniers paiements STRICTEMENT antérieurs à t 00:00, ×3×365. Pas de look-ahead (testé).",
          f"- Coûts par jambe : spot {pct(c0['commission_spot'], 2)} + glissement {pct(c0['glissement_spot'], 2)} ; perp {pct(c0['commission_perp'], 2)} + "
          f"glissement {pct(c0['glissement_perp'], 2)}. 4 jambes par aller-retour. Stress : commissions et glissement ×{STRESS:g}.",
          f"- Rééquilibrage vérifié chaque jour, exécuté si une jambe s'écarte de plus de {pct(c0['bande'], 0)} de sa cible (frais payés).",
          f"- Liquidation : chaque jour, si au plus haut perp du jour la marge tombe sous la marge de maintenance ({pct(c0['marge_maintenance'], 1)}, hypothèse), "
          "la marge est perdue et le spot vendu.",
          "- Position passive tenue jusqu'au bout : ses frais de sortie sont imputés au dernier jour de l'échantillon. "
          "Les trades d'une période = ceux qui la chevauchent.",
          "- Approximation : funding calculé sur le notionnel au prix perp d'ouverture du jour (pas au mark exact de chaque paiement). "
          "La marge USDT ne rapporte rien.",
          "- Référence sans risque : 0 %/an (HYPOTHÈSE, aucune série de taux chargée). Achat-conservation spot sur les mêmes jours.",
          "- Périodes : développement 2020-01 → 2022-12, validation 2023, contrôle 2024-01 → fin des archives (ouvert une seule fois)."]
    L += ["", "## 3. Grille déclarée avant tout test et critères annoncés", "",
          f"Grille (par symbole) : {', '.join('`' + g + '`' for g in o['grille'])} → **{o['n_variantes_total']} variantes au total** "
          "(N ∈ {3, 21} paiements, entrée ∈ {10 %, 20 %}/an annualisé sur le notionnel, sortie < 0 %).", "",
          "Critères « candidate démo » (TOUS requis, fixés avant le lancement) :", "",
          f"1. Sélection : {CRITERES['selection']}.",
          "2. Validation 2023 : rendement annualisé net > 0 % (sans risque supposé 0 %) et Sharpe ≥ 0,5.",
          "3. Validation 2023 avec coûts ×3 : rendement annualisé net > 0 %.",
          "4. Aucune liquidation de la jambe short (levier 1) sur toute la période simulée.",
          "5. DSR (dev + validation, 10 variantes) ≥ 0,95.",
          "6. Pire baisse dev + validation ≥ −20 %.",
          "7. Contrôle 2024+ : rendement annualisé net > 0 % (sert uniquement à rejeter).",
          "", f"PBO (CSCV, 10 variantes, dev+val) : {num(o['essais']['pbo_dev_val_10_variantes'])}."]

    L += ["", "## 4. Résultats par période", ""]
    for s in S.SYMBOLES:
        b = o["symboles"][s]
        L += [f"### {s}", "",
              "| Variante | Période | Rend. annuel | Vol | Sharpe | Pire baisse | Trades | Réussite | PF | Temps exposé | Funding encaissé* | Coûts* |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for nv, v in b["variantes"].items():
            per = [("dév", v["developpement"]), ("val", v["validation"]), ("contrôle", b["controle"]["toutes_variantes"][nv])]
            for nomp, m in per:
                L.append(f"| {nv}{' ★' if nv == b['retenue']['variante'] else ''} | {nomp} | {pct(m['rendement_annuel'])} | {pct(m['volatilite'])} | "
                         f"{num(m['sharpe'])} | {pct(m['pire_baisse'])} | {m['trades']} | {pct(m['reussite'], 0)} | {num(m['profit_factor'])} | "
                         f"{pct(m['part_temps_expose'], 0)} | {pct(m['funding_encaisse_sur_capital'])} | {pct(m['couts_sur_capital'], 2)} |")
        bh = b["achat_conservation"]
        L += ["", "\\* cumul sur la période, en fraction du capital initial de la période (somme simple). ★ = variante retenue (meilleur Sharpe en dév).", "",
              f"Achat-conservation {s} (spot) : dév {pct(bh['developpement']['rendement_annuel'])}/an, Sharpe {num(bh['developpement']['sharpe'])}, pire baisse {pct(bh['developpement']['pire_baisse'])} ; "
              f"val {pct(bh['validation']['rendement_annuel'])}/an, Sharpe {num(bh['validation']['sharpe'])}, pire baisse {pct(bh['validation']['pire_baisse'])} ; "
              f"contrôle {pct(bh['controle']['rendement_annuel'])}/an, Sharpe {num(bh['controle']['sharpe'])}, pire baisse {pct(bh['controle']['pire_baisse'])}.", ""]
        r = b["retenue"]
        L += [f"Retenue : `{r['variante']}` — DSR dev+val {num(r['dsr_dev_val'], 3)} (Sharpe journalier max attendu par hasard {num(r['sharpe_max_attendu_hasard_journalier'], 4)}), "
              f"pire baisse dev+val {pct(r['pire_baisse_dev_val'])}"
              + (f", bootstrap p(retenue ≤ passive, dev+val) = {num(r['p_bootstrap_retenue_pas_mieux_que_passive'], 3)}" if r['p_bootstrap_retenue_pas_mieux_que_passive'] is not None else "")
              + ".", ""]

    L += ["## 5. Rendement net par année (coûts de base, toute la période)", "",
          "Montre l'évolution du carry dans le temps. Les années de bord sont partielles (2026 jusqu'à la fin des archives).", ""]
    for s in S.SYMBOLES:
        b = o["symboles"][s]
        ans = sorted({a for d in b["par_annee_toute_periode"].values() for a in d})
        L += [f"**{s}**", "", "| Variante | " + " | ".join(str(a) for a in ans) + " |", "|---|" + "---|" * len(ans)]
        for nv, d in b["par_annee_toute_periode"].items():
            L.append(f"| {nv} | " + " | ".join(pct(d.get(str(a), d.get(a))) for a in ans) + " |")
        bh = b["achat_conservation"]["par_annee"]
        L.append(f"| achat-conservation spot | " + " | ".join(pct(bh.get(str(a), bh.get(a))) for a in ans) + " |")
        L.append("")

    L += ["## 6. Stress des coûts (×3)", "", "| Symbole | Variante | Dév rend. / Sharpe | Val rend. / Sharpe | Contrôle rend. (retenue) |", "|---|---|---|---|---|"]
    for s in S.SYMBOLES:
        b = o["symboles"][s]
        for nv, v in b["variantes"].items():
            st = v["stress_x3"]
            ctl = pct(b["controle"]["retenue_stress_x3"]["rendement_annuel"]) if nv == b["retenue"]["variante"] else ""
            L.append(f"| {s} | {nv} | {pct(st['developpement']['rendement_annuel'])} / {num(st['developpement']['sharpe'])} | "
                     f"{pct(st['validation']['rendement_annuel'])} / {num(st['validation']['sharpe'])} | {ctl} |")

    L += ["", "## 7. Liquidation de la jambe short", "",
          "Rééquilibrage quotidien à l'ouverture ; pire cas = plus haut perp du jour vs ouverture. Seuil = hausse qui épuise la marge "
          "(marge initiale 1/levier, maintenance 0,4 %, hypothèse).", "",
          "| Symbole | Hausse intrajour max (date) | Levier 1 | Levier 2 | Levier 3 | Levier 5 | Liquidations dans la simulation retenue |",
          "|---|---|---|---|---|---|---|"]
    for s in S.SYMBOLES:
        lq = o["symboles"][s]["liquidation_quotidienne"]
        t = lq["toute_periode"]
        L.append(f"| {s} | {pct(t['hausse_intrajour_max'])} ({t['date_max']}) | "
                 + " | ".join(f"{t[f'levier_{l}']['jours_liquides']} j (seuil {pct(t[f'levier_{l}']['seuil_hausse'], 0)})" for l in (1, 2, 3, 5))
                 + f" | {lq['simulation_retenue_liquidations']} |")
    L += ["", "**Même calcul avec le plus haut du MARK PRICE** (archives `markPriceKlines`, prix qui déclenche réellement les liquidations) :", "",
          "| Symbole | Hausse intrajour max (date) | Levier 1 | Levier 2 | Levier 3 | Levier 5 |", "|---|---|---|---|---|---|"]
    for s in S.SYMBOLES:
        t = o["symboles"][s]["liquidation_quotidienne"]["toute_periode_mark_price"]
        L.append(f"| {s} | {pct(t['hausse_intrajour_max'])} ({t['date_max']}) | "
                 + " | ".join(f"{t[f'levier_{l}']['jours_liquides']} j" for l in (1, 2, 3, 5)) + " |")
    L += ["", "Jours sans barre mark dans les archives (repli conservateur sur le dernier prix perp) : "
          + ", ".join(f"{s} {o['symboles'][s]['liquidation_quotidienne']['toute_periode_mark_price']['jours_repli_dernier_prix']}" for s in S.SYMBOLES)
          + ". Le 36,2 % BTC du 2021-07-26 est un tel repli (mèche du dernier prix perp à 48 168 ; plus haut spot 40 550, soit +14,6 %)."]
    L += ["", "**Sensibilité POST-HOC** (ajoutée après avoir constaté la mèche du dernier prix ETH perp le 2020-03-13 : plus haut 323 contre "
          "≈ 140 au spot et au mark) — variante retenue, liquidation contrôlée sur le mark price. Elle **ne modifie pas le statut**, fondé sur la règle déclarée :", ""]
    for s in S.SYMBOLES:
        m = o["symboles"][s]["sensibilite_mark_price_post_hoc"]
        L.append(f"- {s} : liquidations {m['liquidations']} ; dév {pct(m['developpement']['rendement_annuel'])}/an (Sharpe {num(m['developpement']['sharpe'])}), "
                 f"val {pct(m['validation']['rendement_annuel'])}/an, contrôle {pct(m['controle']['rendement_annuel'])}/an ; pire baisse dev+val {pct(m['pire_baisse_dev_val'])} ; "
                 f"DSR dev+val {num(m['dsr_dev_val'], 3)} ; par année : " + ", ".join(f"{a} {pct(v)}" for a, v in m['par_annee'].items()) + ".")
    L += ["", "Limite : le mark price Binance (qui déclenche la liquidation) diffère du dernier prix des klines ; les mèches de dernier prix "
          "peuvent exagérer ou sous-estimer le risque. Le rééquilibrage suppose aussi un transfert spot → marge instantané."]

    L += ["", "## 8. Statut (critères annoncés avant le lancement)", ""]
    for s in S.SYMBOLES:
        b = o["symboles"][s]
        t = b["retenue"]["tests_avant_controle"]
        L.append(f"- **{s} — {b['statut']}** (retenue `{b['retenue']['variante']}`) : "
                 + ", ".join(f"{k} {'✔' if v else '✘'}" for k, v in t.items())
                 + f". Contrôle ouvert le {b['controle']['ouvert_le']}{' (première ouverture)' if b['controle']['premiere_ouverture'] else ' (DÉJÀ ouvert auparavant : résultat moins vierge)'}.")
    L += ["", "« Candidate démo » signifie seulement : mérite un essai en démo/papier avec suivi ; ce n'est pas une validation."]

    L += ["", "## 9. Limites et risques non modélisés", "",
          "- **Faillite / gel de plateforme** (FTX 2022) : spot et marge chez le même tiers ; perte possible de tout le capital. Non modélisé.",
          "- **ADL (auto-deleveraging)** : la jambe short peut être réduite de force lors de liquidations en chaîne, laissant le spot non couvert. Non modélisé.",
          "- **Changement de règles de funding** : formule, plafonds (±0,3 % observés), intervalle (8 h → 4 h/1 h sur certains contrats). Supposé stable.",
          "- **Emprunt** : aucun emprunt modélisé (stratégie entièrement financée) ; une version à levier ajouterait coût d'emprunt et risque de rappel.",
          "- Taux sans risque supposé à 0 % : en 2023-2025 un placement monétaire USD rapportait nettement plus ; la comparaison réelle est donc moins favorable.",
          "- Funding payé au prix d'ouverture (approximation), marge non rémunérée, glissement fixe supposé, pas de carnet d'ordres, exécution simultanée parfaite des 2 jambes.",
          "- Mark price ≠ dernier prix pour la liquidation ; frais de transfert et délais entre comptes spot/futures ignorés ; fiscalité ignorée.",
          "- Survivant : BTC et ETH sont les deux contrats les plus liquides ; résultat non transposable aux altcoins.",
          "- Le registre global `registre/` du labo n'a pas été modifié (consigne) : le registre de ces expériences est `carry/registre/`."]
    return "\n".join(L) + "\n"


def main():
    o = evaluer()
    RAPPORTS.mkdir(exist_ok=True)
    (RAPPORTS / "carry_crypto.json").write_text(json.dumps(o, ensure_ascii=False, indent=1, default=str))
    (RAPPORTS / "carry_crypto.md").write_text(rapport(o))
    for s in S.SYMBOLES:
        b = o["symboles"][s]
        print(s, b["retenue"]["variante"], b["statut"])


if __name__ == "__main__":
    main()
