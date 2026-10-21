"""Limites d'autonomie. Le code de ce dépôt ne contient AUCUN chemin d'exécution en argent réel depuis la boucle
d'amélioration. Ces fonctions lèvent une erreur si quelqu'un tente de l'ajouter sans passer par l'humain."""
LEVIER_MAX = 1.0
VOL_CIBLE_MAX = 0.40

INTERDIT_SANS_HUMAIN = {"deployer_reel", "augmenter_levier", "modifier_limites_risque", "debloquer_compte_reel",
                        "promouvoir_stable"}


class AutorisationRequise(PermissionError):
    pass


def exiger_humain(action, autorisation=None):
    """`autorisation` = texte saisi par l'humain en ligne de commande (jamais généré par l'agent)."""
    if action in INTERDIT_SANS_HUMAIN and not autorisation:
        raise AutorisationRequise(f"« {action} » exige une autorisation humaine explicite")
    if action == "deployer_reel":
        raise AutorisationRequise("le déploiement en argent réel n'est pas implémenté dans la boucle d'amélioration")


def verifier_spec(spec):
    if spec.get("levier", 1.0) > LEVIER_MAX:
        raise AutorisationRequise("levier > 1 interdit sans autorisation humaine")
    if spec.get("vol_cible", VOL_CIBLE_MAX) > VOL_CIBLE_MAX:
        raise AutorisationRequise("vol cible au-dessus de la limite de risque")
