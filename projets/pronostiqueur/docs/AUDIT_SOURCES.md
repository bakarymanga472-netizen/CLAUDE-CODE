# Audit des sources de données (étapes 1 et 2)

Audit réalisé le 29/10/2026. « Vérifié » = testé depuis cet environnement.
« Non testé » = nécessite une clé ou un abonnement, informations issues de la
documentation publique du fournisseur, **à confirmer avant usage**.

| Source | Contenu utile | Coût / quota | Accès | Statut |
|---|---|---|---|---|
| **football-data.co.uk** | Scores **mi-temps** et finaux, tirs, tirs cadrés, corners, cartons, cotes 1N2 / +-2,5 / handicap asiatique (ouverture et clôture, plusieurs bookmakers dont Pinnacle et bet365) ; ~22 championnats, historique depuis les années 1990 | Gratuit, usage personnel | CSV public, HTTP 200 vérifié | ✅ **Vérifié, utilisé** |
| football-data.org (API) | Calendrier, résultats, score mi-temps ; compositions sur offres payantes | Gratuit limité (≈10 req/min, compétitions principales), payant au-delà | Clé API | Non testé |
| API-Football (api-sports.io) | Événements minute par minute, compositions, blessures, statistiques joueurs, cotes dont marchés par mi-temps selon les bookmakers | Gratuit ≈100 req/jour ; payant ensuite | Clé API | Non testé — **candidat n°1 pour le module joueurs et les compositions** |
| The Odds API | Cotes de nombreux bookmakers ; marchés par période selon l'offre | Crédits gratuits limités/mois, puis payant | Clé API | Non testé (présence de Betclic à vérifier) |
| StatsBomb Open Data | Données d'événements détaillées (xG, passes) sur certaines compétitions/saisons | Gratuit (licence non commerciale) | GitHub public | Non testé — utile pour la recherche sur les modèles joueurs |
| Understat | xG/xA par match et par joueur (6 grands championnats) | Gratuit | Pas d'API officielle | **Non utilisé** : extraction automatisée non autorisée explicitement |
| FBref | Statistiques avancées (données Opta) | Gratuit | Limites strictes de requêtes, licence des données | **Non utilisé** : risque de non-respect des conditions |
| Betclic | Cotes réelles de l'utilisateur, y compris par mi-temps | — | Aucune API publique ; site bloqué depuis l'étranger (HTTP 403 observé) | **Non utilisé** : l'utilisateur saisit les cotes (`--cote-h1`, `--cote-h2`) |

## Disponibilité des données par mi-temps (étape 2)

- **Disponible et vérifié** : score à la mi-temps et score final → buts de 1re
  mi-temps (HTHG + HTAG) et de 2e mi-temps (FT − HT), pour chaque match de
  12 championnats sur 8 saisons (30 655 matchs après contrôle qualité).
- **Non disponible dans la source actuelle** : minutes des buts (buts avant la
  15e/30e minute, après la 75e/85e), xG par mi-temps, cotes des marchés par
  mi-temps, compositions, blessures. Ces variables du cahier des charges ne
  sont donc **pas** utilisées pour l'instant ; elles nécessitent API-Football
  (ou équivalent) avec une clé.

## Statistiques individuelles (étape 6)

Aucune source vérifiée de minutes jouées, xG/xA par joueur et compositions
n'est branchée. Conformément au cahier des charges, **le module buteurs /
passeurs n'est pas construit** : il renvoie « Données insuffisantes ».

## Règles de collecte appliquées

- Délai d'attente, trois tentatives espacées, cache local (pas de
  téléchargements répétés inutiles).
- Aucun contournement de protection (pas de rotation d'adresse, pas de faux
  navigateur, pas de contournement des blocages).
- Chaque ligne est horodatée (`fetched_at`) et sourcée (`source`).
- Les clés API futures devront être lues dans des variables d'environnement
  (jamais dans le code ni dans git). Aucun identifiant de compte bookmaker
  n'est demandé ni stocké.
