"""Phase 5 — backtracking: leave/re-enter is deterministic and reflects
persistent state; reset never erases progression."""
from nullshift import rooms, temporal
from nullshift.progression import Progression
from nullshift.states import Game


def test_room_revisit_is_deterministic():
    g = Game()
    g.enter_room("hub")
    first = temporal.compute(rooms.load("hub"), g.progression)
    g.enter_room("power")
    g.enter_room("hub")
    second = temporal.compute(rooms.load("hub"), g.progression)
    assert first == second
    assert g.progression.visits["hub"] == 2


def test_revisit_observes_persistent_change():
    g = Game()
    g.enter_room("hub")
    before = g.temporal["lighting"]
    assert before == "emergency"
    g.progression.set_flag("power_restored")
    g.enter_room("power")
    g.enter_room("hub")
    assert g.temporal["lighting"] == "normal"
    # both hub exits now usable
    assert all(p.unlocked(g.progression) for p in g.world.exits)


def test_reset_does_not_erase_progression_on_revisit():
    g = Game()
    g.enter_room("hub")
    g.progression.set_flag("power_restored")
    g.enter_room("hub")
    assert g.temporal["lighting"] == "normal"
    # reset inside the room keeps the persistent presentation
    from .conftest import actions
    g.world.tick(actions(reset=True))
    g2_temporal = temporal.compute(rooms.load("hub"), g.progression)
    assert g2_temporal["lighting"] == "normal"


def test_echoes_cleared_but_flags_kept_on_transition():
    from .conftest import actions, run
    g = Game()
    g.enter_room("1.2")
    w = g.world
    run(w, 70, actions(right=True))
    run(w, 62, actions(up=True))
    run(w, 68, actions())
    w.tick(actions(reset=True))
    assert len(w.echoes) == 1
    g.progression.set_flag("power_restored")
    g.enter_room("hub")
    assert g.world.echoes == []
    assert g.progression.get_flag("power_restored") is True
