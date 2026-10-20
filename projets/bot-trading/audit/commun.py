"""Audit Aladdin — outils communs (lecture seule du package aladdin/, aucune écriture hors de audit/).

- chargement des prix depuis le cache data/ (jamais de rafraîchissement : reproductible)
- téléchargement éventuel de données SUPPLÉMENTAIRES dans audit/donnees/ (jamais dans data/)
- loi normale (math.erf), Deflated Sharpe Ratio (Bailey & López de Prado 2014), intervalle de Wilson
"""
import json
import math
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

AUDIT = Path(__file__).resolve().parent
RACINE = AUDIT.parent
sys.path.insert(0, str(RACINE))

from aladdin import donnees  # noqa: E402

DONNEES = AUDIT / "donnees"
SORTIES = AUDIT / "sorties"
DONNEES.mkdir(exist_ok=True)
SORTIES.mkdir(exist_ok=True)


def prix():
    """Exactement ce que voit Aladdin (cache data/, week-ends reportés pour SPY/or/TLT)."""
    return donnees.prix(rafraichir=False)


def seances(s):
    """Retire les jours reportés (même règle que aladdin/enquete.py:78)."""
    s = s.dropna()
    return s[s.diff().ne(0) | (s.index == s.index[0])]


# ---------------------------------------------------------------- loi normale
def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def phi_inv(p):
    """Inverse de la loi normale par dichotomie sur math.erf (précision 1e-12)."""
    if p <= 0 or p >= 1:
        raise ValueError(p)
    lo, hi = -40.0, 40.0
    for _ in range(200):
        m = (lo + hi) / 2
        if phi(m) < p:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


EULER = 0.5772156649015329


def sharpe_max_attendu(n_essais, var_sr):
    """Sharpe maximal attendu sous H0 (aucun talent) parmi n essais indépendants (unités par période)."""
    if n_essais <= 1:
        return 0.0
    return math.sqrt(var_sr) * ((1 - EULER) * phi_inv(1 - 1 / n_essais)
                                + EULER * phi_inv(1 - 1 / (n_essais * math.e)))


def psr(sr, sr0, t, skew, kurt):
    """Probabilistic Sharpe Ratio. sr et sr0 par période (non annualisés), kurt = kurtosis NON excédentaire."""
    den = 1 - skew * sr + (kurt - 1) / 4 * sr ** 2
    if den <= 0:
        return float("nan")
    return phi((sr - sr0) * math.sqrt(t - 1) / math.sqrt(den))


def dsr(r, n_essais, var_sr):
    """Deflated Sharpe Ratio d'une série de rendements r (par période)."""
    r = pd.Series(r).dropna()
    sr = r.mean() / r.std(ddof=1)
    z = (r - r.mean()) / r.std(ddof=0)
    skew, kurt = float((z ** 3).mean()), float((z ** 4).mean())
    sr0 = sharpe_max_attendu(n_essais, var_sr)
    return {"sr_periode": sr, "sr0_periode": sr0, "T": len(r), "skew": skew, "kurt": kurt,
            "psr_vs_0": psr(sr, 0.0, len(r), skew, kurt), "dsr": psr(sr, sr0, len(r), skew, kurt)}


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def stats_quotidien(r, ppa):
    """Statistiques d'une série de rendements quotidiens ; ppa = périodes par an (252 séances ou 365 jours)."""
    r = pd.Series(r).fillna(0.0)
    if r.ne(0).any():
        r = r[r.index >= r.ne(0).idxmax()]
    courbe = (1 + r).cumprod()
    ans = max((r.index[-1] - r.index[0]).days / 365.25, 1e-9)
    vol = r.std() * math.sqrt(ppa)
    return {"total": courbe.iloc[-1] - 1, "par_an": courbe.iloc[-1] ** (1 / ans) - 1,
            "pire_baisse": float((courbe / courbe.cummax() - 1).min()),
            "sharpe": r.mean() * ppa / vol if vol > 0 else float("nan"), "vol": vol,
            "exposition_jours": float(r.ne(0).mean())}


def pct(x, d=1):
    return "—" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x * 100:+.{d}f} %"


# ---------------------------------------------------------------- données supplémentaires (audit/donnees/)
def _get(url, ua=False):
    for essai in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"} if ua else {})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if essai == 3:
                raise
            time.sleep(2 ** essai)


def yahoo_ohlc(symbole):
    """OHLC + adjclose Yahoo (séances réelles uniquement), en cache dans audit/donnees/."""
    cache = DONNEES / f"yahoo_ohlc_{symbole.replace('=', '_').replace('^', '')}.csv"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{symbole}?period1=1136073600"
           f"&period2=1792800000&interval=1d")
    res = _get(url, ua=True)["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    adj = res["indicators"].get("adjclose", [{}])[0].get("adjclose") or q["close"]
    df = pd.DataFrame({"open": q["open"], "high": q["high"], "low": q["low"], "close": q["close"],
                       "adjclose": adj}, index=pd.to_datetime(res["timestamp"], unit="s").normalize())
    df = df[~df.index.duplicated(keep="last")].dropna(subset=["close"])
    df = df[df.index <= pd.Timestamp("2026-10-16")]
    df.to_csv(cache)
    return df


def binance(symbole, debut="2020-01-01"):
    """Bougies Binance d'un symbole (y compris retirés de la cote), en cache dans audit/donnees/."""
    cache = DONNEES / f"binance_{symbole}.csv"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    lignes, depuis = [], int(pd.Timestamp(debut).timestamp() * 1000)
    while True:
        try:
            lot = _get(f"https://data-api.binance.vision/api/v3/klines?symbol={symbole}&interval=1d"
                       f"&limit=1000&startTime={depuis}")
        except Exception:
            lot = []
        if not lot:
            break
        lignes += lot
        depuis = lot[-1][0] + 86_400_000
        if len(lot) < 1000:
            break
    if not lignes:
        df = pd.DataFrame(columns=["open", "close"])
    else:
        df = pd.DataFrame(lignes).iloc[:, [0, 1, 4]]
        df.columns = ["t", "open", "close"]
        df.index = pd.to_datetime(df["t"], unit="ms")
        df = df[["open", "close"]].astype(float)
        df = df[df.index <= pd.Timestamp("2026-10-16")]
    df.to_csv(cache)
    return df
