"""T10 — Puzzle: Room 1.2 is solvable ONLY via the intended temporal sequence."""
import pytest

from .conftest import make_world, actions, run


def test_room_12_unsolvable_without_echo():
    """Walking straight at the door never opens it: the echo is necessary."""
    w = make_world("1.2")
    exited = False
    for _ in range(2400):
        evs = w.tick(actions(right=True))
        if any(isinstance(e, tuple) and e[0] == "exit" for e in evs):
            exited = True
            break
    assert not exited
    assert not w.devices["door1"].open


def test_room_12_solved_with_temporal_sequence():
    """Cycle 1: hold the plate, reset. Cycle 2: echo holds it, walk through."""
    w = make_world("1.2")
    # cycle 1 — the holder run
    run(w, 70, actions(right=True))
    run(w, 62, actions(up=True))
    run(w, 68, actions())
    w.tick(actions(reset=True))
    assert len(w.echoes) == 1
    # cycle 2 — walk through while the echo holds the plate
    exited = False
    for _ in range(600):
        evs = w.tick(actions(right=True))
        if any(isinstance(e, tuple) and e[0] == "exit" for e in evs):
            exited = True
            break
    assert exited, "scripted temporal solution failed to reach the exit"


def test_room_11_solved():
    """Room 1.1: console -> door -> exit, single cycle."""
    w = make_world()
    run(w, 158, actions(right=True))
    w.tick(actions(interact=True))
    assert w.devices["door1"].open
    exited = False
    for _ in range(400):
        evs = w.tick(actions(right=True))
        if any(isinstance(e, tuple) and e[0] == "exit" for e in evs):
            exited = True
            break
    assert exited
