---
type: reference
statut: actif
maj: 2026-11-25
tags: [voix, video]
---

# Les 4 voix autorisées pour les vidéos

Choix de l'utilisateur le 2026-11-25, après un casting de 20 voix. **Pour toute vidéo, n'utiliser que ces 4 voix.** Si la demande ne précise pas laquelle, demander en une ligne : 5, 12, 14 ou 15.

| N° | Nom | Voix | Moteur | Prix | Extrait |
|---|---|---|---|---|---|
| 5 | Brooks | Homme, posé | ElevenLabs v4 Turbo via Higgsfield | payant | [écouter](exemples/05-brooks.mp3) |
| 12 | Desmond | Homme, doux | ElevenLabs v4 Turbo via Higgsfield | payant | [écouter](exemples/12-desmond.mp3) |
| 14 | Nora | Femme, conteuse | ElevenLabs v4 Turbo via Higgsfield | payant | [écouter](exemples/14-nora.mp3) |
| 15 | SIWIS | Femme, la voix de la 1re vidéo test | Chatterbox, sur le serveur (`voix_naturelle.py`) | gratuit | [écouter](exemples/15-siwis.mp3) |

## Voix 5, 12 et 14 (payantes)
Identifiants Higgsfield (outil `generate_audio`, modèle `elevenlabs_v4_turbo`, `voice_type: "preset"`) :
- 5 Brooks : `c2acff45-84b2-4974-892d-89fa2d4e5598`
- 12 Desmond : `563f728c-e249-5a85-97ab-8461e8c09da6`
- 14 Nora : `d081b915-6623-4a44-bacf-80d0f1c90a03`

Procédure :
1. Vérifier le solde (`balance`) et chiffrer avec `estimate_audio_cost`. Annoncer le prix avant de lancer. Repère mesuré le 2026-11-25 : environ 3,15 crédits pour 70 s de narration (1 000 caractères). Un appel coûte au moins 0,3 crédit, donc il faut **générer tout le texte en un seul appel**, pas une phrase par appel.
2. Générer : `params.dialogue = [{"text": "<texte complet>", "voice_type": "preset", "voice_id": "<id>"}]`. Le plan gratuit n'accepte qu'une génération à la fois.
3. Télécharger le MP3, puis caler les phrases et normaliser le volume :
   `python3 .claude/skills/voix-off/voix_externe.py narration.mp3 "$(cat texte.txt)" public/voix.wav --timings phrases.json`
   Le script affiche ce que Whisper a entendu phrase par phrase : relire avant le rendu. Pour un nom propre douteux, relancer avec `--modele medium` (le modèle small a déjà confondu « Prieur » et « Prier »).
4. Prononciation : pas d'option `--prononcer` ici. On écrit le mot phonétiquement dans le texte envoyé à ElevenLabs, et on garde l'orthographe normale dans `texte.txt` pour les sous-titres.

Lors du casting, ces voix ont parfaitement prononcé « 10 juillet 1985, port d'Auckland ». Ce sont des voix anglaises à l'origine qui parlent français : un léger accent reste possible sur certains mots.

## Voix 15 (gratuite)
`voix_naturelle.py` sans `--reference` : voix SIWIS par défaut, vérifiée phrase par phrase par Whisper. Crédit obligatoire en description : « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 ».

## Crédits Higgsfield
Plan gratuit : 10 crédits au départ, 5,8 restants le 2026-11-25 après le casting. Ça suffit pour une seule vidéo avec une voix payante. Ensuite, il faut un plan payant ou la voix 15.
