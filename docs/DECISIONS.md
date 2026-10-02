# Decision Records — NULL//SHIFT

Supersede, never rewrite. New decisions get the next number.

---

## D001 — Engine: Pygame (Python)

- **Status:** PROVISIONAL — re-validate at architecture gate (GATE 3)
- **Context:** Prior agreement with Lucas (2026-10-01): Python/Pygame on
  his Windows machine. Must re-check against NULL//SHIFT's actual needs:
  2D top-down, < 300 entities, software-rendered pixel art, no physics
  engine, deterministic fixed-timestep sim, procedural audio.
- **Decision:** Pygame 2.x, Python 3.12+.
- **Alternatives considered:**
  - *Godot 4:* stronger editor/tooling, but GDScript + export pipeline is
    a new stack for a one-weekend build; overkill for tilemap/AABB scope.
  - *Arcade (Python):* cleaner API but smaller community, weaker
    PyInstaller lore, no meaningful advantage for this scope.
  - *Custom engine (SDL/raylib via C):* maximum control, unjustifiable
    time cost.
- **Consequences:** Fastest path to playable; software rendering is fine
  at 640×360; must be disciplined about fixed timestep (Pygame gives no
  engine loop guarantees). Single-language stack (game + tools + build
  scripts).

## D002 — Rendering: software 2D, fixed internal resolution

- **Status:** PROVISIONAL
- **Context:** Pixel-art readability and deterministic timing matter more
  than GPU effects.
- **Decision:** One 640×360 offscreen surface, integer-scaled ×2 to
  1280×720. All sprites 16×16 base. No shaders, no GPU dependency.
- **Consequences:** Runs on decade-old integrated graphics; scaling is
  trivially correct; fullscreen letterboxing handled once.

## D003 — Save format: versioned JSON

- **Status:** ACCEPTED (scope-level)
- **Context:** Save must survive future versions detecting incompatibility
  safely (§11 of scope).
- **Decision:** `{"version": 1, ...}` JSON at `%APPDATA%/NULLSHIFT/saves/`,
  write-temp-then-rename, corrupt file quarantined, never crash on load.
- **Alternatives:** pickle (rejected: unsafe, version-fragile), SQLite
  (rejected: overkill for ~1 KB of state).

## D004 — Echo replay: per-tick snapshot playback, NOT input re-simulation

- **Status:** ACCEPTED (scope-level)
- **Context:** Echoes must replay *exactly*, including interactions.
  Input re-simulation is elegant but fragile: any nondeterminism (float
  drift, ordering) breaks puzzles silently.
- **Decision:** Record `(x, y, facing)` per tick + discrete action events
  with tick stamps. Playback sets transforms and re-fires events.
  2400 ticks × ~16 bytes ≈ 40 KB per echo — negligible.
- **Consequences:** Echoes are robust by construction; slight memory cost;
  echo-vs-hazard uses the same AABB checks as the player.

## D005 — Echo cap: 3, FIFO discard

- **Status:** ACCEPTED (scope-level)
- **Context:** Unbounded echoes trivialize puzzles ("flood the room with
  selves") and unbounded memory; a cap is also a design tool (which echo
  do you sacrifice?).
- **Decision:** Max 3 echoes; 4th reset discards the oldest. HUD pips show
  count. Runs < 60 ticks are not recorded (anti-misclick).
- **Consequences:** Room designs assume ≤ 3 helpers; final room is tuned
  for exactly 3.

## D006 — Cycle model: 40 s fixed, reset on timer/manual/death

- **Status:** ACCEPTED (scope-level; constant tunable after slice)
- **Context:** The loop needs a legible rhythm and a failure cost that is
  fast, not punishing.
- **Decision:** 40 s cycle; R = manual reset; death = instant reset that
  still records the fatal run (enables sacrifice puzzles). Pause freezes
  the timer. World state reverts to sector-entry snapshot each reset;
  only recordings, unlocks, and stats persist.
- **Consequences:** 1-HP design is fair because reset-to-retry is < 1 s;
  puzzles must be solvable within 40 s by construction.
- **Amended 2026-10-02 (GATE 3):** "sector-entry snapshot" corrected to
  **room-entry snapshot** per the scope audit (M1). Snapshots are taken
  at room entry; room transitions clear echoes; checkpoints are per room.
  The original wording was a scope-draft error, corrected here explicitly,
  not silently.

## D007 — Windows build: PyInstaller one-dir

- **Status:** PROVISIONAL
- **Context:** Player must not need Python. One-file exe has slower
  startup (unpack to temp each launch); one-dir is faster and
  debuggable, zipped for distribution.
- **Decision:** PyInstaller `one-dir` → `dist/NULLSHIFT/NULLSHIFT.exe`,
  zipped as `NULLSHIFT-<version>-win64.zip` for GitHub Releases.
- **Consequences:** ~40–80 MB package (bundled interpreter); must test on
  a clean Windows VM/machine without Python.

## D008 — No player combat system

- **Status:** ACCEPTED (scope-level)
- **Context:** Identity decision: fantasy is cleverness, not power.
- **Decision:** No attacks, weapons, or HP. Hazards (drones, turrets,
  lasers) are the entire action layer; death = reset.
- **Consequences:** All "difficulty" is puzzle/timing design; no combat
  code, balance, or animation scope. If playtesting shows the game feels
  empty moment-to-moment, the fix is hazard *density/choreography*, not
  adding attacks (would need a new decision record).

---

## D009 — Room data format: JSON

- **Status:** ACCEPTED (GATE 3)
- **Context:** Rooms must be authorable without touching Python (audit S2).
  Format must be human-editable, diffable, validatable with stdlib.
- **Decision:** JSON, schema versioned (`"format_version": 1`), validated
  by `tools/validate_rooms.py` at build/dev time and re-validated on load
  (fail loud).
- **Alternatives considered:**
  - *TOML:* readable, but no Tiled exporter and weaker ecosystem for
    schema validation; rejected on tooling, not merit.
  - *Python data files:* executable config is a footgun (arbitrary code
    in data); rejected.
  - *Tiled TMX/XML:* heavier than needed; JSON export from Tiled remains
    compatible if we later adopt the editor.
- **Consequences:** Rooms are pure data; validator is the contract
  enforcer (schema + reachability). Schema changes bump
  `format_version`; loader rejects unknown versions loudly.

## D010 — Turret targeting: nearest target, deterministic tie-break

- **Status:** ACCEPTED (GATE 3; resolves scope open question #3)
- **Context:** Turrets must target player and echoes predictably enough
  for puzzle design.
- **Decision:** Candidates = living player + live echoes within range
  with clear line-of-sight (tile raycast). Target = nearest by Euclidean
  distance; tie-break: player first, then lowest entity id. Targeting is
  re-evaluated only at each shot decision (every `period` seconds), not
  per tick — cheaper and more learnable.
- **Consequences:** Fully deterministic given positions; designers can
  reason about "who gets shot". No AI, no prediction, no lead.

## D011 — Simulation: fixed 60 Hz timestep, accumulator

- **Status:** ACCEPTED (GATE 3; formalizes TECHNICAL_REQUIREMENTS)
- **Context:** Echo determinism and fair timing need a tick-quantized sim.
- **Decision:** Fixed 60 Hz simulation via accumulator; render decoupled;
  max 3 catch-up steps, then drop time (never spiral). Recording,
  playback, hazards, and timers all operate in ticks, never wall-clock.
- **Consequences:** Identical inputs → identical outcomes; cycle = 2400
  ticks exactly; pause = stop accumulating. Minor cost: positions are
  tick-quantized (irrelevant at 60 Hz).

## D012 — Collision: AABB via pygame.Rect, axis-separated resolution

- **Status:** ACCEPTED (GATE 3)
- **Context:** Top-down tilemap + small entity counts; pixel-perfect is
  unnecessary at 16 px tiles.
- **Decision:** `pygame.Rect` AABB everywhere (tiles, player, hazards,
  projectiles, devices). Player movement resolved axis-by-axis against
  the tilemap. Echoes do NO tile collision (their recorded positions
  were valid when recorded — pre-validated by construction); echoes use
  AABB only for hazard overlap checks.
- **Alternatives:** masks (rejected: cost without benefit at this scale).
- **Consequences:** Simple, fast, debuggable (F2 overlay draws rects).
  Risk H retired by construction.

## D013 — Project structure: single package `src/nullshift`

- **Status:** ACCEPTED (GATE 3)
- **Context:** The GATE 3 brief's example structure (`game/`, `player/`,
  `echo/`, `world/` … as separate top-level packages) is over-segmented
  for ~3–4 kLOC. Deep trees slow down a weekend build.
- **Decision:** One package, flat modules grouped by the draft's proven
  layout (`sim/`, `render/`, `audio/`, `save/` subpackages only where
  they earn it). Full structure documented in ARCHITECTURE.md §1.
- **Consequences:** Fewer files, obvious imports, no package-plumbing
  overhead. If a module exceeds ~600 lines, split it then — not before.

## D014 — Save implementation deferred to GATE 5 (spec locked at GATE 3)

- **Status:** ACCEPTED (GATE 3)
- **Context:** The vertical slice (rooms 1.1–1.2, single session) gains
  nothing from persistence; building it early spends slice time.
- **Decision:** Save format/location/corruption behavior are fully
  specified now (GAME_SCOPE §11, ARCHITECTURE §16); implementation lands
  with core systems at GATE 5. The slice uses in-memory unlock flags.
- **Consequences:** Slice stays minimal; save module has a frozen spec
  to implement against later. No save code exists until GATE 5.
