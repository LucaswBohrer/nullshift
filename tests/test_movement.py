"""T2 — Player movement: input moves player; walls block; deterministic."""
import math

import pytest

from .conftest import make_world, actions, run, PX_PER_TICK


def test_movement_right():
    w = make_world()
    x0 = w.player.x
    run(w, 60, actions(right=True))
    assert w.player.x == pytest.approx(x0 + 60 * PX_PER_TICK)


def test_diagonal_normalized():
    w = make_world()
    run(w, 60, actions(right=True, down=True))
    # diagonal speed == cardinal speed (no sqrt(2) boost)
    moved = math.hypot(w.player.x - 40.0, w.player.y - 184.0)
    assert moved == pytest.approx(60 * PX_PER_TICK)


def test_wall_blocks_movement():
    w = make_world()
    run(w, 600, actions(left=True))  # run into the left wall
    # wall inner face at x=16; player half-width 6 -> center exactly 22
    assert w.player.x == pytest.approx(22.0)


def test_movement_deterministic():
    def script():
        w = make_world()
        run(w, 37, actions(right=True))
        run(w, 41, actions(up=True))
        run(w, 55, actions(left=True, down=True))
        return (w.player.x, w.player.y, w.player.facing)
    assert script() == script()
