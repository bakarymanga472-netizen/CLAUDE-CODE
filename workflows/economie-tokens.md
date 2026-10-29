# Utilisation max, tokens au minimum

Ce que coûte une session : tout ce qui est dans le contexte est renvoyé à **chaque** message. Le levier n°1 est donc la taille du contexte, pas la longueur de tes prompts.

## Ce que l'architecture fait pour toi
| Mécanisme | Effet |
|---|---|
| `CLAUDE.md` + `cerveau/CLAUDE.md` courts (~30 lignes) | Peu de tokens chargés à chaque message |
| `.claude/rules/projets.md` avec `paths` | Les règles projets ne se chargent que quand Claude touche `projets/` |
| Hook `SessionStart` | `maintenant.md` arrive tout seul, sans que Claude doive le chercher |
| Modèle `opusplan` | Opus réfléchit en mode plan, Sonnet exécute (moins cher) |
| Sous-agents `eclaireur` (Haiku) et `verificateur` | Les sorties longues restent dans leur contexte ; seul le résumé revient |
| `skillOverrides` : task-observer à la demande | Sa skill de ~700 lignes ne se charge plus à chaque session |
| `permissions.deny` sur `.env` et `node_modules` | Ni secrets ni fichiers inutiles lus |

## Tes réflexes (c'est là que se joue 80 % de l'économie)
1. **Une tâche = une session.** Tâche différente → `/clear` (gratuit). `/rename` avant si tu veux la retrouver (`/resume`).
2. **Longue session sur la même tâche** → `/compact` (ce fichier dit quoi garder). Plus cher que `/clear` : il relit tout.
3. **Tâche floue ou grosse** → Shift+Tab jusqu'au mode plan. Tu valides le plan avant qu'il code : pas de travail à refaire.
4. **Prompts précis** : « corrige la fonction X dans `projets/crm/app.js` » plutôt que « améliore le projet ». Cite les fichiers avec `@chemin`.
5. **Mauvaise direction** → Échap tout de suite, `/rewind` pour revenir en arrière.
6. **Ne colle pas de gros logs** : demande au `verificateur` de les lire.
7. **Tâche simple** → `/effort low` ou `/model sonnet`. Problème dur → `/model opus`.
8. **Ne reviens pas après une longue pause sur une session énorme** : le cache a expiré, tout est retraité. Préfère `/clear` + `maintenant.md`.

## Mesurer (sinon tu optimises à l'aveugle)
- `/context` : ce qui occupe le contexte maintenant.
- `/usage` : consommation, et la part de chaque skill, plugin, sous-agent et serveur MCP.
- `/insights` : rapport sur tes habitudes et tes points de friction.
- `/mcp` : désactive les serveurs MCP que tu n'utilises pas.

## À surveiller
- **claude-mem** injecte aussi du contexte au démarrage : il fait doublon avec `maintenant.md`. Si `/usage` montre qu'il pèse lourd, désactive-le (`/plugin`).
- **task-observer** : lance `/task-observer` en fin de semaine sur une vraie session de travail, pas à chaque fois.
