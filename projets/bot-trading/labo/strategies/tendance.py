"""Momentum de série temporelle (Moskowitz-Ooi-Pedersen 2012) : exposé si le rendement passé sur L jours est positif."""
NOM = "tendance"
FAMILLE = "suivi de tendance"
HYPOTHESE = "Les rendements passés sur 1 à 6 mois ont le même signe que les rendements futurs (persistance)."
GRILLE = [{"jours": 30}, {"jours": 90}, {"jours": 180}]


def cible(df, bpj, jours):
    return (df.close / df.close.shift(jours * bpj) - 1 > 0).astype(float)
