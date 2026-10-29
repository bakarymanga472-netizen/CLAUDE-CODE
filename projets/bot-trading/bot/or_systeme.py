"""Système « 7 agents sur l'or » (inspiré du reel Sentinel / Vortex / Phantom / Oracle / Kronos).

Chaque agent rend un avis -1 / 0 / +1 avec les seules données publiées à la date t.
Oracle transforme le consensus en probabilité, estimée sur le passé uniquement.
Kronos exécute à l'ouverture du lendemain et tient le journal.
"""
import json
import time
import urllib.request

import numpy as np
import pandas as pd

from . import data

YAHOO = ("https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
         "?period1=1136073600&period2={fin}&interval=1d")
COT = ("https://publicreporting.cftc.gov/resource/72hh-3qpy.json?$limit=5000"
       "&$where=market_and_exchange_names%20like%20%27GOLD%20-%20COMMODITY%20EXCHANGE%25%27"
       "&$order=report_date_as_yyyy_mm_dd%20ASC")
FRAIS = 0.0005   # 0,05 % par ordre (commission + glissement, prudent pour un future)
HORIZON = 20     # Oracle : probabilité de hausse à 20 jours de bourse


def _json(url):
    for essai in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if essai == 3:
                raise
            time.sleep(2 ** essai)


def prix_or(rafraichir=False):
    cache = data.DATA_DIR / "GC_F.csv"
    if cache.exists() and not rafraichir:
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    r = _json(YAHOO.format(fin=int(time.time())))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    df = pd.DataFrame({k: q[k] for k in ("open", "high", "low", "close", "volume")},
                      index=pd.to_datetime(r["timestamp"], unit="s").normalize())
    df = df.dropna(subset=["close"])
    df = df[~df.index.duplicated(keep="last")]
    df = df[df.index < pd.Timestamp.now().normalize()]
    data.DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(cache)
    return df


def cot_or(rafraichir=False):
    """Positions des gérants de fonds (managed money) sur l'or COMEX, rapport CFTC hebdomadaire."""
    cache = data.DATA_DIR / "cot_or.csv"
    if cache.exists() and not rafraichir:
        return pd.read_csv(cache, index_col=0, parse_dates=True)
    lignes = _json(COT)
    df = pd.DataFrame({
        "long": [float(x["m_money_positions_long_all"]) for x in lignes],
        "short": [float(x["m_money_positions_short_all"]) for x in lignes],
        "oi": [float(x["open_interest_all"]) for x in lignes],
    }, index=pd.to_datetime([x["report_date_as_yyyy_mm_dd"] for x in lignes]))
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df.to_csv(cache)
    return df


def taux_reels(rafraichir=False):
    cache = data.DATA_DIR / "DFII10.csv"
    if rafraichir or not cache.exists():
        data._telecharger(data.FRED.format("DFII10"), cache)
    d = pd.read_csv(cache, index_col=0, parse_dates=True, na_values=".")
    return pd.to_numeric(d.iloc[:, 0], errors="coerce").ffill()


def _aligne(serie, idx, decalage_jours):
    """Rend la série visible seulement `decalage_jours` après sa date (délai de publication)."""
    s = serie.copy()
    s.index = s.index + pd.Timedelta(days=decalage_jours)
    return s.reindex(idx.union(s.index)).ffill().reindex(idx)


def avis_agents(px, rafraichir=False):
    """DataFrame des avis -1/0/+1 des 5 agents d'analyse, indexé sur les jours de bourse de l'or."""
    idx = px.index
    c = px["close"]
    a = pd.DataFrame(index=idx)

    # AG-01 Sentinelle — macro : taux réels US 10 ans sous/sur leur moyenne 50 j (baisse = bon pour l'or)
    tr = taux_reels(rafraichir)
    a["sentinelle"] = _aligne(np.sign(tr.rolling(50).mean() - tr), idx, 1).fillna(0)

    # AG-02 Bouclier — valeur refuge : tension géopolitique dans le top 25 % de l'année → +1
    g = data.geopolitique(rafraichir).sort_index().rolling(7).mean()
    haut = (g > g.rolling(365, min_periods=200).quantile(0.75)).astype(int)
    a["bouclier"] = _aligne(haut, idx, 2).fillna(0)

    # AG-03 Vortex — structure technique : tendance MM50/MM200
    m50, m200 = c.rolling(50).mean(), c.rolling(200).mean()
    a["vortex"] = np.where((c > m50) & (m50 > m200), 1, np.where((c < m50) & (m50 < m200), -1, 0))

    # AG-04 Phantom — institutionnels COMEX : variation sur 4 semaines de la position nette des fonds,
    # -1 si leur position est dans le top 5 % de 3 ans (trop chargée). Rapport du mardi publié le vendredi.
    cot = cot_or(rafraichir)
    net = (cot["long"] - cot["short"]) / cot["oi"]
    tendance = np.sign(net.diff(4))
    rang = net.rolling(156, min_periods=52).rank(pct=True)
    phantom = tendance.where(rang <= 0.95, -1)
    a["phantom"] = _aligne(phantom, idx, 4).fillna(0)

    # AG-05 Atlas — dollar : dollar large sous sa moyenne 50 j → +1
    usd = data.macro(rafraichir)["DTWEXBGS"].dropna()
    a["atlas"] = _aligne(np.sign(usd.rolling(50).mean() - usd), idx, 1).fillna(0)
    return a.astype(int)


def oracle(avis, px, agents_actifs):
    """AG-06 Oracle : probabilité de hausse à 20 jours selon le niveau de consensus, apprise sur le passé.

    Pour le jour t, on n'utilise que les jours dont le résultat était connu à t (t - 20 et avant)."""
    score = avis[agents_actifs].sum(axis=1)
    hausse = (px["close"].shift(-HORIZON) > px["close"]).astype(float)
    hausse[px["close"].shift(-HORIZON).isna()] = np.nan
    proba = pd.Series(np.nan, index=avis.index)
    base = pd.Series(np.nan, index=avis.index)
    cumul, compte = {}, {}
    tot_h, tot_n = 0.0, 0
    vals_s, vals_h = score.values, hausse.values
    for i in range(len(score)):
        j = i - HORIZON                     # résultat du jour j connu au jour i
        if j >= 0 and not np.isnan(vals_h[j]):
            cumul[vals_s[j]] = cumul.get(vals_s[j], 0) + vals_h[j]
            compte[vals_s[j]] = compte.get(vals_s[j], 0) + 1
            tot_h += vals_h[j]
            tot_n += 1
        n = compte.get(vals_s[i], 0)
        if n >= 50 and tot_n >= 250:
            proba.iloc[i] = cumul[vals_s[i]] / n
            base.iloc[i] = tot_h / tot_n
    return score, proba, base


def kronos(px, entree, sortie, stop_atr=3.0):
    """AG-07 Kronos : exécution à l'ouverture du lendemain, stop suiveur, journal des trades.
    `entree` / `sortie` : séries booléennes décidées à la clôture."""
    o, h, l, c = (px[k].values for k in ("open", "high", "low", "close"))
    tr = pd.concat([px["high"] - px["low"], (px["high"] - px["close"].shift()).abs(),
                    (px["low"] - px["close"].shift()).abs()], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().values
    capital, en_pos, prix_e, pic, stop = 1.0, False, 0.0, 0.0, 0.0
    courbe, journal = [], []
    ordre = None
    for i in range(len(px)):
        if ordre == "achat" and not en_pos:
            en_pos, prix_e, pic = True, o[i] * (1 + FRAIS), o[i]
            stop = o[i] - stop_atr * atr[i - 1]
            j_entree = px.index[i]
        elif ordre == "vente" and en_pos:
            sortie_px = o[i] * (1 - FRAIS)
            capital *= sortie_px / prix_e
            journal.append((j_entree, px.index[i], prix_e, sortie_px, "signal"))
            en_pos = False
        ordre = None
        if en_pos and l[i] <= stop:
            sortie_px = min(o[i], stop) * (1 - FRAIS)
            capital *= sortie_px / prix_e
            journal.append((j_entree, px.index[i], prix_e, sortie_px, "stop"))
            en_pos = False
        valeur = capital * (c[i] / prix_e if en_pos else 1.0)
        courbe.append(valeur)
        if en_pos:
            pic = max(pic, c[i])
            stop = max(stop, pic - stop_atr * atr[i])
            if sortie.iloc[i]:
                ordre = "vente"
        elif entree.iloc[i]:
            ordre = "achat"
    if en_pos:
        journal.append((j_entree, px.index[-1], prix_e, c[-1], "fin"))
    t = pd.DataFrame(journal, columns=["entree", "sortie", "prix_entree", "prix_sortie", "raison"])
    if len(t):
        t["rendement"] = t.prix_sortie / t.prix_entree - 1
        t["jours"] = (t.sortie - t.entree).dt.days
    return pd.Series(courbe, index=px.index), t


def strategie(px, avis, agents_actifs, regle="oracle"):
    """Construit les signaux d'entrée/sortie puis exécute avec Kronos."""
    score, proba, base = oracle(avis, px, agents_actifs)
    if regle == "oracle":
        entree = (proba >= base + 0.05).fillna(False)
        sortie = (proba < base).fillna(True)
    else:  # « quand ils sont tous d'accord » : consensus fort
        n = len(agents_actifs)
        entree = score >= max(2, n - 2)
        sortie = score <= 0
    return kronos(px, entree, sortie)
