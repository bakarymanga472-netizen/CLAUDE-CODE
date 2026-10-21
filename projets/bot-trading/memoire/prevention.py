"""Règles de prévention : chaque erreur de processus/exécution confirmée est transformée en un contrôle AVANT ordre,
couvert par un test automatisé (tests/test_memoire.py). On ne prétend pas que l'erreur ne se reproduira plus :
on vérifie seulement que ce contrôle bloque le cas observé.
Chaque contrôle renvoie None si tout va bien, sinon le motif de blocage."""

TOLERANCE_TAILLE = 0.05


def donnees_fraiches(donnees_entree):
    if not donnees_entree.get("qualite_ok", False):
        return "contrôle qualité des données échoué"
    if donnees_entree.get("age_secondes", 0) > 2 * donnees_entree.get("duree_barre_secondes", 86400):
        return "dernière barre trop ancienne (> 2 barres)"
    if any(v is None for v in donnees_entree.get("valeurs", {}).values()):
        return "valeur d'entrée manquante"
    return None


def taille_conforme(taille_demandee, taille_prevue):
    if taille_prevue and abs(taille_demandee / taille_prevue - 1) > TOLERANCE_TAILLE:
        return f"taille {taille_demandee} ≠ taille prévue {taille_prevue} (> {TOLERANCE_TAILLE:.0%})"
    return None


def regles_respectees(regles):
    ops = {"<": lambda a, b: a < b, ">": lambda a, b: a > b, "<=": lambda a, b: a <= b, ">=": lambda a, b: a >= b,
           "==": lambda a, b: a == b}
    ko = [r["nom"] for r in regles if r.get("valeur") is None or not ops[r["op"]](r["valeur"], r["seuil"])]
    return f"règles non satisfaites : {ko}" if ko else None


def pas_de_doublon(ordre_id, ordres_deja_envoyes):
    return f"ordre {ordre_id} déjà envoyé" if ordre_id in ordres_deja_envoyes else None


def ordre_confirme(ordres):
    """Ne jamais considérer une position comme ouverte sans un ordre au statut « rempli »."""
    return None if any(o.get("statut") == "rempli" for o in ordres) else "aucun ordre rempli : position non ouverte"


def glissement_acceptable(spread_estime, maximum):
    """Refuser un ordre au marché si le spread estimé juste avant l'envoi dépasse le maximum fixé."""
    return f"spread estimé {spread_estime:.4f} > {maximum:.4f}" if spread_estime > maximum else None


REGLES = {"PREV-ORDRE": ordre_confirme, "PREV-GLISSEMENT": glissement_acceptable,"PREV-DONNEES": donnees_fraiches, "PREV-TAILLE": taille_conforme,
          "PREV-REGLES": regles_respectees, "PREV-DOUBLON": pas_de_doublon}
