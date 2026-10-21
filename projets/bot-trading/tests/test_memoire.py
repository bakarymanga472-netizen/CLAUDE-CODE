import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from memoire import analyste, prevention
from memoire.base import Memoire
from memoire.exemple_fictif import fabriquer
from memoire.registre import Registre


def trade(i=1, **modifs):
    t = fabriquer(i, np.random.default_rng(i))
    for chemin, v in modifs.items():
        cible, cles = t, chemin.split("__")
        for k in cles[:-1]:
            cible = cible[k]
        cible[cles[-1]] = v
    return t


class Immuabilite(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.m = Memoire(self.dir)

    def test_modification_detectee(self):
        self.m.enregistrer_trade(trade(1))
        self.m.enregistrer_trade(trade(2))
        f = self.dir / "trades.jsonl"
        lignes = f.read_text().splitlines()
        e = json.loads(lignes[0])
        e["resultat"]["net"] = 0.5
        lignes[0] = json.dumps(e)
        f.write_text("\n".join(lignes) + "\n")
        self.assertTrue(self.m.verifier()["trades"])

    def test_suppression_detectee(self):
        for i in range(3):
            self.m.enregistrer_trade(trade(i))
        f = self.dir / "trades.jsonl"
        lignes = f.read_text().splitlines()
        f.write_text("\n".join([lignes[0], lignes[2]]) + "\n")
        self.assertTrue(self.m.verifier()["trades"])

    def test_correction_sans_reecriture(self):
        self.m.enregistrer_trade(trade(1))
        avant = (self.dir / "trades.jsonl").read_text()
        self.m.corriger("FICTIF-0001", "resultat.net", 0.0, "relevé courtier", "test")
        self.assertEqual(avant, (self.dir / "trades.jsonl").read_text())
        eff = self.m.trades_effectifs()[0]
        self.assertEqual(eff["resultat"]["net"], 0.0)
        self.assertEqual(len(eff["corrections"]), 1)
        self.assertEqual(self.m.verifier()["trades"], [])

    def test_refus(self):
        self.m.enregistrer_trade(trade(1))
        with self.assertRaises(ValueError):
            self.m.enregistrer_trade(trade(1))           # doublon
        t = trade(2)
        del t["plan"]
        with self.assertRaises(ValueError):
            self.m.enregistrer_trade(t)                  # incomplet
        with self.assertRaises(ValueError):
            self.m.corriger("FICTIF-0001", "resultat.net", 0, "", "x")   # sans justification

    def test_pas_de_methode_de_suppression(self):
        self.assertFalse(any(n in dir(Registre) for n in ("supprimer", "modifier", "remplacer", "effacer")))


class Diagnostic(unittest.TestCase):
    def test_donnees_perimees(self):
        d = analyste.diagnostiquer(trade(1, donnees_entree__age_secondes=4 * 86400))
        self.assertEqual(d["donnees"]["niveau"], "cause confirmée")

    def test_ordre_rejete_et_doublon(self):
        t = trade(1)
        t["execution"]["ordres"].append(dict(t["execution"]["ordres"][0]))
        t["execution"]["ordres"].append({"id": "R", "statut": "rejete"})
        d = analyste.diagnostiquer(t)
        self.assertEqual(d["execution"]["niveau"], "cause confirmée")
        self.assertEqual(len(d["execution"]["constats"]), 2)

    def test_glissement_probable_puis_confirme(self):
        self.assertEqual(analyste.diagnostiquer(trade(1, resultat__glissement=0.0009))["execution"]["niveau"], "cause probable")
        self.assertEqual(analyste.diagnostiquer(trade(1, resultat__glissement=0.003))["execution"]["niveau"], "cause confirmée")

    def test_taille_et_regle(self):
        d = analyste.diagnostiquer(trade(1, execution__taille=0.3))
        self.assertIn("taille", " ".join(d["processus"]["constats"]))
        t = trade(1)
        t["plan"]["regles"][0]["valeur"] = -1
        self.assertFalse(analyste.diagnostiquer(t)["statistique"]["conforme"])

    def test_gain_non_conforme(self):
        t = trade(1, execution__taille=0.3)
        t["resultat"]["net"] = 0.05
        self.assertIn("NON conforme", analyste.diagnostiquer(t)["statistique"]["lecture"])

    def test_perte_normale_ne_modifie_rien(self):
        t = trade(1)
        t["resultat"].update(net=-0.03, R=-0.5)
        a = analyste.analyser(t, analyste.diagnostiquer(t), [], np.random.default_rng(0).normal(0, 1, 1000))
        self.assertIn("perte normale", a["nature"])
        self.assertIsNone(a["hypothese"])
        self.assertIn("aucune modification", a["decision"])
        self.assertIn("échantillon insuffisant", a["recurrence"]["statut"])


class Prevention(unittest.TestCase):
    def test_chaque_regle_bloque_le_cas_observe(self):
        self.assertIsNotNone(prevention.donnees_fraiches({"qualite_ok": True, "age_secondes": 3e5, "duree_barre_secondes": 86400}))
        self.assertIsNone(prevention.donnees_fraiches({"qualite_ok": True, "age_secondes": 10, "duree_barre_secondes": 86400, "valeurs": {"a": 1}}))
        self.assertIsNotNone(prevention.taille_conforme(0.2, 0.1))
        self.assertIsNone(prevention.taille_conforme(0.102, 0.1))
        self.assertIsNotNone(prevention.regles_respectees([{"nom": "x", "valeur": -1, "op": ">", "seuil": 0}]))
        self.assertIsNotNone(prevention.pas_de_doublon("A", {"A"}))
        self.assertIsNotNone(prevention.ordre_confirme([{"statut": "rejete"}]))
        self.assertIsNotNone(prevention.glissement_acceptable(0.01, 0.002))


class Stats(unittest.TestCase):
    def test_binomiale(self):
        self.assertAlmostEqual(analyste.binom_sup(0, 10, 0.3), 1.0)
        self.assertAlmostEqual(analyste.binom_sup(10, 10, 0.5), 0.5 ** 10)


if __name__ == "__main__":
    unittest.main()
