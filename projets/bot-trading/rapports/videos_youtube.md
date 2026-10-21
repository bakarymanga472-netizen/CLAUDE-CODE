# Les 5 vidéos YouTube : stratégies testées

Commandes : `python3 -m labo.videos.tester` puis `python3 -m labo.videos.rapport`. Règles fixées avant exécution : voir l'en-tête de `labo/videos/tester.py`. Résultats en R (1 R = la perte si le stop est touché) ; « Rendement 1 % » = capital final en risquant 1 % par trade.

## Qui sont les auteurs

| Vidéo | Auteur | Ce qu'il vend | Preuve publique des résultats |
|---|---|---|---|
| Complete Guide to building an AI Trading Bot | Ray Fu, ex-ingénieur Meta | communauté payante (School), cadeaux d'abonnement | aucune ; il précise lui-même que la stratégie n'est pas « magique » |
| J'ai testé une stratégie créée par Claude pendant 24h | Benjamin Deleuze | ses formations ; il conclut que la stratégie est un « piège à débutant » | trading en direct sur une journée : surtout des stops |
| Créer un Bot de Trading Performant avec Claude Code | Nico Trade | canal Telegram gratuit, challenge de prop firm | indicateur « Kumo Stream » non publié, aucun backtest montré |
| J'ai demandé à Claude de me rapporter le plus d'argent en 1h | Kasper | indicateur offert contre des likes | 1 heure de trading discrétionnaire, +42 € |
| Stratégie ULTRA RENTABLE grâce à l'IA | Roro Crypto (Romain), fondateur d'InvestX (site investx.fr, appli) | groupe privé « gratuit » si on ouvre un compte crypto chez ses partenaires (affiliation), modules de formation | captures TradingView sur des périodes choisies ; la stratégie à 81 % n'est pas publiée |

**Roro Crypto (Romain, InvestX)** — ce qui est vérifiable :
- Fondateur du média et de l'application InvestX ; audience surtout TikTok/Instagram (≈ 275 000 abonnés TikTok selon un article). Les articles « avis » trouvés en ligne sont promotionnels ; aucune source indépendante ne vérifie ses performances.
- Modèle économique annoncé dans la vidéo : accès au groupe privé en ouvrant un compte d'échange via ses partenaires. Une affiliation rémunère généralement sur les frais de trading des filleuls : il gagne quand vous tradez, que vous gagniez ou non.
- Sa stratégie « 40 % de gain, 5 % de baisse, 81 % de réussite, profit factor 8,6 » a été obtenue en ré-optimisant avec Claude, à partir de la liste des trades du même backtest, en une douzaine de jours : c'est la définition du surapprentissage. Aucun test sur des données non vues, aucune période fixée à l'avance, et la stratégie n'est pas publiée.
- Sa stratégie de départ (publique) : le même test dans ce labo, avec frais, ne gagne rien (voir plus bas).

**Ce que ces vidéos apprennent d'utile** (outils, pas stratégies) : Claude Code peut écrire du Pine pour TradingView, lire l'export CSV des trades, et piloter TradingView Desktop via un serveur MCP (vidéo de Nico Trade) ; Alpaca se branche à Claude via un MCP pour le paper trading (vidéo de Ray Fu). Le piège commun : optimiser sur le même historique jusqu'à ce que les chiffres soient beaux.

Sources : https://www.youtube.com/@rorovevo · https://t.me/rorovevo · https://www.bordeaux-gazette.com/annuaire/roro-vevo-avis-qui-est-romain-le-ceo-de-investx/ · https://startup.info/fr/rorovevo-avis-romain-de-investx-un-entrepreneur-fiable/ · https://actualites-bourse.com/avis-roro-vevo-romain-de-investx-analyse-du-media-crypto/ · https://www.tiktok.com/discover/Roro-vevo-arnaque (recherche TikTok, aucune preuve d'arnaque dans les résultats)

## Ce que disent les vidéos

### Ray Fu — « Complete Guide to building an AI Trading Bot with Claude for Beginners ».

- Lien : https://youtu.be/oQdkFPhqaGk
- Règles annoncées : Croisement de moyennes mobiles 20 et 50 jours sur Apple, 1 action. Achat quand la 20 croise au-dessus de la 50, vente quand elle repasse dessous. Vérification chaque matin à 9 h 30 (New York) avec les données Yahoo des 100 derniers jours.
- Traduction en code (là où la vidéo est floue) : Décision avec la clôture de la veille, exécution à l'ouverture (moteur labo, execution='ouverture'). Long seulement, 100 % investi quand le signal est actif (pas de stop, comme dans la vidéo).

### Benjamin Deleuze — « J'ai testé une stratégie de trading créée par Claude IA pendant 24h ».

- Lien : https://youtu.be/4pbodmoCeMk
- Règles annoncées : Forex en 5 minutes. Filtre de tendance par moyenne mobile (acheter au-dessus, vendre en dessous), séance de trading fixe (Londres puis New York, 9 h – 18 h à Paris), bougie englobante qui englobe les 2 (ou 3) bougies précédentes mèches comprises, stop sous (sur) l'englobante, objectif 2R, stop ramené au prix d'entrée à 1R, 5 % de risque par trade. Conclusion de l'auteur lui-même : stratégie sans avantage, résultats dus au hasard.
- Traduction en code (là où la vidéo est floue) : Moyenne mobile = EMA 50 (la vidéo ne précise pas la période). Plage 09:30–18:00 heure de Paris. Englobante haussière : bougie verte dont le plus haut dépasse et le plus bas passe sous les N bougies précédentes.

### Nico Trade — « Créer un Bot de Trading Performant avec Claude Code ».

- Lien : https://youtu.be/Y8FO8hnfJuo
- Règles annoncées : Bot basé sur son indicateur « Kumo Stream » (non public) : entrée sur les étiquettes buy/sell, stop = 2 × ATR, objectif = 2R. Le reste de la vidéo porte sur l'outillage (MCP TradingView, skills concepteur/architecte/développeur).
- Traduction en code (là où la vidéo est floue) : APPROXIMATION : l'indicateur réel n'est pas publié. « Kumo » = nuage d'Ichimoku ; on prend le signal classique : clôture qui sort du nuage (9/26/52) avec Tenkan au-dessus (en dessous) de Kijun. Ce test ne juge donc PAS son indicateur, seulement l'idée générique.

### Kasper — « J'ai demandé à Claude IA de me rapporter le plus d'argent possible en 1h ».

- Lien : https://youtu.be/sLmUHb4WloQ
- Règles annoncées : « Liquidity sweep » en 5 minutes (EUR/USD, GBP/USD, DAX, CAC) : repérer une poche de liquidité (plus bas/haut récent, double creux, zone non encore cassée), attendre que le prix la dépasse (« sweep ») puis referme à l'intérieur, entrer sur ce retournement, stop au-delà de la mèche, objectif la liquidité opposée (≈ 2R). Résultat dans la vidéo : +42 € en 1 heure sur quelques trades, en discrétionnaire.
- Traduction en code (là où la vidéo est floue) : Poche = plus bas (plus haut) des `lookback` barres précédentes, en excluant les 3 dernières, et pas encore touchée par ces 3 dernières. Sweep = mèche au-delà puis clôture revenue de l'autre côté. Stop = extrême de la mèche ± 0,05 ATR. Objectif 2R. Plage 08:00–18:00 heure de Paris.

### Roro Crypto (Romain, InvestX) — « Stratégie ULTRA RENTABLE grâce à l'IA (merci Claude) ».

- Lien : https://youtu.be/H1sEgRpYfxg
- Règles annoncées : SMA 20 au-dessus de la SMA 50 = tendance haussière ; quand le prix touche la SMA 20, achat ; stop « sous l'ATR » ; objectif = 1,5 fois le risque. Inverse en tendance baissière (vente à découvert). Testé dans la vidéo sur SOL en 30 min, 1 h, 2 h et 4 h depuis septembre 2020 ; meilleure unité de temps choisie après coup : 4 h (profit factor 1,2, réussite 46 %, pire baisse 8 %). La version « 81 % de réussite, profit factor 8,6 » n'est PAS publique.
- Traduction en code (là où la vidéo est floue) : Contact = le plus bas (achat) ou le plus haut (vente) de la barre atteint la SMA 20. Stop = clôture − 1 × ATR(14) (achat) ou + 1 × ATR(14) (vente). Entrée à l'ouverture suivante.

## Résultats (coûts réalistes)

| Stratégie | Marché | Unité | Période | Trades | Réussite | R moyen | Profit factor | Rendement 1 % | Pire baisse 1 % | Test 2024+ : réussite / R | Coûts ×2 : R | Hasard : R médian | Bat le hasard |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 1h | 2020-09-14 → 2026-10-20 | 7293 | 39 % | -0.22 | 0.70 | -100 % | -100 % | 39 % / -0.26 | -0.42 | -0.27 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 2h | 2020-09-14 → 2026-10-20 | 3453 | 40 % | -0.13 | 0.80 | -99 % | -99 % | 40 % / -0.16 | -0.27 | -0.20 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 4h | 2020-09-14 → 2026-10-20 | 1750 | 40 % | -0.09 | 0.87 | -81 % | -82 % | 40 % / -0.10 | -0.18 | -0.14 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 1d | 2020-09-14 → 2026-10-19 | 280 | 36 % | -0.14 | 0.79 | -34 % | -36 % | 34 % / -0.19 | -0.18 | -0.08 | 17% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 1h | 2020-09-14 → 2026-10-20 | 6975 | 39 % | -0.42 | 0.50 | -100 % | -100 % | 39 % / -0.45 | -0.81 | -0.53 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 2h | 2020-09-14 → 2026-10-20 | 3380 | 39 % | -0.28 | 0.63 | -100 % | -100 % | 41 % / -0.28 | -0.55 | -0.37 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 4h | 2020-09-14 → 2026-10-19 | 1757 | 37 % | -0.25 | 0.66 | -99 % | -99 % | 37 % / -0.27 | -0.44 | -0.25 | 50% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 1d | 2020-09-14 → 2026-10-19 | 281 | 41 % | -0.05 | 0.92 | -15 % | -31 % | 39 % / -0.09 | -0.12 | -0.10 | 73% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 1h | 2020-09-14 → 2026-10-20 | 7047 | 39 % | -0.32 | 0.60 | -100 % | -100 % | 40 % / -0.30 | -0.62 | -0.40 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 2h | 2020-09-14 → 2026-10-20 | 3417 | 39 % | -0.23 | 0.68 | -100 % | -100 % | 39 % / -0.23 | -0.43 | -0.28 | 100% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 4h | 2020-09-14 → 2026-10-20 | 1797 | 38 % | -0.19 | 0.73 | -97 % | -97 % | 38 % / -0.19 | -0.33 | -0.20 | 60% |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 1d | 2020-09-14 → 2026-10-19 | 280 | 40 % | -0.04 | 0.93 | -13 % | -30 % | 43 % / +0.03 | -0.09 | -0.10 | 77% |
| deleuze {'n': 2, 'tp_R': 2.0} | EURUSD | 5m | 2021-01-03 → 2026-10-16 | 2128 | 25 % | -0.07 | 0.88 | -79 % | -81 % | 25 % / -0.06 | -0.13 | -0.11 | 100% |
| deleuze {'n': 3, 'tp_R': 2.0} | EURUSD | 5m | 2021-01-03 → 2026-10-16 | 912 | 25 % | -0.08 | 0.86 | -55 % | -55 % | 24 % / -0.07 | -0.14 | -0.10 | 60% |
| kasper {'lookback': 20, 'tp_R': 2.0} | EURUSD | 5m | 2021-01-03 → 2026-10-16 | 4847 | 33 % | -0.16 | 0.79 | -100 % | -100 % | 32 % / -0.21 | -0.31 | -0.27 | 100% |
| kasper {'lookback': 50, 'tp_R': 2.0} | EURUSD | 5m | 2021-01-03 → 2026-10-16 | 3725 | 32 % | -0.17 | 0.78 | -100 % | -100 % | 31 % / -0.24 | -0.32 | -0.25 | 100% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | EURUSD | 1h | 2021-01-03 → 2026-10-16 | 549 | 34 % | +0.00 | 1.00 | -5 % | -36 % | 36 % / +0.04 | -0.02 | -0.05 | 77% |
| deleuze {'n': 2, 'tp_R': 2.0} | GBPUSD | 5m | 2021-01-03 → 2026-10-16 | 2139 | 25 % | -0.13 | 0.78 | -95 % | -95 % | 25 % / -0.12 | -0.23 | -0.16 | 90% |
| deleuze {'n': 3, 'tp_R': 2.0} | GBPUSD | 5m | 2021-01-03 → 2026-10-16 | 929 | 25 % | -0.11 | 0.81 | -67 % | -68 % | 23 % / -0.15 | -0.19 | -0.14 | 70% |
| kasper {'lookback': 20, 'tp_R': 2.0} | GBPUSD | 5m | 2021-01-03 → 2026-10-16 | 4941 | 33 % | -0.21 | 0.74 | -100 % | -100 % | 33 % / -0.22 | -0.42 | -0.39 | 100% |
| kasper {'lookback': 50, 'tp_R': 2.0} | GBPUSD | 5m | 2021-01-03 → 2026-10-16 | 3691 | 33 % | -0.20 | 0.75 | -100 % | -100 % | 33 % / -0.22 | -0.40 | -0.39 | 100% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | GBPUSD | 1h | 2021-01-03 → 2026-10-16 | 582 | 32 % | -0.05 | 0.93 | -29 % | -34 % | 31 % / -0.08 | -0.07 | -0.02 | 40% |
| deleuze {'n': 2, 'tp_R': 2.0} | AUDUSD | 5m | 2021-01-03 → 2026-10-16 | 2081 | 25 % | -0.09 | 0.84 | -88 % | -92 % | 24 % / -0.15 | -0.18 | -0.13 | 80% |
| deleuze {'n': 3, 'tp_R': 2.0} | AUDUSD | 5m | 2021-01-03 → 2026-10-16 | 906 | 26 % | -0.04 | 0.92 | -37 % | -57 % | 25 % / -0.12 | -0.12 | -0.09 | 90% |
| kasper {'lookback': 20, 'tp_R': 2.0} | AUDUSD | 5m | 2021-01-03 → 2026-10-16 | 4804 | 34 % | -0.19 | 0.77 | -100 % | -100 % | 34 % / -0.20 | -0.39 | -0.35 | 100% |
| kasper {'lookback': 50, 'tp_R': 2.0} | AUDUSD | 5m | 2021-01-03 → 2026-10-16 | 3464 | 34 % | -0.19 | 0.76 | -100 % | -100 % | 33 % / -0.22 | -0.39 | -0.33 | 100% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | AUDUSD | 1h | 2021-01-03 → 2026-10-16 | 590 | 31 % | -0.10 | 0.86 | -48 % | -52 % | 30 % / -0.11 | -0.12 | -0.04 | 27% |
| deleuze {'n': 2, 'tp_R': 2.0} | USDJPY | 5m | 2021-01-03 → 2026-10-16 | 2030 | 26 % | -0.06 | 0.89 | -75 % | -77 % | 26 % / -0.06 | -0.14 | -0.12 | 100% |
| deleuze {'n': 3, 'tp_R': 2.0} | USDJPY | 5m | 2021-01-03 → 2026-10-16 | 886 | 27 % | -0.02 | 0.97 | -21 % | -30 % | 26 % / -0.06 | -0.09 | -0.07 | 100% |
| kasper {'lookback': 20, 'tp_R': 2.0} | USDJPY | 5m | 2021-01-03 → 2026-10-16 | 4721 | 33 % | -0.18 | 0.77 | -100 % | -100 % | 32 % / -0.23 | -0.36 | -0.32 | 100% |
| kasper {'lookback': 50, 'tp_R': 2.0} | USDJPY | 5m | 2021-01-03 → 2026-10-16 | 3478 | 32 % | -0.19 | 0.76 | -100 % | -100 % | 31 % / -0.24 | -0.35 | -0.27 | 100% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | USDJPY | 1h | 2021-01-03 → 2026-10-16 | 500 | 36 % | +0.06 | 1.08 | 25 % | -22 % | 35 % / +0.05 | +0.04 | +0.00 | 77% |
| deleuze {'n': 2, 'tp_R': 2.0} | USDCAD | 5m | 2021-01-03 → 2026-10-16 | 2162 | 25 % | -0.13 | 0.78 | -95 % | -95 % | 25 % / -0.13 | -0.24 | -0.19 | 100% |
| deleuze {'n': 3, 'tp_R': 2.0} | USDCAD | 5m | 2021-01-03 → 2026-10-16 | 931 | 25 % | -0.12 | 0.80 | -71 % | -75 % | 24 % / -0.14 | -0.23 | -0.15 | 80% |
| kasper {'lookback': 20, 'tp_R': 2.0} | USDCAD | 5m | 2021-01-03 → 2026-10-16 | 5250 | 34 % | -0.23 | 0.72 | -100 % | -100 % | 34 % / -0.28 | -0.50 | -0.45 | 100% |
| kasper {'lookback': 50, 'tp_R': 2.0} | USDCAD | 5m | 2021-01-03 → 2026-10-16 | 4106 | 33 % | -0.25 | 0.70 | -100 % | -100 % | 33 % / -0.29 | -0.52 | -0.45 | 100% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | USDCAD | 1h | 2021-01-03 → 2026-10-16 | 506 | 35 % | +0.02 | 1.02 | 3 % | -32 % | 40 % / +0.16 | -0.01 | -0.03 | 83% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | SOLUSDT | 4h | 2020-09-14 → 2026-10-20 | 216 | 37 % | +0.05 | 1.07 | 9 % | -17 % | 37 % / +0.06 | +0.00 | -0.04 | 90% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | BTCUSDT | 4h | 2020-09-14 → 2026-10-19 | 234 | 34 % | -0.07 | 0.90 | -17 % | -21 % | 36 % / -0.02 | -0.16 | -0.10 | 67% |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | ETHUSDT | 4h | 2020-09-14 → 2026-10-20 | 228 | 33 % | -0.08 | 0.89 | -19 % | -28 % | 30 % / -0.17 | -0.15 | -0.06 | 47% |

Forex = vraies cotations FXCM (bid/ask, 1 minute agrégée), coût = spread réel de la barre d'entrée + 0,1 pip.


## Ray Fu : croisement 20/50 jours

| Marché | Version | Trades | Réussite | ≤ 2023 : rendement/an, pire baisse, Sharpe | 2024+ : rendement/an, pire baisse, Sharpe |
|---|---|---|---|---|---|
| AAPL | croisement 20/50 (vidéo) | 75 | 53 % | +15%, -79%, 0.63 | +11%, -24%, 0.64 |
| AAPL | acheter-garder | 1 | 100 % | +25%, -82%, 0.77 | +24%, -33%, 0.90 |
| SPY | croisement 20/50 (vidéo) | 69 | 49 % | +4%, -31%, 0.37 | +13%, -10%, 1.17 |
| SPY | acheter-garder | 1 | 100 % | +7%, -55%, 0.45 | +20%, -20%, 1.26 |
| BTCUSDT | croisement 20/50 (vidéo) | 37 | 41 % | +41%, -76%, 0.92 | +19%, -39%, 0.66 |
| BTCUSDT | acheter-garder | 1 | 100 % | +43%, -83%, 0.86 | +27%, -53%, 0.74 |

## Augmenter le taux de réussite : hypothèses testées

H1 objectif à 1R · H2 seulement dans le sens de la moyenne 50 jours · H3 pas de stop trop serré · H4 = les trois · H5 bougie de retournement (suggestion de la vidéo de Roro). Acceptée seulement si la réussite monte ET le R moyen ne baisse pas, en développement ET en test (≥ 30 trades).

| Stratégie | Marché | Unité | Base test : réussite / R | H1 | H2 | H3 | H4 | H5 | Acceptées |
|---|---|---|---|---|---|---|---|---|---|
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 1h | 39 % / -0.26 | 49 % / -0.27 | 39 % / -0.27 | 38 % / -0.25 | 47 % / -0.26 | 40 % / -0.24 | H4, H5 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 2h | 40 % / -0.16 | 50 % / -0.17 | 39 % / -0.18 | 40 % / -0.15 | 49 % / -0.16 | 39 % / -0.18 | aucune |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 4h | 40 % / -0.10 | 48 % / -0.14 | 39 % / -0.13 | 40 % / -0.10 | 49 % / -0.12 | 41 % / -0.09 | H5 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | SOLUSDT | 1d | 34 % / -0.19 | 45 % / -0.14 | 37 % / -0.11 | 34 % / -0.18 | 47 % / -0.09 | 33 % / -0.21 | H2 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 1h | 39 % / -0.45 | 47 % / -0.48 | 39 % / -0.47 | 39 % / -0.41 | 47 % / -0.43 | 39 % / -0.45 | H4 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 2h | 41 % / -0.28 | 48 % / -0.33 | 40 % / -0.30 | 40 % / -0.26 | 48 % / -0.29 | 40 % / -0.29 | aucune |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 4h | 37 % / -0.27 | 48 % / -0.26 | 37 % / -0.27 | 38 % / -0.24 | 48 % / -0.22 | 37 % / -0.27 | H1, H3, H4 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | BTCUSDT | 1d | 39 % / -0.09 | 50 % / -0.07 | 42 % / -0.02 | 37 % / -0.15 | 50 % / -0.06 | 44 % / +0.04 | H1, H2, H4, H5 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 1h | 40 % / -0.30 | 48 % / -0.34 | 40 % / -0.31 | 40 % / -0.29 | 48 % / -0.31 | 39 % / -0.33 | aucune |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 2h | 39 % / -0.23 | 48 % / -0.26 | 39 % / -0.22 | 40 % / -0.20 | 48 % / -0.23 | 40 % / -0.21 | H5 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 4h | 38 % / -0.19 | 49 % / -0.17 | 39 % / -0.17 | 37 % / -0.20 | 48 % / -0.17 | 39 % / -0.16 | H1, H2, H4, H5 |
| roro {'atr_mult': 1.0, 'tp_R': 1.5} | ETHUSDT | 1d | 43 % / +0.03 | 55 % / +0.05 | 45 % / +0.06 | 43 % / +0.03 | 58 % / +0.11 | 38 % / -0.09 | H1, H2, H4 |
| deleuze {'n': 2, 'tp_R': 2.0} | EURUSD | 5m | 25 % / -0.06 | 52 % / -0.02 | 24 % / -0.08 | 25 % / -0.04 | 52 % / -0.02 | 25 % / -0.06 | H3, H4 |
| deleuze {'n': 3, 'tp_R': 2.0} | EURUSD | 5m | 24 % / -0.07 | 51 % / -0.03 | 25 % / -0.05 | 25 % / -0.03 | 52 % / -0.02 | 24 % / -0.07 | aucune |
| kasper {'lookback': 20, 'tp_R': 2.0} | EURUSD | 5m | 32 % / -0.21 | 44 % / -0.29 | 32 % / -0.22 | 34 % / -0.10 | 47 % / -0.16 | 32 % / -0.12 | H3 |
| kasper {'lookback': 50, 'tp_R': 2.0} | EURUSD | 5m | 31 % / -0.24 | 44 % / -0.29 | 31 % / -0.23 | 32 % / -0.15 | 46 % / -0.18 | 32 % / -0.13 | H2, H3 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | EURUSD | 1h | 36 % / +0.04 | 53 % / +0.03 | 39 % / +0.12 | 35 % / +0.02 | 56 % / +0.07 | 36 % / +0.06 | H2, H4 |
| deleuze {'n': 2, 'tp_R': 2.0} | GBPUSD | 5m | 25 % / -0.12 | 47 % / -0.14 | 24 % / -0.14 | 25 % / -0.09 | 46 % / -0.14 | 25 % / -0.12 | aucune |
| deleuze {'n': 3, 'tp_R': 2.0} | GBPUSD | 5m | 23 % / -0.15 | 46 % / -0.15 | 24 % / -0.17 | 22 % / -0.16 | 44 % / -0.18 | 23 % / -0.15 | aucune |
| kasper {'lookback': 20, 'tp_R': 2.0} | GBPUSD | 5m | 33 % / -0.22 | 44 % / -0.32 | 33 % / -0.22 | 35 % / -0.08 | 49 % / -0.14 | 30 % / -0.19 | H3, H4 |
| kasper {'lookback': 50, 'tp_R': 2.0} | GBPUSD | 5m | 33 % / -0.22 | 44 % / -0.31 | 31 % / -0.28 | 34 % / -0.10 | 49 % / -0.13 | 30 % / -0.18 | H3, H4 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | GBPUSD | 1h | 31 % / -0.08 | 48 % / -0.06 | 27 % / -0.20 | 31 % / -0.10 | 45 % / -0.12 | 31 % / -0.10 | aucune |
| deleuze {'n': 2, 'tp_R': 2.0} | AUDUSD | 5m | 24 % / -0.15 | 48 % / -0.14 | 27 % / -0.08 | 24 % / -0.13 | 50 % / -0.09 | 24 % / -0.15 | H4 |
| deleuze {'n': 3, 'tp_R': 2.0} | AUDUSD | 5m | 25 % / -0.12 | 48 % / -0.13 | 27 % / -0.05 | 24 % / -0.14 | 50 % / -0.07 | 25 % / -0.12 | aucune |
| kasper {'lookback': 20, 'tp_R': 2.0} | AUDUSD | 5m | 34 % / -0.20 | 47 % / -0.30 | 34 % / -0.22 | 36 % / -0.08 | 50 % / -0.14 | 37 % / -0.02 | H3, H5 |
| kasper {'lookback': 50, 'tp_R': 2.0} | AUDUSD | 5m | 33 % / -0.22 | 44 % / -0.33 | 33 % / -0.25 | 35 % / -0.09 | 47 % / -0.20 | 37 % / -0.01 | H3, H4, H5 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | AUDUSD | 1h | 30 % / -0.11 | 46 % / -0.09 | 30 % / -0.12 | 30 % / -0.12 | 47 % / -0.06 | 29 % / -0.14 | H1, H4 |
| deleuze {'n': 2, 'tp_R': 2.0} | USDJPY | 5m | 26 % / -0.06 | 50 % / -0.08 | 27 % / -0.07 | 25 % / -0.05 | 46 % / -0.14 | 26 % / -0.06 | aucune |
| deleuze {'n': 3, 'tp_R': 2.0} | USDJPY | 5m | 26 % / -0.06 | 50 % / -0.07 | 26 % / -0.09 | 26 % / -0.02 | 45 % / -0.16 | 26 % / -0.06 | H3 |
| kasper {'lookback': 20, 'tp_R': 2.0} | USDJPY | 5m | 32 % / -0.23 | 44 % / -0.31 | 32 % / -0.21 | 33 % / -0.14 | 47 % / -0.18 | 35 % / -0.06 | H3, H4, H5 |
| kasper {'lookback': 50, 'tp_R': 2.0} | USDJPY | 5m | 31 % / -0.24 | 44 % / -0.29 | 31 % / -0.23 | 31 % / -0.17 | 48 % / -0.15 | 35 % / -0.06 | H2, H3, H4 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | USDJPY | 1h | 35 % / +0.05 | 51 % / +0.01 | 35 % / +0.02 | 36 % / +0.06 | 50 % / -0.01 | 33 % / -0.02 | H3 |
| deleuze {'n': 2, 'tp_R': 2.0} | USDCAD | 5m | 25 % / -0.13 | 48 % / -0.15 | 28 % / -0.02 | 24 % / -0.13 | 51 % / -0.06 | 25 % / -0.13 | H4 |
| deleuze {'n': 3, 'tp_R': 2.0} | USDCAD | 5m | 24 % / -0.14 | 47 % / -0.14 | 27 % / +0.00 | 25 % / -0.10 | 55 % / +0.03 | 24 % / -0.14 | H4 |
| kasper {'lookback': 20, 'tp_R': 2.0} | USDCAD | 5m | 34 % / -0.28 | 46 % / -0.36 | 34 % / -0.26 | 34 % / -0.15 | 49 % / -0.18 | 33 % / -0.16 | H2, H3, H4 |
| kasper {'lookback': 50, 'tp_R': 2.0} | USDCAD | 5m | 33 % / -0.29 | 45 % / -0.37 | 33 % / -0.27 | 32 % / -0.21 | 48 % / -0.20 | 32 % / -0.18 | H4 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | USDCAD | 1h | 40 % / +0.16 | 50 % / -0.02 | 41 % / +0.21 | 40 % / +0.18 | 52 % / +0.01 | 39 % / +0.13 | H3 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | SOLUSDT | 4h | 37 % / +0.06 | 47 % / -0.12 | 35 % / -0.01 | 38 % / +0.08 | 42 % / -0.22 | 38 % / +0.07 | H5 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | BTCUSDT | 4h | 36 % / -0.02 | 53 % / -0.05 | 44 % / +0.22 | 35 % / -0.04 | 58 % / +0.06 | 36 % / -0.02 | H2, H4 |
| nico (approximation) {'atr_mult': 2.0, 'tp_R': 2.0} | ETHUSDT | 4h | 30 % / -0.17 | 46 % / -0.15 | 34 % / -0.06 | 31 % / -0.13 | 56 % / +0.05 | 29 % / -0.19 | H2, H4 |

## Synthèse

- Variantes testées : **240** (stratégies × marchés × unités × hypothèses). Variantes gagnantes à la fois en développement (≤ 2023) ET en test (2024+) : **14**.
- « Bat le hasard » compare aux mêmes stops et objectifs avec des entrées au hasard : avec des stops très serrés, le hasard perd beaucoup à cause des coûts ; battre le hasard ne veut donc PAS dire gagner de l'argent.
- Une hypothèse « acceptée » améliore la réussite sans baisser le R moyen ; la stratégie peut rester perdante.
- Incertitude : avec 100 trades, le R moyen est connu à environ ± 0,13 R près (règle approximative : 1,3 / √n). Aucune des variantes ci-dessous ne dépasse nettement cette marge, et sur 240 essais, quelques-unes devaient passer par hasard.

| Stratégie | Marché | Unité | Variante | Dév. : trades / réussite / R | Test : trades / réussite / R |
|---|---|---|---|---|---|
| nico (approximation) | BTCUSDT | 4h | H2 | 71 / 39 % / +0.09 | 63 / 44 % / +0.22 |
| nico (approximation) | EURUSD | 1h | H2 | 166 / 35 % / +0.03 | 131 / 39 % / +0.12 |
| roro | ETHUSDT | 1d | H4 | 115 / 54 % / +0.03 | 128 / 58 % / +0.11 |
| nico (approximation) | SOLUSDT | 4h | H3 | 94 / 35 % / +0.02 | 101 / 38 % / +0.08 |
| nico (approximation) | SOLUSDT | 4h | H5 | 100 / 36 % / +0.04 | 109 / 38 % / +0.07 |
| roro | ETHUSDT | 1d | H2 | 106 / 42 % / +0.01 | 101 / 45 % / +0.06 |
| nico (approximation) | BTCUSDT | 4h | H4 | 71 / 58 % / +0.09 | 55 / 58 % / +0.06 |
| nico (approximation) | USDJPY | 1h | H3 | 259 / 36 % / +0.06 | 236 / 36 % / +0.06 |
| nico (approximation) | SOLUSDT | 4h | base | 103 / 36 % / +0.04 | 113 / 37 % / +0.06 |
| nico (approximation) | USDJPY | 1h | base | 260 / 36 % / +0.06 | 240 / 35 % / +0.05 |
| nico (approximation) | ETHUSDT | 4h | H4 | 57 / 61 % / +0.18 | 59 / 56 % / +0.05 |
| roro | BTCUSDT | 1d | H5 | 98 / 44 % / +0.04 | 108 / 44 % / +0.04 |
| nico (approximation) | USDJPY | 1h | H2 | 147 / 35 % / +0.04 | 139 / 35 % / +0.02 |
| nico (approximation) | USDJPY | 1h | H1 | 313 / 56 % / +0.10 | 279 / 51 % / +0.01 |

**Statut : aucune stratégie des vidéos n'est validée.** Les meilleures variantes sont à placer, au mieux, en suivi papier (données futures) avant toute conclusion.
