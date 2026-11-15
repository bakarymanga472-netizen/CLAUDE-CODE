# Maintenant — mémoire court terme

_Dernière mise à jour : 2026-11-15_

## En cours
- Espace de travail optimisé (architecture tokens) — à tester sur ta machine.
- `crm-chantiers` : V1 publiée (données d'exemple) → https://claude.ai/artifact/F99bQiFMm8nspVSJjXvpUE

- 2026-11-15 : config remise à zéro (branche `claude/mcp-skills-config-zkmv53`) : skills `trader-*`, `objectif`, `fin-de-session`, `nouveau-projet`, `task-observer`, plugins claude-mem / claude-code-setup, hook de démarrage et `scripts/installer-plugins.sh` supprimés. Seuls skills : `higgsfield-motion-design`, `higgsfield-marketing-studio` (OSideMedia/higgsfield-ai-prompt-skill @6a6a5dd, MIT, relus). Puis remise à zéro complète : `CLAUDE.md`, `cerveau/CLAUDE.md`, `.claude/settings.json` (permissions comprises), agents, règles, `workflows/plugins.md` et `economie-tokens.md` supprimés. Ce fichier n'est plus chargé automatiquement. Tout est récupérable via l'historique Git.
- `bot-trading` : Aladdin construit et testé ; suivi papier en direct démarré le 2026-10-14 (lancer `python3 -m aladdin.live` chaque jour).

## Prochaines actions
- Remplir les 5 fichiers de `cerveau/contexte/` (priorité n°1).
- Vérifier `/context` et `/usage` après une semaine.

## Bloqué / en attente
- (Résolu 2026-10-21 : push GitHub de nouveau OK.) PR #1 (branche `claude/instagram-video-uga8ko`) à merger dans `main` pour que skills et règles valent dans toutes les sessions.
