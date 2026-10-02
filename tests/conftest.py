import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from nullshift import config, rooms
from nullshift.sim import World


def make_world(room_id="1.1") -> World:
    return World(rooms.load(room_id))


def actions(**kw) -> dict:
    base = {"up": False, "down": False, "left": False, "right": False,
            "interact": False, "reset": False, "pause": False, "mute": False,
            "confirm": False, "debug_overlay": False, "debug_collision": False,
            "debug_warp": False}
    base.update(kw)
    return base


def run(world: World, n: int, act: dict) -> list:
    events = []
    for _ in range(n):
        events.extend(world.tick(act))
    return events


PX_PER_TICK = config.PLAYER_SPEED / config.TICK_HZ
