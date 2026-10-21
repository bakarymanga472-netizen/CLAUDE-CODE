import os
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from amelioration import boucle, garde_fous, surveillance
from amelioration.variantes import exposition
from labo import donnees
from memoire.registre import Registre
from tests.outils import marche_synthetique

COMBINE_OK = {"stable": {"pire_baisse": -0.40}, "candidate": {"pire_baisse": -0.35}}
ROBUSTE = {"delta_sharpe_couts_x3": 0.1, "voisins": [{"delta_sharpe": 0.05}, {"delta_sharpe": 0.02}]}


class Decision(unittest.TestCase):
    def test_acceptee_si_tous_les_criteres(self):
        v, r = boucle.decider(0.01, 4, COMBINE_OK, ROBUSTE)
        self.assertEqual(v, "acceptée comme candidate")
        self.assertEqual(r, [])

    def test_rejetee_pour_chaque_critere(self):
        self.assertEqual(boucle.decider(0.2, 4, COMBINE_OK, ROBUSTE)[0], "rejetée")
        self.assertEqual(boucle.decider(0.01, 2, COMBINE_OK, ROBUSTE)[0], "rejetée")
        pire = {"stable": {"pire_baisse": -0.40}, "candidate": {"pire_baisse": -0.50}}
        self.assertEqual(boucle.decider(0.01, 4, pire, ROBUSTE)[0], "rejetée")
        self.assertEqual(boucle.decider(0.01, 4, COMBINE_OK, {**ROBUSTE, "delta_sharpe_couts_x3": -0.1})[0], "rejetée")
        fragile = {**ROBUSTE, "voisins": [{"delta_sharpe": 0.1}, {"delta_sharpe": -0.01}]}
        self.assertEqual(boucle.decider(0.01, 4, COMBINE_OK, fragile)[0], "rejetée")


class Versions(unittest.TestCase):
    def setUp(self):
        self.ancien = boucle.DOSSIER
        boucle.DOSSIER = Path(tempfile.mkdtemp())
        v = boucle.reg(f"versions_{boucle.INSTRUMENT}")
        v.ajouter({"evenement": "stable_definie", "version": "S1"}, "VER")
        v.ajouter({"evenement": "candidate_acceptee", "version": "S1+H"}, "VER")

    def tearDown(self):
        boucle.DOSSIER = self.ancien

    def test_candidate_ne_remplace_jamais_la_stable(self):
        stable, cand = boucle.etat_versions()
        self.assertEqual(stable, "S1")
        self.assertIn("attente", cand["S1+H"])

    def test_promotion_exige_humain(self):
        with self.assertRaises(garde_fous.AutorisationRequise):
            boucle.promouvoir("S1+H", None)
        self.assertEqual(boucle.etat_versions()[0], "S1")
        boucle.promouvoir("S1+H", "OK de Bakary le 2026-10-21")
        self.assertEqual(boucle.etat_versions()[0], "S1+H")

    def test_retour_stable_en_cas_de_degradation(self):
        boucle.promouvoir("S1+H", "OK humain")
        boucle.retour_stable("S1+H", "Sharpe glissant < 0 en simulation")
        self.assertEqual(boucle.etat_versions()[0], "S1+H")   # retour vers la stable courante, tracé
        evts = [e["evenement"] for e in boucle.reg(f"versions_{boucle.INSTRUMENT}").lire()]
        self.assertEqual(evts[-1], "retour_stable")


class GardeFous(unittest.TestCase):
    def test_interdits(self):
        for a in ("deployer_reel", "augmenter_levier", "modifier_limites_risque", "debloquer_compte_reel"):
            with self.assertRaises(garde_fous.AutorisationRequise):
                garde_fous.exiger_humain(a)
        with self.assertRaises(garde_fous.AutorisationRequise):
            garde_fous.exiger_humain("deployer_reel", "même avec un texte")
        with self.assertRaises(garde_fous.AutorisationRequise):
            exposition(marche_synthetique(300), {"strategie": "tendance", "params": {"jours": 30}, "levier": 2})


class Variantes(unittest.TestCase):
    def test_modifications_sans_futur(self):
        df = marche_synthetique(900)
        for m in ({"type": "regimes_exclus", "regimes": ["range"]}, {"type": "stop_suiveur", "k_sigma": 3.0}):
            spec = {"strategie": "tendance", "params": {"jours": 30}, "modifications": [m]}
            a, b = exposition(df, spec), exposition(df.iloc[:600], spec)
            pd.testing.assert_series_equal(a.iloc[:600], b, check_names=False)

    def test_psi(self):
        rng = np.random.default_rng(0)
        self.assertLess(surveillance.psi(rng.normal(0, 1, 2000), rng.normal(0, 1, 300)), 0.1)
        self.assertGreater(surveillance.psi(rng.normal(0, 1, 2000), rng.normal(2, 1, 300)), 0.25)


@unittest.skipUnless((donnees.DOSSIER / "BTCUSDT_1d.csv").exists() and not os.environ.get("BOUCLE_EN_COURS"),
                     "données réelles absentes, ou lancé depuis la boucle elle-même (évite la récursion)")
class Reproductibilite(unittest.TestCase):
    def test_meme_hypothese_meme_resultat(self):
        evts = Registre(boucle.DOSSIER / "hypotheses.jsonl").lire()
        res = [e for e in evts if e["evenement"] == "resultat" and e["hypothese"] == "H-001"]
        if not res:
            self.skipTest("H-001 pas encore testée")
        h = next(e["definition"] for e in evts if e["evenement"] == "declaree" and e["hypothese"] == "H-001")
        # Le rapport cite le nombre de tests au moment du test : on le rejoue à l'identique
        etapes, verdict, _ = boucle.tester_hypothese(h, res[0]["etapes"]["5_comparaison"]["tests_cumules"] - 1)
        self.assertEqual(boucle.empreinte({"etapes": etapes, "verdict": verdict}), res[0]["empreinte_resultat"])


if __name__ == "__main__":
    unittest.main()
