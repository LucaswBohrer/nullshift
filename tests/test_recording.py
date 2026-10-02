"""T3 — Recording: deterministic action sequence -> expected recording."""
from nullshift import config
from .conftest import make_world, actions, run


def test_recording_captures_frames_and_events():
    w = make_world()
    run(w, 100, actions(right=True))
    # walk to console at (20,11): needs ~158 ticks from spawn
    run(w, 60, actions(right=True))
    w.tick(actions(interact=True))
    assert len(w.rec.frames) == 161
    assert len(w.rec.events) == 1
    tick, dev_id = w.rec.events[0]
    assert dev_id == "con1"
    assert tick == 160  # frame index this tick records


def test_short_runs_not_recorded():
    w = make_world()
    run(w, 30, actions(right=True))
    w.tick(actions(reset=True))
    assert w.recordings == []
    assert w.echoes == []


def test_manual_reset_records_and_spawns_echo():
    w = make_world()
    run(w, 100, actions(right=True))
    events = w.tick(actions(reset=True))
    assert "echo_spawn" in events
    assert "reset" in events
    assert "reason:manual" in events
    assert len(w.recordings) == 1
    assert w.recordings[0].ticks == 100
    assert len(w.echoes) == 1
    assert w.cycle_tick == 0
    # player back at spawn
    assert (w.player.x, w.player.y) == w.spawn_pos


def test_timer_reset():
    w = make_world()
    w.cycle_tick = config.CYCLE_TICKS - 1
    events = w.tick(actions())
    assert "reset" in events
    assert "reason:timer" in events
