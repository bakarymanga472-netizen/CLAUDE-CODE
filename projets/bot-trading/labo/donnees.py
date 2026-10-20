"""Labo — données de marché et contrôle qualité.

Source pilote : Binance spot (data-api.binance.vision), bougies 1d / 4h / 1h depuis l'ouverture de la paire.
Cache dans data/labo/ (non versionné). Chaque chargement renvoie aussi l'empreinte SHA-256 du fichier,
pour que chaque rapport cite exactement les données utilisées.
"""
import hashlib
import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "labo"
BINANCE = "https://data-api.binance.vision/api/v3/klines"
MS = {"1d": 86_400_000, "4h": 14_400_000, "1h": 3_600_000}
BARRES_PAR_JOUR = {"1d": 1, "4h": 6, "1h": 24}


def _get(url):
    for essai in range(5):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:
            if essai == 4:
                raise
            time.sleep(2 ** essai)


def telecharger(symbole, intervalle, debut="2017-01-01"):
    lignes, depuis = [], int(pd.Timestamp(debut).timestamp() * 1000)
    while True:
        lot = _get(f"{BINANCE}?symbol={symbole}&interval={intervalle}&limit=1000&startTime={depuis}")
        if not lot:
            break
        lignes += lot
        depuis = lot[-1][0] + MS[intervalle]
        if len(lot) < 1000:
            break
    df = pd.DataFrame(lignes, columns=["t", "open", "high", "low", "close", "vol_base", "t_fin",
                                        "volume", "n", "tb", "tq", "x"])
    df.index = pd.to_datetime(df["t"], unit="ms")
    df.index.name = "t"
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    maintenant = pd.Timestamp.now(tz="UTC").tz_localize(None)
    return df[df.index + pd.Timedelta(milliseconds=MS[intervalle]) <= maintenant]   # bougies clôturées seulement


def charger(symbole, intervalle, rafraichir=False):
    """Renvoie (DataFrame, empreinte sha256 du cache)."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    cache = DOSSIER / f"{symbole}_{intervalle}.csv"
    if rafraichir or not cache.exists():
        telecharger(symbole, intervalle).to_csv(cache)
    df = pd.read_csv(cache, index_col=0, parse_dates=True)
    return df, hashlib.sha256(cache.read_bytes()).hexdigest()[:16]


def qualite(df, intervalle):
    """Contrôle qualité : profondeur, trous, doublons, incohérences OHLC, rendements extrêmes."""
    pas = pd.Timedelta(milliseconds=MS[intervalle])
    ecarts = df.index.to_series().diff().dropna()
    trous = ecarts[ecarts > pas]
    attendu = int((df.index[-1] - df.index[0]) / pas) + 1
    r = np.log(df.close).diff().dropna()
    z = (r - r.rolling(500, min_periods=100).mean()) / r.rolling(500, min_periods=100).std()
    return {
        "intervalle": intervalle,
        "debut": str(df.index[0]), "fin": str(df.index[-1]),
        "annees": round((df.index[-1] - df.index[0]).days / 365.25, 1),
        "barres": len(df), "barres_attendues": attendu,
        "barres_manquantes": attendu - len(df),
        "plus_long_trou": str(trous.max()) if len(trous) else "aucun",
        "nb_trous": int(len(trous)),
        "doublons": int(df.index.duplicated().sum()),
        "prix_non_positifs": int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum()),
        "ohlc_incoherents": int(((df.high < df[["open", "close"]].max(axis=1)) |
                                 (df.low > df[["open", "close"]].min(axis=1))).sum()),
        "volume_nul": int((df.volume <= 0).sum()),
        "rendements_sup_8_sigma": int((z.abs() > 8).sum()),
    }


def suffisant(q, min_annees=4, max_manquant=0.02):
    """Règle fixée à l'avance : au moins 4 ans et moins de 2 % de barres manquantes."""
    return q["annees"] >= min_annees and q["barres_manquantes"] / q["barres_attendues"] <= max_manquant \
        and q["doublons"] == 0 and q["ohlc_incoherents"] == 0
