#!/usr/bin/env python3
"""Génère une image avec Qwen-Image (modèle Apache 2.0, usage commercial permis) via la démo officielle gratuite
hébergée sur Hugging Face (Space officiel « Qwen/Qwen-Image-2512 », licence Apache 2.0 ; repli sur « Qwen/Qwen-Image »).

Usage : python3 image_qwen.py "description en anglais" sortie.png [--format 9:16] [--graine 42] [--etapes 30]

Quota : gratuit mais limité (temps de calcul GPU « ZeroGPU »). Sans compte : quota du serveur, souvent à zéro.
Avec un compte Hugging Face gratuit : clé dans HF_TOKEN (fichier .env), ou enregistrée comme secret réseau
pour huggingface.co en session cloud (le proxy l'ajoute tout seul). Compter quelques images par jour.
Prérequis : pip install gradio_client
"""
import argparse, os, shutil, sys

def main():
    a = argparse.ArgumentParser()
    a.add_argument("prompt")
    a.add_argument("sortie")
    a.add_argument("--format", default="9:16", choices=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"])
    a.add_argument("--graine", type=int, default=42)
    a.add_argument("--etapes", type=int, default=30, help="30 suffit ; 50 = plus fin mais consomme plus de quota")
    o = a.parse_args()
    from gradio_client import Client
    jeton = os.environ.get("HF_TOKEN") or "hf_jeton-injecte-par-le-proxy"
    try:
        res = None
        # Qwen-Image-2512 d'abord (le Space « Qwen/Qwen-Image » renvoyait NameError le 2026-11-26)
        for space in ("Qwen/Qwen-Image-2512", "Qwen/Qwen-Image"):
            try:  # le paramètre s'appelle « token » dans les versions récentes de gradio_client, « hf_token » avant
                c = Client(space, token=jeton, verbose=False)
            except TypeError:
                c = Client(space, hf_token=jeton, verbose=False)
            try:
                res, graine = c.predict(o.prompt, o.graine, False, o.format, 4.0, o.etapes, False, api_name="/infer")
                break
            except Exception as e:
                if "ZeroGPU quota" in str(e):
                    raise
                print(f"{space} indisponible ({str(e)[:80]}), essai suivant…", file=sys.stderr)
        if res is None:
            sys.exit("Aucune démo Qwen-Image disponible pour l'instant.")
    except Exception as e:
        msg = str(e)
        if "ZeroGPU quota" in msg:
            sys.exit("Quota gratuit épuisé pour aujourd'hui (ou pas de clé Hugging Face). Réessayer plus tard, ou ajouter HF_TOKEN.")
        sys.exit(f"Échec : {msg[:300]}")
    src = res["path"] if isinstance(res, dict) else res
    try:  # la démo renvoie du WebP : on convertit vers le format demandé par l'extension (png, jpg, webp)
        from PIL import Image
        Image.open(src).convert("RGB").save(o.sortie)
    except ImportError:
        shutil.copy(src, o.sortie)
    print(f"{o.sortie} (graine {int(graine)}) · Qwen-Image, licence Apache 2.0")

if __name__ == "__main__":
    main()
