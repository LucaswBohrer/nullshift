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

---

## D015 — Exit pad triggers on overlap (supersedes 30-tick hold)

- **Status:** ACCEPTED (GATE 4)
- **Context:** ARCHITECTURE.md §8 specified a 30-tick (0.5 s) overlap hold
  on exit pads as "anti-brush". Implementation revealed the hold is
  unreachable by normal play: a walking player crosses the 16 px pad in
  ~9 ticks, so the exit could never fire while walking through it.
- **Decision:** Exit pads fire on the first overlap tick (player only;
  echoes never trigger). The hold concept is dropped, not tuned.
- **Consequences:** Simpler, testable (T10), no downside observed in the
  slice. If brush-through exits become a design problem in later rooms,
  revisit with a decision record — do not silently re-add the hold.

---

## D016 — Controlled backtracking & persistent world state

- **Status:** PROPOSED (Phase 4.5) — requires Lucas's approval before any
  implementation. Does not alter locked behavior until approved.
- **Context:** CREATIVE_DIRECTION.md (adopted) requires the station to
  feel like one coherent explorable place with purposeful backtracking
  ("return and the station has changed"). The locked architecture
  (D006, ARCHITECTURE.md §4/§6, test T8) clears echoes on room transition
  and resets rooms to entry snapshots, with nothing persistent except
  unlocks/stats. Unrestricted persistent simulation is explicitly NOT the
  goal — the target is ~80% perceived change via presentation/scripted
  state, ~20% via genuine persistent gameplay state.
- **Decision:** introduce a **Progression** state object, owned by `Game`
  (not by `World`/the cycle sim), holding a flat dict of persistent
  flags, e.g. `{"power_restored": true, "access_level": 2,
  "door_lab_unlocked": true, "met_lia": true}`. Rules:
  - **Ownership:** `Game` owns Progression; `World` receives a read-only
    view at room build/entry. The cycle sim can never write it.
  - **Reset semantics:** cycle reset and death NEVER touch persistent
    state. Only explicit player actions (or scripted story beats) set
    flags, via `Game` — never via echo playback (see D017 invariant).
  - **Room transition semantics:** entering a room rebuilds it from
    (room data + persistent flags + TEMPORAL recompute); echoes and
    recordings are still cleared (T8 semantics preserved).
  - **Entry snapshot:** persistent flags may *influence* the room's entry
    snapshot (e.g. a permanently unlocked door starts open), but the
    flags themselves are never part of the snapshot. Snapshot/restore
    continues to cover RESETTABLE only.
  - **Serialization:** the flags dict is JSON-native; it becomes part of
    the save spec (extends D003/D014, no save code yet).
  - **Determinism:** flags change only via explicit discrete actions;
    no randomness, no time dependence.
- **Explicit answers:**
  - *Cycle reset → persistent state?* Untouched.
  - *Leave and return?* Room rebuilt; persistent effects visible;
    echoes cleared; recordings cleared.
  - *Death?* Like reset; persistent untouched.
  - *What may influence the entry snapshot?* Persistent flags (as initial
    conditions), TEMPORAL recompute (D017). Nothing else.
  - *What may never enter an echo recording?* Persistent flags,
    progression events, TEMPORAL values — recordings capture only
    per-tick frames + in-cycle device events.
- **Consequences:** enables backtracking with real consequences without
  a persistent simulation; T8 must be extended (not rewritten) to assert
  persistent flags survive transitions; new tests listed in
  ARCHITECTURE_DELTA_4_5.md §test impact. No implementation until
  approved.

## D017 — TEMPORAL state category

- **Status:** PROPOSED (Phase 4.5) — requires approval. Extends (does not
  replace) the RESETTABLE/PERSISTENT/SESSION/DERIVED classification.
- **Context:** The creative direction needs state that "depends on the
  temporal phase" (CREATIVE_DIRECTION.md §8): machines operable only when
  story conditions hold, terminal text variants, phase-dependent
  presentation. Calling everything "persistent" would wrongly make it
  writable by gameplay; calling it "resettable" would wrongly make the
  sim mutate it.
- **Decision:** TEMPORAL state is **read-only during a cycle**, computed
  once at room entry as a pure function of
  `(persistent flags, narrative phase, visit counters)`. Examples: a
  machine's *availability* (operable iff `power_restored`), a terminal's
  text variant for the current act, alarm lighting state.
- **The ten questions:**
  1. *TEMPORAL vs RESETTABLE?* The sim may mutate RESETTABLE (and the
     snapshot restores it). The sim may never mutate TEMPORAL.
  2. *Survives cycle reset?* Vacuously yes: reset restores the
     room-entry computed value, which the sim could not have changed.
  3. *Survives room transition?* It is recomputed on every room entry —
     consistent by construction, stored nowhere.
  4. *Observed by an echo?* Echoes don't observe state; but an echo's
     recorded events may target a TEMPORAL-gated device, since the gate
     was fixed at entry and is constant for the cycle.
  5. *Created/modified by an echo?* **Never — invariant.** Only the
     living player's explicit actions (or scripted beats) may change
     persistent inputs; TEMPORAL itself is never written, only recomputed.
  6. *Affects future cycles?* Constant within a room across cycles;
     changes only when its persistent inputs change.
  7. *Deterministic?* Yes — pure function of its inputs.
  8. *Serialized?* Never directly.
  9. *In save data?* No — its inputs (flags, phase, counters) are.
  10. *Reconstructed after load?* Recomputed at room entry from loaded
      inputs. Nothing to migrate.
- **Concrete test case** (machine operated by an echo, player uses the
  result): the machine's *in-cycle* operating state is **RESETTABLE**
  (echo toggles it, player benefits this cycle, reset clears it). The
  machine's *availability* is **TEMPORAL** (f(persistent flags)). If the
  story needs the repair to be permanent, that is a **PERSISTENT** flag
  set only by the player's own explicit action — never by echo playback.
- **Classification rule for future developers:** "Can the cycle sim
  mutate it?" → RESETTABLE. "Is it a pure function of progression at
  entry?" → TEMPORAL. "Must it survive resets as stored data?" →
  PERSISTENT. "Cleared on room exit?" → SESSION. "Recomputable cache?" →
  DERIVED. If none fit, the design is wrong — do not invent a sixth
  category silently.
- **Consequences:** gives the §8 "temporal exploration" a precise
  implementation shape without breaking determinism; terminal/text
  variants and phase presentation become TEMPORAL data, not code
  branches.

## D018 — Scripted temporal entities ("rogue echoes")

- **Status:** PROPOSED (Phase 4.5) — requires approval. No implementation.
- **Context:** CREATIVE_DIRECTION.md §10 (adopted): an echo that continues
  past its recording, enters rooms the player never visited, then
  vanishes — `ECHO TERMINATED / SOURCE: UNKNOWN`. If player recordings
  could spontaneously deviate, determinism (D004) and the entire echo
  test suite (T4, T7, T9) become meaningless.
- **Decision:** introduce a separate runtime category, **scripted
  temporal entity**, disjoint from player echoes:
  - **Player echo:** immutable recording, deterministic playback, fully
    testable (unchanged, D004 stands unweakened).
  - **Scripted temporal entity:** authored behavior (a tick script from
    room/story data, *not* derived from any player recording); may
    visually resemble an echo (same sprite treatment — the ambiguity is
    the point); deterministic by authorship.
  - The player is never told the distinction. The engine always knows it.
- **Rules:**
  - **Lifecycle:** spawned by room/story data (trigger: entry count,
    flag, script point); despawned by script end or room exit. **Survives
    cycle resets within the room** (SESSION-like; this is the horror —
    resetting doesn't banish it). Cleared on room transition.
  - **Identity:** own id; never references a player recording; cannot
    read or mutate recordings.
  - **Rendering:** echo visual treatment (cyan, scanlines).
  - **Collision:** none with the player (as echoes).
  - **Interaction:** may trigger plates/consoles *per its authored
    script*; cannot be "used" by the player; never triggers exits.
  - **Hazards:** immune (it is residue, not matter) — documented, not
    emergent.
  - **Targeting:** turrets never target it (not in the D010 candidate
    set).
  - **Rooms:** room-local, like echoes.
  - **3-echo limit:** does NOT count toward the FIFO cap (the cap is on
    player recordings, D005 unchanged).
  - **Determinism/testing:** the authored tick script is fixed data;
    tests assert exact positions/events per tick, exactly like echo
    fidelity tests. Player-echo immutability is asserted separately.
- **Implementation note (future):** reuse the `Echo` playback machinery
  over an *authored* Recording built from data — shared code path,
  inherited determinism. No new playback system.
- **Consequences:** the §10 horror becomes implementable and testable
  without touching the player-echo contract; QA can distinguish "scripted
  entity misbehaving" (data bug) from "echo misbehaving" (engine bug).
