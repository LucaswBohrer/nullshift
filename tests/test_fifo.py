"""T7 — FIFO: the 4th recording discards the oldest; cap is 3."""
import pytest

from nullshift import config
from .conftest import make_world, actions, run


def cycle(w, move_ticks: int, total: int = 150):
    run(w, move_ticks, actions(right=True))
    run(w, total - move_ticks, actions())
    w.tick(actions(reset=True))


def test_fifo_cap_three():
    w = make_world()
    for i in range(4):
        cycle(w, 70 + 10 * i)
    assert len(w.recordings) == 3
    assert len(w.echoes) == 3
    # recordings are runs 2,3,4 (run 1 discarded): last-frame x grows per run
    xs = [r.frames[-1][0] for r in w.recordings]
    assert xs == sorted(xs)
    assert xs[0] == pytest.approx(40 + 80 * (config.PLAYER_SPEED / config.TICK_HZ))


def test_player_not_counted_in_cap():
    w = make_world()
    for _ in range(3):
        cycle(w, 70)
    # living player + 3 echoes coexist; the cap applies to recordings only
    assert len(w.echoes) == 3
    assert w.player.alive
