# Outils connectés

> Liste ce qui est réellement branché. Ne mets JAMAIS de clé ici — seulement le nom de la variable dans `.env`.

| Outil | Usage | Accès | Variable `.env` |
|---|---|---|---|
| GitHub | Versioning de ce dossier | git / MCP GitHub | — |
| Obsidian | Ce dépôt est le coffre : accueil, vue Projets, modèles, inbox | Ouvrir le dossier cloné + extension Obsidian Git (voir `workflows/obsidian.md`) | — |
| Notion | Tâches ouvertes par projet entre les sessions | Connecteur Notion (MCP) | `NOTION_TOKEN` (si API directe) |
| Higgsfield | Génération image/vidéo, Marketing Studio | Connecteur claude.ai « H » (MCP) | — |
| remotion-best-practices | Vidéos en code React, rendu local gratuit (skill officiel Remotion 4.0.543) | `.claude/skills/remotion-best-practices/` | — |
| voix-off | Voix off : **uniquement les 4 voix choisies** (5 Brooks, 12 Desmond, 14 Nora via ElevenLabs/Higgsfield, payantes ; 15 SIWIS gratuite), voir `voix-choisies.md` (skill) | `.claude/skills/voix-off/` | crédits Higgsfield pour 5, 12, 14 |
| photos-reelles | Vraies photos réutilisables (Openverse + Wikimedia Commons, licences libres seulement), planche de vérification, crédits automatiques (skill) | `.claude/skills/photos-reelles/` | — |
| lemo-opuscar | Films animés dans 99 styles faits en code (tableau blanc, aquarelle, documentaire…), plugin gratuit ; règles maison dans `workflows/films-lemo-opuscar.md` | `.claude/settings.json` (plugin) | ffmpeg 7+ |
| studio vidéo | HyperFrames, GSAP, video-shotcraft, motionmaxxing, threejs-game-skills, blender-mcp, blender-skills : **désactivés** le 2026-11-27 (réactivables avec `/plugin`) ; OpenMontage (application à part). Quel outil pour quelle vidéo : `workflows/studio-video.md` | `.claude/settings.json` + `.claude-plugin/marketplace.json` | selon l'outil |
| image-qwen | Images d'illustration gratuites (Qwen-Image, Apache 2.0) via la démo Hugging Face ; jamais de fausse photo de personne réelle (skill) | `.claude/skills/image-qwen/` | `HF_TOKEN` (compte Hugging Face gratuit) |
| regarder-video | Regarder une vidéo TikTok / Instagram / YouTube / fichier : images, transcription, stats ; Gemini en option (skill) | `.claude/skills/regarder-video/` | `GEMINI_API_KEY` (option) |
| _ajoute ici_ | | | |

## Ménage du 2026-11-27 (fait)
- **Supprimés du coffre** : skills `higgsfield-motion-design` et `higgsfield-marketing-studio`, jamais servis (récupérables dans l'historique Git). Le connecteur Higgsfield « H » reste.
- **Désactivés dans `.claude/settings.json`** : les 27 plugins synchronisés depuis le compte claude.ai (vente, Unity, juridique, RH, finance…) et 5 plugins vidéo (HyperFrames, GSAP, video-shotcraft, motionmaxxing, threejs). Restent actifs : Lemo-Opuscar et `security-guidance` (relecture de sécurité du code, officiel Anthropic, aucun skill).
- **Bloqués** (`permissions.deny`) : 29 connecteurs claude.ai jamais servis, dont Gmail, Google Drive, Agenda, Docusign, Shopify, Vercel, Supabase, Health Data Avatar. Testé : un outil bloqué est refusé et disparaît de la liste.
- **Restent** : H (Higgsfield), GitHub, Canva, Exa, DeepL, Notion, Claude Docs, TEXT_TO_QUANT et Gemini (bot-trading).
- **Limite** : ces réglages valent quand Claude Code est ouvert **dans le dossier du coffre** (ton ordinateur). Les sessions cloud démarrent un dossier plus haut et ne les lisent pas. Le vrai ménage, valable partout (claude.ai, appli, cloud), se fait dans ton compte : https://claude.ai/customize/connectors (connecteurs) et la page des plugins du compte.

## Inventaire complet (2026-11-27)
Environ 290 skills et 90 serveurs MCP sont chargés à chaque session. Une quinzaine servent les projets en cours ; le reste encombre chaque session et donne des droits d'écriture inutiles (Gmail, Drive, Docusign, Shopify, Vercel, Supabase…).

| Bloc | Nombre | Origine | Utilisé dans nos projets |
|---|---|---|---|
| Skills du coffre | 7 | `.claude/skills/` | Oui : voix-off, photos-reelles, image-qwen, regarder-video, remotion ; Higgsfield (2) jamais servis |
| Plugins vidéo installés | 6 plugins, 29 skills | `.claude/settings.json` | Installés le 2026-11-26, pas encore servis en production (Remotion fait tout) |
| Skills intégrés (Claude Code et Anthropic) | ≈ 35 | Claude Code | Ponctuellement (pdf, xlsx, deep-research, artifact…) |
| Plugins synchronisés depuis le compte claude.ai | 28 plugins, ≈ 226 skills | Compte (sales 36, unity 33, eodhd 13, ip-legal 12…) | **Aucun** |
| Connecteurs claude.ai connectés | ≈ 40 | claude.ai, Connecteurs | Utilisés : H (Higgsfield), GitHub ; testé : Canva ; le reste jamais servi |
| Serveurs MCP des plugins, sans connexion | ≈ 46 | Plugins du compte | Aucun (connexion jamais faite) |
| Serveurs MCP en panne | 4 | activecampaign, hubspot, definite, github (plugin engineering) | — |

**À garder** : H (Higgsfield), GitHub, Canva, Exa (recherche), DeepL (sous-titres traduits) ; pour `bot-trading` : TEXT_TO_QUANT (backtests, crypto seulement, payant au crédit) et Gemini (données de marché, lecture seule) ; Notion seulement s'il sert vraiment au suivi des tâches.
**À retirer** (jamais servis, sans rapport avec les projets) : les 28 plugins du compte, et les connecteurs Docusign, Jotform, Shopify, Supabase, Vercel, Lovable, Magic Patterns, Make, Linear, PostHog, Coupler.io, Supermetrics, Perspective AI, LlamaParse, Kiwi.com, SlidesGPT, Gamma, Website Generator B12, Play Sheet Music, Granola, Health Data Avatar (données de santé : à ne garder que par choix conscient).
**Où** : https://claude.ai/customize/connectors (connecteurs et plugins du compte). Claude ne peut pas les retirer lui-même.
