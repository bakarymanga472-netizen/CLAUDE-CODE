"""Chiffres que le moteur Python obtient avec EXACTEMENT les réglages des scripts Pine (100 % du capital, sans
ciblage de volatilité, commission fixe, sans glissement), pour comparer avec le testeur de stratégie TradingView.

Usage : python3 -m tradingview.attendus → tradingview/comparaison.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

from labo import donnees
from labo.couts import Couts
from labo.moteur import simuler
from labo.strategies import cassure, croisement_mm, rebond_tp_sl, tendance

ICI = Path(__file__).resolve().parent
CRYPTO = Couts(commission=0.0015, demi_spread_base=0.0, glissement_sigma=0.0)
ETF = Couts(commission=0.0001, demi_spread_base=0.0, glissement_sigma=0.0)


def style_tradingview(df, res):
    """Mesures au format du testeur TradingView : trades CLÔTURÉS seulement, profit factor en dollars."""
    eq = 10000 * (1 + res["net"]).cumprod()
    t = res["trades"]
    ouvert = len(t) and res["w"].iloc[-1] != 0
    clos = t.iloc[:-1] if ouvert else t
    avant = eq.shift(1).fillna(10000)
    pnl = np.array([avant.loc[e] * x for e, x in zip(clos.entree, clos.net)])
    gains, pertes = pnl[pnl > 0].sum(), -pnl[pnl <= 0].sum()
    return {"trades_clotures": len(clos), "gagnants": f"{(pnl > 0).mean():.1%}" if len(pnl) else "—",
            "profit_factor": f"{gains / pertes:.2f}" if pertes else "—",
            "profit_net_trades_clotures": f"{pnl.sum() / 10000:+.0%}",
            "capital_final_avec_ouvert": f"{eq.iloc[-1]:,.0f} $",
            "pire_baisse_cloture": f"{(eq / eq.cummax() - 1).min():.1%}", "trade_ouvert": bool(ouvert),
            "premier_trade": str(clos.entree.iloc[0].date()) if len(clos) else "—",
            "dernier_bar": str(df.index[-1].date())}


def main():
    L = ["# Comparaison avec TradingView\n",
         "Colle chaque script `.pine` de ce dossier dans TradingView (Pine Editor → Add to chart → onglet Strategy Tester) et compare "
         "avec les chiffres ci-dessous, calculés par le moteur Python avec exactement les mêmes réglages. "
         "Capital 10 000 $, 100 % du capital par trade, pas de glissement.\n",
         "Écarts NORMAUX à attendre : quelques trades en plus/moins au tout début (historique de chauffe), petites différences de prix "
         "entre le flux TradingView et l'API Binance, RSI légèrement différent sur les premières barres. Un écart important "
         "(signe du profit différent, nombre de trades très différent) = bug à investiguer d'un côté ou de l'autre.\n",
         "| Script | Graphique | Réglage | Trades clôturés | Gagnants | Profit factor | Profit net (clôturés) | Pire baisse | Trade ouvert | Premier trade | Données jusqu'au |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    btc, _ = donnees.charger("BTCUSDT", "1d")
    for mod, fichier, grille in ((tendance, "tendance.pine", tendance.GRILLE), (cassure, "cassure.pine", cassure.GRILLE),
                                 (croisement_mm, "croisement_mm.pine", croisement_mm.GRILLE)):
        for p in grille:
            res = simuler(btc, mod.cible(btc, 1, **p), "1d", CRYPTO, dimensionner=False)
            m = style_tradingview(btc, res)
            L.append(f"| {fichier} | BINANCE:BTCUSDT 1D | {p} | {m['trades_clotures']} | {m['gagnants']} | {m['profit_factor']} | "
                     f"{m['profit_net_trades_clotures']} | {m['pire_baisse_cloture']} | {'oui' if m['trade_ouvert'] else 'non'} | {m['premier_trade']} | {m['dernier_bar']} |")
    for sym in ("SPY", "GLD"):
        df, _ = donnees.charger_yahoo(sym)
        res = simuler(df, rebond_tp_sl.cible(df, 1, **rebond_tp_sl.GRILLE[0]), "1d", ETF, dimensionner=False, execution="cloture")
        m = style_tradingview(df, res)
        L.append(f"| rebond.pine | AMEX:{sym} 1D (ADJ) | {rebond_tp_sl.GRILLE[0]} | {m['trades_clotures']} | {m['gagnants']} | {m['profit_factor']} | "
                 f"{m['profit_net_trades_clotures']} | {m['pire_baisse_cloture']} | {'oui' if m['trade_ouvert'] else 'non'} | {m['premier_trade']} | {m['dernier_bar']} |")
    L += ["\n## Ce que TradingView ne vérifie PAS\n",
          "- Le surapprentissage : TradingView affiche un backtest, pas un DSR ni un test hors échantillon. Un bon résultat dans TradingView ne valide rien.",
          "- Les coûts réels : ici commission fixe, sans spread ni glissement variable (le labo, lui, les inclut).",
          "- Le ciblage de volatilité du labo : les scripts Pine investissent 100 % du capital, donc les rendements et les baisses sont plus forts que dans les fiches.",
          "\nÀ me renvoyer : une capture de l'onglet « Performance Summary » et « List of Trades » pour chaque script, je compare ligne à ligne."]
    (ICI / "comparaison.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
