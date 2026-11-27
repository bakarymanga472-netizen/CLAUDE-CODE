# Espace de travail Claude Code

Configuration Claude remise à zéro le 2026-11-15 : pas de `CLAUDE.md`, pas de réglages, pas d'agents, pas de hooks, pas de plugins.
L'ancienne configuration (cerveau, skills `trader-*`, agents…) reste récupérable dans l'historique Git.

## Obsidian
Ce dépôt est un coffre Obsidian : ouvre `Accueil.md`. Installation et synchronisation : `workflows/obsidian.md`. Claude Code suit `CLAUDE.md`.

## Ce qui reste
```
.
├── .claude/skills/
│   ├── image-qwen/                   ← images d'illustration gratuites (Qwen-Image)
│   ├── photos-reelles/               ← vraies photos libres, avec crédits
│   ├── regarder-video/               ← analyser une vidéo TikTok, Instagram, YouTube
│   ├── remotion-best-practices/      ← vidéos en code (React), rendu local gratuit
│   └── voix-off/                     ← voix off : les 4 voix choisies
├── cerveau/              ← notes et mémoire (données, plus chargées automatiquement)
├── projets/<nom>/        ← un dossier par projet, avec son contexte.md
├── workflows/            ← procédures
├── scripts/              ← tâches répétitives
├── .env.example          ← modèle du fichier de secrets
└── .gitignore            ← .env n'est jamais poussé
```

## Skills Higgsfield
- Source : [OSideMedia/higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill) @ `6a6a5dd`, licence MIT.
- Ils ont besoin du connecteur Higgsfield (« H ») sur claude.ai pour générer images et vidéos. Chaque génération consomme des crédits.

## Skill Remotion
- Source : [remotion-dev/skills](https://github.com/remotion-dev/skills) @ `7e541aa` (v4.0.543).
- Gratuit pour un particulier ou une structure de 3 personnes max ; au-delà, licence entreprise.
- Rendu testé : `npx remotion render src/index.ts <Composition> out/video.mp4 --is-production=false`.
