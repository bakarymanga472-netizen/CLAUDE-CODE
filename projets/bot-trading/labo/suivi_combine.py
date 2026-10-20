"""Suivi papier QUOTIDIEN de la stratégie combinée (B10, A5 et la combinaison D1, levier 1). Aucun ordre envoyé.

Après chaque clôture de New York : rafraîchit les 16 ETF, rejoue la règle figée et note les positions ouvertes et les
ordres « au cours de clôture » à passer à la séance suivante. Départ du suivi : 2026-10-21.
Usage : python3 -m labo.suivi_combine
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from . import donnees
from .combine import UNIVERS, VARIANTES, backtest, indicateurs
from .combine80 import VARIANTES80

ICI = Path(__file__).resolve().parent.parent
JOURNAL = ICI / "resultats" / "suivi_combine.jsonl"


def main():
    for s in UNIVERS:
        donnees.charger_yahoo(s, rafraichir=True)
    from .combine import charger
    c = charger()
    ind = indicateurs(c)
    entree = {"horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"), "derniere_cloture": str(c.index[-1].date())}
    regles = {"B10": VARIANTES["B10"], "A5": VARIANTES["A5"], "D1": VARIANTES80["D1"]}
    for nom, v in regles.items():
        _, _, e = backtest(c, ind, etat=True, **v)
        entree[nom] = e
        print(f"{nom} — clôture {c.index[-1].date()} : ouvertes {list(e['ouvertes'])} ; "
              f"à acheter à la prochaine clôture {e['a_acheter']} ; à vendre {e['a_vendre']}")
    JOURNAL.parent.mkdir(exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
