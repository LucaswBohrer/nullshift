"""Persistent progression state (D016).

Owned by Game. Flat JSON-native dict. The cycle sim (World) receives a
read-only view and can NEVER write it — flags are set only by explicit
player actions or scripted story beats, applied by Game.

Every flag documents its owner and mutation point here:

  power_restored   owner: Game.on_flag_console   mutation: player toggles
                   the POWER relay console ON while its required consoles
                   are ON (never via echo playback)
  access_level     owner: (future)               mutation: (future, v1.0 unused)

phase: narrative phase, explicit values only ("WAKE", "POWER").
visits: per-room entry counters (drives LIA lines, temporal variants).
shown: ids of narrative beats already presented (lia lines, barks).
"""
import copy


class Progression:
    def __init__(self):
        self.flags = {}
        self.phase = "WAKE"
        self.visits = {}
        self.shown = set()

    # ---- flags ----
    def set_flag(self, name: str, value=True) -> None:
        self.flags[name] = value

    def get_flag(self, name: str, default=None):
        return self.flags.get(name, default)

    # ---- phase ----
    def set_phase(self, phase: str) -> None:
        self.phase = phase

    # ---- visits ----
    def visit(self, room_id: str) -> int:
        self.visits[room_id] = self.visits.get(room_id, 0) + 1
        return self.visits[room_id]

    # ---- shown beats ----
    def mark_shown(self, beat_id: str) -> None:
        self.shown.add(beat_id)

    def was_shown(self, beat_id: str) -> bool:
        return beat_id in self.shown

    # ---- serialization (future save; D014 still deferred) ----
    def to_dict(self) -> dict:
        return {
            "flags": copy.deepcopy(self.flags),
            "phase": self.phase,
            "visits": dict(self.visits),
            "shown": sorted(self.shown),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Progression":
        p = cls()
        p.flags = dict(d.get("flags", {}))
        p.phase = d.get("phase", "WAKE")
        p.visits = dict(d.get("visits", {}))
        p.shown = set(d.get("shown", []))
        return p
