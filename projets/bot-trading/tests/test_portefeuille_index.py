import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from labo import portefeuille
from memoire import index_sqlite
from memoire.base import Memoire
from tests.test_memoire import trade


class Portefeuille(unittest.TestCase):
    def closes(self, n=900):
        rng = np.random.default_rng(3)
        idx = pd.date_range("2018-01-01", periods=n, freq="D")
        df = pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0.0005, 0.03, (n, 3)), axis=0)), index=idx, columns=list("ABC"))
        df.iloc[:300, 2] = np.nan                       # C n'existe pas encore
        return df

    def test_pas_de_futur(self):
        c = self.closes()
        a, b = portefeuille.poids(c, True), portefeuille.poids(c.iloc[:700], True)
        pd.testing.assert_frame_equal(a.iloc[:700], b)

    def test_sans_levier_et_entree_differee(self):
        w = portefeuille.poids(self.closes(), True)
        self.assertLessEqual(w.abs().sum(axis=1).max(), 1.0 + 1e-9)
        self.assertTrue((w["C"].iloc[:300 + portefeuille.HISTORIQUE_MIN - 1] == 0).all())
        self.assertTrue((w >= 0).all().all())


class IndexSQLite(unittest.TestCase):
    def test_refuse_si_chaine_rompue(self):
        d = Path(tempfile.mkdtemp())
        m = Memoire(d)
        m.enregistrer_trade(trade(1))
        m.enregistrer_trade(trade(2))
        self.assertTrue(index_sqlite.construire(d).exists())
        f = d / "trades.jsonl"
        lignes = f.read_text().splitlines()
        f.write_text(lignes[1] + "\n")
        with self.assertRaises(RuntimeError):
            index_sqlite.construire(d)


if __name__ == "__main__":
    unittest.main()
