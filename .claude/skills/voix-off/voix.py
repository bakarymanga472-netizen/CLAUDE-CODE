#!/usr/bin/env python3
"""Voix off gratuite en local avec Kokoro (kokoro-onnx).

Usage : python3 voix.py "Texte à dire" sortie.wav [--voix ff_siwis] [--langue fr-fr] [--vitesse 1.0]
Prérequis : pip install kokoro-onnx soundfile
Les modèles (~350 Mo) sont téléchargés une fois dans ~/.cache/kokoro.
"""
import argparse, pathlib, sys, urllib.request

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FICHIERS = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]
CACHE = pathlib.Path.home() / ".cache" / "kokoro"


def modeles():
    CACHE.mkdir(parents=True, exist_ok=True)
    for nom in FICHIERS:
        f = CACHE / nom
        if not f.exists():
            print(f"Téléchargement de {nom}…", file=sys.stderr)
            urllib.request.urlretrieve(BASE + nom, f)
    return [str(CACHE / n) for n in FICHIERS]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("texte")
    p.add_argument("sortie")
    p.add_argument("--voix", default="ff_siwis")
    p.add_argument("--langue", default="fr-fr")
    p.add_argument("--vitesse", type=float, default=1.0)
    a = p.parse_args()
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(*modeles())
    audio, sr = k.create(a.texte, voice=a.voix, speed=a.vitesse, lang=a.langue)
    sf.write(a.sortie, audio, sr)
    print(f"{a.sortie} : {len(audio) / sr:.1f} s")


if __name__ == "__main__":
    main()
