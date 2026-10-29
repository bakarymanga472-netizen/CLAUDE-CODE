"""Mesures de qualité des probabilités (section 11 du cahier des charges)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

EPS = 1e-6


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalle de confiance de Wilson pour une proportion (95 % par défaut)."""
    if n == 0:
        return 0.0, 1.0
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def brier(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def log_loss(p: np.ndarray, y: np.ndarray) -> float:
    p = np.clip(np.asarray(p, dtype=float), EPS, 1 - EPS)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def expected_calibration_error(p: np.ndarray, y: np.ndarray, n_bins: int = 10) -> float:
    p, y = np.asarray(p), np.asarray(y)
    edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi) if hi < 1 else (p >= lo) & (p <= hi)
        if mask.any():
            ece += mask.mean() * abs(p[mask].mean() - y[mask].mean())
    return float(ece)


def calibration_table(p: np.ndarray, y: np.ndarray, edges=None) -> pd.DataFrame:
    edges = edges or [0.0, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0001]
    p, y = np.asarray(p), np.asarray(y)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        if not n:
            continue
        k = int(y[mask].sum())
        ci = wilson_interval(k, n)
        rows.append({"tranche": f"{lo:.2f}–{min(hi, 1):.2f}", "n": n, "prob_moyenne": p[mask].mean(),
                     "taux_observe": k / n, "ic95_bas": ci[0], "ic95_haut": ci[1]})
    return pd.DataFrame(rows)


def high_confidence_table(p: np.ndarray, y: np.ndarray,
                          thresholds=(0.75, 0.80, 0.85, 0.88, 0.90, 0.92, 0.95)) -> pd.DataFrame:
    """Taux de réussite des sélections au-dessus de chaque seuil, avec IC 95 %."""
    p, y = np.asarray(p), np.asarray(y)
    rows = []
    for t in thresholds:
        mask = p >= t
        n = int(mask.sum())
        k = int(y[mask].sum()) if n else 0
        ci = wilson_interval(k, n) if n else (float("nan"), float("nan"))
        rows.append({"seuil": t, "n_selections": n, "part_des_matchs": n / len(p) if len(p) else 0.0,
                     "prob_moyenne_annoncee": p[mask].mean() if n else float("nan"),
                     "taux_reussite": k / n if n else float("nan"), "echecs": n - k,
                     "ic95_bas": ci[0], "ic95_haut": ci[1]})
    return pd.DataFrame(rows)


def summary(p: np.ndarray, y: np.ndarray) -> dict:
    return {"n": int(len(y)), "taux_base": float(np.mean(y)), "brier": brier(p, y),
            "log_loss": log_loss(p, y), "ece": expected_calibration_error(p, y)}
