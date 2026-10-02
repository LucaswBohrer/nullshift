"""Phase 5 — narrative: LIA line selection, phase transitions, barks,
terminal availability. All data-driven, no dialogue engine."""
from nullshift.states import Game, load_lia_lines


def dismiss_overlays(g):
    """Dismiss SECTORCARD and LIA until PLAYING."""
    from .conftest import actions
    for _ in range(10):
        if g.state == "SECTORCARD":
            g.tick(actions(confirm=True))
        elif g.state == "LIA":
            g.tick(actions(interact=True))
        else:
            break


def dismiss_lia(g):
    dismiss_overlays(g)


def enter_past_card(g, room_id):
    """enter_room + dismiss SECTORCARD only (LIA stays queued)."""
    from .conftest import actions
    g.enter_room(room_id)
    if g.state == "SECTORCARD":
        g.tick(actions(confirm=True))


def test_lia_first_visit_line():
    g = Game()
    enter_past_card(g, "hub")
    assert g.state == "LIA"
    assert "Good return, Elias." in g.lia_text
    dismiss_lia(g)
    assert g.state == "PLAYING"


def test_lia_line_shown_once():
    g = Game()
    enter_past_card(g, "hub")
    dismiss_lia(g)
    g.enter_room("power")
    dismiss_lia(g)
    g.enter_room("hub")
    # visit 2 has no line; hub_2 needs the flag
    assert g.state == "PLAYING"


def test_lia_flag_triggered_line():
    g = Game()
    enter_past_card(g, "hub")
    dismiss_lia(g)
    g.progression.set_flag("power_restored")
    g.enter_room("hub")
    assert g.state == "LIA"
    assert "Power restored." in g.lia_text


def test_lia_power_room_line():
    g = Game()
    enter_past_card(g, "power")
    assert g.state == "LIA"
    assert "two hands" in g.lia_text


def test_narrative_phase_transition():
    g = Game()
    assert g.progression.phase == "WAKE"
    g.enter_room("hub")
    assert g.progression.phase == "WAKE"
    g.enter_room("power")
    assert g.progression.phase == "POWER"


def test_elias_bark_on_room_entry():
    g = Game()
    g.enter_room("1.1")
    assert g.subtitle is not None
    assert "Empty" in g.subtitle[0]


def test_elias_bark_on_flag_end_to_end():
    """Real path: player flips relay_main -> flag_set -> bark subtitle."""
    from .conftest import actions
    g = Game()
    enter_past_card(g, "power")
    dismiss_lia(g)
    w = g.world
    w.devices["breaker_a"].toggle()
    w.player.spawn(w.devices["relay_main"].rect.centerx + 10,
                   w.devices["relay_main"].rect.centery)
    g.tick(actions(interact=True))
    assert g.progression.get_flag("power_restored") is True
    assert g.subtitle is not None
    assert "Power's back" in g.subtitle[0]


def test_lia_data_is_sane():
    lines = load_lia_lines()
    assert len(lines) >= 4
    ids = [l["id"] for l in lines]
    assert len(set(ids)) == len(ids)
