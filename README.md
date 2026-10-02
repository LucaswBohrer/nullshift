# NULL//SHIFT

A 2D top-down action / survival puzzle game with a temporal-echo mechanic.

You are a maintenance technician trapped in a failing automated research
station. Every cycle is recorded. When the cycle resets, an echo of your
previous self replays your actions — plan, reset, and cooperate with your
own past to open paths and solve puzzles.

**Status: Gate 4 — Vertical Slice** (rooms 1.1 and 1.2 only).
First-time-player playtest is still **pending** — see
`docs/PLAYTEST_PROTOCOL.md`. No content beyond the slice exists yet.

## Run on Windows

Requirements: **Python 3.12+** (64-bit), Windows 10/11.

```bat
git clone https://github.com/LucaswBohrer/nullshift.git
cd nullshift
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=src
python -m nullshift
```

Controls: move `WASD`/`Arrows`, interact `E`, reset cycle `R`,
pause `Esc`, mute `M`.

## Tests

```bat
.venv\Scripts\activate
pip install -r requirements-dev.txt
set PYTHONPATH=src
python -m pytest tests -q
python tools\validate_rooms.py
```

31 tests, all passing at Gate 4.

## Windows executable

**Not yet validated.** The pipeline (`tools\build.ps1`:
test → validate → PyInstaller one-dir → smoke → zip) is defined in
`docs/BUILD.md` but has never run on a Windows machine. Do not claim the
`.exe` works until it has been built and smoke-tested there.

## Docs

Read in order: `docs/GAME_SCOPE.md` → `docs/SCOPE_AUDIT.md` →
`docs/DECISIONS.md` → `docs/ARCHITECTURE.md` (locked) →
`docs/BUILD.md` → `docs/ROADMAP.md`.

## License

MIT — see `LICENSE`.
