"""Croisement de moyennes mobiles : exposé quand la moyenne courte est au-dessus de la longue."""
NOM = "croisement_mm"
FAMILLE = "suivi de tendance"
HYPOTHESE = "La position relative de deux moyennes lisse le bruit et capte les tendances de moyen terme."
GRILLE = [{"court": 10, "long": 50}, {"court": 20, "long": 100}, {"court": 50, "long": 200}]


def cible(df, bpj, court, long):
    return (df.close.rolling(court * bpj).mean() > df.close.rolling(long * bpj).mean()).astype(float)
