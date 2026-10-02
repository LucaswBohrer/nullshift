"""Phase 5 checkpoint — full WAKE -> POWER -> RELAY flow at Game level.

Teleports stand in for walking (movement was validated at Gate 4 and is
unchanged); this test owns the world graph, flags, LIA, phase and
TEMPORAL presentation across the whole first playable segment.
"""
from nullshift.states import Game

from .conftest import actions, run


def _dismiss(g):
    for _ in range(10):
        if g.state == "SECTORCARD":
            g.tick(actions(confirm=True))
        elif g.state in ("LIA", "TERMINAL"):
            g.tick(actions(interact=True))
        else:
            break


def _step_on_exit(g, next_room):
    w = g.world
    pad = next(p for p in w.exits if p.next_room == next_room)
    w.player.spawn(pad.rect.centerx, pad.rect.centery)
    g.tick(actions())
    assert g.world.room_id == next_room, f"expected {next_room}, in {g.world.room_id}"


def test_full_wake_to_relay_flow():
    g = Game()
    g.enter_room("1.1")
    _dismiss(g)
    assert g.state == "PLAYING"
    assert g.progression.phase == "WAKE"

    # 1.1 -> 1.2 (Gate 4 rooms unchanged)
    _step_on_exit(g, "1.2")
    _dismiss(g)

    # 1.2 -> hub: first contact with LIA
    _step_on_exit(g, "hub")
    assert g.state == "LIA"
    assert "Good return, Elias." in g.lia_text
    _dismiss(g)
    assert g.temporal["lighting"] == "emergency"
    east = next(p for p in g.world.exits if p.next_room == "relay")
    assert not east.unlocked(g.progression)

    # hub -> power: phase transition + LIA warning
    _step_on_exit(g, "power")
    assert g.progression.phase == "POWER"
    assert g.state == "LIA"
    _dismiss(g)

    # solve the power puzzle: echo holds breaker_a, player flips relay_main
    w = g.world
    run(w, 61, actions())
    d = w.devices["breaker_a"]
    w.player.spawn(d.rect.centerx + 10, d.rect.centery)
    g.tick(actions(interact=True))
    assert w.devices["breaker_a"].on
    g.tick(actions(reset=True))
    run(w, 120, actions())  # echo re-fires breaker_a
    assert w.devices["breaker_a"].on
    d = w.devices["relay_main"]
    w.player.spawn(d.rect.centerx + 10, d.rect.centery)
    g.tick(actions(interact=True))
    assert g.progression.get_flag("power_restored") is True
    assert g.subtitle is not None and "Power's back" in g.subtitle[0]

    # power -> hub: the station has changed
    _step_on_exit(g, "hub")
    assert g.temporal["lighting"] == "normal"
    assert g.state == "LIA"
    assert "Power restored." in g.lia_text
    _dismiss(g)
    east = next(p for p in g.world.exits if p.next_room == "relay")
    assert east.unlocked(g.progression)
    assert "CURRENT STAFF: 0" in g.world.terminal_texts["t_hub_staff"]

    # hub -> relay: Tomas + Mara
    _step_on_exit(g, "relay")
    assert g.state == "LIA"
    _dismiss(g)
    assert g.subtitle is not None and "Tomas was here" in g.subtitle[0]
    assert g.temporal["lighting"] == "low"
    assert g.progression.visits["relay"] == 1
