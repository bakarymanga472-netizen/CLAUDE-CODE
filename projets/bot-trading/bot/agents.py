"""Les 5 agents spécialisés + le coordinateur.

Chaque agent ne voit que les données disponibles à la clôture du jour t (pas de triche sur le futur).
Les décisions prises à la clôture de t sont exécutées à l'ouverture de t+1 par le moteur.
"""
from dataclasses import dataclass, field

import pandas as pd


def indicateurs(df):
    """Ajoute les colonnes utilisées par les agents (toutes calculées sur le passé)."""
    d = df.copy()
    d["sma50"] = d["close"].rolling(50).mean()
    d["sma200"] = d["close"].rolling(200).mean()
    d["haut20"] = d["high"].rolling(20).max().shift(1)          # plus haut des 20 jours PRÉCÉDENTS
    d["roc30"] = d["close"].pct_change(30)
    tr = pd.concat([d["high"] - d["low"],
                    (d["high"] - d["close"].shift()).abs(),
                    (d["low"] - d["close"].shift()).abs()], axis=1).max(axis=1)
    d["atr14"] = tr.rolling(14).mean()
    d["vol20"] = d["volume"].rolling(20).mean().shift(1)        # volume moyen des 20 jours précédents
    d["vol30"] = d["volume"].rolling(30).mean()
    return d


@dataclass
class Config:
    nom: str = "complet"
    agent_setups: bool = True
    agent_sentiment: bool = True
    agent_flux: bool = True
    agent_risque: bool = True
    agent_macro: bool = False        # MacroMicro-like (taux 10 ans + dollar)
    agent_geopolitique: bool = False  # World Monitor-like (indice de risque géopolitique)
    top_scanner: int = 5            # nb d'actifs retenus par le scanner
    max_positions: int = 4
    risque_par_trade: float = 0.01  # 1 % du capital risqué par trade (stop à 2 ATR)
    plafond_position: float = 0.25  # 25 % du capital max par position
    seuil_avidite: int = 80         # Fear & Greed au-dessus → pas de nouvel achat
    seuil_peur: int = 25            # en dessous → bonus
    aleatoire: bool = False         # référence : entrées tirées au hasard
    proba_aleatoire: float = 0.0
    durees_aleatoires: list = field(default_factory=list)


# ---------- Agent 1 : scanner de marché ----------
def scanner(marches, t, cfg):
    """Garde les actifs les plus liquides qui ont assez d'historique."""
    candidats = []
    for sym, d in marches.items():
        ligne = d.get(t)
        if ligne is None:
            continue
        if pd.isna(ligne["sma200"]) or pd.isna(ligne["vol30"]):
            continue
        candidats.append((ligne["vol30"], sym))
    candidats.sort(reverse=True)
    return [s for _, s in candidats[:cfg.top_scanner]]


# ---------- Agent 2 : recherche de setups ----------
def setups(ligne, cfg):
    """Score 0-3 : tendance haussière, cassure des 20 jours, momentum 30 jours."""
    if not cfg.agent_setups:
        return 2
    tendance = ligne["close"] > ligne["sma50"] > ligne["sma200"]
    cassure = ligne["close"] > ligne["haut20"]
    momentum = ligne["roc30"] > 0
    return int(tendance) + int(cassure) + int(momentum)


# ---------- Agent 3 : sentiment ----------
def sentiment(fng, t, cfg):
    """-1 = veto (avidité extrême), +1 = peur extrême, 0 = neutre."""
    v = fng.get(t) if cfg.agent_sentiment else None
    if v is None:
        return 0
    if v >= cfg.seuil_avidite:
        return -1
    if v <= cfg.seuil_peur:
        return 1
    return 0


# ---------- Agent 4 : flux (proxy des « baleines ») ----------
def flux(ligne, cfg):
    """Volume anormal (> 1,5 × moyenne) : +1 s'il accompagne une hausse, -1 une baisse.
    C'est un PROXY : pas de vraies données on-chain dans ce test."""
    if not cfg.agent_flux or pd.isna(ligne["vol20"]) or ligne["vol20"] == 0:
        return 0
    if ligne["volume"] / ligne["vol20"] < 1.5:
        return 0
    return 1 if ligne["close"] > ligne["open"] else -1


# ---------- Agent 5 : risque ----------
def taille_position(capital, ligne, cfg, facteur_risque=1.0):
    """Nombre d'unités à acheter et stop initial."""
    atr = ligne["atr14"]
    prix = ligne["close"]
    if cfg.agent_risque:
        stop = prix - 2 * atr
        qte = (capital * cfg.risque_par_trade * facteur_risque) / (2 * atr)
        qte = min(qte, capital * cfg.plafond_position / prix)
    else:
        stop = 0.0
        qte = capital * cfg.plafond_position / prix
    return qte, stop


# ---------- Agent 6 : macro (inspiré de MacroMicro) ----------
def contexte_macro_geo(macro_df, gpr, dates):
    """Prépare, pour chaque jour, les avis macro et géopolitique (données du passé seulement).
    Décalages de publication : FRED +1 jour, indice géopolitique +2 jours."""
    idx = pd.DatetimeIndex(dates)
    m = macro_df.sort_index().ffill()
    taux_haut = m["DGS10"] > m["DGS10"].rolling(50).mean()
    dollar_haut = m["DTWEXBGS"] > m["DTWEXBGS"].rolling(50).mean()
    score_macro = pd.Series(0, index=m.index)
    score_macro[taux_haut & dollar_haut] = -1      # conditions financières qui se resserrent
    score_macro[~taux_haut & ~dollar_haut] = 1     # conditions qui se détendent
    score_macro = score_macro.shift(1, freq="D").reindex(idx, method="ffill").fillna(0)

    g = gpr.sort_index()
    g7 = g.rolling(7).mean()
    seuil = g7.rolling(365, min_periods=200).quantile(0.90)
    score_geo = -(g7 > seuil).astype(int)        # -1 si tension géopolitique dans le top 10 % de l'année
    score_geo = score_geo.shift(2, freq="D").reindex(idx, method="ffill").fillna(0)
    return {t: {"macro": int(a), "geo": int(b)} for t, a, b in zip(idx, score_macro.values, score_geo.values)}


# ---------- Coordinateur ----------
def coordinateur(marches, fng, t, cfg, positions, ctx=None):
    """`marches` : {symbole: {date: ligne}} ; `fng` : {date: valeur}.
    Retourne la liste des propositions d'achat triées, chacune avec l'avis de chaque agent."""
    sent = sentiment(fng, t, cfg)
    avis = (ctx or {}).get(t, {"macro": 0, "geo": 0})
    mac = avis["macro"] if cfg.agent_macro else 0
    geo = avis["geo"] if cfg.agent_geopolitique else 0
    propositions = []
    for sym in scanner(marches, t, cfg):
        if sym in positions:
            continue
        ligne = marches[sym][t]
        s, f = setups(ligne, cfg), flux(ligne, cfg)
        if cfg.aleatoire:
            ok = True
        else:
            ok = s >= 2 and sent >= 0 and f >= 0 and mac >= 0 and geo >= 0
        if ok:
            propositions.append({"symbole": sym, "date": t, "prix": ligne["close"],
                                 "setups": s, "sentiment": sent, "flux": f, "macro": mac, "geo": geo,
                                 "score": s + sent + f + mac})
    propositions.sort(key=lambda p: -p["score"])
    return propositions


def doit_sortir(ligne, cfg):
    """Sortie de tendance : clôture sous la moyenne 50 jours."""
    return cfg.agent_setups and ligne["close"] < ligne["sma50"]
