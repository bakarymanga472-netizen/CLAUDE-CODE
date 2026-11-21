"""Connecteur API-Football : lecture du cache, erreurs explicites (aucun accès réseau)."""

import json

import pytest

from pronostiqueur import config
from pronostiqueur.data import api_football as af
from pronostiqueur.data.football_data_uk import DataSourceError

FIXTURES_PAYLOAD = {"errors": [], "response": [
    {"fixture": {"id": 1, "date": "2024-08-17T14:00:00+00:00", "status": {"short": "FT"}},
     "teams": {"home": {"id": 34, "name": "Newcastle"}, "away": {"id": 41, "name": "Southampton"}},
     "score": {"halftime": {"home": 1, "away": 0}, "fulltime": {"home": 1, "away": 0}}},
    {"fixture": {"id": 2, "date": "2024-08-18T14:00:00+00:00", "status": {"short": "PST"}},
     "teams": {"home": {"id": 1, "name": "A"}, "away": {"id": 2, "name": "B"}},
     "score": {"halftime": {"home": None, "away": None}, "fulltime": {"home": None, "away": None}}},
]}
INJURIES_PAYLOAD = {"errors": [], "response": [
    {"fixture": {"id": 1}, "team": {"id": 34},
     "player": {"id": 7, "type": "Missing Fixture", "reason": "Knee Injury"}},
]}


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "RAW_DIR", tmp_path)
    monkeypatch.delenv(af.KEY_ENV, raising=False)

    def write(endpoint, params, payload):
        path = af._cache_path(endpoint, params)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload))
    return write


def test_fixtures_and_injuries_from_cache(cache):
    params = {"league": 39, "season": 2024}
    cache("fixtures", params, FIXTURES_PAYLOAD)
    cache("injuries", params, INJURIES_PAYLOAD)
    fx = af.fixtures("E0", "2425")
    assert list(fx["fixture_id"]) == [1]  # le match reporté est écarté
    assert (fx.loc[0, "ht_home"], fx.loc[0, "ft_home"]) == (1, 1)
    inj = af.injuries("E0", "2425")
    assert inj.loc[0, "type"] == "Missing Fixture"


def test_missing_key_raises_instead_of_inventing(cache):
    with pytest.raises(DataSourceError, match=af.KEY_ENV):
        af.fixtures("E0", "2425")


def test_season_year():
    assert af.season_year("2223") == 2022
