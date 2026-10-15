"""Paper trading : chaque jour, les agents proposent, TOI tu valides. Argent fictif uniquement.

Usage : python3 signal_du_jour.py            → propose et demande ta validation
        python3 signal_du_jour.py --grok     → ajoute l'avis de Grok (XAI_API_KEY requis dans .env)
Portefeuille fictif : resultats/portefeuille_papier.json
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

from bot import agents, data
from bot.backtest import FRAIS, _lignes

ICI = Path(__file__).resolve().parent
PF = ICI / "resultats" / "portefeuille_papier.json"


def charger_pf():
    if PF.exists():
        return json.loads(PF.read_text())
    return {"cash": 10_000.0, "positions": {}, "journal": []}


def avis_grok(propositions, contexte):
    """Demande un avis à Grok (API xAI, compatible OpenAI). Avis seulement : Grok ne décide rien."""
    import urllib.request
    cle = os.environ.get("XAI_API_KEY")
    if not cle:
        return "Pas de clé XAI_API_KEY : avis Grok ignoré."
    corps = {"model": os.environ.get("XAI_MODEL", "grok-4"),
             "messages": [{"role": "system", "content": "Tu es analyste de risque crypto. Réponds en français, 5 lignes max, sans promettre de gain."},
                          {"role": "user", "content": f"Contexte : {contexte}\nPropositions des agents : {propositions}\nQuels risques vois-tu ?"}]}
    req = urllib.request.Request("https://api.x.ai/v1/chat/completions", data=json.dumps(corps).encode(),
                                 headers={"Authorization": f"Bearer {cle}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Grok indisponible ({e})."


def main():
    marches_df, fng_s = data.tout_charger(rafraichir=True)
    marches_df = {s: agents.indicateurs(d) for s, d in marches_df.items()}
    marches, fng = _lignes(marches_df, fng_s)
    t = marches_df["BTCUSDT"].index[-1]
    cfg = agents.Config()
    pf = charger_pf()
    print(f"Clôture du {t.date()} — Fear & Greed : {fng.get(t, '?')}")
    try:
        ctx = agents.contexte_macro_geo(data.macro(True), data.geopolitique(True), marches_df["BTCUSDT"].index)
        a = ctx.get(t, {})
        lib = {-1: "défavorable", 0: "neutre", 1: "favorable"}
        print(f"Info macro (taux + dollar) : {lib.get(a.get('macro'), '?')} | "
              f"tension géopolitique : {'élevée' if a.get('geo') == -1 else 'normale'} "
              f"(à titre d'info : ces agents n'ont pas amélioré le backtest)")
        print("Contexte en direct : https://www.worldmonitor.app — macro : https://www.macromicro.me")
    except Exception as e:
        print(f"Données macro/géopolitique indisponibles ({e}).")

    # Sorties proposées
    for sym, p in list(pf["positions"].items()):
        ligne = marches[sym][t]
        p["pic"] = max(p["pic"], ligne["close"])
        p["stop"] = max(p["stop"], p["pic"] - 3 * ligne["atr14"])
        if ligne["close"] <= p["stop"] or agents.doit_sortir(ligne, cfg):
            if input(f"VENDRE {sym} à ~{ligne['close']:.4g} (stop ou fin de tendance) ? [o/N] ").lower() == "o":
                pf["cash"] += p["qte"] * ligne["close"] * (1 - FRAIS)
                pf["journal"].append({"date": str(t.date()), "action": "vente", "symbole": sym, "prix": ligne["close"]})
                del pf["positions"][sym]

    # Achats proposés
    capital = pf["cash"] + sum(p["qte"] * marches[s][t]["close"] for s, p in pf["positions"].items())
    places = cfg.max_positions - len(pf["positions"])
    props = agents.coordinateur(marches, fng, t, cfg, pf["positions"])[:max(places, 0)]
    if not props:
        print("Aucune proposition d'achat aujourd'hui.")
    if props and "--grok" in sys.argv:
        print("Avis Grok :", avis_grok([{k: v for k, v in p.items() if k != "date"} for p in props],
                                        f"Fear & Greed {fng.get(t)}"))
    for p in props:
        ligne = marches[p["symbole"]][t]
        qte, stop = agents.taille_position(capital, ligne, cfg)
        qte = min(qte, pf["cash"] / (ligne["close"] * (1 + FRAIS)))
        print(f"\nACHAT proposé {p['symbole']} ~{ligne['close']:.4g} | setups {p['setups']}/3, "
              f"sentiment {p['sentiment']:+d}, flux {p['flux']:+d} | {qte * ligne['close']:.0f} USDT, stop {stop:.4g}")
        if qte > 0 and input("Valider ? [o/N] ").lower() == "o":
            pf["cash"] -= qte * ligne["close"] * (1 + FRAIS)
            pf["positions"][p["symbole"]] = {"qte": qte, "prix_entree": ligne["close"], "stop": stop, "pic": ligne["close"]}
            pf["journal"].append({"date": str(t.date()), "action": "achat", "symbole": p["symbole"], "prix": ligne["close"]})

    capital = pf["cash"] + sum(p["qte"] * marches[s][t]["close"] for s, p in pf["positions"].items())
    print(f"\nPortefeuille fictif : {capital:,.0f} USDT ({len(pf['positions'])} positions)")
    PF.parent.mkdir(exist_ok=True)
    PF.write_text(json.dumps(pf, indent=2, default=str))


if __name__ == "__main__":
    main()
