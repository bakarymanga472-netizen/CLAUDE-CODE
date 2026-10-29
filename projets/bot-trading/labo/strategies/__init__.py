"""Stratégies candidates, chacune dans un module indépendant.

Contrat de chaque module :
  NOM, FAMILLE, HYPOTHESE (texte), GRILLE (liste de dicts de paramètres, FIXÉE AVANT les tests),
  cible(df, bpj, **p) -> pd.Series dans [0, 1] : exposition voulue, décidée à la CLÔTURE de chaque barre
  avec uniquement les données jusqu'à cette barre incluse. L'exécution (barre suivante) est faite par le moteur.
"""
from . import achat_conservation, cassure, croisement_mm, rebond_rsi, tendance

CANDIDATES = [tendance, cassure, croisement_mm, rebond_rsi]
REFERENCES = [achat_conservation]
