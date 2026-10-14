# Plugins Claude Code

Source : reel de @hudsonbrendon (« 5 plugins »). Les 5 outils ont été vérifiés ; 3 sont installés.

## Installés

| Outil | Rôle | Où |
|---|---|---|
| **claude-code-setup** (officiel Anthropic) | Analyse le projet, recommande hooks, skills, sous-agents, MCP | `.claude/settings.json` |
| **claude-mem** (thedotmack) | Mémoire entre sessions (SQLite local, worker sur `localhost:37777`) | `.claude/settings.json` |
| **task-observer** (rebelytics, CC BY 4.0) | Note tes corrections, propose d'améliorer tes skills | `.claude/skills/task-observer/` |

**Dans ce dossier** : lance `claude`, fais confiance au dossier, accepte l'installation des plugins proposée.
**Sur ta machine pour tous tes projets** : `scripts/installer-plugins.sh` (ou `--headroom` pour ajouter Headroom).

### À savoir
- claude-mem consomme de l'usage (un modèle résume tes sessions). La synchro cloud cmem.ai est une option séparée : ne l'active pas pour des données clients. `<private>…</private>` exclut un passage de la mémoire.
- claude-mem recoupe `cerveau/memoire/` : garde `maintenant.md` pour les décisions, claude-mem pour le détail technique.
- task-observer écrit des fichiers d'observation dans le dossier. Relis ses propositions avant de les accepter.
- claude-code-setup : demande « recommande-moi des automatisations pour ce projet ». Il propose, tu choisis.

## Non installés

**OmniRoute** : envoie tes requêtes vers des fournisseurs gratuits inconnus quand ton quota est atteint. Ton code sort de chez toi, le modèle n'est plus Claude, les « 1,6 milliard de tokens » ne sont pas vérifiables et des critiques de sécurité existent. Refusé.

**Headroom** : proxy local de compression. Réel, mais un test indépendant sur de vraies sessions Claude Code mesure ~3,7 % d'économie. Optionnel via `scripts/installer-plugins.sh --headroom`, puis `headroom wrap claude`.
