# Build — NULL//SHIFT

**Status:** Phase 1 — pipeline defined; validated at GATE 8 (release
candidate) on a clean Windows machine.

## Pipeline

```text
SOURCE (src/, assets/, data/, build.spec, requirements.txt)
  ↓  pytest tests/                 (unit + room validation + replay regression)
TEST
  ↓  python -m PyInstaller build.spec   (on Windows)
PACKAGE → dist/NULLSHIFT/
  ↓  sanity run: dist/NULLSHIFT/NULLSHIFT.exe --smoke
SMOKE
  ↓  zip
RELEASE ARTIFACT → NULLSHIFT-<version>-win64.zip
  ↓  GitHub Release (manual upload for v1.0)
PLAYER: download → unzip → double-click NULLSHIFT.exe → play
```

## Executable

- Name: `NULLSHIFT.exe` (all-caps, matches project styling).
- Output: `dist/NULLSHIFT/` (one-dir per D007).
- Version: from `src/version.py` (`__version__`), mirrored in
  `--version` flag and title screen. Scheme: `0.1.0` slice → `1.0.0`.
- Icon: `assets/icon.ico` (generated from pixel-art logo; placeholder
  acceptable until art pass).

## Reproducibility

- `requirements.txt` pins Pygame and PyInstaller (hashes optional;
  pins mandatory).
- `build.spec` is checked in; no GUI wizard steps. It bundles `data/`
  and `assets/` explicitly; `paths.resource_path()` resolves
  `sys._MEIPASS` when frozen so the exe runs from any directory.
- Build script `tools/build.ps1`: clean → `pytest` → `validate_rooms.py`
  → PyInstaller → smoke run → zip. One command: `.\tools\build.ps1`.
  The build FAILS if tests or room validation fail — packaging never
  runs on red.
- Smoke test: launch with `--smoke` (auto-quit after title + one
  simulated sector load), exit code 0 = package healthy.

## Validation checklist (GATE 8, clean machine without Python)

1. Unzip on a machine that never had Python/Pygame.
2. Double-click `NULLSHIFT.exe` → title in < 3 s.
3. Start new game → Sector 01 loads < 500 ms.
4. Complete Room 1.2 (echo puzzle) — verifies sim + audio init.
5. Trigger save (sector complete) → close → relaunch → progress kept.
6. No console window, no missing-DLL popups, clean exit via menu.

## Developer quickstart (post-implementation)

```bat
git clone <repo>
cd nullshift
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python -m src.main            REM run from source
pytest                        REM tests
.\tools\build.ps1             REM full release build
```

## Release notes

Each GitHub Release includes: zip, SHA-256, controls list, known issues,
and the audit gate status. No auto-updater; players re-download.
