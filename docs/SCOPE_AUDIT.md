# GAME SCOPE AUDIT — NULL//SHIFT

**Date:** 2026-10-02
**Scope version audited:** `docs/GAME_SCOPE.md` 0.1.0-draft (post room-snapshot fix)
**Auditor:** Muse (principal game architect role)

```text
GAME SCOPE AUDIT
================

Status: PASS WITH CONDITIONS

Critical findings:
  (none)

Major findings:
  M1. Room-snapshot semantics were ambiguous in the first draft
      ("sector-entry snapshot" vs. multi-room sectors). Resolved during
      this audit: snapshots are per ROOM ENTRY, room transitions clear
      echoes, checkpoints are per room. GAME_SCOPE.md §4.8/§4.9 updated.
  M2. The 40-second cycle constant is the single most load-bearing number
      in the design. Every room must be solvable within one cycle by
      construction. CONDITION: the vertical slice must validate 40 s
      against Rooms 1.1–1.2; allowed to move to 30–60 s before GATE 4.
  M3. Art (~100–120 sprites) is the critical path for a weekend. The
      placeholder-first policy (scope §13) is load-bearing, not optional:
      mechanics lock before any final art. No "quick art detour" during
      Sat AM.
  M4. 12 rooms is aggressive for one weekend. A floor of 8 rooms is
      defined (1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, F.1) with cut order
      (4.2, then 2.3). The game is complete at 8; 9–12 is stretch.

Minor findings:
  m1. Turret targeting priority (player vs echo in LoS) unspecified.
      Default: nearest target. Revisit only if playtest complains.
  m2. FIFO echo discard can surprise (a crafted echo lost to a careless
      reset). Mitigated by HUD pips; an "echo lock" is deferred to
      playtest, not promised.
  m3. Manual-reset "farming" (short holder-runs) is not an exploit — it
      IS the intended sacrifice/holder vocabulary. Documented as such.
  m4. Narrative word budget (< 600) and skippability are consistent with
      "no text walls" — no action needed.

Contradictions:
  (none remaining after M1 fix)

Missing specifications:
  S1. Exact room layouts — intentionally deferred to production (GATE 4+);
      room validator tool will enforce schema + solvability bounds.
  S2. Room data format (Tiled JSON vs bespoke) — GATE 3 decision.
  S3. Turret priority (m1) — tunable, defaults documented.

Scope risks:
  R1. Weekend overrun: 12 rooms + audio + build in ~2 days. Mitigated by
      room floor (M4) and Sunday-PM-is-sacred build rule (ROADMAP).
  R2. Mechanic comprehension: if the slice doesn't teach the echo in
      5 minutes, no amount of content saves it. Mitigated by GATE 4's
      explicit comprehension criterion.

Technical risks:
  T1. Pygame fixed-timestep discipline — low risk; architecture draft
      mandates accumulator + fixed update order (determinism).
  T2. Deterministic echo playback — de-risked by D004 (snapshot playback,
      not input re-simulation).
  T3. Clean-machine PyInstaller run — scheduled validation at GATE 8;
      smoke test in pipeline.
  Assessment: no technical risk justifies changing D001/D002/D007.

Content risks:
  C1. Art volume (see M3). Mitigation: placeholders, palette-swap echoes,
      code-drawn particles, zero backgrounds.
  C2. Puzzle design quality for 3-echo rooms (4.3, Final) — hardest design
      work; scheduled after mechanics are proven, not before.

Required changes (all applied):
  - §4.8/§4.9/§9/§11: per-room snapshots, room-entry checkpoints,
    per-room echo lifetime, sector/room unlock persistence.

Deferred decisions:
  - Cycle length final value (after slice playtest).
  - Room data format (GATE 3).
  - Echo lock QoL (playtest-driven, not promised).
  - In-game remapping UI (config-file fallback acceptable).

Recommended phase boundary:
  PASS WITH CONDITIONS → proceed to GATE 3 (architecture lock).
  Conditions: (a) M2 validated in slice; (b) no new systems enter scope
  without a decision record; (c) room floor/cut order honored if schedule
  slips.
```

**Explicit confirmation:** implementation has NOT started. No `src/` code,
no assets, no prototype exist. The next authorized work is GATE 3
(architecture approval), then the vertical slice — not full production.
