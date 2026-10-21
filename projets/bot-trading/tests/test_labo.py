import unittest

import numpy as np
import pandas as pd

from labo import donnees, regimes, validation as V
from labo.couts import Couts
from labo.moteur import simuler
from labo.strategies import CANDIDATES, REFERENCES
from tests.outils import marche_synthetique


class PasDeLookAhead(unittest.TestCase):
    def test_signal_inchange_si_on_coupe_le_futur(self):
        df = marche_synthetique(1200)
        for s in CANDIDATES + REFERENCES:
            for p in s.GRILLE:
                complet = s.cible(df, 1, **p)
                for t in (400, 800):
                    coupe = s.cible(df.iloc[:t], 1, **p)
                    pd.testing.assert_series_equal(complet.iloc[:t], coupe, check_names=False,
                                                   obj=f"{s.NOM} {p} coupé à {t}")

    def test_regimes_sans_futur(self):
        df = marche_synthetique(1200)
        a = regimes.etiqueter(df, "1d")
        b = regimes.etiqueter(df.iloc[:700], "1d")
        pd.testing.assert_series_equal(a.iloc[:700], b)

    def test_futur_modifie_ne_change_pas_le_passe_du_moteur(self):
        df = marche_synthetique(800)
        s = CANDIDATES[0]
        r1 = simuler(df, s.cible(df, 1, **s.GRILLE[0]), "1d")["net"]
        df2 = df.copy()
        df2.iloc[600:, :4] *= 3.0
        r2 = simuler(df2, s.cible(df2, 1, **s.GRILLE[0]), "1d")["net"]
        # la barre 598 porte le rendement d'ouverture 598 → ouverture 599 : inchangée
        pd.testing.assert_series_equal(r1.iloc[:599], r2.iloc[:599])


class Moteur(unittest.TestCase):
    def test_exposition_pleine_sans_cout_egale_ouverture_a_ouverture(self):
        df = marche_synthetique(300)
        zero = Couts(commission=0, demi_spread_base=0, glissement_sigma=0)
        res = simuler(df, pd.Series(1.0, index=df.index), "1d", zero, dimensionner=False)
        attendu = (df.open.shift(-1) / df.open - 1).fillna(0)
        attendu.iloc[0] = 0.0                      # décidé à la clôture 0, exécuté à l'ouverture 1
        np.testing.assert_allclose(res["net"].values, attendu.values, atol=1e-12)

    def test_couts_croissants_et_retard(self):
        df = marche_synthetique(600)
        c = CANDIDATES[0].cible(df, 1, **CANDIDATES[0].GRILLE[0])
        base = simuler(df, c, "1d")["net"].sum()
        x3 = simuler(df, c, "1d", Couts().stresse(3.0))["net"].sum()
        self.assertLess(x3, base)
        w1 = simuler(df, c, "1d")["w"]
        w2 = simuler(df, c, "1d", Couts().stresse(1.0, retard=2))["w"]
        pd.testing.assert_series_equal(w1.shift(1).fillna(0.0), w2, check_names=False)

    def test_trades_comptes(self):
        df = marche_synthetique(100)
        c = pd.Series(0.0, index=df.index)
        c.iloc[10:20] = 1.0
        c.iloc[50:55] = 1.0
        t = simuler(df, c, "1d", dimensionner=False)["trades"]
        self.assertEqual(len(t), 2)
        self.assertEqual(t.entree.iloc[0], df.index[11])


class Statistiques(unittest.TestCase):
    def test_dsr_decroit_avec_le_nombre_essais(self):
        r = np.random.default_rng(0).normal(0.001, 0.02, 1500)
        d1, _ = V.dsr(r, 1, 0.001)
        d100, _ = V.dsr(r, 100, 0.001)
        self.assertGreater(d1, d100)
        self.assertTrue(0 <= d100 <= 1)

    def test_pbo_bornes_et_variante_dominante(self):
        rng = np.random.default_rng(0)
        m = pd.DataFrame(rng.normal(0, 0.01, (1000, 8)))
        p = V.pbo(m)
        self.assertTrue(0 <= p <= 1)
        m[0] += 0.005
        self.assertLess(V.pbo(m), 0.1)

    def test_hasard_meme_exposition(self):
        x = V.hasard(20000, 0.3, 10, 1)
        self.assertAlmostEqual(x.mean(), 0.3, delta=0.05)

    def test_bootstrap_identiques(self):
        a = pd.Series(np.random.default_rng(1).normal(0, 0.01, 500))
        self.assertEqual(V.bootstrap_difference(a, a), 1.0)


class Qualite(unittest.TestCase):
    def test_detecte_trou_et_doublon(self):
        df = marche_synthetique(200)
        df = pd.concat([df.iloc[:50], df.iloc[60:], df.iloc[[100]]]).sort_index()
        q = donnees.qualite(df, "1d")
        self.assertEqual(q["doublons"], 1)
        self.assertGreaterEqual(q["nb_trous"], 1)
        self.assertFalse(donnees.suffisant(q))


if __name__ == "__main__":
    unittest.main()
