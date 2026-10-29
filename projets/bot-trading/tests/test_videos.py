import unittest

import pandas as pd

from labo.videos import deleuze, kasper, nico, rayfu, roro
from tests.outils import marche_synthetique


class SansFutur(unittest.TestCase):
    def test_signaux_identiques_si_on_coupe_le_futur(self):
        df = marche_synthetique(3000, freq="5min")
        for mod in (roro, deleuze, kasper, nico):
            for p in mod.GRILLE:
                a = mod.signaux(df, **p)
                b = mod.signaux(df.iloc[:2000], **p)
                a = a[a.index < df.index[2000]]
                pd.testing.assert_frame_equal(a, b, check_dtype=False, obj=f"{mod.__name__} {p}")

    def test_rayfu(self):
        df = marche_synthetique(500)
        pd.testing.assert_series_equal(rayfu.cible(df).iloc[:300], rayfu.cible(df.iloc[:300]))


if __name__ == "__main__":
    unittest.main()
