"""Forex réel : archive publique FXCM de bougies 1 minute avec prix ACHETEUR et VENDEUR (bid/ask).

URL : https://candledata.fxcorporate.com/m1/{PAIRE}/{année}/{semaine}.csv.gz (heure UTC).
On garde le prix moyen (mid) pour les signaux et l'écart vendeur-acheteur (spread) RÉEL de chaque barre pour les coûts.
Cache : data/fxcm/{PAIRE}_{année}_{semaine}.csv.gz. Usage : python3 -m labo.donnees_fxcm EURUSD GBPUSD ...
"""
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "fxcm"
URL = "https://candledata.fxcorporate.com/m1/{p}/{a}/{s}.csv.gz"


def telecharger(paire, annees):
    DOSSIER.mkdir(parents=True, exist_ok=True)
    for a in annees:
        for s in range(1, 54):
            f = DOSSIER / f"{paire}_{a}_{s:02d}.csv.gz"
            if f.exists():
                continue
            for essai in range(4):
                try:
                    req = urllib.request.Request(URL.format(p=paire, a=a, s=s), headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=60) as r:
                        f.write_bytes(r.read())
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 404 or (e.code == 403 and essai >= 1):   # semaine inexistante (future ou 53e)
                        break
                    time.sleep(2 ** essai)
                except Exception:
                    time.sleep(2 ** essai)
        print(f"{paire} {a} ok", flush=True)


def charger(paire, intervalle="5min"):
    cache = DOSSIER / f"{paire}_{intervalle}.csv"
    sources = sorted(DOSSIER.glob(f"{paire}_2*.csv.gz"))
    if cache.exists() and cache.stat().st_mtime >= max(f.stat().st_mtime for f in sources):
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    agg = _agreger(paire, intervalle)
    agg.to_csv(cache)
    return agg


def _agreger(paire, intervalle):
    morceaux = [pd.read_csv(f) for f in sorted(DOSSIER.glob(f"{paire}_2*.csv.gz"))]
    d = pd.concat(morceaux)
    d.index = pd.to_datetime(d.DateTime, format="%m/%d/%Y %H:%M:%S.%f")
    d = d[~d.index.duplicated()].sort_index()
    mid = pd.DataFrame({k: (d[f"Bid{k.capitalize()}"] + d[f"Ask{k.capitalize()}"]) / 2 for k in ("open", "high", "low", "close")})
    mid["spread"] = d.AskOpen - d.BidOpen
    agg = mid.resample(intervalle, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "spread": "mean"})
    return agg.dropna()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        telecharger(p, range(2021, 2027))
