"""Index SQLite en LECTURE pour interroger la mémoire. La source de vérité reste les fichiers JSONL chaînés :
la base est reconstruite entièrement à chaque appel (jamais modifiée à la main), et refusée si la chaîne est rompue.

Usage : python3 -m memoire.index_sqlite <dossier_memoire> [<fichier.db>]
Exemple : sqlite3 memoire/exemple_fictif/index.db "select regime, count(*), avg(R) from trades group by regime"
"""
import json
import sqlite3
import sys
from pathlib import Path

from .base import Memoire


def construire(dossier, chemin_db=None):
    m = Memoire(dossier)
    integrite = {k: v for k, v in m.verifier().items() if v}
    if integrite:
        raise RuntimeError(f"chaîne rompue, index refusé : {integrite}")
    db = Path(chemin_db or Path(dossier) / "index.db")
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.execute("""create table trades (id text primary key, instrument text, strategie text, version text, entree text,
                   sortie text, regime text, brut real, net real, frais real, glissement real, R real, corrections text, json text)""")
    for t in m.trades_effectifs():
        r = t["resultat"]
        con.execute("insert into trades values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (t["id"], t["instrument"], t["strategie"], t["version"], t["horodatage_entree"], t["horodatage_sortie"],
                     t["regime"], r.get("brut"), r.get("net"), r.get("frais"), r.get("glissement"), r.get("R"),
                     ",".join(t["corrections"]), json.dumps(t, ensure_ascii=False, default=str)))
    for nom, reg in m.r.items():
        if nom == "trades":
            continue
        con.execute(f"create table {nom} (id text primary key, enregistre_le text, json text)")
        for e in reg.lire():
            con.execute(f"insert into {nom} values (?,?,?)", (e["id"], e["enregistre_le"], json.dumps(e, ensure_ascii=False, default=str)))
    con.commit()
    con.execute("pragma query_only = on")
    con.close()
    db.chmod(0o444)                      # lecture seule : la base n'est pas un endroit où écrire
    return db


if __name__ == "__main__":
    print(construire(*sys.argv[1:]))
