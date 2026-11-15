---
name: voix-off
description: Ajoute une voix off (synthèse vocale) à une vidéo, en français par défaut. Gratuit et local avec Kokoro, réglé pour TikTok/YouTube (débit, pauses, -14 LUFS) ; option payante via Higgsfield. Utiliser quand on demande une voix, une narration, un voice-over, « fais parler la vidéo », ou pour sonoriser une vidéo Remotion.
---

# Voix off

## Par défaut : Kokoro, gratuit et local
1. Installer une fois : `pip install kokoro-onnx soundfile pyloudnorm pedalboard scipy`
2. Générer :
   `python3 .claude/skills/voix-off/voix.py "Texte" public/voix.wav --timings src/phrases.json`
   - Voix française : `ff_siwis` (féminine, la seule voix FR de Kokoro). Anglais : `--langue en-us --voix af_heart`.
   - `--timings` écrit le début et la fin de chaque phrase : s'en servir pour caler les sous-titres.
   - Mot mal prononcé : `--prononcer "Mot=Son"` (change l'audio, pas les sous-titres).
   - `--brut` : sortie Kokoro sans pauses ajoutées ni mastering (déconseillé pour publier).
3. Dans Remotion (skill `remotion-best-practices`, `remotion-markup/voiceover.md`) :
   `npm i @remotion/media`, `import {Audio} from '@remotion/media'`, puis
   `<Sequence from={6}><Audio src={staticFile('voix.wav')} /></Sequence>` ;
   une `<Sequence>` par phrase de `phrases.json` pour les sous-titres ; `durationInFrames` = fin de la dernière phrase + 0,8 s.
4. Vérifier : `npx remotion ffprobe out/video.mp4` doit lister un flux `aac`.

## Écrire le texte pour la voix
- Phrases courtes, une idée par phrase : le script coupe après . ? ! et met 0,35 s de pause.
- Ne pas isoler un mot entre deux points (« Trois. ») : Kokoro le prononce mal. « Trois : Remotion monte… » est bien prononcé.
- Viser environ 145 mots par minute : 35 mots pour 15 s, 70 pour 30 s.

## Réglages mesurés (2026-11-15)
Même texte de 44 mots. Mesures : erreurs de transcription Whisper (`small`), débit, part de silences, variation de hauteur de la voix (écart-type en demi-tons), volume.

| Version | Erreurs | Mots/min | Pauses | Intonation | Volume |
|---|---|---|---|---|---|
| Kokoro brut, vitesse 1,0 | 4,5 % | 183 | 6 % | 2,58 | -20,2 LUFS |
| **Kokoro réglé (défaut du script)** | **2,3 %** | **148** | **16 %** | **3,03** | **-14,0 LUFS** |
| Voix humaine de référence (LibriVox) | – | 147 | 15 % | 3,19 | – |

Cibles : 140-150 mots/min pour une vidéo courte, -14 LUFS et crête ≤ -1 dBTP pour YouTube et TikTok (sources : blogs spécialisés ; TikTok ne publie pas de chiffre officiel).
Mesures objectives seulement : elles ne disent pas si le timbre plaît. Faire écouter avant de publier.

Écartés : Piper `fr_FR-mls` et `gilles` (30 à 73 % d'erreurs). Piper `fr_FR-siwis-medium` est bon sur les chiffres (0 % d'erreurs, 144 mots/min), mais moins bien classé en naturel dans les comparatifs publics. Il reste une option si Kokoro déplaît.
Licences : Kokoro-82M Apache 2.0, kokoro-onnx MIT.

## Si Kokoro ne suffit pas (voix masculine, plus de choix, clonage)
- Connecteur Higgsfield « H » : `generate_audio` avec `seed_audio` (voix via `list_voices`) ou `qwen_audio_tts` avec `language: "fr"`. Environ 0,4 crédit pour une phrase courte : toujours faire `get_cost: true` et vérifier `balance` avant.
- ElevenLabs : le plan gratuit interdit l'usage commercial ; il faut un plan payant pour des vidéos monétisées.
