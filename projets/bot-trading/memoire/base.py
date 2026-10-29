"""Mémoire persistante des trades et des connaissances.

Registres (fichiers JSONL chaînés, ajout seul) :
  trades, corrections, diagnostics, erreurs_processus, hypotheses, conditions_marche, modifications.
Les corrections ne touchent jamais le trade d'origine : `trades_effectifs()` applique les corrections en surcouche
et garde la trace de chacune.
"""
from pathlib import Path

from .registre import Registre

REGISTRES = ["trades", "corrections", "diagnostics", "erreurs_processus", "hypotheses", "conditions_marche", "modifications"]

CHAMPS_TRADE = {
    "id": "identifiant unique",
    "instrument": "ex. BTCUSDT", "marche": "ex. binance-spot",
    "strategie": "nom du module", "version": "version de la stratégie",
    "horodatage_entree": "ISO 8601 UTC", "horodatage_sortie": "ISO 8601 UTC",
    "donnees_entree": "{derniere_barre, age_secondes, duree_barre_secondes, qualite_ok, valeurs{...}}",
    "signaux": "{nom: valeur} connus à la décision",
    "plan": "{sens, prix_prevu, stop, objectif, taille_prevue, risque_unitaire, regles[], filtres[], cout_prevu}",
    "execution": "{ordres[{id, statut, prix, quantite, horodatage}], prix_entree, prix_sortie, taille, motif_sortie}",
    "resultat": "{brut, net, frais, glissement, R}",
    "regime": "régime de marché à la décision",
    "decision_agent": "texte : ce que l'agent a décidé et pourquoi",
    "etat_systeme": "{version_code, anomalies[]}",
}


class Memoire:
    def __init__(self, dossier):
        self.dossier = Path(dossier)
        self.r = {n: Registre(self.dossier / f"{n}.jsonl") for n in REGISTRES}

    # --- trades ---
    def enregistrer_trade(self, trade):
        manquants = [c for c in CHAMPS_TRADE if c not in trade]
        if manquants:
            raise ValueError(f"trade incomplet, champs manquants : {manquants}")
        if any(t["id"] == trade["id"] for t in self.r["trades"].lire()):
            raise ValueError(f"trade {trade['id']} déjà enregistré : passer par corriger()")
        return self.r["trades"].ajouter(trade)

    def corriger(self, trade_id, champ, valeur, justification, auteur):
        if not justification:
            raise ValueError("une correction exige une justification")
        if not any(t["id"] == trade_id for t in self.r["trades"].lire()):
            raise KeyError(trade_id)
        return self.r["corrections"].ajouter({"trade_id": trade_id, "champ": champ, "nouvelle_valeur": valeur,
                                              "justification": justification, "auteur": auteur}, "COR")

    def trades_effectifs(self):
        """Trades avec corrections appliquées en surcouche (le registre d'origine reste intact)."""
        corr = self.r["corrections"].lire()
        out = []
        for t in self.r["trades"].lire():
            t = dict(t)
            t["corrections"] = []
            for c in corr:
                if c["trade_id"] == t["id"]:
                    cible, cles = t, c["champ"].split(".")
                    for k in cles[:-1]:
                        cible[k] = dict(cible[k])
                        cible = cible[k]
                    cible[cles[-1]] = c["nouvelle_valeur"]
                    t["corrections"].append(c["id"])
            out.append(t)
        return out

    # --- connaissances ---
    def ajouter(self, registre, entree, prefixe):
        obligatoires = {"hypotheses": ["date", "echantillon", "confiance", "version_modele", "protocole"],
                        "erreurs_processus": ["date", "echantillon", "confiance", "version_modele", "regle_prevention"],
                        "conditions_marche": ["date", "echantillon", "confiance", "version_modele"],
                        "modifications": ["date", "echantillon", "confiance", "version_modele", "resultat"]}
        manquants = [c for c in obligatoires.get(registre, []) if c not in entree]
        if manquants:
            raise ValueError(f"{registre} : champs manquants {manquants}")
        return self.r[registre].ajouter(entree, prefixe)

    def verifier(self):
        return {n: reg.verifier() for n, reg in self.r.items()}
