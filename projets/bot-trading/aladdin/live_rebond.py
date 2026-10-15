"""Aladdin Rebond — suivi papier EN DIRECT de la structure à haut taux de réussite.

Structure figée le 2026-10-15 (avant tout résultat en direct), issue de l'enquête et de aladdin/sorties.py :
  actions (SPY) + or (COMEX), parts égales
  entrée : RSI-2 < 5 alors que le cours est au-dessus de sa MM200 → achat à la clôture suivante
  sortie : objectif +1 % OU stop -10 % OU 20 jours max → vente à la clôture suivante
  Historique : 84 % de réussite 2008-2019, 78 % en validation 2020-2024, 79 % en 2025-2026.

Le suivi rejoue la règle sur les vrais cours, mais ne compte que les trades ouverts APRÈS le départ :
toutes ces décisions ont été prises avec des cours qui n'existaient pas le jour où la règle a été figée.

Usage : python3 -m aladdin.live_rebond   (une fois par jour)
"""
from pathlib import Path

import pandas as pd

from . import donnees
from .reussite import portefeuille

ICI = Path(__file__).resolve().parent.parent
DEPART = pd.Timestamp("2026-10-15")
REGLE = {"entree": "rsi2", "seuil": 5, "mm5": False, "tp": 0.01, "sl": 0.10, "duree": 20}
ACTIFS = ["ACTIONS", "OR"]


def main():
    px = donnees.prix(rafraichir=True)
    port, trades = portefeuille(px, ACTIFS, REGLE)
    t = px.index[-1]
    live = trades[trades.date >= DEPART]
    r = port.loc[DEPART:]
    valeur = 10_000 * (1 + r).prod()
    print(f"Aladdin Rebond — suivi en direct depuis le {DEPART.date()} — dernière clôture {t.date()}")
    print(f"Portefeuille fictif : {valeur:,.0f} USD (départ 10 000)")
    if len(live):
        print(f"Trades : {len(live)} — gagnants {(live.rendement > 0).mean() * 100:.0f} %")
        for x in live.itertuples():
            print(f"  {x.date.date()} {x.actif:8s} {x.rendement * 100:+.2f} %")
    else:
        print(f"Aucun trade encore : la règle attend un repli (RSI-2 < {REGLE['seuil']}) dans une tendance haussière.")
    # Où en est chaque actif aujourd'hui
    from .desks import rsi
    for a in ACTIFS:
        c = px[a].dropna()
        v = rsi(c.to_frame(), 2).iloc[-1, 0]
        tendance = c.iloc[-1] > c.rolling(200).mean().iloc[-1]
        etat = "SIGNAL D'ACHAT" if (v < REGLE["seuil"] and tendance) else "attente"
        print(f"  {a:8s} cours {c.iloc[-1]:,.2f} | RSI-2 {v:5.1f} | tendance {'haussière' if tendance else 'baissière'} → {etat}")
    (ICI / "resultats").mkdir(exist_ok=True)
    live.to_csv(ICI / "resultats" / "aladdin_rebond_journal.csv", index=False)


if __name__ == "__main__":
    main()
