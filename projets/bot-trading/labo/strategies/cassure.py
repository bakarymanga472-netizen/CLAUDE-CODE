"""Cassure de canal (Donchian) : entrée sur plus haut de N jours, sortie sur plus bas de N/2 jours."""
from .outils import etat

NOM = "cassure"
FAMILLE = "cassure / momentum"
HYPOTHESE = "Un nouveau plus haut de N jours est suivi d'une continuation plus souvent que d'un retour."


GRILLE = [{"jours": 20}, {"jours": 55}, {"jours": 100}]


def cible(df, bpj, jours):
    n = jours * bpj
    haut = df.high.rolling(n).max().shift(1)
    bas = df.low.rolling(max(2, n // 2)).min().shift(1)
    return etat(df.close > haut, df.close < bas)
