# Enquête sur les trades perdants de D1 et correctifs

Commande : `python3 -m labo.enquete_d1` · autopsie sur 2000-2015 seulement · correctifs fixés avant de regarder 2016-2021 et 2022+ (en-tête de `labo/enquete_d1.py`).

## Autopsie (2000-2015)

- 626 trades, 155 perdants.
- Perdants par cause : {'objectif/rebond': 104, 'durée': 38, 'stop': 13} — part de la perte totale : {'durée': 0.417, 'objectif/rebond': 0.202, 'stop': 0.381} — perte moyenne : {'durée': -0.0428, 'objectif/rebond': -0.0076, 'stop': -0.1146}.
- « objectif/rebond » = le trade était GAGNANT à la clôture de décision, mais la vente au cours de clôture du LENDEMAIN l'a rendu perdant.
- À l'entrée, gagnants et perdants ont les mêmes caractéristiques (RSI-2, écart à la MM200, baisse sur 5 jours, largeur du marché) : aucun filtre d'entrée ne les sépare. Les stops arrivent plutôt en volatilité élevée ; les sorties par la durée sont déjà à -2,6 % au 10e jour.

## Correctifs testés

| Version | Période | Trades | Réussite | Gain moyen | Perte moyenne | Profit factor | Rendement/an | Pire baisse | Sharpe | Mois positifs |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 ← retenue | 2000-2015 (choix) | 626 | +75 % | +1.4 % | -2.5 % | 1.65 | +3.1 % | -14 % | 0.56 | 58 % |
| D1 ← retenue | 2016-2021 (contrôle) | 309 | +75 % | +1.2 % | -1.8 % | 1.91 | +4.5 % | -9 % | 0.60 | 61 % |
| D1 ← retenue | 2022 → aujourd'hui (test) | 254 | +77 % | +1.5 % | -2.2 % | 2.22 | +6.6 % | -9 % | 1.07 | 67 % |
| F1 | 2000-2015 (choix) | 688 | +96 % | +0.6 % | -4.8 % | 2.54 | +2.8 % | -9 % | 0.70 | 67 % |
| F1 | 2016-2021 (contrôle) | 338 | +93 % | +0.5 % | -3.2 % | 2.07 | +2.7 % | -7 % | 0.52 | 64 % |
| F1 | 2022 → aujourd'hui (test) | 279 | +95 % | +0.6 % | -4.3 % | 2.39 | +3.7 % | -7 % | 0.96 | 74 % |
| F2 | 2000-2015 (choix) | 640 | +73 % | +1.4 % | -2.1 % | 1.77 | +3.5 % | -14 % | 0.66 | 57 % |
| F2 | 2016-2021 (contrôle) | 314 | +70 % | +1.2 % | -2.0 % | 1.42 | +2.7 % | -10 % | 0.41 | 62 % |
| F2 | 2022 → aujourd'hui (test) | 260 | +75 % | +1.5 % | -2.4 % | 1.87 | +5.6 % | -8 % | 1.02 | 67 % |
| F3 | 2000-2015 (choix) | 596 | +75 % | +1.4 % | -2.6 % | 1.56 | +2.6 % | -14 % | 0.49 | 53 % |
| F3 | 2016-2021 (contrôle) | 299 | +75 % | +1.2 % | -1.9 % | 1.83 | +4.0 % | -9 % | 0.55 | 58 % |
| F3 | 2022 → aujourd'hui (test) | 244 | +77 % | +1.4 % | -2.0 % | 2.42 | +6.6 % | -9 % | 1.11 | 62 % |
| F1+F2 | 2000-2015 (choix) | 695 | +93 % | +0.6 % | -3.4 % | 2.34 | +2.7 % | -9 % | 0.70 | 65 % |
| F1+F2 | 2016-2021 (contrôle) | 340 | +90 % | +0.5 % | -3.0 % | 1.47 | +1.7 % | -8 % | 0.36 | 65 % |
| F1+F2 | 2022 → aujourd'hui (test) | 283 | +93 % | +0.6 % | -4.5 % | 1.80 | +2.7 % | -6 % | 0.80 | 72 % |
| F1+F3 | 2000-2015 (choix) | 657 | +95 % | +0.5 % | -4.8 % | 2.36 | +2.5 % | -9 % | 0.63 | 61 % |
| F1+F3 | 2016-2021 (contrôle) | 325 | +93 % | +0.5 % | -3.2 % | 1.92 | +2.4 % | -7 % | 0.45 | 61 % |
| F1+F3 | 2022 → aujourd'hui (test) | 268 | +95 % | +0.6 % | -3.5 % | 3.20 | +4.2 % | -7 % | 1.18 | 69 % |
| F1+F2+F3 | 2000-2015 (choix) | 664 | +93 % | +0.6 % | -3.4 % | 2.23 | +2.4 % | -9 % | 0.64 | 59 % |
| F1+F2+F3 | 2016-2021 (contrôle) | 327 | +90 % | +0.5 % | -3.1 % | 1.38 | +1.3 % | -8 % | 0.29 | 62 % |
| F1+F2+F3 | 2022 → aujourd'hui (test) | 272 | +94 % | +0.6 % | -4.0 % | 2.17 | +3.2 % | -6 % | 1.03 | 67 % |

**Perdants restants en 2000-2015, par cause** :

- D1 : {'objectif/rebond': 104, 'durée': 38, 'stop': 13}
- F1 : {'durée': 24, 'stop': 6}
- F2 : {'objectif/rebond': 98, 'durée': 69, 'stop': 7}
- F3 : {'objectif/rebond': 99, 'durée': 38, 'stop': 13}
- F1+F2 : {'durée': 42, 'stop': 4}
- F1+F3 : {'durée': 24, 'stop': 6}
- F1+F2+F3 : {'durée': 41, 'stop': 4}

## Version retenue par la règle : D1

## Comparaison au hasard (mêmes sorties, 50 tirages, 2000 → aujourd'hui)

| Version | Réussite | Réussite du hasard | Sharpe | Sharpe du hasard | Bat le hasard (réussite) | Bat le hasard (Sharpe) |
|---|---|---|---|---|---|---|
| D1 | 75 % | 70 % | 0.66 | 0.58 | 100 % | 74 % |
| F1 | 95 % | 95 % | 0.68 | 0.39 | 20 % | 100 % |

## À risque égal : curseur de levier

| Version | Levier | Réussite | Rendement/an | Mois moyen | Mois positifs | Pire mois | Pire baisse | Test 2022+ : rendement/an, pire baisse | Risque de perdre 50 % en 5 ans |
|---|---|---|---|---|---|---|---|---|---|
| D1 | ×1 | +75 % | +4.0 % | +0.34 % | 60 % | -9.1 % | -14 % | +6.6 %, -9 % | 0 % |
| D1 | ×2 | +75 % | +7.3 % | +0.64 % | 60 % | -18.2 % | -26 % | +12.6 %, -18 % | 0 % |
| D1 | ×3 | +75 % | +10.0 % | +0.91 % | 59 % | -27.0 % | -37 % | +18.1 %, -27 % | 3 % |
| D1 | ×4 | +75 % | +12.2 % | +1.16 % | 59 % | -35.4 % | -47 % | +23.4 %, -35 % | 13 % |
| F1 | ×1 | +95 % | +3.0 % | +0.25 % | 67 % | -5.5 % | -9 % | +3.7 %, -7 % | 0 % |
| F1 | ×2 | +95 % | +5.7 % | +0.48 % | 67 % | -11.2 % | -18 % | +7.2 %, -13 % | 0 % |
| F1 | ×3 | +95 % | +8.1 % | +0.69 % | 67 % | -16.9 % | -26 % | +10.5 %, -20 % | 0 % |
| F1 | ×4 | +95 % | +10.3 % | +0.90 % | 66 % | -22.5 % | -34 % | +13.6 %, -26 % | 1 % |

**Lecture.** F1 vend dès que le cours touche un seuil fixé la veille (objectif +1 % ou retour au-dessus de la moyenne des 4 dernières clôtures, au moins +0,1 %) : les trades « gagnants à la décision, perdants le lendemain » deviennent gagnants. La réussite passe à ~95 % — mais des entrées au hasard avec la même sortie font aussi ~95 % : ce taux vient de la sortie. Ce qui vient de l'entrée, c'est le Sharpe (comparaison au hasard ci-dessus). Prix à payer : gain moyen ~+0,6 % contre une perte moyenne ~-4,8 % (une perte ≈ 8 gains). À levier 1, F1 rapporte moins que D1 ; à pire baisse égale (F1 ×3 contre D1 ×2), il rapporte autant ou plus. La règle fixée à l'avance le rejette (rendement à levier 1) : il reste candidat au suivi papier, pas validé.


Limite : les ventes à cours limité sont simulées avec le plus haut du jour (marge de 0,05 %) ; en réel, un ordre posé exactement au plus haut peut ne pas être exécuté. Les correctifs ont été choisis après une autopsie sur 2000-2015 : 2016-2021 et 2022+ sont les seuls juges.
