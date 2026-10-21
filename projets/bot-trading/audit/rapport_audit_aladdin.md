# Audit quantitatif indépendant — Aladdin

Date : 2026-10-20. Périmètre : `aladdin/` (donnees, desks, moteur, recherche, reussite, enquete, sorties, live, live_rebond, alpaca) et ses rapports dans `resultats/`. `bot/` vu en second plan seulement.
Données : cache `data/` tel que trouvé le 2026-10-20 (crypto Binance jusqu'au 2026-10-16, Yahoo SPY/GC=F/TLT jusqu'au 2026-10-16). Données SUPPLÉMENTAIRES de l'audit (GLD, OHLC SPY/GC=F, cryptos 2020 BCH/LTC/EOS/XTZ) téléchargées dans `audit/donnees/` uniquement. Aucun fichier existant modifié, aucun commit.

Structures auditées :
- **A. « Aladdin momentum crypto »** : `momentum 120 j | crypto | vol cible` (`resultats/aladdin_structure.txt`), présentée avec « walk-forward +22 %/an » et « coffre-fort +5,5 % ».
- **B. « Aladdin Rebond »** : RSI2 < 5 et cours > MM200, objectif +1 %, stop -10 %, 20 séances, SPY + or 50/50 (`resultats/aladdin_sortie_retenue.txt`), présentée avec « 84 / 78 / 79 % de réussite ».

Scripts (tous dans `audit/`, à lancer depuis `projets/bot-trading`) :

| Script | Contenu | Sortie |
|---|---|---|
| `python3 audit/a00_reproduire.py` | relance `main()` de recherche, reussite, enquete, sorties avec `ICI` redirigé (aucune écriture dans `resultats/`) | `audit/sorties/repro/resultats/` |
| `python3 audit/a01_donnees.py` | qualité des données, jours reportés, GC=F vs GLD | `audit/sorties/a01_donnees.md` |
| `python3 audit/a02_rebond.py` | Rebond : reproduction, coûts, exécution, crises, données manquantes, voisins, hasard, bootstrap, DSR | `audit/sorties/a02_rebond.md` |
| `python3 audit/a03_momentum.py` | Momentum : idem + survivance, corrélation | `audit/sorties/a03_momentum.md` |
| `python3 audit/a04_alpaca.py` | alpaca.py testé hors ligne avec une fausse API | `audit/sorties/a04_alpaca.md` |
| `python3 audit/a05_divers.py` | comptage des essais, walk-forward retardé, annualisation | `audit/sorties/a05_divers.md` |

---

## 1. Anomalies confirmées

Chaque anomalie ci-dessous est confirmée par exécution (E) ou par lecture du code avec démonstration (C).

1. **Le « walk-forward +22 %/an » n'est pas celui de la structure momentum crypto présentée (E).** `recherche.py:83-88` choisit chaque année parmi 48 candidats. Les données Binance commencent le 2020-01-01 (`bot/data.py:31`, `debut="2020-01-01"`) et `recherche.sharpe` exige 730 jours (`recherche.py:60`) : aucun candidat crypto n'est sélectionnable avant 2023 (0/24 candidats crypto évaluables de 2017 à 2022). Six années sur huit (2017-2022) sont des **moyennes mobiles multi-actifs**. La part crypto (2023-2024) fait +81,5 % cumulés. La structure finale n'a été hors échantillon qu'en 2024 (dans le walk-forward) puis en 2025+. Commande : `python3 audit/a03_momentum.py` (§1).
2. **Le coffre-fort 2025+ n'est pas vierge pour Rebond (C).** `reussite.py:174` et `:203-209`, `enquete.py:189-194` puis `sorties.py:26,36` calculent et **affichent les résultats 2025+ de nombreuses variantes avant le choix final**. Le tableau de sorties.py montre la colonne 2025+ pour les 12 meilleurs réglages. La règle a été « figée le 2026-10-15 » (`live_rebond.py`, docstring) après tout cela. Par ailleurs, 2020-2024 sert aussi à la sélection : `sorties.py:37` retient le premier réglage qui atteint ≥ 70 % **en validation** ; reussite.py:182-190 choisit la méthode de sélection sur 2020-2024. Seul 2025+ reste « à demi » hors échantillon, avec 14 trades.
3. **Des trades encore ouverts sont comptés comme clos (E).** `reussite.simuler` et `enquete.simuler_momentum` clôturent à la dernière barre (`s = min(j + 1, n - 1)`, `reussite.py:61`, `enquete.py:67`), sans marqueur. Exemple : le trade ACTIONS entré le 2026-10-01 dans `aladdin_enquete.md` était compté **gagnant (+0,63 %) au 2026-10-14**, et devient perdant (-0,20 %) au 2026-10-16. Il fait passer la réussite 2025+ « Rebond (actions + or) » de 76 % (rapporté) à 72 % (relancé). Pour la structure finale RSI2<5, l'effet est nul aujourd'hui (aucun trade ouvert).
4. **`live_rebond.py` suit une AUTRE règle que celle qui a donné 84/78/79 % (E).** `live_rebond.py:29` appelle `reussite.portefeuille`, qui travaille sur le calendrier 7j/7 avec week-ends reportés (`donnees.py:47-50`). Dans ce moteur, `rolling(200)` couvre 200 jours calendaires (≈ 138 séances) et `duree=20` compte 20 jours calendaires. Les 84/78/79 % viennent de `enquete.executer`, qui travaille en séances (`enquete.py:78`). Relancé, le moteur de live_rebond donne **76 % (178 trades) / 71 % (75) / 75 % (32)**, contre 84 % (89) / 78 % (40) / 79 % (14). Le suivi papier ne mesure donc pas la structure annoncée.
5. **Regard vers le futur dans `reussite.simuler` sur calendrier 7j/7 (E).** « Entrée à la clôture suivante » (`reussite.py:46`) et « sortie à la clôture suivante » (`:61`) tombent sur un samedi reporté quand le signal ou le déclenchement a lieu un vendredi ou une veille de jour férié. Le prix d'exécution est alors **la clôture même du signal**. Pour RSI2<5 sur SPY + or : 21 entrées sur 285 et **57 sorties** se font ainsi. Une sortie de ce type encaisse exactement le cours qui a déclenché l'objectif. Cela concerne les 1 350 combinaisons de reussite.py (dont l'univers « actions+or » d'où vient Rebond) et le moteur de live_rebond. `python3 audit/a01_donnees.py`.
6. **`enquete.py:78` supprime aussi de vraies séances (E).** Le filtre `c.diff().ne(0)` retire les week-ends reportés, mais aussi 13 séances SPY et 25 séances GC=F réelles à variation nulle. Effet faible, mais l'historique de travail n'est plus le vrai calendrier.
7. **« Rendement cumulé des trades » ≠ rendement du portefeuille (E).** sorties.py affiche la somme des log-rendements des trades (`enquete.py:111`), alors que chaque trade n'engage que la moitié du capital. 2020-24 : **+38 % affichés contre +20,6 % pour le portefeuille 50/50 réel**. 2025+ : +13 % contre +8,2 %.
8. **Instrument backtesté ≠ instrument traité (E).** Le backtest utilise GC=F, un future continu non ajusté. `alpaca.py` trade GLD. Corrélation quotidienne GC=F/GLD : **0,886** seulement (clôtures à des heures différentes), et 313 jours sur 5 224 avec un écart > 1 %. Les signaux RSI-2 diffèrent donc. Sur SPY + GLD, Rebond fait 82 / 79 / 82 % avec 92 / 39 / 17 trades (contre 84 / 78 / 79 % avec 89 / 40 / 14).
9. **Défaillances d'`alpaca.py` démontrées avec une fausse API (E, `python3 audit/a04_alpaca.py`).**
   - (A) Lancé deux fois le même jour avant la clôture, il envoie **4 ordres d'achat au lieu de 2**. Aucun contrôle des ordres ouverts.
   - (B) Une position présente chez le courtier mais absente du journal prend comme date d'entrée la barre du jour (`alpaca.py:83`). Le compteur vaut donc **0 jour chaque jour** et la sortie à 20 jours ne se déclenche jamais.
   - (C) Avec un marché fermé (`is_open=False`), les ordres partent quand même : l'horloge est seulement affichée (`:73`). Un jour férié, le dernier prix est ajouté comme une nouvelle barre (`:59`).
   - (D) Une erreur HTTP sur GLD après l'ordre SPY fait planter le script **avant l'écriture du journal**, alors que l'ordre SPY est parti. On retombe alors sur (B).
   - (E) La durée est comptée en 28 jours calendaires (`:86`), soit 16 à 20 séances selon les fériés (différente de 20 dans 65 % des cas). Entrée et sortie se font à la clôture du jour du signal, alors que le backtest les place à la clôture suivante.
10. **Le desk risque sous-estime le risque des positions corrélées (E).** `desks.py:55` divise par √n comme si les cryptos étaient indépendantes. Or leur corrélation moyenne quotidienne est de 0,61 (2021+). La volatilité réalisée atteint **20,6 %/an pour une cible de 15 %**, et 23,6 % les jours investis.
11. **Paramètre codé en dur incompatible (E).** `desks.py:51` impose `min_periods=40`, donc une fenêtre de volatilité inférieure à 40 jours lève une erreur (fenêtre 30 testée → `ValueError`).

## 2. Faiblesses probables

- **Biais de survivance (momentum, testé)** : l'univers BTC, ETH, BNB, SOL et XRP est choisi en 2026. SOL n'existait pas sur Binance en janvier 2020. Avec un univers « point dans le temps » (8 grosses cryptos de janvier 2020 : BTC ETH XRP BCH LTC EOS BNB XTZ), le Sharpe ≤ 2024 tombe de **1,84 à 1,22** et le coffre 2025+ de **+5,2 % à -13,0 %**. Avec les 10 cryptos de `bot/data.py`, 2025+ fait -4,3 %. La composition de l'univers de janvier 2020 est reconstituée de mémoire par l'auditeur, sans source datée. LUNA et FTT, effondrés, ne sont pas inclus : le biais réel est sans doute plus fort.
- **Une seule période crypto** : la sélection repose sur 2020-2024, un seul cycle, avec un départ en plein marché haussier. Aucune crise de type 2018 ou 2014 n'est couverte. Le krach de mars 2020 et LUNA (mai 2022) donnent 0,0 % parce que la stratégie était hors marché (préchauffage de 120 jours en 2020, filtre de tendance en 2022), pas parce qu'elle a été testée sous stress.
- **Instabilité des paramètres hors échantillon (momentum)** : en 2025+, les lookbacks voisins donnent de -14,0 % (250 j) à +18,1 % (60 j). Avec 150 j : -3,5 %, avec 90 j : +2,9 %, avec 120 j : +5,2 %. Sans le desk risque (parts égales) : -10,4 %. Le Sharpe du coffre vaut **0,24, avec une PSR(Sharpe > 0) de 0,63** : on ne peut pas le distinguer de zéro.
- **Le haut taux de réussite de Rebond vient surtout des sorties** : des entrées au hasard (cours > MM200) avec les mêmes sorties +1 % / -10 % / 20 séances donnent **76 % de réussite médiane** (5e-95e centiles : 73-80 %). La règle reste au 99e centile du hasard, mais sur tout l'historique, y compris les périodes qui ont servi à la choisir parmi 1 572 essais. Gain moyen +1,76 %, perte moyenne -2,85 %, pire trade -11,65 % : la réussite d'équilibre est de 62 %.
- **Rebond rapporte peu et dépend de l'exécution** : le portefeuille fait +3,3 %/an (pire baisse -7,3 %, Sharpe 0,74, investi 22 % du temps), contre +11,6 %/an et un Sharpe de 0,88 pour SPY + or 50/50 gardés. Avec **un jour de retard**, la réussite tombe à 75 / 70 / 69 % et le Sharpe à 0,43. Exécuté à la même clôture (le cas idéal visé par alpaca.py), le PF passe à 1,55 en 2020-24 et 1,12 en 2025+.
- **Échantillon 2025+ trop petit** : 11 gagnants sur 14, intervalle de Wilson à 95 % de **52 à 92 %**. 2020-24 : 62-88 %.
- **Surapprentissage par lignée** : 1 662 variantes en tout (48 + 1 350 + 84 + 180, comptées dans le code par `audit/a05_divers.py`), sans compter `bot/`, déjà testé avant. Le DSR de Rebond vaut 0,876 pour N = 1 572 et la variance de la grille voisine, et **0,217 si la variance entre essais est 4 fois plus grande**. Il reste sous le seuil de 0,95 dans les deux cas.
- **Exécution momentum « à la clôture du signal »** : `moteur.py:11` applique le poids décidé avec la clôture t au rendement de t+1, donc l'achat se fait au cours même qui a produit le signal (00:00 UTC). Testé : un ou deux jours de retard ne dégradent pas la période ≤ 2024. En revanche, dans le panier multi-actifs du walk-forward, les poids SPY/TLT/or utilisent l'information crypto de 00:00 UTC, environ 4 h après la clôture de New York (le walk-forward avec 1 jour de retard donne un Sharpe de 1,23 contre 1,37).
- **Fuseau horaire en direct** : `donnees.py:34` et `bot/data.py:50` filtrent avec `pd.Timestamp.now()`, qui est une heure locale naïve. Sur une machine qui n'est pas réglée en UTC (par exemple Paris), une bougie Binance non clôturée peut être incluse après minuit local. Non démontré ici, car le conteneur est en UTC.
- **Qualité de GC=F sur Yahoo** : 457 séances ont une ouverture égale à la clôture (ouvertures inexploitables). Le contrat est continu sans ajustement de roulement. Les écarts avec GLD dépassent 6 à 8 % certains jours (septembre 2008, mars 2009).
- **Stop évalué seulement à la clôture et exécuté le lendemain** : un trade OR (2008-07-31) est sorti à -11,7 % pour un stop à -10 %. Le bootstrap ne peut pas produire de perte pire que celles observées : un gap plus grand (type krach de 1987) est absent de l'échantillon.

## 3. Tests non effectués

- Exécution à l'ouverture suivante **sur GC=F** : ouvertures Yahoo inexploitables, test fait sur GLD à la place.
- Objectif et stop intrajournaliers (plus haut / plus bas) : non modélisés.
- Cryptos retirées de la cote (LUNA, FTT, etc.) : pas de série propre, le symbole LUNAUSDT a été réattribué en 2022.
- Crise 2008 et 2018 pour le momentum crypto : aucune donnée crypto avant 2020.
- Exécution réelle sur Alpaca (paper ou réel) : pas de clés. Écart MOC / clôture Yahoo et flux IEX non mesurés.
- PBO / CSCV (probabilité de surapprentissage) : non calculés. DSR seulement, avec une variance entre essais approchée par des grilles voisines ; la variance réelle des 1 572 essais n'a pas été mesurée.
- Révisions des cours ajustés Yahoo dans le temps : seul un écart de 5,7e-7 a été observé entre deux versions ; les clichés de données des rapports d'origine n'ont pas été conservés.
- Rémunération du cash, impôts, financement : non modélisés.
- `bot/` (agents, backtest, or_systeme) : non relancé, lu seulement en second plan.
- `live.py` : le bug de fuseau horaire n'a pas été démontré, le conteneur étant en UTC.
- Scénarios de choc au-delà des pertes historiques dans le bootstrap : non faits.

## 4. Résultats reproduits

| Chiffre rapporté | Relancé (audit) | Commande |
|---|---|---|
| Walk-forward 2017-2024 : +401,8 %, +22,3 %/an, pire baisse -33,2 %, Sharpe 1,37 | **identique** | `python3 audit/a00_reproduire.py recherche` ; `python3 audit/a03_momentum.py` |
| Top 12 et choix « momentum 120 j \| crypto \| vol cible » (Sharpe 1,84, +46,3 %/an ≤ 2024) | **identique** | idem |
| Coffre momentum +5,5 % (au 2026-10-14) | +5,2 % au 2026-10-16 : 2 jours de plus, cohérent | idem |
| Rebond 84 % (89) / 78 % (40) / 79 % (14), PF 2,72 / 3,15 / 2,37, « +76 / +38 / +13 % » | **identique**, et moteur d'audit égal trade par trade à `enquete.executer` | `python3 audit/a00_reproduire.py sorties` ; `python3 audit/a02_rebond.py` |
| `aladdin_sorties.md` complet | **identique** (diff vide) | `diff audit/sorties/repro/resultats/aladdin_sorties.md resultats/aladdin_sorties.md` |
| reussite.py ≤ 2024 (1 350 combinaisons, choix crypto plus bas 3 j, 61 %, 576 trades) | **identique** | `python3 audit/a00_reproduire.py reussite` |

Résultats de l'audit lui-même (reproductibles, graines fixes) :

- **Rebond**, selon la variante (réussite 2006-19 / 2020-24 / 2025+, Sharpe du portefeuille) :

  | Variante | Réussite 2006-19 / 2020-24 / 2025+ | Sharpe portefeuille |
  |---|---|---|
  | Frais ×2 | 82 / 78 / 79 % | 0,66 |
  | Frais ×3 | 82 / 78 / 79 % | 0,58 |
  | Ouverture suivante (SPY + GLD) | 86 / 79 / 89 % | 0,64 |
  | Ouverture suivante + frais ×3 | — | 0,47 |
  | Un jour de retard | 75 / 70 / 69 % | 0,43 |
  | 5 % des séances retirées (50 tirages) | médiane 83 / 78 / 77 %, 2025+ entre 67 et 87 % | médiane 0,64 [0,41-0,87] |

  - Les paramètres voisins RSI 3/5/7/10 × objectif 0,5-2 % × stop 5/10/15 % sont stables (Sharpe de 0,32 à 0,99, médiane 0,68). La réussite 2025+ dépasse 70 % pour 44 voisins sur 48.
  - En crise : 2008 → -0,8 % (pire baisse -6,0 %), contre -15,3 % en gardant SPY + or ; mars 2020 → +0,7 % ; 2022 → -0,6 %.
  - Bootstrap des trades (7,3 trades/an, 50 % du capital par trade, 10 ans) :

    | Mesure | Valeur |
    |---|---|
    | Pire baisse médiane | -5,8 % |
    | Pire baisse, 1er centile | -14,5 % |
    | P(pire baisse ≥ 20 %) | 0,07 % |
    | P(pire baisse ≥ 50 %, « ruine ») | ≈ 0 |
    | P(perte sur 10 ans) | 0,2 % |
    | P(pire baisse ≥ 20 %), variante 100 % du capital par trade | 3,2 % |
    | P(pire baisse ≥ 20 %), bootstrap par blocs | 0,4 % |

    Ces résultats ne tiennent que sous l'hypothèse d'indépendance des trades et de pertes bornées par l'historique.

- **Momentum** :
  - Frais ×2 : coffre +2,8 %. Frais ×3 : +0,5 % (Sharpe ≤ 2024 : 1,79 et 1,73).
  - Un jour de retard : ≤ 2024 inchangé, coffre +3,9 %. Deux jours : +2,7 %.
  - 5 % des jours retirés : coffre médian +1,4 % [-7,1 % ; +7,2 %].
  - Bootstrap par blocs (2020-2026) : P(perte sur 1 an) = 11 %, pire baisse à 3 ans au 5e centile -30,9 %, P(baisse ≥ 30 % en 3 ans) = 6,1 %. 39 % des mois sont perdants, pire mois -12,0 %.
  - DSR ≤ 2024 : 0,974 pour N = 48, 0,955 pour N = 100. Mais ces 5 ans ne couvrent qu'un seul cycle, et le coffre a une PSR de 0,63.

## 5. Résultats non reproductibles

- **`aladdin_enquete.md`, Rebond (actions + or), 2025+** : « 76 %, PF 2,11, +41 % » rapporté, contre **72 %, PF 2,08, +40 %** relancé. La cause est un trade ouvert valorisé comme clos (anomalie 3). Les médianes gagnants/perdants et le partage des causes changent aussi (85 → 86 perdants).
- **`aladdin_enquete.md`, Momentum, 2025+** : PF 1,04 / -8 % rapporté, contre 1,02 / -10 % relancé (2 jours de plus et une position ouverte).
- **`aladdin_reussite.md`, étape 3** : 143 trades et -22,7 % rapportés, contre 144 trades et -23,3 % relancés (même cause).
- **Taux de 84/78/79 % via le code de suivi** : `live_rebond.py` donne 76/71/75 % (anomalie 4). Le chiffre annoncé ne se reproduit pas avec le code utilisé en direct.
- **Clichés de données** : les rapports ont été produits avec des données au 2026-10-14. Le cache `data/` a été rafraîchi depuis (jusqu'au 2026-10-16) et l'ancienne version n'est pas conservée, donc les chiffres « coffre » et « 2025+ » ne sont pas reproductibles à l'identique. Les chiffres ≤ 2024 le sont.

## 6. Améliorations recommandées

1. **Moteur unique en séances** pour le backtest, le suivi papier et Alpaca : supprimer `reussite.portefeuille` et le calendrier 7j/7 pour les actifs traditionnels. Faire réutiliser à `live_rebond.py` exactement `enquete.executer` (ou une fonction commune).
2. **Marquer les trades ouverts** et les exclure de toutes les statistiques de réussite et de PF.
3. **Rapporter le rendement du portefeuille**, pas la somme des rendements de trades. Ajouter systématiquement la comparaison au panier gardé et à des entrées au hasard avec les mêmes sorties.
4. **Vrai coffre** : geler un cliché daté des données, ne plus afficher aucune colonne 2025+ pendant la sélection, et consigner chaque essai dans un registre (N réel pour le DSR, PBO/CSCV).
5. **Walk-forward honnête** : présenter le walk-forward de la structure crypto seule. Pour le momentum, ajouter des données crypto antérieures à 2020 (Binance dès 2017, ou d'autres sources) et un univers point dans le temps qui inclut les actifs effondrés.
6. **Rebond : trader l'instrument backtesté** (backtest sur GLD ou trader le future), et aligner l'exécution : soit backtester « même clôture » (et l'assumer), soit envoyer l'ordre le lendemain.
7. **alpaca.py** :
   - refuser de tourner si `is_open` est faux ou après 15 h 50 ET ;
   - interroger `/v2/orders?status=open` avant tout envoi et utiliser `client_order_id` déterministe (date + symbole) pour l'idempotence ;
   - entourer chaque appel d'un try/except et écrire le journal après chaque ordre ;
   - ne pas prendre « aujourd'hui » comme date d'entrée par défaut (lire `/v2/account/activities` ou les ordres exécutés) ;
   - prendre le prix d'entrée réel (`filled_avg_price`) ;
   - compter la durée en séances avec `/v2/calendar` ;
   - utiliser le flux SIP pour les clôtures.
8. **Desk risque** : estimer la covariance (et non pas diviser par √n), rendre `min_periods` cohérent avec `fenetre`, et vérifier la volatilité réalisée par rapport à la cible.
9. **Fuseau horaire** : utiliser `pd.Timestamp.now(tz="UTC")` dans `donnees.py:34` et `bot/data.py:50`.

## 7. Décision par structure

| Structure | Décision | Justification courte | Commandes pour relancer |
|---|---|---|---|
| **A. Aladdin momentum crypto** (momentum 120 j, 5 cryptos, vol cible) | **REJET (en l'état)** | Le « +22 %/an » appartient à d'autres structures (anomalie 1). La seule preuve hors échantillon (coffre 2025+) a un Sharpe de 0,24 (PSR 0,63), soit pas mieux que zéro. Le résultat dépend fortement du choix de l'univers fait en 2026 (point dans le temps : -13 % en 2025+) et du lookback (-14 % à +18 % en 2025+). La sélection repose sur un seul cycle crypto (2020-2024). Un nouveau test ne serait envisageable qu'avec un univers point dans le temps et des données antérieures à 2020. Conclusion **provisoire** : échantillon hors échantillon de 21 mois. | `python3 audit/a00_reproduire.py recherche` ; `python3 audit/a03_momentum.py` ; `python3 audit/a05_divers.py` |
| **B. Aladdin Rebond** (RSI2<5, +1 % / -10 % / 20 séances, SPY + or) | **VALIDATION LIMITÉE À LA DÉMO (paper), après correction des anomalies 4, 8 et 9** | La règle résiste aux frais ×3, à 5 % de données manquantes, à GLD, à l'ouverture suivante et à ses voisins, et bat des entrées au hasard. Mais : le taux de réussite vient surtout des sorties (le hasard fait 76 %) ; le rendement est faible (+3,3 %/an, Sharpe 0,74 contre 0,88 pour SPY + or gardés) ; la règle est sensible au retard d'exécution (Sharpe 0,43) ; le DSR vaut 0,876 (< 0,95) pour 1 572 essais ; 2025+ ne compte que 14 trades (IC 52-92 %) et a été vu pendant la sélection. **Aucune décision en argent réel.** Conclusion **provisoire** : il faut au moins 30 à 50 trades réellement hors échantillon, exécutés par le même code que le backtest. | `python3 audit/a00_reproduire.py sorties` ; `python3 audit/a02_rebond.py` ; `python3 audit/a01_donnees.py` ; `python3 audit/a04_alpaca.py` |

Aucune des deux structures n'est validée sur la base d'un seul backtest. Les deux conclusions sont provisoires faute d'échantillon hors échantillon suffisant.
