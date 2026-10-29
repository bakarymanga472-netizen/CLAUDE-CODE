"""Versions de modèles, évolution contrôlée et retour arrière (section 10).

Règles :
- une nouvelle configuration n'est déployée que si elle bat la configuration
  en production sur une période récente qu'aucune des deux n'a vue à
  l'entraînement, avec une amélioration statistiquement crédible
  (bootstrap apparié sur la log-loss) ;
- chaque version est conservée : on peut revenir à la précédente ;
- un pari perdu isolé ne déclenche jamais de modification.
"""

from __future__ import annotations

import json
import pickle
import random
from dataclasses import asdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from . import config
from .features import FeatureBuilder
from .models.ensemble import HalfTimePredictor

REGISTRY_FILE = "registry.json"

# Sécurité : les modèles sont sérialisés avec pickle, qui peut exécuter du code
# au chargement. On ne charge QUE des fichiers produits localement par ce projet
# dans MODELS_DIR (dossier ignoré par git). Ne jamais charger un model.pkl
# reçu ou téléchargé d'ailleurs.


def _registry_path():
    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return config.MODELS_DIR / REGISTRY_FILE


def load_registry() -> dict:
    path = _registry_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"production": None, "history": []}


def save_registry(reg: dict) -> None:
    _registry_path().write_text(json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8")


def save_model(predictor: HalfTimePredictor, settings: config.FeatureSettings, metrics: dict,
               note: str) -> str:
    version = datetime.now(timezone.utc).strftime("v%Y%m%d-%H%M%S")
    folder = config.MODELS_DIR / version
    folder.mkdir(parents=True, exist_ok=True)
    with open(folder / "model.pkl", "wb") as fh:
        pickle.dump(predictor, fh)
    meta = {"version": version, "trained_until": predictor.trained_until,
            "feature_settings": asdict(settings), "metrics": metrics, "note": note,
            "validation": {m: mdl.validation_report for m, mdl in predictor.models.items()}}
    (folder / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False, default=float),
                                          encoding="utf-8")
    reg = load_registry()
    if reg["production"]:
        reg["history"].append(reg["production"])
    reg["production"] = version
    save_registry(reg)
    return version


def load_production() -> tuple[HalfTimePredictor, dict]:
    reg = load_registry()
    if not reg["production"]:
        raise FileNotFoundError("Aucun modèle en production : lancez d'abord `train`.")
    folder = config.MODELS_DIR / reg["production"]
    with open(folder / "model.pkl", "rb") as fh:
        predictor = pickle.load(fh)
    meta = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    return predictor, meta


def rollback() -> str:
    reg = load_registry()
    if not reg["history"]:
        raise RuntimeError("Aucune version précédente disponible.")
    reg["production"] = reg["history"].pop()
    save_registry(reg)
    return reg["production"]


def production_settings() -> config.FeatureSettings:
    try:
        _, meta = load_production()
        s = meta["feature_settings"]
        return config.FeatureSettings(s["half_life_matches"], s["shrinkage_matches"], s["season_carry_over"])
    except FileNotFoundError:
        return config.FeatureSettings()


def _holdout_losses(matches: pd.DataFrame, settings: config.FeatureSettings, cutoff: pd.Timestamp,
                    burn_in: str) -> np.ndarray:
    feats = FeatureBuilder(settings).build(matches)
    feats = feats[feats["season"] != burn_in]
    train, test = feats[feats["date"] < cutoff], feats[feats["date"] >= cutoff]
    preds = HalfTimePredictor().fit(train).predict(test)
    losses = []
    for market, out in preds.items():
        y = test["y_h1" if market == "H1_O05" else "y_h2"].to_numpy()
        p = np.clip(out["probabilite"].to_numpy(), 1e-6, 1 - 1e-6)
        losses.append(-(y * np.log(p) + (1 - y) * np.log(1 - p)))
    return np.concatenate(losses)


def paired_bootstrap(diff: np.ndarray, n_boot: int = 2000, seed: int = 0) -> dict:
    """diff = perte(candidat) - perte(production) par match. Négatif = candidat meilleur."""
    rng = np.random.default_rng(seed)
    means = np.array([rng.choice(diff, size=len(diff), replace=True).mean() for _ in range(n_boot)])
    return {"diff_moyenne": float(diff.mean()), "prob_candidat_meilleur": float((means < 0).mean()),
            "ic95": [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]}


def evolve(matches: pd.DataFrame, holdout_days: int = 120, n_candidates: int = 4,
           min_confidence: float = 0.95, seed: int = 0) -> dict:
    """Teste des configurations candidates contre la production sur une période récente."""
    cutoff = matches["date"].max() - pd.Timedelta(days=holdout_days)
    burn_in = sorted(matches["season"].unique())[0]
    current = production_settings()
    base_loss = _holdout_losses(matches, current, cutoff, burn_in)
    grid = [config.FeatureSettings(hl, sh, co) for hl in (6.0, 10.0, 15.0, 20.0)
            for sh in (3.0, 6.0, 10.0) for co in (0.3, 0.5, 0.8)]
    grid = [g for g in grid if asdict(g) != asdict(current)]
    random.Random(seed).shuffle(grid)
    results, best = [], None
    for cand in grid[:n_candidates]:
        stats = paired_bootstrap(_holdout_losses(matches, cand, cutoff, burn_in) - base_loss)
        stats["settings"] = asdict(cand)
        results.append(stats)
        if stats["prob_candidat_meilleur"] >= min_confidence and stats["diff_moyenne"] < 0:
            if best is None or stats["diff_moyenne"] < best["diff_moyenne"]:
                best = stats
    return {"cutoff": str(cutoff.date()), "production": asdict(current),
            "candidats": results, "promu": best}
