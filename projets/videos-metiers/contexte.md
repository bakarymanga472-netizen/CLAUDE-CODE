# Projet : videos-metiers

Vidéos TikTok de 30 s, format « un métier : salaire, horaires, avantages », inspiré du compte @francevsmonde1 (« Metiersansfiltre », 30,5 k abonnés, 21 vidéos au 2026-11-15). Visuel, nom et texte originaux : rien n'est copié de ce compte.

## Où on en est
- 2026-11-15 : vidéo n°1 « Infirmière à l'hôpital » rendue (30 s, 1080x1920, voix Kokoro à -14 LUFS). Chiffres 2026 croisés sur plusieurs sources secondaires (Salerya, Caducée, La Nasante) : début ≈ 1 700 € net avec la prime Ségur, fin jusqu'à ≈ 3 000 € net, nuits et dimanches +200 à 500 €/mois. Ce sont des estimations, signalées à l'écran.
- La liste des vidéos du compte d'inspiration n'est pas lisible sans compte TikTok connecté : le format a été déduit de la bio et de l'avatar.

## Refaire une vidéo
1. `npm install` (une fois).
2. Écrire `texte.txt` : 9 phrases d'environ 70 mots au total (≈ 28 s de voix). Une phrase = une carte.
3. `npm run voix`, puis modifier le tableau `SCENES` de `src/Metier.tsx` (une entrée par phrase, dans le même ordre).
4. Vérifier les chiffres avec au moins deux sources, puis `npm run rendu`.

## Prochaine étape
- Choisir le métier suivant, publier, puis comparer vues et rétention avant d'en produire en série.
