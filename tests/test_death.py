"""T9 — Death triggers immediate reset; fatal run becomes a vanishing echo."""
import pytest

from nullshift.hazards import LaserGrid
from .conftest import make_world, actions, run


def add_spawn_laser(w):
    # always-on vertical beam covering the spawn point
    w.hazards.append(LaserGrid({
        "id": "lz", "type": "laser",
        "x1": 2, "y1": 10, "x2": 2, "y2": 12,
        "on": 3.0, "off": 0.0, "warn": 0.0,
    }))
    # rebuild snapshot so the test laser is part of the baseline
    w.snapshot = w.capture_initial()


def test_death_resets_immediately():
    w = make_world()
    run(w, 100, actions(right=True))
    add_spawn_laser(w)
    w.player.spawn(*w.spawn_pos)
    events = w.tick(actions())
    assert "death" in events
    assert "reset" in events
    assert "reason:death" in events
    assert (w.player.x, w.player.y) == w.spawn_pos


def add_path_laser(w):
    # always-on vertical beam across the walking path (not at spawn)
    w.hazards.append(LaserGrid({
        "id": "lz", "type": "laser",
        "x1": 12, "y1": 10, "x2": 12, "y2": 12,
        "on": 3.0, "off": 0.0, "warn": 0.0,
    }))
    w.snapshot = w.capture_initial()


def test_fatal_run_becomes_vanishing_echo():
    w = make_world()
    add_path_laser(w)
    for _ in range(300):
        evs = w.tick(actions(right=True))
        if "reason:death" in evs:
            break
    rec = w.recordings[-1]
    assert rec.death_tick is not None and rec.death_tick < 300
    dt = rec.death_tick
    # park the player safely; the echo replays the fatal run up to death_tick
    w.player.spawn(600, 300)
    for _ in range(dt - 1):
        w.tick(actions())
    assert len(w.echoes) == 1
    for _ in range(5):
        w.tick(actions())
    assert w.echoes == []


def test_echo_killed_by_hazard():
    w = make_world()
    run(w, 100, actions(right=True))
    w.tick(actions(reset=True))
    assert len(w.echoes) == 1
    add_spawn_laser(w)
    w.player.spawn(30 * 16 + 8, 11 * 16 + 8)  # park player away from beam
    events = w.tick(actions())
    # echo replays from spawn — inside the beam — and is destroyed
    assert "echo_death" in events
    assert w.echoes == []
    # the tightened death_tick persists: the recording replays nothing
    assert w.recordings[-1].death_tick == 0
