# Maintenant — mémoire court terme

_Dernière mise à jour : 2026-11-26 (vidéo « Journaliste depuis 10 ans », style anime)_

## En cours
- Configuration Claude remise à zéro (PR #13) : pas de réglages ni d'agents ; un `CLAUDE.md` court a été remis pour le coffre Obsidian (PR #15). Skills restants : `higgsfield-motion-design`, `higgsfield-marketing-studio`, `remotion-best-practices`, `voix-off`. Tout l'ancien reste récupérable dans l'historique Git.
- Production vidéo TikTok (Remotion + voix off) :
  - `projets/videos-metiers/` : n°1 « Infirmière à l'hôpital » (30 s) et n°2 « Journaliste depuis 10 ans » (72 s, style anime, scènes IA Z Image, voix 15), rendues, non publiées.
  - `projets/videos-geopolitique/` : vidéo n°1 « La Russie en Afrique » (47 s), rendue, non publiée.
  - `projets/videos-enquete/` : test « Qui a tracé les frontières de l'Afrique ? » (107 s, voix 15, 7 images d'archives), rendu, non publié.
  - `projets/videos-enquete/` : série « Sous scellés », partie 1 « Le sabotage du Rainbow Warrior » (65 s, voix 5 Brooks, vraies photos), rendue, non publiée. Partie 2 à écrire, même voix.
  - Photos : **toujours chercher de vraies photos** (skill `photos-reelles`, licences libres seulement, crédit à l'écran).
  - Voix : **uniquement les 4 voix choisies le 2026-11-25** : 5 Brooks, 12 Desmond, 14 Nora (ElevenLabs via Higgsfield, ~3 crédits par vidéo de 70 s) et 15 SIWIS (gratuite). Voir `.claude/skills/voix-off/voix-choisies.md`.
- `crm-chantiers` : V1 publiée (données d'exemple) → https://claude.ai/artifact/F99bQiFMm8nspVSJjXvpUE
- `bot-trading` : Aladdin en suivi papier depuis le 2026-10-14 (`python3 -m aladdin.live`). Les skills `trader-*` ont été supprimés de la config.

## Prochaines actions
- Obsidian installé (2026-11-21) : cloner le dépôt, l'ouvrir comme coffre, installer Obsidian Git (`workflows/obsidian.md`).
- Monétisation TikTok (Creator Rewards) : il faut des vidéos de **plus d'une minute**, 10 000 abonnés et 100 000 vues sur 30 jours (sources secondaires, novembre 2026). Les vidéos actuelles (30 s et 47 s) font de l'audience, pas de revenus : prévoir des versions de plus de 60 s.
- Publier : connecter TikTok (connecteur Higgsfield `tiktok_connect`, depuis claude.ai) ; publier en brouillon d'abord ; cocher « contenu généré par IA ».
- Enregistrer 15 s de sa propre voix → `voix_naturelle.py --reference` (voix unique et sans crédit à mettre).
- Nettoyer les connecteurs et plugins du compte claude.ai (garder « H » = Higgsfield) : https://claude.ai/customize/connectors
- Remplir les 5 fichiers de `cerveau/contexte/`.

## Bloqué / en attente
- Higgsfield : plan gratuit, environ 1 crédit restant (1,65 dépensé le 2026-11-26 pour 11 images Z Image à 0,15). Plus assez pour une voix payante : plan payant ou voix 15.
- Qwen-Image (Hugging Face, gratuit) : quota ZeroGPU de quelques images par jour, épuisé le 2026-11-26.
- Volume : avant le 2026-11-26, les vidéos sortaient à -11 LUFS au lieu de -14 (mono mesuré, stéréo joué). Corrigé dans `voix.py` et les scripts de mixage ; les vidéos déjà rendues sont à refaire au mixage avant publication.
- YouTube et TikTok bloquent la lecture automatique sans compte connecté : pas d'analyse directe des vidéos d'autres créateurs depuis le serveur.
