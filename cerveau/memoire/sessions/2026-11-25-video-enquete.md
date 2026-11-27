---
type: session
date: "2026-11-25"
projets: [videos-enquete]
tags: [session]
---

# Session du 2026-11-25 : vidéo test format « dossier »

## Fait
- Analyse de la vidéo de référence (@dossierouge, « L'accord secret des autoroutes », 110 s, 177 000 vues) avec le skill regarder-video : écran central, étiquettes, documents caviardés, sous-titres mot à mot, fin en suspens.
- Vidéo test de 70 s « Le sabotage du Rainbow Warrior, partie 1 » : nouveau projet [videos-enquete](../../../projets/videos-enquete/contexte.md). Faits vérifiés (police néo-zélandaise, NZHistory, Universalis, CS Monitor, MercoPress).
- Démo de 9 styles de visuels (showreel, 33 s), restée dans le dossier temporaire et non versionnée.
- Voix : correctif de la coupe de « queue parasite » dans `voix_naturelle.py` (un nom transcrit en deux morceaux était coupé au milieu).

- Casting de 20 voix ; l'utilisateur en garde 4 (5, 12, 14, 15) et laisse Claude choisir. Rainbow Warrior refait en voix 5 avec de vraies photos.
- Skill `photos-reelles` (Openverse + Wikimedia, licences libres, planche de vérification, crédits) ; test « frontières de l'Afrique » (107 s).
- Voix : une phrase dont une année est mal entendue est désormais refusée (« 1854 » pour « 1884 » était passé).

## Décisions (et pourquoi)
- Sujet historique documenté, marque à nous (« SOUS SCELLÉS »), aucune image ni texte du compte de référence.
- Pas de photos de personnes réelles (droits) : silhouettes et noms.
- Pas de date d'arrestation (sources divergentes) ; l'ordre de Mitterrand est présenté comme la note Lacoste, pas comme un fait.
- Vérification de la voix : Whisper « small » s'est trompé sur « Prieur » (« Prier »), « medium » l'entend juste. Dans le doute, faire contre-vérifier un nom propre par « medium ».

## Fichiers modifiés
- `projets/videos-enquete/` (nouveau), `.claude/skills/voix-off/voix_naturelle.py`, `.gitignore`, `Accueil.md`, `cerveau/memoire/maintenant.md`.

## Prochaine étape
- L'utilisateur valide ou corrige la vidéo test ; ensuite, vérifier et écrire la partie 2 (la note Lacoste).
