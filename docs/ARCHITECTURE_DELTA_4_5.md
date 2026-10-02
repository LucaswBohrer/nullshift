# Architecture Delta — Phase 4.5

**Status:** PROPOSAL. Nothing here is implemented. Locked architecture
(ARCHITECTURE.md @ Gate 3/4) is unchanged; amendments below are
old-rule → proposed-rule pairs awaiting Lucas's approval.

**Decisions proposed:** D016 (backtracking/persistent world), D017
(TEMPORAL category), D018 (scripted temporal entities) — see DECISIONS.md.

---

## 1. World model — "station, not level sequence"

The station remains **technically a graph of rooms** (JSON data, as now).
The creative "world" is a presentation/composition layer over that graph:

- **Composition:** rooms link via exits (`exit.next`, already data). Add
  optional bidirectional links and **flag-gated exits** (e.g.
  `"requires": {"access_level": 3}`) — data, not code.
- **Revisit:** entering a room rebuilds it from
  `(room data + persistent flags + TEMPORAL recompute)`. Echoes and
  recordings are still cleared on transition (T8 preserved).
- **Continuity perception:** persistent flags (doors, power, access) +
  TEMPORAL presentation (lighting, terminal variants, LIA lines keyed by
  visit count/phase). No monolithic world simulation exists or is planned.
- **Echoes stay room-local.** This is unchanged and load-bearing: it
  bounds recording memory and keeps puzzles self-contained.

## 2. Narrative system boundary

No narrative engine. The minimum viable narrative layer is **data**:

- Room JSON gains optional: `terminals[].variants` (text keyed by flag),
  `lia_lines[]` (trigger: visit count / flag / room entry),
  `scripted_entities[]` (D018 data).
- A single `narrative_flags` registry (documented list, e.g.
  `met_lia`, `found_mara_recording_2`) — flags live in the D016
  Progression dict.
- **Bounds (locked for v1.0):** text only; total narrative words < 1500;
  no dialogue trees; no quest framework; no event bus; nothing
  gameplay-blocking; nothing required to solve puzzles.

## 3. Tomas Reed — adopted creative constraint

Tomas is **asynchronous in v1.0**: messages, recordings, maintenance
notes, terminal logs — never a live companion or real-time NPC. Rationale
(creative): preserves the station's solitude, which is the theme; also the
cheapest narrative form (pure data). A live Tomas would be a new
character system requiring its own decision record — explicitly out.

## 4. Delta classification

| Area | Classification | Notes |
|---|---|---|
| Fixed 60 Hz sim, tick order | UNCHANGED | |
| Echo recording/playback (D004) | UNCHANGED | D018 adds a *separate* category; player echoes untouched |
| 3-echo FIFO (D005) | UNCHANGED | scripted entities don't count |
| Room JSON format (D009) | CLARIFICATION | optional new fields (variants, requires, scripted_entities); schema version stays 1 until a breaking change |
| State categories | NEW DECISION | D017 adds TEMPORAL; the other four unchanged |
| Reset semantics | REQUIRES AMENDMENT | see §6 amendment A |
| Room snapshots | REQUIRES AMENDMENT | see §6 amendment B |
| Room transitions | CLARIFICATION | echoes still cleared; persistent flags now flow into rebuild |
| Save model (D003/D014) | CLARIFICATION | flags dict + phase + counters join the spec; no code yet |
| Test architecture | FUTURE | new tests listed in §7, not written |
| World map UI | FUTURE | station map screen is post-v1.0 if ever |
| Acts III–IV systems | FUTURE | explicitly out of v1.0 |

## 5. Save impact (D014 extended, still no implementation)

- **Will serialize:** persistent flags dict, narrative phase/act,
  per-room visit counters, settings, stats (already specced).
- **Never serialize:** TEMPORAL values (recomputed), echo recordings
  (SESSION), scripted-entity runtime state (recomputed from data+flags),
  DERIVED caches.
- **Migration:** flags are additive string keys; unknown flags ignored on
  load (forward-compatible by construction).

## 6. Proposed amendments (require approval before implementation)

**Amendment A — reset semantics (ARCHITECTURE.md §3/§6)**
- *Old rule:* "on reset, all RESETTABLE state reverts to the room-entry
  snapshot; only recordings, unlocks, stats persist."
- *Proposed:* "…only recordings, **persistent progression flags**,
  stats persist. Persistent flags are owned by `Game`, invisible to the
  cycle sim, and never written by echo playback."
- *Reason:* D016 backtracking.
- *Affected tests:* T6/T8 extended (new assertions; existing assertions
  unchanged). No existing test is invalidated.
- *Migration:* none (no save code exists yet).

**Amendment B — room entry snapshot (ARCHITECTURE.md §4.3)**
- *Old rule:* snapshot = RESETTABLE baseline captured at room entry from
  room data alone.
- *Proposed:* snapshot baseline = room data + persistent-flag effects
  applied at build + TEMPORAL recompute; flags themselves stay outside
  the snapshot.
- *Reason:* D016/D017 — a permanently unlocked door must start open.
- *Affected tests:* T6 extended with a flag-influenced room fixture.
- *Migration:* none.

**Amendment C — state classification table (ARCHITECTURE.md §6)**
- *Old rule:* four categories.
- *Proposed:* five, with TEMPORAL defined per D017 (read-only during
  cycle, computed at entry, never serialized).
- *Reason:* D017.
- *Affected tests:* new classification tests (§7). Existing table rows
  unchanged.

No other locked section requires amendment.

## 7. Test impact analysis (future tests — NOT written in this phase)

**Persistence (D016):**
- persistent flag survives cycle reset / death / room transition;
- revisiting a room shows flag effects (e.g. door stays open);
- echo playback never sets a persistent flag (invariant test);
- entry snapshot includes flag effects but not the flags.

**TEMPORAL (D017):**
- TEMPORAL value constant across cycles within a room;
- recomputed (not stored) on room re-entry after flag change;
- sim cannot mutate TEMPORAL (attempt → assertion/test);
- TEMPORAL never appears in recordings or save data.

**Scripted entities (D018):**
- authored tick script replays exactly (like T4);
- player recordings immutable in presence of scripted entities;
- scripted entity survives cycle reset, cleared on room transition;
- does not count toward the 3-echo FIFO cap;
- turrets never target it; hazards never kill it.

**Backtracking:**
- room revisit deterministic given same (data, flags, phase);
- presentation reflects persistent state;
- reset does not erase progression.

## 8. What is deliberately NOT in this delta

- Save/load implementation (still D014-deferred).
- The §8 "machine" concrete mechanics (needs D017-approved design work
  at Gate 5).
- Instance-choice ending (FUTURE — needs its own design when Act IV is
  scoped).
- Station map UI, journal/quest log, dialogue runtime (all rejected for
  v1.0 by the narrative boundary, §2).
