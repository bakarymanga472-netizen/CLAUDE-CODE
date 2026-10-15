"""Données de marché : bougies journalières Binance (API publique) et indice Fear & Greed.

Tout est mis en cache dans data/ pour ne pas retélécharger à chaque test.
"""
import json
import time
import urllib.request
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BINANCE = "https://data-api.binance.vision/api/v3/klines"
FNG = "https://api.alternative.me/fng/?limit=0&format=json"

UNIVERS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
           "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"]


def _get(url):
    for essai in range(4):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            if essai == 3:
                raise
            time.sleep(2 ** essai)


def bougies(symbole, debut="2020-01-01", rafraichir=False):
    """DataFrame indexé par date : open, high, low, close, volume (en USDT)."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / f"{symbole}.csv"
    if cache.exists() and not rafraichir:
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    lignes, depuis = [], int(pd.Timestamp(debut).timestamp() * 1000)
    while True:
        lot = _get(f"{BINANCE}?symbol={symbole}&interval=1d&limit=1000&startTime={depuis}")
        if not lot:
            break
        lignes += lot
        depuis = lot[-1][0] + 86_400_000
        if len(lot) < 1000:
            break
    df = pd.DataFrame(lignes, columns=["t", "open", "high", "low", "close", "vol_base", "t_fin",
                                        "volume", "n", "tb", "tq", "x"])
    df.index = pd.to_datetime(df["t"], unit="ms")
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df = df[df.index < pd.Timestamp.now().normalize()]  # pas de bougie du jour non clôturée
    df.to_csv(cache)
    return df


def fear_greed(rafraichir=False):
    """Série journalière 0-100 (0 = peur extrême, 100 = avidité extrême)."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / "fear_greed.csv"
    if cache.exists() and not rafraichir:
        return pd.read_csv(cache, index_col=0, parse_dates=True)["fng"]
    d = _get(FNG)["data"]
    s = pd.Series({pd.to_datetime(int(x["timestamp"]), unit="s"): int(x["value"]) for x in d}, name="fng")
    s = s.sort_index()
    s.to_frame().to_csv(cache)
    return s


def tout_charger(rafraichir=False):
    marches = {s: bougies(s, rafraichir=rafraichir) for s in UNIVERS}
    return marches, fear_greed(rafraichir=rafraichir)
