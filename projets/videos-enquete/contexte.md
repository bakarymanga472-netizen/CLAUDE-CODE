---
type: projet
statut: actif
domaine: vidéo
maj: 2026-11-25
prochaine_etape: "Valider la vidéo test « Rainbow Warrior, partie 1 », puis vérifier et écrire la partie 2 (la note Lacoste)."
tags: [projet, video, enquete]
---

# Projet : videos-enquete

Série d'enquêtes TikTok en plusieurs parties, sur fond noir, inspirée du **format** de @dossierouge : écran central avec des reconstitutions, étiquettes, documents caviardés, tampons, sous-titres mot à mot, et une fin en suspens qui renvoie à la partie suivante. Le sujet, le texte, la marque (« SOUS SCELLÉS ») et le visuel sont les nôtres. On ne reprend ni leurs images ni leur texte.

## Vidéo test n°1 : « Le sabotage du Rainbow Warrior », partie 1 (2026-11-25)
- Note de la vidéo : [rainbow-warrior-partie-1](videos/rainbow-warrior-partie-1.md)
- Tout est fait en code (Remotion) : port d'Auckland de nuit, globe, passeports, dossier, calendrier, journal, conférence de presse, note manuscrite floutée. Aucune photo de personne réelle (droits), aucun document inventé lisible.
- Son : voix naturelle (skill voix-off, voix SIWIS). La nappe et les bruitages sont synthétisés par `mix_enquete.py`, donc sans droits.

## Décisions prises (et pourquoi)
- **Sujet historique et documenté** plutôt que l'actualité politique : faits établis depuis 40 ans, moins de risque juridique, et ça marche (les « dossiers » historiques font de l'audience).
- **Pas de photos de Pereira, Hernu ni Fabius** : sans licence, on met une silhouette et le nom. Pour mettre de vraies photos, il faut des images libres (Wikimedia Commons, avec le crédit) ou des images d'archives sous licence.
- **Pas de date d'arrestation** des « Turenge » : les sources divergent (12 juillet selon la police néo-zélandaise, 24 juillet selon NZHistory).
- **L'ordre de Mitterrand n'est pas affirmé** : il repose sur la note de l'amiral Lacoste (1986, publiée par Le Monde en 2005). Dans la partie 2, le présenter comme « selon la note de l'ancien chef de la DGSE ».

## Faits utilisés (vérifiés le 2026-11-25)
- Nuit du 10 juillet 1985, Marsden Wharf (Auckland) : deux explosions coulent le Rainbow Warrior ; le photographe Fernando Pereira meurt. Les faux époux suisses « Turenge » sont Dominique Prieur et Alain Mafart, de la DGSE. [Police néo-zélandaise](https://www.police.govt.nz/news/ten-one-magazine/rainbow-warrior-40-years), [NZHistory](https://nzhistory.govt.nz/politics/nuclear-free-new-zealand/rainbow-warrior)
- Le bateau devait mener une flottille contre les essais nucléaires français à Mururoa. [NZHistory](https://nzhistory.govt.nz/politics/nuclear-free-new-zealand/rainbow-warrior)
- 17 septembre 1985 : Le Monde révèle une « troisième équipe » de plongeurs de la DGSE. [The Spectator, 28/09/1985](https://archive.spectator.co.uk/article/28th-september-1985/12/mitterrands-fatal-cover-up)
- 20 septembre 1985 : démission de Charles Hernu. 22 septembre : Laurent Fabius déclare « Ce sont des agents de la DGSE qui ont coulé ce bateau. Ils ont agi sur ordre. » [Universalis](https://www.universalis.fr/evenement/17-25-septembre-1985-prolongements-politiques-de-l-affaire-greenpeace-et-demission-de-charles-hernu/), [Christian Science Monitor](https://www.csmonitor.com/1985/0923/osign.html). Larousse date la phrase du 24 : retenu le 22, qu'Universalis et le Wall Street Journal confirment.
- Juillet 2005 : Le Monde publie une note manuscrite de 1986 de l'amiral Pierre Lacoste (ex-chef de la DGSE) selon laquelle Mitterrand a autorisé l'opération. [MercoPress](https://en.mercopress.com/2005/07/11/mitterrand-authorized-rainbow-warrior-sabotage)
- Distances calculées (grand cercle, d3-geo) : Paris-Mururoa 15 472 km, Auckland-Mururoa 4 739 km.

## Refaire une vidéo
1. `npm install`, `npm run polices`, `npm run carte` (une fois).
2. Écrire `texte.txt` (une phrase = un moment ; 15 phrases pour 12 scènes). Adapter `SCENES` et les scènes dans `src/Enquete.tsx`, et les moments clés `EVTS` dans `prep_enquete.py` (mot qui déclenche un tampon, une étiquette, un son).
3. `npm run voix` (environ 1 min par phrase sur CPU), puis `npm run caler` et `npm run mixer`.
4. `npm run rendu` → `out/video.mp4`.

## Prochaine étape
- Partie 2 : la note Lacoste (ce qu'elle dit, ce qui est établi, ce qui ne l'est pas). Partie 3 : les suites (peines, atoll de Hao, indemnisations, excuses d'un des plongeurs en 2015). À vérifier avant d'écrire.
