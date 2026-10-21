"""Données forex intrajournalières : bougies 1 minute Dukascopy (BID), un fichier .bi5 (LZMA) par jour.

Format d'un enregistrement (24 octets, gros-boutiste) : secondes depuis minuit UTC, ouverture, clôture, plus bas,
plus haut (entiers, prix × 10^5, ou × 10^3 pour les paires en JPY), volume (float).
Téléchargement poli (pause entre requêtes, reprises), cache par paire et par mois dans data/fx/.
Usage : python3 -m labo.donnees_fx EURUSD GBPUSD ... --debut 2023-01-01 --fin 2026-10-16
"""
import lzma
import struct
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "fx"
URL = "https://datafeed.dukascopy.com/datafeed/{p}/{a:04d}/{m:02d}/{j:02d}/BID_candles_min_1.bi5"


def _jour(paire, d):
    url = URL.format(p=paire, a=d.year, m=d.month - 1, j=d.day)      # mois de 0 à 11 chez Dukascopy
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for essai in range(6):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                brut = r.read()
            break
        except Exception:
            if essai == 5:
                raise
            time.sleep(min(60, 2 ** (essai + 1)))
    if not brut:
        return None
    d_ = lzma.decompress(brut, format=lzma.FORMAT_ALONE)
    point = 1e3 if "JPY" in paire else 1e5
    lignes = [struct.unpack(">iiiiif", d_[i:i + 24]) for i in range(0, len(d_), 24)]
    df = pd.DataFrame(lignes, columns=["s", "open", "close", "low", "high", "volume"])
    df.index = pd.Timestamp(d) + pd.to_timedelta(df.s, unit="s")
    df = df[["open", "high", "low", "close", "volume"]]
    df[["open", "high", "low", "close"]] /= point
    return df[df.volume > 0]                                          # minutes sans cotation retirées


def telecharger(paire, debut, fin, pause=0.25):
    DOSSIER.mkdir(parents=True, exist_ok=True)
    for mois in pd.period_range(debut, fin, freq="M"):
        f = DOSSIER / f"{paire}_{mois}.csv"
        if f.exists():
            continue
        morceaux = []
        for d in pd.date_range(mois.start_time, min(mois.end_time, pd.Timestamp(fin)), freq="D"):
            if d.dayofweek == 5:                                      # samedi : marché fermé
                continue
            x = _jour(paire, d)
            if x is not None and len(x):
                morceaux.append(x)
            time.sleep(pause)
        if morceaux:
            pd.concat(morceaux).to_csv(f)
        print(f"{paire} {mois} ok", flush=True)


def charger(paire, intervalle="5min"):
    fichiers = sorted(DOSSIER.glob(f"{paire}_*.csv"))
    df = pd.concat(pd.read_csv(f, index_col=0, parse_dates=True) for f in fichiers).sort_index()
    df = df[~df.index.duplicated()]
    return df.resample(intervalle, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}).dropna()


if __name__ == "__main__":
    args = sys.argv[1:]
    debut = args[args.index("--debut") + 1] if "--debut" in args else "2023-01-01"
    fin = args[args.index("--fin") + 1] if "--fin" in args else "2026-10-16"
    for p in [a for a in args if not a.startswith("--") and a not in (debut, fin)]:
        telecharger(p, debut, fin)
