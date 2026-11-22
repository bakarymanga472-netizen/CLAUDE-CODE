# Maintenant — mémoire court terme

_Dernière mise à jour : 2026-11-21 (coffre Obsidian)_

## En cours
- Configuration Claude remise à zéro (PR #13) : pas de réglages ni d'agents ; un `CLAUDE.md` court a été remis pour le coffre Obsidian (PR #15). Skills restants : `higgsfield-motion-design`, `higgsfield-marketing-studio`, `remotion-best-practices`, `voix-off`. Tout l'ancien reste récupérable dans l'historique Git.
- Production vidéo TikTok (Remotion + voix off) :
  - `projets/videos-metiers/` : vidéo n°1 « Infirmière à l'hôpital » (30 s), rendue, non publiée.
  - `projets/videos-geopolitique/` : vidéo n°1 « La Russie en Afrique » (47 s), rendue, non publiée.
  - Voix : mode naturel du skill `voix-off` (Chatterbox + voix SIWIS, vérifiée par Whisper). Créditer « Voix : SIWIS French Speech Synthesis Database, CC BY 4.0 ».
- `crm-chantiers` : V1 publiée (données d'exemple) → https://claude.ai/artifact/F99bQiFMm8nspVSJjXvpUE
- `bot-trading` : Aladdin en suivi papier depuis le 2026-10-14 (`python3 -m aladdin.live`). Les skills `trader-*` ont été supprimés de la config.

## Prochaines actions
- Obsidian installé (2026-11-21) : cloner le dépôt, l'ouvrir comme coffre, installer Obsidian Git (`workflows/obsidian.md`).
- Monétisation TikTok (Creator Rewards) : il faut des vidéos de **plus d'une minute**, 10 000 abonnés et 100 000 vues sur 30 jours (sources secondaires, novembre 2026). Les vidéos actuelles (30 s et 47 s) font de l'audience, pas de revenus : prévoir des versions de plus de 60 s.
- Publier : connecter TikTok (connecteur Higgsfield `tiktok_connect`, depuis claude.ai) ; publier en brouillon d'abord ; cocher « contenu généré par IA ».
- Enregistrer 15 s de sa propre voix → `voix_naturelle.py --reference` (voix unique et sans crédit à mettre).
- Nettoyer les connecteurs et plugins du compte claude.ai (garder « H » = Higgsfield) : https://claude.ai/customize/connectors
- Remplir les 5 fichiers de `cerveau/contexte/`.

## Bloqué / en attente
- Higgsfield : plan gratuit, 10 crédits (une vidéo Seedance coûte au moins 12,5 crédits, Marketing Studio 75).
- YouTube et TikTok bloquent la lecture automatique sans compte connecté : pas d'analyse directe des vidéos d'autres créateurs depuis le serveur.
