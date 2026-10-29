"""Contrôle qualité des données de matchs.

Chaque ligne rejetée est comptée avec son motif. Les lignes incohérentes
sont exclues, jamais corrigées par supposition.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class QualityReport:
    rows_in: int = 0
    rows_out: int = 0
    rejected: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def add(self, reason: str, count: int) -> None:
        if count:
            self.rejected[reason] = self.rejected.get(reason, 0) + int(count)

    def summary(self) -> str:
        lines = [f"Lignes reçues : {self.rows_in} · conservées : {self.rows_out}"]
        for reason, count in sorted(self.rejected.items()):
            lines.append(f"  - rejet « {reason} » : {count}")
        lines.extend(f"  ! {w}" for w in self.warnings)
        return "\n".join(lines)


def clean_matches(df: pd.DataFrame) -> tuple[pd.DataFrame, QualityReport]:
    report = QualityReport(rows_in=len(df))
    out = df.copy()

    mask = out["date"].isna()
    report.add("date illisible", mask.sum())
    out = out[~mask]

    score_cols = ["ft_home", "ft_away", "ht_home", "ht_away"]
    mask = out[score_cols].isna().any(axis=1)
    report.add("score manquant", mask.sum())
    out = out[~mask]

    mask = (out["ht_home"] > out["ft_home"]) | (out["ht_away"] > out["ft_away"])
    report.add("score mi-temps > score final", mask.sum())
    out = out[~mask]

    mask = (out[score_cols] < 0).any(axis=1)
    report.add("score négatif", mask.sum())
    out = out[~mask]

    before = len(out)
    out = out.drop_duplicates(subset=["league", "date", "home", "away"], keep="last")
    report.add("doublon", before - len(out))

    for col in ["odds_over25", "odds_under25", "odds_home", "odds_draw", "odds_away"]:
        bad = out[col].notna() & (out[col] <= 1.0)
        if bad.any():
            report.warnings.append(f"{int(bad.sum())} cotes ≤ 1.0 dans {col} remplacées par « absente »")
            out.loc[bad, col] = float("nan")

    missing_odds = out["odds_over25"].isna().mean() if len(out) else 0.0
    if missing_odds > 0.05:
        report.warnings.append(f"Cotes +/-2,5 absentes pour {missing_odds:.1%} des matchs")

    out = out.sort_values(["date", "league", "home"]).reset_index(drop=True)
    for col in score_cols + ["h1_goals", "h2_goals"]:
        out[col] = out[col].astype(int)
    report.rows_out = len(out)
    return out, report
