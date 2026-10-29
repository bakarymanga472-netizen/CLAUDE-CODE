"""Audit 00 — relance à l'identique des 4 modules de recherche, SANS toucher resultats/.

Chaque module écrit dans ICI/resultats ; on redirige ICI vers audit/sorties/repro/ (monkeypatch), puis on appelle main().
Les prix viennent du cache data/ (aucun rafraîchissement).

Usage : cd projets/bot-trading && python3 audit/a00_reproduire.py [recherche reussite enquete sorties]
"""
import contextlib
import io
import sys
import time

import commun  # noqa: F401  (ajoute la racine au sys.path)
from aladdin import enquete, recherche, reussite, sorties

DEST = commun.SORTIES / "repro"
(DEST / "resultats").mkdir(parents=True, exist_ok=True)
MODULES = {"recherche": recherche, "reussite": reussite, "enquete": enquete, "sorties": sorties}

if __name__ == "__main__":
    choix = [a for a in sys.argv[1:] if a in MODULES] or list(MODULES)
    for nom in choix:
        m = MODULES[nom]
        m.ICI = DEST
        t0 = time.time()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            m.main()
        print(f"[{nom}] relancé en {time.time() - t0:.0f} s → {DEST / 'resultats'}")
