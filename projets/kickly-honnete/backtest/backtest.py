"""Backtest walk-forward du modèle de Verdict contre les cotes de clôture (Pinnacle).
Chaque match n'est prédit qu'avec les matchs qui le précèdent. Aucune donnée du futur.
Les paramètres sont choisis sur les saisons 2020-21 à 2022-23, puis évalués une seule fois sur 2023-24 à 2025-26."""
import csv, math, pathlib, itertools, collections, datetime as dt, sys

D = pathlib.Path(__file__).parent / "data"
LIGUES = ["E0", "SP1", "I1", "D1", "F1"]
SAISONS = ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]
TRAIN = {"2021", "2122", "2223"}; TEST = {"2324", "2425", "2526"}

def fl(x):
    try: return float(x)
    except: return None

def charger(ligue):
    out = []
    for s in SAISONS:
        with open(D / f"{ligue}_{s}.csv", encoding="utf-8-sig", errors="replace") as f:
            for r in csv.DictReader(f):
                if not r.get("FTHG") or not r.get("Date"): continue
                d = r["Date"]; fmt = "%d/%m/%Y" if len(d.split("/")[-1]) == 4 else "%d/%m/%y"
                try: date = dt.datetime.strptime(d, fmt)
                except: continue
                o = [fl(r.get(k)) for k in ("PSCH", "PSCD", "PSCA")]
                if not all(o): o = [fl(r.get(k)) for k in ("AvgCH", "AvgCD", "AvgCA")]
                oa = [fl(r.get(k)) for k in ("AvgH", "AvgD", "AvgA")]   # cotes d'ouverture moyennes
                out.append(dict(s=s, date=date, h=r["HomeTeam"], a=r["AwayTeam"], gh=int(r["FTHG"]), ga=int(r["FTAG"]),
                                o=o if all(o) else None, oa=oa if all(oa) else None))
    out.sort(key=lambda m: m["date"]); return out

def pois(l, k): return math.exp(-l) * l**k / math.factorial(k)

def modele(hist, h, a, N, K, hf=1.08, af=0.93):
    """Même modèle que index.html : forces relatives sur les N derniers matchs, ramenées vers 1 par n/(n+K)."""
    recent = hist[-380:]
    base = sum(m["gh"] + m["ga"] for m in recent) / (2 * len(recent))
    def stat(t):
        gf = ga = n = 0
        for m in reversed(hist):
            if m["h"] == t: gf += m["gh"]; ga += m["ga"]; n += 1
            elif m["a"] == t: gf += m["ga"]; ga += m["gh"]; n += 1
            if n >= N: break
        return gf, ga, n
    def force(t):
        gf, ga, n = stat(t)
        if n == 0: return 1, 1
        w = n / (n + K)
        return 1 + (gf / n / base - 1) * w, 1 + (ga / n / base - 1) * w
    ah, dh = force(h); aa, da = force(a)
    lh, la = base * ah * da * hf, base * aa * dh * af
    H = D_ = V = 0
    for i in range(9):
        for j in range(9):
            q = pois(lh, i) * pois(la, j)
            if i > j: H += q
            elif i == j: D_ += q
            else: V += q
    t = H + D_ + V; return [H / t, D_ / t, V / t]

def devig(o):
    r = [1 / x for x in o]; s = sum(r); return [x / s for x in r]

def ll(p, y): return -math.log(max(p[y], 1e-9))
def brier(p, y): return sum((p[i] - (1 if i == y else 0))**2 for i in range(3))

def run(N, K, seasons, poids=0.6, avec_roi=False, ligues=LIGUES):
    """Retourne métriques du modèle, du marché et du mélange, et le ROI de paris à valeur."""
    acc = collections.defaultdict(list); paris = []
    for lg in ligues:
        ms = charger(lg)
        for i, m in enumerate(ms):
            if m["s"] not in seasons or not m["o"] or i < 380: continue
            y = 0 if m["gh"] > m["ga"] else 1 if m["gh"] == m["ga"] else 2
            pm = modele(ms[:i], m["h"], m["a"], N, K); pk = devig(m["o"])
            pb = [poids * pk[j] + (1 - poids) * pm[j] for j in range(3)]
            for nom, p in (("modele", pm), ("marche", pk), ("melange", pb)):
                acc[nom].append((ll(p, y), brier(p, y)))
            # paris à valeur : cotes d'ouverture moyennes, probabilité du mélange, avantage > 5 %
            if avec_roi and m["oa"]:
                for j in range(3):
                    if pb[j] * m["oa"][j] - 1 > 0.05: paris.append((m["oa"][j], 1 if y == j else 0))
    res = {k: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v), len(v)) for k, v in acc.items()}
    return res, paris

if __name__ == "__main__":
    print("== Choix des paramètres sur", sorted(TRAIN))
    best = None
    for N, K in itertools.product((8, 12, 20), (3, 6, 12)):
        r, _ = run(N, K, TRAIN)
        print(f"N={N:2d} K={K:2d}  logloss modèle {r['modele'][0]:.4f}  (marché {r['marche'][0]:.4f}  n={r['modele'][2]})")
        if best is None or r["modele"][0] < best[0]: best = (r["modele"][0], N, K)
    _, N, K = best
    print(f"\nParamètres retenus : N={N}, K={K}\n\n== Évaluation unique sur", sorted(TEST))
    for lg in LIGUES + ["TOUTES"]:
        r, _ = run(N, K, TEST, ligues=LIGUES if lg == "TOUTES" else [lg])
        print(f"{lg:6s} n={r['modele'][2]:5d} | logloss modèle {r['modele'][0]:.4f} marché {r['marche'][0]:.4f} mélange {r['melange'][0]:.4f} | Brier modèle {r['modele'][1]:.4f} marché {r['marche'][1]:.4f} mélange {r['melange'][1]:.4f}")
    print("\n== Poids du marché dans le mélange (TOUTES, test)")
    for w in (0.0, 0.3, 0.6, 0.8, 0.9, 1.0):
        r, _ = run(N, K, TEST, poids=w); print(f"poids marché {w:.1f}: logloss {r['melange'][0]:.4f}")
    r, paris = run(N, K, TEST, avec_roi=True)
    if paris:
        mise = len(paris); gain = sum(o - 1 if w else -1 for o, w in paris)
        print(f"\n== Paris à valeur (avantage>5 %, cotes d'ouverture moyennes, mise fixe 1) : {mise} paris, réussite {sum(w for _, w in paris)/mise:.1%}, ROI {gain/mise:+.1%}")
