# Changelog

All notable changes to NULL//SHIFT will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project scaffold: README, LICENSE (MIT), .gitignore, CHANGELOG.
- `docs/GAME_SCOPE.md` — complete game scope (phase 1).
- `docs/SCOPE_AUDIT.md` — formal scope audit, PASS WITH CONDITIONS (phase 2).
- `docs/DECISIONS.md` — decision records D001–D014 (D006 amended: room-entry
  snapshots; D009 room JSON format; D010 turret targeting; D011 fixed 60 Hz;
  D012 AABB collision; D013 project structure; D014 save deferred to GATE 5).
- `docs/ARCHITECTURE.md` — **LOCKED at GATE 3**: room lifecycle, snapshot/
  echo/reset models, normative echo CAN/CANNOT, hazard + turret targeting
  spec, state machine, test architecture (10 areas), risk register A–J.
- `docs/TECHNICAL_REQUIREMENTS.md`, `docs/BUILD.md` (test-gated pipeline),
  `docs/ROADMAP.md`.

### Notes
- No gameplay implementation yet. Implementation begins only after the scope
  audit gate (GATE 2) is explicitly approved.

## [0.1.0] — Vertical slice (2026-10-02)

- Runtime shell: Pygame fixed-60 Hz loop, state machine
  (TITLE/PLAYING/PAUSED/SECTORCARD/TERMINAL/GAMECOMPLETE), input, renderer
  (640×360 ×2), procedural SFX (12 sounds, silent fallback), debug overlay.
- Temporal core per locked architecture: tick recording, room-entry
  snapshot reset, echo playback (tick-for-tick), FIFO cap 3, death_tick
  vanishing echoes, per-room temporal state.
- Rooms 1.1 ("Wake") + 1.2 ("First Debt") as validated JSON data; zero
  room-specific code.
- Tests: 31 green (T1–T10); `tools/validate_rooms.py`; `--smoke` boot check.
- D015: exit pad fires on overlap (30-tick hold dropped as unreachable).
- NOT validated: Windows PyInstaller build (Linux sandbox), real-hardware
  FPS, first-time-player comprehension (see docs/PLAYTEST_PROTOCOL.md).

## [1.0.0] — Weekend release (planned)

- Sectors 01–04 + final encounter, hazards, audio, save system,
  reproducible Windows executable via PyInstaller.
