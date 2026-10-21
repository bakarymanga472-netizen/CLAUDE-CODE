"""Nico Trade — « Créer un Bot de Trading Performant avec Claude Code »."""
from .outils import assembler, atr

SOURCE = "https://youtu.be/Y8FO8hnfJuo"
REGLES = ("Bot basé sur son indicateur « Kumo Stream » (non public) : entrée sur les étiquettes buy/sell, stop = 2 × ATR, "
          "objectif = 2R. Le reste de la vidéo porte sur l'outillage (MCP TradingView, skills concepteur/architecte/développeur).")
TRADUCTION = ("APPROXIMATION : l'indicateur réel n'est pas publié. « Kumo » = nuage d'Ichimoku ; on prend le signal "
              "classique : clôture qui sort du nuage (9/26/52) avec Tenkan au-dessus (en dessous) de Kijun. "
              "Ce test ne juge donc PAS son indicateur, seulement l'idée générique.")
GRILLE = [{"atr_mult": 2.0, "tp_R": 2.0}]


def signaux(df, atr_mult=2.0, tp_R=2.0):
    hh = lambda n: df.high.rolling(n).max()
    ll = lambda n: df.low.rolling(n).min()
    tenkan, kijun = (hh(9) + ll(9)) / 2, (hh(26) + ll(26)) / 2
    span_a = ((tenkan + kijun) / 2).shift(26)
    span_b = ((hh(52) + ll(52)) / 2).shift(26)
    haut, bas = span_a.combine(span_b, max), span_a.combine(span_b, min)
    long_ = (df.close > haut) & (df.close.shift(1) <= haut.shift(1)) & (tenkan > kijun)
    short_ = (df.close < bas) & (df.close.shift(1) >= bas.shift(1)) & (tenkan < kijun)
    a = atr(df, 14)
    return assembler(df, long_, short_, df.close - atr_mult * a, df.close + atr_mult * a, tp_R)
