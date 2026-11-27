---
type: session
date: "2026-11-26"
projets: [videos-metiers]
tags: [session]
---

# Session du 2026-11-26 : vidéo « Journaliste depuis 10 ans » (style anime)

## Fait
- Vidéo de 71,6 s, verticale, en scènes d'anime : récit d'une journaliste **fictive**, avec des **chiffres réels** (CCIJP 2024, Afdas 2023, baromètre La Croix-Verian 2026). Note : [journaliste-10-ans](../../../projets/videos-metiers/videos/journaliste-10-ans.md).
- 11 scènes générées par **Z Image** via Higgsfield (0,15 crédit l'image, 1,65 au total) : le quota gratuit de Qwen-Image était épuisé. Le personnage reste cohérent grâce à une description identique dans chaque image.
- Composition `src/Journaliste.tsx` : lignes de vitesse, flashs, pluie, étincelles, trame manga, chiffres qui « pop », bulles de BD, sous-titres mot à mot en police Bangers.
- Musique lo-fi « anime » et bruitages, entièrement synthétisés (`mix_journaliste.py`) : aucun droit à payer.
- Voix 15, contrôlée phrase par phrase par Whisper, puis réécoutée avec Whisper medium.

## Décisions (et pourquoi)
- **Voix 15** plutôt que la 12 (plus adaptée) : 2,65 crédits pour un besoin d'environ 3,3. Voix féminine, d'où une narratrice.
- **Personnage fictif annoncé à l'écran** (« Personnage fictif · chiffres réels · images IA ») : le récit personnel est inventé, seuls les chiffres sont des faits.
- **Source des salaires affichée telle quelle** (« Afdas, 2023, via L'Essentiel de l'éco ») : une seule source secondaire trouvée, l'écran ne doit pas prétendre mieux.

## Bugs trouvés et corrigés
- **Volume** : les vidéos sortaient à -11 LUFS au lieu de -14, avec des crêtes à +1,6 dBFS. Le mono était mesuré, mais la vidéo le joue en stéréo (+3 dB). Corrigé dans `voix.py` (mastering), `mix_afrique.py`, `mix_enquete.py` et `mix_journaliste.py`. **Les vidéos déjà rendues (infirmière, Russie, Rainbow Warrior, Afrique) sont trop fortes** : refaire leur mixage avant publication.
- **Contrôle des nombres** de `voix_naturelle.py` : il refusait « 35 000 » pour « trente-cinq mille ». Les nombres sont maintenant comparés en toutes lettres, et une date fausse (« 1854 » pour « 1884 ») reste refusée.
- **Relance identique** : le tirage aléatoire était fixe, donc relancer reproduisait les mêmes essais ratés. Nouvelle option `--graine`.
- **Nombres dits faux** : au premier passage, la voix disait « 370 euros » au lieu de « 3 560 ». Solution : dicter les nombres et les sigles en toutes lettres avec `--prononcer`.
- **Sous-titres** : `split()` coupait « 1 951 » en deux, car Python considère l'espace insécable comme une espace.

## Fichiers modifiés
- `projets/videos-metiers/` : `src/Journaliste.tsx`, `src/*-journaliste.json`, `src/Root.tsx`, `prep_journaliste.py`, `mix_journaliste.py`, `texte-journaliste.txt`, `public/journaliste/` (11 images et CREDITS.md), `public/fonts/`, `package.json`, `contexte.md`, `videos/journaliste-10-ans.md`.
- `.claude/skills/voix-off/voix_naturelle.py`, `.claude/skills/voix-off/voix.py`, `projets/videos-enquete/mix_afrique.py`, `projets/videos-enquete/mix_enquete.py`.

## Prochaine étape
- Publier en brouillon sur TikTok, cocher « contenu généré par IA », mettre les crédits en description (voir la note vidéo).
- Refaire le mixage des 4 vidéos précédentes (volume) avant de les publier.
- Vérifier dans les conditions d'utilisation de Higgsfield si les images de l'offre gratuite sont utilisables commercialement (le centre d'aide dit oui, des sites tiers disent non).
