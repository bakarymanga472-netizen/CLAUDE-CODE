# Aladdin — comité d'enquête sur les trades perdants


## Rebond (actions + or)

246 trades, 85 perdants (35 %). Causes trouvées :

| Cause probable | Trades perdants | Part | Perte moyenne |
|---|---|---|---|
| bruit : aucune cause mesurable | 16 | 19 % | -1.8 % |
| choc soudain (une journée à plus de 3 écarts-types) | 37 | 44 % | -4.2 % |
| entrée en période de volatilité extrême | 11 | 13 % | -2.8 % |
| la tendance de fond s'est cassée pendant le trade | 17 | 20 % | -4.4 % |
| tendance moyen terme en train de s'essouffler | 4 | 5 % | -0.8 % |

**Comparaison gagnants / perdants au moment de l'entrée** (médianes) :

| Indicateur | Gagnants | Perdants |
|---|---|---|
| volatilité (rang sur 3 ans) | 0.391 | 0.387 |
| écart à la MM200 | 0.075 | 0.064 |
| rendement 20 j | 0.016 | 0.013 |
| écart au plus haut 1 an | -0.030 | -0.029 |
| pente de la MM50 | 0.020 | 0.016 |
| RSI-2 | 10.523 | 10.464 |
| rendement 5 j | -0.011 | -0.012 |

**Boucle de correction** (gardé seulement si ça marche aussi sur des années non vues) :

- Tour 1 : aucun nouveau filtre n'améliore l'apprentissage sans sacrifier le rendement → **arrêt**.

Filtres retenus : aucun

| 2025 → aujourd'hui | Trades | Réussite | Profit factor | Rendement cumulé des trades |
|---|---|---|---|---|
| Avant enquête | 29 | 76 % | 2.11 | +41 % |
| Après enquête | 29 | 76 % | 2.11 | +41 % |

## Momentum crypto (Aladdin v1)

198 trades, 109 perdants (55 %). Causes trouvées :

| Cause probable | Trades perdants | Part | Perte moyenne |
|---|---|---|---|
| acheté un marché déjà en forte chute (couteau qui tombe) | 2 | 2 % | -4.1 % |
| bruit : aucune cause mesurable | 24 | 22 % | -3.5 % |
| choc soudain (une journée à plus de 3 écarts-types) | 12 | 11 % | -8.7 % |
| entrée en période de volatilité extrême | 10 | 9 % | -5.3 % |
| la tendance de fond s'est cassée pendant le trade | 59 | 54 % | -5.8 % |
| tendance moyen terme en train de s'essouffler | 2 | 2 % | -6.5 % |

**Comparaison gagnants / perdants au moment de l'entrée** (médianes) :

| Indicateur | Gagnants | Perdants |
|---|---|---|
| volatilité (rang sur 3 ans) | 0.361 | 0.406 |
| écart à la MM200 | 0.011 | 0.017 |
| rendement 20 j | 0.019 | 0.012 |
| écart au plus haut 1 an | -0.310 | -0.280 |
| pente de la MM50 | -0.010 | -0.001 |
| RSI-2 | 78.714 | 71.292 |
| rendement 5 j | 0.040 | 0.017 |

**Boucle de correction** (gardé seulement si ça marche aussi sur des années non vues) :

- Tour 1 : filtre « pente de la MM50 >= -0.060 » → validation : réussite 44 % → 42 %, rendement cumulé +506 % → +482 % → **REJETÉ (ne tient pas sur des années non vues)**

Filtres retenus : aucun

| 2025 → aujourd'hui | Trades | Réussite | Profit factor | Rendement cumulé des trades |
|---|---|---|---|---|
| Avant enquête | 53 | 51 % | 1.04 | -8 % |
| Après enquête | 53 | 51 % | 1.04 | -8 % |
