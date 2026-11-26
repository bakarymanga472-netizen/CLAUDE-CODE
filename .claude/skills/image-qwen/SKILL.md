---
name: image-qwen
description: Générer gratuitement une image d'illustration (décor, ambiance, objet, scène fictive) avec Qwen-Image, modèle libre Apache 2.0 utilisable commercialement, via la démo officielle Hugging Face. Utiliser pour illustrer une vidéo quand il n'existe pas de vraie photo libre et qu'une illustration convient. Jamais pour représenter une personne réelle ou un événement réel comme s'il s'agissait d'une photo.
---

# Images gratuites avec Qwen-Image

## Lancer
```bash
pip install gradio_client   # une fois
python3 .claude/skills/image-qwen/image_qwen.py "Vintage watercolor map of Africa on a wooden desk" public/illus/carte.png --format 9:16
```
- Écrire la description en anglais (le modèle la comprend mieux). Format 9:16 pour TikTok.
- **Gratuit mais limité** : quota de calcul quotidien. Sans compte, le quota du serveur est souvent à zéro (testé le 2026-11-26 : 0 s restant). Avec un compte Hugging Face gratuit et une clé de lecture (huggingface.co, Settings, Access Tokens), compter quelques images par jour. La clé va dans `HF_TOKEN` (`.env`) ; en session cloud, enregistrée comme secret réseau pour `huggingface.co`.

## Règles
- **Les vraies photos d'abord** (skill `photos-reelles`). Qwen ne sert que pour une illustration assumée : décor, ambiance, objet, carte stylisée.
- **Jamais une personne réelle ni un événement réel** présentés comme une photo, même « pour illustrer ». Une fausse photo dans une vidéo d'enquête détruit la crédibilité et peut être diffamatoire.
- Marquer à l'écran « Illustration IA ». Licence du modèle : Apache 2.0, usage commercial permis. Ne pas utiliser Qwen-Image 2.1, réservé à un usage non commercial.
