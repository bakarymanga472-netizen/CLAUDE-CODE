---
type: video
projet: videos-metiers
statut: rendue
plateforme: TikTok
duree_s: 72
monetisable: true
publiee_le:
vues:
tags: [video, metier, journalisme, anime]
---

# Vidéo : Journaliste depuis 10 ans, ce qu'on ne te dit jamais (style anime)

_Créée le 2026-11-26_. Statuts possibles : idée → script → voix → rendue → publiée.

## Principe
Récit à la première personne d'une journaliste **fictive** (Léa, la trentaine), avec des **chiffres réels** sur le métier en France. Format « métier » du projet, mais plus long (environ 65 s, monétisable) et en scènes d'anime. Mention permanente à l'écran : « Personnage fictif · chiffres réels · images IA ».

## Accroche (les 2 premières secondes)
« Dix ans de journalisme. » Lignes de vitesse façon manga, « 10 ANS » qui claque à l'écran, puis la bulle « Ce qu'on ne te dit jamais ».

## Script
Voir [texte-journaliste.txt](../texte-journaliste.txt) : 17 phrases, 168 mots. Fil conducteur : rêve du début → piges → les chiffres du métier (cartes, précarité, salaires) → horaires → l'enquête → la publication → la défiance → la réponse (montrer ses sources) → bilan → question en commentaire.

## Voix, images, son
- **Voix 15 (SIWIS, gratuite)**. La 12 (Desmond, récit touchant) aurait été la plus adaptée, mais il restait 2,65 crédits pour un besoin d'environ 3,3. La voix 15 est féminine, d'où une narratrice.
- **11 scènes d'anime** générées avec **Z Image** (Tongyi-MAI) via Higgsfield, 0,15 crédit par image, 1,65 crédit au total. Le quota gratuit de Qwen-Image (Hugging Face) était épuisé ce jour-là. Même description du personnage dans chaque image (carré noir, lunettes rondes écaille, trench beige, badge presse) : il reste reconnaissable d'une scène à l'autre. Aucune personne réelle n'est représentée. Les textes visibles dans certaines images (façade de journal, papiers) sont du faux texte d'IA.
- **Animation** : `src/Journaliste.tsx` (Remotion). Zoom lent et léger panoramique sur chaque image, flash blanc à chaque changement de scène, lignes de vitesse, pluie, étincelles, trame façon manga, chiffres qui « pop », bulles de BD, sous-titres mot à mot en police Bangers (OFL).
- **Son** : `mix_journaliste.py`. Musique lo-fi « anime » synthétisée (enchaînement IV-V-iii-vi, piano électrique, basse, batterie feutrée), qui s'assombrit sur la pige et la défiance. Bruitages synthétisés : impacts, swish, pops, appareils photo, pluie, notifications. Aucun fichier sonore externe, donc aucun droit à payer.

## Rendu (2026-11-26)
- 71,6 s, 1080×1920, 30 i/s, son à -14 LUFS (mesuré en stéréo), crête -2 dBFS. Commande : `npm run journaliste-rendu` (après `journaliste-voix`, `journaliste-caler`, `journaliste-mixer`).
- Voix contrôlée par Whisper medium : « 35 000 », « 3 560 », « 1 951 », « CDD », « CDI » et « se disent » justes. Il a fallu dicter les nombres et les sigles en toutes lettres (`--prononcer`) : au premier passage, la voix disait « 370 euros » au lieu de « 3 560 ».
- Point faible : les cœurs « mercis » ne restent visibles qu'environ 0,8 s avant la scène suivante.

## Faits et sources
- **34 948 cartes de presse délivrées en 2024** (+1,46 %), dont environ 8 935 journalistes pigistes ou en CDD, soit 25,88 % de la profession : d'où « un sur quatre ». Bilan de la CCIJP relayé par [CB News](https://www.cbnews.fr/medias/ccijp-hausse-du-nombre-cartes-presse-delivrees-2024). Ordre de grandeur cohérent avec 2023 (34 444 cartes, environ 25 % de pigistes et CDD), d'après l'[Écho du mardi](https://echodumardi.com/actualite/34-444-cartes-de-presse-attribuees-en-2023-par-la-ccijp). Réserve : une légende de CB News parle d'une « baisse de 5,38 % » sans dire de quoi.
- **Salaire médian brut mensuel en 2023 : 3 560 € en CDI, 1 951 € pour les pigistes** (Afdas, mars 2025), d'après [L'Essentiel de l'éco](https://lessentieldeleco.fr/4518-bfmtv-combien-gagne-un-journaliste/) (article du 2 décembre 2025, relu le 2026-11-26). ⚠ **Une seule source secondaire** : le rapport Afdas lui-même n'a pas été trouvé. L'article attribue explicitement 3 560 € à « AFDAS, mars 2025 », chiffres 2023. Pour 1 951 €, il ne cite ni la source ni l'année : c'est très probablement la même étude, mais ce n'est pas écrit. [Capitaine Study](https://www.capitainestudy.fr/metiers/salaire-journaliste/) donne des ordres de grandeur proches (environ 3 600 € en CDI, environ 2 000 € à la pige), mais sans source. D'autres sites donnent des médianes bien plus basses (France Travail : 2 438 € brut, tous statuts confondus) : les chiffres ne mesurent pas la même chose. L'écran indique « Afdas, 2023 (via L'Essentiel de l'éco) ».
- **61 % des Français disent se méfier de ce que disent les médias sur les grands sujets d'actualité** : 39e baromètre La Croix-Verian-La Poste, publié le 15 janvier 2026. Sources : [communiqué de presse (Press Club)](https://pressclub.fr/wp-content/uploads/2026/01/CP-39e-barometre-La-Croix-Verian-La-Poste.pdf), [The Media Leader](https://fr.themedialeader.com/barometre-la-croix-2026-les-francais-demandent-plus-de-transparence-et-dindependance-aux-medias/).
- **Récit personnel** (enquête de 4 mois, insultes et mercis, nuits et jours fériés) : fiction plausible, pas un fait. C'est pour ça que le personnage est présenté comme fictif.

## Avant de publier
- [x] Chiffres vérifiés et sources notées (réserve sur les salaires)
- [x] Plus de 60 s (71,6 s)
- [ ] « Contenu généré par IA » coché (images et voix)
- [ ] Crédits en description : « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 » ; « Images générées par IA (Z Image) » ; sources : CCIJP, Afdas, baromètre La Croix-Verian 2026
- [ ] Publié d'abord en brouillon

## Résultats (après 48 h et 7 jours)
- Vues :
- Rétention :
- À refaire / à changer :
