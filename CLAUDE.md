# Ce dossier est un coffre Obsidian

Le même dossier est ouvert dans Obsidian sur l'ordinateur de l'utilisateur et synchronisé par Git (extension Obsidian Git). Tout ce que tu écris ici apparaît dans son Obsidian après synchronisation.

## Démarrage
1. Lis `cerveau/memoire/maintenant.md`, puis seulement le `contexte.md` du projet concerné. `Accueil.md` liste tout.
2. Trie `inbox/` : chaque note part dans le bon projet ou devient une ligne de `maintenant.md`, puis est supprimée ou archivée.

## Écrire dans le coffre
- Notes en Markdown, en français, avec des propriétés YAML en tête (`type`, `statut`, `maj`, `tags`). Garde les propriétés des notes existantes à jour, en particulier `maj` et `prochaine_etape` des `contexte.md` : la vue `Projets.base` les affiche.
- Liens relatifs au format Markdown `[texte](chemin/note.md)` (lisibles dans Obsidian et sur GitHub).
- Nouvelle note : partir d'un modèle de `modeles/` (projet, vidéo, session, idée). Une vidéo = une note `projets/<projet>/videos/<titre>.md`.
- Images et fichiers joints : `pieces-jointes/`. Jamais de secret ni de clé dans une note (les secrets vont dans `.env`).

## Fin de session
- Réécris `cerveau/memoire/maintenant.md` (30 lignes max) et le `contexte.md` des projets touchés.
- Crée `cerveau/memoire/sessions/AAAA-MM-JJ-sujet.md` depuis `modeles/session.md`.
- Commit et push, pour que l'Obsidian de l'utilisateur se mette à jour.

## Posture
Réponses courtes, en français. Vérité avant confort : signale les erreurs et les angles morts, vérifie et cite tes sources. Ne présente jamais un résultat non testé comme réussi.
