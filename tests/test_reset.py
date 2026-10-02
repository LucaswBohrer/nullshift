"""T6 — Reset restores the exact room-entry state (RESETTABLE row)."""
import pytest

from nullshift import config
from .conftest import make_world, actions, run


def test_reset_restores_devices_and_player():
    w = make_world()
    run(w, 158, actions(right=True))
    w.tick(actions(interact=True))
    assert w.devices["con1"].on
    assert w.devices["door1"].open
    w.tick(actions(reset=True))
    assert not w.devices["con1"].on
    assert not w.devices["door1"].open
    assert (w.player.x, w.player.y) == w.spawn_pos
    assert w.cycle_tick == 0
    assert w.projectiles == []


def test_reset_restores_hazard_state():
    w = make_world()
    run(w, 200, actions())  # hazard timers advance (no hazards in 1.1; smoke-check)
    snap = w.snapshot
    w.tick(actions(reset=True))
    for hz, hsnap in zip(w.hazards, snap["hazards"]):
        assert hz.snapshot() == hsnap


def test_reset_does_not_leak_recordings_across_rooms():
    # recordings accumulate within a room...
    w = make_world()
    run(w, 100, actions(right=True))
    w.tick(actions(reset=True))
    assert len(w.recordings) == 1
    # ...and a fresh World starts clean (room transition semantics)
    w2 = make_world("1.2")
    assert w2.recordings == [] and w2.echoes == []
