import unittest

import pandas as pd

from aladdin import alpaca
from tests.outils import marche_synthetique

OK = "candidate démo (paper uniquement)"


def horloge(ouvert=True, minutes=60):
    t = pd.Timestamp("2026-10-21 14:00", tz="America/New_York")
    return {"is_open": ouvert, "timestamp": str(t), "next_close": str(t + pd.Timedelta(minutes=minutes))}


def donnees_avec_signal(signal_hier=True):
    """Série FICTIVE en hausse puis chute de 10 % la veille → RSI-2 très bas au-dessus de la MM200."""
    df = marche_synthetique(400, derive=0.003, freq="B")
    if signal_hier:
        df.iloc[-1:, :4] = df.iloc[-1:, :4].values * 0.9
    return df


class Decider(unittest.TestCase):
    def setUp(self):
        self.df = donnees_avec_signal()
        self.veille = self.df.index[-1].date()

    def appel(self, **k):
        a = dict(horloge=horloge(), seance_precedente=self.veille, aujourdhui="2026-10-21", donnees_par_actif={"SPY": self.df},
                 positions={}, ordres_ouverts=[], capital=10000, statut=OK)
        a.update(k)
        return alpaca.decider(**a)

    def test_achat_au_signal(self):
        o, _ = self.appel()
        self.assertEqual([x["side"] for x in o], ["buy"])
        self.assertEqual(o[0]["time_in_force"], "cls")

    def test_idempotent_si_ordre_ouvert(self):
        o, m = self.appel(ordres_ouverts=[{"symbol": "SPY"}])
        self.assertEqual(o, [])

    def test_identifiant_client_deterministe(self):
        self.assertEqual(self.appel()[0][0]["client_order_id"], self.appel()[0][0]["client_order_id"])

    def test_marche_ferme_et_trop_tard(self):
        self.assertEqual(self.appel(horloge=horloge(False))[0], [])
        self.assertEqual(self.appel(horloge=horloge(True, 5))[0], [])

    def test_donnees_perimees(self):
        self.assertEqual(self.appel(seance_precedente="2030-01-01")[0], [])

    def test_strategie_non_validee(self):
        o, m = self.appel(statut="non validée")
        self.assertEqual(o, [])
        self.assertIn("aucun ordre", m[0])

    def test_vente_quand_regle_a_plat(self):
        df = marche_synthetique(400, derive=0.003, freq="B")
        o, _ = alpaca.decider(horloge(), df.index[-1].date(), "2026-10-21", {"SPY": df}, {"SPY": {"qty": "3"}}, [], 10000, OK)
        self.assertEqual([(x["side"], x["qty"]) for x in o], [("sell", "3")])

    def test_reel_refuse(self):
        import os
        from amelioration.garde_fous import AutorisationRequise
        os.environ["ALPACA_LIVE"] = "1"
        try:
            with self.assertRaises(AutorisationRequise):
                alpaca._api("/v2/clock")
        finally:
            del os.environ["ALPACA_LIVE"]


if __name__ == "__main__":
    unittest.main()
