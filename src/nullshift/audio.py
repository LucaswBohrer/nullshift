"""Audio manager: mixer init with silent fallback, SFX routing, mute."""
import pygame

from nullshift import synth

_available = False
_sounds = {}
_muted = False


def init() -> bool:
    global _available, _sounds
    try:
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.mixer.init()
    except pygame.error:
        _available = False
        return False
    try:
        _sounds = synth.build_all(pygame)
        _available = True
    except pygame.error:
        _available = False
    return _available


def available() -> bool:
    return _available


def play(name: str) -> None:
    if _available and not _muted and name in _sounds:
        _sounds[name].play()


def toggle_mute() -> bool:
    global _muted
    _muted = not _muted
    return _muted


def muted() -> bool:
    return _muted
