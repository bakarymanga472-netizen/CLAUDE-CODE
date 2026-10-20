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
2026-10-21 : corrections d'audit faites (Rebond corrigé → non validée ; live_rebond, alpaca.py, desks corrigés). Labo sur 11 instruments (BTC ETH BNB XRP LTC SOL GLD SPY TLT EURUSD USDJPY) : aucune stratégie validée. Carry funding : BTC « candidate démo » mais ~3 %/an depuis 2023 (probablement < placement sans risque, non vérifié). Portefeuille de tendance multi-actifs : non validé (DSR 0,41), meilleur profil de risque 2024+ (pire baisse -10 %). Suivi papier quotidien démarré (labo/suivi_portefeuille.py). Scripts Pine pour TradingView dans tradingview/.
2026-10-21 : 5 vidéos YouTube (Ray Fu, Benjamin Deleuze, Nico Trade, Kasper, Roro Crypto) traduites en code (labo/videos/) et testées : forex réel FXCM bid/ask 2021-2026, crypto, Apple/SPY. Aucune rentable de façon solide ; 14 variantes sur 240 positives en dév. ET test, toutes dans la marge du hasard. Monter la réussite à 45-58 % est facile (objectif à 1R, filtres) mais n'augmente pas le gain par trade. Rapport : rapports/videos_youtube.md.

## Prochaine étape
1. Lancer chaque jour `python3 -m labo.suivi_portefeuille` et `python3 -m aladdin.live_rebond` (données vierges).
2. Vérifier le carry contre le taux sans risque (série T-bill FRED).
3. Comparer TradingView ↔ moteur quand l'utilisateur envoie ses captures.
4. Analyser le compte de trading que l'utilisateur a ouvert dans Chrome (attend lien/captures ou session locale avec Claude in Chrome).

## Tâches Notion
Base/page Notion : _lien_
