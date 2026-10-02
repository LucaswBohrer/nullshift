# Architecture — NULL//SHIFT

**Status:** LOCKED at GATE 3 (2026-10-02). Implementation of the vertical
slice is authorized against this document. Changes require a new decision
record (D015+) — never silent edits.

**Authority order:** GAME_SCOPE.md → SCOPE_AUDIT.md → DECISIONS.md → this
document → TECHNICAL_REQUIREMENTS.md → BUILD.md → ROADMAP.md.

**Guiding constraint:** this is a ~3–4 kLOC Pygame game, not an engine.
Every abstraction below names the concrete NULL//SHIFT problem it solves.

---

## 1. Project structure (D013)

```text
nullshift/
├── src/nullshift/            # single package; flat modules
│   ├── __main__.py           # python -m nullshift entry
│   ├── main.py               # init, top-level state machine, --smoke/--version
│   ├── version.py            # __version__ = "0.1.0"
│   ├── config.py             # constants: tick rate, cycle ticks, paths, keymap
│   ├── paths.py              # resource_path() — dev vs PyInstaller (sys._MEIPASS)
│   ├── states.py             # BOOT/TITLE/PLAYING/PAUSED/SECTORCARD/GAMECOMPLETE
│   ├── input.py              # polled action sets; injectable for tests
│   ├── sim.py                # World: tick order, reset, recordings, echoes
│   ├── player.py             # movement + interaction + death
│   ├── echo.py               # Recording (immutable) + Echo (playback cursor)
│   ├── hazards.py            # Drone, Turret, LaserGrid, Bolt (duck-typed)
│   ├── devices.py            # PressurePlate, Console, Door, ExitPad, Terminal
│   ├── rooms.py              # room data load + validate + build + snapshot
│   ├── collision.py          # AABB helpers (D012)
│   ├── render.py             # 640×360 surface, layers, integer scale, HUD
│   ├── sprites.py            # load + cache + echo palette swap
│   ├── particles.py          # visual-only: reset ring, sparks, shimmer
│   ├── synth.py              # procedural SFX → mixer buffers at boot
│   ├── sequencer.py          # chiptune step sequencer
│   ├── audio.py              # mixer init, channels, volumes, mute, silent fallback
│   ├── save.py               # versioned JSON (SPEC LOCKED; impl at GATE 5, D014)
│   ├── strings.py            # all UI/log text in one module
│   └── debug.py              # DEV overlay (F1–F4); stripped/disabled in release
├── data/rooms/*.json        # room data (D009)
├── assets/                   # art/, icon.ico (populated during production)
├── tests/                    # pytest: unit + room validation + replay regression
├── tools/
│   ├── validate_rooms.py     # schema + reachability, run in CI/build
│   └── build.ps1             # clean → test → package → smoke → zip
├── docs/
└── build.spec                # PyInstaller one-dir (D007)
```

Justification: one package keeps imports obvious (`from nullshift.sim
import World`); subpackages (`sim/`, `render/`) were rejected as
over-segmentation for this size (D013). `sim.py` is intentionally the
largest module — the temporal model lives in exactly one place.

---

## 2. Room data architecture (D009)

Format: **JSON**, `"format_version": 1`. Example (Room 1.2, abbreviated):

```json
{
  "format_version": 1,
  "id": "1.2",
  "name": "First Debt",
  "sector": 1,
  "intro_card": "CUSTODIAN: Temporal debt registered. Your previous self will assist you.",
  "tint": "amber",
  "grid": {
    "w": 40, "h": 22,
    "legend": { "#": "wall", ".": "floor", ",": "floor_dark", "=": "floor_hazard" },
    "rows": ["########################################", "..."]
  },
  "spawn": { "tx": 2, "ty": 11 },
  "devices": [
    { "id": "plate1", "type": "pressure_plate", "tx": 10, "ty": 11 },
    { "id": "door1",  "type": "door", "tx": 20, "ty": 10, "th": 1, "tw": 2,
      "links": ["plate1"], "mode": "any" }
  ],
  "hazards": [
    { "id": "tur1", "type": "turret", "tx": 30, "ty": 5,
      "period": 2.5, "range": 220, "bolt_speed": 260 }
  ],
  "terminals": [
    { "id": "log1", "tx": 5, "ty": 11, "text": "OKAFOR: If you're reading this, the loop held." }
  ],
  "exit": { "tx": 38, "ty": 11, "next": "2.1" }
}
```

**Schema rules** (enforced by `tools/validate_rooms.py`, fail loud):
- Required: `format_version`, `id`, `sector`, `grid` (+ all rows equal
  length, only legend chars), `spawn` (on floor), `exit` (+ `next`).
- All device/hazard/terminal ids unique per room; `links` must resolve;
  devices/hazards/terminals/exit/spawn must sit on non-wall tiles.
- `format_version` unknown → loader refuses with explicit error.
- Missing optional fields → documented defaults (`tint: "blue"`,
  `intro_card: null`, door `mode: "any"`, turret defaults per schema).
- Defaults are listed in `rooms.py` next to the loader — one place.

**Validation levels:**
1. *Structural* (validator + loader): schema, legend, links, bounds.
2. *Reachability* (validator): flood fill from spawn to exit ignoring
   hazards — a room that is unreachable even in principle is a data bug.
3. *Solvability bound* (validator, heuristic): rooms declaring > 3
   simultaneously-required plates fail — echoes cap at 3 (D005), so the
   data must respect the mechanic.

**Versioning:** bump `format_version` on any breaking schema change;
loader keeps a migration table (v1 → v2 …); unknown version = loud error,
never silent misload.

---

## 3. Room lifecycle

```text
enter_room(room_id):
  data     = rooms.load(room_id)          # validated; loud on error
  world    = World.build(data)            # tiles, devices, hazards, spawn
  snapshot = world.capture_initial()      # RESETTABLE baseline
  recordings.clear()                      # SESSION reset (echoes don't cross rooms)
  echoes.clear()
  player.spawn(data.spawn)
  cycle = Cycle.new(length_ticks=2400)
  state = PLAYING
```

```text
on_reset(reason):                         # reason ∈ {timer, manual, death}
  rec = cycle.finalize_recording()        # None if < 60 ticks (anti-misclick)
  if rec: recordings.push_fifo(rec, cap=3)  # D005
  world.restore(snapshot)                 # RESETTABLE ← baseline; projectiles purged
  player.spawn(data.spawn)
  echoes = [Echo(r) for r in recordings]  # cursors at tick 0
  cycle = Cycle.new()                     # timer + fresh recording
  fx.reset_flash(reason)                  # 150 ms visual; sim already running
  # NOTE: no RESETTING gameplay state — reset is logically instantaneous.
```

```text
on_exit_pad():
  # The in-progress recording is UNFINISHED → discarded (never an echo).
  unlock(next); save.write()              # save impl at GATE 5; in-memory until then
  enter_room(next)
```

Guarantee: `world.restore(snapshot)` returns every RESETTABLE value to
its room-entry value; the guarantee is tested, not assumed (§19.5).

---

## 4. Temporal snapshot model

### 4.1 Tick (D011)

Fixed 60 Hz accumulator. Everything temporal is counted in **ticks**:
cycle = 2400 ticks; recording cap = 2400 entries; hazard periods stored
as ticks (2.5 s = 150 ticks). No wall-clock time inside `sim.py`.

### 4.2 Recording (immutable)

```text
Recording:
  ticks: int                       # total length, ≤ 2400
  frames: list[(x: float, y: float, facing: int)]   # one per tick
  events: list[(tick: int, device_id: str, action: str)]  # interact/activate
  death_tick: int | None           # set if the run died (echo vanishes after)
```

Memory: 2400 × ~16 B ≈ 40 KB/recording; ≤ 3 recordings + 1 live — trivial
(Risk A: LOW, quantified).

### 4.3 Snapshot (room baseline)

Minimal RESETTABLE state captured at room entry:
- per device: `{id: state}` (door open/closed, plate pressed/unpressed,
  console on/off)
- per hazard: initial dynamic state (drone waypoint index + t, turret
  cooldown, laser phase)
- projectiles: none (purged on reset — they never belong to a snapshot)

Player transform is NOT in the snapshot — the player always respawns at
`data.spawn`. This is the smallest correct baseline.

### 4.4 Echo

```text
Echo:
  recording: Recording   # immutable, shared
  cursor: int            # current tick
  death_tick: int|None   # from recording; echo removed when cursor passes it
  sprite: echo-tinted player frames
  update(world):         # called in fixed tick order after player
    pos = recording.frames[cursor]; fire events at cursor; cursor += 1
    if cursor > death_tick: despawn
```

Echoes do **no tile collision** (D012): recorded positions were valid when
recorded. Echoes DO AABB checks against hazards (to die) and devices (to
trigger).

---

## 5. Echo normative rules — CAN / CANNOT

An echo **CAN**:
- trigger pressure plates (stand = pressed, exactly as recorded)
- toggle consoles (re-fires recorded interact events)
- be hit and destroyed by drones, turret bolts, laser beams
- block line-of-sight for turrets (it is a valid target, D010)

An echo **CANNOT**:
- collide with the player (no interaction whatsoever)
- trigger exit pads (only the living player advances rooms)
- interact with another echo (no echo–echo physics or triggering)
- affect persistent state (unlocks, stats, settings)
- leave its room (recordings are per-room SESSION state)
- be created from a run shorter than 60 ticks
- exceed the FIFO cap: the 4th recording discards the oldest (D005);
  **the living player is NOT counted in the cap** — the cap is on
  recordings/echoes only.

Death semantics: a destroyed echo replays only up to `death_tick` in all
future cycles, then vanishes. A fatal player run becomes an echo that
replays up to its own `death_tick` — this is the sacrifice mechanic,
and it falls out of the model with no special cases.

---

## 6. Reset state classification

| Category | Contents | Lifecycle |
|---|---|---|
| RESETTABLE | device states, hazard dynamic state, player transform, cycle timer, projectiles (purged) | restored from room-entry snapshot on every reset |
| PERSISTENT | unlocked sector/room, settings, stats | save file; never touched by reset |
| SESSION | echo recordings, live echo list, current cycle | cleared on room transition; recordings accumulate across cycles within a room |
| DERIVED | render caches, LoS raycast results, sprite cache | recomputed; never stored |

Every game value must live in exactly one row. The reset test (§19.5)
asserts the RESETTABLE row exhaustively.

---

## 7. Hazard architecture

No combat system (D008). Three hazard kinds, duck-typed — same method
names, no shared base class (three is too few for a hierarchy):

```text
hazard.tick(world)    # advance one tick; may spawn projectiles / kill
hazard.rect           # AABB for overlap tests
hazard.draw(surf)     # 2-frame or phase-driven art
```

- **Drone:** waypoint list (data), speed 70 px/s → ticks; loops; touch =
  kill target. Emits hum when player within 120 px (audio cue + visual
  ring — no audio-only mechanics).
- **Turret:** fixed; every `period` ticks: acquire target (D010) →
  0.4 s armed telegraph (24 ticks: red blink + charge sound) → fire bolt
  (`bolt_speed` px/s, dies on wall or on hitting player/echo). Bolt is a
  minimal `{rect, vel}` — not an entity, purged on reset.
- **LaserGrid:** emitter pair + beam tiles; cycle 3 s on / 2 s off in
  ticks, 0.5 s warning flicker; overlap while on = kill target.

Kill resolution: any hazard overlap with player → `on_reset(death)`;
with echo → set echo `death_tick = current tick`, despawn at cycle end
(it already vanished visually at hit + spark particles).

**Turret targeting (D010, normative):** candidates = living player +
echoes with `cursor <= death_tick`; filter range (Euclidean ≤ `range`)
and LoS (Bresenham raycast on tile grid, walls block); nearest wins;
tie → player, then lowest id. Re-evaluated at each shot decision only.

---

## 8. Interaction system

Proximity + explicit key (E). No directional facing requirement — the
radius is generous (24 px), which playtests better than facing cones.

```text
device = {
  id, kind: plate|console|door|exit|terminal,
  rect, state,
  on_enter(entity), on_exit(entity),       # plates: any entity incl. echoes
  on_interact(entity),                     # consoles/terminals: player OR echo event
  resettable: True                         # all devices reset (no persistent devices v1.0)
}
```

- Plates: `on_enter/on_exit` recompute pressed set each tick from
  overlapping entities (player + echoes) — no event ordering bugs.
- Doors: `links` + `mode: any|all`; recompute open/closed from linked
  device states each tick — derived, never stored.
- Consoles: toggle on interact; echo re-fires via recorded events (§4.2).
- Terminals: overlay text card; sim pauses (like PAUSED) until dismissed.
- ExitPad: player-only overlap → room transition, immediate (D015;
  the 30-tick hold was dropped: a walking player crosses the pad in ~9
  ticks, making the hold unreachable).

---

## 9. Collision (D012)

`pygame.Rect` AABB only. Player movement: move X, resolve vs solid tiles;
move Y, resolve. At 110 px/s ÷ 60 Hz = 1.9 px/tick — no tunneling, no
swept tests needed. Echoes skip tile collision (§4.4). Projectiles die on
first solid tile. Debug F2 draws all rects.

---

## 10. Game state machine

```text
BOOT → TITLE → PLAYING ⇄ PAUSED
                 ↓ (exit pad)
            SECTORCARD → PLAYING        # skippable intro card on sector entry
                 ↓ (final exit)
            GAMECOMPLETE → TITLE
```

- No DEAD state: death is `on_reset(death)` inside PLAYING (< 1 s turnaround).
- No RESETTING state: reset is logically instantaneous + 150 ms FX overlay.
- No LOADING state: room build is synchronous (< 500 ms budget); BOOT shows
  progress for synth asset generation.
- PAUSED freezes the accumulator (timer, sim, sequencer position).

---

## 11. Input

`input.py`: per tick, poll `pygame.key.get_pressed()` → action set
`{up,down,left,right,interact,reset,pause,mute}`. Keymap in `config.py`
(arrows/WASD, E, R, Esc, M). **Testability:** `sim.tick(actions)` takes
the action set as a parameter — scripted replays drive the sim with zero
pygame input involved. No mouse. No controller in v1.0 (documented).

---

## 12. Rendering

- Offscreen 640×360 surface; `pygame.transform.scale ×2` → 1280×720
  (integer scale, no smoothing — crisp pixels).
- Layer order: tiles → devices → hazards → echoes → player → projectiles
  → particles → atmosphere (vignette/scanline, cheap) → HUD (timer bar,
  echo pips, objective line) → overlays (pause, terminal card, FX flash).
- Camera: rooms are designed to fit 640×360; smaller rooms are centered
  (letterbox inside the internal surface).
- Room transition: hard cut + 150 ms reset flash. No scrolling, no fancy
  transitions in v1.0.

---

## 13. Audio

- `audio.py`: `pygame.mixer.pre_init(44100, -16, 2, 512)`; init wrapped —
  failure → `silent=True`, game runs without audio (never crashes).
- `synth.py`: generates all SFX buffers at BOOT (square/triangle/noise +
  envelopes): step, interact, console, door, plate, laser_warn, laser_hit,
  turret_charge, turret_shot, drone_hum (loop), reset_swish, echo_shimmer,
  ui_move, ui_ok, sector_chime, death_zap. **Zero audio files in repo.**
- `sequencer.py`: 64-step patterns, 2 loops ("drift" 90 BPM,
  "pressure" 132 BPM); schedules via mixer channels from the game tick.
- Channels: master/music/sfx/ambient volumes 0–100 + mute-all (M);
  persisted in settings (save module, GATE 5).

---

## 14. Save system (spec locked, implementation at GATE 5 — D014)

```json
{ "version": 1, "unlocked": { "sector": 2, "room": "2.1" },
  "settings": { "master": 80, "music": 70, "sfx": 80, "ambient": 60,
                "mute": false, "fullscreen": false },
  "stats": { "cycles": 0, "deaths": 0, "resets_manual": 0,
             "completions": 0, "best_cycles": {} } }
```

- Location: `%APPDATA%/NULLSHIFT/saves/save.json` (Windows); fallback
  `./saves/` beside the exe if APPDATA is unavailable.
- Write: temp file + atomic rename. Load: unknown `version` → explicit
  error + defaults (never crash); corrupt JSON → quarantine to
  `saves/corrupt-<ts>.json`, start fresh.
- Until GATE 5: in-memory equivalent with identical field names, so the
  implementation is a drop-in.

---

## 15. Data vs code

**Data** (`data/rooms/*.json`, `strings.py`, `config.py` constants):
room layouts, hazard parameters, spawn/exit, device linkage, objective
text, terminal logs, tuning numbers (speeds, periods, ranges).

**Code** (`sim.py`, `hazards.py`, `echo.py`, …): tick order, playback,
collision, reset, rendering, state transitions, synth/sequencer.

Rule: if a designer (Lucas) should tweak it without reading sim logic,
it's data. Room-specific *behavior* does not exist — Rooms 1.1/1.2 use
zero special-case code (§18).

---

## 16. Determinism

Matters where puzzles depend on it: tick order (§3), echo playback
(§4.2 — snapshots, not re-simulation, so determinism is structural),
hazard periods (ticks), turret targeting (D010), reset (snapshot
restore). Visual particles may use RNG freely — they never affect sim
state. Fixed update order per tick is documented in `sim.tick` and
covered by replay regression tests.

---

## 17. Test architecture

`tests/` (pytest; no pygame display needed — sim imports must not require
an initialized display; render/audio are never imported by sim tests):

1. **Room loading:** invalid JSON / bad legend / dangling link / unknown
   version → `RoomError` with message naming file + field. Valid rooms
   load.
2. **Snapshot/reset:** scripted actions mutate devices → `on_reset` →
   assert every RESETTABLE value equals room-entry baseline (§6 table).
3. **Echo fidelity:** scripted 300-tick run → reset → assert echo
   positions/events match recording tick-for-tick.
4. **FIFO:** push 4 recordings → assert oldest discarded, order kept.
5. **Room transition:** enter room with echoes → assert echoes and
   recordings cleared, new snapshot taken.
6. **Death flow:** force hazard overlap → assert reset reason `death`,
   fatal run recorded with correct `death_tick`, echo replays then
   vanishes.
7. **Hazard determinism:** fixed action script, N ticks → identical
   hazard states across runs (turret shot ticks asserted exactly).
8. **Validator:** corrupt room fixtures fail `validate_rooms.py`;
   unreachable-exit fixture fails reachability.
9. **Replay regression:** recorded input scripts for Rooms 1.2 and 3.3
   assert completion within expected tick bounds (written once rooms
   exist; the harness exists at slice time).
10. **Build smoke:** `--smoke` boots to TITLE and loads Room 1.1
    headless-ish (dummy video driver allowed), exit 0.

---

## 18. Vertical slice support

Rooms 1.1 ("Wake": move, interact, console→door, timer, manual reset)
and 1.2 ("First Debt": forced first reset → echo holds plate) are pure
room data + the generic systems above. No `if room_id == ...` anywhere;
the slice exercises every architectural seam (record → reset → playback
→ device trigger → exit) with the smallest possible content.

---

## 19. Debug tools (`debug.py`, DEV builds only)

- **F1:** overlay — FPS, room id, cycle tick/2400, echo count, recording
  ticks, last reset reason.
- **F2:** collision rects + LoS rays.
- **F3:** hazard viz — turret range circles, laser timing phase, drone
  waypoints.
- **F4:** room warp prompt (debug room loading without playing through).
- Disabled (compiled out via `DEV = False`) in release builds. Not an
  editor — just enough to develop and test fast.

---

## 20. Error handling

| Failure | Dev behavior | Release behavior |
|---|---|---|
| Room file missing/invalid | traceback + `RoomError(file, field)` | title-screen error card naming the room; log file; no crash loop |
| Asset (art) missing | raise | magenta placeholder + log (art is non-fatal) |
| Audio device missing | — | silent mode, game continues |
| Save corrupt | — | quarantine + fresh defaults |
| Unexpected exception | traceback | error dialog + `error.log`, clean exit — never silent |

Nothing is swallowed: every `except` either re-raises, shows UI, or logs.

---

## 21. Asset loading (dev vs release)

`paths.resource_path(rel)`: `sys._MEIPASS` when frozen (PyInstaller),
else repo root. Art: `assets/art/*.png` loaded via `sprites.py` cache;
room data: `data/rooms/*.json`. No absolute paths, no CWD dependence —
the exe runs from any directory. PyInstaller `build.spec` bundles
`data/` and `assets/` explicitly (verified by `--smoke` in the pipeline).

---

## 22. Risks A–J

| Risk | Level | Mitigation |
|---|---|---|
| A — recordings too large | LOW | quantified: ~40 KB/echo, cap 3 + live |
| B — snapshot maintenance | LOW | explicit RESETTABLE capture/restore + reset test (§17.2) |
| C — room data over-engineering | MEDIUM | minimal schema, validator, no scripting in data |
| D — pixel-art critical path | HIGH | placeholder-first policy; palette-swap echoes; code particles; 0 backgrounds |
| E — 40 s cycle wrong | MEDIUM | tunable constant; slice must validate (audit M2) |
| F — 3-echo unintended interactions | MEDIUM | normative §5 rules; validator plate bound; hardest rooms scheduled last |
| G — PyInstaller asset breakage | MEDIUM | `resource_path()`; `--smoke`; clean-machine GATE 8 |
| H — collision player vs echo | LOW | retired by D012: echoes skip tile collision by construction |
| I — reset state leaks | MEDIUM | §6 classification; exhaustive reset test |
| J — architecture > game | MEDIUM | this document's constraint; audit §23 checks it |

---

## 23. Architecture self-audit

- **CONSISTENCY:** matches GAME_SCOPE (echo rules §4/§5 formalize scope
  §4; hazards match scope §8; no new gameplay systems).
- **DECISIONS:** D001–D008 validated — all KEEP except D006 amended
  (room-entry snapshot correction, recorded). New: D009–D014.
  (Note: the GATE 3 brief's D001–D008 shorthand used different glosses
  for D002/D003/D007; the decision *records* in DECISIONS.md are
  authoritative, not the brief's shorthand.)
- **COMPLEXITY:** single package, ~20 modules, duck-typed hazards, no
  ECS/event-bus/DI. Proportionate.
- **TESTABILITY:** sim takes injected action sets; 10 test areas defined;
  temporal mechanics testable with zero manual gameplay.
- **DATA:** new rooms = new JSON + validator pass; zero engine changes.
- **RESET:** deterministic, complete, tested (§17.2, §17.5).
- **ECHO:** formally defined (§4–§6).
- **BUILD:** Windows exe path defined (BUILD.md + §21).
- **SCOPE:** architecture introduced no gameplay systems (debug tools are
  dev-only and compiled out).

**Result: PASS.** All 10 implementation-lock criteria (§35 of the brief)
are satisfied at the documentation level.
