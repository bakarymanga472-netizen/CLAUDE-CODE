---
type: procedure
tags: [procedure, obsidian]
---

# Obsidian : installer, synchroniser, utiliser avec Claude

**Principe :** ce dépôt GitHub est ton coffre Obsidian. Obsidian l'affiche sur ton ordinateur, l'extension Obsidian Git le synchronise avec GitHub, et Claude Code (dans le cloud ou sur ton PC) lit et écrit les mêmes notes.

## 1. Récupérer le coffre sur ton ordinateur (une fois)
1. Installe Git : https://git-scm.com/downloads (sur Windows, garde les options par défaut).
2. Ouvre un terminal (Windows : « Git Bash ») et tape :
   `git clone https://github.com/bakarymanga472-netizen/CLAUDE-CODE.git`
   Le dossier `CLAUDE-CODE` est créé là où tu as lancé la commande (souvent `Documents`).
3. Si Git demande de se connecter à GitHub, accepte la fenêtre de connexion dans le navigateur.

## 2. L'ouvrir dans Obsidian
1. Obsidian → « Ouvrir un dossier comme coffre » → choisis le dossier `CLAUDE-CODE`.
2. Si Obsidian demande de faire confiance à l'auteur : oui (c'est ton propre dépôt).
3. Ouvre la note **Accueil** (elle est en favori). La vue **Projets** liste tes projets avec leur statut.

Déjà réglé dans le coffre : modèles (dossier `modeles/`), nouvelles notes dans `inbox/`, pièces jointes dans `pieces-jointes/`, dossiers techniques masqués (`node_modules`, rendus vidéo).

## 3. Synchronisation automatique avec Obsidian Git
1. Paramètres → Extensions de la communauté → Activer → Parcourir → cherche **Git** (auteur : Vinzent) → Installer → Activer.
2. Dans ses options :
   - « Pull on startup » (récupérer au démarrage) : activé
   - « Auto commit-and-sync interval » : 10 minutes
   - « Auto pull interval » : 10 minutes
3. Test : modifie une note, puis palette de commandes (Ctrl+P) → « Git: Commit-and-sync ». La modification doit apparaître sur GitHub.

## 4. Utiliser Claude avec le coffre
- **Claude Code dans le cloud (comme cette session) :** il travaille sur le dépôt GitHub. Ses notes arrivent dans ton Obsidian au prochain « pull », et les tiennes lui parviennent après ton « sync ».
- **Claude Code sur ton PC :** installe-le, puis lance `claude` dans le dossier `CLAUDE-CODE`. Il lit `CLAUDE.md` et travaille directement dans tes notes, sans délai de synchronisation.
- **Claude Desktop / app (optionnel) :** pour qu'une conversation lise ton coffre, ajoute un serveur MCP de fichiers pointé sur le dossier `CLAUDE-CODE`, ou partage le dossier dans Cowork (offre payante). Les serveurs MCP Obsidian sont communautaires : choisis le mode lecture seule si tu ne veux pas que l'IA écrive.
- **Session cloud qui accède directement à ton PC (optionnel) :** app Claude Desktop → Paramètres → Claude Code → Remote Control → ajoute le dossier `CLAUDE-CODE`.

## Au quotidien
- Une idée, un lien, une tâche : note rapide dans `inbox/` (Ctrl+N). Claude la trie à la session suivante.
- Une nouvelle vidéo : nouvelle note depuis le modèle **video** (palette → « Insérer un modèle »), dans `projets/<projet>/videos/`.
- Avant de fermer Obsidian : « Git: Commit-and-sync ».

## En cas de conflit Git
Si la même note est modifiée des deux côtés en même temps, Obsidian Git signale un conflit. Garde les deux versions dans la note, supprime les lignes `<<<<<<<`, `=======` et `>>>>>>>`, puis relance « Commit-and-sync ». Pour l'éviter : un « sync » avant et après chaque session avec Claude.
