#!/usr/bin/env python3
"""Regarder une vidéo (lien TikTok / Instagram / YouTube / X… ou fichier local) pour pouvoir l'analyser.

Produit dans un dossier :
  - planche_XX.jpg : planches d'images (12 vignettes horodatées par planche) à LIRE avec l'outil Read ;
  - rapport.md     : infos de la vidéo, liste des planches, transcription horodatée, analyse Gemini (option).

Usage :
  python3 regarder.py <lien ou fichier> [--dossier DIR] [--pas 1.5] [--modele small]
                      [--gemini "question"] [--modele-gemini gemini-flash-latest]

--gemini : envoie la vidéo à Google Gemini (image + son) avec la question donnée.
  * YouTube : Gemini lit le lien directement (pas de téléchargement, contourne le blocage de YouTube).
  * Autres plateformes / fichiers : la vidéo téléchargée est envoyée à Gemini.
  Clé : variable GEMINI_API_KEY (clé gratuite sur aistudio.google.com). Dans une session cloud
  où la clé est enregistrée comme secret réseau, le proxy l'ajoute tout seul.

Prérequis : pip install yt-dlp faster-whisper pillow imageio-ffmpeg
"""
import argparse, json, os, pathlib, re, subprocess, sys, time, urllib.request

API = "https://generativelanguage.googleapis.com"


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def est_youtube(s):
    return bool(re.search(r"(youtube\.com|youtu\.be)/", s))


def telecharger(url, dossier):
    import yt_dlp
    opts = {"outtmpl": str(dossier / "video.%(ext)s"), "format": "bv*[height<=720]+ba/b[height<=720]/b",
            "merge_output_format": "mp4", "ffmpeg_location": ffmpeg(), "quiet": True, "no_warnings": True,
            "noplaylist": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    fichier = next(dossier.glob("video.*"))
    garder = ["title", "uploader", "channel", "upload_date", "duration", "view_count", "like_count",
              "comment_count", "description", "webpage_url"]
    return fichier, {k: info.get(k) for k in garder if info.get(k) not in (None, "")}


def duree(fichier):
    sortie = subprocess.run([ffmpeg(), "-i", str(fichier)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", sortie)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0


def planches(fichier, dossier, pas):
    from PIL import Image, ImageDraw
    images = dossier / "images"
    images.mkdir(exist_ok=True)
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", str(fichier), "-vf", f"fps=1/{pas},scale=360:-2",
                    str(images / "f_%04d.jpg")], check=True)
    vignettes = sorted(images.glob("f_*.jpg"))
    sorties = []
    for p in range(0, len(vignettes), 12):
        lot = [Image.open(v) for v in vignettes[p:p + 12]]
        w, h = lot[0].size
        planche = Image.new("RGB", (4 * w, 3 * h), "black")
        d = ImageDraw.Draw(planche)
        for k, im in enumerate(lot):
            x, y = (k % 4) * w, (k // 4) * h
            planche.paste(im, (x, y))
            t = (p + k) * pas
            d.rectangle([x, y, x + 92, y + 26], fill="black")
            d.text((x + 6, y + 6), f"{int(t // 60)}:{t % 60:04.1f}", fill="yellow")
        chemin = dossier / f"planche_{p // 12 + 1:02d}.jpg"
        planche.save(chemin, quality=85)
        sorties.append(chemin)
    return sorties


def transcrire(fichier, modele):
    import numpy as np
    from faster_whisper import WhisperModel
    brut = subprocess.run([ffmpeg(), "-v", "error", "-i", str(fichier), "-vn", "-ac", "1", "-ar", "16000",
                           "-f", "s16le", "-"], capture_output=True).stdout
    if not brut:
        return "", []
    audio = np.frombuffer(brut, np.int16).astype(np.float32) / 32768
    segs, info = WhisperModel(modele, device="cpu", compute_type="int8").transcribe(audio, beam_size=5)
    return info.language, [(s.start, s.end, s.text.strip()) for s in segs]


def requete(url, donnees=None, entetes=None, methode=None):
    cle = os.environ.get("GEMINI_API_KEY", "cle-injectee-par-le-proxy")
    h = {"x-goog-api-key": cle, **(entetes or {})}
    req = urllib.request.Request(url, data=donnees, headers=h, method=methode)
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.headers, r.read()


def gemini(source, fichier, question, modele):
    if est_youtube(source):
        partie = {"file_data": {"file_uri": source}}
    else:
        taille = fichier.stat().st_size
        h, _ = requete(f"{API}/upload/v1beta/files", json.dumps({"file": {"display_name": fichier.name}}).encode(),
                       {"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                        "X-Goog-Upload-Header-Content-Length": str(taille),
                        "X-Goog-Upload-Header-Content-Type": "video/mp4", "Content-Type": "application/json"})
        _, corps = requete(h["x-goog-upload-url"], fichier.read_bytes(),
                           {"X-Goog-Upload-Command": "upload, finalize", "X-Goog-Upload-Offset": "0"})
        f = json.loads(corps)["file"]
        for _ in range(60):  # la vidéo doit être traitée par Google avant usage
            if f.get("state") == "ACTIVE":
                break
            time.sleep(5)
            f = json.loads(requete(f"{API}/v1beta/{f['name']}")[1])
        partie = {"file_data": {"file_uri": f["uri"], "mime_type": "video/mp4"}}
    corps = {"contents": [{"parts": [partie, {"text": question}]}]}
    _, rep = requete(f"{API}/v1beta/models/{modele}:generateContent", json.dumps(corps).encode(),
                     {"Content-Type": "application/json"})
    rep = json.loads(rep)
    return "".join(p.get("text", "") for p in rep["candidates"][0]["content"]["parts"])


def hms(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("source")
    a.add_argument("--dossier")
    a.add_argument("--pas", type=float, help="secondes entre deux images (défaut : environ 24 à 36 images au total)")
    a.add_argument("--modele", default="small", help="modèle Whisper : tiny, base, small, medium")
    a.add_argument("--gemini", metavar="QUESTION", help="analyse complète par Google Gemini (image + son)")
    a.add_argument("--modele-gemini", default="gemini-flash-latest")
    o = a.parse_args()

    lien = o.source.startswith("http")
    nom = re.sub(r"[^\w-]+", "_", o.source.rstrip("/").split("/")[-1].split("?")[0])[:40] or "video"
    dossier = pathlib.Path(o.dossier or f"video-analyse/{nom}")
    dossier.mkdir(parents=True, exist_ok=True)
    infos, fichier, erreur = {}, None, None

    if lien:
        try:
            fichier, infos = telecharger(o.source, dossier)
        except Exception as e:
            erreur = str(e).splitlines()[0][:300]
            print(f"Téléchargement impossible : {erreur}", file=sys.stderr)
            if not (o.gemini and est_youtube(o.source)):
                print("→ Envoie le fichier vidéo à la place, ou pour YouTube utilise --gemini.", file=sys.stderr)
                sys.exit(2)
    else:
        fichier = pathlib.Path(o.source)

    lignes = [f"# Analyse vidéo : {infos.get('title', nom)}", "", f"Source : {o.source}", ""]
    if infos:
        lignes += ["## Infos"] + [f"- {k} : {str(v)[:300]}" for k, v in infos.items()] + [""]
    if fichier:
        d = duree(fichier)
        pas = o.pas or max(0.5, min(5.0, round(d / 30, 1))) if d else (o.pas or 1.5)
        pl = planches(fichier, dossier, pas)
        langue, segs = transcrire(fichier, o.modele)
        lignes += [f"Durée : {d:.1f} s · une image toutes les {pas} s · {len(pl)} planche(s)", "",
                   "## Planches (à lire avec Read, dans l'ordre)"] + [f"- {p}" for p in pl] + [""]
        lignes += [f"## Transcription (langue détectée : {langue or 'aucune voix'})"]
        lignes += [f"- [{hms(s)} → {hms(e)}] {t}" for s, e, t in segs] or ["- (pas de parole détectée)"]
        lignes.append("")
    elif erreur:
        lignes += [f"Téléchargement impossible ({erreur}) : analyse par Gemini seulement.", ""]
    if o.gemini:
        try:
            lignes += ["## Analyse Gemini", gemini(o.source, fichier, o.gemini, o.modele_gemini), ""]
        except Exception as e:
            lignes += ["## Analyse Gemini", f"Échec : {e}. Vérifie la clé GEMINI_API_KEY.", ""]
    rapport = dossier / "rapport.md"
    rapport.write_text("\n".join(lignes))
    print(rapport)


if __name__ == "__main__":
    main()
