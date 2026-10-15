"""Aladdin Rebond sur le VRAI marché via Alpaca (compte paper : vrais prix, vraies exécutions, argent fictif).

À lancer chaque jour de bourse vers 15 h 40 (heure de New York), avant la clôture :
  1. lit le compte et les positions chez Alpaca ;
  2. calcule la règle avec les clôtures passées + le dernier prix du jour ;
  3. envoie des ordres « au cours de clôture » (MOC, time_in_force=cls) : achat si signal, vente si objectif/stop/durée.

Actifs : SPY (actions US) et GLD (ETF or), 50 % du capital chacun.
Clés lues dans l'environnement (jamais dans le code ni le chat) : ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY.
Compte réel : mettre ALPACA_LIVE=1 (déconseillé tant que le suivi paper n'a pas 3 mois).

Usage : python3 -m aladdin.alpaca            → envoie les ordres
        python3 -m aladdin.alpaca --verifier → affiche les décisions sans rien envoyer
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

import pandas as pd

from .desks import rsi

ICI = Path(__file__).resolve().parent.parent
JOURNAL = ICI / "resultats" / "alpaca_journal.json"
REGLE = {"seuil": 5, "tp": 0.01, "sl": 0.10, "duree": 20}
ACTIFS = {"SPY": 0.5, "GLD": 0.5}


def _api(chemin, methode="GET", corps=None, data=False):
    base = "https://data.alpaca.markets" if data else (
        "https://api.alpaca.markets" if os.environ.get("ALPACA_LIVE") == "1" else "https://paper-api.alpaca.markets")
    cle, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not cle or not secret:
        sys.exit("Clés Alpaca absentes : ajoute ALPACA_API_KEY_ID et ALPACA_API_SECRET_KEY à l'environnement.")
    req = urllib.request.Request(base + chemin, method=methode,
                                 data=json.dumps(corps).encode() if corps else None,
                                 headers={"APCA-API-KEY-ID": cle, "APCA-API-SECRET-KEY": secret,
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def historique(sym):
    """Clôtures journalières (1 an et demi) + dernier prix du jour."""
    debut = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=500)).strftime("%Y-%m-%d")
    barres, token = [], None
    while True:
        q = f"/v2/stocks/{sym}/bars?timeframe=1Day&start={debut}&limit=1000&adjustment=all&feed=iex" + (f"&page_token={token}" if token else "")
        r = _api(q, data=True)
        barres += r.get("bars") or []
        token = r.get("next_page_token")
        if not token:
            break
    c = pd.Series({pd.Timestamp(b["t"]).normalize(): b["c"] for b in barres}).sort_index()
    dernier = _api(f"/v2/stocks/{sym}/trades/latest?feed=iex", data=True)["trade"]["p"]
    aujourd_hui = pd.Timestamp.now(tz="UTC").normalize()
    c.loc[aujourd_hui] = dernier                                # le cours du jour remplace la future clôture
    return c


def charger():
    return json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {"positions": {}, "ordres": []}


def main():
    verifier = "--verifier" in sys.argv
    horloge = _api("/v2/clock")
    compte = _api("/v2/account")
    capital = float(compte["equity"])
    j = charger()
    print(f"Marché {'OUVERT' if horloge['is_open'] else 'fermé'} — capital {capital:,.2f} USD — "
          f"{'compte RÉEL' if os.environ.get('ALPACA_LIVE') == '1' else 'compte paper'}")
    positions = {p["symbol"]: p for p in _api("/v2/positions")}
    for sym, part in ACTIFS.items():
        c = historique(sym)
        r2 = rsi(c.to_frame(), 2).iloc[-1, 0]
        tendance = c.iloc[-1] > c.rolling(200).mean().iloc[-1]
        prix = c.iloc[-1]
        ordre = None
        if sym in positions:
            e = j["positions"].get(sym, {"prix": float(positions[sym]["avg_entry_price"]), "date": str(c.index[-1].date())})
            gain = prix / e["prix"] - 1
            jours = (c.index[-1] - pd.Timestamp(e["date"], tz="UTC")).days
            if gain >= REGLE["tp"] or gain <= -REGLE["sl"] or jours >= REGLE["duree"] * 7 / 5:
                ordre = {"symbol": sym, "qty": positions[sym]["qty"], "side": "sell", "type": "market", "time_in_force": "cls"}
            print(f"{sym}: en position, gain {gain * 100:+.2f} %, {jours} j → {'VENTE à la clôture' if ordre else 'on garde'}")
        else:
            signal = r2 < REGLE["seuil"] and tendance
            if signal:
                qte = int(capital * part // prix)
                if qte > 0:
                    ordre = {"symbol": sym, "qty": str(qte), "side": "buy", "type": "market", "time_in_force": "cls"}
            print(f"{sym}: RSI-2 {r2:.1f}, tendance {'haussière' if tendance else 'baissière'} → "
                  f"{'ACHAT à la clôture' if ordre else 'pas de signal'}")
        if ordre and not verifier:
            res = _api("/v2/orders", "POST", ordre)
            print(f"  ordre envoyé : {res['id']} ({res['status']})")
            j["ordres"].append({"date": str(pd.Timestamp.now(tz='UTC')), **ordre, "id": res["id"], "prix_indicatif": prix})
            if ordre["side"] == "buy":
                j["positions"][sym] = {"prix": prix, "date": str(c.index[-1].date())}
            else:
                j["positions"].pop(sym, None)
    if not verifier:
        JOURNAL.parent.mkdir(exist_ok=True)
        JOURNAL.write_text(json.dumps(j, indent=2))


if __name__ == "__main__":
    main()
