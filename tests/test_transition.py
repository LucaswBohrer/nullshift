"""T8 — Room transition clears echoes and recordings."""
from nullshift.states import Game
from nullshift import input as inp
from .conftest import actions, run


def test_transition_clears_temporal_state():
    g = Game()
    g.enter_room("1.1")
    # dismiss sector card
    g.tick({**inp.empty_actions(), "confirm": True})
    w = g.world
    run(w, 100, actions(right=True))
    w.tick(actions(reset=True))
    assert len(w.echoes) == 1
    # walk to the exit pad and hold
    w.player.spawn(36 * 16 + 8, 11 * 16 + 8)
    exited = False
    for _ in range(60):
        evs = w.tick(actions())
        if any(isinstance(e, tuple) and e[0] == "exit" for e in evs):
            exited = True
            break
    assert exited
    g.enter_room("1.2")
    assert g.world.room_id == "1.2"
    assert g.world.echoes == []
    assert g.world.recordings == []
    assert g.world.cycle_tick == 0
