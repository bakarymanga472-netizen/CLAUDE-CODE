"""Roro Crypto (Romain, InvestX) — « Stratégie ULTRA RENTABLE grâce à l'IA (merci Claude) »."""
from .outils import assembler, atr, sma

SOURCE = "https://youtu.be/H1sEgRpYfxg"
REGLES = ("SMA 20 au-dessus de la SMA 50 = tendance haussière ; quand le prix touche la SMA 20, achat ; stop « sous l'ATR » ; "
          "objectif = 1,5 fois le risque. Inverse en tendance baissière (vente à découvert). Testé dans la vidéo sur SOL "
          "en 30 min, 1 h, 2 h et 4 h depuis septembre 2020 ; meilleure unité de temps choisie après coup : 4 h "
          "(profit factor 1,2, réussite 46 %, pire baisse 8 %). La version « 81 % de réussite, profit factor 8,6 » n'est PAS publique.")
TRADUCTION = ("Contact = le plus bas (achat) ou le plus haut (vente) de la barre atteint la SMA 20. "
              "Stop = clôture − 1 × ATR(14) (achat) ou + 1 × ATR(14) (vente). Entrée à l'ouverture suivante.")
GRILLE = [{"atr_mult": 1.0, "tp_R": 1.5}]


def signaux(df, atr_mult=1.0, tp_R=1.5):
    s20, s50, a = sma(df.close, 20), sma(df.close, 50), atr(df, 14)
    long_ = (s20 > s50) & (df.low <= s20)
    short_ = (s20 < s50) & (df.high >= s20)
    return assembler(df, long_, short_, df.close - atr_mult * a, df.close + atr_mult * a, tp_R)
