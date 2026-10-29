"""Audit 04 — défaillances techniques de aladdin/alpaca.py, testées HORS LIGNE avec une fausse API (aucun appel réseau, aucune clé).

alpaca._api est remplacé par un simulateur ; le journal est redirigé vers audit/sorties/. Scénarios :
  A. deux lancements le même jour avant la clôture (ordre MOC non encore exécuté) → ordres en double ?
  B. position présente chez le courtier mais absente du journal → la sortie « 20 jours » se déclenche-t-elle un jour ?
  C. lancement un jour férié / week-end (horloge is_open=False) → ordre envoyé ?
  D. erreur HTTP sur le 2e symbole après un ordre sur le 1er → journal écrit ?
  E. compteur de durée : 28 jours calendaires (alpaca.py:86) vs 20 séances (backtest) sur le calendrier SPY réel.

Usage : cd projets/bot-trading && python3 audit/a04_alpaca.py
"""
import contextlib
import io
import os
import urllib.error

import numpy as np
import pandas as pd

import commun
from aladdin import alpaca

out = ["# Audit 04 — alpaca.py (tests hors ligne)\n"]
alpaca.JOURNAL = commun.SORTIES / "alpaca_journal_TEST.json"
os.environ.setdefault("ALPACA_API_KEY_ID", "FAUX")
os.environ.setdefault("ALPACA_API_SECRET_KEY", "FAUX")


def barres_signal():
    """300 séances en hausse puis 3 fortes baisses : RSI-2 < 5 et cours > MM200 → signal d'achat."""
    jours = pd.bdate_range(end=pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=1), periods=300)
    p = np.linspace(100, 160, 300)
    p[-3:] = p[-4] * np.array([0.985, 0.97, 0.955])
    return [{"t": d.strftime("%Y-%m-%dT04:00:00Z"), "c": float(x)} for d, x in zip(jours, p)]


class FausseAPI:
    def __init__(self, ouvert=True, positions=None, erreur_sur=None):
        self.ouvert, self.positions, self.erreur_sur = ouvert, positions or [], erreur_sur
        self.ordres = []
        self.barres = barres_signal()

    def __call__(self, chemin, methode="GET", corps=None, data=False):
        if chemin == "/v2/clock":
            return {"is_open": self.ouvert}
        if chemin == "/v2/account":
            return {"equity": "100000"}
        if chemin == "/v2/positions":
            return self.positions
        if "/bars" in chemin:
            return {"bars": self.barres, "next_page_token": None}
        if "/trades/latest" in chemin:
            return {"trade": {"p": self.barres[-1]["c"]}}
        if chemin == "/v2/orders" and methode == "POST":
            if self.erreur_sur and corps["symbol"] == self.erreur_sur:
                raise urllib.error.HTTPError("x", 403, "insufficient buying power", None, None)
            self.ordres.append(corps)
            return {"id": f"o{len(self.ordres)}", "status": "accepted"}
        raise RuntimeError(chemin)


def lancer(api, argv=()):
    alpaca._api = api
    alpaca.sys.argv = ["alpaca", *argv]
    buf = io.StringIO()
    err = None
    with contextlib.redirect_stdout(buf):
        try:
            alpaca.main()
        except Exception as e:  # noqa: BLE001
            err = e
    return buf.getvalue(), err


# A. double lancement
if alpaca.JOURNAL.exists():
    alpaca.JOURNAL.unlink()
api = FausseAPI()
lancer(api)
lancer(api)            # la position n'existe pas encore chez le courtier (MOC exécuté seulement à 16 h)
out.append(f"- **A. Double lancement le même jour** : {len(api.ordres)} ordres d'achat envoyés "
           f"({', '.join(o['symbol'] + ' ' + o['qty'] for o in api.ordres)}) — aucune vérification des ordres ouverts (/v2/orders?status=open).")

# B. position sans journal
if alpaca.JOURNAL.exists():
    alpaca.JOURNAL.unlink()
api = FausseAPI()
dernier = api.barres[-1]["c"]                       # prix d'entrée = cours actuel → ni objectif ni stop
api.positions = [{"symbol": s_, "qty": "10", "avg_entry_price": str(dernier)} for s_ in ("SPY", "GLD")]
txt, _ = lancer(api, ["--verifier"])
out.append(f"- **B. Position chez le courtier absente du journal** : date d'entrée de repli = dernière barre (alpaca.py:83) → "
           f"« {txt.strip().splitlines()[1].strip()} » ; ce repli n'est jamais enregistré, donc la durée vaut 0 chaque jour "
           f"et la sortie à 20 jours ne se déclenche jamais.")

# C. jour fermé
if alpaca.JOURNAL.exists():
    alpaca.JOURNAL.unlink()
api = FausseAPI(ouvert=False)
lancer(api)
out.append(f"- **C. Marché fermé (is_open=False)** : {len(api.ordres)} ordre(s) envoyé(s) quand même — l'horloge n'est qu'affichée (alpaca.py:73). "
           "Un jour férié, le dernier prix (veille) est ajouté comme une nouvelle barre datée du jour (alpaca.py:59), ce qui fausse RSI-2 et MM200.")

# D. erreur sur le 2e ordre
if alpaca.JOURNAL.exists():
    alpaca.JOURNAL.unlink()
api = FausseAPI(erreur_sur="GLD")
_, err = lancer(api)
out.append(f"- **D. Erreur HTTP sur GLD après l'ordre SPY** : exception {type(err).__name__ if err else 'aucune'} ; "
           f"ordres envoyés {len(api.ordres)} ; journal écrit : {alpaca.JOURNAL.exists()} → l'ordre SPY n'est pas journalisé "
           "(prix et date d'entrée perdus, cf. B). Aucun try/except, aucune relance, aucune alerte.")
if alpaca.JOURNAL.exists():
    alpaca.JOURNAL.unlink()

# E. compteur de durée
spy = pd.read_csv(commun.RACINE / "data" / "yahoo_SPY.csv", index_col=0, parse_dates=True)["close"].loc["2015":]
idx = spy.index
ecarts = []
for k in range(0, len(idx) - 25):
    cible = idx[k] + pd.Timedelta(days=28)
    n = ((idx > idx[k]) & (idx <= cible)).sum()
    ecarts.append(n)
e = pd.Series(ecarts)
out.append(f"- **E. Durée** : 28 jours calendaires = {e.min()}–{e.max()} séances SPY (médiane {e.median():.0f}) au lieu de 20 ; "
           f"{(e != 20).mean():.0%} des dates d'entrée donnent un compte différent de 20. De plus alpaca.py vend à la clôture du jour "
           "où la condition est vue (prix de 15 h 40), le backtest à la clôture SUIVANTE ; l'entrée aussi est décalée d'une séance.")
out.append("- **F. Autres écarts backtest ↔ exécution (lecture du code)** : objectif/stop mesurés depuis le prix indicatif de 15 h 40 "
           "(alpaca.py:80-84) et non le prix d'exécution MOC ; données IEX (`feed=iex`, ~2-3 % du volume) au lieu des clôtures consolidées ; "
           "GLD au lieu de GC=F ; la quantité utilise l'equity totale (pas le cash disponible) ; ordres MOC refusés après 15 h 50 ET sans contrôle de l'heure.")

(commun.SORTIES / "a04_alpaca.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
