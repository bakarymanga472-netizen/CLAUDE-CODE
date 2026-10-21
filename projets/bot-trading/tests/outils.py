import numpy as np
import pandas as pd


def marche_synthetique(n=1500, graine=1, freq="D", derive=0.0):
    """Série OHLC FICTIVE (marche aléatoire) pour les tests."""
    rng = np.random.default_rng(graine)
    r = rng.normal(derive, 0.03, n)
    close = 100 * np.exp(np.cumsum(r))
    open_ = np.r_[100, close[:-1]]
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.01, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.01, n))
    idx = pd.date_range("2017-01-01", periods=n, freq=freq)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": 1.0}, index=idx)
