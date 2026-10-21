"""DÉMONSTRATION (pas une stratégie à utiliser) : ce que donne un bot à « 99 % de réussite » très agressif.

Règle : on achète à la clôture ; on revend dès que le cours touche +objectif (ordre limite, plus haut du jour) ;
AUCUN stop (c'est la seule façon d'avoir ~99 % de trades gagnants) ; on rachète à la clôture suivante.
Levier L : la position est liquidée si le plus bas du jour fait perdre la marge (perte ≥ 90 % de 1/L).
Coûts : 0,10 % par côté (crypto), 0,01 % (indices) ; emprunt 5 %/an sur la part empruntée quand levier > 1 (hypothèse).
Résultats (2026-10-21) : ~100 % de réussite sans levier mais moins que l'achat-conservation et -55 à -83 % de baisse ;
levier ×2 ou ×3 : compte détruit sur SPY, QQQ, Nikkei, Euro Stoxx 50 et BTC selon la date de départ.
Usage : python3 -m labo.demo_99
"""
import numpy as np
import pandas as pd

from . import donnees


def simuler(df, objectif, levier, frais, taux_emprunt=0.0):
    o, h, l, c = (df[k].values for k in ("open", "high", "low", "close"))
    capital, gagnes, perdus, i, n = 1.0, 0, 0, 0, len(df)
    courbe = np.ones(n)
    ruine = None
    seuil_liq = 0.9 / levier
    while i < n - 1:
        p0 = c[i]
        j = i + 1
        sortie = None
        while j < n:
            if l[j] <= p0 * (1 - seuil_liq):                      # liquidation : la marge est perdue
                sortie = ("liquidation", -seuil_liq)
                break
            if h[j] >= p0 * (1 + objectif):                       # objectif touché
                sortie = ("objectif", objectif)
                break
            courbe[j] = capital * (1 + levier * (c[j] / p0 - 1))
            j += 1
        if sortie is None:                                         # trade encore ouvert à la fin des données
            courbe[i + 1:] = capital * (1 + levier * (c[i + 1:] / p0 - 1)) if j >= n else courbe[i + 1:]
            break
        jours = (df.index[j] - df.index[i]).days
        r = levier * sortie[1] - 2 * frais * levier - (levier - 1) * taux_emprunt * jours / 365
        capital *= max(1 + r, 0.0)
        gagnes += r > 0
        perdus += r <= 0
        courbe[j:] = capital
        if capital <= 0.05:
            ruine = df.index[j]
            courbe[j:] = capital
            break
        i = j
    s = pd.Series(courbe, index=df.index)
    return {"trades": gagnes + perdus, "reussite": gagnes / max(gagnes + perdus, 1), "capital_final": capital,
            "pire_baisse": float((s / s.cummax() - 1).min()), "ruine": ruine}


def main():
    btc, _ = donnees.charger("BTCUSDT", "1d")
    spy, _ = donnees.charger_yahoo("SPY")
    lignes = []
    for nom, df, obj, frais in (("BTC", btc, 0.01, 0.001), ("SPY", spy, 0.005, 0.0001)):
        bh = df.close.iloc[-1] / df.close.iloc[0]
        for L in (1, 3, 10):
            m = simuler(df, obj, L, frais)
            lignes.append(f"| {nom} | +{obj:.1%} | ×{L} | {m['trades']} | {m['reussite']:.1%} | {m['capital_final']:.2f} × "
                          f"(achat-gardé : {bh:.1f} ×) | {m['pire_baisse']:.0%} | {m['ruine'].date() if m['ruine'] is not None else '—'} |")
    print("| Actif | Objectif | Levier | Trades | Réussite | Capital final | Pire baisse | Compte détruit le |")
    print("|---|---|---|---|---|---|---|---|")
    print("\n".join(lignes))


if __name__ == "__main__":
    main()
