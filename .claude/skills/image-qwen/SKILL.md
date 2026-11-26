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
- **Gratuit mais limité** : quota de calcul quotidien. Sans compte, le quota du serveur est souvent à zéro. Avec le compte Hugging Face gratuit de l'utilisateur, compter quelques images par jour (environ 35 s par image en 9:16, 928×1664).
- **Clé** : sur ton ordinateur, dans `HF_TOKEN` (`.env`). En session cloud, elle est enregistrée comme secret réseau sur **trois adresses** : `huggingface.co`, puis `qwen-qwen-image-2512.hf.space` et `qwen-qwen-image.hf.space` (en-tête `x-hf-authorization`, préfixe Bearer). Lancer le script avec `HF_TOKEN=proxy-injected` ; le serveur remplace la valeur.
- **Démo utilisée** : `Qwen/Qwen-Image-2512` (Apache 2.0). Le 2026-11-26, la démo `Qwen/Qwen-Image` plantait (NameError) ; le script la garde en secours.

## Règles
- **Les vraies photos d'abord** (skill `photos-reelles`). Qwen ne sert que pour une illustration assumée : décor, ambiance, objet, carte stylisée.
- **Jamais une personne réelle ni un événement réel** présentés comme une photo, même « pour illustrer ». Une fausse photo dans une vidéo d'enquête détruit la crédibilité et peut être diffamatoire.
- **Les textes et les cartes sont faux** : testé le 2026-11-26, une « carte de l'Afrique » sort avec des frontières inventées et des inscriptions en charabia. Jamais d'image IA pour une carte, un chiffre, un document ou un fait. Demander « no text ».
- Marquer à l'écran « Illustration IA ». Licence du modèle : Apache 2.0, usage commercial permis. Ne pas utiliser Qwen-Image 2.1, réservé à un usage non commercial.
