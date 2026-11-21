---
type: projet
statut: actif
domaine: vidéo
maj: 2026-11-21
prochaine_etape: "Publier, mesurer vues et rétention ; sujet suivant possible : la Chine en Afrique (même modèle)."
tags: [projet]
---

# Projet : videos-geopolitique

Vidéos TikTok verticales très animées : carte de l'Afrique (Natural Earth, domaine public), arcs depuis Moscou, zoom sur le Sahel, compteurs, graphiques. Voix : mode naturel du skill voix-off.

## Vidéo n°1 : « La Russie en Afrique : ce qui a vraiment changé » (47 s, 2026-11-15)
Faits utilisés, vérifiés sur des sources de 2026 :
- 3e sommet Russie-Afrique à Moscou, 28-29 octobre 2026 : 48 délégations, dont 22 chefs d'État (France 24, Africa News Agency).
- Africa Corps (ministère russe de la Défense) a remplacé Wagner ; présence au Mali, Burkina Faso, Niger, Centrafrique, Libye (FOI Suède 2026, Congrès américain/CRS). Revers signalés au Mali (perte de Kidal, une seule source) : non utilisé.
- Retraits militaires français : Mali 2022, Burkina Faso 2023, Niger 2023.
- SIPRI (mars 2026, armes majeures 2021-2025) : Afrique subsaharienne : Chine 22 %, Russie 12 %, Turquie 11 %.
- Commerce Russie-Afrique 2025 : ~27,8 Md$ (chiffre d'origine russe, Financial Afrik) ; Chine-Afrique ~348 Md$ (Le Brief) : plus de 12 fois moins.
Crédit à mettre en description : « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0. Carte : Natural Earth. »

## Refaire une vidéo
1. `npm install` puis `npm run carte` (télécharge Natural Earth et projette la carte).
2. Écrire `texte.txt` (une phrase = une scène ; 10 scènes dans `Geo.tsx`), puis `npm run voix`.
3. Adapter `scenesPanneau`, `SOURCES`, `PRESENCE` et `VILLES_*` dans `src/Geo.tsx` ; `npm run rendu`.

## Monétisation
- TikTok Creator Rewards : vidéos de plus d'une minute, 10 000 abonnés, 100 000 vues sur 30 jours, compte personnel, 18 ans et plus (sources secondaires concordantes, novembre 2026 : timetopost.co, postlinkapp.com, shortsfast.com). Une vidéo de moins de 60 s ne rapporte rien via ce programme : viser 61 à 75 s pour les vidéos destinées à la monétisation.

## Prochaine étape
- Publier, mesurer vues et rétention ; sujet suivant possible : la Chine en Afrique (même modèle).
