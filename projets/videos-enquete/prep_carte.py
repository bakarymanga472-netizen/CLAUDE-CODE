"""Données de la carte d'Afrique : pays, frontières rectilignes (segments longs partagés par 2 pays), empires de 1914."""
import json, math, sys
from collections import defaultdict
g = json.load(open(sys.argv[1]))
AFRIQUE = "DZA AGO BEN BWA BFA BDI CMR CAF TCD COD COG CIV DJI EGY GNQ ERI SWZ ETH GAB GMB GHA GIN GNB KEN LSO LBR LBY MDG MWI MLI MRT MAR MOZ NAM NER NGA RWA SEN SLE SOM SOL ZAF SDS SDN TZA TGO TUN UGA SAH ZMB ZWE".split()
EMPIRE_1914 = {  # simplifié, sur les frontières actuelles
 "France": "DZA TUN MAR MRT SEN MLI BFA NER GIN CIV BEN TCD CAF COG GAB MDG DJI",
 "Royaume-Uni": "EGY SDN SDS UGA KEN ZAF BWA ZMB ZWE MWI NGA GHA SLE GMB LSO SWZ SOL",
 "Allemagne": "NAM TZA CMR TGO RWA BDI", "Belgique": "COD", "Portugal": "AGO MOZ GNB",
 "Italie": "LBY ERI SOM", "Espagne": "SAH GNQ", "Indépendant": "ETH LBR"}
INDEP_1960 = "CMR TGO MDG BEN NER BFA CIV TCD CAF COG GAB SEN MLI MRT NGA SOM SOL COD".split()
present = {f["properties"]["ADM0_A3"] for f in g["features"]}
manquants = [a for a in AFRIQUE if a not in present]
aretes = defaultdict(set)
for f in g["features"]:
    a3 = f["properties"]["ADM0_A3"]
    if a3 not in AFRIQUE: continue
    geo = f["geometry"]; polys = geo["coordinates"] if geo["type"] == "MultiPolygon" else [geo["coordinates"]]
    for poly in polys:
        for anneau in poly:
            for p, q in zip(anneau, anneau[1:]):
                cle = tuple(sorted([(round(p[0], 3), round(p[1], 3)), (round(q[0], 3), round(q[1], 3))]))
                aretes[cle].add(a3)
droites = [[list(k[0]), list(k[1])] for k, pays in aretes.items() if len(pays) == 2 and math.dist(k[0], k[1]) >= 2.5]
partagees = sum(math.dist(*k) for k, p in aretes.items() if len(p) == 2)
long_droites = sum(math.dist(*d) for d in droites)
empire = {a: e for e, l in EMPIRE_1914.items() for a in l.split()}
json.dump({"afrique": [a for a in AFRIQUE if a in present], "droites": droites, "empire": empire, "indep1960": INDEP_1960}, open(sys.argv[2], "w"))
print(f"{len(droites)} segments droits ≥ 2,5° ; {long_droites / partagees:.0%} de la longueur des frontières (carte simplifiée) ; manquants : {manquants}")
print("non classés 1914 :", [a for a in AFRIQUE if a in present and a not in empire])
