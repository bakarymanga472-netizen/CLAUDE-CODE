# Audit 05 — essais, walk-forward retardé, annualisation

## 1. Variantes testées avant les choix finaux (comptées dans le code)

- recherche.py : 48 structures (12 signaux × 2 univers × 2 gestions) + sélection annuelle walk-forward (8 choix)
- reussite.py : 270 règles × 5 univers = 1350 combinaisons + 2 méthodes de choix
- enquete.py : 42 filtres candidats par tour (7 indicateurs × 6 quantiles) × 2 structures = 84 (+1 test de validation)
- sorties.py : 180 réglages (3 seuils × 5 objectifs × 4 stops × 3 durées)
- **Total Aladdin : 1662 variantes** ; lignée Rebond (reussite → enquête → sorties) : 1572 ; lignée momentum : 48 (+42 filtres d'enquête). Sans compter bot/ (tester.py, tester_or.py, or_systeme.py) testés avant.

## 2. Walk-forward recalculé avec exécution retardée

- Retard 0 j : +401.8 % (+22.3 %/an), pire baisse -33.2 %, Sharpe 1.37
- Retard 1 j : +438.6 % (+23.4 %/an), pire baisse -31.0 %, Sharpe 1.23
(Poids décidés à la clôture crypto de 00:00 UTC appliqués au rendement SPY/TLT/or depuis la clôture de New York de la veille au soir : ≈ 4 h d'avance pour les actifs traditionnels du panier multi-actifs.)

## 3. Annualisation : calendrier 7j/7 × 365 (moteur.py:24-27) vs séances × 252

- ACTIONS : Sharpe 7j/7×365 = 0.641 ; séances×252 = 0.643 ; vol 7j/7 19.2 % vs 19.2 %
- OR : Sharpe 7j/7×365 = 0.626 ; séances×252 = 0.628 ; vol 7j/7 18.6 % vs 18.7 %
- OBLIGATIONS : Sharpe 7j/7×365 = 0.247 ; séances×252 = 0.248 ; vol 7j/7 14.7 % vs 14.8 %
→ Écart faible : l'annualisation 365 sur un calendrier à week-ends nuls n'est pas une source d'erreur significative.
