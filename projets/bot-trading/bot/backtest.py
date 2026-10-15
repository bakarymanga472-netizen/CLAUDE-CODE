"""Moteur de backtest : décision à la clôture de t, exécution à l'ouverture de t+1, frais inclus."""
import numpy as np
import pandas as pd

from . import agents

FRAIS = 0.001       # 0,1 % par ordre (Binance standard)
GLISSEMENT = 0.0005  # 0,05 % de glissement par ordre


_CACHE = {}


def _lignes(marches, fng):
    """Convertit les DataFrames en dictionnaires {date: ligne} (100× plus rapide que .loc en boucle)."""
    cle = (id(marches), id(fng))
    if cle not in _CACHE:
        _CACHE[cle] = ({s: d.to_dict("index") for s, d in marches.items()}, fng.to_dict())
    return _CACHE[cle]


def executer(marches_df, fng_s, cfg, debut, fin, capital_initial=10_000.0, graine=0):
    rng = np.random.default_rng(graine)
    marches, fng = _lignes(marches_df, fng_s)
    dates = marches_df["BTCUSDT"].loc[debut:fin].index
    cash = capital_initial
    positions = {}          # sym -> dict(qte, prix_entree, stop, pic, date_entree, duree_max)
    ordres_achat, ordres_vente = [], []
    trades, courbe = [], []
    pic_capital = capital_initial

    def valeur(t):
        v = cash
        for s, p in positions.items():
            ligne = marches[s].get(t)
            px = ligne["close"] if ligne else p["dernier"]
            p["dernier"] = px
            v += p["qte"] * px
        return v

    for i, t in enumerate(dates):
        # 1) Exécution à l'ouverture des ordres décidés hier
        for sym in ordres_vente:
            if sym in positions and t in marches[sym]:
                p = positions.pop(sym)
                px = marches[sym][t]["open"] * (1 - GLISSEMENT)
                cash += p["qte"] * px * (1 - FRAIS)
                trades.append(_trade(sym, p, t, px))
        ordres_vente = []
        for prop, qte, stop in ordres_achat:
            sym = prop["symbole"]
            if sym in positions or t not in marches[sym] or len(positions) >= cfg.max_positions:
                continue
            px = marches[sym][t]["open"] * (1 + GLISSEMENT)
            cout = qte * px * (1 + FRAIS)
            if cout > cash:
                qte = cash / (px * (1 + FRAIS))
                cout = cash
            if qte <= 0:
                continue
            cash -= cout
            duree = int(rng.choice(cfg.durees_aleatoires)) if cfg.aleatoire else None
            positions[sym] = {"qte": qte, "prix_entree": px, "stop": stop, "pic": px,
                              "date_entree": t, "duree_max": duree, "dernier": px, "avis": prop}
        ordres_achat = []

        # 2) Stops touchés pendant la journée
        for sym in list(positions):
            ligne = marches[sym].get(t)
            if ligne is None:
                continue
            p = positions[sym]
            if p["stop"] > 0 and ligne["low"] <= p["stop"]:
                px = min(ligne["open"], p["stop"]) * (1 - GLISSEMENT)
                cash += p["qte"] * px * (1 - FRAIS)
                trades.append(_trade(sym, positions.pop(sym), t, px, "stop"))

        # 3) Décisions à la clôture
        capital = valeur(t)
        pic_capital = max(pic_capital, capital)
        drawdown = 1 - capital / pic_capital
        courbe.append((t, capital))
        if i == len(dates) - 1:
            break

        for sym, p in positions.items():
            ligne = marches[sym].get(t)
            if ligne is None:
                continue
            if cfg.agent_risque and not cfg.aleatoire:        # stop suiveur à 3 ATR sous le plus haut
                p["pic"] = max(p["pic"], ligne["close"])
                p["stop"] = max(p["stop"], p["pic"] - 3 * ligne["atr14"])
            if cfg.aleatoire:
                if (t - p["date_entree"]).days >= p["duree_max"]:
                    ordres_vente.append(sym)
            elif agents.doit_sortir(ligne, cfg):
                ordres_vente.append(sym)

        facteur = 0.5 if (cfg.agent_risque and drawdown > 0.20) else 1.0   # coupe-circuit
        places = cfg.max_positions - len(positions) + len(ordres_vente)
        props = agents.coordinateur(marches, fng, t, cfg, positions)
        if cfg.aleatoire:
            props = [p for p in props if rng.random() < cfg.proba_aleatoire]
            rng.shuffle(props)
        for prop in props[:max(places, 0)]:
            qte, stop = agents.taille_position(capital, marches[prop["symbole"]][t], cfg, facteur)
            ordres_achat.append((prop, qte, stop))

    # Clôture des positions restantes au dernier cours (pour compter les trades)
    t = dates[-1]
    for sym, p in list(positions.items()):
        px = p["dernier"]
        trades.append(_trade(sym, p, t, px, "fin"))
    return pd.Series(dict(courbe)), pd.DataFrame(trades)


def _trade(sym, p, t, px, raison="signal"):
    rendement = px * (1 - FRAIS) / (p["prix_entree"] * (1 + FRAIS)) - 1
    return {"symbole": sym, "entree": p["date_entree"], "sortie": t, "prix_entree": p["prix_entree"],
            "prix_sortie": px, "rendement": rendement, "pnl": p["qte"] * (px - p["prix_entree"]),
            "jours": (t - p["date_entree"]).days, "raison": raison}


def metriques(courbe, trades=None):
    r = courbe.pct_change().dropna()
    annees = (courbe.index[-1] - courbe.index[0]).days / 365.25
    total = courbe.iloc[-1] / courbe.iloc[0] - 1
    cagr = (1 + total) ** (1 / annees) - 1 if annees > 0 else np.nan
    dd = (courbe / courbe.cummax() - 1).min()
    sharpe = r.mean() / r.std() * np.sqrt(365) if r.std() > 0 else np.nan
    m = {"rendement_total": total, "cagr": cagr, "drawdown_max": dd, "sharpe": sharpe}
    if trades is not None and len(trades):
        gains = trades.loc[trades.pnl > 0, "pnl"].sum()
        pertes = -trades.loc[trades.pnl < 0, "pnl"].sum()
        m.update({"trades": len(trades), "taux_reussite": (trades.pnl > 0).mean(),
                  "profit_factor": gains / pertes if pertes > 0 else np.inf,
                  "duree_moy_jours": trades.jours.mean()})
    return m


def achat_conserve(marches, symboles, debut, fin, capital=10_000.0):
    """Référence : on achète à parts égales au début et on ne touche plus à rien (frais d'achat inclus)."""
    dispo = [s for s in symboles if len(marches[s].loc[debut:fin]) and marches[s].loc[debut:fin].index[0] <= pd.Timestamp(debut) + pd.Timedelta(days=3)]
    part = capital / len(dispo)
    total = None
    for s in dispo:
        c = marches[s].loc[debut:fin, "close"]
        v = part * (1 - FRAIS) * c / c.iloc[0]
        total = v if total is None else total.add(v, fill_value=0)
    return total.reindex(marches["BTCUSDT"].loc[debut:fin].index).ffill()
