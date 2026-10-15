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


FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
GPR = "https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls"


def _telecharger(url, chemin):
    for essai in range(4):
        try:
            urllib.request.urlretrieve(url, chemin)
            return
        except Exception:
            if essai == 3:
                raise
            time.sleep(2 ** essai)


def macro(rafraichir=False):
    """Équivalent gratuit de MacroMicro : taux US 10 ans (DGS10) et dollar large (DTWEXBGS), source Fed/FRED."""
    DATA_DIR.mkdir(exist_ok=True)
    series = {}
    for code in ("DGS10", "DTWEXBGS"):
        cache = DATA_DIR / f"{code}.csv"
        if rafraichir or not cache.exists():
            _telecharger(FRED.format(code), cache)
        d = pd.read_csv(cache, index_col=0, parse_dates=True, na_values=".")
        series[code] = pd.to_numeric(d.iloc[:, 0], errors="coerce")
    return pd.DataFrame(series)


def geopolitique(rafraichir=False):
    """Équivalent historique de World Monitor : indice quotidien de risque géopolitique (Caldara & Iacoviello)."""
    DATA_DIR.mkdir(exist_ok=True)
    cache = DATA_DIR / "gpr_daily.xls"
    if rafraichir or not cache.exists():
        _telecharger(GPR, cache)
    d = pd.read_excel(cache)
    d = d[pd.to_numeric(d["DAY"], errors="coerce").notna()]
    return pd.Series(d["GPRD"].astype(float).values, index=pd.to_datetime(d["DAY"].astype(int).astype(str)), name="gpr")


def tout_charger(rafraichir=False):
    marches = {s: bougies(s, rafraichir=rafraichir) for s in UNIVERS}
    return marches, fear_greed(rafraichir=rafraichir)
