#!/usr/bin/env python3
"""Trouver et télécharger de VRAIES photos réutilisables (personnes, lieux, objets) pour une vidéo.

Sources : Openverse (Wikimedia Commons, Flickr, musées, archives, plus de 800 millions d'images) et l'API Wikimedia Commons.
Licences gardées : CC0, domaine public, CC BY, CC BY-SA. Écartées : NC (pas d'usage commercial,
or une vidéo monétisée est commerciale) et ND (pas de modification, or on recadre et on zoome).

  python3 photos.py chercher "Charles Hernu" "Rainbow Warrior 1985" --dossier photos-candidates
      → candidats.json + planche.jpg (vignettes numérotées) : LIRE la planche pour vérifier l'identité.
  python3 photos.py prendre photos-candidates 3 7 --vers public/photos
      → télécharge les numéros choisis et complète public/photos/CREDITS.md (auteur, licence, lien).
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

UA = {"User-Agent": "video-photo-research/1.0 (educational; contact via repository)"}
COMMONS = "https://commons.wikimedia.org/w/api.php"
OPENVERSE = "https://api.openverse.org/v1/images/"
LIBRES = re.compile(r"^(cc0|pdm|public domain|cc by(-sa)?( \d\.\d)?|by(-sa)?|attribution|pd.*)$", re.I)


def lire(url, essais=6, binaire=False):
    for k in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
                return data if binaire else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 503) or k == essais - 1:
                raise
            time.sleep(10 * (k + 1))  # les serveurs limitent : on patiente au lieu d'insister


def net(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def openverse(terme, n):
    q = urllib.parse.urlencode({"q": terme, "page_size": n, "license_type": "commercial,modification"})
    out = []
    for r in lire(f"{OPENVERSE}?{q}").get("results", []):
        lic = f"{r['license'].upper()} {r.get('license_version') or ''}".strip().replace("PDM", "Domaine public")
        out.append({"titre": r["title"], "source": r["source"], "auteur": r.get("creator") or "inconnu", "licence": lic,
                    "page": r.get("foreign_landing_url"), "fichier": r["url"], "vignette": f"{OPENVERSE}{r['id']}/thumb/",
                    "taille": f"{r.get('width')}x{r.get('height')}"})
    return out


def commons(terme, n):
    d = lire(f"{COMMONS}?" + urllib.parse.urlencode({"action": "query", "format": "json", "generator": "search", "gsrsearch": terme,
              "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 330}))
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        g = lambda k: net(m.get(k, {}).get("value"))
        lic = g("LicenseShortName")
        if not LIBRES.match(lic) or ii.get("width", 0) < 200:  # licence non libre, ou son/vidéo/document
            continue
        out.append({"titre": p["title"][5:], "source": "wikimedia", "auteur": g("Artist") or "inconnu", "licence": lic,
                    "page": ii["descriptionurl"], "fichier": ii["url"], "vignette": ii.get("thumburl"),
                    "taille": f"{ii['width']}x{ii['height']}", "date": g("DateTimeOriginal")[:20], "description": g("ImageDescription")[:200]})
    return out


def vignette_commons(url):
    """Vignette Wikimedia de taille standard (330 px), plus fiable que le relais d'Openverse."""
    if "upload.wikimedia.org" not in url or "/thumb/" in url:
        return None
    base, chemin = url.split("/commons/", 1)
    nom = chemin.rsplit("/", 1)[1]
    return f"{base}/commons/thumb/{chemin}/330px-{nom}" + (".jpg" if nom.lower().endswith((".tif", ".tiff", ".pdf")) else "")


def chercher(a):
    from PIL import Image, ImageDraw
    import io
    dossier = Path(a.dossier); dossier.mkdir(parents=True, exist_ok=True)
    cands, vus = [], set()
    for terme in a.termes:
        for f in (openverse, commons):
            try:
                for c in f(terme, a.n):
                    cle = c["page"] or c["fichier"]
                    if cle not in vus:
                        vus.add(cle); c["recherche"] = terme; cands.append(c)
            except Exception as e:
                print(f"  {f.__name__} indisponible pour « {terme} » : {e}", file=sys.stderr)
            time.sleep(1)
    vignettes = []
    for i, c in enumerate(cands, 1):
        im = None
        for url in (c["vignette"], vignette_commons(c["fichier"])):
            if not url or im is not None:
                continue
            try:
                im = Image.open(io.BytesIO(lire(url, essais=3, binaire=True))).convert("RGB")
            except Exception:
                pass
        if im is None:
            im = Image.new("RGB", (300, 300), "#333")
        im.thumbnail((300, 300)); case = Image.new("RGB", (300, 330), "black"); case.paste(im, ((300 - im.width) // 2, 28))
        ImageDraw.Draw(case).text((6, 6), f"{i} · {c['licence'][:14]} · {c['source'][:10]}", fill="yellow")
        vignettes.append(case)
        print(f"{i:3d}. [{c['recherche']}] {c['titre'][:60]} | {c['licence']} | {c['auteur'][:40]} | {c.get('date', '')}")
        time.sleep(0.5)
    if vignettes:
        cols = 6; lignes = (len(vignettes) + cols - 1) // cols
        planche = Image.new("RGB", (cols * 300, lignes * 330), "black")
        for i, v in enumerate(vignettes):
            planche.paste(v, ((i % cols) * 300, (i // cols) * 330))
        planche.save(dossier / "planche.jpg", quality=85)
    (dossier / "candidats.json").write_text(json.dumps(cands, ensure_ascii=False, indent=1))
    print(f"\n{len(cands)} candidats → {dossier}/planche.jpg (vérifier l'identité de chaque photo avant de la prendre)")


def prendre(a):
    cands = json.loads((Path(a.dossier) / "candidats.json").read_text())
    vers = Path(a.vers); vers.mkdir(parents=True, exist_ok=True)
    credits = vers / "CREDITS.md"
    if not credits.exists():
        credits.write_text("# Crédits des photos\n\n| Fichier | Sujet | Auteur | Licence | Source |\n|---|---|---|---|---|\n")
    for n in a.numeros:
        c = cands[n - 1]
        url = c["fichier"]
        if "upload.wikimedia.org" in url and "/thumb/" not in url:  # Wikimedia : taille de vignette standard (sinon refus 429)
            parts = url.split("/commons/")
            nom = url.rsplit("/", 1)[1]
            largeur = int(c["taille"].split("x")[0] or 0)
            if largeur > 1280:
                url = f"{parts[0]}/commons/thumb/{parts[1]}/1280px-{nom}" + (".jpg" if nom.lower().endswith((".tif", ".tiff")) else "")
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
        nom_local = re.sub(r"[^a-z0-9]+", "-", c["titre"].lower())[:50].strip("-") + ext
        (vers / nom_local).write_bytes(lire(url, binaire=True))
        with credits.open("a") as f:
            f.write(f"| {nom_local} | {c['titre'][:80]} | {c['auteur'][:60]} | {c['licence']} | {c['page']} |\n")
        print(f"ok {nom_local} ({c['licence']}, {c['auteur'][:40]})")
        time.sleep(3)


def main():
    a = argparse.ArgumentParser()
    s = a.add_subparsers(dest="cmd", required=True)
    c = s.add_parser("chercher"); c.add_argument("termes", nargs="+"); c.add_argument("--dossier", default="photos-candidates"); c.add_argument("-n", type=int, default=8)
    p = s.add_parser("prendre"); p.add_argument("dossier"); p.add_argument("numeros", nargs="+", type=int); p.add_argument("--vers", default="public/photos")
    o = a.parse_args()
    chercher(o) if o.cmd == "chercher" else prendre(o)


if __name__ == "__main__":
    main()
