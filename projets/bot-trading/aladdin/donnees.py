"""Aladdin — données : 5 cryptos (Binance), or (COMEX), actions US (SPY), obligations US (TLT)."""
import json
import time
import urllib.request

import pandas as pd

from bot import data

YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{s}?period1=1136073600&period2={fin}&interval=1d"
CRYPTOS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
TRADITIONNELS = {"OR": "GC=F", "ACTIONS": "SPY", "OBLIGATIONS": "TLT"}
FRAIS = {"crypto": 0.0015, "autre": 0.0005}   # par unité de rotation (commission + glissement)


def _yahoo(symbole, rafraichir):
    cache = data.DATA_DIR / f"yahoo_{symbole.replace('=', '_')}.csv"
    if cache.exists() and not rafraichir:
        return pd.read_csv(cache, index_col=0, parse_dates=True)["close"]
    for essai in range(4):
        try:
            req = urllib.request.Request(YAHOO.format(s=symbole, fin=int(time.time())),
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.loads(r.read())["chart"]["result"][0]
            break
        except Exception:
            if essai == 3:
                raise
            time.sleep(2 ** essai)
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or res["indicators"]["quote"][0]["close"]
    s = pd.Series(adj, index=pd.to_datetime(res["timestamp"], unit="s").normalize(), name="close").dropna()
    s = s[~s.index.duplicated(keep="last")]
    s = s[s.index < pd.Timestamp.now().normalize()]
    data.DATA_DIR.mkdir(exist_ok=True)
    s.to_frame().to_csv(cache)
    return s


def prix(rafraichir=False):
    """DataFrame des clôtures (dividendes inclus pour SPY/TLT), calendrier quotidien 7j/7.
    Week-ends : le dernier cours des marchés fermés est reporté (rendement nul)."""
    series = {s.replace("USDT", ""): data.bougies(s, rafraichir=rafraichir)["close"] for s in CRYPTOS}
    for nom, sym in TRADITIONNELS.items():
        series[nom] = _yahoo(sym, rafraichir)
    df = pd.DataFrame(series).sort_index()
    idx = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(idx)
    for col in TRADITIONNELS:
        df[col] = df[col].ffill()
    return df


def type_actif(nom):
    return "autre" if nom in TRADITIONNELS else "crypto"
