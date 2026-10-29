---
name: objectif
description: Méthode en 4 étapes pour atteindre un objectif chiffré (ex. « bot de trading à 90 % de réussite », « 10 % par mois »). Recherche web des outils → inventaire des outils internes → itérations test/correction jusqu'au critère (viser au-delà) → résultats vérifiés sur données récentes. Utiliser pour toute demande avec un résultat à atteindre, surtout bots/agents de trading, stratégies, automatisations.
---

# Méthode objectif

## Étape 0 — Cadrer (avant tout outil)
- Écris l'objectif en **critère mesurable** + seuil demandé + seuil visé (au-delà du demandé).
- Distingue les métriques ambiguës. Trading : *taux de réussite* (% de trades gagnants) ≠ *rendement* (% de gain sur le capital) ≠ *perte maximale* (drawdown). Un 95 % de trades gagnants peut perdre de l'argent.
- Vérifie le réalisme avec des sources. Seuil irréaliste (ex. +90 %/mois durable) → le dire tout de suite, proposer un seuil défendable, continuer avec les deux.
- Lis ce qui existe déjà : `cerveau/memoire/maintenant.md`, `cerveau/contexte/`, `projets/<projet>/contexte.md`, résultats et journaux, `git log`. Ne refais pas un test déjà fait.

## Étape 1 — Recherche Internet des outils
- WebSearch / Exa (`web_search_exa`, `agent_run` pour une recherche longue) : bibliothèques, API, données, méthodes, études qui servent ce critère.
- Sources primaires (docs officielles, dépôts GitHub, études). Pas de Wikipédia comme source finale.
- Sortie : liste courte (outil — ce qu'il apporte — coût — fiabilité — lien).

## Étape 2 — Inventaire des outils internes
- Skills listés (ex. `trader-*` : scanner, timemachine, risk, budget, broker…), plugins, MCP connectés (ex. TEXT_TO_QUANT pour backtests, GitHub, Notion), sous-agents (`eclaireur`, `verificateur`), scripts de `scripts/`, code des projets (ex. `projets/bot-trading/aladdin`).
- `ToolSearch` pour les outils différés avant de conclure qu'un outil manque.
- Sortie : quels outils internes + externes (étape 1) seront utilisés, et pourquoi.

## Étape 3 — Construire, tester, itérer
Boucle : construire → tester en réel → mesurer contre le critère → corriger → retester.
- Change d'approche quand une piste plafonne (autre modèle, autres règles, autre marché, autre horizon), pas seulement de paramètre.
- Vise mieux que le seuil demandé, **sans surapprentissage** : un résultat ne compte que s'il tient sur des données non utilisées pour l'optimiser.
- Trading, protocole minimal :
  - Données **les plus récentes** : 2025 et 2026 (année en cours) obligatoirement ; plus ancien seulement en complément.
  - Optimisation sur une période, validation sur une autre (hors échantillon) ; walk-forward si possible.
  - Frais, spread et slippage inclus. ≥ 30 trades sinon « non concluant ».
  - Rapporter : nb de trades, taux de réussite, rendement total et mensuel, perte maximale, pire mois, comparaison à « acheter et garder ».
  - Paper par défaut. Aucun ordre réel sans « oui » explicite.
- Coûts : avant un outil payant (crédits TEXT_TO_QUANT…), vérifier le solde et demander si non prévu.

## Étape 4 — Résultat vérifié
Livrer seulement après vérification (relancer le test final, idéalement via `verificateur`). Format :
1. **Objectif** : demandé / visé / **atteint ou non** (chiffre exact).
2. **Preuve** : période testée (dates), données, commandes ou fichiers pour reproduire.
3. **Limites** : ce qui peut casser en réel, ce qui n'a pas été testé.
4. **Suite** : prochaine étape concrète (ex. suivi papier N semaines).

## Arrêts légitimes (seulement eux)
Blocage externe (clé, permission, accès, budget) · objectif impossible ou non garanti par nature · plusieurs approches sans progrès. Alors : ce qui bloque, ce qui a été essayé (avec chiffres), ce qu'il faut de l'utilisateur. Jamais de faux succès.

## Mémoire
En fin de tâche : conclusions clés (ce qui marche / ne marche pas, chiffres, dates) dans `projets/<projet>/contexte.md` ou `cerveau/memoire/maintenant.md`, pour ne pas refaire.
