# NULL//SHIFT — Game Scope

**Status:** Phase 1 — scope definition. Implementation has NOT started.
**Version:** 0.1.0-draft (2026-10-02)

This document is the source of truth for what NULL//SHIFT is. If code ever
disagrees with it, the discrepancy must be resolved explicitly per
`docs/DECISIONS.md` — never silently.

---

## 1. Identity

### 1.1 High concept

NULL//SHIFT is a 2D top-down action/survival puzzle game set inside a failing
automated research station. The player is a maintenance technician trapped
after a temporal synchronization failure locked the station in a 40-second
loop. Every cycle is recorded; when the cycle resets, an echo of the
player's previous self replays their actions. The player plans, acts,
resets, and cooperates with their own echoes to operate machinery, hold
open paths, and survive the station's defenses.

### 1.2 Player fantasy

> You are a lone technician who can cooperate with previous versions of yourself.

The player should feel **clever, not powerful**. Success comes from reading
the room, planning a run, executing it cleanly, and watching a past self
solve half the puzzle for them. The emotional beat the game must deliver,
every sector, is: *"I figured out how to make my past self help my present
self."*

### 1.3 Genre

- **Primary:** top-down puzzle (temporal mechanics)
- **Secondary:** action/survival (hazard avoidance under time pressure)

It is not a roguelike (no procedural generation, no permadeath meta), not an
RPG (no stats), not a platformer.

### 1.4 Target audience

Players who enjoy compact puzzle games with a single strong mechanic
(think *The Company of Myself*, *Cursor*10*-style ideas, *Time Donkey*
experiments). No age-rating-sensitive content: no gore, no voice acting,
minimal text.

### 1.5 Platform

- **Primary and only target for v1.0:** Windows 10/11 64-bit desktop,
  native standalone executable.
- Other platforms (Linux, macOS, web) are explicitly **out of scope** for
  the weekend release. The architecture must not *prevent* ports, but no
  work is spent on them.

### 1.6 Presentation

- 2D top-down, single-room camera: the camera shows one whole room at a
  time (no scrolling within a room; rooms are designed to fit 640×360
  internal pixels). Room transitions are hard cuts with a brief reset flash.
- Pixel art, industrial sci-fi: dark metal floors, hazard striping,
  consoles with blinking lights, cable runs, warning signage. Restrained
  palette: cold blues/grays + amber warnings + cyan UI accents.
- Internal render resolution 640×360, integer-scaled ×2 to a 1280×720
  window (letterboxed if needed). All art authored at 16×16 tile scale.
- Animation philosophy: minimal but readable — 3-frame walks, 2-frame
  machine states, blinking lights. Readability of *timing* (lasers,
  turrets, patrols) outranks visual richness.
- UI philosophy: diegetic-adjacent minimalism — a cycle timer bar, echo
  pips, one-line objective text. No HUD clutter.
- Effects: reset shockwave flash, spark particles on hazard death,
  scanline/vignette overlay for station atmosphere. No screen shake by
  default (toggleable, small amplitude).

### 1.7 Session structure

Linear, sector-based campaign. One sitting of roughly **20–40 minutes**.
Sectors unlock sequentially; within a sector the player may move freely
between its rooms. There is no backtracking across sectors (forward-only
gates), which keeps state management trivial.

---

## 2. Core gameplay loop

```text
EXPLORE room        — read layout, hazards, machines, goal
    ↓
PLAN a run         — decide what this cycle's self must accomplish
    ↓
ACT                — move, interact, dodge (≤ 40 s)
    ↓
RESET              — timer expires, manual reset (R), or death
    ↓
ECHO replays       — previous run becomes a deterministic echo
    ↓
COOPERATE          — act simultaneously with echo(es)
    ↓
SOLVE / SURVIVE    — plates held, consoles toggled, hazards dodged
    ↓
ADVANCE            — reach exit pad → next room/sector
```

**Per minute:** move through a room, dodge one hazard pattern, flip one
machine state.
**Per five minutes:** solve one echo puzzle (2–4 cycles of plan/act/reset).
**Per thirty minutes:** clear a sector, internalizing one new mechanic.
**What sustains play:** the compounding puzzle space — each new echo is a
new "tool" with a fixed, self-authored behavior; later rooms ask "what can
two/three of *you* do that one of you can't?"
**Mastery:** clean execution — minimal cycles per room, no wasted motion,
deliberate sacrifice runs.
**Discovery:** terminal logs, hidden maintenance vents (optional lore),
learning hazard timings by observation.
**Tension:** the 40-second timer plus lethal hazards; every cycle is a
small performance.
**Meaningful decisions:** what to record (every run is a commitment),
when to reset early, which echo to sacrifice, which run becomes the
"holder" vs the "runner".

"Responsive" is defined technically in §8: input sampled per fixed tick
(60 Hz), zero input buffering beyond one tick, movement velocity applied
the same tick, interaction radius generous (≥ 20 px), reset key effective
within 2 ticks.

---

## 3. Systems inventory

Classification: **REQUIRED** / **OPTIONAL** / **NOT PART** / **FUTURE**.

| System | Class | Rationale |
|---|---|---|
| Player controller (8-dir top-down) | REQUIRED | Core verb |
| Movement acceleration/friction | REQUIRED | Simple: constant speed 110 px/s, instant stop |
| Collision (tile + entity AABB) | REQUIRED | Rooms are tilemaps |
| Jumping / climbing / swimming / dashing | NOT PART | No verticality; dash cut — timer pressure is enough |
| Interaction (consoles, terminals, exit pads) | REQUIRED | Core verb #2 |
| Pressure plates | REQUIRED | Primary echo-cooperation device |
| Doors / gates (linked to plates/consoles) | REQUIRED | Progression gates |
| Temporal cycle (40 s timer) | REQUIRED | The game's clock |
| Action recording (per-tick snapshot) | REQUIRED | Enables echoes |
| Temporal reset (timer/manual/death) | REQUIRED | Core verb #3 |
| Echo playback (deterministic replay) | REQUIRED | The game's identity |
| Echo cap: 3, FIFO discard | REQUIRED | Bounds complexity and perf; forces choices |
| Echo vulnerability to hazards | REQUIRED | Enables sacrifice puzzles; prevents tanking |
| Patrol drones (waypoint loops) | REQUIRED | Mobile hazard |
| Turrets (LoS projectiles, timed) | REQUIRED | Ranged hazard |
| Laser grids (timed on/off) | REQUIRED | Timing hazard |
| Player attack / weapons | NOT PART | Fantasy is cleverness, not power; hazards are the "combat" |
| Health system | NOT PART | 1 hit = death = reset (clean, thematic) |
| Stamina / mana | NOT PART | Timer is the resource |
| Status effects | NOT PART | — |
| Enemy AI beyond patrols | NOT PART | Deterministic patterns are a feature (learnable) |
| Bosses | NOT PART | Final encounter is a puzzle sequence, not a boss fight |
| NPCs / dialogue trees | NOT PART | Terminals carry ≤ 3 lines of log text each |
| Quests | NOT PART | Objective = reach the exit; one line of text per room |
| Map / minimap | NOT PART | Single-screen rooms; sector select shows unlocks |
| Checkpoints | REQUIRED | Room-entry checkpoints; echo recordings are per-room (see §4) |
| Save/load (versioned JSON) | REQUIRED | Unlocked sectors + settings (see §9) |
| Progression (mechanics, not stats) | REQUIRED | New device per sector (see §7) |
| Experience / skill trees / upgrades | NOT PART | — |
| Currency / shops / economy | NOT PART | No economy (§10: none) |
| Crafting / inventory | NOT PART | No items to carry (keycards cut — consoles instead) |
| Secrets / collectibles | OPTIONAL | 1 hidden log per sector; zero gameplay effect |
| Achievements | FUTURE | Post-launch |
| Puzzles (environmental) | REQUIRED | The game |
| Physics beyond AABB | NOT PART | No gravity, no ragdoll |
| Destructible objects | NOT PART | — |
| Procedural generation | NOT PART | Hand-designed rooms; determinism is load-bearing |
| Audio: procedural SFX + chiptune | REQUIRED | §11 |
| Dynamic music layers | OPTIONAL | Tension layer in Sector 04/Final if time permits |
| Settings (volume, fullscreen, mute) | REQUIRED | — |
| Input remapping | OPTIONAL | Fixed defaults; remap only if trivial via config file |
| Controller support | FUTURE | Keyboard-only v1.0 (documented) |
| Accessibility options | REQUIRED | §14 (scoped set) |
| Localization | FUTURE | English-only v1.0; all strings in one module for later |
| Tutorial/onboarding | REQUIRED | Sector 01 teaches by doing (no text dumps) |
| Pause | REQUIRED | Esc; freezes sim (timer too) |
| Menus (title/pause/complete) | REQUIRED | Minimal |
| Restart (sector / game) | REQUIRED | — |
| Completion state | REQUIRED | Ending screen + stats (cycles, deaths, time) |

**Cut list (explicitly rejected, not merely deferred):** dash, double-jump,
weapons, HP, XP, currency, crafting, procedural generation, multiplayer,
online features. These contradict the fantasy or the weekend budget.

---

## 4. Temporal mechanics — normative rules

These rules are load-bearing. Puzzles are designed against them; changing
them invalidates room designs.

1. **Cycle length:** 40 seconds, fixed tick 60 Hz (2400 ticks/cycle).
2. **Reset triggers:** timer expiry, manual reset key (R), player death.
   Death-triggered resets still record the fatal run.
3. **Recording:** every tick stores player `(x, y, facing)` plus discrete
   action events (interact, plate enter/exit are derived from position).
   Runs shorter than 60 ticks are discarded (anti-misclick).
4. **Echo spawn:** on reset, the finished run becomes an echo starting at
   tick 0 of the new cycle, replaying its recording exactly.
5. **Echo cap:** maximum 3 echoes. A 4th reset discards the oldest echo
   (FIFO). The HUD shows echo pips so the player can plan around this.
6. **Echo tangibility:** echoes trigger pressure plates, consoles, and
   tripwires exactly as the player did. Echoes do NOT collide with the
   player and do NOT trigger exit pads.
7. **Echo mortality:** hazards destroy an echo. A destroyed echo replays
   only up to its death tick in subsequent cycles, then vanishes. (This is
   what makes sacrifice puzzles work.)
8. **World reset:** on reset, all state of the *current room* (doors,
   plates, consoles, hazard timers, projectiles) reverts to the snapshot
   taken at **room entry**. **Nothing** persists across cycles except:
   echo recordings, unlock/checkpoint flags, and statistics.
9. **Checkpoints and room transitions:** entering a room writes a room
   checkpoint (respawn point + snapshot) and **clears all echoes** —
   recordings belong to the room they were made in and do not transfer.
   The exit pad advances to the next room; the sector exit advances to
   the next sector. There is no mid-room checkpoint — the cycle system
   *is* the checkpoint system.
10. **Pause** freezes the cycle timer. Reset is disabled during pause.

---

## 5. World design

```text
NULL//SHIFT — Meridian Relay Station
└── SECTOR 01 — Arrival (tutorial)
│   ├── Room 1.1 "Wake"        — movement, interact (console → door)
│   └── Room 1.2 "First Debt"  — forced first reset; echo holds plate
├── SECTOR 02 — Power
│   ├── Room 2.1 "Routing"     — power consoles; door needs 2 consoles
│   ├── Room 2.2 "Strobe"      — laser grids (timed); turret introduced
│   └── Room 2.3 "Understudy"  — echo re-flips a console after player passes
├── SECTOR 03 — Maintenance
│   ├── Room 3.1 "Patrol"      — drones on waypoint loops
│   ├── Room 3.2 "Two Hands"   — 2 plates, 1 player → echo mandatory
│   └── Room 3.3 "Martyr"      — sacrifice: echo holds plate inside laser field
├── SECTOR 04 — Core
│   ├── Room 4.1 "Crossfire"   — turrets + drones combined
│   ├── Room 4.2 "Cascade"     — chained consoles on a timer
│   └── Room 4.3 "Triple"      — 3-echo coordination puzzle
└── FINAL — Synchronization
    └── Room F.1 "NULL//SHIFT" — 3 consoles + core pad, one clean 40 s run
```

**Room budget:** 12 rooms, each fitting 640×360, each solvable in 1–6
cycles. Room count is a hard cap — new rooms need a cut elsewhere.
**Traversal:** forward-only; exit pad → next room; sector exit → next
sector (checkpoint + autosave).
**Gates:** doors (plate/console/timer-linked), laser timing, hazard
patterns. No keys, no abilities — the only "keys" are your echoes.
**Environmental storytelling:** damage decals, flickering lights, terminal
logs, abandoned tools. No cutscenes; 2–3 line intro card per sector max.

---

## 6. Narrative

- **Premise:** Meridian Relay Station, an automated deep-space research
  relay, suffered a temporal synchronization failure. The station AI,
  **CUSTODIAN**, locked the facility in a 40-second causality loop while
  it "resolves the anomaly" — you.
- **Protagonist:** a maintenance technician (unnamed; "TECH" on badges).
  No backstory beyond the job — the player projects themselves.
- **Antagonist:** CUSTODIAN — never seen, only heard via terminal text and
  station announcements. Polite, procedural, lethal. Its defenses are not
  malice; they are *maintenance*.
- **Structure:** beginning (wake in Arrival, first loop), middle (push
  toward the Core, CUSTODIAN's messages escalate from helpful to
  threatening), climax (Synchronization: manually re-sync the core),
  ending (loop breaks; the echoes stop; one screen of text + stats —
  deliberately ambiguous whether the tech "survived" or merged).
- **Delivery:** ≤ 3 lines per terminal, ≤ 6 terminals total, sector intro
  cards. Total authored words < 600. Narrative must never block progress
  (all text skippable, none required to solve puzzles).
- **Narrative dependency map:** Sector 01 (establish loop) → Sector 02
  (CUSTODIAN helpful) → Sector 03 (CUSTODIAN concerned) → Sector 04
  (CUSTODIAN hostile) → Final (choice-free climax). Logs are optional and
  order-independent.

---

## 7. Characters

| Character | Type | Gameplay function | Notes |
|---|---|---|---|
| Technician (player) | PLAYER | Move, interact, reset | 16×16, 4-dir, 3-frame walk |
| Echo | MECHANIC | Replays recording; holds plates, flips consoles, dies to hazards | Player sprite, cyan palette-shift + scanline; no new art |
| CUSTODIAN | ANTAGONIST (unseen) | Text only; justifies hazards | Terminal/announcement strings |
| Patrol drone | HAZARD | Waypoint loop; touch = death | 2-frame rotor, 1 type only |
| Turret | HAZARD | Timed LoS projectiles | 2 states (idle/armed), 1 projectile type |
| Dr. Amara Okafor | MINOR NPC (text) | Author of terminal logs | Never appears |
| Laser grid | HAZARD | Timed on/off damage field | Emitter + beam tiles |

One drone type. One turret type. One laser type. Variety comes from
*arrangement and timing*, not from new enemy classes.

---

## 8. Hazard design (in place of combat)

There is no player attack. "Combat" is hazard navigation under the cycle
timer. Rhythms are deterministic and learnable:

- **Drone:** moves waypoints at 70 px/s, loops. Touch (AABB overlap) =
  death. Audible hum when within 120 px (positional cue).
- **Turret:** every 2.5 s, if line-of-sight to player/echo is clear, fires
  a bolt at 260 px/s. Bolt dies on wall. 0.4 s "armed" telegraph (red
  blink + charge sound) before firing. Turrets target echoes too.
- **Laser grid:** cycles 3 s on / 2 s off, with 0.5 s warning flicker.
  Standing in beam while on = death.
- **Death:** immediate reset (per §4.2). No HP, no i-frames, no knockback
  — the loop *is* the failure state, and it is fast (< 1 s to next cycle).
- **Difficulty:** fixed. No scaling, no adaptive difficulty. Fairness via
  determinism: identical inputs → identical outcomes, always.

---

## 9. Progression

Progression is **mechanical, not numerical**. Nothing about the player
improves; the *toolbox* grows:

- S01: move + interact + reset + 1 echo (plates/doors)
- S02: consoles (toggle state), laser timing, turrets
- S03: drones, multi-echo coordination, sacrifice
- S04: chained timed consoles, 3-echo puzzles
- Final: everything combined

**Persistent unlocks:** highest unlocked sector + room. That is the entire
persistent progression state, plus settings and statistics.

---

## 10. Economy

None. There is no currency, no shop, no resources, no sinks. Deliberately
absent: the game's only resource is **time within a cycle**, which needs
no economy design.

---

## 11. Save system

- **Format:** JSON, versioned: `{"version": 1, "unlocked_sector": n,
  "settings": {...}, "stats": {...}}`. Loader rejects unknown versions
  with a clear message and falls back to defaults (never crashes).
- **What is saved:** highest unlocked sector/room, settings (volumes, mute,
  fullscreen), stats (total cycles, deaths, completions, best cycles per
  sector).
- **When:** autosave on sector unlock and on settings change. No manual
  save UI (the checkpoint model makes it redundant).
- **Slots:** one profile. Multiple slots = FUTURE.
- **Corruption handling:** write-temp-then-rename; on parse failure, move
  corrupt file to `saves/corrupt-<timestamp>.json` and start fresh.
- **Location:** `%APPDATA%/NULLSHIFT/saves/` on Windows (portable
  fallback: `./saves/` next to executable if APPDATA unavailable).

---

## 12. Audio

- **Music:** procedural chiptune via a tiny step sequencer (square +
  triangle + noise channels). Two loops: "drift" (sectors 1–3, ~90 BPM,
  sparse) and "pressure" (sector 4 + final, ~132 BPM). Each < 64 steps.
- **Ambience:** low hum + filtered noise bed, per-sector filter cutoff.
- **SFX (all synthesized at startup, no audio files):** step, interact
  blip, console clack, door servo, plate click, laser warn/hit, turret
  charge/shot, drone hum (loop), reset shockwave, echo spawn shimmer,
  UI move/confirm, sector-complete chime, death zap.
- **Channels:** master / music / sfx / ambient, each 0–100, plus mute-all.
  Persisted in settings.
- **Voice:** none. **Subtitles:** n/a (no voice). All audio cues that
  carry gameplay information (laser warn, turret charge) have a visual
  twin — no audio-only mechanics (§14).

---

## 13. Visual asset scope

All art is 16×16-pixel base, authored as PNG (or generated placeholders
in code for the vertical slice). Ranges are honest estimates:

| Category | Items | Notes |
|---|---|---|
| Player | 1 char × 4 dir × (3 walk + 1 idle) = 16 sprites | Echo = palette swap, $0 cost |
| Tileset (industrial) | 40–60 tiles | Floor variants, walls, hazard striping, grates, cables |
| Props | 10–14 | Console (2 states), door (2), plate (2), terminal, exit pad, core, emitter, debris (3) |
| Hazards | ~10 | Drone (2 frames), turret (2 states), bolt, laser beam tiles |
| UI | ~8 | Timer bar, echo pips, objective font (bitmap), menu frames |
| VFX/particles | code-drawn | Reset ring, sparks, shimmer — no sprite cost |
| Backgrounds/parallax | 0 | Single flat room bg per sector tint (5 tints) |
| Cutscenes | 0 | Text cards only |

**Total new sprites: ~100–120.** Weekend-feasible only because: one
character, palette-swap echoes, code-drawn particles, zero backgrounds.
Programmer-art placeholders are acceptable for the vertical slice
(Lucas's standing preference); the art pass happens after mechanics lock.

---

## 14. Accessibility (scoped)

- Fixed keyboard controls shown on-screen; remapping via config file
  (OPTIONAL in-game UI).
- All color-coded information duplicated with shape/symbol (plates =
  shape + color; laser warn = flicker + icon).
- No flashing above 3 Hz; reset flash is a single 150 ms fade.
- Screen shake: off by default, toggleable, ≤ 2 px.
- Volume/mute controls; no audio-only mechanics.
- Text: high-contrast bitmap font, ≥ 8 px cap height at 2× scale.
- Difficulty: fixed by design; no assist mode for v1.0 (documented).

---

## 15. Performance targets

- 60 FPS fixed timestep (render decoupled, max 3 catch-up steps).
- Window 1280×720; internal 640×360 ×2 integer scale.
- Entities: < 300 active (player + 3 echoes + hazards + projectiles +
  particles). Trivial for Pygame at this resolution.
- Memory: < 150 MB. Package: < 100 MB zipped.
- Load: sector load < 500 ms; cold start to title < 3 s.
- Target hardware: any Windows 10/11 64-bit machine with integrated
  graphics from the last ~10 years.

---

## 16. IN SCOPE / OUT OF SCOPE (weekend v1.0)

**IN:** everything marked REQUIRED above; 12 rooms across 4 sectors +
final; 3 hazard types; terminal logs; procedural SFX + 2 chiptune loops;
versioned save; pause/menus/restart; PyInstaller Windows executable;
GitHub repo with docs.

**OUT:** open world, procedural generation, combat/attacks, HP systems,
RPG stats, economy, crafting, inventory, dialogue trees, branching
narrative, multiplayer/online, achievements, controller support,
localization, multiple save slots, cutscenes, web build.

**Explicitly deferred to post-launch:** level editor, speedrun timer,
daily challenge rooms, Linux/macOS ports.

---

## 17. Open questions (must close before/during architecture)

1. Exact cycle length (40 s is a starting constant; playtesting the
   vertical slice may move it to 30–60 s).
2. Whether manual reset keeps the current run's recording (yes, per §4 —
   but verify it doesn't enable degenerate "free echo" farming; FIFO cap
   mitigates).
3. Turret targeting priority when player and echo both in LoS (proposed:
   nearest; verify in slice).
4. Final room layout (designed after Sector 04 proves the mechanics).

Nothing here blocks the audit; all are tunable constants or slice-validated.
