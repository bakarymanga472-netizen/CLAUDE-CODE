"""Ray Fu — « Complete Guide to building an AI Trading Bot with Claude for Beginners »."""
SOURCE = "https://youtu.be/oQdkFPhqaGk"
REGLES = ("Croisement de moyennes mobiles 20 et 50 jours sur Apple, 1 action. Achat quand la 20 croise au-dessus de la 50, "
          "vente quand elle repasse dessous. Vérification chaque matin à 9 h 30 (New York) avec les données Yahoo des 100 derniers jours.")
TRADUCTION = ("Décision avec la clôture de la veille, exécution à l'ouverture (moteur labo, execution='ouverture'). "
              "Long seulement, 100 % investi quand le signal est actif (pas de stop, comme dans la vidéo).")


def cible(df, court=20, long_=50):
    from .outils import sma
    return (sma(df.close, court) > sma(df.close, long_)).astype(float)
