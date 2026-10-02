"""AABB collision in float space (D012). Deterministic, no rounding drift."""
from nullshift import config

T = config.TILE
_EPS = 1e-6


def overlapping_tiles(x: float, y: float, hw: float, hh: float):
    """Tile coords overlapped by the box centered at (x,y) with half-extents."""
    tx0 = int((x - hw) // T)
    tx1 = int((x + hw - _EPS) // T)
    ty0 = int((y - hh) // T)
    ty1 = int((y + hh - _EPS) // T)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            yield (tx, ty)


def sweep(world, x: float, y: float, dx: float, dy: float, hw: float, hh: float):
    """Axis-separated swept move against solid tiles. Returns (x, y)."""
    if dx != 0:
        nx = x + dx
        solids = [t for t in overlapping_tiles(nx, y, hw, hh) if world.is_solid(*t)]
        if solids:
            if dx > 0:
                nx = min(tx * T for tx, _ in solids) - hw
            else:
                nx = max((tx + 1) * T for tx, _ in solids) + hw
        x = nx
    if dy != 0:
        ny = y + dy
        solids = [t for t in overlapping_tiles(x, ny, hw, hh) if world.is_solid(*t)]
        if solids:
            if dy > 0:
                ny = min(ty * T for _, ty in solids) - hh
            else:
                ny = max((ty + 1) * T for _, ty in solids) + hh
        y = ny
    return x, y
