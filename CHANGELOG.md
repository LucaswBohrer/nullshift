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

## [0.1.0] — Vertical slice (planned)

- Player movement + collision, temporal cycle, action recording, reset,
  single-echo playback, one puzzle room demonstrating the echo mechanic.

## [1.0.0] — Weekend release (planned)

- Sectors 01–04 + final encounter, hazards, audio, save system,
  reproducible Windows executable via PyInstaller.
