"""Aladdin en direct (papier) : à lancer une fois par jour après minuit UTC.

- Télécharge les vrais cours de clôture.
- Met à jour la valeur du portefeuille fictif avec les positions d'hier (test « forward », impossible à truquer).
- Calcule les positions de demain et les inscrit au journal.

Usage : python3 -m aladdin.live
Journal : resultats/aladdin_journal.csv
"""
from pathlib import Path

import pandas as pd

from . import desks, donnees
from .donnees import FRAIS, type_actif
from .recherche import UNIVERS

ICI = Path(__file__).resolve().parent.parent
JOURNAL = ICI / "resultats" / "aladdin_journal.csv"


def poids_du_jour(px, structure):
    nom_sig, univers, gestion = [x.strip() for x in structure.split("|")]
    lb = int(nom_sig.split()[1])
    cols = UNIVERS[univers]
    p = px[cols]
    sig = desks.desk_momentum(p, lb)
    w = desks.desk_risque(p, sig) if gestion == "vol cible" else desks.poids_egaux(sig)
    return w.iloc[-1]


def main():
    structure = (ICI / "resultats" / "aladdin_structure.txt").read_text().strip()
    px = donnees.prix(rafraichir=True)
    t = px.index[-1]
    w = poids_du_jour(px, structure)

    if JOURNAL.exists():
        j = pd.read_csv(JOURNAL, parse_dates=["date"])
        dernier = j.iloc[-1]
        if pd.Timestamp(dernier["date"]) >= t:
            print(f"Déjà à jour pour le {t.date()}.")
            return
        anciens = {c[2:]: dernier[c] for c in j.columns if c.startswith("w_")}
        jour_prec = pd.Timestamp(dernier["date"])
        rend = sum(anc * (px.loc[t, a] / px.loc[jour_prec, a] - 1) for a, anc in anciens.items() if anc)
        rotation = sum(abs(w.get(a, 0) - anc) * FRAIS[type_actif(a)] for a, anc in anciens.items())
        valeur = dernier["valeur"] * (1 + rend - rotation)
    else:
        j, valeur, rend = pd.DataFrame(), 10_000.0, 0.0
        rotation = sum(abs(x) * FRAIS[type_actif(a)] for a, x in w.items())
        valeur *= 1 - rotation

    ligne = {"date": t, "valeur": round(valeur, 2), "rendement_jour": round(rend, 5)}
    ligne.update({f"w_{a}": round(x, 4) for a, x in w.items()})
    j = pd.concat([j, pd.DataFrame([ligne])], ignore_index=True)
    JOURNAL.parent.mkdir(exist_ok=True)
    j.to_csv(JOURNAL, index=False)

    print(f"Aladdin — clôture du {t.date()} — structure : {structure}")
    print(f"Portefeuille fictif : {valeur:,.2f} USD (départ 10 000, {len(j)} jour(s) de suivi réel)")
    print("Positions pour demain :")
    for a, x in w.sort_values(ascending=False).items():
        print(f"  {a:12s} {x * 100:5.1f} %  (~{px.loc[t, a]:,.4g})")
    print(f"  {'CASH':12s} {(1 - w.sum()) * 100:5.1f} %")


if __name__ == "__main__":
    main()
