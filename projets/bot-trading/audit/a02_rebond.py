"""Audit 02 — « Aladdin Rebond » (RSI2<5 & cours > MM200 ; objectif +1 %, stop -10 %, 20 séances ; SPY + or 50/50).

Moteur générique `simuler_g` vérifié identique à aladdin.reussite.simuler (décalage 1/1) sur les séances
(c'est enquete.executer → sorties.py qui produit 84/78/79 %).
Tests : reproduction, coûts ×2/×3, exécution (même clôture, ouverture suivante, +1 jour), GLD au lieu de GC=F,
moteur 7j/7 de live_rebond, crises, 5 % de séances retirées, paramètres voisins, entrées aléatoires (hasard),
portefeuille vs somme des trades, bootstrap (pertes, drawdown, ruine), Deflated Sharpe Ratio.

Usage : cd projets/bot-trading && python3 audit/a02_rebond.py
"""
import itertools
import math

import numpy as np
import pandas as pd

import commun
from aladdin import desks, enquete, reussite
from aladdin.donnees import FRAIS

P_APP, P_VAL, P_VER = ("2006-01-01", "2019-12-31"), ("2020-01-01", "2024-12-31"), ("2025-01-01", "2100-01-01")
BASE = {"seuil": 5, "tp": 0.01, "sl": 0.10, "duree": 20}
F_AUTRE = FRAIS["autre"]
rng = np.random.default_rng(20261020)
out = ["# Audit 02 — Aladdin Rebond\n"]


# ------------------------------------------------------------------ moteur
def simuler_g(close, opn, sig, tp, sl, duree, frais, lag_in=1, lag_out=1, ouverture=False):
    """Généralise reussite.simuler. lag_in/lag_out = séances entre le signal (ou le déclenchement) et l'exécution.
    ouverture=True : entrée à l'ouverture de i+1, sortie à l'ouverture qui suit le déclenchement.
    Renvoie une liste (e, s, prix_e, prix_s, rendement_net, ouvert)."""
    n, tr, i = len(close), [], 0
    while i < n - 1 - (1 if ouverture else lag_in):
        if not sig[i]:
            i += 1
            continue
        if ouverture:
            e = i + 1
            px_e = opn[e]
            j = e - 1
        else:
            e = i + lag_in
            px_e = close[e]
            j = e
        fin = False
        while j < n - 1:
            j += 1
            g = close[j] / px_e - 1
            fin = (j - e) >= duree or (tp and g >= tp) or (sl and g <= -sl)
            if fin:
                break
        if ouverture:
            s = min(j + 1, n - 1)
            px_s = opn[s] if fin and s > j else close[s]
        else:
            s = min(j + lag_out, n - 1)
            px_s = close[s]
        tr.append((e, s, px_e, px_s, px_s / px_e * (1 - 2 * frais) - 1, not fin or s < j + (1 if ouverture else lag_out)))
        i = max(s, i + 1)
    return tr


def signal(c, seuil, filtre=200):
    r = desks.rsi(c.to_frame(), 2).iloc[:, 0].values
    return (r < seuil) & (c.values > c.rolling(filtre).mean().values)


def courbe_actif(c, opn, tr, frais, ouverture=False):
    """Rendement quotidien de la poche (séances de l'actif), frais à l'entrée et à la sortie."""
    cv = c.values
    r = np.zeros(len(c))
    for e, s, px_e, px_s, _, _ in tr:
        if ouverture:
            r[e] += cv[e] / px_e - 1
            prem = e + 1
        else:
            prem = e + 1
        for k in range(prem, s + 1):
            base = cv[k - 1]
            fin_px = px_s if k == s else cv[k]
            r[k] += fin_px / base - 1
        r[e if ouverture else min(e + 1, len(c) - 1)] -= frais
        r[s] -= frais
    return pd.Series(r, index=c.index)


def lancer(series, regle=BASE, frais_mult=1.0, lag_in=1, lag_out=1, ouverture=False, opens=None):
    """series : {actif: série de clôtures en séances}. Renvoie (trades DataFrame, portefeuille quotidien 50/50)."""
    lignes, poches = [], {}
    for a, c in series.items():
        f = F_AUTRE * frais_mult
        sig = signal(c, regle["seuil"])
        o = opens[a].reindex(c.index).values if opens is not None else None
        tr = simuler_g(c.values, o, sig, regle["tp"], regle["sl"], regle["duree"], f, lag_in, lag_out, ouverture)
        for e, s, pe, ps, x, ouvert in tr:
            lignes.append({"actif": a, "entree": c.index[e], "sortie": c.index[s], "rendement": x, "ouvert": ouvert,
                           "seances": s - e})
        poches[a] = courbe_actif(c, o, tr, f, ouverture)
    t = pd.DataFrame(lignes)
    df = pd.concat(poches, axis=1, sort=True).fillna(0.0)
    port = df.mean(axis=1)
    return t, port


def note(t, p):
    t = t[(t.entree >= pd.Timestamp(p[0])) & (t.entree <= pd.Timestamp(p[1]))]
    if len(t) == 0:
        return {"n": 0, "reussite": np.nan, "pf": np.nan, "gain": np.nan, "perte": np.nan, "pire": np.nan, "k": 0}
    g, l = t.rendement[t.rendement > 0], t.rendement[t.rendement <= 0]
    return {"n": len(t), "k": int((t.rendement > 0).sum()), "reussite": (t.rendement > 0).mean(),
            "pf": g.sum() / -l.sum() if len(l) and l.sum() < 0 else np.inf,
            "gain": g.mean() if len(g) else np.nan, "perte": l.mean() if len(l) else np.nan, "pire": t.rendement.min()}


def ligne(nom, t, port):
    a, v, w = note(t, P_APP), note(t, P_VAL), note(t, P_VER)
    st = commun.stats_quotidien(port.loc["2006-10-01":], 252)
    return (f"| {nom} | {a['reussite'] * 100:.0f} % ({a['n']}) | {v['reussite'] * 100:.0f} % ({v['n']}) | "
            f"{w['reussite'] * 100:.0f} % ({w['n']}) | {a['pf']:.2f} / {v['pf']:.2f} / {w['pf']:.2f} | "
            f"{commun.pct(st['par_an'])} | {commun.pct(st['pire_baisse'])} | {st['sharpe']:.2f} |")


ENTETE = ["| Variante | Réussite 2006-19 (n) | 2020-24 (n) | 2025+ (n) | PF app/val/2025+ | Portefeuille /an | Pire baisse | Sharpe (252) |",
          "|---|---|---|---|---|---|---|---|"]

# ------------------------------------------------------------------ données
px = commun.prix()
S = {"ACTIONS": commun.seances(px["ACTIONS"]), "OR": commun.seances(px["OR"])}
spy = commun.yahoo_ohlc("SPY")
gld = commun.yahoo_ohlc("GLD")
fac_spy = spy.adjclose / spy.close
fac_gld = gld.adjclose / gld.close
S_GLD = {"ACTIONS": S["ACTIONS"], "OR": gld.adjclose.dropna()}
OPENS = {"ACTIONS": (spy.open * fac_spy), "OR": (gld.open * fac_gld)}
S_OPEN = {"ACTIONS": spy.adjclose.dropna(), "OR": gld.adjclose.dropna()}

# ------------------------------------------------------------------ 1. reproduction
st_ref = {"actifs": ["ACTIONS", "OR"], "regle": {"entree": "rsi2", "seuil": 5, "mm5": False, "tp": 0.01, "sl": 0.10, "duree": 20}}
ref = enquete.executer(px, st_ref)
t0, port0 = lancer(S)
egal = (len(ref) == len(t0) and np.allclose(ref.sort_values(["actif", "entree"]).rendement.values,
                                             t0.sort_values(["actif", "entree"]).rendement.values))
out += ["## 1. Reproduction\n",
        f"- `enquete.executer` (moteur de sorties.py) : {len(ref)} trades ; moteur d'audit : {len(t0)} trades ; identiques : **{egal}**",
        f"- Réussite reproduite : 2006-19 {note(ref, P_APP)['reussite'] * 100:.1f} % ({note(ref, P_APP)['n']}), "
        f"2020-24 {note(ref, P_VAL)['reussite'] * 100:.1f} % ({note(ref, P_VAL)['n']}), 2025+ {note(ref, P_VER)['reussite'] * 100:.1f} % "
        f"({note(ref, P_VER)['n']}) — rapport : 84 / 78 / 79 %, 89 / 40 / 14 trades.",
        f"- Premier trade : {t0.entree.min().date()} (le libellé « 2008-2019 » de sorties.py couvre en fait 2006-2019).",
        f"- Trades encore ouverts comptés comme clos (valorisés à la dernière clôture) : {int(t0.ouvert.sum())}"]
for a in S:
    k = ref[ref.actif == a]
    out.append(f"- {a} : {len(k)} trades, réussite {(k.rendement > 0).mean() * 100:.0f} %")

w = note(t0, P_VER)
lo, hi = commun.wilson(w["k"], w["n"])
lo2, hi2 = commun.wilson(note(t0, P_VAL)["k"], note(t0, P_VAL)["n"])
out.append(f"- Intervalle de confiance 95 % (Wilson) de la réussite 2025+ : {lo * 100:.0f}–{hi * 100:.0f} % ; 2020-24 : {lo2 * 100:.0f}–{hi2 * 100:.0f} %")

# Somme des log-rendements des trades (affichée par sorties.py) vs portefeuille réel 50/50
for nom, p in (("2020-24", P_VAL), ("2025+", P_VER)):
    tt = t0[(t0.entree >= p[0]) & (t0.entree <= p[1])]
    pr = port0.loc[p[0]:p[1]]
    out.append(f"- « Rendement cumulé des trades » {nom} (somme des log, enquete.py:111, affiché par sorties.py) : {np.log1p(tt.rendement).sum() * 100:+.0f} % "
               f"vs portefeuille 50/50 réel : {commun.pct((1 + pr).prod() - 1)}")
st = commun.stats_quotidien(port0.loc["2006-10-01":], 252)
bh = pd.concat([S["ACTIONS"].pct_change(), S["OR"].pct_change()], axis=1, sort=True).fillna(0).mean(axis=1)
sb = commun.stats_quotidien(bh.loc["2006-10-01":], 252)
out.append(f"- Portefeuille Rebond 2006-10→fin : {commun.pct(st['par_an'])}/an, pire baisse {commun.pct(st['pire_baisse'])}, Sharpe {st['sharpe']:.2f}, "
           f"exposition {st['exposition_jours'] * 100:.0f} % des séances ; 50/50 SPY+or gardé : {commun.pct(sb['par_an'])}/an, "
           f"pire baisse {commun.pct(sb['pire_baisse'])}, Sharpe {sb['sharpe']:.2f}")
g, l = t0.rendement[t0.rendement > 0], t0.rendement[t0.rendement <= 0]
out.append(f"- Gain moyen {commun.pct(g.mean(), 2)}, perte moyenne {commun.pct(l.mean(), 2)}, pire trade {commun.pct(t0.rendement.min(), 2)} "
           f"→ réussite d'équilibre = {-l.mean() / (g.mean() - l.mean()) * 100:.0f} %")

# ------------------------------------------------------------------ 2. variantes défavorables
out += ["\n## 2. Coûts, exécution, instrument\n"] + ENTETE
out.append(ligne("Référence (clôture suivante, frais 0,05 %)", t0, port0))
for m in (2, 3):
    t, p = lancer(S, frais_mult=m)
    out.append(ligne(f"Frais ×{m} ({F_AUTRE * m * 100:.2f} % par côté)", t, p))
t, p = lancer(S, lag_in=0, lag_out=0)
out.append(ligne("Même clôture que le signal (optimiste, ≈ alpaca.py idéal)", t, p))
t, p = lancer(S, lag_in=2, lag_out=2)
out.append(ligne("Un jour de retard (clôture t+2)", t, p))
t, p = lancer(S_GLD)
out.append(ligne("GLD au lieu de GC=F (instrument réellement traité)", t, p))
t, p = lancer(S_OPEN)
out.append(ligne("SPY+GLD, clôture suivante (base de comparaison)", t, p))
t, p = lancer(S_OPEN, ouverture=True, opens=OPENS)
out.append(ligne("SPY+GLD, ouverture suivante", t, p))
t, p = lancer(S_OPEN, frais_mult=3, ouverture=True, opens=OPENS)
out.append(ligne("SPY+GLD, ouverture suivante + frais ×3", t, p))
# Moteur 7j/7 de live_rebond
port7, tr7 = reussite.portefeuille(px, ["ACTIONS", "OR"], {"entree": "rsi2", "seuil": 5, "mm5": False, "tp": 0.01, "sl": 0.10, "duree": 20})
tr7 = tr7.rename(columns={"date": "entree"})
out.append(ligne("Moteur 7j/7 de reussite.py = celui de live_rebond.py (Sharpe sur 252 non comparable)", tr7, port7))
for a in S:
    t, p = lancer({a: S[a]})
    out.append(ligne(f"{a} seul", t, p))

# ------------------------------------------------------------------ 3. crises
out += ["\n## 3. Périodes de crise (trades entrés dans la fenêtre, portefeuille sur la fenêtre)\n",
        "| Fenêtre | Trades | Réussite | Pire trade | Rendement portefeuille | Pire baisse portefeuille | SPY+or gardé |", "|---|---|---|---|---|---|---|"]
for nom, d, f in (("2008 (crise financière)", "2008-01-01", "2008-12-31"), ("Krach 2020", "2020-02-15", "2020-04-30"),
                  ("2022 (inflation)", "2022-01-01", "2022-12-31"), ("Or : avril 2013", "2013-04-01", "2013-06-30")):
    tt = t0[(t0.entree >= d) & (t0.entree <= f)]
    pr = port0.loc[d:f]
    c = (1 + pr).cumprod()
    out.append(f"| {nom} | {len(tt)} | {(tt.rendement > 0).mean() * 100 if len(tt) else float('nan'):.0f} % | "
               f"{commun.pct(tt.rendement.min() if len(tt) else np.nan)} | {commun.pct(c.iloc[-1] - 1)} | "
               f"{commun.pct((c / c.cummax() - 1).min())} | {commun.pct((1 + bh.loc[d:f]).prod() - 1)} |")
pires = t0.nsmallest(8, "rendement")
out.append("\nLes 8 pires trades : " + "; ".join(f"{r.actif} {r.entree.date()} {commun.pct(r.rendement)} ({r.seances} s.)" for r in pires.itertuples()))
au_dela = (t0.rendement < -BASE["sl"] - 2 * F_AUTRE).sum()
out.append(f"\nTrades sortis au-delà du stop -10 % (écart de cours / exécution le lendemain) : {au_dela}")

# ------------------------------------------------------------------ 4. données manquantes
res = []
for k in range(50):
    S2 = {a: c[rng.random(len(c)) > 0.05] for a, c in S.items()}
    t, p = lancer(S2)
    res.append((note(t, P_APP)["reussite"], note(t, P_VAL)["reussite"], note(t, P_VER)["reussite"], note(t, P_VER)["n"],
                commun.stats_quotidien(p.loc["2006-10-01":], 252)["sharpe"]))
r = np.array(res, dtype=float)
out += ["\n## 4. 5 % des séances retirées au hasard (50 tirages)\n",
        f"- Réussite 2006-19 : médiane {np.median(r[:, 0]) * 100:.0f} % [min {r[:, 0].min() * 100:.0f} – max {r[:, 0].max() * 100:.0f}]",
        f"- Réussite 2020-24 : médiane {np.median(r[:, 1]) * 100:.0f} % [min {r[:, 1].min() * 100:.0f} – max {r[:, 1].max() * 100:.0f}]",
        f"- Réussite 2025+ : médiane {np.median(r[:, 2]) * 100:.0f} % [min {r[:, 2].min() * 100:.0f} – max {r[:, 2].max() * 100:.0f}], trades {r[:, 3].min():.0f}–{r[:, 3].max():.0f}",
        f"- Sharpe portefeuille : médiane {np.median(r[:, 4]):.2f} [min {r[:, 4].min():.2f} – max {r[:, 4].max():.2f}]"]

# ------------------------------------------------------------------ 5. paramètres voisins
out += ["\n## 5. Paramètres voisins (durée max 20 séances)\n",
        "| RSI2 < | Objectif | Stop | Réussite 06-19 | 20-24 | 2025+ | PF 06-19 / 20-24 / 25+ | Portefeuille /an | Pire baisse | Sharpe |",
        "|---|---|---|---|---|---|---|---|---|---|"]
grille = []
for seuil, tp, sl in itertools.product((3, 5, 7, 10), (0.005, 0.01, 0.015, 0.02), (0.05, 0.10, 0.15)):
    t, p = lancer(S, {"seuil": seuil, "tp": tp, "sl": sl, "duree": 20})
    a, v, w = note(t, P_APP), note(t, P_VAL), note(t, P_VER)
    s = commun.stats_quotidien(p.loc["2006-10-01":], 252)
    grille.append((seuil, tp, sl, a, v, w, s, p))
    out.append(f"| {seuil} | +{tp * 100:.1f} % | -{sl * 100:.0f} % | {a['reussite'] * 100:.0f} % | {v['reussite'] * 100:.0f} % | "
               f"{w['reussite'] * 100:.0f} % | {a['pf']:.2f} / {v['pf']:.2f} / {w['pf']:.2f} | {commun.pct(s['par_an'])} | "
               f"{commun.pct(s['pire_baisse'])} | {s['sharpe']:.2f} |")
srs = np.array([g_[6]["sharpe"] for g_ in grille])
out.append(f"\nSharpe sur la grille de 48 voisins : min {srs.min():.2f}, médiane {np.median(srs):.2f}, max {srs.max():.2f} ; "
           f"référence {commun.stats_quotidien(port0.loc['2006-10-01':], 252)['sharpe']:.2f}. "
           f"Réussite 2025+ ≥ 70 % pour {sum(g_[5]['reussite'] >= 0.70 for g_ in grille)}/48 voisins.")
for d in (5, 10, 30):
    t, p = lancer(S, {"seuil": 5, "tp": 0.01, "sl": 0.10, "duree": d})
    out.append(f"- Durée max {d} séances : réussite {note(t, P_APP)['reussite'] * 100:.0f} / {note(t, P_VAL)['reussite'] * 100:.0f} / "
               f"{note(t, P_VER)['reussite'] * 100:.0f} %, Sharpe {commun.stats_quotidien(p.loc['2006-10-01':], 252)['sharpe']:.2f}")

# ------------------------------------------------------------------ 6. le hasard avec les mêmes sorties
out.append("\n## 6. Entrées au hasard (cours > MM200, même nombre de trades, mêmes sorties +1 % / -10 % / 20 s.) — 200 tirages\n")
hasard = []
for k in range(200):
    lignes_h = []
    for a, c in S.items():
        tend = c.values > c.rolling(200).mean().values
        n_sig = int(signal(c, 5).sum())
        cand = np.flatnonzero(tend)
        sig = np.zeros(len(c), bool)
        sig[rng.choice(cand, size=n_sig, replace=False)] = True
        tr = simuler_g(c.values, None, sig, 0.01, 0.10, 20, F_AUTRE)
        lignes_h += [{"entree": c.index[e], "rendement": x} for e, s, _, _, x, _ in tr]
    th = pd.DataFrame(lignes_h)
    hasard.append((note(th, ("2006-01-01", "2100")).get("reussite"), note(th, ("2006-01-01", "2100"))["pf"],
                   np.log1p(th.rendement).mean()))
h = np.array(hasard, dtype=float)
tot0 = note(t0, ("2006-01-01", "2100"))
out += [f"- Hasard : réussite médiane {np.median(h[:, 0]) * 100:.0f} % (5e–95e centile {np.percentile(h[:, 0], 5) * 100:.0f}–{np.percentile(h[:, 0], 95) * 100:.0f} %), "
        f"PF médian {np.median(h[:, 1]):.2f}",
        f"- Règle RSI2<5 : réussite {tot0['reussite'] * 100:.0f} %, PF {tot0['pf']:.2f} → centile de la règle parmi le hasard : "
        f"réussite {(h[:, 0] < tot0['reussite']).mean() * 100:.0f}e, log-rendement moyen par trade "
        f"{(h[:, 2] < np.log1p(t0.rendement).mean()).mean() * 100:.0f}e"]

# ------------------------------------------------------------------ 7. bootstrap des trades : pertes, drawdown, ruine
tr_all = t0[~t0.ouvert].rendement.values
par_an = len(tr_all) / ((t0.entree.max() - t0.entree.min()).days / 365.25)
sims, ans = 20000, 10
dd, fin, pertes_an = [], [], []
for _ in range(sims):
    n = rng.poisson(par_an * ans)
    x = rng.choice(tr_all, size=n, replace=True) * 0.5          # chaque trade engage une poche de 50 %
    c = np.cumprod(1 + x)
    c = np.concatenate([[1.0], c])
    dd.append((c / np.maximum.accumulate(c) - 1).min())
    fin.append(c[-1] - 1)
dd, fin = np.array(dd), np.array(fin)
# scénario de choc : un trade à -25 % (gap type 2008/2020 non vu à 20 séances) inséré une fois tous les 10 ans
out += ["\n## 7. Bootstrap des trades (hypothèses explicites)\n",
        f"Hypothèses : {len(tr_all)} trades clos 2006-2026 tirés avec remise ; {par_an:.1f} trades/an (Poisson) ; chaque trade engage 50 % "
        f"du capital (une poche) ; trades indépendants (pas de chevauchement modélisé) ; horizon {ans} ans ; {sims} simulations.\n",
        f"- Fréquence des trades perdants : {(tr_all <= 0).mean() * 100:.0f} % ; probabilité d'au moins 2 pertes sur 10 trades : "
        f"{1 - sum(math.comb(10, k) * (tr_all <= 0).mean() ** k * (1 - (tr_all <= 0).mean()) ** (10 - k) for k in range(2)):.0%}",
        f"- Pire baisse sur 10 ans : médiane {commun.pct(np.median(dd))}, 5e centile {commun.pct(np.percentile(dd, 5))}, 1er centile {commun.pct(np.percentile(dd, 1))}",
        f"- P(pire baisse ≥ 10 %) = {(dd <= -0.10).mean():.1%} ; P(≥ 20 %) = {(dd <= -0.20).mean():.2%} ; P(≥ 50 %, « ruine ») = {(dd <= -0.50).mean():.3%}",
        f"- P(perte sur 10 ans) = {(fin < 0).mean():.2%} ; rendement 10 ans médian {commun.pct(np.median(fin))} "
        f"(≈ {commun.pct((1 + np.median(fin)) ** (1 / ans) - 1)}/an)"]
# avec 100 % du capital par trade (si un seul actif)
dd1 = []
for _ in range(5000):
    x = rng.choice(tr_all, size=rng.poisson(par_an / 2 * ans), replace=True)
    c = np.concatenate([[1.0], np.cumprod(1 + x)])
    dd1.append((c / np.maximum.accumulate(c) - 1).min())
dd1 = np.array(dd1)
out.append(f"- Variante 100 % du capital par trade (un seul actif) : P(pire baisse ≥ 20 %) = {(dd1 <= -0.20).mean():.1%}, "
           f"P(≥ 30 %) = {(dd1 <= -0.30).mean():.1%}")
# bootstrap par blocs du portefeuille quotidien
pv = port0.loc["2006-10-01":].values
ddb = []
for _ in range(2000):
    idx = []
    while len(idx) < 252 * ans:
        d0 = rng.integers(0, len(pv) - 21)
        idx += list(range(d0, d0 + 21))
    c = np.cumprod(1 + pv[idx[:252 * ans]])
    ddb.append((c / np.maximum.accumulate(c) - 1).min())
ddb = np.array(ddb)
out.append(f"- Bootstrap par blocs de 21 séances du portefeuille quotidien (10 ans) : pire baisse médiane {commun.pct(np.median(ddb))}, "
           f"5e centile {commun.pct(np.percentile(ddb, 5))}, P(≥ 20 %) = {(ddb <= -0.20).mean():.1%}")

# ------------------------------------------------------------------ 8. Deflated Sharpe Ratio
r_sel = port0.loc["2006-10-01":"2024-12-31"]
var_grille = float(np.var([commun.stats_quotidien(g_[7].loc["2006-10-01":"2024-12-31"], 252)["sharpe"] / math.sqrt(252) for g_ in grille], ddof=1))
out += ["\n## 8. Deflated Sharpe Ratio (portefeuille quotidien 2006-10 → 2024, période de sélection + validation)\n",
        "Essais comptés dans la lignée Rebond : reussite.py 1 350 combinaisons (+2 méthodes de choix), enquete.py 42 filtres × 2 structures "
        "(+1 validation), sorties.py 180 réglages → **1 572 essais** (1 662 pour tout Aladdin). Variance des Sharpe entre essais estimée sur la grille de 48 voisins "
        f"(par séance) = {var_grille:.2e} (borne basse : des voisins sont très corrélés).\n",
        "| Essais N | Sharpe annuel observé | Sharpe annuel attendu du meilleur sous H0 | PSR(0) | DSR |", "|---|---|---|---|---|"]
for n_e, v in ((1, var_grille), (180, var_grille), (1572, var_grille), (1572, 4 * var_grille)):
    d = commun.dsr(r_sel.values, n_e, v)
    out.append(f"| {n_e}{' (var ×4)' if v != var_grille else ''} | {d['sr_periode'] * math.sqrt(252):.2f} | {d['sr0_periode'] * math.sqrt(252):.2f} | "
               f"{d['psr_vs_0']:.3f} | **{d['dsr']:.3f}** |")
d = commun.dsr(r_sel.values, 1572, var_grille)
out.append(f"\nAsymétrie {d['skew']:.2f}, kurtosis {d['kurt']:.1f}, T = {d['T']} séances. DSR > 0,95 requis pour conclure à un Sharpe > 0 après correction.")

(commun.SORTIES / "a02_rebond.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
