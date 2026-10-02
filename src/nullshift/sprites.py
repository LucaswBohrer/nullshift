"""Placeholder art, code-drawn (placeholder-first policy, scope §13).

All sprites are 16x16. Echo frames are palette-shifted player frames + scanlines.
"""
import pygame

_cache = {}

AMBER = (255, 176, 64)
CYAN = (64, 224, 255)
DARK = (10, 12, 18)


def _surf():
    s = pygame.Surface((16, 16), pygame.SRCALPHA)
    return s


def _tile_base():
    s = _surf()
    s.fill((26, 30, 42))
    pygame.draw.rect(s, (20, 23, 33), (0, 0, 16, 16), 1)
    return s


def _make_tile(kind: str):
    s = _tile_base()
    if kind == "floor_dark":
        s.fill((19, 22, 31))
        pygame.draw.rect(s, (15, 17, 25), (0, 0, 16, 16), 1)
    elif kind == "floor_hazard":
        for x in (3, 11):
            pygame.draw.rect(s, (200, 150, 40), (x, 6, 2, 4))
    elif kind == "wall":
        s.fill((68, 76, 98))
        pygame.draw.rect(s, (104, 114, 142), (0, 0, 16, 5))  # top highlight
        pygame.draw.rect(s, (52, 58, 78), (0, 12, 16, 4))    # bottom shade
        pygame.draw.rect(s, (88, 96, 122), (0, 0, 16, 16), 1)
        # rivets
        pygame.draw.rect(s, (96, 104, 130), (3, 7, 2, 2))
        pygame.draw.rect(s, (96, 104, 130), (11, 7, 2, 2))
    return s


def _make_player(echo: bool):
    s = _surf()
    body = CYAN if echo else AMBER
    dark = (16, 90, 110) if echo else (120, 70, 20)
    pygame.draw.rect(s, body, (3, 2, 10, 12), border_radius=3)
    pygame.draw.rect(s, dark, (3, 2, 10, 12), 1, border_radius=3)
    pygame.draw.rect(s, DARK, (5, 5, 6, 4))  # visor
    if echo:
        for y in range(0, 16, 3):  # scanlines mark the echo
            pygame.draw.line(s, (10, 40, 50, 160), (0, y), (16, y))
    return s


def _facing_variant(base: pygame.Surface, facing: int):
    # 0=down,1=up,2=left,3=right — rotate the visor side slightly
    return base  # placeholder: single frame per facing is fine for the slice


def player_frame(facing: int, echo: bool = False):
    key = ("player", facing, echo)
    if key not in _cache:
        _cache[key] = _facing_variant(_make_player(echo), facing)
    return _cache[key]


def echo_ghost():
    if ("ghost",) not in _cache:
        _cache[("ghost",)] = _make_echo_ghost()
    return _cache[("ghost",)]


def tile(kind: str):
    key = ("tile", kind)
    if key not in _cache:
        _cache[key] = _make_tile(kind)
    return _cache[key]


def _make_plate():
    s = _surf()
    pygame.draw.rect(s, (60, 64, 78), (1, 8, 14, 7))
    pygame.draw.rect(s, (120, 90, 40), (3, 5, 10, 4))  # unpressed top
    return s


def _make_plate_pressed():
    s = _surf()
    pygame.draw.rect(s, (60, 64, 78), (1, 8, 14, 7))
    pygame.draw.rect(s, (255, 190, 80), (3, 8, 10, 3))  # pressed: sunk + bright
    return s


def _make_console(on: bool):
    s = _surf()
    pygame.draw.rect(s, (40, 44, 58), (2, 4, 12, 12), border_radius=2)
    col = (80, 255, 140) if on else (200, 60, 60)
    pygame.draw.rect(s, col, (4, 6, 8, 5))
    pygame.draw.rect(s, DARK, (4, 6, 8, 5), 1)
    return s


def _make_power_console(on: bool):
    """D016 flag-setting console: station-power hardware, bolt glyph."""
    s = _surf()
    pygame.draw.rect(s, (52, 46, 30), (1, 3, 14, 13), border_radius=2)
    pygame.draw.rect(s, (90, 78, 40), (1, 3, 14, 13), 1, border_radius=2)
    col = (255, 210, 80) if on else (110, 92, 46)
    pygame.draw.polygon(s, col, [(9, 2), (6, 8), (8, 8), (7, 14), (11, 6), (9, 6)])
    return s


def _make_door():
    s = _surf()
    for i in range(0, 16, 4):  # hazard stripes
        pygame.draw.rect(s, (220, 170, 40), (i, 0, 2, 16))
        pygame.draw.rect(s, (30, 30, 36), (i + 2, 0, 2, 16))
    return s


def _make_exit():
    s = _surf()
    pygame.draw.rect(s, (20, 60, 70), (1, 1, 14, 14), 1)
    pygame.draw.polygon(s, CYAN, [(6, 4), (10, 8), (6, 12)])
    return s


def _make_exit_locked():
    s = _surf()
    pygame.draw.rect(s, (70, 26, 26), (1, 1, 14, 14), 1)
    pygame.draw.polygon(s, (150, 70, 70), [(6, 4), (10, 8), (6, 12)])
    pygame.draw.line(s, (255, 80, 80), (3, 3), (12, 12), 2)
    return s


def _make_echo_ghost():
    """Translucent cyan silhouette used for the temporal shimmer."""
    s = _surf()
    pygame.draw.rect(s, (64, 224, 255, 70), (3, 2, 10, 12), border_radius=3)
    return s


def _make_terminal():
    s = _surf()
    pygame.draw.rect(s, (40, 44, 58), (3, 2, 10, 12))
    pygame.draw.rect(s, (90, 200, 255), (5, 4, 6, 4))
    pygame.draw.rect(s, DARK, (5, 4, 6, 4), 1)
    return s


def _make_drone():
    s = _surf()
    pygame.draw.circle(s, (140, 150, 170), (8, 8), 5)
    pygame.draw.circle(s, (220, 70, 70), (8, 8), 2)
    pygame.draw.line(s, (140, 150, 170), (2, 8), (14, 8))
    return s


def _make_turret(armed: bool):
    s = _surf()
    pygame.draw.rect(s, (70, 76, 94), (3, 8, 10, 6))
    col = (255, 60, 60) if armed else (150, 160, 180)
    pygame.draw.rect(s, col, (7, 2, 2, 8))  # barrel
    pygame.draw.circle(s, col, (8, 10), 2)
    return s


def prop(kind: str, variant=None):
    key = ("prop", kind, variant)
    if key not in _cache:
        if kind == "plate":
            _cache[key] = _make_plate_pressed() if variant else _make_plate()
        elif kind == "console":
            _cache[key] = _make_console(bool(variant)) if variant != "power" \
                and variant != "power_on" else _make_power_console(variant == "power_on")
        elif kind == "door":
            _cache[key] = _make_door()
        elif kind == "exit":
            _cache[key] = _make_exit_locked() if variant == "locked" else _make_exit()
        elif kind == "terminal":
            _cache[key] = _make_terminal()
        elif kind == "drone":
            _cache[key] = _make_drone()
        elif kind == "turret":
            _cache[key] = _make_turret(bool(variant))
        else:
            _cache[key] = _surf()
    return _cache[key]
