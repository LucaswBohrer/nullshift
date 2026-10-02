# NULL//SHIFT

A 2D top-down action / survival puzzle game with a temporal-echo mechanic.

You are a maintenance technician trapped in a failing automated research
station. Every cycle is recorded. When the cycle resets, an echo of your
previous self replays your actions — plan, reset, and cooperate with your
own past to open paths, run machines, and survive the station's defenses.

**Status:** pre-implementation. Phase 1 (game scope) in progress.
See `docs/GAME_SCOPE.md` and `docs/SCOPE_AUDIT.md`. No gameplay code exists yet
by design — implementation starts only after the scope audit gate passes.

## Project layout

```text
nullshift/
├── docs/        # source of truth: scope, audit, decisions, architecture, build
├── src/         # game source (Python/Pygame) — NOT STARTED
├── assets/      # pixel art, audio — NOT STARTED
├── tools/       # build/dev utilities — NOT STARTED
└── dist/        # Windows release output (generated, git-ignored)
```

## Documentation (read in this order)

1. `docs/GAME_SCOPE.md` — what the game is, systems inventory, world, narrative
2. `docs/SCOPE_AUDIT.md` — formal audit findings and gate status
3. `docs/DECISIONS.md` — architectural decision records (D001–D008)
4. `docs/TECHNICAL_REQUIREMENTS.md` — platform, performance, constraints
5. `docs/ARCHITECTURE.md` — technical architecture (DRAFT until gate 3)
6. `docs/BUILD.md` — reproducible Windows build pipeline
7. `docs/ROADMAP.md` — phases, gates, weekend schedule

## Build (once implemented)

```bat
REM from a Windows machine with Python 3.12+
pip install -r requirements.txt
python -m PyInstaller build.spec
REM -> dist\NULLSHIFT\NULLSHIFT.exe
```

Full pipeline: `docs/BUILD.md`.

## License

MIT — see `LICENSE`.
