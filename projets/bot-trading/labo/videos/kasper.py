"""Kasper — « J'ai demandé à Claude IA de me rapporter le plus d'argent possible en 1h »."""
from .outils import assembler, atr, session_paris

SOURCE = "https://youtu.be/sLmUHb4WloQ"
REGLES = ("« Liquidity sweep » en 5 minutes (EUR/USD, GBP/USD, DAX, CAC) : repérer une poche de liquidité (plus bas/haut "
          "récent, double creux, zone non encore cassée), attendre que le prix la dépasse (« sweep ») puis referme à "
          "l'intérieur, entrer sur ce retournement, stop au-delà de la mèche, objectif la liquidité opposée (≈ 2R). "
          "Résultat dans la vidéo : +42 € en 1 heure sur quelques trades, en discrétionnaire.")
TRADUCTION = ("Poche = plus bas (plus haut) des `lookback` barres précédentes, en excluant les 3 dernières, et pas encore "
              "touchée par ces 3 dernières. Sweep = mèche au-delà puis clôture revenue de l'autre côté. Stop = extrême de la "
              "mèche ± 0,05 ATR. Objectif 2R. Plage 08:00–18:00 heure de Paris.")
GRILLE = [{"lookback": 20, "tp_R": 2.0}, {"lookback": 50, "tp_R": 2.0}]


def signaux(df, lookback=20, tp_R=2.0, ecart=3):
    bas = df.low.shift(ecart).rolling(lookback).min()
    haut = df.high.shift(ecart).rolling(lookback).max()
    vierge_bas = df.low.shift(1).rolling(ecart).min() > bas
    vierge_haut = df.high.shift(1).rolling(ecart).max() < haut
    a = atr(df, 14)
    ses = session_paris(df.index, "08:00", "18:00")
    long_ = vierge_bas & (df.low < bas) & (df.close > bas) & ses
    short_ = vierge_haut & (df.high > haut) & (df.close < haut) & ses
    return assembler(df, long_, short_, df.low - 0.05 * a, df.high + 0.05 * a, tp_R)
