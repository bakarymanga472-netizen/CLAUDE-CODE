# Aladdin

Structure de trading en « salle des marchés » : plusieurs desks de stratégie, un desk risque, un comité de sélection qui ne regarde que le passé, et un suivi en direct.

```
Données (Binance, COMEX, SPY, TLT)
   └─ Desks de stratégie : momentum (20/60/120/250 j), moyennes mobiles, rebond RSI-2, combinaisons
        └─ Desk risque : volatilité cible 15 %/an, risque égal entre actifs, sans levier
             └─ Comité (recherche.py) : walk-forward annuel + coffre-fort 2025+ ouvert une seule fois
                  └─ Exécution papier en direct (live.py) : journal quotidien sur les vrais cours
```

## Commandes
```bash
python3 -m aladdin.recherche --rafraichir   # refait toute la recherche → resultats/aladdin_rapport.md
python3 -m aladdin.live                     # une fois par jour : met à jour le portefeuille fictif et donne les positions
```

## Structure retenue (choisie avec les données ≤ 2024)
**Momentum 120 jours sur 5 cryptos (BTC, ETH, BNB, SOL, XRP), volatilité cible.**
Chaque jour : on détient une crypto si elle a monté sur 120 jours, en taille inversement proportionnelle à sa volatilité ; le reste en cash.

## Résultats
| Test | Résultat |
|---|---|
| Walk-forward 2017-2024 (hors échantillon) | +22 %/an, pire baisse -33 %, Sharpe 1,37 |
| **Coffre-fort 2025 → 2026-10-14** | **+5,5 %**, pire baisse -17 % (BTC -14 %, or +56 %, actions +34 %) |
| Taux de trades gagnants | 31 % avant 2025, 38 % dans le coffre |

## Pourquoi pas 99 % de réussite
« Vendre à +1 %, couper à -50 % » sur BTC 2020-2024 : **97 % de trades gagnants**, mais +513 % contre +1 214 % en gardant le BTC.
Le meilleur taux de réussite des 48 structures (70 %, rebond RSI-2) rapporte +2 %/an. Les structures qui gagnent le plus ont 30-40 % de trades gagnants : peu de gros gains, beaucoup de petites pertes.

## Limites
- Le coffre-fort est maintenant ouvert : toute modification future doit être validée par le suivi en direct, pas par l'historique.
- La sélection a préféré les cryptos parce que 2020-2024 leur a été favorable. En 2025-2026 l'or et les actions ont mieux fait.
- Pas d'argent réel. Le suivi en direct ne vaut quelque chose qu'après plusieurs mois.
