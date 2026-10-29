# Index — où tout se trouve

| Chemin | Rôle |
|---|---|
| `CLAUDE.md` | Point d'entrée, importe le cerveau |
| `cerveau/CLAUDE.md` | Règles, préférences, routage des modèles |
| `cerveau/contexte/business.md` | Ton business |
| `cerveau/contexte/offre.md` | Ton offre |
| `cerveau/contexte/clients.md` | Tes clients |
| `cerveau/contexte/voix.md` | Ta voix / ton style |
| `cerveau/contexte/objectifs.md` | Tes objectifs |
| `cerveau/tools.md` | Apps et outils connectés |
| `cerveau/memoire/maintenant.md` | Mémoire court terme (en cours, prochaines actions) |
| `cerveau/memoire/sessions/` | Journal long terme, un fichier par session |
| `projets/<nom>/contexte.md` | État de chaque projet |
| `.claude/skills/` | Skills (chargés automatiquement par Claude Code) |
| `.claude/agents/` | Sous-agents : `eclaireur` (Haiku, recherche), `verificateur` (tests, logs) |
| `.claude/rules/projets.md` | Règles projets, chargées seulement dans `projets/` |
| `.claude/hooks/session-start.sh` | Injecte `maintenant.md` au démarrage |
| `workflows/economie-tokens.md` | Réflexes pour consommer moins |
| `workflows/` | Procédures pas-à-pas |
| `workflows/plugins.md` | Plugins installés et refusés (avec raisons) |
| `.claude/settings.json` | Plugins activés pour ce dossier |
| `scripts/` | Scripts pour tâches répétitives |
| `.env` | Secrets (jamais commité) |

## Projets actifs
<!-- Mis à jour par scripts/nouveau-projet.sh -->
- `projets/crm-chantiers/` — créé le 2026-10-14
- `projets/bot-trading/` — créé le 2026-10-15
- `projets/pronostiqueur/` — créé le 2026-10-29 (IA de prédiction des buts par mi-temps)
