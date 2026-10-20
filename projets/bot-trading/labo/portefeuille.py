"""Portefeuille de tendance multi-instruments (fiche S1 du catalogue : Moskowitz-Ooi-Pedersen 2012, Hurst-Ooi-Pedersen 2017).

Règle fixée AVANT exécution (2026-10-21), sans aucune sélection de paramètres :
- signal par instrument = moyenne des signes des rendements 30, 90 et 180 jours (−1…1) ; long seulement (spot/ETF : 0…1) ;
- budget de risque égal par instrument (signal / vol 30 j), puis mise à l'échelle du portefeuille à 20 %/an de vol
  avec la covariance glissante 90 j ; pas de levier (somme des poids ≤ 100 %) ;
- un instrument n'entre dans l'univers qu'après 400 jours d'historique (pas de cryptos « connues à l'avance ») ;
- décision à la clôture (Binance 00:00 UTC, qui suit la clôture de New York du même jour), exécution à l'ouverture suivante, coûts par instrument.
FX exclu du portefeuille principal (financement non modélisé) ; testé à part comme sensibilité.

Usage : python3 -m labo.portefeuille → rapports/portefeuille_tendance.md / .json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import criteres as K, validation as V
from .couts import Couts
from .moteur import simuler
from .pilote import charger, source

ICI = Path(__file__).resolve().parent.parent
UNIVERS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "LTCUSDT", "SOLUSDT", "GLD", "SPY", "TLT"]
FX = ["EURUSD=X", "USDJPY=X"]
LOOKBACKS = [30, 90, 180]
VOL_PORTEFEUILLE = 0.20
HISTORIQUE_MIN = 400
REGLE = {"version": "portefeuille-tendance-v1-2026-10-21", "lookbacks": LOOKBACKS, "vol_portefeuille": VOL_PORTEFEUILLE,
         "historique_min_jours": HISTORIQUE_MIN, "covariance_jours": 90, "levier_max": 1.0}


def poids(closes, long_seul, vol_cible=VOL_PORTEFEUILLE):
    """closes : DataFrame calendrier quotidien (NaN avant l'existence). Renvoie les poids décidés à chaque clôture."""
    r = closes.pct_change(fill_method=None)
    sig = sum(np.sign(closes / closes.shift(L) - 1) for L in LOOKBACKS) / len(LOOKBACKS)
    if long_seul:
        sig = sig.clip(lower=0)
    age = closes.notna().cumsum()
    sig = sig.where(age >= HISTORIQUE_MIN, 0.0).fillna(0.0)
    vol = r.rolling(30, min_periods=20).std() * np.sqrt(365)
    brut = (sig / vol).replace([np.inf, -np.inf], 0).fillna(0.0)
    cov = r.rolling(90, min_periods=60).cov() * 365
    w = pd.DataFrame(0.0, index=closes.index, columns=closes.columns)
    for t in closes.index:
        b = brut.loc[t]
        if b.abs().sum() == 0 or t not in cov.index.get_level_values(0):
            continue
        c = cov.loc[t].reindex(index=b.index, columns=b.index).fillna(0.0)
        vp = float(np.sqrt(max(b.values @ c.values @ b.values, 0.0)))
        if vp > 0:
            w.loc[t] = b * (vol_cible / vp)
    tot = w.abs().sum(axis=1)
    return w.div(tot.clip(lower=1.0), axis=0)


def executer(symboles, long_seul=True, facteur_couts=1.0, retard=1, signal_constant=None):
    data, cts = {}, {}
    for s in symboles:
        df, _ = charger(s, "1d")
        data[s], cts[s] = df, source(s)["couts"].stresse(facteur_couts, retard=retard)
    closes = pd.DataFrame({s: d.close for s, d in data.items()}).sort_index()
    cal = pd.date_range(closes.index.min(), closes.index.max(), freq="D")
    closes = closes.reindex(cal).ffill().where(closes.reindex(cal).ffill().notna())
    for s in symboles:                                   # NaN avant la première cotation, report ensuite (week-ends)
        premier = data[s].index[0]
        closes.loc[:premier - pd.Timedelta(days=1), s] = np.nan
    w = poids(closes, long_seul) if signal_constant is None else _poids_constant(closes)
    nets = {}
    for s in symboles:
        df = data[s]
        cible = w[s].reindex(df.index, method="ffill").fillna(0.0)      # dernier poids connu à la clôture de la séance
        res = simuler(df, cible, "1d", cts[s], dimensionner=False)
        nets[s] = res["net"].reindex(cal).fillna(0.0)
    port = pd.DataFrame(nets).sum(axis=1)
    return port, w


def _poids_constant(closes):
    """Toujours investi (signal = 1 dès 400 jours d'historique), même budget de risque et même échelle."""
    sig = closes.notna().cumsum().ge(HISTORIQUE_MIN).astype(float)
    r = closes.pct_change(fill_method=None)
    vol = r.rolling(30, min_periods=20).std() * np.sqrt(365)
    brut = (sig / vol).replace([np.inf, -np.inf], 0).fillna(0.0)
    cov = r.rolling(90, min_periods=60).cov() * 365
    w = pd.DataFrame(0.0, index=closes.index, columns=closes.columns)
    for t in closes.index:
        b = brut.loc[t]
        if b.abs().sum() == 0:
            continue
        c = cov.loc[t].reindex(index=b.index, columns=b.index).fillna(0.0)
        vp = float(np.sqrt(max(b.values @ c.values @ b.values, 0.0)))
        if vp > 0:
            w.loc[t] = b * (VOL_PORTEFEUILLE / vp)
    return w.div(w.abs().sum(axis=1).clip(lower=1.0), axis=0)


def mesures(r):
    if len(r) < 30 or r.std() == 0:
        return None
    c = (1 + r).cumprod()
    return {"rendement_annuel": float(c.iloc[-1] ** (365.25 / max((r.index[-1] - r.index[0]).days, 1)) - 1),
            "volatilite": float(r.std() * np.sqrt(365)), "sharpe": V.sharpe_annuel(r),
            "pire_baisse": float((c / c.cummax() - 1).min()),
            "annees_positives": f"{int(((1 + r).groupby(r.index.year).prod() > 1).sum())}/{r.index.year.nunique()}"}


PERIODES = {"developpement (≤2021)": ("2017-01-01", "2021-12-31"), "validation 2022-2023": ("2022-01-01", "2023-12-31"),
            "hors échantillon WF 2019-2023": ("2019-01-01", "2023-12-31"), "2024 → aujourd'hui (déjà vu instrument par instrument)": ("2024-01-01", "2100-01-01")}


def main():
    variantes = {
        "tendance (règle)": executer(UNIVERS)[0],
        "tendance coûts ×3": executer(UNIVERS, facteur_couts=3.0)[0],
        "tendance retard 1 jour": executer(UNIVERS, retard=2)[0],
        "référence : toujours investi, même risque": executer(UNIVERS, signal_constant=True)[0],
        "sensibilité : crypto seulement": executer(UNIVERS[:6])[0],
        "sensibilité : + FX long/short (swap NON modélisé)": executer(UNIVERS + FX, long_seul=False)[0],
    }
    bh = pd.DataFrame({s: charger(s, "1d")[0].close for s in UNIVERS}).sort_index()
    bh = bh.reindex(pd.date_range(bh.index.min(), bh.index.max(), freq="D")).ffill()
    variantes["référence : parts égales achetées-gardées"] = bh.pct_change(fill_method=None).mean(axis=1).fillna(0.0)
    o = {"regle": REGLE, "periodes": {}}
    for p, (a, b) in PERIODES.items():
        o["periodes"][p] = {n: mesures(r.loc[a:b]) for n, r in variantes.items()}
    regle = variantes["tendance (règle)"]
    ref = variantes["référence : toujours investi, même risque"]
    oos = ("2019-01-01", "2023-12-31")
    n_essais = sum(V.nombre_experiences(s) for s in UNIVERS) + 1
    o["dsr"] = {"essais": n_essais, "dsr_var_nulle": V.dsr(regle.loc[oos[0]:oos[1]].values, n_essais, 1 / len(regle.loc[oos[0]:oos[1]]))[0]}
    o["p_superiorite_vs_toujours_investi"] = V.bootstrap_difference(regle.loc[oos[0]:oos[1]], ref.loc[oos[0]:oos[1]])
    o["p_superiorite_vs_toujours_investi_2024plus"] = V.bootstrap_difference(regle.loc["2024-01-01":], ref.loc["2024-01-01":])
    m_oos = o["periodes"]["hors échantillon WF 2019-2023"]
    raisons = []
    if m_oos["tendance (règle)"]["sharpe"] < K.SHARPE_MIN_OOS:
        raisons.append("Sharpe 2019-2023 < 0,5")
    if m_oos["tendance coûts ×3"]["sharpe"] <= 0:
        raisons.append("ne résiste pas aux coûts ×3")
    if o["dsr"]["dsr_var_nulle"] < K.DSR_MIN:
        raisons.append(f"DSR {o['dsr']['dsr_var_nulle']:.2f} < 0,95 avec {n_essais} essais")
    recent = o["periodes"]["2024 → aujourd'hui (déjà vu instrument par instrument)"]["tendance (règle)"]
    if recent["sharpe"] <= 0:
        raisons.append("Sharpe 2024+ ≤ 0")
    o["statut"] = "candidate démo (paper uniquement)" if not raisons else "non validée"
    o["raisons"] = raisons
    (ICI / "rapports" / "portefeuille_tendance.json").write_text(json.dumps(o, indent=1, ensure_ascii=False, default=str))
    L = ["# Portefeuille de tendance multi-instruments\n",
         f"Commande : `python3 -m labo.portefeuille` · règle `{REGLE['version']}` fixée avant exécution (voir l'en-tête de `labo/portefeuille.py`).",
         f"Univers : {', '.join(UNIVERS)} (entrée après {HISTORIQUE_MIN} jours d'historique). Vol cible {VOL_PORTEFEUILLE:.0%}, sans levier.\n"]
    for p, d in o["periodes"].items():
        L += [f"## {p}\n", "| Variante | Rendement/an | Vol | Sharpe | Pire baisse | Années + |", "|---|---|---|---|---|---|"]
        for n, m in d.items():
            if m:
                L.append(f"| {n} | {m['rendement_annuel']:+.1%} | {m['volatilite']:.0%} | {m['sharpe']:.2f} | {m['pire_baisse']:.0%} | {m['annees_positives']} |")
        L.append("")
    L += [f"- DSR (variance nulle, {n_essais} essais cumulés sur l'univers) : {o['dsr']['dsr_var_nulle']:.2f}",
          f"- p (tendance meilleure que « toujours investi, même risque ») : 2019-2023 {o['p_superiorite_vs_toujours_investi']:.3f} · 2024+ {o['p_superiorite_vs_toujours_investi_2024plus']:.3f}",
          f"\n## Statut : **{o['statut']}**\n", f"- Raisons : {'; '.join(raisons) or 'critères démo passés'}",
          "- Données 2024+ déjà vues instrument par instrument dans les fiches : ce n'est pas un test vierge. Seul le suivi papier futur le sera.",
          "- Biais de survivance : les cryptos de l'univers sont celles qui existent encore aujourd'hui (LUNA, FTT absentes)."]
    (ICI / "rapports" / "portefeuille_tendance.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
