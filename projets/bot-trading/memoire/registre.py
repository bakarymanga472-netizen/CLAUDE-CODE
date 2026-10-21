"""Registre en ajout seul, chaîné par empreintes (SHA-256).

Chaque ligne JSON contient l'empreinte de la ligne précédente : modifier ou supprimer une ligne du passé casse la chaîne,
et `verifier()` le détecte. Il n'existe AUCUNE fonction de modification ou de suppression : on corrige en ajoutant.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ORIGINE = "0" * 64


def _empreinte(entree):
    corps = {k: v for k, v in entree.items() if k != "empreinte"}
    return hashlib.sha256(json.dumps(corps, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


class Registre:
    def __init__(self, chemin):
        self.chemin = Path(chemin)
        self.chemin.parent.mkdir(parents=True, exist_ok=True)

    def lire(self):
        if not self.chemin.exists():
            return []
        return [json.loads(l) for l in self.chemin.read_text(encoding="utf-8").splitlines() if l.strip()]

    def ajouter(self, entree, prefixe="E"):
        lignes = self.lire()
        e = dict(entree)
        e.setdefault("id", f"{prefixe}-{len(lignes) + 1:05d}")
        if any(x["id"] == e["id"] for x in lignes):
            raise ValueError(f"identifiant déjà présent : {e['id']} (le registre n'accepte pas d'écrasement)")
        e["enregistre_le"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        e["empreinte_precedente"] = lignes[-1]["empreinte"] if lignes else ORIGINE
        e["empreinte"] = _empreinte(e)
        with open(self.chemin, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, default=str) + "\n")
        return e

    def verifier(self):
        """Renvoie la liste des anomalies d'intégrité (vide si la chaîne est intacte)."""
        erreurs, prec = [], ORIGINE
        for i, e in enumerate(self.lire()):
            if e.get("empreinte_precedente") != prec:
                erreurs.append(f"ligne {i + 1} ({e.get('id')}) : chaînage rompu (ligne supprimée ou insérée)")
            if _empreinte(e) != e.get("empreinte"):
                erreurs.append(f"ligne {i + 1} ({e.get('id')}) : contenu modifié après enregistrement")
            prec = e.get("empreinte")
        return erreurs
