"""T1 — Room loading: 1.1 and 1.2 load; bad data fails loudly."""
import pytest

from nullshift import rooms
from .conftest import make_world


def test_room_11_loads():
    data = rooms.load("1.1")
    assert data["id"] == "1.1"
    assert data["exit"]["next"] == "1.2"


def test_room_12_loads():
    data = rooms.load("1.2")
    assert data["id"] == "1.2"
    assert data["exit"]["next"] == "END"
    assert any(d["type"] == "pressure_plate" for d in data["devices"])


def test_missing_room_file():
    with pytest.raises(rooms.RoomError):
        rooms.load("9.9")


def test_invalid_room_data_rejected():
    bad = {"format_version": 1, "id": "x", "sector": 1,
           "grid": {"w": 3, "h": 3, "rows": ["###", "#.#", "###"]},
           "spawn": {"tx": 1, "ty": 1}}
    with pytest.raises(rooms.RoomError):  # missing exit
        rooms.validate(bad, "x")


def test_unknown_format_version_rejected():
    data = rooms.load("1.1")
    data["format_version"] = 999
    with pytest.raises(rooms.RoomError):
        rooms.validate(data, "1.1")


def test_world_builds_from_data():
    w = make_world("1.1")
    assert w.room_id == "1.1"
    assert len(w.doors) == 1
    assert w.player.alive
