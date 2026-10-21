import unittest

import numpy as np
import pandas as pd

from labo import bracket


def barres(lignes):
    idx = pd.date_range("2024-01-01", periods=len(lignes), freq="5min")
    return pd.DataFrame(lignes, columns=["open", "high", "low", "close"], index=idx)


class Bracket(unittest.TestCase):
    def test_objectif_atteint(self):
        df = barres([(100, 100, 100, 100), (100, 101, 99.5, 100.5), (100.5, 102.5, 100.4, 102), (102, 102, 102, 102)])
        s = pd.DataFrame({"sens": [1], "stop": [99.0], "tp_R": [2.0]}, index=[df.index[0]])
        t = bracket.executer(df, s, 0.0)
        self.assertEqual(t.motif.iloc[0], "objectif")
        self.assertAlmostEqual(t.R.iloc[0], 2.0)

    def test_stop_prioritaire_si_les_deux_dans_la_meme_barre(self):
        df = barres([(100, 100, 100, 100), (100, 103, 98, 100), (100, 100, 100, 100)])
        s = pd.DataFrame({"sens": [1], "stop": [99.0], "tp_R": [2.0]}, index=[df.index[0]])
        t = bracket.executer(df, s, 0.0)
        self.assertEqual(t.motif.iloc[0], "stop")
        self.assertAlmostEqual(t.R.iloc[0], -1.0)

    def test_trou_sous_le_stop(self):
        df = barres([(100, 100, 100, 100), (100, 100.5, 99.5, 100), (97, 97.5, 96, 97), (97, 97, 97, 97)])
        s = pd.DataFrame({"sens": [1], "stop": [99.0], "tp_R": [2.0]}, index=[df.index[0]])
        t = bracket.executer(df, s, 0.0)
        self.assertAlmostEqual(t.R.iloc[0], -3.0)

    def test_couts_et_short(self):
        df = barres([(100, 100, 100, 100), (100, 100.2, 99.9, 100), (100, 100, 97.9, 98), (98, 98, 98, 98)])
        s = pd.DataFrame({"sens": [-1], "stop": [101.0], "tp_R": [2.0]}, index=[df.index[0]])
        t = bracket.executer(df, s, 0.1)
        self.assertAlmostEqual(t.R.iloc[0], 2.0 - 0.1)

    def test_pas_de_chevauchement_et_signal_futur_sans_effet(self):
        df = barres([(100, 100, 100, 100)] + [(100, 100.5, 99.5, 100)] * 10 + [(100, 103, 100, 103)] * 3)
        s = pd.DataFrame({"sens": [1, 1], "stop": [99.0, 99.0], "tp_R": [2.0, 2.0]}, index=[df.index[0], df.index[3]])
        t = bracket.executer(df, s, 0.0)
        self.assertEqual(len(t), 1)                       # le 2e signal arrive pendant la position

    def test_break_even(self):
        df = barres([(100, 100, 100, 100), (100, 101.2, 99.8, 101), (101, 101, 99.9, 100), (100, 100, 100, 100)])
        s = pd.DataFrame({"sens": [1], "stop": [99.0], "tp_R": [2.0]}, index=[df.index[0]])
        t = bracket.executer(df, s, 0.0, be_R=1.0)
        self.assertEqual(t.motif.iloc[0], "break-even")
        self.assertAlmostEqual(t.R.iloc[0], 0.0)


if __name__ == "__main__":
    unittest.main()
