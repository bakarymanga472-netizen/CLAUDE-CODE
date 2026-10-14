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

## Installés à la demande (tu l'as voulu, contre mon avis pour OmniRoute)

Les deux s'installent avec `scripts/installer-plugins.sh` mais **ne changent pas ton Claude par défaut** : ils ne servent que si tu les lances.

**OmniRoute** (`npm install -g omniroute`) : passerelle locale vers des centaines de fournisseurs, avec bascule automatique quand un quota est atteint.
- Utilisation : `omniroute` (tableau de bord sur http://localhost:20128), connecte tes fournisseurs, puis `omniroute run claude`.
- Risques : ton code part chez les fournisseurs que tu connectes ; avec un fournisseur gratuit, ce n'est plus Claude qui répond ; les « 1,6 milliard de tokens gratuits » ne sont pas vérifiables. Les fonctions de type « TLS stealth » servent à se faire passer pour d'autres clients : faire passer un abonnement par là peut violer ses conditions d'utilisation et faire suspendre ton compte.
- Règle : jamais de projet client ni de secret via OmniRoute.

**Headroom** (`pipx install "headroom-ai[all]"`) : proxy local qui compresse les sorties d'outils.
- Utilisation : `headroom wrap claude`.
- Un test indépendant sur de vraies sessions Claude Code mesure ~3,7 % d'économie. Mesure toi-même avant de l'adopter.
