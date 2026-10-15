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

## Prochaine étape
Lancer `python3 -m aladdin.live` chaque jour pendant 3 mois avant toute décision.
Soit abandonner, soit tester une nouvelle idée sur 2024+ (hors échantillon) avant toute optimisation. Pas d'argent réel.

## Tâches Notion
Base/page Notion : _lien_
