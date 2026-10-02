"""Room data loading + validation (D009). Rooms are pure data; no code per room."""
import json
import os

from nullshift import paths

FORMAT_VERSION = 1

LEGEND = {
    "#": "wall",
    ".": "floor",
    ",": "floor_dark",
    "=": "floor_hazard",
}

DEVICE_TYPES = {"pressure_plate", "console", "door", "exit_pad", "terminal"}
HAZARD_TYPES = {"drone", "turret", "laser"}


class RoomError(Exception):
    """Raised for any room data problem. Always names file + field."""


def load(room_id: str) -> dict:
    path = os.path.join(paths.rooms_dir(), f"{room_id}.json")
    if not os.path.exists(path):
        raise RoomError(f"room '{room_id}': file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RoomError(f"room '{room_id}': invalid JSON: {e}") from e
    validate(data, room_id)
    return data


def _req(data: dict, room_id: str, field: str):
    if field not in data:
        raise RoomError(f"room '{room_id}': missing required field '{field}'")
    return data[field]


def validate(data: dict, room_id: str = "?") -> None:
    fv = _req(data, room_id, "format_version")
    if fv != FORMAT_VERSION:
        raise RoomError(
            f"room '{room_id}': unsupported format_version {fv} (loader supports {FORMAT_VERSION})"
        )
    rid = _req(data, room_id, "id")
    if rid != room_id and room_id != "?":
        raise RoomError(f"room file '{room_id}': id mismatch ('{rid}')")
    grid = _req(data, room_id, "grid")
    w = _req(grid, room_id, "w")
    h = _req(grid, room_id, "h")
    rows = _req(grid, room_id, "rows")
    if len(rows) != h:
        raise RoomError(f"room '{room_id}': grid.rows has {len(rows)} rows, expected {h}")
    for i, row in enumerate(rows):
        if len(row) != w:
            raise RoomError(f"room '{room_id}': grid.rows[{i}] length {len(row)}, expected {w}")
        for ch in row:
            if ch not in LEGEND:
                raise RoomError(f"room '{room_id}': grid.rows[{i}]: unknown tile '{ch}'")

    def check_tile(field: str, tx: int, ty: int, allow_wall: bool = False):
        if not (0 <= tx < w and 0 <= ty < h):
            raise RoomError(f"room '{room_id}': {field} out of bounds ({tx},{ty})")
        if not allow_wall and rows[ty][tx] == "#":
            raise RoomError(f"room '{room_id}': {field} placed inside wall ({tx},{ty})")

    spawn = _req(data, room_id, "spawn")
    check_tile("spawn", spawn["tx"], spawn["ty"])
    for ex in _get_exits(data, room_id):
        check_tile(f"exit '{ex.get('id', 'exit')}'", ex["tx"], ex["ty"])
        if "next" not in ex:
            raise RoomError(f"room '{room_id}': exit missing 'next'")
        nxt = ex["next"]
        if nxt != "END" and not os.path.exists(
                os.path.join(paths.rooms_dir(), f"{nxt}.json")):
            raise RoomError(f"room '{room_id}': exit next '{nxt}' has no room file")
        for flag, want in ex.get("requires", {}).items():
            if not isinstance(want, bool):
                raise RoomError(
                    f"room '{room_id}': exit requires flag '{flag}' must map to bool")

    seen_ids = set()
    for d in data.get("devices", []):
        did = _req(d, room_id, "id")
        if did in seen_ids:
            raise RoomError(f"room '{room_id}': duplicate device id '{did}'")
        seen_ids.add(did)
        dtype = _req(d, room_id, "type")
        if dtype not in DEVICE_TYPES:
            raise RoomError(f"room '{room_id}': device '{did}': unknown type '{dtype}'")
        check_tile(f"device '{did}'", d["tx"], d["ty"], allow_wall=(dtype == "door"))
        if dtype == "door":
            for k in ("tw", "th", "links"):
                if k not in d:
                    raise RoomError(f"room '{room_id}': door '{did}' missing '{k}'")
    # links must resolve (second pass)
    for d in data.get("devices", []):
        if d.get("type") == "door":
            for link in d["links"]:
                if link not in seen_ids:
                    raise RoomError(f"room '{room_id}': door '{d['id']}' links unknown '{link}'")
        if d.get("type") == "console":
            if "sets_flag" in d and not isinstance(d["sets_flag"], str):
                raise RoomError(f"room '{room_id}': console '{d['id']}' sets_flag must be str")
            for req in d.get("requires_on", []):
                if req not in seen_ids:
                    raise RoomError(
                        f"room '{room_id}': console '{d['id']}' requires_on unknown '{req}'")
    # optional metadata
    lighting = data.get("lighting", "auto")
    if lighting not in ("auto", "normal", "emergency", "low"):
        raise RoomError(f"room '{room_id}': lighting must be auto/normal/emergency/low")
    for s in data.get("signs", []):
        check_tile(f"sign '{s.get('text', '?')}'", s["tx"], s["ty"], allow_wall=True)
        if "text" not in s:
            raise RoomError(f"room '{room_id}': sign missing 'text'")
        for cond in s.get("variants", {}):
            kind, _, _ = cond.partition(":")
            if kind not in ("flag", "phase"):
                raise RoomError(
                    f"room '{room_id}': sign variant condition "
                    f"'{cond}' must be flag:NAME or phase:NAME")
    for t in data.get("terminals", []):
        for cond in t.get("variants", {}):
            kind, _, _ = cond.partition(":")
            if kind not in ("flag", "phase"):
                raise RoomError(
                    f"room '{room_id}': terminal '{t['id']}' variant condition "
                    f"'{cond}' must be flag:NAME or phase:NAME")
    for hz in data.get("hazards", []):
        hid = _req(hz, room_id, "id")
        if hid in seen_ids:
            raise RoomError(f"room '{room_id}': duplicate hazard id '{hid}'")
        seen_ids.add(hid)
        if _req(hz, room_id, "type") not in HAZARD_TYPES:
            raise RoomError(f"room '{room_id}': hazard '{hid}': unknown type")
    for t in data.get("terminals", []):
        tid = _req(t, room_id, "id")
        check_tile(f"terminal '{tid}'", t["tx"], t["ty"])
        _req(t, room_id, "text")


def _get_exits(data: dict, room_id: str = "?") -> list:
    """Normalize legacy single 'exit' or new 'exits' list -> list of dicts."""
    if "exits" in data:
        exits = data["exits"]
        if not isinstance(exits, list) or not exits:
            raise RoomError(f"room '{room_id}': 'exits' must be a non-empty list")
        return exits
    if "exit" in data:
        return [data["exit"]]
    raise RoomError(f"room '{room_id}': missing required field 'exit'/'exits'")


def get_exits(data: dict) -> list:
    return _get_exits(data, data.get("id", "?"))


def is_wall(data: dict, tx: int, ty: int) -> bool:
    rows = data["grid"]["rows"]
    if not (0 <= tx < data["grid"]["w"] and 0 <= ty < data["grid"]["h"]):
        return True
    return rows[ty][tx] == "#"


def tile_char(data: dict, tx: int, ty: int) -> str:
    rows = data["grid"]["rows"]
    return rows[ty][tx]
