NOM = "achat_conservation"
FAMILLE = "référence"
HYPOTHESE = "Référence : exposition permanente."
GRILLE = [{}]


def cible(df, bpj):
    import pandas as pd
    return pd.Series(1.0, index=df.index)
