"""Aladdin Rebond — suivi papier EN DIRECT (version corrigée après audit, 2026-10-21).

Utilise EXACTEMENT le code du backtest corrigé (`labo/strategies/rebond_tp_sl.py`, `labo/rebond.py`) :
séances réelles, SPY + GLD (l'instrument réellement traité), décision à la clôture t, exécution à la clôture t+1.
L'ancienne version (calendrier 7j/7, or GC=F) mesurait une autre règle (audit, anomalie 4) ; son journal est conservé
dans resultats/aladdin_rebond_journal.csv et n'est plus mis à jour.

Seuls les trades décidés APRÈS le départ comptent (données qui n'existaient pas quand la règle a été figée).
Usage : python3 -m aladdin.live_rebond   (une fois par jour de bourse, après la clôture)
"""
from pathlib import Path

import pandas as pd

from labo import donnees
from labo.rebond import ACTIFS, COUTS, P, executer
from labo.strategies import rebond_tp_sl as R
from labo.strategies.outils import rsi

ICI = Path(__file__).resolve().parent.parent
DEPART = pd.Timestamp("2026-10-15")
JOURNAL = ICI / "resultats" / "aladdin_rebond_journal_v2.csv"


def main():
    lignes = []
    for a in ACTIFS:
        df, h = donnees.charger_yahoo(a, rafraichir=True)
        c = R.cible(df, 1, **P)
        res = executer(df, c)
        t = res["trades"]
        t = t[t.entree > DEPART].copy() if len(t) else t
        for x in t.itertuples():
            ouvert = x.sortie == df.index[-1] and c.iloc[-1] != 0
            lignes.append({"actif": a, "entree": x.entree.date(), "sortie": None if ouvert else x.sortie.date(),
                           "net": x.net, "statut": "ouvert (latent)" if ouvert else "clôturé", "donnees": h})
        v = rsi(df.close, 2).iloc[-1]
        tendance = df.close.iloc[-1] > df.close.rolling(200).mean().iloc[-1]
        etat = "en position / ordre prévu" if c.iloc[-1] else ("SIGNAL → achat à la prochaine clôture" if v < P["seuil"] and tendance else "attente")
        print(f"{a}: clôture {df.index[-1].date()} {df.close.iloc[-1]:.2f} | RSI-2 {v:.1f} | tendance {'haussière' if tendance else 'baissière'} → {etat}")
    j = pd.DataFrame(lignes, columns=["actif", "entree", "sortie", "net", "statut", "donnees"])
    clos = j[j.statut == "clôturé"]
    print(f"Depuis le {DEPART.date()} : {len(clos)} trade(s) clôturé(s)"
          + (f", {(clos.net > 0).mean():.0%} gagnants, somme {clos.net.sum():+.2%}" if len(clos) else "") + f" ; {len(j) - len(clos)} ouvert(s).")
    JOURNAL.parent.mkdir(exist_ok=True)
    j.to_csv(JOURNAL, index=False)


if __name__ == "__main__":
    main()
