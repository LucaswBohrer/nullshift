"""Entry: init, fixed-timestep loop, event routing. No gameplay logic here."""
import os
import sys

AUDIO_EVENTS = {
    "interact": "interact",
    "door": "door",
    "plate": "plate",
    "death": "death",
    "echo_spawn": "echo",
    "reset": "reset",
    "turret_charge": "turret_charge",
    "turret_shot": "turret_shot",
    "room_complete": "room_complete",
    "game_complete": "room_complete",
    "start": "ui",
    "pause": "ui",
    "unpause": "ui",
    "flag_set": "flag_set",
}


def run_game():
    import pygame
    from nullshift import audio, config, input as inp
    from nullshift.debug import Debug
    from nullshift.particles import Particles
    from nullshift.render import Renderer
    from nullshift.states import Game
    from nullshift.version import __version__

    pygame.init()
    audio.init()  # silent fallback if no audio device
    window = pygame.display.set_mode((config.WINDOW_W, config.WINDOW_H))
    pygame.display.set_caption(f"{config.TITLE} v{__version__}")

    game = Game()
    renderer = Renderer()
    particles = Particles()
    debug = Debug()
    clock = pygame.time.Clock()
    flash = 0.0
    step_cd = 0
    last_room = None

    running = True
    acc = 0.0
    step = 1.0 / config.TICK_HZ
    while running:
        just_pressed = set()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN:
                just_pressed.add(ev.key)
                debug.handle_key(ev.key, game)
                if debug.warp_request:
                    try:
                        game.enter_room(debug.warp_request)
                    except Exception:
                        pass
                    debug.warp_request = None
        actions = inp.poll(just_pressed)
        acc += min(clock.tick(config.TICK_HZ) / 1000.0, 0.25)
        n = 0
        while acc >= step and n < 3:
            for uev in game.tick(actions):
                if uev == "mute_toggle":
                    audio.toggle_mute()
                elif uev == "reset":
                    flash = 1.0
                    w = game.world
                    if w:
                        particles.spawn_reset(w.player.x, w.player.y)
                elif uev == "death" and game.world:
                    w = game.world
                    particles.spawn_sparks(w.player.x, w.player.y)
                elif uev == "echo_spawn" and game.world:
                    w = game.world
                    particles.spawn_shimmer(w.player.x, w.player.y)
                if uev in AUDIO_EVENTS:
                    audio.play(AUDIO_EVENTS[uev])
            acc -= step
            n += 1
        if n == 3:
            acc = 0.0  # drop time, never spiral
        flash = max(0.0, flash - 0.06)
        # footsteps (presentation only)
        step_cd -= 1
        if (game.state == "PLAYING" and step_cd <= 0
                and any(actions.get(m) for m in ("left", "right", "up", "down"))):
            audio.play("step")
            step_cd = 16
        # electrical hum follows TEMPORAL lighting (rooms at normal power)
        rid = game.world.room_id if game.world else None
        if rid != last_room:
            last_room = rid
            if game.world and game.temporal.get("lighting") == "normal":
                audio.start_hum()
            else:
                audio.stop_hum()
        particles.update(1.0 / config.TICK_HZ)
        frame = renderer.draw(game, particles, debug, flash)
        pygame.transform.scale(frame, (config.WINDOW_W, config.WINDOW_H), window)
        pygame.display.flip()
    pygame.quit()


def smoke() -> int:
    """Headless boot check for the build pipeline."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    from nullshift import input as inp
    from nullshift.states import Game

    pygame.init()
    game = Game()
    game.tick({**inp.empty_actions(), "confirm": True})   # TITLE -> SECTORCARD
    game.tick({**inp.empty_actions(), "confirm": True})   # SECTORCARD -> PLAYING
    assert game.state == "PLAYING", f"smoke: state={game.state}"
    assert game.world is not None and game.world.room_id == "1.1"
    a = inp.empty_actions()
    for _ in range(120):
        game.tick(a)
    assert game.state == "PLAYING"
    # render one frame to catch draw-time errors
    from nullshift.debug import Debug
    from nullshift.particles import Particles
    from nullshift.render import Renderer
    Renderer().draw(game, Particles(), Debug(), 0.0)
    print("SMOKE OK: boot -> 1.1 -> 120 ticks -> 1 frame, no errors")
    return 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--version" in argv:
        from nullshift.version import __version__
        print(__version__)
        return 0
    if "--smoke" in argv:
        return smoke()
    run_game()
    return 0
