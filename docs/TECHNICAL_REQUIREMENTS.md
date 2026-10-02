# Technical Requirements — NULL//SHIFT

**Status:** Phase 1/2 — supports the scope audit. Freezes at GATE 3.

## Platform

- Target: Windows 10 (1809+) / 11, 64-bit, no admin rights required.
- Player machine needs: nothing beyond the distributed zip (bundled
  interpreter + SDL via Pygame; no Python install, no VC++ redist beyond
  what PyInstaller bundles — verify on clean machine, see `BUILD.md`).
- Dev machine: Windows 10/11 64-bit, Python 3.12+ (Lucas: 3.14.7),
  Pygame 2.5+, PyInstaller 6+, Git.

## Runtime constraints

- Fixed timestep simulation: 60 Hz; render decoupled; max 3 catch-up
  steps before spiral-of-death clamp (drop time, never spiral).
- Determinism: identical inputs → identical outcomes. No wall-clock
  randomness in sim (visual particles may use RNG; gameplay never).
- Input latency: sample per tick; action effective same tick; reset key
  effective within 2 ticks (see scope §2 for the "responsive" contract).

## Performance budgets

| Budget | Target |
|---|---|
| Frame rate | 60 FPS fixed sim |
| Window | 1280×720 (internal 640×360 ×2) |
| Active entities | < 300 |
| Sector load time | < 500 ms |
| Cold start → title | < 3 s |
| RAM | < 150 MB |
| Distribution zip | < 100 MB |

## Data & formats

- Rooms: authored as data (Tiled JSON or a compact custom text/JSON
  format — decided at architecture gate; must be human-editable and
  diffable).
- Art: PNG, 16×16 base tiles, indexed or RGBA.
- Audio: synthesized at runtime (no audio assets in repo); sequencer
  patterns as data.
- Save: versioned JSON per D003.

## Quality bars

- No crash on corrupt/missing save, missing settings, or missing audio
  device (fall back to silent).
- Clean exit always (no hanging mixer threads — Pygame cleanup order
  documented in architecture).
- All gameplay-relevant audio cues have visual twins (accessibility).

## Out of scope (technical)

No networking, no online services, no anti-cheat, no installer framework
(zip distribution), no auto-updater for v1.0.
