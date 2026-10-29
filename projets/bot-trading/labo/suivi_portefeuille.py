"""Suivi papier QUOTIDIEN du portefeuille de tendance, à côté de sa référence « toujours investi, même risque ».

Seul moyen d'obtenir des données vraiment vierges : la règle est figée (labo/portefeuille.py, REGLE) et on note chaque
jour les poids décidés AVANT de connaître la suite. Départ : 2026-10-21. Aucun ordre n'est envoyé.
Usage : python3 -m labo.suivi_portefeuille   (une fois par jour, après 00:05 UTC)
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import donnees
from .pilote import charger
from .portefeuille import REGLE, UNIVERS, _poids_constant, poids

ICI = Path(__file__).resolve().parent.parent
JOURNAL = ICI / "resultats" / "suivi_portefeuille.jsonl"
DEPART = "2026-10-21"


def main():
    closes = {}
    for s in UNIVERS:
        df = donnees.charger(s, "1d", rafraichir=True)[0] if s.endswith("USDT") else donnees.charger_yahoo(s, rafraichir=True)[0]
        closes[s] = df.close
    c = pd.DataFrame(closes).sort_index()
    cal = pd.date_range(c.index.min(), c.index.max(), freq="D")
    c = c.reindex(cal).ffill()
    for s in UNIVERS:
        c.loc[:closes[s].index[0] - pd.Timedelta(days=1), s] = float("nan")
    w, ref = poids(c, True).iloc[-1], _poids_constant(c).iloc[-1]
    entree = {"horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"), "regle": REGLE["version"],
              "derniere_cloture": str(c.index[-1].date()), "prix": {s: float(c[s].iloc[-1]) for s in UNIVERS},
              "poids_tendance": {s: round(float(w[s]), 4) for s in UNIVERS},
              "poids_reference": {s: round(float(ref[s]), 4) for s in UNIVERS}}
    JOURNAL.parent.mkdir(exist_ok=True)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entree, ensure_ascii=False) + "\n")
    print(f"Clôture {entree['derniere_cloture']} — poids décidés (exécution à l'ouverture suivante) :")
    for s in UNIVERS:
        print(f"  {s:8s} tendance {w[s]:6.1%} | référence {ref[s]:6.1%}")
    print(f"  liquidités : tendance {1 - w.sum():.1%} | référence {1 - ref.sum():.1%}")


if __name__ == "__main__":
    main()
