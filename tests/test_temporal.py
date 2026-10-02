"""Phase 5 — D017 TEMPORAL: pure recompute, never mutated, never recorded."""
from nullshift import rooms, temporal
from nullshift.progression import Progression
from nullshift.sim import World

from .conftest import make_world, actions, run


def test_recompute_is_deterministic():
    data = rooms.load("hub")
    p = Progression()
    assert temporal.compute(data, p) == temporal.compute(data, p)


def test_lighting_follows_flag():
    data = rooms.load("hub")
    p = Progression()
    assert temporal.compute(data, p)["lighting"] == "emergency"
    p.set_flag("power_restored")
    assert temporal.compute(data, p)["lighting"] == "normal"


def test_explicit_lighting_declaration_wins():
    data = rooms.load("relay")  # lighting: low
    p = Progression()
    p.set_flag("power_restored")
    assert temporal.compute(data, p)["lighting"] == "low"


def test_terminal_variants_follow_flag():
    data = rooms.load("hub")
    p = Progression()
    before = temporal.compute(data, p)["terminal_texts"]["t_hub_staff"]
    p.set_flag("power_restored")
    after = temporal.compute(data, p)["terminal_texts"]["t_hub_staff"]
    assert "CURRENT STAFF: 0" not in before
    assert "CURRENT STAFF: 0" in after


def test_sim_cannot_mutate_temporal():
    p = Progression()
    data = rooms.load("hub")
    w = World(data, p)
    before = temporal.compute(data, p)
    run(w, 300, actions(right=True))
    w.tick(actions(interact=True))
    w.tick(actions(reset=True))
    assert temporal.compute(data, p) == before


def test_temporal_never_in_recordings():
    w = make_world("1.1")
    run(w, 100, actions(right=True))
    w.tick(actions(reset=True))
    rec = w.recordings[-1]
    blob = repr(rec.frames) + repr(rec.events)
    assert "power_restored" not in blob
    assert "emergency" not in blob
    # frames are pure position tuples
    assert all(len(f) == 3 for f in rec.frames)


def test_world_exposes_temporal_terminal_text():
    from nullshift.states import Game
    g = Game()
    g.enter_room("hub")
    assert "CURRENT STAFF: 0" not in g.world.terminal_texts["t_hub_staff"]
    g.progression.set_flag("power_restored")
    g.enter_room("hub")
    assert "CURRENT STAFF: 0" in g.world.terminal_texts["t_hub_staff"]
