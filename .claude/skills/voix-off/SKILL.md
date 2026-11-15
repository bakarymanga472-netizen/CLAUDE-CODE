---
name: voix-off
description: Ajoute une voix off (synthèse vocale) à une vidéo, en français par défaut. Gratuit et local avec Kokoro ; option payante via Higgsfield. Utiliser quand on demande une voix, une narration, un voice-over, « fais parler la vidéo », ou pour sonoriser une vidéo Remotion.
---

# Voix off

## Par défaut : Kokoro, gratuit et local
1. Installer une fois : `pip install kokoro-onnx soundfile`
2. Générer : `python3 .claude/skills/voix-off/voix.py "Texte" public/voix.wav`
   - Voix française : `ff_siwis` (féminine, la seule voix FR de Kokoro). Anglais : `--langue en-us --voix af_heart`.
   - `--vitesse 1.1` pour accélérer. Un fichier par phrase si la vidéo doit caler la voix sur des scènes.
3. Dans Remotion (skill `remotion-best-practices`, fichier `remotion-markup/voiceover.md`) :
   `import {Audio} from '@remotion/media'` (`npm i @remotion/media`), puis
   `<Sequence from={10}><Audio src={staticFile('voix.wav')} /></Sequence>`.
   Régler `durationInFrames` sur la durée de la voix (affichée par le script).
4. Vérifier qu'il y a bien du son : `npx remotion ffprobe out/video.mp4` doit lister un flux `aac`.

Testé le 2026-11-15 : 3,2 s de voix générées en 1 s sur CPU, vidéo 1080x1920 rendue avec la voix.
Licence : Kokoro-82M Apache 2.0 (usage commercial permis), kokoro-onnx MIT.

## Si la voix Kokoro ne suffit pas (plus de voix, voix masculine, clonage)
- Connecteur Higgsfield « H » : `generate_audio` avec `seed_audio` (voix via `list_voices`) ou `qwen_audio_tts` avec `language: "fr"`. Environ 0,4 crédit pour une phrase courte : toujours faire `get_cost: true` et vérifier `balance` avant.
- ElevenLabs : le plan gratuit n'autorise pas l'usage commercial ; il faut le plan payant pour des vidéos monétisées.
