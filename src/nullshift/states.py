"""Game state machine: TITLE / PLAYING / PAUSED / SECTORCARD / TERMINAL / LIA / GAMECOMPLETE.

No DEAD state (death = instant reset inside PLAYING). No LOADING state
(room build is synchronous). Save is in-memory until GATE 5 (D014).

Phase 5: Game owns Progression (D016). Room entry recomputes TEMPORAL
presentation (D017) and queues due LIA lines. Narrative beats are
data-driven (data/lia.json, room 'barks').
"""
import json
import os

from nullshift import rooms, strings, temporal
from nullshift.progression import Progression
from nullshift.sim import World

_LIA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "lia.json")
_LIA_CACHE = None


def load_lia_lines():
    global _LIA_CACHE
    if _LIA_CACHE is None:
        with open(_LIA_PATH, encoding="utf-8") as f:
            _LIA_CACHE = json.load(f)
    return _LIA_CACHE


class Game:
    def __init__(self):
        self.state = "TITLE"
        self.world = None
        self.sectors_seen = set()
        self.terminal_text = ""
        self.stats = {"cycles": 0, "deaths": 0, "manual_resets": 0}
        # in-memory unlock flags (save module lands at GATE 5, D014)
        self.unlocked = {"sector": 1, "room": "1.1"}
        # D016: persistent progression, owned by Game
        self.progression = Progression()
        # D017: TEMPORAL presentation of the current room
        self.temporal = {"lighting": "emergency", "terminal_texts": {}}
        # narrative presentation
        self.lia_queue = []          # pending LIA lines (dicts)
        self.lia_text = ""
        self.subtitle = None         # (text, ticks_left)
        self.reset_text = None       # (text, ticks_left) after a reset
        self._echo_bark_done = False

    # ---- flow ----
    def enter_room(self, room_id: str) -> None:
        data = rooms.load(room_id)
        visits = self.progression.visit(room_id)
        if data.get("set_phase"):
            self.progression.set_phase(data["set_phase"])
        self.world = World(data, self.progression)
        # D017: recompute TEMPORAL presentation at room entry
        self.temporal = temporal.compute(data, self.progression)
        self.world.terminal_texts = self.temporal["terminal_texts"]
        self.unlocked = {"sector": data["sector"], "room": room_id}
        # narrative: LIA lines due on this entry
        for line in load_lia_lines():
            if line["room"] == room_id and not self.progression.was_shown(line["id"]):
                t = line["trigger"]
                ok = (t.get("visit") == visits if "visit" in t
                      else bool(self.progression.get_flag(t["flag"])) if "flag" in t
                      else False)
                if ok:
                    self.progression.mark_shown(line["id"])
                    self.lia_queue.append(line)
        # narrative: room-entry barks (Elias)
        for bark in data.get("barks", []):
            if bark["trigger"] == "enter" and not self.progression.was_shown(bark["id"]):
                self.progression.mark_shown(bark["id"])
                self.set_subtitle(bark["text"])
        card = data.get("intro_card")
        sector = data["sector"]
        show = bool(card) or (sector not in self.sectors_seen
                              and sector in strings.SECTOR_CARDS)
        if show:
            self.sectors_seen.add(sector)
            self.pending_card = card or "\n".join(strings.SECTOR_CARDS[sector])
            self.state = "SECTORCARD"
        elif self.lia_queue:
            self._next_lia()
        else:
            self.state = "PLAYING"

    def _next_lia(self):
        line = self.lia_queue.pop(0)
        self.lia_text = line["text"]
        self.state = "LIA"

    def set_subtitle(self, text: str, ticks: int = 240) -> None:
        self.subtitle = [text, ticks]

    def start(self):
        self.__init__()
        self.enter_room("1.1")

    # ---- per-tick ----
    def tick(self, actions: dict) -> list:
        """Advance one sim tick. Returns UI-level events for audio/stats."""
        ui = []
        st = self.state
        if actions.get("pause") and st in ("PLAYING", "PAUSED"):
            self.state = "PAUSED" if st == "PLAYING" else "PLAYING"
            return ["pause"] if self.state == "PAUSED" else ["unpause"]
        if st == "TITLE":
            if actions.get("confirm"):
                self.enter_room("1.1")
                ui.append("start")
            return ui
        if st == "SECTORCARD":
            if actions.get("confirm") or actions.get("interact"):
                if self.lia_queue:
                    self._next_lia()
                else:
                    self.state = "PLAYING"
            return ui
        if st == "LIA":
            if actions.get("confirm") or actions.get("interact"):
                if self.lia_queue:
                    self._next_lia()
                else:
                    self.state = "PLAYING"
            return ui
        if st == "TERMINAL":
            if actions.get("interact") or actions.get("confirm") or actions.get("pause"):
                self.state = "PLAYING"
            return ui
        if st == "GAMECOMPLETE":
            if actions.get("confirm"):
                self.state = "TITLE"
            return ui
        if st == "PAUSED":
            return ui
        # PLAYING
        if actions.get("mute"):
            ui.append("mute_toggle")
        # subtitle countdown
        if self.subtitle:
            self.subtitle[1] -= 1
            if self.subtitle[1] <= 0:
                self.subtitle = None
        if self.reset_text:
            self.reset_text[1] -= 1
            if self.reset_text[1] <= 0:
                self.reset_text = None
        events = self.world.tick(actions)
        for ev in events:
            if ev == "reset":
                self.stats["cycles"] += 1
                self.reset_text = [f"CYCLE {self.stats['cycles'] + 1:02d}", 50]
            elif ev == "reason:death":
                self.stats["deaths"] += 1
            elif ev == "reason:manual":
                self.stats["manual_resets"] += 1
            elif ev == "echo_spawn" and not self._echo_bark_done:
                self._echo_bark_done = True
                self.set_subtitle("Huh. That's... me. Okay.")
            elif isinstance(ev, tuple) and ev[0] == "exit":
                nxt = ev[1]
                if nxt == "END":
                    self.state = "GAMECOMPLETE"
                    ui.append("game_complete")
                else:
                    self.enter_room(nxt)
                    ui.append("room_complete")
            elif isinstance(ev, tuple) and ev[0] == "terminal":
                self.terminal_text = ev[1]
                self.state = "TERMINAL"
            elif isinstance(ev, tuple) and ev[0] == "flag_set":
                flag = ev[1]
                self.progression.set_flag(flag)
                ui.append("flag_set")
                # barks triggered by this flag (any room's data is checked
                # on the current room only — flags are global by design)
                for bark in self.world.data.get("barks", []):
                    if (bark["trigger"] == f"flag:{flag}"
                            and not self.progression.was_shown(bark["id"])):
                        self.progression.mark_shown(bark["id"])
                        self.set_subtitle(bark["text"])
        ui.extend(e if isinstance(e, str) else e[0] for e in events
                  if e in ("interact", "door", "plate", "death", "echo_spawn",
                           "turret_charge", "turret_shot", "reset"))
        return ui
