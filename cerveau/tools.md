# Outils connectés

> Liste ce qui est réellement branché. Ne mets JAMAIS de clé ici — seulement le nom de la variable dans `.env`.

| Outil | Usage | Accès | Variable `.env` |
|---|---|---|---|
| GitHub | Versioning de ce dossier | git / MCP GitHub | — |
| Obsidian | Ce dépôt est le coffre : accueil, vue Projets, modèles, inbox | Ouvrir le dossier cloné + extension Obsidian Git (voir `workflows/obsidian.md`) | — |
| Notion | Tâches ouvertes par projet entre les sessions | Connecteur Notion (MCP) | `NOTION_TOKEN` (si API directe) |
| Higgsfield | Génération image/vidéo, Marketing Studio | Connecteur claude.ai « H » (MCP) | — |
| higgsfield-motion-design | Motion design / pub animée : brief → storyboard → vidéo (skill) | `.claude/skills/higgsfield-motion-design/` | — |
| higgsfield-marketing-studio | Pubs vidéo Marketing Studio, 9 presets (skill) | `.claude/skills/higgsfield-marketing-studio/` | — |
| remotion-best-practices | Vidéos en code React, rendu local gratuit (skill officiel Remotion 4.0.543) | `.claude/skills/remotion-best-practices/` | — |
| voix-off | Voix off : **uniquement les 4 voix choisies** (5 Brooks, 12 Desmond, 14 Nora via ElevenLabs/Higgsfield, payantes ; 15 SIWIS gratuite), voir `voix-choisies.md` (skill) | `.claude/skills/voix-off/` | crédits Higgsfield pour 5, 12, 14 |
| photos-reelles | Vraies photos réutilisables (Openverse + Wikimedia Commons, licences libres seulement), planche de vérification, crédits automatiques (skill) | `.claude/skills/photos-reelles/` | — |
| lemo-opuscar | Films animés dans 99 styles faits en code (tableau blanc, aquarelle, documentaire…), plugin gratuit ; règles maison dans `workflows/films-lemo-opuscar.md` | `.claude/settings.json` (plugin) | ffmpeg 7+ |
| studio vidéo | HyperFrames, GSAP, video-shotcraft, motionmaxxing, threejs-game-skills (actifs) ; blender-mcp et blender-skills (désactivés, Blender requis) ; OpenMontage (application à part). Quel outil pour quelle vidéo : `workflows/studio-video.md` | `.claude/settings.json` + `.claude-plugin/marketplace.json` | selon l'outil |
| regarder-video | Regarder une vidéo TikTok / Instagram / YouTube / fichier : images, transcription, stats ; Gemini en option (skill) | `.claude/skills/regarder-video/` | `GEMINI_API_KEY` (option) |
| _ajoute ici_ | | | |
