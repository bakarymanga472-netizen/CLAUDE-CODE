"""Test des stratégies des 5 vidéos YouTube + boucle d'amélioration du taux de réussite.

Usage : python3 -m labo.videos.tester → rapports/videos_youtube.md / .json

Règles fixées AVANT exécution (2026-10-21) :
- développement ≤ 2023-12-31, test ≥ 2024-01-01 (chronologique) ;
- coûts : crypto 0,24 % du prix aller-retour (2 × 0,10 % de frais + 2 × 0,02 % de glissement) ; forex = spread RÉEL mesuré
  (archive FXCM bid/ask, barre d'entrée) + 0,1 pip de glissement ; stress ×2 ;
- forex : vrai forex FXCM 1 minute (EUR/USD, GBP/USD, AUD/USD, USD/JPY, USD/CAD), 2021 → 2026, agrégé en 5 min / 1 h.
  (Changement de source AVANT le test complet : l'approximation Binance EUR/USDT… avait des mèches de faible liquidité
  qui touchent les stops serrés plus souvent que le vrai marché, et les paires GBP/AUD y ont été retirées en 2023.)
- hasard : mêmes distances de stop, même objectif, entrées tirées au hasard (30 tirages ; 10 en 5 minutes) ;
- améliorations testées (hypothèses déclarées avant) : H1 objectif à 1R ; H2 seulement dans le sens de la moyenne 50 jours ;
  H3 pas de stop plus petit que la moitié de la médiane des stops passés ; H4 = H1 + H2 + H3 ;
  H5 (ajoutée avant exécution, tirée de la vidéo de Roro) : n'entrer que sur une bougie de retournement dans le sens du trade ;
- une amélioration est ACCEPTÉE seulement si, en développement ET en test, la réussite monte ET le R moyen ne baisse pas,
  avec au moins 30 trades en test.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .. import donnees, donnees_fxcm, validation as V
from ..couts import Couts
from ..moteur import simuler
from .. import bracket as B
from . import deleuze, kasper, nico, rayfu, roro
from .outils import sma

ICI = Path(__file__).resolve().parents[2]
FIN_DEV, DEBUT_TEST = "2023-12-31", "2024-01-01"
PAIRES = ["EURUSD", "GBPUSD", "AUDUSD", "USDJPY", "USDCAD"]
N_HASARD = 30


def cout_prix(sym, df, facteur=1.0):
    if "spread" in df.columns:                        # forex : spread réel de la barre d'entrée + 0,1 pip de glissement
        pip = 0.01 if "JPY" in sym else 0.0001
        return ((df.spread + 0.1 * pip) * facteur).values
    return (df.close * 0.0024 * facteur).values


def bpj(df):
    pas = pd.Series(df.index).diff().median()
    return max(int(round(pd.Timedelta(days=1) / pas)), 1)


def variante(df, sig, h):
    s = sig.copy()
    if h in ("H1", "H4"):
        s["tp_R"] = 1.0
    if h in ("H2", "H4"):
        m = sma(df.close, 50 * bpj(df)).reindex(s.index)
        c = df.close.reindex(s.index)
        s = s[((s.sens > 0) & (c > m)) | ((s.sens < 0) & (c < m))]
    if h == "H5":
        o, c = df.open.reindex(s.index), df.close.reindex(s.index)
        s = s[((s.sens > 0) & (c > o)) | ((s.sens < 0) & (c < o))]
    if h in ("H3", "H4"):
        dist = (df.close.reindex(s.index) - s.stop).abs() / df.close.reindex(s.index)
        med = dist.expanding().median().shift(1)
        s = s[(dist >= 0.5 * med) | med.isna()]
    return s


def periode(t, a, b):
    return t[(t.entree_t >= pd.Timestamp(a)) & (t.entree_t <= pd.Timestamp(b))] if len(t) else t


def evaluer_bracket(nom, mod, sym, df, p, be):
    sig = mod.signaux(df, **p)
    cp = cout_prix(sym, df)
    base = B.executer(df, sig, cp, be_R=be)
    res = {"strategie": nom, "symbole": sym, "params": p, "donnees": f"{df.index[0].date()} → {df.index[-1].date()} ({len(df)} barres)",
           "dev": B.mesures(periode(base, "1900", FIN_DEV)), "test": B.mesures(periode(base, DEBUT_TEST, "2100")),
           "tout": B.mesures(base), "stress_couts_x2": B.mesures(B.executer(df, sig, cout_prix(sym, df, 2.0), be_R=be))}
    n_h = N_HASARD if len(df) < 100_000 else 10          # 5 minutes : 10 tirages (temps de calcul)
    hz = [B.hasard(df, sig, cp, g, be_R=be) for g in range(n_h)]
    rh = [x.R.mean() for x in hz if len(x)]
    wh = [(x.R > 0).mean() for x in hz if len(x)]
    res["hasard"] = {"R_moyen_median": float(np.median(rh)) if rh else None, "reussite_mediane": float(np.median(wh)) if wh else None,
                     "percentile_R": float((np.array(rh) < res["tout"].get("R_moyen", -9)).mean()) if rh else None}
    res["ameliorations"] = {}
    for h in ("H1", "H2", "H3", "H4", "H5"):
        tv = B.executer(df, variante(df, sig, h), cp, be_R=be)
        d, t = B.mesures(periode(tv, "1900", FIN_DEV)), B.mesures(periode(tv, DEBUT_TEST, "2100"))
        ok = all(x.get("trades", 0) and y.get("trades", 0) and x["reussite"] > y["reussite"] and x["R_moyen"] >= y["R_moyen"]
                 for x, y in ((d, res["dev"]), (t, res["test"]))) and t.get("trades", 0) >= 30
        res["ameliorations"][h] = {"dev": d, "test": t, "acceptee": bool(ok)}
        V.enregistrer_experience(f"videos:{sym}", f"{nom}|{json.dumps(p)}|{h}", "-", {"R_test": t.get("R_moyen")})
    V.enregistrer_experience(f"videos:{sym}", f"{nom}|{json.dumps(p)}|base", "-", {"R_test": res["test"].get("R_moyen")})
    return res


def evaluer_rayfu(sym, df, cts):
    out = {}
    for nom, c in (("croisement 20/50 (vidéo)", rayfu.cible(df)), ("acheter-garder", pd.Series(1.0, index=df.index))):
        r = simuler(df, c, "1d", cts, dimensionner=False)
        out[nom] = {"dev": _m(r, "1900", FIN_DEV), "test": _m(r, DEBUT_TEST, "2100"), "trades": int(len(r["trades"])),
                    "reussite": float((r["trades"].net > 0).mean()) if len(r["trades"]) else None}
    return out


def _m(r, a, b):
    x = r["net"].loc[a:b]
    if len(x) < 30:
        return None
    c = (1 + x).cumprod()
    ans = max((x.index[-1] - x.index[0]).days / 365.25, 0.1)
    return {"rendement_annuel": float(c.iloc[-1] ** (1 / ans) - 1), "pire_baisse": float((c / c.cummax() - 1).min()),
            "sharpe": V.sharpe_annuel(x)}


def main():
    resultats = []
    # Roro : SOL, BTC, ETH sur 1 h, 2 h, 4 h, 1 j depuis le 2020-09-14 (sa période)
    for sym in ("SOLUSDT", "BTCUSDT", "ETHUSDT"):
        for tf in ("1h", "2h", "4h", "1d"):
            df = donnees.charger(sym, tf)[0].loc["2020-09-14":]
            for p in roro.GRILLE:
                resultats.append({**evaluer_bracket("roro", roro, sym, df, p, None), "unite": tf})
    # Deleuze et Kasper : vrai forex 5 min (FXCM) ; Nico : forex 1 h et crypto 4 h
    for sym in PAIRES:
        df = donnees_fxcm.charger(sym, "5min").loc["2021-01-01":]
        for mod, nom, be in ((deleuze, "deleuze", deleuze.BE_R), (kasper, "kasper", None)):
            for p in mod.GRILLE:
                resultats.append({**evaluer_bracket(nom, mod, sym, df, p, be), "unite": "5m"})
        h1 = donnees_fxcm.charger(sym, "1h").loc["2021-01-01":]
        for p in nico.GRILLE:
            resultats.append({**evaluer_bracket("nico (approximation)", nico, sym, h1, p, None), "unite": "1h"})
    for sym in ("SOLUSDT", "BTCUSDT", "ETHUSDT"):
        df = donnees.charger(sym, "4h")[0].loc["2020-09-14":]
        for p in nico.GRILLE:
            resultats.append({**evaluer_bracket("nico (approximation)", nico, sym, df, p, None), "unite": "4h"})
    # Ray Fu : Apple, SPY (Yahoo), BTC
    ray = {}
    for sym in ("AAPL", "SPY"):
        df = donnees.charger_yahoo(sym)[0]
        ray[sym] = evaluer_rayfu(sym, df, Couts(commission=0.0, demi_spread_base=0.0001, glissement_sigma=0.02))
    ray["BTCUSDT"] = evaluer_rayfu("BTCUSDT", donnees.charger("BTCUSDT", "1d")[0], Couts())
    o = {"resultats": resultats, "rayfu": ray}
    (ICI / "rapports" / "videos_youtube.json").write_text(json.dumps(o, indent=1, ensure_ascii=False, default=str))
    print(f"{len(resultats)} évaluations stop/objectif, Ray Fu sur {list(ray)}")


if __name__ == "__main__":
    main()
