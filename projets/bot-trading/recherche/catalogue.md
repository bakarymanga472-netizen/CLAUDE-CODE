# Mission 1 — Recherche quantitative crypto + forex (phase 1 : documentation et données)

Date : 2026-10-20. Statut : **recherche documentaire uniquement. Aucune stratégie n'est validée.**
Une stratégie ne passe « validée » qu'après réplication indépendante dans ce dépôt + test hors échantillon jamais vu.

Légende des niveaux de preuve :
- **A** : revue à comité de lecture, répliquée par d'autres, données longues.
- **B** : publication sérieuse, peu répliquée ou période courte.
- **C** : preprint, blog, ou résultat fragile.
- **Interne** : déjà testé dans ce dépôt (`aladdin/`), résultats réels de nos backtests.

Ce qui est marqué « non vérifié » n'a pas été lu dans la source primaire. Aucun chiffre ci-dessous n'est inventé ; ceux qui manquent sont signalés.

---

## 0. Verdict sur l'objectif « +45 % par mois »

+45 %/mois composé = **×86 par an**. Aucune source académique ni aucun fonds documenté n'approche ça de façon durable.
Ordres de grandeur vérifiés :
- Trend following multi-actifs sur 110 ans : environ **11 %/an net**, volatilité ~10 % (Hurst-Ooi-Pedersen 2017).
- Carry crypto (funding/basis) : **40-60 %/an** en période favorable, avec risque de liquidation et d'effondrement (Schmeling-Schrimpf-Todorov, BIS WP 1087). C'est le chiffre publié le plus élevé trouvé, et il est concentré sur 2020-2021.
- Notre meilleur résultat hors échantillon : **+22 %/an** (Aladdin momentum crypto, walk-forward 2017-2024), **+5,5 %** sur le coffre-fort 2025+.

Conclusion : l'objectif n'est pas « ambitieux », il est hors de portée sans levier extrême, et le levier extrême mène à la ruine. Un objectif défendable : **15-30 %/an avec une pire baisse < 25 %**. Je refuse de construire un système calibré sur +45 %/mois : il serait forcément sur-ajusté.

---

## 1. Fiches stratégies

Format des 15 champs : 1 description · 2 marchés · 3 unités de temps · 4 sources · 5 logique d'entrée · 6 sortie/stop/taille · 7 indicateurs · 8 données · 9 coûts · 10 rendement publié · 11 DD/réussite/PF/nb trades · 12 risques · 13 risque de sur-ajustement · 14 difficulté · 15 plan de réplication.

### S1 — Momentum de série temporelle (trend following) + ciblage de volatilité — preuve **A** + Interne
1. Acheter ce qui a monté sur N mois, vendre/sortir ce qui a baissé, chaque actif jugé contre lui-même.
2. Multi-actifs (futures actions, taux, devises, matières premières) ; crypto.
3. Journalier, rebalancement hebdo/mensuel. Lookback 1-12 mois.
4. Moskowitz, Ooi, Pedersen (2012), *Time Series Momentum*, JFE — https://papers.ssrn.com/abstract=2089463 · données AQR : https://www.aqr.com/insights/datasets/time-series-momentum-original-paper-data · Hurst, Ooi, Pedersen (2017), *A Century of Evidence on Trend-Following Investing*, JPM.
5. Signal = signe du rendement sur 12 mois (ou 1/3/12 mois). Long si > 0, short ou cash si < 0.
6. Taille = volatilité cible / volatilité estimée de l'actif (ex. 40 %/an par actif dans l'article). Sortie quand le signal change de signe.
7. Rendement passé, volatilité réalisée (EWMA).
8. Prix journaliers longs. Crypto : Binance spot (OK). FX : Yahoo/Dukascopy (OK).
9. Rotation faible ; sensible au slippage seulement en petit lookback.
10. ~11 %/an net, vol 9,7 %, positif chaque décennie depuis 1880 (Hurst et al. 2017).
11. DD et PF par stratégie : non relevés dans la source primaire. **Interne** : crypto 5 actifs 120 j + vol target, walk-forward 2017-2024 **+22 %/an, pire baisse -33 %** ; coffre-fort 2025+ **+5,5 %**, pire baisse -17 %.
12. Perd dans les marchés en range et aux retournements brutaux (« momentum crash »).
13. Faible si on garde les paramètres standards (12 mois) ; fort si on optimise le lookback actif par actif.
14. Facile.
15. Rejouer avec lookback fixé à l'avance (1/3/12 mois, moyenne des signaux), données ≤ 2022 pour figer, test 2023+. Déjà fait en partie dans `aladdin/recherche.py`.

### S2 — Momentum transversal crypto (classement entre cryptos) — preuve **A/B**
1. Acheter les cryptos qui ont le plus monté la semaine/mois passé, vendre les plus faibles.
2. Univers large de cryptos (centaines).
3. Hebdomadaire.
4. Liu, Tsyvinski, Wu (2022), *Common Risk Factors in Cryptocurrency*, Journal of Finance — https://papers.ssrn.com/abstract=3379131 · NBER w25882 : https://www.nber.org/papers/w25882.pdf
5. Tri par rendement passé (1-4 semaines), long quintile haut, short quintile bas.
6. Rebalancement hebdo, poids égaux ou par capitalisation.
7. Rendements passés, capitalisation.
8. Historique d'un univers large **avec cryptos mortes** (sinon biais du survivant). CoinGecko OK, mais l'historique des cryptos disparues est incomplet.
9. **Élevés** : petites cryptos = spread large ; le short est souvent impossible en spot.
10. Primes momentum et taille significatives dans l'article (chiffres exacts non recopiés ici → à relire avant de les citer).
11. Non relevés.
12. Effet concentré dans les petites cryptos illiquides (cf. Cakici et al. 2024 sur le ML) ; impossible à capter à petite taille réaliste.
13. Moyen.
14. Moyenne (univers, survivants, short).
15. Univers = top 30 Binance spot au moment t (pas aujourd'hui), long-only top 5 vs équipondéré, frais 0,15 %.

### S3 — Carry crypto : funding des perpétuels / basis des futures — preuve **B**
1. Être long spot + short perpétuel (ou futures) pour encaisser le funding/la prime, sans exposition au prix.
2. BTC, ETH (perps Binance, OKX, Deribit).
3. Funding toutes les 8 h ; positions de plusieurs jours/semaines.
4. Schmeling, Schrimpf, Todorov, *Crypto Carry*, BIS Working Paper 1087 — https://www.bis.org/publ/work1087.pdf
5. Entrer quand le funding annualisé (ou la basis) dépasse un seuil couvrant les coûts.
6. Sortir quand le funding retombe ; taille limitée par la marge et le risque de liquidation de la jambe short.
7. Taux de funding, basis futures/spot, open interest.
8. Funding Binance via archives data.binance.vision (OK) ; OKX funding (OK) ; Deribit (OK). fapi Binance bloqué ici (451), Bybit bloqué (403).
9. 4 jambes de frais (entrée/sortie × 2), coûts d'emprunt, risque de contrepartie de la plateforme.
10. Carry crypto élevé, 40-60 %/an sur certaines périodes, avec épisodes d'effondrement (source BIS).
11. Non relevés précisément.
12. Faillite de plateforme (FTX), liquidation de la jambe short lors d'un pic, funding négatif prolongé, compression du carry à mesure que le marché s'institutionnalise.
13. Faible sur la logique ; fort sur le choix du seuil.
14. Moyenne-élevée (deux jambes, marge, exécution simultanée).
15. Télécharger le funding historique BTC/ETH (Binance archives + OKX), simuler un carry passif net de frais 2019-2024, puis 2025+. Mesurer surtout la décroissance du rendement dans le temps.

### S4 — Carry FX (devises à taux haut contre taux bas) — preuve **A**
1. Emprunter dans une devise à taux bas, placer dans une devise à taux haut.
2. G10 + émergents.
3. Mensuel.
4. Brunnermeier, Nagel, Pedersen (2008), *Carry Trades and Currency Crashes*, NBER w14473 — https://www.nber.org/papers/w14473.pdf · Lustig, Roussanov, Verdelhan (facteur carry, crash risk).
5. Classer les devises par différentiel de taux ; long les plus hauts, short les plus bas.
6. Rebalancement mensuel ; pas de stop dans la littérature de base.
7. Taux courts (ou points de swap).
8. Taux : FRED (CSV gratuit, timeouts intermittents ici) ; prix Yahoo/Dukascopy.
9. Faibles sur le G10 ; swaps de financement chez un broker retail souvent défavorables.
10. Prime positive historiquement ; chiffres exacts non recopiés.
11. Asymétrie négative : gains réguliers, krachs brutaux (2008).
12. « Monter par l'escalier, descendre par l'ascenseur ».
13. Faible.
14. Facile en données, moyenne en exécution (swaps broker).
15. Panier G10, données de taux FRED, 2000-2018 / 2019+.

### S5 — Momentum FX — preuve **A**, attentes basses
1. Acheter les devises qui ont monté le mois passé.
2. Large univers de devises (48 dans l'article).
3. Mensuel.
4. Menkhoff, Sarno, Schmeling, Schrimpf (2012), *Currency Momentum Strategies*, JFE — BIS WP 366 : https://www.bis.org/publ/work366.pdf
5. Classement par rendement passé 1-12 mois.
6. Rebalancement mensuel.
7. Rendements passés.
8. Prix + taux (Yahoo, FRED).
9. **Environ un tiers du profit absorbé par les coûts** ; rendement jusqu'à ~10 %/an bruts, concentré sur des devises peu liquides.
10. Jusqu'à ~10 %/an.
11. Non relevés.
12. Sur les majeures liquides, l'effet est bien plus faible.
13. Moyen.
14. Facile.
15. Limité aux 7-10 majeures accessibles chez un broker retail ; on s'attend à un résultat faible.

### S6 — Règles techniques FX (moyennes mobiles, filtres) — **ÉCHEC documenté**
1. Moyennes mobiles / filtres sur paires FX.
4. Neely, Weller, Ulrich (2009), JFQA, *The Adaptive Markets Hypothesis: Evidence from the Foreign Exchange Market* — https://www.cambridge.org/core/product/9D336CDCA83233819EB5CDD0F4BC0DAA
10. Les profits des règles techniques simples **ont disparu au début des années 1990**.
13. Très élevé : toute règle MA « qui marche » sur EUR/USD récent est suspecte.
15. Ne pas développer. Garder comme **groupe témoin** pour mesurer le sur-ajustement de nos propres recherches.

### S7 — Retour à la moyenne court terme (RSI-2 dans une tendance haussière) — preuve **Interne** (littérature non vérifiée)
1. Acheter un repli de 1-3 jours dans un actif au-dessus de sa MM200.
2. Indices actions (SPY), or. Testé aussi sur crypto : moins bon.
3. Journalier, trades de quelques jours.
4. Littérature praticienne (Connors) : **non vérifiée par moi** — ne pas citer comme preuve.
5. RSI-2 < 5 et cours > MM200 → achat à la clôture suivante.
6. Objectif +1 %, stop -10 %, 20 jours max.
7. RSI-2, MM200.
8. Yahoo (OK), Alpaca (clés manquantes).
9. Faibles sur SPY ; sensibles car le gain par trade est petit (+1 %).
10. Interne : faible rendement total (peu de trades, petits gains).
11. Interne : réussite **84 %** (2008-2019), **78 %** (2020-2024), **79 %** (2025+). Une perte = ~10 gains.
12. Une perte -10 % efface 10 trades ; risque de krach rapide sous la MM200 juste après l'entrée.
13. Moyen : seuils choisis sur ≤ 2019 et validés ensuite, mais 400+ combinaisons testées au total (biais de sélection réel).
14. Facile.
15. Suivi en direct depuis le 2026-10-15 (`aladdin/live_rebond.py`). Calculer le Deflated Sharpe Ratio en tenant compte du nombre de combinaisons testées.

### S8 — Momentum intrajournalier BTC (première demi-heure → dernière demi-heure) — preuve **B**
1. Le rendement de la première demi-heure de la journée prédit celui de la dernière.
2. BTC.
3. 30 minutes.
4. Shen, Urquhart, Wang (2022), Financial Review (lu via résumé, chiffres non recopiés).
5-6. Entrée en fin de journée UTC dans le sens de la première demi-heure ; sortie à la clôture.
8. Binance klines 30 min (OK, accessibles).
9. **Critique** : un trade par jour, l'avantage est petit → les frais de 0,1-0,15 % peuvent tout absorber.
12. Effet publié = probablement atténué depuis (McLean-Pontiff : -58 % après publication en moyenne).
14. Facile.
15. Rejouer 2019-2022 puis 2023+, frais réalistes taker. À abandonner si l'avantage brut < 2× les frais.

### S9 — Portefeuilles gérés par la volatilité — preuve **contestée**
1. Réduire l'exposition quand la volatilité récente monte.
4. Moreira & Muir (2017) pour ; Cederburg, O'Doherty, Wang, Yan (2020, JFE) contre : la plupart des versions **ne battent pas** hors échantillon ; Barroso & Detzel : coûts de transaction.
10. Gains réels surtout en **réduction de pire baisse**, pas en rendement.
15. On l'utilise comme **couche de risque** (déjà dans `desk_risque`), pas comme source de rendement.

### S10 — Stratégies post-annonce (FOMC, CPI, NFP) — preuve **non recherchée**
Non couvert par mes recherches à ce stade. Données nécessaires : calendrier macro horodaté + prix intraday (Dukascopy tick OK pour le FX). **À rechercher avant toute conclusion.**

### S11 — Market making — **exclu**
Exige colocation, carnet d'ordres en temps réel, latence de quelques millisecondes et frais maker négatifs. Notre infrastructure (scripts quotidiens, conteneur cloud) n'est pas adaptée. Ne pas développer.

### S12 — Machine learning (prédiction de rendement) — preuve **C**, plutôt négative
4. Bysik & Ślepaczuk (2026, preprint, non publié) : les modèles ML crypto **échouent après 10 points de base de frais**. Cakici et al. (2024) : les profits ML en crypto sont **concentrés dans les cryptos illiquides**.
13. Maximal : des milliers de paramètres, très peu d'observations indépendantes.
15. Dernier de la liste. Seulement comme filtre sur une stratégie déjà validée, avec coûts inclus dès le départ.

### S13 — Règles techniques et breakouts sur BTC — preuve **B/C**, mitigée
- Detzel et al. (2018) et Corbet et al. (2019, FRL) trouvent un pouvoir prédictif des moyennes mobiles sur BTC, **en échantillon**.
- Hudson & Urquhart (2019) : la prévisibilité ne tient pas hors échantillon.
- Lecture : le breakout/momentum BTC est une variante de S1. Le traiter dans S1 plutôt que comme stratégie séparée.

---

## 2. Stratégies qui ont échoué (à garder visibles)

| Stratégie | Constat | Source |
|---|---|---|
| Règles techniques FX | Profits disparus début 1990 | Neely-Weller-Ulrich 2009 |
| Anomalies publiées en général | -26 % hors échantillon, -58 % après publication | McLean & Pontiff 2016, JF |
| ML crypto | Disparaît après 10 pb de frais | Bysik-Ślepaczuk 2026 (preprint) |
| Vol-managed en rendement | Pas d'avantage robuste OOS | Cederburg et al. 2020 |
| **Interne** : bot multi-agents « 350 bots Grok » | Pas mieux que le hasard depuis 2024 | `resultats/rapport.md` |
| **Interne** : 7 agents sur l'or | +6 % vs +379 % pour l'or gardé | `resultats/rapport_or.md` |
| **Interne** : agent macro | Nuisible | `resultats/rapport.md` |
| **Interne** : filtres anti-pertes | Tous rejetés en validation | `resultats/aladdin_enquete.md` |
| **Interne** : TP +1 %/SL -50 % sur BTC | 97 % de réussite mais +513 % vs +1214 % gardé | `aladdin/moteur.py` (`piege_99`) |

---

## 3. Catalogue par instrument

| Instrument | Candidats sérieux | À éviter | Note |
|---|---|---|---|
| **BTC** | S1 trend + vol target ; S3 carry funding ; S8 intraday (à tester) | ML, règles MA optimisées | Le plus liquide, coûts les plus bas |
| **ETH** | S1, S3 | Idem BTC | Fortement corrélé à BTC : ne compte pas comme diversification |
| **Altcoins** | S1 en panier ; S2 transversal (long-only) | Short d'altcoins, ML | Survivants, liquidité, delistings |
| **EUR/USD** | S1 lent (faible) ; S4 carry en panier | Règles techniques courtes (S6) | Marché très efficient |
| **USD/JPY, AUD/USD, autres majeures** | S4 carry (panier), S5 momentum (panier) | Stratégie sur une seule paire | Un panier G10 est plus robuste qu'une paire isolée |
| **Or** | S1 ; S7 RSI-2 (interne) | Bot 7 agents (échec) | |
| **SPY** (hors mission, déjà en direct) | S7 RSI-2 | | |

---

## 4. Classement comparatif

Échelle de 1 (faible) à 5 (fort). « Sensibilité aux coûts » : 5 = peu sensible.

| # | Stratégie | Preuve | Simplicité | Robustesse OOS | Rendement net plausible | Pire baisse | Sensibilité coûts | Stabilité régimes | Total /35 |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Trend + vol target | 5 | 5 | 4 | 3 | 3 | 5 | 3 | **28** |
| S7 | RSI-2 repli (SPY/or) | 2 | 5 | 4 | 2 | 3 | 3 | 3 | **22** |
| S4 | Carry FX panier | 5 | 4 | 3 | 2 | 2 | 4 | 2 | **22** |
| S3 | Carry funding crypto | 3 | 3 | 3 | 4 | 3 | 3 | 2 | **21** |
| S5 | Momentum FX | 4 | 4 | 2 | 1 | 3 | 2 | 2 | **18** |
| S8 | Intraday BTC | 3 | 4 | 2 | 2 | 3 | 1 | 2 | **17** |
| S2 | Momentum transversal crypto | 4 | 3 | 2 | 2 | 2 | 1 | 2 | **16** |
| S12 | ML | 1 | 1 | 1 | 1 | 2 | 1 | 1 | **8** |

S3 passe avant S7 et S4 dans l'ordre de travail : S7 tourne déjà en direct, et S4 est peu accessible en retail (swaps).

Ces notes sont **mon jugement** à partir des sources, pas une mesure. Elles servent à décider l'ordre de travail, rien d'autre.

---

## 5. Inventaire des données (testé depuis ce conteneur le 2026-10-20)

| Source | Contenu | Accès |
|---|---|---|
| Binance spot (data-api.binance.vision) | Klines crypto 1 min → 1 jour | ✅ |
| data.binance.vision (archives) | Funding + klines futures historiques | ✅ |
| Binance fapi (API futures en direct) | Funding temps réel | ❌ 451 (géo-bloqué) |
| Bybit | Tout | ❌ 403 |
| OKX | Funding | ✅ |
| Deribit | Futures/options BTC-ETH | ✅ |
| CoinGecko | Univers, capitalisations | ✅ (historique des cryptos mortes incomplet) |
| Yahoo Finance | FX journalier ✅, FX 1 h ✅ (~730 jours max) ; SPY, or, TLT | ✅ |
| Dukascopy | Ticks FX (format bi5) | ✅ |
| histdata.com | Minutes FX | ✅ site joignable, téléchargement manuel |
| FRED CSV | Taux, macro | ⚠️ marchait avant, timeout aujourd'hui |
| FRED API | Idem | Clé requise |
| CFTC COT | Positionnement | ✅ |
| Alpaca | Prix + ordres actions (paper) | 🔑 clés manquantes |
| OANDA practice | FX démo + ordres | 🔑 clés manquantes |

**À obtenir** (par toi) : clés Alpaca paper ; un compte démo OANDA (gratuit) pour le FX ; une clé FRED (gratuite).

---

## 6. Liste priorisée à coder (après ton feu vert)

1. **Moteur commun + garde-fous statistiques** : frais/slippage/funding par instrument, walk-forward, Deflated Sharpe Ratio et PBO (Bailey & López de Prado — https://papers.ssrn.com/abstract=2460551), registre des hypothèses en ajout seul (jamais de suppression).
2. **S1 trend + vol target** sur BTC, ETH, panier altcoins, or, panier FX : réplication des paramètres de l'article, sans optimisation.
3. **S3 carry funding BTC/ETH** à partir des archives Binance + OKX.
4. **S7 RSI-2** : continuer le suivi en direct (déjà en cours), ajouter le DSR.
5. **S4/S5 FX en panier** G10 (attentes basses ; sert aussi de témoin).
6. **S8 intraday BTC** : test rapide, abandon si l'avantage brut < 2× les frais.
7. **S12 ML** : seulement en filtre, en dernier.

Exclus : S6 (gardé comme témoin), S11 market making, S10 tant que la recherche n'est pas faite.

---

## 7. Angles morts et limites de cette recherche

- Plusieurs chiffres (S2, S4, S8) ne sont pas recopiés de la source primaire : je l'indique au lieu de les inventer.
- Je n'ai pas cherché la littérature post-annonce (S10).
- Les rendements publiés baissent après publication (McLean-Pontiff) : il faut s'attendre à moins que les chiffres des articles.
- Nos propres tests ont déjà essayé des centaines de combinaisons : nos meilleurs résultats sont biaisés à la hausse tant que le DSR n'est pas calculé.
- Données gratuites = pas de cryptos mortes, pas de spread historique réel en FX retail.
