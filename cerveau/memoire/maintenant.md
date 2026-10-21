# Maintenant — mémoire court terme

_Dernière mise à jour : 2026-10-15_

## En cours
- Espace de travail optimisé (architecture tokens) — à tester sur ta machine.
- `crm-chantiers` : V1 publiée (données d'exemple) → https://claude.ai/artifact/F99bQiFMm8nspVSJjXvpUE

- Skills `trader-*` (11, day-trader-fr @756e4f5) installés dans `.claude/skills/`, relus ; intégrité : `scripts/verifier-trader-skills.sh`. Ordres Alpaca toujours en confirmation (`ask`). État local `trader/` ignoré par Git.
- `bot-trading` : stratégie Équilibrée (STRATEGIE.md) retenue et mise de côté pour la démo (paper, clés Alpaca à fournir). Aladdin construit et testé ; suivi papier en direct démarré le 2026-10-14 (lancer `python3 -m aladdin.live` chaque jour).

## Prochaines actions
- Remplir les 5 fichiers de `cerveau/contexte/` (priorité n°1).
- Lancer `scripts/installer-plugins.sh` sur ta machine.
- Vérifier `/context` et `/usage` après une semaine.

## Bloqué / en attente
- (Résolu 2026-10-21 : push GitHub de nouveau OK.) PR #1 (branche `claude/instagram-video-uga8ko`) à merger dans `main` pour que skills et règles valent dans toutes les sessions.
