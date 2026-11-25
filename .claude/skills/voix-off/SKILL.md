---
name: voix-off
description: Ajoute une voix off (synthèse vocale) à une vidéo, en français par défaut. Mode naturel (Chatterbox + vraie voix de référence, vérifié par transcription) pour publier ; mode rapide (Kokoro) pour les brouillons. Gratuit et local, réglé pour TikTok/YouTube (débit, pauses, -14 LUFS). Utiliser quand on demande une voix, une narration, un voice-over, « fais parler la vidéo », ou pour sonoriser une vidéo Remotion.
---

# Voix off

## Voix autorisées : 4 seulement
L'utilisateur a choisi 4 voix le 2026-11-25 : **5 Brooks, 12 Desmond, 14 Nora** (ElevenLabs via Higgsfield, payantes) et **15 SIWIS** (gratuite, mode naturel ci-dessous). N'en utiliser aucune autre. Claude choisit la plus adaptée au sujet (repères, identifiants, prix et procédure : [voix-choisies.md](voix-choisies.md)).

## Quel mode ?
- **Publier : mode naturel** (`voix_naturelle.py`), environ 30 s de calcul par phrase sur CPU.
- **Brouillon, test de rythme : mode rapide** (`voix.py`, Kokoro), en 1 s. Il sonne plus « robot » : la mélodie de la voix est plate.

## Mode naturel (recommandé)
1. Installer une fois (environ 4 Go avec les modèles) :
   `pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu`
   `pip install chatterbox-tts faster-whisper num2words remotezip pedalboard pyloudnorm soundfile`
2. Générer :
   `python3 .claude/skills/voix-off/voix_naturelle.py "Texte" public/voix.wav --timings src/phrases.json`
   - Chaque phrase est réécoutée par Whisper puis regénérée (4 essais max) si un mot est faux ou répété. Un ⚠ indique une phrase à reformuler.
   - La voix est accélérée sans changer sa hauteur, jusqu'à environ 145 mots/min (`--mots-min`).
   - `--energie 0.6` par défaut ; 0,7 pour un ton plus « TikTok », 0,5 pour un ton calme.
   - `--reference ma_voix.wav` : 10 à 20 s d'une voix à imiter. **Le mieux est ta propre voix** : elle est unique et tu en as les droits.
   - Sans référence, le script prend 4 phrases du corpus SIWIS (comédienne enregistrée pour la synthèse vocale). Licence CC BY 4.0 : mettre en description « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 ».
   - Interdit : cloner la voix d'un créateur, d'une célébrité ou de quelqu'un sans son accord écrit.
3. Remotion : voir plus bas.

## Mode rapide (Kokoro)
1. `pip install kokoro-onnx soundfile pyloudnorm pedalboard scipy`
2. `python3 .claude/skills/voix-off/voix.py "Texte" public/voix.wav --timings src/phrases.json`
   - Voix FR `ff_siwis` (la seule de Kokoro). `--prononcer "Mot=Son"` pour corriger un mot ; `--vitesse 0.9` par défaut.

## Dans Remotion (les deux modes)
`npm i @remotion/media`, `import {Audio} from '@remotion/media'`, `<Sequence from={6}><Audio src={staticFile('voix.wav')} /></Sequence>`, une `<Sequence>` par phrase de `phrases.json` ; `durationInFrames` = fin de la dernière phrase + 0,5 s. Vérifier avec `npx remotion ffprobe out/video.mp4` qu'il y a un flux `aac`.

## Écrire le texte pour la voix
- Phrases courtes, une idée par phrase (le script coupe après . ? !).
- Pas de mot isolé (« Trois. ») ; écrire les chiffres en lettres (« mille sept cents »).
- Si un passage est mal compris (⚠), reformuler plutôt qu'insister. Exemple : « sept heures et demie » devient « jusqu'à douze heures ».
- Viser 70 mots pour 30 s.

## Pourquoi : mesures du 2026-11-15
Références : 4 narrateurs humains LibriVox (domaine public) et les vrais enregistrements SIWIS. YouTube bloque le téléchargement depuis un serveur (« Sign in to confirm you're not a bot ») : pas de comparaison directe avec des vidéos YouTube.

| Indicateur (Praat) | Humains | Kokoro réglé | Naturel (Chatterbox + SIWIS) |
|---|---|---|---|
| Mélodie (écart-type, demi-tons) | 2,96 à 4,84 | **2,86 (plate)** | 3,96 |
| Étendue de la mélodie (demi-tons) | 9,6 à 14,6 | 9,8 | 13,1 |
| Micro-variations de la mélodie | 0,42 à 0,71 | 0,49 | 0,56 |
| Grain : shimmer (%) | 7,2 à 13,1 | 7,5 | 8,5 |
| Pauses irrégulières (CV) | 0,34 à 0,67 | 0,35 | 0,41 |
| Erreurs de transcription | – | 2 à 5 % | 0 % par phrase (vérifié) |

- **Cause de l'effet robot :** Kokoro aplatit la mélodie. La même comédienne, enregistrée en vrai, est à 3,45. Mélanger sa voix avec d'autres voix Kokoro ne change rien (2,43 à 2,50), c'est une limite du modèle.
- **Écartés :** Chatterbox sans voix de référence, qui répétait des phrases et s'est trompé de chiffre (« 1 600 € » au lieu de 1 700 €). Piper `fr_FR-mls` et `gilles`, avec 30 à 73 % d'erreurs.
- **Limite :** ce sont des mesures objectives. L'oreille reste juge.
- **Licences :** Chatterbox MIT (ajoute un filigrane audio inaudible), Kokoro Apache 2.0, SIWIS CC BY 4.0.

## Option payante
Connecteur Higgsfield « H » : `generate_audio` (`seed_audio`, voix via `list_voices`). Environ 3,1 crédits pour 30 s de texte : toujours faire `get_cost: true` et vérifier `balance` avant. ElevenLabs gratuit interdit l'usage commercial.
