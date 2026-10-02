"""Phase 5 — D016 persistence: flags survive reset/death/transition;
only explicit player actions set them; echoes never do."""
import pytest

from nullshift import rooms, temporal
from nullshift.progression import Progression
from nullshift.sim import World
from nullshift.states import Game

from .conftest import make_world, actions, run


def power_world():
    prog = Progression()
    return World(rooms.load("power"), prog), prog


def near(w, dev_id):
    """Teleport the player next to a device (within interact radius)."""
    d = w.devices[dev_id]
    w.player.spawn(d.rect.centerx + 10, d.rect.centery)


def test_flag_set_on_player_rising_edge():
    w, prog = power_world()
    w.devices["breaker_a"].toggle()  # requirement satisfied
    near(w, "relay_main")
    events = w.tick(actions(interact=True))
    assert ("flag_set", "power_restored") in events
    assert w.devices["relay_main"].on


def test_flag_not_set_when_requirements_unmet():
    w, prog = power_world()
    near(w, "relay_main")
    events = w.tick(actions(interact=True))
    assert ("flag_set", "power_restored") not in events
    assert w.devices["relay_main"].on  # device still toggles; flag does not


def test_flag_not_set_on_toggle_off():
    w, prog = power_world()
    w.devices["breaker_a"].toggle()
    w.devices["relay_main"].toggle()  # now ON
    near(w, "relay_main")
    events = w.tick(actions(interact=True))  # toggles OFF
    assert ("flag_set", "power_restored") not in events


def test_echo_refire_never_sets_flag():
    """Full two-cycle script: echo re-fires breaker_a; no flag_set emitted."""
    w, prog = power_world()
    # cycle 1: player turns breaker_a ON, then resets (>= 60 ticks to record)
    run(w, 61, actions())
    near(w, "breaker_a")
    w.tick(actions(interact=True))
    assert w.devices["breaker_a"].on
    events = w.tick(actions(reset=True))
    assert "echo_spawn" in events  # recording kept
    # cycle 2: let the echo replay; it re-fires breaker_a ON
    events = run(w, 120, actions())
    assert "echo_console" in events
    assert ("flag_set", "power_restored") not in events
    assert prog.get_flag("power_restored") is None


def test_power_puzzle_cooperation_end_to_end():
    """Echo holds breaker_a (cycle 1) while the player flips relay_main."""
    w, prog = power_world()
    run(w, 61, actions())
    near(w, "breaker_a")
    w.tick(actions(interact=True))
    w.tick(actions(reset=True))
    run(w, 120, actions())  # echo re-fires breaker_a ON
    assert w.devices["breaker_a"].on
    near(w, "relay_main")
    events = w.tick(actions(interact=True))
    assert ("flag_set", "power_restored") in events


def test_flag_survives_cycle_reset():
    w, prog = power_world()
    prog.set_flag("power_restored")
    w.tick(actions(reset=True))
    assert prog.get_flag("power_restored") is True


def test_flag_survives_death():
    w, prog = power_world()
    prog.set_flag("power_restored")
    w.kill_player([])
    w.tick(actions())  # death -> reset
    assert prog.get_flag("power_restored") is True


def test_flag_survives_room_transition_and_rebuild():
    g = Game()
    g.enter_room("hub")
    g.progression.set_flag("power_restored")
    g.enter_room("power")
    g.enter_room("hub")
    assert g.progression.get_flag("power_restored") is True
    # revisited room observes the persistent effect: east exit unlocked
    east = next(p for p in g.world.exits if p.next_room == "relay")
    assert east.unlocked(g.progression)


def test_locked_exit_blocks_transition():
    g = Game()
    g.enter_room("hub")
    east = next(p for p in g.world.exits if p.next_room == "relay")
    assert not east.unlocked(g.progression)
    # walk the player onto the locked pad: no exit event fires
    w = g.world
    w.player.spawn(east.rect.centerx, east.rect.centery)
    events = w.tick(actions())
    assert not any(isinstance(e, tuple) and e[0] == "exit" for e in events)
    assert g.world.room_id == "hub"


def test_progression_serializes():
    p = Progression()
    p.set_flag("power_restored")
    p.set_phase("POWER")
    p.visit("hub")
    p.mark_shown("lia_hub_1")
    q = Progression.from_dict(p.to_dict())
    assert q.get_flag("power_restored") is True
    assert q.phase == "POWER"
    assert q.visits["hub"] == 1
    assert q.was_shown("lia_hub_1")
