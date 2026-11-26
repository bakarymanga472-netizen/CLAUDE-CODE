#!/usr/bin/env python3
"""Voix off gratuite en local avec Kokoro (kokoro-onnx), prête pour TikTok / YouTube.

Usage : python3 voix.py "Texte à dire" sortie.wav [--voix ff_siwis] [--langue fr-fr]
                        [--vitesse 0.9] [--timings phrases.json] [--brut]
Prérequis : pip install kokoro-onnx soundfile pyloudnorm pedalboard scipy
Les modèles (~350 Mo) sont téléchargés une fois dans ~/.cache/kokoro.

Réglages par défaut, mesurés le 2026-11-15 (voir SKILL.md) :
- une phrase à la fois (coupure après . ? !), pauses variables (0,3 à 0,5 s), débit qui varie de ±3 %
  (ne pas couper après « : » : un mot isolé comme « Trois : » est mal prononcé)
- vitesse 0,9 : 148 mots/min avec les pauses (cible 140-150 pour la vidéo courte)
- mastering : passe-haut 80 Hz, compression douce, légère réverbération, -14 LUFS, crête max -1,5 dBFS
"""
import argparse, json, math, pathlib, re, sys, urllib.request

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FICHIERS = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
CACHE = pathlib.Path.home() / ".cache" / "kokoro"
CIBLE_LUFS, CRETE_DB = -14.0, -1.5


def modeles():
    CACHE.mkdir(parents=True, exist_ok=True)
    for nom in FICHIERS:
        f = CACHE / nom
        if not f.exists():
            print(f"Téléchargement de {nom}…", file=sys.stderr)
            urllib.request.urlretrieve(BASE + nom, f)
    return [str(CACHE / n) for n in FICHIERS]


def mastering(y, sr):
    """Compresse, cale le volume sur -14 LUFS et limite les crêtes à -1,5 dBFS.

    Le volume est mesuré sur la version stéréo (le mono dupliqué sur deux canaux, comme dans la vidéo) :
    mesuré en mono, un fichier à -14 LUFS sort à -11 LUFS dans la vidéo (+3 dB)."""
    import numpy as np, pyloudnorm as pyln
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    from pedalboard import Compressor, HighpassFilter, Pedalboard, Reverb
    # compression douce (ratio 2) : une compression forte écrase les variations de volume naturelles
    # + une pointe de réverbération de petite pièce : une voix 100 % sèche sonne « synthétique »
    y = Pedalboard([HighpassFilter(80), Compressor(threshold_db=-20, ratio=2, attack_ms=10, release_ms=150),
                    Reverb(room_size=0.12, damping=0.6, wet_level=0.05, dry_level=1.0, width=0.6)])(
        y.astype(np.float32), sr).astype(np.float64)
    meter, lim = pyln.Meter(sr), 10 ** (CRETE_DB / 20)
    volume = lambda x: meter.integrated_loudness(np.stack([x, x], axis=1))
    fen = int(sr * 0.005)
    for _ in range(5):  # gain vers la cible, puis limiteur doux (anticipation 5 ms), en quelques passes
        y = y * 10 ** ((CIBLE_LUFS - volume(y)) / 20)
        g = np.minimum(1.0, lim / np.maximum(np.abs(y), 1e-9))
        g = uniform_filter1d(minimum_filter1d(g, 2 * fen + 1), 2 * fen + 1)
        y = y * np.minimum(g, 1.0)
        if abs(volume(y) - CIBLE_LUFS) < 0.3 and np.max(np.abs(y)) <= lim * 1.01:
            break
    pic = float(np.max(np.abs(y)))
    return (y * (lim / pic) if pic > lim else y).astype(np.float32)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("texte")
    p.add_argument("sortie")
    p.add_argument("--voix", default="ff_siwis")
    p.add_argument("--langue", default="fr-fr")
    p.add_argument("--vitesse", type=float, default=0.9)
    p.add_argument("--timings", help="écrit le début/fin de chaque phrase (s) pour caler les sous-titres")
    p.add_argument("--brut", action="store_true", help="sans pauses ajoutées ni mastering")
    p.add_argument("--prononcer", action="append", default=[], metavar="MOT=SON",
                   help="corrige un mot mal prononcé, ex. --prononcer Remotion=Rimôchone (répétable)")
    a = p.parse_args()
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(*modeles())
    regles = [r.split("=", 1) for r in a.prononcer]

    def prononce(s):  # ne change que l'audio : les sous-titres gardent l'orthographe d'origine
        for mot, son in regles:
            s = re.sub(rf"\b{re.escape(mot)}\b", son, s)
        return s

    if a.brut:
        y, sr = k.create(prononce(a.texte), voice=a.voix, speed=a.vitesse, lang=a.langue)
        sf.write(a.sortie, y, sr)
        print(f"{a.sortie} : {len(y) / sr:.1f} s")
        return

    phrases = [m.strip() for m in re.findall(r"[^.?!]+[.?!]?", a.texte) if m.strip()]
    morceaux, timings, t, sr = [], [], 0.0, 24000
    for i, ph in enumerate(phrases):
        # débit légèrement variable d'une phrase à l'autre (±3 %), questions un peu plus posées
        vit = a.vitesse * (1 + 0.03 * math.sin(1.7 * i)) * (0.97 if ph.endswith("?") else 1.0)
        audio, sr = k.create(prononce(ph), voice=a.voix, speed=vit, lang=a.langue)
        timings.append({"texte": ph, "debut": round(t, 3), "fin": round(t + len(audio) / sr, 3)})
        morceaux.append(audio)
        t += len(audio) / sr
        if i < len(phrases) - 1:
            # pauses irrégulières comme à l'oral : plus longues après une question ou avant une longue phrase
            pause = 0.5 if ph.endswith("?") else 0.26 + 0.012 * min(len(phrases[i + 1].split()), 12)
            morceaux.append(np.zeros(int(sr * pause), dtype=audio.dtype))
            t += pause
    y = mastering(np.concatenate(morceaux), sr)
    sf.write(a.sortie, y, sr)
    if a.timings:
        pathlib.Path(a.timings).write_text(json.dumps(timings, ensure_ascii=False, indent=1))
    print(f"{a.sortie} : {len(y) / sr:.1f} s, {len(phrases)} phrases")


if __name__ == "__main__":
    main()
