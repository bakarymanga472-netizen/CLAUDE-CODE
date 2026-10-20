"""Exécuteur Alpaca (compte PAPER uniquement) — réécrit après l'audit (anomalies 8 et 9).

Chronologie identique au backtest corrigé (`labo/rebond.py`) : la décision utilise les clôtures Yahoo jusqu'à la
DERNIÈRE SÉANCE TERMINÉE (t) ; l'ordre est passé au cours de clôture (MOC) de la séance du jour (t+1).
À lancer chaque jour de bourse entre 15 h 00 et 15 h 45 (New York).

Garde-fous :
- n'envoie RIEN si la stratégie n'a pas le statut « candidate démo » dans rapports/rebond_corrige.json ;
- n'envoie rien si le marché est fermé, si l'heure limite MOC est trop proche, ou si les données ne sont pas à jour ;
- idempotent : aucun ordre si un ordre est déjà ouvert sur le symbole, et identifiant client déterministe (Alpaca refuse les doublons) ;
- n'achète qu'au jour exact du signal (pas de rattrapage d'une entrée manquée) ; vend dès que la règle dit « à plat » ;
- journal écrit après CHAQUE ordre, même en cas d'erreur ensuite ;
- aucun chemin vers l'argent réel (ALPACA_LIVE=1 est refusé).

Clés lues dans l'environnement : ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY.
Usage : python3 -m aladdin.alpaca [--verifier]
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from amelioration.garde_fous import exiger_humain
from labo import donnees
from labo.rebond import ACTIFS, P
from labo.strategies import rebond_tp_sl as R

ICI = Path(__file__).resolve().parent.parent
JOURNAL = ICI / "resultats" / "alpaca_journal.jsonl"
STATUT = ICI / "rapports" / "rebond_corrige.json"
PART = {a: 1 / len(ACTIFS) for a in ACTIFS}
MARGE_AVANT_CLOTURE_MIN = 15          # Alpaca accepte les MOC jusqu'à 15 h 50 ; on s'arrête avant


def _api(chemin, methode="GET", corps=None):
    if os.environ.get("ALPACA_LIVE") == "1":
        exiger_humain("deployer_reel")
    cle, secret = os.environ.get("ALPACA_API_KEY_ID"), os.environ.get("ALPACA_API_SECRET_KEY")
    if not cle or not secret:
        sys.exit("Clés Alpaca absentes : ajoute ALPACA_API_KEY_ID et ALPACA_API_SECRET_KEY à l'environnement.")
    req = urllib.request.Request("https://paper-api.alpaca.markets" + chemin, method=methode,
                                 data=json.dumps(corps).encode() if corps else None,
                                 headers={"APCA-API-KEY-ID": cle, "APCA-API-SECRET-KEY": secret, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def journaliser(entree):
    JOURNAL.parent.mkdir(exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps({"horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entree},
                           ensure_ascii=False, default=str) + "\n")


def decider(horloge, seance_precedente, aujourdhui, donnees_par_actif, positions, ordres_ouverts, capital, statut):
    """Fonction pure. Renvoie (ordres, messages). `donnees_par_actif` = {sym: DataFrame Yahoo jusqu'à t}."""
    ordres, msgs = [], []
    if statut != "candidate démo (paper uniquement)":
        msgs.append(f"stratégie au statut « {statut} » : aucun ordre (mode vérification forcé)")
    if not horloge["is_open"]:
        return [], msgs + ["marché fermé : aucun ordre"]
    reste = (pd.Timestamp(horloge["next_close"]) - pd.Timestamp(horloge["timestamp"])).total_seconds() / 60
    if reste < MARGE_AVANT_CLOTURE_MIN:
        return [], msgs + [f"clôture dans {reste:.0f} min : trop tard pour un ordre MOC, aucun ordre"]
    for sym, df in donnees_par_actif.items():
        if df.index[-1].normalize() != pd.Timestamp(seance_precedente):
            msgs.append(f"{sym} : dernière barre {df.index[-1].date()} ≠ séance précédente {seance_precedente} → données périmées, rien")
            continue
        if any(o["symbol"] == sym for o in ordres_ouverts):
            msgs.append(f"{sym} : un ordre est déjà ouvert → rien (évite les doublons)")
            continue
        c = R.cible(df, 1, **P)
        veut, avant = c.iloc[-1], c.iloc[-2]
        tient = sym in positions
        cid = f"rebond-{sym}-{aujourdhui}"
        if veut and not tient:
            if not avant:
                qte = int(capital * PART[sym] // df.close.iloc[-1])
                if qte > 0:
                    ordres.append({"symbol": sym, "qty": str(qte), "side": "buy", "type": "market", "time_in_force": "cls",
                                   "client_order_id": cid + "-buy"})
                    msgs.append(f"{sym} : signal à la clôture {df.index[-1].date()} → ACHAT au cours de clôture du jour")
            else:
                msgs.append(f"{sym} : la règle est en position depuis avant hier mais le compte ne l'est pas → entrée manquée, "
                            "PAS de rattrapage (anomalie à examiner)")
        elif not veut and tient:
            ordres.append({"symbol": sym, "qty": positions[sym]["qty"], "side": "sell", "type": "market", "time_in_force": "cls",
                           "client_order_id": cid + "-sell"})
            msgs.append(f"{sym} : la règle est à plat → VENTE au cours de clôture du jour")
        else:
            msgs.append(f"{sym} : {'en position, on garde' if tient else 'pas de signal'}")
    if statut != "candidate démo (paper uniquement)":
        return [], msgs
    return ordres, msgs


def main():
    verifier = "--verifier" in sys.argv
    statut = json.loads(STATUT.read_text())["statut"] if STATUT.exists() else "inconnu (lancer python3 -m labo.rebond)"
    horloge = _api("/v2/clock")
    jour = pd.Timestamp(horloge["timestamp"]).tz_convert("America/New_York").date()
    cal = _api(f"/v2/calendar?start={(pd.Timestamp(jour) - pd.Timedelta(days=10)).date()}&end={jour}")
    seances = [c["date"] for c in cal if c["date"] < str(jour)]
    data = {s: donnees.charger_yahoo(s, rafraichir=True)[0] for s in ACTIFS}
    positions = {p["symbol"]: p for p in _api("/v2/positions")}
    ouverts = _api("/v2/orders?status=open&limit=100")
    capital = float(_api("/v2/account")["equity"])
    ordres, msgs = decider(horloge, seances[-1], jour, data, positions, ouverts, capital, statut)
    for m in msgs:
        print(m)
    journaliser({"evenement": "decision", "statut_strategie": statut, "messages": msgs, "ordres_prevus": ordres, "verifier": verifier})
    if verifier:
        return
    for o in ordres:
        try:
            res = _api("/v2/orders", "POST", o)
            journaliser({"evenement": "ordre_envoye", **o, "id": res["id"], "statut": res["status"]})
            print(f"  ordre envoyé : {o['side']} {o['symbol']} ({res['status']})")
        except Exception as e:                       # on journalise et on continue : jamais d'état perdu
            journaliser({"evenement": "ordre_echec", **o, "erreur": repr(e)})
            print(f"  ÉCHEC {o['side']} {o['symbol']} : {e}")


if __name__ == "__main__":
    main()
