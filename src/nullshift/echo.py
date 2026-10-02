"""Temporal recordings and echo playback (D004).

A Recording is written during a cycle, finalized on reset, then treated as
immutable — except for the single legal mutation: death_tick may be
tightened when an echo is destroyed mid-playback (ARCHITECTURE.md §4).
"""
import pygame

from nullshift import config


class Recording:
    def __init__(self):
        self.frames = []          # list[(x, y, facing)] per tick
        self.events = []          # list[(tick, device_id)] — console toggles
        self.death_tick = None    # int | None

    @property
    def ticks(self):
        return len(self.frames)

    def finalize(self):
        self.frames = tuple(self.frames)
        self.events = tuple(self.events)
        return self


class Echo:
    """Playback cursor over an immutable recording."""

    def __init__(self, recording: Recording):
        self.recording = recording
        self.cursor = 0
        self.x, self.y, self.facing = recording.frames[0]
        self.rect = pygame.Rect(0, 0, config.PLAYER_SIZE, config.PLAYER_SIZE)
        self._sync_rect()

    def _sync_rect(self):
        self.rect.center = (int(round(self.x)), int(round(self.y)))

    @property
    def vanish_at(self):
        dt = self.recording.death_tick
        return dt if dt is not None else self.recording.ticks

    @property
    def live(self):
        return self.cursor < self.vanish_at and self.cursor < self.recording.ticks

    def update(self, world, events: list) -> None:
        """Advance one tick: apply snapshot, fire due events. Returns False when done."""
        if not self.live:
            return False
        tick = self.cursor
        self.x, self.y, self.facing = self.recording.frames[tick]
        self._sync_rect()
        for etick, device_id in self.recording.events:
            if etick == tick:
                dev = world.devices.get(device_id)
                # Echoes only re-fire consoles (terminals are player-only).
                if dev is not None and dev.kind == "console":
                    dev.toggle()
                    events.append("echo_console")
        self.cursor += 1
        return self.live

    def kill_at(self, tick: int) -> None:
        """A hazard destroyed this echo: tighten death_tick (the legal mutation)."""
        dt = self.recording.death_tick
        self.recording.death_tick = tick if dt is None else min(dt, tick)
