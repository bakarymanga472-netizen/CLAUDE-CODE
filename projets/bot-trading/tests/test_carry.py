"""Tests du carry funding (S3) sur données SYNTHÉTIQUES : aucun réseau."""
import unittest

import numpy as np
import pandas as pd

from carry import donnees as D, strategie as S


def marche(n=400, graine=3, funding=None):
    """Spot, perp (base aléatoire faible) et funding toutes les 8 h, FICTIFS."""
    rng = np.random.default_rng(graine)
    jours = pd.date_range("2021-01-01", periods=n, freq="D")
    s = 100 * np.exp(np.cumsum(rng.normal(0, 0.03, n)))
    f = s * (1 + rng.normal(0, 0.001, n))
    spot = pd.DataFrame({"open": s, "high": s * 1.01, "low": s * 0.99, "close": s, "volume": 1.0}, index=jours)
    perp = pd.DataFrame({"open": f, "high": f * 1.01, "low": f * 0.99, "close": f, "volume": 1.0}, index=jours)
    t = pd.date_range(jours[0], jours[-1] + pd.Timedelta(days=1), freq="8h")
    taux = rng.normal(0.0001, 0.0002, len(t)) if funding is None else np.full(len(t), funding)
    return spot, perp, pd.Series(taux, index=t)


class PasDeLookAhead(unittest.TestCase):
    def test_decisions_inchangees_si_on_coupe_le_futur(self):
        spot, perp, fund = marche()
        df = S.aligner(spot, perp, fund)
        for p in S.GRILLE:
            complet = S.positions(fund, df.index, p)
            for coupe in (150, 300):
                limite = df.index[coupe]
                f2 = fund[fund.index < limite]
                court = S.positions(f2, df.index[:coupe], p)
                pd.testing.assert_series_equal(complet.iloc[:coupe], court, obj=f"{S.nom(p)} coupé à {coupe}")

    def test_futur_modifie_ne_change_pas_le_passe(self):
        spot, perp, fund = marche()
        df = S.aligner(spot, perp, fund)
        p = S.GRILLE[1]
        r1 = S.simuler(df, S.positions(fund, df.index, p), clore_a_la_fin=False)["net"]
        fund2 = fund.copy()
        fund2[fund2.index >= df.index[250]] = -0.003           # funding futur bouleversé
        spot2, perp2 = spot.copy(), perp.copy()
        spot2.iloc[251:, :4] *= 2.0
        perp2.iloc[251:, :4] *= 2.0
        df2 = S.aligner(spot2, perp2, fund2)
        r2 = S.simuler(df2, S.positions(fund2, df2.index, p), clore_a_la_fin=False)["net"]
        # le jour 249 couvre l'ouverture 249 → ouverture 250 et les paiements jusqu'à 250 00:00 (inchangés)
        pd.testing.assert_series_equal(r1.iloc[:249], r2.iloc[:249])

    def test_indicateur_ignore_le_paiement_de_minuit_du_jour(self):
        jours = pd.date_range("2021-01-01", periods=5, freq="D")
        t = pd.date_range("2021-01-01", periods=15, freq="8h")
        fund = pd.Series(0.0, index=t)
        fund[pd.Timestamp("2021-01-03 00:00")] = 1.0
        ind = S.indicateur(fund, 1, jours)
        self.assertEqual(ind[pd.Timestamp("2021-01-03")], 0.0)        # pas encore connu à la décision
        self.assertEqual(ind[pd.Timestamp("2021-01-04")], 0.0)        # dernier paiement < 04 00:00 = 03 16:00


class ComptabiliteFunding(unittest.TestCase):
    def test_funding_journalier_regroupe_08_16_et_minuit_suivant(self):
        t = pd.to_datetime(["2021-01-01 00:00", "2021-01-01 08:00", "2021-01-01 16:00", "2021-01-02 00:00"])
        fj = S.funding_journalier(pd.Series([1.0, 2.0, 3.0, 4.0], index=t))
        self.assertEqual(fj[pd.Timestamp("2020-12-31")], 1.0)
        self.assertEqual(fj[pd.Timestamp("2021-01-01")], 9.0)

    def test_cas_connu_prix_constants_sans_couts(self):
        jours = pd.date_range("2021-01-01", periods=30, freq="D")
        px = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0}, index=jours)
        t = pd.date_range(jours[0], jours[-1] + pd.Timedelta(days=1), freq="8h")
        fund = pd.Series(0.0001, index=t)
        df = S.aligner(px, px, fund)
        zero = S.CoutsCarry(0, 0, 0, 0, bande=0.0)          # rééquilibrage quotidien : notionnel = E/2 chaque jour
        res = S.simuler(df, S.positions(fund, df.index, S.GRILLE[0]), zero)
        # notionnel short = 50 % du capital : 3 × 0,01 % × 0,5 = 0,015 % par jour, composé
        np.testing.assert_allclose(res["net"].values, 0.00015, rtol=1e-9)
        self.assertAlmostEqual((1 + res["net"]).prod(), 1.00015 ** len(df), places=12)

    def test_funding_negatif_coute_au_short(self):
        spot, perp, fund = marche(funding=-0.0002)
        df = S.aligner(spot, perp, fund)
        res = S.simuler(df, S.positions(fund, df.index, S.GRILLE[0]), S.CoutsCarry(0, 0, 0, 0))
        self.assertLess(res["funding"].sum(), 0)

    def test_couverture_delta_neutre(self):
        """Sans funding ni coûts, avec perp = spot, le PnL reste ~nul malgré des prix très volatils."""
        spot, _, fund = marche(funding=0.0)
        df = S.aligner(spot, spot, fund)
        res = S.simuler(df, S.positions(fund, df.index, S.GRILLE[0]), S.CoutsCarry(0, 0, 0, 0, bande=0.0))
        self.assertLess(abs((1 + res["net"]).prod() - 1), 1e-9)


class Couts(unittest.TestCase):
    def test_aller_retour_quatre_jambes(self):
        jours = pd.date_range("2021-01-01", periods=10, freq="D")
        px = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0, "volume": 1.0}, index=jours)
        fund = pd.Series(0.0, index=pd.date_range(jours[0], jours[-1] + pd.Timedelta(days=1), freq="8h"))
        df = S.aligner(px, px, fund)
        c = S.CoutsCarry()
        pos = pd.Series([0, 1, 1, 1, 0, 0, 0, 0, 0], index=df.index, dtype=float)
        res = S.simuler(df, pos, c)
        k = (c.spot + c.perp) / 2
        self.assertAlmostEqual((1 + res["net"]).prod(), (1 - k) * (1 - k), places=12)
        self.assertEqual(len(res["trades"]), 1)

    def test_couts_croissants(self):
        spot, perp, fund = marche(600)
        df = S.aligner(spot, perp, fund)
        for p in S.GRILLE:
            pos = S.positions(fund, df.index, p)
            tot = [(1 + S.simuler(df, pos, S.CoutsCarry().stresse(f))["net"]).prod() for f in (0.0, 1.0, 2.0, 3.0)]
            self.assertTrue(all(a > b for a, b in zip(tot, tot[1:])), f"{S.nom(p)} : {tot}")


class Liquidation(unittest.TestCase):
    def test_seuil_levier_1_proche_de_100_pourcent(self):
        self.assertAlmostEqual(S.seuil_liquidation(1, 0.004), 0.996 / 1.004)
        self.assertAlmostEqual(S.seuil_liquidation(2, 0.0), 0.5)

    def test_pic_detecte(self):
        spot, perp, fund = marche()
        perp.iloc[100, perp.columns.get_loc("high")] = perp.open.iloc[100] * 2.5
        df = S.aligner(spot, perp, fund)
        res = S.simuler(df, S.positions(fund, df.index, S.GRILLE[0]))
        self.assertEqual(res["liquidations"].sum(), 1)
        self.assertEqual(S.liquidations_quotidiennes(perp, perp.index[0], perp.index[-1])["levier_1"]["jours_liquides"], 1)


class Lecture(unittest.TestCase):
    def test_funding_csv_avec_gigue(self):
        txt = "calc_time,funding_interval_hours,last_funding_rate\n1577836800000,8,-0.00012359\n1577923200002,8,0.00003662\n"
        df = D.lire_funding_csv(txt)
        self.assertEqual(str(df.index[1]), "2020-01-02 00:00:00")
        self.assertAlmostEqual(df.taux.iloc[0], -0.00012359)

    def test_klines_avec_et_sans_entete(self):
        ligne = "1577836800000,7189.43,7260.43,7170.15,7197.57,56801.329,1577923199999,409678760.5,101871,28834.2,208001969.8,0\n"
        ent = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
        a, b = D.lire_klines_csv(ligne), D.lire_klines_csv(ent + ligne)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(a.open.iloc[0], 7189.43)

    def test_qualite_detecte_trou_et_doublon(self):
        t = pd.date_range("2021-01-01", periods=12, freq="8h").delete(5)
        df = pd.DataFrame({"intervalle_h": 8.0, "taux": 0.0001}, index=t)
        df = pd.concat([df, df.iloc[[2]]])
        q = D.qualite_funding(df)
        self.assertEqual((q["nb_trous"], q["doublons"], q["manquants"]), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
