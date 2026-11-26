#!/usr/bin/env python3
"""Génère une image avec Qwen-Image (modèle Apache 2.0, usage commercial permis) via la démo officielle gratuite
hébergée sur Hugging Face (Space « Qwen/Qwen-Image »).

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
        c = Client("Qwen/Qwen-Image", hf_token=jeton, verbose=False)
        res, graine = c.predict(o.prompt, o.graine, False, o.format, 4.0, o.etapes, False, api_name="/infer")
    except Exception as e:
        msg = str(e)
        if "ZeroGPU quota" in msg:
            sys.exit("Quota gratuit épuisé pour aujourd'hui (ou pas de clé Hugging Face). Réessayer plus tard, ou ajouter HF_TOKEN.")
        sys.exit(f"Échec : {msg[:300]}")
    src = res["path"] if isinstance(res, dict) else res
    shutil.copy(src, o.sortie)
    print(f"{o.sortie} (graine {int(graine)}) · Qwen-Image, licence Apache 2.0")

if __name__ == "__main__":
    main()
