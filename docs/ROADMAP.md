# Roadmap — NULL//SHIFT

## Gates

```text
GATE 0 — Discovery complete .............. DONE (2026-10-02)
GATE 1 — Game scope complete ............. DONE (2026-10-02)
GATE 2 — Scope audit approved ............ DONE (2026-10-02, PASS WITH CONDITIONS)
GATE 3 — Architecture approved ........... DONE (2026-10-02, PASS — see gate report in chat)
GATE 4 — Vertical slice approved ......... DONE (2026-10-02, APPROVED WITH CONDITIONS —
  condition: first-time-player validation via docs/PLAYTEST_PROTOCOL.md
  before content production)
GATE 5 — Core systems complete ........... PENDING (hazards, devices, audio, save impl)
GATE 6 — Content complete (12 rooms) ..... PENDING
GATE 7 — QA complete ..................... PENDING
GATE 8 — Release candidate (clean-machine)  PENDING
GATE 9 — Windows release ................. PENDING
```

No gate is passed silently. Each gate states its acceptance criteria and
the evidence.

## Vertical slice (GATE 4) — acceptance criteria

Playable Room 1.1 + Room 1.2 ("First Debt") proving:

1. 8-dir movement + collision + interact feel right (the §2 responsiveness
   contract, measured, not vibes).
2. 40 s cycle, recording, reset (timer + R + death), 1 echo playback.
3. Echo holds pressure plate → player passes door → exit pad.
4. Reset flash + timer bar + echo pip HUD readable.
5. One placeholder art pass (programmer art acceptable), one SFX each for
   interact/door/reset/death, title + pause + room-complete screens.
6. Runs from source on Windows; no packaging yet.

If the slice does not make a first-time player say "my past self is part
of the puzzle" within 5 minutes, the mechanic — not the content — is
wrong. Fix the mechanic before building rooms.

## Weekend schedule (asymmetric — scope is the constraint)

| When | Goal |
|---|---|
| Fri (today) | Scope + audit + architecture lock (GATES 1–3) |
| Sat AM | Vertical slice: movement, cycle, recording, reset, 1 echo (GATE 4) |
| Sat PM | Devices (plates/consoles/doors), hazards v1, rooms 1.1–2.3 |
| Sun AM | Rooms 3.1–4.3 + final, audio synth + sequencer, save system |
| Sun PM | Art pass, QA checklist, PyInstaller build, clean-machine test (GATES 7–9) |

Buffer rule: Sunday PM is sacred — if content slips, cut rooms (4.2,
then 2.3), never cut the build/QA window. Room cap is 12; floor is 8
(1.1, 1.2, 2.1, 2.2, 3.1, 3.2, 4.1, F.1) and the game still works.

## MVP definition (v1.0)

The smallest shippable game: 8 rooms (floor above), 3 hazard types,
echo system per §4, procedural audio, save, menus, Windows exe. Anything
beyond is stretch and gets cut first.

## Post-launch (explicitly not scheduled)

Level editor, speedrun timer, achievements, controller support,
localization, Linux/macOS ports — only if v1.0 ships and Lucas wants more.
