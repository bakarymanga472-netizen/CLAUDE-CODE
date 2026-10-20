"""Rapport lisible à partir de rapports/videos_youtube.json. Usage : python3 -m labo.videos.rapport"""
import json
from pathlib import Path

from . import deleuze, kasper, nico, rayfu, roro

ICI = Path(__file__).resolve().parents[2]


PROFILS = [
    "## Qui sont les auteurs\n",
    "| Vidéo | Auteur | Ce qu'il vend | Preuve publique des résultats |",
    "|---|---|---|---|",
    "| Complete Guide to building an AI Trading Bot | Ray Fu, ex-ingénieur Meta | communauté payante (School), cadeaux d'abonnement | aucune ; il précise lui-même que la stratégie n'est pas « magique » |",
    "| J'ai testé une stratégie créée par Claude pendant 24h | Benjamin Deleuze | ses formations ; il conclut que la stratégie est un « piège à débutant » | trading en direct sur une journée : surtout des stops |",
    "| Créer un Bot de Trading Performant avec Claude Code | Nico Trade | canal Telegram gratuit, challenge de prop firm | indicateur « Kumo Stream » non publié, aucun backtest montré |",
    "| J'ai demandé à Claude de me rapporter le plus d'argent en 1h | Kasper | indicateur offert contre des likes | 1 heure de trading discrétionnaire, +42 € |",
    "| Stratégie ULTRA RENTABLE grâce à l'IA | Roro Crypto (Romain), fondateur d'InvestX (site investx.fr, appli) | groupe privé « gratuit » si on ouvre un compte crypto chez ses partenaires (affiliation), modules de formation | captures TradingView sur des périodes choisies ; la stratégie à 81 % n'est pas publiée |",
    "",
    "**Roro Crypto (Romain, InvestX)** — ce qui est vérifiable :",
    "- Fondateur du média et de l'application InvestX ; audience surtout TikTok/Instagram (≈ 275 000 abonnés TikTok selon un article). "
    "Les articles « avis » trouvés en ligne sont promotionnels ; aucune source indépendante ne vérifie ses performances.",
    "- Modèle économique annoncé dans la vidéo : accès au groupe privé en ouvrant un compte d'échange via ses partenaires. "
    "Une affiliation rémunère généralement sur les frais de trading des filleuls : il gagne quand vous tradez, que vous gagniez ou non.",
    "- Sa stratégie « 40 % de gain, 5 % de baisse, 81 % de réussite, profit factor 8,6 » a été obtenue en ré-optimisant avec Claude, "
    "à partir de la liste des trades du même backtest, en une douzaine de jours : c'est la définition du surapprentissage. "
    "Aucun test sur des données non vues, aucune période fixée à l'avance, et la stratégie n'est pas publiée.",
    "- Sa stratégie de départ (publique) : le même test dans ce labo, avec frais, ne gagne rien (voir plus bas).",
    "",
    "**Ce que ces vidéos apprennent d'utile** (outils, pas stratégies) : Claude Code peut écrire du Pine pour TradingView, "
    "lire l'export CSV des trades, et piloter TradingView Desktop via un serveur MCP (vidéo de Nico Trade) ; "
    "Alpaca se branche à Claude via un MCP pour le paper trading (vidéo de Ray Fu). "
    "Le piège commun : optimiser sur le même historique jusqu'à ce que les chiffres soient beaux.\n",
    "Sources : https://www.youtube.com/@rorovevo · https://t.me/rorovevo · "
    "https://www.bordeaux-gazette.com/annuaire/roro-vevo-avis-qui-est-romain-le-ceo-de-investx/ · "
    "https://startup.info/fr/rorovevo-avis-romain-de-investx-un-entrepreneur-fiable/ · "
    "https://actualites-bourse.com/avis-roro-vevo-romain-de-investx-analyse-du-media-crypto/ · "
    "https://www.tiktok.com/discover/Roro-vevo-arnaque (recherche TikTok, aucune preuve d'arnaque dans les résultats)\n",
]


def p(x, d=0):
    return "—" if x is None else f"{x * 100:.{d}f} %"


def r(x):
    return "—" if x is None else f"{x:+.2f}"


def ligne(m):
    if not m or not m.get("trades"):
        return "0 | — | — | — | — | —"
    return (f"{m['trades']} | {p(m['reussite'])} | {r(m['R_moyen'])} | {m['profit_factor']:.2f} | "
            f"{p(m['rendement_1pct'])} | {p(m['pire_baisse_1pct'])}")


def main():
    o = json.loads((ICI / "rapports" / "videos_youtube.json").read_text())
    L = ["# Les 5 vidéos YouTube : stratégies testées\n",
         "Commandes : `python3 -m labo.videos.tester` puis `python3 -m labo.videos.rapport`. Règles fixées avant exécution : "
         "voir l'en-tête de `labo/videos/tester.py`. Résultats en R (1 R = la perte si le stop est touché) ; "
         "« Rendement 1 % » = capital final en risquant 1 % par trade.\n"] + PROFILS + ["## Ce que disent les vidéos\n"]
    for mod in (rayfu, deleuze, nico, kasper, roro):
        L += [f"### {mod.__doc__.strip()}\n", f"- Lien : {mod.SOURCE}", f"- Règles annoncées : {mod.REGLES}",
              f"- Traduction en code (là où la vidéo est floue) : {mod.TRADUCTION}\n"]
    L += ["## Résultats (coûts réalistes)\n",
          "| Stratégie | Marché | Unité | Période | Trades | Réussite | R moyen | Profit factor | Rendement 1 % | Pire baisse 1 % | Test 2024+ : réussite / R | Coûts ×2 : R | Hasard : R médian | Bat le hasard |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in o["resultats"]:
        t, s, h = x["test"], x["stress_couts_x2"], x["hasard"]
        L.append(f"| {x['strategie']} {x['params']} | {x['symbole']} | {x['unite']} | {x['donnees'].split(' (')[0]} | {ligne(x['tout'])} | "
                 f"{p(t.get('reussite'))} / {r(t.get('R_moyen'))} | {r(s.get('R_moyen'))} | {r(h['R_moyen_median'])} | "
                 f"{'—' if h['percentile_R'] is None else format(h['percentile_R'], '.0%')} |")
    L += ["\nForex long terme = paires EUR/USDT, GBP/USDT, AUD/USDT de Binance (approximation de l'EUR/USD, etc.), coûts forex de détail.\n",
          "## Contrôle sur le vrai forex (Yahoo, 60 derniers jours, 5 min)\n",
          "| Stratégie | Paire | Trades | Réussite | R moyen | Profit factor | Rendement 1 % | Pire baisse 1 % |", "|---|---|---|---|---|---|---|---|"]
    for y in o["yahoo_60j"]:
        if "erreur" in y:
            L.append(f"| — | {y['symbole']} | erreur de téléchargement | | | | | |")
        else:
            L.append(f"| {y['strategie']} {y['params']} | {y['symbole']} | {ligne(y)} |")
    L += ["\n## Ray Fu : croisement 20/50 jours\n", "| Marché | Version | Trades | Réussite | ≤ 2023 : rendement/an, pire baisse, Sharpe | 2024+ : rendement/an, pire baisse, Sharpe |", "|---|---|---|---|---|---|"]
    for sym, d in o["rayfu"].items():
        for nom, m in d.items():
            f = lambda z: "—" if not z else f"{z['rendement_annuel']:+.0%}, {z['pire_baisse']:.0%}, {z['sharpe']:.2f}"
            L.append(f"| {sym} | {nom} | {m['trades']} | {p(m['reussite'])} | {f(m['dev'])} | {f(m['test'])} |")
    L += ["\n## Augmenter le taux de réussite : hypothèses testées\n",
          "H1 objectif à 1R · H2 seulement dans le sens de la moyenne 50 jours · H3 pas de stop trop serré · H4 = les trois · "
          "H5 bougie de retournement (suggestion de la vidéo de Roro). "
          "Acceptée seulement si la réussite monte ET le R moyen ne baisse pas, en développement ET en test (≥ 30 trades).\n",
          "| Stratégie | Marché | Unité | Base test : réussite / R | H1 | H2 | H3 | H4 | H5 | Acceptées |", "|---|---|---|---|---|---|---|---|---|---|"]
    for x in o["resultats"]:
        a = x["ameliorations"]
        c = [f"{p(a[h]['test'].get('reussite'))} / {r(a[h]['test'].get('R_moyen'))}" for h in ("H1", "H2", "H3", "H4", "H5")]
        acc = [h for h in a if a[h]["acceptee"]]
        L.append(f"| {x['strategie']} {x['params']} | {x['symbole']} | {x['unite']} | {p(x['test'].get('reussite'))} / {r(x['test'].get('R_moyen'))} | "
                 + " | ".join(c) + f" | {', '.join(acc) or 'aucune'} |")
    (ICI / "rapports" / "videos_youtube.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
