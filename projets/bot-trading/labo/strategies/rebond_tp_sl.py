"""Rebond (structure « Aladdin Rebond » figée le 2026-10-15), réécrite en SÉANCES réelles.

Signal à la clôture t : RSI-2 < seuil et clôture > moyenne des 200 dernières SÉANCES.
Entrée : clôture t+1 (ordre au cours de clôture). Prix d'entrée = clôture t+1.
Sortie décidée à une clôture j ≥ t+1 si gain ≥ objectif, ou perte ≥ stop, ou j - (t+1) ≥ durée (en séances) ;
exécutée à la clôture j+1. Le moteur doit être appelé avec execution="cloture".
"""
import numpy as np
import pandas as pd

from .outils import rsi

NOM = "rebond_tp_sl"
FAMILLE = "retour à la moyenne"
HYPOTHESE = "Un repli de très court terme dans une tendance haussière se corrige rapidement."
GRILLE = [{"seuil": 5, "tp": 0.01, "sl": 0.10, "duree": 20}]     # règle figée, pas d'optimisation


def cible(df, bpj, seuil, tp, sl, duree):
    c = df.close.values
    sig = ((rsi(df.close, 2) < seuil) & (df.close > df.close.rolling(200).mean())).values
    out = np.zeros(len(c))
    etat, entree_i = 0, None          # 0 à plat, 1 en attente d'exécution, 2 en position
    for i in range(len(c)):
        if etat == 0:
            if sig[i]:
                etat, entree_i = 1, i + 1
        elif etat == 1:               # i = séance d'exécution : le prix d'entrée c[i] est maintenant connu
            etat = 2
        if etat == 2:
            g = c[i] / c[entree_i] - 1
            if g >= tp or g <= -sl or (i - entree_i) >= duree:
                etat = 0              # vente à la clôture suivante
        out[i] = 1.0 if etat else 0.0
    return pd.Series(out, index=df.index)
