"""T5 — Interaction: echo triggers plates/consoles via the same rules as the player."""
import pytest

from .conftest import make_world, actions, run


def walk_to_plate(w):
    """Cycle 1 of the 1.2 solution: walk from spawn to plate1, wait, reset."""
    run(w, 70, actions(right=True))   # x: 40 -> ~168
    run(w, 62, actions(up=True))      # y: 184 -> ~70 (plate at (10,4))
    run(w, 68, actions())             # stand on the plate
    w.tick(actions(reset=True))


def test_player_presses_plate():
    w = make_world("1.2")
    run(w, 70, actions(right=True))
    run(w, 62, actions(up=True))
    plate = w.devices["plate1"]
    assert plate.pressed
    assert w.devices["door1"].open


def test_echo_presses_plate_and_opens_door():
    w = make_world("1.2")
    walk_to_plate(w)
    assert len(w.echoes) == 1
    # cycle 2: echo replays; once it reaches the plate the door opens
    run(w, 140, actions())
    assert w.devices["door1"].open
    # the echo never triggers the exit pad even if it walks over it


def test_echo_holds_plate_while_player_passes():
    w = make_world("1.2")
    walk_to_plate(w)
    # cycle 2: walk straight through the door while the echo holds the plate
    run(w, 170, actions(right=True))
    assert w.devices["door1"].open
    assert w.player.x == pytest.approx(40 + 170 * (110.0 / 60), abs=2.0)
    assert w.player.x > 336  # past the door tiles at x=320..336
