"""Game state machine: TITLE / PLAYING / PAUSED / SECTORCARD / TERMINAL / GAMECOMPLETE.

No DEAD state (death = instant reset inside PLAYING). No LOADING state
(room build is synchronous). Save is in-memory until GATE 5 (D014).
"""
from nullshift import rooms, strings
from nullshift.sim import World


class Game:
    def __init__(self):
        self.state = "TITLE"
        self.world = None
        self.sectors_seen = set()
        self.terminal_text = ""
        self.stats = {"cycles": 0, "deaths": 0, "manual_resets": 0}
        # in-memory unlock flags (save module lands at GATE 5, D014)
        self.unlocked = {"sector": 1, "room": "1.1"}

    # ---- flow ----
    def enter_room(self, room_id: str) -> None:
        data = rooms.load(room_id)
        self.world = World(data)
        self.unlocked = {"sector": data["sector"], "room": room_id}
        card = data.get("intro_card")
        sector = data["sector"]
        show = bool(card) or (sector not in self.sectors_seen
                              and sector in strings.SECTOR_CARDS)
        if show:
            self.sectors_seen.add(sector)
            self.pending_card = card or "\n".join(strings.SECTOR_CARDS[sector])
            self.state = "SECTORCARD"
        else:
            self.state = "PLAYING"

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
        events = self.world.tick(actions)
        for ev in events:
            if ev == "reset":
                self.stats["cycles"] += 1
            elif ev == "reason:death":
                self.stats["deaths"] += 1
            elif ev == "reason:manual":
                self.stats["manual_resets"] += 1
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
        ui.extend(e if isinstance(e, str) else e[0] for e in events
                  if e in ("interact", "door", "plate", "death", "echo_spawn",
                           "turret_charge", "turret_shot", "reset"))
        return ui
