---
name: photos-reelles
description: Trouver de VRAIES photos (personnes, lieux, objets, documents d'archives) sur Internet et les intégrer à une vidéo avec leur crédit. Uniquement des images réutilisables (CC0, domaine public, CC BY, CC BY-SA), via Openverse et Wikimedia Commons. À utiliser pour TOUTE vidéo qui parle de personnes, de lieux, d'objets ou d'événements réels, sans attendre que l'utilisateur le demande.
---

# Photos réelles

**Règle de l'utilisateur (2026-11-25) :** dès qu'il existe des photos réelles et authentiques d'une personne, d'un lieu ou d'un objet du sujet, on les cherche et on les met dans la vidéo. Un dessin ou une silhouette ne sert que s'il n'existe aucune photo réutilisable.

## Procédure
1. **Lister les sujets** du script : chaque personne nommée, chaque lieu, chaque objet (bateau, document, bâtiment), chaque événement. Pour une personne, ajouter l'époque à la recherche (« Laurent Fabius 1985 »).
2. **Chercher** (Openverse, plus de 800 millions d'images, et Wikimedia Commons ; seules les licences réutilisables sont gardées) :
   `python3 .claude/skills/photos-reelles/photos.py chercher "Charles Hernu" "Rainbow Warrior 1985" --dossier photos-candidates`
3. **Vérifier à l'œil** : lire `photos-candidates/planche.jpg` avec Read, puis la description de chaque photo retenue (`candidats.json`). Les homonymes sont fréquents : « Fernando Pereira » renvoie à un footballeur, à un syndicaliste et à d'autres. Une photo *prise par* quelqu'un n'est pas une photo *de* lui. En cas de doute sur l'identité, on ne l'utilise pas.
4. **Prendre** les numéros validés : `python3 .claude/skills/photos-reelles/photos.py prendre photos-candidates 7 21 --vers public/photos`
   Le script télécharge les images en taille standard (Wikimedia refuse les autres) et remplit `public/photos/CREDITS.md`.
5. **Intégrer** dans la vidéo avec le crédit lisible à l'écran : auteur, licence et source (composant `Photo` de `projets/videos-enquete/src/Enquete.tsx`). Recopier les crédits dans la description de la vidéo.

## Ce qui est interdit (et pourquoi)
- **Les photos de presse ou d'agence** (AFP, Reuters, Getty, Sipa, journaux) et les photos d'Instagram ou de Google Images sans licence. Sur une vidéo monétisée, c'est un retrait pour droits d'auteur, voire une sanction sur le compte. « Trouvé sur Internet » ne veut pas dire « libre de droits ».
- **Les licences NC et ND.** NC interdit l'usage commercial, or une vidéo monétisée est commerciale. ND interdit la modification, or on recadre et on zoome.
- **Une photo qui accuse par association.** Montrer quelqu'un sur une question comme « sur l'ordre de qui ? » sans source qui le relie au fait, c'est de la diffamation par l'image. Chaque photo de personne doit correspondre à ce que dit la voix à ce moment-là.
- **Présenter une photo pour ce qu'elle n'est pas** (mauvaise date, mauvais lieu, autre bateau du même nom). La légende reprend la date et le lieu donnés par la source.

## Quand rien n'existe
On garde une silhouette ou une reconstitution marquée « Illustration », et on prévient l'utilisateur : « Aucune photo libre de X ». Si l'utilisateur veut quand même une photo protégée, il peut acheter une licence à l'agence ; on ne la récupère jamais sans licence.

## Sources utiles en plus de l'outil
Archives publiques : Nationaal Archief (Pays-Bas, CC0), Archives New Zealand (CC BY), NASA et administrations américaines (domaine public), Library of Congress, Europeana, Gallica (domaine public). Pour les politiques français de 1960 à 1990, le fonds Anefo du Nationaal Archief, en CC0, est souvent la meilleure piste.
