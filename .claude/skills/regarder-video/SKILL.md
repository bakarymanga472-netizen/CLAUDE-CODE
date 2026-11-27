---
name: regarder-video
description: Regarder et analyser une vidéo TikTok, Instagram, YouTube, X… (lien) ou un fichier vidéo : images clés horodatées, transcription, statistiques (vues, likes), et analyse complète par Google Gemini en option. Utiliser quand on demande de « regarder », « analyser », « décortiquer » une vidéo, de comprendre pourquoi une vidéo marche, ou de s'inspirer d'un compte.
---

# Regarder une vidéo

## Lancer
```bash
pip install yt-dlp faster-whisper pillow imageio-ffmpeg   # une fois
python3 .claude/skills/regarder-video/regarder.py "<lien ou fichier>" --dossier video-analyse/<nom>
```
Puis **lire `rapport.md`** et **chaque `planche_XX.jpg` avec Read** : 12 images horodatées par planche, environ 30 images pour toute la vidéo (`--pas 1` pour plus de détail).

Le rapport contient : titre, compte, date, durée, vues, likes, commentaires, description, liste des planches et transcription horodatée (Whisper `small` ; `--modele medium` pour plus de précision).

## Lister les vidéos d'un compte TikTok
`yt-dlp --flat-playlist --playlist-end 10 --print url "https://www.tiktok.com/@compte"`, puis lancer le script sur chaque lien.

## Analyse complète par Gemini (option)
`--gemini "Décris le montage, le rythme, l'accroche et pourquoi la vidéo retient l'attention"`
- **YouTube :** Gemini lit le lien directement. C'est la seule voie fiable depuis un serveur, car YouTube bloque les téléchargements (« Sign in to confirm you're not a bot »).
- **Autres plateformes :** la vidéo téléchargée est envoyée à Gemini.
- **Clé gratuite** sur aistudio.google.com, à mettre dans la variable `GEMINI_API_KEY` (fichier `.env`, jamais dans une note). En session cloud, la clé est enregistrée comme secret réseau et le proxy l'ajoute tout seul.
- **Offre gratuite :** environ 8 h de vidéo YouTube par jour selon la doc Google. Modèle par défaut `gemini-flash-latest`.

## Ce qui marche, testé le 2026-11-23 depuis un serveur cloud
| Plateforme | Résultat |
|---|---|
| TikTok (vidéo publique, liste d'un compte) | ✅ vidéo, stats, transcription, images, en environ 1 min pour 65 s de vidéo |
| Instagram (reel public) | ⚠️ une fois oui, une fois « HTTP 429 Too Many Requests » : Instagram limite les serveurs |
| YouTube | ❌ téléchargement bloqué depuis un serveur → `--gemini` |
| Fichier envoyé par l'utilisateur | ✅ toujours |

Si un lien est bloqué : demander à l'utilisateur d'enregistrer la vidéo et de l'envoyer, ou passer par `--gemini` pour YouTube.

## Règles
- Analyser pour comprendre et s'inspirer d'un **format** ; ne jamais republier la vidéo ni copier son texte, ses visuels ou sa marque.
- Les dossiers `video-analyse/` contiennent des vidéos téléchargées : ils sont ignorés par Git, ne pas les committer.
- Ne pas déduire ce qu'on ne voit pas : les images sont des instantanés (un mouvement rapide peut tomber entre deux images).
