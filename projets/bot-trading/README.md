# Bot de trading multi-agents (paper trading)

Version honnête du reel « 350 bots Grok » : 5 agents spécialisés + un coordinateur, **ta validation avant chaque trade**, argent fictif.

| Agent | Rôle | Fichier |
|---|---|---|
| Scanner | Garde les 5 cryptos les plus liquides | `bot/agents.py` → `scanner` |
| Setups | Tendance (MM50 > MM200), cassure 20 jours, momentum 30 jours | `setups` |
| Sentiment | Indice Fear & Greed : veto si avidité ≥ 80 | `sentiment` |
| Flux | Volume anormal (proxy « baleines », pas de vraie donnée on-chain) | `flux` |
| Risque | 1 % du capital risqué par trade, stop 2 ATR puis suiveur 3 ATR, coupe-circuit à -20 % | `taille_position` |
| Macro (optionnel) | Inspiré de MacroMicro : veto si taux US 10 ans ET dollar au-dessus de leur moyenne 50 j (données Fed/FRED) | `contexte_macro_geo` |
| Géopolitique (optionnel) | Inspiré de World Monitor : veto si l'indice de risque géopolitique (Caldara-Iacoviello) est dans le top 10 % de l'année | `contexte_macro_geo` |
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

## Ajout des agents macro et géopolitique (reel « 3 sites de trading cachés »)
| 2024 → aujourd'hui | Rendement | Pire baisse | vs hasard |
|---|---|---|---|
| Bot 5 agents | +10 % | -22 % | 48e percentile |
| + macro | **-20 %** | -25 % | — |
| + géopolitique | +19 % | -21 % | ≈ médiane du hasard (+11 %) |
| 7 agents | **-20 %** | -25 % | 0e percentile |

- **Macro : nuisible.** Ses jours de veto (37 % du temps) ont été suivis de *meilleures* hausses du BTC que les autres. Désactivé par défaut.
- **Géopolitique : léger mieux, pas significatif.** Désactivé par défaut ; affiché à titre d'info dans `signal_du_jour.py`.
- **Novex Terminal : introuvable** (aucune trace publique), donc pas intégré.
- MacroMicro n'a qu'une API payante (offre entreprise) : remplacée par les données gratuites de la Fed. World Monitor n'a pas d'historique exploitable : remplacé par l'indice géopolitique académique qui le couvre depuis 1985.

## Système « 7 agents sur l'or » (reel Sentinel / Vortex / Phantom / Oracle / Kronos)
`python3 tester_or.py` → `resultats/rapport_or.md` et journal Kronos `resultats/journal_or_kronos.csv`.

| Agent | Rôle | Donnée réelle |
|---|---|---|
| Sentinelle | Macro : taux réels US 10 ans en baisse → +1 | Fed (FRED DFII10) |
| Bouclier | Valeur refuge : tension géopolitique élevée → +1 | Indice Caldara-Iacoviello |
| Vortex | Structure technique : tendance MM50/MM200 | Future or COMEX |
| Phantom | Institutionnels COMEX : position nette des fonds (rapport COT) | CFTC, hebdomadaire |
| Atlas | Dollar en baisse → +1 | Fed (FRED DTWEXBGS) |
| Oracle | Probabilité de hausse à 20 j selon le consensus, apprise sur le passé seulement | — |
| Kronos | Exécution le lendemain, stop 3 ATR, journal des trades | — |

| 2008 → aujourd'hui | Rendement | Pire baisse | vs hasard |
|---|---|---|---|
| Oracle 5 agents | +6 % | -29 % | 31e percentile |
| Consensus fort | +51 % | -18 % | — |
| **Acheter et garder l'or** | **+379 %** | -44 % | — |

Depuis 2024 : Oracle -6 %, consensus -8 %, or +98 %. **Le système fait moins bien que des entrées au hasard.**
Les « iceberg orders » du reel demandent des données de carnet d'ordres COMEX payantes : remplacés par le rapport COT public (hebdomadaire).

## Limites du test
- Paramètres fixés à l'avance, non optimisés ; 10 cryptos seulement ; journalier.
- Les 10 cryptos sont choisies avec ce qu'on sait aujourd'hui (biais du survivant : elles ont toutes survécu).
- Grok n'est pas testé (pas de clé API) et ne donne qu'un avis, il ne décide rien.

## Labo par instrument, mémoire post-trade, amélioration continue, audit (2026-10-20)

| Module | Rôle | Commande |
|---|---|---|
| `labo/` | Données + contrôle qualité, caractéristiques, 4 stratégies concurrentes (modules indépendants), 3 unités de temps, coûts variables, régimes, walk-forward, références, DSR/PBO, coffre, fiche | `python3 -m labo.pilote BTCUSDT` → `rapports/labo_BTCUSDT.md` |
| `memoire/` | Journal immuable chaîné (SHA-256), corrections séparées, diagnostic 4 catégories, analyse pertes/gains, 4 registres de connaissances, rapports | `python3 -m memoire.exemple_fictif` → `rapports/exemple_fictif/` (DONNÉES FICTIVES) |
| `amelioration/` | Seuils fixés à l'avance, surveillance, détecteurs de changement évalués, hypothèses avec protocole, validation en 8 étapes, versions (jamais de remplacement automatique), garde-fous | `python3 -m amelioration.boucle declarer` / `tester` / `rapport` → `rapports/amelioration_BTCUSDT.md` |
| `audit/` | Audit indépendant d'Aladdin (lecture seule) | `audit/rapport_audit_aladdin.md` |
| `tests/` | 33 tests (look-ahead, moteur, statistiques, immuabilité, diagnostic, prévention, décision, versions, garde-fous, reproductibilité) | `python3 -m unittest discover -s tests -t .` |

Critères de décision : `labo/criteres.py` et `amelioration/boucle.py:DECISION`, fixés avant les tests. Registres en ajout seul : `registre/`, `amelioration/registre/`.
