"""Carry — stratégie long spot + short perpétuel (delta-neutre) et backtest journalier sans look-ahead.

Chronologie :
  - Paiements de funding Binance à 00:00, 08:00, 16:00 UTC. Le « funding du jour t » = paiements de t 08:00, t 16:00
    et t+1 00:00 : ce sont ceux encaissés par une position ouverte à l'ouverture (00:00) du jour t et tenue jusqu'à
    l'ouverture du jour t+1.
  - Décision pour le jour t : indicateur calculé avec les paiements STRICTEMENT antérieurs à t 00:00 (le paiement de
    t 00:00 lui-même est ignoré : conservateur d'un paiement).
  - Exécution des 2 jambes à l'ouverture (00:00 UTC) du jour t, au prix d'ouverture spot ET perp du même jour :
    l'écart de base perp/spot à l'entrée et à la sortie est donc dans le PnL.
Capital : 50 % spot, 50 % en marge USDT sur le perp, short de même notionnel → levier 1 sur la jambe short.
Rééquilibrage : vérifié chaque jour à l'ouverture ; exécuté si une jambe s'écarte de plus de BANDE de sa cible (E/2).
Liquidation : contrôlée chaque jour avec le PLUS HAUT perp du jour (pire cas intrajournalier).
Approximation : le funding est payé sur le notionnel au prix perp d'ouverture du jour (et non au mark exact de 08:00/16:00/00:00).
La marge USDT ne rapporte rien (hypothèse : placement sans risque à 0 %).
"""
from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

# ---------- Grille FIXÉE avant tout test (2026-10-20) ----------
GRILLE = [{"type": "passive"}] + [
    {"type": "conditionnelle", "N": n, "entree": e, "sortie": 0.0} for n in (3, 21) for e in (0.10, 0.20)]
SYMBOLES = ["BTCUSDT", "ETHUSDT"]
N_VARIANTES_TOTAL = len(GRILLE) * len(SYMBOLES)          # 10 : sert au DSR


def nom(p):
    return "passive" if p["type"] == "passive" else f"cond_N{p['N']}_in{int(p['entree']*100)}_out{int(p['sortie']*100)}"


@dataclass(frozen=True)
class CoutsCarry:
    commission_spot: float = 0.0010      # taker spot Binance, sans remise
    commission_perp: float = 0.0005      # taker USDT-M
    glissement_spot: float = 0.0002      # hypothèse (inclut le demi-spread)
    glissement_perp: float = 0.0002
    marge_maintenance: float = 0.004     # hypothèse : palier 1 BTC/ETH USDT-M
    bande: float = 0.05                  # rééquilibrage si une jambe s'écarte de > 5 % de sa cible

    @property
    def spot(self):
        return self.commission_spot + self.glissement_spot

    @property
    def perp(self):
        return self.commission_perp + self.glissement_perp

    def stresse(self, f):
        return replace(self, commission_spot=self.commission_spot * f, commission_perp=self.commission_perp * f,
                       glissement_spot=self.glissement_spot * f, glissement_perp=self.glissement_perp * f)


# ---------- Préparation ----------
def funding_journalier(fund):
    """fund : Series de taux indexée par heure de paiement. Renvoie la somme des paiements dans ]t 00:00, t+1 00:00]."""
    jour = (fund.index - pd.Timedelta(minutes=1)).normalize()
    return fund.groupby(jour).sum()


def indicateur(fund, n, jours):
    """Moyenne des n derniers paiements annualisée (×3×365), connue STRICTEMENT avant jours (00:00)."""
    m = fund.rolling(n, min_periods=n).mean() * 3 * 365
    return m.reindex(m.index.union(jours - pd.Timedelta(seconds=1))).ffill().loc[jours - pd.Timedelta(seconds=1)] \
        .set_axis(jours)


def aligner(spot, perp, fund):
    """Cadre journalier commun. Le dernier jour exige le paiement de t+1 00:00 et l'ouverture de t+1."""
    fj = funding_journalier(fund)
    dernier_paiement = fund.index.max()
    jours = spot.index.intersection(perp.index)
    jours = jours[(jours >= fund.index.min().normalize()) & (jours + pd.Timedelta(days=1) <= dernier_paiement)]
    df = pd.DataFrame({"s_open": spot.open, "f_open": perp.open, "f_high": perp.high}).loc[jours]
    df["s_next"] = spot.open.reindex(jours + pd.Timedelta(days=1)).values
    df["f_next"] = perp.open.reindex(jours + pd.Timedelta(days=1)).values
    df["funding_jour"] = fj.reindex(jours).fillna(0.0)
    return df.dropna()


def positions(fund, jours, p):
    """Exposition voulue (0/1) pour chaque jour, décidée avec des données passées uniquement."""
    if p["type"] == "passive":
        return pd.Series(1.0, index=jours)
    ind = indicateur(fund, p["N"], jours).values
    out, cur = np.zeros(len(jours)), 0.0
    for i, x in enumerate(ind):
        if np.isnan(x):
            cur = 0.0
        elif cur == 0.0 and x > p["entree"]:
            cur = 1.0
        elif cur == 1.0 and x < p["sortie"]:
            cur = 0.0
        out[i] = cur
    return pd.Series(out, index=jours)


# ---------- Simulation ----------
def simuler(df, pos, c=CoutsCarry(), clore_a_la_fin=True):
    """Boucle journalière en unités monétaires (capital initial 1). Renvoie rendements nets, détail et trades."""
    n = len(df)
    E = 1.0
    cash, qs, qp, mg = 1.0, 0.0, 0.0, 0.0
    net, funding_recu, couts, expo, liq = (np.zeros(n) for _ in range(5))
    pos = pos.reindex(df.index).fillna(0.0).values
    so, fo, fh = df.s_open.values, df.f_open.values, df.f_high.values
    sn, fn, fj = df.s_next.values, df.f_next.values, df.funding_jour.values
    en_pos = False
    for i in range(n):
        S, F = so[i], fo[i]
        E0 = cash + qs * S + mg
        cout = 0.0
        if pos[i] == 1.0 and not en_pos:                       # entrée : 4 jambes = 2 ici + 2 à la sortie
            cout = E0 / 2 * c.spot + E0 / 2 * c.perp
            E1 = E0 - cout
            qs, qp, mg, cash = E1 / 2 / S, E1 / 2 / F, E1 / 2, 0.0
            en_pos = True
        elif pos[i] == 0.0 and en_pos:                         # sortie
            cout = qs * S * c.spot + qp * F * c.perp
            cash, qs, qp, mg = E0 - cout, 0.0, 0.0, 0.0
            en_pos = False
        elif en_pos:                                           # rééquilibrage éventuel (marge et neutralité)
            cible = E0 / 2
            if abs(qs * S / cible - 1) > c.bande or abs(mg / cible - 1) > c.bande:
                nqs, nqp = cible / S, cible / F
                cout = abs(nqs - qs) * S * c.spot + abs(nqp - qp) * F * c.perp
                E1 = E0 - cout
                qs, qp, mg = E1 / 2 / S, E1 / 2 / F, E1 / 2
        couts[i] = cout
        if en_pos:
            H = fh[i]
            if mg - qp * (H - F) <= c.marge_maintenance * qp * H:   # liquidation de la jambe short
                liq[i] = 1.0
                cash = qs * sn[i] * (1 - c.spot)                  # marge perdue, spot vendu (à l'ouverture suivante)
                qs = qp = mg = 0.0
                en_pos = False
            else:
                f = qp * F * fj[i]
                funding_recu[i] = f
                mg += -qp * (fn[i] - F) + f
                expo[i] = 1.0
        E = cash + qs * sn[i] + mg
        net[i] = E / E0 - 1
    if clore_a_la_fin and en_pos:                              # frais de sortie finaux imputés au dernier jour
        cout = qs * sn[-1] * c.spot + qp * fn[-1] * c.perp
        couts[-1] += cout
        net[-1] = (E - cout) / (E / (1 + net[-1])) - 1
    idx = df.index
    r = pd.Series(net, index=idx)
    w = pd.Series(expo, index=idx)
    return {"net": r, "w": w, "couts": pd.Series(couts, index=idx), "funding": pd.Series(funding_recu, index=idx),
            "liquidations": pd.Series(liq, index=idx), "pos": pd.Series(pos, index=idx),
            "trades": trades(r, pd.Series(pos, index=idx))}


def trades(net, pos):
    """Un trade = jours d'exposition continue + le jour de sortie (qui porte les frais de sortie)."""
    a = pos.values == 1.0
    lignes, i, n = [], 0, len(a)
    while i < n:
        if not a[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and a[j + 1]:
            j += 1
        fin = min(j + 1, n - 1)
        seg = net.values[i:fin + 1]
        lignes.append({"entree": net.index[i], "sortie": net.index[fin], "jours": fin - i + 1,
                       "net": float(np.prod(1 + seg) - 1), "R": np.nan})
        i = fin + 1
    return pd.DataFrame(lignes, columns=["entree", "sortie", "jours", "net", "R"])


# ---------- Liquidation contrefactuelle (rééquilibrage quotidien, levier variable) ----------
def seuil_liquidation(levier, mm):
    """Hausse du perp depuis le dernier rééquilibrage qui épuise la marge : 1/levier - x = mm (1 + x)."""
    return (1 / levier - mm) / (1 + mm)


def liquidations_quotidiennes(perp, debut, fin, leviers=(1, 2, 3, 5), mm=0.004):
    """Rééquilibrage chaque jour à l'ouverture ; pire cas = plus haut du jour. Compte les jours de liquidation."""
    p = perp.loc[debut:fin]
    hausse = p.high / p.open - 1
    return {"hausse_intrajour_max": float(hausse.max()), "date_max": str(hausse.idxmax().date()),
            **{f"levier_{l}": {"seuil_hausse": round(seuil_liquidation(l, mm), 4),
                               "jours_liquides": int((hausse >= seuil_liquidation(l, mm)).sum())} for l in leviers}}
