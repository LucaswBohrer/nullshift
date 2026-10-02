"""World: the single temporal simulation authority (GATE 4 §4).

Owns: tick progression, recordings, snapshots, playback, reset, cycle
timing. Fixed update order per tick (ARCHITECTURE.md §3):

  timer -> player -> echoes -> hazards -> devices -> projectiles
    -> death -> exit -> record
"""
import math

import pygame

from nullshift import config, rooms
from nullshift.devices import make_device, ExitPad, PressurePlate, Console, Door
from nullshift.echo import Recording, Echo
from nullshift.hazards import make_hazard
from nullshift.player import Player

T = config.TILE


class World:
    def __init__(self, data: dict):
        self.data = data
        self.room_id = data["id"]
        self.w = data["grid"]["w"]
        self.h = data["grid"]["h"]

        self.devices = {}
        for d in data.get("devices", []):
            dev = make_device(d)
            self.devices[dev.id] = dev
        self.plates = [d for d in self.devices.values() if isinstance(d, PressurePlate)]
        self.consoles = [d for d in self.devices.values() if isinstance(d, Console)]
        self.doors = [d for d in self.devices.values() if isinstance(d, Door)]
        self.terminals = [d for d in data.get("terminals", [])]

        ex = data["exit"]
        self.exit = ExitPad(ex, ex["next"])
        self.exit_rect = self.exit.rect

        self.hazards = [make_hazard(hz) for hz in data.get("hazards", [])]
        self.projectiles = []

        self.player = Player()
        sp = data["spawn"]
        self.spawn_pos = (sp["tx"] * T + T // 2, sp["ty"] * T + T // 2)
        self.player.spawn(*self.spawn_pos)

        self.recordings = []   # SESSION: cleared on room transition
        self.echoes = []
        self.cycle_tick = 0
        self.rec = Recording()
        self._death_pending = False
        self.last_reset_reason = None

        self.snapshot = self.capture_initial()

    # ---- solidity ----
    def is_solid(self, tx: int, ty: int) -> bool:
        if not (0 <= tx < self.w and 0 <= ty < self.h):
            return True
        if rooms.is_wall(self.data, tx, ty):
            return True
        for door in self.doors:
            if not door.open:
                for dx in range(door.tw):
                    for dy in range(door.th):
                        if (tx, ty) == (door.tx + dx, door.ty + dy):
                            return True
        return False

    # ---- snapshot ----
    def capture_initial(self) -> dict:
        return {
            "devices": {did: dev.snapshot() for did, dev in self.devices.items()},
            "hazards": [hz.snapshot() for hz in self.hazards],
        }

    def restore(self, snap: dict) -> None:
        for did, dsnap in snap["devices"].items():
            self.devices[did].restore(dsnap)
        for hz, hsnap in zip(self.hazards, snap["hazards"]):
            hz.restore(hsnap)
        self.projectiles = []

    # ---- kills ----
    def kill_player(self, events: list) -> None:
        if not self._death_pending:
            self._death_pending = True
            events.append("death")

    def kill_echo(self, echo: Echo, events: list) -> None:
        echo.kill_at(len(self.rec.frames))
        if echo in self.echoes:
            self.echoes.remove(echo)
        events.append("echo_death")

    # ---- interaction ----
    def _nearest_interactable(self):
        px, py = self.player.x, self.player.y
        best = None
        best_d = config.INTERACT_RADIUS
        for dev in self.consoles:
            d = math.hypot(dev.rect.centerx - px, dev.rect.centery - py)
            if d <= best_d:
                best, best_d = dev, d
        for t in self.terminals:
            tx, ty = t["tx"] * T + T // 2, t["ty"] * T + T // 2
            d = math.hypot(tx - px, ty - py)
            if d <= best_d:
                best, best_d = t, d
        return best

    def _plate_pressed(self, plate) -> bool:
        if (self.player.rect.colliderect(plate.rect)):
            return True
        return any(e.live and e.rect.colliderect(plate.rect) for e in self.echoes)

    # ---- main tick ----
    def tick(self, actions: dict) -> list:
        events = []
        # 1. timer
        self.cycle_tick += 1
        if self.cycle_tick >= config.CYCLE_TICKS:
            return self._do_reset("timer", events)
        if actions.get("reset"):
            return self._do_reset("manual", events)
        # 2. player
        self.player.update(actions, self)
        if actions.get("interact"):
            dev = self._nearest_interactable()
            if dev is not None:
                if isinstance(dev, Console):
                    dev.toggle()
                    # event index = frame index this tick will record
                    self.rec.events.append((len(self.rec.frames), dev.id))
                    events.append("interact")
                else:  # terminal dict
                    events.append(("terminal", dev["text"]))
        # 3. echoes
        for echo in list(self.echoes):
            if not echo.update(self, events):
                self.echoes.remove(echo)
        # 4. hazards
        self._death_pending = False
        for hz in self.hazards:
            hz.tick(self, events)
        # 5. devices recompute
        for plate in self.plates:
            was = plate.pressed
            plate.pressed = self._plate_pressed(plate)
            if plate.pressed != was:
                events.append("plate")
        for door in self.doors:
            if door.recompute(self.devices):
                events.append("door")
        # projectiles
        self._tick_projectiles(events)
        # 6. death
        if self._death_pending:
            return self._do_reset("death", events)
        # 7. exit (player only) — immediate on overlap; echoes never trigger
        if (self.player.rect.colliderect(self.exit_rect)):
            events.append(("exit", self.exit.next_room))
            return events
        # 8. record frame
        self.rec.frames.append((self.player.x, self.player.y, self.player.facing))
        return events

    def _tick_projectiles(self, events):
        for p in list(self.projectiles):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["rect"].center = (int(round(p["x"])), int(round(p["y"])))
            tx, ty = int(p["x"] // T), int(p["y"] // T)
            if self.is_solid(tx, ty):
                self.projectiles.remove(p)
                continue
            if (p["rect"].colliderect(self.player.rect)):
                self.projectiles.remove(p)
                self.kill_player(events)
                return
            for echo in list(self.echoes):
                if echo.live and (p["rect"].colliderect(echo.rect)):
                    self.projectiles.remove(p)
                    self.kill_echo(echo, events)
                    break

    # ---- reset ----
    def _do_reset(self, reason: str, events: list) -> list:
        rec = self.rec.finalize()
        if reason == "death":
            rec.death_tick = len(rec.frames)
        if rec.ticks >= config.MIN_RECORD_TICKS:
            self.recordings.append(rec)
            while len(self.recordings) > config.MAX_ECHOES:
                self.recordings.pop(0)
            events.append("echo_spawn")
        self.restore(self.snapshot)
        self.player.spawn(*self.spawn_pos)
        self.echoes = [Echo(r) for r in self.recordings]
        self.cycle_tick = 0
        self.rec = Recording()
        self._death_pending = False
        self.last_reset_reason = reason
        events.append("reset")
        events.append(f"reason:{reason}")
        return events
