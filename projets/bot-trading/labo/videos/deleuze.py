"""Benjamin Deleuze — « J'ai testé une stratégie de trading créée par Claude IA pendant 24h »."""
from .outils import assembler, ema, session_paris

SOURCE = "https://youtu.be/4pbodmoCeMk"
REGLES = ("Forex en 5 minutes. Filtre de tendance par moyenne mobile (acheter au-dessus, vendre en dessous), séance de "
          "trading fixe (Londres puis New York, 9 h – 18 h à Paris), bougie englobante qui englobe les 2 (ou 3) bougies "
          "précédentes mèches comprises, stop sous (sur) l'englobante, objectif 2R, stop ramené au prix d'entrée à 1R, "
          "5 % de risque par trade. Conclusion de l'auteur lui-même : stratégie sans avantage, résultats dus au hasard.")
TRADUCTION = ("Moyenne mobile = EMA 50 (la vidéo ne précise pas la période). Plage 09:30–18:00 heure de Paris. "
              "Englobante haussière : bougie verte dont le plus haut dépasse et le plus bas passe sous les N bougies précédentes.")
GRILLE = [{"n": 2, "tp_R": 2.0}, {"n": 3, "tp_R": 2.0}]
BE_R = 1.0


def signaux(df, n=2, tp_R=2.0):
    hh = df.high.shift(1).rolling(n).max()
    ll = df.low.shift(1).rolling(n).min()
    englobe = (df.high > hh) & (df.low < ll)
    e = ema(df.close, 50)
    ses = session_paris(df.index)
    long_ = englobe & (df.close > df.open) & (df.close > e) & ses
    short_ = englobe & (df.close < df.open) & (df.close < e) & ses
    return assembler(df, long_, short_, df.low, df.high, tp_R)
