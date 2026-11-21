"""Module joueurs (buteurs, passeurs décisifs) — PHASE 2, NON IMPLÉMENTÉ.

Conformément au cahier des charges (section 15, étape 6), ce module ne sera
construit que lorsque des données individuelles fiables seront connectées :
minutes jouées, xG/xA par 90 minutes, tirs, passes clés, tireurs de
penalties, compositions probables et règles de règlement des bookmakers.

Source pressentie : API-Football (clé payante ou offre gratuite limitée),
voir docs/AUDIT_SOURCES.md. Tant que ces données ne sont pas branchées,
aucune probabilité de buteur ou de passeur n'est produite : le rapport
affiche « Données insuffisantes » au lieu d'un chiffre inventé.
"""

from __future__ import annotations

PLAYER_MARKETS = ["Buteur : joueur identifié", "Passeur : joueur identifié"]


def player_markets_status() -> list[tuple[str, str]]:
    return [(label, "Données insuffisantes (module joueurs non implémenté)") for label in PLAYER_MARKETS]


def predict_scorer(*_args, **_kwargs):
    raise NotImplementedError("Module joueurs non implémenté : données individuelles non connectées.")


def predict_assist(*_args, **_kwargs):
    raise NotImplementedError("Module joueurs non implémenté : données individuelles non connectées.")
