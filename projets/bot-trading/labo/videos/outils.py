import numpy as np
import pandas as pd


def sma(x, n):
    return x.rolling(n).mean()


def ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    pc = df.close.shift(1)
    tr = pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def session_paris(index, debut="09:30", fin="18:00"):
    """Vrai si l'ouverture de la barre tombe dans la plage horaire de Paris (heure d'été/hiver gérée)."""
    loc = pd.DatetimeIndex(index).tz_localize("UTC").tz_convert("Europe/Paris")
    m = loc.hour * 60 + loc.minute
    h0, m0 = map(int, debut.split(":"))
    h1, m1 = map(int, fin.split(":"))
    return pd.Series((m >= h0 * 60 + m0) & (m < h1 * 60 + m1), index=index)


def assembler(df, long_, short_, stop_long, stop_short, tp_R):
    l = df.index[long_.fillna(False).values]
    s = df.index[short_.fillna(False).values]
    a = pd.DataFrame({"sens": 1, "stop": stop_long.reindex(l), "tp_R": tp_R}, index=l)
    b = pd.DataFrame({"sens": -1, "stop": stop_short.reindex(s), "tp_R": tp_R}, index=s)
    return pd.concat([a, b]).sort_index().dropna()
