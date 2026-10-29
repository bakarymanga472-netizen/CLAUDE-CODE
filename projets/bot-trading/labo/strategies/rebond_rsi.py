"""Retour à la moyenne court terme : achat d'un repli (RSI-2 bas) dans une tendance haussière (cours > MM200 jours)."""
from .outils import etat, rsi

NOM = "rebond_rsi"
FAMILLE = "retour à la moyenne"
HYPOTHESE = "Un excès de baisse de courte durée dans une tendance haussière se corrige en quelques barres."
GRILLE = [{"seuil": 5}, {"seuil": 10}, {"seuil": 20}]


def cible(df, bpj, seuil):
    r2 = rsi(df.close, 2)
    mm200 = df.close.rolling(200 * bpj).mean()
    mm5 = df.close.rolling(5).mean()
    return etat((r2 < seuil) & (df.close > mm200), (df.close > mm5) | (df.close < mm200))
