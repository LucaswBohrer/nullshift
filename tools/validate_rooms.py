#!/usr/bin/env python3
"""Room data validator: schema + reachability + solvability bound.

Fails loudly. Run: python tools/validate_rooms.py (also invoked by build.ps1).
"""
import glob
import json
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from nullshift import rooms

# Persistent flags the game knows about (D016). Exit `requires` and terminal
# variants may only reference these — catches typos in data.
KNOWN_FLAGS = {"power_restored"}
KNOWN_PHASES = {"WAKE", "POWER"}


def check_reachability(data: dict) -> None:
    rid = data["id"]
    w, h = data["grid"]["w"], data["grid"]["h"]
    sp = data["spawn"]
    exits = rooms.get_exits(data)
    # doors are passable for reachability (they open); walls block
    seen = {(sp["tx"], sp["ty"])}
    q = deque(seen)
    found = set()
    while q:
        x, y = q.popleft()
        for ex in exits:
            if (x, y) == (ex["tx"], ex["ty"]):
                found.add(ex.get("id", "exit"))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen
                    and not rooms.is_wall(data, nx, ny)):
                seen.add((nx, ny))
                q.append((nx, ny))
    missing = {ex.get("id", "exit") for ex in exits} - found
    if missing:
        raise rooms.RoomError(
            f"room '{rid}': exits unreachable from spawn (doors treated as "
            f"passable): {sorted(missing)}")


def check_plate_bound(data: dict) -> None:
    rid = data["id"]
    plates = [d for d in data.get("devices", []) if d["type"] == "pressure_plate"]
    if len(plates) > 3:
        raise rooms.RoomError(
            f"room '{rid}': {len(plates)} pressure plates exceed the 3-echo cap (D005)")


def check_progression_refs(data: dict) -> None:
    """All flag/phase references must be known (D016/D017)."""
    rid = data["id"]
    for ex in rooms.get_exits(data):
        for flag in ex.get("requires", {}):
            if flag not in KNOWN_FLAGS:
                raise rooms.RoomError(
                    f"room '{rid}': exit requires unknown flag '{flag}'")
    for d in data.get("devices", []):
        if d.get("type") == "console" and "sets_flag" in d:
            if d["sets_flag"] not in KNOWN_FLAGS:
                raise rooms.RoomError(
                    f"room '{rid}': console '{d['id']}' sets unknown flag "
                    f"'{d['sets_flag']}'")
    for t in data.get("terminals", []):
        for cond in t.get("variants", {}):
            kind, _, name = cond.partition(":")
            if kind == "flag" and name not in KNOWN_FLAGS:
                raise rooms.RoomError(
                    f"room '{rid}': terminal '{t['id']}' variant references "
                    f"unknown flag '{name}'")
            if kind == "phase" and name not in KNOWN_PHASES:
                raise rooms.RoomError(
                    f"room '{rid}': terminal '{t['id']}' variant references "
                    f"unknown phase '{name}'")
    if "set_phase" in data and data["set_phase"] not in KNOWN_PHASES:
        raise rooms.RoomError(f"room '{rid}': set_phase '{data['set_phase']}' unknown")


def check_lia_refs(repo_root: str) -> None:
    """LIA lines must reference real rooms, flags and phases."""
    path = os.path.join(repo_root, "data", "lia.json")
    room_ids = {os.path.splitext(os.path.basename(p))[0]
                for p in glob.glob(os.path.join(repo_root, "data", "rooms", "*.json"))}
    with open(path, encoding="utf-8") as f:
        lines = json.load(f)
    seen = set()
    for line in lines:
        lid = line["id"]
        if lid in seen:
            raise rooms.RoomError(f"lia.json: duplicate id '{lid}'")
        seen.add(lid)
        if line["room"] not in room_ids:
            raise rooms.RoomError(f"lia.json: line '{lid}' references unknown room")
        t = line["trigger"]
        if "visit" in t and (not isinstance(t["visit"], int) or t["visit"] < 1):
            raise rooms.RoomError(f"lia.json: line '{lid}' bad visit trigger")
        if "flag" in t and t["flag"] not in KNOWN_FLAGS:
            raise rooms.RoomError(f"lia.json: line '{lid}' references unknown flag")


def main() -> int:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(repo_root, "data", "rooms", "*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print("validate_rooms: no room files found")
        return 1
    ok = True
    for path in files:
        rid = os.path.splitext(os.path.basename(path))[0]
        try:
            data = rooms.load(rid)
            check_reachability(data)
            check_plate_bound(data)
            check_progression_refs(data)
            n_dev = len(data.get("devices", []))
            n_haz = len(data.get("hazards", []))
            n_ex = len(rooms.get_exits(data))
            print(f"OK  {rid}: {n_dev} devices, {n_haz} hazards, "
                  f"{n_ex} exit(s) reachable")
        except rooms.RoomError as e:
            print(f"FAIL {rid}: {e}")
            ok = False
    try:
        check_lia_refs(repo_root)
        print("OK  lia.json: all lines reference known rooms/flags")
    except rooms.RoomError as e:
        print(f"FAIL lia.json: {e}")
        ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
