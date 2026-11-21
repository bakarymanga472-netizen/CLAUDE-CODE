---
type: projet
statut: actif
domaine: vidéo
maj: 2026-11-21
prochaine_etape: "Choisir le métier suivant, publier, puis comparer vues et rétention avant d'en produire en série."
tags: [projet]
---

# Projet : videos-metiers

Vidéos TikTok de 30 s, format « un métier : salaire, horaires, avantages », inspiré du compte @francevsmonde1 (« Metiersansfiltre », 30,5 k abonnés, 21 vidéos au 2026-11-15). Visuel, nom et texte originaux : rien n'est copié de ce compte.

## Où on en est
- 2026-11-15 : vidéo n°1 « Infirmière à l'hôpital » rendue (30 s, 1080x1920, voix Kokoro à -14 LUFS). Chiffres 2026 croisés sur plusieurs sources secondaires (Salerya, Caducée, La Nasante) : début ≈ 1 700 € net avec la prime Ségur, fin jusqu'à ≈ 3 000 € net, nuits et dimanches +200 à 500 €/mois. Ce sont des estimations, signalées à l'écran.
- 2026-11-15 (v2) : voix jugée trop robotique → passage au mode naturel du skill voix-off (Chatterbox + voix SIWIS, vérifiée phrase par phrase, 0 % d'erreur). Créditer en description : « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 ».
- La liste des vidéos du compte d'inspiration n'est pas lisible sans compte TikTok connecté : le format a été déduit de la bio et de l'avatar.

## Refaire une vidéo
1. `npm install` (une fois).
2. Écrire `texte.txt` : 9 phrases d'environ 70 mots au total (≈ 28 s de voix). Une phrase = une carte.
3. `npm run voix` (mode naturel, ~30 s par phrase ; `npm run voix-rapide` pour un brouillon), puis modifier le tableau `SCENES` de `src/Metier.tsx` (une entrée par phrase, dans le même ordre).
4. Vérifier les chiffres avec au moins deux sources, puis `npm run rendu`.

## Monétisation
- TikTok Creator Rewards : vidéos de plus d'une minute, 10 000 abonnés, 100 000 vues sur 30 jours, compte personnel, 18 ans et plus (sources secondaires concordantes, novembre 2026 : timetopost.co, postlinkapp.com, shortsfast.com). Une vidéo de moins de 60 s ne rapporte rien via ce programme : viser 61 à 75 s pour les vidéos destinées à la monétisation.

## Prochaine étape
- Choisir le métier suivant, publier, puis comparer vues et rétention avant d'en produire en série.
