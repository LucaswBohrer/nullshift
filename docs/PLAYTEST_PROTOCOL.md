# Playtest Protocol — NULL//SHIFT Vertical Slice

**Purpose:** the one thing unit tests cannot prove — *can a first-time
player understand the temporal-echo mechanic within ~5 minutes?*

**Status:** NOT YET PERFORMED. The developer playing their own game does
not count. This protocol is for Lucas (or another first-time player) on
the Windows build.

## Setup

- Build: `NULLSHIFT.exe` (or `python -m nullshift` from source).
- No instructions beyond: "Move with WASD/arrows, E interacts. That's it."
- Do NOT explain echoes, resets, or the puzzle beforehand.

## Session script

1. Player starts Room 1.1. Observe silently.
2. Note the timestamp of: first movement, first interact, first reset
   (timer expiry counts, manual R counts double), first terminal read.
3. Player enters Room 1.2. Observe silently.
4. Note: first intentional reset in 1.2, first moment the player watches
   their echo, first verbal/written sign they understand causality
   ("oh — it's doing what I did"), time to solve 1.2.
5. End at slice-complete screen or after 20 minutes, whichever first.

## Record

```text
Tester:
Experience (puzzle games?):
Time to first reset:
Time to first intentional echo use:
Time to understand echo causality:
Time to solve Room 1.2:
Hints required (quote them):
Confusion points (quote them):
Did the player distinguish echo vs self immediately? (Y/N + note)
Cycle length felt: too short / ok / too long:
```

## Pass criteria (GATE 4)

- Echo causality understood within ~5 minutes of first reset.
- Room 1.2 solved without the tester being told the solution.
- Echo vs player visually distinguishable (asked directly after).

## Fail handling

If the slice fails, do NOT add content. Candidate fixes in order:
1. Room 1.2 legibility (plate/door sightlines, echo visibility).
2. Objective/hint text (minimal, contextual).
3. Cycle length (only with observed evidence).
4. Mechanic presentation (reset flash, echo spawn effect).
5. Last resort: mechanic rules (requires a decision record).

## Automated comprehension proxies (already covered)

- T10 proves the puzzle is *solvable* via the intended sequence and
  *unsolvable* without the echo — necessary but not sufficient for
  human comprehension. The manual protocol above is the real gate.
