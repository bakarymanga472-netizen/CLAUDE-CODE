"""Rapports : un par trade clôturé, un bilan périodique, l'historique des modifications."""


def _f(x, d=2):
    return "—" if x is None else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def rapport_trade(t, diag, a, entete=""):
    L = [entete, f"# Rapport post-trade {t['id']} — {t['instrument']} — {t['strategie']} {t['version']}\n",
         f"Entrée {t['horodatage_entree']} · sortie {t['horodatage_sortie']} · régime {t['regime']} · "
         f"net {t['resultat']['net'] * 100:+.2f} % · **{_f(t['resultat']['R'])} R**\n",
         "## Diagnostic\n", "| Catégorie | Statut | Niveau de preuve | Constats |", "|---|---|---|---|"]
    for k in ("donnees", "execution", "processus"):
        c = diag[k]
        L.append(f"| {k} | {c['statut']} | {c['niveau'] or '—'} | {'<br>'.join(c['constats']) or '—'} |")
    L += [f"| statistique | {'conforme' if diag['statistique']['conforme'] else 'non conforme'} | — | {diag['statistique']['lecture']} |\n",
          "## Plan contre exécution\n", "| | Prévu | Réalisé |", "|---|---|---|"]
    p = a["plan_vs_execution"]
    L += [f"| Prix d'entrée | {_f(p['prix_prevu'])} | {_f(p['prix_entree'])} |",
          f"| Taille | {_f(p['taille_prevue'], 4)} | {_f(p['taille'], 4)} |",
          f"| Coûts | {p['cout_prevu']} | frais {_f(p['frais'], 5)}, glissement {_f(p['glissement'], 5)} |",
          f"| Sortie | — | {p['motif_sortie']} |\n",
          "## Lecture\n", f"- Nature : **{a['nature']}**",
          f"- Position du résultat dans la distribution attendue : {('centile ' + format(a['rang_dans_distribution_attendue'] * 100, '.0f')) if a['rang_dans_distribution_attendue'] is not None else 'inconnue'}",
          f"- Cas comparables : {a['comparables']['n']} (confiance {a['comparables']['confiance']}), part de perdants "
          f"{_f(a['comparables']['part_perdants'])}, R moyen {_f(a['comparables']['R_moyen'])} — ex. {', '.join(a['comparables']['ids'])}",
          f"- Récurrence : {a['recurrence']}"]
    if "R_moyen_par_regime_comparables" in a:
        L.append(f"- R moyen des comparables par régime (R, n) : {a['R_moyen_par_regime_comparables']}")
    L += ["\n## Ce qui est connu\n"] + [f"- {x}" for x in a["connu"] or ["aucune anomalie confirmée"]]
    L += ["\n## Ce qui reste incertain\n"] + [f"- {x}" for x in a["incertain"] or ["—"]]
    L += ["\n## Ce qui nécessite plus de données\n"] + [f"- {x}" for x in a["a_collecter"] or ["—"]]
    L += ["\n## Décision\n", f"- {a['decision']}"]
    if a["hypothese"]:
        L.append(f"- Hypothèse : {a['hypothese']['enonce']} (p = {a['hypothese']['p_valeur']:.3f})\n- Protocole : {a['hypothese']['protocole']}")
    for e in a["erreurs_prevention"]:
        L.append(f"- Erreur confirmée ({e['categorie']}) → règle de prévention testée `{e['regle_prevention']}`")
    return "\n".join(L) + "\n"


def rapport_bilan(b, periode, entete=""):
    L = [entete, f"# Bilan périodique — {periode} — version {b.get('version')}\n",
         f"Trades : {b['n']} · réussite {b['reussite'] * 100:.0f} % · R moyen {b['R_moyen']:+.2f} · R total {b['R_total']:+.1f} · "
         f"profit factor {_f(b['profit_factor'])} · taux de perte attendu (backtest) {b['taux_perte_attendu'] * 100:.0f} %\n",
         "| Régime | Trades | Pertes | R moyen | p brute | p Holm | Confiance | Motif significatif |", "|---|---|---|---|---|---|---|---|"]
    for t in b["par_regime"]:
        L.append(f"| {t['regime']} | {t['n']} | {t['pertes']} | {t['R_moyen']:+.2f} | {t['p_brute']:.3f} | {t['p_holm']:.3f} | "
                 f"{t['confiance']} | {'oui' if t['significatif'] else 'non'} |")
    sig = [t for t in b["par_regime"] if t["significatif"]]
    L += ["\n## Lecture\n",
          "- Motifs significatifs après correction de Holm : " + (", ".join(t["regime"] for t in sig) if sig else "aucun") + ".",
          "- Un motif significatif n'est qu'une hypothèse : elle doit être testée sur des données distinctes avant toute modification."]
    return "\n".join(L) + "\n"


def historique_modifications(mods, entete=""):
    L = [entete, "# Historique des modifications\n", "| Id | Date | Objet | Résultat | Échantillon | Confiance | Version |", "|---|---|---|---|---|---|---|"]
    for m in mods:
        L.append(f"| {m['id']} | {m['date']} | {m.get('objet', '')} | {m['resultat']} | {m['echantillon']} | {m['confiance']} | {m['version_modele']} |")
    return "\n".join(L) + "\n"
