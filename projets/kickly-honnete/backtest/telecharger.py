"""Télécharge les résultats + cotes de clôture depuis football-data.co.uk (gratuit)."""
import urllib.request, pathlib
LIGUES = ["E0", "SP1", "I1", "D1", "F1"]            # PL, Liga, Serie A, Bundesliga, Ligue 1
SAISONS = ["1920", "2021", "2122", "2223", "2324", "2425", "2526"]
d = pathlib.Path(__file__).parent / "data"
for s in SAISONS:
    for l in LIGUES:
        f = d / f"{l}_{s}.csv"
        if f.exists():
            continue
        try:
            raw = urllib.request.urlopen(f"https://www.football-data.co.uk/mmz4281/{s}/{l}.csv", timeout=30).read()
            f.write_bytes(raw)
            print("ok", f.name, len(raw))
        except Exception as e:
            print("echec", f.name, e)
