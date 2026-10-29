# Limites connues et feuille de route

## Ce qui est fait et testé (version 0.1)

- Collecte football-data.co.uk, contrôle qualité, base SQLite.
- Variables par mi-temps sans fuite de données futures.
- Six modèles par mi-temps (dont Dixon-Coles) + combinaison calibrée hors échantillon.
- Validation chronologique sur 22 315 matchs (12 championnats, saisons 2021/22 à 2026/27, 2019/20 sert de rodage et 2020/21 uniquement d'entraînement).
- Prédiction d'un match, tableau au format demandé, statut et indice de risque.
- Journal des pronostics, règlement automatique, rapport de performance réelle.
- Évolution contrôlée des réglages (bootstrap apparié) et retour arrière.
- 14 tests automatiques (aucun accès réseau requis).

## Ce qui n'est PAS fait (ne pas le présenter comme disponible)

| Élément du cahier des charges | État | Ce qu'il faut pour le faire |
|---|---|---|
| Buteurs et passeurs décisifs (marchés C et D) | **Non implémenté** | Données joueurs fiables : minutes, xG/xA, compositions (API-Football ou équivalent) |
| Compositions officielles, blessures, suspensions | Non connectées | Même source ; à vérifier manuellement en attendant |
| Minutes des buts (avant 15e/30e, après 75e/85e) | Non disponibles | Événements minute par minute (API) |
| xG / xGA par mi-temps | Non disponibles | Fournisseur de xG sous licence |
| Cotes par mi-temps et historique des mouvements | Non disponibles | API de cotes ; en attendant, saisie manuelle de la cote Betclic |
| Rendement financier en simulation | **Impossible à calculer** | Historique de cotes par mi-temps |
| Météo, arbitre, motivation | Non utilisés | Ne seront ajoutés que si un gain hors échantillon est démontré |
| Matchs de coupe | Non couverts | Les fichiers utilisés ne contiennent que les championnats |

## Résultats honnêtes de la validation (voir reports/backtest_report.md)

- **2e mi-temps (+0,5)** : taux de base 79,4 %. Sélections annoncées à ≥ 90 % :
  89,9 % de réussite observée (328 matchs, IC95 86,2 – 92,7 %). Au seuil 95 % :
  9 sélections seulement, 8 réussies — échantillon trop petit, rien n'est prouvé.
- **1re mi-temps (+0,5)** : taux de base 71,2 %, très peu de matchs dépassent 85 %.
- **Le modèle de marché (cotes +/-2,5) est le meilleur modèle individuel** ;
  les statistiques d'équipe n'apportent presque rien au-delà des cotes pour la
  2e mi-temps (poids ≈ 0 dans l'ensemble). Les bookmakers intègrent déjà
  l'essentiel de l'information disponible dans cette source.
- **L'objectif de 95 % n'est pas atteint** et rien n'indique, avec ces données,
  qu'il soit atteignable sur un volume utile. Une cote juste à 95 % vaut 1,05 :
  même atteint, ce niveau ne serait rentable qu'avec des cotes ≥ 1,06 après marge.

## Prochaines étapes, par priorité

1. Brancher une API (clé dans une variable d'environnement) pour les
   compositions, les blessures et les minutes des buts ; mesurer le gain hors
   échantillon avant de garder chaque variable.
2. Enregistrer les cotes Betclic par mi-temps saisies à chaque pronostic pour
   constituer un historique et mesurer le rendement réel.
3. Dixon-Coles : **fait et testé**, mais sans gain mesurable (log-loss 0,6021 contre 0,6021 pour le Poisson simple en 1re mi-temps, 0,5121 contre 0,5122 en 2e). La correction du 0-0 par mi-temps est quasi nulle avec ces données ; le modèle reste dans l'ensemble, qui lui attribue un poids proche de zéro.
4. Module joueurs une fois les données individuelles validées.
5. Calibration par ligue si les biais détectés (ex. Serie A surestimée) se confirment.
