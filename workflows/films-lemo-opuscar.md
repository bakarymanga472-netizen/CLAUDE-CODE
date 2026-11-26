---
type: procedure
statut: actif
maj: 2026-11-26
tags: [video, outil]
---

# Films animés avec Lemo-Opuscar

**Lemo-Opuscar** est un plugin gratuit pour Claude Code (dépôt `lemomo-ai/lemo-opuscar`, environ 20 000 étoiles). Il propose 99 styles de films faits entièrement en code : tableau blanc, aquarelle, dessin animé des années 50, documentaire, carte satellite, papier découpé… Claude écrit l'histoire, dessine, compose la musique, mixe le son et rend la vidéo image par image. Il n'y a pas de générateur vidéo payant.

- Galerie des styles : https://lemomo-ai.github.io/lemo-opuscar/
- Découvert via un reel de @melvynxdev (2026-11-26) ; vérifié et installé le même jour.

## Installation
- **Dans ce coffre**, c'est automatique : `.claude/settings.json` déclare la boutique `lemolab` et active `lemo-opuscar@lemolab`. Claude Code propose de l'installer à l'ouverture du dossier.
- **À la main**, dans un terminal : `claude plugin marketplace add lemomo-ai/lemo-opuscar` puis `claude plugin install lemo-opuscar@lemolab`.
- Au premier film, le skill télécharge sa bibliothèque dans `~/lemo-opuscar` et installe ses paquets (quelques minutes).
- **Prérequis** : Node 20+, Python 3.11+ et **ffmpeg 7 ou plus**. Avec ffmpeg 6, la normalisation du volume fausse la durée de l'audio et l'assemblage final échoue. Sur ton ordinateur, installe ffmpeg 7.
- **En session cloud**, le ffmpeg du système est en 6.1. Le ffmpeg 9 fourni avec `imageio-ffmpeg` (déjà installé pour nos outils) convient : mettre un lien `ffmpeg` vers lui dans un dossier, et ce dossier en tête du `PATH`, uniquement pour les commandes du skill. Testé le 2026-11-26 : le skill ne signale plus rien de manquant.

## Utilisation
Taper `/lemo-opuscar:lemo-opuscar`, ou demander en une phrase : « Fais un film de 70 s en style aquarelle sur … ». Le skill pose ses questions une seule fois, puis travaille 30 à 60 minutes et consomme beaucoup de jetons.

## Nos règles, à appliquer avec ce skill
- **Format TikTok** : demander explicitement du **vertical 1080×1920**. Par défaut, le skill sort du 1920×1080 horizontal.
- **Voix** : uniquement nos 4 voix ([voix-choisies](../.claude/skills/voix-off/voix-choisies.md)). Quand le skill demande si on a sa propre voix, répondre oui et lui fournir la narration générée avec la voix choisie. Ne pas utiliser sa voix par défaut (Kokoro, voix anglaise, le côté « robot » qu'on a écarté).
- **Vraies photos** : pour un sujet réel, chercher d'abord les photos libres (skill `photos-reelles`) et les fournir comme matériel.
- **Faits** : vérifiés et sourcés comme d'habitude (note vidéo dans le projet concerné).
- **Plus de 60 s** pour la monétisation TikTok.

## Licence (à respecter)
- Les films produits sont **à nous, y compris pour un usage commercial**, et sans crédit obligatoire. Le matériel tiers utilisé dedans (musiques, photos) garde sa propre licence.
- Le code est sous MIT, mais les guides et les fiches de style sont sous CC BY-NC 4.0. On peut les suivre et les adapter pour nos films, mais **pas les recopier dans ce dépôt, ni les partager ou les revendre**. C'est pour ça que le coffre déclare seulement le plugin, sans copie des fichiers.
- Trois styles (marqués ✦) exigent un générateur d'images qu'on n'a pas. Les autres fonctionnent sans.
