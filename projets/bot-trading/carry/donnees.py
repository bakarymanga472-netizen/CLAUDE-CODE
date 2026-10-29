"""Carry — données : funding Binance USDT-M (archives data.binance.vision), klines perp 1d, contrôle croisé OKX.

Format vérifié (2026-10-20) des archives fundingRate : CSV avec en-tête
  calc_time (ms UTC, avec quelques ms de gigue), funding_interval_hours (8), last_funding_rate (fraction par période,
  0.0001 = 0,01 % par 8 h ; payé par les longs aux shorts si > 0).
Premier mois disponible : 2020-01 (BTCUSDT et ETHUSDT ; 2019-09 → 2019-12 renvoient 404).
Klines perp : 12 colonnes sans en-tête dans les vieux fichiers, avec en-tête dans les récents.
Cache : data/carry/ (non versionné).
"""
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

DOSSIER = Path(__file__).resolve().parent.parent / "data" / "carry"
ARCHIVES = "https://data.binance.vision/data/futures/um/monthly"
OKX = "https://www.okx.com/api/v5/public/funding-rate-history"
PREMIER_MOIS = "2020-01"
COLS_KLINES = ["t", "open", "high", "low", "close", "volume", "t_fin", "qv", "n", "tb", "tq", "x"]


def _telecharger(url, essais=4):
    """Renvoie les octets, ou None si 404."""
    for k in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (recherche carry)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if k == essais - 1:
                raise
        except Exception:
            if k == essais - 1:
                raise
        time.sleep(2 ** k)


def _mois(jusqu_a=None):
    fin = (pd.Timestamp.now(tz="UTC").tz_localize(None) if jusqu_a is None else pd.Timestamp(jusqu_a))
    fin = (fin.to_period("M") - 1)                 # dernier mois complet
    return [str(p) for p in pd.period_range(PREMIER_MOIS, fin, freq="M")]


def _zip_csv(contenu):
    with zipfile.ZipFile(io.BytesIO(contenu)) as z:
        nom = [n for n in z.namelist() if n.endswith(".csv")][0]
        return z.read(nom).decode()


def _archive(genre, symbole, mois):
    """genre : 'fundingRate', 'klines1d' ou 'markPrice1d'. Cache du zip brut ; renvoie le texte CSV ou None."""
    rep = DOSSIER / "brut" / symbole / genre
    rep.mkdir(parents=True, exist_ok=True)
    f = rep / f"{mois}.zip"
    absent = rep / f"{mois}.absent"
    if absent.exists():
        return None
    if not f.exists():
        if genre == "fundingRate":
            url = f"{ARCHIVES}/fundingRate/{symbole}/{symbole}-fundingRate-{mois}.zip"
        elif genre == "markPrice1d":
            url = f"{ARCHIVES}/markPriceKlines/{symbole}/1d/{symbole}-1d-{mois}.zip"
        else:
            url = f"{ARCHIVES}/klines/{symbole}/1d/{symbole}-1d-{mois}.zip"
        b = _telecharger(url)
        if b is None:
            absent.write_text("404")
            return None
        f.write_bytes(b)
    return _zip_csv(f.read_bytes())


def lire_funding_csv(texte):
    df = pd.read_csv(io.StringIO(texte))
    if "calc_time" not in df.columns:          # sécurité si un fichier n'a pas d'en-tête
        df = pd.read_csv(io.StringIO(texte), header=None, names=["calc_time", "funding_interval_hours", "last_funding_rate"])
    out = pd.DataFrame({"brut_ms": df.calc_time.astype("int64"),
                        "intervalle_h": df.funding_interval_hours.astype(float),
                        "taux": df.last_funding_rate.astype(float)})
    out.index = pd.to_datetime(out.brut_ms, unit="ms").dt.round("1min")   # enlève la gigue de quelques ms
    out.index.name = "t"
    return out


def lire_klines_csv(texte):
    premiere = texte.split("\n", 1)[0]
    df = pd.read_csv(io.StringIO(texte), header=0 if premiere.startswith("open_time") else None)
    df = df.iloc[:, :6]
    df.columns = COLS_KLINES[:6]
    df.index = pd.to_datetime(df.t.astype("int64"), unit="ms")
    df.index.name = "t"
    return df[["open", "high", "low", "close", "volume"]].astype(float)


def _assembler(genre, symbole, lecteur, jusqu_a=None):
    morceaux, manquants = [], []
    for m in _mois(jusqu_a):
        txt = _archive(genre, symbole, m)
        if txt is None:
            manquants.append(m)
            continue
        morceaux.append(lecteur(txt))
    df = pd.concat(morceaux).sort_index()
    return df, manquants


def _empreinte(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()[:16]


def funding(symbole, jusqu_a=None):
    """Renvoie (DataFrame funding [intervalle_h, taux], mois absents, empreinte). Doublons exacts conservés ici :
    ils sont comptés par qualite_funding puis retirés par nettoyer_funding."""
    df, manquants = _assembler("fundingRate", symbole, lire_funding_csv, jusqu_a)
    return df, manquants, _empreinte(df)


def klines_perp(symbole, jusqu_a=None):
    df, manquants = _assembler("klines1d", symbole, lire_klines_csv, jusqu_a)
    df = df[~df.index.duplicated(keep="first")]
    return df, manquants, _empreinte(df)


def mark_perp(symbole, jusqu_a=None):
    """Klines 1d du MARK PRICE (prix qui déclenche les liquidations chez Binance)."""
    df, manquants = _assembler("markPrice1d", symbole, lire_klines_csv, jusqu_a)
    df = df[~df.index.duplicated(keep="first")]
    return df, manquants, _empreinte(df)


def nettoyer_funding(df):
    return df[~df.index.duplicated(keep="first")].sort_index()


SEUIL_ABERRANT = 0.003      # |taux| > 0,3 % par 8 h signalé (≈ 330 %/an) : vérifié à la main, pas supprimé


def qualite_funding(df):
    """Trous (attendu 3 paiements/jour avec intervalle 8 h), doublons, valeurs aberrantes."""
    d = df[~df.index.duplicated(keep="first")]
    ecarts = d.index.to_series().diff().dropna()
    pas = pd.Timedelta(hours=8)
    trous = ecarts[ecarts > pas + pd.Timedelta(minutes=5)]
    rapproches = ecarts[ecarts < pas - pd.Timedelta(minutes=5)]
    attendu = int((d.index[-1] - d.index[0]) / pas) + 1
    hors_grille = int(((d.index.hour % 8 != 0) | (d.index.minute != 0)).sum())
    par_jour = d.groupby(d.index.normalize()).size()
    z = (d.taux - d.taux.rolling(90, min_periods=30).median()).abs() / \
        (d.taux.rolling(90, min_periods=30).std() + 1e-12)
    return {
        "debut": str(d.index[0]), "fin": str(d.index[-1]),
        "paiements": int(len(d)), "paiements_attendus_8h": attendu,
        "manquants": int(attendu - len(d)),
        "nb_trous": int(len(trous)), "plus_long_trou": str(trous.max()) if len(trous) else "aucun",
        "trous_detail": [f"{a} (+{b})" for a, b in list(trous.items())[:10]],
        "ecarts_inferieurs_8h": int(len(rapproches)),
        "heures_hors_grille_00_08_16": hors_grille,
        "jours_pas_3_paiements": int((par_jour != 3).sum()),
        "intervalles_h": sorted({float(x) for x in d.intervalle_h.unique()}),
        "doublons": int(df.index.duplicated().sum()),
        "taux_min": float(d.taux.min()), "taux_max": float(d.taux.max()),
        "taux_moyen_annualise": float(d.taux.mean() * 3 * 365),
        "part_negatifs": float((d.taux < 0).mean()),
        "aberrants_abs_sup_0_3pct": int((d.taux.abs() > SEUIL_ABERRANT + 1e-12).sum()),
        "au_plafond_abs_0_3pct": int((d.taux.abs() >= SEUIL_ABERRANT - 1e-12).sum()),
        "aberrants_z_sup_10": int((z > 10).sum()),
        "nan": int(d.taux.isna().sum()),
    }


def qualite_klines(df):
    ecarts = df.index.to_series().diff().dropna()
    trous = ecarts[ecarts > pd.Timedelta(days=1)]
    attendu = int((df.index[-1] - df.index[0]) / pd.Timedelta(days=1)) + 1
    return {"debut": str(df.index[0].date()), "fin": str(df.index[-1].date()), "barres": int(len(df)),
            "manquantes": int(attendu - len(df)), "nb_trous": int(len(trous)),
            "prix_non_positifs": int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())}


# ---------- OKX (contrôle croisé, historique court) ----------
def funding_okx(symbole, max_pages=60):
    """BTCUSDT → BTC-USDT-SWAP. Pagination vers le passé avec 'after'. Cache CSV (rafraîchi si absent)."""
    DOSSIER.mkdir(parents=True, exist_ok=True)
    cache = DOSSIER / f"okx_{symbole}.csv"
    if cache.exists():
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    inst = symbole.replace("USDT", "-USDT-SWAP")
    lignes, apres = [], None
    for _ in range(max_pages):
        url = f"{OKX}?instId={inst}&limit=100" + (f"&after={apres}" if apres else "")
        b = _telecharger(url)
        lot = json.loads(b).get("data", []) if b else []
        if not lot:
            break
        lignes += lot
        apres = lot[-1]["fundingTime"]
        time.sleep(0.25)
    df = pd.DataFrame({"taux": [float(x["realizedRate"] or x["fundingRate"]) for x in lignes]},
                      index=pd.to_datetime([int(x["fundingTime"]) for x in lignes], unit="ms"))
    df.index.name = "t"
    df = df[~df.index.duplicated()].sort_index()
    df.to_csv(cache)
    return df


def controle_croise(binance, okx):
    """Compare les paiements aux mêmes horodatages."""
    b = nettoyer_funding(binance).taux
    commun = b.index.intersection(okx.index)
    if len(commun) < 10:
        return {"paiements_communs": int(len(commun))}
    x, y = b.loc[commun], okx.taux.loc[commun]
    return {"paiements_communs": int(len(commun)), "debut": str(commun[0]), "fin": str(commun[-1]),
            "correlation": float(np.corrcoef(x, y)[0, 1]),
            "binance_annualise": float(x.mean() * 3 * 365), "okx_annualise": float(y.mean() * 3 * 365),
            "ecart_absolu_moyen_par_paiement": float((x - y).abs().mean()),
            "meme_signe": float((np.sign(x) == np.sign(y)).mean())}
