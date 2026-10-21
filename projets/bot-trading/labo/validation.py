"""Labo — validation : walk-forward, références aléatoires, Deflated Sharpe Ratio, PBO (CSCV), bootstrap apparié."""
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

N01 = NormalDist()
REGISTRE = Path(__file__).resolve().parent.parent / "registre"


def journalier(net):
    return (1 + net).groupby(net.index.normalize()).prod() - 1


def sharpe_annuel(r_jour):
    s = r_jour.std()
    if s == 0 or len(r_jour) < 3:
        return 0.0
    from .donnees import par_an
    return float(r_jour.mean() / s * np.sqrt(par_an(r_jour.index)))


# ---------- Walk-forward ----------
def walk_forward(series, annees, debut_hist):
    """series : {cle: rendements journaliers}. Chaque année Y, choisit la clé au meilleur Sharpe sur [debut_hist, Y-1]
    et l'applique sur Y. Renvoie (rendements hors échantillon concaténés, choix par année)."""
    morceaux, choix = [], {}
    for y in annees:
        fin_app = pd.Timestamp(f"{y - 1}-12-31")
        scores = {k: sharpe_annuel(s.loc[debut_hist:fin_app]) for k, s in series.items()}
        best = max(scores, key=scores.get)
        choix[y] = best
        morceaux.append(series[best].loc[f"{y}-01-01":f"{y}-12-31"])
    return pd.concat(morceaux), choix


# ---------- Exposition aléatoire de même profil ----------
def hasard(n, exposition, duree_moy, graine):
    """Expositions 0/1 aléatoires : durées de position et d'attente géométriques, calées pour avoir
    la même exposition moyenne et la même durée moyenne de position que la stratégie testée."""
    rng = np.random.default_rng(graine)
    duree_moy = max(duree_moy, 1.0)
    attente_moy = max(duree_moy * (1 - exposition) / max(exposition, 1e-9), 1.0)
    morceaux, total, etat = [], 0, int(rng.random() < exposition)
    while total < n:
        d = int(rng.geometric(1 / (duree_moy if etat else attente_moy)))
        morceaux.append(np.full(d, etat, dtype=float))
        total += d
        etat = 1 - etat
    return np.concatenate(morceaux)[:n]


# ---------- Deflated Sharpe Ratio (Bailey & López de Prado 2014) ----------
def sharpe_max_attendu(n_essais, var_sharpe):
    g = 0.5772156649
    if n_essais < 2:
        return 0.0
    return np.sqrt(var_sharpe) * ((1 - g) * N01.inv_cdf(1 - 1 / n_essais) + g * N01.inv_cdf(1 - 1 / (n_essais * np.e)))


def dsr(r, n_essais, var_sharpe_essais):
    """r : rendements (périodiques) de la stratégie retenue ; var_sharpe_essais : variance des Sharpe (même périodicité)
    de tous les essais. Renvoie la probabilité que le vrai Sharpe soit > au maximum attendu par hasard."""
    r = np.asarray(r, dtype=float)
    t = len(r)
    sr = r.mean() / r.std(ddof=1)
    sk = pd.Series(r).skew()
    ku = pd.Series(r).kurt() + 3
    sr0 = sharpe_max_attendu(n_essais, var_sharpe_essais)
    den = np.sqrt(max(1 - sk * sr + (ku - 1) / 4 * sr ** 2, 1e-12))
    return float(N01.cdf((sr - sr0) * np.sqrt(t - 1) / den)), float(sr0)


# ---------- Probability of Backtest Overfitting (CSCV) ----------
def pbo(matrice, blocs=10):
    """matrice : DataFrame (dates × variantes) de rendements. Renvoie la part des combinaisons où la meilleure variante
    en échantillon finit sous la médiane hors échantillon."""
    m = matrice.dropna()
    idx = np.array_split(np.arange(len(m)), blocs)
    lambdas = []
    for combo in itertools.combinations(range(blocs), blocs // 2):
        dedans = np.concatenate([idx[i] for i in combo])
        dehors = np.concatenate([idx[i] for i in range(blocs) if i not in combo])
        sd, so = m.iloc[dedans], m.iloc[dehors]
        s_in = sd.mean() / sd.std()
        s_out = so.mean() / so.std()
        best = s_in.idxmax()
        rang = (s_out < s_out[best]).sum() + 1
        w = rang / (len(s_out) + 1)
        lambdas.append(np.log(w / (1 - w)))
    lambdas = np.array(lambdas)
    return float((lambdas <= 0).mean())


# ---------- Bootstrap apparié par blocs ----------
def bootstrap_difference(a, b, bloc=20, n=1000, graine=0):
    """p-valeur unilatérale que Sharpe(a) ≤ Sharpe(b), bootstrap par blocs sur les mêmes jours."""
    df = pd.concat([a, b], axis=1).dropna().values
    t = len(df)
    rng = np.random.default_rng(graine)
    obs = []
    for _ in range(n):
        debuts = rng.integers(0, t - bloc, t // bloc + 1)
        ech = np.concatenate([df[d:d + bloc] for d in debuts])[:t]
        sa = ech[:, 0].mean() / ech[:, 0].std()
        sb = ech[:, 1].mean() / ech[:, 1].std()
        obs.append(sa - sb)
    return float((np.array(obs) <= 0).mean())


# ---------- Registre des expériences (ajout seul) ----------
def enregistrer_experience(instrument, cle, empreinte, resume):
    REGISTRE.mkdir(exist_ok=True)
    with open(REGISTRE / "experiences.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"date": datetime.now(timezone.utc).isoformat(timespec="seconds"), "instrument": instrument,
                            "experience": cle, "donnees": empreinte, **resume}, ensure_ascii=False) + "\n")


def nombre_experiences(instrument):
    """Nombre de configurations DISTINCTES jamais testées sur cet instrument (sert au DSR)."""
    f = REGISTRE / "experiences.jsonl"
    if not f.exists():
        return 0
    cles = {json.loads(l)["experience"] for l in f.read_text(encoding="utf-8").splitlines()
            if l.strip() and json.loads(l)["instrument"] == instrument}
    return len(cles)


def ouvrir_coffre(instrument):
    """Note la première ouverture du coffre. Renvoie (date de première ouverture, vierge?)."""
    REGISTRE.mkdir(exist_ok=True)
    f = REGISTRE / "coffre.json"
    etat = json.loads(f.read_text()) if f.exists() else {}
    if instrument in etat:
        return etat[instrument], False
    etat[instrument] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    f.write_text(json.dumps(etat, indent=2))
    return etat[instrument], True
