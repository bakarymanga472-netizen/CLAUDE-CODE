---
type: procedure
statut: actif
maj: 2026-11-26
tags: [video, outil]
---

# Studio vidéo : quel outil pour quelle vidéo

Outils installés le 2026-11-26, d'après deux reels (achille.ia : « 9 skills gratuits », @melvynxdev : Lemo-Opuscar). Chaque dépôt a été relu avant installation : code, hooks, serveurs lancés et licence. Ils sont déclarés dans `.claude/settings.json`, et Claude Code propose de les installer à l'ouverture du coffre.

## Choisir
| Besoin | Outil | Remarques |
|---|---|---|
| Enquête, histoire, géopolitique, cartes, chiffres (notre format « Sous scellés ») | **Remotion** (notre code, `projets/videos-enquete`) | Le plus maîtrisé : vraies photos, nos voix, sous-titres calés |
| Film animé dans un style marqué (aquarelle, tableau blanc, dessin animé, documentaire…) | **Lemo-Opuscar** (99 styles) | 30 à 60 min par film ; demander du vertical ; voir [films-lemo-opuscar](films-lemo-opuscar.md) |
| Vidéo écrite en HTML (titres, cartes, données, « motion graphics ») | **HyperFrames** (HeyGen, 29 skills) | Rendu local gratuit en ligne de commande (`npx hyperframes`) ; le service en ligne de HeyGen est à part |
| Animations fluides dans du HTML ou du code | **GSAP** (8 skills officiels) | Complément de HyperFrames, Remotion et Lemo-Opuscar |
| Promo de produit à partir d'un site web | **video-shotcraft** (124 recettes de plans) | Remotion et captures réelles du site |
| Motion design « pro » (lancements, typographie animée) | **motionmaxxing** | Sans clé ElevenLabs : ni voix ni musique ; lui fournir notre narration |
| Jeux 3D dans le navigateur | **threejs-game-skills** (9 skills) | Hors vidéo ; utile pour un mini-jeu ou une scène 3D |
| 3D dans Blender | **blender-mcp** / **blender-skills** | **Désactivés** : il faut le logiciel Blender ouvert sur ton ordinateur (voir plus bas) |
| Studio complet piloté par l'agent (recherche, images IA, montage) | **OpenMontage** | Pas un plugin : une application à part (voir plus bas) |

## Nos règles s'appliquent à tous ces outils
- **Voix** : uniquement nos 4 voix ([voix-choisies](../.claude/skills/voix-off/voix-choisies.md)), choisies par Claude selon le sujet. Ne jamais utiliser la voix par défaut d'un outil (Kokoro, edge-tts, ElevenLabs inconnu).
- **Vraies photos** pour un sujet réel (skill `photos-reelles`), licences libres seulement, crédit à l'écran.
- **Format vertical 1080×1920** pour TikTok, **plus de 60 s** pour la monétisation, faits vérifiés et sourcés.

## Détails d'installation
- **Catalogue du coffre** `coffre-video` (`.claude-plugin/marketplace.json`) : video-shotcraft, motionmaxxing et threejs-game-skills, chacun **figé à la version relue** (commit). Rien n'est copié dans le coffre : video-shotcraft pèse 85 Mo, à cause de ses modèles et de ses sons. Pour passer à une version plus récente, relire le dépôt puis changer le `sha`. Ce catalogue est lu sur la branche principale du dépôt : il ne marche qu'une fois la PR fusionnée.
- **Blender** :
  - **blender-mcp** permet à Claude de piloter Blender en direct. Il faut Blender ouvert avec l'extension du dépôt. Il envoie par défaut des statistiques d'usage anonymes à son auteur : mettre `DISABLE_TELEMETRY=true` avant de l'activer.
  - **blender-skills** contient 188 skills, ce qui encombre le contexte de chaque session. Son serveur MCP est écrit pour Windows (`cmd /c`).
  - Pour les activer sur ton ordinateur : `/plugin`, puis les cocher.
- **OpenMontage** (licence AGPL) : `git clone https://github.com/OpenMontageInc/OpenMontage`, puis suivre son README (environnement Python), puis ouvrir Claude Code dans ce dossier. Il fonctionne sans clé en mode « open source », mais ses meilleures fonctions demandent des clés payantes (Kling, ElevenLabs, OpenAI…). Les vidéos produites ne sont pas concernées par l'AGPL.
- **Remotion** : déjà installé depuis le début (`.claude/skills/remotion-best-practices`).

## Les « 50 générateurs vidéo IA gratuits »
Ce ne sont ni des skills ni des MCP, mais des sites web : Kling, Runway, Pika, CapCut, Veo, Hailuo… Leur « gratuit » veut dire quelques crédits d'essai. Plusieurs sont déjà accessibles via Higgsfield (Kling, Seedance, Wan, Hailuo), avec des crédits payants. Les modèles libres de la liste (Wan, Hunyuan, LTX, CogVideoX, Open-Sora, AnimateDiff) demandent une carte graphique (GPU), qu'on n'a pas en session cloud. La consigne « commente LINK » est une technique pour gonfler l'engagement, pas une liste cachée.

## « Payant contre gratuit » (reel ai.praful, vérifié le 2026-11-26)
| Domaine | « Payant » | « Gratuit » annoncé | La réalité pour une vidéo monétisée |
|---|---|---|---|
| Design | Canva | Lovart AI | Canva a une offre gratuite et **est déjà connecté à Claude** (miniatures, couvertures). Lovart : 500 crédits pour les nouveaux comptes, et les conditions commerciales se contredisent selon les pages |
| Voix | ElevenLabs | « Voice Studio » | ElevenLabs gratuit : 10 000 crédits par mois, **usage non commercial seulement**, avec mention obligatoire. La première offre commerciale coûte environ 6 $ par mois. « Voice Studio » : plusieurs applications portent ce nom, impossible de savoir laquelle |
| Vidéo | Runway, Higgsfield | MiniMax H3, Hailuo | Hailuo gratuit = crédits d'essai, filigrane, 768p, sans droits commerciaux (source tierce, à confirmer sur hailuoai.video) |
| Image | Midjourney | Qwen Image | Qwen-Image d'origine : Apache 2.0, usage commercial permis, mais il faut une carte graphique (GPU) pour le faire tourner. Qwen-Image 2.1 : **non commercial**. Qwen Chat en ligne : conditions non confirmées |

Conclusion : nos voix restent les 4 choisies. Pour des voix payantes moins chères que les crédits Higgsfield, ElevenLabs Starter (environ 6 $ par mois, environ 30 000 caractères, soit environ 25 vidéos de 70 s) mérite d'être comparé, mais sans garantie de retrouver exactement les voix Brooks, Desmond et Nora.
