"""Audit 03 — « Aladdin momentum crypto » (momentum 120 j | crypto | vol cible), walk-forward +22 %/an, coffre-fort +5,5 %.

Tests : reproduction et décomposition du walk-forward, coûts ×2/×3, retard d'exécution, crises, 5 % de jours retirés,
lookback voisins, réglages du desk risque, retrait d'un actif, univers « point dans le temps » (grandes cryptos de janvier 2020),
volatilité réalisée vs cible, corrélation des positions, bootstrap par blocs, Deflated Sharpe Ratio.

Usage : cd projets/bot-trading && python3 audit/a03_momentum.py
"""
import math

import numpy as np
import pandas as pd

import commun
from aladdin import desks, donnees, moteur, recherche

COFFRE = "2025-01-01"
rng = np.random.default_rng(20261020)
out = ["# Audit 03 — Aladdin momentum crypto\n"]
px = commun.prix()
CRY = ["BTC", "ETH", "BNB", "SOL", "XRP"]


def strat(p, lb=120, vol_cible=0.15, fenetre=60, retard=0, gestion="vol cible"):
    sig = desks.desk_momentum(p, lb)
    if gestion == "vol cible":
        w = desks.desk_risque(p, sig, vol_cible, fenetre)
    else:
        w = desks.poids_egaux(sig.where(p.notna()))
    if retard:
        w = w.shift(retard).fillna(0.0)
    return moteur.portefeuille(p, w), w


def resume(r):
    a = moteur.stats(r, fin="2024-12-31")
    b = moteur.stats(r, debut=COFFRE)
    return a, b


def ligne(nom, r):
    a, b = resume(r)
    return (f"| {nom} | {commun.pct(a['par_an'])} | {commun.pct(a['pire_baisse'])} | {a['sharpe']:.2f} | "
            f"{commun.pct(b['rendement'])} | {commun.pct(b['pire_baisse'])} | {b['sharpe']:.2f} |")


ENTETE = ["| Variante | ≤2024 /an | ≤2024 pire baisse | ≤2024 Sharpe | 2025+ total | 2025+ pire baisse | 2025+ Sharpe |",
          "|---|---|---|---|---|---|---|"]

# ------------------------------------------------------------------ 1. reproduction + décomposition du walk-forward
cands = recherche.candidats(px)
choix, morceaux = [], []
for y in recherche.ANNEES_WF:
    passe = f"{y - 1}-12-31"
    finis = {k: recherche.sharpe(c["rend"].loc[:passe]) for k, c in cands.items()}
    meilleur = max(cands, key=lambda k: finis[k])
    choix.append((y, meilleur, sum(np.isfinite(v) for v in finis.values()),
                  sum(np.isfinite(v) for k, v in finis.items() if "| crypto |" in k)))
    morceaux.append(cands[meilleur]["rend"].loc[f"{y}-01-01":f"{y}-12-31"])
wf = pd.concat(morceaux)
st = moteur.stats(wf)
r0, w0 = strat(px[CRY])
final = recherche.UNIVERS["crypto"]
ref_r = cands["momentum 120 j | crypto | vol cible"]["rend"]
out += ["## 1. Reproduction et décomposition\n",
        f"- Walk-forward reproduit : {commun.pct(st['rendement'])} ({commun.pct(st['par_an'])}/an), pire baisse {commun.pct(st['pire_baisse'])}, "
        f"Sharpe {st['sharpe']:.2f} (rapport : +401,8 %, +22,3 %/an, -33,2 %, 1,37).",
        f"- Coffre-fort reproduit (données au {px.index[-1].date()}, 2 jours de plus que le rapport) : "
        f"{commun.pct(moteur.stats(ref_r, debut=COFFRE)['rendement'])} (rapport : +5,5 % au 2026-10-14).",
        f"- Moteur d'audit identique à recherche.candidats : {np.allclose(r0.values, ref_r.values)}",
        f"- Données crypto Binance : début 2020-01-01 (bot/data.py:31 `debut=\"2020-01-01\"`) ; SOL dès 2020-08-11.\n",
        "| Année WF | Structure choisie | Candidats évaluables (Sharpe fini) | dont crypto | Résultat |", "|---|---|---|---|---|"]
for (y, k, n, nc), m in zip(choix, morceaux):
    out.append(f"| {y} | {k} | {n}/48 | {nc}/24 | {commun.pct((1 + m).prod() - 1)} |")
wf_crypto = pd.concat([m for (y, k, _, _), m in zip(choix, morceaux) if "| crypto |" in k])
out.append(f"\n→ Le walk-forward +22 %/an n'est PAS celui de la structure présentée : 6 années sur 8 viennent de moyennes mobiles "
           f"multi-actifs. Années où une structure crypto a été choisie (2023-2024) : {commun.pct((1 + wf_crypto).prod() - 1)} cumulé. "
           f"La structure finale « momentum 120 j | crypto | vol cible » n'a été hors échantillon qu'en 2024 (WF) et 2025+ (coffre).")
an = (1 + r0).groupby(r0.index.year).prod() - 1
out.append("\nRésultat annuel de la structure finale : " + ", ".join(f"{y} {commun.pct(v)}" for y, v in an.items()))
btc = px["BTC"].pct_change().fillna(0)
bta = (1 + btc).groupby(btc.index.year).prod() - 1
out.append("\nBTC gardé : " + ", ".join(f"{y} {commun.pct(v)}" for y, v in bta.items()))

# ------------------------------------------------------------------ 2. coûts, retard
out += ["\n## 2. Coûts et exécution\n"] + ENTETE
out.append(ligne("Référence (frais 0,15 %/rotation, clôture 00:00 UTC)", r0))
sauve = dict(donnees.FRAIS)
for m in (2, 3):
    donnees.FRAIS["crypto"] = sauve["crypto"] * m
    out.append(ligne(f"Frais ×{m}", strat(px[CRY])[0]))
donnees.FRAIS.update(sauve)
out.append(ligne("Exécution 1 jour plus tard", strat(px[CRY], retard=1)[0]))
out.append(ligne("Exécution 2 jours plus tard", strat(px[CRY], retard=2)[0]))
rot = w0.shift(1).fillna(0).diff().abs().sum(axis=1)
out.append(f"\nRotation moyenne {rot.mean() * 365:.1f}× le capital par an → frais annuels ≈ {rot.mean() * 365 * 0.0015 * 100:.2f} % au tarif de base.")

# ------------------------------------------------------------------ 3. paramètres voisins
out += ["\n## 3. Paramètres voisins\n"] + ENTETE
for lb in (60, 90, 100, 110, 120, 130, 140, 150, 180, 250):
    out.append(ligne(f"lookback {lb} j", strat(px[CRY], lb=lb)[0]))
for vc in (0.10, 0.20, 0.30):
    out.append(ligne(f"lookback 120, vol cible {vc:.0%}", strat(px[CRY], vol_cible=vc)[0]))
for fe in (45, 90):  # 30 impossible : min_periods=40 codé en dur (desks.py:51)
    out.append(ligne(f"lookback 120, fenêtre vol {fe} j", strat(px[CRY], fenetre=fe)[0]))
out.append(ligne("lookback 120, parts égales", strat(px[CRY], gestion="égales")[0]))

# ------------------------------------------------------------------ 4. univers : survivance
out += ["\n## 4. Univers (biais de survivance)\n"] + ENTETE
for a in CRY:
    reste = [x for x in CRY if x != a]
    out.append(ligne(f"sans {a}", strat(px[reste])[0]))
for a in CRY:
    out.append(ligne(f"{a} seul", strat(px[[a]])[0]))
ext = {}
for s in ["ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"]:
    ext[s.replace("USDT", "")] = pd.read_csv(commun.RACINE / "data" / f"{s}.csv", index_col=0, parse_dates=True)["close"]
dix = pd.concat([px[CRY], pd.DataFrame(ext).reindex(px.index)], axis=1).loc[:"2026-10-14"]
out.append(ligne("10 cryptos de bot/data.py (+ADA DOGE AVAX LINK DOT)", strat(dix)[0]))
# Univers point-dans-le-temps : 8 plus grosses cryptos non-stables listées sur Binance au 1er janvier 2020
pit = {}
for s in ["BTCUSDT", "ETHUSDT", "XRPUSDT", "BCHUSDT", "LTCUSDT", "EOSUSDT", "BNBUSDT", "XTZUSDT"]:
    d = commun.binance(s)
    if len(d):
        pit[s.replace("USDT", "")] = d["close"]
pdt = pd.DataFrame(pit).reindex(px.index)
out.append(ligne(f"Point-dans-le-temps janv. 2020 ({', '.join(pit)})", strat(pdt)[0]))
out.append("\n(Univers point-dans-le-temps : capitalisations de janvier 2020 de mémoire d'auditeur — BSV exclu car retiré de Binance en 2019 ; "
           "LUNA/FTT non inclus faute de série propre : le symbole LUNAUSDT a été réattribué en 2022.)")

# ------------------------------------------------------------------ 5. crises
out += ["\n## 5. Crises\n", "| Fenêtre | Stratégie | Pire baisse stratégie | BTC gardé |", "|---|---|---|---|"]
for nom, d, f in (("Krach mars 2020", "2020-02-15", "2020-04-30"), ("Mai-juil. 2021", "2021-05-01", "2021-07-31"),
                  ("LUNA mai 2022", "2022-05-01", "2022-06-30"), ("Année 2022", "2022-01-01", "2022-12-31"),
                  ("FTX nov. 2022", "2022-11-01", "2022-11-30")):
    rr = r0.loc[d:f]
    c = (1 + rr).cumprod()
    out.append(f"| {nom} | {commun.pct(c.iloc[-1] - 1)} | {commun.pct((c / c.cummax() - 1).min())} | {commun.pct((1 + btc.loc[d:f]).prod() - 1)} |")
out.append(f"\nPire jour de la stratégie : {commun.pct(r0.min())} ({r0.idxmin().date()}) ; pire semaine glissante "
           f"{commun.pct(((1 + r0).rolling(7).apply(np.prod, raw=True) - 1).min())}")

# ------------------------------------------------------------------ 6. corrélation, vol réalisée
rend = px[CRY].pct_change().loc["2021-01-01":]
cm = rend.corr().values
moy_corr = cm[np.triu_indices(5, 1)].mean()
vol_r = r0.loc["2021-01-01":].std() * math.sqrt(365)
vol_inv = r0[r0 != 0].loc["2021-01-01":].std() * math.sqrt(365)
expo = w0.sum(axis=1).loc["2021-01-01":]
out += ["\n## 6. Corrélation des positions et volatilité réalisée\n",
        f"- Corrélation moyenne des rendements quotidiens entre les 5 cryptos (2021+) : **{moy_corr:.2f}**",
        f"- desk_risque divise par √n (desks.py:55) comme si les actifs étaient indépendants ; vol réalisée de la stratégie 2021+ : "
        f"{vol_r * 100:.1f} %/an (cible 15 %), {vol_inv * 100:.1f} %/an les jours investis ; exposition brute moyenne {expo.mean() * 100:.0f} %, max {expo.max() * 100:.0f} %"]

# ------------------------------------------------------------------ 7. données manquantes
res = []
for k in range(50):
    garde = px.index[rng.random(len(px)) > 0.05]
    p2 = px.loc[garde, CRY]
    r2, _ = strat(p2)
    a, b = resume(r2)
    res.append((a["sharpe"], a["par_an"], b["rendement"]))
r = np.array(res)
out += ["\n## 7. 5 % des jours retirés au hasard (50 tirages)\n",
        f"- Sharpe ≤2024 : médiane {np.median(r[:, 0]):.2f} [{r[:, 0].min():.2f} – {r[:, 0].max():.2f}] ; par an ≤2024 médiane {commun.pct(np.median(r[:, 1]))}",
        f"- Coffre 2025+ : médiane {commun.pct(np.median(r[:, 2]))} [{commun.pct(r[:, 2].min())} – {commun.pct(r[:, 2].max())}]"]

# ------------------------------------------------------------------ 8. bootstrap par blocs : pertes, drawdown, ruine
rv = r0.loc["2020-03-01":].values
for horizon in (1, 3):
    n = 365 * horizon
    dd, fin = [], []
    for _ in range(5000):
        idx = []
        while len(idx) < n:
            d0 = rng.integers(0, len(rv) - 30)
            idx += list(range(d0, d0 + 30))
        c = np.cumprod(1 + rv[idx[:n]])
        dd.append((c / np.maximum.accumulate(c) - 1).min())
        fin.append(c[-1] - 1)
    dd, fin = np.array(dd), np.array(fin)
    if horizon == 1:
        out += ["\n## 8. Bootstrap par blocs de 30 jours (rendements quotidiens 2020-03 → 2026-10 ; 5 000 tirages)\n",
                "Hypothèse : le futur ressemble à 2020-2026 (un seul cycle crypto, haussier) ; blocs de 30 j pour garder l'autocorrélation.\n"]
    out.append(f"- Horizon {horizon} an(s) : P(perte) = {(fin < 0).mean():.0%} ; pire baisse médiane {commun.pct(np.median(dd))}, "
               f"5e centile {commun.pct(np.percentile(dd, 5))} ; P(baisse ≥ 30 %) = {(dd <= -0.30).mean():.1%} ; P(baisse ≥ 50 %) = {(dd <= -0.50).mean():.2%}")
mois = (1 + r0.loc["2020-03-01":]).resample("ME").prod() - 1
out.append(f"- Mois perdants : {(mois < 0).mean():.0%} ({(mois < 0).sum()}/{len(mois)}) ; pire mois {commun.pct(mois.min())}")

# ------------------------------------------------------------------ 9. Deflated Sharpe Ratio
srs = []
for k, c in cands.items():
    rr = c["rend"].loc[:"2024-12-31"]
    rr = rr[rr.index >= rr.ne(0).idxmax()] if rr.ne(0).any() else rr
    if rr.std() > 0:
        srs.append(rr.mean() / rr.std())
v = float(np.var(srs, ddof=1))
rs = r0.loc[:"2024-12-31"]
rs = rs[rs.index >= rs.ne(0).idxmax()]
out += ["\n## 9. Deflated Sharpe Ratio (rendements quotidiens de la structure finale, période de sélection ≤ 2024)\n",
        f"Essais : 48 candidats de recherche.py (+ sélection walk-forward annuelle) ; variance des Sharpe quotidiens des 48 = {v:.2e}. "
        "Le projet a aussi testé auparavant bot/ (5-7 agents crypto) et l'or : N=100 est une borne plus honnête.\n",
        "| Essais N | Sharpe annuel observé | Sharpe max attendu sous H0 | PSR(0) | DSR |", "|---|---|---|---|---|"]
for n_e in (1, 48, 100):
    d = commun.dsr(rs.values, n_e, v)
    out.append(f"| {n_e} | {d['sr_periode'] * math.sqrt(365):.2f} | {d['sr0_periode'] * math.sqrt(365):.2f} | {d['psr_vs_0']:.3f} | **{d['dsr']:.3f}** |")
d = commun.dsr(r0.loc[COFFRE:].values, 1, v)
out.append(f"\nCoffre 2025+ seul : Sharpe annuel {d['sr_periode'] * math.sqrt(365):.2f}, PSR(Sharpe>0) = {d['psr_vs_0']:.2f} (T = {d['T']} jours).")

(commun.SORTIES / "a03_momentum.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
