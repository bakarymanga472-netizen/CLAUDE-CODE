"""Stratégie COMBINÉE à haut taux de réussite (demande du 2026-10-21) — construite à partir de ce que le labo a appris.

Ce qui est repris, et pourquoi :
- le repli de court terme (RSI-2, famille « Rebond ») : seule famille testée qui donne ≥ 70 % de trades gagnants ;
- le filtre de tendance (cours > moyenne 200 séances) : seul ingrédient qui a amélioré plusieurs stratégies (H2) ;
- la diversification sur 16 ETF liquides (leçon du portefeuille de tendance) : plus de trades, moins de dépendance à un actif ;
- l'exécution au cours de clôture de la séance suivante et les coûts réalistes (corrections de l'audit) ;
- un stop toujours présent (-10 %), pas de martingale, levier limité et testé comme un « curseur de risque ».
Ce qui est écarté : les stratégies des vidéos (aucun avantage après frais), le carry (rendement trop faible), les filtres
« 99 % » sans stop (ruine démontrée).

Règles FIXÉES AVANT EXÉCUTION (2026-10-21) :
- signal à la clôture t : RSI-2 < seuil ET clôture > moyenne 200 séances ; les candidats sont classés du RSI le plus bas au plus haut ;
- au plus K = 5 positions simultanées, chacune pèse L / K du capital (L = levier, 1 par défaut) ; entrée à la clôture t+1 ;
- sorties (décidées à une clôture, exécutées à la suivante), deux variantes :
    A « Rebond »  : gain ≥ +1 % ou perte ≤ -10 % ou 20 séances ;
    B « Connors » : clôture > moyenne 5 séances, ou perte ≤ -10 %, ou 10 séances ;
- seuil ∈ {5, 10} → 4 variantes ; choix sur 2000-2015 (Sharpe), contrôle 2016-2021, test 2022 → aujourd'hui ;
- coûts : 0,02 % par côté (ETF très liquides, ordre au cours de clôture) ; emprunt 5 %/an sur la part au-delà de 100 % ;
- références : entrées au hasard (mêmes sorties, même fréquence, au-dessus de la moyenne 200), achat-conservation équipondéré.
AJOUT APRÈS LA 1re EXÉCUTION (2026-10-21, tracé) : la règle de choix (Sharpe 2000-2015) ignorait la contrainte de
l'utilisateur « ≥ 70 % de réussite » ; elle a choisi B10 (≈ 64 %). Second choix, déclaré ici : meilleure variante en Sharpe
2000-2015 PARMI celles qui ont ≥ 70 % de réussite sur 2000-2015 — critère qui n'utilise ni 2016-2021 ni le test.
Le curseur de levier est montré pour les deux choix, jusqu'à ×10, pour rendre visible le prix des « gros gains ».
Usage : python3 -m labo.combine → rapports/combine.md / .json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import donnees, validation as V
from .strategies.outils import rsi

ICI = Path(__file__).resolve().parent.parent
UNIVERS = ["SPY", "QQQ", "IWM", "DIA", "EFA", "EEM", "GLD", "TLT", "XLE", "XLF", "XLK", "XLV", "XLY", "XLP", "XLI", "XLU"]
K = 5
COUT = 0.0002
EMPRUNT = 0.05
PERIODES = {"2000-2015 (choix)": ("2000-01-01", "2015-12-31"), "2016-2021 (contrôle)": ("2016-01-01", "2021-12-31"),
            "2022 → aujourd'hui (test)": ("2022-01-01", "2100-01-01")}
VARIANTES = {f"{s}{n}": {"sortie": s, "seuil": n} for s in ("A", "B") for n in (5, 10)}


def charger():
    px = {s: donnees.charger_yahoo(s)[0].close for s in UNIVERS}
    c = pd.DataFrame(px).sort_index()
    c = c.loc[c.index >= c.SPY.first_valid_index()]
    return c


def charger_ohlc():
    """Clôtures + ouvertures + plus hauts alignés sur le calendrier du SPY (pour les ordres limites intrajournaliers)."""
    d = {s: donnees.charger_yahoo(s)[0] for s in UNIVERS}
    c = pd.DataFrame({s: x.close for s, x in d.items()}).sort_index()
    c = c.loc[c.index >= c.SPY.first_valid_index()]
    o = pd.DataFrame({s: x.open for s, x in d.items()}).reindex(c.index)
    h = pd.DataFrame({s: x.high for s, x in d.items()}).reindex(c.index)
    return c, o, h


def indicateurs(c, o=None, h=None):
    ind = _indicateurs(c)
    if o is not None:
        ind["open"], ind["high"] = o, h
    ref = c["SPY"] if "SPY" in c.columns else c.iloc[:, 0]
    spy_vol = ref.pct_change().rolling(20).std()
    ind["spy_vol_rang"] = spy_vol.expanding(250).rank(pct=True)
    return ind


def _indicateurs(c):
    return {"rsi": c.apply(lambda s: rsi(s.dropna(), 2)).reindex(c.index),
            "mm200": c.rolling(200).mean(), "mm50": c.rolling(50).mean(), "mm5": c.rolling(5).mean()}


def backtest(c, ind, sortie="A", seuil=5, levier=1.0, signal=None, etat=False, tp=0.01, tendance_forte=False,
             stop=0.10, duree=20, limite=False, filtre_vol=False, marge_limite=0.0005, taux_emprunt=EMPRUNT, cfd=False):
    """Boucle quotidienne au niveau du portefeuille. Renvoie (rendements quotidiens, trades)
    et, si etat=True, l'état final : positions ouvertes et ordres à passer à la prochaine clôture."""
    cv, rs, m200, m5 = c.values, ind["rsi"].values, ind["mm200"].values, ind["mm5"].values
    n, a = cv.shape
    sig = signal if signal is not None else (rs < seuil) & (cv > m200)
    if tendance_forte and signal is None:
        sig = sig & (ind["mm50"].values > m200)
    if filtre_vol and signal is None:                  # F3 : pas d'entrée quand la volatilité du marché est extrême
        sig = sig & ~(ind["spy_vol_rang"].values[:, None] > 0.8)
    if limite:
        ov, hv = ind["open"].values, ind["high"].values
    limites = {}                                       # j -> prix limite de vente valable pour la séance suivante
    w = levier / K
    ouvertes, a_entrer, a_sortir = {}, [], set()       # ouvertes : j -> (indice d'entrée, prix d'entrée)
    motifs = {}
    rend, trades = np.zeros(n), []
    for i in range(1, n):
        r = 0.0
        # 0) F1 : ventes à cours limité pendant la séance (ordre posé à la clôture précédente)
        if limite:
            for j in list(ouvertes):
                L = limites.get(j)
                if L is not None and np.isfinite(hv[i, j]) and hv[i, j] >= L * (1 + marge_limite) and j not in a_sortir:
                    e_i, e_p = ouvertes.pop(j)
                    prix = max(L, ov[i, j]) if np.isfinite(ov[i, j]) else L
                    r += w * (prix / cv[i - 1, j] - 1) - w * COUT
                    chemin = np.append(cv[e_i:i, j], prix) / e_p - 1
                    trades.append({"actif": c.columns[j], "entree": c.index[e_i], "sortie": c.index[i],
                                   "rendement": prix / e_p - 1 - 2 * COUT, "seances": i - e_i, "motif": "limite",
                                   "mfe": float(np.nanmax(chemin)), "mae": float(np.nanmin(chemin)), "i_entree": e_i, "j": j})
                    limites.pop(j, None)
                    a_entrer = [x for x in a_entrer if x != j]
        # 1) rendement de la journée pour les positions détenues depuis la clôture précédente
        for j in ouvertes:
            if np.isfinite(cv[i, j]) and np.isfinite(cv[i - 1, j]):
                r += w * (cv[i, j] / cv[i - 1, j] - 1)
        expo = w * len(ouvertes)
        # financement : courtier sur marge = intérêts sur la part empruntée ; CFD = financement sur TOUTE la position
        r -= (expo if cfd else max(expo - 1.0, 0.0)) * taux_emprunt / 252
        # 2) exécutions à la clôture i : sorties décidées hier, puis entrées décidées hier
        for j in list(a_sortir):
            e_i, e_p = ouvertes.pop(j)
            chemin = cv[e_i:i + 1, j] / e_p - 1
            trades.append({"actif": c.columns[j], "entree": c.index[e_i], "sortie": c.index[i],
                           "rendement": cv[i, j] / e_p - 1 - 2 * COUT, "seances": i - e_i,
                           "motif": motifs.pop(j, ""), "mfe": float(np.nanmax(chemin)), "mae": float(np.nanmin(chemin)),
                           "i_entree": e_i, "j": j})
            r -= w * COUT
        a_sortir.clear()
        for j in a_entrer:
            if np.isfinite(cv[i, j]):
                ouvertes[j] = (i, cv[i, j])
                r -= w * COUT
        a_entrer = []
        rend[i] = r
        # 3) décisions à la clôture i (exécution à la clôture i+1)
        for j, (e_i, e_p) in ouvertes.items():
            g = cv[i, j] / e_p - 1
            if sortie == "A":
                fin = g >= 0.01 or g <= -0.10 or (i - e_i) >= 20
            elif sortie == "C":                       # hybride A + B : objectif, ou rebond au-dessus de la MM5 SI en gain
                fin = g >= tp or (cv[i, j] > m5[i, j] and g > 0) or g <= -stop or (i - e_i) >= duree
            else:
                fin = cv[i, j] > m5[i, j] or g <= -0.10 or (i - e_i) >= 10
            if limite and sortie == "C":
                # F1 : l'objectif et le « rebond au-dessus de la MM5 en gain » deviennent un ordre limite pour demain.
                # clôture(t+1) > MM5(t+1)  ⇔  clôture(t+1) > moyenne des 4 dernières clôtures (connue ce soir).
                fin = g <= -stop or (i - e_i) >= duree
                p4 = np.nanmean(cv[i - 3:i + 1, j])
                limites[j] = min(e_p * (1 + tp), max(p4, e_p * 1.001))
            if fin:
                a_sortir.add(j)
                limites.pop(j, None)
                motifs[j] = ("stop" if g <= -(stop if sortie == "C" else 0.10) else
                             "durée" if (i - e_i) >= (duree if sortie == "C" else 20 if sortie == "A" else 10) else "objectif/rebond")
        libres = K - (len(ouvertes) - len(a_sortir))
        if libres > 0:
            cand = [j for j in range(a) if sig[i, j] and j not in ouvertes]
            cand.sort(key=lambda j: rs[i, j] if np.isfinite(rs[i, j]) else 1e9)
            a_entrer = cand[:libres]
    if etat:
        return pd.Series(rend, index=c.index), pd.DataFrame(trades), {
            "ouvertes": {c.columns[j]: {"entree": str(c.index[e_i].date()), "prix": float(e_p),
                                        "gain_latent": float(cv[-1, j] / e_p - 1)} for j, (e_i, e_p) in ouvertes.items()},
            "a_acheter": [c.columns[j] for j in a_entrer], "a_vendre": [c.columns[j] for j in a_sortir],
            "ventes_limites_demain": {c.columns[j]: round(float(L), 4) for j, L in limites.items() if j in ouvertes}}
    return pd.Series(rend, index=c.index), pd.DataFrame(trades)


def mesures(r, t, a, b):
    x = r.loc[a:b]
    tt = t[(t.entree >= pd.Timestamp(a)) & (t.entree <= pd.Timestamp(b))] if len(t) else t
    c = (1 + x).cumprod()
    ans = max((x.index[-1] - x.index[0]).days / 365.25, 0.1)
    mois = (1 + x).resample("ME").prod() - 1
    g, p = tt.rendement[tt.rendement > 0].sum(), -tt.rendement[tt.rendement <= 0].sum()
    return {"trades": int(len(tt)), "reussite": float((tt.rendement > 0).mean()) if len(tt) else None,
            "gain_moyen": float(tt.rendement[tt.rendement > 0].mean()) if (tt.rendement > 0).any() else None,
            "perte_moyenne": float(tt.rendement[tt.rendement <= 0].mean()) if (tt.rendement <= 0).any() else None,
            "pire_trade": float(tt.rendement.min()) if len(tt) else None,
            "profit_factor": float(g / p) if p > 0 else None,
            "rendement_annuel": float(c.iloc[-1] ** (1 / ans) - 1), "pire_baisse": float((c / c.cummax() - 1).min()),
            "sharpe": float(x.mean() / x.std() * np.sqrt(252)) if x.std() > 0 else 0.0,
            "mois_moyen": float(mois.mean()), "mois_median": float(mois.median()), "mois_positifs": float((mois > 0).mean()),
            "pire_mois": float(mois.min()), "meilleur_mois": float(mois.max())}


def ruine(r, annees=5, seuil=-0.5, n=2000, bloc=21, graine=0):
    """Probabilité de perdre au moins 50 % du capital (depuis un sommet) en `annees` ans, bootstrap par blocs de 21 séances."""
    x = r.values[r.values != 0] if (r.values != 0).sum() > 500 else r.values
    x = r.values
    rng = np.random.default_rng(graine)
    T = 252 * annees
    k = 0
    for _ in range(n):
        d = rng.integers(0, len(x) - bloc, T // bloc + 1)
        s = np.concatenate([x[i:i + bloc] for i in d])[:T]
        c = np.cumprod(1 + s)
        k += (c / np.maximum.accumulate(c) - 1).min() <= seuil
    return k / n


def main():
    c = charger()
    ind = indicateurs(c)
    o = {"univers": UNIVERS, "K": K, "variantes": {}}
    resultats = {}
    for nom, v in VARIANTES.items():
        r, t = backtest(c, ind, **v)
        resultats[nom] = (r, t)
        o["variantes"][nom] = {p: mesures(r, t, a, b) for p, (a, b) in PERIODES.items()}
        V.enregistrer_experience("combine:etf16", f"{nom}|K{K}|L1", "-", {"sharpe_choix": o["variantes"][nom]["2000-2015 (choix)"]["sharpe"]})
    choix = max(VARIANTES, key=lambda n: o["variantes"][n]["2000-2015 (choix)"]["sharpe"])
    ok70 = [n for n in VARIANTES if o["variantes"][n]["2000-2015 (choix)"]["reussite"] >= 0.70]
    choix70 = max(ok70, key=lambda n: o["variantes"][n]["2000-2015 (choix)"]["sharpe"]) if ok70 else None
    o["choisie"], o["choisie_70"] = choix, choix70
    cv, m200 = c.values, ind["mm200"].values
    bh = c.pct_change(fill_method=None).mean(axis=1).fillna(0.0)
    o["achat_conservation"] = {p: mesures(bh, pd.DataFrame(columns=["entree", "rendement"]), a, b) for p, (a, b) in PERIODES.items()}
    o["hasard"], o["levier"] = {}, {}
    for nom in dict.fromkeys([choix, choix70]):
        if nom is None:
            continue
        v = VARIANTES[nom]
        # Hasard : mêmes sorties, entrées tirées au hasard au-dessus de la moyenne 200, même fréquence de signaux
        vrai = (ind["rsi"].values < v["seuil"]) & (cv > m200)
        freq = vrai.sum() / max((cv > m200).sum(), 1)
        hz = []
        for g in range(50):
            rng = np.random.default_rng(g)
            sgn = (rng.random(cv.shape) < freq) & (cv > m200)
            rh, th = backtest(c, ind, signal=sgn, **v)
            hz.append(mesures(rh, th, "2000-01-01", "2100-01-01"))
        tout = mesures(*resultats[nom], "2000-01-01", "2100-01-01")
        o["hasard"][nom] = {"reussite_mediane": float(np.median([h["reussite"] for h in hz])),
                            "sharpe_median": float(np.median([h["sharpe"] for h in hz])),
                            "percentile_sharpe": float(np.mean([h["sharpe"] < tout["sharpe"] for h in hz])),
                            "percentile_reussite": float(np.mean([h["reussite"] < tout["reussite"] for h in hz]))}
        o["levier"][nom] = {}
        for Lv in (1, 2, 3, 4, 6, 10):
            r, t = backtest(c, ind, levier=float(Lv), **v)
            o["levier"][nom][Lv] = {"tout": mesures(r, t, "2000-01-01", "2100-01-01"),
                                    "test": mesures(r, t, *PERIODES["2022 → aujourd'hui (test)"]), "ruine_5ans": ruine(r)}
            V.enregistrer_experience("combine:etf16", f"{nom}|K{K}|L{Lv}", "-", {"sharpe_tout": o["levier"][nom][Lv]["tout"]["sharpe"]})
    (ICI / "rapports" / "combine.json").write_text(json.dumps(o, indent=1, ensure_ascii=False, default=str))
    rapport(o)


def pc(x, d=1):
    return "—" if x is None else f"{x * 100:+.{d}f} %"


def rapport(o):
    L = ["# Stratégie combinée à haut taux de réussite\n", "Commande : `python3 -m labo.combine` · règles fixées avant exécution : en-tête de `labo/combine.py`.\n",
         "## Les 4 variantes (levier 1, 5 positions max de 20 %)\n",
         "| Variante | Période | Trades | Réussite | Gain moyen | Perte moyenne | Pire trade | Profit factor | Rendement/an | Pire baisse | Sharpe | Mois positifs | Mois moyen | Pire mois |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, d in o["variantes"].items():
        for p, m in d.items():
            tag = (" ← choix Sharpe" if n == o["choisie"] else "") + (" ← choix ≥ 70 %" if n == o.get("choisie_70") else "")
            L.append(f"| {n}{tag} | {p} | {m['trades']} | {pc(m['reussite'], 0)} | {pc(m['gain_moyen'])} | {pc(m['perte_moyenne'])} | "
                     f"{pc(m['pire_trade'])} | {'—' if m['profit_factor'] is None else format(m['profit_factor'], '.2f')} | {pc(m['rendement_annuel'])} | "
                     f"{pc(m['pire_baisse'], 0)} | {m['sharpe']:.2f} | {m['mois_positifs'] * 100:.0f} % | {pc(m['mois_moyen'], 2)} | {pc(m['pire_mois'])} |")
    L += ["\n**Achat-conservation équipondéré des 16 ETF (référence)** :\n", "| Période | Rendement/an | Pire baisse | Sharpe | Mois positifs | Mois moyen | Pire mois |", "|---|---|---|---|---|---|---|"]
    for p, m in o["achat_conservation"].items():
        L.append(f"| {p} | {pc(m['rendement_annuel'])} | {pc(m['pire_baisse'], 0)} | {m['sharpe']:.2f} | {m['mois_positifs'] * 100:.0f} % | {pc(m['mois_moyen'], 2)} | {pc(m['pire_mois'])} |")
    L += ["\n## Curseur de levier — ce que coûtent des gains plus gros\n"]
    for nom in o["levier"]:
        h = o["hasard"][nom]
        etiquette = "choix initial (Sharpe)" if nom == o["choisie"] else "choix sous contrainte ≥ 70 % de réussite"
        if nom == o["choisie"] and nom == o.get("choisie_70"):
            etiquette = "choix initial et contrainte 70 %"
        L += [f"\n### {nom} — {etiquette}\n",
              f"**Entrées au hasard, mêmes sorties (50 tirages)** : réussite médiane {h['reussite_mediane'] * 100:.0f} %, "
              f"Sharpe médian {h['sharpe_median']:.2f} ; la stratégie bat {h['percentile_reussite'] * 100:.0f} % des tirages en réussite et "
              f"{h['percentile_sharpe'] * 100:.0f} % en Sharpe.\n",
              "| Levier | Réussite | Rendement/an (2000 → auj.) | Mois moyen | Mois médian | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for Lv, d in o["levier"][nom].items():
            m, t = d["tout"], d["test"]
            L.append(f"| ×{Lv} | {pc(m['reussite'], 0)} | {pc(m['rendement_annuel'])} | {pc(m['mois_moyen'], 2)} | {pc(m['mois_median'], 2)} | {m['mois_positifs'] * 100:.0f} % | "
                     f"{pc(m['pire_mois'])} | {pc(m['pire_baisse'], 0)} | {pc(t['rendement_annuel'])}, {pc(t['pire_baisse'], 0)} | {d['ruine_5ans'] * 100:.0f} % |")
    L += ["\nLevier ×L = chaque position pèse L × 20 % ; au-delà de 100 % investi, emprunt à 5 %/an. Risque de ruine estimé par "
          "rééchantillonnage de l'historique (blocs d'un mois) : il ne contient pas de krach pire que ceux déjà vus.\n"]
    (ICI / "rapports" / "combine.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
