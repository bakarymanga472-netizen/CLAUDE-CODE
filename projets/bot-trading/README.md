# Bot de trading multi-agents (paper trading)

Version honnête du reel « 350 bots Grok » : 5 agents spécialisés + un coordinateur, **ta validation avant chaque trade**, argent fictif.

| Agent | Rôle | Fichier |
|---|---|---|
| Scanner | Garde les 5 cryptos les plus liquides | `bot/agents.py` → `scanner` |
| Setups | Tendance (MM50 > MM200), cassure 20 jours, momentum 30 jours | `setups` |
| Sentiment | Indice Fear & Greed : veto si avidité ≥ 80 | `sentiment` |
| Flux | Volume anormal (proxy « baleines », pas de vraie donnée on-chain) | `flux` |
| Risque | 1 % du capital risqué par trade, stop 2 ATR puis suiveur 3 ATR, coupe-circuit à -20 % | `taille_position` |
| Coordinateur | Achète si setups ≥ 2/3, pas de veto, flux ≥ 0 | `coordinateur` |

## Utilisation
```bash
pip install pandas numpy
python3 tester.py            # backtest complet → resultats/rapport.md
python3 signal_du_jour.py    # propositions du jour, tu valides o/N (portefeuille fictif)
python3 signal_du_jour.py --grok   # + avis de Grok si XAI_API_KEY est dans l'environnement
```

## Résultats (test du 2026-10-15, voir `resultats/rapport.md`)
- **2020-2023 : ça marche** (+142 %, pire baisse -18 %, meilleur que 100 % des bots au hasard).
- **2024 → aujourd'hui : ça ne marche plus** (+10 % en 2,8 ans, pas mieux qu'un bot au hasard : 48e percentile). Garder du BTC a fait +85 %.
- Agent utile : **setups** (la tendance). Agent risque : divise la pire baisse par 2-4, mais coûte beaucoup de rendement.
- Agents inutiles ou nuisibles : **sentiment** (fait perdre du rendement), **flux** (effet nul).

Conclusion : **ne pas mettre d'argent réel**. Le gain venait du marché haussier 2020-2021, pas d'un avantage durable.

## Limites du test
- Paramètres fixés à l'avance, non optimisés ; 10 cryptos seulement ; journalier.
- Les 10 cryptos sont choisies avec ce qu'on sait aujourd'hui (biais du survivant : elles ont toutes survécu).
- Grok n'est pas testé (pas de clé API) et ne donne qu'un avis, il ne décide rien.
