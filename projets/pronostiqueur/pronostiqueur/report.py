"""Tableau de bord : performance en simulation (backtest) et en réel (journal)."""

from __future__ import annotations

import html
import math
from datetime import datetime, timezone

import pandas as pd

from . import config, metrics


def _fmt(x, pct=False, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.1%}" if pct else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def _df_md(df: pd.DataFrame, pct_cols=()) -> str:
    if df.empty:
        return "_(aucune donnée)_"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_fmt(r[c], c in pct_cols) for c in cols) + " |")
    return "\n".join(lines)


def backtest_markdown(evaluation: dict, bias: pd.DataFrame, data_summary: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = [f"# Rapport de validation (simulation historique) — {now}", "",
           "> Résultats **en simulation** (walk-forward chronologique, sans fuite de données futures). "
           "Ce ne sont pas des résultats de paris réels. Aucune cote par mi-temps n'existe dans "
           "l'historique utilisé : le rendement financier ne peut pas être calculé.", "",
           "## Données", "```", data_summary, "```"]
    for market, ev in evaluation.items():
        out += ["", f"## {config.MARKETS[market]}", "", "### Qualité globale des probabilités (plus bas = mieux)"]
        g = pd.DataFrame(ev["global"]).T.reset_index().rename(columns={"index": "modèle"})
        out.append(_df_md(g[["modèle", "n", "taux_base", "brier", "log_loss", "ece"]], pct_cols=("taux_base",)))
        out += ["", "### Calibration de l'ensemble", _df_md(ev["calibration"],
                pct_cols=("prob_moyenne", "taux_observe", "ic95_bas", "ic95_haut"))]
        hc_pct = ("part_des_matchs", "prob_moyenne_annoncee", "taux_reussite", "ic95_bas", "ic95_haut")
        out += ["", "### Haute confiance : taux de réussite au-dessus de chaque seuil",
                _df_md(ev["haute_confiance"], pct_cols=hc_pct),
                "", "### Haute confiance — équipes avec historique suffisant",
                _df_md(ev["haute_confiance_equipes_rodees"], pct_cols=hc_pct)]
        s = ev["selection_regles"]
        out += ["", "### Application des règles de sélection",
                f"- Matchs : {s['n_matchs']} · sélections : {s['n_selections']} ({_fmt(s['taux_selection'], True)})",
                f"- Probabilité moyenne annoncée : {_fmt(s['prob_moyenne_annoncee'], True)} · "
                f"réussite observée : {_fmt(s['taux_reussite'], True)} "
                f"(IC95 {_fmt(s['ic95'][0], True)} – {_fmt(s['ic95'][1], True)})",
                f"- Cote juste moyenne des sélections : {_fmt(s['cote_juste_moyenne'], nd=2)} "
                "(une cote proposée inférieure rend le pari défavorable)"]
        ps = pd.DataFrame(ev["par_saison"]).T.reset_index().rename(columns={"index": "saison"})
        out += ["", "### Par saison", _df_md(ps[["saison", "n", "taux_base", "brier", "log_loss", "ece"]],
                                             pct_cols=("taux_base",))]
        pl = pd.DataFrame(ev["par_ligue"]).T.reset_index().rename(columns={"index": "ligue"})
        out += ["", "### Par ligue", _df_md(pl[["ligue", "n", "taux_base", "brier", "log_loss", "ece"]],
                                            pct_cols=("taux_base",))]
    out += ["", "## Biais détectés (écart annoncé − observé, segments ≥ 30 matchs)",
            _df_md(bias.head(15).assign(tranche=lambda d: d["tranche"].astype(str)),
                   pct_cols=("annonce", "observe", "ecart"))]
    out += ["", "## Objectif 95 %", "",
            "Le tableau « haute confiance » indique, pour chaque seuil, le nombre de sélections, "
            "le taux de réussite et son intervalle de confiance. **L'objectif de 95 % n'est considéré "
            "comme atteint que si la borne basse de l'IC95 dépasse 95 % sur un échantillon hors "
            "entraînement.** Sinon, il ne l'est pas, quel que soit le taux brut."]
    return "\n".join(out)


def journal_markdown(settled: pd.DataFrame) -> str:
    out = ["# Performance réelle (journal des pronostics)", ""]
    if settled.empty:
        return "\n".join(out + ["_Aucun pronostic réglé pour l'instant._"])
    for market, g in settled.groupby("market"):
        p, y = g["probability"].to_numpy(), g["result"].to_numpy()
        s = metrics.summary(p, y)
        k, n = int(y.sum()), len(y)
        lo, hi = metrics.wilson_interval(k, n)
        out += [f"## {config.MARKETS.get(market, market)}",
                f"- Pronostics réglés : {n} · réussite : {k}/{n} = {k / n:.1%} (IC95 {lo:.1%} – {hi:.1%})",
                f"- Probabilité moyenne annoncée : {p.mean():.1%} · Brier {s['brier']:.3f} · log-loss {s['log_loss']:.3f}"]
        taken = g[g["taken_odds"].notna()]
        if not taken.empty:
            profit = (taken["result"] * taken["taken_odds"] - 1).sum()
            out.append(f"- Paris réellement pris : {len(taken)} · rendement net {profit / len(taken):+.1%} par unité")
        adm = g[g["status"] == "admissible"]
        if not adm.empty:
            out.append(f"- Dont « admissibles » : {len(adm)} · réussite {adm['result'].mean():.1%}")
        out.append("")
    return "\n".join(out)


def to_html(markdown_text: str, title: str) -> str:
    """Rendu HTML minimal et autonome du rapport (tableau de bord statique)."""
    body = []
    in_table = False
    for line in markdown_text.splitlines():
        if line.startswith("|"):
            cells = [html.escape(c.strip()) for c in line.strip("|").split("|")]
            if all(set(c) <= {"-"} for c in cells):
                continue
            if not in_table:
                body.append("<table>")
                in_table = True
                body.append("<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>")
            else:
                body.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            body.append("</table>")
            in_table = False
        esc = html.escape(line)
        if line.startswith("### "):
            body.append(f"<h3>{esc[4:]}</h3>")
        elif line.startswith("## "):
            body.append(f"<h2>{esc[3:]}</h2>")
        elif line.startswith("# "):
            body.append(f"<h1>{esc[2:]}</h1>")
        elif line.strip():
            body.append(f"<p>{esc}</p>")
    if in_table:
        body.append("</table>")
    style = ("body{font-family:system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;"
             "background:#fff;color:#111}table{border-collapse:collapse;margin:8px 0;font-size:14px}"
             "td,th{border:1px solid #ccc;padding:4px 8px;text-align:right}th{background:#f2f2f2}"
             "@media (prefers-color-scheme: dark){body{background:#111;color:#eee}th{background:#222}"
             "td,th{border-color:#444}}")
    return (f"<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)}"
            f"</title><style>{style}</style></head><body>{''.join(body)}</body></html>")
