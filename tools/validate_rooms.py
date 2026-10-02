#!/usr/bin/env python3
"""Room data validator: schema + reachability + solvability bound.

Fails loudly. Run: python tools/validate_rooms.py (also invoked by build.ps1).
"""
import glob
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from nullshift import rooms


def check_reachability(data: dict) -> None:
    rid = data["id"]
    w, h = data["grid"]["w"], data["grid"]["h"]
    sp, ex = data["spawn"], data["exit"]
    # doors are passable for reachability (they open); walls block
    seen = {(sp["tx"], sp["ty"])}
    q = deque(seen)
    while q:
        x, y = q.popleft()
        if (x, y) == (ex["tx"], ex["ty"]):
            return
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen
                    and not rooms.is_wall(data, nx, ny)):
                seen.add((nx, ny))
                q.append((nx, ny))
    raise rooms.RoomError(f"room '{rid}': exit unreachable from spawn (doors treated as passable)")


def check_plate_bound(data: dict) -> None:
    rid = data["id"]
    plates = [d for d in data.get("devices", []) if d["type"] == "pressure_plate"]
    if len(plates) > 3:
        raise rooms.RoomError(
            f"room '{rid}': {len(plates)} pressure plates exceed the 3-echo cap (D005)")


def main() -> int:
    pattern = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "data", "rooms", "*.json")
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
            n_dev = len(data.get("devices", []))
            n_haz = len(data.get("hazards", []))
            print(f"OK  {rid}: {n_dev} devices, {n_haz} hazards, exit reachable")
        except rooms.RoomError as e:
            print(f"FAIL {rid}: {e}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
