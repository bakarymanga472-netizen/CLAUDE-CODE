"""Ensemble de modèles pour les marchés « +0,5 / +1,5 but en 1re / 2e mi-temps ».

Chaque marché (mi-temps x seuil) a son propre modèle, entraîné sur sa propre
cible : on ne déduit jamais la 2e mi-temps de la 1re, ni le +1,5 du +0,5.

Modèles de base (complémentaires) :
  1. poisson   : Poisson attaque x défense par mi-temps, P(au moins k buts)
  2. dixon_coles: Poisson domicile/extérieur avec correction de Dixon-Coles
                 des petits scores (ρ estimé par maximum de vraisemblance)
  3. marche    : λ total implicite des cotes +/-2,5 (marge retirée), réparti
                 selon la part de buts de la ligue dans la mi-temps
  4. bayes     : fréquences « but dans la mi-temps » des deux équipes,
                 rétrécies vers la ligue (bayésien empirique) ; pour +1,5,
                 converties en λ puis en P(au moins 2 buts)
  5. logistique: régression logistique sur les variables d'avant-match
  6. gbm       : gradient boosting (HistGradientBoosting)

Combinaison : poids positifs (somme 1) appliqués aux logits des modèles,
puis calibration de Platt, le tout optimisé sur des prédictions hors
échantillon obtenues par validation croisée temporelle. Un modèle qui
n'apporte rien hors échantillon reçoit un poids proche de zéro.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize, minimize_scalar

from .. import config
from ..metrics import wilson_interval

BASE_MODELS = ["poisson", "dixon_coles", "marche", "bayes", "logistique", "gbm"]
EPS = 1e-4


def half_of(market: str) -> str:
    return config.MARKET_SPECS[market][0]


def prob_at_least(lam, k: int):
    """P(au moins k buts) pour un nombre de buts de Poisson de moyenne λ (k = 1 ou 2)."""
    lam = np.clip(np.asarray(lam, dtype=float), 0, None)
    if k == 1:
        return 1 - np.exp(-lam)
    if k == 2:
        return 1 - np.exp(-lam) * (1 + lam)
    raise ValueError(f"seuil non géré : {k}")


def feature_columns(h: str) -> list[str]:
    cols = [f"poisson_lambda_{h}", f"league_any_{h}", "league_h1_share",
            "market_p_over25", "market_lambda_total", "market_fav_strength", "market_home_fav",
            "home_n_matches", "away_n_matches", "home_rest_days", "away_rest_days"]
    for side in ("home", "away"):
        cols += [f"{side}_{h}_for", f"{side}_{h}_against", f"{side}_{h}_any",
                 f"{side}_shots_for", f"{side}_shots_against", f"{side}_sot_for", f"{side}_sot_against"]
    cols += [f"home_home_{h}_for", f"home_home_{h}_against", f"away_away_{h}_for", f"away_away_{h}_against"]
    return cols


def dixon_coles_prob_goal(lam_home, lam_away, rho: float, k: int = 1):
    """P(au moins k buts, k = 1 ou 2) avec la correction de Dixon-Coles.

    P(0-0) = e^(-λd-λe)·τ(0,0) avec τ(0,0) = 1 - λd·λe·ρ ; pour k = 2 s'ajoutent
    P(1-0) = e^(-λd-λe)·λd·τ(1,0) et P(0-1) = e^(-λd-λe)·λe·τ(0,1), avec
    τ(1,0) = 1 + λe·ρ et τ(0,1) = 1 + λd·ρ.
    ρ < 0 augmente la probabilité d'un 0-0 par rapport au Poisson indépendant.
    """
    lam_home = np.clip(np.asarray(lam_home, dtype=float), 0, None)
    lam_away = np.clip(np.asarray(lam_away, dtype=float), 0, None)
    base = np.exp(-(lam_home + lam_away))
    below = base * np.clip(1 - lam_home * lam_away * rho, 1e-6, None)
    if k == 2:
        below = below + base * (lam_home * np.clip(1 + lam_away * rho, 1e-6, None)
                                + lam_away * np.clip(1 + lam_home * rho, 1e-6, None))
    elif k != 1:
        raise ValueError(f"seuil non géré : {k}")
    return np.clip(1 - below, 0.0, 1.0)


def fit_dixon_coles_rho(lam_home, lam_away, y, k: int = 1) -> float:
    """Estime ρ par maximum de vraisemblance sur la cible « au moins k buts »."""
    y = np.asarray(y, dtype=float)

    def nll(rho):
        p = np.clip(dixon_coles_prob_goal(lam_home, lam_away, rho, k), EPS, 1 - EPS)
        return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))

    return float(minimize_scalar(nll, bounds=(-1.0, 0.9), method="bounded").x)


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, EPS, 1 - EPS)
    return np.log(p / (1 - p))


class HalfGoalModel:
    """Modèle complet (bases + méta-modèle) pour un marché de mi-temps."""

    def __init__(self, market: str, random_state: int = 0):
        self.market = market
        self.h, self.k = config.MARKET_SPECS[market]
        self.target = config.target_column(market)
        self.cols = feature_columns(self.h)
        self.random_state = random_state
        self.logistic = None
        self.gbm = None
        self.weights = np.full(len(BASE_MODELS), 1 / len(BASE_MODELS))
        self.platt = (0.0, 1.0)
        self.rho = 0.0
        self.validation_report: dict = {}
        self.calibration_bins: list[dict] = []

    # ------------------------------------------------------- modèles de base
    def _rule_based(self, df: pd.DataFrame) -> pd.DataFrame:
        h, k = self.h, getattr(self, "k", 1)  # getattr : modèles enregistrés avant le +1,5
        out = pd.DataFrame(index=df.index)
        out["poisson"] = prob_at_least(df[f"poisson_lambda_{h}"], k)
        out["dixon_coles"] = dixon_coles_prob_goal(df[f"poisson_lambda_home_{h}"],
                                                   df[f"poisson_lambda_away_{h}"], self.rho, k)
        share = df["league_h1_share"] if h == "h1" else 1 - df["league_h1_share"]
        out["marche"] = prob_at_least(share * df["market_lambda_total"], k)
        freq = (df[f"home_{h}_any"] + df[f"away_{h}_any"]) / 2
        out["bayes"] = freq if k == 1 else prob_at_least(-np.log(1 - freq.clip(upper=0.999)), k)
        return out

    def _fit_ml(self, df: pd.DataFrame) -> None:
        X, y = df[self.cols], df[self.target]
        self.rho = fit_dixon_coles_rho(df[f"poisson_lambda_home_{self.h}"],
                                       df[f"poisson_lambda_away_{self.h}"], y, self.k)
        self.logistic = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                      LogisticRegression(C=0.5, max_iter=2000))
        self.logistic.fit(X, y)
        self.gbm = HistGradientBoostingClassifier(learning_rate=0.04, max_iter=250, max_depth=3,
                                                  min_samples_leaf=80, l2_regularization=1.0,
                                                  random_state=self.random_state)
        self.gbm.fit(X, y)

    def base_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        out = self._rule_based(df)
        X = df[self.cols]
        out["logistique"] = self.logistic.predict_proba(X)[:, 1]
        out["gbm"] = self.gbm.predict_proba(X)[:, 1]
        return out

    def _filled_logits(self, base: pd.DataFrame) -> np.ndarray:
        filled = base.copy()
        filled["marche"] = filled["marche"].fillna(filled["poisson"])
        return np.column_stack([_logit(filled[m].to_numpy()) for m in BASE_MODELS])

    def _combine(self, logits: np.ndarray) -> np.ndarray:
        z = self.platt[0] + self.platt[1] * (logits @ self.weights)
        return 1 / (1 + np.exp(-z))

    # -------------------------------------------------------------- entraînement
    def fit(self, train: pd.DataFrame, n_folds: int = 3, fold_fraction: float = 0.15) -> "HalfGoalModel":
        """Validation croisée temporelle puis combinaison pondérée et calibrée.

        Les prédictions hors échantillon (« out-of-fold ») sont produites sur
        les dernières tranches de la période d'entraînement, chacune prédite par
        des modèles entraînés uniquement sur ce qui précède. Les poids de
        l'ensemble (positifs, de somme 1) et la calibration (Platt) sont ajustés
        sur ces prédictions, puis les modèles ML sont ré-entraînés sur tout.
        """
        train = train.sort_values("date").reset_index(drop=True)
        n = len(train)
        bounds = [int(n * (1 - fold_fraction * (n_folds - k))) for k in range(n_folds + 1)]
        oof_base, oof_y, oof_dates = [], [], []
        for start, stop in zip(bounds[:-1], bounds[1:]):
            past, block = train.iloc[:start], train.iloc[start:stop]
            self._fit_ml(past)
            oof_base.append(self.base_probabilities(block))
            oof_y.append(block[self.target].to_numpy())
            oof_dates.append(block["date"])
        base_v = pd.concat(oof_base, ignore_index=True)
        y_v = np.concatenate(oof_y)
        dates = pd.concat(oof_dates)
        logits = self._filled_logits(base_v)

        self.validation_report = {"n_validation": int(len(y_v)),
                                  "periode_validation": [str(dates.min().date()), str(dates.max().date())]}
        for i, m in enumerate(BASE_MODELS):
            self.validation_report[f"logloss_{m}"] = float(log_loss(y_v, 1 / (1 + np.exp(-logits[:, i])),
                                                                    labels=[0, 1]))

        # Poids positifs (paramétrage softmax) + calibration de Platt, optimisés
        # conjointement sur la log-loss hors échantillon.
        k = len(BASE_MODELS)

        def objective(theta):
            w = np.exp(theta[:k] - theta[:k].max())
            w /= w.sum()
            z = theta[k] + theta[k + 1] * (logits @ w)
            p = np.clip(1 / (1 + np.exp(-z)), EPS, 1 - EPS)
            return -np.mean(y_v * np.log(p) + (1 - y_v) * np.log(1 - p))

        theta0 = np.concatenate([np.zeros(k), [0.0, 1.0]])
        res = minimize(objective, theta0, method="L-BFGS-B")
        w = np.exp(res.x[:k] - res.x[:k].max())
        self.weights = w / w.sum()
        self.platt = (float(res.x[k]), float(res.x[k + 1]))
        combined = self._combine(logits)
        self.validation_report["logloss_ensemble"] = float(log_loss(y_v, combined, labels=[0, 1]))
        self.validation_report["poids"] = {m: float(x) for m, x in zip(BASE_MODELS, self.weights)}
        self.validation_report["platt"] = list(self.platt)
        self.calibration_bins = _calibration_bins(combined, y_v, None if self.k == 1 else EDGES_O15)

        # Modèles ML (et ρ de Dixon-Coles) ré-entraînés sur toute la période disponible.
        self._fit_ml(train)
        self.validation_report["rho_dixon_coles"] = self.rho
        return self

    # --------------------------------------------------------------- prédiction
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        base = self.base_probabilities(df)
        final = self._combine(self._filled_logits(base))
        out = base.copy()
        out["probabilite"] = final
        spread = base[BASE_MODELS].std(axis=1, skipna=True)
        out["ecart_modeles"] = spread
        lows, highs = [], []
        for p, s in zip(final, spread.fillna(0).to_numpy()):
            lo, hi = self.interval(p)
            lows.append(max(0.0, min(lo, p - s)))
            highs.append(min(1.0, max(hi, p + s)))
        out["prob_basse"] = lows
        out["prob_haute"] = highs
        return out

    def interval(self, p: float) -> tuple[float, float]:
        """Intervalle de Wilson à 95 % du taux observé dans la tranche de calibration."""
        for b in self.calibration_bins:
            if b["low"] <= p < b["high"] or (p >= 1.0 and b["high"] >= 1.0):
                return b["ci_low"], b["ci_high"]
        return max(0.0, p - 0.1), min(1.0, p + 0.1)


# Tranches de calibration du +1,5 (probabilités typiquement entre 25 et 70 %).
EDGES_O15 = [0.0, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 1.0001]


def _calibration_bins(p: np.ndarray, y: np.ndarray, edges=None) -> list[dict]:
    edges = edges or [0.0, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0001]
    bins = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        if n == 0:
            bins.append({"low": lo, "high": hi, "n": 0, "pred": math.nan, "obs": math.nan,
                         "ci_low": lo, "ci_high": min(hi, 1.0)})
            continue
        k = int(y[mask].sum())
        ci_low, ci_high = wilson_interval(k, n)
        bins.append({"low": lo, "high": hi, "n": n, "pred": float(p[mask].mean()),
                     "obs": k / n, "ci_low": ci_low, "ci_high": ci_high})
    return bins


class HalfTimePredictor:
    """Regroupe les modèles de tous les marchés de mi-temps."""

    def __init__(self, random_state: int = 0):
        self.models = {m: HalfGoalModel(m, random_state) for m in config.MARKETS}
        self.trained_until: str | None = None

    def fit(self, train: pd.DataFrame) -> "HalfTimePredictor":
        for model in self.models.values():
            model.fit(train)
        self.trained_until = str(train["date"].max().date())
        return self

    def predict(self, df: pd.DataFrame) -> dict[str, pd.DataFrame]:
        return {m: model.predict(df) for m, model in self.models.items()}
