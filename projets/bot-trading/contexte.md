# Projet : bot-trading

_Créé le 2026-10-15 — Dernière mise à jour : 2026-10-15_

## Objectif (une phrase, mesurable)
Savoir si un bot multi-agents (inspiré du reel « 350 bots Grok ») bat le hasard et l'achat-conservation, en argent fictif.

## Où on en est
V1 testée le 2026-10-15 : bat le hasard en 2020-2023, plus d'avantage depuis 2024 (48e percentile). Agents sentiment et flux inutiles. Voir resultats/rapport.md.
2026-10-15 : agents macro (MacroMicro) et géopolitique (World Monitor) ajoutés et testés : macro nuisible, géopolitique marginal. Les deux désactivés par défaut.
2026-10-15 : système 7 agents sur l'or testé 2008-2026 : +6 % contre +379 % pour l'or acheté-gardé, sous le hasard (31e percentile). Ne pas trader.
2026-10-15 : Aladdin (aladdin/) : 48 structures, walk-forward 2017-2024 +22 %/an, coffre-fort 2025+ +5,5 % (pire baisse -17 %). Suivi papier en direct démarré le 2026-10-14 (resultats/aladdin_journal.csv).
2026-10-15 : enquête sur les trades perdants → pertes indiscernables à l'entrée ; Aladdin Rebond (RSI2<5, +1 %/-10 %/20 j sur SPY + or) : 84 % / 78 % / 79 % de réussite. Connecteur Alpaca paper prêt, attend les clés.

## Décisions prises (et pourquoi)
- Paper trading uniquement, validation humaine obligatoire.
- Pas de 350 bots : 5 agents suffisent pour tester l'idée.
- Grok = avis facultatif, jamais décideur.

2026-10-20 : Mission 1 phase 1 — catalogue de recherche + inventaire des données : recherche/catalogue.md. Verdict +45 %/mois : irréaliste.
2026-10-20 : labo par instrument (pilote BTC), mémoire post-trade, boucle d'amélioration, audit indépendant d'Aladdin. BTC : aucune stratégie validée (DSR, pas mieux que l'achat-conservation de façon significative ; coffre 2024+ sous l'achat-conservation). 3 hypothèses d'amélioration testées : 3 rejetées. Audit : momentum Aladdin rejeté, Rebond limité à la démo après correction de live_rebond.py, alpaca.py (ordres en double) et desks.py.

## Prochaine étape
1. Décision humaine sur les corrections de l'audit (anomalies 4, 5, 8, 9) — ne pas lancer alpaca.py avant correction.
2. Généraliser le labo à ETH puis au FX (OANDA démo) ; ajouter le carry funding (S3).
3. Brancher la mémoire post-trade sur le suivi papier réel.

## Tâches Notion
Base/page Notion : _lien_
