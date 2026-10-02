"""T4 — Playback: echo reproduces its recording tick-for-tick."""
from .conftest import make_world, actions, run


def do_cycle(w, move_ticks, total=120, move="right"):
    run(w, move_ticks, actions(**{move: True}))
    run(w, total - move_ticks, actions())
    w.tick(actions(reset=True))
    return total  # recording length


def test_echo_replays_positions():
    w = make_world()
    total = do_cycle(w, 100)
    rec = w.recordings[0]
    assert rec.ticks == total
    # cycle 2: no input; echo should trace the recording exactly.
    # (the echo is removed during its final tick, so check total-1 frames)
    for i in range(total - 1):
        w.tick(actions())
        echo = w.echoes[0]
        assert (echo.x, echo.y, echo.facing) == rec.frames[i]
    # after the recording ends the echo is gone
    w.tick(actions())
    assert w.echoes == []


def test_echo_replays_console_event():
    w = make_world()
    run(w, 158, actions(right=True))
    w.tick(actions(interact=True))  # toggles con1 on
    assert w.devices["con1"].on
    w.tick(actions(reset=True))
    assert not w.devices["con1"].on  # reset restored
    # cycle 2: echo re-fires the console at the recorded tick
    run(w, 159, actions())
    assert w.devices["con1"].on
    assert w.devices["door1"].open
