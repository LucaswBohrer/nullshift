"""Interactable devices. All state is RESETTABLE; snapshot()/restore() cover it."""
import pygame

from nullshift import config

T = config.TILE


class Device:
    kind = "device"

    def __init__(self, d: dict):
        self.id = d["id"]
        self.tx = d["tx"]
        self.ty = d["ty"]
        self.rect = pygame.Rect(self.tx * T, self.ty * T, T, T)

    def snapshot(self) -> dict:
        return {}

    def restore(self, snap: dict) -> None:
        pass

    def solid_tiles(self):
        return []


class PressurePlate(Device):
    kind = "pressure_plate"

    def __init__(self, d: dict):
        super().__init__(d)
        self.pressed = False

    def snapshot(self):
        return {"pressed": self.pressed}

    def restore(self, snap):
        self.pressed = snap["pressed"]


class Console(Device):
    kind = "console"

    def __init__(self, d: dict):
        super().__init__(d)
        self.on = False
        # D016: optional persistent flag set on PLAYER rising edge only.
        # Echoes re-firing this console never set the flag (D017 invariant).
        self.sets_flag = d.get("sets_flag")
        self.requires_on = list(d.get("requires_on", []))

    def toggle(self):
        self.on = not self.on

    def snapshot(self):
        return {"on": self.on}

    def restore(self, snap):
        self.on = snap["on"]


class Door(Device):
    kind = "door"

    def __init__(self, d: dict):
        super().__init__(d)
        self.tw = d["tw"]
        self.th = d["th"]
        self.links = list(d["links"])
        self.mode = d.get("mode", "any")
        self.rect = pygame.Rect(self.tx * T, self.ty * T, self.tw * T, self.th * T)
        self.open = False

    def recompute(self, devices: dict) -> bool:
        """Recompute open state from linked devices. Returns True if changed."""
        states = []
        for link in self.links:
            dev = devices[link]
            if isinstance(dev, PressurePlate):
                states.append(dev.pressed)
            elif isinstance(dev, Console):
                states.append(dev.on)
            else:
                states.append(False)
        new_open = all(states) if self.mode == "all" else any(states)
        changed = new_open != self.open
        self.open = new_open
        return changed

    def solid_tiles(self):
        if self.open:
            return []
        return [(self.tx + dx, self.ty + dy) for dy in range(self.th) for dx in range(self.tw)]

    def snapshot(self):
        return {"open": self.open}

    def restore(self, snap):
        self.open = snap["open"]


class ExitPad(Device):
    kind = "exit_pad"

    def __init__(self, d: dict, next_room: str):
        # d here is the exit dict (no 'id'/'type' required); synthesize them.
        super().__init__({"id": d.get("id", "exit"), "tx": d["tx"], "ty": d["ty"]})
        self.next_room = next_room
        # D016: optional persistent-flag gate, e.g. {"power_restored": True}
        self.requires = dict(d.get("requires", {}))

    def unlocked(self, progression) -> bool:
        if progression is None:
            return not self.requires
        return all(progression.get_flag(f) == want for f, want in self.requires.items())


class Terminal(Device):
    kind = "terminal"

    def __init__(self, d: dict):
        super().__init__(d)
        self.text = d["text"]


def make_device(d: dict) -> Device:
    dtype = d["type"]
    if dtype == "pressure_plate":
        return PressurePlate(d)
    if dtype == "console":
        return Console(d)
    if dtype == "door":
        return Door(d)
    if dtype == "terminal":
        return Terminal(d)
    raise ValueError(f"unknown device type: {dtype}")
