"""Hazards: drones, turrets, laser grids, bolts.

Duck-typed: each hazard implements tick(world, events), snapshot(),
restore(). No shared base class — three kinds are too few for a hierarchy.
All timing is in ticks (D011).
"""
import math

import pygame

from nullshift import config

T = config.TILE


def _bresenham_los_clear(world, x0, y0, x1, y1) -> bool:
    """Tile raycast; walls (incl. closed doors) block. Endpoints excluded."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while not (x == x1 and y == y1):
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
        if (x == x1 and y == y1):
            break
        if world.is_solid(x, y):
            return False
    return True


class Drone:
    kind = "drone"

    def __init__(self, d: dict):
        self.id = d["id"]
        wps = d["waypoints"]  # list of [tx, ty]
        self.waypoints = [(wx * T + T // 2, wy * T + T // 2) for wx, wy in wps]
        self.speed = d.get("speed", 70) / config.TICK_HZ  # px/tick
        self.seg = 0
        self.seg_t = 0.0
        self.x, self.y = self.waypoints[0]
        self.rect = pygame.Rect(0, 0, 12, 12)
        self._sync()

    def _sync(self):
        self.rect.center = (int(round(self.x)), int(round(self.y)))

    def tick(self, world, events):
        a = self.waypoints[self.seg]
        b = self.waypoints[(self.seg + 1) % len(self.waypoints)]
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        if dist > 0:
            self.seg_t += self.speed / dist
        if self.seg_t >= 1.0:
            self.seg = (self.seg + 1) % len(self.waypoints)
            self.seg_t = 0.0
            a = self.waypoints[self.seg]
            b = self.waypoints[(self.seg + 1) % len(self.waypoints)]
        self.x = a[0] + (b[0] - a[0]) * self.seg_t
        self.y = a[1] + (b[1] - a[1]) * self.seg_t
        self._sync()
        if self.rect.colliderect(world.player.rect):
            world.kill_player(events)
            return
        for e in list(world.echoes):
            if e.live and self.rect.colliderect(e.rect):
                world.kill_echo(e, events)

    def snapshot(self):
        return {"seg": self.seg, "seg_t": self.seg_t}

    def restore(self, snap):
        self.seg = snap["seg"]
        self.seg_t = snap["seg_t"]
        a = self.waypoints[self.seg]
        b = self.waypoints[(self.seg + 1) % len(self.waypoints)]
        self.x = a[0] + (b[0] - a[0]) * self.seg_t
        self.y = a[1] + (b[1] - a[1]) * self.seg_t
        self._sync()


class Turret:
    kind = "turret"

    ARM_TICKS = 24  # 0.4 s telegraph

    def __init__(self, d: dict):
        self.id = d["id"]
        self.tx, self.ty = d["tx"], d["ty"]
        self.x = self.tx * T + T // 2
        self.y = self.ty * T + T // 2
        self.period = int(d.get("period", 2.5) * config.TICK_HZ)
        self.range = d.get("range", 220)
        self.bolt_speed = d.get("bolt_speed", 260) / config.TICK_HZ
        self.cooldown = self.period // 2  # first shot comes sooner
        self.armed = 0
        self.target = None
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.rect.center = (int(self.x), int(self.y))

    def _acquire(self, world):
        """D010: nearest in range + LoS; tie -> player, then lowest id."""
        cands = []
        if world.player.alive:
            cands.append(("player", world.player.x, world.player.y))
        for i, e in enumerate(world.echoes):
            if e.live:
                cands.append((f"echo{i}", e.x, e.y))
        best = None
        for name, x, y in cands:
            dist = math.hypot(x - self.x, y - self.y)
            if dist > self.range:
                continue
            tx, ty = int(x // T), int(y // T)
            if not _bresenham_los_clear(world, self.tx, self.ty, tx, ty):
                continue
            key = (dist, 0 if name == "player" else 1, name)
            if best is None or key < best[0]:
                best = (key, (x, y))
        return best[1] if best else None

    def tick(self, world, events):
        if self.armed > 0:
            self.armed -= 1
            if self.armed == 0 and self.target:
                tx, ty = self.target
                dx, dy = tx - self.x, ty - self.y
                dist = math.hypot(dx, dy) or 1.0
                vx = dx / dist * self.bolt_speed
                vy = dy / dist * self.bolt_speed
                world.projectiles.append({
                    "x": self.x, "y": self.y, "vx": vx, "vy": vy,
                    "rect": pygame.Rect(0, 0, 6, 6),
                })
                events.append("turret_shot")
                self.target = None
                self.cooldown = self.period
            return
        if self.cooldown > 0:
            self.cooldown -= 1
            if self.cooldown == 0:
                self.target = self._acquire(world)
                if self.target:
                    self.armed = self.ARM_TICKS
                    events.append("turret_charge")
                else:
                    self.cooldown = 30  # retry soon

    def snapshot(self):
        return {"cooldown": self.cooldown, "armed": self.armed}

    def restore(self, snap):
        self.cooldown = snap["cooldown"]
        self.armed = snap["armed"]
        self.target = None


class LaserGrid:
    kind = "laser"

    def __init__(self, d: dict):
        self.id = d["id"]
        x1, y1, x2, y2 = d["x1"], d["y1"], d["x2"], d["y2"]
        assert x1 == x2 or y1 == y2, "laser beams must be axis-aligned"
        self.on_ticks = int(d.get("on", 3.0) * config.TICK_HZ)
        self.off_ticks = int(d.get("off", 2.0) * config.TICK_HZ)
        self.warn_ticks = int(d.get("warn", 0.5) * config.TICK_HZ)
        self.phase = 0
        xa, xb = sorted([x1, x2])
        ya, yb = sorted([y1, y2])
        self.rect = pygame.Rect(xa * T, ya * T, (xb - xa + 1) * T, (yb - ya + 1) * T)

    @property
    def cycle(self):
        return self.on_ticks + self.off_ticks

    @property
    def active(self):
        return (self.phase % self.cycle) < self.on_ticks

    @property
    def warning(self):
        p = self.phase % self.cycle
        return self.on_ticks <= p < self.on_ticks + self.warn_ticks

    def tick(self, world, events):
        self.phase += 1
        if self.active:
            if self.rect.colliderect(world.player.rect):
                world.kill_player(events)
                return
            for e in list(world.echoes):
                if e.live and self.rect.colliderect(e.rect):
                    world.kill_echo(e, events)

    def snapshot(self):
        return {"phase": self.phase}

    def restore(self, snap):
        self.phase = snap["phase"]


def make_hazard(d: dict):
    htype = d["type"]
    if htype == "drone":
        return Drone(d)
    if htype == "turret":
        return Turret(d)
    if htype == "laser":
        return LaserGrid(d)
    raise ValueError(f"unknown hazard type: {htype}")
