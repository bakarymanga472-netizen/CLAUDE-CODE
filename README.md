# Espace de travail pour agents IA (Claude Code)

Structure en 20 points pour qu'un agent ne reparte pas de zéro à chaque session.

## Arborescence
```
.                         ← 1. dossier principal
├── CLAUDE.md             ← point d'entrée chargé par Claude Code, importe le cerveau
├── cerveau/              ← 2. dossier cerveau
│   ├── CLAUDE.md         ← 3. règles + préférences, 4. routage des modèles
│   ├── contexte/         ← 5. business, offre, clients, voix, objectifs
│   ├── memoire/          ← 6. journal des sessions + 13. maintenant.md (court terme)
│   ├── index.md          ← 7. où tout se trouve
│   ├── tools.md          ← 8. apps connectées
│   └── regles-projets.md ← 15. les projets ne se mélangent pas
├── projets/<nom>/        ← 9. un dossier par projet, 10. contexte.md dans chacun
├── .claude/skills/       ← 16. skills
├── .claude/agents/       ← sous-agent léger utilisé par le routage (4)
├── workflows/            ← 17. procédures
├── scripts/              ← 18. tâches répétitives
├── .env.example          ← 19. modèle du fichier de secrets
└── .gitignore            ← 20. .env n'est jamais poussé
```
11. Obsidian : ouvre ce dossier comme coffre. 12. GitHub : ce dépôt. 14. Notion : connecteur pour les tâches.

## Démarrage
1. `git clone` ce dépôt, `cp .env.example .env`, remplis `.env`.
2. **Remplis les 5 fichiers de `cerveau/contexte/`.** Sans ça, le reste ne sert à rien.
3. Obsidian → « Ouvrir un dossier comme coffre » → ce dossier.
4. Notion : connecte Notion à Claude (connecteurs claude.ai ou `claude mcp add`).
5. `claude` dans ce dossier → `workflows/demarrer-session.md`.
6. Nouveau projet : `scripts/nouveau-projet.sh mon-projet`. Sauvegarde : `scripts/sauvegarde.sh "message"`.

## Écarts volontaires par rapport à la vidéo
- Claude Code ne charge pas automatiquement `cerveau/CLAUDE.md` si tu le lances depuis la racine. Un `CLAUDE.md` racine l'importe donc avec `@cerveau/CLAUDE.md`.
- Les skills ne sont détectés que dans `.claude/skills/<nom>/SKILL.md`, pas dans un dossier `skills/` quelconque.
- Un `CLAUDE.md` ne change pas de modèle tout seul. Le routage passe par un sous-agent (`.claude/agents/eclaireur.md`, `model: haiku`).
