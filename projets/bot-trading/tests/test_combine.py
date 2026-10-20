import unittest

import numpy as np
import pandas as pd

from labo import combine


def univers_fictif(n=600, a=4, graine=0):
    rng = np.random.default_rng(graine)
    idx = pd.bdate_range("2010-01-01", periods=n)
    return pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0004, 0.012, (n, a)), axis=0)), index=idx,
                        columns=[f"E{i}" for i in range(a)])


class Combine(unittest.TestCase):
    def test_pas_de_futur(self):
        c = univers_fictif()
        r1, t1 = combine.backtest(c, combine.indicateurs(c), sortie="B", seuil=10)
        c2 = c.copy()
        c2.iloc[450:] *= 1.5
        r2, t2 = combine.backtest(c2, combine.indicateurs(c2), sortie="B", seuil=10)
        pd.testing.assert_series_equal(r1.iloc[:450], r2.iloc[:450])

    def test_au_plus_K_positions_et_stop(self):
        c = univers_fictif(a=8)
        _, t, e = combine.backtest(c, combine.indicateurs(c), sortie="A", seuil=10, etat=True)
        self.assertLessEqual(len(e["ouvertes"]), combine.K)
        self.assertTrue((t.rendement > -0.5).all())
        for _, x in t.iterrows():                      # chevauchement : jamais plus de K positions à la fois
            n = ((t.entree <= x.entree) & (t.sortie > x.entree)).sum()
            self.assertLessEqual(n, combine.K)


if __name__ == "__main__":
    unittest.main()
